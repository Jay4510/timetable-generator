/**
 * Timetable Generator Component
 * Professional UI for running algorithm with dry run, progress tracking, and results
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  LinearProgress,
  Chip,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Slider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  CircularProgress
} from '@mui/material';
import {
  PlayArrow,
  CheckCircle,
  Warning,
  Error,
  Settings,
  Assessment,
  Timer,
  Speed,
  TrendingUp,
  Visibility,
  Save
} from '@mui/icons-material';

import type { GenerationRequest, GenerationResult, DashboardStats } from '../types/api';
import timetableApi from '../services/timetableApi';

interface TimetableGeneratorProps {
  onNavigate: (view: string) => void;
}

const TimetableGenerator: React.FC<TimetableGeneratorProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Generation states
  const [generationId, setGenerationId] = useState<string | null>(null);
  const [generationResult, setGenerationResult] = useState<GenerationResult | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Configuration states
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [dryRun, setDryRun] = useState(true);
  const [selectedDivisions, setSelectedDivisions] = useState<string[]>([]);
  const [availableDivisions, setAvailableDivisions] = useState<any[]>([]);
  const [config, setConfig] = useState<GenerationRequest>({
    dry_run: false,
    use_division_specific: true,
    algorithm_type: 'comprehensive',
    population_size: 10,    // Optimized from memories for Division-Specific Algorithm
    generations: 15,        // Optimized from memories for Division-Specific Algorithm
    mutation_rate: 0.2,
    division_ids: []
  });

  // Preflight check states
  const [preflightOpen, setPreflightOpen] = useState(false);
  const [preflightChecks, setPreflightChecks] = useState<any[]>([]);

  const steps = [
    'Validation',
    'Initialization', 
    'Generation',
    'Optimization',
    'Results'
  ];

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isGenerating && generationId) {
      interval = setInterval(checkProgress, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isGenerating, generationId]);

  const loadStats = async () => {
    try {
      const dashboardStats = await timetableApi.getDashboardStats();
      setStats(dashboardStats);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const runPreflightChecks = async () => {
    setLoading(true);
    try {
      const [dataValidation, configValidation] = await Promise.all([
        timetableApi.validateData(),
        timetableApi.validateConfiguration()
      ]);

      const checks = [
        {
          name: 'Data Completeness',
          status: stats?.system_health.data_completeness || 0 >= 80 ? 'pass' : 'fail',
          message: `${stats?.system_health.data_completeness || 0}% complete`,
          critical: true
        },
        {
          name: 'Teachers Available',
          status: (stats?.teachers_count || 0) > 0 ? 'pass' : 'fail',
          message: `${stats?.teachers_count || 0} teachers configured`,
          critical: true
        },
        {
          name: 'Subjects Defined',
          status: (stats?.subjects_count || 0) > 0 ? 'pass' : 'fail',
          message: `${stats?.subjects_count || 0} subjects configured`,
          critical: true
        },
        {
          name: 'Rooms & Labs',
          status: ((stats?.rooms_count || 0) + (stats?.labs_count || 0)) > 0 ? 'pass' : 'fail',
          message: `${(stats?.rooms_count || 0) + (stats?.labs_count || 0)} locations available`,
          critical: true
        },
        {
          name: 'Time Slots',
          status: (stats?.timeslots_count || 0) > 0 ? 'pass' : 'fail',
          message: `${stats?.timeslots_count || 0} time slots configured`,
          critical: true
        },
        {
          name: 'System Configuration',
          status: stats?.system_health.configuration_status === 'complete' ? 'pass' : 'warning',
          message: stats?.system_health.configuration_status === 'complete' ? 'Complete' : 'Partial configuration',
          critical: false
        },
        {
          name: 'Data Validation',
          status: dataValidation.isValid ? 'pass' : 'fail',
          message: dataValidation.isValid ? 'All data valid' : `${dataValidation.errors.length} errors found`,
          critical: true
        }
      ];

      setPreflightChecks(checks);
      setPreflightOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Preflight checks failed');
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    return preflightChecks.filter(check => check.critical && check.status === 'fail').length === 0;
  };

  const startGeneration = async () => {
    if (!canProceed()) {
      setError('Please resolve critical issues before proceeding');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setSuccess(null);
    setCurrentStep(0);
    setProgress(0);
    setPreflightOpen(false);

    try {
      const result = await timetableApi.generateTimetable(config);
      setGenerationId(result.id);
      
      if (config.dry_run) {
        // For dry run, we get immediate results
        setGenerationResult(result);
        setCurrentStep(4);
        setProgress(100);
        setIsGenerating(false);
        setSuccess('Dry run completed successfully');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
      setIsGenerating(false);
    }
  };

  const checkProgress = async () => {
    if (!generationId) return;

    try {
      const result = await timetableApi.getGenerationStatus(generationId);
      
      if (result.status === 'completed') {
        setGenerationResult(result);
        setCurrentStep(4);
        setProgress(100);
        setIsGenerating(false);
        setSuccess(`Generation completed! Created ${result.sessions_created} sessions`);
      } else if (result.status === 'failed') {
        setError('Generation failed');
        setIsGenerating(false);
      } else {
        // Update progress based on step
        const stepProgress = Math.min(currentStep * 20 + 20, 80);
        setProgress(stepProgress);
        if (stepProgress >= 20 && currentStep < 3) {
          setCurrentStep(prev => prev + 1);
        }
      }
    } catch (err) {
      console.error('Failed to check progress:', err);
    }
  };

  const renderConfigurationPanel = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Generation Configuration</Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={dryRun}
                  onChange={(e) => {
                    setDryRun(e.target.checked);
                    setConfig({...config, dry_run: e.target.checked});
                  }}
                />
              }
              label="Dry Run (Preview Only)"
            />
            <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
              Test the algorithm without creating actual sessions
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.use_division_specific || false}
                  onChange={(e) => setConfig({...config, use_division_specific: e.target.checked})}
                />
              }
              label="Division-Specific Generation"
            />
            <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
              Generate separate timetables for each division
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Button
              variant="outlined"
              onClick={() => setShowAdvanced(!showAdvanced)}
              startIcon={<Settings />}
              size="small"
            >
              {showAdvanced ? 'Hide' : 'Show'} Advanced Algorithm Parameters
            </Button>
            <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
              Only modify if you understand genetic algorithm parameters
            </Typography>
          </Grid>

          {showAdvanced && (
            <>
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    <strong>Advanced Parameters:</strong> These control the genetic algorithm's behavior. 
                    Default values are optimized for most college timetables. Only modify if you have specific requirements.
                  </Typography>
                </Alert>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Typography gutterBottom>Population Size: {config.population_size || 10}</Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                  Number of candidate solutions (5-25 optimized)
                </Typography>
                <Slider
                  value={config.population_size || 10}
                  onChange={(_, value) => setConfig({...config, population_size: value as number})}
                  min={5}
                  max={25}
                  step={5}
                  marks
                  valueLabelDisplay="auto"
                />
                <Typography variant="body2" color="text.secondary">
                  Larger populations find better solutions but take longer
                </Typography>
              </Grid>

              <Grid item xs={12} md={4}>
                <Typography gutterBottom>Generations: {config.generations || 15}</Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                  Evolution cycles (10-50 optimized)
                </Typography>
                <Slider
                  value={config.generations || 15}
                  onChange={(_, value) => setConfig({...config, generations: value as number})}
                  min={10}
                  max={50}
                  step={5}
                  marks={[
                    { value: 10, label: '10' },
                    { value: 15, label: '15' },
                    { value: 25, label: '25' },
                    { value: 50, label: '50' }
                  ]}
                  valueLabelDisplay="auto"
                />
                <Typography variant="body2" color="text.secondary">
                  More generations improve quality but increase time
                </Typography>
              </Grid>

              <Grid item xs={12} md={4}>
                <Typography gutterBottom>Mutation Rate: {config.mutation_rate || 0.2}</Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                  Solution variation rate (0.1-0.3 recommended)
                </Typography>
                <Slider
                  value={config.mutation_rate || 0.2}
                  onChange={(_, value) => setConfig({...config, mutation_rate: value as number})}
                  min={0.1}
                  max={0.3}
                  step={0.05}
                  marks={[
                    { value: 0.1, label: '0.1' },
                    { value: 0.2, label: '0.2' },
                    { value: 0.3, label: '0.3' }
                  ]}
                  valueLabelDisplay="auto"
                />
                <Typography variant="body2" color="text.secondary">
                  Higher mutation explores more solutions
                </Typography>
              </Grid>
            </>
          )}
        </Grid>
      </CardContent>
    </Card>
  );

  const renderPreflightDialog = () => (
    <Dialog open={preflightOpen} onClose={() => setPreflightOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>Pre-Generation Checklist</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Please review the system status before proceeding with generation.
        </Typography>

        <List>
          {preflightChecks.map((check, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                {check.status === 'pass' && <CheckCircle color="success" />}
                {check.status === 'warning' && <Warning color="warning" />}
                {check.status === 'fail' && <Error color="error" />}
              </ListItemIcon>
              <ListItemText
                primary={check.name}
                secondary={check.message}
              />
              {check.critical && check.status === 'fail' && (
                <Chip label="Critical" color="error" size="small" />
              )}
            </ListItem>
          ))}
        </List>

        {!canProceed() && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Please resolve critical issues before proceeding. Check the Data Setup section.
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setPreflightOpen(false)}>Cancel</Button>
        <Button onClick={() => onNavigate('data-setup')} variant="outlined">
          Fix Issues
        </Button>
        <Button 
          onClick={startGeneration} 
          variant="contained" 
          disabled={!canProceed()}
          startIcon={dryRun ? <Visibility /> : <PlayArrow />}
        >
          {dryRun ? 'Run Dry Run' : 'Generate Timetable'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderProgressPanel = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Typography variant="h6">Generation Progress</Typography>
          {isGenerating && <CircularProgress size={20} />}
        </Box>

        <Stepper activeStep={currentStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ height: 8, borderRadius: 4, mb: 2 }}
        />

        <Typography variant="body2" color="text.secondary" align="center">
          {progress}% Complete
        </Typography>
      </CardContent>
    </Card>
  );

  const renderResultsPanel = () => {
    if (!generationResult) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Generation Results</Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <TrendingUp color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h4" color="primary">
                  {generationResult.fitness_score.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Fitness Score
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Warning color={generationResult.total_violations === 0 ? 'success' : 'warning'} sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h4" color={generationResult.total_violations === 0 ? 'success.main' : 'warning.main'}>
                  {generationResult.total_violations}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Violations
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Assessment color="info" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h4" color="info.main">
                  {generationResult.sessions_created}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Sessions Created
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Timer color="secondary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h4" color="secondary.main">
                  {generationResult.execution_time_seconds}s
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Execution Time
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="subtitle1" gutterBottom>Algorithm Details</Typography>
          <Typography variant="body2" color="text.secondary">
            Algorithm Used: {generationResult.algorithm_used}
          </Typography>
          
          {generationResult.total_violations > 0 && (
            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Assessment />}
                onClick={() => onNavigate('violations')}
              >
                Review Violations
              </Button>
            </Box>
          )}

          {!config.dry_run && generationResult.sessions_created > 0 && (
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={() => onNavigate('publish')}
              >
                Publish Timetable
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
        🚀 Create Your Timetable
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Let's create your college timetable! Just click "Generate Timetable" and we'll do all the hard work for you. You can also test it first with "Preview Mode".
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {renderConfigurationPanel()}

      {isGenerating && renderProgressPanel()}

      {generationResult && renderResultsPanel()}

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="outlined"
          onClick={runPreflightChecks}
          disabled={loading || isGenerating}
          startIcon={<CheckCircle />}
        >
          Run Preflight Checks
        </Button>

        <Button
          variant="contained"
          onClick={runPreflightChecks}
          disabled={loading || isGenerating}
          startIcon={dryRun ? <Visibility /> : <PlayArrow />}
          size="large"
        >
          {loading ? 'Checking...' : dryRun ? 'Preview Generation' : 'Generate Timetable'}
        </Button>
      </Box>

      {renderPreflightDialog()}
    </Box>
  );
};

export default TimetableGenerator;
