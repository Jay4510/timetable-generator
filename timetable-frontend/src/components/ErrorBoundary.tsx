import React from 'react';
import { Alert, Button, Box, Typography } from '@mui/material';
import { Refresh } from '@mui/icons-material';

interface ErrorBoundaryProps {
  error?: string | null;
  onRetry?: () => void;
  children?: React.ReactNode;
}

const ErrorBoundary: React.FC<ErrorBoundaryProps> = ({ error, onRetry, children }) => {
  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error" 
          action={
            onRetry && (
              <Button 
                color="inherit" 
                size="small" 
                onClick={onRetry}
                startIcon={<Refresh />}
              >
                Retry
              </Button>
            )
          }
        >
          <Typography variant="body1">
            {error}
          </Typography>
        </Alert>
      </Box>
    );
  }

  return <>{children}</>;
};

export default ErrorBoundary;
