"""
Core module for C-Q-T modeling framework
Contains all fundamental mathematical models and algorithms
"""

from .mathematical_models import *

__version__ = "1.0.0"
__author__ = "C-Q-T Framework Team"
__description__ = "Integrated Computational Materials Engineering Framework for Steel Gear Manufacturing"

# Core module components will be imported as they are implemented
try:
    from .material_properties import *
except ImportError:
    pass

try:
    from .fem_solver import *
except ImportError:
    pass

try:
    from .validation import *
except ImportError:
    pass

__all__ = [
    # Mathematical models
    'PhaseTransformationModels',
    'SteelComposition', 
    'ThermalModels',
    'ThermalProperties',
    'HeatTreatmentCycle',
    'CarbonDiffusionModels',
    'GrainGrowthModels',
    'HardnessPredictionModels',
]