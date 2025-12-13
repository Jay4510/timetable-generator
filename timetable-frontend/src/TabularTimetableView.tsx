import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Download,
  Refresh,
  Schedule
} from '@mui/icons-material';
import apiService from './services/apiService';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface TimetableSession {
  id: number;
  subject_name: string;
  teacher_name: string;
  room_name: string;
  lab_name?: string;
  timeslot_info: string;
  batch_number?: number;
  year_division: string;
}

interface TabularTimetableViewProps {
  filteredSessions?: TimetableSession[];
  selectedDivision?: string;
}

const TabularTimetableView: React.FC<TabularTimetableViewProps> = ({ 
  filteredSessions, 
  selectedDivision 
}) => {
  const [sessions, setSessions] = useState<TimetableSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedYear, setSelectedYear] = useState<string>('ALL');
  const [internalDivision, setInternalDivision] = useState<string>('ALL');
  const [selectedYearDivision, setSelectedYearDivision] = useState<string>('ALL');

  // Time slots configuration (matching API response format)
  const timeSlots = [
    { slot: 1, time: '09:00-10:00' },
    { slot: 2, time: '10:00-11:00' },
    { slot: 3, time: '11:00-12:00' },
    { slot: 4, time: '12:00-13:00' },
    { slot: 5, time: '13:00-13:45', isBreak: true },
    { slot: 6, time: '13:45-14:45' },
    { slot: 7, time: '14:45-15:45' },
    { slot: 8, time: '15:45-16:45' },
    { slot: 9, time: '16:45-17:45' }
  ];

  const days = ['MON', 'TUE', 'WED', 'THU', 'FRI'];

  useEffect(() => {
    if (filteredSessions) {
      // Use filtered sessions from parent component
      setSessions(filteredSessions);
    } else {
      // Load all sessions if no filter provided
      loadTimetable();
    }
  }, [filteredSessions]);

  const loadTimetable = async () => {
    setLoading(true);
    try {
      const data = await apiService.getTimetable();
      console.log('Timetable data received:', data);
      
      // Handle different response formats
      let sessionsData = data;
      if (data && typeof data === 'object' && 'results' in data) {
        sessionsData = (data as any).results;
      } else if (Array.isArray(data)) {
        sessionsData = data;
      }
      
      console.log('Sessions data:', sessionsData);
      setSessions(sessionsData || []);
    } catch (error) {
      console.error('Error loading timetable:', error);
    }
    setLoading(false);
  };

  const parseTimeslotInfo = (timeslotInfo: string) => {
    // Parse "tuesday 15:45-16:45" format
    if (!timeslotInfo) return { day: '', time: '' };
    
    const parts = timeslotInfo.toLowerCase().split(' ');
    if (parts.length < 2) return { day: '', time: '' };
    
    const day = parts[0];
    const time = parts[1];
    
    // Convert day to uppercase format for matching
    const dayMap: { [key: string]: string } = {
      'monday': 'MON',
      'tuesday': 'TUE', 
      'wednesday': 'WED',
      'thursday': 'THU',
      'friday': 'FRI'
    };
    
    return { 
      day: dayMap[day] || day.toUpperCase(), 
      time: time 
    };
  };

  const getSessionForSlot = (day: string, timeSlot: string) => {
    return sessions.find(session => {
      const { day: sessionDay, time: sessionTime } = parseTimeslotInfo(session.timeslot_info || '');
      console.log(`Checking: ${sessionDay} === ${day} && ${sessionTime} === ${timeSlot}`);
      return sessionDay === day && sessionTime === timeSlot;
    });
  };

  const displaySessions = sessions.filter(session => {
    if (selectedYear !== 'ALL' && !session.year_division.includes(selectedYear)) return false;
    if (internalDivision !== 'ALL' && !session.year_division.includes(internalDivision)) return false;
    return true;
  });

  const renderSessionCell = (session: TimetableSession | undefined, isBreak: boolean = false) => {
    if (isBreak) {
      return (
        <TableCell 
          sx={{ 
            textAlign: 'center', 
            backgroundColor: '#f5f5f5',
            fontWeight: 'bold',
            color: '#666'
          }}
        >
          RECESS
        </TableCell>
      );
    }

    if (!session) {
      return <TableCell sx={{ textAlign: 'center', color: '#ccc' }}>-</TableCell>;
    }

    return (
      <TableCell sx={{ padding: '8px', minWidth: '120px' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.75rem' }}>
            {session.subject_name}
          </Typography>
          <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.7rem' }}>
            {session.teacher_name}
          </Typography>
          <Typography variant="caption" sx={{ color: 'primary.main', fontSize: '0.7rem' }}>
            {session.room_name || session.lab_name}
          </Typography>
          {session.batch_number && (
            <Chip 
              label={`B${session.batch_number}`} 
              size="small" 
              sx={{ fontSize: '0.6rem', height: '16px' }}
            />
          )}
        </Box>
      </TableCell>
    );
  };

  const generatePDF = () => {
    const pdf = new jsPDF('l', 'mm', 'a4'); // Landscape orientation
    
    // Title
    pdf.setFontSize(16);
    pdf.text('COLLEGE TIMETABLE', pdf.internal.pageSize.width / 2, 20, { align: 'center' });
    
    pdf.setFontSize(12);
    pdf.text(`Academic Year: 2024-25 | Semester: VII`, pdf.internal.pageSize.width / 2, 30, { align: 'center' });
    
    // Create table data
    const tableData: string[][] = [];
    
    // Header row
    const headerRow = ['DAYS', ...timeSlots.map(slot => 
      slot.isBreak ? 'RECESS' : `${slot.slot}\n${slot.time}`
    )];
    tableData.push(headerRow);
    
    // Data rows
    days.forEach(day => {
      const row = [day];
      timeSlots.forEach(slot => {
        if (slot.isBreak) {
          row.push('RECESS');
        } else {
          const session = getSessionForSlot(day, slot.time);
          if (session) {
            row.push(`${session.subject_name}\n${session.teacher_name}\n${session.room_name || session.lab_name}`);
          } else {
            row.push('-');
          }
        }
      });
      tableData.push(row);
    });

    // Add table to PDF
    autoTable(pdf, {
      head: [headerRow],
      body: tableData.slice(1),
      startY: 40,
      styles: {
        fontSize: 8,
        cellPadding: 3,
        halign: 'center',
        valign: 'middle'
      },
      headStyles: {
        fillColor: [41, 128, 185],
        textColor: 255,
        fontStyle: 'bold'
      },
      columnStyles: {
        0: { fillColor: [52, 152, 219], textColor: 255, fontStyle: 'bold' },
        4: { fillColor: [241, 196, 15] } // Recess column
      },
      alternateRowStyles: {
        fillColor: [245, 245, 245]
      }
    });
    
    pdf.save('timetable.pdf');
  };

  const years = ['ALL', 'SE', 'TE', 'BE'];
  const divisions = ['ALL', 'A', 'B'];

  return (
    <Box sx={{ p: 3 }}>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4" sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Schedule color="primary" />
              College Timetable
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadTimetable}
                disabled={loading}
              >
                Refresh
              </Button>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={generatePDF}
                disabled={loading || sessions.length === 0}
              >
                Download PDF
              </Button>
            </Box>
          </Box>

              {/* Filters */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Year Division Filter</InputLabel>
                    <Select
                      value={selectedYearDivision}
                      label="Year Division Filter"
                      onChange={(e) => setSelectedYearDivision(e.target.value)}
                    >
                      <MenuItem value="ALL">All Year Divisions</MenuItem>
                      <MenuItem value="SE A">SE A</MenuItem>
                      <MenuItem value="SE B">SE B</MenuItem>
                      <MenuItem value="TE A">TE A</MenuItem>
                      <MenuItem value="TE B">TE B</MenuItem>
                      <MenuItem value="BE A">BE A</MenuItem>
                      <MenuItem value="BE B">BE B</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Year</InputLabel>
                    <Select
                      value={selectedYear}
                      label="Year"
                      onChange={(e) => setSelectedYear(e.target.value)}
                    >
                      {years.map(year => (
                        <MenuItem key={year} value={year}>{year}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Division</InputLabel>
                    <Select
                      value={selectedDivision}
                      label="Division"
                      onChange={(e) => setSelectedDivision(e.target.value)}
                    >
                      {divisions.map(division => (
                        <MenuItem key={division} value={division}>{division}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : sessions.length === 0 ? (
            <Alert severity="info">
              No timetable data available. Please generate a timetable first.
            </Alert>
          ) : (
            <TableContainer component={Paper} sx={{ maxHeight: '70vh', overflow: 'auto' }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#1976d2', color: 'white' }}>
                      DAYS
                    </TableCell>
                    {timeSlots.map((slot, index) => (
                      <TableCell 
                        key={index}
                        sx={{ 
                          fontWeight: 'bold', 
                          textAlign: 'center',
                          backgroundColor: slot.isBreak ? '#ff9800' : '#1976d2',
                          color: 'white',
                          minWidth: '120px'
                        }}
                      >
                        {slot.isBreak ? (
                          'RECESS'
                        ) : (
                          <Box>
                            <Typography variant="body2">{slot.slot}</Typography>
                            <Typography variant="caption">{slot.time}</Typography>
                          </Box>
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {days.map((day) => (
                    <TableRow key={day}>
                      <TableCell 
                        sx={{ 
                          fontWeight: 'bold', 
                          backgroundColor: '#2196f3', 
                          color: 'white',
                          textAlign: 'center'
                        }}
                      >
                        {day}
                      </TableCell>
                      {timeSlots.map((slot, index) => {
                        if (slot.isBreak) {
                          return <React.Fragment key={`${day}-${index}`}>{renderSessionCell(undefined, true)}</React.Fragment>;
                        }
                        const session = getSessionForSlot(day, slot.time);
                        return (
                          <React.Fragment key={`${day}-${index}`}>
                            {renderSessionCell(session)}
                          </React.Fragment>
                        );
                      })}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Statistics */}
          {sessions.length > 0 && (
            <Box sx={{ mt: 3, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>Statistics</Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2">Total Sessions: <strong>{sessions.length}</strong></Typography>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2">
                    Teachers: <strong>{new Set(sessions.map(s => s.teacher_name)).size}</strong>
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2">
                    Subjects: <strong>{new Set(sessions.map(s => s.subject_name)).size}</strong>
                  </Typography>
                </Grid>
                <Grid size={{ xs: 6, sm: 3 }}>
                  <Typography variant="body2">
                    Years: <strong>{new Set(sessions.map(s => s.year_division.split(' ')[0])).size}</strong>
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default TabularTimetableView;
