# COMPREHENSIVE FRONTEND FIX PROMPT FOR TIMETABLE SYSTEM

## ROLE & CONTEXT
You are a Senior UX/UI Engineer tasked with fixing critical issues in a timetable generation system's frontend. The backend uses a sophisticated genetic algorithm with 15+ constraints, but the frontend currently has validation mismatches, poor UX for timetable incharges, and missing functionality.

## CRITICAL ISSUES TO FIX IMMEDIATELY

### 1. CONFIGURATION VALUE MISMATCHES (HIGH PRIORITY)

**Current Problem:** UI allows invalid values that don't match backend algorithm constraints.

**Teacher Workload Limits - WRONG VALUES:**
```typescript
// Current (INCORRECT)
minSessions: { min: 1, max: 25, default: 10 }
maxSessions: { min: 1, max: 30, default: 20 }

// Must Change To (CORRECT)
minSessions: { min: 6, max: 12, default: 8 }
maxSessions: { min: 10, max: 18, default: 14 }
```

**Session Distribution - WRONG IMPLEMENTATION:**
```typescript
// Current (INCORRECT) - Two separate sliders
morningPercentage: 0-100%
afternoonPercentage: 0-100%

// Must Change To (CORRECT) - Single balance slider
morningAfternoonRatio: { 
  min: 30, 
  max: 70, 
  default: 50,
  label: "Morning Session Ratio (30-70%)",
  description: "Percentage of sessions scheduled before 1 PM"
}
```

### 2. GENETIC ALGORITHM PARAMETERS - WRONG UX (HIGH PRIORITY)

**Current Problem:** Technical GA parameters exposed to non-technical users in main workflow.

**Must Hide These by Default:**
- Population Size (20-50, default: 30)
- Generations (100-300, default: 150) 
- Mutation Rate (0.1-0.3, default: 0.2)
- Division-Specific Generation toggle

**Required Changes:**
```typescript
// Main "Create Timetable" Interface Should Only Show:
interface MainGenerationUI {
  dryRun: boolean;                    // "Preview Mode" toggle
  generateTimetable: () => void;      // Primary CTA button
  advancedOptions: {
    collapsed: true;                  // Hidden by default
    populationSize: 30;              // Read-only when collapsed
    generations: 150;                // Read-only when collapsed
    mutationRate: 0.2;               // Read-only when collapsed
  }
}
```

### 3. MISSING CRITICAL VALIDATIONS

**Data Input Validation Requirements:**
```typescript
interface ValidationRules {
  // Teachers
  teacherName: { required: true, minLength: 2, maxLength: 50 }
  teacherEmail: { required: true, format: "email" }
  
  // Subjects  
  subjectName: { required: true, minLength: 2, maxLength: 100 }
  sessionsPerWeek: { min: 1, max: 6, default: 3 }
  requiresLab: boolean
  equipmentRequired: string[]  // Chips/tags, not free text
  
  // Rooms/Labs
  roomName: { required: true, minLength: 2, maxLength: 50 }
  capacity: { required: true, min: 10, max: 200 }
  availableEquipment: string[]  // Predefined list + custom
  
  // Divisions
  divisionName: { required: true }
  studentCount: { required: true, min: 10, max: 100 }
  year: { required: true }
  
  // Time Slots
  dayOfWeek: { required: true, enum: ["Monday", "Tuesday", ...] }
  startTime: { required: true, format: "HH:MM" }
  endTime: { required: true, format: "HH:MM", mustBeAfter: "startTime" }
  noOverlaps: true  // Validate no overlapping slots same day/room
}
```

### 4. UX FLOW CORRECTIONS

**Current Issues:**
- Too many technical options in main flow
- No clear data setup wizard
- Missing data validation feedback
- No preflight checks before generation

**Required UX Flow:**
```
1. Dashboard → Quick status, "Setup Data" or "Generate Timetable"
2. Data Setup Wizard:
   - Step 1: Teachers (with CSV import)
   - Step 2: Subjects (with equipment selection)  
   - Step 3: Rooms/Labs (with capacity validation)
   - Step 4: Divisions (with student counts)
   - Step 5: Time Slots (with overlap checking)
3. Configuration → System constraints (corrected values)
4. Generation → Simple "Preview" or "Generate" (GA params hidden)
5. Results → Violations list, timetable view, export options
```

