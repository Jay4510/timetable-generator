import React from 'react';
import { AppBar, Toolbar, Box, Typography, Chip, IconButton } from '@mui/material';
import { HelpOutline, Settings, School } from '@mui/icons-material';

interface DMCEHeaderProps {
  currentAcademicYear: string;
  selectedDepartment: string;
}

const DMCEHeader: React.FC<DMCEHeaderProps> = ({ 
  currentAcademicYear, 
  selectedDepartment 
}) => {
  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
      }}
    >
      <Toolbar sx={{ minHeight: '64px !important', py: 1 }}>
        {/* Left - Logo and Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid rgba(255,255,255,0.3)',
            }}
          >
            <School sx={{ fontSize: 28, color: 'white' }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1.1rem', lineHeight: 1.2 }}>
              Datta Meghe College of Engineering
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.75rem' }}>
              Smart Timetable Generator • Airoli, Navi Mumbai
            </Typography>
          </Box>
        </Box>

        {/* Right - Info and Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={`AY ${currentAcademicYear || '2025-26'}`}
              size="small"
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 600,
                fontSize: '0.75rem',
              }}
            />
            <Chip
              label={selectedDepartment || 'No Department'}
              size="small"
              sx={{
                backgroundColor: selectedDepartment ? 'rgba(255,255,255,0.25)' : 'rgba(255,255,255,0.1)',
                color: 'white',
                fontWeight: 600,
                fontSize: '0.75rem',
              }}
            />
          </Box>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <IconButton size="small" sx={{ color: 'white' }} title="Help & Support">
              <HelpOutline fontSize="small" />
            </IconButton>
            <IconButton size="small" sx={{ color: 'white' }} title="Settings">
              <Settings fontSize="small" />
            </IconButton>
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default DMCEHeader;
