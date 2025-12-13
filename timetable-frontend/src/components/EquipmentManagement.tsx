import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Button,
  Chip,
  IconButton,
  Alert,
  Autocomplete,
  Divider,
  List,
  ListItem
} from '@mui/material';
import { Add, Save, Computer, Science, School } from '@mui/icons-material';
import apiService from '../services/apiService';

interface Equipment {
  id: string;
  name: string;
  type: 'projector' | 'computer' | 'lab_equipment' | 'audio_visual' | 'other';
}

interface Room {
  id: number;
  name: string;
  capacity: number;
  available_equipment: string[];
}

interface Subject {
  id: number;
  name: string;
  code: string;
  equipment_requirements: string[];
}

const EquipmentManagement: React.FC = () => {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [availableEquipment, setAvailableEquipment] = useState<string[]>([
    'Projector', 'Computer', 'Whiteboard', 'Audio System', 'Microscope',
    'Lab Equipment', 'Smart Board', 'Document Camera', 'Speakers'
  ]);
  const [newEquipment, setNewEquipment] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [roomsData, subjectsData] = await Promise.all([
        apiService.getRooms(),
        apiService.getSubjects()
      ]);
      setRooms(roomsData);
      setSubjects(subjectsData);
    } catch (err) {
      setError('Failed to load data');
    }
  };

  const addEquipment = () => {
    if (newEquipment && !availableEquipment.includes(newEquipment)) {
      setAvailableEquipment([...availableEquipment, newEquipment]);
      setNewEquipment('');
    }
  };

  const updateRoomEquipment = (roomId: number, equipment: string[]) => {
    setRooms(rooms.map(room => 
      room.id === roomId 
        ? { ...room, available_equipment: equipment }
        : room
    ));
  };

  const updateSubjectRequirements = (subjectId: number, requirements: string[]) => {
    setSubjects(subjects.map(subject => 
      subject.id === subjectId 
        ? { ...subject, equipment_requirements: requirements }
        : subject
    ));
  };

  const saveChanges = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Save room equipment updates
      for (const room of rooms) {
        await apiService.updateRoom(room.id, {
          available_equipment: room.available_equipment
        });
      }
      
      // Save subject requirement updates
      for (const subject of subjects) {
        await apiService.updateSubject(subject.id, {
          equipment_requirements: subject.equipment_requirements
        });
      }
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Computer />
        Equipment Management
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Manage equipment availability in rooms and requirements for subjects
      </Typography>

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Equipment configuration saved successfully!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        
        {/* Equipment Library */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Equipment Library
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  size="small"
                  placeholder="Add new equipment"
                  value={newEquipment}
                  onChange={(e) => setNewEquipment(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addEquipment()}
                />
                <IconButton onClick={addEquipment} color="primary">
                  <Add />
                </IconButton>
              </Box>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {availableEquipment.map((equipment, index) => (
                  <Chip
                    key={index}
                    label={equipment}
                    size="small"
                    onDelete={() => {
                      setAvailableEquipment(availableEquipment.filter((_, i) => i !== index));
                    }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Room Equipment */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <School />
                Room Equipment
              </Typography>
              
              <List dense>
                {rooms.map((room) => (
                  <ListItem key={room.id} sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', mb: 1 }}>
                      <Typography variant="subtitle2">
                        {room.name} (Capacity: {room.capacity})
                      </Typography>
                    </Box>
                    
                    <Autocomplete
                      multiple
                      size="small"
                      options={availableEquipment}
                      value={room.available_equipment || []}
                      onChange={(_, newValue) => updateRoomEquipment(room.id, newValue)}
                      renderTags={(value, getTagProps) =>
                        value.map((option, index) => (
                          <Chip
                            variant="outlined"
                            label={option}
                            size="small"
                            {...getTagProps({ index })}
                          />
                        ))
                      }
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          placeholder="Select equipment"
                        />
                      )}
                    />
                    
                    {room !== rooms[rooms.length - 1] && <Divider sx={{ mt: 2 }} />}
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Subject Requirements */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Science />
                Subject Requirements
              </Typography>
              
              <List dense>
                {subjects.slice(0, 10).map((subject) => (
                  <ListItem key={subject.id} sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', mb: 1 }}>
                      <Typography variant="subtitle2">
                        {subject.code} - {subject.name}
                      </Typography>
                    </Box>
                    
                    <Autocomplete
                      multiple
                      size="small"
                      options={availableEquipment}
                      value={subject.equipment_requirements || []}
                      onChange={(_, newValue) => updateSubjectRequirements(subject.id, newValue)}
                      renderTags={(value, getTagProps) =>
                        value.map((option, index) => (
                          <Chip
                            variant="outlined"
                            label={option}
                            size="small"
                            color="secondary"
                            {...getTagProps({ index })}
                          />
                        ))
                      }
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          placeholder="Required equipment"
                        />
                      )}
                    />
                    
                    {subject !== subjects.slice(0, 10)[subjects.slice(0, 10).length - 1] && <Divider sx={{ mt: 2 }} />}
                  </ListItem>
                ))}
              </List>
              
              {subjects.length > 10 && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
                  Showing first 10 subjects. Use API for bulk updates.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Save Button */}
        <Grid size={{ xs: 12 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<Save />}
              onClick={saveChanges}
              disabled={loading}
              sx={{ minWidth: 200 }}
            >
              {loading ? 'Saving...' : 'Save Equipment Configuration'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EquipmentManagement;
