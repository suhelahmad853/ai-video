import React, { useState } from 'react';
import axios from 'axios';

// API configuration
const API_BASE_URL = 'http://localhost:8001';

const VideoProcessor: React.FC = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [quality, setQuality] = useState('720p');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [videoInfo, setVideoInfo] = useState<any>(null);
  const [metadata, setMetadata] = useState<any>(null);
  const [metadataSavedPath, setMetadataSavedPath] = useState<string | null>(null);
  const [restrictions, setRestrictions] = useState<any>(null);
  const [canProcess, setCanProcess] = useState<boolean | null>(null);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!videoUrl.trim()) return;

    setIsProcessing(true);
    setProgress(0);
    setStatus('Validating YouTube URL...');


    try {
      // Step 1: Validate and get video info
      const response = await axios.post(`${API_BASE_URL}/process-video`, {
        url: videoUrl,
        quality: quality
      });

      if (response.data.status === 'validated') {
        setVideoInfo(response.data.video_info);
        setProgress(25);
        setStatus('URL validated! Starting content analysis...');

        // Step 2: Analyze content for AI transformation
        const analysisResponse = await axios.post(`${API_BASE_URL}/analyze-content`, {
          url: videoUrl,
          quality: quality
        });

        if (analysisResponse.data.status === 'analyzed') {
          setProgress(100);
          setStatus('Content analysis completed! Ready for audio processing.');

        } else {
          throw new Error(analysisResponse.data.message || 'Analysis failed');
        }
      } else {
        throw new Error(response.data.message || 'Validation failed');
      }
    } catch (error: any) {
      setStatus(`Error: ${error.response?.data?.detail || error.message}`);
      
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExtractMetadata = async () => {
    if (!videoUrl.trim()) return;
    setIsProcessing(true);
    setStatus('Extracting video metadata...');
    try {
      const resp = await axios.post(`${API_BASE_URL}/extract-metadata`, {
        url: videoUrl,
        save: true,
      });
      if (resp.data.status === 'metadata_extracted') {
        setMetadata(resp.data.metadata);
        setMetadataSavedPath(resp.data.saved ? resp.data.saved_path : null);
        setStatus('Metadata extracted successfully.');
      } else {
        throw new Error(resp.data.message || 'Metadata extraction failed');
      }
    } catch (error: any) {
      setStatus(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const checkVideoRestrictions = async () => {
    if (!videoUrl.trim()) return;
    setIsProcessing(true);
    setStatus('Checking video restrictions...');
    try {
      const resp = await axios.post(`${API_BASE_URL}/check-restrictions`, {
        url: videoUrl,
      });
      if (resp.data.status === 'restrictions_checked') {
        setRestrictions(resp.data.restrictions);
        setCanProcess(resp.data.can_process);
        if (resp.data.can_process) {
          setStatus('Video can be processed! No restrictions detected.');
        } else {
          setStatus(`Video has restrictions: ${resp.data.restrictions.reason}`);
        }
      } else {
        throw new Error(resp.data.message || 'Restriction check failed');
      }
    } catch (error: any) {
      setStatus(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsProcessing(false);
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
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
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
              disabled={isProcessing || !videoUrl.trim()}
            >
              {isProcessing ? (
                <>
                  <span className="loading"></span>
                  Processing...
                </>
              ) : (
                'Analyze Content'
              )}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ marginLeft: '0.5rem' }}
              disabled={isProcessing || !videoUrl.trim()}
              onClick={handleExtractMetadata}
            >
              {isProcessing ? 'Please wait...' : 'Extract Metadata'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ marginLeft: '0.5rem' }}
              disabled={isProcessing || !videoUrl.trim()}
              onClick={checkVideoRestrictions}
            >
              {isProcessing ? 'Please wait...' : 'Check Restrictions'}
            </button>
          </form>

          {isProcessing && (
            <div className="progress-section">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="progress-text">{status}</p>
            </div>
          )}

          {status && !isProcessing && (
            <div className={`status-message ${progress === 100 ? 'success' : 'info'}`}>
              {status}
              {progress === 100 && videoInfo && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
                  <span style={{ color: '#28a745' }}>✅ Content analysis complete</span>
                  <br />
                  <span style={{ color: '#17a2b8' }}>🔄 Ready for audio processing phase</span>
                </div>
              )}
            </div>
          )}

          {videoInfo && (
            <div className="card" style={{ marginTop: '2rem' }}>
              <h3>Video Information</h3>
              
              {/* Data Quality Indicator */}
              <div style={{ 
                padding: '0.5rem', 
                marginBottom: '1rem', 
                borderRadius: '4px',
                backgroundColor: videoInfo.real_data ? '#d4edda' : '#fff3cd',
                border: `1px solid ${videoInfo.real_data ? '#c3e6cb' : '#ffeaa7'}`,
                color: videoInfo.real_data ? '#155724' : '#856404'
              }}>
                <strong>📊 Data Quality:</strong> {
                  videoInfo.real_data 
                    ? 'Real data extracted from YouTube' 
                    : 'Limited data (extraction issues)'
                }
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                <div>
                  <strong>Title:</strong> {videoInfo.title}
                </div>
                <div>
                  <strong>Duration:</strong> {
                    videoInfo.duration > 0 
                      ? `${Math.round(videoInfo.duration / 60)} minutes` 
                      : 'Unknown'
                  }
                </div>
                <div>
                  <strong>Uploader:</strong> {videoInfo.uploader}
                </div>
                <div>
                  <strong>Views:</strong> {
                    videoInfo.view_count > 0 
                      ? videoInfo.view_count.toLocaleString() 
                      : 'Unknown'
                  }
                </div>
                <div>
                  <strong>Likes:</strong> {
                    videoInfo.like_count > 0 
                      ? videoInfo.like_count.toLocaleString() 
                      : 'Unknown'
                  }
                </div>
                <div>
                  <strong>Quality:</strong> {quality}
                </div>
                <div>
                  <strong>Status:</strong> {videoInfo.status}
                </div>
              </div>
              
              {videoInfo.description && (
                <div style={{ marginTop: '1rem' }}>
                  <strong>Description:</strong>
                  <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    {videoInfo.description}
                  </p>
                </div>
              )}
              
              {videoInfo.note && (
                <div style={{ marginTop: '1rem', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                  <strong>Note:</strong> {videoInfo.note}
                </div>
              )}
            </div>
          )}

          {metadata && (
            <div className="card" style={{ marginTop: '1rem' }}>
              <h3>Extracted Metadata</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                <div>
                  <strong>Video ID:</strong> {metadata.video_id}
                </div>
                <div>
                  <strong>Title:</strong> {metadata.title}
                </div>
                <div>
                  <strong>Uploader:</strong> {metadata.uploader}
                </div>
                <div>
                  <strong>Duration (s):</strong> {metadata.duration_seconds}
                </div>
                <div>
                  <strong>Views:</strong> {metadata.view_count}
                </div>
                <div>
                  <strong>Likes:</strong> {metadata.like_count}
                </div>
                <div>
                  <strong>Subtitles:</strong> {metadata.has_subtitles ? 'Yes' : 'No'}
                </div>
                <div>
                  <strong>Auto Captions:</strong> {metadata.has_automatic_captions ? 'Yes' : 'No'}
                </div>
                <div>
                  <strong>Saved:</strong> {metadataSavedPath ? 'Yes' : 'No'}
                </div>
                {metadataSavedPath && (
                  <div style={{ gridColumn: '1 / -1' }}>
                    <strong>Saved Path:</strong> {metadataSavedPath}
                  </div>
                )}
              </div>
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
        </div>
      </div>
    </div>
  );
};

export default VideoProcessor; 