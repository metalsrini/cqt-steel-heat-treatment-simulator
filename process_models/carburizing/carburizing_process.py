"""
Carburizing Process Model
Implementation of carbon diffusion and grain growth during carburizing
Based on equations from the research paper
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
import time
from scipy.integrate import solve_ivp
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

# Import core mathematical models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'mathematical_models'))

from phase_transformation import SteelComposition, STEEL_COMPOSITIONS
from carbon_diffusion import CarbonDiffusionModels
from grain_growth import GrainGrowthModels
from thermal_models import ThermalModels, FurnaceAtmosphere

@dataclass
class CarburizingParameters:
    """Parameters for carburizing process simulation"""
    # Process conditions
    temperature: float              # Carburizing temperature (°C)
    carbon_potential: float         # Carbon potential of atmosphere (wt%)
    time_duration: float           # Carburizing time (hours)
    heating_rate: float            # Heating rate (°C/min)
    
    # Atmosphere properties
    mass_transfer_coefficient: float  # β (cm/s)
    gas_flow_rate: float           # Relative gas flow rate
    
    # Geometry and discretization
    geometry_type: str             # 'slab', 'cylinder', 'sphere'
    characteristic_length: float   # Characteristic dimension (m)
    n_spatial_points: int          # Number of spatial discretization points
    time_step: float              # Time step (s)
    
    # Initial conditions
    initial_carbon: float          # Initial carbon content (wt%)
    initial_grain_size: float      # Initial grain size (μm)
    surface_condition: str         # 'mass_transfer' or 'dirichlet'

@dataclass
class CarburizingResults:
    """Results from carburizing simulation"""
    # Spatial arrays
    distance_array: np.ndarray          # Distance from surface (m)
    carbon_profile: np.ndarray          # Final carbon distribution (wt%)
    grain_size_profile: np.ndarray      # Final grain size distribution (μm)
    
    # Time evolution
    time_array: np.ndarray              # Time points (s)
    surface_carbon_history: np.ndarray  # Surface carbon vs time
    temperature_history: np.ndarray     # Temperature vs time
    
    # Process metrics
    case_depth: float                   # Case depth (m)
    surface_carbon_final: float         # Final surface carbon (wt%)
    average_grain_size: float           # Average grain size (μm)
    diffusion_time_constant: float      # Characteristic diffusion time (s)
    
    # Validation metrics
    mass_balance_error: float           # Mass balance residual
    convergence_iterations: int         # Number of iterations to convergence

class CarburizingProcess:
    """
    Comprehensive carburizing process model implementing:
    - Carbon diffusion with Fick's laws
    - Grain growth kinetics
    - Temperature-dependent properties
    - Mass transfer boundary conditions
    """
    
    def __init__(self, steel_composition: SteelComposition, parameters: CarburizingParameters):
        self.composition = steel_composition
        self.parameters = parameters
        
        # Initialize mathematical models
        self.carbon_diffusion = CarbonDiffusionModels()
        self.grain_growth = GrainGrowthModels()
        self.thermal_models = ThermalModels()
        
        # Initialize arrays
        self.setup_spatial_discretization()
        self.setup_temporal_discretization()
        
        # Initialize atmosphere model
        self.atmosphere = FurnaceAtmosphere(
            parameters.carbon_potential, parameters.temperature)
    
    def setup_spatial_discretization(self):
        """Setup spatial discretization based on geometry"""
        n = self.parameters.n_spatial_points
        L = self.parameters.characteristic_length
        
        if self.parameters.geometry_type == 'slab':
            # 1D slab geometry (plane wall)
            self.distance = np.linspace(0, L, n)
            self.dx = L / (n - 1)
            self.geometry_factor = 1.0
            
        elif self.parameters.geometry_type == 'cylinder':
            # Cylindrical geometry (radial diffusion)
            self.distance = np.linspace(0, L, n)
            self.dx = L / (n - 1)
            self.geometry_factor = 2.0  # For cylindrical coordinates
            
        elif self.parameters.geometry_type == 'sphere':
            # Spherical geometry
            self.distance = np.linspace(0, L, n)
            self.dx = L / (n - 1)
            self.geometry_factor = 3.0  # For spherical coordinates
        
        # Initialize solution arrays
        self.carbon = np.full(n, self.parameters.initial_carbon)
        self.grain_size = np.full(n, self.parameters.initial_grain_size)
        self.temperature = np.full(n, 25.0)  # Room temperature initially
    
    def setup_temporal_discretization(self):
        """Setup time discretization for simulation"""
        total_time = self.parameters.time_duration * 3600  # Convert to seconds
        self.time_points = np.arange(0, total_time + self.parameters.time_step, 
                                    self.parameters.time_step)
        self.n_time_points = len(self.time_points)
        
        # Initialize history arrays
        self.carbon_history = np.zeros((self.n_time_points, len(self.distance)))
        self.grain_size_history = np.zeros_like(self.carbon_history)
        self.temperature_history = np.zeros(self.n_time_points)
        self.surface_carbon_history = np.zeros(self.n_time_points)
    
    def temperature_profile(self, time: float) -> float:
        """
        Calculate temperature profile during carburizing cycle
        
        Args:
            time: Current time (s)
            
        Returns:
            Temperature (°C)
        """
        # Calculate heating phase duration
        heating_time = (self.parameters.temperature - 25) / self.parameters.heating_rate * 60
        
        if time <= heating_time:
            # Heating phase
            return 25 + self.parameters.heating_rate * time / 60
        else:
            # Holding phase at carburizing temperature
            return self.parameters.temperature
    
    def calculate_diffusivity_field(self, temperature: float) -> np.ndarray:
        """
        Calculate carbon diffusivity at all spatial points
        
        Args:
            temperature: Current temperature (°C)
            
        Returns:
            Diffusivity field (m²/s)
        """
        diffusivity = np.zeros_like(self.carbon)
        
        for i in range(len(self.carbon)):
            diffusivity[i] = self.carbon_diffusion.calculate_carbon_diffusivity(
                temperature, self.carbon[i], self.composition)
        
        return diffusivity
    
    def calculate_mass_transfer_boundary_flux(self, temperature: float, 
                                            surface_carbon: float) -> float:
        """
        Calculate mass transfer flux at surface using Equation (5)
        
        Args:
            temperature: Surface temperature (°C)
            surface_carbon: Current surface carbon content (wt%)
            
        Returns:
            Mass transfer flux (wt%·m/s)
        """
        # Update mass transfer coefficient based on temperature and flow
        beta = self.atmosphere.calculate_mass_transfer_coefficient(
            self.parameters.gas_flow_rate)
        
        # Convert from cm/s to m/s
        beta_m = beta * 0.01
        
        flux = beta_m * (self.parameters.carbon_potential - surface_carbon)
        
        return flux
    
    def solve_carbon_diffusion_step(self, time_step: float, temperature: float) -> np.ndarray:
        """
        Solve one time step of carbon diffusion using implicit finite difference
        
        Args:
            time_step: Time step size (s)
            temperature: Current temperature (°C)
            
        Returns:
            Updated carbon distribution
        """
        n = len(self.carbon)
        carbon_new = self.carbon.copy()
        
        # Calculate diffusivity field
        D = self.calculate_diffusivity_field(temperature)
        
        # Build coefficient matrix for implicit method
        # For 1D diffusion: ∂C/∂t = ∂/∂x(D ∂C/∂x)
        
        # Stability parameter
        alpha = time_step / (self.dx ** 2)
        
        # Build tridiagonal matrix
        main_diag = np.ones(n)
        upper_diag = np.zeros(n-1)
        lower_diag = np.zeros(n-1)
        rhs = self.carbon.copy()
        
        # Interior points
        for i in range(1, n-1):
            D_avg_plus = 0.5 * (D[i] + D[i+1])
            D_avg_minus = 0.5 * (D[i-1] + D[i])
            
            if self.parameters.geometry_type == 'slab':
                # Cartesian coordinates
                lower_diag[i-1] = -alpha * D_avg_minus
                main_diag[i] = 1 + alpha * (D_avg_plus + D_avg_minus)
                upper_diag[i] = -alpha * D_avg_plus
                
            elif self.parameters.geometry_type == 'cylinder':
                # Cylindrical coordinates: ∂C/∂t = (1/r) ∂/∂r(r D ∂C/∂r)
                r = self.distance[i]
                r_plus = self.distance[i] + 0.5 * self.dx
                r_minus = self.distance[i] - 0.5 * self.dx
                
                if r > 0:
                    coeff_plus = alpha * D_avg_plus * r_plus / r
                    coeff_minus = alpha * D_avg_minus * r_minus / r
                    
                    lower_diag[i-1] = -coeff_minus
                    main_diag[i] = 1 + coeff_plus + coeff_minus
                    upper_diag[i] = -coeff_plus
                else:
                    # Special treatment at r=0
                    lower_diag[i-1] = -2 * alpha * D_avg_minus
                    main_diag[i] = 1 + 2 * alpha * D_avg_plus
                    upper_diag[i] = -2 * alpha * D_avg_plus
        
        # Boundary conditions
        if self.parameters.surface_condition == 'mass_transfer':
            # Mass transfer boundary condition at surface (x=0)
            flux = self.calculate_mass_transfer_boundary_flux(temperature, self.carbon[0])
            D_surface = D[0]
            
            # Robin boundary condition: -D ∂C/∂x|surface = flux
            # Discretized: -D (C[1] - C[0])/dx = flux
            # Rearranged: C[0] = C[1] + flux*dx/D
            
            main_diag[0] = 1
            upper_diag[0] = -1
            rhs[0] = -flux * self.dx / D_surface
            
        elif self.parameters.surface_condition == 'dirichlet':
            # Fixed surface concentration
            main_diag[0] = 1
            upper_diag[0] = 0
            rhs[0] = self.parameters.carbon_potential
        
        # Zero flux at center/far boundary
        main_diag[-1] = 1
        lower_diag[-2] = -1
        rhs[-1] = 0
        
        # Solve tridiagonal system
        matrix = diags([lower_diag, main_diag, upper_diag], [-1, 0, 1], 
                      shape=(n, n), format='csr')
        carbon_new = spsolve(matrix, rhs)
        
        return carbon_new
    
    def update_grain_size_step(self, time_step: float, current_time: float, 
                              temperature: float) -> np.ndarray:
        """
        Update grain size for one time step
        
        Args:
            time_step: Time step size (s)
            current_time: Current time (s)
            temperature: Current temperature (°C)
            
        Returns:
            Updated grain size distribution
        """
        grain_size_new = self.grain_size.copy()
        
        # Calculate grain growth rate at current conditions
        if current_time > 0 and temperature > 800:  # Only grow above 800°C
            growth_rate = self.grain_growth.calculate_grain_growth_rate(
                temperature, current_time, self.composition)
            
            # Update grain size using Euler integration
            for i in range(len(grain_size_new)):
                grain_size_new[i] += growth_rate * time_step
                
                # Ensure grain size doesn't decrease
                grain_size_new[i] = max(grain_size_new[i], self.grain_size[i])
        
        return grain_size_new
    
    def calculate_case_depth(self, threshold_carbon: float = 0.4) -> float:
        """
        Calculate case depth based on carbon content threshold
        
        Args:
            threshold_carbon: Carbon content threshold for case depth (wt%)
            
        Returns:
            Case depth (m)
        """
        return self.carbon_diffusion.calculate_carbon_penetration_depth(
            self.carbon, self.distance, threshold_carbon)
    
    def calculate_mass_balance_error(self) -> float:
        """
        Calculate mass balance error for validation
        
        Returns:
            Mass balance error (wt%)
        """
        # Calculate total carbon in the system
        if self.parameters.geometry_type == 'slab':
            # For slab geometry
            total_carbon = np.trapz(self.carbon, self.distance)
            
        elif self.parameters.geometry_type == 'cylinder':
            # For cylindrical geometry: integrate C * r dr
            r_weights = 2 * np.pi * self.distance
            total_carbon = np.trapz(self.carbon * r_weights, self.distance)
            
        elif self.parameters.geometry_type == 'sphere':
            # For spherical geometry: integrate C * r² dr
            r_weights = 4 * np.pi * self.distance ** 2
            total_carbon = np.trapz(self.carbon * r_weights, self.distance)
        
        # Expected carbon based on initial conditions and surface flux
        # This is a simplified calculation - more sophisticated methods needed for exact validation
        initial_total = self.parameters.initial_carbon * self.parameters.characteristic_length
        expected_increase = (self.parameters.carbon_potential - self.parameters.initial_carbon) * 0.1  # Simplified
        
        expected_total = initial_total + expected_increase
        error = abs(total_carbon - expected_total) / expected_total * 100
        
        return error
    
    def run_simulation(self, verbose: bool = True) -> CarburizingResults:
        """
        Run complete carburizing simulation
        
        Args:
            verbose: Print progress information
            
        Returns:
            Simulation results
        """
        if verbose:
            print("Starting carburizing simulation...")
            print(f"Steel: {self.composition}")
            print(f"Temperature: {self.parameters.temperature}°C")
            print(f"Time: {self.parameters.time_duration} hours")
            print(f"Carbon potential: {self.parameters.carbon_potential} wt%")
        
        start_time = time.time()
        convergence_iterations = 0
        
        # Initialize history arrays
        self.carbon_history[0] = self.carbon.copy()
        self.grain_size_history[0] = self.grain_size.copy()
        self.temperature_history[0] = self.temperature_profile(0)
        self.surface_carbon_history[0] = self.carbon[0]
        
        # Time integration loop
        for i, t in enumerate(self.time_points[1:], 1):
            dt = self.time_points[i] - self.time_points[i-1]
            current_temp = self.temperature_profile(t)
            
            # Update carbon distribution
            self.carbon = self.solve_carbon_diffusion_step(dt, current_temp)
            
            # Update grain size
            self.grain_size = self.update_grain_size_step(dt, t, current_temp)
            
            # Store history
            self.carbon_history[i] = self.carbon.copy()
            self.grain_size_history[i] = self.grain_size.copy()
            self.temperature_history[i] = current_temp
            self.surface_carbon_history[i] = self.carbon[0]
            
            # Progress reporting
            if verbose and i % max(1, len(self.time_points) // 10) == 0:
                progress = i / len(self.time_points) * 100
                print(f"Progress: {progress:.1f}% - Surface C: {self.carbon[0]:.3f} wt%")
            
            convergence_iterations += 1
        
        # Calculate final results
        case_depth = self.calculate_case_depth()
        mass_balance_error = self.calculate_mass_balance_error()
        
        # Calculate diffusion time constant
        D_avg = self.carbon_diffusion.calculate_carbon_diffusivity(
            self.parameters.temperature, self.parameters.initial_carbon, self.composition)
        diffusion_time_constant = (self.parameters.characteristic_length ** 2) / D_avg
        
        simulation_time = time.time() - start_time
        
        if verbose:
            print(f"\nSimulation completed in {simulation_time:.2f} seconds")
            print(f"Final surface carbon: {self.carbon[0]:.3f} wt%")
            print(f"Case depth: {case_depth*1000:.2f} mm")
            print(f"Average grain size: {np.mean(self.grain_size):.1f} μm")
            print(f"Mass balance error: {mass_balance_error:.2f}%")
        
        # Create results object
        results = CarburizingResults(
            distance_array=self.distance.copy(),
            carbon_profile=self.carbon.copy(),
            grain_size_profile=self.grain_size.copy(),
            time_array=self.time_points.copy(),
            surface_carbon_history=self.surface_carbon_history.copy(),
            temperature_history=self.temperature_history.copy(),
            case_depth=case_depth,
            surface_carbon_final=self.carbon[0],
            average_grain_size=np.mean(self.grain_size),
            diffusion_time_constant=diffusion_time_constant,
            mass_balance_error=mass_balance_error,
            convergence_iterations=convergence_iterations
        )
        
        return results
    
    def save_results(self, results: CarburizingResults, filename: str):
        """Save simulation results to file"""
        np.savez(filename,
                distance=results.distance_array,
                carbon_profile=results.carbon_profile,
                grain_size_profile=results.grain_size_profile,
                time_array=results.time_array,
                surface_carbon_history=results.surface_carbon_history,
                temperature_history=results.temperature_history,
                case_depth=results.case_depth,
                surface_carbon_final=results.surface_carbon_final,
                average_grain_size=results.average_grain_size)
    
    def validate_against_experimental(self, experimental_data: Dict) -> Dict:
        """
        Validate simulation results against experimental data
        
        Args:
            experimental_data: Dictionary with experimental measurements
            
        Returns:
            Validation metrics
        """
        validation_results = {}
        
        if 'carbon_profile' in experimental_data:
            exp_carbon = experimental_data['carbon_profile']
            exp_distance = experimental_data.get('distance', self.distance)
            
            # Interpolate simulation results to experimental points
            sim_carbon = np.interp(exp_distance, self.distance, self.carbon)
            
            # Calculate validation metrics
            mae = np.mean(np.abs(sim_carbon - exp_carbon))
            rmse = np.sqrt(np.mean((sim_carbon - exp_carbon) ** 2))
            max_error = np.max(np.abs(sim_carbon - exp_carbon))
            
            validation_results['carbon_profile'] = {
                'mae': mae,
                'rmse': rmse,
                'max_error': max_error,
                'experimental': exp_carbon,
                'simulated': sim_carbon
            }
        
        if 'case_depth' in experimental_data:
            exp_case_depth = experimental_data['case_depth']
            sim_case_depth = self.calculate_case_depth()
            error = abs(sim_case_depth - exp_case_depth) / exp_case_depth * 100
            
            validation_results['case_depth'] = {
                'experimental': exp_case_depth,
                'simulated': sim_case_depth,
                'relative_error': error
            }
        
        return validation_results

# Standard carburizing parameter sets
STANDARD_CARBURIZING_CONDITIONS = {
    'automotive_920C': CarburizingParameters(
        temperature=920, carbon_potential=1.0, time_duration=6.0,
        heating_rate=5.0, mass_transfer_coefficient=1e-4, gas_flow_rate=1.0,
        geometry_type='slab', characteristic_length=0.005, n_spatial_points=51,
        time_step=60.0, initial_carbon=0.2, initial_grain_size=20.0,
        surface_condition='mass_transfer'
    ),
    'heavy_duty_950C': CarburizingParameters(
        temperature=950, carbon_potential=1.2, time_duration=8.0,
        heating_rate=3.0, mass_transfer_coefficient=1.2e-4, gas_flow_rate=1.2,
        geometry_type='slab', characteristic_length=0.008, n_spatial_points=81,
        time_step=60.0, initial_carbon=0.15, initial_grain_size=25.0,
        surface_condition='mass_transfer'
    ),
    'precision_880C': CarburizingParameters(
        temperature=880, carbon_potential=0.8, time_duration=10.0,
        heating_rate=2.0, mass_transfer_coefficient=8e-5, gas_flow_rate=0.8,
        geometry_type='slab', characteristic_length=0.003, n_spatial_points=31,
        time_step=30.0, initial_carbon=0.25, initial_grain_size=15.0,
        surface_condition='mass_transfer'
    )
}

# Example usage
if __name__ == "__main__":
    # Test carburizing simulation with 8620 steel
    steel = STEEL_COMPOSITIONS['8620']
    params = STANDARD_CARBURIZING_CONDITIONS['automotive_920C']
    
    # Create and run simulation
    carb_process = CarburizingProcess(steel, params)
    results = carb_process.run_simulation(verbose=True)
    
    # Print key results
    print(f"\n=== CARBURIZING RESULTS ===")
    print(f"Steel composition: 8620")
    print(f"Process conditions: 920°C, 6h, 1.0% CP")
    print(f"Final surface carbon: {results.surface_carbon_final:.3f} wt%")
    print(f"Case depth (0.4% C): {results.case_depth*1000:.2f} mm")
    print(f"Average grain size: {results.average_grain_size:.1f} μm")
    print(f"Mass balance error: {results.mass_balance_error:.2f}%")