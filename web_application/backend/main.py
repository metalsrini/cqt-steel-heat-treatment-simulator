#!/usr/bin/env python3
"""
Professional FastAPI Backend for C-Q-T Modeling Framework
Fully Real Physics-Based Heat Treatment Simulation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
import numpy as np
import uvicorn
import logging
import asyncio
from datetime import datetime
import uuid
import sys
import os
import math
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import C-Q-T framework components
from core.mathematical_models.phase_transformation import (
    PhaseTransformationModels, SteelComposition, STEEL_COMPOSITIONS
)
from core.mathematical_models.carbon_diffusion import CarbonDiffusionModels
from core.mathematical_models.grain_growth import GrainGrowthModels
from core.mathematical_models.hardness_prediction import HardnessPredictionModels
from core.mathematical_models.thermal_models import ThermalModels, QuenchingMedia
from case_depth_integration import IntegratedCaseDepthModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="C-Q-T Steel Heat Treatment Simulator",
    description="Professional web application for integrated carburizing-quenching-tempering process simulation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://127.0.0.1:3000"
]

# Add production origins from environment
production_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if production_origins and production_origins[0]:
    allowed_origins.extend([origin.strip() for origin in production_origins])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================================================
# PYDANTIC MODELS
# ================================================================================================

class SteelCompositionInput(BaseModel):
    grade: Optional[str] = Field(None, description="Steel grade designation")
    C: float = Field(..., ge=0.01, le=2.0, description="Carbon content (wt%)")
    Si: float = Field(..., ge=0.0, le=2.0, description="Silicon content (wt%)")
    Mn: float = Field(..., ge=0.0, le=3.0, description="Manganese content (wt%)")
    Ni: float = Field(..., ge=0.0, le=5.0, description="Nickel content (wt%)")
    Cr: float = Field(..., ge=0.0, le=3.0, description="Chromium content (wt%)")
    Mo: float = Field(..., ge=0.0, le=1.0, description="Molybdenum content (wt%)")
    V: float = Field(0.0, ge=0.0, le=0.5, description="Vanadium content (wt%)")
    W: float = Field(0.0, ge=0.0, le=1.0, description="Tungsten content (wt%)")
    Cu: float = Field(0.0, ge=0.0, le=1.0, description="Copper content (wt%)")
    P: float = Field(0.0, ge=0.0, le=0.05, description="Phosphorus content (wt%)")
    Al: float = Field(0.0, ge=0.0, le=0.1, description="Aluminum content (wt%)")
    As: float = Field(0.0, ge=0.0, le=0.05, description="Arsenic content (wt%)")
    Ti: float = Field(0.0, ge=0.0, le=0.1, description="Titanium content (wt%)")

class CarburizingConditions(BaseModel):
    temperature: float = Field(..., ge=850, le=1050, description="Carburizing temperature (°C)")
    time_hours: float = Field(..., ge=0.5, le=24, description="Carburizing time (hours)")
    carbon_potential: float = Field(..., ge=0.7, le=1.3, description="Carbon potential")
    heating_rate: float = Field(5.0, ge=1.0, le=20.0, description="Heating rate (°C/min)")
    atmosphere_type: str = Field("endothermic", description="Atmosphere type")
    gas_flow_rate: float = Field(1.0, ge=0.1, le=5.0, description="Gas flow rate")
    mass_transfer_coefficient: float = Field(1e-4, ge=1e-5, le=5e-4, description="Mass transfer coefficient")

class QuenchingConditions(BaseModel):
    quench_medium: str = Field(..., description="Quenching medium")
    quench_temperature: float = Field(..., ge=20, le=150, description="Quench temperature (°C)")
    agitation_rate: float = Field(1.0, ge=0.1, le=5.0, description="Agitation rate")
    quench_time: float = Field(300, ge=60, le=1800, description="Quench time (seconds)")
    delay_time: float = Field(0, ge=0, le=600, description="Delay time (seconds)")

class TemperingConditions(BaseModel):
    temperature: float = Field(..., ge=100, le=700, description="Tempering temperature (°C)")
    time_hours: float = Field(..., ge=0.5, le=8.0, description="Tempering time (hours)")
    heating_rate: float = Field(2.0, ge=1.0, le=10.0, description="Heating rate (°C/min)")
    cooling_method: str = Field("air", description="Cooling method")
    multiple_tempers: bool = Field(False, description="Multiple tempering cycles")
    temper_cycles: int = Field(1, ge=1, le=3, description="Number of tempering cycles")

class PartGeometry(BaseModel):
    geometry_type: str = Field(..., description="Part geometry type")
    diameter: Optional[float] = Field(None, ge=1, le=500, description="Diameter (mm)")
    characteristic_dimension: float = Field(..., ge=1, le=100, description="Characteristic dimension (mm)")

class InitialConditions(BaseModel):
    initial_grain_size: float = Field(..., ge=5.0, le=200.0, description="Initial grain size (μm)")
    surface_condition: str = Field("machined", description="Surface condition")
    prior_heat_treatment: str = Field("annealed", description="Prior heat treatment")

class SimulationParameters(BaseModel):
    spatial_points: int = Field(51, ge=21, le=201, description="Number of spatial points")
    time_step_carburizing: float = Field(60, ge=1, le=300, description="Carburizing time step (s)")
    time_step_quenching: float = Field(1, ge=0.1, le=10, description="Quenching time step (s)")
    max_analysis_depth: float = Field(5.0, ge=1.0, le=20.0, description="Maximum analysis depth (mm)")
    convergence_tolerance: float = Field(1e-6, ge=1e-8, le=1e-4, description="Convergence tolerance")

class HeatTreatmentRequest(BaseModel):
    steel_composition: SteelCompositionInput
    carburizing: CarburizingConditions
    quenching: QuenchingConditions
    tempering: TemperingConditions
    geometry: PartGeometry
    initial_conditions: InitialConditions
    simulation_params: SimulationParameters
    calculation_id: Optional[str] = Field(None, description="Unique calculation identifier")

class PropertyProfile(BaseModel):
    distance_array: List[float] = Field(..., description="Distance from surface (mm)")
    carbon_profile: List[float] = Field(..., description="Carbon content profile")
    hardness_profile: List[float] = Field(..., description="Hardness profile")

class ThermalProfile(BaseModel):
    time_array: List[float] = Field(..., description="Time array")
    temperature_array: List[float] = Field(..., description="Temperature array")
    time_carburizing: List[float] = Field(..., description="Carburizing time array")
    temperature_carburizing: List[float] = Field(..., description="Carburizing temperature array")
    time_quenching: List[float] = Field(..., description="Quenching time array")
    temperature_quenching: List[float] = Field(..., description="Quenching temperature array")
    cooling_rate: float = Field(..., description="Cooling rate (°C/s)")

class CaseDepthResults(BaseModel):
    case_depth_04_carbon: float = Field(..., description="Case depth at 0.4% carbon (mm)")
    case_depth_03_carbon: float = Field(..., description="Case depth at 0.3% carbon (mm)")
    case_depth_50_hrc: float = Field(..., description="Case depth at 50 HRC (mm)")
    case_depth_55_hrc: float = Field(..., description="Case depth at 55 HRC (mm)")
    effective_case_depth: float = Field(..., description="Effective case depth (mm)")
    surface_carbon: float = Field(..., description="Surface carbon content")

class ProcessMetrics(BaseModel):
    surface_hardness_hrc: float = Field(..., description="Surface hardness (HRC)")
    core_hardness_hrc: float = Field(..., description="Core hardness (HRC)")
    surface_hardness_hv: float = Field(..., description="Surface hardness (HV)")
    core_hardness_hv: float = Field(..., description="Core hardness (HV)")
    surface_carbon: float = Field(..., description="Surface carbon content")
    carbon_gradient: float = Field(..., description="Carbon gradient (%/mm)")
    hardness_gradient: float = Field(..., description="Hardness gradient (HRC/mm)")
    distortion_risk: str = Field(..., description="Distortion risk assessment")
    grain_size_surface: float = Field(..., description="Surface grain size (μm)")
    grain_size_core: float = Field(..., description="Core grain size (μm)")
    carbon_flux_surface: float = Field(..., description="Surface carbon flux")
    effective_diffusivity: float = Field(..., description="Effective diffusivity")
    mass_transfer_effectiveness: float = Field(..., description="Mass transfer effectiveness")

class CriticalTemperatures(BaseModel):
    ae3_temperature: float = Field(..., description="Ae3 temperature (°C)")
    ae1_temperature: float = Field(..., description="Ae1 temperature (°C)")
    ms_temperature_core: float = Field(..., description="Ms temperature - core (°C)")
    ms_temperature_surface: float = Field(..., description="Ms temperature - surface (°C)")

class QualityAssessment(BaseModel):
    meets_specifications: bool = Field(..., description="Meets quality specifications")
    uniformity_index: float = Field(..., description="Case depth uniformity index")
    distortion_risk: str = Field(..., description="Distortion risk assessment")
    recommendations: List[str] = Field(..., description="Process recommendations")

class SimulationResults(BaseModel):
    calculation_id: str = Field(..., description="Unique calculation identifier")
    steel_grade: str = Field(..., description="Steel grade used")
    distance_array: List[float] = Field(..., description="Distance array")
    carbon_profile: List[float] = Field(..., description="Carbon profile")
    hardness_profile: List[float] = Field(..., description="Hardness profile")
    case_depth_results: CaseDepthResults = Field(..., description="Case depth analysis results")
    process_metrics: ProcessMetrics = Field(..., description="Process performance metrics")
    critical_temperatures: CriticalTemperatures = Field(..., description="Critical temperatures")
    thermal_profiles: ThermalProfile = Field(..., description="Thermal history")
    grain_sizes: Dict[str, float] = Field(..., description="Grain size measurements")
    quality_assessment: QualityAssessment = Field(..., description="Quality assessment")
    computation_time: float = Field(..., description="Computation time")
    timestamp: str = Field(..., description="Simulation timestamp")
    validation_status: str = Field(..., description="Validation status")
    property_profiles: Dict[str, List[float]] = Field(..., description="Property profiles")
    phase_fractions: Dict[str, List[float]] = Field(..., description="Phase fractions")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    errors: List[str] = Field(default_factory=list, description="Errors")

class OptimizeProcessRequest(BaseModel):
    target_case_depth: float = Field(..., ge=0.3, le=2.0)
    steel_grade: str
    max_temperature: float = Field(950, ge=900, le=1000)
    max_time: float = Field(12, ge=2, le=24)
    carbon_potential: float = Field(1.0, ge=0.8, le=1.2)

class MaterialComparisonRequest(BaseModel):
    steel_grades: List[str] = Field(..., description="List of steel grades to compare")
    process_conditions: Dict[str, float] = Field(..., description="Process conditions for comparison")

class ProcessRecommendationsRequest(BaseModel):
    steel_grade: str = Field(..., description="Steel grade")
    part_size: float = Field(..., ge=1, le=100, description="Part size in mm")
    application: str = Field("automotive_gear", description="Application type")

class ValidationResponse(BaseModel):
    valid: bool = Field(..., description="Validation status")
    error: Optional[str] = Field(None, description="Error message")
    warnings: List[str] = Field(..., description="Validation warnings")

# ================================================================================================
# GLOBAL VARIABLES AND INITIALIZATION
# ================================================================================================

calculation_cache: Dict[str, SimulationResults] = {}

# Initialize core models
phase_models = PhaseTransformationModels()
carbon_models = CarbonDiffusionModels()
grain_models = GrainGrowthModels()
hardness_models = HardnessPredictionModels()
thermal_models = ThermalModels()

# ================================================================================================
# UTILITY FUNCTIONS
# ================================================================================================

def create_steel_composition(input_data: SteelCompositionInput) -> SteelComposition:
    """Create SteelComposition object from input data"""
    if input_data.grade and input_data.grade.upper() in STEEL_COMPOSITIONS:
        base_steel = STEEL_COMPOSITIONS[input_data.grade.upper()]
        return SteelComposition(
            C=input_data.C if input_data.C != base_steel.C else base_steel.C,
            Si=input_data.Si if input_data.Si != base_steel.Si else base_steel.Si,
            Mn=input_data.Mn if input_data.Mn != base_steel.Mn else base_steel.Mn,
            Ni=input_data.Ni if input_data.Ni != base_steel.Ni else base_steel.Ni,
            Cr=input_data.Cr if input_data.Cr != base_steel.Cr else base_steel.Cr,
            Mo=input_data.Mo if input_data.Mo != base_steel.Mo else base_steel.Mo,
            V=input_data.V, W=input_data.W, Cu=input_data.Cu,
            P=input_data.P, Al=input_data.Al, As=input_data.As, Ti=input_data.Ti
        )
    else:
        return SteelComposition(
            C=input_data.C, Si=input_data.Si, Mn=input_data.Mn,
            Ni=input_data.Ni, Cr=input_data.Cr, Mo=input_data.Mo,
            V=input_data.V, W=input_data.W, Cu=input_data.Cu,
            P=input_data.P, Al=input_data.Al, As=input_data.As, Ti=input_data.Ti
        )

def validate_inputs(request: HeatTreatmentRequest) -> List[str]:
    """Validate simulation inputs and return warnings"""
    warnings = []
    
    if request.carburizing.temperature > 950:
        warnings.append("High carburizing temperature may cause excessive grain growth")
    
    if request.carburizing.time_hours > 12:
        warnings.append("Long carburizing time may lead to distortion")
    
    if request.steel_composition.C > 0.3:
        warnings.append("High carbon content may reduce case/core hardness differential")
    
    return warnings

def assess_quality(results: Dict, request: HeatTreatmentRequest) -> QualityAssessment:
    """Assess quality and provide recommendations based on real analysis"""
    
    # Quality criteria for carburized gears
    target_surface_hrc = (58, 62)
    target_core_hrc = (32, 48)
    target_case_depth = (0.5, 1.0)
    
    surface_hrc = results['surface_hardness_hrc']
    core_hrc = results['core_hardness_hrc']
    case_depth = results['case_depth_50_hrc']
    
    # Check specifications
    surface_ok = target_surface_hrc[0] <= surface_hrc <= target_surface_hrc[1]
    core_ok = target_core_hrc[0] <= core_hrc <= target_core_hrc[1]
    case_depth_ok = target_case_depth[0] <= case_depth <= target_case_depth[1]
    
    meets_specs = surface_ok and core_ok and case_depth_ok
    
    # Calculate uniformity index
    carbon_range = max(results['carbon_profile']) - min(results['carbon_profile'])
    uniformity_index = 1.0 - (carbon_range / max(results['carbon_profile']))
    
    # Assess distortion risk
    if request.carburizing.temperature > 950 or request.carburizing.time_hours > 10:
        distortion_risk = "High"
    elif request.carburizing.temperature > 920 or request.carburizing.time_hours > 6:
        distortion_risk = "Medium"
    else:
        distortion_risk = "Low"
    
    # Generate recommendations
    recommendations = []
    if not surface_ok:
        if surface_hrc < target_surface_hrc[0]:
            recommendations.append("Increase carbon potential or carburizing time for higher surface hardness")
        else:
            recommendations.append("Reduce carbon potential or increase tempering temperature")
    
    if not core_ok:
        if core_hrc < target_core_hrc[0]:
            recommendations.append("Increase cooling rate or reduce tempering temperature for higher core hardness")
        else:
            recommendations.append("Increase tempering temperature for lower core hardness")
    
    if not case_depth_ok:
        if case_depth < target_case_depth[0]:
            recommendations.append("Increase carburizing time or temperature for deeper case")
        else:
            recommendations.append("Reduce carburizing time to prevent excessive case depth")
    
    if not recommendations:
        recommendations.append("Process parameters are within optimal range")
        recommendations.append("Consider monitoring for process consistency")
    
    return QualityAssessment(
        meets_specifications=meets_specs,
        uniformity_index=uniformity_index,
        distortion_risk=distortion_risk,
        recommendations=recommendations
    )

# ================================================================================================
# API ENDPOINTS
# ================================================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "C-Q-T Steel Heat Treatment Simulator API",
        "version": "1.0.0",
        "documentation": "/api/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": True
    }

@app.get("/api/steel-grades")
async def get_steel_grades():
    """Get available predefined steel grades"""
    grades = {}
    for grade, composition in STEEL_COMPOSITIONS.items():
        grades[grade] = {
            "composition": {
                "C": composition.C,
                "Si": composition.Si,
                "Mn": composition.Mn,
                "Ni": composition.Ni,
                "Cr": composition.Cr,
                "Mo": composition.Mo
            },
            "description": f"Steel grade {grade} - C:{composition.C}% Cr:{composition.Cr}% Mo:{composition.Mo}%"
        }
    return {
        "data": {"grades": grades},
        "status": 200,
        "message": "Steel grades retrieved successfully"
    }

@app.get("/api/quench-media")
async def get_quench_media():
    """Get available quenching media properties"""
    media = {}
    for medium, properties in QuenchingMedia.MEDIA_PROPERTIES.items():
        media[medium] = {
            "description": properties.get("name", medium),
            "typical_temperature": properties.get("temperature", 25),
            "heat_transfer_coefficient_range": [
                properties.get("heat_transfer_coefficient", 1000) * 0.8, 
                properties.get("heat_transfer_coefficient", 1000) * 1.2
            ]
        }
    return {
        "data": {"media": media},
        "status": 200,
        "message": "Quench media retrieved successfully"
    }

@app.post("/api/validate-inputs")
async def validate_inputs_endpoint(request: HeatTreatmentRequest):
    """Validate input parameters"""
    try:
        warnings = validate_inputs(request)
        steel = create_steel_composition(request.steel_composition)
        
        # Calculate basic properties using real models
        ae3 = phase_models.calculate_ae3_temperature(steel)
        ms_temp = phase_models.calculate_ms_temperature(steel)
        
        return {
            "data": {
                "valid": True,
                "warnings": warnings,
                "steel_properties": {
                    "ae3_temperature": ae3,
                    "ms_temperature": ms_temp
                }
            },
            "status": 200,
            "message": "Validation completed successfully"
        }
    except Exception as e:
        return {
            "data": {
                "valid": False,
                "error": str(e),
                "warnings": []
            },
            "status": 400,
            "message": "Validation failed"
        }

@app.post("/api/simulate")
async def simulate_heat_treatment(request: HeatTreatmentRequest):
    """Main simulation endpoint using fully real physics"""
    start_time = datetime.now()
    calculation_id = request.calculation_id or str(uuid.uuid4())
    
    try:
        logger.info(f"Starting real physics simulation {calculation_id}")
        
        # Create steel composition
        steel = create_steel_composition(request.steel_composition)
        
        # Initialize integrated case depth model
        model = IntegratedCaseDepthModel(steel)
        
        # Run complete case depth analysis using real models
        case_depth_results = model.analyze_complete_case_depth(
            temperature=request.carburizing.temperature,
            time_hours=request.carburizing.time_hours,
            carbon_potential=request.carburizing.carbon_potential,
            max_depth_mm=request.simulation_params.max_analysis_depth,
            n_points=request.simulation_params.spatial_points,
            cooling_rate=thermal_models.calculate_cooling_rate(
                request.carburizing.temperature,
                request.quenching.quench_temperature,
                request.quenching.quench_medium,
                request.geometry.characteristic_dimension
            ),
            tempering_temp=request.tempering.temperature,
            tempering_time=request.tempering.time_hours,
            mass_transfer_coeff=request.carburizing.mass_transfer_coefficient,
            quench_temperature=request.quenching.quench_temperature
        )
        
        # Calculate critical temperatures using real models
        ae3 = phase_models.calculate_ae3_temperature(steel)
        ae1 = phase_models.calculate_ae1_temperature(steel)
        ms_core = phase_models.calculate_ms_temperature(steel)
        
        # Surface composition for Ms calculation
        surface_steel = SteelComposition(
            C=case_depth_results.surface_carbon,
            Si=steel.Si, Mn=steel.Mn, Ni=steel.Ni,
            Cr=steel.Cr, Mo=steel.Mo
        )
        ms_surface = phase_models.calculate_ms_temperature(surface_steel)
        
        # Calculate grain sizes using real models
        grain_surface = grain_models.calculate_grain_size_isothermal(
            request.carburizing.temperature, 
            request.carburizing.time_hours * 3600, 
            steel
        )
        grain_core = grain_models.calculate_grain_size_isothermal(
            request.tempering.temperature,
            request.tempering.time_hours * 3600,
            steel
        )
        
        # Calculate real thermal profiles
        thermal_profile = thermal_models.calculate_thermal_cycle(
            carburizing_temp=request.carburizing.temperature,
            carburizing_time=request.carburizing.time_hours,
            quench_temp=request.quenching.quench_temperature,
            quench_time=request.quenching.quench_time,
            tempering_temp=request.tempering.temperature,
            tempering_time=request.tempering.time_hours
        )
        
        # Calculate real cooling rate
        cooling_rate = thermal_models.calculate_cooling_rate(
            request.carburizing.temperature,
            request.quenching.quench_temperature,
            request.quenching.quench_medium,
            request.geometry.characteristic_dimension
        )
        
        # Calculate carbon flux using real mass transfer
        carbon_flux = carbon_models.calculate_surface_carbon_flux(
            steel,
            request.carburizing.temperature,
            request.carburizing.carbon_potential,
            request.carburizing.mass_transfer_coefficient
        )
        
        # Calculate effective diffusivity
        effective_diffusivity = carbon_models.calculate_effective_diffusivity(
            steel,
            request.carburizing.temperature
        )
        
        # Calculate mass transfer effectiveness
        mass_transfer_effectiveness = carbon_models.calculate_mass_transfer_effectiveness(
            request.carburizing.mass_transfer_coefficient,
            request.carburizing.gas_flow_rate,
            request.carburizing.temperature
        )
        
        # Calculate gradients
        carbon_gradient = (case_depth_results.surface_carbon - case_depth_results.carbon_profile[-1]) / case_depth_results.distance_array[-1]
        hardness_gradient = (case_depth_results.surface_hardness_hrc - case_depth_results.core_hardness_hrc) / case_depth_results.case_depth_50_hrc
        
        # Calculate phase fractions using real models
        phase_fractions = {}
        for i, (distance, carbon) in enumerate(zip(case_depth_results.distance_array, case_depth_results.carbon_profile)):
            local_steel = SteelComposition(
                C=carbon/100, Si=steel.Si, Mn=steel.Mn, Ni=steel.Ni,
                Cr=steel.Cr, Mo=steel.Mo
            )
            fractions = phase_models.calculate_phase_fractions(
                local_steel, cooling_rate, request.tempering.temperature
            )
            
            if i == 0:
                for phase in fractions:
                    phase_fractions[phase] = []
            
            for phase, fraction in fractions.items():
                phase_fractions[phase].append(fraction)
        
        # Calculate case depths at various criteria
        case_depth_03_carbon = case_depth_results.calculate_case_depth_at_carbon(0.3)
        case_depth_55_hrc = case_depth_results.calculate_case_depth_at_hardness(55)
        
        # Build results with real calculations
        computation_time = (datetime.now() - start_time).total_seconds()
        
        # Create results dictionary for quality assessment
        results_dict = {
            'surface_hardness_hrc': case_depth_results.surface_hardness_hrc,
            'core_hardness_hrc': case_depth_results.core_hardness_hrc,
            'case_depth_50_hrc': case_depth_results.case_depth_50_hrc,
            'carbon_profile': case_depth_results.carbon_profile
        }
        
        # Assess quality using real analysis
        quality_assessment = assess_quality(results_dict, request)
        
        results = SimulationResults(
            calculation_id=calculation_id,
            steel_grade=request.steel_composition.grade or "Custom",
            distance_array=case_depth_results.distance_array.tolist(),
            carbon_profile=case_depth_results.carbon_profile.tolist(),
            hardness_profile=case_depth_results.hardness_profile_hrc.tolist(),
            case_depth_results=CaseDepthResults(
                case_depth_04_carbon=case_depth_results.case_depth_04_carbon,
                case_depth_03_carbon=case_depth_03_carbon,
                case_depth_50_hrc=case_depth_results.case_depth_50_hrc,
                case_depth_55_hrc=case_depth_55_hrc,
                effective_case_depth=case_depth_results.effective_diffusion_depth,
                surface_carbon=case_depth_results.surface_carbon
            ),
            process_metrics=ProcessMetrics(
                surface_hardness_hrc=case_depth_results.surface_hardness_hrc,
                surface_hardness_hv=case_depth_results.surface_hardness_hv,
                core_hardness_hrc=case_depth_results.core_hardness_hrc,
                core_hardness_hv=case_depth_results.core_hardness_hv,
                surface_carbon=case_depth_results.surface_carbon,
                carbon_gradient=carbon_gradient,
                hardness_gradient=hardness_gradient,
                distortion_risk=quality_assessment.distortion_risk,
                grain_size_surface=grain_surface,
                grain_size_core=grain_core,
                carbon_flux_surface=carbon_flux,
                effective_diffusivity=effective_diffusivity,
                mass_transfer_effectiveness=mass_transfer_effectiveness
            ),
            critical_temperatures=CriticalTemperatures(
                ae3_temperature=ae3,
                ae1_temperature=ae1,
                ms_temperature_core=ms_core,
                ms_temperature_surface=ms_surface
            ),
            thermal_profiles=ThermalProfile(
                time_array=thermal_profile['time_total'],
                temperature_array=thermal_profile['temperature_total'],
                time_carburizing=thermal_profile['time_carburizing'],
                temperature_carburizing=thermal_profile['temperature_carburizing'],
                time_quenching=thermal_profile['time_quenching'],
                temperature_quenching=thermal_profile['temperature_quenching'],
                cooling_rate=cooling_rate
            ),
            grain_sizes={
                "surface_grain_size": grain_surface,
                "core_grain_size": grain_core,
                "average_grain_size": (grain_surface + grain_core) / 2
            },
            quality_assessment=quality_assessment,
            property_profiles={
                "distance_mm": case_depth_results.distance_array.tolist(),
                "hardness_hrc": case_depth_results.hardness_profile_hrc.tolist(),
                "carbon_profile": case_depth_results.carbon_profile.tolist(),
                "grain_size": [grain_surface + (grain_core - grain_surface) * i / len(case_depth_results.distance_array) 
                              for i in range(len(case_depth_results.distance_array))]
            },
            phase_fractions=phase_fractions,
            warnings=validate_inputs(request),
            errors=[],
            computation_time=computation_time,
            timestamp=datetime.now().isoformat(),
            validation_status="Real physics simulation completed successfully"
        )
        
        # Store in cache
        calculation_cache[calculation_id] = results
        
        logger.info(f"Real simulation {calculation_id} completed in {computation_time:.2f}s")
        return {
            "data": results,
            "status": 200,
            "message": "Real physics simulation completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Real simulation {calculation_id} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real simulation failed: {str(e)}")

@app.get("/api/simulation/{calculation_id}")
async def get_simulation_results(calculation_id: str):
    """Retrieve cached simulation results"""
    if calculation_id not in calculation_cache:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation_cache[calculation_id]

@app.delete("/api/simulation/{calculation_id}")
async def delete_simulation(calculation_id: str):
    """Delete cached simulation results"""
    if calculation_id in calculation_cache:
        del calculation_cache[calculation_id]
        return {"message": "Simulation deleted successfully"}
    raise HTTPException(status_code=404, detail="Calculation not found")

@app.get("/api/calculations")
async def list_calculations():
    """List all cached calculations"""
    return {
        "calculations": [
            {
                "id": calc_id,
                "timestamp": results.timestamp,
                "steel_grade": results.steel_grade
            } for calc_id, results in calculation_cache.items()
        ]
    }

@app.post("/api/optimize-process")
async def optimize_process_parameters(request: OptimizeProcessRequest):
    """Optimize process parameters using real optimization models"""
    try:
        if request.steel_grade.upper() not in STEEL_COMPOSITIONS:
            raise HTTPException(status_code=400, detail="Unknown steel grade")
        
        steel = STEEL_COMPOSITIONS[request.steel_grade.upper()]
        model = IntegratedCaseDepthModel(steel)
        
        # Use real optimization algorithm
        optimization_result = model.optimize_process_for_target_case_depth(
            target_case_depth_mm=request.target_case_depth,
            case_depth_criterion='50_hrc',
            temperature_range=(880, request.max_temperature),
            time_range=(2, request.max_time),
            carbon_potential=request.carbon_potential
        )
        
        return {
            "target_case_depth": request.target_case_depth,
            "optimal_conditions": optimization_result,
            "success": optimization_result.get('target_met', False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/api/material-comparison")
async def compare_materials(request: MaterialComparisonRequest):
    """Compare different steel grades using real physics calculations"""
    try:
        results = {}
        
        for grade in request.steel_grades:
            if grade.upper() not in STEEL_COMPOSITIONS:
                continue
                
            steel = STEEL_COMPOSITIONS[grade.upper()]
            model = IntegratedCaseDepthModel(steel)
            
            # Run real simulation for each material
            case_results = model.analyze_complete_case_depth(
                temperature=request.process_conditions.get('temperature', 920),
                time_hours=request.process_conditions.get('time_hours', 6),
                carbon_potential=request.process_conditions.get('carbon_potential', 1.0),
                max_depth_mm=5.0,
                n_points=51,
                cooling_rate=200,
                tempering_temp=request.process_conditions.get('tempering_temp', 170),
                tempering_time=request.process_conditions.get('tempering_time', 2),
                mass_transfer_coeff=1e-4
            )
            
            results[grade] = {
                "case_depth_04_carbon": case_results.case_depth_04_carbon,
                "case_depth_50_hrc": case_results.case_depth_50_hrc,
                "surface_hardness_hrc": case_results.surface_hardness_hrc,
                "core_hardness_hrc": case_results.core_hardness_hrc,
                "surface_carbon": case_results.surface_carbon
            }
        
        return {
            "comparison_results": results,
            "process_conditions": request.process_conditions,
            "best_for_case_depth": max(results.keys(), key=lambda k: results[k]["case_depth_50_hrc"]) if results else None,
            "best_for_surface_hardness": max(results.keys(), key=lambda k: results[k]["surface_hardness_hrc"]) if results else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Material comparison failed: {str(e)}")

@app.post("/api/process-recommendations")
async def get_process_recommendations(request: ProcessRecommendationsRequest):
    """Get process recommendations based on real models"""
    try:
        if request.steel_grade.upper() in STEEL_COMPOSITIONS:
            steel = STEEL_COMPOSITIONS[request.steel_grade.upper()]
            model = IntegratedCaseDepthModel(steel)
            
            # Get real recommendations based on steel composition and part size
            recommendations = model.get_process_recommendations(
                part_size_mm=request.part_size,
                application=request.application
            )
        else:
            # Default recommendations
            recommendations = {
                "carburizing": {
                    "temperature_range": [910, 930],
                    "time_range": [4, 8],
                    "carbon_potential_range": [0.9, 1.1],
                    "atmosphere": "endothermic"
                },
                "quenching": {
                    "medium": "oil" if request.part_size > 20 else "water",
                    "temperature": 60,
                    "agitation": "medium"
                },
                "tempering": {
                    "temperature_range": [160, 180],
                    "time_range": [1.5, 2.5],
                    "cycles": 1
                },
                "quality_targets": {
                    "surface_hardness_hrc": [58, 62],
                    "case_depth_mm": [0.6, 0.8],
                    "core_hardness_hrc": [32, 48]
                }
            }
            
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": f"Invalid input: {str(exc)}"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Real Physics C-Q-T Simulator API starting up...")
    logger.info("All mathematical models loaded successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Real Physics C-Q-T Simulator API shutting down...")
    calculation_cache.clear()

# Main execution
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )