#!/usr/bin/env python3
"""
Comprehensive Test Suite for C-Q-T Modeling Framework
Tests all core functionality and validates against research paper equations
"""

import numpy as np
import sys
import os
import unittest
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Add paths to modules
sys.path.append(os.path.dirname(__file__))

# Import core mathematical models
from core.mathematical_models.phase_transformation import (
    PhaseTransformationModels, SteelComposition, STEEL_COMPOSITIONS
)
from core.mathematical_models.carbon_diffusion import CarbonDiffusionModels
from core.mathematical_models.grain_growth import GrainGrowthModels
from core.mathematical_models.hardness_prediction import HardnessPredictionModels
from core.mathematical_models.thermal_models import (
    ThermalModels, ThermalProperties, HeatTreatmentCycle, QuenchingMedia
)

# Import process models
try:
    from process_models.carburizing.carburizing_process import (
        CarburizingProcess, CarburizingParameters
    )
except ImportError:
    print("Warning: Carburizing process model not available for testing")
    CarburizingProcess = None
    CarburizingParameters = None

class TestSteelComposition(unittest.TestCase):
    """Test steel composition data structure"""
    
    def setUp(self):
        self.steel_8620 = SteelComposition(
            C=0.20, Si=0.25, Mn=0.80, Ni=0.50, Cr=0.50, Mo=0.20
        )
    
    def test_composition_creation(self):
        """Test steel composition creation"""
        self.assertEqual(self.steel_8620.C, 0.20)
        self.assertEqual(self.steel_8620.Cr, 0.50)
        self.assertEqual(self.steel_8620.V, 0.0)  # Default value
    
    def test_negative_composition_validation(self):
        """Test that negative compositions raise errors"""
        with self.assertRaises(ValueError):
            SteelComposition(C=-0.1)
    
    def test_standard_compositions(self):
        """Test standard steel compositions from paper"""
        self.assertIn('8620', STEEL_COMPOSITIONS)
        self.assertIn('SCR420', STEEL_COMPOSITIONS)
        self.assertIn('SAE_4320', STEEL_COMPOSITIONS)

