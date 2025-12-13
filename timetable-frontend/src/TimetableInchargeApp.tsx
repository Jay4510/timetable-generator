import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Alert,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  CssBaseline,
  ThemeProvider,
  createTheme,
  CircularProgress,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import {
  Menu,
  Dashboard as DashboardIcon,
  PlayArrow,
  Settings,
  Assessment,
  Publish,
  People,
  School,
  Build,
  PersonRemove
} from '@mui/icons-material';

// Import new components
import Dashboard from './components/Dashboard';
import DataSetup from './components/DataSetup';
import TimetableGenerator from './components/TimetableGenerator';
import ConstraintsConfiguration from './components/ConstraintsConfiguration';
import ViolationsReview from './components/ViolationsReview';
import PublishExport from './components/PublishExport';
import EquipmentManagement from './components/EquipmentManagement';
import DMCETimetableGenerator from './components/DMCETimetableGenerator';

// Legacy imports for backward compatibility
import TabularTimetableView from './TabularTimetableView';
import DivisionSelector from './components/DivisionSelector';
import SystemConfigurationDashboard from './components/SystemConfigurationDashboard';
import ConfigurationDashboard from './ConfigurationDashboard';
import ProficiencyWizard from './ProficiencyWizard';
import ResignationManagement from './ResignationManagement';
import DataManagementCenter from './DataManagementCenter';
import ErrorBoundaryWrapper from './components/ErrorBoundaryWrapper';

import apiService from './services/apiService';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

const TimetableInchargeApp: React.FC = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [systemReady, setSystemReady] = useState(false);
  const [selectedDivision, setSelectedDivision] = useState('');
  const [divisionSessions, setDivisionSessions] = useState<any[]>([]);

  useEffect(() => {
    checkSystem();
  }, []);

  const checkSystem = async () => {
    try {
      const teachers = await apiService.getTeachers();
      setSystemReady(Array.isArray(teachers) && teachers.length > 0);
      setError(null);
    } catch (e) {
      setError('Backend not accessible. Please start the Django server.');
      setSystemReady(false);
    }
  };

  const handleDivisionChange = (divisionKey: string, sessions: any[]) => {
    setSelectedDivision(divisionKey);
    setDivisionSessions(sessions);
  };

  const generateTimetable = async () => {
    setLoading(true);
    setError(null);
    try {
      await apiService.generateTimetable();
      setCurrentView('timetable');
    } catch (e) {
      setError('Failed to generate timetable. Please try again.');
    }
    setLoading(false);
  };

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  // Navigation handler
  const handleNavigate = (view: string) => {
    setCurrentView(view);
  };

  // Render specific views with new components
  if (currentView !== 'dashboard') {
    const components = {
      // New professional components
      'dmce-generator': <DMCETimetableGenerator />,
      'data-setup': <DataSetup />,
      'generator': <TimetableGenerator onNavigate={handleNavigate} />,
      'constraints': <ConstraintsConfiguration />,
      'violations': <ViolationsReview />,
      'publish': <PublishExport />,
      'equipment': <EquipmentManagement />,
      'configuration': <ConfigurationDashboard />,
      'systemconfig': <SystemConfigurationDashboard />,
      'proficiency': <ProficiencyWizard />,
      'resignation': <ResignationManagement />,
      'data': <DataManagementCenter />,
      'timetable': (
        <Box>
          <Typography variant="h4" gutterBottom>
            Enhanced Timetable View
          </Typography>
          <Box sx={{ mb: 3 }}>
            <DivisionSelector 
              onDivisionChange={handleDivisionChange}
              selectedDivision={selectedDivision}
            />
          </Box>
          {divisionSessions.length > 0 && (
            <TabularTimetableView sessions={divisionSessions} />
          )}
        </Box>
      )
    };

    const component = components[currentView as keyof typeof components];
    
    if (component) {
      return (
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <ErrorBoundaryWrapper>
            <Container maxWidth="xl" sx={{ py: 4 }}>
              {component}
            </Container>
          </ErrorBoundaryWrapper>
        </ThemeProvider>
      );
    }
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ErrorBoundaryWrapper>
        <Container maxWidth="xl" sx={{ py: 4 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Main Dashboard - Use new Dashboard component */}
          <Dashboard onNavigate={handleNavigate} />
        </Container>
      </ErrorBoundaryWrapper>
    </ThemeProvider>
  );
};

export default TimetableInchargeApp;
