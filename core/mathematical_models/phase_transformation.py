"""
Phase Transformation Models for C-Q-T Process Chain
Exact implementation of equations from the research paper:
"Integrated Modeling of Carburizing-Quenching-Tempering of Steel Gears for an ICME Framework"
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SteelComposition:
    """
    Steel chemical composition in weight percent
    Based on the compositions used in the research paper
    """
    C: float = 0.0    # Carbon
    Si: float = 0.0   # Silicon
    Mn: float = 0.0   # Manganese
    Ni: float = 0.0   # Nickel
    Cr: float = 0.0   # Chromium
    Mo: float = 0.0   # Molybdenum
    V: float = 0.0    # Vanadium
    W: float = 0.0    # Tungsten
    Cu: float = 0.0   # Copper
    P: float = 0.0    # Phosphorus
    Al: float = 0.0   # Aluminum
    As: float = 0.0   # Arsenic
    Ti: float = 0.0   # Titanium

    def __post_init__(self):
        """Validate composition values"""
        for element, value in self.__dict__.items():
            if value < 0:
                raise ValueError(f"{element} content cannot be negative: {value}")

class PhaseTransformationModels:
    """
    Implementation of all phase transformation models from the paper
    """
    
    def __init__(self):
        self.R_gas_constant = 8.314  # J/mol.K
        self.R_gas_constant_cal = 1.987  # cal/mol.K
        
    def calculate_ae3_temperature(self, composition: SteelComposition) -> float:
        """
        Calculate AE3 temperature using Equation (1) from the paper
        
        AE3(°C) = 912 - 203√C - 15.2Ni + 44.7Si + 104V + 31.5Mo + 13.1W
                  - 30Mn - 11Cr - 20Cu + 700P + 400Al + 120As + 400Ti
        
        Args:
            composition: Steel chemical composition
            
        Returns:
            AE3 temperature in °C
        """
        ae3 = (912 - 203 * math.sqrt(composition.C) - 15.2 * composition.Ni +
               44.7 * composition.Si + 104 * composition.V + 31.5 * composition.Mo +
               13.1 * composition.W - 30 * composition.Mn - 11 * composition.Cr -
               20 * composition.Cu + 700 * composition.P + 400 * composition.Al +
               120 * composition.As + 400 * composition.Ti)
        
        return ae3
    
    def calculate_ae1_temperature(self, composition: SteelComposition) -> float:
        """
        Calculate AE1 (eutectoid) temperature
        
        AE1 is the temperature at which austenite transforms to ferrite + cementite
        Base temperature is 727°C for pure iron-carbon, modified by alloying elements
        
        Args:
            composition: Steel chemical composition
            
        Returns:
            AE1 temperature in °C
        """
        # Base eutectoid temperature for pure iron-carbon system
        ae1 = 727.0
        
        # Corrections for alloying elements (typical values from literature)
        ae1 += (-10.0 * composition.Mn +  # Mn lowers AE1
                -5.0 * composition.Cr +   # Cr lowers AE1
                -8.0 * composition.Ni +   # Ni lowers AE1
                +12.0 * composition.Si +  # Si raises AE1
                +15.0 * composition.Mo +  # Mo raises AE1
                -30.0 * composition.C +   # C content effect
                +20.0 * composition.Al +  # Al raises AE1
                +10.0 * composition.V)    # V raises AE1
        
        # Ensure reasonable bounds (typical range 680-750°C)
        ae1 = max(680.0, min(750.0, ae1))
        
        return ae1
    
    def calculate_grain_growth_activation_energy(self, composition: SteelComposition) -> float:
        """
        Calculate activation energy for grain growth using Equation (3)
        
        Q(J/mol) = 89,098 + 3581C + 1211Ni + 1443Cr + 4031Mo
        
        Args:
            composition: Steel chemical composition
            
        Returns:
            Activation energy in J/mol
        """
        Q = (89098 + 3581 * composition.C + 1211 * composition.Ni +
             1443 * composition.Cr + 4031 * composition.Mo)
        
        return Q
    
    def calculate_grain_size_isothermal(self, temperature: float, time: float, 
                                      composition: SteelComposition) -> float:
        """
        Calculate grain size under isothermal conditions using Equation (2)
        
        D = K₀ * exp(-Q/R(T+273)) * t^n
        
        Args:
            temperature: Temperature in °C
            time: Time in seconds
            composition: Steel chemical composition
            
        Returns:
            Austenite grain diameter in μm
        """
        K_o = 76671  # pre-exponential constant
        n = 0.211    # time exponent
        
        Q = self.calculate_grain_growth_activation_energy(composition)
        
        D = (K_o * math.exp(-Q / (self.R_gas_constant * (temperature + 273))) * 
             (time ** n))
        
        return D
    
    def calculate_grain_growth_rate(self, temperature: float, time: float, 
                                  composition: SteelComposition) -> float:
        """
        Calculate grain growth rate using Equation (4) - differential form
        
        dD/dt = K₀ * exp(-Q/R(T+273)) * n * t^(n-1)
        
        Args:
            temperature: Temperature in °C
            time: Time in seconds
            composition: Steel chemical composition
            
        Returns:
            Grain growth rate dD/dt in μm/s
        """
        K_o = 76671  # pre-exponential constant
        n = 0.211    # time exponent
        
        Q = self.calculate_grain_growth_activation_energy(composition)
        
        if time <= 0:
            return 0.0
            
        dD_dt = (K_o * math.exp(-Q / (self.R_gas_constant * (temperature + 273))) *
                n * (time ** (n - 1)))
        
        return dD_dt
    
    def calculate_carbon_diffusion_q_factor(self, composition: SteelComposition) -> float:
        """
        Calculate q factor for carbon diffusivity using Equation (10)
        
        q = 1 + (0.15+0.033Si)Si - 0.0365Mn - (0.13-0.0055Cr)Cr 
            + (0.03-0.03365Ni)Ni - (0.025-0.01Mo)Mo - (0.03-0.02Al)Al
            - (0.016+0.0014Cu)Cu - (0.22-0.01V)V
        
        Args:
            composition: Steel chemical composition
            
        Returns:
            q factor (dimensionless)
        """
        q = (1 + (0.15 + 0.033 * composition.Si) * composition.Si -
             0.0365 * composition.Mn -
             (0.13 - 0.0055 * composition.Cr) * composition.Cr +
             (0.03 - 0.03365 * composition.Ni) * composition.Ni -
             (0.025 - 0.01 * composition.Mo) * composition.Mo -
             (0.03 - 0.02 * composition.Al) * composition.Al -
             (0.016 + 0.0014 * composition.Cu) * composition.Cu -
             (0.22 - 0.01 * composition.V) * composition.V)
        
        return q
    
    def calculate_carbon_diffusivity(self, temperature: float, carbon_content: float,
                                   composition: SteelComposition) -> float:
        """
        Calculate carbon diffusivity using Equations (9) and (10)
        
        D(m²/s) = 0.47×10⁻⁴ * exp(-1.6C - (37000-6600C)/R(T+273)) * q
        
        Args:
            temperature: Temperature in °C
            carbon_content: Local carbon content in wt%
            composition: Steel chemical composition
            
        Returns:
            Carbon diffusivity in m²/s
        """
        q = self.calculate_carbon_diffusion_q_factor(composition)
        
        # Calculate diffusivity (Equation 9)
        D = (0.47e-4 * math.exp(-1.6 * carbon_content -
             (37000 - 6600 * carbon_content) / (self.R_gas_constant_cal * (temperature + 273))) * q)
        
        return D
    
    def calculate_carbon_mass_transfer_flux(self, beta: float, carbon_potential: float, 
                                          surface_carbon: float) -> float:
        """
        Calculate carbon mass transfer flux using Equation (5)
        
        J = β(Cp - Cs)
        
        Args:
            beta: Mass transfer coefficient (cm/s)
            carbon_potential: Carbon potential of atmosphere (wt%)
            surface_carbon: Carbon concentration at steel surface (wt%)
            
        Returns:
            Carbon flux (wt%·cm/s)
        """
        return beta * (carbon_potential - surface_carbon)
    
    def calculate_ms_temperature_correction_factor(self, carbon_content: float) -> float:
        """
        Calculate correction factor for Ms temperature using Equation (14)
        
        CF = 0.0 (for C < 0.53%)
        CF = 242.42C³ - 357.26C² + 272.65C - 80.103 (for C > 0.53%)
        
        Args:
            carbon_content: Carbon content in wt%
            
        Returns:
            Correction factor CF
        """
        if carbon_content < 0.53:
            return 0.0
        else:
            return (242.42 * (carbon_content ** 3) - 357.26 * (carbon_content ** 2) +
                   272.65 * carbon_content - 80.103)
    
    def calculate_ms_temperature(self, composition: SteelComposition) -> float:
        """
        Calculate martensite start temperature using Equations (13) and (14)
        
        Ms(°C) = 561 - 474C - 33Mn - 17Ni - 17Cr - 21Mo + CF
        
        Args:
            composition: Steel chemical composition
            
        Returns:
            Ms temperature in °C
        """
        C_F = self.calculate_ms_temperature_correction_factor(composition.C)
        
        ms_temp = (561 - 474 * composition.C - 33 * composition.Mn -
                   17 * composition.Ni - 17 * composition.Cr -
                   21 * composition.Mo + C_F)
        
        return ms_temp
    
    def calculate_martensitic_transformation(self, temperature: float, ms_temperature: float,
                                           retained_austenite_fraction: float) -> float:
        """
        Calculate martensitic transformation using Koistinen-Marbuger equation (12)
        
        Xm⁰ = Xa-Ms⁰ * (1 - exp(-0.011(Ms - T)))
        
        Args:
            temperature: Current temperature in °C
            ms_temperature: Ms temperature in °C
            retained_austenite_fraction: Austenite fraction at Ms temperature
            
        Returns:
            Martensite fraction formed
        """
        if temperature >= ms_temperature:
            return 0.0
        
        martensite_fraction = (retained_austenite_fraction *
                              (1 - math.exp(-0.011 * (ms_temperature - temperature))))
        
        return martensite_fraction
    
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
        
        return hv_afp
    
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
        
        return hv_b
    
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
        
        return hv_m
    
    def calculate_phase_hardness(self, composition: SteelComposition, 
                                cooling_rate: float) -> Dict[str, float]:
        """
        Calculate individual phase hardness using Maynier equations (15-17)
        
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
        
        return total_hardness
    
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
        
        return max(0.0, f)  # Ensure non-negative factor
    
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
        # Calculate tempered martensite hardness
        tempered_martensite_hardness = self.calculate_tempered_martensite_hardness(
            as_quenched_hardness_values['martensite'], tempering_temp, 
            tempering_time, carbon_content)
        
        # Calculate total hardness (assuming only martensite is affected by tempering)
        total_hardness = (as_quenched_hardness_values['austenite_ferrite_pearlite'] *
                         (phase_fractions.get('austenite', 0) +
                          phase_fractions.get('ferrite', 0) +
                          phase_fractions.get('pearlite', 0)) +
                         as_quenched_hardness_values['bainite'] * phase_fractions.get('bainite', 0) +
                         tempered_martensite_hardness * phase_fractions.get('martensite', 0))
        
        return total_hardness
    
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
        
        return max(0.0, hrc)  # Ensure non-negative result
    
    def calculate_phase_fractions(self, composition: SteelComposition, cooling_rate: float, 
                                 tempering_temp: float) -> Dict[str, float]:
        """
        Calculate phase fractions based on composition, cooling rate, and tempering temperature
        
        Args:
            composition: Steel composition
            cooling_rate: Cooling rate (°C/s)
            tempering_temp: Tempering temperature (°C)
            
        Returns:
            Dictionary of phase fractions
        """
        # Calculate critical cooling rate for martensite formation
        # Simplified model - in practice would use CCT diagrams
        critical_cooling_rate = 50.0 * (1 - 0.5 * composition.C) * (1 - 0.1 * composition.Cr - 0.05 * composition.Ni)
        
        # Calculate Ms temperature
        ms_temp = self.calculate_ms_temperature(composition)
        
        # Determine phase fractions based on cooling rate
        if cooling_rate > critical_cooling_rate:
            # Fast cooling - predominantly martensite
            martensite_fraction = 0.9 - 0.1 * (tempering_temp / 200.0)  # Reduced by tempering
            bainite_fraction = 0.05
            ferrite_fraction = 0.03
            pearlite_fraction = 0.02
        elif cooling_rate > critical_cooling_rate * 0.1:
            # Intermediate cooling - mixed microstructure
            martensite_fraction = 0.6 - 0.2 * (tempering_temp / 200.0)
            bainite_fraction = 0.25
            ferrite_fraction = 0.1
            pearlite_fraction = 0.05
        else:
            # Slow cooling - ferrite + pearlite
            martensite_fraction = 0.1
            bainite_fraction = 0.1
            ferrite_fraction = 0.4
            pearlite_fraction = 0.4
        
        # Normalize fractions
        total = martensite_fraction + bainite_fraction + ferrite_fraction + pearlite_fraction
        
        return {
            'martensite': martensite_fraction / total,
            'bainite': bainite_fraction / total,
            'ferrite': ferrite_fraction / total,
            'pearlite': pearlite_fraction / total,
            'austenite': 0.0  # Retained austenite - simplified to 0
        }