class TestPhaseTransformationModels(unittest.TestCase):
    """Test phase transformation equations from the paper"""
    
    def setUp(self):
        self.models = PhaseTransformationModels()
        self.steel_8620 = STEEL_COMPOSITIONS['8620']
        self.steel_scr420 = STEEL_COMPOSITIONS['SCR420']
    
    def test_ae3_temperature_calculation(self):
        """Test AE3 temperature calculation (Equation 1)"""
        ae3 = self.models.calculate_ae3_temperature(self.steel_8620)
        
        # Expected range for 8620 steel
        self.assertGreater(ae3, 700)
        self.assertLess(ae3, 900)
        
        # Test with different compositions
        ae3_scr420 = self.models.calculate_ae3_temperature(self.steel_scr420)
        self.assertIsInstance(ae3_scr420, float)
    
    def test_grain_growth_activation_energy(self):
        """Test grain growth activation energy (Equation 3)"""
        Q = self.models.calculate_grain_growth_activation_energy(self.steel_8620)
        
        # Should be positive and in reasonable range for steel
        self.assertGreater(Q, 80000)
        self.assertLess(Q, 150000)
    
    def test_ms_temperature_calculation(self):
        """Test Ms temperature calculation (Equations 13-14)"""
        ms_temp = self.models.calculate_ms_temperature(self.steel_8620)
        
        # Reasonable range for Ms temperature
        self.assertGreater(ms_temp, 200)
        self.assertLess(ms_temp, 500)
        
        # Test high carbon correction factor
        high_carbon_steel = SteelComposition(C=0.8)
        ms_high_c = self.models.calculate_ms_temperature(high_carbon_steel)
        self.assertLess(ms_high_c, ms_temp)  # Higher carbon = lower Ms
    
    def test_martensitic_transformation(self):
        """Test Koistinen-Marburger equation (Equation 12)"""
        ms_temp = 350  # °C
        temp = 250     # °C
        retained_austenite = 1.0
        
        martensite_fraction = self.models.calculate_martensitic_transformation(
            temp, ms_temp, retained_austenite)
        
        # Should be between 0 and 1
        self.assertGreaterEqual(martensite_fraction, 0)
        self.assertLessEqual(martensite_fraction, 1)
        
        # Should be zero above Ms temperature
        martensite_above_ms = self.models.calculate_martensitic_transformation(
            400, ms_temp, retained_austenite)
        self.assertEqual(martensite_above_ms, 0)
    
    def test_phase_hardness_calculations(self):
        """Test Maynier hardness equations (Equations 15-17)"""
        cooling_rate = 100  # °C/hr
        
        # Test individual phase hardness
        hv_afp = self.models.calculate_austenite_ferrite_pearlite_hardness(
            self.steel_8620, cooling_rate)
        hv_b = self.models.calculate_bainite_hardness(self.steel_8620, cooling_rate)
        hv_m = self.models.calculate_martensite_hardness(self.steel_8620, cooling_rate)
        
        # All should be positive
        self.assertGreater(hv_afp, 0)
        self.assertGreater(hv_b, 0)
        self.assertGreater(hv_m, 0)
        
        # Martensite should be hardest
        self.assertGreater(hv_m, hv_b)
        self.assertGreater(hv_m, hv_afp)
        
        # Test all phases at once
        phase_hardness = self.models.calculate_phase_hardness(self.steel_8620, cooling_rate)
        self.assertIn('martensite', phase_hardness)
        self.assertEqual(phase_hardness['martensite'], hv_m)
    
    def test_total_hardness_calculation(self):
        """Test total hardness calculation (Equation 18)"""
        cooling_rate = 100
        phase_hardness = self.models.calculate_phase_hardness(self.steel_8620, cooling_rate)
        
        phase_fractions = {
            'austenite': 0.1,
            'ferrite': 0.0,
            'pearlite': 0.1,
            'bainite': 0.0,
            'martensite': 0.8
        }
        
        total_hardness = self.models.calculate_total_quenched_hardness(
            phase_fractions, phase_hardness)
        
        self.assertGreater(total_hardness, 0)
        self.assertIsInstance(total_hardness, float)
    
    def test_tempering_calculations(self):
        """Test tempering hardness calculations (Equations 19-24)"""
        carbon_content = 0.6  # wt%
        tempering_temp = 170  # °C
        tempering_time = 2    # hours
        
        # Test Jaffe-Holloman parameter
        K = self.models.calculate_jaffe_holloman_parameter(carbon_content)
        expected_K = 21.3 - 5.8 * carbon_content
        self.assertAlmostEqual(K, expected_K, places=2)
        
        # Test equivalent tempering temperature
        T_eq = self.models.calculate_equivalent_tempering_temperature(
            tempering_temp, tempering_time, carbon_content)
        self.assertGreater(T_eq, tempering_temp)
        
        # Test tempering factor
        f = self.models.calculate_tempering_factor(T_eq, carbon_content)
        self.assertGreater(f, 0)
        self.assertLess(f, 1)  # Should reduce hardness
    
    def test_hardness_conversion(self):
        """Test Vickers to Rockwell conversion (Equation 25)"""
        hv_values = [200, 400, 600, 800]
        
        for hv in hv_values:
            hrc = self.models.convert_vickers_to_rockwell(hv)
            self.assertGreaterEqual(hrc, 0)
            
        # Test specific conversion
        hv_600 = 600
        hrc_600 = self.models.convert_vickers_to_rockwell(hv_600)
        # Should be approximately 56 HRC
        self.assertGreater(hrc_600, 50)
        self.assertLess(hrc_600, 65)

