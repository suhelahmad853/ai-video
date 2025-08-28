import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import VideoProcessor from './pages/VideoProcessor';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Simple Header */}
        <header className="header">
          <div className="header-content">
            <h1 className="logo">🎬 AI Video Creator Tool</h1>
            <nav className="nav-menu">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/video-processor" className="nav-link">Video Processor</Link>
              <Link to="/content-analysis" className="nav-link">Content Analysis</Link>
              <Link to="/ai-transformation" className="nav-link">AI Transformation</Link>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/video-processor" element={<VideoProcessor />} />
            <Route path="/content-analysis" element={<ContentAnalysisPage />} />
            <Route path="/ai-transformation" element={<AITransformationPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

// Home Page Component
function HomePage() {
  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">AI Video Creator Tool</h1>
          <p className="page-subtitle">
            Transform YouTube videos into new, monetizable content using AI-powered tools
          </p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card">
            <h3>🎬 Video Processing</h3>
            <p>Download and process YouTube videos with advanced quality options</p>
            <Link to="/video-processor" className="btn btn-primary">Get Started</Link>
          </div>
          
          <div className="feature-card">
            <h3>📝 Content Analysis</h3>
            <p>Extract transcripts and analyze content structure automatically</p>
            <Link to="/content-analysis" className="btn btn-secondary">Learn More</Link>
          </div>
          
          <div className="feature-card">
            <h3>🤖 AI Transformation</h3>
            <p>Transform content using AI-powered rewriting and voice generation</p>
            <Link to="/ai-transformation" className="btn btn-info">Explore</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// Content Analysis Page Component
function ContentAnalysisPage() {
  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">Content Analysis</h1>
          <p className="page-subtitle">
            Analyze video content structure and extract key insights
          </p>
        </div>
        
        <div className="info-card">
          <h3>Content Analysis Features</h3>
          <ul>
            <li>Speech-to-text transcription using real YouTube captions</li>
            <li>Content structure analysis and topic extraction</li>
            <li>Key points identification with importance scoring</li>
            <li>Content insights and engagement factors</li>
            <li>Export analysis results to JSON format</li>
          </ul>
          <Link to="/video-processor" className="btn btn-primary">Start Analysis</Link>
        </div>
      </div>
    </div>
  );
}

// AI Transformation Page Component
function AITransformationPage() {
  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">AI Content Transformation</h1>
          <p className="page-subtitle">
            Transform analyzed content using AI-powered tools
          </p>
        </div>
        
        <div className="info-card">
          <h3>Coming Soon</h3>
          <p>AI content transformation features are currently in development.</p>
          <p>This will include:</p>
          <ul>
            <li>Content rewriting and optimization</li>
            <li>Voice generation and text-to-speech</li>
            <li>Content originality validation</li>
            <li>Enhanced narrative flow</li>
          </ul>
          <Link to="/video-processor" className="btn btn-secondary">Back to Video Processor</Link>
        </div>
      </div>
    </div>
  );
}

export default App; 