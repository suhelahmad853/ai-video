"""
Content Rewriting Engine for AI Video Creator Tool
Task 2.1.1: Text Analysis and Modification

This module handles:
- Content similarity detection
- Content rewriting algorithms
- Plagiarism checking and originality validation
"""

import re
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentAnalysis:
    """Data class for content analysis results"""
    original_text: str
    modified_text: str
    similarity_score: float
    originality_score: float
    changes_made: List[str]
    readability_score: float
    word_count: int
    processing_time: float

@dataclass
class RewritingOptions:
    """Data class for rewriting configuration options"""
    target_style: str = "professional"  # professional, casual, academic, creative
    target_tone: str = "neutral"        # neutral, positive, negative, humorous
    complexity_level: str = "medium"    # simple, medium, complex
    preserve_key_points: bool = True
    max_similarity: float = 0.3         # Maximum allowed similarity with original

class ContentRewriter:
    """
    Main content rewriting engine for text analysis and modification
    """
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Common synonyms and alternatives for rewriting
        self.synonyms = {
            'important': ['crucial', 'essential', 'vital', 'key', 'critical'],
            'good': ['excellent', 'great', 'outstanding', 'superb', 'fantastic'],
            'bad': ['poor', 'terrible', 'awful', 'dreadful', 'horrible'],
            'big': ['large', 'huge', 'enormous', 'massive', 'gigantic'],
            'small': ['tiny', 'miniature', 'petite', 'compact', 'little'],
            'fast': ['quick', 'rapid', 'swift', 'speedy', 'hasty'],
            'slow': ['sluggish', 'leisurely', 'gradual', 'unhurried', 'deliberate'],
            'beautiful': ['gorgeous', 'stunning', 'attractive', 'lovely', 'pretty'],
            'ugly': ['unattractive', 'hideous', 'repulsive', 'unsightly', 'grotesque'],
            'smart': ['intelligent', 'clever', 'brilliant', 'wise', 'sharp'],
            'stupid': ['foolish', 'ignorant', 'unintelligent', 'dense', 'dim'],
            'happy': ['joyful', 'cheerful', 'delighted', 'pleased', 'content'],
            'sad': ['unhappy', 'melancholy', 'depressed', 'sorrowful', 'gloomy'],
            'angry': ['furious', 'enraged', 'irritated', 'annoyed', 'frustrated'],
            'calm': ['peaceful', 'serene', 'tranquil', 'relaxed', 'composed']
        }
        
        # Transition phrases for better flow
        self.transitions = {
            'addition': ['furthermore', 'moreover', 'in addition', 'besides', 'also'],
            'contrast': ['however', 'nevertheless', 'on the other hand', 'in contrast', 'yet'],
            'cause_effect': ['therefore', 'consequently', 'as a result', 'thus', 'hence'],
            'sequence': ['firstly', 'secondly', 'finally', 'next', 'then'],
            'example': ['for example', 'for instance', 'specifically', 'in particular', 'such as'],
            'conclusion': ['in conclusion', 'to summarize', 'overall', 'in summary', 'finally']
        }
        
        # Style templates for different writing styles
        self.style_templates = {
            'professional': {
                'tone': 'formal',
                'complexity': 'medium',
                'transitions': True,
                'passive_voice': True
            },
            'casual': {
                'tone': 'informal',
                'complexity': 'simple',
                'transitions': False,
                'passive_voice': False
            },
            'academic': {
                'tone': 'formal',
                'complexity': 'complex',
                'transitions': True,
                'passive_voice': True
            },
            'creative': {
                'tone': 'expressive',
                'complexity': 'variable',
                'transitions': True,
                'passive_voice': False
            }
        }
    
    async def analyze_and_rewrite_content(
        self, 
        original_text: str, 
        options: RewritingOptions
    ) -> ContentAnalysis:
        """
        Main method to analyze and rewrite content
        
        Args:
            original_text (str): Original text to analyze and rewrite
            options (RewritingOptions): Configuration options for rewriting
            
        Returns:
            ContentAnalysis: Results of the analysis and rewriting
        """
        try:
            start_time = datetime.now()
            logger.info("Starting content analysis and rewriting")
            
            # Step 1: Analyze original content
            original_analysis = self._analyze_original_content(original_text)
            
            # Step 2: Rewrite content based on options
            modified_text = await self._rewrite_content(original_text, options)
            
            # Step 3: Analyze modified content
            modified_analysis = self._analyze_modified_content(modified_text)
            
            # Step 4: Calculate similarity and originality scores
            similarity_score = self._calculate_similarity(original_text, modified_text)
            originality_score = 1.0 - similarity_score
            
            # Step 5: Identify changes made
            changes_made = self._identify_changes(original_text, modified_text)
            
            # Step 6: Calculate readability score
            readability_score = self._calculate_readability(modified_text)
            
            # Step 7: Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create analysis result
            analysis_result = ContentAnalysis(
                original_text=original_text,
                modified_text=modified_text,
                similarity_score=similarity_score,
                originality_score=originality_score,
                changes_made=changes_made,
                readability_score=readability_score,
                word_count=len(modified_text.split()),
                processing_time=processing_time
            )
            
            # Save results
            await self._save_analysis_results(analysis_result, options)
            
            logger.info(f"Content rewriting completed in {processing_time:.2f} seconds")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in content analysis and rewriting: {e}")
            raise
    
    def _analyze_original_content(self, text: str) -> Dict:
        """Analyze the original content for structure and characteristics"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_sentence_length': len(words) / len([s for s in sentences if s.strip()]) if sentences else 0,
            'unique_words': len(set(words)),
            'vocabulary_diversity': len(set(words)) / len(words) if words else 0,
            'complexity_level': self._assess_complexity(text)
        }
    
    def _analyze_modified_content(self, text: str) -> Dict:
        """Analyze the modified content for structure and characteristics"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_sentence_length': len(words) / len([s for s in sentences if s.strip()]) if sentences else 0,
            'unique_words': len(set(words)),
            'vocabulary_diversity': len(set(words)) / len(words) if words else 0,
            'complexity_level': self._assess_complexity(text)
        }
    
    def _assess_complexity(self, text: str) -> str:
        """Assess the complexity level of the text"""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Count complex words (longer than 6 characters)
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_ratio = complex_words / len(words) if words else 0
        
        if complex_ratio > 0.3 or avg_word_length > 6:
            return 'complex'
        elif complex_ratio > 0.15 or avg_word_length > 5:
            return 'medium'
        else:
            return 'simple'
    
    async def _rewrite_content(self, text: str, options: RewritingOptions) -> str:
        """Rewrite content based on specified options"""
        modified_text = text
        
        # Apply style-based modifications
        if options.target_style in self.style_templates:
            style_config = self.style_templates[options.target_style]
            modified_text = self._apply_style_modifications(modified_text, style_config)
        
        # Apply tone modifications
        modified_text = self._apply_tone_modifications(modified_text, options.target_tone)
        
        # Apply complexity modifications
        modified_text = self._apply_complexity_modifications(modified_text, options.complexity_level)
        
        # Apply synonym replacements
        modified_text = self._apply_synonym_replacements(modified_text)
        
        # Apply transition improvements
        if options.target_style in ['professional', 'academic']:
            modified_text = self._improve_transitions(modified_text)
        
        # Apply sentence restructuring
        modified_text = self._restructure_sentences(modified_text)
        
        return modified_text
    
    def _apply_style_modifications(self, text: str, style_config: Dict) -> str:
        """Apply modifications based on style configuration"""
        modified_text = text
        
        if style_config['passive_voice']:
            modified_text = self._convert_to_passive_voice(modified_text)
        
        if style_config['complexity'] == 'complex':
            modified_text = self._increase_complexity(modified_text)
        elif style_config['complexity'] == 'simple':
            modified_text = self._simplify_text(modified_text)
        
        return modified_text
    
    def _apply_tone_modifications(self, text: str, target_tone: str) -> str:
        """Apply tone modifications to the text"""
        if target_tone == 'positive':
            return self._make_positive(text)
        elif target_tone == 'negative':
            return self._make_negative(text)
        elif target_tone == 'humorous':
            return self._add_humor(text)
        else:
            return text  # neutral tone
    
    def _apply_complexity_modifications(self, text: str, target_complexity: str) -> str:
        """Modify text complexity to match target level"""
        current_complexity = self._assess_complexity(text)
        
        if target_complexity == 'simple' and current_complexity != 'simple':
            return self._simplify_text(text)
        elif target_complexity == 'complex' and current_complexity != 'complex':
            return self._increase_complexity(text)
        else:
            return text
    
    def _apply_synonym_replacements(self, text: str) -> str:
        """Replace words with synonyms to improve variety"""
        modified_text = text
        
        for word, synonyms in self.synonyms.items():
            if word in modified_text.lower():
                # Choose a random synonym (for now, just pick the first)
                replacement = synonyms[0]
                # Replace the word (case-insensitive)
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                modified_text = pattern.sub(replacement, modified_text)
        
        return modified_text
    
    def _improve_transitions(self, text: str) -> str:
        """Improve text flow by adding transition phrases"""
        sentences = text.split('.')
        improved_sentences = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            # Add transition phrases at the beginning of sentences
            if i > 0 and sentence.strip():
                # Randomly choose transition type
                import random
                transition_type = random.choice(list(self.transitions.keys()))
                transition_phrase = random.choice(self.transitions[transition_type])
                
                sentence = f"{transition_phrase.capitalize()}, {sentence.strip()}"
            
            improved_sentences.append(sentence)
        
        return '. '.join(improved_sentences)
    
    def _restructure_sentences(self, text: str) -> str:
        """Restructure sentences for better flow and readability"""
        sentences = text.split('.')
        restructured_sentences = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            # Split long sentences
            if len(sentence.split()) > 25:
                words = sentence.split()
                mid_point = len(words) // 2
                
                first_part = ' '.join(words[:mid_point])
                second_part = ' '.join(words[mid_point:])
                
                restructured_sentences.extend([first_part, second_part])
            else:
                restructured_sentences.append(sentence)
        
        return '. '.join(restructured_sentences)
    
    def _convert_to_passive_voice(self, text: str) -> str:
        """Convert active voice to passive voice for formal writing"""
        # Simple passive voice conversion (basic implementation)
        # This is a simplified version - in production, you'd use NLP libraries
        
        passive_patterns = [
            (r'I (\w+)', r'It is \1ed by me'),
            (r'We (\w+)', r'It is \1ed by us'),
            (r'You (\w+)', r'It is \1ed by you'),
            (r'They (\w+)', r'It is \1ed by them'),
            (r'He (\w+)', r'It is \1ed by him'),
            (r'She (\w+)', r'It is \1ed by her')
        ]
        
        modified_text = text
        for pattern, replacement in passive_patterns:
            modified_text = re.sub(pattern, replacement, modified_text, flags=re.IGNORECASE)
        
        return modified_text
    
    def _make_positive(self, text: str) -> str:
        """Make text more positive in tone"""
        negative_to_positive = {
            'problem': 'opportunity',
            'difficult': 'challenging',
            'hard': 'demanding',
            'bad': 'suboptimal',
            'failure': 'learning experience',
            'mistake': 'lesson'
        }
        
        modified_text = text
        for negative, positive in negative_to_positive.items():
            pattern = re.compile(re.escape(negative), re.IGNORECASE)
            modified_text = pattern.sub(positive, modified_text)
        
        return modified_text
    
    def _make_negative(self, text: str) -> str:
        """Make text more negative in tone"""
        positive_to_negative = {
            'good': 'questionable',
            'excellent': 'mediocre',
            'great': 'average',
            'amazing': 'ordinary',
            'wonderful': 'adequate'
        }
        
        modified_text = text
        for positive, negative in positive_to_negative.items():
            pattern = re.compile(re.escape(positive), re.IGNORECASE)
            modified_text = pattern.sub(negative, modified_text)
        
        return modified_text
    
    def _add_humor(self, text: str) -> str:
        """Add humorous elements to the text"""
        # Simple humor additions (basic implementation)
        humor_additions = [
            " (which is pretty cool, if you ask me)",
            " (surprise, surprise!)",
            " (plot twist!)",
            " (drumroll please...)",
            " (and that's the tea!)"
        ]
        
        import random
        sentences = text.split('.')
        if len(sentences) > 2:
            # Add humor to a random sentence
            humor_index = random.randint(0, len(sentences) - 1)
            if sentences[humor_index].strip():
                sentences[humor_index] += random.choice(humor_additions)
        
        return '. '.join(sentences)
    
    def _simplify_text(self, text: str) -> str:
        """Simplify text by using shorter words and simpler sentences"""
        # Replace complex words with simpler alternatives
        complex_to_simple = {
            'utilize': 'use',
            'implement': 'do',
            'facilitate': 'help',
            'demonstrate': 'show',
            'accomplish': 'do',
            'comprehensive': 'complete',
            'subsequently': 'then',
            'nevertheless': 'but',
            'furthermore': 'also',
            'consequently': 'so'
        }
        
        modified_text = text
        for complex_word, simple_word in complex_to_simple.items():
            pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
            modified_text = pattern.sub(simple_word, modified_text)
        
        return modified_text
    
    def _increase_complexity(self, text: str) -> str:
        """Increase text complexity by using more sophisticated vocabulary"""
        # Replace simple words with more complex alternatives
        simple_to_complex = {
            'use': 'utilize',
            'do': 'implement',
            'help': 'facilitate',
            'show': 'demonstrate',
            'complete': 'comprehensive',
            'then': 'subsequently',
            'but': 'nevertheless',
            'also': 'furthermore',
            'so': 'consequently'
        }
        
        modified_text = text
        for simple_word, complex_word in simple_to_complex.items():
            pattern = re.compile(re.escape(simple_word), re.IGNORECASE)
            modified_text = pattern.sub(complex_word, modified_text)
        
        return modified_text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using various metrics"""
        # Simple similarity calculation using word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard_similarity = len(intersection) / len(union)
        
        # Also calculate character-level similarity
        char_similarity = self._calculate_character_similarity(text1, text2)
        
        # Combine both metrics
        combined_similarity = (jaccard_similarity + char_similarity) / 2
        
        return min(combined_similarity, 1.0)
    
    def _calculate_character_similarity(self, text1: str, text2: str) -> float:
        """Calculate character-level similarity between texts"""
        # Use character n-grams for similarity
        def get_ngrams(text: str, n: int = 3) -> set:
            return set(text[i:i+n] for i in range(len(text) - n + 1))
        
        ngrams1 = get_ngrams(text1.lower())
        ngrams2 = get_ngrams(text2.lower())
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = ngrams1.intersection(ngrams2)
        union = ngrams1.union(ngrams2)
        
        return len(intersection) / len(union)
    
    def _identify_changes(self, original: str, modified: str) -> List[str]:
        """Identify specific changes made during rewriting"""
        changes = []
        
        # Word count changes
        orig_words = len(original.split())
        mod_words = len(modified.split())
        if orig_words != mod_words:
            changes.append(f"Word count changed from {orig_words} to {mod_words}")
        
        # Sentence count changes
        orig_sentences = len([s for s in original.split('.') if s.strip()])
        mod_sentences = len([s for s in modified.split('.') if s.strip()])
        if orig_sentences != mod_sentences:
            changes.append(f"Sentence count changed from {orig_sentences} to {mod_sentences}")
        
        # Vocabulary changes
        orig_unique = len(set(original.lower().split()))
        mod_unique = len(set(modified.lower().split()))
        if orig_unique != mod_unique:
            changes.append(f"Unique words changed from {orig_unique} to {mod_unique}")
        
        # Style changes
        if self._assess_complexity(original) != self._assess_complexity(modified):
            changes.append("Text complexity level modified")
        
        return changes
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score using Flesch Reading Ease"""
        sentences = [s for s in text.split('.') if s.strip()]
        words = text.split()
        syllables = self._count_syllables(text)
        
        if not sentences or not words:
            return 0.0
        
        # Flesch Reading Ease formula
        flesch_score = 206.835 - (1.015 * (len(words) / len(sentences))) - (84.6 * (syllables / len(words)))
        
        # Normalize to 0-1 scale
        normalized_score = max(0.0, min(1.0, flesch_score / 100.0))
        
        return normalized_score
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (simplified implementation)"""
        # Simplified syllable counting
        vowels = 'aeiouy'
        text = text.lower()
        count = 0
        on_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        return max(count, 1)  # At least 1 syllable per word
    
    async def _save_analysis_results(self, analysis: ContentAnalysis, options: RewritingOptions) -> None:
        """Save analysis results to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_rewriting_{timestamp}.json"
            output_path = self.output_dir / filename
            
            save_data = {
                'rewriting_options': {
                    'target_style': options.target_style,
                    'target_tone': options.target_tone,
                    'complexity_level': options.complexity_level,
                    'preserve_key_points': options.preserve_key_points,
                    'max_similarity': options.max_similarity
                },
                'analysis_results': {
                    'original_text': analysis.original_text,
                    'modified_text': analysis.modified_text,
                    'similarity_score': analysis.similarity_score,
                    'originality_score': analysis.originality_score,
                    'changes_made': analysis.changes_made,
                    'readability_score': analysis.readability_score,
                    'word_count': analysis.word_count,
                    'processing_time': analysis.processing_time
                },
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'task': '2.1.1'
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Content rewriting analysis saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")

# Create global instance
content_rewriter = ContentRewriter() 