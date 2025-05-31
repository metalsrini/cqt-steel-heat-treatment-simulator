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
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  AlertTitle,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  Stack,
  Tooltip,
  IconButton,
  SelectChangeEvent
} from '@mui/material';
import {
  Compare as CompareIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  PlayArrow as PlayArrowIcon,
  Science as ScienceIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import Plot from 'react-plotly.js';
import { Data, Config } from 'plotly.js';
import {
  SteelGradesResponse,
  MaterialComparisonResponse,
  MaterialComparisonResult,
  CarburizingConditions,
  QuenchingConditions,
  TemperingConditions,
  PartGeometry
} from '../types/simulation';

interface MaterialComparisonProps {
  steelGrades: SteelGradesResponse;
  onCompare: (steelGrades: string[], processConditions: any) => Promise<MaterialComparisonResponse>;
  loading: boolean;
}

const MaterialComparison: React.FC<MaterialComparisonProps> = ({
  steelGrades,
  onCompare,
  loading
}) => {
  const [selectedGrades, setSelectedGrades] = useState<string[]>([]);
  const [comparisonResults, setComparisonResults] = useState<MaterialComparisonResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>(['selection']);

  // Process conditions for comparison
  const [processConditions, setProcessConditions] = useState({
    carburizing: {
      temperature: 920,
      time_hours: 6.0,
      carbon_potential: 1.0,
      heating_rate: 5.0,
      atmosphere_type: 'endothermic',
      gas_flow_rate: 1.0,
      mass_transfer_coefficient: 1e-4
    } as CarburizingConditions,
    quenching: {
      quench_medium: 'oil',
      quench_temperature: 60,
      agitation_rate: 1.0,
      quench_time: 300,
      delay_time: 0
    } as QuenchingConditions,
    tempering: {
      temperature: 170,
      time_hours: 2.0,
      heating_rate: 2.0,
      cooling_method: 'air',
      multiple_tempers: false,
      temper_cycles: 1
    } as TemperingConditions,
    geometry: {
      geometry_type: 'cylinder',
      diameter: 25.0,
      characteristic_dimension: 25.0
    } as PartGeometry
  });

  const handleGradeSelection = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    setSelectedGrades(typeof value === 'string' ? value.split(',') : value);
  };

  const handleRemoveGrade = (gradeToRemove: string) => {
    setSelectedGrades(prev => prev.filter(grade => grade !== gradeToRemove));
  };

  const handleSectionToggle = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const handleProcessConditionChange = (section: string, field: string, value: any) => {
    setProcessConditions(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [field]: value
      }
    }));
  };

  const handleRunComparison = useCallback(async () => {
    if (selectedGrades.length < 2) {
      setError('Please select at least 2 steel grades for comparison');
      return;
    }

    try {
      setError(null);
      const results = await onCompare(selectedGrades, processConditions);
      setComparisonResults(results);
    } catch (err: any) {
      setError(err.message || 'Comparison failed');
    }
  }, [selectedGrades, processConditions, onCompare]);

  const comparisonChart = useMemo(() => {
    if (!comparisonResults) return null;

    const data = comparisonResults.comparison_results.map((result, index) => ({
      x: result.results.property_profiles.distance_mm,
      y: result.results.property_profiles.hardness_hrc,
      type: 'scatter',
      mode: 'lines',
      name: result.steel_grade,
      line: { width: 3 }
    }));

    return {
      data,
      layout: {
        title: {
          text: 'Hardness Profile Comparison',
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
  }, [comparisonResults]);

  const exportResults = () => {
    if (!comparisonResults) return;
    
    const dataStr = JSON.stringify(comparisonResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `material_comparison_${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <Box sx={{ maxWidth: 1200, margin: '0 auto' }}>
      <Paper elevation={2} sx={{ padding: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 3 }}>
          <CompareIcon sx={{ marginRight: 2, color: 'primary.main', fontSize: 32 }} />
          <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Material Comparison
          </Typography>
          {comparisonResults && (
            <Tooltip title="Export Comparison Results">
              <IconButton onClick={exportResults} color="primary">
                <DownloadIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Steel Grade Selection */}
        <Accordion
          expanded={expandedSections.includes('selection')}
          onChange={() => handleSectionToggle('selection')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <ScienceIcon sx={{ marginRight: 1, color: 'primary.main' }} />
              <Typography variant="h6">Steel Grade Selection</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Select Steel Grades to Compare</InputLabel>
                  <Select
                    multiple
                    value={selectedGrades}
                    onChange={handleGradeSelection}
                    label="Select Steel Grades to Compare"
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip
                            key={value}
                            label={value}
                            onDelete={() => handleRemoveGrade(value)}
                            deleteIcon={<ClearIcon />}
                          />
                        ))}
                      </Box>
                    )}
                  >
                    {steelGrades?.grades && Object.keys(steelGrades.grades).map((grade) => (
                      <MenuItem key={grade} value={grade}>
                        {grade} - {steelGrades.grades[grade].description}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="textSecondary">
                  Selected {selectedGrades.length} steel grades. Minimum 2 required for comparison.
                </Typography>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Process Conditions */}
        <Accordion
          expanded={expandedSections.includes('process')}
          onChange={() => handleSectionToggle('process')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AssessmentIcon sx={{ marginRight: 1, color: 'primary.main' }} />
              <Typography variant="h6">Process Conditions</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Carburizing Conditions
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Temperature (°C)"
                  type="number"
                  value={processConditions.carburizing.temperature}
                  onChange={(e) => handleProcessConditionChange('carburizing', 'temperature', Number(e.target.value))}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Time (hours)"
                  type="number"
                  value={processConditions.carburizing.time_hours}
                  onChange={(e) => handleProcessConditionChange('carburizing', 'time_hours', Number(e.target.value))}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Carbon Potential (wt%)"
                  type="number"
                  value={processConditions.carburizing.carbon_potential}
                  onChange={(e) => handleProcessConditionChange('carburizing', 'carbon_potential', Number(e.target.value))}
                  size="small"
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom sx={{ marginTop: 2 }}>
                  Quenching Conditions
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Quench Medium</InputLabel>
                  <Select
                    value={processConditions.quenching.quench_medium}
                    onChange={(e) => handleProcessConditionChange('quenching', 'quench_medium', e.target.value)}
                    label="Quench Medium"
                  >
                    <MenuItem value="oil">Oil</MenuItem>
                    <MenuItem value="water">Water</MenuItem>
                    <MenuItem value="air">Air</MenuItem>
                    <MenuItem value="polymer">Polymer</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Temperature (°C)"
                  type="number"
                  value={processConditions.quenching.quench_temperature}
                  onChange={(e) => handleProcessConditionChange('quenching', 'quench_temperature', Number(e.target.value))}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Quench Time (s)"
                  type="number"
                  value={processConditions.quenching.quench_time}
                  onChange={(e) => handleProcessConditionChange('quenching', 'quench_time', Number(e.target.value))}
                  size="small"
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom sx={{ marginTop: 2 }}>
                  Tempering Conditions
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Temperature (°C)"
                  type="number"
                  value={processConditions.tempering.temperature}
                  onChange={(e) => handleProcessConditionChange('tempering', 'temperature', Number(e.target.value))}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Time (hours)"
                  type="number"
                  value={processConditions.tempering.time_hours}
                  onChange={(e) => handleProcessConditionChange('tempering', 'time_hours', Number(e.target.value))}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Characteristic Dimension (mm)"
                  type="number"
                  value={processConditions.geometry.characteristic_dimension}
                  onChange={(e) => handleProcessConditionChange('geometry', 'characteristic_dimension', Number(e.target.value))}
                  size="small"
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Run Comparison Button */}
        <Box sx={{ marginY: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleRunComparison}
            disabled={loading || selectedGrades.length < 2}
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            sx={{ minWidth: 200, height: 48 }}
          >
            {loading ? 'Running Comparison...' : 'Run Comparison'}
          </Button>
        </Box>

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ marginBottom: 3 }}>
            <AlertTitle>Comparison Error</AlertTitle>
            {error}
          </Alert>
        )}

        {/* Comparison Results */}
        {comparisonResults && (
          <Box sx={{ marginTop: 4 }}>
            <Typography variant="h6" gutterBottom>
              Comparison Results
            </Typography>

            {/* Performance Ranking */}
            <Card elevation={2} sx={{ marginBottom: 3 }}>
              <CardHeader title="Performance Ranking" />
              <CardContent>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {comparisonResults.ranking.map((grade, index) => (
                    <Chip
                      key={grade}
                      label={`${index + 1}. ${grade}`}
                      color={index === 0 ? 'success' : index === 1 ? 'primary' : 'default'}
                      variant={index < 2 ? 'filled' : 'outlined'}
                    />
                  ))}
                </Stack>
              </CardContent>
            </Card>

            {/* Hardness Profile Comparison Chart */}
            {comparisonChart && (
              <Paper elevation={2} sx={{ padding: 2, marginBottom: 3 }}>
                <Plot
                  data={comparisonChart.data as Data[]}
                  layout={comparisonChart.layout}
                  config={comparisonChart.config as Partial<Config>}
                  style={{ width: '100%', height: '500px' }}
                />
              </Paper>
            )}

            {/* Detailed Comparison Table */}
            <Card elevation={2}>
              <CardHeader title="Detailed Comparison" />
              <CardContent>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Steel Grade</TableCell>
                        <TableCell align="right">Surface Hardness (HRC)</TableCell>
                        <TableCell align="right">Core Hardness (HRC)</TableCell>
                        <TableCell align="right">Case Depth (0.4% C)</TableCell>
                        <TableCell align="right">Case Depth (50 HRC)</TableCell>
                        <TableCell align="right">Surface Carbon (%)</TableCell>
                        <TableCell align="right">Overall Grade</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {comparisonResults.comparison_results.map((result) => (
                        <TableRow key={result.steel_grade}>
                          <TableCell component="th" scope="row">
                            <Typography fontWeight={600}>{result.steel_grade}</Typography>
                          </TableCell>
                          <TableCell align="right">
                            {result.results.process_metrics.surface_hardness_hrc.toFixed(1)}
                          </TableCell>
                          <TableCell align="right">
                            {result.results.process_metrics.core_hardness_hrc.toFixed(1)}
                          </TableCell>
                          <TableCell align="right">
                            {result.results.case_depth_results.case_depth_04_carbon.toFixed(2)} mm
                          </TableCell>
                          <TableCell align="right">
                            {result.results.case_depth_results.case_depth_50_hrc.toFixed(2)} mm
                          </TableCell>
                          <TableCell align="right">
                            {result.results.process_metrics.surface_carbon.toFixed(2)}
                          </TableCell>
                          <TableCell align="right">
                            <Chip
                              label={result.results.quality_assessment.overall_grade}
                              color={result.results.quality_assessment.overall_grade === 'A' ? 'success' : 
                                     result.results.quality_assessment.overall_grade === 'B' ? 'primary' : 'warning'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default MaterialComparison;