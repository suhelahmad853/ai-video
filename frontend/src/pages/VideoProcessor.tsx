import React, { useState } from 'react';
import axios from 'axios';

// API configuration
const API_BASE_URL = 'http://localhost:8001';

const VideoProcessor: React.FC = () => {
  // State variables
  const [url, setUrl] = useState<string>('');
  const [quality, setQuality] = useState<string>('720p');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [restrictions, setRestrictions] = useState<any>(null);
  const [canProcess, setCanProcess] = useState<boolean>(true);
  const [transcription, setTranscription] = useState<any>(null);
  const [transcriptionStatus, setTranscriptionStatus] = useState<string>('');
  const [isTranscribing, setIsTranscribing] = useState<boolean>(false);
  const [contentAnalysis, setContentAnalysis] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/process-video`, {
        url: url,
        quality: quality
      });
      
      setResult(response.data);
      
      // Check restrictions after processing
      await checkVideoRestrictions();
      
    } catch (error: any) {
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExtractMetadata = async () => {
    if (!url.trim()) return;

    setIsProcessing(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/extract-metadata`, {
        url: url,
        quality: quality
      });

      setResult((prev: any) => ({ ...prev, metadata: response.data }));

    } catch (error: any) {
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const checkVideoRestrictions = async () => {
    if (!url.trim()) return;
    setIsProcessing(true);
    setError(null);
    try {
      const resp = await axios.post(`${API_BASE_URL}/check-restrictions`, {
        url: url,
      });
      if (resp.data.status === 'restrictions_checked') {
        setRestrictions(resp.data.restrictions);
        setCanProcess(resp.data.can_process);
        if (resp.data.can_process) {
          setTranscriptionStatus('Video can be processed! No restrictions detected.');
        } else {
          setTranscriptionStatus(`Video has restrictions: ${resp.data.restrictions.reason}`);
        }
      } else {
        throw new Error(resp.data.message || 'Restriction check failed');
      }
    } catch (error: any) {
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const transcribeAudio = async () => {
    if (!url.trim()) return;
    setIsTranscribing(true);
    setTranscriptionStatus('Starting transcription...');
    
    try {
      // First, we need to simulate having an audio file
      // In a real implementation, this would come from the video processing pipeline
      const mockAudioPath = `temp/${url.split('v=')[1]}_audio.mp3`;
      
      const resp = await axios.post(`${API_BASE_URL}/transcribe-speech`, {
        audio_path: mockAudioPath,
        language: 'en',
        model_size: 'base'
      });
      
      if (resp.data.status === 'transcription_completed') {
        setTranscription(resp.data.transcription);
        setTranscriptionStatus('Transcription completed successfully!');
        setTranscriptionStatus('Speech-to-text transcription completed. Ready for content structure analysis.');
      } else {
        throw new Error(resp.data.message || 'Transcription failed');
      }
    } catch (error: any) {
      setTranscriptionStatus(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsTranscribing(false);
    }
  };

  const performFullPipeline = async () => {
    try {
      if (!url) {
        setError('Please enter a YouTube URL first');
        return;
      }
      
      setIsProcessing(true);
      setError(null);
      
      // Step 1: Check video restrictions
      await checkVideoRestrictions();
      
      if (!canProcess) {
        setIsProcessing(false);
        return;
      }
      
      // Step 2: Process video
      const response = await axios.post(`${API_BASE_URL}/process-video`, {
        url: url,
        quality: quality
      });
      
      setResult(response.data);
      
      // Step 3: Extract metadata
      await handleExtractMetadata();
      
      // Step 4: Use the working transcription approach
      await transcribeAndAnalyze();
      
      setIsProcessing(false);
    } catch (error: any) {
      setError(error.response?.data?.detail || error.message);
      setIsProcessing(false);
    }
  };

  const analyzeContentStructure = async (transcriptionData: any) => {
    try {
      setIsAnalyzing(true);
      setError(null);
      
      console.log('Analyzing transcription data:', transcriptionData); // Debug log
      
      const response = await axios.post(`${API_BASE_URL}/analyze-content-structure`, {
        text: transcriptionData.text || transcriptionData,
        language: transcriptionData.language || "en",
        model_size: transcriptionData.model_size || "base"
      });
      
      console.log('Content analysis response:', response.data); // Debug log
      
      setContentAnalysis(response.data);
      
      // Fix: Handle the response structure correctly
      if (response.data.analysis && response.data.analysis.content_structure) {
        setAnalysisResult(response.data.analysis.content_structure);
      } else if (response.data.content_structure) {
        setAnalysisResult(response.data.content_structure);
      } else {
        console.error('Unexpected response structure:', response.data);
        setError('Unexpected response structure from content analysis');
      }
      
    } catch (error: any) {
      console.error('Content analysis error:', error); // Debug log
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const transcribeAndAnalyze = async () => {
    try {
      if (!url) {
        setError('Please enter a YouTube URL first');
        return;
      }
      
      setIsTranscribing(true);
      setIsAnalyzing(true);
      setError(null);
      
      // Extract REAL YouTube transcript with timestamps
      const transcriptResponse = await axios.post(`${API_BASE_URL}/extract-youtube-transcript`, {
        url: url,
        language: "en"
      });
      
      console.log('Real YouTube transcript response:', transcriptResponse.data);
      
      if (transcriptResponse.data.transcript && transcriptResponse.data.transcript.transcription) {
        setTranscription(transcriptResponse.data.transcript.transcription);
        
        // Now analyze the content structure with the real transcript
        if (transcriptResponse.data.transcript.transcription.text) {
          await analyzeContentStructure(transcriptResponse.data.transcript.transcription);
        }
      } else {
        setError('No real transcript data received from YouTube');
      }
      
    } catch (error: any) {
      console.error('Real transcript extraction error:', error);
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsTranscribing(false);
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">Process Video</h1>
          <p className="page-subtitle">
            Enter a YouTube video URL to analyze content and prepare for AI transformation
          </p>
        </div>

        <div className="video-input-section">
          <form onSubmit={handleSubmit} className="video-input-form">
            <div className="form-group">
              <label htmlFor="videoUrl" className="form-label">
                YouTube Video URL
              </label>
              <input
                type="url"
                id="videoUrl"
                className="form-input"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="quality" className="form-label">
                Quality Preference
              </label>
              <select
                id="quality"
                className="form-select"
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
              >
                <option value="720p">720p (HD)</option>
                <option value="1080p">1080p (Full HD)</option>
                <option value="480p">480p (SD)</option>
                <option value="360p">360p (Low)</option>
              </select>
            </div>

            <div className="button-group">
              <button type="submit" className="btn btn-primary" disabled={isProcessing}>
                {isProcessing ? 'Processing...' : 'Process Video'}
              </button>
              
              <button 
                type="button" 
                className="btn btn-success" 
                onClick={handleExtractMetadata}
                disabled={isProcessing}
              >
                {isProcessing ? 'Please wait...' : 'Extract Metadata'}
              </button>
              
              <button 
                type="button" 
                className="btn btn-info" 
                onClick={checkVideoRestrictions}
                disabled={isProcessing}
              >
                Check Restrictions
              </button>
            </div>
          </form>
        </div>

        {/* Button Workflow Explanation */}
        <div className="workflow-guide" style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h3>🎯 Workflow Guide</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
            <div>
              <strong>1. Process Video:</strong> Validates YouTube URL and extracts basic info
            </div>
            <div>
              <strong>2. Extract Metadata:</strong> Gets detailed video information (views, likes, etc.)
            </div>
            <div>
              <strong>3. Check Restrictions:</strong> Verifies if video can be processed
            </div>
            <div>
              <strong>4. Quick Transcribe & Analyze:</strong> Extracts REAL YouTube transcript with timestamps and analyzes content
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="action-buttons" style={{ marginTop: '2rem' }}>
          <div className="button-group" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="btn btn-primary"
              disabled={isTranscribing || isAnalyzing || !url.trim()}
              onClick={transcribeAndAnalyze}
            >
              {(isTranscribing || isAnalyzing) ? 'Processing...' : 'Quick Transcribe & Analyze'}
            </button>
            
            <button
              type="button"
              className="btn btn-secondary"
              disabled={isAnalyzing || !transcription}
              onClick={() => transcription && analyzeContentStructure(transcription)}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Content Structure'}
            </button>
            
            <button
              type="button"
              className="btn btn-success"
              disabled={isTranscribing || isAnalyzing || !url.trim()}
              onClick={performFullPipeline}
            >
              {isProcessing ? 'Processing...' : 'Run Full Pipeline'}
            </button>
          </div>
        </div>

          {/* Progress Section */}
          {isProcessing && (
            <div className="progress-section">
              <div className="progress-header">
                <h3>Processing Video</h3>
                <div className="progress-steps">
                  <div className={`step ${result ? 'completed' : 'active'}`}>
                    <span className="step-number">1</span>
                    <span className="step-label">Video Processing</span>
                  </div>
                  <div className={`step ${transcription ? 'completed' : result ? 'active' : ''}`}>
                    <span className="step-number">2</span>
                    <span className="step-label">Audio Extraction</span>
                  </div>
                  <div className={`step ${contentAnalysis ? 'completed' : transcription ? 'active' : ''}`}>
                    <span className="step-number">3</span>
                    <span className="step-label">Content Analysis</span>
                  </div>
                </div>
              </div>
              
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ 
                    width: `${result && transcription && contentAnalysis ? 100 : 
                           result && transcription ? 66 : 
                           result ? 33 : 0}%` 
                  }}
                ></div>
              </div>
              
              <div className="progress-status">
                {!result && <p>🔄 Validating YouTube URL and processing video...</p>}
                {result && !transcription && <p>🔄 Extracting audio and transcribing speech...</p>}
                {transcription && !contentAnalysis && <p>🔄 Analyzing content structure...</p>}
                {contentAnalysis && <p>✅ All processing completed successfully!</p>}
              </div>
            </div>
          )}

        {/* Results Display */}
        {result && (
          <div className="results-section">
            <h2>Processing Results</h2>
            
            <div className="result-cards">
              {result.status && (
                <div className="result-card">
                  <h3>Status</h3>
                  <div className="result-content">
                    <p><strong>Status:</strong> {result.status}</p>
                    {result.message && (
                      <p><strong>Message:</strong> {result.message}</p>
                    )}
                  </div>
                </div>
              )}

              {result.metadata && (
                <div className="result-card">
                  <h3>Video Metadata</h3>
                  <div className="result-content">
                    <p><strong>Status:</strong> {result.metadata.status}</p>
                    {result.metadata.message && (
                      <p><strong>Message:</strong> {result.metadata.message}</p>
                    )}
                    
                    {/* Display actual video metadata if available */}
                    {result.metadata.metadata && (
                      <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                        <h4>Video Details</h4>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                          <p><strong>Title:</strong> {result.metadata.metadata.title || 'N/A'}</p>
                          <p><strong>Uploader:</strong> {result.metadata.metadata.uploader || 'N/A'}</p>
                          <p><strong>Duration:</strong> {result.metadata.metadata.duration_seconds ? `${Math.floor(result.metadata.metadata.duration_seconds / 60)}:${String(result.metadata.metadata.duration_seconds % 60).padStart(2, '0')}` : 'N/A'}</p>
                          <p><strong>Views:</strong> {result.metadata.metadata.view_count ? result.metadata.metadata.view_count.toLocaleString() : 'N/A'}</p>
                          <p><strong>Likes:</strong> {result.metadata.metadata.like_count ? result.metadata.metadata.like_count.toLocaleString() : 'N/A'}</p>
                          <p><strong>Video ID:</strong> {result.metadata.metadata.video_id || 'N/A'}</p>
                        </div>
                        
                        {result.metadata.metadata.description && (
                          <div style={{ marginTop: '1rem' }}>
                            <strong>Description:</strong>
                            <div style={{ 
                              marginTop: '0.5rem', 
                              padding: '0.5rem', 
                              backgroundColor: '#e9ecef', 
                              borderRadius: '4px',
                              fontSize: '0.9rem',
                              maxHeight: '200px',
                              overflowY: 'auto'
                            }}>
                              {result.metadata.metadata.description}
                            </div>
                          </div>
                        )}
                        
                        {result.metadata.metadata.thumbnail && (
                          <div style={{ marginTop: '1rem' }}>
                            <strong>Thumbnail:</strong>
                            <div style={{ marginTop: '0.5rem' }}>
                              <img 
                                src={result.metadata.metadata.thumbnail} 
                                alt="Video thumbnail" 
                                style={{ maxWidth: '200px', borderRadius: '4px' }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Transcription Display */}
        {transcription && (
          <div className="card" style={{ marginTop: '1rem' }}>
            <h3>Speech-to-Text Transcription</h3>
            <div style={{ 
              padding: '1rem', 
              marginBottom: '1rem', 
              borderRadius: '4px',
              backgroundColor: '#d1ecf1',
              border: '1px solid #bee5eb',
              color: '#0c5460'
            }}>
              <strong>Status:</strong> ✅ Transcription Completed
              <br />
              <strong>Model Used:</strong> {transcription.model_used}
              <br />
              <strong>Language:</strong> {transcription.language}
              <br />
              <strong>Word Count:</strong> {transcription.word_count}
              <br />
              <strong>Confidence Score:</strong> {(transcription.confidence_score * 100).toFixed(1)}%
              <br />
              <strong>Processing Time:</strong> {transcription.processing_time_seconds}s
            </div>
            
            <div style={{ marginTop: '1rem' }}>
              <strong>Transcribed Text:</strong>
              <div style={{ 
                marginTop: '0.5rem', 
                padding: '1rem', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '4px',
                fontSize: '0.9rem',
                lineHeight: '1.5',
                maxHeight: '300px',
                overflowY: 'auto'
              }}>
                {transcription.text}
              </div>
            </div>
            
            {transcription.segments && transcription.segments.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <strong>Segments:</strong>
                <div style={{ marginTop: '0.5rem' }}>
                  {transcription.segments.map((segment: any, index: number) => (
                    <div key={index} style={{ 
                      marginBottom: '0.5rem', 
                      padding: '0.5rem', 
                      backgroundColor: '#e9ecef', 
                      borderRadius: '4px',
                      fontSize: '0.85rem'
                    }}>
                      <strong>Segment {index + 1}:</strong> {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                      <br />
                      <strong>Confidence:</strong> {(segment.confidence * 100).toFixed(1)}%
                      <br />
                      <strong>Text:</strong> {segment.text.substring(0, 100)}{segment.text.length > 100 ? '...' : ''}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div style={{ marginTop: '1rem', padding: '0.5rem', backgroundColor: '#d4edda', borderRadius: '4px' }}>
              <strong>Next Step:</strong> {transcription.next_step || 'Content structure analysis'}
            </div>
          </div>
        )}

        {/* Content Analysis Section */}
        {contentAnalysis && (
          <div className="content-analysis-section">
            <h2>Content Structure Analysis</h2>
            
            {/* Debug Information */}
            <div className="debug-info" style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#fff3cd', borderRadius: '0.25rem', fontSize: '0.8rem' }}>
              <strong>Debug:</strong> 
              contentAnalysis: {contentAnalysis ? '✅' : '❌'}, 
              analysisResult: {analysisResult ? '✅' : '❌'}, 
              overview: {analysisResult?.overview ? '✅' : '❌'}
            </div>
            
            <div className="analysis-overview">
              <h3>Content Overview</h3>
              {analysisResult?.overview ? (
                <div className="overview-grid">
                  <div className="overview-item">
                    <strong>Total Words:</strong> {analysisResult.overview.total_words}
                  </div>
                  <div className="overview-item">
                    <strong>Total Sentences:</strong> {analysisResult.overview.total_sentences}
                  </div>
                  <div className="overview-item">
                    <strong>Estimated Duration:</strong> {analysisResult.overview.estimated_duration_minutes} minutes
                  </div>
                  <div className="overview-item">
                    <strong>Content Type:</strong> {analysisResult.overview.content_type}
                  </div>
                  <div className="overview-item">
                    <strong>Complexity Level:</strong> {analysisResult.overview.complexity_level}
                  </div>
                </div>
              ) : (
                <div style={{ padding: '1rem', backgroundColor: '#f8d7da', borderRadius: '0.25rem', color: '#721c24' }}>
                  <strong>No overview data available.</strong> 
                  <br />
                  analysisResult: {JSON.stringify(analysisResult, null, 2)}
                </div>
              )}
            </div>

            {analysisResult?.topics && analysisResult.topics.length > 0 && (
              <div className="analysis-topics">
                <h3>Main Topics</h3>
                <div className="topics-list">
                  {analysisResult.topics.map((topic: any, index: number) => (
                    <div key={index} className="topic-item">
                      <span className="topic-name">{topic.topic}</span>
                      <span className="topic-relevance">Relevance: {topic.relevance_score}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysisResult?.key_points && analysisResult.key_points.length > 0 && (
              <div className="analysis-key-points">
                <h3>Key Points</h3>
                <div className="key-points-list">
                  {analysisResult.key_points.slice(0, 5).map((point: any, index: number) => (
                    <div key={index} className="key-point-item">
                      <div className="point-content">{point.point}</div>
                      <div className="point-meta">
                        <span className="point-type">{point.type}</span>
                        <span className="point-importance">Importance: {point.importance_score}/10</span>
                        <span className="point-category">{point.category}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysisResult?.insights && (
              <div className="analysis-insights">
                <h3>Content Insights</h3>
                <div className="insights-grid">
                  <div className="insight-item">
                    <strong>Content Flow:</strong> {analysisResult.insights.content_flow}
                  </div>
                  <div className="insight-item">
                    <strong>Engagement Factors:</strong> {analysisResult.insights.engagement_factors?.join(', ')}
                  </div>
                  {analysisResult.insights.difficulty_distribution && (
                    <div className="insight-item">
                      <strong>Difficulty:</strong> {analysisResult.insights.difficulty_distribution.easy_percentage}% Easy, 
                      {analysisResult.insights.difficulty_distribution.medium_percentage}% Medium, 
                      {analysisResult.insights.difficulty_distribution.hard_percentage}% Hard
                    </div>
                  )}
                </div>
              </div>
            )}

            {contentAnalysis.saved_path && (
              <div className="analysis-export">
                <p><strong>Analysis saved to:</strong> {contentAnalysis.saved_path}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoProcessor; 