## SPECIFIC COMPONENT FIXES REQUIRED

### Teacher Management Component
```typescript
interface TeacherFormData {
  name: string;                    // Required, 2-50 chars
  email: string;                   // Required, valid email
  department: string;              // Optional
  preferences: {
    lectureTimePreference: "morning" | "afternoon" | "no_preference";
    labTimePreference: "morning" | "afternoon" | "no_preference";
  };
  subjectProficiencies: {          // Map subjects to proficiency scores
    subjectId: string;
    proficiencyScore: number;      // 1-10 scale with clear labels
  }[];
}
```

### System Configuration Component  
```typescript
interface SystemConfigurationCorrect {
  // Teacher Constraints
  minSessionsPerTeacher: number;        // 6-12, default: 8 (NOT 1-25)
  maxSessionsPerTeacher: number;        // 10-18, default: 14 (NOT 1-30)
  maxConsecutiveHours: number;          // 2-6, default: 4
  
  // Time Constraints
  breakStartTime: string;               // HH:MM format, default: "13:00"
  breakEndTime: string;                 // HH:MM format, default: "13:45"
  morningSessionRatio: number;          // 30-70, default: 50 (NOT separate sliders)
  
  // Lab & Session Constraints
  defaultLabDurationHours: number;      // 1-4, default: 2
  remedialLecturesPerWeek: number;      // 0-3, default: 1
  allowCrossYearLabConflicts: boolean;  // default: false
}
```

### Generation Interface Component
```typescript
interface GenerationInterface {
  // Main Interface (Always Visible)
  preflightStatus: {
    dataComplete: boolean;
    validationErrors: string[];
    warnings: string[];
  };
  
  primaryActions: {
    previewGeneration: () => Promise<PreviewResult>;  // Dry run
    generateTimetable: () => Promise<GenerationResult>;
  };
  
  // Advanced Options (Collapsed by Default)
  advancedOptions: {
    visible: false;
    algorithm: {
      populationSize: { min: 20, max: 50, default: 30 };
      generations: { min: 100, max: 300, default: 150 };
      mutationRate: { min: 0.1, max: 0.3, default: 0.2 };
    };
    divisionSpecificGeneration: boolean;
    tooltip: "Advanced genetic algorithm parameters. Only modify if you understand the implications.";
  };
}
```

## MISSING FUNCTIONALITY TO ADD

### 1. Data Import/Export
```typescript
// CSV Import for bulk data entry
interface CSVImportFeature {
  teachers: { uploadCSV: true, validateColumns: true, previewBeforeImport: true };
  subjects: { uploadCSV: true, validateColumns: true, previewBeforeImport: true };
  rooms: { uploadCSV: true, validateColumns: true, previewBeforeImport: true };
  timeslots: { uploadCSV: true, validateColumns: true, previewBeforeImport: true };
}

// Timetable Export Options
interface ExportOptions {
  pdf: { byDivision: true, byTeacher: true, printOptimized: true };
  csv: { sessionsList: true, teacherSchedules: true, roomUtilization: true };
  excel: { multiSheet: true, formattedGrid: true };
}
```

### 2. Validation & Error Handling
```typescript
interface ValidationSystem {
  realTimeValidation: true;        // As user types
  bulkValidation: true;            // Before generation
  errorMessages: {                 // Human-friendly, specific messages
    "Room capacity too small": "Room {roomName} (capacity: {capacity}) cannot accommodate {division} with {studentCount} students";
    "Time overlap detected": "Time slot {timeSlot} overlaps with existing slot {existingSlot} on {day}";
    "Missing teacher proficiency": "Teacher {teacherName} has no proficiency data for subject {subjectName}";
  };
  preflightChecks: {
    allRequiredDataPresent: true;
    noConflictingConstraints: true;
    reasonableConfiguration: true;
  };
}
```

### 3. Results & Analysis
```typescript
interface ResultsInterface {
  fitnessScore: number;
  totalViolations: number;
  
  violationBreakdown: {
    type: string;                    // "Room Capacity", "Teacher Conflict", etc.
    count: number;
    severity: "high" | "medium" | "low";
    affectedEntities: string[];      // Teacher names, room names, etc.
    suggestedFixes: string[];        // "Increase room capacity", "Adjust time slot"
  }[];
  
  timetableViews: {
    byDivision: WeeklyGrid[];
    byTeacher: WeeklyGrid[];
    byRoom: WeeklyGrid[];
  };
  
  analytics: {
    teacherWorkloadDistribution: ChartData;
    roomUtilization: ChartData;
    timeSlotPopularity: ChartData;
  };
}
```

