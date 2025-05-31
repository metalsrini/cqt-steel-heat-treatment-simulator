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
  Stack,
  Divider,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Thermostat as ThermostatIcon,
  Speed as SpeedIcon,
  LocalFireDepartment as LocalFireDepartmentIcon,
  AcUnit as AcUnitIcon,
  Download as DownloadIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import Plot from 'react-plotly.js';
import { Data, Config } from 'plotly.js';
import { SimulationResults, SimulationRequest } from '../types/simulation';

interface ThermalAnalysisProps {
  results: SimulationResults | null;
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
      id={`thermal-tabpanel-${index}`}
      aria-labelledby={`thermal-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

const ThermalAnalysis: React.FC<ThermalAnalysisProps> = ({ results, inputData }) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Complete thermal cycle chart
  const thermalCycleChart = useMemo(() => {
    if (!results) return null;

    const { thermal_profiles } = results;
    
    // Combine carburizing and quenching data
    const carburizingTime = thermal_profiles.time_carburizing;
    const carburizingTemp = thermal_profiles.temperature_carburizing;
    const quenchingTime = thermal_profiles.time_quenching.map(t => carburizingTime[carburizingTime.length - 1] + t / 3600);
    const quenchingTemp = thermal_profiles.temperature_quenching;

    return {
      data: [
        {
          x: carburizingTime,
          y: carburizingTemp,
          type: 'scatter',
          mode: 'lines',
          name: 'Carburizing',
          line: { color: '#d32f2f', width: 3 },
          hovertemplate: 'Time: %{x:.1f} h<br>Temperature: %{y:.0f}°C<extra></extra>'
        },
        {
          x: quenchingTime,
          y: quenchingTemp,
          type: 'scatter',
          mode: 'lines',
          name: 'Quenching',
          line: { color: '#1976d2', width: 3 },
          hovertemplate: 'Time: %{x:.3f} h<br>Temperature: %{y:.0f}°C<extra></extra>'
        },
        {
          x: [carburizingTime[carburizingTime.length - 1], carburizingTime[carburizingTime.length - 1] + inputData?.tempering.time_hours!],
          y: [inputData?.tempering.temperature!, inputData?.tempering.temperature!],
          type: 'scatter',
          mode: 'lines',
          name: 'Tempering',
          line: { color: '#f57c00', width: 3 },
          hovertemplate: 'Time: %{x:.1f} h<br>Temperature: %{y:.0f}°C<extra></extra>'
        }
      ],
      layout: {
        title: {
          text: 'Complete Thermal Cycle',
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
  }, [results, inputData]);

  // Cooling rate analysis chart
  const coolingRateChart = useMemo(() => {
    if (!results) return null;

    const { thermal_profiles } = results;
    const quenchingTime = thermal_profiles.time_quenching;
    const quenchingTemp = thermal_profiles.temperature_quenching;
    
    // Calculate instantaneous cooling rates
    const coolingRates = [];
    const timePoints = [];
    
    for (let i = 1; i < quenchingTemp.length; i++) {
      const deltaT = quenchingTemp[i] - quenchingTemp[i-1];
      const deltaTime = (quenchingTime[i] - quenchingTime[i-1]) / 3600; // Convert to hours
      const rate = Math.abs(deltaT / deltaTime); // °C/h
      
      coolingRates.push(rate);
      timePoints.push(quenchingTime[i]);
    }

    return {
      data: [
        {
          x: timePoints,
          y: coolingRates,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Cooling Rate',
          line: { color: '#1976d2', width: 2 },
          marker: { size: 4, color: '#1976d2' },
          hovertemplate: 'Time: %{x:.0f} s<br>Cooling Rate: %{y:.0f} °C/h<extra></extra>'
        }
      ],
      layout: {
        title: {
          text: 'Cooling Rate During Quenching',
          font: { size: 18, family: 'Roboto, sans-serif' }
        },
        xaxis: {
          title: 'Time (seconds)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        yaxis: {
          title: 'Cooling Rate (°C/h)',
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

  // Critical temperatures visualization
  const criticalTemperaturesChart = useMemo(() => {
    if (!results) return null;

    const { critical_temperatures } = results;
    const temperatures = [
      { name: 'AE3', value: critical_temperatures.ae3_temperature, color: '#d32f2f' },
      { name: 'AE1', value: critical_temperatures.ae1_temperature, color: '#f57c00' },
      { name: 'Ms (Surface)', value: critical_temperatures.ms_temperature_surface, color: '#1976d2' },
      { name: 'Ms (Core)', value: critical_temperatures.ms_temperature_core, color: '#388e3c' },
      { name: 'Bs', value: critical_temperatures.bs_temperature, color: '#7b1fa2' }
    ];

    return {
      data: [
        {
          x: temperatures.map(t => t.name),
          y: temperatures.map(t => t.value),
          type: 'bar',
          marker: {
            color: temperatures.map(t => t.color)
          },
          hovertemplate: '%{x}: %{y:.0f}°C<extra></extra>'
        }
      ],
      layout: {
        title: {
          text: 'Critical Transformation Temperatures',
          font: { size: 18, family: 'Roboto, sans-serif' }
        },
        xaxis: {
          title: 'Phase Transformation',
          gridcolor: '#f0f0f0'
        },
        yaxis: {
          title: 'Temperature (°C)',
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

  // Heat flux visualization
  const heatFluxChart = useMemo(() => {
    if (!results) return null;

    const { thermal_profiles } = results;
    
    return {
      data: [
        {
          x: thermal_profiles.time_quenching,
          y: thermal_profiles.surface_heat_flux,
          type: 'scatter',
          mode: 'lines',
          name: 'Surface Heat Flux',
          line: { color: '#f57c00', width: 3 },
          hovertemplate: 'Time: %{x:.0f} s<br>Heat Flux: %{y:.0f} W/m²<extra></extra>'
        }
      ],
      layout: {
        title: {
          text: 'Surface Heat Flux During Quenching',
          font: { size: 18, family: 'Roboto, sans-serif' }
        },
        xaxis: {
          title: 'Time (seconds)',
          gridcolor: '#f0f0f0',
          showgrid: true
        },
        yaxis: {
          title: 'Heat Flux (W/m²)',
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

  const exportThermalData = () => {
    if (!results) return;
    
    const thermalData = {
      thermal_profiles: results.thermal_profiles,
      critical_temperatures: results.critical_temperatures,
      input_conditions: inputData,
      timestamp: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(thermalData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `thermal_analysis_${results.calculation_id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  if (!results) {
    return (
      <Paper sx={{ padding: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="textSecondary">
          No thermal analysis data available
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ marginTop: 1 }}>
          Please run a simulation first to view thermal analysis
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 3 }}>
        <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600 }}>
          Thermal Analysis
        </Typography>
        <Tooltip title="Export Thermal Data">
          <IconButton onClick={exportThermalData} color="primary">
            <DownloadIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Key Thermal Metrics */}
      <Grid container spacing={3} sx={{ marginBottom: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2} sx={{ borderLeft: '4px solid', borderLeftColor: 'primary.main' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                <SpeedIcon sx={{ color: 'primary.main', marginRight: 1 }} />
                <Typography variant="h6" sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
                  {results.thermal_profiles.cooling_rate.toFixed(1)} °C/s
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Average Cooling Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2} sx={{ borderLeft: '4px solid', borderLeftColor: 'secondary.main' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                <ThermostatIcon sx={{ color: 'secondary.main', marginRight: 1 }} />
                <Typography variant="h6" sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
                  {results.critical_temperatures.ae3_temperature.toFixed(0)}°C
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                AE3 Temperature
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2} sx={{ borderLeft: '4px solid', borderLeftColor: 'info.main' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                <AcUnitIcon sx={{ color: 'info.main', marginRight: 1 }} />
                <Typography variant="h6" sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
                  {results.critical_temperatures.ms_temperature_surface.toFixed(0)}°C
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Ms Temperature (Surface)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2} sx={{ borderLeft: '4px solid', borderLeftColor: 'warning.main' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                <LocalFireDepartmentIcon sx={{ color: 'warning.main', marginRight: 1 }} />
                <Typography variant="h6" sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
                  {inputData?.carburizing.temperature || 0}°C
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Carburizing Temperature
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Navigation tabs */}
      <Paper elevation={1} sx={{ marginBottom: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Thermal Cycle" icon={<TimelineIcon />} iconPosition="start" />
          <Tab label="Cooling Analysis" icon={<TrendingDownIcon />} iconPosition="start" />
          <Tab label="Critical Temperatures" icon={<ThermostatIcon />} iconPosition="start" />
          <Tab label="Process Data" icon={<TrendingUpIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Tab panels */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ padding: 2 }}>
              {thermalCycleChart && (
                <Plot
                  data={thermalCycleChart.data as Data[]}
                  layout={thermalCycleChart.layout}
                  config={thermalCycleChart.config as Partial<Config>}
                  style={{ width: '100%', height: '500px' }}
                />
              )}
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardHeader title="Process Summary" />
              <CardContent>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="textSecondary">Total Cycle Time</Typography>
                    <Typography variant="h6">
                      {((inputData?.carburizing.time_hours || 0) + 
                        (inputData?.quenching.quench_time || 0) / 3600 + 
                        (inputData?.tempering.time_hours || 0)).toFixed(1)} hours
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="textSecondary">Peak Temperature</Typography>
                    <Typography variant="h6">{inputData?.carburizing.temperature || 0}°C</Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="textSecondary">Quench Medium</Typography>
                    <Typography variant="h6">{inputData?.quenching.quench_medium || 'N/A'}</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper elevation={2} sx={{ padding: 2 }}>
              {coolingRateChart && (
                <Plot
                  data={coolingRateChart.data as Data[]}
                  layout={coolingRateChart.layout}
                  config={coolingRateChart.config as Partial<Config>}
                  style={{ width: '100%', height: '400px' }}
                />
              )}
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardHeader title="Cooling Analysis" />
              <CardContent>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="body2" color="textSecondary">Average Cooling Rate</Typography>
                    <Typography variant="h6">{results.thermal_profiles.cooling_rate.toFixed(1)} °C/s</Typography>
                  </Box>
                  <Divider />
                  <Box>
                    <Typography variant="body2" color="textSecondary">Quench Time</Typography>
                    <Typography variant="h6">{inputData?.quenching.quench_time || 0} seconds</Typography>
                  </Box>
                  <Divider />
                  <Box>
                    <Typography variant="body2" color="textSecondary">Quench Temperature</Typography>
                    <Typography variant="h6">{inputData?.quenching.quench_temperature || 0}°C</Typography>
                  </Box>
                  <Divider />
                  <Box>
                    <Typography variant="body2" color="textSecondary">Distortion Risk</Typography>
                    <Chip 
                      label={results.process_metrics.distortion_risk}
                      color={results.process_metrics.distortion_risk === 'Low' ? 'success' : 
                             results.process_metrics.distortion_risk === 'Medium' ? 'warning' : 'error'}
                      size="small"
                    />
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ padding: 2 }}>
              {heatFluxChart && (
                <Plot
                  data={heatFluxChart.data as Data[]}
                  layout={heatFluxChart.layout}
                  config={heatFluxChart.config as Partial<Config>}
                  style={{ width: '100%', height: '350px' }}
                />
              )}
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper elevation={2} sx={{ padding: 2 }}>
              {criticalTemperaturesChart && (
                <Plot
                  data={criticalTemperaturesChart.data as Data[]}
                  layout={criticalTemperaturesChart.layout}
                  config={criticalTemperaturesChart.config as Partial<Config>}
                  style={{ width: '100%', height: '400px' }}
                />
              )}
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardHeader title="Critical Temperatures" />
              <CardContent>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell>AE3 (Austenite Formation)</TableCell>
                        <TableCell align="right">{results.critical_temperatures.ae3_temperature.toFixed(0)}°C</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>AE1 (Eutectoid)</TableCell>
                        <TableCell align="right">{results.critical_temperatures.ae1_temperature.toFixed(0)}°C</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Ms Surface (Martensite Start)</TableCell>
                        <TableCell align="right">{results.critical_temperatures.ms_temperature_surface.toFixed(0)}°C</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Ms Core (Martensite Start)</TableCell>
                        <TableCell align="right">{results.critical_temperatures.ms_temperature_core.toFixed(0)}°C</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Bs (Bainite Start)</TableCell>
                        <TableCell align="right">{results.critical_temperatures.bs_temperature.toFixed(0)}°C</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardHeader title="Process Conditions" />
              <CardContent>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Process Stage</TableCell>
                        <TableCell align="right">Temperature</TableCell>
                        <TableCell align="right">Time</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>Carburizing</TableCell>
                        <TableCell align="right">{inputData?.carburizing.temperature}°C</TableCell>
                        <TableCell align="right">{inputData?.carburizing.time_hours} hours</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Quenching</TableCell>
                        <TableCell align="right">{inputData?.quenching.quench_temperature}°C</TableCell>
                        <TableCell align="right">{inputData?.quenching.quench_time} seconds</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Tempering</TableCell>
                        <TableCell align="right">{inputData?.tempering.temperature}°C</TableCell>
                        <TableCell align="right">{inputData?.tempering.time_hours} hours</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card elevation={2}>
              <CardHeader title="Thermal Properties" />
              <CardContent>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell>Heating Rate (Carburizing)</TableCell>
                        <TableCell align="right">{inputData?.carburizing.heating_rate} °C/min</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Carbon Potential</TableCell>
                        <TableCell align="right">{inputData?.carburizing.carbon_potential} wt%</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Atmosphere Type</TableCell>
                        <TableCell align="right">{inputData?.carburizing.atmosphere_type}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Agitation Rate</TableCell>
                        <TableCell align="right">{inputData?.quenching.agitation_rate} (relative)</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Tempering Cycles</TableCell>
                        <TableCell align="right">{inputData?.tempering.temper_cycles}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default ThermalAnalysis;