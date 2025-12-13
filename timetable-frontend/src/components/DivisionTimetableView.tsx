import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Grid
} from '@mui/material';
import { School, AccessTime, Person, Room } from '@mui/icons-material';

interface Division {
  id: number;
  name: string;
  year_name: string;
  key: string;
  display_name: string;
}

interface Session {
  id: number;
  subject: {
    name: string;
    code: string;
    year: { name: string };
    division: { name: string };
  };
  teacher: {
    name: string;
  };
  room?: {
    name: string;
  };
  lab?: {
    name: string;
  };
  timeslot: {
    day: string;
    start_time: string;
    end_time: string;
    slot_number: number;
  };
  batch_number: number;
}

const DivisionTimetableView: React.FC = () => {
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [selectedDivision, setSelectedDivision] = useState<string>('');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchDivisions();
  }, []);

  const fetchDivisions = async () => {
    try {
      const divisionsData = await apiService.getDivisions();
      setDivisions(divisionsData);
    } catch (error) {
      console.error('Error fetching divisions:', error);
      setError('Failed to load divisions');
    }
  };

  const fetchDivisionTimetable = async (divisionKey: string) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`http://localhost:8000/api/timetable/?division=${divisionKey}`);
      if (response.ok) {
        const sessionsData = await response.json();
        setSessions(sessionsData);
      } else {
        setError('Failed to load timetable');
      }
    } catch (error) {
      console.error('Error fetching timetable:', error);
      setError('Failed to load timetable');
    }
    
    setLoading(false);
  };

  const handleDivisionChange = (divisionKey: string) => {
    setSelectedDivision(divisionKey);
    if (divisionKey) {
      fetchDivisionTimetable(divisionKey);
    } else {
      setSessions([]);
    }
  };

  const groupSessionsByDay = (sessions: Session[]) => {
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
    const grouped: { [key: string]: Session[] } = {};
    
    days.forEach(day => {
      grouped[day] = sessions
        .filter(session => session.timeslot.day.toLowerCase() === day)
        .sort((a, b) => a.timeslot.slot_number - b.timeslot.slot_number);
    });
    
    return grouped;
  };

  const getSelectedDivisionInfo = () => {
    return divisions.find(div => div.key === selectedDivision);
  };

  const sessionsByDay = groupSessionsByDay(sessions);

  return (
    <Box sx={{ maxWidth: 1400, mx: 'auto', p: 3 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <School color="primary" />
            Division-Specific Timetable View
          </Typography>
          
          <Typography variant="body1" color="text.secondary" paragraph>
            View timetables for specific divisions with proper proficiency-based assignments.
          </Typography>

          <Box sx={{ mb: 4 }}>
            <FormControl fullWidth sx={{ maxWidth: 400 }}>
              <InputLabel>Select Division</InputLabel>
              <Select
                value={selectedDivision}
                onChange={(e) => handleDivisionChange(e.target.value)}
                label="Select Division"
              >
                <MenuItem value="">
                  <em>All Divisions</em>
                </MenuItem>
                {divisions.map((division) => (
                  <MenuItem key={division.key} value={division.key}>
                    {division.display_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {loading && (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
              <CircularProgress />
            </Box>
          )}

          {selectedDivision && !loading && sessions.length > 0 && (
            <Box>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AccessTime />
                Timetable for {getSelectedDivisionInfo()?.display_name}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                Total Sessions: {sessions.length} | Division: {selectedDivision}
              </Typography>

              <Grid container spacing={3}>
                {Object.entries(sessionsByDay).map(([day, daySessions]) => (
                  <Grid item xs={12} key={day}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom sx={{ textTransform: 'capitalize' }}>
                          {day}
                        </Typography>
                        
                        {daySessions.length > 0 ? (
                          <TableContainer component={Paper} variant="outlined">
                            <Table size="small">
                              <TableHead>
                                <TableRow>
                                  <TableCell>Time</TableCell>
                                  <TableCell>Subject</TableCell>
                                  <TableCell>Teacher</TableCell>
                                  <TableCell>Location</TableCell>
                                  <TableCell>Batch</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {daySessions.map((session) => (
                                  <TableRow key={session.id}>
                                    <TableCell>
                                      <Typography variant="body2" fontWeight="bold">
                                        {session.timeslot.start_time} - {session.timeslot.end_time}
                                      </Typography>
                                      <Typography variant="caption" color="text.secondary">
                                        Slot {session.timeslot.slot_number}
                                      </Typography>
                                    </TableCell>
                                    <TableCell>
                                      <Typography variant="body2" fontWeight="bold">
                                        {session.subject.name}
                                      </Typography>
                                      <Typography variant="caption" color="text.secondary">
                                        {session.subject.code}
                                      </Typography>
                                    </TableCell>
                                    <TableCell>
                                      <Box display="flex" alignItems="center" gap={1}>
                                        <Person fontSize="small" />
                                        {session.teacher.name}
                                      </Box>
                                    </TableCell>
                                    <TableCell>
                                      <Box display="flex" alignItems="center" gap={1}>
                                        <Room fontSize="small" />
                                        {session.room?.name || session.lab?.name || 'TBD'}
                                      </Box>
                                    </TableCell>
                                    <TableCell>
                                      <Chip 
                                        label={`Batch ${session.batch_number}`}
                                        size="small"
                                        color="primary"
                                        variant="outlined"
                                      />
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        ) : (
                          <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                            No sessions scheduled for {day}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {selectedDivision && !loading && sessions.length === 0 && !error && (
            <Alert severity="info">
              No sessions found for the selected division. Generate a timetable first.
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default DivisionTimetableView;
