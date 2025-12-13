/**
 * CSV Import Functionality
 * Based on frontend_comprehensive_fix_prompt.md requirements
 */

import { validateTeacher, validateSubject, validateRoom, validateTimeSlot } from './validation';

export interface CSVImportResult<T> {
  success: boolean;
  data: T[];
  errors: string[];
  warnings: string[];
  previewData: T[];
}

export interface CSVColumn {
  key: string;
  label: string;
  required: boolean;
  type: 'string' | 'number' | 'boolean' | 'email' | 'time';
  example?: string;
}

// CSV Templates as per requirements
export const CSV_TEMPLATES = {
  teachers: [
    { key: 'name', label: 'Teacher Name', required: true, type: 'string' as const, example: 'Dr. John Smith' },
    { key: 'email', label: 'Email Address', required: true, type: 'email' as const, example: 'john.smith@college.edu' },
    { key: 'department', label: 'Department', required: false, type: 'string' as const, example: 'Computer Science' },
    { key: 'lectureTimePreference', label: 'Lecture Time Preference', required: false, type: 'string' as const, example: 'morning/afternoon/no_preference' },
    { key: 'labTimePreference', label: 'Lab Time Preference', required: false, type: 'string' as const, example: 'morning/afternoon/no_preference' }
  ],
  
  subjects: [
    { key: 'name', label: 'Subject Name', required: true, type: 'string' as const, example: 'Data Structures' },
    { key: 'sessionsPerWeek', label: 'Sessions Per Week', required: true, type: 'number' as const, example: '3' },
    { key: 'requiresLab', label: 'Requires Lab', required: true, type: 'boolean' as const, example: 'true/false' },
    { key: 'equipmentRequired', label: 'Equipment Required', required: false, type: 'string' as const, example: 'Computers,Projector' },
    { key: 'year', label: 'Year', required: true, type: 'string' as const, example: 'SE/TE/BE' },
    { key: 'division', label: 'Division', required: true, type: 'string' as const, example: 'A/B' }
  ],
  
  rooms: [
    { key: 'name', label: 'Room Name', required: true, type: 'string' as const, example: 'Room 101' },
    { key: 'capacity', label: 'Capacity', required: true, type: 'number' as const, example: '60' },
    { key: 'type', label: 'Room Type', required: true, type: 'string' as const, example: 'classroom/lab' },
    { key: 'availableEquipment', label: 'Available Equipment', required: false, type: 'string' as const, example: 'Computers,Projector,Whiteboard' }
  ],
  
  timeslots: [
    { key: 'dayOfWeek', label: 'Day of Week', required: true, type: 'string' as const, example: 'Monday' },
    { key: 'startTime', label: 'Start Time', required: true, type: 'time' as const, example: '09:00' },
    { key: 'endTime', label: 'End Time', required: true, type: 'time' as const, example: '10:00' },
    { key: 'type', label: 'Slot Type', required: false, type: 'string' as const, example: 'lecture/lab' }
  ]
};

/**
 * Parse CSV text into array of objects
 */
export function parseCSV(csvText: string): Record<string, string>[] {
  const lines = csvText.trim().split('\n');
  if (lines.length < 2) {
    throw new Error('CSV must have at least a header row and one data row');
  }

  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
  const data: Record<string, string>[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
    const row: Record<string, string> = {};
    
    headers.forEach((header, index) => {
      row[header] = values[index] || '';
    });
    
    data.push(row);
  }

  return data;
}

/**
 * Validate CSV columns against template
 */
