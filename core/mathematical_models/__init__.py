"""
Mathematical models module
Implementation of all equations from the research paper:
"Integrated Modeling of Carburizing-Quenching-Tempering of Steel Gears for an ICME Framework"
"""

# Core mathematical model classes
try:
    from .phase_transformation import PhaseTransformationModels, SteelComposition
except ImportError:
    PhaseTransformationModels = None
    SteelComposition = None

try:
    from .thermal_models import ThermalModels, ThermalProperties, HeatTreatmentCycle
except ImportError:
    ThermalModels = None
    ThermalProperties = None
    HeatTreatmentCycle = None

try:
    from .carbon_diffusion import CarbonDiffusionModels
except ImportError:
    CarbonDiffusionModels = None

try:
    from .grain_growth import GrainGrowthModels
except ImportError:
    GrainGrowthModels = None

try:
    from .hardness_prediction import HardnessPredictionModels
except ImportError:
    HardnessPredictionModels = None

# Module metadata
__version__ = "1.0.0"
__author__ = "C-Q-T Framework Development Team"
__description__ = "Mathematical models for integrated C-Q-T process simulation"

# List of all available models
__all__ = [
    'PhaseTransformationModels',
    'SteelComposition', 
    'ThermalModels',
    'ThermalProperties',
    'HeatTreatmentCycle',
    'CarbonDiffusionModels',
    'GrainGrowthModels',
    'HardnessPredictionModels',
]

# Model registry for dynamic access
MODEL_REGISTRY = {
    'phase_transformation': PhaseTransformationModels,
    'thermal': ThermalModels,
    'carbon_diffusion': CarbonDiffusionModels,
    'grain_growth': GrainGrowthModels,
    'hardness_prediction': HardnessPredictionModels,
}

def get_model(model_name: str):
    """
    Get a model class by name from the registry
    
    Args:
        model_name: Name of the model to retrieve
        
    Returns:
        Model class if available, None otherwise
    """
    return MODEL_REGISTRY.get(model_name)

def list_available_models():
    """
    List all available mathematical models
    
    Returns:
        List of available model names
    """
    return [name for name, model in MODEL_REGISTRY.items() if model is not None]