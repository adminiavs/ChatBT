"""
DSDE Speculation Length Adapter
Implements dynamic speculation length adaptation based on KLD variance and other signals
"""

import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import logging
from collections import defaultdict, deque
import time

from .signals import CombinedSignalProcessor, SignalConfig

logger = logging.getLogger(__name__)

@dataclass
class AdapterConfig:
    """Configuration for speculation length adapter"""
    min_speculation_length: int = 1
    max_speculation_length: int = 8
    default_speculation_length: int = 4
    
    # Adaptation parameters
    stability_threshold_high: float = 0.7
    stability_threshold_low: float = 0.3
    wvir_threshold_stable: float = 1.0
    wvir_threshold_unstable: float = 3.0
    
    # Learning parameters
    adaptation_rate: float = 0.2
    history_weight: float = 0.8
    
    # Performance thresholds
    min_acceptance_rate: float = 0.3
    target_acceptance_rate: float = 0.7
    
    # Batch optimization
    enable_batch_capping: bool = True
    straggler_tolerance: float = 2.0

class SpeculationLengthAdapter:
    """
    Dynamic speculation length adapter using DSDE methodology
    """
    
    def __init__(self, adapter_config: AdapterConfig = None, signal_config: SignalConfig = None):
        self.config = adapter_config or AdapterConfig()
        self.signal_processor = CombinedSignalProcessor(signal_config)
        
        # Per-sequence state
        self.sequence_states = {}
        self.sequence_performance = defaultdict(lambda: {
            'recent_acceptance_rates': deque(maxlen=10),
            'recent_speculation_lengths': deque(maxlen=10),
            'total_tokens_generated': 0,
            'total_tokens_accepted': 0,
            'last_update_time': time.time()
        })
        
        # Batch-level state
        self.batch_metrics = {
            'current_batch_size': 0,
            'average_sl': 0.0,
            'sl_variance': 0.0,
            'straggler_count': 0
        }
        
        logger.info(f"Initialized SpeculationLengthAdapter with config: {self.config}")
    
    def predict_optimal_sl(self, sequence_id: str, context_info: Dict = None) -> int:
        """
        Predict optimal speculation length for a sequence
        
        Args:
            sequence_id: Unique sequence identifier
            context_info: Additional context information
            
        Returns:
            Predicted optimal speculation length
        """
        # Get current signal metrics
        metrics = self.signal_processor.get_sequence_metrics(sequence_id)
        
        # Get performance history
        perf = self.sequence_performance[sequence_id]
        
        # Base prediction on stability
        base_sl = self._predict_from_stability(metrics)
        
        # Adjust based on historical performance
        history_adjusted_sl = self._adjust_for_history(sequence_id, base_sl)
        
        # Apply context-specific adjustments
        context_adjusted_sl = self._adjust_for_context(history_adjusted_sl, context_info)
        
        # Clamp to valid range
        final_sl = max(self.config.min_speculation_length, 
                      min(self.config.max_speculation_length, context_adjusted_sl))
        
        # Update sequence state
        self._update_sequence_state(sequence_id, final_sl, metrics)
        
        return int(final_sl)
    
    def _predict_from_stability(self, metrics: Dict[str, float]) -> float:
        """
        Predict speculation length based on stability signals
        
        Args:
            metrics: Signal metrics dictionary
            
        Returns:
            Base speculation length prediction
        """
        stability = metrics.get('stability', 0.5)
        wvir = metrics.get('wvir', 1.0)
        entropy = metrics.get('current_entropy', 2.0)
        
        # High stability -> longer speculation
        if stability > self.config.stability_threshold_high and wvir < self.config.wvir_threshold_stable:
            base_sl = self.config.max_speculation_length * 0.8
        # Low stability -> shorter speculation
        elif stability < self.config.stability_threshold_low or wvir > self.config.wvir_threshold_unstable:
            base_sl = self.config.min_speculation_length * 1.5
        # Moderate stability -> adaptive middle ground
        else:
            # Linear interpolation based on stability
            stability_factor = (stability - self.config.stability_threshold_low) / \
                             (self.config.stability_threshold_high - self.config.stability_threshold_low)
            stability_factor = max(0.0, min(1.0, stability_factor))
            
            base_sl = (self.config.min_speculation_length + 
                      stability_factor * (self.config.max_speculation_length - self.config.min_speculation_length))
        
        # Adjust for entropy (lower entropy = more predictable = longer speculation)
        if entropy < 1.0:  # Very low entropy
            base_sl *= 1.2
        elif entropy > 4.0:  # Very high entropy
            base_sl *= 0.8
        
        return base_sl
    
    def _adjust_for_history(self, sequence_id: str, base_sl: float) -> float:
        """
        Adjust speculation length based on historical performance
        
        Args:
            sequence_id: Sequence identifier
            base_sl: Base speculation length
            
        Returns:
            History-adjusted speculation length
        """
        perf = self.sequence_performance[sequence_id]
        
        if not perf['recent_acceptance_rates']:
            return base_sl
        
        # Calculate recent average acceptance rate
        recent_acceptance = np.mean(perf['recent_acceptance_rates'])
        
        # Adjust based on acceptance rate performance
        if recent_acceptance > self.config.target_acceptance_rate:
            # High acceptance rate -> can afford longer speculation
            adjustment = 1.0 + (recent_acceptance - self.config.target_acceptance_rate) * 2.0
        elif recent_acceptance < self.config.min_acceptance_rate:
            # Low acceptance rate -> reduce speculation length
            adjustment = 0.5 + (recent_acceptance / self.config.min_acceptance_rate) * 0.5
        else:
            # Moderate acceptance rate -> minor adjustments
            target_diff = recent_acceptance - self.config.target_acceptance_rate
            adjustment = 1.0 + target_diff * 0.5
        
        # Apply adaptation rate for smooth transitions
        adjusted_sl = base_sl * (self.config.history_weight * adjustment + 
                                (1 - self.config.history_weight) * 1.0)
        
        return adjusted_sl
    
    def _adjust_for_context(self, base_sl: float, context_info: Dict = None) -> float:
        """
        Apply context-specific adjustments
        
        Args:
            base_sl: Base speculation length
            context_info: Context information
            
        Returns:
            Context-adjusted speculation length
        """
        if not context_info:
            return base_sl
        
        adjusted_sl = base_sl
        
        # Task-specific adjustments
        task_type = context_info.get('task_type', 'general')
        if task_type == 'code_generation':
            # Code generation often has more predictable patterns
            adjusted_sl *= 1.1
        elif task_type == 'creative_writing':
            # Creative writing is less predictable
            adjusted_sl *= 0.9
        elif task_type == 'dialogue':
            # Dialogue can be highly variable
            adjusted_sl *= 0.95
        
        # Sequence length adjustments
        sequence_length = context_info.get('current_length', 0)
        if sequence_length > 1000:
            # Very long sequences might have more established patterns
            adjusted_sl *= 1.05
        elif sequence_length < 50:
            # Short sequences are harder to predict
            adjusted_sl *= 0.95
        
        # Temperature adjustments
        temperature = context_info.get('temperature', 1.0)
        if temperature < 0.3:
            # Low temperature -> more predictable
            adjusted_sl *= 1.1
        elif temperature > 1.5:
            # High temperature -> less predictable
            adjusted_sl *= 0.9
        
        return adjusted_sl
    
    def _update_sequence_state(self, sequence_id: str, predicted_sl: int, metrics: Dict):
        """Update internal state for sequence"""
        current_time = time.time()
        
        self.sequence_states[sequence_id] = {
            'last_predicted_sl': predicted_sl,
            'last_metrics': metrics,
            'last_update': current_time,
            'prediction_count': self.sequence_states.get(sequence_id, {}).get('prediction_count', 0) + 1
        }
    
    def update_performance(self, sequence_id: str, 
                          speculation_length: int,
                          accepted_tokens: int,
                          total_tokens: int,
                          processing_time: float = None):
        """
        Update performance metrics after a speculation round
        
        Args:
            sequence_id: Sequence identifier
            speculation_length: Speculation length used
            accepted_tokens: Number of tokens accepted
            total_tokens: Total number of tokens speculated
            processing_time: Time taken for this round
        """
        perf = self.sequence_performance[sequence_id]
        
        # Calculate acceptance rate
        acceptance_rate = accepted_tokens / max(1, total_tokens)
        
        # Update metrics
        perf['recent_acceptance_rates'].append(acceptance_rate)
        perf['recent_speculation_lengths'].append(speculation_length)
        perf['total_tokens_generated'] += total_tokens
        perf['total_tokens_accepted'] += accepted_tokens
        perf['last_update_time'] = time.time()
        
        # Update signal processor with verification results (if we have the logits)
        # This would typically be called with actual logits in a real implementation
        
        logger.debug(f"Updated performance for {sequence_id}: "
                    f"SL={speculation_length}, accepted={accepted_tokens}/{total_tokens}, "
                    f"rate={acceptance_rate:.3f}")
    
    def get_sequence_stats(self, sequence_id: str) -> Dict:
        """Get comprehensive statistics for a sequence"""
        perf = self.sequence_performance[sequence_id]
        state = self.sequence_states.get(sequence_id, {})
        metrics = self.signal_processor.get_sequence_metrics(sequence_id)
        
        stats = {
            'sequence_id': sequence_id,
            'current_metrics': metrics,
            'performance': {
                'total_generated': perf['total_tokens_generated'],
                'total_accepted': perf['total_tokens_accepted'],
                'overall_acceptance_rate': perf['total_tokens_accepted'] / max(1, perf['total_tokens_generated']),
                'recent_acceptance_rate': np.mean(perf['recent_acceptance_rates']) if perf['recent_acceptance_rates'] else 0.0,
                'recent_avg_sl': np.mean(perf['recent_speculation_lengths']) if perf['recent_speculation_lengths'] else 0.0
            },
            'state': state
        }
        
        return stats

