/**
 * Comprehensive TypeScript API Contracts
 * Matches backend models and genetic algorithm outputs
 */

// Core Entity Types
export interface Teacher {
  id: number;
  name: string;
  email: string;
  phone?: string;
  department?: string;
  max_sessions_per_week: number;
  min_sessions_per_week: number;
  time_preference: 'morning' | 'afternoon' | 'no_preference';
  available: boolean;
  created_at: string;
  updated_at: string;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  year: number;
  division: number;
  sessions_per_week: number;
  requires_lab: boolean;
  lecture_duration_hours: number;
  lab_frequency_per_week: number;
  requires_remedial: boolean;
  equipment_requirements: string[];
}

export interface Room {
  id: number;
  name: string;
  capacity: number;
  room_type: string;
  available: boolean;
  available_equipment: string[];
}

export interface Lab {
  id: number;
  name: string;
  capacity: number;
  lab_type: string;
  available_equipment: string[];
}

export interface Division {
  id: number;
  year: number;
  name: string;
  num_batches: number;
  student_count: number;
}

export interface TimeSlot {
  id: number;
  day_of_week: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday';
  start_time: string;
  end_time: string;
  slot_type: 'lecture' | 'lab';
}

export interface SystemConfiguration {
  id: number;
  break_start_time: string;
  break_end_time: string;
  max_sessions_per_teacher: number;
  min_sessions_per_teacher: number;
  default_lab_duration_hours: number;
  remedial_lectures_per_week: number;
  morning_session_percentage: number;
  afternoon_session_percentage: number;
  allow_cross_year_lab_conflicts: boolean;
  max_consecutive_hours: number;
  created_at: string;
  updated_at: string;
}

export interface SubjectProficiency {
  id: number;
  teacher: number;
  subject: number;
  knowledge_rating: number; // 1-10
  willingness_rating: number; // 1-10
  overall_score: number; // Calculated: 60% knowledge + 40% willingness
}

// Generation Types
export interface GenerationRequest {
  dry_run?: boolean;
  use_division_specific?: boolean;
  algorithm_type?: 'comprehensive' | 'division_specific' | 'improved';
  population_size?: number;
  generations?: number;
  mutation_rate?: number;
}

export interface GenerationGene {
  subject_id: number;
  teacher_id: number;
  location_id: number;
  timeslot_id: number;
  batch?: string;
}

export interface ConstraintViolation {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  count: number;
  details: string;
  affected_entities: {
    teachers?: number[];
    subjects?: number[];
    rooms?: number[];
    timeslots?: number[];
  };
}

export interface GenerationResult {
  id: string;
  status: 'running' | 'completed' | 'failed';
  fitness_score: number;
  total_violations: number;
  violations_by_type: Record<string, number>;
  constraint_details: Record<string, any>;
  genes: GenerationGene[];
  sessions_created: number;
  algorithm_used: string;
  execution_time_seconds: number;
  created_at: string;
}

export interface Session {
  id: number;
  subject: Subject;
  teacher: Teacher;
  room?: Room;
  lab?: Lab;
  timeslot: TimeSlot;
  division: Division;
  batch?: string;
  created_at: string;
}

// Dashboard Types
export interface DashboardStats {
  teachers_count: number;
  subjects_count: number;
  rooms_count: number;
  labs_count: number;
  timeslots_count: number;
  divisions_count: number;
  last_generation?: {
    timestamp: string;
    fitness_score: number;
    total_violations: number;
    sessions_created: number;
  };
  system_health: {
    data_completeness: number; // 0-100%
    configuration_status: 'complete' | 'partial' | 'missing';
    critical_issues: string[];
  };
}

// Form Validation Types
export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface FormValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: string[];
}

// Export Types
export interface ExportRequest {
  format: 'pdf' | 'csv' | 'json';
  scope: 'all' | 'division' | 'teacher';
  entity_id?: number;
  include_violations?: boolean;
}

export interface ExportResult {
  id: string;
  status: 'processing' | 'completed' | 'failed';
  download_url?: string;
  file_size?: number;
  created_at: string;
}

// API Response Wrappers
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

// Equipment Management
export interface EquipmentItem {
  id: string;
  name: string;
  category: 'projector' | 'computer' | 'lab_equipment' | 'audio_visual' | 'other';
  description?: string;
}

export interface EquipmentAssignment {
  room_id?: number;
  lab_id?: number;
  equipment_ids: string[];
}

export interface EquipmentRequirement {
  subject_id: number;
  required_equipment: string[];
  priority: 'required' | 'preferred' | 'optional';
}

// Conflict Resolution
export interface ConflictSuggestion {
  type: 'timeslot_change' | 'room_change' | 'teacher_change';
  description: string;
  impact_score: number;
  auto_applicable: boolean;
  changes: {
    entity_type: string;
    entity_id: number;
    field: string;
    old_value: any;
    new_value: any;
  }[];
}

export interface ViolationDetail {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affected_sessions: number[];
  suggestions: ConflictSuggestion[];
  can_auto_fix: boolean;
}
