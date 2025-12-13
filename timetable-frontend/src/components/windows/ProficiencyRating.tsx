import React, { useState, useEffect } from 'react';
import { MenuBook, Book, Science, TrackChanges } from '@mui/icons-material';
import './ProficiencyRating.css';

interface ProficiencyRatingProps {
  config: any;
  updateConfig: (updates: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

interface Subject {
  id: string;
  name: string;
  code: string;
  type: 'theory' | 'lab' | 'project';
}

const ProficiencyRating: React.FC<ProficiencyRatingProps> = ({ 
  config, 
  updateConfig, 
  onNext, 
  onPrev 
}) => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [showSubjectModal, setShowSubjectModal] = useState(false);
  const [newSubject, setNewSubject] = useState({
    name: '',
    code: '',
    type: 'theory' as 'theory' | 'lab' | 'project'
  });

  const teachers = config.teachers || [];
  const proficiencyData = config.proficiencyData || {};

  // Common subjects for different departments
  const subjectTemplates = {
    'IT': [
      { name: 'Data Structures and Algorithms', code: 'DSA', type: 'theory' },
      { name: 'Database Management Systems', code: 'DBMS', type: 'theory' },
      { name: 'Computer Networks', code: 'CN', type: 'theory' },
      { name: 'Software Engineering', code: 'SE', type: 'theory' },
      { name: 'Web Development Lab', code: 'WDL', type: 'lab' },
      { name: 'Database Lab', code: 'DBL', type: 'lab' },
      { name: 'Major Project', code: 'MP', type: 'project' }
    ],
    'CS': [
      { name: 'Operating Systems', code: 'OS', type: 'theory' },
      { name: 'Computer Graphics', code: 'CG', type: 'theory' },
      { name: 'Machine Learning', code: 'ML', type: 'theory' },
      { name: 'Artificial Intelligence', code: 'AI', type: 'theory' },
      { name: 'Programming Lab', code: 'PL', type: 'lab' },
      { name: 'Graphics Lab', code: 'GL', type: 'lab' }
    ],
    'ME': [
      { name: 'Thermodynamics', code: 'TD', type: 'theory' },
      { name: 'Fluid Mechanics', code: 'FM', type: 'theory' },
      { name: 'Manufacturing Processes', code: 'MP', type: 'theory' },
      { name: 'Machine Design', code: 'MD', type: 'theory' },
      { name: 'Workshop Practice', code: 'WP', type: 'lab' },
      { name: 'CAD Lab', code: 'CAD', type: 'lab' }
    ],
    'CE': [
      { name: 'Structural Analysis', code: 'SA', type: 'theory' },
      { name: 'Concrete Technology', code: 'CT', type: 'theory' },
      { name: 'Geotechnical Engineering', code: 'GE', type: 'theory' },
      { name: 'Transportation Engineering', code: 'TE', type: 'theory' },
      { name: 'Survey Lab', code: 'SL', type: 'lab' },
      { name: 'Materials Lab', code: 'ML', type: 'lab' }
    ],
    'HS': [
      { name: 'Engineering Mathematics', code: 'EM', type: 'theory' },
      { name: 'Engineering Physics', code: 'EP', type: 'theory' },
      { name: 'Engineering Chemistry', code: 'EC', type: 'theory' },
      { name: 'Communication Skills', code: 'CS', type: 'theory' },
      { name: 'Physics Lab', code: 'PL', type: 'lab' },
      { name: 'Chemistry Lab', code: 'CL', type: 'lab' }
    ]
  };

  useEffect(() => {
    // Load subjects based on department
    const departmentSubjects = subjectTemplates[config.department as keyof typeof subjectTemplates] || [];
    const defaultSubjects = departmentSubjects.map((subject, index) => ({
      id: `subject_${index + 1}`,
      ...subject
    }));
    setSubjects(defaultSubjects);
  }, [config.department]);

  const addSubject = () => {
    if (!newSubject.name.trim() || !newSubject.code.trim()) return;

    const subject: Subject = {
      id: `subject_${Date.now()}`,
      name: newSubject.name.trim(),
      code: newSubject.code.trim().toUpperCase(),
      type: newSubject.type
    };

    setSubjects([...subjects, subject]);
    setNewSubject({ name: '', code: '', type: 'theory' });
    setShowSubjectModal(false);
  };

  const deleteSubject = (subjectId: string) => {
    if (window.confirm('Are you sure you want to remove this subject?')) {
      setSubjects(subjects.filter(s => s.id !== subjectId));
      
      // Remove proficiency data for this subject
      const updatedProficiency = { ...proficiencyData };
      Object.keys(updatedProficiency).forEach(teacherId => {
        if (updatedProficiency[teacherId][subjectId]) {
          delete updatedProficiency[teacherId][subjectId];
        }
      });
      updateConfig({ proficiencyData: updatedProficiency });
    }
  };

  const updateProficiency = (teacherId: string, subjectId: string, type: 'knowledge' | 'willingness', value: number) => {
    const updatedProficiency = { ...proficiencyData };
    
    if (!updatedProficiency[teacherId]) {
      updatedProficiency[teacherId] = {};
    }
    
    if (!updatedProficiency[teacherId][subjectId]) {
      updatedProficiency[teacherId][subjectId] = { knowledge: 7, willingness: 7 };
    }
    
    updatedProficiency[teacherId][subjectId][type] = value;
    updateConfig({ proficiencyData: updatedProficiency });
  };

  const getProficiency = (teacherId: string, subjectId: string, type: 'knowledge' | 'willingness'): number => {
    return proficiencyData[teacherId]?.[subjectId]?.[type] || 7;
  };

  const getOverallScore = (teacherId: string, subjectId: string): number => {
    const knowledge = getProficiency(teacherId, subjectId, 'knowledge');
    const willingness = getProficiency(teacherId, subjectId, 'willingness');
    // Backend uses 60% knowledge + 40% willingness weighting
    return Math.round((knowledge * 0.6 + willingness * 0.4) * 10) / 10;
  };

  const getScoreColor = (score: number): string => {
    if (score >= 8) return '#10b981'; // Green
    if (score >= 6) return '#f59e0b'; // Yellow
    if (score >= 4) return '#ef4444'; // Red
    return '#6b7280'; // Gray
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 9) return 'Expert';
    if (score >= 8) return 'Very Good';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Average';
    return 'Beginner';
  };

