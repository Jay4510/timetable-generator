import React, { useState } from 'react';
import { School, Science, Assignment, MeetingRoom } from '@mui/icons-material';
import './RoomsLabsSetup.css';

interface Room {
  id: string;
  name: string;
  type: 'classroom' | 'lab';
  capacity: number;
  equipment?: string;
  assignedYears: string[];
}

interface RoomsLabsSetupProps {
  config: any;
  updateConfig: (updates: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

const RoomsLabsSetup: React.FC<RoomsLabsSetupProps> = ({ 
  config, 
  updateConfig, 
  onNext, 
  onPrev 
}) => {
  const [showRoomModal, setShowRoomModal] = useState(false);
  const [newRoom, setNewRoom] = useState({
    name: '',
    type: 'classroom' as 'classroom' | 'lab',
    capacity: 60,
    equipment: ''
  });
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  const rooms = config.rooms || [];
  const yearsManaged = config.yearsManaged || [];

  // Common room templates for different departments
  const roomTemplates = {
    'IT': [
      { name: 'Room 101', type: 'classroom', capacity: 60 },
      { name: 'Room 102', type: 'classroom', capacity: 60 },
      { name: 'Room 103', type: 'classroom', capacity: 80 },
      { name: 'Computer Lab 1', type: 'lab', capacity: 30, equipment: 'Computers, Projector, AC' },
      { name: 'Computer Lab 2', type: 'lab', capacity: 30, equipment: 'Computers, Projector, AC' },
      { name: 'Network Lab', type: 'lab', capacity: 25, equipment: 'Network Equipment, Servers' },
      { name: 'Project Lab', type: 'lab', capacity: 40, equipment: 'Computers, Development Tools' }
    ],
    'CS': [
      { name: 'Classroom A', type: 'classroom', capacity: 70 },
      { name: 'Classroom B', type: 'classroom', capacity: 70 },
      { name: 'Programming Lab', type: 'lab', capacity: 35, equipment: 'Computers, IDEs, Compilers' },
      { name: 'Graphics Lab', type: 'lab', capacity: 30, equipment: 'High-end Graphics Workstations' },
      { name: 'AI/ML Lab', type: 'lab', capacity: 25, equipment: 'GPU Workstations, ML Software' }
    ],
    'ME': [
      { name: 'Lecture Hall 1', type: 'classroom', capacity: 100 },
      { name: 'Lecture Hall 2', type: 'classroom', capacity: 80 },
      { name: 'Workshop', type: 'lab', capacity: 40, equipment: 'Machines, Tools, Safety Equipment' },
      { name: 'CAD Lab', type: 'lab', capacity: 30, equipment: 'CAD Workstations, Software' },
      { name: 'Materials Lab', type: 'lab', capacity: 20, equipment: 'Testing Equipment, Specimens' }
    ],
    'CE': [
      { name: 'Room 201', type: 'classroom', capacity: 80 },
      { name: 'Room 202', type: 'classroom', capacity: 60 },
      { name: 'Survey Lab', type: 'lab', capacity: 25, equipment: 'Survey Instruments, Total Station' },
      { name: 'Concrete Lab', type: 'lab', capacity: 30, equipment: 'Testing Machines, Specimens' },
      { name: 'Soil Lab', type: 'lab', capacity: 20, equipment: 'Soil Testing Equipment' }
    ],
    'HS': [
      { name: 'Physics Lab', type: 'lab', capacity: 30, equipment: 'Physics Instruments, Apparatus' },
      { name: 'Chemistry Lab', type: 'lab', capacity: 25, equipment: 'Chemical Equipment, Fume Hoods' },
      { name: 'Language Lab', type: 'lab', capacity: 40, equipment: 'Audio Equipment, Computers' }
    ]
  };

  const generateId = () => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };

  const addRoom = () => {
    const newErrors: {[key: string]: string} = {};

    if (!newRoom.name.trim()) {
      newErrors.name = 'Room name is required';
    }

    if (rooms.some((r: Room) => r.name.toLowerCase() === newRoom.name.toLowerCase())) {
      newErrors.name = 'Room with this name already exists';
    }

    if (newRoom.capacity < 1 || newRoom.capacity > 200) {
      newErrors.capacity = 'Capacity must be between 1 and 200';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const room: Room = {
      id: generateId(),
      name: newRoom.name.trim(),
      type: newRoom.type,
      capacity: newRoom.capacity,
      equipment: newRoom.equipment.trim() || undefined,
      assignedYears: []
    };

    updateConfig({
      rooms: [...rooms, room]
    });

    setNewRoom({ name: '', type: 'classroom', capacity: 60, equipment: '' });
    setShowRoomModal(false);
    setErrors({});
  };

  const deleteRoom = (roomId: string) => {
    if (window.confirm('Are you sure you want to remove this room?')) {
      updateConfig({
        rooms: rooms.filter((r: Room) => r.id !== roomId)
      });
    }
  };

  const updateRoomYears = (roomId: string, year: string, assigned: boolean) => {
    const updatedRooms = rooms.map((room: Room) => {
      if (room.id === roomId) {
        const currentYears = room.assignedYears || [];
        const newYears = assigned
          ? [...currentYears, year]
          : currentYears.filter(y => y !== year);
        return { ...room, assignedYears: newYears };
      }
      return room;
    });

    updateConfig({ rooms: updatedRooms });
  };

  const bulkAssignYear = (year: string, roomType: 'classroom' | 'lab' | 'all', assignAll: boolean) => {
    const updatedRooms = rooms.map((room: Room) => {
      if (roomType === 'all' || room.type === roomType) {
        const currentYears = room.assignedYears || [];
        const newYears = assignAll
          ? [...new Set([...currentYears, year])]
          : currentYears.filter(y => y !== year);
        return { ...room, assignedYears: newYears };
      }
      return room;
    });

    updateConfig({ rooms: updatedRooms });
  };

  const loadTemplate = () => {
    const departmentRooms = roomTemplates[config.department as keyof typeof roomTemplates] || [];
    const templateRooms = departmentRooms.map((r: any) => ({
      id: generateId(),
      name: r.name,
      type: r.type,
      capacity: r.capacity,
      equipment: r.equipment,
      assignedYears: []
    }));

    updateConfig({
      rooms: [...rooms, ...templateRooms]
    });
  };

  const getYearColor = (year: string) => {
    const colors: {[key: string]: string} = {
      'FE': '#10b981',
      'SE': '#3b82f6',
      'TE': '#f59e0b',
      'BE': '#ef4444'
    };
    return colors[year] || '#6b7280';
  };

  const validateAndNext = () => {
    const classrooms = rooms.filter((r: Room) => r.type === 'classroom');
    const labs = rooms.filter((r: Room) => r.type === 'lab');

    if (classrooms.length === 0) {
      setErrors({ general: 'Please add at least one classroom before continuing' });
      return;
    }

    if (labs.length === 0) {
      setErrors({ general: 'Please add at least one lab before continuing' });
      return;
    }

    const unassignedRooms = rooms.filter((r: Room) => !r.assignedYears || r.assignedYears.length === 0);
    if (unassignedRooms.length > 0) {
      setErrors({ general: 'All rooms must be assigned to at least one year' });
      return;
    }

    setErrors({});
    onNext();
  };

  const classrooms = rooms.filter((r: Room) => r.type === 'classroom');
  const labs = rooms.filter((r: Room) => r.type === 'lab');

  return (
    <div className="rooms-labs-setup">
      {/* Quick Template */}
      <div className="template-section">
        <h3 className="section-title">
          Quick Start Template
        </h3>
        <p className="section-subtitle">
          Load common rooms and labs for {config.department} department
        </p>
        
        <div className="template-card">
          <div className="template-info">
            <h4 className="template-name">{config.department} Department Rooms</h4>
            <p className="template-description">
              Standard classrooms and laboratories for {config.department} department
            </p>
            <div className="template-preview">
              {roomTemplates[config.department as keyof typeof roomTemplates]?.slice(0, 3).map((room, i) => (
                <span key={i} className="preview-room">
                  {room.name}
                </span>
              ))}
              {(roomTemplates[config.department as keyof typeof roomTemplates]?.length || 0) > 3 && (
                <span className="preview-more">
                  +{(roomTemplates[config.department as keyof typeof roomTemplates]?.length || 0) - 3} more
                </span>
              )}
            </div>
          </div>
          <button
            className="btn btn-primary"
            onClick={loadTemplate}
            disabled={!roomTemplates[config.department as keyof typeof roomTemplates]}
          >
            Load Template
          </button>
        </div>
      </div>

      {/* Add Room Section */}
      <div className="add-room-section">
        <div className="section-header">
          <h3 className="section-title">
            Rooms & Labs ({rooms.length})
          </h3>
          <div className="add-room-buttons">
            <button
              className="btn btn-secondary"
              onClick={() => {
                setNewRoom({ ...newRoom, type: 'classroom' });
                setShowRoomModal(true);
              }}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
              Add Classroom
            </button>
            <button
              className="btn btn-primary"
              onClick={() => {
                setNewRoom({ ...newRoom, type: 'lab' });
                setShowRoomModal(true);
              }}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
              Add Lab
            </button>
          </div>
        </div>

        {errors.general && (
          <div className="error-message">{errors.general}</div>
        )}

        {/* Rooms Display */}
        <div className="rooms-display">
          {/* Classrooms */}
          <div className="room-type-section">
            <h4 className="room-type-title">
              <School sx={{ mr: 1, verticalAlign: 'middle' }} />
              Classrooms ({classrooms.length})
            </h4>
            {classrooms.length > 0 ? (
              <div className="rooms-grid">
                {classrooms.map(room => (
                  <div key={room.id} className="room-card classroom">
                    <div className="room-header">
                      <div className="room-info">
                        <h5 className="room-name">{room.name}</h5>
                        <span className="room-capacity">Capacity: {room.capacity}</span>
                      </div>
                      <button
                        className="action-btn delete-btn"
                        onClick={() => deleteRoom(room.id)}
                        title="Delete Room"
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
                      </button>
                    </div>
                    <div className="room-years">
                      <span className="years-label">Assigned Years:</span>
                      <div className="years-badges">
                        {room.assignedYears && room.assignedYears.length > 0 ? (
                          room.assignedYears.map(year => (
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
                ))}
              </div>
            ) : (
              <div className="empty-room-type">
                <span className="empty-icon"><School sx={{ fontSize: 48, color: '#94a3b8' }} /></span>
                <span>No classrooms added yet</span>
              </div>
            )}
          </div>

          {/* Labs */}
          <div className="room-type-section">
            <h4 className="room-type-title">
              <Science sx={{ mr: 1, verticalAlign: 'middle' }} />
              Laboratories ({labs.length})
            </h4>
            {labs.length > 0 ? (
              <div className="rooms-grid">
                {labs.map(room => (
                  <div key={room.id} className="room-card lab">
                    <div className="room-header">
                      <div className="room-info">
                        <h5 className="room-name">{room.name}</h5>
                        <span className="room-capacity">Capacity: {room.capacity}</span>
                        {room.equipment && (
                          <span className="room-equipment">{room.equipment}</span>
                        )}
                      </div>
                      <button
                        className="action-btn delete-btn"
                        onClick={() => deleteRoom(room.id)}
                        title="Delete Room"
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
                      </button>
                    </div>
                    <div className="room-years">
                      <span className="years-label">Assigned Years:</span>
                      <div className="years-badges">
                        {room.assignedYears && room.assignedYears.length > 0 ? (
                          room.assignedYears.map(year => (
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
                ))}
              </div>
            ) : (
              <div className="empty-room-type">
                <span className="empty-icon"><Science sx={{ fontSize: 48, color: '#94a3b8' }} /></span>
                <span>No labs added yet</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Year Assignment Matrix */}
      {rooms.length > 0 && (
        <div className="assignment-section">
          <h3 className="section-title">
            <Assignment sx={{ mr: 1, verticalAlign: 'middle' }} />
            Room Assignments by Year
          </h3>
          <p className="section-subtitle">
            Assign rooms and labs to different academic years. Rooms can be shared across years.
          </p>

          {yearsManaged.map((year: string) => (
            <div key={year} className="year-assignment-section">
              <div className="year-header">
                <h4 className="year-title" style={{ color: getYearColor(year) }}>
                  {year} Year Assignments
                </h4>
                <div className="bulk-actions">
                  <button
                    className="bulk-btn"
                    onClick={() => {
                      const allClassroomsAssigned = classrooms.every((r: Room) => 
                        r.assignedYears && r.assignedYears.includes(year)
                      );
                      bulkAssignYear(year, 'classroom', !allClassroomsAssigned);
                    }}
                  >
                    {classrooms.every((r: Room) => r.assignedYears && r.assignedYears.includes(year)) ? '☑️' : '☐'} All Classrooms
                  </button>
                  <button
                    className="bulk-btn"
                    onClick={() => {
                      const allLabsAssigned = labs.every((r: Room) => 
                        r.assignedYears && r.assignedYears.includes(year)
                      );
                      bulkAssignYear(year, 'lab', !allLabsAssigned);
                    }}
                  >
                    {labs.every((r: Room) => r.assignedYears && r.assignedYears.includes(year)) ? '☑️' : '☐'} All Labs
                  </button>
                </div>
              </div>

              <div className="year-rooms-grid">
                <div className="room-type-column">
                  <h5 className="column-title">
                    <School sx={{ mr: 0.5, fontSize: 18, verticalAlign: 'middle' }} />
                    Lecture Rooms
                  </h5>
                  <div className="room-checkboxes">
                    {classrooms.map((room: Room) => (
                      <label key={room.id} className="room-checkbox">
                        <input
                          type="checkbox"
                          checked={room.assignedYears && room.assignedYears.includes(year)}
                          onChange={(e) => updateRoomYears(room.id, year, e.target.checked)}
                        />
                        <span className="checkbox-custom"></span>
                        <span className="room-label">
                          {room.name} ({room.capacity})
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="room-type-column">
                  <h5 className="column-title">
                    <Science sx={{ mr: 0.5, fontSize: 18, verticalAlign: 'middle' }} />
                    Laboratories
                  </h5>
                  <div className="room-checkboxes">
                    {labs.map((room: Room) => (
                      <label key={room.id} className="room-checkbox">
                        <input
                          type="checkbox"
                          checked={room.assignedYears && room.assignedYears.includes(year)}
                          onChange={(e) => updateRoomYears(room.id, year, e.target.checked)}
                        />
                        <span className="checkbox-custom"></span>
                        <span className="room-label">
                          {room.name} ({room.capacity})
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Room Modal */}
      {showRoomModal && (
        <div className="modal-overlay" onClick={() => setShowRoomModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">
                Add New {newRoom.type === 'classroom' ? 'Classroom' : 'Laboratory'}
              </h3>
              <button
                className="modal-close"
                onClick={() => setShowRoomModal(false)}
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">
                  {newRoom.type === 'classroom' ? 'Classroom' : 'Lab'} Name
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder={`e.g., ${newRoom.type === 'classroom' ? 'Room 101' : 'Computer Lab 1'}`}
                  value={newRoom.name}
                  onChange={(e) => setNewRoom({ ...newRoom, name: e.target.value })}
                />
                {errors.name && <div className="error-message">{errors.name}</div>}
              </div>

              <div className="form-row grid-2">
                <div className="form-group">
                  <label className="form-label">Capacity</label>
                  <input
                    type="number"
                    className="form-input"
                    min="1"
                    max="200"
                    value={newRoom.capacity}
                    onChange={(e) => setNewRoom({ ...newRoom, capacity: parseInt(e.target.value) || 60 })}
                  />
                  {errors.capacity && <div className="error-message">{errors.capacity}</div>}
                </div>

                <div className="form-group">
                  <label className="form-label">Type</label>
                  <select
                    className="form-select"
                    value={newRoom.type}
                    onChange={(e) => setNewRoom({ ...newRoom, type: e.target.value as 'classroom' | 'lab' })}
                  >
                    <option value="classroom">Classroom</option>
                    <option value="lab">Laboratory</option>
                  </select>
                </div>
              </div>

              {newRoom.type === 'lab' && (
                <div className="form-group">
                  <label className="form-label">Equipment & Facilities</label>
                  <textarea
                    className="form-input"
                    rows={3}
                    placeholder="e.g., Computers, Projector, AC, Network Equipment"
                    value={newRoom.equipment}
                    onChange={(e) => setNewRoom({ ...newRoom, equipment: e.target.value })}
                  />
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setShowRoomModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={addRoom}
                disabled={!newRoom.name.trim()}
              >
                Add {newRoom.type === 'classroom' ? 'Classroom' : 'Lab'}
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
          <div className="rooms-summary">
            <span className="summary-text">
              {classrooms.length} classrooms • {labs.length} labs • Cross-year sharing enabled
            </span>
          </div>
        </div>
        <div className="nav-right">
          <button 
            className="btn btn-primary"
            onClick={validateAndNext}
            disabled={classrooms.length === 0 || labs.length === 0}
          >
            Continue to Preferences
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default RoomsLabsSetup;
