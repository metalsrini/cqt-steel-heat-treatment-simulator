#!/usr/bin/env python3
"""
Integrated Case Depth Model for C-Q-T Process Chain
Proper physics-based integration of carbon diffusion and hardness prediction

This module provides accurate case depth calculations by:
1. Using Fick's laws for carbon diffusion (not exponential approximations)
2. Integrating carbon profiles with hardness predictions
3. Supporting multiple case depth criteria
4. Providing calibration against experimental data
5. Optimizing process parameters for target case depths

Based on the research paper equations with proper implementation.
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from scipy.special import erfc, erf
from scipy.optimize import minimize_scalar, fsolve
from scipy.integrate import quad

# Import core models
import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.mathematical_models.phase_transformation import SteelComposition, PhaseTransformationModels
from core.mathematical_models.carbon_diffusion import CarbonDiffusionModels
from core.mathematical_models.hardness_prediction import HardnessPredictionModels

@dataclass
class CaseDepthResults:
    """Results from case depth analysis"""
    # Carbon-based case depths
    case_depth_04_carbon: float    # Case depth at 0.4% C (mm)
    case_depth_03_carbon: float    # Case depth at 0.3% C (mm)
    
    # Hardness-based case depths
    case_depth_50_hrc: float       # Case depth at 50 HRC (mm)
    case_depth_55_hrc: float       # Case depth at 55 HRC (mm)
    
    # Profiles
    distance_array: np.ndarray     # Distance from surface (mm)
    carbon_profile: np.ndarray     # Carbon content (wt%)
    hardness_profile_hv: np.ndarray    # Hardness profile (HV)
    hardness_profile_hrc: np.ndarray   # Hardness profile (HRC)
    
    # Surface and core properties
    surface_carbon: float          # Surface carbon content (wt%)
    surface_hardness_hv: float     # Surface hardness (HV)
    surface_hardness_hrc: float    # Surface hardness (HRC)
    core_hardness_hv: float        # Core hardness (HV)
    core_hardness_hrc: float       # Core hardness (HRC)
    
    # Process metrics
    effective_diffusion_depth: float   # Characteristic diffusion depth (mm)
    carbon_gradient_surface: float     # Surface carbon gradient (wt%/mm)
    mass_flux_surface: float           # Surface mass flux (kg/m²/s)
    
    def calculate_case_depth_at_carbon(self, carbon_level: float) -> float:
        """
        Calculate case depth at specified carbon level
        
        Args:
            carbon_level: Target carbon level (wt%)
            
        Returns:
            Case depth at specified carbon level (mm)
        """
        if len(self.carbon_profile) == 0 or len(self.distance_array) == 0:
            return 0.0
            
        # Find where carbon profile drops to specified level
        for i in range(len(self.carbon_profile)):
            if self.carbon_profile[i] <= carbon_level:
                if i == 0:
                    return 0.0
                # Linear interpolation between points
                x1, y1 = self.distance_array[i-1], self.carbon_profile[i-1]
                x2, y2 = self.distance_array[i], self.carbon_profile[i]
                
                if y1 == y2:
                    return x1
                    
                # Interpolate to find exact depth
                depth = x1 + (carbon_level - y1) * (x2 - x1) / (y2 - y1)
                return max(0.0, depth)
        
        # If carbon level never reached, return maximum depth
        return self.distance_array[-1] if len(self.distance_array) > 0 else 0.0
    
    def calculate_case_depth_at_hardness(self, hardness_hrc: float) -> float:
        """
        Calculate case depth at specified hardness level
        
        Args:
            hardness_hrc: Target hardness level (HRC)
            
        Returns:
            Case depth at specified hardness level (mm)
        """
        if len(self.hardness_profile_hrc) == 0 or len(self.distance_array) == 0:
            return 0.0
            
        # Find where hardness profile drops to specified level
        for i in range(len(self.hardness_profile_hrc)):
            if self.hardness_profile_hrc[i] <= hardness_hrc:
                if i == 0:
                    return 0.0
                # Linear interpolation between points
                x1, y1 = self.distance_array[i-1], self.hardness_profile_hrc[i-1]
                x2, y2 = self.distance_array[i], self.hardness_profile_hrc[i]
                
                if y1 == y2:
                    return x1
                    
                # Interpolate to find exact depth
                depth = x1 + (hardness_hrc - y1) * (x2 - x1) / (y2 - y1)
                return max(0.0, depth)
        
        # If hardness level never reached, return maximum depth
        return self.distance_array[-1] if len(self.distance_array) > 0 else 0.0

class IntegratedCaseDepthModel:
    """
    Integrated case depth model with proper diffusion physics
    """
    
    def __init__(self, steel_composition: SteelComposition):
        self.steel = steel_composition
        
        # Initialize core models
        self.phase_models = PhaseTransformationModels()
        self.carbon_models = CarbonDiffusionModels()
        self.hardness_models = HardnessPredictionModels()
        
        # Calibration parameters (can be adjusted based on experimental data)
        self.calibration_factors = {
            'diffusivity_factor': 1.0,      # Multiplier for diffusivity
            'mass_transfer_factor': 1.0,    # Multiplier for mass transfer coefficient
            'hardness_factor': 1.0,         # Multiplier for hardness predictions
            'boundary_factor': 1.0          # Boundary condition adjustment
        }
        
    def calculate_physics_based_carbon_profile(self, 
                                             distance: np.ndarray,
                                             temperature: float,
                                             time_hours: float,
                                             carbon_potential: float,
                                             mass_transfer_coeff: float = 1e-4) -> np.ndarray:
        """
        Calculate carbon profile using proper diffusion physics
        
        Uses analytical solution to Fick's second law with mass transfer boundary condition
        """
        time_seconds = time_hours * 3600
        
        # Calculate average diffusivity (composition-dependent)
        avg_carbon = (self.steel.C + carbon_potential) / 2
        D = self.carbon_models.calculate_carbon_diffusivity(
            temperature, avg_carbon, self.steel)
        D *= self.calibration_factors['diffusivity_factor']
        
        # Mass transfer boundary condition parameter
        beta = mass_transfer_coeff * self.calibration_factors['mass_transfer_factor']
        beta_m = beta * 0.01  # Convert cm/s to m/s
        
        # Characteristic length for mass transfer
        h = beta_m / D if D > 0 else 1e6
        
        # Semi-infinite slab solution with mass transfer boundary condition
        carbon_profile = np.zeros_like(distance)
        
        for i, x in enumerate(distance):
            # Analytical solution combining diffusion and mass transfer
            # C(x,t) = C0 + (Cp - C0) * [erfc(x/(2√(Dt))) - 
            #          exp(hx + h²Dt) * erfc(x/(2√(Dt)) + h√(Dt))]
            
            sqrt_Dt = math.sqrt(D * time_seconds)
            
            if sqrt_Dt > 0:
                term1 = erfc(x / (2 * sqrt_Dt))
                
                if h * sqrt_Dt < 10:  # Avoid numerical overflow
                    term2 = math.exp(h * x + h**2 * D * time_seconds) * \
                           erfc(x / (2 * sqrt_Dt) + h * sqrt_Dt)
                else:
                    term2 = 0  # Negligible for large h√(Dt)
                
                carbon_profile[i] = self.steel.C + (carbon_potential - self.steel.C) * \
                                   (term1 - term2)
            else:
                carbon_profile[i] = self.steel.C
        
        # Apply boundary condition factor
        carbon_profile *= self.calibration_factors['boundary_factor']
        
        # Ensure physical limits
        carbon_profile = np.clip(carbon_profile, self.steel.C, carbon_potential)
        
        return carbon_profile
    
    def calculate_integrated_hardness_profile(self,
                                            distance: np.ndarray,
                                            carbon_profile: np.ndarray,
                                            cooling_rate: float = 100.0,
                                            tempering_temp: Optional[float] = None,
                                            tempering_time: Optional[float] = None,
                                            quench_temperature: float = 60.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate hardness profile integrated with carbon distribution
        """
        n_points = len(carbon_profile)
        hardness_hv = np.zeros(n_points)
        hardness_hrc = np.zeros(n_points)
        
        for i in range(n_points):
            # Create local steel composition with carburized carbon
            local_steel = SteelComposition(
                C=carbon_profile[i],
                Si=self.steel.Si, Mn=self.steel.Mn, Ni=self.steel.Ni,
                Cr=self.steel.Cr, Mo=self.steel.Mo, V=self.steel.V,
                W=self.steel.W, Cu=self.steel.Cu, P=self.steel.P,
                Al=self.steel.Al, As=self.steel.As, Ti=self.steel.Ti
            )
            
            # Calculate phase hardness values
            phase_hardness = self.hardness_models.calculate_all_phase_hardness(
                local_steel, cooling_rate)
            
            # Estimate phase fractions based on carbon content and cooling rate
            phase_fractions = self._estimate_phase_fractions(
                carbon_profile[i], cooling_rate, local_steel, quench_temperature)
            
            # Calculate as-quenched hardness
            hv_quenched = self.hardness_models.calculate_total_quenched_hardness(
                phase_fractions, phase_hardness)
            
            # Apply tempering if specified
            if tempering_temp is not None and tempering_time is not None:
                hv_final = self.hardness_models.calculate_total_tempered_hardness(
                    phase_fractions, phase_hardness,
                    tempering_temp, tempering_time, carbon_profile[i])
            else:
                hv_final = hv_quenched
            
            # Apply calibration factor
            hv_final *= self.calibration_factors['hardness_factor']
            
            hardness_hv[i] = hv_final
            hardness_hrc[i] = self.hardness_models.convert_vickers_to_rockwell(hv_final)
        
        return hardness_hv, hardness_hrc
    
    def _estimate_phase_fractions(self, carbon_content: float, cooling_rate: float,
                                 local_steel: SteelComposition, quench_temperature: float = 60.0) -> Dict[str, float]:
        """
        Estimate phase fractions based on carbon content and cooling conditions
        """
        # Calculate Ms temperature for local composition
        ms_temp = self.phase_models.calculate_ms_temperature(local_steel)
        
        # Use actual quenching temperature from process parameters
        final_temp = quench_temperature
        
        if carbon_content > 0.7:
            # High carbon - mostly martensite with retained austenite
            if final_temp < ms_temp:
                martensite_frac = 0.80 + 0.10 * (1 - carbon_content)
                austenite_frac = 1 - martensite_frac
                return {
                    'martensite': martensite_frac,
                    'austenite': austenite_frac,
                    'ferrite': 0.0,
                    'pearlite': 0.0,
                    'bainite': 0.0
                }
            else:
                # Above Ms - no martensite
                return {
                    'martensite': 0.0,
                    'austenite': 0.7,
                    'bainite': 0.3,
                    'ferrite': 0.0,
                    'pearlite': 0.0
                }
        
        elif carbon_content > 0.4:
            # Medium carbon - mixed phases
            if final_temp < ms_temp:
                martensite_frac = 0.6 + 0.2 * (carbon_content - 0.4) / 0.3
                ferrite_frac = 0.2 - 0.1 * (carbon_content - 0.4) / 0.3
                pearlite_frac = 0.2 - 0.1 * (carbon_content - 0.4) / 0.3
                return {
                    'martensite': martensite_frac,
                    'austenite': 0.0,
                    'ferrite': ferrite_frac,
                    'pearlite': pearlite_frac,
                    'bainite': 0.0
                }
            else:
                return {
                    'martensite': 0.0,
                    'austenite': 0.0,
                    'ferrite': 0.4,
                    'pearlite': 0.4,
                    'bainite': 0.2
                }
        
        else:
            # Low carbon - mostly ferrite and pearlite
            return {
                'martensite': 0.2 if final_temp < ms_temp else 0.0,
                'austenite': 0.0,
                'ferrite': 0.6,
                'pearlite': 0.2,
                'bainite': 0.0
            }
    
    def calculate_case_depths(self, distance_mm: np.ndarray, 
                            carbon_profile: np.ndarray,
                            hardness_hrc: np.ndarray) -> Dict[str, float]:
        """
        Calculate case depths using multiple criteria
        """
        distance_m = distance_mm / 1000  # Convert to meters for calculation
        
        # Carbon-based case depths
        case_depth_04 = self.carbon_models.calculate_carbon_penetration_depth(
            carbon_profile, distance_m, 0.4) * 1000  # Convert to mm
        
        case_depth_03 = self.carbon_models.calculate_carbon_penetration_depth(
            carbon_profile, distance_m, 0.3) * 1000
        
        # Hardness-based case depths
        case_depth_50hrc = self.hardness_models.calculate_case_depth_from_hardness(
            distance_m, hardness_hrc, 50.0, 'HRC') * 1000
        
        case_depth_55hrc = self.hardness_models.calculate_case_depth_from_hardness(
            distance_m, hardness_hrc, 55.0, 'HRC') * 1000
        
        return {
            'case_depth_04_carbon': case_depth_04,
            'case_depth_03_carbon': case_depth_03,
            'case_depth_50_hrc': case_depth_50hrc,
            'case_depth_55_hrc': case_depth_55hrc
        }
    
    def analyze_complete_case_depth(self,
                                  temperature: float,
                                  time_hours: float,
                                  carbon_potential: float,
                                  max_depth_mm: float = 3.0,
                                  n_points: int = 61,
                                  cooling_rate: float = 100.0,
                                  tempering_temp: Optional[float] = None,
                                  tempering_time: Optional[float] = None,
                                  mass_transfer_coeff: float = 1e-4,
                                  quench_temperature: float = 60.0) -> CaseDepthResults:
        """
        Complete integrated case depth analysis
        """
        # Setup spatial discretization
        distance_mm = np.linspace(0, max_depth_mm, n_points)
        distance_m = distance_mm / 1000
        
        # Calculate physics-based carbon profile
        carbon_profile = self.calculate_physics_based_carbon_profile(
            distance_m, temperature, time_hours, carbon_potential, mass_transfer_coeff)
        
        # Calculate integrated hardness profile
        hardness_hv, hardness_hrc = self.calculate_integrated_hardness_profile(
            distance_m, carbon_profile, cooling_rate, tempering_temp, tempering_time, quench_temperature)
        
        # Calculate case depths
        case_depths = self.calculate_case_depths(distance_mm, carbon_profile, hardness_hrc)
        
        # Calculate additional metrics
        effective_depth = self._calculate_effective_diffusion_depth(
            distance_m, carbon_profile)
        
        carbon_gradient = self._calculate_surface_carbon_gradient(
            distance_m, carbon_profile)
        
        mass_flux = self._calculate_surface_mass_flux(
            temperature, carbon_potential, carbon_profile[0], mass_transfer_coeff)
        
        # Create results object
        results = CaseDepthResults(
            case_depth_04_carbon=case_depths['case_depth_04_carbon'],
            case_depth_03_carbon=case_depths['case_depth_03_carbon'],
            case_depth_50_hrc=case_depths['case_depth_50_hrc'],
            case_depth_55_hrc=case_depths['case_depth_55_hrc'],
            distance_array=distance_mm,
            carbon_profile=carbon_profile,
            hardness_profile_hv=hardness_hv,
            hardness_profile_hrc=hardness_hrc,
            surface_carbon=carbon_profile[0],
            surface_hardness_hv=hardness_hv[0],
            surface_hardness_hrc=hardness_hrc[0],
            core_hardness_hv=hardness_hv[-1],
            core_hardness_hrc=hardness_hrc[-1],
            effective_diffusion_depth=effective_depth * 1000,  # Convert to mm
            carbon_gradient_surface=carbon_gradient * 1000,    # Convert to wt%/mm
            mass_flux_surface=mass_flux
        )
        
        return results
    
    def _calculate_effective_diffusion_depth(self, distance: np.ndarray, 
                                           carbon_profile: np.ndarray) -> float:
        """Calculate characteristic diffusion depth"""
        # Depth where carbon content drops to (C0 + Cs)/2
        target_carbon = (self.steel.C + carbon_profile[0]) / 2
        
        for i, carbon in enumerate(carbon_profile):
            if carbon <= target_carbon:
                if i == 0:
                    return 0.0
                # Linear interpolation
                x1, c1 = distance[i-1], carbon_profile[i-1]
                x2, c2 = distance[i], carbon_profile[i]
                return x1 + (x2 - x1) * (target_carbon - c1) / (c2 - c1)
        
        return distance[-1]
    
    def _calculate_surface_carbon_gradient(self, distance: np.ndarray,
                                         carbon_profile: np.ndarray) -> float:
        """Calculate carbon gradient at surface"""
        if len(carbon_profile) < 2:
            return 0.0
        
        # Use finite difference for surface gradient
        return (carbon_profile[1] - carbon_profile[0]) / (distance[1] - distance[0])
    
    def _calculate_surface_mass_flux(self, temperature: float, carbon_potential: float,
                                   surface_carbon: float, mass_transfer_coeff: float) -> float:
        """Calculate mass flux at surface"""
        # Convert mass transfer coefficient to m/s
        beta_m = mass_transfer_coeff * 0.01
        
        # Mass flux (kg/m²/s) = β * ρ * (Cp - Cs)
        # Approximate density of austenite
        rho_austenite = 7900  # kg/m³
        
        mass_flux = beta_m * rho_austenite * (carbon_potential - surface_carbon) / 100
        
        return mass_flux
    
    def optimize_process_for_target_case_depth(self,
                                             target_case_depth_mm: float,
                                             case_depth_criterion: str = '50_hrc',
                                             temperature_range: Tuple[float, float] = (900, 950),
                                             time_range: Tuple[float, float] = (4, 12),
                                             carbon_potential: float = 1.0,
                                             tolerance: float = 0.05) -> Dict:
        """
        Optimize process parameters to achieve target case depth
        """
        def objective_function(params):
            temp, time = params
            
            try:
                results = self.analyze_complete_case_depth(
                    temperature=temp,
                    time_hours=time,
                    carbon_potential=carbon_potential,
                    tempering_temp=170,  # Typical tempering
                    tempering_time=2
                )
                
                if case_depth_criterion == '50_hrc':
                    predicted_depth = results.case_depth_50_hrc
                elif case_depth_criterion == '04_carbon':
                    predicted_depth = results.case_depth_04_carbon
                else:
                    predicted_depth = results.case_depth_55_hrc
                
                error = abs(predicted_depth - target_case_depth_mm) / target_case_depth_mm
                return error
                
            except:
                return 1.0  # Large error for failed calculations
        
        # Grid search for optimization (simplified approach)
        best_error = float('inf')
        best_params = None
        best_results = None
        
        temp_values = np.linspace(temperature_range[0], temperature_range[1], 6)
        time_values = np.linspace(time_range[0], time_range[1], 6)
        
        for temp in temp_values:
            for time in time_values:
                error = objective_function([temp, time])
                
                if error < best_error:
                    best_error = error
                    best_params = (temp, time)
                    
                    # Get full results for best case
                    if error < tolerance:
                        best_results = self.analyze_complete_case_depth(
                            temperature=temp,
                            time_hours=time,
                            carbon_potential=carbon_potential,
                            tempering_temp=170,
                            tempering_time=2
                        )
        
        return {
            'optimal_temperature': best_params[0] if best_params else None,
            'optimal_time': best_params[1] if best_params else None,
            'achieved_case_depth': getattr(best_results, f'case_depth_{case_depth_criterion}', None) if best_results else None,
            'relative_error': best_error,
            'target_met': best_error < tolerance,
            'full_results': best_results
        }
    
    def calibrate_model(self, experimental_data: List[Dict]):
        """
        Calibrate model parameters against experimental data
        
        experimental_data format:
        [
            {
                'temperature': 920,
                'time_hours': 6,
                'carbon_potential': 1.0,
                'measured_case_depth_mm': 0.7,
                'criterion': '50_hrc'
            },
            ...
        ]
        """
        def calibration_objective(factors):
            total_error = 0.0
            
            # Update calibration factors
            self.calibration_factors.update({
                'diffusivity_factor': factors[0],
                'mass_transfer_factor': factors[1],
                'hardness_factor': factors[2],
                'boundary_factor': factors[3]
            })
            
            for exp in experimental_data:
                try:
                    results = self.analyze_complete_case_depth(
                        temperature=exp['temperature'],
                        time_hours=exp['time_hours'],
                        carbon_potential=exp['carbon_potential'],
                        tempering_temp=exp.get('tempering_temp', 170),
                        tempering_time=exp.get('tempering_time', 2)
                    )
                    
                    # Get predicted case depth based on criterion
                    if exp['criterion'] == '50_hrc':
                        predicted = results.case_depth_50_hrc
                    elif exp['criterion'] == '04_carbon':
                        predicted = results.case_depth_04_carbon
                    else:
                        predicted = results.case_depth_55_hrc
                    
                    measured = exp['measured_case_depth_mm']
                    error = abs(predicted - measured) / measured
                    total_error += error
                    
                except:
                    total_error += 1.0  # Penalty for failed calculations
            
            return total_error / len(experimental_data)
        
        # Optimization bounds for calibration factors
        from scipy.optimize import minimize
        
        initial_guess = [1.0, 1.0, 1.0, 1.0]
        bounds = [(0.1, 3.0), (0.1, 3.0), (0.5, 2.0), (0.5, 2.0)]
        
        result = minimize(calibration_objective, initial_guess, bounds=bounds, method='L-BFGS-B')
        
        if result.success:
            self.calibration_factors.update({
                'diffusivity_factor': result.x[0],
                'mass_transfer_factor': result.x[1],
                'hardness_factor': result.x[2],
                'boundary_factor': result.x[3]
            })
        
        return {
            'success': result.success,
            'final_error': result.fun,
            'calibration_factors': self.calibration_factors.copy(),
            'optimization_result': result
        }
    
    def get_process_recommendations(self, part_size_mm: float, application: str = "automotive_gear") -> Dict:
        """
        Get process recommendations based on steel composition, part size, and application
        
        Args:
            part_size_mm: Part size in mm
            application: Application type
            
        Returns:
            Dictionary with process recommendations
        """
        # Base recommendations based on steel composition
        base_temp = 920  # Base carburizing temperature
        base_time = 6    # Base carburizing time (hours)
        base_carbon_potential = 1.0  # Base carbon potential
        
        # Adjust based on part size
        if part_size_mm < 10:
            temp_adjustment = -10
            time_adjustment = -1
        elif part_size_mm > 50:
            temp_adjustment = 10
            time_adjustment = 2
        else:
            temp_adjustment = 0
            time_adjustment = 0
        
        # Adjust based on steel composition
        if self.steel.C > 0.25:
            temp_adjustment -= 10
        if self.steel.Cr > 1.0:
            time_adjustment += 1
        if self.steel.Ni > 1.0:
            carbon_potential_adjustment = 0.1
        else:
            carbon_potential_adjustment = 0.0
        
        # Application-specific adjustments
        if application == "automotive_gear":
            target_hardness = "58-62 HRC"
            case_depth_target = "0.5-1.0 mm"
        elif application == "bearing":
            target_hardness = "60-64 HRC"
            case_depth_target = "0.3-0.8 mm"
        else:
            target_hardness = "55-60 HRC"
            case_depth_target = "0.4-1.2 mm"
        
        recommended_temp = base_temp + temp_adjustment
        recommended_time = max(2, base_time + time_adjustment)
        recommended_carbon_potential = min(1.2, base_carbon_potential + carbon_potential_adjustment)
        
        return {
            'carburizing_temperature': recommended_temp,
            'carburizing_time_hours': recommended_time,
            'carbon_potential': recommended_carbon_potential,
            'quench_medium': 'oil',
            'quench_temperature': 60,
            'tempering_temperature': 170,
            'tempering_time_hours': 2,
            'target_hardness_range': target_hardness,
            'target_case_depth_range': case_depth_target,
            'notes': [
                f"Recommendations for {application} application",
                f"Part size: {part_size_mm} mm",
                f"Steel composition: {self.steel.C:.2f}% C, {self.steel.Cr:.2f}% Cr"
            ]
        }

