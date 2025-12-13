import React, { useState, useEffect } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  CircularProgress
} from '@mui/material';

interface Division {
  id: number;
  name: string;
  year_name: string;
  key: string;
  display_name: string;
  num_batches: number;
}

interface DivisionSelectorProps {
  onDivisionChange: (divisionKey: string, sessions: any[]) => void;
  selectedDivision: string;
}

const DivisionSelector: React.FC<DivisionSelectorProps> = ({ 
  onDivisionChange, 
  selectedDivision 
}) => {
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDivisions();
  }, []);

  const fetchDivisions = async () => {
    setLoading(true);
    try {
      console.log('Fetching divisions from /api/divisions-list/');
      const response = await fetch('/api/divisions-list/');
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers.get('content-type'));
      
      if (response.ok) {
        const text = await response.text();
        console.log('Raw response text:', text);
        
        try {
          const data = JSON.parse(text);
          console.log('Parsed JSON data:', data);
          setDivisions(data);
        } catch (parseError) {
          console.error('JSON parse error:', parseError);
          console.error('Response text that failed to parse:', text);
        }
      } else {
        console.error('Failed to fetch divisions. Status:', response.status);
        const errorText = await response.text();
        console.error('Error response:', errorText);
      }
    } catch (error) {
      console.error('Network error fetching divisions:', error);
    }
    setLoading(false);
  };

  const handleDivisionChange = async (divisionKey: string) => {
    if (!divisionKey) {
      onDivisionChange('', []);
      return;
    }

    try {
      // Fetch filtered timetable
      const response = await fetch(`/api/timetable/?division=${divisionKey}`);
      if (response.ok) {
        const sessions = await response.json();
        onDivisionChange(divisionKey, sessions);
      } else {
        console.error('Failed to fetch filtered timetable');
        onDivisionChange(divisionKey, []);
      }
    } catch (error) {
      console.error('Error fetching filtered timetable:', error);
      onDivisionChange(divisionKey, []);
    }
  };

  if (loading) {
    return (
      <Box display="flex" alignItems="center" gap={2}>
        <CircularProgress size={20} />
        <Typography>Loading divisions...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ minWidth: 300 }}>
      <FormControl fullWidth>
        <InputLabel>Select Division</InputLabel>
        <Select
          value={selectedDivision}
          onChange={(e) => handleDivisionChange(e.target.value)}
          label="Select Division"
        >
          <MenuItem value="">
            <em>All Divisions</em>
          </MenuItem>
          {divisions.map((division) => (
            <MenuItem key={division.key} value={division.key}>
              {division.display_name} ({division.num_batches} batches)
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      {selectedDivision && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Showing timetable for: {divisions.find(d => d.key === selectedDivision)?.display_name}
        </Typography>
      )}
    </Box>
  );
};

export default DivisionSelector;
