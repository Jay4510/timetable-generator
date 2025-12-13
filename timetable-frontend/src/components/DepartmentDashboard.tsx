import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
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
  IconButton,
  Alert,
  Tabs,
  Tab,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  School,
  Add,
  Edit,
  Delete,
  Visibility,
  Schedule,
  People,
  Settings
} from '@mui/icons-material';

interface Department {
  id: number;
  name: string;
  code: string;
  incharge_name: string;
  incharge_email: string;
  years: Year[];
}

interface Year {
  id: number;
  name: string;
  divisions: Division[];
}

interface Division {
  id: number;
  name: string;
  num_batches: number;
  is_active: boolean;
}

const DepartmentDashboard: React.FC = () => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<Department | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Dialog states
  const [addDivisionDialog, setAddDivisionDialog] = useState(false);
  const [newDivision, setNewDivision] = useState({ 
    year_id: '', 
    name: '', 
    num_batches: 3 
  });

  useEffect(() => {
    fetchDepartments();
  }, []);

  const fetchDepartments = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/departments/');
      if (response.ok) {
        const data = await response.json();
        setDepartments(data);
        if (data.length > 0 && !selectedDepartment) {
          setSelectedDepartment(data[0]);
        }
      } else {
        setError('Failed to load departments');
      }
    } catch (error) {
      console.error('Error fetching departments:', error);
      setError('Failed to load departments');
    }
    setLoading(false);
  };

  const handleAddDivision = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/manage-divisions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'add',
          year_id: newDivision.year_id,
          division_name: newDivision.name,
          num_batches: newDivision.num_batches
        })
      });

      if (response.ok) {
        setAddDivisionDialog(false);
        setNewDivision({ year_id: '', name: '', num_batches: 3 });
        fetchDepartments();
      } else {
        setError('Failed to add division');
      }
    } catch (error) {
      console.error('Error adding division:', error);
      setError('Failed to add division');
    }
  };

  const handleToggleDivision = async (yearId: number, divisionName: string, isActive: boolean) => {
    try {
      const response = await fetch('http://localhost:8000/api/manage-divisions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: isActive ? 'remove' : 'add',
          year_id: yearId,
          division_name: divisionName
        })
      });

      if (response.ok) {
        fetchDepartments();
      } else {
        setError('Failed to update division');
      }
    } catch (error) {
      console.error('Error updating division:', error);
      setError('Failed to update division');
    }
  };

  const generateDepartmentTimetable = async () => {
    if (!selectedDepartment) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/generate-timetable/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          department_code: selectedDepartment.code,
          use_division_specific: true
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Timetable generated successfully! ${result.total_sessions} sessions created.`);
      } else {
        setError('Failed to generate timetable');
      }
    } catch (error) {
      console.error('Error generating timetable:', error);
      setError('Failed to generate timetable');
    }
    setLoading(false);
  };

  const TabPanel = ({ children, value, index }: any) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  if (loading && departments.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading departments...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1400, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <School color="primary" />
        Department Timetable Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Department Selection */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Select Department
              </Typography>
              {departments.map((dept) => (
                <Button
                  key={dept.id}
                  fullWidth
                  variant={selectedDepartment?.id === dept.id ? 'contained' : 'outlined'}
                  onClick={() => setSelectedDepartment(dept)}
                  sx={{ mb: 1, justifyContent: 'flex-start' }}
                >
                  <Box textAlign="left">
                    <Typography variant="body2" fontWeight="bold">
                      {dept.code}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {dept.name}
                    </Typography>
                  </Box>
                </Button>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Department Details */}
        <Grid item xs={12} md={9}>
          {selectedDepartment && (
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                  <Typography variant="h5">
                    {selectedDepartment.name} ({selectedDepartment.code})
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<Schedule />}
                    onClick={generateDepartmentTimetable}
                    disabled={loading}
                  >
                    Generate Timetable
                  </Button>
                </Box>

                <Typography variant="body2" color="text.secondary" paragraph>
                  Incharge: {selectedDepartment.incharge_name || 'Not assigned'} 
                  {selectedDepartment.incharge_email && ` (${selectedDepartment.incharge_email})`}
                </Typography>

                <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
                  <Tab label="Division Management" />
                  <Tab label="Timetable View" />
                  <Tab label="Teacher Preferences" />
                </Tabs>

                {/* Division Management Tab */}
                <TabPanel value={tabValue} index={0}>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6">Manage Divisions</Typography>
                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => setAddDivisionDialog(true)}
                    >
                      Add Division
                    </Button>
                  </Box>

                  {selectedDepartment.years.map((year) => (
                    <Card key={year.id} variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {selectedDepartment.code} {year.name}
                        </Typography>
                        
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Division</TableCell>
                                <TableCell>Batches</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Actions</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {year.divisions.map((division) => (
                                <TableRow key={division.id}>
                                  <TableCell>
                                    <Typography fontWeight="bold">
                                      {selectedDepartment.code} {year.name} {division.name}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>{division.num_batches}</TableCell>
                                  <TableCell>
                                    <Chip
                                      label={division.is_active ? 'Active' : 'Inactive'}
                                      color={division.is_active ? 'success' : 'default'}
                                      size="small"
                                    />
                                  </TableCell>
                                  <TableCell>
                                    <FormControlLabel
                                      control={
                                        <Switch
                                          checked={division.is_active}
                                          onChange={() => handleToggleDivision(year.id, division.name, division.is_active)}
                                        />
                                      }
                                      label="Active"
                                    />
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  ))}
                </TabPanel>

                {/* Timetable View Tab */}
                <TabPanel value={tabValue} index={1}>
                  <Typography variant="h6" gutterBottom>
                    Department Timetables
                  </Typography>
                  <Alert severity="info">
                    Select a specific division to view its timetable. Each division has its own optimized schedule.
                  </Alert>
                  
                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    {selectedDepartment.years.map((year) =>
                      year.divisions
                        .filter(div => div.is_active)
                        .map((division) => (
                          <Grid item xs={12} sm={6} md={4} key={`${year.id}-${division.id}`}>
                            <Card variant="outlined">
                              <CardContent>
                                <Typography variant="h6">
                                  {selectedDepartment.code} {year.name} {division.name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {division.num_batches} Batches
                                </Typography>
                                <Button
                                  fullWidth
                                  variant="outlined"
                                  startIcon={<Visibility />}
                                  sx={{ mt: 2 }}
                                  onClick={() => {
                                    // Navigate to division-specific timetable
                                    const divisionKey = `${selectedDepartment.code}_${year.name}_${division.name}`;
                                    window.open(`/timetable?division=${divisionKey}`, '_blank');
                                  }}
                                >
                                  View Timetable
                                </Button>
                              </CardContent>
                            </Card>
                          </Grid>
                        ))
                    )}
                  </Grid>
                </TabPanel>

                {/* Teacher Preferences Tab */}
                <TabPanel value={tabValue} index={2}>
                  <Typography variant="h6" gutterBottom>
                    Teacher Preferences & Proficiency
                  </Typography>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Configure teacher preferences for first/second half scheduling and subject proficiencies.
                  </Alert>
                  <Button
                    variant="contained"
                    startIcon={<People />}
                    onClick={() => {
                      // Navigate to enhanced proficiency wizard
                      window.open('/proficiency-wizard', '_blank');
                    }}
                  >
                    Manage Teacher Preferences
                  </Button>
                </TabPanel>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Add Division Dialog */}
      <Dialog open={addDivisionDialog} onClose={() => setAddDivisionDialog(false)}>
        <DialogTitle>Add New Division</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Year</InputLabel>
            <Select
              value={newDivision.year_id}
              onChange={(e) => setNewDivision({ ...newDivision, year_id: e.target.value as string })}
              displayEmpty
            >
              <MenuItem value="">
                <em>Select a year</em>
              </MenuItem>
              {selectedDepartment?.years.map((year) => (
                <MenuItem key={year.id} value={year.id.toString()}>
                  {selectedDepartment.code} {year.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Division Name"
            value={newDivision.name || ''}
            onChange={(e) => setNewDivision({ ...newDivision, name: e.target.value.toUpperCase() })}
            sx={{ mt: 2 }}
            placeholder="A, B, C, etc."
          />
          
          <TextField
            fullWidth
            type="number"
            label="Number of Batches"
            value={newDivision.num_batches || 3}
            onChange={(e) => setNewDivision({ ...newDivision, num_batches: parseInt(e.target.value) || 3 })}
            sx={{ mt: 2 }}
            inputProps={{ min: 1, max: 5 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDivisionDialog(false)}>Cancel</Button>
          <Button onClick={handleAddDivision} variant="contained">Add Division</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DepartmentDashboard;