class BatchOptimizer:
    """
    Optimizes speculation lengths across a batch to prevent straggler problems
    """
    
    def __init__(self, config: AdapterConfig = None):
        self.config = config or AdapterConfig()
    
    def optimize_batch_speculation_lengths(self, 
                                         predicted_sls: List[int],
                                         sequence_priorities: List[float] = None) -> Tuple[List[int], int]:
        """
        Optimize speculation lengths for a batch to minimize straggler effects
        
        Args:
            predicted_sls: Individual predicted speculation lengths
            sequence_priorities: Optional priority weights for sequences
            
        Returns:
            Tuple of (optimized_sls, sl_cap)
        """
        if not predicted_sls:
            return [], 0
        
        # Calculate adaptive SL cap using MSE minimization (from paper)
        sl_cap = self._calculate_adaptive_sl_cap(predicted_sls, sequence_priorities)
        
        # Apply cap to all predictions
        optimized_sls = [min(sl, sl_cap) for sl in predicted_sls]
        
        # Additional batch-level optimizations
        optimized_sls = self._apply_batch_balancing(optimized_sls)
        
        return optimized_sls, sl_cap
    
    def _calculate_adaptive_sl_cap(self, predicted_sls: List[int], priorities: List[float] = None) -> int:
        """
        Calculate adaptive speculation length cap using MSE minimization
        Based on equation (11) from the DSDE paper
        """
        if not predicted_sls:
            return self.config.default_speculation_length
        
        if priorities is None:
            # Simple arithmetic mean (equation 11 from paper)
            sl_cap = sum(predicted_sls) / len(predicted_sls)
        else:
            # Weighted mean considering priorities
            weighted_sum = sum(sl * priority for sl, priority in zip(predicted_sls, priorities))
            total_weight = sum(priorities)
            sl_cap = weighted_sum / max(total_weight, 1e-8)
        
        # Round to nearest integer and clamp to valid range
        sl_cap = max(self.config.min_speculation_length,
                    min(self.config.max_speculation_length, round(sl_cap)))
        
        return int(sl_cap)
    
    def _apply_batch_balancing(self, speculation_lengths: List[int]) -> List[int]:
        """
        Apply additional batch-level balancing to reduce variance
        """
        if not speculation_lengths:
            return speculation_lengths
        
        # Calculate statistics
        mean_sl = np.mean(speculation_lengths)
        std_sl = np.std(speculation_lengths)
        
        # If variance is too high, apply smoothing
        if std_sl > mean_sl * 0.5:  # High variance threshold
            # Smooth extreme values towards the mean
            balanced_sls = []
            for sl in speculation_lengths:
                if abs(sl - mean_sl) > self.config.straggler_tolerance * std_sl:
                    # Pull extreme values towards mean
                    balanced_sl = sl + 0.3 * (mean_sl - sl)
                    balanced_sls.append(max(1, min(self.config.max_speculation_length, round(balanced_sl))))
                else:
                    balanced_sls.append(sl)
            
            return balanced_sls
        
        return speculation_lengths
    
    def analyze_batch_efficiency(self, 
                                speculation_lengths: List[int],
                                processing_times: List[float] = None) -> Dict:
        """
        Analyze batch processing efficiency
        
        Args:
            speculation_lengths: Speculation lengths used
            processing_times: Optional processing times per sequence
            
        Returns:
            Efficiency analysis dictionary
        """
        if not speculation_lengths:
            return {}
        
        analysis = {
            'batch_size': len(speculation_lengths),
            'mean_sl': np.mean(speculation_lengths),
            'std_sl': np.std(speculation_lengths),
            'min_sl': min(speculation_lengths),
            'max_sl': max(speculation_lengths),
            'sl_range': max(speculation_lengths) - min(speculation_lengths),
            'coefficient_of_variation': np.std(speculation_lengths) / max(np.mean(speculation_lengths), 1e-8)
        }
        
        # Identify potential stragglers
        mean_sl = analysis['mean_sl']
        std_sl = analysis['std_sl']
        straggler_threshold = mean_sl + self.config.straggler_tolerance * std_sl
        
        stragglers = [i for i, sl in enumerate(speculation_lengths) if sl > straggler_threshold]
        analysis['straggler_indices'] = stragglers
        analysis['straggler_count'] = len(stragglers)
        analysis['straggler_percentage'] = len(stragglers) / len(speculation_lengths) * 100
        
        # Processing time analysis if available
        if processing_times and len(processing_times) == len(speculation_lengths):
            analysis['processing_times'] = {
                'mean_time': np.mean(processing_times),
                'std_time': np.std(processing_times),
                'max_time': max(processing_times),
                'min_time': min(processing_times),
                'time_efficiency': min(processing_times) / max(processing_times) if max(processing_times) > 0 else 1.0
            }
        
        return analysis

