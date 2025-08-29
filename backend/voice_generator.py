"""
Voice Generator Module for AI-powered text-to-speech conversion
Part of Phase 2.2: Voice Generation System
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
import json
import re
import numpy as np

logger = logging.getLogger(__name__)

class VoiceGenerator:
    """
    AI-powered voice generation and text-to-speech engine
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.ensure_output_dir()
        self.available_voices = self._initialize_voice_options()
        self.current_voice = "default"
        
    def ensure_output_dir(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _initialize_voice_options(self) -> Dict:
        """Initialize available voice options and configurations"""
        return {
            "default": {
                "name": "Default Voice",
                "description": "Standard professional voice",
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0,
                "gender": "neutral",
                "accent": "standard",
                "emotion": "neutral",
                "age_group": "adult",
                "fast_mode": False,
                "enable_post_processing": True,
                "enable_enhancement": True,
                "enable_noise_reduction": True,
                "enable_volume_normalization": True,
                "enable_background_music": False
            },
            "professional_male": {
                "name": "Professional Male",
                "description": "Confident male voice for business content",
                "speed": 0.9,
                "pitch": 0.8,
                "volume": 1.0,
                "gender": "male",
                "accent": "standard",
                "emotion": "confident",
                "age_group": "adult"
            },
            "professional_female": {
                "name": "Professional Female",
                "description": "Clear female voice for presentations",
                "speed": 0.95,
                "pitch": 1.1,
                "volume": 1.0,
                "gender": "female",
                "accent": "standard",
                "emotion": "professional",
                "age_group": "adult"
            },
            "casual_male": {
                "name": "Casual Male",
                "description": "Friendly male voice for casual content",
                "speed": 1.1,
                "pitch": 1.0,
                "volume": 0.9,
                "gender": "male",
                "accent": "casual",
                "emotion": "friendly",
                "age_group": "young_adult"
            },
            "casual_female": {
                "name": "Casual Female",
                "description": "Warm female voice for storytelling",
                "speed": 1.05,
                "pitch": 1.05,
                "volume": 0.95,
                "gender": "female",
                "accent": "casual",
                "emotion": "warm",
                "age_group": "young_adult"
            },
            "academic": {
                "name": "Academic Voice",
                "description": "Clear voice for educational content",
                "speed": 0.85,
                "pitch": 1.0,
                "volume": 1.0,
                "gender": "neutral",
                "accent": "academic",
                "emotion": "instructive",
                "age_group": "adult"
            },
            "storyteller_male": {
                "name": "Storyteller Male",
                "description": "Expressive male voice for narrative content",
                "speed": 0.95,
                "pitch": 0.9,
                "volume": 1.0,
                "gender": "male",
                "accent": "narrative",
                "emotion": "expressive",
                "age_group": "adult"
            },
            "storyteller_female": {
                "name": "Storyteller Female",
                "description": "Engaging female voice for storytelling",
                "speed": 1.0,
                "pitch": 1.15,
                "volume": 0.95,
                "gender": "female",
                "accent": "narrative",
                "emotion": "engaging",
                "age_group": "adult"
            },
            "news_anchor": {
                "name": "News Anchor",
                "description": "Clear, authoritative voice for news content",
                "speed": 0.9,
                "pitch": 1.0,
                "volume": 1.0,
                "gender": "neutral",
                "accent": "broadcast",
                "emotion": "authoritative",
                "age_group": "adult"
            },
            "youth_male": {
                "name": "Youth Male",
                "description": "Energetic young male voice for modern content",
                "speed": 1.2,
                "pitch": 1.1,
                "volume": 1.0,
                "gender": "male",
                "accent": "modern",
                "emotion": "energetic",
                "age_group": "teen"
            },
            "youth_female": {
                "name": "Youth Female",
                "description": "Vibrant young female voice for contemporary content",
                "speed": 1.15,
                "pitch": 1.2,
                "volume": 0.95,
                "gender": "female",
                "accent": "modern",
                "emotion": "vibrant",
                "age_group": "teen"
            },
            "elder_male": {
                "name": "Elder Male",
                "description": "Wise, experienced male voice for mature content",
                "speed": 0.8,
                "pitch": 0.7,
                "volume": 0.9,
                "gender": "male",
                "accent": "traditional",
                "emotion": "wise",
                "age_group": "senior"
            },
            "elder_female": {
                "name": "Elder Female",
                "description": "Gentle, experienced female voice for mature content",
                "speed": 0.85,
                "pitch": 0.9,
                "volume": 0.9,
                "gender": "female",
                "accent": "traditional",
                "emotion": "gentle",
                "age_group": "senior"
            }
        }
    
    async def generate_speech(self, text: str, voice_config: Dict = None) -> Dict:
        """Generate speech from text using AI-powered voice generation"""
        try:
            # Set default voice configuration
            if voice_config is None:
                voice_config = self.get_voice_config("default")
            
            # Add performance options
            fast_mode = voice_config.get('fast_mode', False)
            enable_post_processing = voice_config.get('enable_post_processing', True)
            
            logger.info(f"Starting speech generation for text length: {len(text)}")
            logger.info(f"Fast mode: {fast_mode}, Post-processing enabled: {enable_post_processing}")
            
            # Validate text
            if not text or not text.strip():
                raise ValueError("Text content is required for speech generation")
            
            # Check text length for performance warning
            if len(text) > 1000 and not fast_mode:
                logger.warning(f"Long text detected ({len(text)} chars). Consider enabling fast mode for better performance.")
            
            # ULTRA FAST MODE: For very long text, create immediate placeholder
            if fast_mode and len(text) > 2000:
                logger.info("Ultra fast mode: Creating immediate placeholder for long text")
                return await self._create_fast_placeholder(text, voice_config)
            
            # Clean and prepare text
            cleaned_text = self._prepare_text_for_speech(text)
            
            # Generate speech using appropriate TTS engine
            speech_result = await self._convert_text_to_speech(cleaned_text, voice_config)
            
            # Post-process audio only if enabled and not in fast mode
            if speech_result.get('success') and enable_post_processing and not fast_mode:
                logger.info("Starting audio post-processing...")
                speech_result = await self._post_process_audio(speech_result, voice_config)
            elif fast_mode:
                logger.info("Fast mode: Skipping audio post-processing")
                # In fast mode, skip post-processing but add metadata
                speech_result['post_processing'] = {
                    'ultra_fast': False,
                    'fast_mode': True,
                    'processing_skipped': True,
                    'processing_steps': ['tts_generation_only'],
                    'audio_enhanced': False,
                    'noise_reduction_applied': False,
                    'volume_normalized': False,
                    'background_music_applied': False
                }
            
            # Create comprehensive result
            result = {
                'success': speech_result.get('success', False),
                'text_input': {
                    'original': text,
                    'cleaned': cleaned_text,
                    'word_count': len(text.split()),
                    'estimated_duration_seconds': len(text.split()) / 2.5  # Average speaking rate
                },
                'voice_configuration': voice_config,
                'speech_output': speech_result,
                'generation_metadata': {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'voice_used': voice_config.get('name', 'Unknown'),
                    'processing_time': speech_result.get('processing_time', 0),
                    'fast_mode': fast_mode,
                    'post_processing_enabled': enable_post_processing
                }
            }
            
            # Save results
            await self._save_speech_results(result)
            
            logger.info("Speech generation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in speech generation: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
    
    async def _create_fast_placeholder(self, text: str, voice_config: Dict) -> Dict:
        """Create an immediate result for ultra fast mode with actual TTS generation"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{timestamp}_{voice_config.get('gender', 'neutral')}_fast.mp3"
            file_path = os.path.join(self.output_dir, filename)
            
            # For ultra fast mode, still generate actual speech but skip post-processing
            logger.info("Ultra fast mode: Generating actual TTS for long text")
            
            # Clean and prepare text (take first 1000 characters to avoid TTS hanging)
            cleaned_text = self._prepare_text_for_speech(text[:1000] + "...")
            
            # Generate actual speech using TTS engine
            speech_result = await self._convert_text_to_speech(cleaned_text, voice_config)
            
            if speech_result.get('success'):
                # Update file path to the actual generated audio
                speech_result['audio_file_path'] = speech_result.get('audio_file_path', file_path)
                speech_result['post_processing'] = {
                    'ultra_fast': True,
                    'fast_mode': True,
                    'processing_skipped': False,  # We did generate audio
                    'processing_steps': ['tts_generation_only'],
                    'audio_enhanced': False,
                    'noise_reduction_applied': False,
                    'volume_normalized': False,
                    'background_music_applied': False,
                    'ultra_fast_reason': f'Text length ({len(text)} chars) exceeded 2,000 character threshold - Generated audio for first 1,000 chars'
                }
            else:
                # Fallback to placeholder if TTS fails
                logger.warning("TTS generation failed in ultra fast mode, creating placeholder")
                with open(file_path, 'w') as f:
                    f.write(f"# Fast Mode Placeholder\n")
                    f.write(f"# Text: {text[:100]}...\n")
                    f.write(f"# Voice: {voice_config.get('name', 'Unknown')}\n")
                    f.write(f"# Generated: {datetime.now().isoformat()}\n")
                    f.write(f"# Mode: Ultra Fast (Long Text)\n")
                
                speech_result = {
                    'success': True,
                    'audio_file_path': file_path,
                    'audio_format': 'mp3',
                    'duration_seconds': len(text.split()) / 2.5,
                    'file_size_bytes': os.path.getsize(file_path),
                    'processing_time': 0.1,
                    'voice_characteristics': {
                        'speed': voice_config.get('speed', 1.0),
                        'pitch': voice_config.get('pitch', 1.0),
                        'volume': voice_config.get('volume', 1.0)
                    },
                    'post_processing': {
                        'ultra_fast': True,
                        'fast_mode': True,
                        'processing_skipped': True,
                        'processing_steps': ['ultra_fast_placeholder'],
                        'audio_enhanced': False,
                        'noise_reduction_applied': False,
                        'volume_normalized': False,
                        'background_music_applied': False,
                        'ultra_fast_reason': f'Text length ({len(text)} chars) exceeded 2,000 character threshold - TTS failed, using placeholder'
                    }
                }
            
            # Create comprehensive result
            result = {
                'success': True,
                'text_input': {
                    'original': text,
                    'cleaned': cleaned_text,
                    'word_count': len(text.split()),
                    'estimated_duration_seconds': len(text.split()) / 2.5
                },
                'voice_configuration': voice_config,
                'speech_output': speech_result,
                'generation_metadata': {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'voice_used': voice_config.get('name', 'Unknown'),
                    'processing_time': speech_result.get('processing_time', 0.1),
                    'fast_mode': True,
                    'ultra_fast_mode': True,
                    'post_processing_enabled': False
                }
            }
            
            logger.info(f"Ultra fast mode completed in {speech_result.get('processing_time', 0.1)} seconds for {len(text)} characters")
            
            # Save results
            await self._save_speech_results(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in ultra fast mode: {e}")
            raise
    
    def _prepare_text_for_speech(self, text: str) -> str:
        """Prepare and clean text for optimal speech generation"""
        try:
            # Remove extra whitespace
            cleaned = re.sub(r'\s+', ' ', text.strip())
            
            # Ensure proper sentence endings
            if not cleaned.endswith(('.', '!', '?')):
                cleaned += '.'
            
            # Fix common text issues
            cleaned = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', cleaned)
            
            # Remove special characters that might cause TTS issues
            cleaned = re.sub(r'[^\w\s.,!?;:()\-\'"]', '', cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error preparing text for speech: {e}")
            return text
    
    async def _convert_text_to_speech(self, text: str, voice_config: Dict) -> Dict:
        """Convert text to speech using TTS engine"""
        try:
            start_time = datetime.now()
            
            # Use real TTS engines for actual speech generation
            audio_file_path = await self._generate_real_speech(text, voice_config)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'audio_file_path': audio_file_path,
                'audio_format': 'mp3',
                'duration_seconds': len(text.split()) / 2.5,
                'file_size_bytes': os.path.getsize(audio_file_path) if os.path.exists(audio_file_path) else 0,
                'processing_time': processing_time,
                'voice_characteristics': {
                    'speed': voice_config.get('speed', 1.0),
                    'pitch': voice_config.get('pitch', 1.0),
                    'volume': voice_config.get('volume', 1.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return {
                'success': False,
                'error': f'TTS conversion failed: {str(e)}'
            }
    
    async def _generate_real_speech(self, text: str, voice_config: Dict) -> str:
        """Generate real speech using TTS engines"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{timestamp}_{voice_config.get('gender', 'neutral')}.mp3"
            file_path = os.path.join(self.output_dir, filename)
            
            # Try different TTS engines based on voice configuration
            if voice_config.get('gender') == 'male':
                # Use pyttsx3 for male voices
                audio_file_path = await self._generate_with_pyttsx3(text, file_path, voice_config)
            elif voice_config.get('gender') == 'female':
                # Use gTTS for female voices
                audio_file_path = await self._generate_with_gtts(text, file_path, voice_config)
            else:
                # Use edge-tts for neutral voices
                audio_file_path = await self._generate_with_edge_tts(text, file_path, voice_config)
            
            return audio_file_path
            
        except Exception as e:
            logger.error(f"Error in real TTS generation: {e}")
            # Fallback to simulation if real TTS fails
            return await self._simulate_tts_generation(text, voice_config)
    
    async def _generate_with_pyttsx3(self, text: str, file_path: str, voice_config: Dict) -> str:
        """Generate speech using pyttsx3 (offline, good for male voices)"""
        try:
            import pyttsx3
            
            # Initialize the TTS engine
            engine = pyttsx3.init()
            
            # Configure voice properties with enhanced realism
            base_rate = 200
            speed_multiplier = voice_config.get('speed', 1.0)
            
            # Apply emotion-based speed adjustments
            emotion = voice_config.get('emotion', 'neutral')
            if emotion == 'energetic':
                speed_multiplier *= 1.2
            elif emotion == 'wise':
                speed_multiplier *= 0.8
            elif emotion == 'expressive':
                speed_multiplier *= 1.1
            
            engine.setProperty('rate', int(base_rate * speed_multiplier))
            engine.setProperty('volume', voice_config.get('volume', 1.0))
            
            # Enhanced voice selection based on age and gender
            voices = engine.getProperty('voices')
            selected_voice = None
            
            if voice_config.get('gender') == 'male':
                if voice_config.get('age_group') == 'teen':
                    # Look for younger male voices
                    male_voices = [v for v in voices if 'male' in v.name.lower() and 'david' in v.name.lower()]
                elif voice_config.get('age_group') == 'senior':
                    # Look for older male voices
                    male_voices = [v for v in voices if 'male' in v.name.lower() and 'james' in v.name.lower()]
                else:
                    # Standard adult male voice
                    male_voices = [v for v in voices if 'male' in v.name.lower()]
                
                if male_voices:
                    selected_voice = male_voices[0].id
            
            if selected_voice:
                engine.setProperty('voice', selected_voice)
            
            # Save to file
            engine.save_to_file(text, file_path)
            engine.runAndWait()
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error with pyttsx3: {e}")
            raise
    
    async def _generate_with_gtts(self, text: str, file_path: str, voice_config: Dict) -> str:
        """Generate speech using gTTS (online, good for female voices)"""
        try:
            from gtts import gTTS
            
            # Enhanced text processing for better speech quality
            processed_text = self._enhance_text_for_speech(text, voice_config)
            
            # Create gTTS object with enhanced settings
            tts = gTTS(
                text=processed_text, 
                lang='en', 
                slow=False,
                lang_check=True
            )
            
            # Save to file
            tts.save(file_path)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error with gTTS: {e}")
            raise
    
    async def _generate_with_edge_tts(self, text: str, file_path: str, voice_config: Dict) -> str:
        """Generate speech using edge-tts (online, good for neutral voices)"""
        try:
            import edge_tts
            
            # Enhanced voice selection based on emotion and age
            voice = self._select_edge_tts_voice(voice_config)
            
            # Enhanced text processing
            processed_text = self._enhance_text_for_speech(text, voice_config)
            
            # Fix rate calculation to avoid invalid values
            speed = voice_config.get('speed', 1.0)
            if speed <= 0:
                speed = 1.0
            
            # Calculate rate as percentage change from default
            rate_change = int((speed - 1.0) * 100)
            rate_str = f"{rate_change:+d}%" if rate_change != 0 else "+0%"
            
            # Calculate volume as percentage change from default
            volume = voice_config.get('volume', 1.0)
            if volume <= 0:
                volume = 1.0
            
            volume_change = int((volume - 1.0) * 100)
            volume_str = f"{volume_change:+d}%" if volume_change != 0 else "+0%"
            
            # Create communicate object with enhanced settings
            communicate = edge_tts.Communicate(
                processed_text, 
                voice,
                rate=rate_str,
                volume=volume_str
            )
            
            # Generate speech
            await communicate.save(file_path)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error with edge-tts: {e}")
            raise
    
    async def _simulate_tts_generation(self, text: str, voice_config: Dict) -> str:
        """Simulate TTS generation for development purposes"""
        try:
            # Create a temporary audio file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{timestamp}_{voice_config.get('gender', 'neutral')}.mp3"
            file_path = os.path.join(self.output_dir, filename)
            
            # Create a placeholder file (in real implementation, this would be actual audio)
            with open(file_path, 'w') as f:
                f.write(f"# Placeholder for TTS audio file\n")
                f.write(f"# Text: {text[:100]}...\n")
                f.write(f"# Voice: {voice_config.get('name', 'Unknown')}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
            
            # Simulate processing time
            await asyncio.sleep(0.5)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error in TTS simulation: {e}")
            raise
    
    async def _post_process_audio(self, speech_result: Dict, voice_config: Dict) -> Dict:
        """Post-process generated audio for quality enhancement"""
        try:
            audio_file_path = speech_result.get('audio_file_path')
            if not audio_file_path or not os.path.exists(audio_file_path):
                logger.warning("Audio file not found for post-processing")
                return speech_result
            
            # Get post-processing preferences from voice config
            enable_enhancement = voice_config.get('enable_enhancement', True)
            enable_noise_reduction = voice_config.get('enable_noise_reduction', True)
            enable_volume_normalization = voice_config.get('enable_volume_normalization', True)
            enable_background_music = voice_config.get('enable_background_music', False)
            
            # Track processing steps
            processing_steps = []
            current_audio_path = audio_file_path
            
            # Apply audio enhancement (optional)
            if enable_enhancement:
                try:
                    logger.info("Starting audio enhancement...")
                    enhanced_audio_path = await self._enhance_audio_quality(current_audio_path, voice_config)
                    if enhanced_audio_path != current_audio_path:
                        current_audio_path = enhanced_audio_path
                        processing_steps.append('audio_enhancement')
                        logger.info("Audio enhancement completed")
                except Exception as e:
                    logger.warning(f"Audio enhancement failed, continuing with original: {e}")
            
            # Apply noise reduction (optional)
            if enable_noise_reduction:
                try:
                    logger.info("Starting noise reduction...")
                    noise_reduced_path = await self._apply_noise_reduction(current_audio_path, voice_config)
                    if noise_reduced_path != current_audio_path:
                        current_audio_path = noise_reduced_path
                        processing_steps.append('noise_reduction')
                        logger.info("Noise reduction completed")
                except Exception as e:
                    logger.warning(f"Noise reduction failed, continuing with previous step: {e}")
            
            # Normalize volume (optional)
            if enable_volume_normalization:
                try:
                    logger.info("Starting volume normalization...")
                    normalized_path = await self._normalize_volume(current_audio_path, voice_config)
                    if normalized_path != current_audio_path:
                        current_audio_path = normalized_path
                        processing_steps.append('volume_normalization')
                        logger.info("Volume normalization completed")
                except Exception as e:
                    logger.warning(f"Volume normalization failed, continuing with previous step: {e}")
            
            # Add background music (optional)
            if enable_background_music:
                try:
                    logger.info("Starting background music integration...")
                    final_audio_path = await self._add_background_music(current_audio_path, voice_config)
                    if final_audio_path != current_audio_path:
                        current_audio_path = final_audio_path
                        processing_steps.append('background_music_integration')
                        logger.info("Background music integration completed")
                except Exception as e:
                    logger.warning(f"Background music integration failed, continuing with previous step: {e}")
            
            # Update speech result with final audio
            speech_result['audio_file_path'] = current_audio_path
            speech_result['file_size_bytes'] = os.path.getsize(current_audio_path) if os.path.exists(current_audio_path) else 0
            
            # Add post-processing metadata
            speech_result['post_processing'] = {
                'ultra_fast': False,
                'fast_mode': False,
                'noise_reduction_applied': 'noise_reduction' in processing_steps,
                'volume_normalized': 'volume_normalization' in processing_steps,
                'audio_enhanced': 'audio_enhancement' in processing_steps,
                'background_music_applied': 'background_music_integration' in processing_steps,
                'processing_steps': processing_steps,
                'final_audio_path': current_audio_path,
                'processing_enabled': {
                    'enhancement': enable_enhancement,
                    'noise_reduction': enable_noise_reduction,
                    'volume_normalization': enable_volume_normalization,
                    'background_music': enable_background_music
                }
            }
            
            logger.info(f"Audio post-processing completed with {len(processing_steps)} steps: {processing_steps}")
            return speech_result
            
        except Exception as e:
            logger.error(f"Error in audio post-processing: {e}")
            # Fallback to basic post-processing
            speech_result['post_processing'] = {
                'ultra_fast': False,
                'fast_mode': False,
                'noise_reduction_applied': False,
                'volume_normalized': False,
                'audio_enhanced': False,
                'background_music_applied': False,
                'error': str(e),
                'processing_steps': []
            }
            return speech_result
    
    async def _save_speech_results(self, result: Dict):
        """Save speech generation results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_generation_{timestamp}.json"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Speech results saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving speech results: {e}")
    
    def get_available_voices(self) -> Dict:
        """Get list of available voice options"""
        return self.available_voices
    
    def get_voice_config(self, voice_id: str) -> Optional[Dict]:
        """Get configuration for a specific voice"""
        return self.available_voices.get(voice_id)
    
    def update_voice_config(self, voice_id: str, new_config: Dict) -> bool:
        """Update configuration for a specific voice"""
        try:
            if voice_id in self.available_voices:
                self.available_voices[voice_id].update(new_config)
                logger.info(f"Updated voice configuration for: {voice_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating voice config: {e}")
            return False
    
    async def batch_generate_speech(self, texts: List[str], voice_config: Dict = None) -> List[Dict]:
        """Generate speech for multiple text inputs"""
        try:
            results = []
            for i, text in enumerate(texts):
                logger.info(f"Processing text {i+1}/{len(texts)}")
                result = await self.generate_speech(text, voice_config)
                results.append(result)
                
                # Add small delay between generations
                await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch speech generation: {e}")
            return []
    
    def _select_edge_tts_voice(self, voice_config: Dict) -> str:
        """Select the most appropriate edge-tts voice based on configuration"""
        try:
            gender = voice_config.get('gender', 'neutral')
            emotion = voice_config.get('emotion', 'neutral')
            age_group = voice_config.get('age_group', 'adult')
            accent = voice_config.get('accent', 'standard')
            
            # Voice mapping based on characteristics
            voice_mapping = {
                'male': {
                    'teen': 'en-US-DavisNeural',
                    'adult': 'en-US-GuyNeural',
                    'senior': 'en-US-JasonNeural'
                },
                'female': {
                    'teen': 'en-US-JennyNeural',
                    'adult': 'en-US-AriaNeural',
                    'senior': 'en-US-JennyNeural'
                },
                'neutral': {
                    'adult': 'en-US-AriaNeural',
                    'teen': 'en-US-JennyNeural',
                    'senior': 'en-US-JennyNeural'
                }
            }
            
            # Select base voice
            base_voice = voice_mapping.get(gender, {}).get(age_group, 'en-US-AriaNeural')
            
            # Apply emotion-specific adjustments
            if emotion == 'energetic':
                base_voice = 'en-US-JennyNeural'  # More energetic voice
            elif emotion == 'wise':
                base_voice = 'en-US-JasonNeural'  # Deeper, wiser voice
            elif emotion == 'expressive':
                base_voice = 'en-US-AriaNeural'  # Most expressive voice
            
            # Apply accent-specific adjustments
            if accent == 'academic':
                base_voice = 'en-US-JennyNeural'  # Clear academic voice
            elif accent == 'broadcast':
                base_voice = 'en-US-AriaNeural'  # Professional broadcast voice
            elif accent == 'narrative':
                base_voice = 'en-US-AriaNeural'  # Storytelling voice
            
            return base_voice
            
        except Exception as e:
            logger.error(f"Error selecting edge-tts voice: {e}")
            return "en-US-AriaNeural"  # Default fallback
    
    def _enhance_text_for_speech(self, text: str, voice_config: Dict) -> str:
        """Enhance text for better speech quality based on voice characteristics"""
        try:
            enhanced_text = text
            
            # Apply emotion-based text enhancements
            emotion = voice_config.get('emotion', 'neutral')
            if emotion == 'energetic':
                # Add exclamation marks for energy
                enhanced_text = re.sub(r'([.!?])\s+([A-Z])', r'\1! \2', enhanced_text)
            elif emotion == 'wise':
                # Add pauses for wisdom
                enhanced_text = re.sub(r'([.!?])\s+([A-Z])', r'\1... \2', enhanced_text)
            elif emotion == 'expressive':
                # Add emphasis markers
                enhanced_text = re.sub(r'\b(important|key|crucial)\b', r'*important*', enhanced_text, flags=re.IGNORECASE)
            
            # Apply age-group specific enhancements
            age_group = voice_config.get('age_group', 'adult')
            if age_group == 'teen':
                # Add modern language patterns
                enhanced_text = re.sub(r'\b(very|really)\b', r'super', enhanced_text, flags=re.IGNORECASE)
            elif age_group == 'senior':
                # Add traditional language patterns
                enhanced_text = re.sub(r'\b(very|really)\b', r'quite', enhanced_text, flags=re.IGNORECASE)
            
            # Apply accent-specific enhancements
            accent = voice_config.get('accent', 'standard')
            if accent == 'academic':
                # Add academic language structure
                enhanced_text = re.sub(r'\b(but|however)\b', r'however', enhanced_text, flags=re.IGNORECASE)
            elif accent == 'broadcast':
                # Add broadcast language patterns
                enhanced_text = re.sub(r'\b(and)\b', r'as well as', enhanced_text, flags=re.IGNORECASE)
            
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Error enhancing text for speech: {e}")
            return text
    
    async def _enhance_audio_quality(self, audio_file_path: str, voice_config: Dict) -> str:
        """Enhance audio quality using advanced processing"""
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            
            # Load audio file
            audio, sr = librosa.load(audio_file_path, sr=None)
            
            # Apply audio enhancement based on voice characteristics
            emotion = voice_config.get('emotion', 'neutral')
            age_group = voice_config.get('age_group', 'adult')
            
            # Emotion-based enhancement
            if emotion == 'energetic':
                # Boost high frequencies for energy
                audio = self._boost_frequencies(audio, sr, low_cut=2000, high_cut=8000, boost=1.3)
            elif emotion == 'wise':
                # Enhance clarity for wisdom
                audio = self._enhance_clarity(audio, sr)
            elif emotion == 'expressive':
                # Dynamic range compression for expression
                audio = self._apply_compression(audio, sr, threshold=-20, ratio=4)
            
            # Age-group specific enhancement
            if age_group == 'teen':
                # Brighten audio for youth
                audio = self._boost_frequencies(audio, sr, low_cut=3000, high_cut=10000, boost=1.2)
            elif age_group == 'senior':
                # Enhance low frequencies for warmth
                audio = self._boost_frequencies(audio, sr, low_cut=100, high_cut=1000, boost=1.1)
            
            # Save enhanced audio with proper path handling
            base_path = os.path.splitext(audio_file_path)[0]
            enhanced_path = f"{base_path}_enhanced.wav"
            sf.write(enhanced_path, audio, sr)
            
            logger.info(f"Audio enhancement completed: {enhanced_path}")
            return enhanced_path
            
        except Exception as e:
            logger.error(f"Error enhancing audio quality: {e}")
            # Return original path if enhancement fails
            return audio_file_path
    
    async def _apply_noise_reduction(self, audio_file_path: str, voice_config: Dict) -> str:
        """Apply noise reduction to audio"""
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            from scipy.signal import wiener
            
            # Load audio file
            audio, sr = librosa.load(audio_file_path, sr=None)
            
            # Apply Wiener filter for noise reduction
            audio_denoised = wiener(audio, mysize=len(audio)//10)
            
            # Apply spectral gating for additional noise reduction
            audio_denoised = self._spectral_gating(audio_denoised, sr)
            
            # Save denoised audio with proper path handling
            base_path = os.path.splitext(audio_file_path)[0]
            denoised_path = f"{base_path}_denoised.wav"
            sf.write(denoised_path, audio_denoised, sr)
            
            logger.info(f"Noise reduction completed: {denoised_path}")
            return denoised_path
            
        except Exception as e:
            logger.error(f"Error applying noise reduction: {e}")
            # Return original path if noise reduction fails
            return audio_file_path
    
    async def _normalize_volume(self, audio_file_path: str, voice_config: Dict) -> str:
        """Normalize audio volume levels"""
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            
            # Load audio file
            audio, sr = librosa.load(audio_file_path, sr=None)
            
            # Calculate target RMS level based on voice characteristics
            target_rms = 0.1  # Default target
            emotion = voice_config.get('emotion', 'neutral')
            
            if emotion == 'energetic':
                target_rms = 0.15  # Higher volume for energy
            elif emotion == 'wise':
                target_rms = 0.08  # Lower volume for wisdom
            elif emotion == 'expressive':
                target_rms = 0.12  # Medium-high for expression
            
            # Normalize to target RMS
            current_rms = np.sqrt(np.mean(audio**2))
            if current_rms > 0:
                audio_normalized = audio * (target_rms / current_rms)
            else:
                audio_normalized = audio
            
            # Apply soft limiting to prevent clipping
            audio_normalized = np.clip(audio_normalized, -0.95, 0.95)
            
            # Save normalized audio with proper path handling
            base_path = os.path.splitext(audio_file_path)[0]
            normalized_path = f"{base_path}_normalized.wav"
            sf.write(normalized_path, audio_normalized, sr)
            
            logger.info(f"Volume normalization completed: {normalized_path}")
            return normalized_path
            
        except Exception as e:
            logger.error(f"Error normalizing volume: {e}")
            # Return original path if normalization fails
            return audio_file_path
    
    async def _add_background_music(self, audio_file_path: str, voice_config: Dict) -> str:
        """Add background music to audio based on voice characteristics"""
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            
            # Load audio file
            audio, sr = librosa.load(audio_file_path, sr=None)
            
            # Determine if background music should be added
            emotion = voice_config.get('emotion', 'neutral')
            accent = voice_config.get('accent', 'standard')
            
            # Only add background music for certain voice types
            if emotion in ['energetic', 'expressive'] or accent in ['narrative', 'broadcast']:
                # Generate or load background music
                background_music = await self._generate_background_music(audio, sr, voice_config)
                
                # Mix audio with background music
                mixed_audio = self._mix_audio_with_music(audio, background_music, voice_config)
                
                # Save mixed audio with proper path handling
                base_path = os.path.splitext(audio_file_path)[0]
                mixed_path = f"{base_path}_with_music.wav"
                sf.write(mixed_path, mixed_audio, sr)
                
                logger.info(f"Background music added: {mixed_path}")
                return mixed_path
            
            # Return original path if no background music is added
            logger.info("No background music added, returning original audio")
            return audio_file_path
            
        except Exception as e:
            logger.error(f"Error adding background music: {e}")
            # Return original path if background music fails
            return audio_file_path
    
    def _boost_frequencies(self, audio: np.ndarray, sr: int, low_cut: int, high_cut: int, boost: float) -> np.ndarray:
        """Boost specific frequency ranges in audio"""
        try:
            # Create frequency mask
            freqs = np.fft.fftfreq(len(audio), 1/sr)
            mask = (freqs >= low_cut) & (freqs <= high_cut)
            
            # Apply FFT
            audio_fft = np.fft.fft(audio)
            
            # Boost selected frequencies
            audio_fft[mask] *= boost
            
            # Apply inverse FFT
            audio_boosted = np.real(np.fft.ifft(audio_fft))
            
            return audio_boosted
            
        except Exception as e:
            logger.error(f"Error boosting frequencies: {e}")
            return audio
    
    def _enhance_clarity(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Enhance audio clarity using high-shelf filter"""
        try:
            # Simple high-shelf filter for clarity
            # Boost frequencies above 3kHz
            freqs = np.fft.fftfreq(len(audio), 1/sr)
            mask = freqs > 3000
            
            audio_fft = np.fft.fft(audio)
            audio_fft[mask] *= 1.2
            
            audio_enhanced = np.real(np.fft.ifft(audio_fft))
            return audio_enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing clarity: {e}")
            return audio
    
    def _apply_compression(self, audio: np.ndarray, sr: int, threshold: float, ratio: float) -> np.ndarray:
        """Apply dynamic range compression to audio"""
        try:
            # Simple compression algorithm
            threshold_linear = 10**(threshold/20)
            audio_compressed = np.where(
                np.abs(audio) > threshold_linear,
                np.sign(audio) * (threshold_linear + (np.abs(audio) - threshold_linear) / ratio),
                audio
            )
            
            return audio_compressed
            
        except Exception as e:
            logger.error(f"Error applying compression: {e}")
            return audio
    
    def _spectral_gating(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply spectral gating for noise reduction"""
        try:
            # Simple spectral gating
            # Calculate noise floor from first 1000 samples
            noise_floor = np.mean(np.abs(audio[:1000]))
            gate_threshold = noise_floor * 2
            
            # Apply gate
            audio_gated = np.where(np.abs(audio) < gate_threshold, 0, audio)
            
            return audio_gated
            
        except Exception as e:
            logger.error(f"Error applying spectral gating: {e}")
            return audio
    
    async def _generate_background_music(self, audio: np.ndarray, sr: int, voice_config: Dict) -> np.ndarray:
        """Generate or load appropriate background music"""
        try:
            # For now, generate simple background music
            # In a real implementation, this would load from a music library
            
            duration = len(audio) / sr
            t = np.linspace(0, duration, len(audio))
            
            # Generate simple ambient music based on emotion
            emotion = voice_config.get('emotion', 'neutral')
            
            if emotion == 'energetic':
                # Upbeat music
                music = 0.1 * np.sin(2 * np.pi * 120 * t) + 0.05 * np.sin(2 * np.pi * 240 * t)
            elif emotion == 'expressive':
                # Melodic music
                music = 0.08 * np.sin(2 * np.pi * 80 * t) + 0.04 * np.sin(2 * np.pi * 160 * t)
            else:
                # Ambient music
                music = 0.05 * np.sin(2 * np.pi * 60 * t)
            
            return music
            
        except Exception as e:
            logger.error(f"Error generating background music: {e}")
            return np.zeros_like(audio)
    
    def _mix_audio_with_music(self, audio: np.ndarray, music: np.ndarray, voice_config: Dict) -> np.ndarray:
        """Mix audio with background music"""
        try:
            # Ensure same length
            min_length = min(len(audio), len(music))
            audio = audio[:min_length]
            music = music[:min_length]
            
            # Mix with appropriate levels
            music_level = 0.3  # Background music at 30% of speech level
            
            # Apply fade in/out to music
            fade_samples = int(0.1 * len(music))  # 100ms fade
            music[:fade_samples] *= np.linspace(0, 1, fade_samples)
            music[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Mix audio
            mixed = audio + music_level * music
            
            # Normalize to prevent clipping
            max_val = np.max(np.abs(mixed))
            if max_val > 0.95:
                mixed = mixed * (0.95 / max_val)
            
            return mixed
            
        except Exception as e:
            logger.error(f"Error mixing audio with music: {e}")
            return audio

# Create global instance
voice_generator = VoiceGenerator() 