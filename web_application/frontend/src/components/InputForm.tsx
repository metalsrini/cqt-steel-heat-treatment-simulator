import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControlLabel,
  Switch,
  Chip,
  Alert,
  Divider,
  InputAdornment,
  Tooltip,
  IconButton,
  Card,
  CardContent,
  Stack
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Science as ScienceIcon,
  Whatshot as WhatshotIcon,
  Water as WaterIcon,
  LocalFireDepartment as LocalFireDepartmentIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  AutoFixHigh as AutoFixHighIcon,
  RestartAlt as RestartAltIcon
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  SimulationRequest,
  SteelGradesResponse,
  QuenchMediaResponse
} from '../types/simulation';
import { createDefaultSimulationRequest } from '../services/api';

interface InputFormProps {
  onSubmit: (data: SimulationRequest) => void;
  steelGrades: SteelGradesResponse;
  quenchMedia: QuenchMediaResponse;
  loading: boolean;
}

const validationSchema = Yup.object({
  steel_composition: Yup.object({
    grade: Yup.string(),
    C: Yup.number().min(0.01).max(2.0).required('Carbon content is required'),
    Si: Yup.number().min(0.0).max(2.0).required(),
    Mn: Yup.number().min(0.0).max(3.0).required(),
    Ni: Yup.number().min(0.0).max(5.0).required(),
    Cr: Yup.number().min(0.0).max(3.0).required(),
    Mo: Yup.number().min(0.0).max(1.0).required(),
    V: Yup.number().min(0.0).max(0.5).required(),
    W: Yup.number().min(0.0).max(1.0).required(),
    Cu: Yup.number().min(0.0).max(1.0).required(),
    P: Yup.number().min(0.0).max(0.1).required(),
    Al: Yup.number().min(0.0).max(0.1).required(),
    As: Yup.number().min(0.0).max(0.1).required(),
    Ti: Yup.number().min(0.0).max(0.1).required()
  }),
  carburizing: Yup.object({
    temperature: Yup.number().min(850).max(1050).required('Temperature is required'),
    time_hours: Yup.number().min(0.5).max(24).required('Time is required'),
    carbon_potential: Yup.number().min(0.6).max(1.5).required('Carbon potential is required'),
    heating_rate: Yup.number().min(1.0).max(20.0).required(),
    gas_flow_rate: Yup.number().min(0.1).max(5.0).required(),
    mass_transfer_coefficient: Yup.number().min(1e-5).max(5e-4).required()
  }),
  quenching: Yup.object({
    quench_medium: Yup.string().required('Quench medium is required'),
    quench_temperature: Yup.number().min(20).max(150).required(),
    agitation_rate: Yup.number().min(0.0).max(3.0).required(),
    quench_time: Yup.number().min(60).max(1800).required(),
    delay_time: Yup.number().min(0).max(600).required()
  }),
  tempering: Yup.object({
    temperature: Yup.number().min(100).max(700).required('Temperature is required'),
    time_hours: Yup.number().min(0.5).max(8.0).required('Time is required'),
    heating_rate: Yup.number().min(0.5).max(10.0).required(),
    temper_cycles: Yup.number().min(1).max(3).required()
  }),
  geometry: Yup.object({
    geometry_type: Yup.string().required('Geometry type is required'),
    characteristic_dimension: Yup.number().min(1).max(100).required('Characteristic dimension is required')
  }),
  initial_conditions: Yup.object({
    initial_grain_size: Yup.number().min(5.0).max(200.0).required()
  }),
  simulation_params: Yup.object({
    spatial_points: Yup.number().min(21).max(201).required(),
    max_analysis_depth: Yup.number().min(1.0).max(20.0).required()
  })
});

