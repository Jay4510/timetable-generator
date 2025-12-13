/**
 * Constraints & Preferences Configuration
 * Professional UI for system configuration and teacher preferences
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Slider,
  Alert,
  Divider,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  Save,
  Settings,
  Schedule,
  People,
  School,
  AccessTime,
  Speed,
  Edit,
  CheckCircle,
  Warning,
  Info
} from '@mui/icons-material';

import type { SystemConfiguration, Teacher, SubjectProficiency } from '../types/api';
import timetableApi from '../services/timetableApi';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ paddingTop: 24 }}>
    {value === index && children}
  </div>
);

const ConstraintsConfiguration: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // System configuration
  const [systemConfig, setSystemConfig] = useState<SystemConfiguration | null>(null);
  const [configChanged, setConfigChanged] = useState(false);

  // Teachers and proficiencies
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [proficiencies, setProficiencies] = useState<SubjectProficiency[]>([]);
  const [editingTeacher, setEditingTeacher] = useState<Teacher | null>(null);
  const [teacherDialogOpen, setTeacherDialogOpen] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [config, teachersData, proficienciesData] = await Promise.all([
        timetableApi.getSystemConfiguration(),
        timetableApi.getTeachers(),
        timetableApi.getSubjectProficiencies()
      ]);

      setSystemConfig(config);
      setTeachers(teachersData.results || []);
      setProficiencies(proficienciesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (field: keyof SystemConfiguration, value: any) => {
    if (!systemConfig) return;
    
    setSystemConfig({
      ...systemConfig,
      [field]: value
    });
    setConfigChanged(true);
  };

  const saveSystemConfiguration = async () => {
    if (!systemConfig) return;

    setLoading(true);
    try {
      const updatedConfig = await timetableApi.updateSystemConfiguration(systemConfig);
      setSystemConfig(updatedConfig);
      setConfigChanged(false);
      setSuccess('System configuration saved successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  const openTeacherPreferences = (teacher: Teacher) => {
    setEditingTeacher(teacher);
    setTeacherDialogOpen(true);
  };

  const saveTeacherPreferences = async () => {
    if (!editingTeacher) return;

    setLoading(true);
    try {
      const updatedTeacher = await timetableApi.updateTeacher(editingTeacher.id, editingTeacher);
      setTeachers(teachers.map(t => t.id === editingTeacher.id ? updatedTeacher : t));
      setTeacherDialogOpen(false);
      setSuccess('Teacher preferences saved successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save teacher preferences');
    } finally {
      setLoading(false);
    }
  };

  const getConstraintStatus = () => {
    if (!systemConfig) return { score: 0, issues: [] };

    const issues = [];
    let score = 100;

    if (systemConfig.max_sessions_per_teacher <= systemConfig.min_sessions_per_teacher) {
      issues.push('Max sessions must be greater than min sessions');
      score -= 20;
    }

    if (systemConfig.default_lab_duration_hours < 1) {
      issues.push('Lab duration should be at least 1 hour');
      score -= 15;
    }

    if (systemConfig.morning_session_percentage + systemConfig.afternoon_session_percentage !== 100) {
      issues.push('Morning and afternoon percentages must sum to 100%');
      score -= 25;
    }

    if (!systemConfig.break_start_time || !systemConfig.break_end_time) {
      issues.push('Break times must be configured');
      score -= 20;
    }

    return { score: Math.max(0, score), issues };
  };

  const renderSystemConfigurationTab = () => {
    if (!systemConfig) return <LinearProgress />;

    const { score, issues } = getConstraintStatus();

    return (
      <Box>
        {/* Configuration Health */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Settings color="primary" />
              <Typography variant="h6">Configuration Health</Typography>
              <Chip 
                label={`${score}%`} 
                color={score >= 90 ? 'success' : score >= 70 ? 'warning' : 'error'}
              />
            </Box>
            
            <LinearProgress 
              variant="determinate" 
              value={score} 
              color={score >= 90 ? 'success' : score >= 70 ? 'warning' : 'error'}
              sx={{ height: 8, borderRadius: 4, mb: 2 }}
            />

            {issues.length > 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Configuration Issues:</Typography>
                {issues.map((issue, index) => (
                  <Typography key={index} variant="body2">• {issue}</Typography>
                ))}
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Teacher Workload - Auto-Calculated by Backend */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <People color="primary" />
              Teacher Workload Distribution
            </Typography>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Automatic Fair Distribution:</strong> The system automatically distributes teaching loads fairly among all teachers. 
                No manual limits needed - the algorithm ensures balanced workload with 20% tolerance from the ideal distribution.
              </Typography>
            </Alert>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    How Workload Distribution Works:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • System calculates ideal sessions per teacher based on total sessions and available teachers<br/>
                    • Allows ±20% variance from ideal load for flexibility<br/>
                    • Automatically prevents overloading or underutilizing teachers<br/>
                    • Considers teacher proficiency scores for optimal assignment
                  </Typography>
                </Box>
              </Grid>

            </Grid>
          </CardContent>
        </Card>

        {/* Break Times */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AccessTime color="primary" />
              Break Time Configuration
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Break Start Time"
                  type="time"
                  value={systemConfig.break_start_time}
                  onChange={(e) => handleConfigChange('break_start_time', e.target.value)}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Break End Time"
                  type="time"
                  value={systemConfig.break_end_time}
                  onChange={(e) => handleConfigChange('break_end_time', e.target.value)}
                />
              </Grid>
            </Grid>
            
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              No classes will be scheduled during this break period
            </Typography>
          </CardContent>
        </Card>

        {/* Lab Configuration */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <School color="primary" />
              Lab & Session Configuration
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Default Lab Duration (Hours)"
                  type="number"
                  value={systemConfig.default_lab_duration_hours}
                  onChange={(e) => handleConfigChange('default_lab_duration_hours', parseInt(e.target.value))}
                  inputProps={{ min: 1, max: 4 }}
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Standard duration for lab sessions
                </Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Remedial Lectures per Week"
                  type="number"
                  value={systemConfig.remedial_lectures_per_week}
                  onChange={(e) => handleConfigChange('remedial_lectures_per_week', parseInt(e.target.value))}
                  inputProps={{ min: 0, max: 3 }}
                  helperText="Recommended: 0-3 lectures per week"
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Required remedial lectures per subject per week (0-3 range)
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={systemConfig.allow_cross_year_lab_conflicts}
                      onChange={(e) => handleConfigChange('allow_cross_year_lab_conflicts', e.target.checked)}
                    />
                  }
                  label="Allow Cross-Year Lab Conflicts"
                />
                <Typography variant="body2" color="text.secondary">
                  Allow students from different years to use the same lab simultaneously
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Session Distribution - Auto-Balanced by Backend */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Schedule color="primary" />
              Morning/Afternoon Session Balance
            </Typography>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Automatic Balance:</strong> The system automatically balances sessions between morning and afternoon slots. 
                Target: 40-60% morning sessions with 35-65% tolerance for optimal distribution.
              </Typography>
            </Alert>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    How Session Balance Works:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Algorithm automatically aims for 40-60% morning sessions<br/>
                    • Allows 35-65% range for flexibility based on constraints<br/>
                    • Considers teacher preferences and room availability<br/>
                    • Balances workload across morning and afternoon periods<br/>
                    • No manual adjustment needed - optimized automatically
                  </Typography>
                </Box>
              </Grid>

            </Grid>
          </CardContent>
        </Card>

        {/* Save Button */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<Save />}
            onClick={saveSystemConfiguration}
            disabled={!configChanged || loading}
          >
            {loading ? 'Saving...' : 'Save Configuration'}
          </Button>
        </Box>
      </Box>
    );
  };

  const renderTeacherPreferencesTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Teacher Preferences</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure individual teacher preferences for optimal scheduling
      </Typography>

      <List>
        {teachers.map((teacher) => (
          <Paper key={teacher.id} sx={{ mb: 2 }}>
            <ListItem>
              <ListItemText
                primary={teacher.name}
                secondary={
                  <Box>
                    <Typography variant="body2">
                      Time Preference: <Chip label={teacher.time_preference} size="small" />
                    </Typography>
                    <Typography variant="body2">
                      Sessions: {teacher.min_sessions_per_week}-{teacher.max_sessions_per_week} per week
                    </Typography>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <Tooltip title="Edit Preferences">
                  <IconButton onClick={() => openTeacherPreferences(teacher)}>
                    <Edit />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          </Paper>
        ))}
      </List>
    </Box>
  );

  const renderTeacherPreferencesDialog = () => (
    <Dialog open={teacherDialogOpen} onClose={() => setTeacherDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>Edit Teacher Preferences - {editingTeacher?.name}</DialogTitle>
      <DialogContent>
        {editingTeacher && (
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Min Sessions per Week"
                  type="number"
                  value={editingTeacher.min_sessions_per_week}
                  onChange={(e) => setEditingTeacher({
                    ...editingTeacher,
                    min_sessions_per_week: parseInt(e.target.value)
                  })}
                  inputProps={{ min: 1, max: 30 }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Max Sessions per Week"
                  type="number"
                  value={editingTeacher.max_sessions_per_week}
                  onChange={(e) => setEditingTeacher({
                    ...editingTeacher,
                    max_sessions_per_week: parseInt(e.target.value)
                  })}
                  inputProps={{ min: 1, max: 40 }}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography gutterBottom>Time Preference</Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {['morning', 'afternoon', 'no_preference'].map((pref) => (
                    <Chip
                      key={pref}
                      label={pref.replace('_', ' ')}
                      clickable
                      color={editingTeacher.time_preference === pref ? 'primary' : 'default'}
                      onClick={() => setEditingTeacher({
                        ...editingTeacher,
                        time_preference: pref as any
                      })}
                    />
                  ))}
                </Box>
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={editingTeacher.available}
                      onChange={(e) => setEditingTeacher({
                        ...editingTeacher,
                        available: e.target.checked
                      })}
                    />
                  }
                  label="Available for Scheduling"
                />
              </Grid>
            </Grid>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setTeacherDialogOpen(false)}>Cancel</Button>
        <Button onClick={saveTeacherPreferences} variant="contained" disabled={loading}>
          Save Preferences
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Constraints & Preferences
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Configure system constraints and teacher preferences for optimal timetable generation
      </Typography>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

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

      <Card>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab icon={<Settings />} label="System Configuration" />
          <Tab icon={<People />} label="Teacher Preferences" />
        </Tabs>

        <CardContent>
          <TabPanel value={activeTab} index={0}>
            {renderSystemConfigurationTab()}
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            {renderTeacherPreferencesTab()}
          </TabPanel>
        </CardContent>
      </Card>

      {renderTeacherPreferencesDialog()}
    </Box>
  );
};

export default ConstraintsConfiguration;
