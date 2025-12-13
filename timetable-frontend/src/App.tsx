import { useState } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container, Switch, FormControlLabel } from '@mui/material';
import TimetableView from './TimetableView';
import DataManagement from './DataManagement';
import OptimizationDashboard from './OptimizationDashboard';
import TimetableInchargeApp from './TimetableInchargeApp';
import DMCETimetableGenerator from './components/DMCETimetableGenerator';
import ErrorBoundaryWrapper from './components/ErrorBoundaryWrapper';

function App() {
  const [currentView, setCurrentView] = useState('incharge');
  const [useNewInterface, setUseNewInterface] = useState(true);

  if (useNewInterface) {
    return (
      <ErrorBoundaryWrapper>
        <DMCETimetableGenerator />
      </ErrorBoundaryWrapper>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            College Timetable Generator
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={useNewInterface}
                onChange={(e) => setUseNewInterface(e.target.checked)}
                color="default"
              />
            }
            label="New Interface"
            sx={{ color: 'white', mr: 2 }}
          />
          
          <Button 
            color="inherit" 
            onClick={() => setCurrentView('timetable')}
            variant={currentView === 'timetable' ? 'outlined' : 'text'}
          >
            Timetable
          </Button>
          <Button 
            color="inherit" 
            onClick={() => setCurrentView('data')}
            variant={currentView === 'data' ? 'outlined' : 'text'}
          >
            Data Management
          </Button>
          <Button 
            color="inherit" 
            onClick={() => setCurrentView('optimization')}
            variant={currentView === 'optimization' ? 'outlined' : 'text'}
          >
            Dashboard
          </Button>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth={false} sx={{ mt: 2 }}>
        <ErrorBoundaryWrapper>
          {currentView === 'timetable' && <TimetableView />}
          {currentView === 'data' && <DataManagement />}
          {currentView === 'optimization' && <OptimizationDashboard />}
        </ErrorBoundaryWrapper>
      </Container>
    </Box>
  );
}

export default App;