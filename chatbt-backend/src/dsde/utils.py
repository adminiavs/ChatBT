"""
DSDE Utility Classes and Data Structures
Supporting classes for performance monitoring, metrics, and data structures
"""

import time
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from collections import deque, defaultdict
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class DSDecodeResult:
    """Result from a DSDE decoding operation"""
    sequence_id: str
    generated_text: str
    tokens_generated: int
    tokens_accepted: int
    speculation_rounds: int
    total_time: float
    average_sl: float
    final_metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def acceptance_rate(self) -> float:
        """Calculate overall acceptance rate"""
        return self.tokens_accepted / max(self.tokens_generated, 1)
    
    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second"""
        return self.tokens_generated / max(self.total_time, 0.001)
    
    @property
    def speedup_estimate(self) -> float:
        """Estimate speedup compared to autoregressive decoding"""
        # Simplified speedup calculation
        theoretical_time = self.tokens_generated * 0.1  # Assume 0.1s per token
        return theoretical_time / max(self.total_time, 0.001)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'sequence_id': self.sequence_id,
            'generated_text': self.generated_text,
            'tokens_generated': self.tokens_generated,
            'tokens_accepted': self.tokens_accepted,
            'speculation_rounds': self.speculation_rounds,
            'total_time': self.total_time,
            'average_sl': self.average_sl,
            'acceptance_rate': self.acceptance_rate,
            'tokens_per_second': self.tokens_per_second,
            'speedup_estimate': self.speedup_estimate,
            'final_metrics': self.final_metrics
        }

@dataclass
class SpeculationRoundMetrics:
    """Metrics for a single speculation round"""
    round_id: int
    sequence_count: int
    speculation_lengths: List[int]
    accepted_tokens: List[int]
    processing_time: float
    timestamp: float = field(default_factory=time.time)
    
    @property
    def average_sl(self) -> float:
        """Average speculation length for this round"""
        return np.mean(self.speculation_lengths) if self.speculation_lengths else 0.0
    
    @property
    def average_acceptance_rate(self) -> float:
        """Average acceptance rate for this round"""
        if not self.speculation_lengths or not self.accepted_tokens:
            return 0.0
        
        total_speculated = sum(self.speculation_lengths)
        total_accepted = sum(self.accepted_tokens)
        return total_accepted / max(total_speculated, 1)
    
    @property
    def throughput(self) -> float:
        """Tokens per second throughput"""
        total_tokens = sum(self.accepted_tokens)
        return total_tokens / max(self.processing_time, 0.001)

class PerformanceMetrics:
    """
    Comprehensive performance monitoring for DSDE
    """
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        
        # Round-level metrics
        self.round_metrics = deque(maxlen=history_size)
        self.round_counter = 0
        
        # Sequence-level tracking
        self.sequence_metrics = defaultdict(lambda: {
            'start_time': time.time(),
            'rounds': [],
            'total_tokens_generated': 0,
            'total_tokens_accepted': 0,
            'total_processing_time': 0.0
        })
        
        # System-level metrics
        self.system_metrics = {
            'start_time': time.time(),
            'total_rounds': 0,
            'total_sequences': 0,
            'total_tokens_generated': 0,
            'total_tokens_accepted': 0,
            'total_processing_time': 0.0
        }
        
        # Performance windows for trend analysis
        self.recent_throughput = deque(maxlen=50)
        self.recent_acceptance_rates = deque(maxlen=50)
        self.recent_speculation_lengths = deque(maxlen=50)
    
    def update_round_metrics(self, 
                           sequence_count: int,
                           processing_time: float,
                           speculation_lengths: List[int] = None,
                           accepted_tokens: List[int] = None):
        """Update metrics after a speculation round"""
        
        self.round_counter += 1
        
        # Create round metrics
        round_metrics = SpeculationRoundMetrics(
            round_id=self.round_counter,
            sequence_count=sequence_count,
            speculation_lengths=speculation_lengths or [],
            accepted_tokens=accepted_tokens or [],
            processing_time=processing_time
        )
        
        self.round_metrics.append(round_metrics)
        
        # Update system metrics
        self.system_metrics['total_rounds'] += 1
        self.system_metrics['total_processing_time'] += processing_time
        
        if speculation_lengths:
            self.system_metrics['total_tokens_generated'] += sum(speculation_lengths)
            self.recent_speculation_lengths.extend(speculation_lengths)
        
        if accepted_tokens:
            self.system_metrics['total_tokens_accepted'] += sum(accepted_tokens)
        
        # Update recent performance windows
        if round_metrics.throughput > 0:
            self.recent_throughput.append(round_metrics.throughput)
        
        if round_metrics.average_acceptance_rate > 0:
            self.recent_acceptance_rates.append(round_metrics.average_acceptance_rate)
    
    def update_sequence_metrics(self, 
                              sequence_id: str,
                              tokens_generated: int,
                              tokens_accepted: int,
                              processing_time: float,
                              is_complete: bool = False):
        """Update metrics for a specific sequence"""
        
        metrics = self.sequence_metrics[sequence_id]
        metrics['total_tokens_generated'] += tokens_generated
        metrics['total_tokens_accepted'] += tokens_accepted
        metrics['total_processing_time'] += processing_time
        
        if is_complete:
            metrics['end_time'] = time.time()
            metrics['total_time'] = metrics['end_time'] - metrics['start_time']
            self.system_metrics['total_sequences'] += 1
    
    def get_current_performance(self) -> Dict[str, Any]:
        """Get current performance snapshot"""
        current_time = time.time()
        uptime = current_time - self.system_metrics['start_time']
        
        # Calculate rates
        tokens_per_second = self.system_metrics['total_tokens_generated'] / max(uptime, 1)
        rounds_per_second = self.system_metrics['total_rounds'] / max(uptime, 1)
        
        # Calculate recent averages
        recent_throughput_avg = np.mean(self.recent_throughput) if self.recent_throughput else 0.0
        recent_acceptance_avg = np.mean(self.recent_acceptance_rates) if self.recent_acceptance_rates else 0.0
        recent_sl_avg = np.mean(self.recent_speculation_lengths) if self.recent_speculation_lengths else 0.0
        
        # Overall acceptance rate
        overall_acceptance_rate = (
            self.system_metrics['total_tokens_accepted'] / 
            max(self.system_metrics['total_tokens_generated'], 1)
        )
        
        return {
            'uptime_seconds': uptime,
            'total_rounds': self.system_metrics['total_rounds'],
            'total_sequences': self.system_metrics['total_sequences'],
            'total_tokens_generated': self.system_metrics['total_tokens_generated'],
            'total_tokens_accepted': self.system_metrics['total_tokens_accepted'],
            'overall_acceptance_rate': overall_acceptance_rate,
            'tokens_per_second': tokens_per_second,
            'rounds_per_second': rounds_per_second,
            'recent_metrics': {
                'throughput': recent_throughput_avg,
                'acceptance_rate': recent_acceptance_avg,
                'average_speculation_length': recent_sl_avg
            },
            'active_sequences': len([s for s in self.sequence_metrics.values() if 'end_time' not in s])
        }
    
    def get_performance_trends(self, window_size: int = 20) -> Dict[str, Any]:
        """Analyze performance trends over recent history"""
        if len(self.round_metrics) < window_size:
            return {'insufficient_data': True}
        
        recent_rounds = list(self.round_metrics)[-window_size:]
        
        # Extract trend data
        throughputs = [r.throughput for r in recent_rounds if r.throughput > 0]
        acceptance_rates = [r.average_acceptance_rate for r in recent_rounds if r.average_acceptance_rate > 0]
        processing_times = [r.processing_time for r in recent_rounds]
        speculation_lengths = []
        for r in recent_rounds:
            speculation_lengths.extend(r.speculation_lengths)
        
        trends = {}
        
        # Throughput trend
        if len(throughputs) >= 2:
            throughput_trend = np.polyfit(range(len(throughputs)), throughputs, 1)[0]
            trends['throughput_trend'] = 'increasing' if throughput_trend > 0 else 'decreasing'
            trends['throughput_slope'] = throughput_trend
        
        # Acceptance rate trend
        if len(acceptance_rates) >= 2:
            acceptance_trend = np.polyfit(range(len(acceptance_rates)), acceptance_rates, 1)[0]
            trends['acceptance_rate_trend'] = 'increasing' if acceptance_trend > 0 else 'decreasing'
            trends['acceptance_rate_slope'] = acceptance_trend
        
        # Processing time trend
        if len(processing_times) >= 2:
            time_trend = np.polyfit(range(len(processing_times)), processing_times, 1)[0]
            trends['processing_time_trend'] = 'increasing' if time_trend > 0 else 'decreasing'
            trends['processing_time_slope'] = time_trend
        
        # Statistics
        trends['statistics'] = {
            'throughput': {
                'mean': np.mean(throughputs) if throughputs else 0,
                'std': np.std(throughputs) if throughputs else 0,
                'min': min(throughputs) if throughputs else 0,
                'max': max(throughputs) if throughputs else 0
            },
            'acceptance_rate': {
                'mean': np.mean(acceptance_rates) if acceptance_rates else 0,
                'std': np.std(acceptance_rates) if acceptance_rates else 0,
                'min': min(acceptance_rates) if acceptance_rates else 0,
                'max': max(acceptance_rates) if acceptance_rates else 0
            },
            'speculation_length': {
                'mean': np.mean(speculation_lengths) if speculation_lengths else 0,
                'std': np.std(speculation_lengths) if speculation_lengths else 0,
                'min': min(speculation_lengths) if speculation_lengths else 0,
                'max': max(speculation_lengths) if speculation_lengths else 0
            }
        }
        
        return trends
    
    def export_metrics(self, filepath: str = None) -> Dict[str, Any]:
        """Export all metrics to dictionary/file"""
        export_data = {
            'timestamp': time.time(),
            'system_metrics': self.system_metrics.copy(),
            'current_performance': self.get_current_performance(),
            'performance_trends': self.get_performance_trends(),
            'round_history': [
                {
                    'round_id': r.round_id,
                    'sequence_count': r.sequence_count,
                    'average_sl': r.average_sl,
                    'average_acceptance_rate': r.average_acceptance_rate,
                    'throughput': r.throughput,
                    'processing_time': r.processing_time,
                    'timestamp': r.timestamp
                }
                for r in list(self.round_metrics)[-100:]  # Last 100 rounds
            ],
            'sequence_summary': {
                seq_id: {
                    'total_tokens_generated': metrics['total_tokens_generated'],
                    'total_tokens_accepted': metrics['total_tokens_accepted'],
                    'total_processing_time': metrics['total_processing_time'],
                    'acceptance_rate': metrics['total_tokens_accepted'] / max(metrics['total_tokens_generated'], 1),
                    'is_complete': 'end_time' in metrics
                }
                for seq_id, metrics in self.sequence_metrics.items()
            }
        }
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                logger.info(f"Metrics exported to {filepath}")
            except Exception as e:
                logger.error(f"Failed to export metrics to {filepath}: {e}")
        
        return export_data
    
    def reset(self):
        """Reset all metrics"""
        self.round_metrics.clear()
        self.round_counter = 0
        self.sequence_metrics.clear()
        self.recent_throughput.clear()
        self.recent_acceptance_rates.clear()
        self.recent_speculation_lengths.clear()
        
        self.system_metrics = {
            'start_time': time.time(),
            'total_rounds': 0,
            'total_sequences': 0,
            'total_tokens_generated': 0,
            'total_tokens_accepted': 0,
            'total_processing_time': 0.0
        }
        
        logger.info("Performance metrics reset")

class BatchOptimizer:
    """
    Batch optimization utilities for DSDE
    Handles straggler mitigation and batch-level optimizations
    """
    
    def __init__(self, straggler_threshold: float = 2.0):
        self.straggler_threshold = straggler_threshold
        self.batch_history = deque(maxlen=100)
    
    def optimize_batch_speculation_lengths(self, 
                                         predicted_sls: List[int],
                                         priorities: List[float] = None) -> Tuple[List[int], int]:
        """
        Optimize speculation lengths for batch processing
        
        Args:
            predicted_sls: Individual predicted speculation lengths
            priorities: Optional priority weights
            
        Returns:
            Tuple of (optimized_sls, sl_cap)
        """
        if not predicted_sls:
            return [], 0
        
        # Calculate SL cap using MSE minimization (DSDE paper equation 11)
        if priorities:
            weighted_sum = sum(sl * p for sl, p in zip(predicted_sls, priorities))
            total_weight = sum(priorities)
            sl_cap = weighted_sum / max(total_weight, 1e-8)
        else:
            sl_cap = sum(predicted_sls) / len(predicted_sls)
        
        sl_cap = max(1, min(8, round(sl_cap)))
        
        # Apply cap and additional optimizations
        optimized_sls = [min(sl, sl_cap) for sl in predicted_sls]
        
        # Record batch metrics
        self.batch_history.append({
            'original_sls': predicted_sls.copy(),
            'optimized_sls': optimized_sls.copy(),
            'sl_cap': sl_cap,
            'variance_reduction': np.var(predicted_sls) - np.var(optimized_sls),
            'timestamp': time.time()
        })
        
        return optimized_sls, sl_cap
    
    def analyze_batch_efficiency(self, batch_metrics: Dict) -> Dict[str, Any]:
        """Analyze batch processing efficiency"""
        if not self.batch_history:
            return {'no_data': True}
        
        recent_batches = list(self.batch_history)[-20:]  # Last 20 batches
        
        analysis = {
            'average_sl_cap': np.mean([b['sl_cap'] for b in recent_batches]),
            'average_variance_reduction': np.mean([b['variance_reduction'] for b in recent_batches]),
            'optimization_effectiveness': sum(1 for b in recent_batches if b['variance_reduction'] > 0) / len(recent_batches),
            'batch_count': len(recent_batches)
        }
        
        return analysis

class DynamicScheduler:
    """
    Dynamic scheduler for DSDE operations
    Handles sequence scheduling and resource allocation
    """
    
    def __init__(self):
        self.active_sequences = {}
        self.sequence_priorities = {}
        self.resource_allocation = {}
    
    def schedule_sequences(self, 
                          sequences: List[Dict],
                          resource_constraints: Dict = None) -> List[Dict]:
        """
        Schedule sequences for processing based on priorities and constraints
        
        Args:
            sequences: List of sequences to schedule
            resource_constraints: Optional resource constraints
            
        Returns:
            Scheduled sequences in optimal order
        """
        # Simple priority-based scheduling
        # In a real implementation, this would be more sophisticated
        
        # Assign priorities based on sequence characteristics
        for seq in sequences:
            seq_id = seq['id']
            priority = self._calculate_priority(seq)
            self.sequence_priorities[seq_id] = priority
        
        # Sort by priority (higher priority first)
        scheduled = sorted(sequences, 
                         key=lambda s: self.sequence_priorities.get(s['id'], 0.5), 
                         reverse=True)
        
        return scheduled
    
    def _calculate_priority(self, sequence: Dict) -> float:
        """Calculate priority for a sequence"""
        # Simple priority calculation based on sequence characteristics
        priority = 0.5  # Base priority
        
        # Adjust based on sequence length
        prompt_length = len(sequence.get('prompt', ''))
        if prompt_length < 100:
            priority += 0.1  # Short sequences get slight priority
        elif prompt_length > 1000:
            priority -= 0.1  # Very long sequences get lower priority
        
        # Adjust based on max_tokens
        max_tokens = sequence.get('max_tokens', 100)
        if max_tokens < 50:
            priority += 0.1  # Short generation gets priority
        elif max_tokens > 500:
            priority -= 0.1  # Long generation gets lower priority
        
        return max(0.0, min(1.0, priority))
    
    def update_sequence_status(self, sequence_id: str, status: str, metrics: Dict = None):
        """Update status of a sequence"""
        self.active_sequences[sequence_id] = {
            'status': status,
            'last_update': time.time(),
            'metrics': metrics or {}
        }
    
    def get_scheduling_stats(self) -> Dict[str, Any]:
        """Get scheduling statistics"""
        return {
            'active_sequences': len(self.active_sequences),
            'average_priority': np.mean(list(self.sequence_priorities.values())) if self.sequence_priorities else 0.0,
            'priority_distribution': {
                'high': sum(1 for p in self.sequence_priorities.values() if p > 0.7),
                'medium': sum(1 for p in self.sequence_priorities.values() if 0.3 <= p <= 0.7),
                'low': sum(1 for p in self.sequence_priorities.values() if p < 0.3)
            }
        }

