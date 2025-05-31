"""
Hardness Prediction Models for C-Q-T Process Chain
Implementation of Maynier equations and tempering hardness models (Equations 15-25)
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .phase_transformation import SteelComposition

@dataclass
class HardnessResults:
    """Results from hardness calculations"""
    vickers_hardness: float
    rockwell_c_hardness: float
    phase_contributions: Dict[str, float]
    total_hardness: float

class HardnessPredictionModels:
    """
    Implementation of hardness prediction models from the research paper
    """
    
    def __init__(self):
        pass
    
    def calculate_austenite_ferrite_pearlite_hardness(self, composition: SteelComposition, 
                                                     cooling_rate: float) -> float:
        """
        Calculate austenite-ferrite-pearlite hardness using Equation (15)
        
        HVa-f-p(V.H.N) = 42+223C+53Si+30Mn+12.6Ni+7Cr+19Mo+log₁₀Vr(10-19Si+4Ni+8Cr+130V)
        
        Args:
            composition: Steel chemical composition
            cooling_rate: Cooling rate at 700°C in °C/hr
            
        Returns:
            Vickers hardness of austenite-ferrite-pearlite mixture
        """
        log_vr = math.log10(cooling_rate) if cooling_rate > 0 else 0
        
        hv_afp = (42 + 223 * composition.C + 53 * composition.Si +
                  30 * composition.Mn + 12.6 * composition.Ni +
                  7 * composition.Cr + 19 * composition.Mo +
                  log_vr * (10 - 19 * composition.Si + 4 * composition.Ni +
                           8 * composition.Cr + 130 * composition.V))
        
        return max(0.0, hv_afp)
    
    def calculate_bainite_hardness(self, composition: SteelComposition, 
                                  cooling_rate: float) -> float:
        """
        Calculate bainite hardness using Equation (16)
        
        HVb(V.H.N) = -323+185C+330Si+153Mn+65Ni+144Cr+191Mo+log₁₀Vr(89+53C-55Si-22Mn-10Ni-20Cr-33Mo)
        
        Args:
            composition: Steel chemical composition
            cooling_rate: Cooling rate at 700°C in °C/hr
            
        Returns:
            Vickers hardness of bainite
        """
        log_vr = math.log10(cooling_rate) if cooling_rate > 0 else 0
        
        hv_b = (-323 + 185 * composition.C + 330 * composition.Si +
                153 * composition.Mn + 65 * composition.Ni +
                144 * composition.Cr + 191 * composition.Mo +
                log_vr * (89 + 53 * composition.C - 55 * composition.Si -
                         22 * composition.Mn - 10 * composition.Ni -
                         20 * composition.Cr - 33 * composition.Mo))
        
        return max(0.0, hv_b)
    
    def calculate_martensite_hardness(self, composition: SteelComposition, 
                                     cooling_rate: float) -> float:
        """
        Calculate martensite hardness using Equation (17)
        
        HVm(V.H.N) = 127+949C+27Si+11Mn+8Ni+16Cr+211log₁₀Vr
        
        Args:
            composition: Steel chemical composition
            cooling_rate: Cooling rate at 700°C in °C/hr
            
        Returns:
            Vickers hardness of martensite
        """
        log_vr = math.log10(cooling_rate) if cooling_rate > 0 else 0
        
        hv_m = (127 + 949 * composition.C + 27 * composition.Si +
                11 * composition.Mn + 8 * composition.Ni +
                16 * composition.Cr + 211 * log_vr)
        
        return max(0.0, hv_m)
    
    def calculate_all_phase_hardness(self, composition: SteelComposition, 
                                   cooling_rate: float) -> Dict[str, float]:
        """
        Calculate hardness for all phases using Maynier equations (15-17)
        
        Args:
            composition: Steel chemical composition
            cooling_rate: Cooling rate at 700°C in °C/hr
            
        Returns:
            Dictionary with hardness values for each phase
        """
        return {
            'austenite_ferrite_pearlite': self.calculate_austenite_ferrite_pearlite_hardness(
                composition, cooling_rate),
            'bainite': self.calculate_bainite_hardness(composition, cooling_rate),
            'martensite': self.calculate_martensite_hardness(composition, cooling_rate)
        }
    
    def calculate_total_quenched_hardness(self, phase_fractions: Dict[str, float],
                                        phase_hardness: Dict[str, float]) -> float:
        """
        Calculate total as-quenched hardness using law of mixture (Equation 18)
        
        HV = HVa-f-p(Xa⁰ + Xf⁰ + Xp⁰) + HVb*Xb⁰ + HVm*Xm⁰
        
        Args:
            phase_fractions: Dictionary of phase fractions
            phase_hardness: Dictionary of individual phase hardness values
            
        Returns:
            Total hardness in Vickers
        """
        total_hardness = (phase_hardness['austenite_ferrite_pearlite'] *
                         (phase_fractions.get('austenite', 0) +
                          phase_fractions.get('ferrite', 0) +
                          phase_fractions.get('pearlite', 0)) +
                         phase_hardness['bainite'] * phase_fractions.get('bainite', 0) +
                         phase_hardness['martensite'] * phase_fractions.get('martensite', 0))
        
        return max(0.0, total_hardness)
    
    def calculate_jaffe_holloman_parameter(self, carbon_content: float) -> float:
        """
        Calculate Jaffe-Holloman material constant K using Equation (20)
        
        K = 21.3 - 5.8C
        
        Args:
            carbon_content: Carbon content in wt%
            
        Returns:
            Jaffe-Holloman parameter K
        """
        return 21.3 - 5.8 * carbon_content
    
    def calculate_equivalent_tempering_temperature(self, tempering_temp: float,
                                                 tempering_time: float,
                                                 carbon_content: float) -> float:
        """
        Calculate equivalent tempering temperature using Equation (21)
        
        Teq = [(Tt + 273)(K + log tt)/K] - 273
        
        Args:
            tempering_temp: Actual tempering temperature in °C
            tempering_time: Tempering time in hours
            carbon_content: Carbon content in wt%
            
        Returns:
            Equivalent temperature in °C
        """
        K = self.calculate_jaffe_holloman_parameter(carbon_content)
        
        if K <= 0:
            raise ValueError("Invalid Jaffe-Holloman parameter K")
            
        if tempering_time <= 0:
            raise ValueError("Tempering time must be positive")
            
        T_eq = ((tempering_temp + 273) * (K + math.log10(tempering_time)) / K) - 273
        
        return T_eq
    
    def calculate_tempering_factor(self, temperature: float, carbon_content: float) -> float:
        """
        Calculate tempering factor f using Equation (23)
        
        f = 1.304(1-0.0013323T)(1-0.3619482C) for C < 0.45
        f = 1.102574(1-0.0016554T)(1+0.19088063C) for C ≥ 0.45
        
        Args:
            temperature: Tempering temperature in °C
            carbon_content: Carbon content in wt%
            
        Returns:
            Tempering factor f
        """
        if carbon_content < 0.45:
            f = (1.304 * (1 - 0.0013323 * temperature) *
                (1 - 0.3619482 * carbon_content))
        else:
            f = (1.102574 * (1 - 0.0016554 * temperature) *
                (1 + 0.19088063 * carbon_content))
        
        return max(0.0, f)
    
    def calculate_tempered_martensite_hardness(self, as_quenched_hardness: float,
                                             tempering_temp: float, tempering_time: float,
                                             carbon_content: float) -> float:
        """
        Calculate tempered martensite hardness using Equations (22) and (23)
        
        HVmT = HVm × f
        
        Args:
            as_quenched_hardness: As-quenched martensite hardness
            tempering_temp: Tempering temperature in °C
            tempering_time: Tempering time in hours
            carbon_content: Carbon content in wt%
            
        Returns:
            Tempered martensite hardness
        """
        T_eq = self.calculate_equivalent_tempering_temperature(
            tempering_temp, tempering_time, carbon_content)
        
        f = self.calculate_tempering_factor(T_eq, carbon_content)
        
        return as_quenched_hardness * f
    
    def calculate_total_tempered_hardness(self, phase_fractions: Dict[str, float],
                                        as_quenched_hardness_values: Dict[str, float],
                                        tempering_temp: float, tempering_time: float,
                                        carbon_content: float) -> float:
        """
        Calculate total tempered hardness using Equation (24)
        
        HVT = HVa-f-p(Xa⁰ + Xf⁰ + Xp⁰) + HVb*Xb⁰ + HVmT*Xm⁰
        
        Args:
            phase_fractions: Dictionary of phase fractions
            as_quenched_hardness_values: Dictionary of as-quenched hardness values
            tempering_temp: Tempering temperature in °C
            tempering_time: Tempering time in hours
            carbon_content: Carbon content in wt%
            
        Returns:
            Total tempered hardness
        """
        tempered_martensite_hardness = self.calculate_tempered_martensite_hardness(
            as_quenched_hardness_values['martensite'], tempering_temp, 
            tempering_time, carbon_content)
        
        total_hardness = (as_quenched_hardness_values['austenite_ferrite_pearlite'] *
                         (phase_fractions.get('austenite', 0) +
                          phase_fractions.get('ferrite', 0) +
                          phase_fractions.get('pearlite', 0)) +
                         as_quenched_hardness_values['bainite'] * phase_fractions.get('bainite', 0) +
                         tempered_martensite_hardness * phase_fractions.get('martensite', 0))
        
        return max(0.0, total_hardness)
    
    def convert_vickers_to_rockwell(self, hv_hardness: float) -> float:
        """
        Convert Vickers hardness to Rockwell C scale using Equation (25)
        
        HRc = 193 log HV - 21.41(log HV)² - 316
        
        Args:
            hv_hardness: Vickers hardness value
            
        Returns:
            Rockwell C hardness
        """
        if hv_hardness <= 0:
            return 0.0
        
        log_hv = math.log10(hv_hardness)
        hrc = 193 * log_hv - 21.41 * (log_hv ** 2) - 316
        
        return max(0.0, hrc)
    
    def convert_rockwell_to_vickers(self, hrc_hardness: float) -> float:
        """
        Convert Rockwell C to Vickers hardness (inverse of Equation 25)
        
        Args:
            hrc_hardness: Rockwell C hardness value
            
        Returns:
            Vickers hardness
        """
        if hrc_hardness <= 0:
            return 0.0
        
        # Solve quadratic equation: 193x - 21.41x² - 316 = HRc
        # where x = log₁₀(HV)
        a = -21.41
        b = 193
        c = -316 - hrc_hardness
        
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            return 0.0
        
        # Take positive root
        x = (-b + math.sqrt(discriminant)) / (2*a)
        
        return 10**x
    
    def calculate_hardness_distribution(self, carbon_profile: np.ndarray,
                                       phase_fraction_profiles: Dict[str, np.ndarray],
                                       composition: SteelComposition,
                                       cooling_rate: float,
                                       tempering_temp: Optional[float] = None,
                                       tempering_time: Optional[float] = None) -> Dict:
        """
        Calculate hardness distribution along a profile (e.g., from surface to core)
        
        Args:
            carbon_profile: Carbon content distribution (wt%)
            phase_fraction_profiles: Phase fraction distributions
            composition: Base steel composition
            cooling_rate: Cooling rate (°C/hr)
            tempering_temp: Tempering temperature (°C), optional
            tempering_time: Tempering time (hours), optional
            
        Returns:
            Dictionary with hardness distributions
        """
        n_points = len(carbon_profile)
        
        # Initialize arrays
        hv_quenched = np.zeros(n_points)
        hv_tempered = np.zeros(n_points)
        hrc_quenched = np.zeros(n_points)
        hrc_tempered = np.zeros(n_points)
        
        for i in range(n_points):
            # Get local composition (modified carbon content)
            local_composition = SteelComposition(
                C=carbon_profile[i],
                Si=composition.Si, Mn=composition.Mn, Ni=composition.Ni,
                Cr=composition.Cr, Mo=composition.Mo, V=composition.V,
                W=composition.W, Cu=composition.Cu, P=composition.P,
                Al=composition.Al, As=composition.As, Ti=composition.Ti
            )
            
            # Calculate phase hardness
            phase_hardness = self.calculate_all_phase_hardness(local_composition, cooling_rate)
            
            # Get local phase fractions
            local_phase_fractions = {
                phase: profile[i] for phase, profile in phase_fraction_profiles.items()
            }
            
            # Calculate quenched hardness
            hv_quenched[i] = self.calculate_total_quenched_hardness(
                local_phase_fractions, phase_hardness)
            hrc_quenched[i] = self.convert_vickers_to_rockwell(hv_quenched[i])
            
            # Calculate tempered hardness if tempering conditions provided
            if tempering_temp is not None and tempering_time is not None:
                hv_tempered[i] = self.calculate_total_tempered_hardness(
                    local_phase_fractions, phase_hardness,
                    tempering_temp, tempering_time, carbon_profile[i])
                hrc_tempered[i] = self.convert_vickers_to_rockwell(hv_tempered[i])
            else:
                hv_tempered[i] = hv_quenched[i]
                hrc_tempered[i] = hrc_quenched[i]
        
        return {
            'carbon_profile': carbon_profile,
            'hv_quenched': hv_quenched,
            'hv_tempered': hv_tempered,
            'hrc_quenched': hrc_quenched,
            'hrc_tempered': hrc_tempered,
            'phase_fractions': phase_fraction_profiles
        }
    
    def calculate_case_depth_from_hardness(self, distance: np.ndarray,
                                         hardness_profile: np.ndarray,
                                         threshold_hardness: float,
                                         hardness_type: str = 'HRC') -> float:
        """
        Calculate case depth based on hardness criterion
        
        Args:
            distance: Distance from surface (m)
            hardness_profile: Hardness values along profile
            threshold_hardness: Threshold hardness for case depth
            hardness_type: Type of hardness ('HRC' or 'HV')
            
        Returns:
            Case depth (m)
        """
        for i, hardness in enumerate(hardness_profile):
            if hardness < threshold_hardness:
                if i == 0:
                    return 0.0
                
                # Linear interpolation
                x1, h1 = distance[i-1], hardness_profile[i-1]
                x2, h2 = distance[i], hardness_profile[i]
                
                case_depth = x1 + (x2 - x1) * (threshold_hardness - h1) / (h2 - h1)
                return case_depth
        
        return distance[-1]
    
    def validate_hardness_predictions(self, experimental_data: Dict,
                                    predicted_data: Dict,
                                    tolerance: float = 5.0) -> Dict:
        """
        Validate hardness predictions against experimental data
        
        Args:
            experimental_data: Experimental hardness measurements
            predicted_data: Predicted hardness values
            tolerance: Acceptable tolerance (HRC or HV units)
            
        Returns:
            Validation results
        """
        errors = []
        absolute_errors = []
        
        for exp_val, pred_val in zip(experimental_data.values(), predicted_data.values()):
            if isinstance(exp_val, (list, np.ndarray)):
                for e, p in zip(exp_val, pred_val):
                    error = p - e
                    abs_error = abs(error)
                    errors.append(error)
                    absolute_errors.append(abs_error)
            else:
                error = pred_val - exp_val
                abs_error = abs(error)
                errors.append(error)
                absolute_errors.append(abs_error)
        
        mean_error = np.mean(errors)
        mean_absolute_error = np.mean(absolute_errors)
        max_error = np.max(absolute_errors)
        rmse = np.sqrt(np.mean(np.array(errors)**2))
        
        within_tolerance = np.sum(np.array(absolute_errors) <= tolerance) / len(absolute_errors)
        
        return {
            'mean_error': mean_error,
            'mean_absolute_error': mean_absolute_error,
            'max_error': max_error,
            'rmse': rmse,
            'within_tolerance_fraction': within_tolerance,
            'tolerance': tolerance,
            'n_points': len(errors)
        }

# Standard hardness criteria for case depth determination
CASE_DEPTH_CRITERIA = {
    'automotive_gears': {
        'surface_hardness_min': 58,  # HRC
        'surface_hardness_max': 62,  # HRC
        'case_depth_threshold': 50,  # HRC
        'core_hardness_min': 32,     # HRC
        'core_hardness_max': 48      # HRC
    },
    'bearing_races': {
        'surface_hardness_min': 60,  # HRC
        'surface_hardness_max': 65,  # HRC
        'case_depth_threshold': 55,  # HRC
        'core_hardness_min': 30,     # HRC
        'core_hardness_max': 45      # HRC
    }
}

# Example usage
if __name__ == "__main__":
    from .phase_transformation import STEEL_COMPOSITIONS
    
    models = HardnessPredictionModels()
    
    # Test with 8620 steel
    steel_8620 = STEEL_COMPOSITIONS['8620']
    cooling_rate = 100.0  # °C/hr
    
    # Calculate phase hardness
    phase_hardness = models.calculate_all_phase_hardness(steel_8620, cooling_rate)
    print("Phase hardness values (HV):")
    for phase, hardness in phase_hardness.items():
        print(f"  {phase}: {hardness:.1f}")
    
    # Test total hardness calculation
    phase_fractions = {
        'austenite': 0.05,
        'ferrite': 0.0,
        'pearlite': 0.15,
        'bainite': 0.0,
        'martensite': 0.80
    }
    
    total_hv = models.calculate_total_quenched_hardness(phase_fractions, phase_hardness)
    total_hrc = models.convert_vickers_to_rockwell(total_hv)
    
    print(f"\nTotal as-quenched hardness:")
    print(f"  {total_hv:.1f} HV")
    print(f"  {total_hrc:.1f} HRC")
    
    # Test tempering calculations
    tempering_temp = 170  # °C
    tempering_time = 2    # hours
    carbon_content = 0.8  # wt% (carburized surface)
    
    tempered_hardness = models.calculate_total_tempered_hardness(
        phase_fractions, phase_hardness, tempering_temp, tempering_time, carbon_content)
    tempered_hrc = models.convert_vickers_to_rockwell(tempered_hardness)
    
    print(f"\nTempered hardness (170°C, 2h):")
    print(f"  {tempered_hardness:.1f} HV")
    print(f"  {tempered_hrc:.1f} HRC")
    
    # Test Jaffe-Holloman calculations
    K = models.calculate_jaffe_holloman_parameter(carbon_content)
    T_eq = models.calculate_equivalent_tempering_temperature(
        tempering_temp, tempering_time, carbon_content)
    f = models.calculate_tempering_factor(T_eq, carbon_content)
    
    print(f"\nTempering parameters:")
    print(f"  K parameter: {K:.1f}")
    print(f"  Equivalent temperature: {T_eq:.1f}°C")
    print(f"  Tempering factor: {f:.3f}")