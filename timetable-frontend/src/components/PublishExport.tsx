/**
 * Publish & Export Component
 * Professional interface for approving, publishing, and exporting timetables
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Alert,
  LinearProgress,
  Chip,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Checkbox,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Publish,
  Download,
  PictureAsPdf,
  TableChart,
  DataObject,
  CheckCircle,
  Warning,
  Schedule,
  Assessment,
  Visibility,
  Save,
  History,
  Share
} from '@mui/icons-material';

import type { GenerationResult, ExportRequest, ExportResult, Session } from '../types/api';
import timetableApi from '../services/timetableApi';

interface PublishExportProps {
  generationResult?: GenerationResult;
}

const PublishExport: React.FC<PublishExportProps> = ({ generationResult }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Approval states
  const [activeStep, setActiveStep] = useState(0);
  const [approved, setApproved] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState('');

  // Export states
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [exportConfig, setExportConfig] = useState<ExportRequest>({
    format: 'pdf',
    scope: 'all',
    include_violations: false
  });
  const [exportResults, setExportResults] = useState<ExportResult[]>([]);

  // Sessions data
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionStats, setSessionStats] = useState({
    total: 0,
    byDivision: {} as Record<string, number>,
    byTeacher: {} as Record<string, number>
  });

  // Version history
  const [versions, setVersions] = useState<any[]>([]);

  const steps = [
    'Review Results',
    'Quality Check',
    'Approval',
    'Publish',
    'Export'
  ];

  useEffect(() => {
    if (generationResult) {
      loadSessionData();
      loadVersionHistory();
    }
  }, [generationResult]);

  const loadSessionData = async () => {
    if (!generationResult) return;

    setLoading(true);
    try {
      const sessionsData = await timetableApi.getSessions({
        generation_id: generationResult.id
      });
      setSessions(sessionsData);
      calculateSessionStats(sessionsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const loadVersionHistory = async () => {
    // Mock version history for now
    setVersions([
      {
        id: '1',
        version: 'v1.0',
        created_at: '2024-01-15T10:00:00Z',
        fitness_score: 85.2,
        violations: 12,
        status: 'published'
      },
      {
        id: '2',
        version: 'v1.1',
        created_at: '2024-01-20T14:30:00Z',
        fitness_score: 89.7,
        violations: 8,
        status: 'draft'
      }
    ]);
  };

  const calculateSessionStats = (sessionsData: Session[]) => {
    const stats = {
      total: sessionsData.length,
      byDivision: {} as Record<string, number>,
      byTeacher: {} as Record<string, number>
    };

    sessionsData.forEach(session => {
      const divisionKey = `${session.division.year} ${session.division.name}`;
      const teacherKey = session.teacher.name;

      stats.byDivision[divisionKey] = (stats.byDivision[divisionKey] || 0) + 1;
      stats.byTeacher[teacherKey] = (stats.byTeacher[teacherKey] || 0) + 1;
    });

    setSessionStats(stats);
  };

  const canPublish = () => {
    if (!generationResult) return false;
    
    // Check if violations are within acceptable limits
    const criticalViolations = generationResult.total_violations;
    const fitnessThreshold = 70; // Minimum fitness score
    
    return (
      criticalViolations <= 5 && 
      generationResult.fitness_score >= fitnessThreshold &&
      approved
    );
  };

  const handleApproval = () => {
    setApproved(true);
    setActiveStep(3);
    setSuccess('Timetable approved for publishing');
  };

  const handlePublish = async () => {
    if (!canPublish()) {
      setError('Cannot publish: please resolve critical issues first');
      return;
    }

    setLoading(true);
    try {
      // Mock publish API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setActiveStep(4);
      setSuccess('Timetable published successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to publish');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setLoading(true);
    try {
      const exportResult = await timetableApi.requestExport(exportConfig);
      setExportResults([...exportResults, exportResult]);
      setExportDialogOpen(false);
      setSuccess(`Export started: ${exportConfig.format.toUpperCase()}`);
      
      // Poll for completion
      pollExportStatus(exportResult.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setLoading(false);
    }
  };

  const pollExportStatus = async (exportId: string) => {
    const checkStatus = async () => {
      try {
        const result = await timetableApi.getExportStatus(exportId);
        
        if (result.status === 'completed') {
          setExportResults(prev => 
            prev.map(exp => exp.id === exportId ? result : exp)
          );
          setSuccess('Export completed successfully!');
        } else if (result.status === 'failed') {
          setError('Export failed');
        } else {
          // Continue polling
          setTimeout(checkStatus, 2000);
        }
      } catch (err) {
        console.error('Failed to check export status:', err);
      }
    };

    checkStatus();
  };

  const renderQualityCheck = () => {
    if (!generationResult) return null;

    const qualityChecks = [
      {
        name: 'Fitness Score',
        status: generationResult.fitness_score >= 70 ? 'pass' : 'fail',
        value: `${generationResult.fitness_score.toFixed(1)}/100`,
        threshold: '≥70'
      },
      {
        name: 'Critical Violations',
        status: generationResult.total_violations <= 5 ? 'pass' : 'fail',
        value: generationResult.total_violations.toString(),
        threshold: '≤5'
      },
      {
        name: 'Sessions Created',
        status: generationResult.sessions_created > 0 ? 'pass' : 'fail',
        value: generationResult.sessions_created.toString(),
        threshold: '>0'
      },
      {
        name: 'Algorithm Completion',
        status: generationResult.status === 'completed' ? 'pass' : 'fail',
        value: generationResult.status,
        threshold: 'completed'
      }
    ];

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment />
            Quality Assessment
          </Typography>

          <List>
            {qualityChecks.map((check, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {check.status === 'pass' ? (
                    <CheckCircle color="success" />
                  ) : (
                    <Warning color="error" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={check.name}
                  secondary={`Current: ${check.value} | Required: ${check.threshold}`}
                />
                <Chip
                  label={check.status.toUpperCase()}
                  color={check.status === 'pass' ? 'success' : 'error'}
                  size="small"
                />
              </ListItem>
            ))}
          </List>

          {!canPublish() && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Quality checks must pass before publishing. Please resolve issues or regenerate the timetable.
            </Alert>
          )}
        </CardContent>
      </Card>
    );
  };

  const renderSessionsOverview = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Schedule color="primary" sx={{ fontSize: 40, mb: 1 }} />
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            {sessionStats.total}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total Sessions
          </Typography>
        </Paper>
      </Grid>

      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>By Division</Typography>
          {Object.entries(sessionStats.byDivision).slice(0, 3).map(([division, count]) => (
            <Typography key={division} variant="body2">
              {division}: {count} sessions
            </Typography>
          ))}
        </Paper>
      </Grid>

      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>Top Teachers</Typography>
          {Object.entries(sessionStats.byTeacher)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 3)
            .map(([teacher, count]) => (
              <Typography key={teacher} variant="body2">
                {teacher}: {count} sessions
              </Typography>
            ))}
        </Paper>
      </Grid>
    </Grid>
  );

  const renderApprovalStep = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Approval Required</Typography>
        
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Approval Notes (Optional)"
          value={approvalNotes}
          onChange={(e) => setApprovalNotes(e.target.value)}
          placeholder="Add any notes about this timetable version..."
          sx={{ mb: 3 }}
        />

        <FormControlLabel
          control={
            <Checkbox
              checked={approved}
              onChange={(e) => setApproved(e.target.checked)}
            />
          }
          label="I approve this timetable for publishing"
        />

        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            onClick={handleApproval}
            disabled={!approved || !canPublish()}
            startIcon={<CheckCircle />}
          >
            Approve Timetable
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const renderExportDialog = () => (
    <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Export Timetable</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ pt: 2 }}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>Export Format</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {[
                { value: 'pdf', label: 'PDF', icon: <PictureAsPdf /> },
                { value: 'csv', label: 'CSV', icon: <TableChart /> },
                { value: 'json', label: 'JSON', icon: <DataObject /> }
              ].map((format) => (
                <Chip
                  key={format.value}
                  icon={format.icon}
                  label={format.label}
                  clickable
                  color={exportConfig.format === format.value ? 'primary' : 'default'}
                  onClick={() => setExportConfig({...exportConfig, format: format.value as any})}
                />
              ))}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>Export Scope</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {[
                { value: 'all', label: 'All Divisions' },
                { value: 'division', label: 'Specific Division' },
                { value: 'teacher', label: 'Specific Teacher' }
              ].map((scope) => (
                <Chip
                  key={scope.value}
                  label={scope.label}
                  clickable
                  color={exportConfig.scope === scope.value ? 'primary' : 'default'}
                  onClick={() => setExportConfig({...exportConfig, scope: scope.value as any})}
                />
              ))}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={exportConfig.include_violations || false}
                  onChange={(e) => setExportConfig({
                    ...exportConfig,
                    include_violations: e.target.checked
                  })}
                />
              }
              label="Include violations report"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setExportDialogOpen(false)}>Cancel</Button>
        <Button onClick={handleExport} variant="contained" disabled={loading}>
          {loading ? 'Exporting...' : 'Export'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderVersionHistory = () => (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <History />
          Version History
        </Typography>

        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Version</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Fitness</TableCell>
                <TableCell>Violations</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {versions.map((version) => (
                <TableRow key={version.id}>
                  <TableCell>{version.version}</TableCell>
                  <TableCell>{new Date(version.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>{version.fitness_score}</TableCell>
                  <TableCell>{version.violations}</TableCell>
                  <TableCell>
                    <Chip
                      label={version.status}
                      color={version.status === 'published' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  if (!generationResult) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Publish sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" color="text.secondary">
          No Generation Results
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Please generate a timetable first before publishing.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Publish & Export
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Review, approve, and export your generated timetable
      </Typography>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Progress Stepper */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Stepper activeStep={activeStep} orientation="vertical">
            <Step>
              <StepLabel>Review Results</StepLabel>
              <StepContent>
                {renderSessionsOverview()}
                <Button onClick={() => setActiveStep(1)} variant="outlined">
                  Continue to Quality Check
                </Button>
              </StepContent>
            </Step>

            <Step>
              <StepLabel>Quality Check</StepLabel>
              <StepContent>
                {renderQualityCheck()}
                <Button 
                  onClick={() => setActiveStep(2)} 
                  variant="outlined"
                  disabled={!canPublish()}
                >
                  Proceed to Approval
                </Button>
              </StepContent>
            </Step>

            <Step>
              <StepLabel>Approval</StepLabel>
              <StepContent>
                {renderApprovalStep()}
              </StepContent>
            </Step>

            <Step>
              <StepLabel>Publish</StepLabel>
              <StepContent>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  Ready to publish the approved timetable.
                </Typography>
                <Button
                  variant="contained"
                  onClick={handlePublish}
                  disabled={!approved || loading}
                  startIcon={<Publish />}
                >
                  Publish Timetable
                </Button>
              </StepContent>
            </Step>

            <Step>
              <StepLabel>Export</StepLabel>
              <StepContent>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  Timetable published successfully! Export in your preferred format.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => setExportDialogOpen(true)}
                    startIcon={<Download />}
                  >
                    Export Timetable
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Share />}
                  >
                    Share Link
                  </Button>
                </Box>
              </StepContent>
            </Step>
          </Stepper>
        </CardContent>
      </Card>

      {/* Export Results */}
      {exportResults.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Export History</Typography>
            <List>
              {exportResults.map((result) => (
                <ListItem key={result.id}>
                  <ListItemIcon>
                    <Download color={result.status === 'completed' ? 'success' : 'primary'} />
                  </ListItemIcon>
                  <ListItemText
                    primary={`${result.id} - ${result.status}`}
                    secondary={new Date(result.created_at).toLocaleString()}
                  />
                  {result.download_url && (
                    <Button
                      variant="outlined"
                      size="small"
                      href={result.download_url}
                      download
                    >
                      Download
                    </Button>
                  )}
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {renderVersionHistory()}
      {renderExportDialog()}
    </Box>
  );
};

export default PublishExport;
