import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add,
  Delete,
  Edit,
  School,
  Person,
  Room,
  Schedule,
  DeleteSweep,
  Upload,
  Download,
  Refresh
} from '@mui/icons-material';
import apiService from './services/apiService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DataManagementCenter: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [subjects, setSubjects] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [timeslots, setTimeslots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [resetDialog, setResetDialog] = useState(false);
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [currentItem, setCurrentItem] = useState<any>(null);
  const [resetOptions, setResetOptions] = useState({
    teachers: false,
    subjects: false,
    rooms: false,
    timeslots: false,
    timetable: false,
    proficiencies: false
  });

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [teacherData, subjectData, roomData] = await Promise.all([
        apiService.getTeachers(),
        apiService.getSubjects(),
        fetch('http://localhost:8000/api/rooms/').then(r => r.json()).catch(() => []),
      ]);
      
      setTeachers(teacherData);
      setSubjects(subjectData);
      setRooms(Array.isArray(roomData) ? roomData : roomData.results || []);
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleAdd = (type: string) => {
    const newItem = {
      type,
      id: null,
      name: '',
      email: '',
      department: 'Information Technology',
      max_sessions_per_week: 14
    };
    setCurrentItem(newItem);
    setAddDialog(true);
  };

  const handleEdit = (item: any, type: string) => {
    setCurrentItem({ ...item, type });
    setEditDialog(true);
  };

  const handleDelete = async (id: number, type: string) => {
    if (window.confirm(`Are you sure you want to delete this ${type}?`)) {
      try {
        const response = await fetch(`http://localhost:8000/api/${type}s/${id}/`, { 
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        if (response.ok) {
          alert(`${type} deleted successfully`);
          loadAllData();
        } else {
          alert(`Error deleting ${type}`);
        }
      } catch (error) {
        console.error(`Error deleting ${type}:`, error);
        alert(`Error deleting ${type}: ${error}`);
      }
    }
  };

  const handleSave = async () => {
    try {
      const { type, id, ...data } = currentItem;
      const url = id 
        ? `http://localhost:8000/api/${type}s/${id}/`
        : `http://localhost:8000/api/${type}s/`;
      
      const method = id ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        alert(`${type} ${id ? 'updated' : 'created'} successfully`);
        setAddDialog(false);
        setEditDialog(false);
        loadAllData();
      } else {
        alert(`Error ${id ? 'updating' : 'creating'} ${type}`);
      }
    } catch (error) {
      console.error('Error saving:', error);
      alert(`Error saving: ${error}`);
    }
  };

  const handleResetData = async () => {
    setLoading(true);
    try {
      const promises = [];
      if (resetOptions.teachers) promises.push(fetch('http://localhost:8000/api/reset-teachers/', { method: 'POST' }));
      if (resetOptions.subjects) promises.push(fetch('http://localhost:8000/api/reset-subjects/', { method: 'POST' }));
      if (resetOptions.rooms) promises.push(fetch('http://localhost:8000/api/reset-rooms/', { method: 'POST' }));
      if (resetOptions.timetable) promises.push(fetch('http://localhost:8000/api/reset-timetable/', { method: 'POST' }));
      
      await Promise.all(promises);
      loadAllData();
      setResetDialog(false);
    } catch (error) {
      console.error('Error resetting data:', error);
    }
    setLoading(false);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <School />
            Data Management Center
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage all timetable data: professors, subjects, classrooms, and system settings
          </Typography>
          
          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteSweep />}
              onClick={() => setResetDialog(true)}
            >
              Reset Data
            </Button>
            <Button variant="outlined" startIcon={<Upload />}>
              Import Data
            </Button>
            <Button variant="outlined" startIcon={<Download />}>
              Export Data
            </Button>
            <Button variant="outlined" startIcon={<Refresh />} onClick={loadAllData}>
              Refresh
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={currentTab} onChange={handleTabChange}>
            <Tab label={`Teachers (${teachers.length})`} icon={<Person />} />
            <Tab label={`Subjects (${subjects.length})`} icon={<School />} />
            <Tab label={`Rooms (${rooms.length})`} icon={<Room />} />
            <Tab label="Time Slots" icon={<Schedule />} />
          </Tabs>
        </Box>

        {/* Teachers Tab */}
        <TabPanel value={currentTab} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Teachers Management</Typography>
            <Button variant="contained" startIcon={<Add />} onClick={() => handleAdd('teacher')}>
              Add Teacher
            </Button>
          </Box>
          
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Max Sessions/Week</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {teachers.map((teacher) => (
                  <TableRow key={teacher.id}>
                    <TableCell>{teacher.name}</TableCell>
                    <TableCell>{teacher.department}</TableCell>
                    <TableCell>{teacher.max_sessions_per_week || 14}</TableCell>
                    <TableCell>
                      <Chip 
                        label={teacher.status || 'active'} 
                        color={teacher.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleEdit(teacher, 'teacher')}>
                        <Edit />
                      </IconButton>
                      <IconButton onClick={() => handleDelete(teacher.id, 'teacher')} color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Subjects Tab */}
        <TabPanel value={currentTab} index={1}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Subjects Management</Typography>
            <Button variant="contained" startIcon={<Add />} onClick={() => handleAdd('subject')}>
              Add Subject
            </Button>
          </Box>
          
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Subject Name</TableCell>
                  <TableCell>Code</TableCell>
                  <TableCell>Year/Division</TableCell>
                  <TableCell>Sessions/Week</TableCell>
                  <TableCell>Lab Required</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {subjects.map((subject) => (
                  <TableRow key={subject.id}>
                    <TableCell>{subject.name}</TableCell>
                    <TableCell>{subject.code}</TableCell>
                    <TableCell>{subject.year_name} {subject.division_name}</TableCell>
                    <TableCell>{subject.sessions_per_week}</TableCell>
                    <TableCell>
                      <Chip 
                        label={subject.requires_lab ? 'Yes' : 'No'} 
                        color={subject.requires_lab ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleEdit(subject, 'subject')}>
                        <Edit />
                      </IconButton>
                      <IconButton onClick={() => handleDelete(subject.id, 'subject')} color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Rooms Tab */}
        <TabPanel value={currentTab} index={2}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Rooms & Labs Management</Typography>
            <Button variant="contained" startIcon={<Add />} onClick={() => handleAdd('room')}>
              Add Room
            </Button>
          </Box>
          
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Room Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Capacity</TableCell>
                  <TableCell>Available</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rooms.map((room) => (
                  <TableRow key={room.id}>
                    <TableCell>{room.name}</TableCell>
                    <TableCell>
                      <Chip 
                        label={room.is_lab ? 'Lab' : 'Classroom'} 
                        color={room.is_lab ? 'secondary' : 'primary'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{room.capacity || 'N/A'}</TableCell>
                    <TableCell>
                      <Chip 
                        label={room.is_available ? 'Yes' : 'No'} 
                        color={room.is_available ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleEdit(room, 'room')}>
                        <Edit />
                      </IconButton>
                      <IconButton onClick={() => handleDelete(room.id, 'room')} color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Time Slots Tab */}
        <TabPanel value={currentTab} index={3}>
          <Typography variant="h6" gutterBottom>Time Slots Configuration</Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            Time slots are automatically generated based on your system configuration. 
            Go to Configuration Dashboard to modify college timings.
          </Alert>
          <Button variant="outlined" onClick={() => window.location.href = '#configuration'}>
            Configure Time Slots
          </Button>
        </TabPanel>
      </Card>

      {/* Add Dialog */}
      <Dialog open={addDialog} onClose={() => setAddDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New {currentItem?.type}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={currentItem?.name || ''}
            onChange={(e) => setCurrentItem(prev => ({ ...prev, name: e.target.value }))}
            margin="normal"
          />
          {currentItem?.type === 'teacher' && (
            <>
              <TextField
                fullWidth
                label="Email"
                value={currentItem?.email || ''}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, email: e.target.value }))}
                margin="normal"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Department</InputLabel>
                <Select
                  value={currentItem?.department || 'Information Technology'}
                  label="Department"
                  onChange={(e) => setCurrentItem(prev => ({ ...prev, department: e.target.value }))}
                >
                  <MenuItem value="Information Technology">Information Technology</MenuItem>
                  <MenuItem value="Computer Science">Computer Science</MenuItem>
                  <MenuItem value="Electronics">Electronics</MenuItem>
                  <MenuItem value="Mechanical">Mechanical</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Max Sessions Per Week"
                type="number"
                value={currentItem?.max_sessions_per_week || 14}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, max_sessions_per_week: parseInt(e.target.value) }))}
                margin="normal"
              />
            </>
          )}
          {currentItem?.type === 'subject' && (
            <>
              <TextField
                fullWidth
                label="Code"
                value={currentItem?.code || ''}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, code: e.target.value }))}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Credits"
                type="number"
                value={currentItem?.credits || 3}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, credits: parseInt(e.target.value) }))}
                margin="normal"
              />
            </>
          )}
          {currentItem?.type === 'room' && (
            <>
              <TextField
                fullWidth
                label="Capacity"
                type="number"
                value={currentItem?.capacity || 60}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, capacity: parseInt(e.target.value) }))}
                margin="normal"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Room Type</InputLabel>
                <Select
                  value={currentItem?.room_type || 'classroom'}
                  label="Room Type"
                  onChange={(e) => setCurrentItem(prev => ({ ...prev, room_type: e.target.value }))}
                >
                  <MenuItem value="classroom">Classroom</MenuItem>
                  <MenuItem value="lab">Laboratory</MenuItem>
                  <MenuItem value="auditorium">Auditorium</MenuItem>
                </Select>
              </FormControl>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialog(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit {currentItem?.type}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={currentItem?.name || ''}
            onChange={(e) => setCurrentItem(prev => ({ ...prev, name: e.target.value }))}
            margin="normal"
          />
          {currentItem?.type === 'teacher' && (
            <>
              <TextField
                fullWidth
                label="Email"
                value={currentItem?.email || ''}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, email: e.target.value }))}
                margin="normal"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Department</InputLabel>
                <Select
                  value={currentItem?.department || 'Information Technology'}
                  label="Department"
                  onChange={(e) => setCurrentItem(prev => ({ ...prev, department: e.target.value }))}
                >
                  <MenuItem value="Information Technology">Information Technology</MenuItem>
                  <MenuItem value="Computer Science">Computer Science</MenuItem>
                  <MenuItem value="Electronics">Electronics</MenuItem>
                  <MenuItem value="Mechanical">Mechanical</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Max Sessions Per Week"
                type="number"
                value={currentItem?.max_sessions_per_week || 14}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, max_sessions_per_week: parseInt(e.target.value) }))}
                margin="normal"
              />
            </>
          )}
          {currentItem?.type === 'subject' && (
            <>
              <TextField
                fullWidth
                label="Code"
                value={currentItem?.code || ''}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, code: e.target.value }))}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Credits"
                type="number"
                value={currentItem?.credits || 3}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, credits: parseInt(e.target.value) }))}
                margin="normal"
              />
            </>
          )}
          {currentItem?.type === 'room' && (
            <>
              <TextField
                fullWidth
                label="Capacity"
                type="number"
                value={currentItem?.capacity || 60}
                onChange={(e) => setCurrentItem(prev => ({ ...prev, capacity: parseInt(e.target.value) }))}
                margin="normal"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Room Type</InputLabel>
                <Select
                  value={currentItem?.room_type || 'classroom'}
                  label="Room Type"
                  onChange={(e) => setCurrentItem(prev => ({ ...prev, room_type: e.target.value }))}
                >
                  <MenuItem value="classroom">Classroom</MenuItem>
                  <MenuItem value="lab">Laboratory</MenuItem>
                  <MenuItem value="auditorium">Auditorium</MenuItem>
                </Select>
              </FormControl>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">Update</Button>
        </DialogActions>
      </Dialog>

      {/* Reset Dialog */}
      <Dialog open={resetDialog} onClose={() => setResetDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reset System Data</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This action will permanently delete selected data. This cannot be undone!
          </Alert>
          
          <Typography variant="subtitle1" gutterBottom>Select data to reset:</Typography>
          
          {Object.entries(resetOptions).map(([key, value]) => (
            <FormControlLabel
              key={key}
              control={
                <Switch
                  checked={value}
                  onChange={(e) => setResetOptions(prev => ({ ...prev, [key]: e.target.checked }))}
                />
              }
              label={key.charAt(0).toUpperCase() + key.slice(1)}
            />
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialog(false)}>Cancel</Button>
          <Button onClick={handleResetData} color="error" variant="contained">
            Reset Selected Data
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataManagementCenter;
