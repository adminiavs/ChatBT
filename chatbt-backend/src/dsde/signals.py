"""
DSDE Signal Processing Module
Implements KLD-based stability signals and WVIR (Windowed Variance in Regional) calculations
"""

import numpy as np
import torch
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple, Union
from collections import deque
import logging
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)

@dataclass
class SignalConfig:
    """Configuration for DSDE signals"""
    short_window_size: int = 4
    long_window_size: int = 12
    min_history_length: int = 2
    kld_threshold: float = 0.1
    variance_threshold: float = 0.05
    entropy_weight: float = 0.3
    kld_weight: float = 0.7

class KLDVarianceSignal:
    """
    Kullback-Leibler Divergence variance signal for regional stability detection
    Based on the DSDE paper's methodology for measuring model disagreement
    """
    
    def __init__(self, config: SignalConfig = None):
        self.config = config or SignalConfig()
        self.kld_history = deque(maxlen=self.config.long_window_size)
        self.sequence_histories = {}
        
    def compute_kld(self, draft_logits: torch.Tensor, target_logits: torch.Tensor) -> float:
        """
        Compute KL divergence between draft and target model distributions
        
        Args:
            draft_logits: Draft model logits [vocab_size]
            target_logits: Target model logits [vocab_size]
            
        Returns:
            KL divergence value
        """
        try:
            # Convert to probabilities
            draft_probs = F.softmax(draft_logits, dim=-1)
            target_probs = F.softmax(target_logits, dim=-1)
            
            # Compute KL divergence: KL(P||Q) = sum(P * log(P/Q))
            kld = F.kl_div(
                target_probs.log(), 
                draft_probs, 
                reduction='sum',
                log_target=False
            ).item()
            
            return max(0.0, kld)  # Ensure non-negative
            
        except Exception as e:
            logger.warning(f"KLD computation failed: {e}")
            return 0.0
    
    def update_history(self, sequence_id: str, kld_values: List[float]):
        """
        Update KLD history for a specific sequence
        
        Args:
            sequence_id: Unique sequence identifier
            kld_values: List of KLD values from current verification step
        """
        if sequence_id not in self.sequence_histories:
            self.sequence_histories[sequence_id] = deque(maxlen=self.config.long_window_size)
        
        # Add all KLD values from this verification step
        for kld_val in kld_values:
            self.sequence_histories[sequence_id].append(kld_val)
    
    def get_regional_stability(self, sequence_id: str) -> float:
        """
        Calculate regional stability based on KLD variance
        
        Args:
            sequence_id: Sequence to analyze
            
        Returns:
            Stability score (higher = more stable)
        """
        if sequence_id not in self.sequence_histories:
            return 0.5  # Neutral stability for new sequences
        
        history = list(self.sequence_histories[sequence_id])
        
        if len(history) < self.config.min_history_length:
            return 0.5
        
        # Calculate variance of recent KLD values
        recent_klds = history[-self.config.short_window_size:]
        if len(recent_klds) < 2:
            return 0.5
        
        variance = np.var(recent_klds)
        
        # Convert variance to stability score (inverse relationship)
        # Lower variance = higher stability
        stability = 1.0 / (1.0 + variance)
        
        return min(1.0, max(0.0, stability))
    
    def predict_acceptance_likelihood(self, sequence_id: str, draft_entropy: float = None) -> float:
        """
        Predict likelihood of token acceptance based on stability signals
        
        Args:
            sequence_id: Sequence identifier
            draft_entropy: Optional entropy from draft model
            
        Returns:
            Acceptance likelihood [0, 1]
        """
        stability = self.get_regional_stability(sequence_id)
        
        # Base prediction on stability
        base_likelihood = stability
        
        # Incorporate entropy if available (lower entropy = higher likelihood)
        if draft_entropy is not None:
            entropy_factor = 1.0 / (1.0 + draft_entropy)
            combined_likelihood = (
                self.config.kld_weight * base_likelihood + 
                self.config.entropy_weight * entropy_factor
            )
        else:
            combined_likelihood = base_likelihood
        
        return min(1.0, max(0.0, combined_likelihood))

class WVIRCalculator:
    """
    Windowed Variance in Regional (WVIR) calculator
    Implements the DSDE paper's approach to measuring regional variance
    """
    
    def __init__(self, config: SignalConfig = None):
        self.config = config or SignalConfig()
        
    def calculate_wvir(self, kld_history: List[float]) -> float:
        """
        Calculate WVIR (Windowed Variance in Regional) signal
        
        Args:
            kld_history: Historical KLD values
            
        Returns:
            WVIR value indicating regional variance
        """
        if len(kld_history) < self.config.short_window_size:
            return 0.0
        
        # Get short and long windows
        short_window = kld_history[-self.config.short_window_size:]
        long_window = kld_history[-self.config.long_window_size:] if len(kld_history) >= self.config.long_window_size else kld_history
        
        # Calculate variances
        short_var = np.var(short_window) if len(short_window) > 1 else 0.0
        long_var = np.var(long_window) if len(long_window) > 1 else 0.0
        
        # WVIR is the ratio of short-term to long-term variance
        if long_var == 0:
            return 1.0 if short_var > 0 else 0.0
        
        wvir = short_var / long_var
        return min(10.0, max(0.0, wvir))  # Clamp to reasonable range
    
    def get_stability_classification(self, wvir: float) -> str:
        """
        Classify stability based on WVIR value
        
        Args:
            wvir: WVIR value
            
        Returns:
            Stability classification string
        """
        if wvir < 0.5:
            return "highly_stable"
        elif wvir < 1.0:
            return "stable"
        elif wvir < 2.0:
            return "moderate"
        elif wvir < 4.0:
            return "unstable"
        else:
            return "highly_unstable"

