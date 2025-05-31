// ================================================================================================
// SIMULATION TYPE DEFINITIONS
// Complete TypeScript interfaces matching backend Pydantic models
// ================================================================================================

export interface SteelCompositionInput {
  grade?: string;
  C: number;
  Si: number;
  Mn: number;
  Ni: number;
  Cr: number;
  Mo: number;
  V: number;
  W: number;
  Cu: number;
  P: number;
  Al: number;
  As: number;
  Ti: number;
}

export interface CarburizingConditions {
  temperature: number;
  time_hours: number;
  carbon_potential: number;
  heating_rate: number;
  atmosphere_type: string;
  gas_flow_rate: number;
  mass_transfer_coefficient: number;
  diffusion_temperature?: number;
  diffusion_time?: number;
}

export interface QuenchingConditions {
  quench_medium: string;
  quench_temperature: number;
  heat_transfer_coefficient?: number;
  agitation_rate: number;
  quench_time: number;
  delay_time: number;
}

export interface TemperingConditions {
  temperature: number;
  time_hours: number;
  heating_rate: number;
  cooling_method: string;
  multiple_tempers: boolean;
  temper_cycles: number;
}

export interface PartGeometry {
  geometry_type: string;
  diameter?: number;
  length?: number;
  thickness?: number;
  characteristic_dimension: number;
  surface_area?: number;
  volume?: number;
}

export interface InitialConditions {
  initial_grain_size: number;
  initial_hardness?: number;
  surface_condition: string;
  prior_heat_treatment: string;
}

export interface SimulationParameters {
  spatial_points: number;
  time_step_carburizing: number;
  time_step_quenching: number;
  max_analysis_depth: number;
  convergence_tolerance: number;
  output_resolution: string;
}

export interface SimulationRequest {
  steel_composition: SteelCompositionInput;
  carburizing: CarburizingConditions;
  quenching: QuenchingConditions;
  tempering: TemperingConditions;
  geometry: PartGeometry;
  initial_conditions: InitialConditions;
  simulation_params: SimulationParameters;
  calculation_id?: string;
}

export interface PropertyProfile {
  distance_mm: number[];
  carbon_profile: number[];
  hardness_hv: number[];
  hardness_hrc: number[];
  grain_size: number[];
  phase_fractions: Record<string, number[]>;
}

export interface ThermalProfile {
  time_carburizing: number[];
  temperature_carburizing: number[];
  time_quenching: number[];
  temperature_quenching: number[];
  cooling_rate: number;
  surface_heat_flux: number[];
}

export interface CaseDepthResults {
  case_depth_04_carbon: number;
  case_depth_03_carbon: number;
  case_depth_50_hrc: number;
  case_depth_55_hrc: number;
  effective_case_depth: number;
  total_case_depth: number;
}

export interface ProcessMetrics {
  surface_carbon: number;
  surface_hardness_hv: number;
  surface_hardness_hrc: number;
  core_hardness_hv: number;
  core_hardness_hrc: number;
  hardness_gradient: number;
  carbon_gradient: number;
  distortion_risk: string;
  grain_size_surface: number;
  grain_size_core: number;
}

export interface CriticalTemperatures {
  ae3_temperature: number;
  ae1_temperature: number;
  ms_temperature_core: number;
  ms_temperature_surface: number;
  bs_temperature: number;
}

export interface QualityAssessment {
  gear_requirements_met: boolean;
  surface_hardness_ok: boolean;
  case_depth_ok: boolean;
  core_hardness_ok: boolean;
  grain_size_ok: boolean;
  overall_grade: string;
  recommendations: string[];
}

export interface SimulationResults {
  calculation_id: string;
  timestamp: string;
  computation_time: number;
  property_profiles: PropertyProfile;
  thermal_profiles: ThermalProfile;
  case_depth_results: CaseDepthResults;
  process_metrics: ProcessMetrics;
  critical_temperatures: CriticalTemperatures;
  quality_assessment: QualityAssessment;
  input_summary: Record<string, any>;
  warnings: string[];
  errors: string[];
  validation_status: string;
}

