import React, { useState, useEffect } from 'react';
import axios, { AxiosError } from 'axios';
import { 
  Container, 
  Typography, 
  Button, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Alert, 
  CircularProgress, 
  Box, 
  // Grid,  // Commented out as it's not used
  LinearProgress
} from '@mui/material';

interface Session {
  id: number;
  subject_name: string;
  teacher_name: string;
  room_name: string | null;
  lab_name: string | null;
  timeslot_info: string;
  batch_number: number;
  year_division: string;
}

const TimetableView: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchTimetable();
  }, []);

  const fetchTimetable = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/timetable/');
      setSessions(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch timetable. Please generate one first.');
    } finally {
      setLoading(false);
    }
  };

  const [progress, setProgress] = useState<number>(0);
  const [progressText, setProgressText] = useState<string>('');

  const handleGenerate = async () => {
    setGenerating(true);
    setProgress(0);
    setProgressText('Starting Multi-Algorithm Optimization...');
    setError(null);
    
    try {
      // Enhanced generation with better progress tracking
      setProgressText('Initializing optimization algorithms...');
      setProgress(10);
      
      const startResponse = await axios.post('http://localhost:8000/api/generate-timetable/', {
        timeout: 300000 // 5 minute timeout
      });
      
      // Simulate progress for better UX (since we're running synchronously)
      const progressSteps = [
        { progress: 20, text: 'Analyzing problem complexity...' },
        { progress: 35, text: 'Running Genetic Algorithm...' },
        { progress: 60, text: 'Applying Hybrid Optimization...' },
        { progress: 80, text: 'Fine-tuning with Simulated Annealing...' },
        { progress: 95, text: 'Saving optimized timetable...' }
      ];
      
      for (const step of progressSteps) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setProgress(step.progress);
        setProgressText(step.text);
      }
      
      if (startResponse.data.status === 'success') {
        setProgress(100);
        setProgressText('Multi-Algorithm Optimization completed successfully!');
        
        // Show optimization details
        const details = startResponse.data.optimization_details;
        if (details) {
          console.log('Optimization Details:', details);
          setProgressText(
            `Success! Used algorithms: ${details.algorithms_used?.join(', ')} | ` +
            `Fitness: ${details.final_fitness} | Time: ${details.optimization_time?.toFixed(2)}s`
          );
        }
        
        await fetchTimetable();
      } else {
        throw new Error(startResponse.data.message || 'Failed to generate timetable');
      }
      
    } catch (error: unknown) {
      console.error('Error generating timetable:', error);
      const errorMessage = error instanceof AxiosError 
        ? error.response?.data?.message || error.message
        : 'Failed to generate timetable. Please try again.';
      setError(errorMessage);
      setProgress(0);
    } finally {
      setGenerating(false);
      // Clear progress after 5 seconds
      setTimeout(() => {
        setProgress(0);
        setProgressText('');
      }, 5000);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          College Timetable Generator
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Box sx={{ width: '100%', mb: 2 }}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleGenerate} 
              disabled={generating}
              fullWidth
              sx={{ mb: 1 }}
              startIcon={generating ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {generating ? 'Generating...' : 'Generate New Timetable'}
            </Button>
            
            {generating && (
              <Box sx={{ width: '100%', mt: 1 }}>
                <LinearProgress 
                  variant={progress > 0 ? 'determinate' : 'indeterminate'} 
                  value={progress} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {progressText}
                </Typography>
              </Box>
            )}
          </Box>
          <Button 
            variant="outlined" 
            onClick={fetchTimetable} 
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {loading && (
          <Box display="flex" justifyContent="center" sx={{ my: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {!loading && sessions.length > 0 ? (
          <TableContainer component={Paper}>
            <Table sx={{ minWidth: 650 }} aria-label="timetable">
              <TableHead>
                <TableRow>
                  <TableCell>Time Slot</TableCell>
                  <TableCell>Subject</TableCell>
                  <TableCell>Teacher</TableCell>
                  <TableCell>Room/Lab</TableCell>
                  <TableCell>Year/Division</TableCell>
                  <TableCell>Batch</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sessions.map((session) => (
                  <TableRow key={session.id}>
                    <TableCell>{session.timeslot_info}</TableCell>
                    <TableCell>{session.subject_name}</TableCell>
                    <TableCell>{session.teacher_name}</TableCell>
                    <TableCell>{session.room_name || 'N/A'}</TableCell>
                    <TableCell>{session.year_division}</TableCell>
                    <TableCell>{session.batch_number}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          !loading && (
            <Alert severity="info">
              No timetable data available. Please generate a new one.
            </Alert>
          )
        )}
      </Box>
    </Container>
  );
};

export default TimetableView;