class TestCarbonDiffusionModels(unittest.TestCase):
    """Test carbon diffusion equations"""
    
    def setUp(self):
        self.models = CarbonDiffusionModels()
        self.steel_8620 = STEEL_COMPOSITIONS['8620']
    
    def test_mass_transfer_flux(self):
        """Test mass transfer flux calculation (Equation 5)"""
        beta = 1e-4      # cm/s
        cp = 1.0         # wt%
        cs = 0.8         # wt%
        
        flux = self.models.calculate_carbon_mass_transfer_flux(beta, cp, cs)
        expected_flux = beta * (cp - cs)
        
        self.assertAlmostEqual(flux, expected_flux)
        self.assertGreater(flux, 0)  # Should be positive when cp > cs
    
    def test_q_factor_calculation(self):
        """Test q factor for diffusivity (Equation 10)"""
        q = self.models.calculate_carbon_diffusion_q_factor(self.steel_8620)
        
        # Should be close to 1 for typical steels
        self.assertGreater(q, 0.5)
        self.assertLess(q, 2.0)
    
    def test_carbon_diffusivity(self):
        """Test carbon diffusivity calculation (Equation 9)"""
        temperature = 920  # °C
        carbon_content = 0.5  # wt%
        
        D = self.models.calculate_carbon_diffusivity(
            temperature, carbon_content, self.steel_8620)
        
        # Should be positive and in reasonable range
        self.assertGreater(D, 0)
        self.assertLess(D, 1e-8)  # Reasonable upper bound
        
        # Test temperature dependence
        D_higher = self.models.calculate_carbon_diffusivity(
            950, carbon_content, self.steel_8620)
        self.assertGreater(D_higher, D)
    
    def test_case_depth_calculation(self):
        """Test case depth calculation"""
        # Create mock carbon profile
        distance = np.linspace(0, 0.005, 51)  # 5 mm depth
        carbon_profile = 0.8 * np.exp(-distance * 1000) + 0.2
        
        case_depth = self.models.calculate_carbon_penetration_depth(
            carbon_profile, distance, threshold_carbon=0.4)
        
        self.assertGreater(case_depth, 0)
        self.assertLess(case_depth, 0.005)
    
    def test_carburizing_time_estimation(self):
        """Test carburizing time estimation"""
        target_depth = 0.0007  # 0.7 mm
        diffusivity = 1e-11    # m²/s
        surface_carbon = 1.0   # wt%
        core_carbon = 0.2      # wt%
        
        estimated_time = self.models.estimate_carburizing_time(
            target_depth, diffusivity, surface_carbon, core_carbon)
        
        self.assertGreater(estimated_time, 0)
        # Convert to hours for reasonableness check
        time_hours = estimated_time / 3600
        self.assertGreater(time_hours, 1)
        self.assertLess(time_hours, 24)

class TestGrainGrowthModels(unittest.TestCase):
    """Test grain growth equations"""
    
    def setUp(self):
        self.models = GrainGrowthModels()
        self.steel_8620 = STEEL_COMPOSITIONS['8620']
    
    def test_activation_energy(self):
        """Test activation energy calculation (Equation 3)"""
        Q = self.models.calculate_activation_energy(self.steel_8620)
        
        # Should match phase transformation model
        phase_models = PhaseTransformationModels()
        Q_phase = phase_models.calculate_grain_growth_activation_energy(self.steel_8620)
        self.assertEqual(Q, Q_phase)
    
    def test_isothermal_grain_growth(self):
        """Test isothermal grain growth (Equation 2)"""
        temperature = 920  # °C
        time = 6 * 3600    # 6 hours in seconds
        
        grain_size = self.models.calculate_grain_size_isothermal(
            temperature, time, self.steel_8620)
        
        self.assertGreater(grain_size, 0)
        
        # Test time dependence
        grain_size_longer = self.models.calculate_grain_size_isothermal(
            temperature, time * 2, self.steel_8620)
        self.assertGreater(grain_size_longer, grain_size)
    
    def test_grain_growth_rate(self):
        """Test grain growth rate (Equation 4)"""
        temperature = 920
        time = 3600  # 1 hour
        
        rate = self.models.calculate_grain_growth_rate(
            temperature, time, self.steel_8620)
        
        self.assertGreater(rate, 0)
        
        # Rate should be higher at higher temperature
        rate_higher = self.models.calculate_grain_growth_rate(
            950, time, self.steel_8620)
        self.assertGreater(rate_higher, rate)
    
    def test_astm_grain_number_conversion(self):
        """Test ASTM grain number conversions"""
        grain_size = 50.0  # μm
        
        astm_number = self.models.calculate_astm_grain_number(grain_size)
        self.assertGreater(astm_number, 0)
        
        # Convert back
        calculated_size = self.models.calculate_grain_diameter_from_astm(astm_number)
        self.assertAlmostEqual(calculated_size, grain_size, places=1)
    
    def test_carburizing_simulation(self):
        """Test complete carburizing grain growth simulation"""
        results = self.models.simulate_carburizing_grain_growth(
            initial_grain_size=20.0,
            carburizing_temperature=920,
            carburizing_time=6.0,
            composition=self.steel_8620,
            heating_rate=5.0
        )
        
        self.assertIn('final_grain_size', results)
        self.assertIn('grain_growth_factor', results)
        self.assertGreater(results['final_grain_size'], 20.0)
        self.assertGreater(results['grain_growth_factor'], 1.0)

