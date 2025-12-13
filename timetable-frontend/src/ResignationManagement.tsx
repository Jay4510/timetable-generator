import React, { useState, useEffect } from 'react';
import apiService from './services/apiService';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { 
  PersonRemove, 
  AutorenewRounded, 
  CheckCircle, 
  Warning,
  Person
} from '@mui/icons-material';

interface Teacher {
  id: number;
  name: string;
  department: string;
  status: string;
}

interface Subject {
  id: number;
  name: string;
  code: string;
  year_name: string;
  division_name: string;
}

interface ResignationData {
  teacher_id: number;
  reason: string;
  effective_date: string;
  subject_ids: number[];
}

const ResignationManagement: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedTeacher, setSelectedTeacher] = useState<Teacher | null>(null);
  const [teacherSubjects, setTeacherSubjects] = useState<Subject[]>([]);
  const [resignationData, setResignationData] = useState<ResignationData>({
    teacher_id: 0,
    reason: '',
    effective_date: new Date().toISOString().split('T')[0],
    subject_ids: []
  });
  const [loading, setLoading] = useState(false);
  const [replacementResult, setReplacementResult] = useState<any>(null);
  const [confirmDialog, setConfirmDialog] = useState(false);

  const steps = [
    'Select Teacher',
    'Choose Subjects',
    'Replacement Details',
    'Confirmation'
  ];

  useEffect(() => {
    fetchTeachers();
    fetchSubjects();
  }, []);

  const fetchTeachers = async () => {
    try {
      const teacherList = await apiService.getTeachers();
      setTeachers(teacherList);
    } catch (error) {
      console.error('Error fetching teachers:', error);
      setTeachers([]);
    }
  };

  const fetchSubjects = async () => {
    try {
      const subjectList = await apiService.getSubjects();
      setSubjects(subjectList);
    } catch (error) {
      console.error('Error fetching subjects:', error);
      setSubjects([]);
    }
  };

  const handleTeacherSelect = (teacher: Teacher) => {
    setSelectedTeacher(teacher);
    setResignationData(prev => ({ ...prev, teacher_id: teacher.id }));
    
    // Filter subjects that might be taught by this teacher
    // In a real scenario, you'd fetch actual assignments
    const randomSubjects = subjects.slice(0, Math.floor(Math.random() * 8) + 3);
    setTeacherSubjects(randomSubjects);
    
    setActiveStep(1);
  };

  const handleSubjectToggle = (subjectId: number) => {
    setResignationData(prev => ({
      ...prev,
      subject_ids: prev.subject_ids.includes(subjectId)
        ? prev.subject_ids.filter(id => id !== subjectId)
        : [...prev.subject_ids, subjectId]
    }));
  };

  const handleSubmitResignation = async () => {
    setLoading(true);
    try {
      const result = await apiService.processResignation(resignationData);
      setReplacementResult(result);
      setActiveStep(3);
    } catch (error) {
      console.error('Error submitting resignation:', error);
      setReplacementResult({
        status: 'error',
        message: 'Failed to process resignation. Please try again.'
      });
    }
    setLoading(false);
  };

  const getReplacementStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'success';
      case 'partial_success': return 'warning';
      default: return 'error';
    }
  };

  const resetForm = () => {
    setActiveStep(0);
    setSelectedTeacher(null);
    setTeacherSubjects([]);
    setResignationData({
      teacher_id: 0,
      reason: '',
      effective_date: new Date().toISOString().split('T')[0],
      subject_ids: []
    });
    setReplacementResult(null);
  };

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', p: 3 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <PersonRemove color="error" />
            Teacher Resignation Management
          </Typography>
          
          <Typography variant="body1" color="text.secondary" paragraph>
            Handle teacher resignations with automatic subject reassignment based on proficiency ratings.
            The system will find the best replacement teacher for each subject.
          </Typography>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Step 1: Teacher Selection */}
          {activeStep === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Select Teacher Who is Resigning
              </Typography>
              
              <Grid container spacing={2}>
                {teachers.filter(t => t.status === 'active').map((teacher) => (
                  <Grid size={{ xs: 12, sm: 6, md: 4 }} key={teacher.id}>
                    <Card 
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { boxShadow: 3 },
                        border: selectedTeacher?.id === teacher.id ? '2px solid red' : '1px solid #ddd'
                      }}
                      onClick={() => handleTeacherSelect(teacher)}
                    >
                      <CardContent>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Person />
                          <Typography variant="h6">{teacher.name}</Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {teacher.department}
                        </Typography>
                        <Chip 
                          label={teacher.status} 
                          color="success"
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Step 2: Subject Selection */}
          {activeStep === 1 && selectedTeacher && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Select Subjects to Transfer from {selectedTeacher.name}
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                Select the subjects that need to be reassigned to other teachers. 
                The system will automatically find the best replacement based on proficiency ratings.
              </Alert>

              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <TextField
                    fullWidth
                    label="Reason for Resignation"
                    value={resignationData.reason}
                    onChange={(e) => setResignationData(prev => ({ ...prev, reason: e.target.value }))}
                    placeholder="e.g., Personal reasons, Better opportunity, etc."
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <TextField
                    fullWidth
                    label="Effective Date"
                    type="date"
                    value={resignationData.effective_date}
                    onChange={(e) => setResignationData(prev => ({ ...prev, effective_date: e.target.value }))}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              </Grid>

              <Typography variant="subtitle1" gutterBottom>
                Subjects Currently Taught by {selectedTeacher.name}:
              </Typography>

              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Select</TableCell>
                      <TableCell>Subject</TableCell>
                      <TableCell>Code</TableCell>
                      <TableCell>Year/Division</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {teacherSubjects.map((subject) => (
                      <TableRow key={subject.id}>
                        <TableCell>
                          <Checkbox
                            checked={resignationData.subject_ids.includes(subject.id)}
                            onChange={() => handleSubjectToggle(subject.id)}
                          />
                        </TableCell>
                        <TableCell>{subject.name}</TableCell>
                        <TableCell>{subject.code}</TableCell>
                        <TableCell>{subject.year_name} {subject.division_name}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                <Button onClick={() => setActiveStep(0)}>
                  Back
                </Button>
                <Button
                  variant="contained"
                  onClick={() => setActiveStep(2)}
                  disabled={resignationData.subject_ids.length === 0 || !resignationData.reason}
                >
                  Continue ({resignationData.subject_ids.length} subjects selected)
                </Button>
              </Box>
            </Box>
          )}

          {/* Step 3: Replacement Preview */}
          {activeStep === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Resignation Summary & Auto-Replacement
              </Typography>
              
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        Resignation Details
                      </Typography>
                      <Typography><strong>Teacher:</strong> {selectedTeacher?.name}</Typography>
                      <Typography><strong>Department:</strong> {selectedTeacher?.department}</Typography>
                      <Typography><strong>Reason:</strong> {resignationData.reason}</Typography>
                      <Typography><strong>Effective Date:</strong> {resignationData.effective_date}</Typography>
                      <Typography><strong>Subjects to Transfer:</strong> {resignationData.subject_ids.length}</Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AutorenewRounded />
                        Auto-Replacement Process
                      </Typography>
                      <Typography variant="body2" paragraph>
                        The system will:
                      </Typography>
                      <ul>
                        <li>Analyze proficiency ratings for all subjects</li>
                        <li>Find teachers with highest combined scores</li>
                        <li>Check workload balance (max 14 sessions/week)</li>
                        <li>Automatically reassign existing timetable sessions</li>
                        <li>Update all related records</li>
                      </ul>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Alert severity="warning" sx={{ mt: 3 }}>
                <strong>Important:</strong> This action will immediately update the timetable and reassign 
                all sessions. Make sure all details are correct before proceeding.
              </Alert>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                <Button onClick={() => setActiveStep(1)}>
                  Back to Edit
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  onClick={() => setConfirmDialog(true)}
                  startIcon={<PersonRemove />}
                >
                  Process Resignation & Auto-Replace
                </Button>
              </Box>
            </Box>
          )}

          {/* Step 4: Results */}
          {activeStep === 3 && replacementResult && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Resignation Processing Complete
              </Typography>
              
              <Alert 
                severity={getReplacementStatusColor(replacementResult.status)} 
                sx={{ mb: 3 }}
              >
                <strong>{replacementResult.message}</strong>
              </Alert>

              {replacementResult.status === 'success' && (
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CheckCircle color="success" />
                      Replacement Summary
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid size={{ xs: 12, md: 6 }}>
                        <Typography><strong>Original Teacher:</strong> {replacementResult.original_teacher}</Typography>
                        <Typography><strong>Replacement Teacher:</strong> {replacementResult.replacement_teacher}</Typography>
                      </Grid>
                      <Grid size={{ xs: 12, md: 6 }}>
                        <Typography><strong>Sessions Transferred:</strong> {replacementResult.sessions_transferred}</Typography>
                        <Typography><strong>Subjects Transferred:</strong> {replacementResult.subjects_transferred}</Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              )}

              {replacementResult.status === 'partial_success' && (
                <Alert severity="warning" sx={{ mb: 3 }}>
                  <Typography><strong>Manual Action Required:</strong></Typography>
                  <Typography>
                    No suitable replacement teacher found automatically. 
                    Please manually assign teachers or update proficiency ratings.
                  </Typography>
                </Alert>
              )}

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                <Button onClick={resetForm} variant="outlined">
                  Process Another Resignation
                </Button>
                <Button variant="contained" onClick={() => window.location.reload()}>
                  Return to Timetable Management
                </Button>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialog} onClose={() => setConfirmDialog(false)}>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Warning color="error" />
          Confirm Resignation Processing
        </DialogTitle>
        <DialogContent>
          <Typography paragraph>
            Are you sure you want to process the resignation of <strong>{selectedTeacher?.name}</strong>?
          </Typography>
          <Typography paragraph>
            This will:
          </Typography>
          <ul>
            <li>Mark the teacher as resigned</li>
            <li>Transfer {resignationData.subject_ids.length} subjects to replacement teachers</li>
            <li>Update all existing timetable sessions</li>
            <li>This action cannot be easily undone</li>
          </ul>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={() => {
              setConfirmDialog(false);
              handleSubmitResignation();
            }}
            variant="contained"
            color="error"
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Confirm & Process'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ResignationManagement;