// ================================================================================================
// API RESPONSE TYPES
// ================================================================================================

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ValidationResponse {
  valid: boolean;
  error?: string;
  warnings: string[];
}

export interface SteelGrade {
  name: string;
  composition: SteelCompositionInput;
  description: string;
  applications: string[];
  typical_properties: Record<string, number>;
}

export interface SteelGradesResponse {
  grades: Record<string, SteelGrade>;
}

export interface QuenchMedium {
  name: string;
  typical_temperature: number;
  heat_transfer_coefficient_range: [number, number];
  description: string;
  applications: string[];
}

export interface QuenchMediaResponse {
  media: Record<string, QuenchMedium>;
}

export interface MaterialComparisonRequest {
  steel_grades: string[];
  process_conditions: {
    carburizing: CarburizingConditions;
    quenching: QuenchingConditions;
    tempering: TemperingConditions;
    geometry: PartGeometry;
  };
}

export interface MaterialComparisonResult {
  steel_grade: string;
  results: SimulationResults;
  relative_performance: Record<string, number>;
}

export interface MaterialComparisonResponse {
  comparison_results: MaterialComparisonResult[];
  ranking: string[];
  summary: Record<string, any>;
}

export interface ProcessOptimizationRequest {
  target_case_depth: number;
  steel_grade: string;
  constraints: {
    temperature_range: [number, number];
    time_range: [number, number];
    carbon_potential_range: [number, number];
  };
  optimization_objective: string;
}

export interface ProcessOptimizationResult {
  optimized_conditions: {
    carburizing: CarburizingConditions;
    quenching: QuenchingConditions;
    tempering: TemperingConditions;
  };
  predicted_results: SimulationResults;
  optimization_score: number;
  convergence_info: Record<string, any>;
}

// ================================================================================================
// UI STATE TYPES
// ================================================================================================

export interface FormErrors {
  [key: string]: string | undefined;
}

export interface LoadingState {
  simulation: boolean;
  validation: boolean;
  comparison: boolean;
  optimization: boolean;
}

export interface NotificationState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

export interface ChartData {
  x: number[];
  y: number[];
  name: string;
  type?: string;
  mode?: string;
  line?: Record<string, any>;
  marker?: Record<string, any>;
}

export interface PlotlyData {
  data: ChartData[];
  layout: Record<string, any>;
  config?: Record<string, any>;
}

// ================================================================================================
// FORM VALIDATION SCHEMAS
// ================================================================================================

export interface ValidationRules {
  steel_composition: {
    [K in keyof SteelCompositionInput]: {
      min?: number;
      max?: number;
      required?: boolean;
    };
  };
  carburizing: {
    [K in keyof CarburizingConditions]: {
      min?: number;
      max?: number;
      required?: boolean;
      options?: string[];
    };
  };
  quenching: {
    [K in keyof QuenchingConditions]: {
      min?: number;
      max?: number;
      required?: boolean;
      options?: string[];
    };
  };
  tempering: {
    [K in keyof TemperingConditions]: {
      min?: number;
      max?: number;
      required?: boolean;
      options?: string[];
    };
  };
  geometry: {
    [K in keyof PartGeometry]: {
      min?: number;
      max?: number;
      required?: boolean;
      options?: string[];
    };
  };
}

// ================================================================================================
// CHART CONFIGURATION TYPES
// ================================================================================================

export interface ChartConfig {
  title: string;
  xAxis: {
    title: string;
    unit: string;
  };
  yAxis: {
    title: string;
    unit: string;
  };
  showLegend: boolean;
  height: number;
  colors: string[];
}

export interface DashboardChartConfigs {
  caseDepthProfile: ChartConfig;
  carbonProfile: ChartConfig;
  hardnessDistribution: ChartConfig;
  thermalHistory: ChartConfig;
  phaseTransformation: ChartConfig;
  grainSizeDistribution: ChartConfig;
}