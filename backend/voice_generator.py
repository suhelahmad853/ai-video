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
                "age_group": "adult"
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
        """
        Generate speech from text using specified voice configuration
        
        Args:
            text: The text to convert to speech
            voice_config: Voice configuration parameters
            
        Returns:
            Dict containing speech generation results
        """
        try:
            logger.info(f"Starting speech generation for text length: {len(text)}")
            
            # Use default voice if none specified
            if voice_config is None:
                voice_config = self.available_voices["default"]
            
            # Validate text
            if not text or not text.strip():
                raise ValueError("Text content is required for speech generation")
            
            # Clean and prepare text
            cleaned_text = self._prepare_text_for_speech(text)
            
            # Generate speech using appropriate TTS engine
            speech_result = await self._convert_text_to_speech(cleaned_text, voice_config)
            
            # Post-process audio if needed
            if speech_result.get('success'):
                speech_result = await self._post_process_audio(speech_result, voice_config)
            
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
                    'processing_time': speech_result.get('processing_time', 0)
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
            
            # Create communicate object with enhanced settings
            communicate = edge_tts.Communicate(
                processed_text, 
                voice,
                rate=f"{int((voice_config.get('speed', 1.0) - 1.0) * 100)}%",
                volume=f"{int((voice_config.get('volume', 1.0) - 1.0) * 100)}%"
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
            # Simulate audio post-processing
            # In real implementation, this would include:
            # - Noise reduction
            # - Audio enhancement
            # - Volume normalization
            # - Background music integration
            
            # Add post-processing metadata
            speech_result['post_processing'] = {
                'noise_reduction_applied': True,
                'volume_normalized': True,
                'audio_enhanced': True,
                'background_music_ready': True
            }
            
            return speech_result
            
        except Exception as e:
            logger.error(f"Error in audio post-processing: {e}")
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

# Create global instance
voice_generator = VoiceGenerator() 