"""
Carbon Diffusion Models for Carburizing Process
Implementation of Fick's laws and mass transfer equations (Equations 5-10)
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from .phase_transformation import SteelComposition

@dataclass
class CarbonDiffusionParameters:
    """Parameters for carbon diffusion simulation"""
    carbon_potential: float     # Carbon potential of atmosphere (wt%)
    mass_transfer_coefficient: float  # β (cm/s)
    temperature: float         # Temperature (°C)
    time_step: float          # Time step for simulation (s)
    spatial_step: float       # Spatial discretization (m)

class CarbonDiffusionModels:
    """
    Implementation of carbon diffusion models from the research paper
    """
    
    def __init__(self):
        self.R_gas_constant_cal = 1.987  # cal/mol.K
        
    def calculate_carbon_mass_transfer_flux(self, beta: float, 
                                          carbon_potential: float,
                                          surface_carbon: float) -> float:
        """
        Calculate carbon mass transfer flux using Equation (5)
        
        J = β(Cp - Cs)
        
        Args:
            beta: Mass transfer coefficient (cm/s)
            carbon_potential: Carbon potential of atmosphere (wt%)
            surface_carbon: Carbon concentration at surface (wt%)
            
        Returns:
            Carbon flux (wt%·cm/s)
        """
        return beta * (carbon_potential - surface_carbon)
    
    def calculate_surface_carbon_flux(self, steel: SteelComposition, temperature: float, 
                                     carbon_potential: float, mass_transfer_coefficient: float) -> float:
        """
        Calculate surface carbon flux considering steel composition
        
        Args:
            steel: Steel composition
            temperature: Temperature (°C)
            carbon_potential: Carbon potential (wt%)
            mass_transfer_coefficient: Mass transfer coefficient (cm/s)
            
        Returns:
            Surface carbon flux (wt%·cm/s)
        """
        # Estimate surface carbon concentration based on equilibrium
        surface_carbon = min(carbon_potential * 0.9, 1.2)  # Simplified estimate
        
        return mass_transfer_coefficient * (carbon_potential - surface_carbon)
    
    def calculate_effective_diffusivity(self, steel: SteelComposition, temperature: float) -> float:
        """
        Calculate effective carbon diffusivity in austenite
        
        Args:
            steel: Steel composition
            temperature: Temperature (°C)
            
        Returns:
            Effective diffusivity (cm²/s)
        """
        # Temperature in Kelvin
        T_kelvin = temperature + 273.15
        
        # Base diffusivity for carbon in austenite (Arrhenius equation)
        D0 = 0.23  # Pre-exponential factor (cm²/s)
        Q = 32900  # Activation energy (cal/mol)
        
        # Base diffusivity
        D_base = D0 * math.exp(-Q / (self.R_gas_constant_cal * T_kelvin))
        
        # Corrections for alloying elements
        correction = (1.0 - 0.1 * steel.Cr - 0.05 * steel.Ni - 0.08 * steel.Mo - 0.02 * steel.Mn)
        
        return D_base * max(0.1, correction)
    
    def calculate_mass_transfer_effectiveness(self, mass_transfer_coefficient: float,
                                           gas_flow_rate: float, temperature: float) -> float:
        """
        Calculate mass transfer effectiveness
        
        Args:
            mass_transfer_coefficient: Mass transfer coefficient (cm/s)
            gas_flow_rate: Gas flow rate
            temperature: Temperature (°C)
            
        Returns:
            Mass transfer effectiveness (dimensionless)
        """
        # Simplified effectiveness calculation
        base_effectiveness = 0.8
        flow_correction = min(1.0, gas_flow_rate / 1.0)  # Normalized to reference flow
        temp_correction = 1.0 + 0.001 * (temperature - 920)  # Reference temp 920°C
        
        return base_effectiveness * flow_correction * temp_correction

    def calculate_diffusion_flux_ficks_first_law(self, diffusivity: float,
                                                carbon_gradient: float) -> float:
        """
        Calculate diffusion flux using Fick's first law (Equation 6)
        
        J = -D(∇C)
        
        Args:
            diffusivity: Carbon diffusivity (m²/s)
            carbon_gradient: Carbon concentration gradient (wt%/m)
            
        Returns:
            Diffusion flux (wt%·m/s)
        """
        return -diffusivity * carbon_gradient
    
    def calculate_carbon_concentration_rate(self, diffusivity: float,
                                          carbon_laplacian: float,
                                          diffusivity_gradient: np.ndarray = None,
                                          carbon_gradient: np.ndarray = None) -> float:
        """
        Calculate rate of carbon concentration change using Fick's second law (Equation 7)
        
        ∂C/∂t = ∇·(D(∇C))
        
        For constant diffusivity: ∂C/∂t = D∇²C
        For variable diffusivity: ∂C/∂t = D∇²C + ∇D·∇C
        
        Args:
            diffusivity: Carbon diffusivity (m²/s)
            carbon_laplacian: Laplacian of carbon concentration (∇²C)
            diffusivity_gradient: Gradient of diffusivity (optional)
            carbon_gradient: Gradient of carbon concentration (optional)
            
        Returns:
            Rate of carbon concentration change (wt%/s)
        """
        # Basic term: D∇²C
        rate = diffusivity * carbon_laplacian
        
        # Additional term for variable diffusivity: ∇D·∇C
        if diffusivity_gradient is not None and carbon_gradient is not None:
            rate += np.dot(diffusivity_gradient, carbon_gradient)
            
        return rate
    
    def calculate_boundary_condition_mass_balance(self, beta: float,
                                                carbon_potential: float,
                                                surface_carbon: float,
                                                diffusivity: float,
                                                carbon_gradient_at_surface: float) -> float:
        """
        Calculate mass balance at steel surface (Equation 8)
        
        β(Cp - Cs) = -D(∇C)|surface
        
        Args:
            beta: Mass transfer coefficient (cm/s)
            carbon_potential: Carbon potential (wt%)
            surface_carbon: Surface carbon concentration (wt%)
            diffusivity: Diffusivity at surface (m²/s)
            carbon_gradient_at_surface: Carbon gradient at surface (wt%/m)
            
        Returns:
            Mass balance residual (should be zero for equilibrium)
        """
        # Convert beta from cm/s to m/s
        beta_m = beta * 0.01
        
        left_side = beta_m * (carbon_potential - surface_carbon)
        right_side = -diffusivity * carbon_gradient_at_surface
        
        return left_side - right_side
    
    def calculate_carbon_diffusivity_q_factor(self, composition: SteelComposition) -> float:
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
    
    def calculate_carbon_diffusivity(self, temperature: float, 
                                   carbon_content: float,
                                   composition: SteelComposition) -> float:
        """
        Calculate carbon diffusivity using Equation (9)
        
        D(m²/s) = 0.47×10⁻⁴ * exp(-1.6C - (37000-6600C)/R(T+273)) * q
        
        Args:
            temperature: Temperature (°C)
            carbon_content: Local carbon content (wt%)
            composition: Steel chemical composition
            
        Returns:
            Carbon diffusivity (m²/s)
        """
        q = self.calculate_carbon_diffusivity_q_factor(composition)
        
        # Calculate diffusivity (Equation 9)
        D = (0.47e-4 * 
             math.exp(-1.6 * carbon_content - 
                      (37000 - 6600 * carbon_content) / 
                      (self.R_gas_constant_cal * (temperature + 273))) * q)
        
        return D
    
    def calculate_effective_diffusivity_array(self, temperature_field: np.ndarray,
                                            carbon_field: np.ndarray,
                                            composition: SteelComposition) -> np.ndarray:
        """
        Calculate diffusivity field for spatially varying conditions
        
        Args:
            temperature_field: Temperature distribution (°C)
            carbon_field: Carbon concentration distribution (wt%)
            composition: Steel chemical composition
            
        Returns:
            Diffusivity field (m²/s)
        """
        diffusivity_field = np.zeros_like(temperature_field)
        
        for i in range(temperature_field.shape[0]):
            for j in range(temperature_field.shape[1] if len(temperature_field.shape) > 1 else 1):
                if len(temperature_field.shape) > 1:
                    temp = temperature_field[i, j]
                    carbon = carbon_field[i, j]
                else:
                    temp = temperature_field[i]
                    carbon = carbon_field[i]
                    
                diffusivity_field[i, j if len(temperature_field.shape) > 1 else 0] = \
                    self.calculate_carbon_diffusivity(temp, carbon, composition)
        
        return diffusivity_field
    
    def solve_1d_diffusion_explicit(self, initial_carbon: np.ndarray,
                                   diffusivity: np.ndarray,
                                   time_step: float,
                                   spatial_step: float,
                                   boundary_conditions: Dict) -> np.ndarray:
        """
        Solve 1D carbon diffusion using explicit finite difference method
        
        ∂C/∂t = D ∂²C/∂x²
        
        Args:
            initial_carbon: Initial carbon distribution (wt%)
            diffusivity: Diffusivity distribution (m²/s)
            time_step: Time step (s)
            spatial_step: Spatial step (m)
            boundary_conditions: Boundary condition specifications
            
        Returns:
            Updated carbon distribution (wt%)
        """
        carbon = initial_carbon.copy()
        n_points = len(carbon)
        
        # Stability criterion for explicit method
        max_diffusivity = np.max(diffusivity)
        max_dt = 0.5 * spatial_step**2 / max_diffusivity
        
        if time_step > max_dt:
            raise ValueError(f"Time step {time_step} exceeds stability limit {max_dt}")
        
        # Finite difference coefficients
        alpha = time_step / (spatial_step**2)
        
        # Update interior points
        for i in range(1, n_points - 1):
            d_avg = 0.5 * (diffusivity[i] + diffusivity[i+1])
            d_avg_left = 0.5 * (diffusivity[i-1] + diffusivity[i])
            
            carbon[i] += alpha * (d_avg * (initial_carbon[i+1] - initial_carbon[i]) -
                                d_avg_left * (initial_carbon[i] - initial_carbon[i-1]))
        
        # Apply boundary conditions
        if 'left' in boundary_conditions:
            if boundary_conditions['left']['type'] == 'dirichlet':
                carbon[0] = boundary_conditions['left']['value']
            elif boundary_conditions['left']['type'] == 'neumann':
                # Zero gradient: C[0] = C[1]
                carbon[0] = carbon[1]
            elif boundary_conditions['left']['type'] == 'mass_transfer':
                # Apply mass transfer boundary condition
                beta = boundary_conditions['left']['beta']
                cp = boundary_conditions['left']['carbon_potential']
                # Simplified implementation
                carbon[0] = cp  # Approximate surface equilibrium
        
        if 'right' in boundary_conditions:
            if boundary_conditions['right']['type'] == 'dirichlet':
                carbon[-1] = boundary_conditions['right']['value']
            elif boundary_conditions['right']['type'] == 'neumann':
                carbon[-1] = carbon[-2]
        
        return carbon
    
    def solve_1d_diffusion_implicit(self, initial_carbon: np.ndarray,
                                   diffusivity: np.ndarray,
                                   time_step: float,
                                   spatial_step: float,
                                   boundary_conditions: Dict) -> np.ndarray:
        """
        Solve 1D carbon diffusion using implicit finite difference method
        (More stable than explicit method)
        
        Args:
            initial_carbon: Initial carbon distribution (wt%)
            diffusivity: Diffusivity distribution (m²/s)
            time_step: Time step (s)
            spatial_step: Spatial step (m)
            boundary_conditions: Boundary condition specifications
            
        Returns:
            Updated carbon distribution (wt%)
        """
        n_points = len(initial_carbon)
        alpha = time_step / (spatial_step**2)
        
        # Build tridiagonal matrix A for implicit method
        A = np.zeros((n_points, n_points))
        b = initial_carbon.copy()
        
        # Interior points
        for i in range(1, n_points - 1):
            d_avg = 0.5 * (diffusivity[i] + diffusivity[i+1])
            d_avg_left = 0.5 * (diffusivity[i-1] + diffusivity[i])
            
            A[i, i-1] = -alpha * d_avg_left
            A[i, i] = 1 + alpha * (d_avg + d_avg_left)
            A[i, i+1] = -alpha * d_avg
        
        # Boundary conditions
        A[0, 0] = 1
        A[-1, -1] = 1
        
        if 'left' in boundary_conditions:
            if boundary_conditions['left']['type'] == 'dirichlet':
                b[0] = boundary_conditions['left']['value']
            elif boundary_conditions['left']['type'] == 'neumann':
                A[0, 0] = 1
                A[0, 1] = -1
                b[0] = 0
        
        if 'right' in boundary_conditions:
            if boundary_conditions['right']['type'] == 'dirichlet':
                b[-1] = boundary_conditions['right']['value']
            elif boundary_conditions['right']['type'] == 'neumann':
                A[-1, -1] = 1
                A[-1, -2] = -1
                b[-1] = 0
        
        # Solve linear system
        carbon_new = np.linalg.solve(A, b)
        
        return carbon_new
    
    def calculate_carbon_penetration_depth(self, carbon_profile: np.ndarray,
                                         spatial_coordinates: np.ndarray,
                                         threshold_carbon: float = 0.4) -> float:
        """
        Calculate carbon penetration depth (case depth)
        
        Args:
            carbon_profile: Carbon concentration profile (wt%)
            spatial_coordinates: Spatial coordinates (m)
            threshold_carbon: Threshold carbon content for case depth (wt%)
            
        Returns:
            Case depth (m)
        """
        # Find the depth where carbon content drops below threshold
        for i, carbon in enumerate(carbon_profile):
            if carbon < threshold_carbon:
                if i == 0:
                    return 0.0
                
                # Linear interpolation between points
                x1, c1 = spatial_coordinates[i-1], carbon_profile[i-1]
                x2, c2 = spatial_coordinates[i], carbon_profile[i]
                
                # Interpolate to find exact position
                case_depth = x1 + (x2 - x1) * (threshold_carbon - c1) / (c2 - c1)
                return case_depth
        
        # If threshold never reached, return maximum depth
        return spatial_coordinates[-1]
    
    def estimate_carburizing_time(self, target_case_depth: float,
                                 diffusivity: float,
                                 surface_carbon: float,
                                 core_carbon: float,
                                 threshold_carbon: float = 0.4) -> float:
        """
        Estimate required carburizing time using analytical approximation
        
        Args:
            target_case_depth: Desired case depth (m)
            diffusivity: Average diffusivity (m²/s)
            surface_carbon: Surface carbon content (wt%)
            core_carbon: Core carbon content (wt%)
            threshold_carbon: Threshold for case depth (wt%)
            
        Returns:
            Estimated carburizing time (s)
        """
        # Simplified analytical solution for semi-infinite medium
        # C(x,t) = Cs + (C0 - Cs) * erf(x / (2√(Dt)))
        
        # For case depth calculation: solve for t when C = threshold at x = case_depth
        carbon_fraction = (threshold_carbon - surface_carbon) / (core_carbon - surface_carbon)
        
        # Inverse error function approximation
        if carbon_fraction <= 0:
            return 0.0
        
        # Use approximation: erf⁻¹(y) ≈ √(π)/2 * y for small y
        if carbon_fraction < 0.5:
            erf_inv = math.sqrt(math.pi) / 2 * carbon_fraction
        else:
            # More accurate approximation for larger values
            erf_inv = math.sqrt(-math.log(1 - carbon_fraction**2))
        
        # Calculate time
        time = (target_case_depth / (2 * erf_inv))**2 / diffusivity
        
        return time

# Standard diffusion parameters for common conditions
STANDARD_DIFFUSION_CONDITIONS = {
    'carburizing_920C': {
        'temperature': 920,      # °C
        'carbon_potential': 1.0, # wt%
        'beta': 1e-4,           # cm/s
    },
    'carburizing_950C': {
        'temperature': 950,      # °C
        'carbon_potential': 1.2, # wt%
        'beta': 1.2e-4,         # cm/s
    },
    'carburizing_880C': {
        'temperature': 880,      # °C
        'carbon_potential': 0.8, # wt%
        'beta': 8e-5,           # cm/s
    }
}

# Example usage
if __name__ == "__main__":
    from .phase_transformation import STEEL_COMPOSITIONS
    
    models = CarbonDiffusionModels()
    steel_8620 = STEEL_COMPOSITIONS['8620']
    
    # Test diffusivity calculation
    temp = 920  # °C
    carbon_content = 0.2  # wt%
    
    diffusivity = models.calculate_carbon_diffusivity(temp, carbon_content, steel_8620)
    print(f"Carbon diffusivity at {temp}°C: {diffusivity:.2e} m²/s")
    
    # Test q factor
    q_factor = models.calculate_carbon_diffusivity_q_factor(steel_8620)
    print(f"Q factor for 8620 steel: {q_factor:.3f}")
    
    # Test mass transfer flux
    beta = 1e-4  # cm/s
    cp = 1.0     # wt%
    cs = 0.8     # wt%
    
    flux = models.calculate_carbon_mass_transfer_flux(beta, cp, cs)
    print(f"Mass transfer flux: {flux:.2e} wt%·cm/s")
    
    # Test case depth estimation
    target_depth = 0.0007  # 0.7 mm
    estimated_time = models.estimate_carburizing_time(
        target_depth, diffusivity, 1.0, 0.2, 0.4)
    print(f"Estimated carburizing time: {estimated_time/3600:.1f} hours")