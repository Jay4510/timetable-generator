/**
 * Main Dashboard for Timetable Incharge
 * Clean, professional design with clear status and quick actions
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
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Assessment,
  Settings,
  People,
  School,
  Room,
  Schedule,
  CheckCircle,
  Warning,
  Error,
  Refresh,
  Download
} from '@mui/icons-material';

import type { DashboardStats } from '../types/api';
import timetableApi from '../services/timetableApi';

interface DashboardProps {
  onNavigate: (view: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setError(null);
      const dashboardStats = await timetableApi.getDashboardStats();
      setStats(dashboardStats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    timetableApi.clearCache();
    await loadDashboardData();
    setRefreshing(false);
  };

  const getHealthColor = (completeness: number) => {
    if (completeness >= 90) return 'success';
    if (completeness >= 70) return 'warning';
    return 'error';
  };

  const getHealthIcon = (completeness: number) => {
    if (completeness >= 90) return <CheckCircle color="success" />;
    if (completeness >= 70) return <Warning color="warning" />;
    return <Error color="error" />;
  };

  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>Loading Dashboard...</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="outlined" onClick={loadDashboardData}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
            📅 Welcome, Timetable Incharge!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Your one-stop solution for creating and managing college timetables. Everything you need is right here - simple and easy to use.
          </Typography>
        </Box>
        <Tooltip title="Refresh Data">
          <IconButton onClick={handleRefresh} disabled={refreshing}>
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* System Health Status */}
      <Card sx={{ mb: 4, border: '1px solid', borderColor: 'divider' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            {getHealthIcon(stats?.system_health.data_completeness || 0)}
            <Typography variant="h6">System Health</Typography>
            <Chip 
              label={`${stats?.system_health.data_completeness || 0}% Complete`}
              color={getHealthColor(stats?.system_health.data_completeness || 0)}
              size="small"
            />
          </Box>
          
          <LinearProgress 
            variant="determinate" 
            value={stats?.system_health.data_completeness || 0}
            color={getHealthColor(stats?.system_health.data_completeness || 0)}
            sx={{ mb: 2, height: 8, borderRadius: 4 }}
          />

          {stats?.system_health.critical_issues && stats.system_health.critical_issues.length > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Critical Issues:</Typography>
              {stats.system_health.critical_issues.map((issue, index) => (
                <Typography key={index} variant="body2">• {issue}</Typography>
              ))}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Last Generation Status */}
      {stats?.last_generation && (
        <Card sx={{ mb: 4, border: '1px solid', borderColor: 'divider' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Last Generation</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 600 }}>
                    {stats.last_generation.fitness_score.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Fitness Score
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color={stats.last_generation.total_violations === 0 ? 'success.main' : 'warning.main'}>
                    {stats.last_generation.total_violations}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Violations
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    {stats.last_generation.sessions_created}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Sessions Created
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {new Date(stats.last_generation.timestamp).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Generated On
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card 
            sx={{ 
              cursor: 'pointer',
              border: '2px solid',
              borderColor: 'primary.main',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              '&:hover': { 
                transform: 'translateY(-2px)',
                boxShadow: 4
              },
              transition: 'all 0.2s ease-in-out'
            }}
            onClick={() => onNavigate('generator')}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <PlayArrow sx={{ fontSize: 32 }} />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  Generate Timetable
                </Typography>
              </Box>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Run the algorithm to create optimized timetables
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card 
            sx={{ 
              cursor: 'pointer',
              border: '1px solid',
              borderColor: 'divider',
              '&:hover': { 
                transform: 'translateY(-2px)',
                boxShadow: 4
              },
              transition: 'all 0.2s ease-in-out'
            }}
            onClick={() => onNavigate('violations')}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Assessment color="primary" sx={{ fontSize: 32 }} />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  Review Violations
                </Typography>
              </Box>
              <Typography variant="body1" color="text.secondary">
                Analyze and resolve scheduling conflicts
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Data Overview */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Data Overview</Typography>
          <Grid container spacing={3}>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <People color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {stats?.teachers_count || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Teachers
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <School color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {stats?.subjects_count || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Subjects
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Room color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {(stats?.rooms_count || 0) + (stats?.labs_count || 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rooms & Labs
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Schedule color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {stats?.timeslots_count || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Time Slots
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Settings color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h5" sx={{ fontWeight: 600, color: stats?.system_health.configuration_status === 'complete' ? 'success.main' : 'warning.main' }}>
                  {stats?.system_health.configuration_status === 'complete' ? '✓' : '!'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Config
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={2}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Download color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {stats?.divisions_count || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Divisions
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Setup Actions */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Setup & Configuration</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<People />}
                onClick={() => onNavigate('data-setup')}
                sx={{ py: 1.5, justifyContent: 'flex-start' }}
              >
                Manage Data
              </Button>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Settings />}
                onClick={() => onNavigate('constraints')}
                sx={{ py: 1.5, justifyContent: 'flex-start' }}
              >
                Configure Constraints
              </Button>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Download />}
                onClick={() => onNavigate('export')}
                sx={{ py: 1.5, justifyContent: 'flex-start' }}
              >
                Export & Publish
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;
