import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Paper,
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
  LinearProgress,
  Tooltip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingUpIcon,
  Download as DownloadIcon,
  Print as PrintIcon,
  ExpandMore as ExpandMoreIcon,
  Science as ScienceIcon,
  Build as BuildIcon,
  Speed as SpeedIcon,
  Recommend as RecommendIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon
} from '@mui/icons-material';
import Plot from 'react-plotly.js';
import { Data, Config } from 'plotly.js';
import { SimulationResults, SimulationRequest } from '../types/simulation';

interface QualityReportProps {
  results: SimulationResults | null;
  inputData: SimulationRequest | null;
}

const QualityReport: React.FC<QualityReportProps> = ({ results, inputData }) => {
  const [expandedSections, setExpandedSections] = useState<string[]>(['overview', 'requirements']);

  const handleSectionToggle = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  // Quality metrics analysis
  const qualityMetrics = useMemo(() => {
    if (!results) return null;

    const { quality_assessment, process_metrics, case_depth_results } = results;
    
    return [
      {
        category: 'Surface Hardness',
        value: process_metrics.surface_hardness_hrc,
        target: '58-65 HRC',
        status: quality_assessment.surface_hardness_ok,
        score: quality_assessment.surface_hardness_ok ? 100 : 70,
        unit: 'HRC'
      },
      {
        category: 'Case Depth',
        value: case_depth_results.case_depth_04_carbon,
        target: '0.8-1.5 mm',
        status: quality_assessment.case_depth_ok,
        score: quality_assessment.case_depth_ok ? 100 : 75,
        unit: 'mm'
      },
      {
        category: 'Core Hardness',
        value: process_metrics.core_hardness_hrc,
        target: '25-35 HRC',
        status: quality_assessment.core_hardness_ok,
        score: quality_assessment.core_hardness_ok ? 100 : 65,
        unit: 'HRC'
      },
      {
        category: 'Grain Size',
        value: process_metrics.grain_size_surface,
        target: '< 50 μm',
        status: quality_assessment.grain_size_ok,
        score: quality_assessment.grain_size_ok ? 100 : 80,
        unit: 'μm'
      }
    ];
  }, [results]);

  // Overall quality score
  const overallScore = useMemo(() => {
    if (!qualityMetrics) return 0;
    return qualityMetrics.reduce((sum, metric) => sum + metric.score, 0) / qualityMetrics.length;
  }, [qualityMetrics]);

  // Quality spider chart
  const qualitySpiderChart = useMemo(() => {
    if (!qualityMetrics) return null;

    return {
      data: [
        {
          type: 'scatterpolar',
          r: qualityMetrics.map(m => m.score),
          theta: qualityMetrics.map(m => m.category),
          fill: 'toself',
          name: 'Current Quality',
          line: { color: '#1976d2' },
          fillcolor: 'rgba(25, 118, 210, 0.2)'
        },
        {
          type: 'scatterpolar',
          r: [100, 100, 100, 100],
          theta: qualityMetrics.map(m => m.category),
          fill: 'toself',
          name: 'Target Quality',
          line: { color: '#4caf50', dash: 'dash' },
          fillcolor: 'rgba(76, 175, 80, 0.1)'
        }
      ],
      layout: {
        polar: {
          radialaxis: {
            visible: true,
            range: [0, 100]
          }
        },
        showlegend: true,
        title: {
          text: 'Quality Assessment Radar',
          font: { size: 16, family: 'Roboto, sans-serif' }
        },
        margin: { t: 60, r: 40, b: 40, l: 40 }
      },
      config: {
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d']
      }
    };
  }, [qualityMetrics]);

  // Grade color mapping
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'success';
      case 'B': return 'primary';
      case 'C': return 'warning';
      case 'D': return 'error';
      default: return 'default';
    }
  };

  // Grade stars
  const renderGradeStars = (grade: string) => {
    const gradeMap = { 'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1 };
    const stars = gradeMap[grade as keyof typeof gradeMap] || 1;
    
    return (
      <Box sx={{ display: 'flex' }}>
        {[1, 2, 3, 4, 5].map((star) => (
          star <= stars ? 
            <StarIcon key={star} sx={{ color: 'gold', fontSize: 20 }} /> :
            <StarBorderIcon key={star} sx={{ color: 'grey.300', fontSize: 20 }} />
        ))}
      </Box>
    );
  };

  const exportReport = () => {
    if (!results) return;
    
    const report = {
      quality_assessment: results.quality_assessment,
      process_metrics: results.process_metrics,
      case_depth_results: results.case_depth_results,
      input_summary: results.input_summary,
      quality_metrics: qualityMetrics,
      overall_score: overallScore,
      timestamp: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(report, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `quality_report_${results.calculation_id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  if (!results) {
    return (
      <Paper sx={{ padding: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="textSecondary">
          No quality assessment data available
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ marginTop: 1 }}>
          Please run a simulation first to view quality report
        </Typography>
      </Paper>
    );
  }

  const { quality_assessment } = results;

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 3 }}>
        <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600 }}>
          Quality Assessment Report
        </Typography>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Export Report">
            <IconButton onClick={exportReport} color="primary">
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Print Report">
            <IconButton color="primary">
              <PrintIcon />
            </IconButton>
          </Tooltip>
        </Stack>
      </Box>

      {/* Overall Quality Overview */}
      <Accordion
        expanded={expandedSections.includes('overview')}
        onChange={() => handleSectionToggle('overview')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AssessmentIcon sx={{ marginRight: 1, color: 'primary.main' }} />
            <Typography variant="h6">Overall Quality Assessment</Typography>
            <Chip
              label={`Grade ${quality_assessment.overall_grade}`}
              color={getGradeColor(quality_assessment.overall_grade) as any}
              sx={{ marginLeft: 2 }}
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      margin: '0 auto 16px',
                      bgcolor: getGradeColor(quality_assessment.overall_grade) + '.main',
                      fontSize: '2rem'
                    }}
                  >
                    {quality_assessment.overall_grade}
                  </Avatar>
                  <Typography variant="h4" gutterBottom>
                    Grade {quality_assessment.overall_grade}
                  </Typography>
                  {renderGradeStars(quality_assessment.overall_grade)}
                  <Typography variant="h6" sx={{ marginTop: 2 }}>
                    {overallScore.toFixed(1)}% Quality Score
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={overallScore}
                    sx={{ marginTop: 2, height: 8, borderRadius: 4 }}
                  />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Compliance Status
                  </Typography>
                  <Stack spacing={2}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {quality_assessment.gear_requirements_met ? (
                        <CheckCircleIcon sx={{ color: 'success.main', marginRight: 1 }} />
                      ) : (
                        <ErrorIcon sx={{ color: 'error.main', marginRight: 1 }} />
                      )}
                      <Typography>
                        Gear Requirements: {quality_assessment.gear_requirements_met ? 'Met' : 'Not Met'}
                      </Typography>
                    </Box>
                    <Alert 
                      severity={quality_assessment.gear_requirements_met ? 'success' : 'warning'}
                      sx={{ marginTop: 2 }}
                    >
                      {quality_assessment.gear_requirements_met 
                        ? 'This part meets all standard gear application requirements.'
                        : 'This part may require process adjustments for gear applications.'
                      }
                    </Alert>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Individual Requirements */}
      <Accordion
        expanded={expandedSections.includes('requirements')}
        onChange={() => handleSectionToggle('requirements')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <CheckCircleIcon sx={{ marginRight: 1, color: 'primary.main' }} />
            <Typography variant="h6">Individual Requirements</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <TableContainer component={Paper} elevation={1}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Property</TableCell>
                      <TableCell align="right">Actual Value</TableCell>
                      <TableCell align="right">Target Range</TableCell>
                      <TableCell align="center">Status</TableCell>
                      <TableCell align="right">Score</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {qualityMetrics?.map((metric, index) => (
                      <TableRow key={index}>
                        <TableCell component="th" scope="row">
                          <Typography fontWeight={600}>{metric.category}</Typography>
                        </TableCell>
                        <TableCell align="right">
                          {typeof metric.value === 'number' ? metric.value.toFixed(2) : metric.value} {metric.unit}
                        </TableCell>
                        <TableCell align="right">{metric.target}</TableCell>
                        <TableCell align="center">
                          {metric.status ? (
                            <CheckCircleIcon sx={{ color: 'success.main' }} />
                          ) : (
                            <WarningIcon sx={{ color: 'warning.main' }} />
                          )}
                        </TableCell>
                        <TableCell align="right">
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                            <Typography sx={{ marginRight: 1 }}>{metric.score}%</Typography>
                            <LinearProgress
                              variant="determinate"
                              value={metric.score}
                              sx={{ width: 50, height: 6, borderRadius: 3 }}
                            />
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ padding: 2, height: 'fit-content' }}>
                {qualitySpiderChart && (
                  <Plot
                    data={qualitySpiderChart.data as Data[]}
                    layout={qualitySpiderChart.layout}
                    config={qualitySpiderChart.config as Partial<Config>}
                    style={{ width: '100%', height: '350px' }}
                  />
                )}
              </Paper>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Recommendations */}
      <Accordion
        expanded={expandedSections.includes('recommendations')}
        onChange={() => handleSectionToggle('recommendations')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <RecommendIcon sx={{ marginRight: 1, color: 'primary.main' }} />
            <Typography variant="h6">Recommendations</Typography>
            <Chip 
              label={`${quality_assessment.recommendations.length} items`}
              size="small"
              sx={{ marginLeft: 2 }}
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {quality_assessment.recommendations.length > 0 ? (
            <List>
              {quality_assessment.recommendations.map((recommendation, index) => (
                <ListItem key={index} sx={{ paddingLeft: 0 }}>
                  <ListItemIcon>
                    <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: '0.875rem' }}>
                      {index + 1}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={recommendation}
                    primaryTypographyProps={{ fontWeight: 500 }}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Alert severity="success">
              <AlertTitle>Excellent Quality</AlertTitle>
              No specific recommendations needed. The current process parameters produce high-quality results.
            </Alert>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Detailed Analysis */}
      <Accordion
        expanded={expandedSections.includes('analysis')}
        onChange={() => handleSectionToggle('analysis')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <ScienceIcon sx={{ marginRight: 1, color: 'primary.main' }} />
            <Typography variant="h6">Detailed Analysis</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardHeader title="Hardness Analysis" />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Surface Hardness</Typography>
                      <Typography variant="h6">
                        {results.process_metrics.surface_hardness_hrc.toFixed(1)} HRC
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        ({results.process_metrics.surface_hardness_hv.toFixed(0)} HV)
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Core Hardness</Typography>
                      <Typography variant="h6">
                        {results.process_metrics.core_hardness_hrc.toFixed(1)} HRC
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        ({results.process_metrics.core_hardness_hv.toFixed(0)} HV)
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Divider sx={{ marginY: 1 }} />
                      <Typography variant="body2" color="textSecondary">Hardness Gradient</Typography>
                      <Typography variant="h6">
                        {results.process_metrics.hardness_gradient.toFixed(1)} HRC/mm
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardHeader title="Case Depth Analysis" />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Effective Case Depth</Typography>
                      <Typography variant="h6">
                        {results.case_depth_results.effective_case_depth.toFixed(2)} mm
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Total Case Depth</Typography>
                      <Typography variant="h6">
                        {results.case_depth_results.total_case_depth.toFixed(2)} mm
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">0.4% Carbon Depth</Typography>
                      <Typography variant="body1">
                        {results.case_depth_results.case_depth_04_carbon.toFixed(2)} mm
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">50 HRC Depth</Typography>
                      <Typography variant="body1">
                        {results.case_depth_results.case_depth_50_hrc.toFixed(2)} mm
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardHeader title="Microstructure Analysis" />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Surface Grain Size</Typography>
                      <Typography variant="h6">
                        {results.process_metrics.grain_size_surface.toFixed(1)} μm
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Core Grain Size</Typography>
                      <Typography variant="h6">
                        {results.process_metrics.grain_size_core.toFixed(1)} μm
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Divider sx={{ marginY: 1 }} />
                      <Typography variant="body2" color="textSecondary">Surface Carbon Content</Typography>
                      <Typography variant="h6">
                        {results.process_metrics.surface_carbon.toFixed(2)} wt%
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={2}>
                <CardHeader title="Process Assessment" />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="textSecondary">Distortion Risk</Typography>
                      <Chip 
                        label={results.process_metrics.distortion_risk}
                        color={results.process_metrics.distortion_risk === 'Low' ? 'success' : 
                               results.process_metrics.distortion_risk === 'Medium' ? 'warning' : 'error'}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Computation Time</Typography>
                      <Typography variant="body1">
                        {results.computation_time.toFixed(2)} seconds
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Validation Status</Typography>
                      <Typography variant="body1">
                        {results.validation_status}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Final Summary */}
      <Paper elevation={2} sx={{ padding: 3, marginTop: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quality Report Summary
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="body1" paragraph>
              <strong>Overall Assessment:</strong> This heat treatment process has achieved a Grade {quality_assessment.overall_grade} quality rating 
              with a {overallScore.toFixed(1)}% quality score. 
              {quality_assessment.gear_requirements_met 
                ? ' The part meets all standard gear application requirements.'
                : ' Some requirements may need attention for optimal gear performance.'
              }
            </Typography>
            {quality_assessment.recommendations.length > 0 && (
              <Typography variant="body1">
                <strong>Key Recommendations:</strong> Focus on {quality_assessment.recommendations.length} improvement areas 
                to enhance overall quality and performance.
              </Typography>
            )}
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'center' }}>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Report Generated
            </Typography>
            <Typography variant="body1">
              {new Date().toLocaleDateString()}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              ID: {results.calculation_id}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default QualityReport;