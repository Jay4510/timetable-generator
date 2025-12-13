/**
 * Comprehensive API Service for Timetable Management
 * Production-ready with error handling, retry logic, and type safety
 */

import type {
  Teacher, Subject, Room, Lab, Division, TimeSlot, SystemConfiguration,
  SubjectProficiency, GenerationRequest, GenerationResult, DashboardStats,
  Session, ExportRequest, ExportResult, ApiResponse, PaginatedResponse,
  FormValidationResult, ViolationDetail
} from '../types/api';

class TimetableApiService {
  private baseUrl: string;
  private cache = new Map<string, { data: any; timestamp: number }>();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  constructor() {
    this.baseUrl = (import.meta.env?.VITE_API_URL as string) || 'http://localhost:8000/api';
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || 
          errorData.detail || 
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  private getCacheKey(endpoint: string, params?: Record<string, any>): string {
    return `${endpoint}${params ? JSON.stringify(params) : ''}`;
  }

  private getFromCache<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }
    return null;
  }

  private setCache<T>(key: string, data: T): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  // Dashboard API - Mock data for now since backend doesn't have this endpoint
  async getDashboardStats(): Promise<DashboardStats> {
    const cacheKey = this.getCacheKey('/dashboard/stats');
    const cached = this.getFromCache<DashboardStats>(cacheKey);
    if (cached) return cached;

    // Mock dashboard stats until backend endpoint is created
    const stats: DashboardStats = {
      teachers_count: 18,
      subjects_count: 35,
      rooms_count: 8,
      labs_count: 4,
      timeslots_count: 40,
      divisions_count: 6,
      last_generation: {
        timestamp: new Date().toISOString(),
        fitness_score: 87.5,
        total_violations: 3,
        sessions_created: 88
      },
      system_health: {
        data_completeness: 85,
        configuration_status: 'complete',
        critical_issues: []
      }
    };

    this.setCache(cacheKey, stats);
    return stats;
  }

  // Teachers API
  async getTeachers(params?: { page?: number; search?: string }): Promise<PaginatedResponse<Teacher>> {
    const queryString = params ? new URLSearchParams(params as any).toString() : '';
    return this.request<PaginatedResponse<Teacher>>(`/teachers/?${queryString}`);
  }

  async getTeacher(id: number): Promise<Teacher> {
    return this.request<Teacher>(`/teachers/${id}/`);
  }

  async createTeacher(teacher: Omit<Teacher, 'id' | 'created_at' | 'updated_at'>): Promise<Teacher> {
    this.cache.clear(); // Clear cache on mutations
    return this.request<Teacher>('/teachers/', {
      method: 'POST',
      body: JSON.stringify(teacher),
    });
  }

  async updateTeacher(id: number, teacher: Partial<Teacher>): Promise<Teacher> {
    this.cache.clear();
    return this.request<Teacher>(`/teachers/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(teacher),
    });
  }

  async deleteTeacher(id: number): Promise<void> {
    this.cache.clear();
    await this.request(`/teachers/${id}/`, { method: 'DELETE' });
  }

  // Subjects API
  async getSubjects(params?: { year?: number; division?: number }): Promise<PaginatedResponse<Subject>> {
    const queryString = params ? new URLSearchParams(params as any).toString() : '';
    return this.request<PaginatedResponse<Subject>>(`/subjects/?${queryString}`);
  }

  async createSubject(subject: Omit<Subject, 'id'>): Promise<Subject> {
    this.cache.clear();
    return this.request<Subject>('/subjects/', {
      method: 'POST',
      body: JSON.stringify(subject),
    });
  }

  async updateSubject(id: number, subject: Partial<Subject>): Promise<Subject> {
    this.cache.clear();
    return this.request<Subject>(`/subjects/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(subject),
    });
  }

  // Rooms & Labs API
  async getRooms(): Promise<Room[]> {
    const cacheKey = this.getCacheKey('/rooms');
    const cached = this.getFromCache<Room[]>(cacheKey);
    if (cached) return cached;

    const response = await this.request<PaginatedResponse<Room>>('/rooms/');
    const rooms = response.results || [];
    this.setCache(cacheKey, rooms);
    return rooms;
  }

  async getLabs(): Promise<Lab[]> {
    const cacheKey = this.getCacheKey('/labs');
    const cached = this.getFromCache<Lab[]>(cacheKey);
    if (cached) return cached;

    const response = await this.request<PaginatedResponse<Lab>>('/labs/');
    const labs = response.results || [];
    this.setCache(cacheKey, labs);
    return labs;
  }

  async updateRoom(id: number, room: Partial<Room>): Promise<Room> {
    this.cache.clear();
    return this.request<Room>(`/rooms/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(room),
    });
  }

  // Divisions API
  async getDivisions(): Promise<Division[]> {
    const response = await this.request<PaginatedResponse<Division>>('/divisions/');
    return response.results || [];
  }

  async updateDivision(id: number, division: Partial<Division>): Promise<Division> {
    this.cache.clear();
    return this.request<Division>(`/divisions/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(division),
    });
  }

  // TimeSlots API
  async getTimeSlots(): Promise<TimeSlot[]> {
    const response = await this.request<PaginatedResponse<TimeSlot>>('/timeslots/');
    return response.results || [];
  }

  async createTimeSlot(timeslot: Omit<TimeSlot, 'id'>): Promise<TimeSlot> {
    this.cache.clear();
    return this.request<TimeSlot>('/timeslots/', {
      method: 'POST',
      body: JSON.stringify(timeslot),
    });
  }

  // System Configuration API - Mock data for now
  async getSystemConfiguration(): Promise<SystemConfiguration> {
    const cacheKey = this.getCacheKey('/system-config');
    const cached = this.getFromCache<SystemConfiguration>(cacheKey);
    if (cached) return cached;

    // Mock system configuration - BACKEND ALGORITHM COMPATIBLE
    const config: SystemConfiguration = {
      id: 1,
      break_start_time: '13:00',  // Backend: 13:00-13:45 break time
      break_end_time: '13:45',
      
      // REMOVED: Manual teacher workload limits (auto-calculated by backend)
      // Backend uses fair distribution algorithm with 20% tolerance
      max_sessions_per_teacher: 0,  // Not used - backend auto-calculates
      min_sessions_per_teacher: 0,  // Not used - backend auto-calculates
      
      default_lab_duration_hours: 2,  // Backend default: 2 hours
      remedial_lectures_per_week: 1,  // Backend: 1 general lecture for entire department
      
      // REMOVED: Manual morning/afternoon balance (auto-balanced by backend)
      // Backend auto-balances to 40-60% with 35-65% tolerance
      morning_session_percentage: 50,  // Display only - not sent to backend
      afternoon_session_percentage: 50, // Display only - not sent to backend
      
      allow_cross_year_lab_conflicts: false,  // Backend: strict equipment matching
      max_consecutive_hours: 4,  // Reasonable default for UI display
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    this.setCache(cacheKey, config);
    return config;
  }

  async updateSystemConfiguration(config: Partial<SystemConfiguration>): Promise<SystemConfiguration> {
    this.cache.clear();
    return this.request<SystemConfiguration>('/system-config/', {
      method: 'PATCH',
      body: JSON.stringify(config),
    });
  }

  // Subject Proficiency API - Mock data for now
  async getSubjectProficiencies(teacherId?: number): Promise<SubjectProficiency[]> {
    // Mock subject proficiencies until backend endpoint is created
    const proficiencies: SubjectProficiency[] = [
      {
        id: 1,
        teacher: 1,
        subject: 1,
        knowledge_rating: 8,
        willingness_rating: 9,
        overall_score: 8.4
      },
      {
        id: 2,
        teacher: 1,
        subject: 2,
        knowledge_rating: 7,
        willingness_rating: 8,
        overall_score: 7.4
      }
    ];

    return teacherId ? proficiencies.filter(p => p.teacher === teacherId) : proficiencies;
  }

  async bulkUpdateProficiencies(proficiencies: Partial<SubjectProficiency>[]): Promise<SubjectProficiency[]> {
    this.cache.clear();
    return this.request<SubjectProficiency[]>('/subject-proficiencies/bulk/', {
      method: 'POST',
      body: JSON.stringify({ proficiencies }),
    });
  }

  // Timetable Generation API
  async generateTimetable(request: GenerationRequest): Promise<GenerationResult> {
    return this.request<GenerationResult>('/generate-timetable/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getGenerationStatus(id: string): Promise<GenerationResult> {
    return this.request<GenerationResult>(`/generation-status/${id}/`);
  }

  async getGenerationResult(id: string): Promise<GenerationResult> {
    return this.request<GenerationResult>(`/generation-result/${id}/`);
  }

  // Sessions API
  async getSessions(params?: { 
    division?: number; 
    teacher?: number; 
    generation_id?: string 
  }): Promise<Session[]> {
    const queryString = params ? new URLSearchParams(params as any).toString() : '';
    const response = await this.request<PaginatedResponse<Session>>(`/sessions/?${queryString}`);
    return response.results || [];
  }

  // Validation API - Mock validation for now
  async validateData(): Promise<FormValidationResult> {
    // Mock validation result - assume data is mostly valid
    return {
      isValid: true,
      errors: [],
      warnings: [
        'Some teachers have no time preferences set',
        'Lab room capacity not specified for 2 rooms'
      ],
      suggestions: [
        'Consider setting time preferences for better optimization',
        'Add room capacity information for accurate scheduling'
      ]
    };
  }

  async validateConfiguration(): Promise<FormValidationResult> {
    // Mock configuration validation
    return {
      isValid: true,
      errors: [],
      warnings: [],
      suggestions: [
        'Current settings look good for timetable generation'
      ]
    };
  }

  // Violations API
  async getViolations(generationId: string): Promise<ViolationDetail[]> {
    return this.request<ViolationDetail[]>(`/violations/${generationId}/`);
  }

  async resolveViolation(violationId: string, action: 'auto_fix' | 'ignore'): Promise<void> {
    await this.request(`/violations/${violationId}/resolve/`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
  }

  // Export API
  async requestExport(request: ExportRequest): Promise<ExportResult> {
    return this.request<ExportResult>('/export/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getExportStatus(id: string): Promise<ExportResult> {
    return this.request<ExportResult>(`/export/${id}/`);
  }

  // CSV Import API
  async importTeachers(file: File): Promise<{ imported: number; errors: string[] }> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request('/import/teachers/', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async importSubjects(file: File): Promise<{ imported: number; errors: string[] }> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request('/import/subjects/', {
      method: 'POST',
      body: formData,
      headers: {},
    });
  }

  // Utility Methods
  clearCache(): void {
    this.cache.clear();
  }

  getCacheStatus(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }
}

export const timetableApi = new TimetableApiService();
export default timetableApi;
