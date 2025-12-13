import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Tabs,
  Tab,
  Alert,
  Chip,
  Card,
  CardContent
} from '@mui/material';

interface Teacher {
  id: number;
  name: string;
  email: string;
  max_sessions_per_week: number;
}

interface Subject {
  id: number;
  name: string;
  year: number;
  division: number;
  sessions_per_week: number;
  is_lab: boolean;
}

interface Room {
  id: number;
  name: string;
  capacity: number;
  room_type: string;
}

interface TimeSlot {
  id: number;
  day: string;
  start_time: string;
  end_time: string;
}

interface Year {
  id: number;
  name: string;
}

interface Division {
  id: number;
  name: string;
  year: number;
  batches: number;
}

const DataManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [timeslots, setTimeslots] = useState<TimeSlot[]>([]);
  const [years, setYears] = useState<Year[]>([]);
  const [divisions, setDivisions] = useState<Division[]>([]);
  
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [formData, setFormData] = useState<any>({});
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      const [teachersRes, subjectsRes, roomsRes, timeslotsRes, yearsRes, divisionsRes] = await Promise.all([
        axios.get('http://localhost:8000/api/teachers/'),
        axios.get('http://localhost:8000/api/subjects/'),
        axios.get('http://localhost:8000/api/rooms/'),
        axios.get('http://localhost:8000/api/timeslots/'),
        axios.get('http://localhost:8000/api/years/'),
        axios.get('http://localhost:8000/api/divisions/'),
      ]);
      
      setTeachers(teachersRes.data.results || []);
      setSubjects(subjectsRes.data.results || []);
      setRooms(roomsRes.data.results || []);
      setTimeslots(timeslotsRes.data.results || []);
      setYears(yearsRes.data.results || []);
      setDivisions(divisionsRes.data.results || []);
    } catch (err) {
      setError('Failed to fetch data');
    }
  };

  const handleAdd = (type: string) => {
    setDialogType(type);
    setFormData({});
    setOpenDialog(true);
  };

  const handleSave = async () => {
    try {
      let endpoint = '';
      switch (dialogType) {
        case 'teacher':
          endpoint = '/api/teachers/';
          break;
        case 'subject':
          endpoint = '/api/subjects/';
          break;
        case 'room':
          endpoint = '/api/rooms/';
          break;
        case 'timeslot':
          endpoint = '/api/timeslots/';
          break;
        case 'year':
          endpoint = '/api/years/';
          break;
        case 'division':
          endpoint = '/api/divisions/';
          break;
      }

      await axios.post(`http://localhost:8000${endpoint}`, formData);
      setSuccess(`${dialogType} added successfully!`);
      setOpenDialog(false);
      fetchAllData();
    } catch (err) {
      setError(`Failed to add ${dialogType}`);
    }
  };

  const renderTeachersTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Teachers</Typography>
        <Button variant="contained" onClick={() => handleAdd('teacher')}>
          Add Teacher
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Max Sessions/Week</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {teachers.map((teacher) => (
              <TableRow key={teacher.id}>
                <TableCell>{teacher.name}</TableCell>
                <TableCell>{teacher.email}</TableCell>
                <TableCell>{teacher.max_sessions_per_week}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderSubjectsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Subjects</Typography>
        <Button variant="contained" onClick={() => handleAdd('subject')}>
          Add Subject
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Year</TableCell>
              <TableCell>Division</TableCell>
              <TableCell>Sessions/Week</TableCell>
              <TableCell>Type</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {subjects.map((subject) => (
              <TableRow key={subject.id}>
                <TableCell>{subject.name}</TableCell>
                <TableCell>{subject.year}</TableCell>
                <TableCell>{subject.division}</TableCell>
                <TableCell>{subject.sessions_per_week}</TableCell>
                <TableCell>
                  <Chip 
                    label={subject.is_lab ? 'Lab' : 'Theory'} 
                    color={subject.is_lab ? 'secondary' : 'primary'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderRoomsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Rooms & Labs</Typography>
        <Button variant="contained" onClick={() => handleAdd('room')}>
          Add Room
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Capacity</TableCell>
              <TableCell>Type</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rooms.map((room) => (
              <TableRow key={room.id}>
                <TableCell>{room.name}</TableCell>
                <TableCell>{room.capacity}</TableCell>
                <TableCell>
                  <Chip 
                    label={room.room_type} 
                    color={room.room_type === 'lab' ? 'secondary' : 'primary'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderDialog = () => (
    <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Add {dialogType}</DialogTitle>
      <DialogContent>
        {dialogType === 'teacher' && (
          <Box>
            <TextField
              fullWidth
              label="Name"
              margin="normal"
              value={formData.name || ''}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
            <TextField
              fullWidth
              label="Email"
              margin="normal"
              value={formData.email || ''}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
            <TextField
              fullWidth
              label="Max Sessions Per Week"
              type="number"
              margin="normal"
              value={formData.max_sessions_per_week || 14}
              onChange={(e) => setFormData({...formData, max_sessions_per_week: parseInt(e.target.value)})}
            />
          </Box>
        )}
        
        {dialogType === 'subject' && (
          <Box>
            <TextField
              fullWidth
              label="Subject Name"
              margin="normal"
              value={formData.name || ''}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Year</InputLabel>
              <Select
                value={formData.year || ''}
                onChange={(e) => setFormData({...formData, year: e.target.value})}
              >
                {years.map((year) => (
                  <MenuItem key={year.id} value={year.id}>{year.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth margin="normal">
              <InputLabel>Division</InputLabel>
              <Select
                value={formData.division || ''}
                onChange={(e) => setFormData({...formData, division: e.target.value})}
              >
                {divisions.map((division) => (
                  <MenuItem key={division.id} value={division.id}>{division.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Sessions Per Week"
              type="number"
              margin="normal"
              value={formData.sessions_per_week || 3}
              onChange={(e) => setFormData({...formData, sessions_per_week: parseInt(e.target.value)})}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Type</InputLabel>
              <Select
                value={formData.is_lab ? 'true' : 'false'}
                onChange={(e) => setFormData({...formData, is_lab: e.target.value === 'true'})}
              >
                <MenuItem value="false">Theory</MenuItem>
                <MenuItem value="true">Lab</MenuItem>
              </Select>
            </FormControl>
          </Box>
        )}

        {dialogType === 'room' && (
          <Box>
            <TextField
              fullWidth
              label="Room Name"
              margin="normal"
              value={formData.name || ''}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
            <TextField
              fullWidth
              label="Capacity"
              type="number"
              margin="normal"
              value={formData.capacity || 60}
              onChange={(e) => setFormData({...formData, capacity: parseInt(e.target.value)})}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Room Type</InputLabel>
              <Select
                value={formData.room_type || 'class'}
                onChange={(e) => setFormData({...formData, room_type: e.target.value})}
              >
                <MenuItem value="class">Classroom</MenuItem>
                <MenuItem value="lab">Laboratory</MenuItem>
              </Select>
            </FormControl>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
        <Button onClick={handleSave} variant="contained">Save</Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          College Data Management
        </Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <Box sx={{ display: 'flex', gap: 3, mb: 3, flexWrap: 'wrap' }}>
          <Box sx={{ flex: '1 1 200px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6">Teachers</Typography>
                <Typography variant="h4" color="primary">{teachers.length}</Typography>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 200px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6">Subjects</Typography>
                <Typography variant="h4" color="primary">{subjects.length}</Typography>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 200px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6">Rooms</Typography>
                <Typography variant="h4" color="primary">{rooms.length}</Typography>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 200px' }}>
            <Card>
              <CardContent>
                <Typography variant="h6">Time Slots</Typography>
                <Typography variant="h4" color="primary">{timeslots.length}</Typography>
              </CardContent>
            </Card>
          </Box>
        </Box>

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab label="Teachers" />
            <Tab label="Subjects" />
            <Tab label="Rooms & Labs" />
          </Tabs>
        </Box>

        <Box sx={{ mt: 3 }}>
          {activeTab === 0 && renderTeachersTab()}
          {activeTab === 1 && renderSubjectsTab()}
          {activeTab === 2 && renderRoomsTab()}
        </Box>

        {renderDialog()}
      </Box>
    </Container>
  );
};

export default DataManagement;
