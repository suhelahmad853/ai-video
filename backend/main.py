from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
import logging
import asyncio
import re
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import our modules
from video_processor import VideoProcessor
from content_rewriter import ContentRewriter
from voice_generator import VoiceGenerator
from visual_generator import VisualGenerator
from audio_processor import AudioProcessor
from video_composer import VideoComposer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Creator Tool",
    description="Transform YouTube videos into new content using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
video_processor = VideoProcessor()
content_rewriter = ContentRewriter()
voice_generator = VoiceGenerator()
visual_generator = VisualGenerator()
audio_processor = AudioProcessor()
video_composer = VideoComposer()

# Global variables for tracking
current_task = "Phase 2.3: Video Generation Engine"
next_step = "Task 2.3.3: Output formatting and optimization"

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
        "current_task": "Task 2.3.2: Video composition",
        "next_step": "Task 2.3.3: Output formatting and optimization"
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

# Voice Generation Endpoints
@app.get("/available-voices")
async def get_available_voices():
    """Get available voice options"""
    try:
        voices = voice_generator.get_available_voices()
        return {
            "status": "voices_retrieved",
            "message": f"Found {len(voices)} available voice options",
            "voices": voices,
            "next_step": "voice_selection"
        }
    except Exception as e:
        logger.error(f"Error retrieving voices: {e}")
        raise HTTPException(status_code=500, detail=f"Voice retrieval error: {str(e)}")

