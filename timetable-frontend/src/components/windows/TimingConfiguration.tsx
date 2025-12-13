import React, { useState, useEffect } from 'react';
import { CalendarMonth, MenuBook, Coffee, Lightbulb, Restaurant, BarChart, TrackChanges } from '@mui/icons-material';
import './TimingConfiguration.css';

interface TimingConfigurationProps {
  config: any;
  updateConfig: (updates: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

interface TimeSlot {
  id: number;
  startTime: string;
  endTime: string;
  type: 'lecture' | 'recess';
  duration: number;
}

const TimingConfiguration: React.FC<TimingConfigurationProps> = ({ 
  config, 
  updateConfig, 
  onNext, 
  onPrev 
}) => {
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  // Generate time slots based on college timings
  const generateTimeSlots = () => {
    const slots: TimeSlot[] = [];
    let slotId = 1;

    const startTime = new Date(`2000-01-01T${config.collegeStartTime}:00`);
    const endTime = new Date(`2000-01-01T${config.collegeEndTime}:00`);
    const recessStart = new Date(`2000-01-01T${config.recessStartTime}:00`);
    const recessEnd = new Date(`2000-01-01T${config.recessEndTime}:00`);

    let currentTime = new Date(startTime);

    while (currentTime < endTime) {
      // Check if we're at recess time
      if (currentTime.getTime() === recessStart.getTime()) {
        slots.push({
          id: slotId++,
          startTime: formatTime(currentTime),
          endTime: formatTime(recessEnd),
          type: 'recess',
          duration: (recessEnd.getTime() - recessStart.getTime()) / (1000 * 60)
        });
        currentTime = new Date(recessEnd);
        continue;
      }

      // Regular lecture slot (1 hour)
      const slotEnd = new Date(currentTime.getTime() + 60 * 60 * 1000);
      
      // Don't create slot if it would overlap with recess
      if (slotEnd > recessStart && currentTime < recessStart) {
        slots.push({
          id: slotId++,
          startTime: formatTime(currentTime),
          endTime: formatTime(recessStart),
          type: 'lecture',
          duration: (recessStart.getTime() - currentTime.getTime()) / (1000 * 60)
        });
        currentTime = new Date(recessStart);
        continue;
      }

      // Skip if slot would be during recess
      if (currentTime >= recessStart && currentTime < recessEnd) {
        currentTime = new Date(recessEnd);
        continue;
      }

      slots.push({
        id: slotId++,
        startTime: formatTime(currentTime),
        endTime: formatTime(slotEnd),
        type: 'lecture',
        duration: 60
      });

      currentTime = slotEnd;
    }

    setTimeSlots(slots);
  };

  const formatTime = (date: Date): string => {
    return date.toTimeString().slice(0, 5);
  };

  const formatDisplayTime = (time: string): string => {
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  useEffect(() => {
    generateTimeSlots();
  }, [config.collegeStartTime, config.collegeEndTime, config.recessStartTime, config.recessEndTime]);

  const validateTiming = () => {
    const newErrors: {[key: string]: string} = {};

    const start = new Date(`2000-01-01T${config.collegeStartTime}:00`);
    const end = new Date(`2000-01-01T${config.collegeEndTime}:00`);
    const recessStart = new Date(`2000-01-01T${config.recessStartTime}:00`);
    const recessEnd = new Date(`2000-01-01T${config.recessEndTime}:00`);

    if (start >= end) {
      newErrors.timing = 'College end time must be after start time';
    }

    if (recessStart >= recessEnd) {
      newErrors.recess = 'Recess end time must be after start time';
    }

    if (recessStart <= start || recessEnd >= end) {
      newErrors.recess = 'Recess must be within college hours';
    }

    if (timeSlots.filter(slot => slot.type === 'lecture').length < 4) {
      newErrors.slots = 'At least 4 teaching slots are required for effective timetabling';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateTiming()) {
      // Store the generated time slots in config
      updateConfig({ 
        timeSlots: timeSlots,
        totalTeachingSlots: timeSlots.filter(slot => slot.type === 'lecture').length
      });
      onNext();
    }
  };

  const presetTimings = [
    {
      name: 'Standard Engineering College',
      collegeStartTime: '09:00',
      collegeEndTime: '17:45',
      recessStartTime: '13:00',
      recessEndTime: '13:45'
    },
    {
      name: 'Morning Shift',
      collegeStartTime: '08:00',
      collegeEndTime: '14:00',
      recessStartTime: '11:00',
      recessEndTime: '11:15'
    },
    {
      name: 'Afternoon Shift',
      collegeStartTime: '14:00',
      collegeEndTime: '20:00',
      recessStartTime: '17:00',
      recessEndTime: '17:15'
    }
  ];

  const applyPreset = (preset: any) => {
    updateConfig({
      collegeStartTime: preset.collegeStartTime,
      collegeEndTime: preset.collegeEndTime,
      recessStartTime: preset.recessStartTime,
      recessEndTime: preset.recessEndTime
    });
  };

  const lectureSlots = timeSlots.filter(slot => slot.type === 'lecture');
  const totalTeachingHours = lectureSlots.reduce((sum, slot) => sum + slot.duration, 0) / 60;

  return (
    <div className="timing-configuration">
      {/* Quick Presets */}
      <div className="presets-section">
        <h3 className="section-title">
          <span className="title-icon">⚡</span>
          Quick Presets
        </h3>
        <p className="section-subtitle">
          Choose a common timing pattern or customize your own
        </p>
        
        <div className="presets-grid">
          {presetTimings.map((preset, index) => (
            <div
              key={index}
              className="preset-card"
              onClick={() => applyPreset(preset)}
            >
              <div className="preset-name">{preset.name}</div>
              <div className="preset-timing">
                {formatDisplayTime(preset.collegeStartTime)} - {formatDisplayTime(preset.collegeEndTime)}
              </div>
              <div className="preset-recess">
                Recess: {formatDisplayTime(preset.recessStartTime)} - {formatDisplayTime(preset.recessEndTime)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Custom Timing Configuration */}
      <div className="timing-form">
        <h3 className="section-title">
          <span className="title-icon">⏰</span>
          Custom Timing Configuration
        </h3>
        
        <div className="timing-grid">
          <div className="timing-group">
            <h4 className="group-title">College Hours</h4>
            <div className="time-inputs">
              <div className="time-input-group">
                <label className="form-label">Start Time</label>
                <input
                  type="time"
                  className="form-input time-input"
                  value={config.collegeStartTime}
                  onChange={(e) => updateConfig({ collegeStartTime: e.target.value })}
                />
              </div>
              <div className="time-separator">to</div>
              <div className="time-input-group">
                <label className="form-label">End Time</label>
                <input
                  type="time"
                  className="form-input time-input"
                  value={config.collegeEndTime}
                  onChange={(e) => updateConfig({ collegeEndTime: e.target.value })}
                />
              </div>
            </div>
          </div>

          <div className="timing-group">
            <h4 className="group-title">Recess Period</h4>
            <div className="time-inputs">
              <div className="time-input-group">
                <label className="form-label">Recess Start</label>
                <input
                  type="time"
                  className="form-input time-input"
                  value={config.recessStartTime}
                  onChange={(e) => updateConfig({ recessStartTime: e.target.value })}
                />
              </div>
              <div className="time-separator">to</div>
              <div className="time-input-group">
                <label className="form-label">Recess End</label>
                <input
                  type="time"
                  className="form-input time-input"
                  value={config.recessEndTime}
                  onChange={(e) => updateConfig({ recessEndTime: e.target.value })}
                />
              </div>
            </div>
          </div>
        </div>

        {(errors.timing || errors.recess) && (
          <div className="error-message">
            {errors.timing || errors.recess}
          </div>
        )}
      </div>

      {/* Generated Time Slots Preview */}
      <div className="slots-preview">
        <div className="preview-header">
          <h3 className="section-title">
            <CalendarMonth sx={{ mr: 1, verticalAlign: 'middle' }} />
            Generated Time Slots
          </h3>
          <div className="slots-summary">
            <div className="summary-item">
              <span className="summary-label">Teaching Slots:</span>
              <span className="summary-value">{lectureSlots.length}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Teaching Hours:</span>
              <span className="summary-value">{totalTeachingHours.toFixed(1)} hrs</span>
            </div>
          </div>
        </div>

        <div className="slots-grid">
          {timeSlots.map((slot) => (
            <div
              key={slot.id}
              className={`slot-card ${slot.type}`}
            >
              <div className="slot-number">
                {slot.type === 'lecture' ? `Slot ${lectureSlots.findIndex(s => s.id === slot.id) + 1}` : 'Recess'}
              </div>
              <div className="slot-time">
                {formatDisplayTime(slot.startTime)} - {formatDisplayTime(slot.endTime)}
              </div>
              <div className="slot-duration">
                {slot.duration} min
              </div>
              <div className="slot-icon">
                {slot.type === 'lecture' ? <MenuBook sx={{ fontSize: 20 }} /> : <Coffee sx={{ fontSize: 20 }} />}
              </div>
            </div>
          ))}
        </div>

        {errors.slots && (
          <div className="error-message">
            {errors.slots}
          </div>
        )}
      </div>

      {/* Timing Guidelines */}
      <div className="guidelines-section">
        <h4 className="guidelines-title">
          <Lightbulb sx={{ mr: 1, verticalAlign: 'middle' }} />
          Timing Guidelines
        </h4>
        <div className="guidelines-grid">
          <div className="guideline-item">
            <div className="guideline-icon">⏱️</div>
            <div className="guideline-text">
              <strong>Standard Slot Duration:</strong> 1 hour for lectures, 2-3 hours for labs
            </div>
          </div>
          <div className="guideline-item">
            <div className="guideline-icon"><Restaurant /></div>
            <div className="guideline-text">
              <strong>Recess Timing:</strong> Usually 45 minutes around lunch time (1:00-1:45 PM)
            </div>
          </div>
          <div className="guideline-item">
            <div className="guideline-icon"><BarChart /></div>
            <div className="guideline-text">
              <strong>Minimum Slots:</strong> At least 6-8 teaching slots recommended per day
            </div>
          </div>
          <div className="guideline-item">
            <div className="guideline-icon"><TrackChanges /></div>
            <div className="guideline-text">
              <strong>Best Practice:</strong> Keep consistent timing across all working days
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
          <div className="timing-summary">
            <span className="summary-text">
              {lectureSlots.length} teaching slots • {totalTeachingHours.toFixed(1)} hours daily
            </span>
          </div>
        </div>
        <div className="nav-right">
          <button 
            className="btn btn-primary"
            onClick={handleNext}
            disabled={lectureSlots.length < 4}
          >
            Continue to Teachers
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TimingConfiguration;
