import React, { useState } from 'react';
import { Person, School, Assignment, Delete, Refresh, Info, CheckCircle, Clear } from '@mui/icons-material';
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
  // const [editingTeacher, setEditingTeacher] = useState<Teacher | null>(null);
  const [newTeacher, setNewTeacher] = useState<Teacher>({
    id: '',
    name: '',
    experience: 1,
    designation: '',
    assignedYears: []
  });
  const [errors, setErrors] = useState<any>({});

  const teachers = config.teachers || [];
  const yearsManaged = config.yearsManaged || ['FE', 'SE', 'TE', 'BE']; // Fallback to default years
  
  // Debug logging
  console.log('TeacherManagement - yearsManaged:', yearsManaged);
  console.log('TeacherManagement - teachers:', teachers.length);

  // Department-specific teacher templates
  const teacherTemplates: TeacherTemplate[] = [
    {
      name: 'DMCE Information Technology Department (Real Data)',
      description: 'Complete IT faculty based on actual DMCE timetables and curriculum',
      teachers: [
        // SE Faculty (Second Year)
        { id: '1', name: 'Mrs. P. R. Desai', experience: 12, designation: 'Associate Professor', assignedYears: ['SE'] },
        { id: '2', name: 'Mr. S. K. Sharma', experience: 10, designation: 'Assistant Professor', assignedYears: ['SE'] },
        { id: '3', name: 'Mrs. A. B. Patil', experience: 8, designation: 'Assistant Professor', assignedYears: ['SE'] },
        { id: '4', name: 'Dr. R. M. Joshi', experience: 15, designation: 'Professor', assignedYears: ['SE'] },
        { id: '5', name: 'Mr. V. K. Singh', experience: 9, designation: 'Assistant Professor', assignedYears: ['SE'] },
        { id: '6', name: 'Mrs. N. S. Kulkarni', experience: 11, designation: 'Associate Professor', assignedYears: ['SE'] },
        
        // TE Faculty (Third Year)
        { id: '7', name: 'Mrs. A. D. Mhaitre (ADM)', experience: 14, designation: 'Associate Professor', assignedYears: ['TE'] },
        { id: '8', name: 'Mrs. R. A. Jolhe (RAJ)', experience: 13, designation: 'Associate Professor', assignedYears: ['TE'] },
        { id: '9', name: 'Mrs. Sonali Patil (SP)', experience: 10, designation: 'Assistant Professor', assignedYears: ['TE'] },
        { id: '10', name: 'Dr. Namita Shah (NS)', experience: 16, designation: 'Professor', assignedYears: ['TE'] },
        { id: '11', name: 'Mrs. N. Y. Mohaskar (NYM)', experience: 9, designation: 'Assistant Professor', assignedYears: ['TE'] },
        { id: '12', name: 'Mrs. N. G. Jamkar (NGJ)', experience: 12, designation: 'Associate Professor', assignedYears: ['TE'] },
        { id: '13', name: 'Mrs. Harshita D. Bhagwat (HDB)', experience: 7, designation: 'Assistant Professor', assignedYears: ['TE'] },
        { id: '14', name: 'Mr. K. A. Jadhav (KPR)', experience: 11, designation: 'Assistant Professor', assignedYears: ['TE'] },
        
        // BE Faculty (Fourth Year)
        { id: '15', name: 'Dr. A. K. Tripathi', experience: 18, designation: 'Professor', assignedYears: ['BE'] },
        { id: '16', name: 'Mrs. S. D. Joshi', experience: 13, designation: 'Associate Professor', assignedYears: ['BE'] },
        { id: '17', name: 'Mr. R. P. Kulkarni', experience: 15, designation: 'Associate Professor', assignedYears: ['BE'] },
        { id: '18', name: 'Dr. M. N. Patil', experience: 20, designation: 'Professor', assignedYears: ['BE'] },
        { id: '19', name: 'Mrs. K. L. Sharma', experience: 14, designation: 'Associate Professor', assignedYears: ['BE'] },
        { id: '20', name: 'Mr. T. S. Rao', experience: 12, designation: 'Assistant Professor', assignedYears: ['BE'] }
      ]
    },
    {
      name: 'DMCE IT Department (Cross-Year Faculty)',
      description: 'Faculty assigned to multiple years for better resource utilization',
      teachers: [
        // Senior Faculty (Multi-year assignments)
        { id: '1', name: 'Dr. R. M. Joshi', experience: 15, designation: 'Professor', assignedYears: ['SE', 'TE'] },
        { id: '2', name: 'Dr. Namita Shah (NS)', experience: 16, designation: 'Professor', assignedYears: ['TE', 'BE'] },
        { id: '3', name: 'Dr. A. K. Tripathi', experience: 18, designation: 'Professor', assignedYears: ['TE', 'BE'] },
        { id: '4', name: 'Dr. M. N. Patil', experience: 20, designation: 'Professor', assignedYears: ['TE', 'BE'] },
        
        // Associate Professors (Multi-year)
        { id: '5', name: 'Mrs. A. D. Mhaitre (ADM)', experience: 14, designation: 'Associate Professor', assignedYears: ['TE', 'BE'] },
        { id: '6', name: 'Mrs. R. A. Jolhe (RAJ)', experience: 13, designation: 'Associate Professor', assignedYears: ['SE', 'TE'] },
        { id: '7', name: 'Mrs. P. R. Desai', experience: 12, designation: 'Associate Professor', assignedYears: ['SE', 'TE'] },
        { id: '8', name: 'Mrs. N. S. Kulkarni', experience: 11, designation: 'Associate Professor', assignedYears: ['SE', 'TE'] },
        { id: '9', name: 'Mrs. N. G. Jamkar (NGJ)', experience: 12, designation: 'Associate Professor', assignedYears: ['TE', 'BE'] },
        { id: '10', name: 'Mrs. S. D. Joshi', experience: 13, designation: 'Associate Professor', assignedYears: ['TE', 'BE'] },
        { id: '11', name: 'Mr. R. P. Kulkarni', experience: 15, designation: 'Associate Professor', assignedYears: ['TE', 'BE'] },
        { id: '12', name: 'Mrs. K. L. Sharma', experience: 14, designation: 'Associate Professor', assignedYears: ['TE', 'BE'] },
        
        // Assistant Professors (Flexible assignments)
        { id: '13', name: 'Mr. S. K. Sharma', experience: 10, designation: 'Assistant Professor', assignedYears: ['SE', 'TE'] },
        { id: '14', name: 'Mrs. A. B. Patil', experience: 8, designation: 'Assistant Professor', assignedYears: ['SE', 'TE'] },
        { id: '15', name: 'Mr. V. K. Singh', experience: 9, designation: 'Assistant Professor', assignedYears: ['SE', 'TE'] },
        { id: '16', name: 'Mrs. Sonali Patil (SP)', experience: 10, designation: 'Assistant Professor', assignedYears: ['TE', 'BE'] },
        { id: '17', name: 'Mrs. N. Y. Mohaskar (NYM)', experience: 9, designation: 'Assistant Professor', assignedYears: ['TE', 'BE'] },
        { id: '18', name: 'Mrs. Harshita D. Bhagwat (HDB)', experience: 7, designation: 'Assistant Professor', assignedYears: ['TE', 'BE'] },
        { id: '19', name: 'Mr. K. A. Jadhav (KPR)', experience: 11, designation: 'Assistant Professor', assignedYears: ['TE', 'BE'] },
        { id: '20', name: 'Mr. T. S. Rao', experience: 12, designation: 'Assistant Professor', assignedYears: ['TE', 'BE'] }
      ]
    },
    {
      name: 'Computer Science Department (Generic)',
      description: 'Standard CS faculty setup for comparison',
      teachers: [
        { id: '1', name: 'Dr. Rajesh Kumar', experience: 15, designation: 'Professor', assignedYears: ['SE', 'TE', 'BE'] },
        { id: '2', name: 'Mrs. Priya Sharma', experience: 8, designation: 'Associate Professor', assignedYears: ['FE', 'SE'] },
        { id: '3', name: 'Mr. Amit Patel', experience: 5, designation: 'Assistant Professor', assignedYears: ['FE', 'SE'] },
        { id: '4', name: 'Dr. Sunita Joshi', experience: 12, designation: 'Professor', assignedYears: ['TE', 'BE'] },
        { id: '5', name: 'Mr. Vikram Singh', experience: 6, designation: 'Assistant Professor', assignedYears: ['SE', 'TE'] }
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
    
    // ✅ FIX: Don't override yearsManaged - keep user's selection
    updateConfig({ 
      teachers: templatedTeachers
    });
    
    console.log('Template loaded with teachers:', templatedTeachers);
    console.log('Years managed (preserved):', yearsManaged);
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
          <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
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
            <Person sx={{ mr: 1, verticalAlign: 'middle' }} />
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
                        onClick={() => console.log('Edit teacher:', teacher.name)}
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
                      <School sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
                      {teacher.designation}
                    </span>
                    <span className="detail-item">
                      <School sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
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
            <div className="empty-icon"><Person sx={{ fontSize: 48, color: '#94a3b8' }} /></div>
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
              <Assignment sx={{ mr: 1, verticalAlign: 'middle' }} />
              Year Assignments
            </h3>
            <div className="assignment-controls">
              <button
                className="btn btn-secondary btn-small"
                onClick={() => {
                  const updatedTeachers = teachers.map((teacher: Teacher) => ({
                    ...teacher,
                    assignedYears: [...yearsManaged]
                  }));
                  updateConfig({ teachers: updatedTeachers });
                  console.log('Assigned all teachers to all years:', updatedTeachers);
                }}
              >
                ✅ Assign All to All Years
              </button>
              <button
                className="btn btn-secondary btn-small"
                onClick={() => {
                  // Clear all assignments
                  const updatedTeachers = teachers.map((teacher: Teacher) => ({
                    ...teacher,
                    assignedYears: []
                  }));
                  updateConfig({ teachers: updatedTeachers });
                }}
              >
                <Delete sx={{ fontSize: 16, mr: 0.5 }} /> Clear All Assignments
              </button>
              <button
                className="btn btn-primary btn-small"
                onClick={() => {
                  // Force set years and refresh
                  updateConfig({ 
                    yearsManaged: ['FE', 'SE', 'TE', 'BE'],
                    teachers: teachers.length > 0 ? teachers : [
                      { id: '1', name: 'Test Teacher', experience: 5, designation: 'Professor', assignedYears: [] }
                    ]
                  });
                  console.log('Force refreshed matrix with years:', ['FE', 'SE', 'TE', 'BE']);
                }}
              >
                <Refresh sx={{ fontSize: 16, mr: 0.5 }} /> Show Matrix
              </button>
            </div>
          </div>
          
          <div className="assignment-help">
            <p><Info sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle', color: '#3b82f6' }} /> <strong>How to use:</strong> Click checkboxes to assign teachers to years. Use column headers to assign all teachers to a year, or row buttons to assign all years to a teacher.</p>
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
              {teachers.map((teacher: Teacher) => (
                <div key={teacher.id} className="matrix-row">
                  <div className="teacher-cell">
                    <div className="teacher-info">
                      <div className="teacher-name">{teacher.name}</div>
                      <div className="teacher-meta">
                        <span className="designation">{teacher.designation}</span>
                        <span className="teacher-experience">{teacher.experience}y exp</span>
                      </div>
                    </div>
                    <button
                      className="teacher-select-all"
                      onClick={() => {
                        // Toggle all years for this teacher
                        const allAssigned = yearsManaged.every((year: string) => 
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
                      {yearsManaged.every((year: string) => teacher.assignedYears?.includes(year)) ? (
                        <><Clear sx={{ fontSize: 14, mr: 0.5 }} /> Clear</>
                      ) : (
                        <><CheckCircle sx={{ fontSize: 14, mr: 0.5 }} /> All</>
                      )}
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
            <div className="summary-stats">
              {yearsManaged.map((year: string) => {
                const assignedCount = teachers.filter((teacher: Teacher) => 
                  teacher.assignedYears?.includes(year)
                ).length;
                return (
                  <div key={year} className="year-stat">
                    <span className="year-stat-name" style={{ color: getYearColor(year) }}>{year}:</span>
                    <span className={`year-stat-count ${assignedCount === 0 ? 'warning' : ''}`}>
                      {assignedCount} teacher{assignedCount !== 1 ? 's' : ''}
                    </span>
                  </div>
                );
              })}
            </div>
            <div className="unassigned-teachers">
              {teachers.filter((teacher: Teacher) => !teacher.assignedYears || teacher.assignedYears.length === 0).length > 0 && (
                <div className="warning-message">
                  ⚠️ {teachers.filter((teacher: Teacher) => !teacher.assignedYears || teacher.assignedYears.length === 0).length} teacher(s) not assigned to any year
                </div>
              )}
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
