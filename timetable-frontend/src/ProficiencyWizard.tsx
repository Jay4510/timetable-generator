import React, { useState, useEffect } from 'react';
import apiService from './services/apiService';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Slider,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Chip,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  TextField
} from '@mui/material';
import { CheckCircle, School, Person } from '@mui/icons-material';

interface Teacher {
  id: number;
  name: string;
  department: string;
  status: string;
}

interface TeacherPreferences {
  lecture_time_preference: 'morning' | 'afternoon' | 'no_preference';
  lab_time_preference: 'morning' | 'afternoon' | 'no_preference';
  cross_year_teaching: boolean;
  preferred_years: string[];
  max_cross_year_sessions: number;
}

interface Subject {
  id: number;
  name: string;
  code: string;
  year_name: string;
  division_name: string;
}

interface ProficiencyRating {
  teacher_id: number;
  subject_id: number;
  knowledge_rating: number;
  willingness_rating: number;
}

const ProficiencyWizard: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [proficiencies, setProficiencies] = useState<ProficiencyRating[]>([]);
  const [currentTeacher, setCurrentTeacher] = useState<Teacher | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitDialog, setSubmitDialog] = useState(false);
  const [completedTeachers, setCompletedTeachers] = useState<Set<number>>(new Set());
  const [teacherPreferences, setTeacherPreferences] = useState<{[key: number]: TeacherPreferences}>({});

  const steps = [
    'Select Teachers',
    'Input Proficiency Ratings',
    'Review & Submit'
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [teacherList, subjectList] = await Promise.all([
        apiService.getTeachers(),
        apiService.getSubjects()
      ]);

      setTeachers(teacherList);
      setSubjects(subjectList);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  const handleTeacherSelect = (teacher: Teacher) => {
    setCurrentTeacher(teacher);
    setActiveStep(1);
  };

  const handleTeacherComplete = () => {
    if (currentTeacher) {
      setCompletedTeachers(prev => new Set([...prev, currentTeacher.id]));
      setActiveStep(2); // Go to review step
    }
  };

  const handlePreferenceChange = (field: keyof TeacherPreferences, value: any) => {
    if (currentTeacher) {
      setTeacherPreferences(prev => ({
        ...prev,
        [currentTeacher.id]: {
          ...prev[currentTeacher.id],
          [field]: value
        }
      }));
    }
  };

  const handleProficiencyChange = (
    subjectId: number,
    type: 'knowledge' | 'willingness',
    value: number
  ) => {
    setProficiencies(prev => {
      const existing = prev.find(p => 
        p.teacher_id === currentTeacher?.id && p.subject_id === subjectId
      );

      if (existing) {
        return prev.map(p => 
          p.teacher_id === currentTeacher?.id && p.subject_id === subjectId
            ? { ...p, [type + '_rating']: value }
            : p
        );
      } else {
        return [...prev, {
          teacher_id: currentTeacher!.id,
          subject_id: subjectId,
          knowledge_rating: type === 'knowledge' ? value : 5,
          willingness_rating: type === 'willingness' ? value : 5
        }];
      }
    });
  };

  const getProficiencyForSubject = (subjectId: number) => {
    return proficiencies.find(p => 
      p.teacher_id === currentTeacher?.id && p.subject_id === subjectId
    );
  };

  const handleSubmitAll = async () => {
    setLoading(true);
    try {
      const submissionData = {
        proficiencies: Array.from(completedTeachers).map(teacherId => ({
          teacher_id: teacherId,
          lecture_time_preference: teacherPreferences[teacherId]?.lecture_time_preference || 'no_preference',
          lab_time_preference: teacherPreferences[teacherId]?.lab_time_preference || 'no_preference',
          cross_year_teaching: teacherPreferences[teacherId]?.cross_year_teaching || false,
          preferred_years: teacherPreferences[teacherId]?.preferred_years || [],
          max_cross_year_sessions: teacherPreferences[teacherId]?.max_cross_year_sessions || 6,
          subject_ratings: proficiencies.filter(p => p.teacher_id === teacherId)
        }))
      };

      console.log('Submitting enhanced proficiencies:', submissionData);
      
      const response = await apiService.submitProficiencies(submissionData);
      console.log('Submission response:', response);
      
      setSubmitDialog(true);
    } catch (error) {
      console.error('Error submitting proficiencies:', error);
    }
    setLoading(false);
  };

  const getCombinedScore = (knowledge: number, willingness: number) => {
    return (knowledge * 0.6 + willingness * 0.4).toFixed(1);
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'success';
    if (score >= 6) return 'warning';
    return 'error';
  };

  if (loading && teachers.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <School color="primary" />
            Teacher Proficiency Input Wizard
          </Typography>
          
          <Typography variant="body1" color="text.secondary" paragraph>
            Input knowledge and willingness ratings for each teacher across all subjects.
            This data will be used to optimize subject assignments in the timetable.
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
                Select Teacher to Input Proficiency Ratings
              </Typography>
              
              <Grid container spacing={2}>
                {teachers.map((teacher) => (
                  <Grid size={{ xs: 12, sm: 6, md: 4 }} key={teacher.id}>
                    <Card 
                      sx={{ 
                        cursor: 'pointer',
                        border: completedTeachers.has(teacher.id) ? '2px solid green' : '1px solid #ddd',
                        '&:hover': { boxShadow: 3 }
                      }}
                      onClick={() => handleTeacherSelect(teacher)}
                    >
                      <CardContent>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Person />
                          <Typography variant="h6">{teacher.name}</Typography>
                          {completedTeachers.has(teacher.id) && (
                            <CheckCircle color="success" />
                          )}
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {teacher.department}
                        </Typography>
                        <Chip 
                          label={teacher.status} 
                          color={teacher.status === 'active' ? 'success' : 'default'}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">
                  Completed: {completedTeachers.size} / {teachers.length} teachers
                </Typography>
                <Button
                  variant="contained"
                  onClick={() => setActiveStep(2)}
                  disabled={completedTeachers.size === 0}
                >
                  Review & Submit ({completedTeachers.size} teachers)
                </Button>
              </Box>
            </Box>
          )}

          {/* Step 2: Proficiency Input */}
          {activeStep === 1 && currentTeacher && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Proficiency Ratings for {currentTeacher.name}
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                Rate each subject on a scale of 1-10 for both Knowledge and Willingness to teach.
                Combined Score = (Knowledge × 60%) + (Willingness × 40%)
              </Alert>

              {/* Teacher Preferences Section */}
              <Card sx={{ mb: 3, p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Teaching Preferences for {currentTeacher.name}
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <FormControl fullWidth>
                      <InputLabel>Lecture Time Preference</InputLabel>
                      <Select
                        value={teacherPreferences[currentTeacher.id]?.lecture_time_preference || 'no_preference'}
                        onChange={(e) => handlePreferenceChange('lecture_time_preference', e.target.value)}
                        label="Lecture Time Preference"
                      >
                        <MenuItem value="no_preference">No Preference</MenuItem>
                        <MenuItem value="morning">Morning (Before 1 PM)</MenuItem>
                        <MenuItem value="afternoon">Afternoon (After 1 PM)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid size={{ xs: 12, md: 6 }}>
                    <FormControl fullWidth>
                      <InputLabel>Lab Time Preference</InputLabel>
                      <Select
                        value={teacherPreferences[currentTeacher.id]?.lab_time_preference || 'no_preference'}
                        onChange={(e) => handlePreferenceChange('lab_time_preference', e.target.value)}
                        label="Lab Time Preference"
                      >
                        <MenuItem value="no_preference">No Preference</MenuItem>
                        <MenuItem value="morning">Morning (Before 1 PM)</MenuItem>
                        <MenuItem value="afternoon">Afternoon (After 1 PM)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid size={{ xs: 12, md: 6 }}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={teacherPreferences[currentTeacher.id]?.cross_year_teaching || false}
                          onChange={(e) => handlePreferenceChange('cross_year_teaching', e.target.checked)}
                        />
                      }
                      label="Allow Cross-Year Teaching"
                    />
                  </Grid>
                  
                  <Grid size={{ xs: 12, md: 6 }}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Max Cross-Year Sessions"
                      value={teacherPreferences[currentTeacher.id]?.max_cross_year_sessions || 6}
                      onChange={(e) => handlePreferenceChange('max_cross_year_sessions', parseInt(e.target.value))}
                      inputProps={{ min: 0, max: 20 }}
                    />
                  </Grid>
                </Grid>
              </Card>

              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Subject</TableCell>
                      <TableCell>Year/Division</TableCell>
                      <TableCell>Knowledge (1-10)</TableCell>
                      <TableCell>Willingness (1-10)</TableCell>
                      <TableCell>Combined Score</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {subjects.map((subject) => {
                      const proficiency = getProficiencyForSubject(subject.id);
                      const knowledge = proficiency?.knowledge_rating || 5;
                      const willingness = proficiency?.willingness_rating || 5;
                      const combined = parseFloat(getCombinedScore(knowledge, willingness));

                      return (
                        <TableRow key={subject.id}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="bold">
                              {subject.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {subject.code}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {subject.year_name} {subject.division_name}
                          </TableCell>
                          <TableCell sx={{ width: 200 }}>
                            <Slider
                              value={knowledge}
                              onChange={(_, value) => 
                                handleProficiencyChange(subject.id, 'knowledge', value as number)
                              }
                              min={1}
                              max={10}
                              step={1}
                              marks
                              valueLabelDisplay="on"
                            />
                          </TableCell>
                          <TableCell sx={{ width: 200 }}>
                            <Slider
                              value={willingness}
                              onChange={(_, value) => 
                                handleProficiencyChange(subject.id, 'willingness', value as number)
                              }
                              min={1}
                              max={10}
                              step={1}
                              marks
                              valueLabelDisplay="on"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={combined}
                              color={getScoreColor(combined)}
                              variant="outlined"
                            />
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                <Button onClick={() => setActiveStep(0)}>
                  Back to Teachers
                </Button>
                <Button
                  variant="contained"
                  onClick={handleTeacherComplete}
                >
                  Complete {currentTeacher.name}
                </Button>
              </Box>
            </Box>
          )}

          {/* Step 3: Review & Submit */}
          {activeStep === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Review Proficiency Data
              </Typography>
              
              <Alert severity="success" sx={{ mb: 3 }}>
                Proficiency data collected for {completedTeachers.size} teachers across {proficiencies.length} subject assignments.
              </Alert>

              <Typography variant="body1" paragraph>
                Summary:
              </Typography>
              <ul>
                <li>Teachers completed: {completedTeachers.size}</li>
                <li>Total proficiency ratings: {proficiencies.length}</li>
                <li>Average ratings will be used for optimal teacher-subject matching</li>
                <li>High proficiency teachers will be prioritized for their strong subjects</li>
              </ul>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                <Button onClick={() => setActiveStep(0)}>
                  Back to Edit
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSubmitAll}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={20} /> : 'Submit All Proficiency Data'}
                </Button>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Success Dialog */}
      <Dialog open={submitDialog} onClose={() => setSubmitDialog(false)}>
        <DialogTitle>Proficiency Data Submitted Successfully!</DialogTitle>
        <DialogContent>
          <Typography>
            All teacher proficiency ratings have been saved. The timetable generation 
            algorithm will now use this data to create optimized assignments.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSubmitDialog(false)} variant="contained">
            Continue to Timetable Generation
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProficiencyWizard;
