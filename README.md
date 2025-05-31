# Integrated C-Q-T Modeling Framework for Steel Gears

This project replicates the exact research from: **"Integrated Modeling of Carburizing-Quenching-Tempering of Steel Gears for an ICME Framework"** by Danish Khan and BP Gautham (2018).

## Project Overview

Complete implementation of the integrated computational modeling framework for carburizing-quenching-tempering (C-Q-T) process chain used in steel gear manufacturing, designed for Integrated Computational Materials Engineering (ICME) workflows.

### Key Features

- **Exact Mathematical Models**: All equations from the research paper implemented precisely
- **Chemical Composition Dependency**: Models work with any steel composition  
- **Integrated FEM Framework**: Sequential process coupling with information flow
- **Complete Validation**: Three validation cases against experimental data
- **ICME Workflow**: Automated gear design and optimization
- **Manufacturing Design**: Process parameter optimization capabilities
- **Material Selection**: Composition-dependent optimization

## Project Structure

```
├── core/                           # Core mathematical models and algorithms
│   ├── mathematical_models/        # All equations from the research paper
│   │   ├── phase_transformation.py # Phase transformation kinetics
│   │   ├── thermal_models.py       # Heat conduction modeling
│   │   ├── carbon_diffusion.py     # Carbon diffusion during carburizing
│   │   ├── grain_growth.py         # Grain growth kinetics
│   │   └── hardness_prediction.py  # Hardness calculation models
│   ├── material_properties/        # Steel compositions and properties
│   ├── fem_solver/                 # FEM implementation
│   └── validation/                 # Validation against experimental data
│
├── process_models/                 # Individual process implementations
│   ├── carburizing/                # Carbon diffusion and grain growth
│   ├── quenching/                  # Phase transformation kinetics  
│   ├── tempering/                  # Hardness evolution
│   └── thermal/                    # Heat conduction modeling
│
├── integration/                    # Process chain coupling
│   ├── process_chain/              # Sequential process integration
│   ├── information_flow/           # Data transfer between simulations
│   └── automation/                 # Automation and wrapper scripts
│
├── icme_framework/                 # ICME workflow implementation
│   ├── gear_module/                # Automated gear design module
│   ├── material_selection/         # Composition optimization
│   └── manufacturing_design/       # Process parameter optimization
│
├── validation_cases/               # Three validation cases from paper
│   ├── case1_carburizing/          # SCR420 steel gear ring
│   ├── case2_cq_process/           # JIS-SCR420H steel gear ring
│   └── case3_cqt_process/          # SAE 4320 steel fatigue specimen
│
├── applications/                   # Practical applications
│   ├── spur_gear_design/           # 8620 steel spur gear example
│   ├── material_comparison/        # Steel grade comparisons
│   └── process_optimization/       # Heat treatment optimization
│
└── data/                          # Data and results
    ├── steel_compositions/         # Chemical composition database
    ├── experimental_data/          # Literature validation data
    └── results/                   # Simulation outputs
```

## Mathematical Models Implemented

### 1. Austenitization During Heating
- **Equation (1)**: AE3 temperature calculation with chemical composition dependency
- Supports all major alloying elements (C, Si, Mn, Ni, Cr, Mo, V, W, Cu, P, Al, As, Ti)

### 2. Grain Growth During Carburizing
- **Equations (2-4)**: Chemical composition-dependent power law expression
- Activation energy calculation for different steel compositions
- Differential form for non-isothermal conditions

### 3. Carbon Diffusion During Carburizing
- **Equations (5-10)**: Fick's laws with mass transfer boundary conditions
- Temperature and composition-dependent diffusivity
- Mass balance at steel surface

### 4. Phase Transformation During Quenching
- **Equation (11)**: Semi-empirical kinetic equations for diffusional transformations
- **Equation (12)**: Koistinen-Marburger equation for martensitic transformation
- **Equations (13-14)**: Ms temperature with high carbon correction factor

### 5. Hardness Prediction
- **Equations (15-18)**: Maynier equations for individual phase hardness
- **Equations (19-25)**: Tempering hardness using Jaffe-Holloman equivalence
- Vickers to Rockwell conversion

### 6. Thermal Modeling
- **Equations (26-29)**: 3D Fourier heat conduction with convective/radiative boundaries
- Rule of mixtures for thermal properties

## Installation

### Dependencies
```bash
pip install numpy scipy matplotlib pandas
pip install fenics mshr  # For FEM implementation
pip install pyyaml jsonschema  # For configuration management
```

### Quick Start
```python
from core.mathematical_models import PhaseTransformationModels, SteelComposition

# Define steel composition
steel_8620 = SteelComposition(
    C=0.20, Si=0.25, Mn=0.80, Ni=0.50, Cr=0.50, Mo=0.20
)

# Initialize models
models = PhaseTransformationModels()

# Calculate critical temperatures
ae3 = models.calculate_ae3_temperature(steel_8620)
ms_temp = models.calculate_ms_temperature(steel_8620)

print(f"AE3 Temperature: {ae3:.1f}°C")
print(f"Ms Temperature: {ms_temp:.1f}°C")
```

## Validation Cases

### Case 1: Carburizing Validation
- **Steel**: SCR420
- **Reference**: Kim et al. (2011)
- **Validation**: Carbon profile along radial section

### Case 2: Carburizing-Quenching Validation  
- **Steel**: JIS-SCR420H
- **Reference**: Inoue et al. (2007)
- **Validation**: Vickers hardness distribution

### Case 3: Complete C-Q-T Validation
- **Steel**: SAE 4320
- **Reference**: Medlin et al. (1999)
- **Validation**: Surface hardness, retained austenite, case depth

## Applications

### Manufacturing Design
- Heat treatment cycle optimization for 8620 steel spur gears
- Process parameter exploration (temperature, time, atmosphere)
- Case depth and hardness requirement achievement

### Material Selection
- Comparison of 8620, 4130, and 4320 steel grades
- Composition-dependent property prediction
- Optimization for specific performance requirements

### ICME Integration
- Automated gear design module
- Manufacturing process design space exploration
- Material and process co-optimization

## Usage Examples

### Basic Hardness Calculation
```python
from core.mathematical_models import PhaseTransformationModels

models = PhaseTransformationModels()
steel = SteelComposition(C=0.20, Mn=0.80, Cr=0.50)

# Calculate phase hardness values
cooling_rate = 100.0  # °C/hr
phase_hardness = models.calculate_phase_hardness(steel, cooling_rate)

# Convert to Rockwell
hrc = models.convert_vickers_to_rockwell(600.0)
```

### Complete Process Chain Simulation
```python
from integration.process_chain import CQTProcessChain

# Define process parameters
process_params = {
    'carburizing_temp': 920,      # °C
    'carburizing_time': 6,        # hours
    'carbon_potential': 1.0,      # %
    'quenching_temp': 60,         # °C
    'tempering_temp': 170,        # °C
    'tempering_time': 2           # hours
}

# Run integrated simulation
chain = CQTProcessChain(steel_composition, gear_geometry)
results = chain.run_simulation(process_params)
```

## Research Citation

```
Khan, D., Gautham, B. Integrated Modeling of Carburizing-Quenching-Tempering of Steel Gears 
for an ICME Framework. Integr Mater Manuf Innov 7, 28–41 (2018). 
https://doi.org/10.1007/s40192-018-0107-x
```

## License

This implementation is provided for educational and research purposes, replicating the methodologies described in the referenced research paper.

## Contributing

This project aims for exact replication of the research paper methodologies. Contributions should maintain scientific accuracy and reference validation against experimental data.