const InputForm: React.FC<InputFormProps> = ({
  onSubmit,
  steelGrades,
  quenchMedia,
  loading
}) => {
  const [expandedSections, setExpandedSections] = useState<string[]>([
    'steel_composition',
    'carburizing'
  ]);
  const [useCustomComposition, setUseCustomComposition] = useState(false);

  const formik = useFormik<SimulationRequest>({
    initialValues: createDefaultSimulationRequest(),
    validationSchema,
    onSubmit: (values) => {
      onSubmit(values);
    }
  });

  const handleSectionToggle = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const handleSteelGradeChange = (grade: string) => {
    if (grade && steelGrades?.grades && steelGrades.grades[grade]) {
      const composition = steelGrades.grades[grade].composition;
      formik.setFieldValue('steel_composition', {
        ...composition,
        grade
      });
      setUseCustomComposition(false);
    }
  };

  const handleQuenchMediumChange = (medium: string) => {
    if (medium && quenchMedia?.media && quenchMedia.media[medium]) {
      const mediaData = quenchMedia.media[medium];
      formik.setFieldValue('quenching.quench_medium', medium);
      formik.setFieldValue('quenching.quench_temperature', mediaData.typical_temperature);
      if (mediaData.heat_transfer_coefficient_range) {
        const avgHTC = (mediaData.heat_transfer_coefficient_range[0] + mediaData.heat_transfer_coefficient_range[1]) / 2;
        formik.setFieldValue('quenching.heat_transfer_coefficient', avgHTC);
      }
    }
  };

  const handleResetForm = () => {
    formik.resetForm();
    setUseCustomComposition(false);
  };

  const renderTextField = (
    name: string,
    label: string,
    unit?: string,
    tooltip?: string,
    type: string = 'number'
  ) => (
    <TextField
      fullWidth
      name={name}
      label={label}
      type={type}
      value={formik.getFieldProps(name).value}
      onChange={formik.handleChange}
      onBlur={formik.handleBlur}
      error={Boolean(formik.getFieldMeta(name).touched && formik.getFieldMeta(name).error)}
      helperText={formik.getFieldMeta(name).touched && formik.getFieldMeta(name).error}
      InputProps={{
        endAdornment: unit ? <InputAdornment position="end">{unit}</InputAdornment> : undefined,
        inputProps: type === 'number' ? { step: 'any' } : undefined
      }}
      InputLabelProps={{
        shrink: true
      }}
      size="small"
    />
  );

  return (
    <Box sx={{ maxWidth: 1200, margin: '0 auto' }}>
      <Paper elevation={2} sx={{ padding: 3, marginBottom: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 3 }}>
          <ScienceIcon sx={{ marginRight: 2, color: 'primary.main', fontSize: 32 }} />
          <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Simulation Parameters
          </Typography>
          <Stack direction="row" spacing={1}>
            <Tooltip title="Reset to defaults">
              <IconButton onClick={handleResetForm} color="secondary">
                <RestartAltIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Auto-optimize parameters">
              <IconButton color="primary">
                <AutoFixHighIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </Box>

        <form onSubmit={formik.handleSubmit}>
          {/* Steel Composition Section */}
          <Accordion
            expanded={expandedSections.includes('steel_composition')}
            onChange={() => handleSectionToggle('steel_composition')}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ScienceIcon sx={{ marginRight: 1, color: 'primary.main' }} />
                <Typography variant="h6">Steel Composition</Typography>
                {formik.values.steel_composition.grade && (
                  <Chip
                    label={formik.values.steel_composition.grade}
                    size="small"
                    color="primary"
                    sx={{ marginLeft: 2 }}
                  />
                )}
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useCustomComposition}
                        onChange={(e) => {
                          const isCustom = e.target.checked;
                          setUseCustomComposition(isCustom);
                          if (isCustom) {
                            // Clear the grade field when using custom composition
                            formik.setFieldValue('steel_composition.grade', '');
                          }
                        }}
                      />
                    }
                    label="Use custom composition"
                  />
                </Grid>

                {!useCustomComposition && (
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Steel Grade</InputLabel>
                      <Select
                        value={formik.values.steel_composition.grade || ''}
                        onChange={(e) => handleSteelGradeChange(e.target.value)}
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
                )}

                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Chemical Composition (wt%)
                  </Typography>
                  <Grid container spacing={2}>
                    {[
                      { name: 'C', label: 'Carbon', max: 2.0 },
                      { name: 'Si', label: 'Silicon', max: 2.0 },
                      { name: 'Mn', label: 'Manganese', max: 3.0 },
                      { name: 'Ni', label: 'Nickel', max: 5.0 },
                      { name: 'Cr', label: 'Chromium', max: 3.0 },
                      { name: 'Mo', label: 'Molybdenum', max: 1.0 },
                      { name: 'V', label: 'Vanadium', max: 0.5 },
                      { name: 'W', label: 'Tungsten', max: 1.0 },
                      { name: 'Cu', label: 'Copper', max: 1.0 },
                      { name: 'P', label: 'Phosphorus', max: 0.1 },
                      { name: 'Al', label: 'Aluminum', max: 0.1 },
                      { name: 'As', label: 'Arsenic', max: 0.1 },
                      { name: 'Ti', label: 'Titanium', max: 0.1 }
                    ].map((element) => (
                      <Grid item xs={6} sm={4} md={3} key={element.name}>
                        {renderTextField(
                          `steel_composition.${element.name}`,
                          element.label,
                          'wt%',
                          `${element.label} content (0 - ${element.max} wt%)`
                        )}
                      </Grid>
                    ))}
                  </Grid>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Carburizing Section */}
          <Accordion
            expanded={expandedSections.includes('carburizing')}
            onChange={() => handleSectionToggle('carburizing')}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <WhatshotIcon sx={{ marginRight: 1, color: 'primary.main' }} />
                <Typography variant="h6">Carburizing Process</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'carburizing.temperature',
                    'Temperature',
                    '°C',
                    'Carburizing temperature (850-1050°C)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'carburizing.time_hours',
                    'Time',
                    'hours',
                    'Carburizing time (0.5-24 hours)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'carburizing.carbon_potential',
                    'Carbon Potential',
                    'wt%',
                    'Target carbon potential (0.6-1.5 wt%)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'carburizing.heating_rate',
                    'Heating Rate',
                    '°C/min',
                    'Heating rate to carburizing temperature'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Atmosphere Type</InputLabel>
                    <Select
                      name="carburizing.atmosphere_type"
                      value={formik.values.carburizing.atmosphere_type}
                      onChange={formik.handleChange}
                      label="Atmosphere Type"
                    >
                      <MenuItem value="endothermic">Endothermic</MenuItem>
                      <MenuItem value="nitrogen-methanol">Nitrogen-Methanol</MenuItem>
                      <MenuItem value="propane">Propane</MenuItem>
                      <MenuItem value="acetylene">Acetylene</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'carburizing.gas_flow_rate',
                    'Gas Flow Rate',
                    'relative',
                    'Relative gas flow rate (0.1-5.0)'
                  )}
                </Grid>
                <Grid item xs={12} md={6}>
                  {renderTextField(
                    'carburizing.mass_transfer_coefficient',
                    'Mass Transfer Coefficient',
                    'cm/s',
                    'Surface mass transfer coefficient'
                  )}
                </Grid>
                <Grid item xs={12} md={3}>
                  {renderTextField(
                    'carburizing.diffusion_temperature',
                    'Diffusion Temperature',
                    '°C',
                    'Optional diffusion stage temperature'
                  )}
                </Grid>
                <Grid item xs={12} md={3}>
                  {renderTextField(
                    'carburizing.diffusion_time',
                    'Diffusion Time',
                    'hours',
                    'Optional diffusion stage time'
                  )}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Quenching Section */}
          <Accordion
            expanded={expandedSections.includes('quenching')}
            onChange={() => handleSectionToggle('quenching')}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <WaterIcon sx={{ marginRight: 1, color: 'primary.main' }} />
                <Typography variant="h6">Quenching Process</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Quench Medium</InputLabel>
                    <Select
                      name="quenching.quench_medium"
                      value={formik.values.quenching.quench_medium}
                      onChange={(e) => handleQuenchMediumChange(e.target.value)}
                      label="Quench Medium"
                    >
                      {quenchMedia?.media && Object.keys(quenchMedia.media).map((medium) => (
                        <MenuItem key={medium} value={medium}>
                          {medium} - {quenchMedia.media[medium].description}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'quenching.quench_temperature',
                    'Temperature',
                    '°C',
                    'Quench medium temperature'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'quenching.heat_transfer_coefficient',
                    'Heat Transfer Coefficient',
                    'W/m²K',
                    'Surface heat transfer coefficient'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'quenching.agitation_rate',
                    'Agitation Rate',
                    'relative',
                    'Relative agitation rate (0.0-3.0)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'quenching.quench_time',
                    'Quench Time',
                    'seconds',
                    'Total quenching time'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'quenching.delay_time',
                    'Delay Time',
                    'seconds',
                    'Delay before quenching starts'
                  )}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Tempering Section */}
          <Accordion
            expanded={expandedSections.includes('tempering')}
            onChange={() => handleSectionToggle('tempering')}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <LocalFireDepartmentIcon sx={{ marginRight: 1, color: 'primary.main' }} />
                <Typography variant="h6">Tempering Process</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'tempering.temperature',
                    'Temperature',
                    '°C',
                    'Tempering temperature (100-700°C)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'tempering.time_hours',
                    'Time',
                    'hours',
                    'Tempering time (0.5-8 hours)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'tempering.heating_rate',
                    'Heating Rate',
                    '°C/min',
                    'Heating rate to tempering temperature'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Cooling Method</InputLabel>
                    <Select
                      name="tempering.cooling_method"
                      value={formik.values.tempering.cooling_method}
                      onChange={formik.handleChange}
                      label="Cooling Method"
                    >
                      <MenuItem value="air">Air Cooling</MenuItem>
                      <MenuItem value="furnace">Furnace Cooling</MenuItem>
                      <MenuItem value="water">Water Cooling</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        name="tempering.multiple_tempers"
                        checked={formik.values.tempering.multiple_tempers}
                        onChange={formik.handleChange}
                      />
                    }
                    label="Multiple Tempering Cycles"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'tempering.temper_cycles',
                    'Number of Cycles',
                    '',
                    'Number of tempering cycles (1-3)'
                  )}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Part Geometry Section */}
          <Accordion
            expanded={expandedSections.includes('geometry')}
            onChange={() => handleSectionToggle('geometry')}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SettingsIcon sx={{ marginRight: 1, color: 'primary.main' }} />
                <Typography variant="h6">Part Geometry</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Geometry Type</InputLabel>
                    <Select
                      name="geometry.geometry_type"
                      value={formik.values.geometry.geometry_type}
                      onChange={formik.handleChange}
                      label="Geometry Type"
                    >
                      <MenuItem value="cylinder">Cylinder</MenuItem>
                      <MenuItem value="slab">Slab</MenuItem>
                      <MenuItem value="sphere">Sphere</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'geometry.diameter',
                    'Diameter',
                    'mm',
                    'Part diameter (for cylinder/sphere)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'geometry.length',
                    'Length',
                    'mm',
                    'Part length (for cylinder)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'geometry.thickness',
                    'Thickness',
                    'mm',
                    'Part thickness (for slab)'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'geometry.characteristic_dimension',
                    'Characteristic Dimension',
                    'mm',
                    'Characteristic dimension for analysis'
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderTextField(
                    'geometry.surface_area',
                    'Surface Area',
                    'mm²',
                    'Total surface area (optional)'
                  )}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Initial Conditions and Simulation Parameters */}
          <Accordion
            expanded={expandedSections.includes('advanced')}
            onChange={() => handleSectionToggle('advanced')}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SettingsIcon sx={{ marginRight: 1, color: 'primary.main' }} />
                <Typography variant="h6">Advanced Settings</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Initial Conditions
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  {renderTextField(
                    'initial_conditions.initial_grain_size',
                    'Initial Grain Size',
                    'μm',
                    'ASTM grain size (5-200 μm)'
                  )}
                </Grid>
                <Grid item xs={12} md={3}>
                  {renderTextField(
                    'initial_conditions.initial_hardness',
                    'Initial Hardness',
                    'HV',
                    'Initial hardness (optional)'
                  )}
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Surface Condition</InputLabel>
                    <Select
                      name="initial_conditions.surface_condition"
                      value={formik.values.initial_conditions.surface_condition}
                      onChange={formik.handleChange}
                      label="Surface Condition"
                    >
                      <MenuItem value="machined">Machined</MenuItem>
                      <MenuItem value="ground">Ground</MenuItem>
                      <MenuItem value="as-forged">As-Forged</MenuItem>
                      <MenuItem value="polished">Polished</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Prior Heat Treatment</InputLabel>
                    <Select
                      name="initial_conditions.prior_heat_treatment"
                      value={formik.values.initial_conditions.prior_heat_treatment}
                      onChange={formik.handleChange}
                      label="Prior Heat Treatment"
                    >
                      <MenuItem value="annealed">Annealed</MenuItem>
                      <MenuItem value="normalized">Normalized</MenuItem>
                      <MenuItem value="as-rolled">As-Rolled</MenuItem>
                      <MenuItem value="quenched_tempered">Quenched & Tempered</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ marginY: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Simulation Parameters
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  {renderTextField(
                    'simulation_params.spatial_points',
                    'Spatial Points',
                    '',
                    'Number of spatial discretization points'
                  )}
                </Grid>
                <Grid item xs={12} md={3}>
                  {renderTextField(
                    'simulation_params.max_analysis_depth',
                    'Analysis Depth',
                    'mm',
                    'Maximum depth for analysis'
                  )}
                </Grid>
                <Grid item xs={12} md={3}>
                  {renderTextField(
                    'simulation_params.time_step_carburizing',
                    'Carburizing Time Step',
                    'seconds',
                    'Time step for carburizing simulation'
                  )}
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Output Resolution</InputLabel>
                    <Select
                      name="simulation_params.output_resolution"
                      value={formik.values.simulation_params.output_resolution}
                      onChange={formik.handleChange}
                      label="Output Resolution"
                    >
                      <MenuItem value="coarse">Coarse</MenuItem>
                      <MenuItem value="standard">Standard</MenuItem>
                      <MenuItem value="fine">Fine</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Form Validation Summary */}
          {formik.errors && Object.keys(formik.errors).length > 0 && (
            <Alert severity="warning" sx={{ marginTop: 3 }}>
              <Typography variant="body2">
                Please review the form for validation errors before submitting.
              </Typography>
            </Alert>
          )}

          {/* Submit Button */}
          <Box sx={{ marginTop: 4, textAlign: 'center' }}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={loading || !formik.isValid}
              startIcon={<ScienceIcon />}
              sx={{
                minWidth: 200,
                height: 48,
                fontSize: '1.1rem',
                fontWeight: 600
              }}
            >
              {loading ? 'Running Simulation...' : 'Start Simulation'}
            </Button>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};

export default InputForm;