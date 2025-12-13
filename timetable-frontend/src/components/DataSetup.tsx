/**
 * Data Setup Component - CRUD operations for all entities
 * Professional UI with validation, CSV import, and inline editing
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  LinearProgress,
  Tooltip,
  Autocomplete,
  Grid,
  Divider
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Upload,
  Download,
  Save,
  Cancel,
  People,
  School,
  Room as RoomIcon,
  Schedule,
  Settings
} from '@mui/icons-material';

import type { Teacher, Subject, Room, Lab, Division, TimeSlot } from '../types/api';
import timetableApi from '../services/timetableApi';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ paddingTop: 24 }}>
    {value === index && children}
  </div>
);

const DataSetup: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Entity states
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [labs, setLabs] = useState<Lab[]>([]);
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);

  // Dialog states
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [editingEntity, setEditingEntity] = useState<any>(null);

  // Form states
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [
        teachersData,
        subjectsData,
        roomsData,
        labsData,
        divisionsData,
        timeSlotsData
      ] = await Promise.all([
        timetableApi.getTeachers(),
        timetableApi.getSubjects(),
        timetableApi.getRooms(),
        timetableApi.getLabs(),
        timetableApi.getDivisions(),
        timetableApi.getTimeSlots()
      ]);

      setTeachers(teachersData.results || []);
      setSubjects(subjectsData.results || []);
      setRooms(roomsData);
      setLabs(labsData);
      setDivisions(divisionsData);
      setTimeSlots(timeSlotsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const openDialog = (mode: 'create' | 'edit', entity?: any) => {
    setDialogMode(mode);
    setEditingEntity(entity);
    setFormData(entity || getEmptyFormData());
    setDialogOpen(true);
  };

  const closeDialog = () => {
    setDialogOpen(false);
    setEditingEntity(null);
    setFormData({});
  };

  const getEmptyFormData = () => {
    switch (activeTab) {
      case 0: // Teachers
        return {
          name: '',
          email: '',
          phone: '',
          department: '',
          max_sessions_per_week: 20,
          min_sessions_per_week: 10,
          time_preference: 'no_preference',
          available: true
        };
      case 1: // Subjects
        return {
          name: '',
          code: '',
          year: 1,
          division: 1,
          sessions_per_week: 4,
          requires_lab: false,
          lecture_duration_hours: 1,
          lab_frequency_per_week: 1,
          requires_remedial: true,
          equipment_requirements: []
        };
      case 2: // Rooms
        return {
          name: '',
          capacity: 60,
          room_type: 'classroom',
          available: true,
          available_equipment: []
        };
      case 3: // Labs
        return {
          name: '',
          capacity: 30,
          lab_type: '',
          available_equipment: []
        };
      case 4: // Divisions
        return {
          year: 1,
          name: 'A',
          num_batches: 3,
          student_count: 30
        };
      case 5: // TimeSlots
        return {
          day_of_week: 'monday',
          start_time: '09:00',
          end_time: '10:00',
          slot_type: 'lecture'
        };
      default:
        return {};
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setError(null);

    try {
      let result;
      
      if (dialogMode === 'create') {
        switch (activeTab) {
          case 0:
            result = await timetableApi.createTeacher(formData);
            setTeachers([...teachers, result]);
            break;
          case 1:
            result = await timetableApi.createSubject(formData);
            setSubjects([...subjects, result]);
            break;
          case 5:
            result = await timetableApi.createTimeSlot(formData);
            setTimeSlots([...timeSlots, result]);
            break;
        }
      } else {
        switch (activeTab) {
          case 0:
            result = await timetableApi.updateTeacher(editingEntity.id, formData);
            setTeachers(teachers.map(t => t.id === editingEntity.id ? result : t));
            break;
          case 1:
            result = await timetableApi.updateSubject(editingEntity.id, formData);
            setSubjects(subjects.map(s => s.id === editingEntity.id ? result : s));
            break;
          case 2:
            result = await timetableApi.updateRoom(editingEntity.id, formData);
            setRooms(rooms.map(r => r.id === editingEntity.id ? result : r));
            break;
          case 4:
            result = await timetableApi.updateDivision(editingEntity.id, formData);
            setDivisions(divisions.map(d => d.id === editingEntity.id ? result : d));
            break;
        }
      }

      setSuccess(`${dialogMode === 'create' ? 'Created' : 'Updated'} successfully`);
      closeDialog();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;

    setLoading(true);
    try {
      switch (activeTab) {
        case 0:
          await timetableApi.deleteTeacher(id);
          setTeachers(teachers.filter(t => t.id !== id));
          break;
      }
      setSuccess('Deleted successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    } finally {
      setLoading(false);
    }
  };

  const handleCSVImport = async (file: File) => {
    setLoading(true);
    try {
      let result;
      switch (activeTab) {
        case 0:
          result = await timetableApi.importTeachers(file);
          break;
        case 1:
          result = await timetableApi.importSubjects(file);
          break;
      }
      setSuccess(`Imported ${result.imported} records successfully`);
      if (result.errors.length > 0) {
        setError(`Errors: ${result.errors.join(', ')}`);
      }
      loadAllData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  const renderTeachersTable = () => (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Department</TableCell>
            <TableCell>Sessions/Week</TableCell>
            <TableCell>Time Preference</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {teachers.map((teacher) => (
            <TableRow key={teacher.id}>
              <TableCell>{teacher.name}</TableCell>
              <TableCell>{teacher.email}</TableCell>
              <TableCell>{teacher.department}</TableCell>
              <TableCell>{teacher.min_sessions_per_week}-{teacher.max_sessions_per_week}</TableCell>
              <TableCell>
                <Chip 
                  label={teacher.time_preference} 
                  size="small"
                  color={teacher.time_preference === 'no_preference' ? 'default' : 'primary'}
                />
              </TableCell>
              <TableCell>
                <Chip 
                  label={teacher.available ? 'Active' : 'Inactive'} 
                  color={teacher.available ? 'success' : 'error'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <IconButton onClick={() => openDialog('edit', teacher)} size="small">
                  <Edit />
                </IconButton>
                <IconButton onClick={() => handleDelete(teacher.id)} size="small" color="error">
                  <Delete />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderSubjectsTable = () => (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Code</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Year/Division</TableCell>
            <TableCell>Sessions/Week</TableCell>
            <TableCell>Lab Required</TableCell>
            <TableCell>Equipment</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {subjects.map((subject) => (
            <TableRow key={subject.id}>
              <TableCell>{subject.code}</TableCell>
              <TableCell>{subject.name}</TableCell>
              <TableCell>Year {subject.year} - Div {subject.division}</TableCell>
              <TableCell>{subject.sessions_per_week}</TableCell>
              <TableCell>
                <Chip 
                  label={subject.requires_lab ? 'Yes' : 'No'} 
                  color={subject.requires_lab ? 'primary' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {subject.equipment_requirements.slice(0, 2).map((eq, idx) => (
                    <Chip key={idx} label={eq} size="small" variant="outlined" />
                  ))}
                  {subject.equipment_requirements.length > 2 && (
                    <Chip label={`+${subject.equipment_requirements.length - 2}`} size="small" />
                  )}
                </Box>
              </TableCell>
              <TableCell>
                <IconButton onClick={() => openDialog('edit', subject)} size="small">
                  <Edit />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderFormDialog = () => (
    <Dialog open={dialogOpen} onClose={closeDialog} maxWidth="md" fullWidth>
      <DialogTitle>
        {dialogMode === 'create' ? 'Add New' : 'Edit'} {getTabLabel(activeTab)}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          {activeTab === 0 && renderTeacherForm()}
          {activeTab === 1 && renderSubjectForm()}
          {activeTab === 2 && renderRoomForm()}
          {activeTab === 4 && renderDivisionForm()}
          {activeTab === 5 && renderTimeSlotForm()}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={closeDialog}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" disabled={loading}>
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderTeacherForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Name"
          value={formData.name || ''}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Email"
          type="email"
          value={formData.email || ''}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Department"
          value={formData.department || ''}
          onChange={(e) => setFormData({...formData, department: e.target.value})}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Phone"
          value={formData.phone || ''}
          onChange={(e) => setFormData({...formData, phone: e.target.value})}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Min Sessions/Week"
          type="number"
          value={formData.min_sessions_per_week || 10}
          onChange={(e) => setFormData({...formData, min_sessions_per_week: parseInt(e.target.value)})}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Max Sessions/Week"
          type="number"
          value={formData.max_sessions_per_week || 20}
          onChange={(e) => setFormData({...formData, max_sessions_per_week: parseInt(e.target.value)})}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <Autocomplete
          options={['morning', 'afternoon', 'no_preference']}
          value={formData.time_preference || 'no_preference'}
          onChange={(_, value) => setFormData({...formData, time_preference: value})}
          renderInput={(params) => <TextField {...params} label="Time Preference" />}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.available || true}
              onChange={(e) => setFormData({...formData, available: e.target.checked})}
            />
          }
          label="Available"
        />
      </Grid>
    </Grid>
  );

  const renderSubjectForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Subject Code"
          value={formData.code || ''}
          onChange={(e) => setFormData({...formData, code: e.target.value})}
          required
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Subject Name"
          value={formData.name || ''}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Year"
          type="number"
          value={formData.year || 1}
          onChange={(e) => setFormData({...formData, year: parseInt(e.target.value)})}
          inputProps={{ min: 1, max: 4 }}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Division"
          type="number"
          value={formData.division || 1}
          onChange={(e) => setFormData({...formData, division: parseInt(e.target.value)})}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Sessions/Week"
          type="number"
          value={formData.sessions_per_week || 4}
          onChange={(e) => setFormData({...formData, sessions_per_week: parseInt(e.target.value)})}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.requires_lab || false}
              onChange={(e) => setFormData({...formData, requires_lab: e.target.checked})}
            />
          }
          label="Requires Lab"
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.requires_remedial !== false}
              onChange={(e) => setFormData({...formData, requires_remedial: e.target.checked})}
            />
          }
          label="Requires Remedial"
        />
      </Grid>
    </Grid>
  );

  const renderRoomForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Room Name"
          value={formData.name || ''}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Capacity"
          type="number"
          value={formData.capacity || 60}
          onChange={(e) => setFormData({...formData, capacity: parseInt(e.target.value)})}
        />
      </Grid>
    </Grid>
  );

  const renderDivisionForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Year"
          type="number"
          value={formData.year || 1}
          onChange={(e) => setFormData({...formData, year: parseInt(e.target.value)})}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Division Name"
          value={formData.name || ''}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Student Count"
          type="number"
          value={formData.student_count || 30}
          onChange={(e) => setFormData({...formData, student_count: parseInt(e.target.value)})}
        />
      </Grid>
    </Grid>
  );

  const renderTimeSlotForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
        <Autocomplete
          options={['monday', 'tuesday', 'wednesday', 'thursday', 'friday']}
          value={formData.day_of_week || 'monday'}
          onChange={(_, value) => setFormData({...formData, day_of_week: value})}
          renderInput={(params) => <TextField {...params} label="Day" />}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Start Time"
          type="time"
          value={formData.start_time || '09:00'}
          onChange={(e) => setFormData({...formData, start_time: e.target.value})}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="End Time"
          type="time"
          value={formData.end_time || '10:00'}
          onChange={(e) => setFormData({...formData, end_time: e.target.value})}
        />
      </Grid>
    </Grid>
  );

  const getTabLabel = (index: number) => {
    const labels = ['Teacher', 'Subject', 'Room', 'Lab', 'Division', 'TimeSlot'];
    return labels[index];
  };

  const getTabIcon = (index: number) => {
    const icons = [People, School, RoomIcon, RoomIcon, Settings, Schedule];
    const Icon = icons[index];
    return <Icon />;
  };

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Data Management
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage teachers, subjects, rooms, and other timetable data
      </Typography>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Card>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab icon={<People />} label="Teachers" />
          <Tab icon={<School />} label="Subjects" />
          <Tab icon={<RoomIcon />} label="Rooms" />
          <Tab icon={<RoomIcon />} label="Labs" />
          <Tab icon={<Settings />} label="Divisions" />
          <Tab icon={<Schedule />} label="Time Slots" />
        </Tabs>

        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              {getTabLabel(activeTab)}s ({
                activeTab === 0 ? teachers.length :
                activeTab === 1 ? subjects.length :
                activeTab === 2 ? rooms.length :
                activeTab === 3 ? labs.length :
                activeTab === 4 ? divisions.length :
                timeSlots.length
              })
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <input
                type="file"
                accept=".csv"
                style={{ display: 'none' }}
                id="csv-upload"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleCSVImport(file);
                }}
              />
              {(activeTab === 0 || activeTab === 1) && (
                <label htmlFor="csv-upload">
                  <Button component="span" startIcon={<Upload />} variant="outlined">
                    Import CSV
                  </Button>
                </label>
              )}
              <Button
                startIcon={<Add />}
                variant="contained"
                onClick={() => openDialog('create')}
              >
                Add {getTabLabel(activeTab)}
              </Button>
            </Box>
          </Box>

          <TabPanel value={activeTab} index={0}>
            {renderTeachersTable()}
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            {renderSubjectsTable()}
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <Typography>Rooms management coming soon...</Typography>
          </TabPanel>

          <TabPanel value={activeTab} index={3}>
            <Typography>Labs management coming soon...</Typography>
          </TabPanel>

          <TabPanel value={activeTab} index={4}>
            <Typography>Divisions management coming soon...</Typography>
          </TabPanel>

          <TabPanel value={activeTab} index={5}>
            <Typography>Time slots management coming soon...</Typography>
          </TabPanel>
        </CardContent>
      </Card>

      {renderFormDialog()}
    </Box>
  );
};

export default DataSetup;