class TestHardnessPredictionModels(unittest.TestCase):
    """Test hardness prediction equations"""
    
    def setUp(self):
        self.models = HardnessPredictionModels()
        self.steel_8620 = STEEL_COMPOSITIONS['8620']
    
    def test_individual_phase_hardness(self):
        """Test individual phase hardness calculations"""
        cooling_rate = 100  # °C/hr
        
        hv_afp = self.models.calculate_austenite_ferrite_pearlite_hardness(
            self.steel_8620, cooling_rate)
        hv_b = self.models.calculate_bainite_hardness(self.steel_8620, cooling_rate)
        hv_m = self.models.calculate_martensite_hardness(self.steel_8620, cooling_rate)
        
        # All should be positive
        for hv in [hv_afp, hv_b, hv_m]:
            self.assertGreater(hv, 0)
            self.assertLess(hv, 2000)  # Reasonable upper limit
    
    def test_hardness_distribution_calculation(self):
        """Test hardness distribution along profile"""
        # Create mock data
        carbon_profile = np.array([0.8, 0.6, 0.4, 0.3, 0.2])
        phase_fractions = {
            'martensite': np.array([0.8, 0.7, 0.5, 0.3, 0.2]),
            'austenite': np.array([0.1, 0.1, 0.1, 0.1, 0.1]),
            'ferrite': np.array([0.1, 0.2, 0.4, 0.6, 0.7])
        }
        
        results = self.models.calculate_hardness_distribution(
            carbon_profile, phase_fractions, self.steel_8620, 100.0)
        
        self.assertIn('hv_quenched', results)
        self.assertEqual(len(results['hv_quenched']), len(carbon_profile))
        
        # Hardness should decrease with depth (lower carbon, less martensite)
        self.assertGreater(results['hv_quenched'][0], results['hv_quenched'][-1])
    
    def test_case_depth_from_hardness(self):
        """Test case depth calculation from hardness profile"""
        distance = np.linspace(0, 0.005, 51)  # 5 mm
        hardness = 60 * np.exp(-distance * 1000) + 30  # Exponential decay
        
        case_depth = self.models.calculate_case_depth_from_hardness(
            distance, hardness, 50.0, 'HRC')
        
        self.assertGreater(case_depth, 0)
        self.assertLess(case_depth, 0.005)
    
    def test_validation_metrics(self):
        """Test validation metrics calculation"""
        experimental_data = {'test': [60, 55, 50, 45, 40]}
        predicted_data = {'test': [62, 54, 49, 46, 39]}
        
        metrics = self.models.validate_hardness_predictions(
            experimental_data, predicted_data, tolerance=5.0)
        
        self.assertIn('mean_error', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('within_tolerance_fraction', metrics)

class TestThermalModels(unittest.TestCase):
    """Test thermal modeling equations"""
    
    def setUp(self):
        self.models = ThermalModels()
    
    def test_convective_heat_flux(self):
        """Test convective heat flux (Equation 27)"""
        h = 1000        # W/m².K
        T_medium = 333  # K (60°C)
        T_surface = 1173  # K (900°C)
        
        flux = self.models.convective_heat_flux(h, T_medium, T_surface)
        expected = h * (T_medium - T_surface)
        
        self.assertAlmostEqual(flux, expected)
        self.assertLess(flux, 0)  # Should be negative (cooling)
    
    def test_radiative_heat_flux(self):
        """Test radiative heat flux (Equation 28)"""
        emissivity = 0.8
        T_medium = 333
        T_surface = 1173
        
        flux = self.models.radiative_heat_flux(emissivity, T_medium, T_surface)
        
        self.assertLess(flux, 0)  # Should be negative (cooling)
        self.assertGreater(abs(flux), 1000)  # Should be significant at high temperature
    
    def test_mixed_thermal_properties(self):
        """Test rule of mixtures for thermal properties (Equation 29)"""
        from core.mathematical_models.thermal_models import STEEL_THERMAL_PROPERTIES
        
        phase_fractions = {'austenite': 0.7, 'martensite': 0.3}
        mixed_props = self.models.calculate_mixed_thermal_properties(
            phase_fractions, STEEL_THERMAL_PROPERTIES, 900)
        
        # Should be between pure phase values
        aus_props = STEEL_THERMAL_PROPERTIES['austenite']
        mart_props = STEEL_THERMAL_PROPERTIES['martensite']
        
        self.assertGreater(mixed_props.density, min(aus_props.density, mart_props.density))
        self.assertLess(mixed_props.density, max(aus_props.density, mart_props.density))
    
    def test_quenching_media_properties(self):
        """Test quenching media property database"""
        oil_props = QuenchingMedia.get_properties('oil')
        water_props = QuenchingMedia.get_properties('water')
        
        self.assertIn('heat_transfer_coefficient', oil_props)
        self.assertIn('temperature', oil_props)
        
        # Water should have higher heat transfer coefficient than oil
        self.assertGreater(water_props['heat_transfer_coefficient'],
                          oil_props['heat_transfer_coefficient'])

class TestProcessIntegration(unittest.TestCase):
    """Test integration between process models"""
    
    def setUp(self):
        self.steel_8620 = STEEL_COMPOSITIONS['8620']
    
    def test_carburizing_process_integration(self):
        """Test carburizing process model integration"""
        if CarburizingProcess is None:
            self.skipTest("Carburizing process model not available")
        
        params = CarburizingParameters(
            temperature=920, carbon_potential=1.0, time_duration=2.0,
            heating_rate=5.0, mass_transfer_coefficient=1e-4, gas_flow_rate=1.0,
            geometry_type='slab', characteristic_length=0.002, n_spatial_points=21,
            time_step=120.0, initial_carbon=0.2, initial_grain_size=20.0,
            surface_condition='mass_transfer'
        )
        
        process = CarburizingProcess(self.steel_8620, params)
        results = process.run_simulation(verbose=False)
        
        # Check that results are reasonable
        self.assertGreater(results.surface_carbon_final, 0.2)
        self.assertLess(results.surface_carbon_final, 1.2)
        self.assertGreater(results.case_depth, 0)
        self.assertGreater(results.average_grain_size, 20.0)
    
    def test_complete_cqt_workflow(self):
        """Test complete C-Q-T workflow integration"""
        # This tests the integration of multiple models
        phase_models = PhaseTransformationModels()
        hardness_models = HardnessPredictionModels()
        
        # Simulate carburized profile
        distance = np.linspace(0, 0.003, 31)  # 3 mm
        carbon_profile = 0.8 * np.exp(-distance * 1000) + 0.2
        
        # Calculate hardness at each point
        cooling_rate = 100
        hardness_profile = []
        
        for carbon in carbon_profile:
            local_steel = SteelComposition(
                C=carbon, Si=self.steel_8620.Si, Mn=self.steel_8620.Mn,
                Ni=self.steel_8620.Ni, Cr=self.steel_8620.Cr, Mo=self.steel_8620.Mo
            )
            
            phase_hardness = hardness_models.calculate_all_phase_hardness(
                local_steel, cooling_rate)
            
            # Assume mostly martensite
            phase_fractions = {'martensite': 0.8, 'austenite': 0.2}
            total_hardness = hardness_models.calculate_total_quenched_hardness(
                phase_fractions, phase_hardness)
            
            hardness_profile.append(total_hardness)
        
        hardness_profile = np.array(hardness_profile)
        
        # Check that surface is harder than core
        self.assertGreater(hardness_profile[0], hardness_profile[-1])
        
        # Convert to HRC and check reasonable values
        hrc_profile = [hardness_models.convert_vickers_to_rockwell(hv) 
                      for hv in hardness_profile]
        
        self.assertGreater(hrc_profile[0], 50)  # Surface should be hard
        self.assertLess(hrc_profile[-1], 50)    # Core should be softer

class TestValidationCases(unittest.TestCase):
    """Test validation against experimental data"""
    
    def test_steel_compositions_from_paper(self):
        """Test that all steel compositions from paper are available"""
        required_steels = ['SCR420', 'JIS_SCR420H', 'SAE_4320', '8620', '4130', '4320']
        
        for steel_name in required_steels:
            self.assertIn(steel_name, STEEL_COMPOSITIONS)
            steel = STEEL_COMPOSITIONS[steel_name]
            self.assertIsInstance(steel, SteelComposition)
            self.assertGreater(steel.C, 0)
    
    def test_experimental_validation_data_ranges(self):
        """Test that calculations produce results in experimental ranges"""
        steel_4320 = STEEL_COMPOSITIONS['SAE_4320']
        phase_models = PhaseTransformationModels()
        hardness_models = HardnessPredictionModels()
        
        # Test Ms temperature for high carbon (carburized surface)
        high_carbon_steel = SteelComposition(
            C=0.8, Si=steel_4320.Si, Mn=steel_4320.Mn,
            Ni=steel_4320.Ni, Cr=steel_4320.Cr, Mo=steel_4320.Mo
        )
        
        ms_temp = phase_models.calculate_ms_temperature(high_carbon_steel)
        
        # Should be significantly lower than core steel Ms
        core_ms = phase_models.calculate_ms_temperature(steel_4320)
        self.assertLess(ms_temp, core_ms)
        
        # Surface hardness should be in experimental range (60-65 HRC)
        phase_hardness = hardness_models.calculate_all_phase_hardness(
            high_carbon_steel, 100)
        
        # Assume 85% martensite, 15% retained austenite (typical for carburized surface)
        phase_fractions = {'martensite': 0.85, 'austenite': 0.15}
        total_hardness = hardness_models.calculate_total_quenched_hardness(
            phase_fractions, phase_hardness)
        
        surface_hrc = hardness_models.convert_vickers_to_rockwell(total_hardness)
        
        # Should be in reasonable range for carburized steel
        self.assertGreater(surface_hrc, 55)
        self.assertLess(surface_hrc, 70)

def run_comprehensive_tests():
    """Run all tests and generate report"""
    
    print("="*80)
    print("COMPREHENSIVE C-Q-T MODELING FRAMEWORK TEST SUITE")
    print("="*80)
    
    # Create test suite
    test_classes = [
        TestSteelComposition,
        TestPhaseTransformationModels,
        TestCarbonDiffusionModels,
        TestGrainGrowthModels,
        TestHardnessPredictionModels,
        TestThermalModels,
        TestProcessIntegration,
        TestValidationCases
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures:
            print(f"  ✗ {len(result.failures)} failures")
            for test, traceback in result.failures:
                print(f"    FAIL: {test}")
        
        if result.errors:
            print(f"  ✗ {len(result.errors)} errors")
            for test, traceback in result.errors:
                print(f"    ERROR: {test}")
        
        if not result.failures and not result.errors:
            print(f"  ✓ All {result.testsRun} tests passed")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total tests run: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success rate: {(total_tests - total_failures - total_errors) / total_tests * 100:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 ALL TESTS PASSED - Framework is working correctly!")
        print("\nCore functionality validated:")
        print("✓ Phase transformation equations (Equations 1, 12-18)")
        print("✓ Carbon diffusion models (Equations 5-10)")
        print("✓ Grain growth kinetics (Equations 2-4)")
        print("✓ Hardness prediction (Equations 15-25)")
        print("✓ Thermal modeling (Equations 26-29)")
        print("✓ Process integration")
        print("✓ Experimental validation ranges")
    else:
        print(f"\n⚠ {total_failures + total_errors} tests failed - Review implementation")
    
    return total_failures + total_errors == 0

def test_specific_equations():
    """Test specific equations from the research paper"""
    
    print("\n" + "="*60)
    print("TESTING SPECIFIC