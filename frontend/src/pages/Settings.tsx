import React, { useState } from 'react';

const Settings: React.FC = () => {
  const [settings, setSettings] = useState({
    outputQuality: '720p',
    voiceType: 'natural',
    processingSpeed: 'normal',
    autoCompliance: true
  });

  const handleSettingChange = (key: string, value: string | boolean) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">Settings</h1>
          <p className="page-subtitle">
            Configure your video processing preferences and options
          </p>
        </div>

        <div className="video-input-section">
          <div className="card">
            <h2>Video Output Settings</h2>
            
            <div className="form-group">
              <label className="form-label">Output Quality</label>
              <select
                className="form-input"
                value={settings.outputQuality}
                onChange={(e) => handleSettingChange('outputQuality', e.target.value)}
              >
                <option value="480p">480p</option>
                <option value="720p">720p (Recommended)</option>
                <option value="1080p">1080p</option>
                <option value="4K">4K</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Voice Type</label>
              <select
                className="form-input"
                value={settings.voiceType}
                onChange={(e) => handleSettingChange('voiceType', e.target.value)}
              >
                <option value="natural">Natural</option>
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="energetic">Energetic</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Processing Speed</label>
              <select
                className="form-input"
                value={settings.processingSpeed}
                onChange={(e) => handleSettingChange('processingSpeed', e.target.value)}
              >
                <option value="fast">Fast (Lower Quality)</option>
                <option value="normal">Normal (Balanced)</option>
                <option value="high">High Quality (Slower)</option>
              </select>
            </div>

            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={settings.autoCompliance}
                  onChange={(e) => handleSettingChange('autoCompliance', e.target.checked)}
                />
                <span>Auto-compliance checking</span>
              </label>
              <small style={{ color: 'var(--text-secondary)', marginTop: '0.25rem', display: 'block' }}>
                Automatically check for copyright compliance and YouTube AI policy violations
              </small>
            </div>
          </div>

          <div className="card" style={{ marginTop: '2rem' }}>
            <h2>System Information</h2>
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Status:</strong> Ready</p>
            <p><strong>Storage:</strong> 2.5GB available</p>
            <p><strong>Memory:</strong> 8GB allocated</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 