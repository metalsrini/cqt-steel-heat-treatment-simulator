"""
Grain Growth Models for C-Q-T Process Chain
Implementation of grain growth kinetics during carburizing (Equations 2-4)
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from .phase_transformation import SteelComposition

@dataclass
class GrainGrowthParameters:
    """Parameters for grain growth simulation"""
    initial_grain_size: float     # Initial grain size (μm)
    temperature_profile: Callable # Temperature as function of time
    time_step: float             # Time step for integration (s)
    total_time: float           # Total time for simulation (s)

class GrainGrowthModels:
    """
    Implementation of grain growth models from the research paper
    """
    
    def __init__(self):
        self.R_gas_constant = 8.314  # J/mol.K
        self.K_o = 76671  # Pre-exponential constant
        self.n = 0.211    # Time exponent
        
    def calculate_activation_energy(self, composition: SteelComposition) -> float:
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
        Q = self.calculate_activation_energy(composition)
        
        D = (self.K_o * 
             math.exp(-Q / (self.R_gas_constant * (temperature + 273))) * 
             (time ** self.n))
        
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
        Q = self.calculate_activation_energy(composition)
        
        if time <= 0:
            return 0.0
            
        dD_dt = (self.K_o * 
                math.exp(-Q / (self.R_gas_constant * (temperature + 273))) *
                self.n * (time ** (self.n - 1)))
        
        return dD_dt
    
    def calculate_grain_size_non_isothermal(self, initial_grain_size: float,
                                          temperature_profile: Callable,
                                          time_array: np.ndarray,
                                          composition: SteelComposition) -> np.ndarray:
        """
        Calculate grain size evolution under non-isothermal conditions
        using numerical integration of the differential equation
        
        Args:
            initial_grain_size: Initial grain size (μm)
            temperature_profile: Function T(t) returning temperature at time t
            time_array: Array of time points (s)
            composition: Steel chemical composition
            
        Returns:
            Array of grain sizes at each time point (μm)
        """
        grain_sizes = np.zeros_like(time_array)
        grain_sizes[0] = initial_grain_size
        
        for i in range(1, len(time_array)):
            dt = time_array[i] - time_array[i-1]
            t_current = time_array[i-1]
            T_current = temperature_profile(t_current)
            
            # Calculate growth rate at current conditions
            dD_dt = self.calculate_grain_growth_rate(T_current, t_current, composition)
            
            # Euler integration
            grain_sizes[i] = grain_sizes[i-1] + dD_dt * dt
            
            # Ensure grain size doesn't decrease
            grain_sizes[i] = max(grain_sizes[i], grain_sizes[i-1])
        
        return grain_sizes
    
    def calculate_grain_size_runge_kutta(self, initial_grain_size: float,
                                       temperature_profile: Callable,
                                       time_array: np.ndarray,
                                       composition: SteelComposition) -> np.ndarray:
        """
        Calculate grain size evolution using 4th order Runge-Kutta method
        for improved accuracy
        
        Args:
            initial_grain_size: Initial grain size (μm)
            temperature_profile: Function T(t) returning temperature at time t
            time_array: Array of time points (s)
            composition: Steel chemical composition
            
        Returns:
            Array of grain sizes at each time point (μm)
        """
        grain_sizes = np.zeros_like(time_array)
        grain_sizes[0] = initial_grain_size
        
        for i in range(1, len(time_array)):
            dt = time_array[i] - time_array[i-1]
            t = time_array[i-1]
            D = grain_sizes[i-1]
            
            # RK4 coefficients
            k1 = dt * self._growth_rate_function(t, D, temperature_profile, composition)
            k2 = dt * self._growth_rate_function(t + dt/2, D + k1/2, temperature_profile, composition)
            k3 = dt * self._growth_rate_function(t + dt/2, D + k2/2, temperature_profile, composition)
            k4 = dt * self._growth_rate_function(t + dt, D + k3, temperature_profile, composition)
            
            grain_sizes[i] = D + (k1 + 2*k2 + 2*k3 + k4) / 6
            
            # Ensure grain size doesn't decrease
            grain_sizes[i] = max(grain_sizes[i], grain_sizes[i-1])
        
        return grain_sizes
    
    def _growth_rate_function(self, time: float, grain_size: float,
                            temperature_profile: Callable,
                            composition: SteelComposition) -> float:
        """
        Helper function for numerical integration methods
        
        Args:
            time: Current time (s)
            grain_size: Current grain size (μm) - not used in current model
            temperature_profile: Temperature function
            composition: Steel composition
            
        Returns:
            Growth rate at current conditions
        """
        temperature = temperature_profile(time)
        return self.calculate_grain_growth_rate(temperature, time, composition)
    
    def calculate_equivalent_isothermal_time(self, temperature_profile: Callable,
                                           time_array: np.ndarray,
                                           reference_temperature: float,
                                           composition: SteelComposition) -> float:
        """
        Calculate equivalent isothermal time at reference temperature
        
        Args:
            temperature_profile: Temperature function T(t)
            time_array: Array of time points (s)
            reference_temperature: Reference temperature (°C)
            composition: Steel composition
            
        Returns:
            Equivalent isothermal time (s)
        """
        Q = self.calculate_activation_energy(composition)
        
        # Reference growth rate factor
        ref_factor = math.exp(-Q / (self.R_gas_constant * (reference_temperature + 273)))
        
        equivalent_time = 0.0
        
        for i in range(1, len(time_array)):
            dt = time_array[i] - time_array[i-1]
            T_avg = 0.5 * (temperature_profile(time_array[i-1]) + 
                          temperature_profile(time_array[i]))
            
            # Growth rate factor at current temperature
            current_factor = math.exp(-Q / (self.R_gas_constant * (T_avg + 273)))
            
            # Equivalent time increment
            equivalent_time += dt * (current_factor / ref_factor)
        
        return equivalent_time
    
    def calculate_astm_grain_number(self, grain_diameter: float) -> float:
        """
        Convert grain diameter to ASTM grain number
        
        ASTM Grain Number G = 1 + 3.322 * log₁₀(N)
        where N = number of grains per square inch at 100x magnification
        
        Args:
            grain_diameter: Grain diameter in μm
            
        Returns:
            ASTM grain number
        """
        if grain_diameter <= 0:
            return 0.0
        
        # Convert μm to mm
        diameter_mm = grain_diameter / 1000
        
        # Number of grains per mm² (approximate)
        grains_per_mm2 = 1.0 / (diameter_mm ** 2)
        
        # Convert to grains per square inch at 100x
        grains_per_inch2_100x = grains_per_mm2 * (25.4 ** 2) / (100 ** 2)
        
        # ASTM grain number
        G = 1 + 3.322 * math.log10(grains_per_inch2_100x)
        
        return G
    
    def calculate_grain_diameter_from_astm(self, astm_grain_number: float) -> float:
        """
        Convert ASTM grain number to grain diameter
        
        Args:
            astm_grain_number: ASTM grain number
            
        Returns:
            Grain diameter in μm
        """
        # Number of grains per square inch at 100x
        N = 10 ** ((astm_grain_number - 1) / 3.322)
        
        # Convert to grains per mm²
        grains_per_mm2 = N * (100 ** 2) / (25.4 ** 2)
        
        # Grain diameter in mm
        diameter_mm = 1.0 / math.sqrt(grains_per_mm2)
        
        # Convert to μm
        return diameter_mm * 1000
    
    def simulate_carburizing_grain_growth(self, initial_grain_size: float,
                                        carburizing_temperature: float,
                                        carburizing_time: float,
                                        composition: SteelComposition,
                                        heating_rate: float = 5.0) -> Dict:
        """
        Simulate grain growth during complete carburizing cycle
        
        Args:
            initial_grain_size: Initial grain size (μm)
            carburizing_temperature: Carburizing temperature (°C)
            carburizing_time: Time at carburizing temperature (hours)
            composition: Steel composition
            heating_rate: Heating rate (°C/min)
            
        Returns:
            Dictionary with simulation results
        """
        # Convert times to seconds
        carb_time_s = carburizing_time * 3600
        heating_time_s = carburizing_temperature / heating_rate * 60
        
        # Create time array
        total_time = heating_time_s + carb_time_s
        time_step = min(60.0, total_time / 1000)  # 1 minute or 1/1000 of total time
        time_array = np.arange(0, total_time + time_step, time_step)
        
        # Define temperature profile
        def temperature_profile(t):
            if t <= heating_time_s:
                return 25 + heating_rate * t / 60  # Heating from room temperature
            else:
                return carburizing_temperature  # Holding at carburizing temperature
        
        # Calculate grain growth
        grain_sizes = self.calculate_grain_size_runge_kutta(
            initial_grain_size, temperature_profile, time_array, composition)
        
        # Calculate ASTM grain numbers
        astm_numbers = [self.calculate_astm_grain_number(d) for d in grain_sizes]
        
        # Calculate equivalent isothermal time
        equiv_time = self.calculate_equivalent_isothermal_time(
            temperature_profile, time_array, carburizing_temperature, composition)
        
        return {
            'time_array': time_array,
            'temperature_profile': [temperature_profile(t) for t in time_array],
            'grain_sizes': grain_sizes,
            'astm_grain_numbers': astm_numbers,
            'final_grain_size': grain_sizes[-1],
            'final_astm_number': astm_numbers[-1],
            'equivalent_isothermal_time': equiv_time / 3600,  # Convert to hours
            'grain_growth_factor': grain_sizes[-1] / initial_grain_size
        }
    
    def compare_steel_compositions(self, compositions: Dict[str, SteelComposition],
                                 temperature: float = 920,
                                 time: float = 6) -> Dict:
        """
        Compare grain growth behavior for different steel compositions
        
        Args:
            compositions: Dictionary of steel compositions
            temperature: Temperature (°C)
            time: Time (hours)
            
        Returns:
            Comparison results
        """
        time_s = time * 3600
        results = {}
        
        for name, composition in compositions.items():
            Q = self.calculate_activation_energy(composition)
            grain_size = self.calculate_grain_size_isothermal(temperature, time_s, composition)
            growth_rate = self.calculate_grain_growth_rate(temperature, time_s, composition)
            astm_number = self.calculate_astm_grain_number(grain_size)
            
            results[name] = {
                'activation_energy': Q,
                'grain_size': grain_size,
                'growth_rate': growth_rate,
                'astm_grain_number': astm_number,
                'composition': composition
            }
        
        return results

# Standard initial grain sizes for different steel conditions
STANDARD_INITIAL_GRAIN_SIZES = {
    'fine_grained': 10.0,      # μm (ASTM 10-12)
    'medium_grained': 25.0,    # μm (ASTM 7-8)
    'coarse_grained': 50.0,    # μm (ASTM 4-5)
    'very_coarse': 100.0       # μm (ASTM 1-2)
}

# Example usage
if __name__ == "__main__":
    from .phase_transformation import STEEL_COMPOSITIONS
    
    models = GrainGrowthModels()
    
    # Test activation energy calculation
    steel_8620 = STEEL_COMPOSITIONS['8620']
    Q = models.calculate_activation_energy(steel_8620)
    print(f"Activation energy for 8620 steel: {Q:,.0f} J/mol")
    
    # Test isothermal grain growth
    temp = 920  # °C
    time_hours = 6
    time_s = time_hours * 3600
    initial_size = 20.0  # μm
    
    final_size = models.calculate_grain_size_isothermal(temp, time_s, steel_8620)
    print(f"Grain size after {time_hours}h at {temp}°C: {final_size:.1f} μm")
    
    # Test ASTM conversion
    astm = models.calculate_astm_grain_number(final_size)
    print(f"ASTM grain number: {astm:.1f}")
    
    # Test complete carburizing simulation
    results = models.simulate_carburizing_grain_growth(
        initial_grain_size=20.0,
        carburizing_temperature=920,
        carburizing_time=6.0,
        composition=steel_8620,
        heating_rate=5.0
    )
    
    print(f"\nCarburizing simulation results:")
    print(f"Initial grain size: {results['grain_sizes'][0]:.1f} μm")
    print(f"Final grain size: {results['final_grain_size']:.1f} μm")
    print(f"Final ASTM number: {results['final_astm_number']:.1f}")
    print(f"Grain growth factor: {results['grain_growth_factor']:.2f}")
    print(f"Equivalent isothermal time: {results['equivalent_isothermal_time']:.1f} hours")
    
    # Compare different steels
    comparison = models.compare_steel_compositions(
        {'8620': STEEL_COMPOSITIONS['8620'],
         '4320': STEEL_COMPOSITIONS['4320'],
         '4130': STEEL_COMPOSITIONS['4130']},
        temperature=920, time=6)
    
    print(f"\nSteel comparison at 920°C for 6 hours:")
    for steel, data in comparison.items():
        print(f"{steel}: Q = {data['activation_energy']:,.0f} J/mol, "
              f"Final size = {data['grain_size']:.1f} μm, "
              f"ASTM = {data['astm_grain_number']:.1f}")