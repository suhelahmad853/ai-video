import React, { useState } from 'react';
import axios from 'axios';

// API configuration
const API_BASE_URL = 'http://localhost:8001';

const VideoProcessor: React.FC = () => {
  // State variables
  const [url, setUrl] = useState("");
  const [quality, setQuality] = useState("720p");
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [restrictions, setRestrictions] = useState<any>(null);
  const [canProcess, setCanProcess] = useState<boolean | null>(null);
  const [transcription, setTranscription] = useState<any>(null);
  const [transcriptionStatus, setTranscriptionStatus] = useState<string>("");
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [contentAnalysis, setContentAnalysis] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsProcessing(true);
    setError(null);

    try {
      // Step 1: Validate and get video info
      const response = await axios.post(`${API_BASE_URL}/process-video`, {
        url: url,
        quality: quality
      });

      setResult(response.data);

      // Step 2: Analyze content for AI transformation
      const analysisResponse = await axios.post(`${API_BASE_URL}/analyze-content`, {
        url: url,
        quality: quality
      });

      setResult((prev: any) => ({ ...prev, analysis: analysisResponse.data }));

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
      
      // Step 3: Extract and transcribe audio
      const transcribeResponse = await axios.post(`${API_BASE_URL}/extract-and-transcribe`, {
        video_path: response.data.video_path,
        quality: quality,
        language: "en",
        model_size: "base"
      });
      
      setTranscription(transcribeResponse.data);
      
      // Step 4: Analyze content structure
      if (transcribeResponse.data.transcription?.text) {
        await analyzeContentStructure(transcribeResponse.data.transcription);
      }
      
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
      setIsTranscribing(true);
      setIsAnalyzing(true);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/transcribe-and-analyze`, {
        audio_path: "temp/ADXNcv6KbMQ_audio.mp3",
        language: "en",
        model_size: "base"
      });
      
      setTranscription(response.data.transcription);
      setContentAnalysis(response.data.content_analysis);
      // Fix: Set the analysis result correctly
      setAnalysisResult(response.data.content_analysis.content_structure);
      
    } catch (error: any) {
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
                placeholder="https://www.youtube.com/watch?v=..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isProcessing}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="quality" className="form-label">
                Analysis Quality
              </label>
              <select
                id="quality"
                className="form-input"
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                disabled={isProcessing}
              >
                <option value="480p">480p (Faster)</option>
                <option value="720p">720p (Recommended)</option>
                <option value="1080p">1080p (Higher Quality)</option>
              </select>
            </div>

            <button
              type="submit"
              className="btn"
              disabled={isProcessing || !url.trim()}
            >
              {isProcessing ? (
                <>
                  <span className="loading"></span>
                  Processing...
                </>
              ) : (
                'Process Video'
              )}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ marginLeft: '0.5rem' }}
              disabled={isProcessing || !url.trim()}
              onClick={handleExtractMetadata}
            >
              {isProcessing ? 'Please wait...' : 'Extract Metadata'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ marginLeft: '0.5rem' }}
              disabled={isProcessing || !url.trim()}
              onClick={checkVideoRestrictions}
            >
              {isProcessing ? 'Please wait...' : 'Check Restrictions'}
            </button>
            <button
              type="button"
              className="btn btn-primary"
              style={{ marginLeft: '0.5rem' }}
              disabled={isProcessing || !url.trim()}
              onClick={performFullPipeline}
            >
              {isProcessing ? 'Processing...' : 'Run Full Pipeline'}
            </button>
            <button
              type="button"
              className="btn btn-info"
              style={{ marginLeft: '0.5rem' }}
              disabled={isTranscribing || !transcription}
              onClick={() => transcription && analyzeContentStructure(transcription)}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Content Structure'}
            </button>
            <button
              type="button"
              className="btn btn-success"
              style={{ marginLeft: '0.5rem' }}
              disabled={isTranscribing || isAnalyzing || !url.trim()}
              onClick={transcribeAndAnalyze}
            >
              {(isTranscribing || isAnalyzing) ? 'Processing...' : 'Quick Transcribe & Analyze'}
            </button>
            <button
              type="button"
              className="btn btn-warning"
              style={{ marginLeft: '0.5rem' }}
              disabled={isAnalyzing}
              onClick={() => {
                const testData = {
                  text: "This is a test text for content analysis. It contains multiple sentences to analyze the structure and extract insights. This will help us debug the content overview display issue."
                };
                analyzeContentStructure(testData);
              }}
            >
              {isAnalyzing ? 'Testing...' : 'Test Content Analysis'}
            </button>
          </form>

          {/* Button Workflow Explanation */}
          <div className="workflow-explanation" style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '0.5rem', border: '1px solid #dee2e6' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>📋 Workflow Guide:</h4>
            <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
              <p><strong>1. Process Video:</strong> Basic video processing and validation</p>
              <p><strong>2. Extract Metadata:</strong> Get video information and details</p>
              <p><strong>3. Check Restrictions:</strong> Verify video can be processed</p>
              <p><strong>4. Run Full Pipeline:</strong> Complete workflow: video → audio → transcription → analysis</p>
              <p><strong>5. Analyze Content Structure:</strong> Analyze existing transcription (requires transcription first)</p>
              <p><strong>6. Quick Transcribe & Analyze:</strong> Fast transcription + analysis using test audio file</p>
              <p><strong>7. Test Content Analysis:</strong> Test content analysis with sample data (for debugging)</p>
            </div>
          </div>

          {/* Progress Section */}
          {isProcessing && (
            <div className="status-message info">
              <p>Processing video... Please wait.</p>
            </div>
          )}

          {/* Results Section */}
          {result && (
            <div className="results-section">
              <h2>Processing Results</h2>
              
              <div className="result-card">
                <h3>Video Information</h3>
                <div className="result-content">
                  <p><strong>Status:</strong> {result.status}</p>
                  {result.video_path && (
                    <p><strong>Video Path:</strong> {result.video_path}</p>
                  )}
                  {result.message && (
                    <p><strong>Message:</strong> {result.message}</p>
                  )}
                </div>
              </div>

              {result.analysis && (
                <div className="result-card">
                  <h3>Content Analysis</h3>
                  <div className="result-content">
                    <p><strong>Status:</strong> {result.analysis.status}</p>
                    {result.analysis.message && (
                      <p><strong>Message:</strong> {result.analysis.message}</p>
                    )}
                  </div>
                </div>
              )}

              {result.metadata && (
                <div className="result-card">
                  <h3>Metadata</h3>
                  <div className="result-content">
                    <p><strong>Status:</strong> {result.metadata.status}</p>
                    {result.metadata.message && (
                      <p><strong>Message:</strong> {result.metadata.message}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {restrictions && (
            <div className="card" style={{ marginTop: '1rem' }}>
              <h3>Video Restrictions</h3>
              <div style={{ 
                padding: '1rem', 
                marginBottom: '1rem', 
                borderRadius: '4px',
                backgroundColor: canProcess ? '#d4edda' : '#f8d7da',
                border: `1px solid ${canProcess ? '#c3e6cb' : '#f5c6cb'}`,
                color: canProcess ? '#155724' : '#721c24'
              }}>
                <strong>Status:</strong> {canProcess ? '✅ Can Process' : '❌ Cannot Process'}
                <br />
                <strong>Reason:</strong> {restrictions.reason}
                {restrictions.recommendation && (
                  <>
                    <br />
                    <strong>Recommendation:</strong> {restrictions.recommendation}
                  </>
                )}
                {restrictions.age_limit && (
                  <>
                    <br />
                    <strong>Age Limit:</strong> {restrictions.age_limit}+
                  </>
                )}
              </div>
              
              {restrictions.video_id && (
                <div style={{ marginTop: '1rem' }}>
                  <strong>Video ID:</strong> {restrictions.video_id}
                </div>
              )}
              
              {restrictions.title && (
                <div style={{ marginTop: '0.5rem' }}>
                  <strong>Title:</strong> {restrictions.title}
                </div>
              )}
            </div>
          )}

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

          {transcriptionStatus && !transcription && (
            <div className="card" style={{ marginTop: '1rem' }}>
              <h3>Transcription Status</h3>
              <div style={{ 
                padding: '1rem', 
                borderRadius: '4px',
                backgroundColor: isTranscribing ? '#fff3cd' : '#f8d7da',
                border: `1px solid ${isTranscribing ? '#ffeaa7' : '#f5c6cb'}`,
                color: isTranscribing ? '#856404' : '#721c24'
              }}>
                <strong>Status:</strong> {isTranscribing ? '🔄 Transcribing...' : '❌ Transcription Failed'}
                <br />
                <strong>Message:</strong> {transcriptionStatus}
              </div>
            </div>
          )}
        </div>
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