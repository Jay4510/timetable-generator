import React, { useState } from 'react';
import { Box, Stepper, Step, StepLabel, Container, LinearProgress, Typography, Paper } from '@mui/material';
import './DMCETimetableGenerator.css';

// Import all window components
import DMCEHeader from './DMCEHeader';
import WelcomeSetup from './windows/WelcomeSetup';
import TimingConfiguration from './windows/TimingConfiguration';
import TeacherManagement from './windows/TeacherManagement';
import ProficiencyRating from './windows/ProficiencyRating';
import RoomsLabsSetup from './windows/RoomsLabsSetup';
import TimePreferences from './windows/TimePreferences';
import FinalConfiguration from './windows/FinalConfiguration';
import GenerationProcess from './windows/GenerationProcess';
import ResultsDownload from './windows/ResultsDownload';

interface TimetableConfig {
  // Department setup
  department: string;
  academicYear: string;
  ttInchargeName: string;
  designation: string;
  contactEmail: string;
  yearsManaged: string[];
  
  // Timing configuration
  timing?: {
    startTime: string;
    endTime: string;
    recessStart: string;
    recessEnd: string;
    timeSlots: Array<{
      start: string;
      end: string;
      type: 'lecture' | 'lab' | 'recess';
    }>;
  };
  
  // Teachers
  teachers: Array<{
    id: string;
    name: string;
    experience: number;
    designation: string;
    assignedYears: string[];
  }>;
  
  // Subjects
  subjects: Array<{
    id: string;
    name: string;
    code: string;
    type: 'theory' | 'practical';
    hoursPerWeek: number;
  }>;
  
  // Proficiency ratings
  proficiency: {
    [teacherId: string]: {
      [subjectId: string]: {
        knowledge: number;
        willingness: number;
      };
    };
  };
  
  // Rooms and labs
  rooms?: {
    classrooms: Array<{
      id: string;
      name: string;
      capacity: number;
      equipment?: string;
    }>;
    labs: Array<{
      id: string;
      name: string;
      capacity: number;
      equipment: string;
    }>;
  };
  
  // Room assignments
  roomAssignments?: {
    [year: string]: {
      classrooms: string[];
      labs: string[];
    };
  };
  
  // Time preferences
  teacherPreferences?: {
    [teacherId: string]: {
      lecturePreference: 'morning' | 'afternoon' | 'flexible';
      labPreference: 'morning' | 'afternoon' | 'flexible';
      projectPreference: 'morning' | 'afternoon' | 'flexible';
      notes?: string;
    };
  };
  
  // Final configuration
  divisions?: {
    [year: string]: {
      count: number;
      names: string[];
      batchesPerDivision: number;
      studentsPerBatch: number;
    };
  };
  
  projectWork?: {
    [year: string]: {
      hasProjects: boolean;
      projectType: string;
      hoursPerWeek: number;
      timeSlot: string;
      groupSize: number;
      supervisorsNeeded: number;
    };
  };
  
  balanceSettings?: {
    workloadBalance: number;
    timeDistribution: number;
    roomUtilization: number;
    conflictTolerance: number;
    optimizationLevel: string;
  };
  
  // Generation result
  generationResult?: any;
}

