// ================================================================================================
// API SERVICE LAYER
// Comprehensive API client for C-Q-T Steel Heat Treatment Simulator backend
// ================================================================================================

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  SimulationRequest,
  SimulationResults,
  ValidationResponse,
  SteelGradesResponse,
  QuenchMediaResponse,
  MaterialComparisonRequest,
  MaterialComparisonResponse,
  ProcessOptimizationRequest,
  ProcessOptimizationResult,
  ApiResponse
} from '../types/simulation';

// ================================================================================================
// API CONFIGURATION
// ================================================================================================

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 300000, // 5 minutes for complex simulations
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });

    // Request interceptor for logging and auth
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        return this.handleApiError(error);
      }
    );
  }

  // ================================================================================================
  // ERROR HANDLING
  // ================================================================================================

  private handleApiError(error: AxiosError): Promise<never> {
    let errorMessage = 'An unexpected error occurred';
    let errorDetails: any = {};

    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data as any;

      switch (status) {
        case 400:
          errorMessage = data?.detail || 'Invalid request parameters';
          errorDetails = data?.validation_errors || {};
          break;
        case 401:
          errorMessage = 'Authentication required';
          break;
        case 403:
          errorMessage = 'Access forbidden';
          break;
        case 404:
          errorMessage = 'Resource not found';
          break;
        case 422:
          errorMessage = 'Validation error';
          errorDetails = data?.detail || {};
          break;
        case 500:
          errorMessage = 'Internal server error';
          errorDetails = data?.detail || 'Server processing error';
          break;
        case 503:
          errorMessage = 'Service temporarily unavailable';
          break;
        default:
          errorMessage = `Server error (${status})`;
      }

      console.error(`API Error ${status}:`, errorMessage, errorDetails);
    } else if (error.request) {
      // Network error
      errorMessage = 'Network connection error. Please check your internet connection.';
      console.error('Network Error:', error.request);
    } else {
      // Request setup error
      errorMessage = error.message;
      console.error('Request Setup Error:', error.message);
    }

    const enhancedError = new Error(errorMessage) as any;
    enhancedError.originalError = error;
    enhancedError.details = errorDetails;
    enhancedError.status = error.response?.status;

    return Promise.reject(enhancedError);
  }

  // ================================================================================================
  // HEALTH CHECK
  // ================================================================================================

  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    const response = await this.client.get('/api/health');
    return response.data;
  }

  // ================================================================================================
  // SIMULATION ENDPOINTS
  // ================================================================================================

  async runSimulation(request: SimulationRequest): Promise<ApiResponse<SimulationResults>> {
    console.log('Starting simulation with request:', request);
    const response = await this.client.post('/api/simulate', request);
    return response.data;
  }

  async validateInputs(request: SimulationRequest): Promise<ApiResponse<ValidationResponse>> {
    const response = await this.client.post('/api/validate-inputs', request);
    return response.data;
  }

  async getSimulationResults(calculationId: string): Promise<ApiResponse<SimulationResults>> {
    const response = await this.client.get(`/api/results/${calculationId}`);
    return response.data;
  }

  async deleteSimulation(calculationId: string): Promise<ApiResponse<{ message: string }>> {
    const response = await this.client.delete(`/api/results/${calculationId}`);
    return response.data;
  }

  async listCalculations(): Promise<ApiResponse<{ calculations: string[] }>> {
    const response = await this.client.get('/api/calculations');
    return response.data;
  }

  // ================================================================================================
  // STEEL GRADES AND MATERIALS
  // ================================================================================================

  async getSteelGrades(): Promise<ApiResponse<SteelGradesResponse>> {
    const response = await this.client.get('/api/steel-grades');
    return response.data;
  }

  async getQuenchMedia(): Promise<ApiResponse<QuenchMediaResponse>> {
    const response = await this.client.get('/api/quench-media');
    return response.data;
  }

  // ================================================================================================
  // MATERIAL COMPARISON
  // ================================================================================================

  async compareMaterials(
    steelGrades: string[],
    processConditions: MaterialComparisonRequest['process_conditions']
  ): Promise<ApiResponse<MaterialComparisonResponse>> {
    const request: MaterialComparisonRequest = {
      steel_grades: steelGrades,
      process_conditions: processConditions
    };

    console.log('Starting material comparison:', request);
    const response = await this.client.post('/api/compare-materials', request);
    return response.data;
  }

  // ================================================================================================
  // PROCESS OPTIMIZATION
  // ================================================================================================

  async optimizeProcess(
    targetCaseDepth: number,
    steelGrade: string,
    constraints: ProcessOptimizationRequest['constraints'],
    objective: string = 'minimize_time'
  ): Promise<ApiResponse<ProcessOptimizationResult>> {
    const request: ProcessOptimizationRequest = {
      target_case_depth: targetCaseDepth,
      steel_grade: steelGrade,
      constraints: constraints,
      optimization_objective: objective
    };

    console.log('Starting process optimization:', request);
    const response = await this.client.post('/api/optimize-process', request);
    return response.data;
  }

  // ================================================================================================
  // PROCESS RECOMMENDATIONS
  // ================================================================================================

  async getProcessRecommendations(
    steelGrade: string,
    partGeometry: any,
    requirements: any
  ): Promise<ApiResponse<{ recommendations: any[] }>> {
    const request = {
      steel_grade: steelGrade,
      part_geometry: partGeometry,
      requirements: requirements
    };

    const response = await this.client.post('/api/process-recommendations', request);
    return response.data;
  }

  // ================================================================================================
  // UTILITY METHODS
  // ================================================================================================

  async downloadResults(calculationId: string, format: 'json' | 'xlsx' | 'pdf' = 'json'): Promise<Blob> {
    const response = await this.client.get(`/api/export/${calculationId}`, {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }

  async uploadSteelComposition(file: File): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/upload-steel-composition', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }

  // ================================================================================================
  // BATCH OPERATIONS
  // ================================================================================================

  async batchSimulation(requests: SimulationRequest[]): Promise<ApiResponse<SimulationResults[]>> {
    const response = await this.client.post('/api/batch-simulate', { simulations: requests });
    return response.data;
  }

  async parametricStudy(
    baseRequest: SimulationRequest,
    parameters: { parameter: string; values: number[] }[]
  ): Promise<ApiResponse<any>> {
    const request = {
      base_simulation: baseRequest,
      parameter_variations: parameters
    };

    const response = await this.client.post('/api/parametric-study', request);
    return response.data;
  }
}

// ================================================================================================
// SINGLETON INSTANCE
// ================================================================================================

export const simulationService = new ApiService();

// ================================================================================================
// UTILITY FUNCTIONS
// ================================================================================================

export const createDefaultSimulationRequest = (): SimulationRequest => {
  return {
    steel_composition: {
      grade: '',
      C: 0.20,
      Si: 0.25,
      Mn: 0.80,
      Ni: 0.55,
      Cr: 0.50,
      Mo: 0.20,
      V: 0.0,
      W: 0.0,
      Cu: 0.0,
      P: 0.0,
      Al: 0.0,
      As: 0.0,
      Ti: 0.0
    },
    carburizing: {
      temperature: 920,
      time_hours: 6.0,
      carbon_potential: 1.0,
      heating_rate: 5.0,
      atmosphere_type: 'endothermic',
      gas_flow_rate: 1.0,
      mass_transfer_coefficient: 1e-4
    },
    quenching: {
      quench_medium: 'oil',
      quench_temperature: 60,
      agitation_rate: 1.0,
      quench_time: 300,
      delay_time: 0
    },
    tempering: {
      temperature: 170,
      time_hours: 2.0,
      heating_rate: 2.0,
      cooling_method: 'air',
      multiple_tempers: false,
      temper_cycles: 1
    },
    geometry: {
      geometry_type: 'cylinder',
      diameter: 25.0,
      characteristic_dimension: 25.0
    },
    initial_conditions: {
      initial_grain_size: 20.0,
      surface_condition: 'machined',
      prior_heat_treatment: 'annealed'
    },
    simulation_params: {
      spatial_points: 51,
      time_step_carburizing: 60,
      time_step_quenching: 1,
      max_analysis_depth: 5.0,
      convergence_tolerance: 1e-6,
      output_resolution: 'standard'
    }
  };
};

export const validateSimulationRequest = (request: Partial<SimulationRequest>): string[] => {
  const errors: string[] = [];

  // Required fields validation
  if (!request.steel_composition) {
    errors.push('Steel composition is required');
  } else {
    if (!request.steel_composition.C || request.steel_composition.C < 0.01 || request.steel_composition.C > 2.0) {
      errors.push('Carbon content must be between 0.01% and 2.0%');
    }
  }

  if (!request.carburizing) {
    errors.push('Carburizing conditions are required');
  } else {
    if (request.carburizing.temperature < 850 || request.carburizing.temperature > 1050) {
      errors.push('Carburizing temperature must be between 850°C and 1050°C');
    }
    if (request.carburizing.time_hours < 0.5 || request.carburizing.time_hours > 24) {
      errors.push('Carburizing time must be between 0.5 and 24 hours');
    }
  }

  if (!request.quenching) {
    errors.push('Quenching conditions are required');
  }

  if (!request.tempering) {
    errors.push('Tempering conditions are required');
  }

  if (!request.geometry) {
    errors.push('Part geometry is required');
  } else {
    if (!request.geometry.characteristic_dimension || request.geometry.characteristic_dimension < 1) {
      errors.push('Characteristic dimension must be at least 1 mm');
    }
  }

  return errors;
};

export default simulationService;