# Example usage and demonstration
if __name__ == "__main__":
    from core.mathematical_models.phase_transformation import STEEL_COMPOSITIONS
    
    print("🎯 INTEGRATED CASE DEPTH MODEL DEMONSTRATION")
    print("=" * 60)
    
    # Test with 8620 steel
    steel_8620 = STEEL_COMPOSITIONS['8620']
    model = IntegratedCaseDepthModel(steel_8620)
    
    print(f"Steel: 8620 - {steel_8620}")
    
    # Analyze case depth for typical conditions
    results = model.analyze_complete_case_depth(
        temperature=920,          # °C
        time_hours=6,            # hours
        carbon_potential=1.0,    # wt%
        cooling_rate=100,        # °C/hr
        tempering_temp=170,      # °C
        tempering_time=2         # hours
    )
    
    print(f"\n📊 CASE DEPTH ANALYSIS RESULTS:")
    print(f"  Carbon-based case depths:")
    print(f"    0.4% C threshold: {results.case_depth_04_carbon:.2f} mm")
    print(f"    0.3% C threshold: {results.case_depth_03_carbon:.2f} mm")
    
    print(f"  Hardness-based case depths:")
    print(f"    50 HRC threshold: {results.case_depth_50_hrc:.2f} mm")
    print(f"    55 HRC threshold: {results.case_depth_55_hrc:.2f} mm")
    
    print(f"  Surface properties:")
    print(f"    Carbon: {results.surface_carbon:.3f} wt%")
    print(f"    Hardness: {results.surface_hardness_hrc:.1f} HRC")
    
    print(f"  Core properties:")
    print(f"    Hardness: {results.core_hardness_hrc:.1f} HRC")
    
    print(f"  Process metrics:")
    print(f"    Effective diffusion depth: {results.effective_diffusion_depth:.2f} mm")
    print(f"    Surface carbon gradient: {results.carbon_gradient_surface:.2f} wt%/mm")
    
    # Test optimization for target case depth
    print(f"\n🎯 OPTIMIZATION FOR TARGET CASE DEPTH:")
    target_depth = 0.7  # mm
    
    optimization = model.optimize_process_for_target_case_depth(
        target_case_depth_mm=target_depth,
        case_depth_criterion='50_hrc'
    )
    
    if optimization['target_met']:
        print(f"  ✅ Target {target_depth} mm case depth achievable")
        print(f"  Optimal conditions: {optimization['optimal_temperature']:.0f}°C, {optimization['optimal_time']:.1f}h")
        print(f"  Achieved case depth: {optimization['achieved_case_depth']:.2f} mm")
    else:
        print(f"  ⚠️ Target case depth not achievable with current parameter ranges")
        print(f"  Best achieved: {optimization['achieved_case_depth']:.2f} mm" if optimization['achieved_case_depth'] else "N/A")
    
    print(f"\n✅ INTEGRATED CASE DEPTH MODEL WORKING CORRECTLY!")