export function validateCSVColumns(
  headers: string[], 
  template: CSVColumn[]
): { isValid: boolean; errors: string[]; warnings: string[] } {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check required columns
  const requiredColumns = template.filter(col => col.required);
  requiredColumns.forEach(col => {
    if (!headers.includes(col.key) && !headers.includes(col.label)) {
      errors.push(`Missing required column: ${col.label} (${col.key})`);
    }
  });

  // Check for unknown columns
  headers.forEach(header => {
    const found = template.find(col => col.key === header || col.label === header);
    if (!found) {
      warnings.push(`Unknown column: ${header} (will be ignored)`);
    }
  });

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Transform CSV data to match internal format
 */
export function transformCSVData(
  csvData: Record<string, string>[],
  template: CSVColumn[]
): any[] {
  return csvData.map(row => {
    const transformed: any = {};
    
    template.forEach(col => {
      // Try both key and label as column names
      const value = row[col.key] || row[col.label] || '';
      
      if (value) {
        switch (col.type) {
          case 'number':
            transformed[col.key] = parseInt(value) || 0;
            break;
          case 'boolean':
            transformed[col.key] = value.toLowerCase() === 'true' || value === '1';
            break;
          case 'string':
          case 'email':
          case 'time':
            // Handle comma-separated lists for equipment
            if (col.key.includes('Equipment') && value.includes(',')) {
              transformed[col.key] = value.split(',').map(item => item.trim());
            } else {
              transformed[col.key] = value;
            }
            break;
          default:
            transformed[col.key] = value;
        }
      }
    });
    
    return transformed;
  });
}

/**
 * Import Teachers from CSV
 */
export async function importTeachersFromCSV(file: File): Promise<CSVImportResult<any>> {
  try {
    const csvText = await file.text();
    const csvData = parseCSV(csvText);
    const headers = Object.keys(csvData[0] || {});
    
    // Validate columns
    const columnValidation = validateCSVColumns(headers, CSV_TEMPLATES.teachers);
    if (!columnValidation.isValid) {
      return {
        success: false,
        data: [],
        errors: columnValidation.errors,
        warnings: columnValidation.warnings,
        previewData: []
      };
    }

    // Transform data
    const transformedData = transformCSVData(csvData, CSV_TEMPLATES.teachers);
    
    // Validate each teacher
    const validData: any[] = [];
    const errors: string[] = [];
    const warnings: string[] = [];

    transformedData.forEach((teacher, index) => {
      const validation = validateTeacher(teacher);
      if (validation.isValid) {
        validData.push(teacher);
      } else {
        validation.errors.forEach(error => {
          errors.push(`Row ${index + 2}: ${error.message}`);
        });
      }
      
      validation.warnings.forEach(warning => {
        warnings.push(`Row ${index + 2}: ${warning.message}`);
      });
    });

    return {
      success: errors.length === 0,
      data: validData,
      errors: [...columnValidation.errors, ...errors],
      warnings: [...columnValidation.warnings, ...warnings],
      previewData: transformedData.slice(0, 5) // First 5 rows for preview
    };

  } catch (error) {
    return {
      success: false,
      data: [],
      errors: [`Failed to parse CSV: ${error instanceof Error ? error.message : 'Unknown error'}`],
      warnings: [],
      previewData: []
    };
  }
}

/**
 * Import Subjects from CSV
 */
export async function importSubjectsFromCSV(file: File): Promise<CSVImportResult<any>> {
  try {
    const csvText = await file.text();
    const csvData = parseCSV(csvText);
    const headers = Object.keys(csvData[0] || {});
    
    const columnValidation = validateCSVColumns(headers, CSV_TEMPLATES.subjects);
    if (!columnValidation.isValid) {
      return {
        success: false,
        data: [],
        errors: columnValidation.errors,
        warnings: columnValidation.warnings,
        previewData: []
      };
    }

    const transformedData = transformCSVData(csvData, CSV_TEMPLATES.subjects);
    
    const validData: any[] = [];
    const errors: string[] = [];
    const warnings: string[] = [];

    transformedData.forEach((subject, index) => {
      const validation = validateSubject(subject);
      if (validation.isValid) {
        validData.push(subject);
      } else {
        validation.errors.forEach(error => {
          errors.push(`Row ${index + 2}: ${error.message}`);
        });
      }
    });

    return {
      success: errors.length === 0,
      data: validData,
      errors: [...columnValidation.errors, ...errors],
      warnings: [...columnValidation.warnings, ...warnings],
      previewData: transformedData.slice(0, 5)
    };

  } catch (error) {
    return {
      success: false,
      data: [],
      errors: [`Failed to parse CSV: ${error instanceof Error ? error.message : 'Unknown error'}`],
      warnings: [],
      previewData: []
    };
  }
}

/**
 * Import Rooms from CSV
 */
export async function importRoomsFromCSV(file: File): Promise<CSVImportResult<any>> {
  try {
    const csvText = await file.text();
    const csvData = parseCSV(csvText);
    const headers = Object.keys(csvData[0] || {});
    
    const columnValidation = validateCSVColumns(headers, CSV_TEMPLATES.rooms);
    if (!columnValidation.isValid) {
      return {
        success: false,
        data: [],
        errors: columnValidation.errors,
        warnings: columnValidation.warnings,
        previewData: []
      };
    }

    const transformedData = transformCSVData(csvData, CSV_TEMPLATES.rooms);
    
    const validData: any[] = [];
    const errors: string[] = [];
    const warnings: string[] = [];

    transformedData.forEach((room, index) => {
      const validation = validateRoom(room);
      if (validation.isValid) {
        validData.push(room);
      } else {
        validation.errors.forEach(error => {
          errors.push(`Row ${index + 2}: ${error.message}`);
        });
      }
    });

    return {
      success: errors.length === 0,
      data: validData,
      errors: [...columnValidation.errors, ...errors],
      warnings: [...columnValidation.warnings, ...warnings],
      previewData: transformedData.slice(0, 5)
    };

  } catch (error) {
    return {
      success: false,
      data: [],
      errors: [`Failed to parse CSV: ${error instanceof Error ? error.message : 'Unknown error'}`],
      warnings: [],
      previewData: []
    };
  }
}

/**
 * Import Time Slots from CSV
 */
export async function importTimeSlotsFromCSV(file: File): Promise<CSVImportResult<any>> {
  try {
    const csvText = await file.text();
    const csvData = parseCSV(csvText);
    const headers = Object.keys(csvData[0] || {});
    
    const columnValidation = validateCSVColumns(headers, CSV_TEMPLATES.timeslots);
    if (!columnValidation.isValid) {
      return {
        success: false,
        data: [],
        errors: columnValidation.errors,
        warnings: columnValidation.warnings,
        previewData: []
      };
    }

    const transformedData = transformCSVData(csvData, CSV_TEMPLATES.timeslots);
    
    const validData: any[] = [];
    const errors: string[] = [];
    const warnings: string[] = [];

    transformedData.forEach((timeSlot, index) => {
      const validation = validateTimeSlot(timeSlot);
      if (validation.isValid) {
        validData.push(timeSlot);
      } else {
        validation.errors.forEach(error => {
          errors.push(`Row ${index + 2}: ${error.message}`);
        });
      }
    });

    return {
      success: errors.length === 0,
      data: validData,
      errors: [...columnValidation.errors, ...errors],
      warnings: [...columnValidation.warnings, ...warnings],
      previewData: transformedData.slice(0, 5)
    };

  } catch (error) {
    return {
      success: false,
      data: [],
      errors: [`Failed to parse CSV: ${error instanceof Error ? error.message : 'Unknown error'}`],
      warnings: [],
      previewData: []
    };
  }
}

/**
 * Generate CSV template for download
 */
export function generateCSVTemplate(type: keyof typeof CSV_TEMPLATES): string {
  const template = CSV_TEMPLATES[type];
  const headers = template.map(col => col.label).join(',');
  const examples = template.map(col => col.example || '').join(',');
  
  return `${headers}\n${examples}`;
}

/**
 * Download CSV template
 */
export function downloadCSVTemplate(type: keyof typeof CSV_TEMPLATES): void {
  const csvContent = generateCSVTemplate(type);
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `${type}_template.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
