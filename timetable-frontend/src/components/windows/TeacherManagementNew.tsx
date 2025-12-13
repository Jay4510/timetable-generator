import React, { useState } from 'react';
import './TeacherManagement.css';

interface Teacher {
  id: string;
  name: string;
  experience: number;
  designation: string;
  assignedYears: string[];
}

interface TeacherTemplate {
  name: string;
  description: string;
  teachers: Teacher[];
}

interface TeacherManagementProps {
  config: any;
  updateConfig: (updates: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

const TeacherManagement: React.FC<TeacherManagementProps> = ({
  config,
  updateConfig,
  onNext,
  onPrev
}) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState<Teacher | null>(null);
  const [newTeacher, setNewTeacher] = useState<Teacher>({
    id: '',
    name: '',
    experience: 1,
    designation: '',
    assignedYears: []
  });
  const [errors, setErrors] = useState<any>({});

  const teachers = config.teachers || [];
  const yearsManaged = config.yearsManaged || [];

  // Department-specific teacher templates
  const teacherTemplates: TeacherTemplate[] = [
    {
      name: 'Computer Science Department',
      description: 'Standard CS faculty setup',
      teachers: [
        { id: '1', name: 'Dr. Rajesh Kumar', experience: 15, designation: 'Professor', assignedYears: ['SE', 'TE', 'BE'] },
        { id: '2', name: 'Mrs. Priya Sharma', experience: 8, designation: 'Associate Professor', assignedYears: ['FE', 'SE'] },
        { id: '3', name: 'Mr. Amit Patel', experience: 5, designation: 'Assistant Professor', assignedYears: ['FE', 'SE'] },
        { id: '4', name: 'Dr. Sunita Joshi', experience: 12, designation: 'Professor', assignedYears: ['TE', 'BE'] },
        { id: '5', name: 'Mr. Vikram Singh', experience: 6, designation: 'Assistant Professor', assignedYears: ['SE', 'TE'] }
      ]
    },
    {
      name: 'Information Technology',
      description: 'IT department faculty',
      teachers: [
        { id: '1', name: 'Dr. Neha Agarwal', experience: 18, designation: 'Professor', assignedYears: ['TE', 'BE'] },
        { id: '2', name: 'Mr. Rohit Mehta', experience: 10, designation: 'Associate Professor', assignedYears: ['SE', 'TE'] },
        { id: '3', name: 'Mrs. Kavita Desai', experience: 7, designation: 'Assistant Professor', assignedYears: ['FE', 'SE'] },
        { id: '4', name: 'Dr. Arjun Rao', experience: 14, designation: 'Professor', assignedYears: ['BE'] },
        { id: '5', name: 'Ms. Pooja Gupta', experience: 4, designation: 'Assistant Professor', assignedYears: ['FE'] }
      ]
    }
  ];

  const addTeacher = () => {
    if (!newTeacher.name.trim()) {
      setErrors({ name: 'Teacher name is required' });
      return;
    }

    if (!newTeacher.designation) {
      setErrors({ designation: 'Designation is required' });
      return;
    }

    const teacher: Teacher = {
      ...newTeacher,
      id: Date.now().toString()
    };

    updateConfig({
      teachers: [...teachers, teacher]
    });

    setNewTeacher({
      id: '',
      name: '',
      experience: 1,
      designation: '',
      assignedYears: []
    });
    setShowAddModal(false);
    setErrors({});
  };

  const deleteTeacher = (teacherId: string) => {
    const updatedTeachers = teachers.filter((t: Teacher) => t.id !== teacherId);
    updateConfig({ teachers: updatedTeachers });
  };

  const updateTeacherYears = (teacherId: string, year: string, isAssigned: boolean) => {
    const updatedTeachers = teachers.map((teacher: Teacher) => {
      if (teacher.id === teacherId) {
        const currentYears = teacher.assignedYears || [];
        const newYears = isAssigned
          ? [...currentYears, year]
          : currentYears.filter(y => y !== year);
        return { ...teacher, assignedYears: newYears };
      }
      return teacher;
    });
    updateConfig({ teachers: updatedTeachers });
  };

  const bulkAssignYear = (year: string, assign: boolean) => {
    const updatedTeachers = teachers.map((teacher: Teacher) => {
      const currentYears = teacher.assignedYears || [];
      const newYears = assign
        ? [...currentYears.filter(y => y !== year), year]
        : currentYears.filter(y => y !== year);
      return { ...teacher, assignedYears: newYears };
    });
    updateConfig({ teachers: updatedTeachers });
  };

  const loadTemplate = (template: TeacherTemplate) => {
    const templatedTeachers = template.teachers.map(teacher => ({
      ...teacher,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      assignedYears: teacher.assignedYears.filter(year => yearsManaged.includes(year))
    }));
    updateConfig({ teachers: templatedTeachers });
  };

  const getYearColor = (year: string) => {
    const colors: { [key: string]: string } = {
      'FE': '#4CAF50',
      'SE': '#2196F3', 
      'TE': '#FF9800',
      'BE': '#9C27B0'
    };
    return colors[year] || '#757575';
  };

  const validateAndNext = () => {
    if (teachers.length === 0) {
      setErrors({ general: 'Please add at least one teacher' });
      return;
    }

    const unassignedTeachers = teachers.filter((t: Teacher) => !t.assignedYears || t.assignedYears.length === 0);
    if (unassignedTeachers.length > 0) {
      setErrors({ 
        general: `${unassignedTeachers.length} teacher(s) are not assigned to any year. Please assign them or remove them.` 
      });
      return;
    }

    setErrors({});
    onNext();
  };

  return (
    <div className="teacher-management">
      <div className="window-header">
        <h2 className="window-title">
          <span className="title-icon">👨‍🏫</span>
          Teacher Management
        </h2>
        <p className="window-subtitle">
          Add teachers and assign them to the years they will handle
        </p>
      </div>

      {/* Quick Templates */}
      <div className="templates-section">
        <div className="section-header">
          <h3 className="section-title">
            <span className="title-icon">⚡</span>
            Quick Start Templates
          </h3>
          <p className="section-subtitle">
            Load pre-configured teacher setups for common departments
          </p>
        </div>
        
        <div className="templates-grid">
          {teacherTemplates.map((template, index) => (
            <div key={index} className="template-card">
              <h4 className="template-name">{template.name}</h4>
              <p className="template-description">{template.description}</p>
              <div className="template-preview">
                {template.teachers.slice(0, 3).map((teacher, idx) => (
                  <div key={idx} className="preview-teacher">
                    {teacher.name.split(' ')[0]}
                  </div>
                ))}
                {template.teachers.length > 3 && (
                  <div className="preview-more">+{template.teachers.length - 3} more</div>
                )}
              </div>
              <button
                className="btn btn-secondary btn-small"
                onClick={() => loadTemplate(template)}
              >
                Load Template
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Add Teacher Section */}
      <div className="add-teacher-section">
        <div className="section-header">
          <h3 className="section-title">
            <span className="title-icon">👨‍🏫</span>
            Teachers ({teachers.length})
          </h3>
          <button
            className="btn btn-primary"
            onClick={() => setShowAddModal(true)}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
            Add Teacher
          </button>
        </div>

        {errors.general && (
          <div className="error-message">{errors.general}</div>
        )}

        {/* Teachers List */}
        {teachers.length > 0 ? (
          <div className="teachers-list">
            {teachers.map((teacher: Teacher) => (
              <div key={teacher.id} className="teacher-card">
                <div className="teacher-info">
                  <div className="teacher-header">
                    <h4 className="teacher-name">{teacher.name}</h4>
                    <div className="teacher-actions">
                      <button
                        className="action-btn edit-btn"
                        onClick={() => setEditingTeacher(teacher)}
                        title="Edit Teacher"
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                        </svg>
                      </button>
                      <button
                        className="action-btn delete-btn"
                        onClick={() => deleteTeacher(teacher.id)}
                        title="Delete Teacher"
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div className="teacher-details">
                    <span className="detail-item">
                      <span className="detail-icon">🎓</span>
                      {teacher.designation}
                    </span>
                    <span className="detail-item">
                      <span className="detail-icon">⏱️</span>
                      {teacher.experience} years experience
                    </span>
                  </div>
                  <div className="teacher-years">
                    <span className="years-label">Assigned Years:</span>
                    <div className="years-badges">
                      {teacher.assignedYears && teacher.assignedYears.length > 0 ? (
                        teacher.assignedYears.map(year => (
                          <span
                            key={year}
                            className="year-badge"
                            style={{ backgroundColor: getYearColor(year) }}
                          >
                            {year}
                          </span>
                        ))
                      ) : (
                        <span className="no-years">Not assigned</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">👨‍🏫</div>
            <h3>No Teachers Added</h3>
            <p>Start by adding teachers to your department</p>
            <button
              className="btn btn-primary"
              onClick={() => setShowAddModal(true)}
            >
              Add Your First Teacher
            </button>
          </div>
        )}
      </div>

      {/* Enhanced Year Assignments Section */}
      {teachers.length > 0 && (
        <div className="year-assignments-section">
          <div className="section-header">
            <h3 className="section-title">
              <span className="title-icon">📋</span>
              Year Assignments Matrix
            </h3>
            <div className="assignment-controls">
              <button
                className="btn btn-secondary btn-small"
                onClick={() => {
                  const updatedTeachers = teachers.map((teacher: Teacher) => ({
                    ...teacher,
                    assignedYears: yearsManaged
                  }));
                  updateConfig({ teachers: updatedTeachers });
                }}
              >
                ✅ Assign All to All Years
              </button>
              <button
                className="btn btn-secondary btn-small"
                onClick={() => {
                  const updatedTeachers = teachers.map((teacher: Teacher) => ({
                    ...teacher,
                    assignedYears: []
                  }));
                  updateConfig({ teachers: updatedTeachers });
                }}
              >
                🗑️ Clear All Assignments
              </button>
            </div>
          </div>
          
          <div className="assignment-help">
            <p>💡 <strong>Tip:</strong> Click column headers to assign all teachers to a year, or row buttons to assign all years to a teacher.</p>
          </div>

          <div className="assignment-matrix">
            <div className="matrix-header">
              <div className="teacher-column-header">
                <div className="header-content">
                  <strong>Teacher</strong>
                  <small>({teachers.length} total)</small>
                </div>
              </div>
              {yearsManaged.map((year: string) => (
                <div key={year} className="year-column-header">
                  <div className="year-header-content">
                    <div className="year-name" style={{ color: getYearColor(year) }}>
                      <strong>{year}</strong>
                    </div>
                    <button
                      className="bulk-assign-btn"
                      onClick={() => {
                        const allAssigned = teachers.every((t: Teacher) => 
                          t.assignedYears && t.assignedYears.includes(year)
                        );
                        bulkAssignYear(year, !allAssigned);
                      }}
                      title={`Toggle all teachers for ${year}`}
                      style={{ backgroundColor: getYearColor(year) }}
                    >
                      {teachers.every((t: Teacher) => t.assignedYears && t.assignedYears.includes(year)) ? '☑️' : '☐'}
                    </button>
                    <small className="assignment-count">
                      {teachers.filter((t: Teacher) => t.assignedYears?.includes(year)).length} assigned
                    </small>
                  </div>
                </div>
              ))}
            </div>

            <div className="matrix-body">
              {teachers.map((teacher: Teacher, index: number) => (
                <div key={teacher.id} className={`matrix-row ${index % 2 === 0 ? 'even' : 'odd'}`}>
                  <div className="teacher-cell">
                    <div className="teacher-info">
                      <div className="teacher-name">{teacher.name}</div>
                      <div className="teacher-meta">
                        <span className="designation">{teacher.designation}</span>
                        <span className="experience">{teacher.experience}y exp</span>
                      </div>
                    </div>
                    <button
                      className="teacher-select-all"
                      onClick={() => {
                        const allAssigned = yearsManaged.every(year => 
                          teacher.assignedYears?.includes(year)
                        );
                        const updatedTeachers = teachers.map((t: Teacher) => {
                          if (t.id === teacher.id) {
                            return {
                              ...t,
                              assignedYears: allAssigned ? [] : [...yearsManaged]
                            };
                          }
                          return t;
                        });
                        updateConfig({ teachers: updatedTeachers });
                      }}
                      title={`Toggle all years for ${teacher.name}`}
                    >
                      {yearsManaged.every(year => teacher.assignedYears?.includes(year)) ? '🗑️ Clear' : '✅ All'}
                    </button>
                  </div>

                  {yearsManaged.map((year: string) => (
                    <div key={year} className="assignment-cell">
                      <label className="assignment-checkbox">
                        <input
                          type="checkbox"
                          checked={teacher.assignedYears?.includes(year) || false}
                          onChange={(e) => updateTeacherYears(teacher.id, year, e.target.checked)}
                        />
                        <span 
                          className="checkmark" 
                          style={{ 
                            borderColor: getYearColor(year),
                            backgroundColor: teacher.assignedYears?.includes(year) ? getYearColor(year) : 'transparent'
                          }}
                        >
                          {teacher.assignedYears?.includes(year) && '✓'}
                        </span>
                      </label>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Assignment Summary */}
          <div className="assignment-summary">
            <div className="summary-header">
              <h4>📊 Assignment Summary</h4>
            </div>
            <div className="summary-content">
              <div className="summary-stats">
                {yearsManaged.map((year: string) => {
                  const assignedCount = teachers.filter((teacher: Teacher) => 
                    teacher.assignedYears?.includes(year)
                  ).length;
                  const percentage = teachers.length > 0 ? Math.round((assignedCount / teachers.length) * 100) : 0;
                  return (
                    <div key={year} className="year-stat">
                      <div className="stat-header">
                        <span className="year-stat-name" style={{ color: getYearColor(year) }}>
                          <strong>{year}</strong>
                        </span>
                        <span className={`year-stat-count ${assignedCount === 0 ? 'warning' : 'success'}`}>
                          {assignedCount}/{teachers.length}
                        </span>
                      </div>
                      <div className="stat-bar">
                        <div 
                          className="stat-fill" 
                          style={{ 
                            width: `${percentage}%`,
                            backgroundColor: getYearColor(year)
                          }}
                        ></div>
                      </div>
                      <small className="stat-percentage">{percentage}% coverage</small>
                    </div>
                  );
                })}
              </div>
              
              <div className="summary-warnings">
                {teachers.filter((teacher: Teacher) => !teacher.assignedYears || teacher.assignedYears.length === 0).length > 0 && (
                  <div className="warning-message">
                    ⚠️ <strong>{teachers.filter((teacher: Teacher) => !teacher.assignedYears || teacher.assignedYears.length === 0).length} teacher(s)</strong> not assigned to any year
                  </div>
                )}
                
                {yearsManaged.filter(year => 
                  teachers.filter((teacher: Teacher) => teacher.assignedYears?.includes(year)).length === 0
                ).length > 0 && (
                  <div className="warning-message">
                    ⚠️ <strong>{yearsManaged.filter(year => 
                      teachers.filter((teacher: Teacher) => teacher.assignedYears?.includes(year)).length === 0
                    ).join(', ')}</strong> year(s) have no assigned teachers
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Teacher Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Add New Teacher</h3>
              <button
                className="modal-close"
                onClick={() => setShowAddModal(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">
                  Full Name <span className="required">*</span>
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Enter teacher's full name"
                  value={newTeacher.name}
                  onChange={(e) => setNewTeacher({ ...newTeacher, name: e.target.value })}
                />
                {errors.name && <div className="error-message">{errors.name}</div>}
              </div>

              <div className="form-row grid-2">
                <div className="form-group">
                  <label className="form-label">Years of Experience</label>
                  <input
                    type="number"
                    className="form-input"
                    min="1"
                    max="50"
                    value={newTeacher.experience}
                    onChange={(e) => setNewTeacher({ ...newTeacher, experience: parseInt(e.target.value) || 1 })}
                  />
                  {errors.experience && <div className="error-message">{errors.experience}</div>}
                </div>

                <div className="form-group">
                  <label className="form-label">Designation</label>
                  <select
                    className="form-select"
                    value={newTeacher.designation}
                    onChange={(e) => setNewTeacher({ ...newTeacher, designation: e.target.value })}
                  >
                    <option value="">Select designation</option>
                    <option value="Professor">Professor</option>
                    <option value="Associate Professor">Associate Professor</option>
                    <option value="Assistant Professor">Assistant Professor</option>
                    <option value="Lecturer">Lecturer</option>
                    <option value="HOD">Head of Department</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setShowAddModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={addTeacher}
                disabled={!newTeacher.name.trim()}
              >
                Add Teacher
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
          <div className="teachers-summary">
            <span className="summary-text">
              {teachers.length} teachers • {teachers.filter((t: Teacher) => t.assignedYears && t.assignedYears.length > 0).length} assigned
            </span>
          </div>
        </div>
        <div className="nav-right">
          <button 
            className="btn btn-primary"
            onClick={validateAndNext}
            disabled={teachers.length === 0}
          >
            Continue to Proficiency
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TeacherManagement;