  const autoFillDefaults = () => {
    const updatedProficiency = { ...proficiencyData };
    
    teachers.forEach((teacher: any) => {
      if (!updatedProficiency[teacher.id]) {
        updatedProficiency[teacher.id] = {};
      }
      
      subjects.forEach(subject => {
        if (!updatedProficiency[teacher.id][subject.id]) {
          // Set smart defaults based on experience and subject type
          let baseKnowledge = Math.min(teacher.experience / 2 + 4, 8);
          let baseWillingness = 7;
          
          // Adjust for subject type
          if (subject.type === 'lab') {
            baseKnowledge = Math.max(baseKnowledge - 1, 5);
            baseWillingness = Math.max(baseWillingness - 0.5, 6);
          } else if (subject.type === 'project') {
            baseKnowledge = Math.min(baseKnowledge + 0.5, 9);
            baseWillingness = Math.min(baseWillingness + 0.5, 8);
          }
          
          updatedProficiency[teacher.id][subject.id] = {
            knowledge: Math.round(baseKnowledge),
            willingness: Math.round(baseWillingness)
          };
        }
      });
    });
    
    updateConfig({ proficiencyData: updatedProficiency });
  };

  const resetAll = () => {
    if (window.confirm('Are you sure you want to reset all proficiency ratings?')) {
      updateConfig({ proficiencyData: {} });
    }
  };

  const validateAndNext = () => {
    if (subjects.length === 0) {
      alert('Please add at least one subject before continuing');
      return;
    }

    // Store subjects in config
    updateConfig({ subjects });
    onNext();
  };