## UI/UX REQUIREMENTS

### Design System Requirements
```scss
// Colors (Professional, not flashy)
$primary: #2563eb;           // Professional blue
$secondary: #64748b;         // Muted slate
$success: #059669;           // Success green  
$warning: #d97706;           // Warning amber
$error: #dc2626;             // Error red
$neutral-50: #f8fafc;        // Light background
$neutral-900: #0f172a;       // Dark text

// Typography
$font-primary: 'Inter', sans-serif;
$font-size-base: 16px;       // Readable default
$line-height: 1.5;           // Comfortable reading

// Spacing (8px grid)
$space-xs: 4px;
$space-sm: 8px;
$space-md: 16px;
$space-lg: 24px;
$space-xl: 32px;
```

### Accessibility Requirements
```typescript
interface AccessibilityRequirements {
  keyboardNavigation: "full";       // All features accessible via keyboard
  screenReaderSupport: "complete";  // All elements properly labeled
  colorContrast: "AA";              // WCAG AA compliant
  focusIndicators: "visible";       // Clear focus states
  errorAnnouncement: "immediate";   // Screen readers announce errors
  formLabels: "descriptive";        // Clear, helpful labels
}
```

## BACKEND INTEGRATION REQUIREMENTS

### API Contract Validation
```typescript
interface APIIntegration {
  // Must match backend exactly
  endpoints: {
    "POST /api/teachers": TeacherCreateRequest;
    "PUT /api/teachers/:id": TeacherUpdateRequest;
    "POST /api/system-config": SystemConfigurationCorrect;  // Use corrected values
    "POST /api/generate": {
      dryRun: boolean;
      populationSize: number;    // 20-50
      generations: number;       // 100-300  
      mutationRate: number;      // 0.1-0.3
    };
  };
  
  errorHandling: {
    validation: "400 with specific field errors";
    serverError: "500 with retry option";
    timeout: "Show progress, allow cancellation";
  };
  
  responseValidation: {
    validateFitnessScore: "number";
    validateViolations: "object with breakdown";
    validateGenes: "array of tuples [subject_id, teacher_id, location_id, timeslot_id, batch]";
  };
}
```

## SUCCESS CRITERIA

### User Experience Goals
1. **Timetable incharge can complete setup in < 30 minutes** without training
2. **Zero invalid configurations** can be submitted to backend
3. **Clear error messages** guide users to fix issues
4. **One-click generation** after data setup
5. **Professional appearance** that doesn't look "cheap"

### Technical Goals
1. **100% backend compatibility** - all API calls work correctly
2. **Comprehensive validation** - catch errors before submission
3. **Responsive design** - works on tablets and desktops
4. **Fast performance** - < 3 second page loads
5. **Robust error handling** - graceful degradation

## IMPLEMENTATION PRIORITY

**Phase 1 (Critical - Fix Immediately):**
1. Fix configuration value ranges (teacher workload, session distribution)
2. Hide genetic algorithm parameters in advanced section
3. Add basic form validation for all data entry
4. Fix backend API integration

**Phase 2 (Important - Next Sprint):**
1. Add CSV import functionality
2. Implement comprehensive error handling
3. Add preflight validation checks
4. Improve timetable result display

**Phase 3 (Enhancement - Future):**
1. Advanced analytics and reporting
2. Bulk operations and batch processing
3. Advanced visualization features
4. Multi-language support

## QUALITY GATES

Before marking as complete, verify:
- [ ] All configuration values match backend algorithm constraints exactly
- [ ] Non-technical users never see genetic algorithm parameters in main flow  
- [ ] Every form field has proper validation with helpful error messages
- [ ] CSV import works for teachers, subjects, rooms, and timeslots
- [ ] Timetable generation produces results that match backend API contract
- [ ] Export functionality works for PDF, CSV, and Excel formats
- [ ] System handles missing data gracefully with clear guidance
- [ ] UI looks professional and polished, not "cheap" or amateurish

This frontend must seamlessly integrate with the comprehensive genetic algorithm backend while providing an intuitive, professional experience for timetable incharges.