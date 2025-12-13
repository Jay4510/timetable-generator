/**
 * Comprehensive Form Validation System
 * Based on frontend_comprehensive_fix_prompt.md requirements
 */

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  format?: 'email' | 'time' | 'number';
  enum?: string[];
  mustBeAfter?: string;
}

export interface ValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

// Validation Rules as per frontend_comprehensive_fix_prompt.md
export const VALIDATION_RULES = {
  // Teachers
  teacher: {
    name: { required: true, minLength: 2, maxLength: 50 },
    email: { required: true, format: 'email' as const },
    department: { maxLength: 100 },
    preferences: {
      lectureTimePreference: { enum: ['morning', 'afternoon', 'no_preference'] },
      labTimePreference: { enum: ['morning', 'afternoon', 'no_preference'] }
    }
  },
  
  // Subjects
  subject: {
    name: { required: true, minLength: 2, maxLength: 100 },
    sessionsPerWeek: { required: true, min: 1, max: 6 },
    requiresLab: { required: true },
    equipmentRequired: { required: false }
  },
  
  // Rooms/Labs
  room: {
    name: { required: true, minLength: 2, maxLength: 50 },
    capacity: { required: true, min: 10, max: 200 },
    availableEquipment: { required: false }
  },
  
  // Divisions
  division: {
    name: { required: true, minLength: 1, maxLength: 50 },
    studentCount: { required: true, min: 10, max: 100 },
    year: { required: true }
  },
  
  // Time Slots
  timeSlot: {
    dayOfWeek: { required: true, enum: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] },
    startTime: { required: true, format: 'time' as const },
    endTime: { required: true, format: 'time' as const, mustBeAfter: 'startTime' }
  }
};

// Human-friendly error messages as per requirements
export const ERROR_MESSAGES = {
  required: (field: string) => `${field} is required`,
  minLength: (field: string, min: number) => `${field} must be at least ${min} characters`,
  maxLength: (field: string, max: number) => `${field} must not exceed ${max} characters`,
  min: (field: string, min: number) => `${field} must be at least ${min}`,
  max: (field: string, max: number) => `${field} must not exceed ${max}`,
  email: (field: string) => `${field} must be a valid email address`,
  time: (field: string) => `${field} must be in HH:MM format`,
  enum: (field: string, options: string[]) => `${field} must be one of: ${options.join(', ')}`,
  mustBeAfter: (field: string, afterField: string) => `${field} must be after ${afterField}`,
  
  // Specific business logic messages
  roomCapacityTooSmall: (roomName: string, capacity: number, division: string, studentCount: number) => 
    `Room ${roomName} (capacity: ${capacity}) cannot accommodate ${division} with ${studentCount} students`,
  timeOverlapDetected: (timeSlot: string, existingSlot: string, day: string) => 
    `Time slot ${timeSlot} overlaps with existing slot ${existingSlot} on ${day}`,
  missingTeacherProficiency: (teacherName: string, subjectName: string) => 
    `Teacher ${teacherName} has no proficiency data for subject ${subjectName}`
};

/**
 * Validate a single field against its rules
 */
export function validateField(
  fieldName: string, 
  value: any, 
  rules: ValidationRule,
  allData?: Record<string, any>
): ValidationError[] {
  const errors: ValidationError[] = [];
  const displayName = fieldName.charAt(0).toUpperCase() + fieldName.slice(1);

  // Required validation
  if (rules.required && (value === null || value === undefined || value === '')) {
    errors.push({
      field: fieldName,
      message: ERROR_MESSAGES.required(displayName),
      severity: 'error'
    });
    return errors; // Don't continue if required field is empty
  }

  // Skip other validations if field is empty and not required
  if (!value && !rules.required) {
    return errors;
  }

  // String length validations
  if (typeof value === 'string') {
    if (rules.minLength && value.length < rules.minLength) {
      errors.push({
        field: fieldName,
        message: ERROR_MESSAGES.minLength(displayName, rules.minLength),
        severity: 'error'
      });
    }
    
    if (rules.maxLength && value.length > rules.maxLength) {
      errors.push({
        field: fieldName,
        message: ERROR_MESSAGES.maxLength(displayName, rules.maxLength),
        severity: 'error'
      });
    }
  }

  // Numeric validations
  if (typeof value === 'number' || !isNaN(Number(value))) {
    const numValue = Number(value);
    
    if (rules.min !== undefined && numValue < rules.min) {
      errors.push({
        field: fieldName,
        message: ERROR_MESSAGES.min(displayName, rules.min),
        severity: 'error'
      });
    }
    
    if (rules.max !== undefined && numValue > rules.max) {
      errors.push({
        field: fieldName,
        message: ERROR_MESSAGES.max(displayName, rules.max),
        severity: 'error'
      });
    }
  }

  // Format validations
  if (rules.format) {
    switch (rules.format) {
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          errors.push({
            field: fieldName,
            message: ERROR_MESSAGES.email(displayName),
            severity: 'error'
          });
        }
        break;
        
      case 'time':
        const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
        if (!timeRegex.test(value)) {
          errors.push({
            field: fieldName,
            message: ERROR_MESSAGES.time(displayName),
            severity: 'error'
          });
        }
        break;
    }
  }

  // Enum validation
  if (rules.enum && !rules.enum.includes(value)) {
    errors.push({
      field: fieldName,
      message: ERROR_MESSAGES.enum(displayName, rules.enum),
      severity: 'error'
    });
  }

  // Must be after validation (for time fields)
  if (rules.mustBeAfter && allData) {
    const afterValue = allData[rules.mustBeAfter];
    if (afterValue && value <= afterValue) {
      errors.push({
        field: fieldName,
        message: ERROR_MESSAGES.mustBeAfter(displayName, rules.mustBeAfter),
        severity: 'error'
      });
    }
  }

  return errors;
}

