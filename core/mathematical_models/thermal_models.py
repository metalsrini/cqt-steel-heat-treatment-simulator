"""
Thermal Modeling for C-Q-T Process Chain
Implementation of Fourier heat conduction with convective and radiative boundary conditions
Equations (26-29) from the research paper
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass

@dataclass
class ThermalProperties:
    """Thermal properties of steel phases"""
    density: float          # kg/m³
    specific_heat: float    # J/kg.K
    thermal_conductivity: float  # W/m.K
    emissivity: float = 0.8     # Surface emissivity

class ThermalModels:
    """
    Implementation of thermal modeling equations from the paper
    """
    
    def __init__(self):
        self.stefan_boltzmann = 5.67e-8  # W/m².K⁴
        
    def fourier_heat_conduction_3d(self, temperature: np.ndarray,
                                  thermal_properties: ThermalProperties,
                                  heat_generation: float = 0.0) -> np.ndarray:
        """
        3D Fourier heat conduction equation (Equation 26)
        
        ρc(∂T/∂t) = ∇·(k(∇T)) + q̇
        
        Args:
            temperature: Temperature field
            thermal_properties: Material thermal properties
            heat_generation: Rate of latent heat evolution
            
        Returns: 
            ∂T/∂t for time integration
        """
        rho = thermal_properties.density
        c = thermal_properties.specific_heat
        k = thermal_properties.thermal_conductivity
        
        # This is the governing equation structure
        # In actual FEM implementation, spatial derivatives would be computed
        # by the finite element discretization
        
        # Placeholder for spatial derivatives - would be computed by FEM solver
        laplacian_T = np.zeros_like(temperature)  # ∇²T approximation
        
        dT_dt = (k * laplacian_T + heat_generation) / (rho * c)
        
        return dT_dt
    
    def convective_heat_flux(self, heat_transfer_coefficient: float,
                           medium_temperature: float,
                           surface_temperature: float) -> float:
        """
        Convective heat flux calculation (Equation 27)
        
        Ψc = h(Tm - Ts)
        
        Args:
            heat_transfer_coefficient: Convective heat transfer coefficient (W/m².K)
            medium_temperature: Medium temperature (K)
            surface_temperature: Surface temperature (K)
            
        Returns:
            Convective heat flux (W/m²)
        """
        return heat_transfer_coefficient * (medium_temperature - surface_temperature)
    
    def radiative_heat_flux(self, emissivity: float,
                          medium_temperature: float,
                          surface_temperature: float) -> float:
        """
        Radiative heat flux calculation (Equation 28)
        
        Ψr = σε(Tm⁴ - Ts⁴)
        
        Args:
            emissivity: Surface emissivity
            medium_temperature: Medium temperature (K)
            surface_temperature: Surface temperature (K)
            
        Returns:
            Radiative heat flux (W/m²)
        """
        return (self.stefan_boltzmann * emissivity *
                (medium_temperature**4 - surface_temperature**4))
    
    def total_heat_flux(self, heat_transfer_coefficient: float,
                       emissivity: float,
                       medium_temperature: float,
                       surface_temperature: float) -> float:
        """
        Total heat flux combining convection and radiation
        
        Args:
            heat_transfer_coefficient: Convective heat transfer coefficient
            emissivity: Surface emissivity
            medium_temperature: Medium temperature (K)
            surface_temperature: Surface temperature (K)
            
        Returns:
            Total heat flux (W/m²)
        """
        convective = self.convective_heat_flux(heat_transfer_coefficient,
                                             medium_temperature,
                                             surface_temperature)
        radiative = self.radiative_heat_flux(emissivity,
                                           medium_temperature,
                                           surface_temperature)
        
        return convective + radiative
    
    def calculate_mixed_thermal_properties(self, phase_fractions: Dict[str, float],
                                         phase_properties: Dict[str, ThermalProperties],
                                         temperature: float) -> ThermalProperties:
        """
        Calculate thermal properties using rule of mixtures (Equation 29)
        
        P(T) = Σ P(T)k * Xk⁰
        
        Args:
            phase_fractions: Dictionary of phase fractions
            phase_properties: Dictionary of thermal properties for each phase
            temperature: Current temperature
            
        Returns:
            Mixed thermal properties
        """
        total_density = 0.0
        total_specific_heat = 0.0
        total_conductivity = 0.0
        total_emissivity = 0.0
        
        for phase, fraction in phase_fractions.items():
            if phase in phase_properties:
                props = phase_properties[phase]
                total_density += props.density * fraction
                total_specific_heat += props.specific_heat * fraction
                total_conductivity += props.thermal_conductivity * fraction
                total_emissivity += props.emissivity * fraction
        
        return ThermalProperties(
            density=total_density,
            specific_heat=total_specific_heat,
            thermal_conductivity=total_conductivity,
            emissivity=total_emissivity
        )
    
    def temperature_dependent_properties(self, base_properties: ThermalProperties,
                                       temperature: float) -> ThermalProperties:
        """
        Calculate temperature-dependent thermal properties
        
        Args:
            base_properties: Base thermal properties at reference temperature
            temperature: Current temperature in °C
            
        Returns:
            Temperature-adjusted thermal properties
        """
        # Simple temperature dependence - in practice would use more sophisticated models
        temp_factor = 1.0 + 0.0001 * (temperature - 20)  # Simplified temperature dependence
        
        return ThermalProperties(
            density=base_properties.density * (1.0 - 0.00001 * (temperature - 20)),
            specific_heat=base_properties.specific_heat * temp_factor,
            thermal_conductivity=base_properties.thermal_conductivity * (1.0 - 0.0001 * (temperature - 20)),
            emissivity=base_properties.emissivity
        )
    
    def calculate_cooling_rate(self, initial_temp: float, final_temp: float, 
                              quench_medium: str, characteristic_dimension: float) -> float:
        """
        Calculate cooling rate during quenching
        
        Args:
            initial_temp: Initial temperature before quenching (°C)
            final_temp: Final temperature after quenching (°C)
            quench_medium: Quenching medium ('oil', 'water', 'air', 'polymer')
            characteristic_dimension: Characteristic dimension of part (mm)
            
        Returns:
            Cooling rate (°C/s)
        """
        # Heat transfer coefficients for different quenching media (W/m².K)
        heat_transfer_coeffs = {
            'water': 3000,
            'oil': 1200,
            'polymer': 800,
            'air': 50
        }
        heat_transfer_coeff = heat_transfer_coeffs.get(quench_medium, 1200)
        
        # Convert characteristic dimension from mm to m
        char_length = characteristic_dimension / 1000.0
        
        # Steel thermal properties
        k_steel = 30.0  # Thermal conductivity (W/m.K)
        rho_steel = 7850.0  # Density (kg/m³)
        cp_steel = 500.0  # Specific heat (J/kg.K)
        alpha = k_steel / (rho_steel * cp_steel)  # Thermal diffusivity (m²/s)
        
        # Calculate Biot number
        biot_number = heat_transfer_coeff * char_length / k_steel
        
        # Characteristic time for cooling
        characteristic_time = char_length**2 / alpha
        
        # Cooling rate factor based on Biot number
        cooling_factor = biot_number / (1 + biot_number)
        
        # Calculate initial cooling rate (°C/s)
        # This is the instantaneous cooling rate at the beginning of quenching
        delta_temp = initial_temp - final_temp
        cooling_rate = (delta_temp * cooling_factor) / characteristic_time
        
        # Typical cooling rates for validation:
        # Water quench: 100-1000 °C/s
        # Oil quench: 10-100 °C/s  
        # Air cooling: 0.1-10 °C/s
        
        # Ensure reasonable bounds
        max_rates = {
            'water': 1000,
            'oil': 100,
            'polymer': 50,
            'air': 10
        }
        max_rate = max_rates.get(quench_medium, 100)
        
        return min(cooling_rate, max_rate)
    
    def calculate_thermal_cycle(self, carburizing_temp: float, carburizing_time: float,
                               quench_temp: float, quench_time: float,
                               tempering_temp: float, tempering_time: float) -> Dict[str, List[float]]:
        """
        Calculate complete thermal cycle profile
        
        Args:
            carburizing_temp: Carburizing temperature (°C)
            carburizing_time: Carburizing time (hours)
            quench_temp: Quench temperature (°C)
            quench_time: Quench time (seconds)
            tempering_temp: Tempering temperature (°C)
            tempering_time: Tempering time (hours)
            
        Returns:
            Dictionary with time and temperature arrays for thermal profile
        """
        # Create time arrays for each phase
        carb_time_points = np.linspace(0, carburizing_time * 3600, 100)  # Convert to seconds
        quench_time_points = np.linspace(0, quench_time, 50)
        temper_time_points = np.linspace(0, tempering_time * 3600, 100)  # Convert to seconds
        
        # Calculate temperature profiles for each phase
        carb_temps = np.full_like(carb_time_points, carburizing_temp)
        
        # Exponential cooling during quenching
        quench_temps = quench_temp + (carburizing_temp - quench_temp) * np.exp(-quench_time_points / (quench_time / 5))
        
        # Tempering profile (heating + holding + cooling)
        temper_temps = np.full_like(temper_time_points, tempering_temp)
        
        # Combine all phases
        total_time = np.concatenate([
            carb_time_points,
            carb_time_points[-1] + quench_time_points,
            carb_time_points[-1] + quench_time + temper_time_points
        ])
        
        total_temp = np.concatenate([carb_temps, quench_temps, temper_temps])
        
        return {
            'time_carburizing': carb_time_points.tolist(),
            'temperature_carburizing': carb_temps.tolist(),
            'time_quenching': quench_time_points.tolist(),
            'temperature_quenching': quench_temps.tolist(),
            'time_tempering': temper_time_points.tolist(),
            'temperature_tempering': temper_temps.tolist(),
            'time_total': total_time.tolist(),
            'temperature_total': total_temp.tolist()
        }

# Standard thermal properties for steel phases
STEEL_THERMAL_PROPERTIES = {
    'austenite': ThermalProperties(
        density=7900,           # kg/m³
        specific_heat=600,      # J/kg.K
        thermal_conductivity=25, # W/m.K
        emissivity=0.8
    ),
    'ferrite': ThermalProperties(
        density=7870,
        specific_heat=450,
        thermal_conductivity=50,
        emissivity=0.8
    ),
    'pearlite': ThermalProperties(
        density=7850,
        specific_heat=480,
        thermal_conductivity=40,
        emissivity=0.8
    ),
    'bainite': ThermalProperties(
        density=7860,
        specific_heat=500,
        thermal_conductivity=35,
        emissivity=0.8
    ),
    'martensite': ThermalProperties(
        density=7840,
        specific_heat=520,
        thermal_conductivity=30,
        emissivity=0.8
    )
}

class HeatTreatmentCycle:
    """
    Defines a complete heat treatment cycle with temperature profiles
    """
    
    def __init__(self):
        self.thermal_models = ThermalModels()
        
    def carburizing_temperature_profile(self, time: float,
                                      carburizing_temp: float,
                                      heating_rate: float,
                                      holding_time: float) -> float:
        """
        Temperature profile during carburizing stage
        
        Args:
            time: Current time (hours)
            carburizing_temp: Target carburizing temperature (°C)
            heating_rate: Heating rate (°C/min)
            holding_time: Holding time at carburizing temperature (hours)
            
        Returns:
            Temperature at given time (°C)
        """
        heating_time = carburizing_temp / (heating_rate * 60)  # Convert to hours
        
        if time <= heating_time:
            # Heating phase
            return heating_rate * 60 * time  # Convert back to °C/hr
        elif time <= heating_time + holding_time:
            # Holding phase
            return carburizing_temp
        else:
            # Cooling or transition phase
            return carburizing_temp
    
    def diffusion_temperature_profile(self, time: float,
                                    diffusion_temp: float,
                                    diffusion_time: float) -> float:
        """
        Temperature profile during diffusion stage
        
        Args:
            time: Current time relative to diffusion start (hours)
            diffusion_temp: Diffusion temperature (°C)
            diffusion_time: Diffusion time (hours)
            
        Returns:
            Temperature at given time (°C)
        """
        if time <= diffusion_time:
            return diffusion_temp
        else:
            return diffusion_temp  # Maintain temperature until next stage
    
    def quenching_temperature_profile(self, time: float,
                                    initial_temp: float,
                                    quench_medium_temp: float,
                                    heat_transfer_coefficient: float,
                                    characteristic_length: float = 0.01) -> float:
        """
        Temperature profile during quenching (exponential decay)
        
        Args:
            time: Current time (seconds)
            initial_temp: Initial temperature before quenching (°C)
            quench_medium_temp: Quenching medium temperature (°C)
            heat_transfer_coefficient: Heat transfer coefficient (W/m².K)
            characteristic_length: Characteristic length for cooling (m)
            
        Returns:
            Temperature at given time (°C)
        """
        # Simplified exponential cooling model
        # In practice, this would be solved by FEM with proper boundary conditions
        
        # Estimate characteristic time (Biot number approach)
        k_steel = 30.0  # Approximate thermal conductivity of steel (W/m.K)
        biot_number = heat_transfer_coefficient * characteristic_length / k_steel
        
        # Characteristic time based on Biot number
        alpha = k_steel / (7850 * 500)  # Thermal diffusivity (m²/s)
        characteristic_time = characteristic_length**2 / alpha
        
        # Cooling rate factor
        cooling_factor = biot_number / (1 + biot_number)
        
        return (quench_medium_temp +
                (initial_temp - quench_medium_temp) *
                math.exp(-cooling_factor * time / characteristic_time))
    
    def tempering_temperature_profile(self, time: float,
                                    tempering_temp: float,
                                    heating_rate: float,
                                    holding_time: float) -> float:
        """
        Temperature profile during tempering stage
        
        Args:
            time: Current time (hours)
            tempering_temp: Tempering temperature (°C)
            heating_rate: Heating rate to tempering temperature (°C/min)
            holding_time: Holding time at tempering temperature (hours)
            
        Returns:
            Temperature at given time (°C)
        """
        heating_time = tempering_temp / (heating_rate * 60)  # Convert to hours
        
        if time <= heating_time:
            # Heating phase
            return heating_rate * 60 * time
        elif time <= heating_time + holding_time:
            # Holding phase
            return tempering_temp
        else:
            # Cooling phase (air cooling)
            cooling_time = time - heating_time - holding_time
            # Simple air cooling approximation
            return tempering_temp * math.exp(-0.1 * cooling_time)

class QuenchingMedia:
    """
    Properties of different quenching media
    """
    
    MEDIA_PROPERTIES = {
        'oil': {
            'temperature': 60,  # °C
            'heat_transfer_coefficient': 1000,  # W/m².K
            'name': 'Oil Quench'
        },
        'water': {
            'temperature': 25,  # °C
            'heat_transfer_coefficient': 3000,  # W/m².K
            'name': 'Water Quench'
        },
        'air': {
            'temperature': 25,  # °C
            'heat_transfer_coefficient': 50,   # W/m².K
            'name': 'Air Cooling'
        },
        'polymer': {
            'temperature': 40,  # °C
            'heat_transfer_coefficient': 1500, # W/m².K
            'name': 'Polymer Quench'
        }
    }
    
    @classmethod
    def get_properties(cls, medium: str) -> Dict:
        """Get properties for a specific quenching medium"""
        return cls.MEDIA_PROPERTIES.get(medium, cls.MEDIA_PROPERTIES['oil'])

class FurnaceAtmosphere:
    """
    Properties of carburizing atmosphere
    """
    
    def __init__(self, carbon_potential: float, temperature: float):
        self.carbon_potential = carbon_potential  # wt%
        self.temperature = temperature            # °C
        
    def calculate_mass_transfer_coefficient(self, gas_flow_rate: float = 1.0) -> float:
        """
        Calculate mass transfer coefficient β
        
        Args:
            gas_flow_rate: Relative gas flow rate
            
        Returns:
            Mass transfer coefficient in cm/s
        """
        # Typical values from literature: 2×10⁻⁵ to 2×10⁻⁴ cm/s for 800-1000°C
        base_beta = 1e-4  # cm/s
        
        # Temperature dependence
        temp_factor = math.exp(-(self.temperature - 900) / 100)
        
        # Flow rate dependence
        flow_factor = gas_flow_rate ** 0.5
        
        return base_beta * temp_factor * flow_factor

# Example usage
if __name__ == "__main__":
    thermal_models = ThermalModels()
    
    # Test convective heat flux
    h = 1000  # W/m².K
    T_medium = 333  # 60°C in Kelvin
    T_surface = 1173  # 900°C in Kelvin
    
    conv_flux = thermal_models.convective_heat_flux(h, T_medium, T_surface)
    print(f"Convective heat flux: {conv_flux:,.0f} W/m²")
    
    # Test radiative heat flux
    emissivity = 0.8
    rad_flux = thermal_models.radiative_heat_flux(emissivity, T_medium, T_surface)
    print(f"Radiative heat flux: {rad_flux:,.0f} W/m²")
    
    # Test total heat flux
    total_flux = thermal_models.total_heat_flux(h, emissivity, T_medium, T_surface)
    print(f"Total heat flux: {total_flux:,.0f} W/m²")
    
    # Test mixed properties
    phase_fractions = {'austenite': 0.7, 'martensite': 0.3}
    mixed_props = thermal_models.calculate_mixed_thermal_properties(
        phase_fractions, STEEL_THERMAL_PROPERTIES, 900)
    
    print(f"\nMixed thermal properties:")
    print(f"Density: {mixed_props.density:.0f} kg/m³")
    print(f"Specific heat: {mixed_props.specific_heat:.0f} J/kg.K")
    print(f"Thermal conductivity: {mixed_props.thermal_conductivity:.1f} W/m.K")
    
    # Test heat treatment cycle
    cycle = HeatTreatmentCycle()
    
    # Quenching profile test
    initial_temp = 900  # °C
    quench_temp = 60    # °C
    h_quench = 1000     # W/m².K
    
    time_points = [0, 10, 30, 60, 120]  # seconds
    print(f"\nQuenching temperature profile:")
    for t in time_points:
        temp = cycle.quenching_temperature_profile(t, initial_temp, quench_temp, h_quench)
        print(f"t = {t:3d}s: T = {temp:.1f}°C")