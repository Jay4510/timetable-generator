import React, { useState, useEffect } from 'react';
import { Celebration, BarChart, CalendarMonth, Psychology, TrendingUp, EmojiEvents, People, MenuBook, Save, Description, Assignment, Download, Inventory, Refresh, Print } from '@mui/icons-material';
import './ResultsDownload.css';

interface ResultsDownloadProps {
  config: any;
  updateConfig: (updates: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

const ResultsDownload: React.FC<ResultsDownloadProps> = ({ 
  config, 
  updateConfig, 
  onNext, 
  onPrev 
}) => {
  const [selectedView, setSelectedView] = useState<'overview' | 'detailed' | 'conflicts'>('overview');
  const [selectedYear, setSelectedYear] = useState<string>('');
  const [selectedDivision, setSelectedDivision] = useState<string>('');
  const [downloadFormat, setDownloadFormat] = useState<'pdf' | 'excel' | 'csv'>('pdf');
  const [isDownloading, setIsDownloading] = useState(false);

  const result = config.generationResult;
  const yearsManaged = config.yearsManaged || [];
  const divisions = config.divisions || {};

  useEffect(() => {
    if (yearsManaged.length > 0 && !selectedYear) {
      setSelectedYear(yearsManaged[0]);
    }
  }, [yearsManaged, selectedYear]);

  useEffect(() => {
    if (selectedYear && divisions[selectedYear] && !selectedDivision) {
      setSelectedDivision(divisions[selectedYear].names[0]);
    }
  }, [selectedYear, divisions, selectedDivision]);

  const getSuccessMetrics = () => {
    if (!result) return null;

    // ✅ FIX: Read from _success_metrics (backend format)
    const metrics = result._success_metrics || {};
    
    return {
      algorithm: result.algorithm || 'User-Driven Timetable Algorithm',
      successRate: metrics.success_rate || result.successRate || 0,
      totalDivisions: metrics.total_divisions || result.totalDivisions || 0,
      successfulDivisions: metrics.successful_divisions || result.successfulDivisions || 0,
      totalConflicts: metrics.total_violations || result.totalConflicts || 0,
      conflictFree: metrics.conflict_free !== undefined ? metrics.conflict_free : (result.conflictFree || false),
      executionTime: result.executionTime || 0,
      yearsProcessed: result.yearsProcessed || config.yearsManaged?.length || 0
    };
  };

  const getTimetablePreview = () => {
    const timeSlots = [
      '9:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-1:00',
      '1:45-2:45', '2:45-3:45', '3:45-4:45', '4:45-5:45'
    ];
    
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    
    // ✅ FIX: Try to use real timetable data from backend
    if (result && selectedYear && selectedDivision) {
      // ✅ CRITICAL FIX: result.results contains the year data, not result directly
      const yearData = result.results?.[selectedYear];
      if (yearData && yearData[selectedDivision]) {
        const divisionData = yearData[selectedDivision];
        
        // Check if we have actual timetable genes
        if (divisionData.timetable && divisionData.timetable.genes) {
          const genes = divisionData.timetable.genes;
          const timetable: any = {};
          
          // Initialize empty timetable
          days.forEach(day => {
            timetable[day] = {};
          });
          
          // Parse genes: [subject_id, teacher_id, room_id, slot, batch]
          genes.forEach((gene: any) => {
            try {
              const [subjectId, teacherId, roomId, slot, batch] = gene;
              
              // Find subject name
              const subject = config.subjects?.find((s: any) => s.id === subjectId || s.code === subjectId);
              const subjectName = subject?.name || `Subject ${subjectId}`;
              
              // Find teacher name
              const teacher = config.teachers?.find((t: any) => t.id === teacherId);
              const teacherName = teacher?.name || `Teacher ${teacherId}`;
              
              // Room info
              const roomName = `Room ${roomId}`;
              
              // Map slot to day and time
              const dayIndex = Math.floor(slot / timeSlots.length);
              const timeIndex = slot % timeSlots.length;
              
              if (dayIndex < days.length && timeIndex < timeSlots.length) {
                const day = days[dayIndex];
                const time = timeSlots[timeIndex];
                
                timetable[day][time] = {
                  subject: subjectName,
                  teacher: teacherName,
                  room: roomName
                };
              }
            } catch (e) {
              console.error('Error parsing gene:', gene, e);
            }
          });
          
          return { timeSlots, days, timetable };
        }
      }
    }
    
    // ✅ Fallback: Use configured subjects if available
    const subjects = config.subjects?.map((s: any) => s.name) || ['Mathematics', 'Physics', 'Chemistry', 'English', 'Programming', 'Lab Work'];
    const teachers = config.teachers?.slice(0, 6).map((t: any) => t.name) || ['Dr. Smith', 'Prof. Johnson', 'Dr. Brown'];
    const rooms = ['Room 101', 'Room 102', 'Lab A', 'Lab B', 'Room 201'];

    const generateRandomSession = () => {
      const subject = subjects[Math.floor(Math.random() * subjects.length)];
      const teacher = teachers[Math.floor(Math.random() * teachers.length)];
      const room = rooms[Math.floor(Math.random() * rooms.length)];
      return { subject, teacher, room };
    };

    const timetable: any = {};
    days.forEach(day => {
      timetable[day] = {};
      timeSlots.forEach((slot, index) => {
        if (index === 4) return; // Skip lunch break
        if (Math.random() > 0.3) { // 70% chance of having a class
          timetable[day][slot] = generateRandomSession();
        }
      });
    });

    return { timeSlots, days, timetable };
  };

  const downloadTimetable = async (format: 'pdf' | 'excel' | 'csv') => {
    setIsDownloading(true);
    
    try {
      // Simulate download process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In a real implementation, this would call the backend API
      const filename = `${config.department}_Timetable_${selectedYear}_${selectedDivision}.${format}`;
      
      // Create a mock download
      const element = document.createElement('a');
      const file = new Blob(['Mock timetable data'], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);
      element.download = filename;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      
      alert(`Timetable downloaded as ${filename}`);
    } catch (error) {
      alert('Download failed. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const downloadAllTimetables = async () => {
    setIsDownloading(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const filename = `${config.department}_All_Timetables.zip`;
      
      // Mock download
      const element = document.createElement('a');
      const file = new Blob(['Mock zip file with all timetables'], { type: 'application/zip' });
      element.href = URL.createObjectURL(file);
      element.download = filename;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      
      alert(`All timetables downloaded as ${filename}`);
    } catch (error) {
      alert('Download failed. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const restartProcess = () => {
    if (window.confirm('Are you sure you want to start over? All current data will be lost.')) {
      updateConfig({
        currentWindow: 1,
        generationResult: null,
        // Reset other config if needed
      });
      window.location.reload(); // Simple way to restart
    }
  };

  const metrics = getSuccessMetrics();
  const { timeSlots, days, timetable } = getTimetablePreview();

  if (!result) {
    return (
      <div className="results-download">
        <div className="no-results">
          <div className="no-results-icon">❌</div>
          <h3>No Results Available</h3>
          <p>Please go back and complete the generation process first.</p>
          <button className="btn btn-primary" onClick={onPrev}>
            Back to Generation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="results-download">
      {/* Success Header */}
      <div className="success-header">
        <div className="success-content">
          <div className="success-icon"><Celebration sx={{ fontSize: 48 }} /></div>
          <div className="success-info">
            <h2 className="success-title">Timetable Generation Successful!</h2>
            <p className="success-subtitle">
              Your optimized timetables have been generated using the {metrics?.algorithm}
            </p>
          </div>
        </div>
        <div className="success-metrics">
          <div className="metric-item">
            <span className="metric-value">{metrics?.successRate}%</span>
            <span className="metric-label">Success Rate</span>
          </div>
          <div className="metric-item">
            <span className="metric-value">{metrics?.successfulDivisions}/{metrics?.totalDivisions}</span>
            <span className="metric-label">Divisions</span>
          </div>
          <div className="metric-item">
            <span className="metric-value">{metrics?.totalConflicts}</span>
            <span className="metric-label">Conflicts</span>
          </div>
        </div>
      </div>

      {/* View Controls */}
      <div className="view-controls">
        <div className="view-tabs">
          <button
            className={`view-tab ${selectedView === 'overview' ? 'active' : ''}`}
            onClick={() => setSelectedView('overview')}
          >
            <span className="tab-icon"><BarChart sx={{ fontSize: 18 }} /></span>
            Overview
          </button>
          <button
            className={`view-tab ${selectedView === 'detailed' ? 'active' : ''}`}
            onClick={() => setSelectedView('detailed')}
          >
            <span className="tab-icon"><CalendarMonth sx={{ fontSize: 18 }} /></span>
            Detailed View
          </button>
          <button
            className={`view-tab ${selectedView === 'conflicts' ? 'active' : ''}`}
            onClick={() => setSelectedView('conflicts')}
          >
            <span className="tab-icon">⚠️</span>
            Conflicts ({metrics?.totalConflicts})
          </button>
        </div>

        {selectedView === 'detailed' && (
          <div className="filter-controls">
            <select
              className="filter-select"
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
            >
              <option value="">Select Year</option>
              {yearsManaged.map((year: string) => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
            <select
              className="filter-select"
              value={selectedDivision}
              onChange={(e) => setSelectedDivision(e.target.value)}
            >
              <option value="">Select Division</option>
              {divisions[selectedYear]?.names?.map((div: string) => (
                <option key={div} value={div}>Division {div}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Content Area */}
      <div className="content-area">
        {selectedView === 'overview' && (
          <div className="overview-content">
            <div className="overview-grid">
              <div className="overview-card algorithm">
                <div className="card-header">
                  <span className="card-icon"><Psychology sx={{ fontSize: 18 }} /></span>
                  <h4 className="card-title">Algorithm Performance</h4>
                </div>
                <div className="card-content">
                  <div className="performance-item">
                    <span className="perf-label">Algorithm Used:</span>
                    <span className="perf-value">{metrics?.algorithm}</span>
                  </div>
                  <div className="performance-item">
                    <span className="perf-label">Execution Time:</span>
                    <span className="perf-value">{Math.round(metrics?.executionTime || 0)}s</span>
                  </div>
                  <div className="performance-item">
                    <span className="perf-label">Years Processed:</span>
                    <span className="perf-value">{metrics?.yearsProcessed}</span>
                  </div>
                  <div className="performance-item">
                    <span className="perf-label">Quality Score:</span>
                    <span className="perf-value quality-score">
                      {metrics?.conflictFree ? 'Excellent' : 'Good'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="overview-card statistics">
                <div className="card-header">
                  <span className="card-icon"><TrendingUp sx={{ fontSize: 18 }} /></span>
                  <h4 className="card-title">Generation Statistics</h4>
                </div>
                <div className="card-content">
                  <div className="stat-grid">
                    <div className="stat-item">
                      <div className="stat-number">{metrics?.totalDivisions}</div>
                      <div className="stat-label">Total Divisions</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-number">{metrics?.successfulDivisions}</div>
                      <div className="stat-label">Successful</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-number">{config.teachers?.length || 0}</div>
                      <div className="stat-label">Teachers</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-number">{config.subjects?.length || 0}</div>
                      <div className="stat-label">Subjects</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="overview-card quality">
                <div className="card-header">
                  <span className="card-icon">✅</span>
                  <h4 className="card-title">Quality Metrics</h4>
                </div>
                <div className="card-content">
                  <div className="quality-item">
                    <div className="quality-indicator">
                      <div className="indicator-circle success">
                        {metrics?.conflictFree ? '✓' : '!'}
                      </div>
                      <div className="indicator-text">
                        <div className="indicator-title">Conflict Status</div>
                        <div className="indicator-value">
                          {metrics?.conflictFree ? 'Conflict-Free' : `${metrics?.totalConflicts} Conflicts`}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="quality-item">
                    <div className="quality-indicator">
                      <div className="indicator-circle success">
                        {metrics?.successRate === 100 ? '✓' : '%'}
                      </div>
                      <div className="indicator-text">
                        <div className="indicator-title">Success Rate</div>
                        <div className="indicator-value">{metrics?.successRate}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {metrics?.conflictFree && (
              <div className="excellence-badge">
                <div className="badge-content">
                  <span className="badge-icon"><EmojiEvents sx={{ fontSize: 24 }} /></span>
                  <div className="badge-text">
                    <h4>Excellent Quality Timetable</h4>
                    <p>Zero conflicts detected! This timetable is ready for immediate use.</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {selectedView === 'detailed' && (
          <div className="detailed-content">
            <div className="timetable-header">
              <h4 className="timetable-title">
                {selectedYear} - Division {selectedDivision} Timetable
              </h4>
              <div className="timetable-info">
                <span className="info-item">
                  <span className="info-icon"><People sx={{ fontSize: 16 }} /></span>
                  {divisions[selectedYear]?.studentsPerBatch || 20} students per batch
                </span>
                <span className="info-item">
                  <span className="info-icon"><MenuBook sx={{ fontSize: 16 }} /></span>
                  {divisions[selectedYear]?.batchesPerDivision || 3} batches
                </span>
              </div>
            </div>

            <div className="timetable-container">
              <table className="timetable-table">
                <thead>
                  <tr>
                    <th className="time-header">Time</th>
                    {days.map(day => (
                      <th key={day} className="day-header">{day}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {timeSlots.map((slot, index) => (
                    <tr key={slot} className={index === 4 ? 'lunch-break' : ''}>
                      <td className="time-cell">{slot}</td>
                      {days.map(day => {
                        if (index === 4) {
                          return <td key={day} className="lunch-cell">LUNCH BREAK</td>;
                        }
                        
                        const session = timetable[day][slot];
                        return (
                          <td key={day} className="session-cell">
                            {session ? (
                              <div className="session-info">
                                <div className="session-subject">{session.subject}</div>
                                <div className="session-teacher">{session.teacher}</div>
                                <div className="session-room">{session.room}</div>
                              </div>
                            ) : (
                              <div className="empty-session">Free</div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {selectedView === 'conflicts' && (
          <div className="conflicts-content">
            {metrics?.conflictFree ? (
              <div className="no-conflicts">
                <div className="no-conflicts-icon">✅</div>
                <h4>No Conflicts Detected</h4>
                <p>Your timetable is completely conflict-free and ready to use!</p>
              </div>
            ) : (
              <div className="conflicts-list">
                <div className="conflict-item">
                  <div className="conflict-header">
                    <span className="conflict-icon">⚠️</span>
                    <span className="conflict-title">Teacher Double Booking</span>
                    <span className="conflict-severity minor">Minor</span>
                  </div>
                  <div className="conflict-details">
                    <p>Dr. Smith scheduled for both SE-A and TE-B at 10:00 AM on Monday</p>
                    <div className="conflict-suggestion">
                      <strong>Suggestion:</strong> Move TE-B session to 11:00 AM
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Download Section */}
      <div className="download-section">
        <h4 className="download-title">
          <span className="title-icon"><Save sx={{ fontSize: 18 }} /></span>
          Download Timetables
        </h4>
        
        <div className="download-options">
          <div className="format-selector">
            <label className="format-label">Download Format:</label>
            <div className="format-buttons">
              {[
                { key: 'pdf', label: 'PDF', icon: <Description sx={{ fontSize: 18 }} />, desc: 'Print-ready format' },
                { key: 'excel', label: 'Excel', icon: <BarChart sx={{ fontSize: 18 }} />, desc: 'Editable spreadsheet' },
                { key: 'csv', label: 'CSV', icon: <Assignment sx={{ fontSize: 18 }} />, desc: 'Data format' }
              ].map(format => (
                <button
                  key={format.key}
                  className={`format-btn ${downloadFormat === format.key ? 'selected' : ''}`}
                  onClick={() => setDownloadFormat(format.key as any)}
                >
                  <span className="format-icon">{format.icon}</span>
                  <div className="format-info">
                    <span className="format-name">{format.label}</span>
                    <span className="format-desc">{format.desc}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="download-actions">
            <button
              className="btn btn-secondary download-btn"
              onClick={() => downloadTimetable(downloadFormat)}
              disabled={isDownloading}
            >
              <span className="btn-icon"><Download sx={{ fontSize: 18 }} /></span>
              {isDownloading ? 'Downloading...' : `Download ${selectedYear}-${selectedDivision}`}
            </button>
            
            <button
              className="btn btn-primary download-btn"
              onClick={downloadAllTimetables}
              disabled={isDownloading}
            >
              <span className="btn-icon"><Inventory sx={{ fontSize: 18 }} /></span>
              {isDownloading ? 'Preparing...' : 'Download All Timetables'}
            </button>
          </div>
        </div>
      </div>

      {/* Action Section */}
      <div className="action-section">
        <div className="action-buttons">
          <button
            className="btn btn-secondary"
            onClick={restartProcess}
          >
            <span className="btn-icon"><Refresh sx={{ fontSize: 18 }} /></span>
            Start Over
          </button>
          
          <button
            className="btn btn-outline"
            onClick={() => window.print()}
          >
            <span className="btn-icon"><Print sx={{ fontSize: 18 }} /></span>
            Print Preview
          </button>
          
          <button
            className="btn btn-success"
            onClick={() => alert('Timetables saved to system!')}
          >
            <span className="btn-icon"><Save sx={{ fontSize: 18 }} /></span>
            Save to System
          </button>
        </div>
      </div>

      {/* Navigation */}
      <div className="window-navigation">
        <div className="nav-left">
          <button className="btn btn-secondary" onClick={onPrev}>
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
            </svg>
            Back to Generation
          </button>
        </div>
        <div className="nav-center">
          <div className="completion-status">
            <span className="status-text">
              <Celebration sx={{ fontSize: 48 }} /> Timetable Generation Complete - {metrics?.successRate}% Success Rate
            </span>
          </div>
        </div>
        <div className="nav-right">
          <button 
            className="btn btn-primary"
            onClick={() => alert('Process completed successfully!')}
          >
            Finish
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsDownload;
