import React from 'react';
import { WbSunny, WbTwilight, Sync, MenuBook, Science, TrackChanges, Person, BarChart, Lightbulb } from '@mui/icons-material';
import './TimePreferences.css';

interface TimePreferencesProps {
  config: any;
  updateConfig: (updates: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

type PreferenceType = 'morning' | 'afternoon' | 'flexible';

const TimePreferences: React.FC<TimePreferencesProps> = ({ 
  config, 
  updateConfig, 
  onNext, 
  onPrev 
}) => {
  const teachers = config.teachers || [];
  const teacherPreferences = config.teacherPreferences || {};

  const timeDefinitions = {
    morning: { label: 'Morning', time: '9:00 AM - 1:00 PM', icon: <WbSunny />, color: '#f59e0b' },
    afternoon: { label: 'Afternoon', time: '1:45 PM - 5:45 PM', icon: <WbTwilight />, color: '#3b82f6' },
    flexible: { label: 'Flexible', time: 'Any Time', icon: <Sync />, color: '#10b981' }
  };

  const classTypes = [
    { 
      key: 'lecturePreference', 
      label: 'Lecture Preference', 
      icon: <MenuBook />, 
      description: 'When teacher prefers to conduct theory lectures',
      color: '#3b82f6'
    },
    { 
      key: 'labPreference', 
      label: 'Lab Preference', 
      icon: <Science />, 
      description: 'When teacher prefers to conduct laboratory sessions',
      color: '#10b981'
    },
    { 
      key: 'projectPreference', 
      label: 'Project Preference', 
      icon: <TrackChanges />, 
      description: 'When teacher prefers to guide project work',
      color: '#f59e0b'
    }
  ];

  const updateTeacherPreference = (teacherId: string, preferenceType: string, value: PreferenceType) => {
    const updatedPreferences = { ...teacherPreferences };
    
    if (!updatedPreferences[teacherId]) {
      updatedPreferences[teacherId] = {
        lecturePreference: 'flexible',
        labPreference: 'flexible',
        projectPreference: 'flexible',
        notes: ''
      };
    }
    
    updatedPreferences[teacherId][preferenceType] = value;
    updateConfig({ teacherPreferences: updatedPreferences });
  };

  const updateTeacherNotes = (teacherId: string, notes: string) => {
    const updatedPreferences = { ...teacherPreferences };
    
    if (!updatedPreferences[teacherId]) {
      updatedPreferences[teacherId] = {
        lecturePreference: 'flexible',
        labPreference: 'flexible',
        projectPreference: 'flexible',
        notes: ''
      };
    }
    
    updatedPreferences[teacherId].notes = notes;
    updateConfig({ teacherPreferences: updatedPreferences });
  };

  const getPreference = (teacherId: string, preferenceType: string): PreferenceType => {
    return teacherPreferences[teacherId]?.[preferenceType] || 'flexible';
  };

  const getNotes = (teacherId: string): string => {
    return teacherPreferences[teacherId]?.notes || '';
  };

  const bulkSetPreference = (preferenceType: string, value: PreferenceType) => {
    const updatedPreferences = { ...teacherPreferences };
    
    teachers.forEach((teacher: any) => {
      if (!updatedPreferences[teacher.id]) {
        updatedPreferences[teacher.id] = {
          lecturePreference: 'flexible',
          labPreference: 'flexible',
          projectPreference: 'flexible',
          notes: ''
        };
      }
      updatedPreferences[teacher.id][preferenceType] = value;
    });
    
    updateConfig({ teacherPreferences: updatedPreferences });
  };

  const setSmartDefaults = () => {
    const updatedPreferences = { ...teacherPreferences };
    
    teachers.forEach((teacher: any, index: number) => {
      if (!updatedPreferences[teacher.id]) {
        updatedPreferences[teacher.id] = {
          lecturePreference: 'flexible',
          labPreference: 'flexible',
          projectPreference: 'flexible',
          notes: ''
        };
      }
      
      // Smart defaults based on experience and position
      if (teacher.experience >= 10 || teacher.designation.includes('HOD') || teacher.designation.includes('Professor')) {
        // Senior faculty prefer morning lectures
        updatedPreferences[teacher.id].lecturePreference = 'morning';
        updatedPreferences[teacher.id].projectPreference = 'morning';
      } else if (teacher.experience <= 5) {
        // Junior faculty more flexible, often get afternoon slots
        updatedPreferences[teacher.id].lecturePreference = 'flexible';
        updatedPreferences[teacher.id].labPreference = 'afternoon';
      }
      
      // Alternate preferences to balance load
      if (index % 2 === 0) {
        updatedPreferences[teacher.id].labPreference = updatedPreferences[teacher.id].labPreference || 'morning';
      } else {
        updatedPreferences[teacher.id].labPreference = updatedPreferences[teacher.id].labPreference || 'afternoon';
      }
    });
    
    updateConfig({ teacherPreferences: updatedPreferences });
  };

  const resetAllPreferences = () => {
    if (window.confirm('Are you sure you want to reset all time preferences to flexible?')) {
      const resetPreferences: any = {};
      teachers.forEach((teacher: any) => {
        resetPreferences[teacher.id] = {
          lecturePreference: 'flexible',
          labPreference: 'flexible',
          projectPreference: 'flexible',
          notes: ''
        };
      });
      updateConfig({ teacherPreferences: resetPreferences });
    }
  };

  const getPreferenceStats = () => {
    const stats = {
      morning: { lectures: 0, labs: 0, projects: 0 },
      afternoon: { lectures: 0, labs: 0, projects: 0 },
      flexible: { lectures: 0, labs: 0, projects: 0 }
    };

    teachers.forEach((teacher: any) => {
      const prefs = teacherPreferences[teacher.id];
      if (prefs) {
        const lectureKey = (prefs.lecturePreference || 'flexible') as keyof typeof stats;
        const labKey = (prefs.labPreference || 'flexible') as keyof typeof stats;
        const projectKey = (prefs.projectPreference || 'flexible') as keyof typeof stats;
        
        stats[lectureKey].lectures++;
        stats[labKey].labs++;
        stats[projectKey].projects++;
      } else {
        stats.flexible.lectures++;
        stats.flexible.labs++;
        stats.flexible.projects++;
      }
    });

    return stats;
  };

  const validateAndNext = () => {
    // All teachers should have preferences set (even if flexible)
    const missingPreferences = teachers.filter((teacher: any) => 
      !teacherPreferences[teacher.id]
    );

    if (missingPreferences.length > 0) {
      // Auto-set flexible for missing preferences
      const updatedPreferences = { ...teacherPreferences };
      missingPreferences.forEach((teacher: any) => {
        updatedPreferences[teacher.id] = {
          lecturePreference: 'flexible',
          labPreference: 'flexible',
          projectPreference: 'flexible',
          notes: ''
        };
      });
      updateConfig({ teacherPreferences: updatedPreferences });
    }

    onNext();
  };

  const stats = getPreferenceStats();

  return (
    <div className="time-preferences">
      {/* Time Definitions */}
      <div className="time-definitions-section">
        <h3 className="section-title">
          <span className="title-icon">⏰</span>
          Time Slot Definitions
        </h3>
        <p className="section-subtitle">
          Based on your college timing configuration
        </p>
        
        <div className="time-definitions-grid">
          {Object.entries(timeDefinitions).map(([key, def]) => (
            <div key={key} className={`time-definition-card ${key}`}>
              <div className="time-icon" style={{ color: def.color }}>
                {def.icon}
              </div>
              <div className="time-info">
                <h4 className="time-label">{def.label}</h4>
                <p className="time-range">{def.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bulk Actions */}
      <div className="bulk-actions-section">
        <h3 className="section-title">
          <span className="title-icon">⚡</span>
          Quick Actions
        </h3>
        
        <div className="bulk-actions-grid">
          <button
            className="bulk-action-btn smart-defaults"
            onClick={setSmartDefaults}
          >
            <TrackChanges sx={{ fontSize: 24, mb: 1 }} />
            <div className="action-info">
              <h4>Smart Defaults</h4>
              <p>Set preferences based on experience & designation</p>
            </div>
          </button>
          
          <button
            className="bulk-action-btn reset-all"
            onClick={resetAllPreferences}
          >
            <Sync sx={{ fontSize: 24, mb: 1 }} />
            <div className="action-info">
              <h4>Reset All</h4>
              <p>Set all preferences to flexible</p>
            </div>
          </button>
        </div>

        <div className="bulk-preference-controls">
          {classTypes.map(classType => (
            <div key={classType.key} className="bulk-control-group">
              <div className="bulk-control-header">
                <span className="class-icon" style={{ color: classType.color }}>
                  {classType.icon}
                </span>
                <span className="class-label">{classType.label}</span>
              </div>
              <div className="bulk-buttons">
                {Object.entries(timeDefinitions).map(([prefKey, prefDef]) => (
                  <button
                    key={prefKey}
                    className={`bulk-pref-btn ${prefKey}`}
                    onClick={() => bulkSetPreference(classType.key, prefKey as PreferenceType)}
                    style={{ borderColor: prefDef.color }}
                  >
                    {prefDef.icon} All {prefDef.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Preferences Matrix */}
      <div className="preferences-section">
        <h3 className="section-title">
          <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
          Teacher Time Preferences
        </h3>
        <p className="section-subtitle">
          Configure when each teacher prefers to conduct different types of classes
        </p>

        <div className="preferences-matrix">
          <div className="matrix-container">
            <table className="preferences-table">
              <thead>
                <tr>
                  <th className="teacher-header">Teacher</th>
                  {classTypes.map(classType => (
                    <th key={classType.key} className="class-header">
                      <div className="class-header-content">
                        <span className="class-icon" style={{ color: classType.color }}>
                          {classType.icon}
                        </span>
                        <div className="class-info">
                          <span className="class-name">{classType.label}</span>
                          <span className="class-desc">{classType.description}</span>
                        </div>
                      </div>
                    </th>
                  ))}
                  <th className="notes-header">Special Requirements</th>
                </tr>
              </thead>
              <tbody>
                {teachers.map((teacher: any) => (
                  <tr key={teacher.id}>
                    <td className="teacher-cell">
                      <div className="teacher-info">
                        <div className="teacher-name">{teacher.name}</div>
                        <div className="teacher-details">
                          <span className="teacher-designation">{teacher.designation}</span>
                          <span className="teacher-experience">{teacher.experience}y exp</span>
                        </div>
                      </div>
                    </td>
                    
                    {classTypes.map(classType => (
                      <td key={classType.key} className="preference-cell">
                        <div className="preference-options">
                          {Object.entries(timeDefinitions).map(([prefKey, prefDef]) => (
                            <label
                              key={prefKey}
                              className={`preference-option ${prefKey} ${
                                getPreference(teacher.id, classType.key) === prefKey ? 'selected' : ''
                              }`}
                            >
                              <input
                                type="radio"
                                name={`${teacher.id}-${classType.key}`}
                                value={prefKey}
                                checked={getPreference(teacher.id, classType.key) === prefKey}
                                onChange={() => updateTeacherPreference(teacher.id, classType.key, prefKey as PreferenceType)}
                              />
                              <span className="option-content">
                                <span className="option-icon">{prefDef.icon}</span>
                                <span className="option-label">{prefDef.label}</span>
                              </span>
                            </label>
                          ))}
                        </div>
                      </td>
                    ))}
                    
                    <td className="notes-cell">
                      <textarea
                        className="notes-input"
                        placeholder="Any special requirements or constraints..."
                        value={getNotes(teacher.id)}
                        onChange={(e) => updateTeacherNotes(teacher.id, e.target.value)}
                        rows={2}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Preference Statistics */}
      <div className="stats-section">
        <h3 className="section-title">
          <BarChart sx={{ mr: 1, verticalAlign: 'middle' }} />
          Preference Distribution
        </h3>
        
        <div className="stats-grid">
          {Object.entries(timeDefinitions).map(([timeKey, timeDef]) => (
            <div key={timeKey} className={`stat-card ${timeKey}`}>
              <div className="stat-header">
                <span className="stat-icon" style={{ color: timeDef.color }}>
                  {timeDef.icon}
                </span>
                <h4 className="stat-title">{timeDef.label}</h4>
              </div>
              <div className="stat-content">
                <div className="stat-item">
                  <span className="stat-label"><MenuBook sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} /> Lectures:</span>
                  <span className="stat-value">{stats[timeKey as keyof typeof stats].lectures}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label"><Science sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} /> Labs:</span>
                  <span className="stat-value">{stats[timeKey as keyof typeof stats].labs}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label"><TrackChanges sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} /> Projects:</span>
                  <span className="stat-value">{stats[timeKey as keyof typeof stats].projects}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Guidelines */}
      <div className="guidelines-section">
        <h4 className="guidelines-title">
          <Lightbulb sx={{ mr: 1, verticalAlign: 'middle' }} />
          Preference Guidelines
        </h4>
        <div className="guidelines-grid">
          <div className="guideline-item">
            <div className="guideline-icon"><WbSunny /></div>
            <div className="guideline-text">
              <strong>Morning Preference:</strong> Ideal for senior faculty and important subjects. Better student attention.
            </div>
          </div>
          <div className="guideline-item">
            <div className="guideline-icon"><WbTwilight /></div>
            <div className="guideline-text">
              <strong>Afternoon Preference:</strong> Good for labs and practical sessions. More equipment availability.
            </div>
          </div>
          <div className="guideline-item">
            <div className="guideline-icon"><Sync /></div>
            <div className="guideline-text">
              <strong>Flexible:</strong> Allows algorithm to optimize based on other constraints. Recommended for most teachers.
            </div>
          </div>
          <div className="guideline-item">
            <div className="guideline-icon">⚖️</div>
            <div className="guideline-text">
              <strong>Balance:</strong> Mix of preferences helps create balanced timetables without conflicts.
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="window-navigation">
        <div className="nav-left">
          <button className="btn btn-secondary" onClick={onPrev}>
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
            </svg>
            Back
          </button>
        </div>
        <div className="nav-center">
          <div className="preferences-summary">
            <span className="summary-text">
              {teachers.length} teachers • Morning: {stats.morning.lectures + stats.morning.labs + stats.morning.projects} • 
              Afternoon: {stats.afternoon.lectures + stats.afternoon.labs + stats.afternoon.projects} • 
              Flexible: {stats.flexible.lectures + stats.flexible.labs + stats.flexible.projects}
            </span>
          </div>
        </div>
        <div className="nav-right">
          <button 
            className="btn btn-primary"
            onClick={validateAndNext}
          >
            Continue to Final Config
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TimePreferences;
