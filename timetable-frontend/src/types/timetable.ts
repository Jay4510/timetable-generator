// src/types/timetable.ts

export interface ClassConfig {
  name: string;
  selected: boolean;
  divisions: number;
}

export interface WelcomeData {
  department: string;
  academicYear: string;
  classes: ClassConfig[];
}

export interface TimingData {
  startTime: string;
  slotDuration: number;
  recessAfterSlot: number;
  recessDuration: number;
  totalSlots: number;
  workingDays: string[];
}

export interface TheorySubject {
  id: string;
  name: string;
  code: string;
  year: string;
  weeklyLoad: number;
  type: 'Theory' | 'Elective';
}

export interface LabSubject {
  id: string;
  name: string;
  code: string;
  year: string;
  batchCount: number;
  sessionsPerWeek: number;
  durationPerSession: number;
  isSpecial: boolean;
  type: 'Lab' | 'Tutorial';
}

export interface CurriculumData {
  theorySubjects: TheorySubject[];
  labSubjects: LabSubject[];
}

export interface InfrastructureData {
  theoryRooms: string[];
  labRooms: string[];
  specialAssignments: Record<string, string>;
}

export interface Faculty {
  id: string;
  name: string;
  shortCode: string;
  role: 'HOD' | 'Div Incharge' | 'Faculty';
  experience: number;
  shift: '9-5' | '10-6';
}

export interface FacultyData {
  faculty: Faculty[];
}

export interface SubjectAllocation {
  subjectId: string;
  subjectName: string;
  divisions: Record<string, string | null>;
}

export interface WorkloadData {
  preferences: Record<string, string[]>;
  allocations: SubjectAllocation[];
}

export interface ConstraintsData {
  labEquipmentMapping: Record<string, string[]>;
  homeRoomAssignments: Record<string, string>;
  shiftBias: Record<string, 'morning' | 'afternoon'>;
}

export interface BackendBatch {
  batch?: string;
  subject: string;
  teacher: string;
  room: string;
}

export interface BackendEntry {
  slot: number;
  duration: number;
  // UPDATED: Added MATHS_TUT
  type: "THEORY" | "LAB" | "PROJECT" | "REMEDIAL" | "ELECTIVE" | "TUTORIAL" | "MATHS_TUT";
  subject: string;
  teacher: string;
  room: string;
  batches?: BackendBatch[];
}

export interface ResultsData {
  totalGaps: number;
  unplacedLectures: number;
  fitnessScore: number;
  timetable: Record<string, Record<string, BackendEntry[]>> | null;
}

export interface TimetableFormData {
  welcome: WelcomeData;
  timing: TimingData;
  curriculum: CurriculumData;
  infrastructure: InfrastructureData;
  faculty: FacultyData;
  workload: WorkloadData;
  constraints: ConstraintsData;
  generation: any; 
  results: ResultsData;
}

export const INITIAL_FORM_DATA: TimetableFormData = {
  welcome: {
    department: '',
    academicYear: '2024-25',
    classes: [
      { name: 'SE', selected: false, divisions: 1 },
      { name: 'TE', selected: false, divisions: 1 },
      { name: 'BE', selected: false, divisions: 1 },
    ],
  },
  timing: {
    startTime: '09:00',
    slotDuration: 60,
    recessAfterSlot: 4,
    recessDuration: 45,
    totalSlots: 9,
    workingDays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  },
  curriculum: {
    theorySubjects: [],
    labSubjects: [],
  },
  infrastructure: {
    theoryRooms: [],
    labRooms: [],
    specialAssignments: {},
  },
  faculty: {
    faculty: [],
  },
  workload: {
    preferences: {},
    allocations: [],
  },
  constraints: {
    labEquipmentMapping: {},
    homeRoomAssignments: {},
    shiftBias: {},
  },
  generation: {},
  results: {
    totalGaps: 0,
    unplacedLectures: 0,
    fitnessScore: 0,
    timetable: null,
  },
};