"""
Dynamic Speculative Decoding Engine (DSDE)
A training-free framework for dynamic speculation length adaptation in LLM inference
"""

from .core import DSDecoder, DSDecodeConfig
from .signals import KLDVarianceSignal, WVIRCalculator, SignalConfig
from .adapter import SpeculationLengthAdapter, AdapterConfig
from .utils import PerformanceMetrics, BatchOptimizer, DynamicScheduler

__version__ = "1.0.0"
__all__ = [
    "DSDecoder",
    "DSDecodeConfig",
    "KLDVarianceSignal", 
    "WVIRCalculator",
    "SignalConfig",
    "SpeculationLengthAdapter",
    "AdapterConfig",
    "DynamicScheduler",
    "PerformanceMetrics",
    "BatchOptimizer"
]