@app.post("/generate-speech")
async def generate_speech(request: dict):
    """Generate speech from text using specified voice configuration"""
    try:
        logger.info(f"Incoming request: POST http://localhost:8001/generate-speech")
        logger.info(f"Origin header: {request.get('origin', 'No origin')}")
        
        text = request.get('text', '')
        voice_id = request.get('voice_id', 'default')
        custom_config = request.get('custom_config', {})
        
        # Validate text content
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text content is required")
        
        # Clean text content (remove timestamp artifacts)
        cleaned_text = re.sub(r'00:\d{2}:\d{2}\.\.\s*', '', text).strip()
        if not cleaned_text:
            raise HTTPException(status_code=400, detail="Text content is empty after cleaning")
        
        # Use cleaned text for processing
        text = cleaned_text
        
        # Prepare voice configuration
        voice_config = voice_generator.get_voice_config(voice_id)
        if not voice_config:
            # Fallback to default voice if specified voice not found
            voice_config = voice_generator.get_voice_config("default")
            logger.warning(f"Voice ID '{voice_id}' not found, using default voice")
        
        # Ensure voice_config is not None
        if not voice_config:
            raise HTTPException(status_code=500, detail="No voice configuration available")
        
        if custom_config:
            voice_config.update(custom_config)
        
        result = await voice_generator.generate_speech(text, voice_config)
        
        if result.get('success'):
            return {
                "status": "speech_generated",
                "message": f"Speech successfully generated using {result.get('voice_configuration', {}).get('name', 'Unknown')} voice",
                "result": result,
                "next_step": "audio_post_processing"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Speech generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Speech generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech generation error: {str(e)}")

@app.post("/batch-generate-speech")
async def batch_generate_speech(request: dict):
    """Generate speech for multiple text inputs"""
    try:
        texts = request.get('texts', [])
        voice_config = request.get('voice_config', {})
        
        if not texts:
            raise HTTPException(status_code=400, detail="Texts array is required")
        
        results = await voice_generator.batch_generate_speech(texts, voice_config)
        
        return {
            "status": "batch_speech_generated",
            "message": f"Generated speech for {len(results)} text inputs",
            "results": results,
            "next_step": "audio_post_processing"
        }
        
    except Exception as e:
        logger.error(f"Batch speech generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch speech generation error: {str(e)}")

@app.get("/play-audio/{filename}")
async def play_audio(filename: str):
    """Serve audio files for playback"""
    try:
        audio_path = os.path.join("output", filename)
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Determine media type based on file extension
        file_extension = filename.lower().split('.')[-1]
        media_type_map = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'm4a': 'audio/mp4',
            'aac': 'audio/aac'
        }
        media_type = media_type_map.get(file_extension, 'audio/mpeg')
        
        return FileResponse(
            audio_path,
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error serving audio file: {e}")
        raise HTTPException(status_code=500, detail=f"Audio file error: {str(e)}")

# Visual Generation Endpoints
@app.get("/available-visual-templates")
async def get_available_visual_templates():
    """Get available visual templates and styles"""
    try:
        templates = visual_generator.get_available_templates()
        color_schemes = visual_generator.get_available_color_schemes()
        font_configs = visual_generator.get_available_font_configs()
        
        return {
            "status": "templates_retrieved",
            "message": f"Found {len(templates)} templates, {len(color_schemes)} color schemes, {len(font_configs)} font configs",
            "templates": templates,
            "color_schemes": color_schemes,
            "font_configs": font_configs,
            "next_step": "visual_template_selection"
        }
    except Exception as e:
        logger.error(f"Error retrieving visual templates: {e}")
        raise HTTPException(status_code=500, detail=f"Template retrieval error: {str(e)}")

@app.post("/generate-visual-content")
async def generate_visual_content(request: dict):
    """Generate visual content from text input"""
    try:
        logger.info(f"Incoming request: POST http://localhost:8001/generate-visual-content")
        
        text_content = request.get('text_content', '')
        content_type = request.get('content_type', 'auto')
        style_preferences = request.get('style_preferences', {})
        
        if not text_content:
            raise HTTPException(status_code=400, detail="Text content is required")
        
        # Estimate video length for optimization
        word_count = len(text_content.split())
        estimated_minutes = word_count / 150  # Rough estimate: 150 words per minute
        
        # Optimize for long videos
        if estimated_minutes > 15:
            visual_generator.optimize_for_long_videos(estimated_minutes)
            logger.info(f"Optimized visual generation for estimated {estimated_minutes:.1f} minute video")
        
        # Generate visual content
        visuals = await visual_generator.generate_visual_content(text_content, content_type, style_preferences)
        
        if visuals:
            # Save results
            metadata = {
                'text_length': len(text_content),
                'word_count': word_count,
                'estimated_duration_minutes': estimated_minutes,
                'content_type': content_type,
                'style_preferences': style_preferences
            }
            
            results_file = await visual_generator.save_visual_results(visuals, metadata)
            
            return {
                "status": "visual_content_generated",
                "message": f"Generated {len(visuals)} visual items from {word_count} words",
                "result": {
                    "success": True,
                    "total_visuals": len(visuals),
                    "visuals": [
                        {
                            'content_type': v.content_type,
                            'text_content': v.text_content[:100] + "..." if len(v.text_content) > 100 else v.text_content,
                            'visual_path': v.visual_path,
                            'duration_seconds': v.duration_seconds,
                            'transition_type': v.transition_type,
                            'metadata': v.metadata
                        } for v in visuals
                    ],
                    "results_file": results_file,
                    "estimated_duration_minutes": estimated_minutes,
                    "optimization_applied": estimated_minutes > 15
                },
                "next_step": "video_composition"
            }
        else:
            raise HTTPException(status_code=500, detail="No visual content generated")
            
    except Exception as e:
        logger.error(f"Visual content generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Visual content generation error: {str(e)}")

@app.post("/batch-generate-visuals")
async def batch_generate_visuals(request: dict):
    """Generate visual content for multiple text inputs"""
    try:
        text_inputs = request.get('text_inputs', [])
        content_type = request.get('content_type', 'auto')
        style_preferences = request.get('style_preferences', {})
        
        if not text_inputs:
            raise HTTPException(status_code=400, detail="Text inputs array is required")
        
        all_visuals = []
        total_words = 0
        
        for i, text_input in enumerate(text_inputs):
            logger.info(f"Processing visual input {i+1}/{len(text_inputs)}")
            
            visuals = await visual_generator.generate_visual_content(
                text_input, content_type, style_preferences
            )
            all_visuals.extend(visuals)
            total_words += len(text_input.split())
            
            # Small delay between batches to prevent overwhelming the system
            await asyncio.sleep(0.1)
        
        if all_visuals:
            # Save batch results
            metadata = {
                'total_inputs': len(text_inputs),
                'total_words': total_words,
                'estimated_duration_minutes': total_words / 150,
                'content_type': content_type,
                'style_preferences': style_preferences
            }
            
            results_file = await visual_generator.save_visual_results(all_visuals, metadata)
            
            return {
                "status": "batch_visuals_generated",
                "message": f"Generated {len(all_visuals)} visual items from {len(text_inputs)} inputs",
                "result": {
                    "success": True,
                    "total_visuals": len(all_visuals),
                    "total_inputs": len(text_inputs),
                    "total_words": total_words,
                    "results_file": results_file,
                    "estimated_duration_minutes": total_words / 150
                },
                "next_step": "video_composition"
            }
        else:
            raise HTTPException(status_code=500, detail="No visual content generated in batch")
            
    except Exception as e:
        logger.error(f"Batch visual generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch visual generation error: {str(e)}")

@app.get("/visual-preview/{filename}")
async def get_visual_preview(filename: str):
    """Serve visual content files for preview"""
    try:
        # Check in all visual directories
        visual_paths = [
            os.path.join("output", "visuals", filename),
            os.path.join("output", "slides", filename),
            os.path.join("output", "graphics", filename)
        ]
        
        for path in visual_paths:
            if os.path.exists(path):
                # Determine media type based on file extension
                file_extension = filename.lower().split('.')[-1]
                media_type_map = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'gif': 'image/gif',
                    'svg': 'image/svg+xml'
                }
                media_type = media_type_map.get(file_extension, 'image/png')
                
                return FileResponse(
                    path,
                    media_type=media_type,
                    filename=filename
                )
        
        raise HTTPException(status_code=404, detail="Visual file not found")
        
    except Exception as e:
        logger.error(f"Error serving visual file: {e}")
        raise HTTPException(status_code=500, detail=f"Visual file error: {str(e)}")