class EntropySignal:
    """
    Forward-looking entropy signal from draft model
    Complementary to KLD-based signals
    """
    
    def __init__(self):
        self.entropy_history = {}
    
    def compute_entropy(self, logits: torch.Tensor) -> float:
        """
        Compute entropy of draft model distribution
        
        Args:
            logits: Model logits [vocab_size]
            
        Returns:
            Entropy value
        """
        try:
            probs = F.softmax(logits, dim=-1)
            entropy = -torch.sum(probs * torch.log(probs + 1e-10)).item()
            return max(0.0, entropy)
        except Exception as e:
            logger.warning(f"Entropy computation failed: {e}")
            return 0.0
    
    def update_history(self, sequence_id: str, entropy: float):
        """Update entropy history for sequence"""
        if sequence_id not in self.entropy_history:
            self.entropy_history[sequence_id] = deque(maxlen=10)
        self.entropy_history[sequence_id].append(entropy)
    
    def get_trend(self, sequence_id: str) -> str:
        """
        Get entropy trend for sequence
        
        Returns:
            "increasing", "decreasing", or "stable"
        """
        if sequence_id not in self.entropy_history or len(self.entropy_history[sequence_id]) < 3:
            return "stable"
        
        recent = list(self.entropy_history[sequence_id])[-3:]
        
        if recent[-1] > recent[0] * 1.1:
            return "increasing"
        elif recent[-1] < recent[0] * 0.9:
            return "decreasing"
        else:
            return "stable"

class CombinedSignalProcessor:
    """
    Combines multiple signals for robust speculation length prediction
    """
    
    def __init__(self, config: SignalConfig = None):
        self.config = config or SignalConfig()
        self.kld_signal = KLDVarianceSignal(config)
        self.wvir_calculator = WVIRCalculator(config)
        self.entropy_signal = EntropySignal()
    
    def process_verification_step(self, 
                                sequence_id: str,
                                draft_logits: List[torch.Tensor],
                                target_logits: List[torch.Tensor],
                                accepted_tokens: int) -> Dict[str, float]:
        """
        Process a complete verification step and update all signals
        
        Args:
            sequence_id: Unique sequence identifier
            draft_logits: List of draft model logits for each speculated token
            target_logits: List of target model logits for each speculated token
            accepted_tokens: Number of tokens actually accepted
            
        Returns:
            Dictionary of computed signals and metrics
        """
        results = {}
        
        # Compute KLD values for each token position
        kld_values = []
        for i in range(min(len(draft_logits), len(target_logits))):
            kld = self.kld_signal.compute_kld(draft_logits[i], target_logits[i])
            kld_values.append(kld)
        
        # Update KLD history
        self.kld_signal.update_history(sequence_id, kld_values)
        
        # Calculate regional stability
        stability = self.kld_signal.get_regional_stability(sequence_id)
        results['stability'] = stability
        
        # Calculate WVIR if we have enough history
        if sequence_id in self.kld_signal.sequence_histories:
            history = list(self.kld_signal.sequence_histories[sequence_id])
            wvir = self.wvir_calculator.calculate_wvir(history)
            results['wvir'] = wvir
            results['stability_class'] = self.wvir_calculator.get_stability_classification(wvir)
        
        # Process entropy signals
        if draft_logits:
            entropy = self.entropy_signal.compute_entropy(draft_logits[0])
            self.entropy_signal.update_history(sequence_id, entropy)
            results['entropy'] = entropy
            results['entropy_trend'] = self.entropy_signal.get_trend(sequence_id)
        
        # Calculate acceptance rate
        if len(draft_logits) > 0:
            acceptance_rate = accepted_tokens / len(draft_logits)
            results['acceptance_rate'] = acceptance_rate
        
        # Predict next step acceptance likelihood
        next_likelihood = self.kld_signal.predict_acceptance_likelihood(
            sequence_id, 
            results.get('entropy')
        )
        results['next_acceptance_likelihood'] = next_likelihood
        
        return results
    
    def get_sequence_metrics(self, sequence_id: str) -> Dict[str, float]:
        """Get current metrics for a sequence"""
        metrics = {}
        
        # Stability metrics
        metrics['stability'] = self.kld_signal.get_regional_stability(sequence_id)
        
        # WVIR metrics
        if sequence_id in self.kld_signal.sequence_histories:
            history = list(self.kld_signal.sequence_histories[sequence_id])
            if history:
                metrics['wvir'] = self.wvir_calculator.calculate_wvir(history)
                metrics['mean_kld'] = np.mean(history[-5:]) if len(history) >= 5 else np.mean(history)
        
        # Entropy metrics
        if sequence_id in self.entropy_signal.entropy_history:
            recent_entropy = list(self.entropy_signal.entropy_history[sequence_id])
            if recent_entropy:
                metrics['current_entropy'] = recent_entropy[-1]
                metrics['entropy_trend'] = self.entropy_signal.get_trend(sequence_id)
        
        return metrics

