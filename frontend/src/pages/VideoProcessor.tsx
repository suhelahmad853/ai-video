import React, { useState, useEffect } from 'react';
import axios from 'axios';

// API configuration
const API_BASE_URL = 'http://localhost:8001';

const VideoProcessor: React.FC = () => {
  // Add CSS animation for spinner
  React.useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

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
  const [isRewriting, setIsRewriting] = useState(false);
  const [rewritingResult, setRewritingResult] = useState<any>(null);
  const [rewritingOptions, setRewritingOptions] = useState({
    modificationType: 'enhance',
    targetAudience: 'general',
    stylePreference: 'professional'
  });

  // Voice Generation State
  const [isGeneratingSpeech, setIsGeneratingSpeech] = useState<boolean>(false);
  const [speechProgress, setSpeechProgress] = useState<string>('');
  const [speechResult, setSpeechResult] = useState<any>(null);
  const [availableVoices, setAvailableVoices] = useState<any[]>([]);
  const [voiceOptions, setVoiceOptions] = useState({
    voiceId: 'default',
    customConfig: {
      speed: 1.0,
      pitch: 1.0,
      volume: 1.0,
      fastMode: false,
      enablePostProcessing: true
    }
  });

  // Audio Post-Processing Options
  const [postProcessingOptions, setPostProcessingOptions] = useState({
    enableAudioEnhancement: true,
    enableNoiseReduction: true,
    enableVolumeNormalization: true,
    enableBackgroundMusic: false,
    backgroundMusicStyle: 'ambient'
  });

  // Visual Generation State
  const [isGeneratingVisuals, setIsGeneratingVisuals] = useState<boolean>(false);
  const [visualProgress, setVisualProgress] = useState<string>('');
  const [visualResult, setVisualResult] = useState<any>(null);
  const [availableVisualTemplates, setAvailableVisualTemplates] = useState<any>(null);
  const [visualOptions, setVisualOptions] = useState({
    contentType: 'auto',
    stylePreferences: {
      colorScheme: 'professional',
      fontSize: 36
    }
  });

  // Video Composition State
  const [isComposingVideo, setIsComposingVideo] = useState<boolean>(false);
  const [compositionProgress, setCompositionProgress] = useState<string>('');
  const [compositionResult, setCompositionResult] = useState<any>(null);
  const [availableCompositionPresets, setAvailableCompositionPresets] = useState<any>(null);
  const [compositionOptions, setCompositionOptions] = useState({
    outputFormat: 'mp4',
    resolution: '1920x1080',
    frameRate: 30,
    enableTransitions: true,
    transitionDuration: 0.5,
    enableEnhancement: true
  });

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

  const rewriteContent = async () => {
    try {
      if (!transcription?.text) {
        setError('Please transcribe content first before rewriting');
        return;
      }
      
      setIsRewriting(true);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/rewrite-content`, {
        text: transcription.text,
        modification_type: rewritingOptions.modificationType,
        target_audience: rewritingOptions.targetAudience,
        style_preference: rewritingOptions.stylePreference
      });
      
      console.log('Content rewriting response:', response.data);
      
      if (response.data.result) {
        setRewritingResult(response.data.result);
      } else {
        setError('No rewriting result received');
      }
      
    } catch (error: any) {
      console.error('Content rewriting error:', error);
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsRewriting(false);
    }
  };

  const analyzeContentSimilarity = async () => {
    try {
      if (!transcription?.text || !rewritingResult?.rewritten_content?.text) {
        setError('Please have both original and rewritten content for similarity analysis');
        return;
      }
      
      setIsAnalyzing(true);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/analyze-content-similarity`, {
        original_text: transcription.text,
        comparison_text: rewritingResult.rewritten_content.text
      });
      
      console.log('Similarity analysis response:', response.data);
      
      if (response.data.result) {
        // Update analysis result with similarity data
        setAnalysisResult((prev: any) => ({
          ...prev,
          similarity_analysis: response.data.result
        }));
      }
      
    } catch (error: any) {
      console.error('Similarity analysis error:', error);
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const checkPlagiarism = async () => {
    try {
      if (!rewritingResult?.rewritten_content?.text) {
        setError('Please rewrite content first before checking plagiarism');
        return;
      }
      
      setIsAnalyzing(true);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/check-plagiarism`, {
        text: rewritingResult.rewritten_content.text
      });
      
      console.log('Plagiarism check response:', response.data);
      
      if (response.data.result) {
        // Update analysis result with plagiarism data
        setAnalysisResult((prev: any) => ({
          ...prev,
          plagiarism_check: response.data.result
        }));
      }
      
    } catch (error: any) {
      console.error('Plagiarism check error:', error);
      setError(error.response?.data?.detail || error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Voice Generation Functions
  const fetchAvailableVoices = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/available-voices`);
      console.log('Available voices response:', response.data);
      
      if (response.data.voices) {
        setAvailableVoices(Object.entries(response.data.voices).map(([id, voice]: [string, any]) => ({
          id,
          ...voice
        })));
      }
    } catch (error: any) {
      console.error('Error fetching voices:', error);
      setError('Failed to fetch available voices');
    }
  };

  const generateSpeech = async () => {
    try {
      if (!rewritingResult?.rewritten_content?.text) {
        setError('Please rewrite content first before generating speech');
        return;
      }
      
      setIsGeneratingSpeech(true);
      setError(null);
      setSpeechProgress('Initializing speech generation...');
      
      // Add timeout handling
      const timeoutId = setTimeout(() => {
        setError('Speech generation is taking longer than expected. Try enabling Fast Mode for quicker results.');
        setIsGeneratingSpeech(false);
        setSpeechProgress('');
      }, 30000); // 30 second timeout
      
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setSpeechProgress(prev => {
          if (voiceOptions.customConfig.fastMode) {
            // Fast mode progress
            if (prev.includes('Generating speech')) {
              return 'Fast mode: Processing...';
            } else {
              return 'Fast mode: Generating speech...';
            }
          } else {
            // Regular mode progress
            if (prev.includes('Generating speech')) {
              return 'Processing audio...';
            } else if (prev.includes('Processing audio')) {
              return 'Applying post-processing...';
            } else if (prev.includes('Applying post-processing')) {
              return 'Finalizing audio...';
            } else {
              return 'Generating speech...';
            }
          }
        });
      }, voiceOptions.customConfig.fastMode ? 1500 : 3000); // Faster updates for fast mode
      
      const response = await axios.post(`${API_BASE_URL}/generate-speech`, {
        text: rewritingResult.rewritten_content.text,
        voice_id: voiceOptions.voiceId,
        custom_config: {
          ...voiceOptions.customConfig,
          // In fast mode, disable all post-processing
          fast_mode: voiceOptions.customConfig.fastMode,
          enable_post_processing: voiceOptions.customConfig.enablePostProcessing && !voiceOptions.customConfig.fastMode,
          // Only pass post-processing options if not in fast mode
          ...(voiceOptions.customConfig.fastMode ? {} : {
            enable_enhancement: postProcessingOptions.enableAudioEnhancement,
            enable_noise_reduction: postProcessingOptions.enableNoiseReduction,
            enable_volume_normalization: postProcessingOptions.enableVolumeNormalization,
            enable_background_music: postProcessingOptions.enableBackgroundMusic
          })
        }
      }, {
        timeout: voiceOptions.customConfig.fastMode ? 30000 : 60000 // Shorter timeout for fast mode
      });
      
      clearTimeout(timeoutId);
      clearInterval(progressInterval);
      setSpeechProgress('Speech generation completed!');
      
      console.log('Speech generation response:', response.data);
      
      if (response.data.result) {
        setSpeechResult(response.data.result);
      } else {
        setError('No speech result received');
      }
      
    } catch (error: any) {
      console.error('Speech generation error:', error);
      if (error.code === 'ECONNABORTED') {
        setError('Speech generation timed out. Try enabling Fast Mode or reducing text length.');
      } else {
        setError(error.response?.data?.detail || error.message);
      }
    } finally {
      setIsGeneratingSpeech(false);
      setTimeout(() => setSpeechProgress(''), 2000); // Clear progress after 2 seconds
    }
  };

  const updateVoiceConfig = (key: string, value: number | boolean) => {
    setVoiceOptions(prev => ({
      ...prev,
      customConfig: {
        ...prev.customConfig,
        [key]: value
      }
    }));
  };

  const testVoicePreview = async () => {
    try {
      const testText = "This is a voice preview test. You can hear how the voice settings sound.";
      
      setIsGeneratingSpeech(true);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/generate-speech`, {
        text: testText,
        voice_id: voiceOptions.voiceId,
        custom_config: voiceOptions.customConfig
      });
      
      if (response.data.result) {
        // Store preview result separately
        setSpeechResult({
          ...response.data.result,
          isPreview: true,
          previewText: testText
        });
      }
      
    } catch (error: any) {
      console.error('Voice preview error:', error);
      setError('Failed to generate voice preview');
    } finally {
      setIsGeneratingSpeech(false);
    }
  };

  const handleGenerateVisuals = async () => {
    if (!rewritingResult?.rewritten_content?.text) {
      alert('Please rewrite content first before generating visuals.');
      return;
    }

    setIsGeneratingVisuals(true);
    setVisualProgress('Initializing visual generation...');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/generate-visual-content`, {
        text_content: rewritingResult.rewritten_content.text,
        content_type: visualOptions.contentType,
        style_preferences: visualOptions.stylePreferences
      });
      
      setVisualResult(response.data);
      setVisualProgress('Visual generation completed!');
      
    } catch (error: any) {
      setVisualProgress('Error: ' + (error.response?.data?.detail || error.message));
      console.error('Visual generation error:', error);
    } finally {
      setIsGeneratingVisuals(false);
    }
  };

  const loadAvailableVisualTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/available-visual-templates`);
      setAvailableVisualTemplates(response.data);
    } catch (error: any) {
      console.error('Error loading visual templates:', error);
    }
  };

  const handleComposeVideo = async () => {
    if (!visualResult?.result?.visuals || !speechResult?.speech_output?.audio_file_path) {
      alert('Please generate both visual content and speech before composing video.');
      return;
    }

    setIsComposingVideo(true);
    setCompositionProgress('Initializing video composition...');
    
    try {
      // Prepare composition configuration
      const [width, height] = compositionOptions.resolution.split('x').map(Number);
      const compositionConfig = {
        output_format: compositionOptions.outputFormat,
        resolution: [width, height],
        frame_rate: compositionOptions.frameRate,
        enable_transitions: compositionOptions.enableTransitions,
        transition_duration: compositionOptions.transitionDuration,
        enable_video_enhancement: compositionOptions.enableEnhancement
      };

      // Get audio file path
      const audioPath = speechResult.speech_output.audio_file_path;
      
      // Compose video
      const response = await axios.post(`${API_BASE_URL}/compose-video`, {
        visuals: visualResult.result.visuals,
        audio_path: audioPath,
        composition_config: compositionConfig
      });
      
      setCompositionResult(response.data);
      setCompositionProgress('Video composition completed!');
      
    } catch (error: any) {
      setCompositionProgress('Error: ' + (error.response?.data?.detail || error.message));
      console.error('Video composition error:', error);
    } finally {
      setIsComposingVideo(false);
    }
  };

  const loadAvailableCompositionPresets = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/composition-presets`);
      setAvailableCompositionPresets(response.data);
    } catch (error: any) {
      console.error('Error loading composition presets:', error);
    }
  };

  const previewVideoTimeline = async () => {
    if (!visualResult?.result?.visuals) {
      alert('Please generate visual content first before previewing timeline.');
      return;
    }

    try {
      const [width, height] = compositionOptions.resolution.split('x').map(Number);
      const compositionConfig = {
        output_format: compositionOptions.outputFormat,
        resolution: [width, height],
        frame_rate: compositionOptions.frameRate,
        enable_transitions: compositionOptions.enableTransitions,
        transition_duration: compositionOptions.transitionDuration
      };

      const response = await axios.post(`${API_BASE_URL}/preview-timeline`, {
        visuals: visualResult.result.visuals,
        composition_config: compositionConfig
      });
      
      // Show timeline preview
      console.log('Timeline preview:', response.data.preview);
      alert(`Timeline Preview:\nTotal Duration: ${response.data.preview.total_duration.toFixed(1)}s\nSegments: ${response.data.preview.total_segments}`);
      
    } catch (error: any) {
      console.error('Timeline preview error:', error);
      alert('Failed to generate timeline preview');
    }
  };

  // Fetch available voices on component mount
  useEffect(() => {
    fetchAvailableVoices();
    loadAvailableVisualTemplates();
    loadAvailableCompositionPresets();
  }, []);

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
              <strong>Phase 1 - Core Processing:</strong>
              <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                <li>1. Process Video: Validates YouTube URL and extracts basic info</li>
                <li>2. Extract Metadata: Gets detailed video information (views, likes, etc.)</li>
                <li>3. Check Restrictions: Verifies if video can be processed</li>
                <li>4. Quick Transcribe & Analyze: Extracts REAL YouTube transcript with timestamps and analyzes content</li>
              </ul>
            </div>
            <div>
              <strong>Phase 2 - AI Transformation:</strong>
              <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                <li>5. Transform Content: AI-powered content rewriting and enhancement</li>
                <li>6. Analyze Similarity: Compare original vs. transformed content</li>
                <li>7. Check Plagiarism: Ensure content uniqueness and compliance</li>
                <li>8. Voice Generation: Convert text to natural speech</li>
                <li>9. Visual Generation: Create slides, images, and graphics</li>
                <li>10. Video Composition: Combine audio and visuals into final video</li>
                <li>11. Next: Output formatting and optimization (coming soon)</li>
              </ul>
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

        {/* Content Analysis Results */}
        {analysisResult && (
          <div className="result-card">
            <h3>Content Analysis Results</h3>
            <div className="result-content">
              <p><strong>Status:</strong> Content analysis completed</p>
              {analysisResult.content_structure && (
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                  <h4>Content Structure</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                    <p><strong>Total Sentences:</strong> {analysisResult.content_structure.total_sentences || 'N/A'}</p>
                    <p><strong>Total Words:</strong> {analysisResult.content_structure.total_words || 'N/A'}</p>
                    <p><strong>Average Sentence Length:</strong> {analysisResult.content_structure.average_sentence_length || 'N/A'}</p>
                    <p><strong>Complexity Score:</strong> {analysisResult.content_structure.complexity_score || 'N/A'}</p>
                    <p><strong>Readability Level:</strong> {analysisResult.content_structure.readability_level || 'N/A'}</p>
                    <p><strong>Main Topics:</strong> {analysisResult.content_structure.content_topics?.join(', ') || 'N/A'}</p>
                  </div>
                </div>
              )}
              {analysisResult.similarity_analysis && (
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '4px' }}>
                  <h4>Similarity Analysis</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                    <p><strong>Similarity Score:</strong> {analysisResult.similarity_analysis.similarity_score}%</p>
                    <p><strong>Similarity Level:</strong> {analysisResult.similarity_analysis.similarity_level}</p>
                    <p><strong>Word Overlap:</strong> {analysisResult.similarity_analysis.word_overlap_percentage}%</p>
                    <p><strong>Risk Assessment:</strong> {analysisResult.similarity_analysis.risk_assessment}</p>
                  </div>
                  {analysisResult.similarity_analysis.recommendations && (
                    <div style={{ marginTop: '0.5rem' }}>
                      <strong>Recommendations:</strong>
                      <ul style={{ marginTop: '0.25rem', marginLeft: '1.5rem' }}>
                        {analysisResult.similarity_analysis.recommendations.map((rec: string, index: number) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              {analysisResult.plagiarism_check && (
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#fff3cd', borderRadius: '4px' }}>
                  <h4>Plagiarism Check</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                    <p><strong>Uniqueness Score:</strong> {analysisResult.plagiarism_check.uniqueness_score}%</p>
                    <p><strong>Risk Level:</strong> {analysisResult.plagiarism_check.risk_level}</p>
                    <p><strong>Compliance Status:</strong> {analysisResult.plagiarism_check.compliance_status}</p>
                  </div>
                  {analysisResult.plagiarism_check.recommendations && (
                    <div style={{ marginTop: '0.5rem' }}>
                      <strong>Recommendations:</strong>
                      <ul style={{ marginTop: '0.25rem', marginLeft: '1.5rem' }}>
                        {analysisResult.plagiarism_check.recommendations.map((rec: string, index: number) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Content Rewriting Section */}
        {transcription?.text && (
          <div className="result-card">
            <h3>🎨 AI Content Transformation</h3>
            <div className="result-content">
              <p><strong>Phase 2:</strong> Transform your transcribed content using AI-powered rewriting</p>
              
              {/* Rewriting Options */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                <h4>Rewriting Options</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label><strong>Modification Type:</strong></label>
                    <select 
                      value={rewritingOptions.modificationType}
                      onChange={(e) => setRewritingOptions(prev => ({ ...prev, modificationType: e.target.value }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value="enhance">Enhance & Improve</option>
                      <option value="simplify">Simplify & Clarify</option>
                      <option value="formalize">Make Formal</option>
                      <option value="casual">Make Casual</option>
                    </select>
                  </div>
                  <div>
                    <label><strong>Target Audience:</strong></label>
                    <select 
                      value={rewritingOptions.targetAudience}
                      onChange={(e) => setRewritingOptions(prev => ({ ...prev, targetAudience: e.target.value }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value="general">General</option>
                      <option value="technical">Technical</option>
                      <option value="academic">Academic</option>
                      <option value="casual">Casual</option>
                    </select>
                  </div>
                  <div>
                    <label><strong>Writing Style:</strong></label>
                    <select 
                      value={rewritingOptions.stylePreference}
                      onChange={(e) => setRewritingOptions(prev => ({ ...prev, stylePreference: e.target.value }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value="professional">Professional</option>
                      <option value="conversational">Conversational</option>
                      <option value="academic">Academic</option>
                    </select>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'end' }}>
                    <button 
                      onClick={rewriteContent}
                      disabled={isRewriting}
                      className="btn btn-primary"
                      style={{ width: '100%' }}
                    >
                      {isRewriting ? '🔄 Rewriting...' : '🚀 Transform Content'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Content Rewriting Results */}
        {rewritingResult && (
          <div className="result-card">
            <h3>✨ Transformed Content</h3>
            <div className="result-content">
              <p><strong>Status:</strong> Content successfully transformed</p>
              
              {/* Original vs Rewritten Comparison */}
              <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                  <h4>📝 Original Content</h4>
                  <p><strong>Words:</strong> {rewritingResult.original_content?.word_count || 'N/A'}</p>
                  <p><strong>Characters:</strong> {rewritingResult.original_content?.character_count || 'N/A'}</p>
                  <div style={{ maxHeight: '200px', overflowY: 'auto', marginTop: '0.5rem', padding: '0.5rem', backgroundColor: 'white', borderRadius: '4px' }}>
                    <p style={{ fontSize: '0.9rem', lineHeight: '1.4' }}>{rewritingResult.original_content?.text}</p>
                  </div>
                </div>
                
                <div style={{ padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '4px' }}>
                  <h4>🎯 Transformed Content</h4>
                  <p><strong>Words:</strong> {rewritingResult.rewritten_content?.word_count || 'N/A'}</p>
                  <p><strong>Characters:</strong> {rewritingResult.rewritten_content?.character_count || 'N/A'}</p>
                  <div style={{ maxHeight: '200px', overflowY: 'auto', marginTop: '0.5rem', padding: '0.5rem', backgroundColor: 'white', borderRadius: '4px' }}>
                    <p style={{ fontSize: '0.9rem', lineHeight: '1.4' }}>{rewritingResult.rewritten_content?.text}</p>
                  </div>
                </div>
              </div>
              
              {/* Improvement Metrics */}
              {rewritingResult.rewritten_content?.improvement_metrics && (
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#fff3cd', borderRadius: '4px' }}>
                  <h4>📊 Improvement Metrics</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                    <p><strong>Word Count Change:</strong> {rewritingResult.rewritten_content.improvement_metrics.word_count_change} ({rewritingResult.rewritten_content.improvement_metrics.word_count_change_percent}%)</p>
                    <p><strong>Complexity Improvement:</strong> {rewritingResult.rewritten_content.improvement_metrics.complexity_improvement}</p>
                    <p><strong>Readability:</strong> {rewritingResult.rewritten_content.improvement_metrics.readability_improvement}</p>
                  </div>
                </div>
              )}
              
              {/* Action Buttons */}
              <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
                <button 
                  onClick={analyzeContentSimilarity}
                  disabled={isAnalyzing}
                  className="btn btn-secondary"
                >
                  {isAnalyzing ? '🔍 Analyzing...' : '🔍 Analyze Similarity'}
                </button>
                <button 
                  onClick={checkPlagiarism}
                  disabled={isAnalyzing}
                  className="btn btn-secondary"
                >
                  {isAnalyzing ? '🔍 Checking...' : '🔍 Check Plagiarism'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Voice Generation Section */}
        {rewritingResult && (
          <div className="result-card">
            <h3>🎤 Voice Generation System</h3>
            <div className="result-content">
              <p><strong>Phase 2.2:</strong> Convert your transformed content to natural speech</p>
              
              {/* Voice Selection */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                <h4>Voice Options</h4>
                
                {/* Voice Type Selection */}
                <div style={{ marginBottom: '1rem' }}>
                  <label><strong>Voice Type:</strong></label>
                  <select 
                    value={voiceOptions.voiceId}
                    onChange={(e) => setVoiceOptions(prev => ({ ...prev, voiceId: e.target.value }))}
                    style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                  >
                    {availableVoices.map(voice => (
                      <option key={voice.id} value={voice.id}>
                        {voice.name} - {voice.description}
                      </option>
                    ))}
                  </select>
                </div>
                
                {/* Voice Characteristics Display */}
                {availableVoices.find(v => v.id === voiceOptions.voiceId) && (
                  <div style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: 'white', borderRadius: '4px' }}>
                    <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>Voice Characteristics:</h5>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', fontSize: '0.8rem' }}>
                      <span><strong>Gender:</strong> {availableVoices.find(v => v.id === voiceOptions.voiceId)?.gender}</span>
                      <span><strong>Emotion:</strong> {availableVoices.find(v => v.id === voiceOptions.voiceId)?.emotion}</span>
                      <span><strong>Age Group:</strong> {availableVoices.find(v => v.id === voiceOptions.voiceId)?.age_group}</span>
                      <span><strong>Accent:</strong> {availableVoices.find(v => v.id === voiceOptions.voiceId)?.accent}</span>
                    </div>
                  </div>
                )}
                
                {/* Voice Customization Controls */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label><strong>Speed:</strong></label>
                    <input
                      type="range"
                      min="0.5"
                      max="2.0"
                      step="0.1"
                      value={voiceOptions.customConfig.speed}
                      onChange={(e) => updateVoiceConfig('speed', parseFloat(e.target.value))}
                      style={{ width: '100%', marginTop: '0.25rem' }}
                    />
                    <span style={{ fontSize: '0.8rem', color: '#666' }}>
                      {voiceOptions.customConfig.speed}x
                    </span>
                  </div>
                  
                  <div>
                    <label><strong>Pitch:</strong></label>
                    <input
                      type="range"
                      min="0.5"
                      max="2.0"
                      step="0.1"
                      value={voiceOptions.customConfig.pitch}
                      onChange={(e) => updateVoiceConfig('pitch', parseFloat(e.target.value))}
                      style={{ width: '100%', marginTop: '0.25rem' }}
                    />
                    <span style={{ fontSize: '0.8rem', color: '#666' }}>
                      {voiceOptions.customConfig.pitch}x
                    </span>
                  </div>
                  
                  <div>
                    <label><strong>Volume:</strong></label>
                    <input
                      type="range"
                      min="0.1"
                      max="2.0"
                      step="0.1"
                      value={voiceOptions.customConfig.volume}
                      onChange={(e) => updateVoiceConfig('volume', parseFloat(e.target.value))}
                      style={{ width: '100%', marginTop: '0.25rem' }}
                    />
                    <span style={{ fontSize: '0.8rem', color: '#666' }}>
                      {voiceOptions.customConfig.volume}x
                    </span>
                  </div>
                </div>
                
                {/* Performance Options */}
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: voiceOptions.customConfig.fastMode ? '#e8f5e8' : '#fff3cd', borderRadius: '4px', border: voiceOptions.customConfig.fastMode ? '2px solid #28a745' : '1px solid #ffc107' }}>
                  <h5 style={{ color: voiceOptions.customConfig.fastMode ? '#155724' : '#856404' }}>
                    {voiceOptions.customConfig.fastMode ? '🚀 Fast Mode Enabled' : '⚡ Performance Options'}
                  </h5>
                  
                  {/* Fast Mode Status */}
                  {voiceOptions.customConfig.fastMode && (
                    <div style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#d4edda', borderRadius: '4px', border: '1px solid #c3e6cb' }}>
                      <p style={{ fontSize: '0.9rem', margin: '0', color: '#155724' }}>
                        ✅ <strong>Fast Mode Active:</strong> Audio post-processing disabled for maximum speed
                      </p>
                    </div>
                  )}
                  
                  {/* Text Length Warning */}
                  {rewritingResult?.rewritten_content?.text && (
                    <div style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#ffe6e6', borderRadius: '4px', border: '1px solid #ffcccc' }}>
                      <p style={{ fontSize: '0.8rem', margin: '0 0 0.5rem 0', color: '#d63384' }}>
                        <strong>⚠️ Text Length Warning:</strong> Your content is {rewritingResult.rewritten_content.text.length} characters long.
                      </p>
                      {rewritingResult.rewritten_content.text.length > 2000 ? (
                        <div>
                          <p style={{ fontSize: '0.8rem', margin: '0 0 0.5rem 0', color: '#dc3545', fontWeight: 'bold' }}>
                            🚨 ULTRA LONG TEXT DETECTED!
                          </p>
                          <p style={{ fontSize: '0.8rem', margin: '0 0 0.5rem 0', color: '#dc3545' }}>
                            <strong>Recommendation:</strong> Enable Fast Mode for immediate results (will use ultra fast mode).
                          </p>
                          <p style={{ fontSize: '0.8rem', margin: '0', color: '#dc3545' }}>
                            <strong>Note:</strong> Ultra fast mode creates a placeholder file for immediate response.
                          </p>
                        </div>
                      ) : rewritingResult.rewritten_content.text.length > 1000 ? (
                        <p style={{ fontSize: '0.8rem', margin: '0', color: '#d63384' }}>
                          <strong>Recommendation:</strong> Enable Fast Mode for quicker generation with long content.
                        </p>
                      ) : (
                        <p style={{ fontSize: '0.8rem', margin: '0', color: '#28a745' }}>
                          <strong>Good:</strong> Content length is manageable for full processing.
                        </p>
                      )}
                    </div>
                  )}
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input
                          type="checkbox"
                          checked={voiceOptions.customConfig.fastMode || false}
                          onChange={(e) => updateVoiceConfig('fastMode', e.target.checked)}
                        />
                        <strong>Fast Mode</strong>
                      </label>
                      <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                        Skip audio post-processing for faster generation
                      </p>
                    </div>
                    
                    <div>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input
                          type="checkbox"
                          checked={voiceOptions.customConfig.enablePostProcessing !== false}
                          onChange={(e) => updateVoiceConfig('enablePostProcessing', e.target.checked)}
                          disabled={voiceOptions.customConfig.fastMode}
                        />
                        <strong>Enable Post-Processing</strong>
                      </label>
                      <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                        Apply audio enhancement and effects
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Audio Post-Processing Options */}
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '4px' }}>
                  <h5 style={{ margin: '0 0 0.5rem 0' }}>🎵 Audio Post-Processing</h5>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input
                          type="checkbox"
                          checked={postProcessingOptions.enableAudioEnhancement}
                          onChange={(e) => setPostProcessingOptions(prev => ({ ...prev, enableAudioEnhancement: e.target.checked }))}
                        />
                        <strong>Audio Enhancement</strong>
                      </label>
                      <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                        Improve audio quality and clarity
                      </p>
                    </div>
                    
                    <div>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input
                          type="checkbox"
                          checked={postProcessingOptions.enableNoiseReduction}
                          onChange={(e) => setPostProcessingOptions(prev => ({ ...prev, enableNoiseReduction: e.target.checked }))}
                        />
                        <strong>Noise Reduction</strong>
                      </label>
                      <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                        Remove background noise and artifacts
                      </p>
                    </div>
                    
                    <div>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input
                          type="checkbox"
                          checked={postProcessingOptions.enableVolumeNormalization}
                          onChange={(e) => setPostProcessingOptions(prev => ({ ...prev, enableVolumeNormalization: e.target.checked }))}
                        />
                        <strong>Volume Normalization</strong>
                      </label>
                      <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                        Balance audio levels and prevent clipping
                      </p>
                    </div>
                    
                    <div>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input
                          type="checkbox"
                          checked={postProcessingOptions.enableBackgroundMusic}
                          onChange={(e) => setPostProcessingOptions(prev => ({ ...prev, enableBackgroundMusic: e.target.checked }))}
                        />
                        <strong>Background Music</strong>
                      </label>
                      <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                        Add ambient music for enhanced atmosphere
                      </p>
                    </div>
                  </div>
                  
                  {postProcessingOptions.enableBackgroundMusic && (
                    <div style={{ marginTop: '1rem' }}>
                      <label><strong>Music Style:</strong></label>
                      <select
                        value={postProcessingOptions.backgroundMusicStyle}
                        onChange={(e) => setPostProcessingOptions(prev => ({ ...prev, backgroundMusicStyle: e.target.value }))}
                        style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                      >
                        <option value="ambient">Ambient</option>
                        <option value="energetic">Energetic</option>
                        <option value="melodic">Melodic</option>
                        <option value="professional">Professional</option>
                      </select>
                    </div>
                  )}
                </div>
                
                <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                  <button 
                    onClick={testVoicePreview}
                    disabled={isGeneratingSpeech}
                    className="btn btn-secondary"
                    style={{ flex: 1, maxWidth: '200px' }}
                  >
                    {isGeneratingSpeech ? '🎵 Testing...' : '🎵 Test Voice'}
                  </button>
                  <button 
                    onClick={generateSpeech}
                    disabled={isGeneratingSpeech}
                    className="btn btn-primary"
                    style={{ flex: 1, maxWidth: '200px' }}
                  >
                    {isGeneratingSpeech ? '🎤 Generating...' : '🎤 Generate Speech'}
                  </button>
                </div>
                
                {/* Progress Indicator */}
                {isGeneratingSpeech && speechProgress && (
                  <div style={{ 
                    marginTop: '1rem', 
                    padding: '1rem', 
                    backgroundColor: voiceOptions.customConfig.fastMode && (rewritingResult?.rewritten_content?.text?.length || 0) > 2000 ? '#d4edda' : '#e3f2fd', 
                    borderRadius: '4px',
                    textAlign: 'center',
                    border: voiceOptions.customConfig.fastMode && (rewritingResult?.rewritten_content?.text?.length || 0) > 2000 ? '2px solid #28a745' : '1px solid #2196f3'
                  }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      gap: '0.5rem',
                      marginBottom: '0.5rem'
                    }}>
                      <div style={{
                        width: '20px',
                        height: '20px',
                        border: voiceOptions.customConfig.fastMode && (rewritingResult?.rewritten_content?.text?.length || 0) > 2000 ? '2px solid #28a745' : '2px solid #2196f3',
                        borderTop: voiceOptions.customConfig.fastMode && (rewritingResult?.rewritten_content?.text?.length || 0) > 2000 ? '2px solid #28a745' : '2px solid #2196f3',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}></div>
                      <span style={{ 
                        fontWeight: 'bold', 
                        color: voiceOptions.customConfig.fastMode && (rewritingResult?.rewritten_content?.text?.length || 0) > 2000 ? '#155724' : '#1976d2'
                      }}>
                        {voiceOptions.customConfig.fastMode && (rewritingResult?.rewritten_content?.text?.length || 0) > 2000 ? '🚀 ULTRA FAST MODE' : speechProgress}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: '#666', margin: 0 }}>
                      {voiceOptions.customConfig.fastMode && (rewritingResult?.rewritten_content?.text?.length || 0) > 2000 ? 
                        'Ultra Fast Mode: Generating real audio for long content (first 1,000 chars)' : 
                        voiceOptions.customConfig.fastMode ? 
                          'Fast Mode: Skipping audio post-processing for quicker results' : 
                          'Processing audio with full enhancement pipeline'
                      }
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Voice Generation Results */}
        {speechResult && (
          <div className="result-card">
            <h3>{speechResult.isPreview ? '🎵 Voice Preview' : '🎵 Generated Speech'}</h3>
            <div className="result-content">
              <p><strong>Status:</strong> {speechResult.isPreview ? 'Voice preview generated' : 'Speech successfully generated'}</p>
              
              {speechResult.isPreview && (
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#fff3cd', borderRadius: '4px' }}>
                  <h4>🎯 Preview Text:</h4>
                  <p style={{ fontStyle: 'italic' }}>"{speechResult.previewText}"</p>
                  <p style={{ fontSize: '0.8rem', color: '#666' }}>
                    This is a test preview. Use the "Generate Speech" button for your full content.
                  </p>
                </div>
              )}
              
              {/* Speech Details */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '4px' }}>
                <h4>Audio Information</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <p><strong>Duration:</strong> {speechResult.speech_output?.duration_seconds?.toFixed(2) || 'N/A'} seconds</p>
                  <p><strong>File Size:</strong> {speechResult.speech_output?.file_size_bytes || 'N/A'} bytes</p>
                  <p><strong>Format:</strong> {speechResult.speech_output?.audio_format || 'N/A'}</p>
                  <p><strong>Processing Time:</strong> {speechResult.speech_output?.processing_time?.toFixed(2) || 'N/A'} seconds</p>
                </div>
                
                {/* Voice Characteristics */}
                {speechResult.speech_output?.voice_characteristics && (
                  <div style={{ marginTop: '1rem', padding: '0.5rem', backgroundColor: 'white', borderRadius: '4px' }}>
                    <h5>Voice Settings Applied:</h5>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                      <p><strong>Speed:</strong> {speechResult.speech_output.voice_characteristics.speed}x</p>
                      <p><strong>Pitch:</strong> {speechResult.speech_output.voice_characteristics.pitch}x</p>
                      <p><strong>Volume:</strong> {speechResult.speech_output.voice_characteristics.volume}x</p>
                    </div>
                  </div>
                )}
                
                {/* Audio File Path */}
                <div style={{ marginTop: '1rem', padding: '0.5rem', backgroundColor: '#fff3cd', borderRadius: '4px' }}>
                  <p><strong>Audio File:</strong> {speechResult.speech_output?.audio_file_path || 'N/A'}</p>
                  <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                    File saved to backend output directory
                  </p>
                </div>
                
                {/* Audio Player */}
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
                  <h5>🎵 Listen to Generated Speech:</h5>
                  
                  {/* Check if this is a placeholder file from ultra fast mode */}
                  {speechResult?.speech_output?.post_processing?.ultra_fast ? (
                    <div style={{ 
                      marginBottom: '1rem', 
                      padding: '1rem', 
                      backgroundColor: '#d4edda', 
                      borderRadius: '4px',
                      border: '1px solid #c3e6cb',
                      textAlign: 'center'
                    }}>
                      <h6 style={{ margin: '0 0 0.5rem 0', color: '#155724' }}>🚀 Ultra Fast Mode - Real Audio Generated!</h6>
                      <p style={{ fontSize: '0.9rem', margin: '0 0 0.5rem 0', color: '#155724' }}>
                        <strong>Success!</strong> Your long content was processed using ultra fast mode.
                      </p>
                      <p style={{ fontSize: '0.8rem', margin: '0 0 0.5rem 0', color: '#155724' }}>
                        <strong>Audio:</strong> Real MP3 file generated for the first 1,000 characters
                      </p>
                      <p style={{ fontSize: '0.8rem', margin: '0', color: '#155724' }}>
                        <strong>File:</strong> {speechResult.speech_output?.audio_file_path?.split('/')?.pop() || 'N/A'}
                      </p>
                    </div>
                  ) : (
                    <>
                      {/* Audio Test Section */}
                      <div style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#fff3cd', borderRadius: '4px' }}>
                        <p style={{ fontSize: '0.8rem', margin: '0 0 0.5rem 0' }}>
                          <strong>Debug Info:</strong> Audio files are being served from backend. If you can't hear anything, check the browser console for errors.
                        </p>
                        <p style={{ fontSize: '0.8rem', margin: '0 0 0.5rem 0' }}>
                          <strong>File Path:</strong> {speechResult.speech_output?.audio_file_path || 'N/A'}
                        </p>
                        <p style={{ fontSize: '0.8rem', margin: '0' }}>
                          <strong>Direct URL:</strong> {`${API_BASE_URL}/play-audio/${speechResult.speech_output?.audio_file_path?.split('/')?.pop() || ''}`}
                        </p>
                        
                        {/* Test Audio Button */}
                        <button 
                          onClick={() => {
                            const testAudio = new Audio(`${API_BASE_URL}/play-audio/${speechResult.speech_output?.audio_file_path?.split('/')?.pop() || ''}`);
                            testAudio.play().catch(e => {
                              console.error('Test audio failed:', e);
                              alert('Audio test failed. Check console for details.');
                            });
                          }}
                          style={{ 
                            padding: '0.25rem 0.5rem', 
                            fontSize: '0.8rem', 
                            backgroundColor: '#007bff', 
                            color: 'white', 
                            border: 'none', 
                            borderRadius: '4px',
                            cursor: 'pointer'
                          }}
                        >
                          🔊 Test Audio Playback
                        </button>
                      </div>
                    </>
                  )}
                  
                  {/* Main Audio Player */}
                  <div style={{ marginBottom: '1rem' }}>
                    <h6 style={{ margin: '0 0 0.5rem 0' }}>🎵 Audio Player:</h6>
                    <audio 
                      controls 
                      style={{ width: '100%', marginTop: '0.5rem' }}
                      src={`${API_BASE_URL}/play-audio/${speechResult.speech_output?.audio_file_path?.split('/')?.pop() || ''}`}
                      onError={(e) => {
                        console.error('Audio playback error:', e);
                        console.error('Audio element error details:', e.target);
                      }}
                      onLoadStart={() => console.log('Audio loading started')}
                      onCanPlay={() => console.log('Audio can play')}
                      onPlay={() => console.log('Audio playing')}
                      onPause={() => console.log('Audio paused')}
                      onLoadedData={() => console.log('Audio data loaded')}
                      onProgress={() => console.log('Audio loading progress')}
                    >
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                  
                  {/* Download Buttons */}
                  <div style={{ marginTop: '1rem', textAlign: 'center', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    {/* Download Final Audio */}
                    <a 
                      href={`${API_BASE_URL}/play-audio/${speechResult.speech_output?.audio_file_path?.split('/')?.pop() || ''}`}
                      download={speechResult.speech_output?.audio_file_path?.split('/')?.pop() || 'generated_speech.mp3'}
                      className="btn btn-secondary"
                      style={{ display: 'inline-block', textDecoration: 'none' }}
                    >
                      {speechResult?.speech_output?.post_processing?.ultra_fast ? 
                        '💾 Download Ultra Fast Audio' : 
                        '💾 Download Generated Audio'
                      }
                    </a>
                  </div>
                  
                  <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                    {speechResult?.speech_output?.post_processing?.ultra_fast ? (
                      <>
                        <strong>Note:</strong> This audio was generated using ultra fast mode for your long content. For full content, consider breaking it into smaller sections.
                      </>
                    ) : (
                      <>
                        <strong>Note:</strong> Your audio has been generated successfully! You can play it above or download it below.
                      </>
                    )}
                  </p>
                </div>
              </div>
              
              {/* Next Steps */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#d1ecf1', borderRadius: '4px' }}>
                <h4>🚀 Next Steps</h4>
                <p>Your speech has been generated! The next phase will be:</p>
                <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                  <li>Audio post-processing and enhancement</li>
                  <li>Video generation with visual content</li>
                  <li>Final video composition and output</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Visual Generation Section */}
        {rewritingResult && (
          <div className="result-card">
            <h3>🎨 Visual Content Generation System</h3>
            <div className="result-content">
              <p><strong>Phase 2.3:</strong> Create visual content from your transformed text</p>
              
              {/* Visual Options */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                <h4>Visual Options</h4>
                
                {/* Content Type Selection */}
                <div style={{ marginBottom: '1rem' }}>
                  <label><strong>Content Type:</strong></label>
                  <select 
                    value={visualOptions.contentType}
                    onChange={(e) => setVisualOptions(prev => ({ ...prev, contentType: e.target.value }))}
                    style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                  >
                    <option value="auto">Auto-detect (Recommended)</option>
                    <option value="slide">Slides Only</option>
                    <option value="image">Images Only</option>
                    <option value="graphic">Graphics Only</option>
                  </select>
                  <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.25rem' }}>
                    Auto-detect will choose the best visual type based on your content
                  </p>
                </div>
                
                {/* Style Preferences */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label><strong>Color Scheme:</strong></label>
                    <select
                      value={visualOptions.stylePreferences.colorScheme}
                      onChange={(e) => setVisualOptions(prev => ({ 
                        ...prev, 
                        stylePreferences: { 
                          ...prev.stylePreferences, 
                          colorScheme: e.target.value 
                        } 
                      }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value="professional">Professional</option>
                      <option value="modern">Modern</option>
                      <option value="minimal">Minimal</option>
                    </select>
                  </div>
                  
                  <div>
                    <label><strong>Font Size:</strong></label>
                    <select
                      value={visualOptions.stylePreferences.fontSize}
                      onChange={(e) => setVisualOptions(prev => ({ 
                        ...prev, 
                        stylePreferences: { 
                          ...prev.stylePreferences, 
                          fontSize: parseInt(e.target.value) 
                        } 
                      }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value={18}>Small (18px)</option>
                      <option value={24}>Medium (24px)</option>
                      <option value={28}>Large (28px)</option>
                      <option value={36}>Extra Large (36px)</option>
                      <option value={48}>Title (48px)</option>
                    </select>
                  </div>
                </div>
                
                {/* Available Templates Info */}
                {availableVisualTemplates && (
                  <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '4px' }}>
                    <h5 style={{ margin: '0 0 0.5rem 0', color: '#155724' }}>Available Templates:</h5>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8rem' }}>
                      <div>
                        <strong>Slide Templates:</strong> {Object.keys(availableVisualTemplates.templates || {}).length}
                      </div>
                      <div>
                        <strong>Color Schemes:</strong> {Object.keys(availableVisualTemplates.color_schemes || {}).length}
                      </div>
                      <div>
                        <strong>Font Configs:</strong> {Object.keys(availableVisualTemplates.font_configs || {}).length}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Generate Button */}
                <div style={{ marginTop: '1rem', textAlign: 'center' }}>
                  <button 
                    onClick={handleGenerateVisuals}
                    disabled={isGeneratingVisuals}
                    className="btn btn-primary"
                    style={{ padding: '0.75rem 2rem', fontSize: '1.1rem' }}
                  >
                    {isGeneratingVisuals ? '🎨 Generating...' : '🎨 Generate Visual Content'}
                  </button>
                </div>
                
                {/* Progress Indicator */}
                {isGeneratingVisuals && visualProgress && (
                  <div style={{ 
                    marginTop: '1rem', 
                    padding: '1rem', 
                    backgroundColor: '#e3f2fd', 
                    borderRadius: '4px',
                    textAlign: 'center',
                    border: '1px solid #2196f3'
                  }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      gap: '0.5rem',
                      marginBottom: '0.5rem'
                    }}>
                      <div style={{
                        width: '20px',
                        height: '20px',
                        border: '2px solid #2196f3',
                        borderTop: '2px solid #2196f3',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}></div>
                      <span style={{ fontWeight: 'bold', color: '#1976d2' }}>
                        {visualProgress}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Visual Generation Results */}
        {visualResult && (
          <div className="result-card">
            <h3>🎨 Generated Visual Content</h3>
            <div className="result-content">
              <p><strong>Status:</strong> Visual content successfully generated!</p>
              
              {/* Visual Statistics */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '4px' }}>
                <h4>Generation Summary</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <p><strong>Total Visuals:</strong> {visualResult.result?.total_visuals || 'N/A'}</p>
                  <p><strong>Estimated Duration:</strong> {visualResult.result?.estimated_duration_minutes?.toFixed(1) || 'N/A'} minutes</p>
                  <p><strong>Content Type:</strong> {visualResult.result?.content_type || 'Mixed (Auto-detected)'}</p>
                  <p><strong>Optimization Applied:</strong> {visualResult.result?.optimization_applied ? 'Yes' : 'No'}</p>
                </div>
              </div>
              
              {/* Generated Visuals List */}
              {visualResult.result?.visuals && (
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                  <h4>Generated Visuals</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {visualResult.result.visuals.map((visual: any, index: number) => (
                      <div key={index} style={{ 
                        padding: '0.5rem', 
                        backgroundColor: 'white', 
                        borderRadius: '4px',
                        border: '1px solid #dee2e6'
                      }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', fontSize: '0.9rem' }}>
                          <span><strong>Type:</strong> {visual.content_type}</span>
                          <span><strong>Duration:</strong> {visual.duration_seconds}s</span>
                          <span><strong>Transition:</strong> {visual.transition_type}</span>
                        </div>
                        <p style={{ fontSize: '0.8rem', color: '#666', margin: '0.25rem 0 0 0' }}>
                          <strong>Preview:</strong> {visual.text_content.length > 100 ? 
                            visual.text_content.substring(0, 100).replace(/00:\d{2}:\d{2}\.\.\s*/g, '') + '...' : 
                            visual.text_content.replace(/00:\d{2}:\d{2}\.\.\s*/g, '')
                          }
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Next Steps */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#d1ecf1', borderRadius: '4px' }}>
                <h4>🚀 Next Steps</h4>
                <p>Your visual content has been generated! The next phase will be:</p>
                <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                  <li>Video composition and timeline creation</li>
                  <li>Audio-visual synchronization</li>
                  <li>Final video export and optimization</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Video Composition Section */}
        {visualResult && speechResult && (
          <div className="result-card">
            <h3>🎬 Video Composition System</h3>
            <div className="result-content">
              <p><strong>Phase 2.3.2:</strong> Combine audio and visuals into final video</p>
              
              {/* Composition Options */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                <h4>Composition Options</h4>
                
                {/* Output Format and Quality */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <label><strong>Output Format:</strong></label>
                    <select
                      value={compositionOptions.outputFormat}
                      onChange={(e) => setCompositionOptions(prev => ({ ...prev, outputFormat: e.target.value }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value="mp4">MP4 (Recommended)</option>
                      <option value="avi">AVI</option>
                      <option value="mov">MOV</option>
                      <option value="gif">GIF</option>
                    </select>
                  </div>
                  
                  <div>
                    <label><strong>Resolution:</strong></label>
                    <select
                      value={compositionOptions.resolution}
                      onChange={(e) => setCompositionOptions(prev => ({ ...prev, resolution: e.target.value }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value="1920x1080">HD (1920x1080)</option>
                      <option value="1280x720">HD Ready (1280x720)</option>
                      <option value="1080x1080">Square (1080x1080)</option>
                      <option value="3840x2160">4K (3840x2160)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label><strong>Frame Rate:</strong></label>
                    <select
                      value={compositionOptions.frameRate}
                      onChange={(e) => setCompositionOptions(prev => ({ ...prev, frameRate: parseInt(e.target.value) }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value={24}>24 fps (Film)</option>
                      <option value={25}>25 fps (PAL)</option>
                      <option value={30}>30 fps (NTSC)</option>
                      <option value={60}>60 fps (Smooth)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label><strong>Transition Duration:</strong></label>
                    <select
                      value={compositionOptions.transitionDuration}
                      onChange={(e) => setCompositionOptions(prev => ({ ...prev, transitionDuration: parseFloat(e.target.value) }))}
                      style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                    >
                      <option value={0.3}>Fast (0.3s)</option>
                      <option value={0.5}>Normal (0.5s)</option>
                      <option value={0.8}>Slow (0.8s)</option>
                      <option value={1.0}>Very Slow (1.0s)</option>
                    </select>
                  </div>
                </div>
                
                {/* Enhancement Options */}
                <div style={{ marginBottom: '1rem' }}>
                  <h5>Enhancement Options</h5>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={compositionOptions.enableTransitions}
                        onChange={(e) => setCompositionOptions(prev => ({ ...prev, enableTransitions: e.target.checked }))}
                      />
                      <strong>Enable Transitions</strong>
                    </label>
                    
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={compositionOptions.enableEnhancement}
                        onChange={(e) => setCompositionOptions(prev => ({ ...prev, enableEnhancement: e.target.checked }))}
                      />
                      <strong>Video Enhancement</strong>
                    </label>
                  </div>
                </div>
                
                {/* Available Presets Info */}
                {availableCompositionPresets && (
                  <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '4px' }}>
                    <h5 style={{ margin: '0 0 0.5rem 0', color: '#155724' }}>Available Presets:</h5>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8rem' }}>
                      <div>
                        <strong>YouTube:</strong> {availableCompositionPresets.presets?.youtube?.resolution?.join('x') || 'N/A'}
                      </div>
                      <div>
                        <strong>Social Media:</strong> {availableCompositionPresets.presets?.social_media?.resolution?.join('x') || 'N/A'}
                      </div>
                      <div>
                        <strong>Presentation:</strong> {availableCompositionPresets.presets?.presentation?.resolution?.join('x') || 'N/A'}
                      </div>
                      <div>
                        <strong>GIF:</strong> {availableCompositionPresets.presets?.gif?.resolution?.join('x') || 'N/A'}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Action Buttons */}
                <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                  <button 
                    onClick={previewVideoTimeline}
                    disabled={isComposingVideo}
                    className="btn btn-secondary"
                    style={{ padding: '0.75rem 1.5rem' }}
                  >
                    👁️ Preview Timeline
                  </button>
                  
                  <button 
                    onClick={handleComposeVideo}
                    disabled={isComposingVideo}
                    className="btn btn-primary"
                    style={{ padding: '0.75rem 2rem', fontSize: '1.1rem' }}
                  >
                    {isComposingVideo ? '🎬 Composing...' : '🎬 Compose Video'}
                  </button>
                </div>
                
                {/* Progress Indicator */}
                {isComposingVideo && compositionProgress && (
                  <div style={{ 
                    marginTop: '1rem', 
                    padding: '1rem', 
                    backgroundColor: '#e3f2fd', 
                    borderRadius: '4px',
                    textAlign: 'center',
                    border: '1px solid #2196f3'
                  }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      gap: '0.5rem',
                      marginBottom: '0.5rem'
                    }}>
                      <div style={{
                        width: '20px',
                        height: '20px',
                        border: '2px solid #2196f3',
                        borderTop: '2px solid #2196f3',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}></div>
                      <span style={{ fontWeight: 'bold', color: '#1976d2' }}>
                        {compositionProgress}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Video Composition Results */}
        {compositionResult && (
          <div className="result-card">
            <h3>🎬 Composed Video</h3>
            <div className="result-content">
              <p><strong>Status:</strong> Video successfully composed!</p>
              
              {/* Composition Summary */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '4px' }}>
                <h4>Composition Summary</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <p><strong>Total Duration:</strong> {compositionResult.result?.metadata?.total_duration?.toFixed(1) || 'N/A'} seconds</p>
                  <p><strong>Total Segments:</strong> {compositionResult.result?.metadata?.total_segments || 'N/A'}</p>
                  <p><strong>Output Format:</strong> {compositionResult.result?.metadata?.output_format || 'N/A'}</p>
                  <p><strong>Resolution:</strong> {compositionResult.result?.metadata?.resolution?.join('x') || 'N/A'}</p>
                  <p><strong>Frame Rate:</strong> {compositionResult.result?.metadata?.frame_rate || 'N/A'} fps</p>
                  <p><strong>Video File:</strong> {compositionResult.result?.video_path?.split('/')?.pop() || 'N/A'}</p>
                </div>
              </div>
              
              {/* Download Video */}
              <div style={{ marginTop: '1rem', textAlign: 'center' }}>
                <a 
                  href={`${API_BASE_URL}/download-video/${compositionResult.result?.video_path?.split('/')?.pop() || ''}`}
                  download={compositionResult.result?.video_path?.split('/')?.pop() || 'composed_video.mp4'}
                  className="btn btn-success"
                  style={{ padding: '1rem 2rem', fontSize: '1.2rem', textDecoration: 'none', display: 'inline-block' }}
                >
                  💾 Download Composed Video
                </a>
              </div>
              
              {/* Next Steps */}
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#d1ecf1', borderRadius: '4px' }}>
                <h4>🚀 Next Steps</h4>
                <p>Your video has been composed successfully! The next phase will be:</p>
                <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                  <li>Video quality optimization and enhancement</li>
                  <li>Multiple format export options</li>
                  <li>Batch processing capabilities</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoProcessor; 