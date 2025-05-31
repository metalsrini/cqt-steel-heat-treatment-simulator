import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  AlertTitle,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Divider,
  Stack,
  Tooltip,
  IconButton,
  InputAdornment
} from '@mui/material';
import {
  Calculate as CalculateIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  PlayArrow as PlayArrowIcon,
  TrendingUp as TrendingUpIcon,
  Settings as SettingsIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Speed as SpeedIcon,
  LocalFireDepartment as LocalFireDepartmentIcon
} from '@mui/icons-material';
import Plot from 'react-plotly.js';
import { Data, Config } from 'plotly.js';
import {
  SteelGradesResponse,
  ProcessOptimizationResult,
  ProcessOptimizationRequest
} from '../types/simulation';

interface ProcessOptimizationProps {
  steelGrades: SteelGradesResponse;
  onOptimize: (targetCaseDepth: number, steelGrade: string, constraints: any, objective?: string) => Promise<ProcessOptimizationResult>;
  loading: boolean;
}

const ProcessOptimization: React.FC<ProcessOptimizationProps> = ({
  steelGrades,
  onOptimize,
  loading
}) => {
  const [targetCaseDepth, setTargetCaseDepth] = useState<number>(1.0);
  const [selectedGrade, setSelectedGrade] = useState<string>('8620');
  const [optimizationObjective, setOptimizationObjective] = useState<string>('minimize_time');
  const [optimizationResults, setOptimizationResults] = useState<ProcessOptimizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>(['target', 'constraints']);

  // Optimization constraints
  const [constraints, setConstraints] = useState({
    temperature_range: [900, 1000] as [number, number],
    time_range: [2.0, 12.0] as [number, number],
    carbon_potential_range: [0.8, 1.2] as [number, number]
  });

  const handleSectionToggle = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const handleConstraintChange = (constraint: string, index: number, value: number) => {
    setConstraints(prev => ({
      ...prev,
      [constraint]: [
        index === 0 ? value : prev[constraint as keyof typeof prev][0],
        index === 1 ? value : prev[constraint as keyof typeof prev][1]
      ]
    }));
  };

  const handleRunOptimization = useCallback(async () => {
    if (!selectedGrade || targetCaseDepth <= 0) {
      setError('Please specify a valid target case depth and steel grade');
      return;
    }

    try {
      setError(null);
      const results = await onOptimize(targetCaseDepth, selectedGrade, constraints, optimizationObjective);
      setOptimizationResults(results);
    } catch (err: any) {
      setError(err.message || 'Optimization failed');
    }
  }, [targetCaseDepth, selectedGrade, constraints, optimizationObjective, onOptimize]);

  const optimizationChart = useMemo(() => {
    if (!optimizationResults) return null;

    const { predicted_results } = optimizationResults;
    
    return {
      data: [
        {
          x: predicted_results.property_profiles.distance_mm,
          y: predicted_results.property_profiles.hardness_hrc,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Optimized Hardness Profile',
          line: { color: '#1976d2', width: 3 },
          marker: { size: 4, color: '#1976d2' }
        },
        {
          x: [targetCaseDepth, targetCaseDepth],
          y: [0, Math.max(...predicted_results.property_profiles.hardness_hrc)],
          type: 'scatter',
          mode: 'lines',
          name: `Target Case Depth (${targetCaseDepth} mm)`,
          line: { color: '#f57c00', width: 3, dash: 'dash' }
        },
        {
          x: [predicted_results.case_depth_results.case_depth_04_carbon, predicted_results.case_depth_results.case_depth_04_carbon],
          y: [0, Math.max(...predicted_results.property_profiles.hardness_hrc)],
          type: 'scatter',
          mode: 'lines',
          name: 'Achieved Case Depth (0.4% C)',
          line: { color: '#388e3c', width: 2, dash: 'dot' }
        }
      ],
      layout: {
        title: {
          text: 'Optimized Case Depth Profile',
          font: { size: 18, family: 'Roboto, sans-serif' }
        },
        xaxis: {
          title: 'Distance from Surface (mm)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        yaxis: {
          title: 'Hardness (HRC)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        showlegend: true,
        legend: { x: 0.6, y: 0.9 },
        margin: { t: 60, r: 40, b: 60, l: 60 },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white'
      },
      config: {
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d']
      }
    };
  }, [optimizationResults, targetCaseDepth]);

  const exportResults = () => {
    if (!optimizationResults) return;
    
    const dataStr = JSON.stringify(optimizationResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `process_optimization_${selectedGrade}_${targetCaseDepth}mm.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const achievedCaseDepth = optimizationResults?.predicted_results.case_depth_results.case_depth_04_carbon || 0;
  const accuracy = optimizationResults ? (1 - Math.abs(achievedCaseDepth - targetCaseDepth) / targetCaseDepth) * 100 : 0;

  return (
    <Box sx={{ maxWidth: 1200, margin: '0 auto' }}>
      <Paper elevation={2} sx={{ padding: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 3 }}>
          <CalculateIcon sx={{ marginRight: 2, color: 'primary.main', fontSize: 32 }} />
          <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Process Optimization
          </Typography>
          {optimizationResults && (
            <Tooltip title="Export Optimization Results">
              <IconButton onClick={exportResults} color="primary">
                <DownloadIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Target Specification */}
        <Accordion
          expanded={expandedSections.includes('target')}
          onChange={() => handleSectionToggle('target')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TrendingUpIcon sx={{ marginRight: 1, color: 'primary.main' }} />
              <Typography variant="h6">Target Specification</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Target Case Depth"
                  type="number"
                  value={targetCaseDepth}
                  onChange={(e) => setTargetCaseDepth(Number(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">mm</InputAdornment>,
                    inputProps: { min: 0.1, max: 10.0, step: 0.1 }
                  }}
                  helperText="Target case depth at 0.4% carbon"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Steel Grade</InputLabel>
                  <Select
                    value={selectedGrade}
                    onChange={(e) => setSelectedGrade(e.target.value)}
                    label="Steel Grade"
                  >
                    {steelGrades?.grades && Object.keys(steelGrades.grades).map((grade) => (
                      <MenuItem key={grade} value={grade}>
                        {grade} - {steelGrades.grades[grade].description}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Optimization Objective</InputLabel>
                  <Select
                    value={optimizationObjective}
                    onChange={(e) => setOptimizationObjective(e.target.value)}
                    label="Optimization Objective"
                  >
                    <MenuItem value="minimize_time">Minimize Process Time</MenuItem>
                    <MenuItem value="minimize_temperature">Minimize Temperature</MenuItem>
                    <MenuItem value="maximize_uniformity">Maximize Uniformity</MenuItem>
                    <MenuItem value="minimize_cost">Minimize Energy Cost</MenuItem>
                    <MenuItem value="maximize_hardness">Maximize Surface Hardness</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Optimization Constraints */}
        <Accordion
          expanded={expandedSections.includes('constraints')}
          onChange={() => handleSectionToggle('constraints')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <SettingsIcon sx={{ marginRight: 1, color: 'primary.main' }} />
              <Typography variant="h6">Process Constraints</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Temperature Range (°C)
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Minimum Temperature"
                  type="number"
                  value={constraints.temperature_range[0]}
                  onChange={(e) => handleConstraintChange('temperature_range', 0, Number(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">°C</InputAdornment>
                  }}
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Maximum Temperature"
                  type="number"
                  value={constraints.temperature_range[1]}
                  onChange={(e) => handleConstraintChange('temperature_range', 1, Number(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">°C</InputAdornment>
                  }}
                  size="small"
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom sx={{ marginTop: 2 }}>
                  Time Range (hours)
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Minimum Time"
                  type="number"
                  value={constraints.time_range[0]}
                  onChange={(e) => handleConstraintChange('time_range', 0, Number(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hours</InputAdornment>
                  }}
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Maximum Time"
                  type="number"
                  value={constraints.time_range[1]}
                  onChange={(e) => handleConstraintChange('time_range', 1, Number(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">hours</InputAdornment>
                  }}
                  size="small"
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom sx={{ marginTop: 2 }}>
                  Carbon Potential Range (wt%)
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Minimum Carbon Potential"
                  type="number"
                  value={constraints.carbon_potential_range[0]}
                  onChange={(e) => handleConstraintChange('carbon_potential_range', 0, Number(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">wt%</InputAdornment>
                  }}
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Maximum Carbon Potential"
                  type="number"
                  value={constraints.carbon_potential_range[1]}
                  onChange={(e) => handleConstraintChange('carbon_potential_range', 1, Number(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">wt%</InputAdornment>
                  }}
                  size="small"
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Run Optimization Button */}
        <Box sx={{ marginY: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleRunOptimization}
            disabled={loading || !selectedGrade || targetCaseDepth <= 0}
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            sx={{ minWidth: 200, height: 48 }}
          >
            {loading ? 'Optimizing...' : 'Run Optimization'}
          </Button>
        </Box>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ marginBottom: 3 }}>
            <AlertTitle>Optimization Error</AlertTitle>
            {error}
          </Alert>
        )}

        {/* Optimization Results */}
        {optimizationResults && (
          <Box sx={{ marginTop: 4 }}>
            <Typography variant="h6" gutterBottom>
              Optimization Results
            </Typography>

            {/* Optimization Summary */}
            <Grid container spacing={3} sx={{ marginBottom: 3 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={2}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                      <TrendingUpIcon sx={{ color: 'primary.main', marginRight: 1 }} />
                      <Typography variant="h6" sx={{ fontSize: '1.1rem' }}>
                        {achievedCaseDepth.toFixed(2)} mm
                      </Typography>
                      {accuracy > 95 ? (
                        <CheckCircleIcon sx={{ color: 'success.main', marginLeft: 'auto' }} />
                      ) : (
                        <WarningIcon sx={{ color: 'warning.main', marginLeft: 'auto' }} />
                      )}
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Achieved Case Depth
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Accuracy: {accuracy.toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={2}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                      <SpeedIcon sx={{ color: 'secondary.main', marginRight: 1 }} />
                      <Typography variant="h6" sx={{ fontSize: '1.1rem' }}>
                        {optimizationResults.optimization_score.toFixed(2)}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Optimization Score
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Higher is better
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={2}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                      <LocalFireDepartmentIcon sx={{ color: 'warning.main', marginRight: 1 }} />
                      <Typography variant="h6" sx={{ fontSize: '1.1rem' }}>
                        {optimizationResults.optimized_conditions.carburizing.temperature}°C
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Optimized Temperature
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Carburizing temperature
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={2}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                      <TimelineIcon sx={{ color: 'info.main', marginRight: 1 }} />
                      <Typography variant="h6" sx={{ fontSize: '1.1rem' }}>
                        {optimizationResults.optimized_conditions.carburizing.time_hours} h
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Optimized Time
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Carburizing time
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Optimization Chart */}
            {optimizationChart && (
              <Paper elevation={2} sx={{ padding: 2, marginBottom: 3 }}>
                <Plot
                  data={optimizationChart.data as Data[]}
                  layout={optimizationChart.layout}
                  config={optimizationChart.config as Partial<Config>}
                  style={{ width: '100%', height: '500px' }}
                />
              </Paper>
            )}

            {/* Optimized Process Parameters */}
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card elevation={2}>
                  <CardHeader title="Optimized Process Conditions" />
                  <CardContent>
                    <TableContainer>
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell><strong>Carburizing</strong></TableCell>
                            <TableCell></TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ paddingLeft: 3 }}>Temperature</TableCell>
                            <TableCell align="right">{optimizationResults.optimized_conditions.carburizing.temperature}°C</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ paddingLeft: 3 }}>Time</TableCell>
                            <TableCell align="right">{optimizationResults.optimized_conditions.carburizing.time_hours} hours</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ paddingLeft: 3 }}>Carbon Potential</TableCell>
                            <TableCell align="right">{optimizationResults.optimized_conditions.carburizing.carbon_potential} wt%</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell><strong>Quenching</strong></TableCell>
                            <TableCell></TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ paddingLeft: 3 }}>Medium</TableCell>
                            <TableCell align="right">{optimizationResults.optimized_conditions.quenching.quench_medium}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ paddingLeft: 3 }}>Temperature</TableCell>
                            <TableCell align="right">{optimizationResults.optimized_conditions.quenching.quench_temperature}°C</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell><strong>Tempering</strong></TableCell>
                            <TableCell></TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ paddingLeft: 3 }}>Temperature</TableCell>
                            <TableCell align="right">{optimizationResults.optimized_conditions.tempering.temperature}°C</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ paddingLeft: 3 }}>Time</TableCell>
                            <TableCell align="right">{optimizationResults.optimized_conditions.tempering.time_hours} hours</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card elevation={2}>
                  <CardHeader title="Predicted Results" />
                  <CardContent>
                    <TableContainer>
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell>Surface Hardness</TableCell>
                            <TableCell align="right">
                              {optimizationResults.predicted_results.process_metrics.surface_hardness_hrc.toFixed(1)} HRC
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Core Hardness</TableCell>
                            <TableCell align="right">
                              {optimizationResults.predicted_results.process_metrics.core_hardness_hrc.toFixed(1)} HRC
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Case Depth (0.4% C)</TableCell>
                            <TableCell align="right">
                              {optimizationResults.predicted_results.case_depth_results.case_depth_04_carbon.toFixed(2)} mm
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Case Depth (50 HRC)</TableCell>
                            <TableCell align="right">
                              {optimizationResults.predicted_results.case_depth_results.case_depth_50_hrc.toFixed(2)} mm
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Surface Carbon</TableCell>
                            <TableCell align="right">
                              {optimizationResults.predicted_results.process_metrics.surface_carbon.toFixed(2)} wt%
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Overall Grade</TableCell>
                            <TableCell align="right">
                              <Chip
                                label={optimizationResults.predicted_results.quality_assessment.overall_grade}
                                color={optimizationResults.predicted_results.quality_assessment.overall_grade === 'A' ? 'success' : 
                                       optimizationResults.predicted_results.quality_assessment.overall_grade === 'B' ? 'primary' : 'warning'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Convergence Information */}
            {optimizationResults.convergence_info && (
              <Alert severity="info" sx={{ marginTop: 3 }}>
                <AlertTitle>Convergence Information</AlertTitle>
                <Typography variant="body2">
                  Optimization completed successfully with convergence criteria met.
                </Typography>
              </Alert>
            )}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default ProcessOptimization;