  return (
    <div className="proficiency-rating">
      {/* Subjects Management */}
      <div className="subjects-section">
        <div className="section-header">
          <h3 className="section-title">
            <MenuBook sx={{ mr: 1, verticalAlign: 'middle' }} />
            Subjects ({subjects.length})
          </h3>
          <button
            className="btn btn-primary"
            onClick={() => setShowSubjectModal(true)}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
            Add Subject
          </button>
        </div>

        <div className="subjects-grid">
          {subjects.map(subject => (
            <div key={subject.id} className={`subject-card ${subject.type}`}>
              <div className="subject-header">
                <div className="subject-info">
                  <h4 className="subject-name">{subject.name}</h4>
                  <span className="subject-code">{subject.code}</span>
                </div>
                <div className="subject-actions">
                  <span className={`subject-type ${subject.type}`}>
                    {subject.type === 'theory' && <Book sx={{ fontSize: 16, mr: 0.5 }} />}
                    {subject.type === 'lab' && <Science sx={{ fontSize: 16, mr: 0.5 }} />}
                    {subject.type === 'project' && <TrackChanges sx={{ fontSize: 16, mr: 0.5 }} />}
                    {subject.type}
                  </span>
                  <button
                    className="action-btn delete-btn"
                    onClick={() => deleteSubject(subject.id)}
                    title="Delete Subject"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Proficiency Rating Matrix */}
      {subjects.length > 0 && teachers.length > 0 && (
        <div className="proficiency-section">
          <div className="section-header">
            <h3 className="section-title">
              <span className="title-icon">⭐</span>
              Teacher Proficiency Ratings
            </h3>
            <div className="rating-actions">
              <button className="btn btn-secondary" onClick={autoFillDefaults}>
                <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                Auto-Fill Defaults
              </button>
              <button className="btn btn-secondary" onClick={resetAll}>
                <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                  <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                </svg>
                Reset All
              </button>
            </div>
          </div>

          <div className="rating-guidelines">
            <h4 className="guidelines-title">Rating Guidelines</h4>
            <div className="guidelines-grid">
              <div className="guideline-item">
                <span className="guideline-score">1-3</span>
                <span className="guideline-label">Beginner</span>
                <span className="guideline-desc">Basic understanding</span>
              </div>
              <div className="guideline-item">
                <span className="guideline-score">4-6</span>
                <span className="guideline-label">Good</span>
                <span className="guideline-desc">Can teach effectively</span>
              </div>
              <div className="guideline-item">
                <span className="guideline-score">7-8</span>
                <span className="guideline-label">Very Good</span>
                <span className="guideline-desc">Strong expertise</span>
              </div>
              <div className="guideline-item">
                <span className="guideline-score">9-10</span>
                <span className="guideline-label">Expert</span>
                <span className="guideline-desc">Subject matter expert</span>
              </div>
            </div>
          </div>

          <div className="proficiency-matrix">
            <div className="matrix-container">
              <table className="proficiency-table">
                <thead>
                  <tr>
                    <th className="teacher-header">Teacher</th>
                    {subjects.map(subject => (
                      <th key={subject.id} className="subject-header">
                        <div className="subject-header-content">
                          <div className="subject-name">{subject.name}</div>
                          <div className="subject-code">({subject.code})</div>
                          <span className="subject-type-icon">
                            {subject.type === 'theory' && <Book sx={{ fontSize: 14 }} />}
                            {subject.type === 'lab' && <Science sx={{ fontSize: 14 }} />}
                            {subject.type === 'project' && <TrackChanges sx={{ fontSize: 14 }} />}
                          </span>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {teachers.map((teacher: any) => (
                    <tr key={teacher.id}>
                      <td className="teacher-cell">
                        <div className="teacher-info">
                          <div className="teacher-name">{teacher.name}</div>
                          <div className="teacher-exp">{teacher.experience}y exp</div>
                        </div>
                      </td>
                      {subjects.map(subject => {
                        const knowledge = getProficiency(teacher.id, subject.id, 'knowledge');
                        const willingness = getProficiency(teacher.id, subject.id, 'willingness');
                        const overall = getOverallScore(teacher.id, subject.id);
                        
                        return (
                          <td key={subject.id} className="rating-cell">
                            <div className="rating-container">
                              <div className="subject-indicator">
                                <span className="subject-mini-name">{subject.code}</span>
                              </div>
                              <div className="rating-group">
                                <label className="rating-label">Knowledge</label>
                                <div className="slider-container">
                                  <input
                                    type="range"
                                    min="1"
                                    max="10"
                                    value={knowledge}
                                    onChange={(e) => updateProficiency(teacher.id, subject.id, 'knowledge', parseInt(e.target.value))}
                                    className="rating-slider knowledge"
                                  />
                                  <span className="rating-value">{knowledge}</span>
                                </div>
                              </div>
                              
                              <div className="rating-group">
                                <label className="rating-label">Willingness</label>
                                <div className="slider-container">
                                  <input
                                    type="range"
                                    min="1"
                                    max="10"
                                    value={willingness}
                                    onChange={(e) => updateProficiency(teacher.id, subject.id, 'willingness', parseInt(e.target.value))}
                                    className="rating-slider willingness"
                                  />
                                  <span className="rating-value">{willingness}</span>
                                </div>
                              </div>
                              
                              <div className="overall-score">
                                <span 
                                  className="score-badge"
                                  style={{ backgroundColor: getScoreColor(overall) }}
                                >
                                  {overall}
                                </span>
                                <span className="score-label">{getScoreLabel(overall)}</span>
                              </div>
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Add Subject Modal */}
      {showSubjectModal && (
        <div className="modal-overlay" onClick={() => setShowSubjectModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Add New Subject</h3>
              <button
                className="modal-close"
                onClick={() => setShowSubjectModal(false)}
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Subject Name</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., Data Structures and Algorithms"
                  value={newSubject.name}
                  onChange={(e) => setNewSubject({ ...newSubject, name: e.target.value })}
                />
              </div>

              <div className="form-row grid-2">
                <div className="form-group">
                  <label className="form-label">Subject Code</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g., DSA"
                    value={newSubject.code}
                    onChange={(e) => setNewSubject({ ...newSubject, code: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Subject Type</label>
                  <select
                    className="form-select"
                    value={newSubject.type}
                    onChange={(e) => setNewSubject({ ...newSubject, type: e.target.value as 'theory' | 'lab' | 'project' })}
                  >
                    <option value="theory">Theory</option>
                    <option value="lab">Laboratory</option>
                    <option value="project">Project</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setShowSubjectModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={addSubject}
                disabled={!newSubject.name.trim() || !newSubject.code.trim()}
              >
                Add Subject
              </button>
            </div>
          </div>
        </div>
      )}

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
          <div className="proficiency-summary">
            <span className="summary-text">
              {subjects.length} subjects • {teachers.length} teachers • 60% knowledge + 40% willingness
            </span>
          </div>
        </div>
        <div className="nav-right">
          <button 
            className="btn btn-primary"
            onClick={validateAndNext}
            disabled={subjects.length === 0}
          >
            Continue to Rooms
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProficiencyRating;
