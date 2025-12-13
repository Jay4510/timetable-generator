import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  MenuItem,
  Card,
  CardContent,
  Chip,
  Button,
  Alert,
  Paper,
  Divider,
} from '@mui/material';
import {
  Computer,
  Memory,
  Build,
  Construction,
  ElectricalServices,
  Router,
  Science,
  MenuBook,
  BusinessCenter,
  Storage,
  Speed,
  CheckCircle,
  Devices,
  ArrowForward,
} from '@mui/icons-material';

interface WelcomeSetupProps {
  config: any;
  updateConfig: (updates: any) => void;
  onNext: () => void;
}

const WelcomeSetup: React.FC<WelcomeSetupProps> = ({ config, updateConfig, onNext }) => {
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  const departmentIcons: { [key: string]: React.ReactElement } = {
    IT: <Computer />,
    CS: <Memory />,
    ME: <Build />,
    CE: <Construction />,
    EE: <ElectricalServices />,
    EC: <Router />,
    IC: <Science />,
    HS: <MenuBook />,
    MBA: <BusinessCenter />,
    MCA: <Storage />,
  };

  const dmceDepartments = [
    { value: 'IT', label: 'Information Technology' },
    { value: 'CS', label: 'Computer Science' },
    { value: 'ME', label: 'Mechanical Engineering' },
    { value: 'CE', label: 'Civil Engineering' },
    { value: 'EE', label: 'Electrical Engineering' },
    { value: 'EC', label: 'Electronics & Communication' },
    { value: 'IC', label: 'Instrumentation & Control' },
    { value: 'HS', label: 'Humanities & Science' },
    { value: 'MBA', label: 'Master of Business Administration' },
    { value: 'MCA', label: 'Master of Computer Applications' }
  ];

  const academicYears = ['2025-26', '2024-25', '2023-24', '2022-23'];

  const yearOptions = [
    { value: 'FE', label: 'First Year (FE)', color: '#10b981' },
    { value: 'SE', label: 'Second Year (SE)', color: '#3b82f6' },
    { value: 'TE', label: 'Third Year (TE)', color: '#f59e0b' },
    { value: 'BE', label: 'Final Year (BE)', color: '#ef4444' }
  ];

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};

    if (!config.department) {
      newErrors.department = 'Please select your department';
    }

    if (!config.ttInchargeName?.trim()) {
      newErrors.ttInchargeName = 'Please enter TT Incharge name';
    }

    if (!config.contactEmail?.trim()) {
      newErrors.contactEmail = 'Please enter contact email';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(config.contactEmail)) {
      newErrors.contactEmail = 'Please enter a valid email address';
    }

    if (!config.yearsManaged || config.yearsManaged.length === 0) {
      newErrors.yearsManaged = 'Please select at least one year to manage';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateForm()) {
      onNext();
    }
  };

  const handleYearToggle = (year: string) => {
    const currentYears = config.yearsManaged || [];
    const newYears = currentYears.includes(year)
      ? currentYears.filter((y: string) => y !== year)
      : [...currentYears, year];
    
    updateConfig({ yearsManaged: newYears });
  };

  const selectedDepartment = dmceDepartments.find(dept => dept.value === config.department);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Welcome Section */}
      <Paper
        elevation={0}
        sx={{
          background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
          color: 'white',
          p: 4,
          mb: 4,
          borderRadius: 3,
        }}
      >
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
          Welcome to Smart Timetable Generator
        </Typography>
        <Typography variant="h6" sx={{ mb: 3, opacity: 0.95, fontWeight: 400 }}>
          Create optimized timetables for your department with our intelligent scheduling system
        </Typography>
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Speed sx={{ fontSize: 28 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              Fast & Efficient
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircle sx={{ fontSize: 28 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              Conflict-Free Scheduling
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Devices sx={{ fontSize: 28 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              Professional Interface
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Department Information */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
          Department Information
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
            Select Department <span style={{ color: '#ef4444' }}>*</span>
          </Typography>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
            gap: 2 
          }}>
            {dmceDepartments.map((dept) => (
              <Card
                key={dept.value}
                sx={{
                  cursor: 'pointer',
                  border: config.department === dept.value ? '2px solid #1e40af' : '1px solid #e2e8f0',
                  backgroundColor: config.department === dept.value ? '#eff6ff' : 'white',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    borderColor: '#3b82f6',
                    boxShadow: 3,
                    transform: 'translateY(-2px)',
                  },
                }}
                onClick={() => updateConfig({ department: dept.value })}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box
                      sx={{
                        color: config.department === dept.value ? '#1e40af' : '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      {departmentIcons[dept.value]}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600, mb: 0.5 }}>
                        {dept.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {dept.label}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
          {errors.department && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {errors.department}
            </Alert>
          )}
        </Box>

        <Box sx={{ maxWidth: 400 }}>
          <TextField
            select
            fullWidth
            label="Academic Year"
            value={config.academicYear}
            onChange={(e) => updateConfig({ academicYear: e.target.value })}
          >
            {academicYears.map((year) => (
              <MenuItem key={year} value={year}>
                {year}
              </MenuItem>
            ))}
          </TextField>
        </Box>
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* TT Incharge Details */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
          Timetable Incharge Details
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
            <TextField
              fullWidth
              required
              label="Full Name"
              placeholder="Enter your full name"
              value={config.ttInchargeName || ''}
              onChange={(e) => updateConfig({ ttInchargeName: e.target.value })}
              error={!!errors.ttInchargeName}
              helperText={errors.ttInchargeName}
            />

            <TextField
              fullWidth
              label="Designation"
              placeholder="e.g., Assistant Professor, HOD"
              value={config.designation || ''}
              onChange={(e) => updateConfig({ designation: e.target.value })}
            />
          </Box>

          <Box sx={{ maxWidth: { xs: '100%', md: '50%' } }}>
            <TextField
              fullWidth
              required
              type="email"
              label="Contact Email"
              placeholder="your.email@dmce.ac.in"
              value={config.contactEmail || ''}
              onChange={(e) => updateConfig({ contactEmail: e.target.value })}
              error={!!errors.contactEmail}
              helperText={errors.contactEmail}
            />
          </Box>
        </Box>
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* Years Managed */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 1, fontWeight: 600 }}>
          Years Managed <span style={{ color: '#ef4444' }}>*</span>
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Select the academic years your department handles
        </Typography>
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
          gap: 2 
        }}>
          {yearOptions.map((year) => (
            <Card
              key={year.value}
              sx={{
                cursor: 'pointer',
                border: config.yearsManaged?.includes(year.value) ? `2px solid ${year.color}` : '1px solid #e2e8f0',
                backgroundColor: config.yearsManaged?.includes(year.value) ? `${year.color}15` : 'white',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  borderColor: year.color,
                  boxShadow: 2,
                  transform: 'translateY(-2px)',
                },
              }}
              onClick={() => handleYearToggle(year.value)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: year.color }}>
                      {year.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {year.label}
                    </Typography>
                  </Box>
                  {config.yearsManaged?.includes(year.value) && (
                    <CheckCircle sx={{ color: year.color }} />
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
        {errors.yearsManaged && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {errors.yearsManaged}
          </Alert>
        )}
      </Box>

      {/* Summary Card */}
      {config.department && config.ttInchargeName && (
        <Paper elevation={2} sx={{ p: 3, mb: 4, backgroundColor: '#f8fafc', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
            Setup Summary
          </Typography>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' },
            gap: 2 
          }}>
            <Box>
              <Typography variant="body2" color="text.secondary">Department:</Typography>
              <Typography variant="body1" sx={{ fontWeight: 500, mt: 0.5 }}>
                {selectedDepartment?.label} ({config.department})
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">TT Incharge:</Typography>
              <Typography variant="body1" sx={{ fontWeight: 500, mt: 0.5 }}>
                {config.ttInchargeName}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">Academic Year:</Typography>
              <Typography variant="body1" sx={{ fontWeight: 500, mt: 0.5 }}>
                {config.academicYear}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">Years Managing:</Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                {config.yearsManaged?.map((year: string) => {
                  const yearInfo = yearOptions.find(y => y.value === year);
                  return (
                    <Chip
                      key={year}
                      label={year}
                      size="small"
                      sx={{
                        backgroundColor: yearInfo?.color,
                        color: 'white',
                        fontWeight: 500,
                      }}
                    />
                  );
                })}
              </Box>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Navigation */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 4, gap: 2, flexWrap: 'wrap' }}>
        <Alert severity="info" icon={false} sx={{ flex: 1, minWidth: 250 }}>
          All information can be modified later if needed
        </Alert>
        <Button
          variant="contained"
          size="large"
          endIcon={<ArrowForward />}
          onClick={handleNext}
          disabled={!config.department || !config.ttInchargeName}
          sx={{
            px: 4,
            py: 1.5,
            fontSize: '1rem',
            fontWeight: 600,
          }}
        >
          Get Started
        </Button>
      </Box>
    </Box>
  );
};

export default WelcomeSetup;
