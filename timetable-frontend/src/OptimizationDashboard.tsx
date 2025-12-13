import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert
} from '@mui/material';
import {
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

interface OptimizationStats {
  algorithmsUsed: string[];
  finalFitness: number;
  optimizationTime: number;
  sessionsCreated: number;
  complexityLevel: string;
}

const OptimizationDashboard: React.FC = () => {
  const [stats, setStats] = useState<OptimizationStats | null>(null);
  const [phase1Features] = useState([
    {
      name: 'Multi-Algorithm Optimizer',
      status: 'completed',
      description: 'Intelligent algorithm selection based on problem complexity'
    },
    {
      name: 'Genetic Algorithm Enhanced',
      status: 'completed',
      description: 'Adaptive mutation rates and diversity tracking'
    },
    {
      name: 'Simulated Annealing',
      status: 'completed',
      description: 'Fine-tuning optimization for local improvements'
    },
    {
      name: 'Advanced Constraint Checking',
      status: 'completed',
      description: 'Detailed violation reporting and constraint categorization'
    },
    {
      name: 'Performance Analytics',
      status: 'completed',
      description: 'Algorithm performance tracking and optimization'
    }
  ]);

  useEffect(() => {
    // In a real implementation, this would fetch from an API
    // For now, we'll simulate the data
    const mockStats: OptimizationStats = {
      algorithmsUsed: ['genetic', 'hybrid_genetic', 'simulated_annealing'],
      finalFitness: -15.2,
      optimizationTime: 45.7,
      sessionsCreated: 84,
      complexityLevel: 'medium'
    };
    setStats(mockStats);
  }, []);

  const getComplexityColor = (level: string) => {
    switch (level) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  const getAlgorithmIcon = (algorithm: string) => {
    switch (algorithm) {
      case 'genetic': return <PsychologyIcon />;
      case 'hybrid_genetic': return <SpeedIcon />;
      case 'simulated_annealing': return <TimelineIcon />;
      default: return <SettingsIcon />;
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🚀 Phase 1: Advanced Optimization Engine
        </Typography>
        
        <Alert severity="success" sx={{ mb: 3 }}>
          <strong>Phase 1 Complete!</strong> Multi-algorithm optimization engine is now active. 
          The system intelligently selects and combines algorithms based on problem complexity.
        </Alert>

        <Grid container spacing={3}>
          {/* Optimization Statistics */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Latest Optimization Results
                </Typography>
                {stats && (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="body2" sx={{ mr: 1 }}>
                        Problem Complexity:
                      </Typography>
                      <Chip 
                        label={stats.complexityLevel.toUpperCase()} 
                        color={getComplexityColor(stats.complexityLevel) as any}
                        size="small"
                      />
                    </Box>
                    
                    <Typography variant="body2" gutterBottom>
                      <strong>Final Fitness Score:</strong> {stats.finalFitness}
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Optimization Time:</strong> {stats.optimizationTime}s
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Sessions Created:</strong> {stats.sessionsCreated}
                    </Typography>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="subtitle2" gutterBottom>
                      Algorithms Used:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {stats.algorithmsUsed.map((algorithm) => (
                        <Chip
                          key={algorithm}
                          icon={getAlgorithmIcon(algorithm)}
                          label={algorithm.replace('_', ' ').toUpperCase()}
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Phase 1 Features */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Phase 1 Features Implemented
                </Typography>
                <List dense>
                  {phase1Features.map((feature, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircleIcon color="success" />
                      </ListItemIcon>
                      <ListItemText
                        primary={feature.name}
                        secondary={feature.description}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Algorithm Performance Comparison */}
          <Grid size={{ xs: 12 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Algorithm Performance Insights
                </Typography>
                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <PsychologyIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                      <Typography variant="h6">Genetic Algorithm</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Best for initial solution exploration and handling complex constraint spaces
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <SpeedIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                      <Typography variant="h6">Hybrid Genetic</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Adaptive mutation rates and diversity tracking for better convergence
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 4 }}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <TimelineIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                      <Typography variant="h6">Simulated Annealing</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Fine-tuning and local optimization for polishing solutions
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Next Phase Preview */}
          <Grid size={{ xs: 12 }}>
            <Card sx={{ bgcolor: 'grey.50' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🔮 Coming Next: Phase 2 - AI Analytics & Collaboration
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  The next phase will introduce AI-powered analytics, predictive insights, 
                  real-time collaboration features, and advanced constraint management.
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label="AI Analytics" variant="outlined" />
                  <Chip label="Predictive Insights" variant="outlined" />
                  <Chip label="Real-time Collaboration" variant="outlined" />
                  <Chip label="Advanced Constraints" variant="outlined" />
                  <Chip label="Performance Monitoring" variant="outlined" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default OptimizationDashboard;
