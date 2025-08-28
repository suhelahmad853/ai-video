"""
Video Processor Module for AI Video Creator Tool
Handles YouTube video downloads, validation, and basic processing
"""

import os
import re
import asyncio
import logging
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import requests
import yt_dlp
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """Handles video processing operations including YouTube downloads"""
    
    def __init__(self, download_dir: str = "temp", max_file_size: int = 1024 * 1024 * 1024):  # 1GB default
        self.download_dir = Path(download_dir)
        self.max_file_size = max_file_size
        self.download_dir.mkdir(exist_ok=True)
        
        # Also ensure an output directory exists for metadata
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options
        self.ydl_opts = {
            # Don't specify format - let yt-dlp choose the best available formats automatically
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'writeinfojson': False,  # Disable for now to avoid issues
            'writesubtitles': False,  # Disable for now to avoid issues
            'writeautomaticsub': False,  # Disable for now to avoid issues
            'subtitleslangs': ['en'],
            'ignoreerrors': True,  # Enable to handle format issues gracefully
            'no_check_certificate': True,  # Handle SSL issues
            'extractor_retries': 3,  # Retry extraction
        }
    
    def validate_youtube_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate if the provided URL is a valid YouTube URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Basic URL validation
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"
            
            # Check if it's a YouTube domain
            youtube_domains = [
                'youtube.com', 'www.youtube.com', 'm.youtube.com',
                'youtu.be', 'www.youtu.be'
            ]
            
            if parsed.netloc not in youtube_domains:
                return False, "URL is not from YouTube"
            
            # Extract video ID
            video_id = self._extract_video_id(url)
            if not video_id:
                return False, "Could not extract video ID from URL"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating YouTube URL: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        # Common YouTube URL patterns
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def get_video_info(self, url: str) -> Dict:
        """
        Get video information without downloading - Enhanced version
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            Dict: Video information
        """
        try:
            # Strategy 1: Try to get full info with best quality
            try:
                full_opts = {
                    # Don't specify format - let yt-dlp choose the best available formats automatically
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'ignoreerrors': True,
                    'writesubtitles': False,
                    'writeautomaticsub': False,
                    'writeinfojson': False,
                    'no_check_certificate': True,
                    'extractor_retries': 3,
                }
                
                with yt_dlp.YoutubeDL(full_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info and info.get('title'):
                        logger.info(f"Full video info extracted successfully: {info.get('title')}")
                        
                        # Extract comprehensive information
                        video_info = {
                            'title': info.get('title', 'Unknown Title'),
                            'duration': info.get('duration', 0),
                            'uploader': info.get('uploader', 'Unknown'),
                            'view_count': info.get('view_count', 0),
                            'like_count': info.get('like_count', 0),
                            'description': info.get('description', '')[:500] if info.get('description') else '',
                            'thumbnail': info.get('thumbnail', ''),
                            'formats': [],
                            'subtitles': {},
                            'automatic_captions': {},
                            'status': 'full_info_extracted',
                            'real_data': True
                        }
                        
                        # Get available formats
                        if 'formats' in info:
                            for fmt in info['formats']:
                                if fmt.get('height') and fmt.get('ext'):
                                    video_info['formats'].append({
                                        'format_id': fmt.get('format_id', ''),
                                        'ext': fmt.get('ext', ''),
                                        'height': fmt.get('height', 0),
                                        'filesize': fmt.get('filesize', 0),
                                        'vcodec': fmt.get('vcodec', ''),
                                        'acodec': fmt.get('acodec', ''),
                                    })
                        
                        return video_info
                        
            except Exception as full_error:
                logger.warning(f"Full info extraction failed: {full_error}")
            
            # Strategy 2: Try basic info extraction
            try:
                basic_opts = {
                    # Don't specify format - let yt-dlp choose the best available formats automatically
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                    'ignoreerrors': True,
                    'no_check_certificate': True,
                    'extractor_retries': 3,
                }
                
                with yt_dlp.YoutubeDL(basic_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info:
                        logger.info(f"Basic video info extracted: {info.get('title', 'Unknown')}")
                        
                        video_info = {
                            'title': info.get('title', 'Unknown Title'),
                            'duration': info.get('duration', 0),
                            'uploader': info.get('uploader', 'Unknown'),
                            'view_count': info.get('view_count', 0),
                            'like_count': info.get('like_count', 0),
                            'description': info.get('description', '')[:500] if info.get('description') else '',
                            'thumbnail': info.get('thumbnail', ''),
                            'formats': [],
                            'subtitles': {},
                            'automatic_captions': {},
                            'status': 'basic_info_extracted',
                            'real_data': True
                        }
                        
                        return video_info
                        
            except Exception as basic_error:
                logger.warning(f"Basic info extraction failed: {basic_error}")
            
            # Strategy 3: Try with age restriction bypass
            try:
                age_bypass_opts = {
                    # Don't specify format - let yt-dlp choose the best available formats automatically
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                    'ignoreerrors': True,
                    'no_check_certificate': True,
                    'extractor_retries': 3,
                    'cookiesfrombrowser': ('chrome',),  # Try to use browser cookies
                }
                
                with yt_dlp.YoutubeDL(age_bypass_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info:
                        logger.info(f"Age-restricted video info extracted: {info.get('title', 'Unknown')}")
                        
                        video_info = {
                            'title': info.get('title', 'Unknown Title'),
                            'duration': info.get('duration', 0),
                            'uploader': info.get('uploader', 'Unknown'),
                            'view_count': info.get('view_count', 0),
                            'like_count': info.get('like_count', 0),
                            'description': info.get('description', '')[:500] if info.get('description') else '',
                            'thumbnail': info.get('thumbnail', ''),
                            'formats': [],
                            'subtitles': {},
                            'automatic_captions': {},
                            'status': 'age_restricted_info_extracted',
                            'real_data': True,
                            'note': 'Video may be age-restricted or region-blocked'
                        }
                        
                        return video_info
                        
            except Exception as age_bypass_error:
                logger.warning(f"Age bypass extraction failed: {age_bypass_error}")
            
            # Strategy 4: Fallback to URL-based info
            video_id = self._extract_video_id(url)
            if video_id:
                logger.warning(f"Using fallback info for video {video_id}")
                return {
                    'title': f'Video {video_id}',
                    'duration': 0,
                    'uploader': 'Unknown',
                    'view_count': 0,
                    'like_count': 0,
                    'description': '',
                    'thumbnail': '',
                    'formats': [],
                    'subtitles': {},
                    'automatic_captions': {},
                    'status': 'url_only',
                    'video_id': video_id,
                    'note': 'Limited information due to extraction issues. Video may be age-restricted, region-blocked, or have other restrictions.',
                    'real_data': False,
                    'restriction_type': 'unknown'
                }
            else:
                raise Exception("Could not extract any video information")
                
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise Exception(f"Failed to get video information: {str(e)}")
    
    async def check_video_restrictions(self, url: str) -> Dict:
        """
        Check if a video has restrictions that prevent normal processing
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            Dict: Restriction information and recommendations
        """
        try:
            video_id = self._extract_video_id(url)
            if not video_id:
                return {
                    'restricted': True,
                    'reason': 'Invalid video ID',
                    'recommendation': 'Check if the URL is correct'
                }
            
            # Try to get video info using the main method
            try:
                video_info = await self.get_video_info(url)
                
                if video_info and video_info.get('real_data', False):
                    # Video info was successfully extracted
                    return {
                        'restricted': False,
                        'reason': 'No restrictions detected',
                        'video_id': video_id,
                        'title': video_info.get('title', 'Unknown'),
                        'status': video_info.get('status', 'unknown')
                    }
                else:
                    # Limited info available
                    return {
                        'restricted': True,
                        'reason': 'Limited video information available',
                        'note': video_info.get('note', 'No additional information'),
                        'recommendation': 'Video may be age-restricted, region-blocked, or have other access limitations',
                        'video_id': video_id,
                        'title': video_info.get('title', 'Unknown')
                    }
                            
            except Exception as e:
                # If we can't get info, assume it's restricted
                return {
                    'restricted': True,
                    'reason': 'Cannot extract video information',
                    'error': str(e),
                    'recommendation': 'Video may be region-blocked, age-restricted, or have other access limitations',
                    'video_id': video_id
                }
                
        except Exception as e:
            logger.error(f"Error checking video restrictions: {e}")
            return {
                'restricted': True,
                'reason': 'Error during restriction check',
                'error': str(e),
                'recommendation': 'Try a different video or check your internet connection'
            }
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string to be safe for filenames."""
        try:
            sanitized = re.sub(r'[^a-zA-Z0-9\-_\. ]+', '', name)
            sanitized = sanitized.strip().replace(' ', '_')
            return sanitized[:120] if sanitized else f"video_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        except Exception:
            return f"video_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    async def extract_video_metadata(self, url: str, save_to_file: bool = True) -> Dict:
        """
        Extract detailed video metadata and optionally save as JSON (Phase 1.2.4)
        
        Args:
            url (str): YouTube video URL
            save_to_file (bool): Whether to persist metadata to output directory
        
        Returns:
            Dict: Metadata including optional file path
        """
        try:
            # Validate URL
            is_valid, error_msg = self.validate_youtube_url(url)
            if not is_valid:
                raise Exception(error_msg)
            
            # Pull info using existing method
            info = await self.get_video_info(url)
            
            # Enrich/normalize metadata
            video_id = self._extract_video_id(url)
            normalized = {
                'video_id': video_id,
                'source_url': url,
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'duration_seconds': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'thumbnail': info.get('thumbnail', ''),
                'has_subtitles': bool(info.get('subtitles')),
                'has_automatic_captions': bool(info.get('automatic_captions')),
                'formats': info.get('formats', []),
                'description': info.get('description', ''),
                'status': info.get('status', 'unknown'),
                'real_data': info.get('real_data', False),
                'extracted_at_utc': datetime.utcnow().isoformat() + 'Z'
            }
            
            saved_path = None
            if save_to_file:
                base_name = self._sanitize_filename(normalized.get('title') or (video_id or 'video'))
                filename = f"{base_name}__{video_id or 'unknown'}.metadata.json"
                saved_path = self.output_dir / filename
                with open(saved_path, 'w', encoding='utf-8') as f:
                    json.dump(normalized, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'metadata': normalized,
                'saved': bool(saved_path),
                'saved_path': str(saved_path) if saved_path else None,
                'message': 'Video metadata extracted successfully'
            }
        except Exception as e:
            logger.error(f"Error extracting video metadata: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Video metadata extraction failed: {str(e)}'
            }
    
    async def analyze_video_content(self, url: str, quality: str = '720p') -> Dict:
        """
        Analyze YouTube video content for AI transformation (Phase 1.2.2)
        
        Args:
            url (str): YouTube video URL
            quality (str): Preferred quality for analysis
            
        Returns:
            Dict: Content analysis results for AI transformation
        """
        try:
            # Validate URL first
            is_valid, error_msg = self.validate_youtube_url(url)
            if not is_valid:
                raise Exception(error_msg)
            
            video_id = self._extract_video_id(url)
            logger.info(f"Starting content analysis for video: {url}")
            
            # Get comprehensive video information
            video_info = await self.get_video_info(url)
            
            # Analyze content for AI transformation
            content_analysis = {
                'video_id': video_id,
                'url': url,
                'quality': quality,
                'analysis_status': 'ready_for_audio_processing',
                'content_summary': {
                    'title': video_info.get('title', 'Unknown'),
                    'duration': video_info.get('duration', 0),
                    'uploader': video_info.get('uploader', 'Unknown'),
                    'view_count': video_info.get('view_count', 0),
                    'like_count': video_info.get('like_count', 0),
                    'description_length': len(video_info.get('description', '')),
                    'has_subtitles': bool(video_info.get('subtitles')),
                    'has_automatic_captions': bool(video_info.get('automatic_captions')),
                },
                'audio_processing_ready': {
                    'content_available': True,
                    'text_content': video_info.get('description', ''),
                    'metadata_complete': video_info.get('real_data', False),
                    'processing_complexity': 'medium' if video_info.get('duration', 0) > 300 else 'low',
                    'audio_extraction_needed': True,
                    'estimated_audio_time': '2-5 minutes'
                },
                'next_phase': 'audio_extraction_and_analysis',
                'estimated_processing_time': '5-15 minutes',
                'compliance_notes': 'Content analysis complete. Ready for audio processing phase.',
                'video_info': video_info
            }
            
            logger.info(f"Content analysis completed for video {video_id}")
            return content_analysis
                
        except Exception as e:
            logger.error(f"Error in content analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Content analysis failed: {str(e)}',
                'analysis_status': 'failed'
            }
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Clean up temporary files older than specified age
        
        Args:
            max_age_hours (int): Maximum age of files in hours
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.download_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        logger.info(f"Cleaned up old file: {file_path.name}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
    
    def get_download_progress(self) -> Dict:
        """
        Get current download progress information
        
        Returns:
            Dict: Progress information
        """
        try:
            temp_files = list(self.download_dir.iterdir())
            total_size = sum(f.stat().st_size for f in temp_files if f.is_file())
            
            return {
                'temp_files_count': len(temp_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'download_dir': str(self.download_dir)
            }
            
        except Exception as e:
            logger.error(f"Error getting download progress: {e}")
            return {'error': str(e)}

# Create a global instance
video_processor = VideoProcessor() 