from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import uvicorn
from datetime import datetime
import os

# Import our modules
from video_processor import video_processor
from audio_processor import audio_processor
from content_rewriter import content_rewriter
from voice_generator import voice_generator

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Video Creator Tool API",
    description="Backend API for transforming YouTube videos into new, original content",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost:3001",   # Alternative port
        "http://127.0.0.1:3001",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add logging middleware to debug CORS issues
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.info(f"Origin header: {request.headers.get('origin', 'No origin')}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Video Creator Tool API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "GET /health",
            "video_processing": {
                "process_video": "POST /process-video",
                "check_restrictions": "POST /check-restrictions",
                "get_video_info": "POST /get-video-info"
            },
            "audio_processing": {
                "extract_audio": "POST /extract-audio",
                "analyze_audio": "POST /analyze-audio",
                "prepare_for_ai": "POST /prepare-for-ai"
            },
            "transcription": {
                "transcribe_speech": "POST /transcribe-speech",
                "transcription_status": "GET /transcription-status/{audio_filename}",
                "extract_and_transcribe": "POST /extract-and-transcribe",
                "extract_youtube_transcript": "POST /extract-youtube-transcript"
            },
            "content_analysis": {
                "analyze_content_structure": "POST /analyze-content-structure",
                "transcribe_and_analyze": "POST /transcribe-and-analyze"
            },
            "ai_transformation": {
                "rewrite_content": "POST /rewrite-content",
                "analyze_content_similarity": "POST /analyze-content-similarity",
                "check_plagiarism": "POST /check-plagiarism"
            },
            "voice_generation": {
                "generate_speech": "POST /generate-speech",
                "get_available_voices": "GET /available-voices",
                "batch_generate_speech": "POST /batch-generate-speech",
                "play_audio": "GET /play-audio/{filename}"
            },
            "status": "GET /process-status/{task_id}"
        },
        "current_task": "Task 2.2.1: Text-to-speech integration",
        "next_step": "Voice Generation System"
    }

@app.get("/test-cors")
async def test_cors():
    """Test endpoint to verify CORS is working"""
    return {
        "message": "CORS test successful",
        "timestamp": "2024-12-01T00:00:00Z",
        "cors_status": "enabled"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-12-01T00:00:00Z",
        "services": {
            "api": "running",
            "video_processing": "ready",
            "ai_models": "ready"
        }
    }

