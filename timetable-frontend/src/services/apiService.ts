// API Service with request management to prevent 429 errors
class ApiService {
  private baseUrl = 'http://localhost:8000/api';
  private cache = new Map<string, { data: any; timestamp: number }>();
  private pendingRequests = new Map<string, Promise<any>>();
  private readonly CACHE_DURATION = 30000; // 30 seconds
  private readonly REQUEST_DELAY = 100; // 100ms between requests

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getCacheKey(url: string): string {
    return url;
  }

  private isValidCache(timestamp: number): boolean {
    return Date.now() - timestamp < this.CACHE_DURATION;
  }

  private async makeRequest(url: string, options?: RequestInit): Promise<any> {
    const cacheKey = this.getCacheKey(url);
    
    // Check cache first
    const cached = this.cache.get(cacheKey);
    if (cached && this.isValidCache(cached.timestamp)) {
      return cached.data;
    }

    // Check if request is already pending
    if (this.pendingRequests.has(cacheKey)) {
      return this.pendingRequests.get(cacheKey);
    }

    // Make new request
    const requestPromise = this.executeRequest(url, options);
    this.pendingRequests.set(cacheKey, requestPromise);

    try {
      const result = await requestPromise;
      
      // Cache successful results
      if (result) {
        this.cache.set(cacheKey, {
          data: result,
          timestamp: Date.now()
        });
      }
      
      return result;
    } finally {
      this.pendingRequests.delete(cacheKey);
    }
  }

  private async executeRequest(url: string, options?: RequestInit): Promise<any> {
    // Add small delay to prevent overwhelming the server
    await this.delay(this.REQUEST_DELAY);

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      }
    });

    if (!response.ok) {
      if (response.status === 429) {
        // Wait longer and retry once for 429 errors
        await this.delay(1000);
        const retryResponse = await fetch(url, options);
        if (!retryResponse.ok) {
          throw new Error(`HTTP ${retryResponse.status}: ${retryResponse.statusText}`);
        }
        return retryResponse.json();
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Public API methods
  async getTeachers(): Promise<any[]> {
    try {
      const data = await this.makeRequest(`${this.baseUrl}/teachers/`);
      return Array.isArray(data) ? data : (data.results || []);
    } catch (error: unknown) {
      console.error('Error fetching teachers:', error);
      return [];
    }
  }

  async getSubjects(): Promise<any[]> {
    try {
      const data = await this.makeRequest(`${this.baseUrl}/subjects/`);
      return Array.isArray(data) ? data : (data.results || []);
    } catch (error: unknown) {
      console.error('Error fetching subjects:', error);
      return [];
    }
  }

  async getTimetable(): Promise<any[]> {
    try {
      const data = await this.makeRequest(`${this.baseUrl}/timetable/`);
      return Array.isArray(data) ? data : [];
    } catch (error: unknown) {
      console.error('Error fetching timetable:', error);
      return [];
    }
  }

  async getConfiguration(): Promise<any | null> {
    try {
      const data = await this.makeRequest(`${this.baseUrl}/timetable-config/`);
      return data.configuration || null;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (errorMessage.includes('404')) {
        return null; // No configuration exists yet
      }
      console.error('Error fetching configuration:', error);
      return null;
    }
  }

  async createConfiguration(config: any): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/timetable-config/`, {
      method: 'POST',
      body: JSON.stringify(config)
    });
  }

  async submitProficiencies(proficiencies: any): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/teacher-preferences/`, {
      method: 'POST',
      body: JSON.stringify({ proficiencies })
    });
  }

  async processResignation(resignationData: any): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/teacher-resignation/`, {
      method: 'POST',
      body: JSON.stringify(resignationData)
    });
  }

  async getDivisions(): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/divisions/`);
  }

  async generateTimetable(): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/generate-timetable/`, {
      method: 'POST',
      body: JSON.stringify({})
    });
  }

  // System Configuration APIs
  async getSystemConfiguration(): Promise<any> {
    try {
      return await this.makeRequest(`${this.baseUrl}/system-configuration/`);
    } catch (error: unknown) {
      console.error('Error fetching system configuration:', error);
      return null;
    }
  }

  async saveSystemConfiguration(config: any): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/system-configuration/`, {
      method: 'POST',
      body: JSON.stringify(config)
    });
  }

  // Remedial Lecture APIs
  async getRemedialLectures(): Promise<any[]> {
    try {
      const data = await this.makeRequest(`${this.baseUrl}/remedial-lectures/`);
      return Array.isArray(data) ? data : [];
    } catch (error: unknown) {
      console.error('Error fetching remedial lectures:', error);
      return [];
    }
  }

  async saveRemedialLecture(remedialData: any): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/remedial-lectures/`, {
      method: 'POST',
      body: JSON.stringify(remedialData)
    });
  }

  // Room Management APIs
  async getRooms(): Promise<any[]> {
    try {
      const data = await this.makeRequest(`${this.baseUrl}/rooms/`);
      return Array.isArray(data) ? data : (data.results || []);
    } catch (error: unknown) {
      console.error('Error fetching rooms:', error);
      return [];
    }
  }

  async updateRoom(roomId: number, roomData: any): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/rooms/${roomId}/`, {
      method: 'PATCH',
      body: JSON.stringify(roomData)
    });
  }

  // Subject Management APIs  
  async updateSubject(subjectId: number, subjectData: any): Promise<any> {
    return this.makeRequest(`${this.baseUrl}/subjects/${subjectId}/`, {
      method: 'PATCH',
      body: JSON.stringify(subjectData)
    });
  }

  // Clear cache when needed
  clearCache(): void {
    this.cache.clear();
  }

  // Get cache status for debugging
  getCacheStatus(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
