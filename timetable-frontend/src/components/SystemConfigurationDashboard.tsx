import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  Divider,
  Chip,
  Paper
} from '@mui/material';
import { Save, Settings, Schedule, School } from '@mui/icons-material';
import apiService from '../services/apiService';

interface SystemConfig {
  id?: number;
  break_start_time: string;
  break_end_time: string;
  max_sessions_per_teacher_per_week: number;
  min_sessions_per_teacher_per_week: number;
  default_lab_duration_hours: number;
  allow_cross_year_lab_conflicts: boolean;
  remedial_lectures_per_week: number;
  remedial_preferred_time: string;
  project_time_slots_per_week: number;
  morning_afternoon_balance_percentage: number;
}

const SystemConfigurationDashboard: React.FC = () => {
  const [config, setConfig] = useState<SystemConfig>({
    break_start_time: '13:00',
    break_end_time: '13:45',
    max_sessions_per_teacher_per_week: 14,
    min_sessions_per_teacher_per_week: 10,
    default_lab_duration_hours: 2,
    allow_cross_year_lab_conflicts: false,
    remedial_lectures_per_week: 1,
    remedial_preferred_time: 'afternoon',
    project_time_slots_per_week: 2,
    morning_afternoon_balance_percentage: 50
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      const data = await apiService.getSystemConfiguration();
      if (data) {
        setConfig(data);
      }
    } catch (err) {
      console.log('Using default configuration');
    }
  };

  const handleConfigChange = (field: keyof SystemConfig, value: any) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await apiService.saveSystemConfiguration(config);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save configuration. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Settings />
        System Configuration Dashboard
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Configure global timetable generation parameters and constraints
      </Typography>

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Configuration saved successfully!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        
        {/* Break Time Configuration */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Schedule />
                Break Time Settings
              </Typography>
              
              <Grid container spacing={2}>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="time"
                    label="Break Start Time"
                    value={config.break_start_time}
                    onChange={(e) => handleConfigChange('break_start_time', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="time"
                    label="Break End Time"
                    value={config.break_end_time}
                    onChange={(e) => handleConfigChange('break_end_time', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              </Grid>
              
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Currently: {config.break_start_time} - {config.break_end_time}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Teacher Workload Settings */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <School />
                Teacher Workload
              </Typography>
              
              <Grid container spacing={2}>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Sessions/Week"
                    value={config.max_sessions_per_teacher_per_week}
                    onChange={(e) => handleConfigChange('max_sessions_per_teacher_per_week', parseInt(e.target.value))}
                    inputProps={{ min: 1, max: 30 }}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Min Sessions/Week"
                    value={config.min_sessions_per_teacher_per_week}
                    onChange={(e) => handleConfigChange('min_sessions_per_teacher_per_week', parseInt(e.target.value))}
                    inputProps={{ min: 1, max: 25 }}
                  />
                </Grid>
              </Grid>
              
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Range: {config.min_sessions_per_teacher_per_week} - {config.max_sessions_per_teacher_per_week} sessions per week
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Lab Configuration */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Lab Settings
              </Typography>
              
              <Grid container spacing={2}>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Default Lab Duration (Hours)"
                    value={config.default_lab_duration_hours}
                    onChange={(e) => handleConfigChange('default_lab_duration_hours', parseInt(e.target.value))}
                    inputProps={{ min: 1, max: 4 }}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.allow_cross_year_lab_conflicts}
                        onChange={(e) => handleConfigChange('allow_cross_year_lab_conflicts', e.target.checked)}
                      />
                    }
                    label="Allow Cross-Year Lab Conflicts"
                  />
                  <Typography variant="body2" color="text.secondary">
                    {config.allow_cross_year_lab_conflicts ? 'Enabled' : 'Disabled'} - Cross-year lab scheduling
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Remedial Lecture Settings */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Remedial Lectures
              </Typography>
              
              <Grid container spacing={2}>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Remedial Lectures/Week"
                    value={config.remedial_lectures_per_week}
                    onChange={(e) => handleConfigChange('remedial_lectures_per_week', parseInt(e.target.value))}
                    inputProps={{ min: 0, max: 5 }}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FormControl fullWidth>
                    <InputLabel>Preferred Time</InputLabel>
                    <Select
                      value={config.remedial_preferred_time}
                      onChange={(e) => handleConfigChange('remedial_preferred_time', e.target.value)}
                      label="Preferred Time"
                    >
                      <MenuItem value="morning">Morning</MenuItem>
                      <MenuItem value="afternoon">Afternoon</MenuItem>
                      <MenuItem value="either">Either</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Project Time & Balance Settings */}
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Advanced Settings
              </Typography>
              
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Project Time Slots/Week"
                    value={config.project_time_slots_per_week}
                    onChange={(e) => handleConfigChange('project_time_slots_per_week', parseInt(e.target.value))}
                    inputProps={{ min: 0, max: 10 }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Dedicated project work sessions
                  </Typography>
                </Grid>
                
                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Morning/Afternoon Balance %"
                    value={config.morning_afternoon_balance_percentage}
                    onChange={(e) => handleConfigChange('morning_afternoon_balance_percentage', parseInt(e.target.value))}
                    inputProps={{ min: 20, max: 80 }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Target morning session percentage
                  </Typography>
                </Grid>
                
                <Grid size={{ xs: 12, md: 4 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Current Balance
                    </Typography>
                    <Typography variant="h6">
                      {config.morning_afternoon_balance_percentage}% / {100 - config.morning_afternoon_balance_percentage}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Morning / Afternoon
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Save Button */}
        <Grid size={{ xs: 12 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<Save />}
              onClick={handleSave}
              disabled={loading}
              sx={{ minWidth: 200 }}
            >
              {loading ? 'Saving...' : 'Save Configuration'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemConfigurationDashboard;