@app.post("/process-video")
async def process_video(video_data: Dict[str, Any]):
    """Process a YouTube video URL and transform it"""
    try:
        video_url = video_data.get("url")
        quality = video_data.get("quality", "720p")
        
        if not video_url:
            raise HTTPException(status_code=400, detail="Video URL is required")
        
        # Validate YouTube URL first
        is_valid, error_msg = video_processor.validate_youtube_url(video_url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid YouTube URL: {error_msg}")
        
        # Get video information
        video_info = await video_processor.get_video_info(video_url)
        
        return {
            "status": "validated",
            "message": "Video URL validated successfully",
            "video_url": video_url,
            "video_info": video_info,
            "quality": quality,
            "next_step": "download_video"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/analyze-content")
async def analyze_video_content(video_data: Dict[str, Any]):
    """Analyze YouTube video content for AI transformation"""
    try:
        video_url = video_data.get("url")
        quality = video_data.get("quality", "720p")
        
        if not video_url:
            raise HTTPException(status_code=400, detail="Video URL is required")
        
        # Analyze content for AI transformation
        analysis_result = await video_processor.analyze_video_content(video_url, quality)
        
        if analysis_result.get('analysis_status') == 'ready_for_audio_processing':
            return {
                "status": "analyzed",
                "message": "Content analysis completed successfully",
                "analysis_result": analysis_result,
                "next_step": "audio_extraction_and_analysis"
            }
        else:
            raise HTTPException(status_code=500, detail=analysis_result.get('error', 'Analysis failed'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content analysis error: {str(e)}")

@app.get("/video-info/{video_id}")
async def get_video_info(video_id: str):
    """Get information about a specific video by ID"""
    try:
        # This would typically query a database for stored video info
        # For now, return a placeholder response
        return {
            "video_id": video_id,
            "status": "info_retrieved",
            "message": "Video information retrieved"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving video info: {str(e)}")

@app.get("/audio-status")
async def get_audio_status():
    """Get current audio processing status"""
    try:
        status = await audio_processor.get_audio_processing_status()
        return {
            "status": "success",
            "audio_status": status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting audio status: {str(e)}")

@app.post("/extract-audio")
async def extract_audio(audio_data: Dict[str, Any]):
    """Extract audio from video for AI processing"""
    try:
        video_path = audio_data.get("video_path")
        quality = audio_data.get("quality", "medium")
        
        if not video_path:
            raise HTTPException(status_code=400, detail="Video path is required")
        
        # Extract audio
        extraction_result = await audio_processor.extract_audio_from_video(video_path, quality)
        
        if extraction_result['success']:
            return {
                "status": "extracted",
                "message": "Audio extracted successfully",
                "extraction_result": extraction_result,
                "next_step": "analyze_audio"
            }
        else:
            raise HTTPException(status_code=500, detail=extraction_result['error'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio extraction error: {str(e)}")

@app.post("/analyze-audio")
async def analyze_audio(audio_data: Dict[str, Any]):
    """Analyze audio content for AI transformation"""
    try:
        audio_path = audio_data.get("audio_path")
        
        if not audio_path:
            raise HTTPException(status_code=400, detail="Audio path is required")
        
        # Analyze audio content
        analysis_result = await audio_processor.analyze_audio_content(audio_path)
        
        if analysis_result['success']:
            return {
                "status": "analyzed",
                "message": "Audio analysis completed",
                "analysis_result": analysis_result,
                "next_step": "prepare_for_ai"
            }
        else:
            raise HTTPException(status_code=500, detail=analysis_result['error'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio analysis error: {str(e)}")

@app.post("/prepare-audio-for-ai")
async def prepare_audio_for_ai(audio_data: Dict[str, Any]):
    """Prepare audio content for AI transformation"""
    try:
        audio_path = audio_data.get("audio_path")
        
        if not audio_path:
            raise HTTPException(status_code=400, detail="Audio path is required")
        
        # Prepare audio for AI transformation
        preparation_result = await audio_processor.prepare_for_ai_transformation(audio_path)
        
        if preparation_result['success']:
            return {
                "status": "prepared",
                "message": "Audio prepared for AI transformation",
                "preparation_result": preparation_result,
                "next_step": "ai_content_transformation"
            }
        else:
            raise HTTPException(status_code=500, detail=preparation_result['error'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI preparation error: {str(e)}")

@app.post("/cleanup-temp-files")
async def cleanup_temp_files(max_age_hours: int = 24):
    """Clean up temporary files older than specified age"""
    try:
        await video_processor.cleanup_temp_files(max_age_hours)
        return {
            "status": "success",
            "message": f"Cleaned up temp files older than {max_age_hours} hours"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up temp files: {str(e)}")

@app.post("/extract-metadata")
async def extract_metadata(video_data: Dict[str, Any]):
    """Extract and optionally save video metadata (Phase 1.2.4)"""
    try:
        video_url = video_data.get("url")
        save_to_file = bool(video_data.get("save", True))
        if not video_url:
            raise HTTPException(status_code=400, detail="Video URL is required")
        
        result = await video_processor.extract_video_metadata(video_url, save_to_file)
        if result.get('success'):
            return {
                "status": "metadata_extracted",
                "message": result.get('message'),
                "metadata": result.get('metadata'),
                "saved": result.get('saved'),
                "saved_path": result.get('saved_path')
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Metadata extraction failed'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata extraction error: {str(e)}")

@app.post("/check-restrictions")
async def check_video_restrictions(video_data: Dict[str, Any]):
    """Check if a video has restrictions that prevent processing"""
    try:
        video_url = video_data.get("url")
        if not video_url:
            raise HTTPException(status_code=400, detail="Video URL is required")
        
        restrictions = await video_processor.check_video_restrictions(video_url)
        return {
            "status": "restrictions_checked",
            "restrictions": restrictions,
            "can_process": not restrictions.get('restricted', True)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restriction check error: {str(e)}")

@app.post("/transcribe-speech")
async def transcribe_speech_to_text(transcription_data: Dict[str, Any]):
    """Transcribe speech from audio file to text (Task 1.3.1)"""
    try:
        audio_path = transcription_data.get("audio_path")
        language = transcription_data.get("language", "en")
        model_size = transcription_data.get("model_size", "base")
        
        if not audio_path:
            raise HTTPException(status_code=400, detail="Audio path is required")
        
        # Validate model size
        valid_models = ['tiny', 'base', 'small', 'medium', 'large']
        if model_size not in valid_models:
            raise HTTPException(status_code=400, detail=f"Invalid model size. Must be one of: {valid_models}")
        
        # Perform transcription
        transcription_result = await audio_processor.transcribe_speech_to_text(
            audio_path, language, model_size
        )
        
        if transcription_result.get('success'):
            return {
                "status": "transcription_completed",
                "message": transcription_result.get('message'),
                "transcription": transcription_result.get('transcription'),
                "saved_path": transcription_result.get('saved_path'),
                "next_step": transcription_result.get('next_step')
            }
        else:
            raise HTTPException(status_code=500, detail=transcription_result.get('error', 'Transcription failed'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

@app.get("/transcription-status/{audio_filename}")
async def get_transcription_status(audio_filename: str):
    """Get the status of transcription for a specific audio file"""
    try:
        # Construct the full audio path
        audio_path = f"temp/{audio_filename}"
        
        # Convert to absolute path if needed
        if not os.path.isabs(audio_path):
            # Go up one level from backend directory to project root
            project_root = os.path.dirname(os.getcwd())
            audio_path = os.path.join(project_root, audio_path)
        
        status = await audio_processor.get_transcription_status(audio_path)
        return {
            "status": "status_retrieved",
            "audio_file": audio_filename,
            "transcription_status": status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval error: {str(e)}")

@app.post("/extract-and-transcribe")
async def extract_audio_and_transcribe(video_data: Dict[str, Any]):
    """Extract audio from video and transcribe to text in one operation"""
    try:
        video_path = video_data.get("video_path")
        quality = video_data.get("quality", "medium")
        language = video_data.get("language", "en")
        model_size = video_data.get("model_size", "base")
        
        if not video_path:
            raise HTTPException(status_code=400, detail="Video path is required")
        
        # Convert to absolute path if needed
        if not os.path.isabs(video_path):
            # Go up one level from backend directory to project root
            project_root = os.path.dirname(os.getcwd())
            video_path = os.path.join(project_root, video_path)
        
        # Step 1: Extract audio
        extraction_result = await audio_processor.extract_audio_from_video(video_path, quality)
        
        if not extraction_result.get('success'):
            raise HTTPException(status_code=500, detail=extraction_result.get('error', 'Audio extraction failed'))
        
        audio_path = extraction_result.get('audio_file')
        
        # Step 2: Transcribe audio
        transcription_result = await audio_processor.transcribe_speech_to_text(
            audio_path, language, model_size
        )
        
        if transcription_result.get('success'):
            return {
                "status": "extraction_and_transcription_completed",
                "message": "Audio extracted and transcribed successfully",
                "audio_extraction": extraction_result,
                "transcription": transcription_result,
                "next_step": "content_structure_analysis"
            }
        else:
            raise HTTPException(status_code=500, detail=transcription_result.get('error', 'Transcription failed'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction and transcription error: {str(e)}")

@app.post("/analyze-content-structure")
async def analyze_content_structure(transcription_data: Dict[str, Any]):
    """Analyze content structure from transcription (Task 1.3.2)"""
    try:
        # Validate input
        if not transcription_data.get('text'):
            raise HTTPException(status_code=400, detail="Transcription text is required")
        
        # Perform content structure analysis
        analysis_result = await audio_processor.analyze_content_structure(transcription_data)
        
        if analysis_result.get('success'):
            return {
                "status": "content_analysis_completed",
                "message": "Content structure analysis completed successfully",
                "analysis": analysis_result,
                "next_step": "ai_content_transformation"
            }
        else:
            raise HTTPException(status_code=500, detail=analysis_result.get('error', 'Content analysis failed'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content analysis error: {str(e)}")

@app.post("/transcribe-and-analyze")
async def transcribe_andAnalyze(audio_data: Dict[str, Any]):
    """Transcribe audio and analyze content structure in one operation"""
    try:
        audio_path = audio_data.get("audio_path")
        language = audio_data.get("language", "en")
        model_size = audio_data.get("model_size", "base")
        
        if not audio_path:
            raise HTTPException(status_code=400, detail="Audio path is required")
        
        # Step 1: Transcribe speech to text
        transcription_result = await audio_processor.transcribe_speech_to_text(
            audio_path, language, model_size
        )
        
        if not transcription_result.get('success'):
            raise HTTPException(status_code=500, detail=transcription_result.get('error', 'Transcription failed'))
        
        # Step 2: Analyze content structure
        analysis_result = await audio_processor.analyze_content_structure(
            transcription_result.get('transcription', {})
        )
        
        if analysis_result.get('success'):
            return {
                "status": "transcription_and_analysis_completed",
                "message": "Audio transcribed and content analyzed successfully",
                "transcription": transcription_result,
                "content_analysis": analysis_result,
                "next_step": "ai_content_transformation"
            }
        else:
            raise HTTPException(status_code=500, detail=analysis_result.get('error', 'Content analysis failed'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription and analysis error: {str(e)}")

@app.post("/extract-youtube-transcript")
async def extract_youtube_transcript(video_data: Dict[str, Any]):
    """Extract real transcript from YouTube video with timestamps"""
    try:
        youtube_url = video_data.get("url")
        language = video_data.get("language", "en")
        
        if not youtube_url:
            raise HTTPException(status_code=400, detail="YouTube URL is required")
        
        # Validate YouTube URL first
        is_valid, error_msg = video_processor.validate_youtube_url(youtube_url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid YouTube URL: {error_msg}")
        
        print(f"Attempting to extract transcript from: {youtube_url}")  # Debug log
        
        # Extract transcript directly from YouTube using the audio processor
        transcript_result = await audio_processor.extract_youtube_transcript_robust(youtube_url, language)
        
        print(f"Transcript result: {transcript_result}")  # Debug log
        
        if not transcript_result.get('success'):
            raise HTTPException(status_code=500, detail=transcript_result.get('error', 'YouTube transcript extraction failed'))
        
        return {
            "status": "youtube_transcript_extracted",
            "message": "Real YouTube transcript extracted successfully",
            "transcript": transcript_result,
            "next_step": "content_structure_analysis"
        }
    
    except Exception as e:
        print(f"Error in extract_youtube_transcript: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"YouTube transcript extraction error: {str(e)}")

@app.get("/process-status/{task_id}")
async def get_process_status(task_id: str):
    """Get the status of a processing task"""
    return {
        "task_id": task_id,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

# ===== PHASE 2: AI Content Transformation =====

@app.post("/rewrite-content")
async def rewrite_content(content_data: Dict[str, Any]):
    """Rewrite and enhance content using AI-powered analysis"""
    try:
        original_text = content_data.get("text")
        modification_type = content_data.get("modification_type", "enhance")
        target_audience = content_data.get("target_audience", "general")
        style_preference = content_data.get("style_preference", "professional")
        
        if not original_text:
            raise HTTPException(status_code=400, detail="Original text is required")
        
        # Validate parameters
        valid_modification_types = ["enhance", "simplify", "formalize", "casual"]
        valid_target_audiences = ["general", "technical", "academic", "casual"]
        valid_style_preferences = ["professional", "conversational", "academic"]
        
        if modification_type not in valid_modification_types:
            raise HTTPException(status_code=400, detail=f"Invalid modification_type. Must be one of: {valid_modification_types}")
        
        if target_audience not in valid_target_audiences:
            raise HTTPException(status_code=400, detail=f"Invalid target_audience. Must be one of: {valid_target_audiences}")
        
        if style_preference not in valid_style_preferences:
            raise HTTPException(status_code=400, detail=f"Invalid style_preference. Must be one of: {valid_style_preferences}")
        
        # Process content rewriting
        result = await content_rewriter.analyze_and_rewrite_content(
            original_text=original_text,
            modification_type=modification_type,
            target_audience=target_audience,
            style_preference=style_preference
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Content rewriting failed'))
        
        return {
            "status": "content_rewritten",
            "message": f"Content successfully rewritten using {modification_type} modification",
            "result": result,
            "next_step": "voice_generation"
        }
        
    except Exception as e:
        logger.error(f"Error in content rewriting: {e}")
        raise HTTPException(status_code=500, detail=f"Content rewriting error: {str(e)}")

@app.post("/analyze-content-similarity")
async def analyze_content_similarity(content_data: Dict[str, Any]):
    """Analyze content similarity and detect potential plagiarism"""
    try:
        original_text = content_data.get("original_text")
        comparison_text = content_data.get("comparison_text")
        
        if not original_text or not comparison_text:
            raise HTTPException(status_code=400, detail="Both original_text and comparison_text are required")
        
        # Calculate similarity metrics
        similarity_result = await content_rewriter.analyze_content_similarity(original_text, comparison_text)
        
        return {
            "status": "similarity_analyzed",
            "message": "Content similarity analysis completed",
            "result": similarity_result,
            "next_step": "compliance_check"
        }
        
    except Exception as e:
        logger.error(f"Error in content similarity analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Similarity analysis error: {str(e)}")

@app.post("/check-plagiarism")
async def check_plagiarism(content_data: Dict[str, Any]):
    """Check content for potential plagiarism and copyright issues"""
    try:
        text = content_data.get("text")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text content is required")
        
        # Perform plagiarism check
        plagiarism_result = await content_rewriter.check_plagiarism(text)
        
        return {
            "status": "plagiarism_checked",
            "message": "Plagiarism check completed",
            "result": plagiarism_result,
            "next_step": "content_validation"
        }
        
    except Exception as e:
        logger.error(f"Error in plagiarism check: {e}")
        raise HTTPException(status_code=500, detail=f"Plagiarism check error: {str(e)}")

# ===== PHASE 2.2: Voice Generation System =====

@app.get("/available-voices")
async def get_available_voices():
    """Get list of available voice options and configurations"""
    try:
        voices = voice_generator.get_available_voices()
        return {
            "status": "voices_retrieved",
            "message": f"Found {len(voices)} available voice options",
            "voices": voices,
            "next_step": "voice_selection"
        }
    except Exception as e:
        logger.error(f"Error retrieving available voices: {e}")
        raise HTTPException(status_code=500, detail=f"Voice retrieval error: {str(e)}")

@app.post("/generate-speech")
async def generate_speech(speech_data: Dict[str, Any]):
    """Generate speech from text using specified voice configuration"""
    try:
        text = speech_data.get("text")
        voice_id = speech_data.get("voice_id", "default")
        custom_config = speech_data.get("custom_config", {})
        
        if not text:
            raise HTTPException(status_code=400, detail="Text content is required for speech generation")
        
        # Get voice configuration
        voice_config = voice_generator.get_voice_config(voice_id)
        if not voice_config:
            raise HTTPException(status_code=400, detail=f"Voice ID '{voice_id}' not found")
        
        # Apply custom configuration if provided
        if custom_config:
            voice_config = {**voice_config, **custom_config}
        
        # Generate speech
        result = await voice_generator.generate_speech(text, voice_config)
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Speech generation failed'))
        
        return {
            "status": "speech_generated",
            "message": f"Speech successfully generated using {voice_config.get('name', 'Unknown')} voice",
            "result": result,
            "next_step": "audio_post_processing"
        }
        
    except Exception as e:
        logger.error(f"Error in speech generation: {e}")
        raise HTTPException(status_code=500, detail=f"Speech generation error: {str(e)}")

@app.post("/batch-generate-speech")
async def batch_generate_speech(batch_data: Dict[str, Any]):
    """Generate speech for multiple text inputs"""
    try:
        texts = batch_data.get("texts", [])
        voice_id = batch_data.get("voice_id", "default")
        custom_config = batch_data.get("custom_config", {})
        
        if not texts or not isinstance(texts, list):
            raise HTTPException(status_code=400, detail="Texts array is required for batch speech generation")
        
        if len(texts) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 texts allowed per batch")
        
        # Get voice configuration
        voice_config = voice_generator.get_voice_config(voice_id)
        if not voice_config:
            raise HTTPException(status_code=400, detail=f"Voice ID '{voice_id}' not found")
        
        # Apply custom configuration if provided
        if custom_config:
            voice_config = {**voice_config, **custom_config}
        
        # Generate speech for all texts
        results = await voice_generator.batch_generate_speech(texts, voice_config)
        
        return {
            "status": "batch_speech_generated",
            "message": f"Successfully generated speech for {len(texts)} text inputs",
            "results": results,
            "voice_used": voice_config.get('name', 'Unknown'),
            "next_step": "audio_post_processing"
        }
        
    except Exception as e:
        logger.error(f"Error in batch speech generation: {e}")
        raise HTTPException(status_code=500, detail=f"Batch speech generation error: {str(e)}")

@app.get("/play-audio/{filename}")
async def play_audio(filename: str):
    """Serve audio files for playback"""
    try:
        # Construct the full path to the audio file
        audio_path = os.path.join("output", filename)
        
        # Check if file exists
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Return the audio file for playback
        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Error serving audio file: {e}")
        raise HTTPException(status_code=500, detail=f"Audio file error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 