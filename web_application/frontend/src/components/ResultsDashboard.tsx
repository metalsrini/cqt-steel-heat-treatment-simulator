import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Paper,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  AlertTitle,
  IconButton,
  Tooltip,
  Stack,
  Divider,
  Button
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Science as ScienceIcon,
  TrendingUp as TrendingUpIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Print as PrintIcon,
  Visibility as VisibilityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import Plot from 'react-plotly.js';
import { Data, Config } from 'plotly.js';
import { SimulationResults, SimulationRequest } from '../types/simulation';

interface ResultsDashboardProps {
  results: SimulationResults;
  inputData: SimulationRequest | null;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`results-tabpanel-${index}`}
      aria-labelledby={`results-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ results, inputData }) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Key metrics for dashboard cards
  const keyMetrics = useMemo(() => {
    const { process_metrics, case_depth_results, quality_assessment } = results;
    return [
      {
        title: 'Surface Hardness',
        value: `${process_metrics.surface_hardness_hrc.toFixed(1)} HRC`,
        subtitle: `${process_metrics.surface_hardness_hv.toFixed(0)} HV`,
        icon: <ScienceIcon />,
        color: 'primary',
        status: quality_assessment.surface_hardness_ok ? 'success' : 'warning'
      },
      {
        title: 'Case Depth (0.4% C)',
        value: `${case_depth_results.case_depth_04_carbon.toFixed(2)} mm`,
        subtitle: `Effective: ${case_depth_results.effective_case_depth.toFixed(2)} mm`,
        icon: <TrendingUpIcon />,
        color: 'secondary',
        status: quality_assessment.case_depth_ok ? 'success' : 'warning'
      },
      {
        title: 'Core Hardness',
        value: `${process_metrics.core_hardness_hrc.toFixed(1)} HRC`,
        subtitle: `${process_metrics.core_hardness_hv.toFixed(0)} HV`,
        icon: <AssessmentIcon />,
        color: 'info',
        status: quality_assessment.core_hardness_ok ? 'success' : 'warning'
      },
      {
        title: 'Overall Grade',
        value: quality_assessment.overall_grade,
        subtitle: quality_assessment.gear_requirements_met ? 'Gear Spec Met' : 'Review Required',
        icon: quality_assessment.gear_requirements_met ? <CheckCircleIcon /> : <WarningIcon />,
        color: quality_assessment.gear_requirements_met ? 'success' : 'warning',
        status: quality_assessment.gear_requirements_met ? 'success' : 'warning'
      }
    ];
  }, [results]);

  // Case depth profile chart (PRIMARY VISUALIZATION)
  const caseDepthChart = useMemo(() => {
    const { property_profiles } = results;
    
    return {
      data: [
        {
          x: property_profiles.distance_mm,
          y: property_profiles.hardness_hrc,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Hardness Profile',
          line: { color: '#1976d2', width: 3 },
          marker: { size: 4, color: '#1976d2' }
        },
        {
          x: [results.case_depth_results.case_depth_04_carbon, results.case_depth_results.case_depth_04_carbon],
          y: [0, Math.max(...property_profiles.hardness_hrc)],
          type: 'scatter',
          mode: 'lines',
          name: 'Case Depth (0.4% C)',
          line: { color: '#f57c00', width: 2, dash: 'dash' }
        },
        {
          x: [results.case_depth_results.case_depth_50_hrc, results.case_depth_results.case_depth_50_hrc],
          y: [0, Math.max(...property_profiles.hardness_hrc)],
          type: 'scatter',
          mode: 'lines',
          name: 'Case Depth (50 HRC)',
          line: { color: '#d32f2f', width: 2, dash: 'dot' }
        }
      ],
      layout: {
        title: {
          text: 'Case Depth Profile - Hardness vs Distance',
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
        legend: { x: 0.7, y: 0.9 },
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
  }, [results]);

  // Carbon profile chart
  const carbonProfileChart = useMemo(() => {
    const { property_profiles } = results;
    
    return {
      data: [
        {
          x: property_profiles.distance_mm,
          y: property_profiles.carbon_profile,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Carbon Content',
          line: { color: '#388e3c', width: 3 },
          marker: { size: 4, color: '#388e3c' }
        },
        {
          x: property_profiles.distance_mm,
          y: property_profiles.distance_mm.map(() => 0.4),
          type: 'scatter',
          mode: 'lines',
          name: '0.4% C Reference',
          line: { color: '#f57c00', width: 2, dash: 'dash' }
        }
      ],
      layout: {
        title: {
          text: 'Carbon Profile vs Distance',
          font: { size: 18, family: 'Roboto, sans-serif' }
        },
        xaxis: {
          title: 'Distance from Surface (mm)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        yaxis: {
          title: 'Carbon Content (wt%)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        showlegend: true,
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
  }, [results]);

  // Thermal history chart
  const thermalChart = useMemo(() => {
    const { thermal_profiles } = results;
    
    return {
      data: [
        {
          x: thermal_profiles.time_carburizing,
          y: thermal_profiles.temperature_carburizing,
          type: 'scatter',
          mode: 'lines',
          name: 'Carburizing',
          line: { color: '#d32f2f', width: 3 }
        },
        {
          x: thermal_profiles.time_quenching.map(t => t / 3600), // Convert to hours
          y: thermal_profiles.temperature_quenching,
          type: 'scatter',
          mode: 'lines',
          name: 'Quenching',
          line: { color: '#1976d2', width: 3 }
        }
      ],
      layout: {
        title: {
          text: 'Thermal History',
          font: { size: 18, family: 'Roboto, sans-serif' }
        },
        xaxis: {
          title: 'Time (hours)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        yaxis: {
          title: 'Temperature (°C)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        showlegend: true,
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
  }, [results]);

  // Grain size distribution chart
  const grainSizeChart = useMemo(() => {
    const { property_profiles } = results;
    
    return {
      data: [
        {
          x: property_profiles.distance_mm,
          y: property_profiles.grain_size,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Grain Size',
          line: { color: '#7b1fa2', width: 3 },
          marker: { size: 4, color: '#7b1fa2' }
        }
      ],
      layout: {
        title: {
          text: 'Grain Size Distribution',
          font: { size: 18, family: 'Roboto, sans-serif' }
        },
        xaxis: {
          title: 'Distance from Surface (mm)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        yaxis: {
          title: 'Grain Size (μm)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        showlegend: false,
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
  }, [results]);

  const exportResults = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `cqt_results_${results.calculation_id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header with actions */}
      <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 3 }}>
        <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600 }}>
          Simulation Results
        </Typography>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Export Results">
            <IconButton onClick={exportResults} color="primary">
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Share Results">
            <IconButton color="primary">
              <ShareIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Print Report">
            <IconButton color="primary">
              <PrintIcon />
            </IconButton>
          </Tooltip>
        </Stack>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ marginBottom: 4 }}>
        {keyMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              elevation={2}
              sx={{ 
                height: '100%',
                borderLeft: `4px solid`,
                borderLeftColor: `${metric.color}.main`
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                  <Box sx={{ color: `${metric.color}.main`, marginRight: 1 }}>
                    {metric.icon}
                  </Box>
                  <Typography variant="h6" sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
                    {metric.value}
                  </Typography>
                  <Box sx={{ marginLeft: 'auto' }}>
                    {metric.status === 'success' ? (
                      <CheckCircleIcon sx={{ color: 'success.main', fontSize: 20 }} />
                    ) : (
                      <WarningIcon sx={{ color: 'warning.main', fontSize: 20 }} />
                    )}
                  </Box>
                </Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {metric.title}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {metric.subtitle}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quality Assessment Alert */}
      <Alert 
        severity={results.quality_assessment.gear_requirements_met ? 'success' : 'warning'}
        sx={{ marginBottom: 3 }}
      >
        <AlertTitle>
          Quality Assessment - Grade {results.quality_assessment.overall_grade}
        </AlertTitle>
        <Typography variant="body2">
          {results.quality_assessment.gear_requirements_met 
            ? 'All requirements met for gear applications'
            : 'Some requirements may need review'
          }
        </Typography>
        {results.quality_assessment.recommendations.length > 0 && (
          <Box sx={{ marginTop: 1 }}>
            <Typography variant="body2" fontWeight={600}>Recommendations:</Typography>
            <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
              {results.quality_assessment.recommendations.map((rec, index) => (
                <li key={index}>
                  <Typography variant="body2">{rec}</Typography>
                </li>
              ))}
            </ul>
          </Box>
        )}
      </Alert>

      {/* Tabs for different views */}
      <Paper elevation={1} sx={{ marginBottom: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Case Depth Profile" icon={<TrendingUpIcon />} iconPosition="start" />
          <Tab label="Carbon Profile" icon={<ScienceIcon />} iconPosition="start" />
          <Tab label="Thermal History" icon={<TimelineIcon />} iconPosition="start" />
          <Tab label="Detailed Data" icon={<AssessmentIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Tab panels */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ padding: 2 }}>
              <Plot
                data={caseDepthChart.data as Data[]}
                layout={caseDepthChart.layout}
                config={caseDepthChart.config as Partial<Config>}
                style={{ width: '100%', height: '500px' }}
              />
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ padding: 2 }}>
              <Plot
                data={grainSizeChart.data as Data[]}
                layout={grainSizeChart.layout}
                config={grainSizeChart.config as Partial<Config>}
                style={{ width: '100%', height: '400px' }}
              />
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardHeader title="Case Depth Summary" />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">0.4% Carbon</Typography>
                    <Typography variant="h6">{results.case_depth_results.case_depth_04_carbon.toFixed(2)} mm</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">0.3% Carbon</Typography>
                    <Typography variant="h6">{results.case_depth_results.case_depth_03_carbon.toFixed(2)} mm</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">50 HRC</Typography>
                    <Typography variant="h6">{results.case_depth_results.case_depth_50_hrc.toFixed(2)} mm</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">55 HRC</Typography>
                    <Typography variant="h6">{results.case_depth_results.case_depth_55_hrc.toFixed(2)} mm</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Divider sx={{ marginY: 1 }} />
                    <Typography variant="body2" color="textSecondary">Effective Case Depth</Typography>
                    <Typography variant="h5" color="primary">{results.case_depth_results.effective_case_depth.toFixed(2)} mm</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ padding: 2 }}>
              <Plot
                data={carbonProfileChart.data as Data[]}
                layout={carbonProfileChart.layout}
                config={carbonProfileChart.config as Partial<Config>}
                style={{ width: '100%', height: '500px' }}
              />
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardHeader title="Carbon Analysis" />
              <CardContent>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="textSecondary">Surface Carbon</Typography>
                    <Typography variant="h6">{results.process_metrics.surface_carbon.toFixed(2)}%</Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="textSecondary">Carbon Gradient</Typography>
                    <Typography variant="h6">{results.process_metrics.carbon_gradient.toFixed(3)} %/mm</Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="textSecondary">Hardness Gradient</Typography>
                    <Typography variant="h6">{results.process_metrics.hardness_gradient.toFixed(1)} HRC/mm</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ padding: 2 }}>
              <Plot
                data={thermalChart.data as Data[]}
                layout={thermalChart.layout}
                config={thermalChart.config as Partial<Config>}
                style={{ width: '100%', height: '500px' }}
              />
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardHeader title="Critical Temperatures" />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">AE3</Typography>
                    <Typography variant="h6">{results.critical_temperatures.ae3_temperature.toFixed(0)}°C</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">AE1</Typography>
                    <Typography variant="h6">{results.critical_temperatures.ae1_temperature.toFixed(0)}°C</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Ms (Surface)</Typography>
                    <Typography variant="h6">{results.critical_temperatures.ms_temperature_surface.toFixed(0)}°C</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Ms (Core)</Typography>
                    <Typography variant="h6">{results.critical_temperatures.ms_temperature_core.toFixed(0)}°C</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardHeader title="Process Metrics" />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">Cooling Rate</Typography>
                    <Typography variant="h6">{results.thermal_profiles.cooling_rate.toFixed(1)} °C/s</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">Distortion Risk</Typography>
                    <Chip 
                      label={results.process_metrics.distortion_risk}
                      color={results.process_metrics.distortion_risk === 'Low' ? 'success' : 
                             results.process_metrics.distortion_risk === 'Medium' ? 'warning' : 'error'}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">Computation Time</Typography>
                    <Typography variant="body1">{results.computation_time.toFixed(2)} seconds</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardHeader title="Process Metrics" />
              <CardContent>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell>Surface Hardness (HV)</TableCell>
                        <TableCell align="right">{results.process_metrics.surface_hardness_hv.toFixed(0)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Surface Hardness (HRC)</TableCell>
                        <TableCell align="right">{results.process_metrics.surface_hardness_hrc.toFixed(1)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Core Hardness (HV)</TableCell>
                        <TableCell align="right">{results.process_metrics.core_hardness_hv.toFixed(0)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Core Hardness (HRC)</TableCell>
                        <TableCell align="right">{results.process_metrics.core_hardness_hrc.toFixed(1)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Surface Grain Size</TableCell>
                        <TableCell align="right">{results.process_metrics.grain_size_surface.toFixed(1)} μm</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Core Grain Size</TableCell>
                        <TableCell align="right">{results.process_metrics.grain_size_core.toFixed(1)} μm</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardHeader title="Input Summary" />
              <CardContent>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell>Steel Grade</TableCell>
                        <TableCell align="right">{inputData?.steel_composition.grade || 'Custom'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Carburizing Temp</TableCell>
                        <TableCell align="right">{inputData?.carburizing.temperature}°C</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Carburizing Time</TableCell>
                        <TableCell align="right">{inputData?.carburizing.time_hours}h</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Carbon Potential</TableCell>
                        <TableCell align="right">{inputData?.carburizing.carbon_potential}%</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Quench Medium</TableCell>
                        <TableCell align="right">{inputData?.quenching.quench_medium}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Tempering Temp</TableCell>
                        <TableCell align="right">{inputData?.tempering.temperature}°C</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Warnings and Errors */}
      {(results.warnings.length > 0 || results.errors.length > 0) && (
        <Box sx={{ marginTop: 3 }}>
          {results.warnings.length > 0 && (
            <Alert severity="warning" sx={{ marginBottom: 2 }}>
              <AlertTitle>Warnings</AlertTitle>
              {results.warnings.map((warning, index) => (
                <Typography key={index} variant="body2">• {warning}</Typography>
              ))}
            </Alert>
          )}
          {results.errors.length > 0 && (
            <Alert severity="error">
              <AlertTitle>Errors</AlertTitle>
              {results.errors.map((error, index) => (
                <Typography key={index} variant="body2">• {error}</Typography>
              ))}
            </Alert>
          )}
        </Box>
      )}
    </Box>
  );
};

export default ResultsDashboard;