# Standard steel compositions from the research paper
STEEL_COMPOSITIONS = {
    'SCR420': SteelComposition(C=0.18, Si=0.15, Mn=0.65, Ni=0.25, Cr=1.00, Mo=0.20),
    'JIS_SCR420H': SteelComposition(C=0.20, Si=0.25, Mn=0.80, Ni=0.25, Cr=1.20, Mo=0.20),
    'SAE_4320': SteelComposition(C=0.20, Si=0.25, Mn=0.65, Ni=1.75, Cr=0.50, Mo=0.25),
    '8620': SteelComposition(C=0.20, Si=0.25, Mn=0.80, Ni=0.50, Cr=0.50, Mo=0.20),
    '4130': SteelComposition(C=0.30, Si=0.25, Mn=0.50, Ni=0.25, Cr=0.95, Mo=0.20),
    '4320': SteelComposition(C=0.20, Si=0.25, Mn=0.65, Ni=1.75, Cr=0.50, Mo=0.25),
}

# Example usage and validation
if __name__ == "__main__":
    # Test with 8620 steel composition from the paper
    steel_8620 = STEEL_COMPOSITIONS['8620']
    
    models = PhaseTransformationModels()
    
    # Test critical temperature calculations
    ae3 = models.calculate_ae3_temperature(steel_8620)
    ms_temp = models.calculate_ms_temperature(steel_8620)
    
    print(f"8620 Steel Properties:")
    print(f"AE3 Temperature: {ae3:.1f}°C")
    print(f"Ms Temperature: {ms_temp:.1f}°C")
    
    # Test hardness calculations
    cooling_rate = 100.0  # °C/hr
    phase_hardness = models.calculate_phase_hardness(steel_8620, cooling_rate)
    
    print(f"\nPhase Hardness Values (at {cooling_rate}°C/hr cooling):")
    for phase, hardness in phase_hardness.items():
        print(f"  {phase}: {hardness:.1f} HV")
    
    # Test conversion
    hv_sample = 600.0
    hrc = models.convert_vickers_to_rockwell(hv_sample)
    print(f"\nHardness Conversion:")
    print(f"{hv_sample} HV = {hrc:.1f} HRc")
    
    # Test tempering calculations
    tempering_temp = 170.0  # °C
    tempering_time = 2.0    # hours
    carbon_content = 0.8    # wt% (carburized surface)
    
    T_eq = models.calculate_equivalent_tempering_temperature(
        tempering_temp, tempering_time, carbon_content)
    f = models.calculate_tempering_factor(T_eq, carbon_content)
    
    print(f"\nTempering Calculations:")
    print(f"Equivalent Temperature: {T_eq:.1f}°C")
    print(f"Tempering Factor: {f:.3f}")