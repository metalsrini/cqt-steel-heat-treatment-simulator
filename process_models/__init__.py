"""
Process Models Module
Implementation of individual C-Q-T process models
"""

# Core process model imports
try:
    from .carburizing import *
except ImportError:
    pass

try:
    from .quenching import *
except ImportError:
    pass

try:
    from .tempering import *
except ImportError:
    pass

# Module metadata
__version__ = "1.0.0"
__author__ = "C-Q-T Framework Development Team"
__description__ = "Individual process models for carburizing, quenching, and tempering"

# Available process models
__all__ = [
    'CarburizingProcess',
    'QuenchingProcess', 
    'TemperingProcess',
    'ProcessModelBase',
]

# Process model registry
PROCESS_REGISTRY = {}

def register_process_model(name: str, model_class):
    """Register a process model for dynamic access"""
    PROCESS_REGISTRY[name] = model_class

def get_process_model(name: str):
    """Get a process model by name"""
    return PROCESS_REGISTRY.get(name)

def list_available_processes():
    """List all registered process models"""
    return list(PROCESS_REGISTRY.keys())