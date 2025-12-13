import React, { useState } from 'react';
import { TrackChanges, AccountBalance, Business, People, School, WbSunny, WbTwilight, Sync, Assignment, ExpandLess, ExpandMore } from '@mui/icons-material';
import './FinalConfiguration.css';

interface FinalConfigurationProps {
  config: any;
  updateConfig: (updates: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

const FinalConfiguration: React.FC<FinalConfigurationProps> = ({ 
  config, 
  updateConfig, 
  onNext, 
  onPrev 
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const yearsManaged = config.yearsManaged || [];
  const divisions = config.divisions || {};
  const projectWork = config.projectWork || {};
  const balanceSettings = config.balanceSettings || {
    workloadBalance: 85,
    timeDistribution: 70,
    roomUtilization: 80,
    conflictTolerance: 0,
    optimizationLevel: 'balanced'
  };

  // Division configuration
  const updateDivisions = (year: string, divisionCount: number) => {
    const updatedDivisions = { ...divisions };
    const divisionNames = [];
    
    for (let i = 0; i < divisionCount; i++) {
      divisionNames.push(String.fromCharCode(65 + i)); // A, B, C, D...
    }
    
    updatedDivisions[year] = {
      count: divisionCount,
      names: divisionNames,
      batchesPerDivision: updatedDivisions[year]?.batchesPerDivision || 3,
      studentsPerBatch: updatedDivisions[year]?.studentsPerBatch || 20
    };
    
    updateConfig({ divisions: updatedDivisions });
  };

  const updateBatchConfig = (year: string, field: string, value: number) => {
    const updatedDivisions = { ...divisions };
    if (!updatedDivisions[year]) {
      updatedDivisions[year] = { count: 2, names: ['A', 'B'], batchesPerDivision: 3, studentsPerBatch: 20 };
    }
    updatedDivisions[year][field] = value;
    updateConfig({ divisions: updatedDivisions });
  };

  // Project work configuration
  const updateProjectWork = (year: string, field: string, value: any) => {
    const updatedProjectWork = { ...projectWork };
    if (!updatedProjectWork[year]) {
      updatedProjectWork[year] = {
        hasProjects: false,
        projectType: 'mini',
        hoursPerWeek: 4,
        timeSlot: 'afternoon',
        groupSize: 4
      };
    }
    updatedProjectWork[year][field] = value;
    updateConfig({ projectWork: updatedProjectWork });
  };

  // Balance settings
  const updateBalanceSettings = (field: string, value: any) => {
    const updatedSettings = { ...balanceSettings };
    updatedSettings[field] = value;
    updateConfig({ balanceSettings: updatedSettings });
  };

  // Smart defaults
  const setSmartDefaults = () => {
    const smartDivisions: any = {};
    const smartProjectWork: any = {};
    
    yearsManaged.forEach((year: string) => {
      // Division defaults based on year
      let divisionCount = 2; // Default 2 divisions
      if (year === 'FE') divisionCount = 3; // FE usually has more students
      if (year === 'BE') divisionCount = 2; // BE might have fewer
      
      smartDivisions[year] = {
        count: divisionCount,
        names: Array.from({ length: divisionCount }, (_, i) => String.fromCharCode(65 + i)),
        batchesPerDivision: 3,
        studentsPerBatch: year === 'FE' ? 25 : 20 // FE batches slightly larger
      };
      
      // Project work defaults
      smartProjectWork[year] = {
        hasProjects: year === 'TE' || year === 'BE', // Only TE and BE have projects
        projectType: year === 'TE' ? 'mini' : 'major',
        hoursPerWeek: year === 'TE' ? 4 : 6,
        timeSlot: 'afternoon',
        groupSize: year === 'TE' ? 4 : 3
      };
    });
    
    updateConfig({ 
      divisions: smartDivisions, 
      projectWork: smartProjectWork,
      balanceSettings: {
        workloadBalance: 85,
        timeDistribution: 70,
        roomUtilization: 80,
        conflictTolerance: 0,
        optimizationLevel: 'balanced'
      }
    });
  };

  const validateAndNext = () => {
    // Ensure all years have division configuration
    const missingDivisions = yearsManaged.filter((year: string) => !divisions[year]);
    if (missingDivisions.length > 0) {
      alert(`Please configure divisions for: ${missingDivisions.join(', ')}`);
      return;
    }

    // Validate project work for TE and BE
    const projectYears = yearsManaged.filter((year: string) => year === 'TE' || year === 'BE');
    const missingProjects = projectYears.filter((year: string) => 
      !projectWork[year] || !projectWork[year].hasProjects
    );
    
    if (missingProjects.length > 0) {
      const confirm = window.confirm(
        `${missingProjects.join(', ')} typically have project work. Continue without projects?`
      );
      if (!confirm) return;
    }

    onNext();
  };

  const getTotalStudents = () => {
    return yearsManaged.reduce((total: number, year: string) => {
      const div = divisions[year];
      if (div) {
        return total + (div.count * div.batchesPerDivision * div.studentsPerBatch);
      }
      return total;
    }, 0);
  };

  const getTotalDivisions = () => {
    return yearsManaged.reduce((total: number, year: string) => {
      return total + (divisions[year]?.count || 0);
    }, 0);
  };

  // ✅ REMOVED: getProjectSupervisors function - not needed anymore

  return (
    <div className="final-configuration">
      {/* Quick Setup */}
      <div className="quick-setup-section">
        <h3 className="section-title">
          <span className="title-icon">⚡</span>
          Quick Setup
        </h3>
        <p className="section-subtitle">
          Apply smart defaults based on typical DMCE patterns
        </p>
        
        <div className="quick-setup-card">
          <div className="setup-info">
            <h4 className="setup-title">Smart Configuration</h4>
            <p className="setup-description">
              Automatically configure divisions, batches, and project work based on year levels and typical college patterns
            </p>
            <ul className="setup-features">
              <li>✅ FE: 3 divisions (higher intake)</li>
              <li>✅ SE/TE/BE: 2 divisions each</li>
              <li>✅ 3 batches per division (A1, A2, A3)</li>
              <li>✅ Project work for TE (Mini) and BE (Major)</li>
              <li>✅ Balanced optimization settings</li>
            </ul>
          </div>
          <button
            className="btn btn-primary setup-btn"
            onClick={setSmartDefaults}
          >
            <span className="btn-icon"><TrackChanges sx={{ fontSize: 18 }} /></span>
            Apply Smart Defaults
          </button>
        </div>
      </div>

      {/* Division Configuration */}
      <div className="divisions-section">
        <h3 className="section-title">
          <span className="title-icon"><AccountBalance sx={{ fontSize: 18 }} /></span>
          Division & Batch Configuration
        </h3>
        <p className="section-subtitle">
          Configure how students are organized into divisions and batches
        </p>

        <div className="divisions-grid">
          {yearsManaged.map((year: string) => (
            <div key={year} className="division-card">
              <div className="division-header">
                <div className="year-badge" data-year={year.toLowerCase()}>
                  {year}
                </div>
                <h4 className="division-title">
                  {year === 'FE' ? 'First Year' : 
                   year === 'SE' ? 'Second Year' : 
                   year === 'TE' ? 'Third Year' : 'Final Year'} Engineering
                </h4>
              </div>

              <div className="division-config">
                <div className="config-row">
                  <label className="config-label">
                    <span className="label-icon"><Business sx={{ fontSize: 18 }} /></span>
                    Number of Divisions
                  </label>
                  <div className="division-selector">
                    {[1, 2, 3, 4].map(count => (
                      <button
                        key={count}
                        className={`division-btn ${
                          divisions[year]?.count === count ? 'selected' : ''
                        }`}
                        onClick={() => updateDivisions(year, count)}
                      >
                        {count} Div{count > 1 ? 's' : ''}
                        <span className="division-names">
                          ({Array.from({ length: count }, (_, i) => 
                            String.fromCharCode(65 + i)
                          ).join(', ')})
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                {divisions[year] && (
                  <>
                    <div className="config-row">
                      <label className="config-label">
                        <span className="label-icon"><People sx={{ fontSize: 18 }} /></span>
                        Batches per Division
                      </label>
                      <div className="number-input-group">
                        <button
                          className="number-btn"
                          onClick={() => updateBatchConfig(year, 'batchesPerDivision', 
                            Math.max(1, (divisions[year]?.batchesPerDivision || 3) - 1))}
                        >
                          -
                        </button>
                        <input
                          type="number"
                          className="number-input"
                          value={divisions[year]?.batchesPerDivision || 3}
                          onChange={(e) => updateBatchConfig(year, 'batchesPerDivision', 
                            parseInt(e.target.value) || 3)}
                          min="1"
                          max="6"
                        />
                        <button
                          className="number-btn"
                          onClick={() => updateBatchConfig(year, 'batchesPerDivision', 
                            Math.min(6, (divisions[year]?.batchesPerDivision || 3) + 1))}
                        >
                          +
                        </button>
                      </div>
                    </div>

                    <div className="config-row">
                      <label className="config-label">
                        <span className="label-icon"><School sx={{ fontSize: 18 }} /></span>
                        Students per Batch
                      </label>
                      <div className="number-input-group">
                        <button
                          className="number-btn"
                          onClick={() => updateBatchConfig(year, 'studentsPerBatch', 
                            Math.max(10, (divisions[year]?.studentsPerBatch || 20) - 5))}
                        >
                          -5
                        </button>
                        <input
                          type="number"
                          className="number-input"
                          value={divisions[year]?.studentsPerBatch || 20}
                          onChange={(e) => updateBatchConfig(year, 'studentsPerBatch', 
                            parseInt(e.target.value) || 20)}
                          min="10"
                          max="40"
                          step="5"
                        />
                        <button
                          className="number-btn"
                          onClick={() => updateBatchConfig(year, 'studentsPerBatch', 
                            Math.min(40, (divisions[year]?.studentsPerBatch || 20) + 5))}
                        >
                          +5
                        </button>
                      </div>
                    </div>

                    <div className="division-summary">
                      <div className="summary-item">
                        <span className="summary-label">Total Students:</span>
                        <span className="summary-value">
                          {(divisions[year]?.count || 0) * 
                           (divisions[year]?.batchesPerDivision || 0) * 
                           (divisions[year]?.studentsPerBatch || 0)}
                        </span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Total Batches:</span>
                        <span className="summary-value">
                          {(divisions[year]?.count || 0) * (divisions[year]?.batchesPerDivision || 0)}
                        </span>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Project Work Configuration */}
      <div className="project-work-section">
        <h3 className="section-title">
          <span className="title-icon"><TrackChanges sx={{ fontSize: 18 }} /></span>
          Project Work Configuration
        </h3>
        <p className="section-subtitle">
          Configure project work for TE (Mini Projects) and BE (Major Projects)
        </p>

        <div className="project-grid">
          {yearsManaged.filter(year => year === 'TE' || year === 'BE').map((year: string) => (
            <div key={year} className="project-card">
              <div className="project-header">
                <div className="year-badge" data-year={year.toLowerCase()}>
                  {year}
                </div>
                <h4 className="project-title">
                  {year === 'TE' ? 'Mini Projects' : 'Major Projects'}
                </h4>
                <label className="project-toggle">
                  <input
                    type="checkbox"
                    checked={projectWork[year]?.hasProjects || false}
                    onChange={(e) => updateProjectWork(year, 'hasProjects', e.target.checked)}
                  />
                  <span className="toggle-slider"></span>
                  <span className="toggle-label">Enable Projects</span>
                </label>
              </div>

              {projectWork[year]?.hasProjects && (
                <div className="project-config">
                  <div className="config-row">
                    <label className="config-label">Project Type</label>
                    <select
                      className="config-select"
                      value={projectWork[year]?.projectType || 'mini'}
                      onChange={(e) => updateProjectWork(year, 'projectType', e.target.value)}
                    >
                      <option value="mini">Mini Project</option>
                      <option value="major">Major Project</option>
                      <option value="research">Research Project</option>
                      <option value="industry">Industry Project</option>
                    </select>
                  </div>

                  <div className="config-row">
                    <label className="config-label">Hours per Week</label>
                    <div className="number-input-group">
                      <button
                        className="number-btn"
                        onClick={() => updateProjectWork(year, 'hoursPerWeek', 
                          Math.max(2, (projectWork[year]?.hoursPerWeek || 4) - 2))}
                      >
                        -2
                      </button>
                      <input
                        type="number"
                        className="number-input"
                        value={projectWork[year]?.hoursPerWeek || 4}
                        onChange={(e) => updateProjectWork(year, 'hoursPerWeek', 
                          parseInt(e.target.value) || 4)}
                        min="2"
                        max="12"
                        step="2"
                      />
                      <button
                        className="number-btn"
                        onClick={() => updateProjectWork(year, 'hoursPerWeek', 
                          Math.min(12, (projectWork[year]?.hoursPerWeek || 4) + 2))}
                      >
                        +2
                      </button>
                    </div>
                  </div>

                  <div className="config-row">
                    <label className="config-label">Preferred Time</label>
                    <div className="time-preference-buttons">
                      {[
                        { key: 'morning', label: 'Morning', icon: <WbSunny sx={{ fontSize: 18 }} /> },
                        { key: 'afternoon', label: 'Afternoon', icon: <WbTwilight sx={{ fontSize: 18 }} /> },
                        { key: 'flexible', label: 'Flexible', icon: <Sync sx={{ fontSize: 18 }} /> }
                      ].map(time => (
                        <button
                          key={time.key}
                          className={`time-btn ${
                            projectWork[year]?.timeSlot === time.key ? 'selected' : ''
                          }`}
                          onClick={() => updateProjectWork(year, 'timeSlot', time.key)}
                        >
                          <span className="time-icon">{time.icon}</span>
                          {time.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="config-row">
                    <label className="config-label">Group Size</label>
                    <div className="number-input-group">
                      <button
                        className="number-btn"
                        onClick={() => updateProjectWork(year, 'groupSize', 
                          Math.max(2, (projectWork[year]?.groupSize || 4) - 1))}
                      >
                        -
                      </button>
                      <input
                        type="number"
                        className="number-input"
                        value={projectWork[year]?.groupSize || 4}
                        onChange={(e) => updateProjectWork(year, 'groupSize', 
                          parseInt(e.target.value) || 4)}
                        min="2"
                        max="8"
                      />
                      <button
                        className="number-btn"
                        onClick={() => updateProjectWork(year, 'groupSize', 
                          Math.min(8, (projectWork[year]?.groupSize || 4) + 1))}
                      >
                        +
                      </button>
                    </div>
                  </div>

                  {/* ✅ REMOVED: Projects don't need supervisors - students work independently */}
                </div>
              )}
            </div>
          ))}
        </div>

        {yearsManaged.filter(year => year === 'TE' || year === 'BE').length === 0 && (
          <div className="no-project-years">
            <div className="no-projects-icon"><TrackChanges sx={{ fontSize: 18 }} /></div>
            <h4>No Project Years Selected</h4>
            <p>TE and BE years typically have project work. Consider adding them in the Department Setup.</p>
          </div>
        )}
      </div>

      {/* Balance Settings */}
      <div className="balance-section">
        <div className="balance-header">
          <h3 className="section-title">
            <span className="title-icon">⚖️</span>
            Optimization & Balance Settings
          </h3>
          <button
            className="toggle-advanced-btn"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? '<ExpandLess /> Hide Advanced' : '<ExpandMore /> Show Advanced'}
          </button>
        </div>
        <p className="section-subtitle">
          Fine-tune how the algorithm balances different constraints
        </p>

        <div className="balance-grid">
          <div className="balance-card">
            <div className="balance-item">
              <label className="balance-label">
                <span className="label-icon"><People sx={{ fontSize: 18 }} /></span>
                Workload Balance
              </label>
              <div className="slider-container">
                <input
                  type="range"
                  className="balance-slider"
                  min="50"
                  max="100"
                  value={balanceSettings.workloadBalance}
                  onChange={(e) => updateBalanceSettings('workloadBalance', parseInt(e.target.value))}
                />
                <div className="slider-value">{balanceSettings.workloadBalance}%</div>
              </div>
              <p className="balance-description">
                How evenly teaching load is distributed among faculty
              </p>
            </div>

            <div className="balance-item">
              <label className="balance-label">
                <span className="label-icon">⏰</span>
                Time Distribution
              </label>
              <div className="slider-container">
                <input
                  type="range"
                  className="balance-slider"
                  min="50"
                  max="100"
                  value={balanceSettings.timeDistribution}
                  onChange={(e) => updateBalanceSettings('timeDistribution', parseInt(e.target.value))}
                />
                <div className="slider-value">{balanceSettings.timeDistribution}%</div>
              </div>
              <p className="balance-description">
                Balance between morning and afternoon sessions
              </p>
            </div>

            <div className="balance-item">
              <label className="balance-label">
                <span className="label-icon"><Business sx={{ fontSize: 18 }} /></span>
                Room Utilization
              </label>
              <div className="slider-container">
                <input
                  type="range"
                  className="balance-slider"
                  min="60"
                  max="95"
                  value={balanceSettings.roomUtilization}
                  onChange={(e) => updateBalanceSettings('roomUtilization', parseInt(e.target.value))}
                />
                <div className="slider-value">{balanceSettings.roomUtilization}%</div>
              </div>
              <p className="balance-description">
                Target room utilization efficiency
              </p>
            </div>

            {showAdvanced && (
              <>
                <div className="balance-item">
                  <label className="balance-label">
                    <span className="label-icon">⚠️</span>
                    Conflict Tolerance
                  </label>
                  <div className="slider-container">
                    <input
                      type="range"
                      className="balance-slider conflict"
                      min="0"
                      max="10"
                      value={balanceSettings.conflictTolerance}
                      onChange={(e) => updateBalanceSettings('conflictTolerance', parseInt(e.target.value))}
                    />
                    <div className="slider-value">{balanceSettings.conflictTolerance}%</div>
                  </div>
                  <p className="balance-description">
                    Acceptable level of minor scheduling conflicts (0% recommended)
                  </p>
                </div>

                <div className="balance-item">
                  <label className="balance-label">
                    <span className="label-icon"><TrackChanges sx={{ fontSize: 18 }} /></span>
                    Optimization Level
                  </label>
                  <div className="optimization-buttons">
                    {[
                      { key: 'fast', label: 'Fast', desc: 'Quick generation' },
                      { key: 'balanced', label: 'Balanced', desc: 'Good quality & speed' },
                      { key: 'thorough', label: 'Thorough', desc: 'Best quality' }
                    ].map(opt => (
                      <button
                        key={opt.key}
                        className={`opt-btn ${
                          balanceSettings.optimizationLevel === opt.key ? 'selected' : ''
                        }`}
                        onClick={() => updateBalanceSettings('optimizationLevel', opt.key)}
                      >
                        <span className="opt-label">{opt.label}</span>
                        <span className="opt-desc">{opt.desc}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Configuration Summary */}
      <div className="summary-section">
        <h3 className="section-title">
          <span className="title-icon"><Assignment sx={{ fontSize: 18 }} /></span>
          Configuration Summary
        </h3>
        
        <div className="summary-grid">
          <div className="summary-card">
            <div className="summary-icon"><AccountBalance sx={{ fontSize: 18 }} /></div>
            <div className="summary-content">
              <h4 className="summary-title">Academic Structure</h4>
              <div className="summary-stats">
                <div className="stat">
                  <span className="stat-value">{getTotalDivisions()}</span>
                  <span className="stat-label">Total Divisions</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{getTotalStudents()}</span>
                  <span className="stat-label">Total Students</span>
                </div>
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon"><TrackChanges sx={{ fontSize: 18 }} /></div>
            <div className="summary-content">
              <h4 className="summary-title">Project Work</h4>
              <div className="summary-stats">
                {/* ✅ REMOVED: Supervisors stat - not needed for projects */}
                <div className="stat">
                  <span className="stat-value">
                    {Object.values(projectWork).filter((p: any) => p.hasProjects).length}
                  </span>
                  <span className="stat-label">Years with Projects</span>
                </div>
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">⚖️</div>
            <div className="summary-content">
              <h4 className="summary-title">Optimization</h4>
              <div className="summary-stats">
                <div className="stat">
                  <span className="stat-value">{balanceSettings.workloadBalance}%</span>
                  <span className="stat-label">Workload Balance</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{balanceSettings.optimizationLevel}</span>
                  <span className="stat-label">Quality Level</span>
                </div>
              </div>
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
          <div className="config-summary">
            <span className="summary-text">
              {getTotalDivisions()} divisions • {getTotalStudents()} students • 
              {Object.values(projectWork).filter((p: any) => p.hasProjects).length} project years
            </span>
          </div>
        </div>
        <div className="nav-right">
          <button 
            className="btn btn-primary"
            onClick={validateAndNext}
          >
            Start Generation
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default FinalConfiguration;