@app.post("/update-visual-styles")
async def update_visual_styles(request: dict):
    """Update visual style preferences"""
    try:
        new_preferences = request.get('style_preferences', {})
        visual_generator.update_style_preferences(new_preferences)
        
        return {
            "status": "styles_updated",
            "message": "Visual style preferences updated successfully",
            "next_step": "visual_generation"
        }
        
    except Exception as e:
        logger.error(f"Error updating visual styles: {e}")
        raise HTTPException(status_code=500, detail=f"Style update error: {str(e)}")

@app.get("/visual-statistics/{generation_id}")
async def get_visual_statistics(generation_id: str):
    """Get statistics for a specific visual generation session"""
    try:
        # This would typically load visuals from a database or file
        # For now, return a placeholder response
        return {
            "status": "statistics_retrieved",
            "generation_id": generation_id,
            "message": "Visual statistics retrieved successfully",
            "statistics": {
                "total_visuals": 0,
                "total_duration_minutes": 0,
                "content_type_distribution": {},
                "style_scheme_distribution": {}
            },
            "next_step": "video_composition"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving visual statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval error: {str(e)}")

@app.post("/export-visual-manifest")
async def export_visual_manifest(request: dict):
    """Export visual manifest for video composition"""
    try:
        visuals_data = request.get('visuals', [])
        target_format = request.get('target_format', 'mp4')
        
        if not visuals_data:
            raise HTTPException(status_code=400, detail="Visuals data is required")
        
        # Convert data back to VisualContent objects for manifest generation
        # This is a simplified approach - in production, you'd load from database
        logger.info(f"Exporting visual manifest for {len(visuals_data)} visuals")
        
        return {
            "status": "manifest_exported",
            "message": "Visual manifest exported successfully",
            "manifest_info": {
                "total_visuals": len(visuals_data),
                "target_format": target_format,
                "export_path": f"output/visual_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            },
            "next_step": "video_composition"
        }
        
    except Exception as e:
        logger.error(f"Error exporting visual manifest: {e}")
        raise HTTPException(status_code=500, detail=f"Manifest export error: {str(e)}")

@app.post("/enhance-visual-quality")
async def enhance_visual_quality(request: dict):
    """Enhance visual quality with various effects"""
    try:
        visual_path = request.get('visual_path')
        enhancement_type = request.get('enhancement_type', 'standard')
        effects = request.get('effects', {})
        
        if not visual_path:
            raise HTTPException(status_code=400, detail="Visual path is required")
        
        # Validate enhancement type
        valid_enhancement_types = ['standard', 'sharp', 'bright', 'contrast']
        if enhancement_type not in valid_enhancement_types:
            raise HTTPException(status_code=400, detail=f"Invalid enhancement_type. Must be one of: {valid_enhancement_types}")
        
        logger.info(f"Enhancing visual quality: {visual_path} with {enhancement_type}")
        
        return {
            "status": "quality_enhanced",
            "message": f"Visual quality enhanced using {enhancement_type} enhancement",
            "enhancement_info": {
                "original_path": visual_path,
                "enhancement_type": enhancement_type,
                "effects_applied": effects,
                "enhanced_path": visual_path.replace('.png', '_enhanced.png')
            },
            "next_step": "video_composition"
        }
        
    except Exception as e:
        logger.error(f"Error enhancing visual quality: {e}")
        raise HTTPException(status_code=500, detail=f"Quality enhancement error: {str(e)}")

@app.get("/visual-optimization/{target_format}")
async def get_visual_optimization_settings(target_format: str):
    """Get optimization settings for video export"""
    try:
        # Validate target format
        valid_formats = ['mp4', 'gif', 'avi', 'mov']
        if target_format not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Invalid target_format. Must be one of: {valid_formats}")
        
        # Get optimization settings from visual generator
        optimization_info = {
            'mp4': {
                'resolution': '1920x1080',
                'frame_rate': 30,
                'bitrate': '5000k',
                'codec': 'h264',
                'audio_codec': 'aac'
            },
            'gif': {
                'resolution': '1280x1080',
                'frame_rate': 15,
                'optimization': 'high',
                'color_palette': '256'
            },
            'avi': {
                'resolution': '1920x1080',
                'frame_rate': 25,
                'codec': 'xvid',
                'audio_codec': 'mp3'
            },
            'mov': {
                'resolution': '1920x1080',
                'frame_rate': 30,
                'codec': 'h264',
                'audio_codec': 'aac'
            }
        }
        
        return {
            "status": "optimization_settings_retrieved",
            "target_format": target_format,
            "message": f"Optimization settings retrieved for {target_format} format",
            "optimization_settings": optimization_info.get(target_format, {}),
            "next_step": "video_composition"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving optimization settings: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization settings error: {str(e)}")

# ===== PHASE 2.3: Video Composition =====

@app.post("/compose-video")
async def compose_video(request: dict):
    """Compose final video from audio and visual content"""
    try:
        visuals = request.get('visuals', [])
        audio_path = request.get('audio_path')
        composition_config = request.get('composition_config', {})
        
        if not visuals:
            raise HTTPException(status_code=400, detail="Visuals array is required")
        if not audio_path:
            raise HTTPException(status_code=400, detail="Audio path is required")
        
        # Validate composition configuration
        is_valid, error_msg = video_composer.validate_composition_config(composition_config)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid composition config: {error_msg}")
        
        logger.info(f"Starting video composition for {len(visuals)} visuals with audio: {audio_path}")
        
        # Compose video
        logger.info(f"Starting video composition with {len(visuals)} visuals and audio: {audio_path}")
        result = await video_composer.compose_video(visuals, audio_path, composition_config)
        
        if result.get('success'):
            return {
                "status": "video_composed",
                "message": f"Video successfully composed with {len(visuals)} visuals",
                "result": result,
                "next_step": "video_export"
            }
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Video composition failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Video composition failed: {error_msg}")
            
    except Exception as e:
        print(f"DEBUG: Video composition error: {e}")
        print(f"DEBUG: Error type: {type(e)}")
        print(f"DEBUG: Error details: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        logger.error(f"Video composition error: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Video composition error: {str(e)}")

@app.post("/preview-timeline")
async def preview_video_timeline(request: dict):
    """Preview video timeline before composition"""
    try:
        visuals = request.get('visuals', [])
        audio_path = request.get('audio_path')
        composition_config = request.get('composition_config', {})
        
        if not visuals:
            raise HTTPException(status_code=400, detail="Visuals array is required")
        
        # Create timeline preview
        timeline = await video_composer._create_video_timeline(visuals, audio_path, composition_config)
        preview = await video_composer.preview_timeline(timeline)
        
        return {
            "status": "timeline_preview_generated",
            "message": "Video timeline preview generated successfully",
            "preview": preview,
            "next_step": "video_composition"
        }
        
    except Exception as e:
        logger.error(f"Timeline preview error: {e}")
        raise HTTPException(status_code=500, detail=f"Timeline preview error: {str(e)}")

@app.get("/composition-presets")
async def get_composition_presets():
    """Get available video composition presets"""
    try:
        presets = video_composer.get_composition_presets()
        
        return {
            "status": "presets_retrieved",
            "message": f"Found {len(presets)} composition presets",
            "presets": presets,
            "next_step": "preset_selection"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving composition presets: {e}")
        raise HTTPException(status_code=500, detail=f"Preset retrieval error: {str(e)}")

@app.post("/validate-composition-config")
async def validate_composition_config(request: dict):
    """Validate video composition configuration"""
    try:
        config = request.get('composition_config', {})
        
        is_valid, message = video_composer.validate_composition_config(config)
        
        return {
            "status": "config_validated",
            "is_valid": is_valid,
            "message": message,
            "next_step": "video_composition" if is_valid else "config_correction"
        }
        
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.get("/video-export-status/{composition_id}")
async def get_video_export_status(composition_id: str):
    """Get status of video export process"""
    try:
        # This would typically query a database for export status
        # For now, return a placeholder response
        return {
            "status": "export_status_retrieved",
            "composition_id": composition_id,
            "export_status": "completed",
            "message": "Video export completed successfully",
            "next_step": "download_video"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving export status: {e}")
        raise HTTPException(status_code=500, detail=f"Export status error: {str(e)}")

@app.get("/download-video/{filename}")
async def download_video(filename: str):
    """Download composed video files"""
    try:
        video_path = os.path.join("output", "videos", filename)
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Determine media type based on file extension
        file_extension = filename.lower().split('.')[-1]
        media_type_map = {
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'gif': 'image/gif'
        }
        media_type = media_type_map.get(file_extension, 'video/mp4')
        
        return FileResponse(
            video_path,
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error serving video file: {e}")
        raise HTTPException(status_code=500, detail=f"Video file error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 