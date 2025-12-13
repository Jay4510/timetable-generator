import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Grid,
  Alert
} from '@mui/material';

interface AddEditFormsProps {
  open: boolean;
  onClose: () => void;
  item: any;
  onSave: (data: any) => void;
  loading?: boolean;
}

const AddEditForms: React.FC<AddEditFormsProps> = ({ open, onClose, item, onSave, loading }) => {
  const [formData, setFormData] = useState<any>({});
  const [errors, setErrors] = useState<any>({});

  useEffect(() => {
    if (item) {
      setFormData({ ...item });
    } else {
      setFormData({});
    }
    setErrors({});
  }, [item]);

  const handleChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev: any) => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors: any = {};
    
    if (item?.type === 'teacher') {
      if (!formData.name?.trim()) newErrors.name = 'Name is required';
      if (!formData.department?.trim()) newErrors.department = 'Department is required';
    } else if (item?.type === 'subject') {
      if (!formData.name?.trim()) newErrors.name = 'Subject name is required';
      if (!formData.code?.trim()) newErrors.code = 'Subject code is required';
      if (!formData.year_name?.trim()) newErrors.year_name = 'Year is required';
      if (!formData.division_name?.trim()) newErrors.division_name = 'Division is required';
    } else if (item?.type === 'room') {
      if (!formData.name?.trim()) newErrors.name = 'Room name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (validateForm()) {
      onSave(formData);
    }
  };

  const renderTeacherForm = () => (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Teacher Name"
          value={formData.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          error={!!errors.name}
          helperText={errors.name}
          required
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Email"
          type="email"
          value={formData.email || ''}
          onChange={(e) => handleChange('email', e.target.value)}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <FormControl fullWidth required error={!!errors.department}>
          <InputLabel>Department</InputLabel>
          <Select
            value={formData.department || ''}
            onChange={(e) => handleChange('department', e.target.value)}
          >
            <MenuItem value="Computer Science">Computer Science</MenuItem>
            <MenuItem value="Information Technology">Information Technology</MenuItem>
            <MenuItem value="Electronics">Electronics</MenuItem>
            <MenuItem value="Mechanical">Mechanical</MenuItem>
            <MenuItem value="Civil">Civil</MenuItem>
            <MenuItem value="Mathematics">Mathematics</MenuItem>
            <MenuItem value="Physics">Physics</MenuItem>
            <MenuItem value="Chemistry">Chemistry</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Max Sessions per Week"
          type="number"
          value={formData.max_sessions_per_week || 14}
          onChange={(e) => handleChange('max_sessions_per_week', parseInt(e.target.value))}
          inputProps={{ min: 1, max: 30 }}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Experience (Years)"
          type="number"
          value={formData.experience_years || 0}
          onChange={(e) => handleChange('experience_years', parseInt(e.target.value))}
          inputProps={{ min: 0, max: 50 }}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Specialization"
          value={formData.specialization || ''}
          onChange={(e) => handleChange('specialization', e.target.value)}
        />
      </Grid>
      <Grid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.status === 'active'}
              onChange={(e) => handleChange('status', e.target.checked ? 'active' : 'inactive')}
            />
          }
          label="Active Status"
        />
      </Grid>
    </Grid>
  );

  const renderSubjectForm = () => (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Subject Name"
          value={formData.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          error={!!errors.name}
          helperText={errors.name}
          required
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Subject Code"
          value={formData.code || ''}
          onChange={(e) => handleChange('code', e.target.value)}
          error={!!errors.code}
          helperText={errors.code}
          required
        />
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <FormControl fullWidth required error={!!errors.year_name}>
          <InputLabel>Year</InputLabel>
          <Select
            value={formData.year_name || ''}
            onChange={(e) => handleChange('year_name', e.target.value)}
          >
            <MenuItem value="FE">First Year (FE)</MenuItem>
            <MenuItem value="SE">Second Year (SE)</MenuItem>
            <MenuItem value="TE">Third Year (TE)</MenuItem>
            <MenuItem value="BE">Final Year (BE)</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <FormControl fullWidth required error={!!errors.division_name}>
          <InputLabel>Division</InputLabel>
          <Select
            value={formData.division_name || ''}
            onChange={(e) => handleChange('division_name', e.target.value)}
          >
            <MenuItem value="A">Division A</MenuItem>
            <MenuItem value="B">Division B</MenuItem>
            <MenuItem value="C">Division C</MenuItem>
            <MenuItem value="D">Division D</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <TextField
          fullWidth
          label="Sessions per Week"
          type="number"
          value={formData.sessions_per_week || 3}
          onChange={(e) => handleChange('sessions_per_week', parseInt(e.target.value))}
          inputProps={{ min: 1, max: 10 }}
        />
      </Grid>
      <Grid size={{ xs: 12 }}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.requires_lab || false}
              onChange={(e) => handleChange('requires_lab', e.target.checked)}
            />
          }
          label="Requires Lab"
        />
      </Grid>
    </Grid>
  );

  const renderRoomForm = () => (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Room Name"
          value={formData.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          error={!!errors.name}
          helperText={errors.name}
          required
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Capacity"
          type="number"
          value={formData.capacity || 60}
          onChange={(e) => handleChange('capacity', parseInt(e.target.value))}
          inputProps={{ min: 1, max: 200 }}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <TextField
          fullWidth
          label="Location/Floor"
          value={formData.location || ''}
          onChange={(e) => handleChange('location', e.target.value)}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <FormControl fullWidth>
          <InputLabel>Building</InputLabel>
          <Select
            value={formData.building || ''}
            onChange={(e) => handleChange('building', e.target.value)}
          >
            <MenuItem value="Main Building">Main Building</MenuItem>
            <MenuItem value="Lab Building">Lab Building</MenuItem>
            <MenuItem value="New Block">New Block</MenuItem>
            <MenuItem value="Admin Block">Admin Block</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.is_lab || false}
              onChange={(e) => handleChange('is_lab', e.target.checked)}
            />
          }
          label="Is Laboratory"
        />
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.is_available !== false}
              onChange={(e) => handleChange('is_available', e.target.checked)}
            />
          }
          label="Available for Scheduling"
        />
      </Grid>
    </Grid>
  );

  const getTitle = () => {
    if (!item) return 'Add Item';
    const action = item.id ? 'Edit' : 'Add';
    const type = item.type?.charAt(0).toUpperCase() + item.type?.slice(1);
    return `${action} ${type}`;
  };

  const renderForm = () => {
    switch (item?.type) {
      case 'teacher':
        return renderTeacherForm();
      case 'subject':
        return renderSubjectForm();
      case 'room':
        return renderRoomForm();
      default:
        return <Alert severity="error">Unknown form type</Alert>;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{getTitle()}</DialogTitle>
      <DialogContent>
        {renderForm()}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" disabled={loading}>
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddEditForms;
