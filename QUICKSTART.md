# Quick Start Guide - C-Q-T Modeling Framework

Welcome to the Integrated Carburizing-Quenching-Tempering (C-Q-T) Modeling Framework! This framework replicates the exact research methodology from:

**"Integrated Modeling of Carburizing-Quenching-Tempering of Steel Gears for an ICME Framework"** by Danish Khan and BP Gautham (2018).

## 🚀 Quick Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd zed\ AI

# Install dependencies
pip install -r requirements.txt

# Run test to verify installation
python test_framework.py
```

## 🎯 What This Framework Does

✅ **Complete C-Q-T Process Chain Simulation**
- Carbon diffusion during carburizing (Fick's laws)
- Grain growth kinetics with chemical composition effects
- Phase transformation during quenching (JMAK + Koistinen-Marburger)
- Hardness prediction with tempering effects

✅ **Exact Research Paper Implementation**
- All 29 equations from the original paper
- Chemical composition-dependent models
- Validated against experimental data

✅ **ICME Integration**
- Material selection optimization
- Manufacturing design exploration
- Automated gear design workflows

## 🏃‍♂️ 5-Minute Quick Start

### 1. Basic Steel Property Calculation

```python
from core.mathematical_models.phase_transformation import PhaseTransformationModels, STEEL_COMPOSITIONS

# Initialize models
models = PhaseTransformationModels()

# Get 8620 steel composition (from the paper)
steel_8620 = STEEL_COMPOSITIONS['8620']

# Calculate critical temperatures
ae3_temp = models.calculate_ae3_temperature(steel_8620)
ms_temp = models.calculate_ms_temperature(steel_8620)

print(f"AE3 Temperature: {ae3_temp:.1f}°C")
print(f"Ms Temperature: {ms_temp:.1f}°C")
```

### 2. Hardness Prediction

```python
from core.mathematical_models.hardness_prediction import HardnessPredictionModels

hardness_models = HardnessPredictionModels()

# Calculate phase hardness for specific cooling rate
cooling_rate = 100  # °C/hr
phase_hardness = hardness_models.calculate_all_phase_hardness(steel_8620, cooling_rate)

print("Phase Hardness Values:")
for phase, hv in phase_hardness.items():
    hrc = hardness_models.convert_vickers_to_rockwell(hv)
    print(f"  {phase}: {hv:.0f} HV ({hrc:.1f} HRC)")
```

### 3. Complete C-Q-T Simulation

```python
# Run the complete demonstration
python example_complete_cqt_simulation.py
```

This will run:
- Complete carburizing simulation (6 hours at 920°C)
- Quenching kinetics with phase transformation
- Tempering hardness calculation
- Material comparison (8620 vs 4130 vs 4320 steel)
- Manufacturing design optimization

## 📊 Key Results You'll Get

### Process Outputs
- **Carbon Profile**: Distribution from surface to core
- **Case Depth**: Both carbon-based (0.4% C) and hardness-based (50 HRC)
- **Hardness Distribution**: Surface to core hardness profile
- **Grain Size**: Evolution during carburizing
- **Phase Fractions**: Martensite, bainite, austenite, etc.

### Validation Metrics
- **Case 1**: SCR420 steel carburizing (vs Kim et al. 2011)
- **Case 2**: JIS-SCR420H quenching (vs Inoue et al. 2007)
- **Case 3**: SAE 4320 complete C-Q-T (vs Medlin et al. 1999)

## 🔧 Advanced Usage

### Custom Steel Composition

```python
from core.mathematical_models.phase_transformation import SteelComposition

# Define your own steel
custom_steel = SteelComposition(
    C=0.25, Si=0.30, Mn=0.70, Ni=0.40, Cr=0.60, Mo=0.15
)

# Use in any calculation
ae3 = models.calculate_ae3_temperature(custom_steel)
```

### Custom Heat Treatment Cycle

```python
heat_treatment = {
    'carburizing_temp': 950,      # °C
    'carburizing_time': 8.0,      # hours
    'carbon_potential': 1.2,      # wt%
    'quenching_temp': 60,         # °C
    'tempering_temp': 180,        # °C
    'tempering_time': 2.5         # hours
}

