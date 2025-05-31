import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Paper,
  Grid,
  Tab,
  Tabs,
  Alert,
  Snackbar,
  LinearProgress,
  Fab,
  Tooltip,
  useMediaQuery
} from '@mui/material';
import {
  Science as ScienceIcon,
  Calculate as CalculateIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  Compare as CompareIcon,
  Timeline as TimelineIcon,
  Download as DownloadIcon,
  Help as HelpIcon
} from '@mui/icons-material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import custom components
import InputForm from './components/InputForm';
import ResultsDashboard from './components/ResultsDashboard';
import MaterialComparison from './components/MaterialComparison';
import ProcessOptimization from './components/ProcessOptimization';
import ThermalAnalysis from './components/ThermalAnalysis';
import QualityReport from './components/QualityReport';
import LoadingOverlay from './components/LoadingOverlay';
import ErrorBoundary from './components/ErrorBoundary';

// Import types and services
import { SimulationRequest, SimulationResults } from './types/simulation';
import { simulationService } from './services/api';
import { useNotification } from './hooks/useNotification';

// Create professional theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#f57c00',
      light: '#ffb74d',
      dark: '#ef6c00',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    text: {
      primary: '#212121',
      secondary: '#757575',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      color: '#1976d2',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      color: '#1976d2',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '1rem',
        },
      },
    },
  },
});

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
      id={`nav-tabpanel-${index}`}
      aria-labelledby={`nav-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [simulationData, setSimulationData] = useState<SimulationRequest | null>(null);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steelGrades, setSteelGrades] = useState<any>({ grades: {} });
  const [quenchMedia, setQuenchMedia] = useState<any>({ media: {} });
  
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { showNotification, NotificationComponent } = useNotification();

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [gradesResponse, mediaResponse] = await Promise.all([
          simulationService.getSteelGrades(),
          simulationService.getQuenchMedia()
        ]);
        setSteelGrades(gradesResponse.data);
        setQuenchMedia(mediaResponse.data);
      } catch (err) {
        console.error('Failed to load initial data:', err);
        showNotification('Failed to load application data', 'error');
      }
    };

    loadInitialData();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleSimulationSubmit = async (data: SimulationRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      showNotification('Starting simulation...', 'info');
      
      // Validate inputs first
      const validationResponse = await simulationService.validateInputs(data);
      if (!validationResponse.data.valid) {
        throw new Error(validationResponse.data.error || 'Invalid input parameters');
      }

      if (validationResponse.data.warnings.length > 0) {
        validationResponse.data.warnings.forEach((warning: string) => {
          showNotification(warning, 'warning');
        });
      }

      // Run simulation
      const response = await simulationService.runSimulation(data);
      setResults(response.data);
      setSimulationData(data);
      
      showNotification('Simulation completed successfully!', 'success');
      setCurrentTab(1); // Switch to results tab
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Simulation failed';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleMaterialComparison = async (steelGrades: string[], processConditions: any) => {
    setLoading(true);
    try {
      const response = await simulationService.compareMaterials(steelGrades, processConditions);
      showNotification('Material comparison completed', 'success');
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Material comparison failed';
      showNotification(errorMessage, 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleProcessOptimization = async (targetCaseDepth: number, steelGrade: string, constraints: any) => {
    setLoading(true);
    try {
      const response = await simulationService.optimizeProcess(targetCaseDepth, steelGrade, constraints);
      showNotification('Process optimization completed', 'success');
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Process optimization failed';
      showNotification(errorMessage, 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const exportResults = () => {
    if (!results) return;
    
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `cqt_simulation_${results.calculation_id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    showNotification('Results exported successfully', 'success');
  };

  const tabs = [
    { label: 'Input Parameters', icon: <SettingsIcon /> },
    { label: 'Results Dashboard', icon: <AssessmentIcon /> },
    { label: 'Material Comparison', icon: <CompareIcon /> },
    { label: 'Process Optimization', icon: <CalculateIcon /> },
    { label: 'Thermal Analysis', icon: <TimelineIcon /> },
    { label: 'Quality Report', icon: <ScienceIcon /> }
  ];

  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: 'background.default' }}>
            {/* Header */}
            <AppBar position="static" elevation={1}>
              <Toolbar>
                <ScienceIcon sx={{ mr: 2 }} />
                <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                  C-Q-T Steel Heat Treatment Simulator
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Professional ICME Framework v1.0
                </Typography>
              </Toolbar>
            </AppBar>

            {/* Loading indicator */}
            {loading && <LinearProgress />}

            {/* Main content */}
            <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
              {/* Navigation tabs */}
              <Paper sx={{ mb: 3 }}>
                <Tabs
                  value={currentTab}
                  onChange={handleTabChange}
                  indicatorColor="primary"
                  textColor="primary"
                  variant={isMobile ? "scrollable" : "fullWidth"}
                  scrollButtons="auto"
                  sx={{ borderBottom: 1, borderColor: 'divider' }}
                >
                  {tabs.map((tab, index) => (
                    <Tab
                      key={index}
                      icon={tab.icon}
                      label={tab.label}
                      iconPosition="start"
                      disabled={loading}
                    />
                  ))}
                </Tabs>
              </Paper>

              {/* Tab panels */}
              <TabPanel value={currentTab} index={0}>
                <InputForm
                  onSubmit={handleSimulationSubmit}
                  steelGrades={steelGrades}
                  quenchMedia={quenchMedia}
                  loading={loading}
                />
              </TabPanel>

              <TabPanel value={currentTab} index={1}>
                {results ? (
                  <ResultsDashboard
                    results={results}
                    inputData={simulationData}
                  />
                ) : (
                  <Paper sx={{ p: 4, textAlign: 'center' }}>
                    <Typography variant="h6" color="textSecondary">
                      No simulation results available
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                      Please run a simulation first to view results
                    </Typography>
                  </Paper>
                )}
              </TabPanel>

              <TabPanel value={currentTab} index={2}>
                <MaterialComparison
                  steelGrades={steelGrades}
                  onCompare={handleMaterialComparison}
                  loading={loading}
                />
              </TabPanel>

              <TabPanel value={currentTab} index={3}>
                <ProcessOptimization
                  steelGrades={steelGrades}
                  onOptimize={handleProcessOptimization}
                  loading={loading}
                />
              </TabPanel>

              <TabPanel value={currentTab} index={4}>
                <ThermalAnalysis
                  results={results}
                  inputData={simulationData}
                />
              </TabPanel>

              <TabPanel value={currentTab} index={5}>
                <QualityReport
                  results={results}
                  inputData={simulationData}
                />
              </TabPanel>
            </Container>

            {/* Floating action buttons */}
            {results && (
              <Box sx={{ position: 'fixed', bottom: 16, right: 16 }}>
                <Tooltip title="Export Results">
                  <Fab color="primary" onClick={exportResults} sx={{ mr: 1 }}>
                    <DownloadIcon />
                  </Fab>
                </Tooltip>
                <Tooltip title="Help">
                  <Fab color="secondary" onClick={() => window.open('/api/docs', '_blank')}>
                    <HelpIcon />
                  </Fab>
                </Tooltip>
              </Box>
            )}

            {/* Loading overlay */}
            <LoadingOverlay open={loading} />

            {/* Notifications */}
            <NotificationComponent />

            {/* Error display */}
            {error && (
              <Snackbar
                open={Boolean(error)}
                autoHideDuration={6000}
                onClose={() => setError(null)}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
              >
                <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
                  {error}
                </Alert>
              </Snackbar>
            )}
          </Box>
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;