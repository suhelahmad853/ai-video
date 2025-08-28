from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import asyncio
from typing import Dict, Any
from video_processor import video_processor
from audio_processor import audio_processor
import logging

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
            "health": "/health",
            "process_video": "/process-video",
            "analyze_content": "/analyze-content",
            "extract_metadata": "/extract-metadata",
            "check_restrictions": "/check-restrictions",
            "transcribe_speech": "/transcribe-speech",
            "transcription_status": "/transcription-status/{audio_filename}",
            "extract_and_transcribe": "/extract-and-transcribe",
            "extract_audio": "/extract-audio",
            "analyze_audio": "/analyze-audio",
            "prepare_audio_for_ai": "/prepare-audio-for-ai",
            "docs": "/docs"
        }
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

@app.get("/process-status/{task_id}")
async def get_process_status(task_id: str):
    """Get the status of a video processing task"""
    # TODO: Implement actual status checking
    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 45,
        "message": "AI content transformation in progress"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 