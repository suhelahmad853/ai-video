"""
Video Composition Module
Handles combining audio, visuals, and transitions into final video output
Part of Phase 2.3: Video Generation Engine
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import asyncio
from dataclasses import dataclass
import subprocess
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VideoSegment:
    """Data class for video timeline segments"""
    start_time: float
    end_time: float
    duration: float
    visual_path: str
    audio_path: Optional[str]
    transition_in: str
    transition_out: str
    segment_type: str  # 'visual', 'audio', 'transition'
    metadata: Dict

@dataclass
class VideoTimeline:
    """Data class for complete video timeline"""
    total_duration: float
    segments: List[VideoSegment]
    audio_track: Optional[str]
    background_music: Optional[str]
    output_format: str
    resolution: Tuple[int, int]
    frame_rate: int
    metadata: Dict

class VideoComposer:
    """Composes final video from audio and visual content"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.videos_dir = os.path.join(output_dir, "videos")
        self.temp_dir = os.path.join(output_dir, "temp")
        
        # Create output directories
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Video composition settings
        self.default_resolution = (1920, 1080)  # HD
        self.default_frame_rate = 30
        self.default_bitrate = "5000k"
        self.transition_duration = 0.5  # seconds
        
        # Supported output formats
        self.supported_formats = ['mp4', 'avi', 'mov', 'gif']
        
        # Transition effects
        self.transition_effects = {
            'fade': 'fade',
            'slide': 'slideleft',
            'dissolve': 'dissolve',
            'wipe': 'wiperight',
            'zoom': 'zoom'
        }
        
        logger.info("Video Composer initialized")
    
    async def compose_video(self, 
                           visuals: List[Dict], 
                           audio_path: str,
                           composition_config: Dict = None) -> Dict:
        """
        Compose final video from visuals and audio
        
        Args:
            visuals: List of visual content items
            audio_path: Path to audio file
            composition_config: Video composition configuration
            
        Returns:
            Composition result with video file path
        """
        try:
            logger.info(f"Starting video composition for {len(visuals)} visuals")
            logger.info(f"Audio path: {audio_path}")
            logger.info(f"Output directory: {self.output_dir}")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            # Validate inputs
            if not visuals:
                raise ValueError("No visual content provided")
            
            # Validate and find audio file
            if not audio_path:
                raise ValueError("Audio path is required")
            
            # Check if audio file exists
            if not os.path.exists(audio_path):
                logger.warning(f"Audio file not found at: {audio_path}")
                # Try to find the file in different locations
                possible_audio_paths = [
                    audio_path,
                    os.path.join(os.getcwd(), audio_path),
                    os.path.join(self.output_dir, audio_path.split('/')[-1]),
                    os.path.join(os.getcwd(), 'output', audio_path.split('/')[-1])
                ]
                
                found_audio_path = None
                for path in possible_audio_paths:
                    if os.path.exists(path):
                        found_audio_path = path
                        logger.info(f"Found audio file at: {found_audio_path}")
                        break
                
                if not found_audio_path:
                    raise ValueError(f"Audio file not found in any location: {audio_path}")
                
                audio_path = found_audio_path
            
            # Apply default configuration
            config = self._get_default_config()
            if composition_config:
                config.update(composition_config)
            
            # Create video timeline
            timeline = await self._create_video_timeline(visuals, audio_path, config)
            
            # Render video
            video_path = await self._render_video(timeline, config)
            
            # Generate composition report
            report = self._generate_composition_report(timeline, video_path)
            
            logger.info(f"Video composition completed: {video_path}")
            return {
                'success': True,
                'video_path': video_path,
                'timeline': timeline,
                'report': report,
                'metadata': {
                    'total_duration': timeline.total_duration,
                    'total_segments': len(timeline.segments),
                    'output_format': timeline.output_format,
                    'resolution': timeline.resolution,
                    'frame_rate': timeline.frame_rate,
                    'composed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in video composition: {e}")
            return {
                'success': False,
                'error': str(e),
                'metadata': {
                    'composed_at': datetime.now().isoformat()
                }
            }
    
    def _get_default_config(self) -> Dict:
        """Get default video composition configuration"""
        return {
            'output_format': 'mp4',
            'resolution': self.default_resolution,
            'frame_rate': self.default_frame_rate,
            'bitrate': self.default_bitrate,
            'enable_transitions': True,
            'transition_duration': self.transition_duration,
            'enable_background_music': False,
            'background_music_volume': 0.3,
            'enable_audio_enhancement': True,
            'enable_video_enhancement': True
        }
    
    async def _create_video_timeline(self, visuals: List[Dict], audio_path: str, config: Dict) -> VideoTimeline:
        """Create video timeline from visuals and audio"""
        try:
            segments = []
            current_time = 0.0
            
            # Process each visual
            for i, visual in enumerate(visuals):
                # Validate visual data
                visual_path = visual.get('visual_path', '')
                if not visual_path:
                    logger.warning(f"Visual {i} missing visual_path, skipping")
                    continue
                
                # Check if visual file exists
                if not os.path.exists(visual_path):
                    logger.warning(f"Visual file not found: {visual_path}")
                    # Try to find the file in different locations
                    possible_paths = [
                        visual_path,
                        os.path.join(os.getcwd(), visual_path),
                        os.path.join(self.output_dir, visual_path.split('/')[-1]),
                        os.path.join(os.getcwd(), 'output', visual_path.split('/')[-1]),
                        os.path.join(self.output_dir, visual_path.split('/')[-2], visual_path.split('/')[-1])
                    ]
                    
                    found_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            found_path = path
                            logger.info(f"Found visual file at: {found_path}")
                            break
                    
                    if not found_path:
                        logger.error(f"Visual file not found in any location: {visual_path}")
                        continue
                    
                    visual_path = found_path
                
                # Calculate segment timing
                segment_duration = visual.get('duration_seconds', 5.0)
                
                # Create visual segment
                visual_segment = VideoSegment(
                    start_time=current_time,
                    end_time=current_time + segment_duration,
                    duration=segment_duration,
                    visual_path=visual_path,
                    audio_path=None,  # Will be synchronized with main audio
                    transition_in=self._get_transition_in(i, visual),
                    transition_out=self._get_transition_out(i, visual, len(visuals)),
                    segment_type='visual',
                    metadata={
                        'content_type': visual.get('content_type', 'unknown'),
                        'original_text': visual.get('text_content', '')[:100],
                        'visual_index': i
                    }
                )
                
                segments.append(visual_segment)
                current_time += segment_duration
            
            # Create timeline
            timeline = VideoTimeline(
                total_duration=current_time,
                segments=segments,
                audio_track=audio_path,
                background_music=None,
                output_format=config['output_format'],
                resolution=config['resolution'],
                frame_rate=config['frame_rate'],
                metadata={
                    'total_visuals': len(visuals),
                    'composition_config': config,
                    'created_at': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Created video timeline with {len(segments)} segments, total duration: {current_time:.2f}s")
            return timeline
            
        except Exception as e:
            logger.error(f"Error creating video timeline: {e}")
            raise
    
    def _get_transition_in(self, index: int, visual: Dict) -> str:
        """Get transition effect for segment start"""
        if index == 0:
            return 'none'  # First segment has no transition in
        
        # Use visual's transition type or default
        transition_type = visual.get('transition_type', 'fade')
        return self.transition_effects.get(transition_type, 'fade')
    
    def _get_transition_out(self, index: int, visual: Dict, total_visuals: int) -> str:
        """Get transition effect for segment end"""
        if index == total_visuals - 1:
            return 'none'  # Last segment has no transition out
        
        # Use visual's transition type or default
        transition_type = visual.get('transition_type', 'fade')
        return self.transition_effects.get(transition_type, 'fade')
    
    async def _render_video(self, timeline: VideoTimeline, config: Dict) -> str:
        """Render final video using FFmpeg"""
        try:
            logger.info("Starting video rendering with FFmpeg")
            
            # Create temporary working directory
            with tempfile.TemporaryDirectory(dir=self.temp_dir) as temp_dir:
                # Generate FFmpeg command
                ffmpeg_cmd = self._build_ffmpeg_command(timeline, config, temp_dir)
                
                # Execute FFmpeg
                result = await self._execute_ffmpeg(ffmpeg_cmd)
                
                if result['success']:
                    # Move output file to final location
                    output_filename = f"composed_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{config['output_format']}"
                    output_path = os.path.join(self.videos_dir, output_filename)
                    
                    if os.path.exists(result['output_path']):
                        shutil.move(result['output_path'], output_path)
                        logger.info(f"Video rendered successfully: {output_path}")
                        return output_path
                    else:
                        raise FileNotFoundError("FFmpeg output file not found")
                else:
                    raise RuntimeError(f"FFmpeg failed: {result['error']}")
                    
        except Exception as e:
            logger.error(f"Error rendering video: {e}")
            raise
    
    def _build_ffmpeg_command(self, timeline: VideoTimeline, config: Dict, temp_dir: str) -> List[str]:
        """Build FFmpeg command for video composition"""
        try:
            # Very simple FFmpeg command for compatibility
            cmd = ['ffmpeg', '-y']  # Overwrite output files
            
            # Add visual inputs
            for i, segment in enumerate(timeline.segments):
                if segment.visual_path and os.path.exists(segment.visual_path):
                    cmd.extend([
                        '-loop', '1',
                        '-t', str(segment.duration),
                        '-i', segment.visual_path
                    ])
            
            # Add audio input
            if timeline.audio_track and os.path.exists(timeline.audio_track):
                cmd.extend(['-i', timeline.audio_track])
            
            # Simple filter: just scale the visuals
            if len(timeline.segments) > 0:
                scale_filters = []
                for i in range(len(timeline.segments)):
                    scale_filters.append(f"[{i}:v]scale={timeline.resolution[0]}:{timeline.resolution[1]}[v{i}]")
                
                # Concatenate visuals
                concat_inputs = ''.join([f"[v{i}]" for i in range(len(timeline.segments))])
                scale_filters.append(f"{concat_inputs}concat=n={len(timeline.segments)}:v=1:a=0[outv]")
                
                # Add audio if available
                if timeline.audio_track and os.path.exists(timeline.audio_track):
                    audio_idx = len(timeline.segments)
                    scale_filters.append(f"[{audio_idx}:a]aformat=sample_rates=44100:channel_layouts=stereo[audio]")
                    scale_filters.append(f"[outv][audio]concat=n=1:v=1:a=1[final]")
                    final_output = "[final]"
                else:
                    final_output = "[outv]"
                
                scale_filters.append(f"{final_output}null")
                filter_complex = ';'.join(scale_filters)
                cmd.extend(['-filter_complex', filter_complex])
            
            # Basic output settings
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '28',
                '-c:a', 'aac',
                '-b:a', '128k'
            ])
            
            # Output file
            output_path = os.path.join(temp_dir, f"output.{config['output_format']}")
            cmd.append(output_path)
            
            return cmd
            
        except Exception as e:
            logger.error(f"Error building FFmpeg command: {e}")
            raise
    
    def _build_filter_complex(self, timeline: VideoTimeline, config: Dict) -> str:
        """Build complex filter for video composition"""
        try:
            # Simplified filter for compatibility
            filters = []
            
            # Process visual segments with basic scaling
            for i, segment in enumerate(timeline.segments):
                if not segment.visual_path or not os.path.exists(segment.visual_path):
                    continue
                
                input_idx = i + 1  # +1 because input 0 is the black background
                
                # Basic scale filter (more compatible)
                filters.append(f"[{input_idx}:v]scale={timeline.resolution[0]}:{timeline.resolution[1]}[v{i}]")
            
            # Simple concatenation without complex transitions
            if len(timeline.segments) > 1:
                # Create a simple concat filter
                concat_inputs = ''.join([f"[v{i}]" for i in range(len(timeline.segments))])
                filters.append(f"{concat_inputs}concat=n={len(timeline.segments)}:v=1:a=0[outv]")
            else:
                filters.append(f"[v0]copy[outv]")
            
            # Add audio if available
            if timeline.audio_track and os.path.exists(timeline.audio_track):
                # Audio input index should be the number of visual inputs + 1
                audio_input_idx = len(timeline.segments)
                filters.append(f"[{audio_input_idx}:a]aformat=sample_rates=44100:channel_layouts=stereo[audio]")
                filters.append(f"[outv][audio]concat=n=1:v=1:a=1[final]")
                final_output = "[final]"
            else:
                final_output = "[outv]"
            
            # Set output
            filters.append(f"{final_output}null")
            
            return ';'.join(filters)
            
        except Exception as e:
            logger.error(f"Error building filter complex: {e}")
            # Fallback to simple filter
            return "null"
    
    async def _execute_ffmpeg(self, cmd: List[str]) -> Dict:
        """Execute FFmpeg command"""
        try:
            logger.info(f"Executing FFmpeg command: {' '.join(cmd)}")
            
            # Run FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Find output file
                output_path = cmd[-1]  # Last argument is output path
                return {
                    'success': True,
                    'output_path': output_path,
                    'stdout': stdout.decode(),
                    'stderr': stderr.decode()
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode(),
                    'stdout': stdout.decode(),
                    'return_code': process.returncode
                }
                
        except Exception as e:
            logger.error(f"Error executing FFmpeg: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_composition_report(self, timeline: VideoTimeline, video_path: str) -> Dict:
        """Generate composition report"""
        try:
            report = {
                'composition_summary': {
                    'total_duration': timeline.total_duration,
                    'total_segments': len(timeline.segments),
                    'output_format': timeline.output_format,
                    'resolution': timeline.resolution,
                    'frame_rate': timeline.frame_rate
                },
                'segment_breakdown': [],
                'performance_metrics': {
                    'rendering_time': datetime.now().isoformat(),
                    'file_size': os.path.getsize(video_path) if os.path.exists(video_path) else 0,
                    'output_path': video_path
                }
            }
            
            # Add segment details
            for i, segment in enumerate(timeline.segments):
                report['segment_breakdown'].append({
                    'index': i,
                    'start_time': segment.start_time,
                    'end_time': segment.end_time,
                    'duration': segment.duration,
                    'type': segment.segment_type,
                    'transition_in': segment.transition_in,
                    'transition_out': segment.transition_out,
                    'content_type': segment.metadata.get('content_type', 'unknown')
                })
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating composition report: {e}")
            return {'error': str(e)}
    
    async def preview_timeline(self, timeline: VideoTimeline) -> Dict:
        """Generate preview of video timeline"""
        try:
            preview_data = {
                'total_duration': timeline.total_duration,
                'total_segments': len(timeline.segments),
                'segments': []
            }
            
            for i, segment in enumerate(timeline.segments):
                preview_data['segments'].append({
                    'index': i,
                    'start_time': segment.start_time,
                    'duration': segment.duration,
                    'type': segment.segment_type,
                    'content_type': segment.metadata.get('content_type', 'unknown'),
                    'transition_in': segment.transition_in,
                    'transition_out': segment.transition_out
                })
            
            return preview_data
            
        except Exception as e:
            logger.error(f"Error generating timeline preview: {e}")
            return {'error': str(e)}
    
    def get_composition_presets(self) -> Dict:
        """Get available composition presets"""
        return {
            'youtube': {
                'resolution': (1920, 1080),
                'frame_rate': 30,
                'bitrate': '8000k',
                'audio_bitrate': '128k',
                'format': 'mp4'
            },
            'social_media': {
                'resolution': (1080, 1080),
                'frame_rate': 30,
                'bitrate': '4000k',
                'audio_bitrate': '128k',
                'format': 'mp4'
            },
            'presentation': {
                'resolution': (1920, 1080),
                'frame_rate': 25,
                'bitrate': '5000k',
                'audio_bitrate': '96k',
                'format': 'mp4'
            },
            'gif': {
                'resolution': (1280, 720),
                'frame_rate': 15,
                'bitrate': 'N/A',
                'audio_bitrate': 'N/A',
                'format': 'gif'
            }
        }
    
    def validate_composition_config(self, config: Dict) -> Tuple[bool, str]:
        """Validate composition configuration"""
        try:
            required_fields = ['output_format', 'resolution', 'frame_rate']
            
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field: {field}"
            
            # Validate format
            if config['output_format'] not in self.supported_formats:
                return False, f"Unsupported output format: {config['output_format']}"
            
            # Validate resolution
            if not isinstance(config['resolution'], (list, tuple)) or len(config['resolution']) != 2:
                return False, "Invalid resolution format"
            
            # Validate frame rate
            if not isinstance(config['frame_rate'], int) or config['frame_rate'] <= 0:
                return False, "Invalid frame rate"
            
            return True, "Configuration valid"
            
        except Exception as e:
            return False, f"Configuration validation error: {e}" 