const DMCETimetableGenerator: React.FC = () => {
  const [currentWindow, setCurrentWindow] = useState(1);
  const [config, setConfig] = useState<TimetableConfig>({
    department: '',
    academicYear: '2025-26',
    ttInchargeName: '',
    designation: '',
    contactEmail: '',
    yearsManaged: [],
    teachers: [],
    subjects: [],
    proficiency: {}
  });


  const windowTitles = [
    'Welcome & Department Setup',
    'College Timing Configuration', 
    'Teacher Management',
    'Teacher Proficiency Rating',
    'Rooms and Labs Setup',
    'Teacher Time Preferences',
    'Final Configuration',
    'Generation Process',
    'Results & Download'
  ];

  const updateConfig = (updates: Partial<TimetableConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  const nextWindow = () => {
    if (currentWindow < 9) {
      setCurrentWindow(prev => prev + 1);
    }
  };

  const prevWindow = () => {
    if (currentWindow > 1) {
      setCurrentWindow(prev => prev - 1);
    }
  };

  const goToWindow = (windowNumber: number) => {
    setCurrentWindow(windowNumber);
  };

  const renderCurrentWindow = () => {
    switch (currentWindow) {
      case 1:
        return (
          <WelcomeSetup 
            config={config}
            updateConfig={updateConfig}
            onNext={nextWindow}
          />
        );
      case 2:
        return (
          <TimingConfiguration
            config={config}
            updateConfig={updateConfig}
            onNext={nextWindow}
            onPrev={prevWindow}
          />
        );
      case 3:
        return (
          <TeacherManagement
            config={config}
            updateConfig={updateConfig}
            onNext={nextWindow}
            onPrev={prevWindow}
          />
        );
      case 4:
        return (
          <ProficiencyRating
            config={config}
            updateConfig={updateConfig}
            onNext={nextWindow}
            onPrev={prevWindow}
          />
        );
      case 5:
        return (
          <RoomsLabsSetup
            config={config}
            updateConfig={updateConfig}
            onNext={nextWindow}
            onPrev={prevWindow}
          />
        );
      case 6:
        return (
          <TimePreferences
            config={config}
            updateConfig={updateConfig}
            onNext={nextWindow}
            onPrev={prevWindow}
          />
        );
      case 7:
        return (
          <FinalConfiguration
            config={config}
            updateConfig={updateConfig}
            onNext={nextWindow}
            onPrev={prevWindow}
          />
        );
      case 8:
        return (
          <GenerationProcess
            config={config}
            updateConfig={updateConfig}
            onNext={nextWindow}
            onPrev={prevWindow}
          />
        );
      case 9:
        return (
          <ResultsDownload
            config={config}
            updateConfig={updateConfig}
            onNext={() => {
              // Process completed
              alert('Timetable generation process completed successfully!');
            }}
            onPrev={prevWindow}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="dmce-timetable-generator">
      <DMCEHeader 
        currentAcademicYear={config.academicYear}
        selectedDepartment={config.department}
      />
      
      {/* Progress Indicator */}
      <div className="progress-container">
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${(currentWindow / 9) * 100}%` }}
          />
        </div>
        <div className="progress-steps">
          {windowTitles.map((title, index) => (
            <div
              key={index}
              className={`progress-step ${currentWindow > index + 1 ? 'completed' : ''} ${currentWindow === index + 1 ? 'active' : ''}`}
              onClick={() => goToWindow(index + 1)}
            >
              <div className="step-number">{index + 1}</div>
              <div className="step-title">{title}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content">
        <div className="window-container">
          <div className="window-header">
            <h2 className="window-title">
              Step {currentWindow}: {windowTitles[currentWindow - 1]}
            </h2>
            <div className="window-subtitle">
              {currentWindow === 1 && "Let's get started with your department information"}
              {currentWindow === 2 && "Configure your college's daily schedule"}
              {currentWindow === 3 && "Add teachers and assign them to years"}
              {currentWindow === 4 && "Rate teacher expertise for each subject"}
              {currentWindow === 5 && "Set up classrooms and laboratories"}
              {currentWindow === 6 && "Configure teacher time preferences"}
              {currentWindow === 7 && "Final settings and configurations"}
              {currentWindow === 8 && "Generating your perfect timetable"}
              {currentWindow === 9 && "Your timetable is ready!"}
            </div>
          </div>
          
          <div className="window-content">
            {renderCurrentWindow()}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="dmce-footer">
        <div className="footer-content">
          <div className="footer-left">
            <p>&copy; 2025 Datta Meghe College of Engineering, Airoli, Navi Mumbai</p>
          </div>
          <div className="footer-right">
            <p>Smart Timetable Generator v2.0 | Powered by AI</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default DMCETimetableGenerator;