/**
 * Validate an entire object against validation rules
 */
export function validateObject(
  data: Record<string, any>,
  rulesSet: Record<string, ValidationRule>
): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  Object.entries(rulesSet).forEach(([fieldName, rules]) => {
    const fieldErrors = validateField(fieldName, data[fieldName], rules, data);
    errors.push(...fieldErrors);
  });

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Validate teacher data
 */
export function validateTeacher(teacher: any): ValidationResult {
  return validateObject(teacher, VALIDATION_RULES.teacher);
}

/**
 * Validate subject data
 */
export function validateSubject(subject: any): ValidationResult {
  return validateObject(subject, VALIDATION_RULES.subject);
}

/**
 * Validate room data
 */
export function validateRoom(room: any): ValidationResult {
  return validateObject(room, VALIDATION_RULES.room);
}

/**
 * Validate division data
 */
export function validateDivision(division: any): ValidationResult {
  return validateObject(division, VALIDATION_RULES.division);
}

/**
 * Validate time slot data
 */
export function validateTimeSlot(timeSlot: any): ValidationResult {
  return validateObject(timeSlot, VALIDATION_RULES.timeSlot);
}

/**
 * Business logic validations
 */
export function validateBusinessLogic(data: {
  rooms?: any[];
  divisions?: any[];
  timeSlots?: any[];
  teachers?: any[];
  subjects?: any[];
}): ValidationError[] {
  const errors: ValidationError[] = [];

  // Room capacity vs division size validation
  if (data.rooms && data.divisions) {
    data.divisions.forEach(division => {
      data.rooms!.forEach(room => {
        if (room.capacity < division.studentCount) {
          errors.push({
            field: 'room_capacity',
            message: ERROR_MESSAGES.roomCapacityTooSmall(
              room.name, 
              room.capacity, 
              division.name, 
              division.studentCount
            ),
            severity: 'warning'
          });
        }
      });
    });
  }

  // Time slot overlap validation
  if (data.timeSlots) {
    const slotsByDay: Record<string, any[]> = {};
    
    data.timeSlots.forEach(slot => {
      if (!slotsByDay[slot.dayOfWeek]) {
        slotsByDay[slot.dayOfWeek] = [];
      }
      slotsByDay[slot.dayOfWeek].push(slot);
    });

    Object.entries(slotsByDay).forEach(([day, slots]) => {
      for (let i = 0; i < slots.length; i++) {
        for (let j = i + 1; j < slots.length; j++) {
          const slot1 = slots[i];
          const slot2 = slots[j];
          
          // Check for overlap
          if (timeOverlaps(slot1.startTime, slot1.endTime, slot2.startTime, slot2.endTime)) {
            errors.push({
              field: 'time_overlap',
              message: ERROR_MESSAGES.timeOverlapDetected(
                `${slot1.startTime}-${slot1.endTime}`,
                `${slot2.startTime}-${slot2.endTime}`,
                day
              ),
              severity: 'error'
            });
          }
        }
      }
    });
  }

  return errors;
}

/**
 * Helper function to check if two time ranges overlap
 */
function timeOverlaps(start1: string, end1: string, start2: string, end2: string): boolean {
  const toMinutes = (time: string) => {
    const [hours, minutes] = time.split(':').map(Number);
    return hours * 60 + minutes;
  };

  const start1Min = toMinutes(start1);
  const end1Min = toMinutes(end1);
  const start2Min = toMinutes(start2);
  const end2Min = toMinutes(end2);

  return start1Min < end2Min && start2Min < end1Min;
}

/**
 * Preflight validation checks as per requirements
 */
export function runPreflightChecks(data: {
  teachers?: any[];
  subjects?: any[];
  rooms?: any[];
  divisions?: any[];
  timeSlots?: any[];
}): {
  allRequiredDataPresent: boolean;
  noConflictingConstraints: boolean;
  reasonableConfiguration: boolean;
  issues: ValidationError[];
} {
  const issues: ValidationError[] = [];

  // Check if all required data is present
  const allRequiredDataPresent = !!(
    data.teachers?.length &&
    data.subjects?.length &&
    data.rooms?.length &&
    data.divisions?.length &&
    data.timeSlots?.length
  );

  if (!allRequiredDataPresent) {
    if (!data.teachers?.length) issues.push({ field: 'teachers', message: 'At least one teacher is required', severity: 'error' });
    if (!data.subjects?.length) issues.push({ field: 'subjects', message: 'At least one subject is required', severity: 'error' });
    if (!data.rooms?.length) issues.push({ field: 'rooms', message: 'At least one room is required', severity: 'error' });
    if (!data.divisions?.length) issues.push({ field: 'divisions', message: 'At least one division is required', severity: 'error' });
    if (!data.timeSlots?.length) issues.push({ field: 'timeSlots', message: 'At least one time slot is required', severity: 'error' });
  }

  // Check for conflicting constraints
  const businessLogicErrors = validateBusinessLogic(data);
  const noConflictingConstraints = businessLogicErrors.filter(e => e.severity === 'error').length === 0;
  issues.push(...businessLogicErrors);

  // Check for reasonable configuration
  let reasonableConfiguration = true;
  
  if (data.teachers && data.subjects) {
    const teacherSubjectRatio = data.subjects.length / data.teachers.length;
    if (teacherSubjectRatio > 5) {
      issues.push({
        field: 'configuration',
        message: `High subject-to-teacher ratio (${teacherSubjectRatio.toFixed(1)}). Consider adding more teachers.`,
        severity: 'warning'
      });
      reasonableConfiguration = false;
    }
  }

  return {
    allRequiredDataPresent,
    noConflictingConstraints,
    reasonableConfiguration,
    issues
  };
}
