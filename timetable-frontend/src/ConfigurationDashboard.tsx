import React, { useState, useEffect } from 'react';
import apiService from './services/apiService';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Switch,
  FormControlLabel
} from '@mui/material';
import { Settings, Schedule, AccessTime, School, Save } from '@mui/icons-material';

interface TimetableConfig {
  name: string;
  academic_year: string;
  semester: string;
  college_start_time: string;
  college_end_time: string;
  lunch_start_time: string;
  lunch_end_time: string;
  project_half_days_per_week: number;
  project_day_preference: string;
  max_sessions_per_teacher: number;
  min_sessions_per_teacher: number;
}

const ConfigurationDashboard: React.FC = () => {
  const [config, setConfig] = useState<TimetableConfig>({
    name: 'Default Configuration',
    academic_year: '2024-25',
    semester: 'Odd',
    college_start_time: '09:00:00',
    college_end_time: '17:45:00',
    lunch_start_time: '13:00:00',
    lunch_end_time: '13:45:00',
    project_half_days_per_week: 1,
    project_day_preference: 'friday_afternoon',
    max_sessions_per_teacher: 14,
    min_sessions_per_teacher: 8
  });

  const [loading, setLoading] = useState(false);
  const [saveDialog, setSaveDialog] = useState(false);
  const [hasActiveConfig, setHasActiveConfig] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);

  useEffect(() => {
    fetchCurrentConfig();
  }, []);

  const fetchCurrentConfig = async () => {
    try {
      const configuration = await apiService.getConfiguration();
      if (configuration && configuration.configuration) {
        // Merge with defaults to ensure no undefined values
        const mergedConfig = {
          name: configuration.configuration.name || 'Default Configuration',
          academic_year: configuration.configuration.academic_year || '2024-25',
          semester: configuration.configuration.semester || 'Odd',
          college_start_time: configuration.configuration.college_start_time || '09:00:00',
          college_end_time: configuration.configuration.college_end_time || '17:45:00',
          lunch_start_time: configuration.configuration.lunch_start_time || '13:00:00',
          lunch_end_time: configuration.configuration.lunch_end_time || '13:45:00',
          project_half_days_per_week: configuration.configuration.project_half_days_per_week || 1,
          project_day_preference: configuration.configuration.project_day_preference || 'friday_afternoon',
          max_sessions_per_teacher: configuration.configuration.max_sessions_per_teacher || 14,
          min_sessions_per_teacher: configuration.configuration.min_sessions_per_teacher || 8
        };
        setConfig(mergedConfig);
        setHasActiveConfig(true);
      } else {
        setHasActiveConfig(false);
      }
    } catch (error) {
      console.error('Error fetching configuration:', error);
      setHasActiveConfig(false);
    }
  };

  const handleConfigChange = (field: keyof TimetableConfig, value: string | number) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSaveConfig = async () => {
    setLoading(true);
    try {
      await apiService.createConfiguration(config);
      setSaveDialog(true);
      setHasActiveConfig(true);
    } catch (error) {
      console.error('Error saving configuration:', error);
    }
    setLoading(false);
  };

  const calculateTimeSlots = () => {
    if (!config.college_start_time || !config.college_end_time || !config.lunch_start_time || !config.lunch_end_time) {
      return {
        totalSlots: 8,
        morningSlots: 4,
        afternoonSlots: 4,
        projectSlots: 4
      };
    }
    
    const startHour = parseInt(config.college_start_time.split(':')[0]);
    const endHour = parseInt(config.college_end_time.split(':')[0]);
    const lunchStart = parseInt(config.lunch_start_time.split(':')[0]);
    const lunchEnd = parseInt(config.lunch_end_time.split(':')[0]);
    
    const totalHours = endHour - startHour;
    const lunchHours = lunchEnd - lunchStart;
    const workingHours = totalHours - lunchHours;
    
    return {
      totalSlots: workingHours,
      morningSlots: lunchStart - startHour,
      afternoonSlots: endHour - lunchEnd,
      projectSlots: config.project_half_days_per_week * 4 // 4 hours per half day
    };
  };

  const timeSlots = calculateTimeSlots();

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', p: 3 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Settings color="primary" />
            Timetable Configuration Dashboard
          </Typography>
          
          <Typography variant="body1" color="text.secondary" paragraph>
            Configure timetable generation parameters. These settings will be used to create 
            optimized schedules that respect your institution's constraints and preferences.
          </Typography>

          {hasActiveConfig && (
            <Alert severity="info" sx={{ mb: 3 }}>
              An active configuration exists. Saving will update the current settings.
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid size={{ xs: 12 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <School />
                    Basic Information
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Configuration Name"
                        value={config.name}
                        onChange={(e) => handleConfigChange('name', e.target.value)}
                        placeholder="e.g., Semester 1 2024-25"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 3 }}>
                      <TextField
                        fullWidth
                        label="Academic Year"
                        value={config.academic_year}
                        onChange={(e) => handleConfigChange('academic_year', e.target.value)}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 3 }}>
                      <FormControl fullWidth>
                        <InputLabel>Semester</InputLabel>
                        <Select
                          value={config.semester}
                          onChange={(e) => handleConfigChange('semester', e.target.value)}
                        >
                          <MenuItem value="Odd">Odd Semester</MenuItem>
                          <MenuItem value="Even">Even Semester</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Time Settings */}
            <Grid size={{ xs: 12 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AccessTime />
                    Time Settings
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 3 }}>
                      <TextField
                        fullWidth
                        label="College Start Time"
                        type="time"
                        value={config.college_start_time}
                        onChange={(e) => handleConfigChange('college_start_time', e.target.value)}
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 3 }}>
                      <TextField
                        fullWidth
                        label="College End Time"
                        type="time"
                        value={config.college_end_time}
                        onChange={(e) => handleConfigChange('college_end_time', e.target.value)}
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 3 }}>
                      <TextField
                        fullWidth
                        label="Lunch Start"
                        type="time"
                        value={config.lunch_start_time}
                        onChange={(e) => handleConfigChange('lunch_start_time', e.target.value)}
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 3 }}>
                      <TextField
                        fullWidth
                        label="Lunch End"
                        type="time"
                        value={config.lunch_end_time}
                        onChange={(e) => handleConfigChange('lunch_end_time', e.target.value)}
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                  </Grid>

                  <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>Time Slot Preview:</Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip label={`Morning: ${timeSlots.morningSlots} slots`} color="primary" size="small" />
                      <Chip label={`Afternoon: ${timeSlots.afternoonSlots} slots`} color="secondary" size="small" />
                      <Chip label={`Total: ${timeSlots.totalSlots} working hours`} color="success" size="small" />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Project Time Settings */}
            <Grid size={{ xs: 12 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Schedule />
                    Project Time Settings
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Project Half-Days per Week"
                        type="number"
                        value={config.project_half_days_per_week}
                        onChange={(e) => handleConfigChange('project_half_days_per_week', parseInt(e.target.value))}
                        inputProps={{ min: 0, max: 5 }}
                        helperText="Number of half-days (4 hours each) dedicated to project work"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <FormControl fullWidth>
                        <InputLabel>Project Day Preference</InputLabel>
                        <Select
                          value={config.project_day_preference}
                          onChange={(e) => handleConfigChange('project_day_preference', e.target.value)}
                        >
                          <MenuItem value="friday_afternoon">Friday Afternoon</MenuItem>
                          <MenuItem value="thursday_afternoon">Thursday Afternoon</MenuItem>
                          <MenuItem value="wednesday_afternoon">Wednesday Afternoon</MenuItem>
                          <MenuItem value="flexible">Flexible - Algorithm Decides</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>

                  {config.project_half_days_per_week > 0 && (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      {timeSlots.projectSlots} hours per week will be reserved for project work
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Faculty Load Settings */}
            <Grid size={{ xs: 12 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Faculty Load Balancing
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Maximum Sessions per Teacher"
                        type="number"
                        value={config.max_sessions_per_teacher}
                        onChange={(e) => handleConfigChange('max_sessions_per_teacher', parseInt(e.target.value))}
                        inputProps={{ min: 8, max: 20 }}
                        helperText="Maximum weekly sessions for any teacher"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Minimum Sessions per Teacher"
                        type="number"
                        value={config.min_sessions_per_teacher}
                        onChange={(e) => handleConfigChange('min_sessions_per_teacher', parseInt(e.target.value))}
                        inputProps={{ min: 4, max: 16 }}
                        helperText="Minimum weekly sessions for any teacher"
                      />
                    </Grid>
                  </Grid>

                  <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>Load Distribution:</Typography>
                    <Typography variant="body2">
                      Target range: {config.min_sessions_per_teacher} - {config.max_sessions_per_teacher} sessions per teacher per week
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Preview Toggle */}
            <Grid size={{ xs: 12 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={previewMode}
                    onChange={(e) => setPreviewMode(e.target.checked)}
                  />
                }
                label="Preview Mode (View configuration without saving)"
              />
            </Grid>

            {/* Action Buttons */}
            <Grid size={{ xs: 12 }}>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  {hasActiveConfig ? 'Update existing configuration' : 'Create new configuration'}
                </Typography>
                
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <Save />}
                  onClick={handleSaveConfig}
                  disabled={loading || previewMode || !config.name}
                  size="large"
                >
                  {loading ? 'Saving...' : hasActiveConfig ? 'Update Configuration' : 'Save Configuration'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Success Dialog */}
      <Dialog open={saveDialog} onClose={() => setSaveDialog(false)}>
        <DialogTitle>Configuration Saved Successfully!</DialogTitle>
        <DialogContent>
          <Typography paragraph>
            Your timetable configuration has been saved and activated. The new settings will be 
            used for all future timetable generations.
          </Typography>
          <Typography variant="subtitle2" gutterBottom>Configuration Summary:</Typography>
          <ul>
            <li>Working Hours: {config.college_start_time} - {config.college_end_time}</li>
            <li>Lunch Break: {config.lunch_start_time} - {config.lunch_end_time}</li>
            <li>Project Time: {config.project_half_days_per_week} half-days per week</li>
            <li>Faculty Load: {config.min_sessions_per_teacher} - {config.max_sessions_per_teacher} sessions</li>
          </ul>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialog(false)} variant="contained">
            Continue to Timetable Generation
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConfigurationDashboard;
