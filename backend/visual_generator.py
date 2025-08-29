"""
Visual Content Generator Module
Handles creation of images, slides, and visual content from text input
Optimized for long videos with efficient processing and memory management
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import asyncio
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisualContent:
    """Data class for visual content items"""
    content_type: str  # 'slide', 'image', 'graphic'
    text_content: str
    visual_path: str
    duration_seconds: float
    transition_type: str
    metadata: Dict

class VisualGenerator:
    """Generates visual content from text input, optimized for long videos"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.visuals_dir = os.path.join(output_dir, "visuals")
        self.slides_dir = os.path.join(output_dir, "slides")
        self.graphics_dir = os.path.join(output_dir, "graphics")
        
        # Create output directories
        os.makedirs(self.visuals_dir, exist_ok=True)
        os.makedirs(self.slides_dir, exist_ok=True)
        os.makedirs(self.graphics_dir, exist_ok=True)
        
        # Visual content templates and styles
        self.slide_templates = self._initialize_slide_templates()
        self.color_schemes = self._initialize_color_schemes()
        self.font_configs = self._initialize_font_configs()
        
        # Performance optimization settings
        self.max_concurrent_generation = 3  # Limit concurrent image generation
        self.batch_size = 10  # Process content in batches for long videos
        self.cache_enabled = True  # Enable caching for repeated content
        
        logger.info("Visual Generator initialized with optimization for long videos")
    
    def _initialize_slide_templates(self) -> Dict:
        """Initialize slide templates for different content types"""
        return {
            'title': {
                'background_color': (25, 118, 210),
                'text_color': (255, 255, 255),
                'font_size': 48,
                'layout': 'centered',
                'padding': 100
            },
            'content': {
                'background_color': (255, 255, 255),
                'text_color': (33, 33, 33),
                'font_size': 32,
                'layout': 'left_aligned',
                'padding': 80
            },
            'bullet': {
                'background_color': (245, 245, 245),
                'text_color': (33, 33, 33),
                'font_size': 28,
                'layout': 'bullet_points',
                'padding': 60
            },
            'quote': {
                'background_color': (76, 175, 80),
                'text_color': (255, 255, 255),
                'font_size': 36,
                'layout': 'centered_quote',
                'padding': 120
            },
            'summary': {
                'background_color': (156, 39, 176),
                'text_color': (255, 255, 255),
                'font_size': 40,
                'layout': 'centered',
                'padding': 90
            }
        }
    
    def _initialize_color_schemes(self) -> Dict:
        """Initialize color schemes for visual consistency"""
        return {
            'professional': {
                'primary': (25, 118, 210),
                'secondary': (156, 39, 176),
                'accent': (76, 175, 80),
                'background': (255, 255, 255),
                'text': (33, 33, 33)
            },
            'modern': {
                'primary': (233, 30, 99),
                'secondary': (156, 39, 176),
                'accent': (255, 193, 7),
                'background': (18, 18, 18),
                'text': (255, 255, 255)
            },
            'minimal': {
                'primary': (0, 0, 0),
                'secondary': (128, 128, 128),
                'accent': (200, 200, 200),
                'background': (255, 255, 255),
                'text': (0, 0, 0)
            }
        }
    
    def _initialize_font_configs(self) -> Dict:
        """Initialize font configurations for different text sizes"""
        return {
            'title': {'size': 48, 'weight': 'bold'},
            'heading': {'size': 36, 'weight': 'bold'},
            'subheading': {'size': 28, 'weight': 'semibold'},
            'body': {'size': 24, 'weight': 'normal'},
            'caption': {'size': 18, 'weight': 'normal'}
        }
    
    async def generate_visual_content(self, text_content: str, content_type: str = 'auto', 
                                    style_preferences: Dict = None) -> List[VisualContent]:
        """
        Generate visual content from text input, optimized for long videos
        
        Args:
            text_content: The text to convert to visual content
            content_type: Type of visual content ('auto', 'slide', 'image', 'graphic')
            style_preferences: User preferences for visual style
            
        Returns:
            List of VisualContent objects
        """
        try:
            logger.info(f"Starting visual content generation for {len(text_content)} characters")
            
            # Optimize for long content
            if len(text_content) > 5000:
                logger.info("Long content detected, using batch processing optimization")
                return await self._generate_long_content_visuals(text_content, content_type, style_preferences)
            else:
                return await self._generate_standard_visuals(text_content, content_type, style_preferences)
                
        except Exception as e:
            logger.error(f"Error in visual content generation: {e}")
            return []
    
    async def _generate_long_content_visuals(self, text_content: str, content_type: str, 
                                           style_preferences: Dict) -> List[VisualContent]:
        """Generate visuals for long content using batch processing"""
        try:
            # Split content into manageable chunks
            content_chunks = self._split_content_into_chunks(text_content)
            logger.info(f"Split long content into {len(content_chunks)} chunks for batch processing")
            
            # Process chunks in batches to avoid memory issues
            all_visuals = []
            for i in range(0, len(content_chunks), self.batch_size):
                batch = content_chunks[i:i + self.batch_size]
                logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(content_chunks) + self.batch_size - 1)//self.batch_size}")
                
                # Process batch concurrently with limited concurrency
                batch_visuals = await self._process_content_batch(batch, content_type, style_preferences)
                all_visuals.extend(batch_visuals)
                
                # Small delay between batches to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(all_visuals)} visual items for long content")
            return all_visuals
            
        except Exception as e:
            logger.error(f"Error in long content visual generation: {e}")
            return []
    
    async def _generate_standard_visuals(self, text_content: str, content_type: str, 
                                       style_preferences: Dict) -> List[VisualContent]:
        """Generate visuals for standard-length content"""
        try:
            if content_type == 'auto':
                content_type = self._determine_content_type(text_content)
            
            if content_type == 'slide':
                return await self._generate_slides(text_content, style_preferences)
            elif content_type == 'image':
                return await self._generate_images(text_content, style_preferences)
            elif content_type == 'graphic':
                return await self._generate_graphics(text_content, style_preferences)
            else:
                logger.warning(f"Unknown content type: {content_type}, defaulting to slides")
                return await self._generate_slides(text_content, style_preferences)
                
        except Exception as e:
            logger.error(f"Error in standard visual generation: {e}")
            return []
    
    def _split_content_into_chunks(self, text_content: str, max_chunk_size: int = 2000) -> List[str]:
        """Split long content into manageable chunks for processing"""
        chunks = []
        sentences = text_content.split('. ')
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _process_content_batch(self, content_chunks: List[str], content_type: str, 
                                   style_preferences: Dict) -> List[VisualContent]:
        """Process a batch of content chunks concurrently"""
        try:
            # Create semaphore to limit concurrent processing
            semaphore = asyncio.Semaphore(self.max_concurrent_generation)
            
            async def process_chunk(chunk: str) -> Optional[VisualContent]:
                async with semaphore:
                    try:
                        if content_type == 'auto':
                            # Auto-detect content type for each chunk
                            detected_type = self._determine_content_type(chunk)
                            if detected_type == 'slide':
                                return await self._create_single_slide(chunk, style_preferences)
                            else:
                                return await self._create_single_visual(chunk, detected_type, style_preferences)
                        elif content_type == 'slide':
                            return await self._create_single_slide(chunk, style_preferences)
                        else:
                            return await self._create_single_visual(chunk, content_type, style_preferences)
                    except Exception as e:
                        logger.error(f"Error processing chunk: {e}")
                        return None
            
            # Process chunks concurrently
            tasks = [process_chunk(chunk) for chunk in content_chunks]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out None results and exceptions
            valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return []
    
    def _determine_content_type(self, text_content: str) -> str:
        """Automatically determine the best content type based on text characteristics"""
        word_count = len(text_content.split())
        
        if word_count < 50:
            return 'slide'  # Use slide for title-like content
        elif word_count < 200:
            return 'slide'
        elif word_count < 500:
            return 'graphic'
        else:
            return 'slide'  # Default to slides for longer content
    
    async def _generate_slides(self, text_content: str, style_preferences: Dict) -> List[VisualContent]:
        """Generate slides from text content"""
        try:
            # Split content into slide-sized chunks
            slide_chunks = self._create_slide_chunks(text_content)
            slides = []
            
            for i, chunk in enumerate(slide_chunks):
                slide = await self._create_single_slide(chunk, style_preferences, slide_number=i+1)
                if slide:
                    slides.append(slide)
            
            logger.info(f"Generated {len(slides)} slides from content")
            return slides
            
        except Exception as e:
            logger.error(f"Error generating slides: {e}")
            return []
    
    def _create_slide_chunks(self, text_content: str, max_words_per_slide: int = 100) -> List[str]:
        """Create slide-sized chunks from text content"""
        words = text_content.split()
        chunks = []
        
        for i in range(0, len(words), max_words_per_slide):
            chunk_words = words[i:i + max_words_per_slide]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
        
        return chunks
    
    async def _create_single_slide(self, text_content: str, style_preferences: Dict, 
                                 slide_number: int = 1) -> Optional[VisualContent]:
        """Create a single slide from text content"""
        try:
            # Determine slide template based on content
            template_type = self._select_slide_template(text_content)
            template = self.slide_templates[template_type]
            
            # Create slide image
            slide_path = await self._render_slide_image(text_content, template, style_preferences, slide_number)
            
            if slide_path:
                return VisualContent(
                    content_type='slide',
                    text_content=text_content,
                    visual_path=slide_path,
                    duration_seconds=self._calculate_slide_duration(text_content),
                    transition_type='fade',
                    metadata={
                        'template_type': template_type,
                        'slide_number': slide_number,
                        'word_count': len(text_content.split()),
                        'generated_at': datetime.now().isoformat()
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating slide: {e}")
            return None
    
    def _select_slide_template(self, text_content: str) -> str:
        """Select appropriate slide template based on content"""
        text_lower = text_content.lower()
        word_count = len(text_content.split())
        
        if word_count < 20:
            return 'title'
        elif any(word in text_lower for word in ['•', '-', '1.', '2.', '3.']):
            return 'bullet'
        elif any(word in text_lower for word in ['"', '"', 'quote', 'said']):
            return 'quote'
        elif word_count > 150:
            return 'summary'
        else:
            return 'content'
    
    async def _render_slide_image(self, text_content: str, template: Dict, 
                                style_preferences: Dict, slide_number: int) -> Optional[str]:
        """Render slide image using PIL"""
        try:
            # Create image with template dimensions
            width, height = 1920, 1080  # HD resolution
            image = Image.new('RGB', (width, height), template['background_color'])
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fallback to default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", template['font_size'])
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", template['font_size'])
                except:
                    font = ImageFont.load_default()
            
            # Apply text layout based on template
            if template['layout'] == 'centered':
                self._draw_centered_text(draw, text_content, font, template['text_color'], width, height, template['padding'])
            elif template['layout'] == 'left_aligned':
                self._draw_left_aligned_text(draw, text_content, font, template['text_color'], width, height, template['padding'])
            elif template['layout'] == 'bullet_points':
                self._draw_bullet_points(draw, text_content, font, template['text_color'], width, height, template['padding'])
            elif template['layout'] == 'centered_quote':
                self._draw_quote_text(draw, text_content, font, template['text_color'], width, height, template['padding'])
            
            # Add slide number
            self._add_slide_number(draw, slide_number, width, height)
            
            # Save slide
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"slide_{timestamp}_{slide_number:03d}.png"
            slide_path = os.path.join(self.slides_dir, filename)
            image.save(slide_path, 'PNG', optimize=True)
            
            logger.info(f"Slide {slide_number} created: {slide_path}")
            return slide_path
            
        except Exception as e:
            logger.error(f"Error rendering slide image: {e}")
            return None
    
    def _draw_centered_text(self, draw: ImageDraw, text: str, font: ImageFont, color: Tuple, 
                           width: int, height: int, padding: int):
        """Draw centered text on image"""
        # Wrap text to fit width
        lines = self._wrap_text(text, font, width - 2 * padding)
        
        # Calculate total text height - use textbbox for modern PIL versions
        try:
            bbox = font.getbbox("A")
            line_height = bbox[3] - bbox[1] + 10
        except AttributeError:
            # Fallback for older PIL versions
            line_height = font.getsize("A")[1] + 10
        
        total_height = len(lines) * line_height
        
        # Start position (center vertically)
        start_y = (height - total_height) // 2
        
        # Draw each line
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + i * line_height
            draw.text((x, y), line, fill=color, font=font)
    
    def _draw_left_aligned_text(self, draw: ImageDraw, text: str, font: ImageFont, color: Tuple, 
                               width: int, height: int, padding: int):
        """Draw left-aligned text on image"""
        lines = self._wrap_text(text, font, width - 2 * padding)
        
        # Calculate line height - use textbbox for modern PIL versions
        try:
            bbox = font.getbbox("A")
            line_height = bbox[3] - bbox[1] + 10
        except AttributeError:
            # Fallback for older PIL versions
            line_height = font.getsize("A")[1] + 10
        
        for i, line in enumerate(lines):
            y = padding + i * line_height
            if y + line_height < height - padding:
                draw.text((padding, y), line, fill=color, font=font)
    
    def _draw_bullet_points(self, draw: ImageDraw, text: str, font: ImageFont, color: Tuple, 
                           width: int, height: int, padding: int):
        """Draw bullet points text on image"""
        # Split text into bullet points
        points = [point.strip() for point in text.split('\n') if point.strip()]
        
        # Calculate line height - use textbbox for modern PIL versions
        try:
            bbox = font.getbbox("A")
            line_height = bbox[3] - bbox[1] + 15
        except AttributeError:
            # Fallback for older PIL versions
            line_height = font.getsize("A")[1] + 15
        
        start_y = padding
        
        for i, point in enumerate(points):
            y = start_y + i * line_height
            if y + line_height < height - padding:
                # Draw bullet
                bullet_x = padding
                bullet_y = y + line_height // 2
                draw.ellipse([bullet_x, bullet_y - 3, bullet_x + 6, bullet_y + 3], fill=color)
                
                # Draw text
                text_x = padding + 20
                draw.text((text_x, y), point, fill=color, font=font)
    
    def _draw_quote_text(self, draw: ImageDraw, text: str, font: ImageFont, color: Tuple, 
                         width: int, height: int, padding: int):
        """Draw quote text on image"""
        # Add quote marks
        quote_text = f'"{text}"'
        lines = self._wrap_text(quote_text, font, width - 2 * padding)
        
        # Calculate line height - use textbbox for modern PIL versions
        try:
            bbox = font.getbbox("A")
            line_height = bbox[3] - bbox[1] + 10
        except AttributeError:
            # Fallback for older PIL versions
            line_height = font.getsize("A")[1] + 10
        
        total_height = len(lines) * line_height
        start_y = (height - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + i * line_height
            draw.text((x, y), line, fill=color, font=font)
    
    def _add_slide_number(self, draw: ImageDraw, slide_number: int, width: int, height: int):
        """Add slide number to bottom right corner"""
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        number_text = f"{slide_number}"
        bbox = draw.textbbox((0, 0), number_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = width - text_width - 30
        y = height - text_height - 30
        
        # Draw background circle
        circle_size = max(text_width, text_height) + 20
        draw.ellipse([x - 10, y - 10, x + circle_size, y + circle_size], fill=(100, 100, 100, 128))
        
        # Draw text
        draw.text((x, y), number_text, fill=(255, 255, 255), font=font)
    
    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _calculate_slide_duration(self, text_content: str) -> float:
        """Calculate appropriate slide duration based on content length"""
        word_count = len(text_content.split())
        # Base duration: 3 seconds + 0.5 seconds per word (reading time)
        base_duration = 3.0 + (word_count * 0.5)
        # Cap at reasonable maximum
        return min(base_duration, 15.0)
    
    async def _create_single_visual(self, text_content: str, content_type: str, 
                                  style_preferences: Dict) -> Optional[VisualContent]:
        """Create a single visual item based on content type"""
        try:
            if content_type == 'image':
                return await self._create_single_image(text_content, style_preferences)
            elif content_type == 'graphic':
                return await self._create_single_graphic(text_content, style_preferences)
            else:
                logger.warning(f"Unknown content type: {content_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating {content_type} visual: {e}")
            return None
    
    async def _create_single_image(self, text_content: str, style_preferences: Dict) -> Optional[VisualContent]:
        """Create a single image from text content"""
        try:
            # Create image with text overlay
            width, height = 1920, 1080  # HD resolution
            image = Image.new('RGB', (width, height), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Apply style preferences
            if style_preferences is None:
                style_preferences = {}
            color_scheme = style_preferences.get('color_scheme', 'professional')
            colors = self.color_schemes.get(color_scheme, self.color_schemes['professional'])
            if not colors:
                colors = self.color_schemes['professional']
            
            # Create background with gradient effect
            self._create_gradient_background(draw, width, height, colors)
            
            # Add text overlay
            font_size = style_preferences.get('font_size', 36)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Draw text with shadow effect
            self._draw_text_with_shadow(draw, text_content, font, colors['text'], width, height)
            
            # Add decorative elements
            self._add_decorative_elements(draw, width, height, colors)
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}_{hash(text_content) % 10000:04d}.png"
            image_path = os.path.join(self.visuals_dir, filename)
            image.save(image_path, 'PNG', optimize=True)
            
            logger.info(f"Image created: {image_path}")
            
            return VisualContent(
                content_type='image',
                text_content=text_content,
                visual_path=image_path,
                duration_seconds=self._calculate_image_duration(text_content),
                transition_type='fade',
                metadata={
                    'style_scheme': color_scheme,
                    'font_size': font_size,
                    'generated_at': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            return None
    
    async def _create_single_graphic(self, text_content: str, style_preferences: Dict) -> Optional[VisualContent]:
        """Create a single graphic from text content"""
        try:
            # Create graphic with infographic style
            width, height = 1920, 1080  # HD resolution
            image = Image.new('RGB', (width, height), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Apply style preferences
            if style_preferences is None:
                style_preferences = {}
            color_scheme = style_preferences.get('color_scheme', 'modern')
            colors = self.color_schemes.get(color_scheme, self.color_schemes['modern'])
            if not colors:
                colors = self.color_schemes['modern']
            
            # Create modern background
            self._create_modern_background(draw, width, height, colors)
            
            # Parse text for graphic elements
            graphic_elements = self._parse_text_for_graphics(text_content)
            
            # Draw graphic elements
            self._draw_graphic_elements(draw, graphic_elements, colors, width, height)
            
            # Add text labels
            font_size = style_preferences.get('font_size', 28)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            self._add_graphic_labels(draw, graphic_elements, font, colors, width, height)
            
            # Save graphic
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"graphic_{timestamp}_{hash(text_content) % 10000:04d}.png"
            graphic_path = os.path.join(self.graphics_dir, filename)
            image.save(graphic_path, 'PNG', optimize=True)
            
            logger.info(f"Graphic created: {graphic_path}")
            
            return VisualContent(
                content_type='graphic',
                text_content=text_content,
                visual_path=graphic_path,
                duration_seconds=self._calculate_graphic_duration(text_content),
                transition_type='slide',
                metadata={
                    'style_scheme': color_scheme,
                    'graphic_elements': len(graphic_elements),
                    'generated_at': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating graphic: {e}")
            return None
    
    def _create_gradient_background(self, draw: ImageDraw, width: int, height: int, colors: Dict):
        """Create a gradient background for images"""
        try:
            # Create gradient from primary to secondary color
            primary = colors['primary']
            secondary = colors['secondary']
            
            for y in range(height):
                # Calculate gradient ratio
                ratio = y / height
                r = int(primary[0] * (1 - ratio) + secondary[0] * ratio)
                g = int(primary[1] * (1 - ratio) + secondary[1] * ratio)
                b = int(primary[2] * (1 - ratio) + secondary[2] * ratio)
                
                # Draw horizontal line
                draw.line([(0, y), (width, y)], fill=(r, g, b))
        except Exception as e:
            logger.warning(f"Could not create gradient background: {e}")
            # Fallback to solid color
            draw.rectangle([0, 0, width, height], fill=colors['background'])
    
    def _create_modern_background(self, draw: ImageDraw, width: int, height: int, colors: Dict):
        """Create a modern geometric background for graphics"""
        try:
            # Fill with base color
            draw.rectangle([0, 0, width, height], fill=colors['background'])
            
            # Add geometric shapes
            shape_color = colors['accent']
            
            # Draw circles
            for i in range(5):
                x = (i * width // 4) + 100
                y = (i * height // 4) + 100
                radius = 50 + (i * 20)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           fill=shape_color, outline=None)
            
            # Draw rectangles
            for i in range(3):
                x = (i * width // 3) + 50
                y = height - 200 - (i * 100)
                w = 80
                h = 60
                draw.rectangle([x, y, x+w, y+h], 
                             fill=colors['secondary'], outline=None)
                
        except Exception as e:
            logger.warning(f"Could not create modern background: {e}")
            # Fallback to solid color
            draw.rectangle([0, 0, width, height], fill=colors['background'])
    
    def _draw_text_with_shadow(self, draw: ImageDraw, text: str, font: ImageFont, 
                              text_color: Tuple, width: int, height: int):
        """Draw text with shadow effect"""
        try:
            # Wrap text
            lines = self._wrap_text(text, font, width - 200)
            
            # Calculate text position - use textbbox for modern PIL versions
            try:
                bbox = font.getbbox("A")
                line_height = bbox[3] - bbox[1] + 15
            except AttributeError:
                # Fallback for older PIL versions
                line_height = font.getsize("A")[1] + 15
            
            total_height = len(lines) * line_height
            start_y = (height - total_height) // 2
            
            # Draw shadow first
            shadow_offset = 3
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + i * line_height
                
                # Draw shadow
                draw.text((x + shadow_offset, y + shadow_offset), line, 
                         fill=(100, 100, 100), font=font)
                
                # Draw main text
                draw.text((x, y), line, fill=text_color, font=font)
                
        except Exception as e:
            logger.warning(f"Could not draw text with shadow: {e}")
            # Fallback to simple text
            self._draw_centered_text(draw, text, font, text_color, width, height, 100)
    
    def _add_decorative_elements(self, draw: ImageDraw, width: int, height: int, colors: Dict):
        """Add decorative elements to images"""
        try:
            # Draw border
            border_width = 10
            draw.rectangle([0, 0, width, height], outline=colors['primary'], width=border_width)
            
            # Add corner accents
            accent_size = 50
            accent_color = colors['accent']
            
            # Top-left corner
            draw.rectangle([0, 0, accent_size, accent_size], fill=accent_color)
            
            # Top-right corner
            draw.rectangle([width-accent_size, 0, width, accent_size], fill=accent_color)
            
            # Bottom-left corner
            draw.rectangle([0, height-accent_size, accent_size, height], fill=accent_color)
            
            # Bottom-right corner
            draw.rectangle([width-accent_size, height-accent_size, width, height], fill=accent_color)
            
        except Exception as e:
            logger.warning(f"Could not add decorative elements: {e}")
    
    def _parse_text_for_graphics(self, text_content: str) -> List[Dict]:
        """Parse text to identify graphic elements"""
        elements = []
        
        # Simple parsing - look for numbers, percentages, and key phrases
        words = text_content.split()
        
        for i, word in enumerate(words):
            # Look for numbers
            if word.replace('.', '').replace('%', '').isdigit():
                elements.append({
                    'type': 'number',
                    'value': word,
                    'position': i,
                    'x': 200 + (i * 100) % 800,
                    'y': 200 + (i * 50) % 400
                })
            
            # Look for percentages
            elif '%' in word:
                elements.append({
                    'type': 'percentage',
                    'value': word,
                    'position': i,
                    'x': 300 + (i * 80) % 600,
                    'y': 300 + (i * 60) % 300
                })
            
            # Look for key phrases
            elif len(word) > 6 and word.lower() in ['important', 'significant', 'major', 'key', 'critical']:
                elements.append({
                    'type': 'highlight',
                    'value': word,
                    'position': i,
                    'x': 400 + (i * 70) % 500,
                    'y': 150 + (i * 40) % 200
                })
        
        # If no elements found, create some default ones
        if not elements:
            elements = [
                {'type': 'highlight', 'value': 'Key Point', 'x': 400, 'y': 200},
                {'type': 'number', 'value': '100%', 'x': 600, 'y': 300},
                {'type': 'highlight', 'value': 'Important', 'x': 800, 'y': 400}
            ]
        
        return elements
    
    def _draw_graphic_elements(self, draw: ImageDraw, elements: List[Dict], colors: Dict, width: int, height: int):
        """Draw graphic elements on the canvas"""
        try:
            for element in elements:
                if element['type'] == 'number':
                    # Draw circle with number
                    x, y = element['x'], element['y']
                    radius = 40
                    draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                               fill=colors['primary'], outline=None)
                    
                    # Draw number
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                    except:
                        font = ImageFont.load_default()
                    
                    bbox = draw.textbbox((0, 0), element['value'], font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    text_x = x - text_width // 2
                    text_y = y - text_height // 2
                    draw.text((text_x, text_y), element['value'], fill=(255, 255, 255), font=font)
                
                elif element['type'] == 'percentage':
                    # Draw progress bar
                    x, y = element['x'], element['y']
                    bar_width = 120
                    bar_height = 20
                    
                    # Background bar
                    draw.rectangle([x, y, x+bar_width, y+bar_height], 
                                 fill=colors['secondary'], outline=None)
                    
                    # Progress fill
                    progress = min(100, int(element['value'].replace('%', '')))
                    fill_width = int((progress / 100) * bar_width)
                    draw.rectangle([x, y, x+fill_width, y+bar_height], 
                                 fill=colors['accent'], outline=None)
                
                elif element['type'] == 'highlight':
                    # Draw highlighted box
                    x, y = element['x'], element['y']
                    box_width = 100
                    box_height = 30
                    
                    draw.rectangle([x, y, x+box_width, y+box_height], 
                                 fill=colors['accent'], outline=None)
                    
        except Exception as e:
            logger.warning(f"Could not draw graphic elements: {e}")
    
    def _add_graphic_labels(self, draw: ImageDraw, elements: List[Dict], font: ImageFont, 
                           colors: Dict, width: int, height: int):
        """Add labels to graphic elements"""
        try:
            for element in elements:
                x, y = element['x'], element['y']
                
                # Add label below element
                label_y = y + 60
                if label_y < height - 50:  # Ensure label fits on screen
                    draw.text((x, label_y), element['type'].title(), 
                             fill=colors['text'], font=font)
                    
        except Exception as e:
            logger.warning(f"Could not add graphic labels: {e}")
    
    def _calculate_image_duration(self, text_content: str) -> float:
        """Calculate appropriate image duration based on content length"""
        word_count = len(text_content.split())
        # Base duration: 2 seconds + 0.3 seconds per word (viewing time)
        base_duration = 2.0 + (word_count * 0.3)
        # Cap at reasonable maximum
        return min(base_duration, 10.0)
    
    def _calculate_graphic_duration(self, text_content: str) -> float:
        """Calculate appropriate graphic duration based on content length"""
        word_count = len(text_content.split())
        # Base duration: 4 seconds + 0.4 seconds per word (comprehension time)
        base_duration = 4.0 + (word_count * 0.4)
        # Cap at reasonable maximum
        return min(base_duration, 12.0)
    
    async def _generate_images(self, text_content: str, style_preferences: Dict) -> List[VisualContent]:
        """Generate images from text content"""
        try:
            # Split content into image-sized chunks
            image_chunks = self._create_image_chunks(text_content)
            images = []
            
            for i, chunk in enumerate(image_chunks):
                image = await self._create_single_image(chunk, style_preferences)
                if image:
                    images.append(image)
            
            logger.info(f"Generated {len(images)} images from content")
            return images
            
        except Exception as e:
            logger.error(f"Error generating images: {e}")
            return []
    
    async def _generate_graphics(self, text_content: str, style_preferences: Dict) -> List[VisualContent]:
        """Generate graphics from text content"""
        try:
            # Split content into graphic-sized chunks
            graphic_chunks = self._create_graphic_chunks(text_content)
            graphics = []
            
            for i, chunk in enumerate(graphic_chunks):
                graphic = await self._create_single_graphic(chunk, style_preferences)
                if graphic:
                    graphics.append(graphic)
            
            logger.info(f"Generated {len(graphics)} graphics from content")
            return graphics
            
        except Exception as e:
            logger.error(f"Error generating graphics: {e}")
            return []
    
    def _create_image_chunks(self, text_content: str, max_words_per_image: int = 80) -> List[str]:
        """Create image-sized chunks from text content"""
        words = text_content.split()
        chunks = []
        
        for i in range(0, len(words), max_words_per_image):
            chunk_words = words[i:i + max_words_per_image]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
        
        return chunks
    
    def _create_graphic_chunks(self, text_content: str, max_words_per_graphic: int = 120) -> List[str]:
        """Create graphic-sized chunks from text content"""
        words = text_content.split()
        chunks = []
        
        for i in range(0, len(words), max_words_per_graphic):
            chunk_words = words[i:i + max_words_per_graphic]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
        
        return chunks
    
    def _enhance_visual_quality(self, image: Image.Image, enhancement_type: str = 'standard') -> Image.Image:
        """Enhance visual quality with various effects"""
        try:
            if enhancement_type == 'sharp':
                # Apply sharpening filter
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.5)
            elif enhancement_type == 'bright':
                # Apply brightness enhancement
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.1)
            elif enhancement_type == 'contrast':
                # Apply contrast enhancement
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.2)
            
            return image
            
        except Exception as e:
            logger.warning(f"Could not enhance visual quality: {e}")
            return image
    
    def _apply_visual_effects(self, image: Image.Image, effects: Dict) -> Image.Image:
        """Apply various visual effects to images"""
        try:
            if effects.get('blur', False):
                from PIL import ImageFilter
                image = image.filter(ImageFilter.GaussianBlur(radius=1))
            
            if effects.get('sharpen', False):
                from PIL import ImageFilter
                image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            
            if effects.get('emboss', False):
                from PIL import ImageFilter
                image = image.filter(ImageFilter.EMBOSS)
            
            return image
            
        except Exception as e:
            logger.warning(f"Could not apply visual effects: {e}")
            return image
    
    def _create_animated_transition(self, visuals: List[VisualContent], transition_type: str = 'fade') -> Dict:
        """Create transition information for video composition"""
        transitions = []
        
        for i, visual in enumerate(visuals):
            if i == 0:
                # First visual - no transition in
                transitions.append({
                    'visual_index': i,
                    'transition_in': 'none',
                    'transition_out': visual.transition_type,
                    'duration': visual.duration_seconds
                })
            else:
                # Subsequent visuals
                transitions.append({
                    'visual_index': i,
                    'transition_in': visuals[i-1].transition_type,
                    'transition_out': visual.transition_type,
                    'duration': visual.duration_seconds
                })
        
        return {
            'total_duration': sum(v.duration_seconds for v in visuals),
            'transitions': transitions,
            'transition_type': transition_type
        }
    
    def _optimize_for_video_export(self, visuals: List[VisualContent], target_format: str = 'mp4') -> Dict:
        """Optimize visuals for video export"""
        optimization_info = {
            'target_format': target_format,
            'total_visuals': len(visuals),
            'total_duration': sum(v.duration_seconds for v in visuals),
            'recommended_settings': {}
        }
        
        if target_format == 'mp4':
            optimization_info['recommended_settings'] = {
                'resolution': '1920x1080',
                'frame_rate': 30,
                'bitrate': '5000k',
                'codec': 'h264'
            }
        elif target_format == 'gif':
            optimization_info['recommended_settings'] = {
                'resolution': '1280x720',
                'frame_rate': 15,
                'optimization': 'high'
            }
        
        return optimization_info
    
    def get_visual_statistics(self, visuals: List[VisualContent]) -> Dict:
        """Get statistics about generated visual content"""
        if not visuals:
            return {}
        
        total_duration = sum(v.duration_seconds for v in visuals)
        content_types = {}
        style_schemes = {}
        
        for visual in visuals:
            # Count content types
            content_types[visual.content_type] = content_types.get(visual.content_type, 0) + 1
            
            # Count style schemes
            if 'style_scheme' in visual.metadata:
                scheme = visual.metadata['style_scheme']
                style_schemes[scheme] = style_schemes.get(scheme, 0) + 1
        
        return {
            'total_visuals': len(visuals),
            'total_duration_seconds': total_duration,
            'total_duration_minutes': total_duration / 60,
            'content_type_distribution': content_types,
            'style_scheme_distribution': style_schemes,
            'average_duration_per_visual': total_duration / len(visuals),
            'estimated_video_length_minutes': total_duration / 60
        }
    
    def export_visual_manifest(self, visuals: List[VisualContent], output_path: str = None) -> str:
        """Export a manifest file for video composition tools"""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(self.output_dir, f"visual_manifest_{timestamp}.json")
            
            manifest = {
                'metadata': {
                    'generated_at': datetime.utcnow().isoformat() + 'Z',
                    'total_visuals': len(visuals),
                    'total_duration_seconds': sum(v.duration_seconds for v in visuals),
                    'version': '1.0'
                },
                'visuals': []
            }
            
            for i, visual in enumerate(visuals):
                manifest['visuals'].append({
                    'index': i,
                    'content_type': visual.content_type,
                    'file_path': visual.visual_path,
                    'duration_seconds': visual.duration_seconds,
                    'transition_type': visual.transition_type,
                    'metadata': visual.metadata,
                    'text_preview': visual.text_content[:100] + "..." if len(visual.text_content) > 100 else visual.text_content
                })
            
            with open(output_path, 'w') as f:
                json.dump(manifest, f, indent=2, default=str)
            
            logger.info(f"Visual manifest exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting visual manifest: {e}")
            return ""
    
    async def save_visual_results(self, visuals: List[VisualContent], metadata: Dict = None) -> str:
        """Save visual generation results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"visual_generation_{timestamp}.json"
            file_path = os.path.join(self.output_dir, filename)
            
            # Convert visuals to serializable format
            serializable_visuals = []
            for visual in visuals:
                serializable_visuals.append({
                    'content_type': visual.content_type,
                    'text_content': visual.text_content,
                    'visual_path': visual.visual_path,
                    'duration_seconds': visual.duration_seconds,
                    'transition_type': visual.transition_type,
                    'metadata': visual.metadata
                })
            
            result = {
                'success': True,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'total_visuals': len(visuals),
                'visuals': serializable_visuals,
                'metadata': metadata or {},
                'processing_info': {
                    'batch_size': self.batch_size,
                    'max_concurrent': self.max_concurrent_generation,
                    'cache_enabled': self.cache_enabled
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Visual results saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving visual results: {e}")
            return ""
    
    def get_available_templates(self) -> Dict:
        """Get available slide templates"""
        return self.slide_templates
    
    def get_available_color_schemes(self) -> Dict:
        """Get available color schemes"""
        return self.color_schemes
    
    def get_available_font_configs(self) -> Dict:
        """Get available font configurations"""
        return self.font_configs
    
    def update_style_preferences(self, new_preferences: Dict):
        """Update style preferences for visual generation"""
        if 'slide_templates' in new_preferences:
            self.slide_templates.update(new_preferences['slide_templates'])
        if 'color_schemes' in new_preferences:
            self.color_schemes.update(new_preferences['color_schemes'])
        if 'font_configs' in new_preferences:
            self.font_configs.update(new_preferences['font_configs'])
        
        logger.info("Style preferences updated")
    
    def optimize_for_long_videos(self, video_length_minutes: int):
        """Optimize settings for long video processing"""
        if video_length_minutes > 30:
            # For very long videos, reduce batch size and increase concurrency limits
            self.batch_size = max(5, self.batch_size - 5)
            self.max_concurrent_generation = min(5, self.max_concurrent_generation + 2)
            logger.info(f"Optimized for long video ({video_length_minutes} min): batch_size={self.batch_size}, max_concurrent={self.max_concurrent_generation}")
        elif video_length_minutes > 15:
            # For medium-long videos, moderate optimization
            self.batch_size = max(8, self.batch_size - 2)
            self.max_concurrent_generation = min(4, self.max_concurrent_generation + 1)
            logger.info(f"Optimized for medium-long video ({video_length_minutes} min): batch_size={self.batch_size}, max_concurrent={self.max_concurrent_generation}") 