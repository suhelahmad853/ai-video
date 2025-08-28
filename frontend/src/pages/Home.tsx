import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">AI Video Creator Tool</h1>
          <p className="page-subtitle">
            Transform YouTube videos into new, monetizable content using AI-powered tools. 
            Create original videos that comply with copyright laws and YouTube's AI policies.
          </p>
        </div>

        <div className="video-input-section">
          <div className="card">
            <h2>Get Started</h2>
            <p style={{ marginBottom: '2rem' }}>
              Ready to create your first AI-generated video? Start by providing a YouTube URL 
              and let our AI transform it into something completely new.
            </p>
            <Link to="/process" className="btn">
              Start Processing Video
            </Link>
          </div>
        </div>

        <div style={{ marginTop: '3rem' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>How It Works</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
            <div className="card">
              <h3>1. Input Video</h3>
              <p>Provide a YouTube video URL from any channel. Our tool will download and analyze the content.</p>
            </div>
            <div className="card">
              <h3>2. AI Transformation</h3>
              <p>Our AI creates different versions with new voices, modified content, and attractive presentations.</p>
            </div>
            <div className="card">
              <h3>3. Compliance Check</h3>
              <p>We ensure 70%+ content difference and full compliance with YouTube's AI policies.</p>
            </div>
            <div className="card">
              <h3>4. Ready to Monetize</h3>
              <p>Download your new video that's eligible for YouTube monetization and ready to publish.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 