# Use in complete simulation
from example_complete_cqt_simulation import CompleteCQTSimulation
sim = CompleteCQTSimulation(custom_steel, heat_treatment)
results = sim.run_complete_simulation()
```

### Process Optimization

```python
# Compare multiple heat treatment cycles
from example_complete_cqt_simulation import demonstrate_manufacturing_design
demonstrate_manufacturing_design()

# Compare different steel grades
from example_complete_cqt_simulation import demonstrate_material_selection
demonstrate_material_selection()
```

## 🧪 Validation Cases

Run the three validation cases from the research paper:

```python
# Validation Case 1: Carburizing of SCR420 steel
from validation_cases.case1_carburizing.validation_case1 import ValidationCase1
case1 = ValidationCase1()
case1.run_validation()

# This compares simulation vs experimental carbon profiles
# Target: MAE < 0.05 wt% for excellent agreement
```

## 📈 Expected Results (From Paper)

### Target Gear Requirements
- **Surface Hardness**: 58-62 HRC
- **Case Depth**: 0.6-0.7 mm (50 HRC threshold)
- **Core Hardness**: 32-48 HRC

### Typical Results for 8620 Steel (920°C, 6h, 1.0% CP)
- **Surface Carbon**: ~0.85 wt%
- **Case Depth**: ~0.65 mm
- **Surface Hardness**: ~60 HRC
- **Grain Size**: ~35 μm

### Material Comparison Results
- **8620**: Balanced properties, good case depth
- **4130**: Higher surface hardness, lower case depth
- **4320**: Higher case depth and core hardness

## 🔍 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure you're in the correct directory
cd "zed AI"
# Add to Python path if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Missing Dependencies**
```bash
# Install specific packages if missing
pip install numpy scipy matplotlib pandas
pip install fenics  # For FEM (optional)
```

**Validation Failures**
- Check steel composition matches paper exactly
- Verify process parameters (temperature, time, carbon potential)
- Ensure spatial/temporal discretization is sufficient

### Performance Tips

- Use fewer spatial points (21-31) for faster simulations
- Increase time steps for preliminary runs
- Enable parallel processing for parameter studies

## 📚 Next Steps

### 1. Study the Research Paper
Read the original paper to understand the theoretical background:
- Phase transformation kinetics
- Carbon diffusion mechanisms
- Grain growth theory
- Hardness prediction models

### 2. Run Validation Cases
```bash
python validation_cases/case1_carburizing/validation_case1.py
```
Target validation metrics:
- MAE < 0.10 wt% for carbon profiles
- R² > 0.90 for experimental correlation
- Relative error < 15%

### 3. Explore Applications
- Automotive gear design optimization
- Material selection for specific requirements
- Process parameter sensitivity analysis
- Cost optimization studies

### 4. Advanced Features
- Custom FEM implementations
- Multi-physics coupling
- Optimization algorithms
- Machine learning integration

## 🎓 Learning Resources

### Key Equations Implemented
- **Equation 1**: AE3 temperature calculation
- **Equations 2-4**: Grain growth kinetics
- **Equations 5-10**: Carbon diffusion (Fick's laws)
- **Equations 11-14**: Phase transformation kinetics
- **Equations 15-18**: Maynier hardness equations
- **Equations 19-25**: Tempering hardness models
- **Equations 26-29**: Thermal modeling

### Validation References
1. Kim et al. (2011) - Carburizing validation
2. Inoue et al. (2007) - C-Q process validation  
3. Medlin et al. (1999) - Complete C-Q-T validation

### Steel Grades Included
- **SCR420**: Validation steel (automotive)
- **JIS-SCR420H**: Enhanced SCR420 variant
- **SAE 4320**: High-nickel gear steel
- **8620**: Standard automotive gear steel
- **4130**: High-chromium alternative
- **4320**: High-nickel alternative

## 🆘 Need Help?

1. **Check the Examples**: `example_complete_cqt_simulation.py`
2. **Run Tests**: `python test_framework.py`
3. **Review Documentation**: Each module has detailed docstrings
4. **Validation Data**: Compare your results with experimental values

## 🎯 Success Criteria

You'll know the framework is working correctly when:

✅ All tests pass (`python test_framework.py`)
✅ Validation cases show good agreement (MAE < 0.10 wt%)
✅ Results match expected ranges from the paper
✅ Material comparisons show expected trends
✅ Process optimization identifies viable cycles

**Ready to start? Run the complete example:**

```bash
python example_complete_cqt_simulation.py
```

This will demonstrate all major capabilities and generate validation plots!