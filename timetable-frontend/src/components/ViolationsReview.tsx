/**
 * Violations Review Component
 * Professional interface for analyzing and resolving scheduling conflicts
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  LinearProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Autocomplete,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Assessment,
  Error,
  Warning,
  Info,
  CheckCircle,
  FilterList,
  AutoFixHigh,
  Visibility,
  ExpandMore,
  Schedule,
  People,
  Room,
  School,
  Build,
  Timeline
} from '@mui/icons-material';

import type { ViolationDetail, GenerationResult, ConflictSuggestion } from '../types/api';
import timetableApi from '../services/timetableApi';

interface ViolationsReviewProps {
  generationId?: string;
}

const ViolationsReview: React.FC<ViolationsReviewProps> = ({ generationId }) => {
  const [violations, setViolations] = useState<ViolationDetail[]>([]);
  const [filteredViolations, setFilteredViolations] = useState<ViolationDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Filter states
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchFilter, setSearchFilter] = useState('');

  // Dialog states
  const [selectedViolation, setSelectedViolation] = useState<ViolationDetail | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<ConflictSuggestion[]>([]);

  // Statistics
  const [violationStats, setViolationStats] = useState({
    total: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    byType: {} as Record<string, number>
  });

  useEffect(() => {
    if (generationId) {
      loadViolations();
    }
  }, [generationId]);

  useEffect(() => {
    applyFilters();
  }, [violations, severityFilter, typeFilter, searchFilter]);

  const loadViolations = async () => {
    if (!generationId) return;

    setLoading(true);
    try {
      const violationsData = await timetableApi.getViolations(generationId);
      setViolations(violationsData);
      calculateStats(violationsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load violations');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (violationsData: ViolationDetail[]) => {
    const stats = {
      total: violationsData.length,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      byType: {} as Record<string, number>
    };

    violationsData.forEach(violation => {
      // Count by severity
      stats[violation.severity as keyof typeof stats]++;
      
      // Count by type
      if (stats.byType[violation.type]) {
        stats.byType[violation.type]++;
      } else {
        stats.byType[violation.type] = 1;
      }
    });

    setViolationStats(stats);
  };

  const applyFilters = () => {
    let filtered = violations;

    // Severity filter
    if (severityFilter !== 'all') {
      filtered = filtered.filter(v => v.severity === severityFilter);
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(v => v.type === typeFilter);
    }

    // Search filter
    if (searchFilter) {
      filtered = filtered.filter(v => 
        v.description.toLowerCase().includes(searchFilter.toLowerCase()) ||
        v.type.toLowerCase().includes(searchFilter.toLowerCase())
      );
    }

    setFilteredViolations(filtered);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <Error color="error" />;
      case 'high': return <Warning color="error" />;
      case 'medium': return <Warning color="warning" />;
      case 'low': return <Info color="info" />;
      default: return <CheckCircle />;
    }
  };

  const getTypeIcon = (type: string) => {
    if (type.includes('teacher')) return <People />;
    if (type.includes('room') || type.includes('lab')) return <Room />;
    if (type.includes('subject')) return <School />;
    if (type.includes('time')) return <Schedule />;
    return <Assessment />;
  };

  const openViolationDetail = (violation: ViolationDetail) => {
    setSelectedViolation(violation);
    setSuggestions(violation.suggestions || []);
    setDetailDialogOpen(true);
  };

  const handleAutoFix = async (violationId: string) => {
    setLoading(true);
    try {
      await timetableApi.resolveViolation(violationId, 'auto_fix');
      setSuccess('Violation resolved automatically');
      loadViolations(); // Reload to see changes
      setDetailDialogOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Auto-fix failed');
    } finally {
      setLoading(false);
    }
  };

  const renderStatsOverview = () => (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      <Grid item xs={12} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Assessment color="primary" sx={{ fontSize: 32, mb: 1 }} />
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            {violationStats.total}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total Violations
          </Typography>
        </Paper>
      </Grid>

      <Grid item xs={12} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Error color="error" sx={{ fontSize: 32, mb: 1 }} />
          <Typography variant="h4" color="error.main" sx={{ fontWeight: 600 }}>
            {violationStats.critical}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Critical
          </Typography>
        </Paper>
      </Grid>

      <Grid item xs={12} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Warning color="error" sx={{ fontSize: 32, mb: 1 }} />
          <Typography variant="h4" color="error.main" sx={{ fontWeight: 600 }}>
            {violationStats.high}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            High
          </Typography>
        </Paper>
      </Grid>

      <Grid item xs={12} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Warning color="warning" sx={{ fontSize: 32, mb: 1 }} />
          <Typography variant="h4" color="warning.main" sx={{ fontWeight: 600 }}>
            {violationStats.medium}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Medium
          </Typography>
        </Paper>
      </Grid>

      <Grid item xs={12} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Info color="info" sx={{ fontSize: 32, mb: 1 }} />
          <Typography variant="h4" color="info.main" sx={{ fontWeight: 600 }}>
            {violationStats.low}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Low
          </Typography>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderFilters = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterList />
          Filters
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Autocomplete
              options={['all', 'critical', 'high', 'medium', 'low']}
              value={severityFilter}
              onChange={(_, value) => setSeverityFilter(value || 'all')}
              renderInput={(params) => <TextField {...params} label="Severity" size="small" />}
            />
          </Grid>

          <Grid item xs={12} md={3}>
            <Autocomplete
              options={['all', ...Object.keys(violationStats.byType)]}
              value={typeFilter}
              onChange={(_, value) => setTypeFilter(value || 'all')}
              renderInput={(params) => <TextField {...params} label="Type" size="small" />}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              size="small"
              label="Search violations..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
            />
          </Grid>
        </Grid>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Showing {filteredViolations.length} of {violations.length} violations
        </Typography>
      </CardContent>
    </Card>
  );

  const renderViolationsTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Type</TableCell>
            <TableCell>Severity</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Affected Sessions</TableCell>
            <TableCell>Auto-Fix</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredViolations.map((violation) => (
            <TableRow key={violation.id} hover>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {getTypeIcon(violation.type)}
                  <Typography variant="body2">
                    {violation.type.replace('_', ' ').toUpperCase()}
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Chip
                  icon={getSeverityIcon(violation.severity)}
                  label={violation.severity.toUpperCase()}
                  color={getSeverityColor(violation.severity) as any}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {violation.description}
                </Typography>
              </TableCell>
              <TableCell>
                <Badge badgeContent={violation.affected_sessions.length} color="primary">
                  <Schedule />
                </Badge>
              </TableCell>
              <TableCell>
                {violation.can_auto_fix ? (
                  <Chip label="Available" color="success" size="small" />
                ) : (
                  <Chip label="Manual" color="default" size="small" />
                )}
              </TableCell>
              <TableCell>
                <Tooltip title="View Details">
                  <IconButton size="small" onClick={() => openViolationDetail(violation)}>
                    <Visibility />
                  </IconButton>
                </Tooltip>
                {violation.can_auto_fix && (
                  <Tooltip title="Auto Fix">
                    <IconButton 
                      size="small" 
                      color="primary"
                      onClick={() => handleAutoFix(violation.id)}
                    >
                      <AutoFixHigh />
                    </IconButton>
                  </Tooltip>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderViolationsByType = () => (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Violations by Type</Typography>
        
        {Object.entries(violationStats.byType).map(([type, count]) => (
          <Accordion key={type}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                {getTypeIcon(type)}
                <Typography sx={{ flexGrow: 1 }}>
                  {type.replace('_', ' ').toUpperCase()}
                </Typography>
                <Chip label={count} color="primary" size="small" />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <List dense>
                {filteredViolations
                  .filter(v => v.type === type)
                  .slice(0, 5)
                  .map(violation => (
                    <ListItem key={violation.id}>
                      <ListItemIcon>
                        {getSeverityIcon(violation.severity)}
                      </ListItemIcon>
                      <ListItemText
                        primary={violation.description}
                        secondary={`${violation.affected_sessions.length} sessions affected`}
                      />
                    </ListItem>
                  ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))}
      </CardContent>
    </Card>
  );

  const renderDetailDialog = () => (
    <Dialog open={detailDialogOpen} onClose={() => setDetailDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        Violation Details - {selectedViolation?.type.replace('_', ' ').toUpperCase()}
      </DialogTitle>
      <DialogContent>
        {selectedViolation && (
          <Box>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Severity</Typography>
                <Chip
                  icon={getSeverityIcon(selectedViolation.severity)}
                  label={selectedViolation.severity.toUpperCase()}
                  color={getSeverityColor(selectedViolation.severity) as any}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Affected Sessions</Typography>
                <Typography variant="body2">
                  {selectedViolation.affected_sessions.length} sessions
                </Typography>
              </Grid>
            </Grid>

            <Typography variant="subtitle2" gutterBottom>Description</Typography>
            <Typography variant="body2" sx={{ mb: 3 }}>
              {selectedViolation.description}
            </Typography>

            {suggestions.length > 0 && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>Suggested Solutions</Typography>
                <List>
                  {suggestions.map((suggestion, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Build color={suggestion.auto_applicable ? 'success' : 'warning'} />
                      </ListItemIcon>
                      <ListItemText
                        primary={suggestion.description}
                        secondary={`Impact Score: ${suggestion.impact_score}/10`}
                      />
                    </ListItem>
                  ))}
                </List>
              </>
            )}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
        {selectedViolation?.can_auto_fix && (
          <Button
            variant="contained"
            startIcon={<AutoFixHigh />}
            onClick={() => handleAutoFix(selectedViolation.id)}
            disabled={loading}
          >
            Apply Auto Fix
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );

  if (!generationId) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Assessment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" color="text.secondary">
          No Generation Selected
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Please run a timetable generation first to review violations.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 1400, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Violations Review
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Analyze and resolve scheduling conflicts from the latest generation
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

      {renderStatsOverview()}
      {renderFilters()}
      {renderViolationsTable()}
      {renderViolationsByType()}
      {renderDetailDialog()}
    </Box>
  );
};

export default ViolationsReview;
