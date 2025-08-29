"""
Content Rewriter Module for AI-powered text analysis and modification
Part of Phase 2: AI Content Transformation
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ContentRewriter:
    """
    AI-powered content rewriting and modification engine
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    async def analyze_and_rewrite_content(self, original_text: str, 
                                       modification_type: str = "enhance",
                                       target_audience: str = "general",
                                       style_preference: str = "professional") -> Dict:
        """
        Analyze and rewrite content based on specified parameters
        
        Args:
            original_text: The original transcript text
            modification_type: Type of modification (enhance, simplify, formalize, casual)
            target_audience: Target audience (general, technical, academic, casual)
            style_preference: Writing style preference (professional, conversational, academic)
            
        Returns:
            Dict containing analysis and rewritten content
        """
        try:
            logger.info(f"Starting content analysis and rewriting for {modification_type} modification")
            
            # Step 1: Analyze original content
            content_analysis = await self._analyze_content_structure(original_text)
            
            # Step 2: Generate rewritten content
            rewritten_content = await self._generate_rewritten_content(
                original_text, 
                content_analysis, 
                modification_type, 
                target_audience, 
                style_preference
            )
            
            # Step 3: Create comprehensive result
            result = {
                'success': True,
                'original_content': {
                    'text': original_text,
                    'word_count': len(original_text.split()),
                    'character_count': len(original_text),
                    'estimated_duration_minutes': len(original_text.split()) / 150  # Average speaking rate
                },
                'content_analysis': content_analysis,
                'rewritten_content': rewritten_content,
                'modification_summary': {
                    'type': modification_type,
                    'target_audience': target_audience,
                    'style_preference': style_preference,
                    'processing_timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            }
            
            # Step 4: Save results
            await self._save_rewriting_results(result)
            
            logger.info("Content analysis and rewriting completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in content analysis and rewriting: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
    
    async def _analyze_content_structure(self, text: str) -> Dict:
        """Analyze the structure and characteristics of the content"""
        try:
            # Basic text analysis
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Word frequency analysis
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 2:  # Skip very short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Content complexity analysis
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            complexity_score = self._calculate_complexity_score(text, avg_sentence_length)
            
            # Topic identification
            topics = self._identify_main_topics(text)
            
            return {
                'text_statistics': {
                    'total_sentences': len(sentences),
                    'total_words': len(words),
                    'average_sentence_length': round(avg_sentence_length, 2),
                    'complexity_score': complexity_score,
                    'readability_level': self._get_readability_level(complexity_score)
                },
                'content_topics': topics,
                'key_phrases': [word for word, freq in top_keywords[:5]],
                'content_structure': {
                    'has_introduction': self._detect_introduction(text),
                    'has_conclusion': self._detect_conclusion(text),
                    'main_sections': self._identify_sections(text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in content structure analysis: {e}")
            return {'error': f'Content analysis failed: {str(e)}'}
    
    async def _generate_rewritten_content(self, original_text: str, 
                                        analysis: Dict, 
                                        modification_type: str,
                                        target_audience: str,
                                        style_preference: str) -> Dict:
        """Generate rewritten content based on analysis and preferences"""
        try:
            # Apply modification based on type
            if modification_type == "enhance":
                rewritten_text = await self._enhance_content(original_text, analysis, target_audience, style_preference)
            elif modification_type == "simplify":
                rewritten_text = await self._simplify_content(original_text, analysis, target_audience)
            elif modification_type == "formalize":
                rewritten_text = await self._formalize_content(original_text, analysis, style_preference)
            elif modification_type == "casual":
                rewritten_text = await self._casualize_content(original_text, analysis)
            else:
                rewritten_text = await self._enhance_content(original_text, analysis, target_audience, style_preference)
            
            # Calculate improvement metrics
            improvement_metrics = self._calculate_improvement_metrics(original_text, rewritten_text, analysis)
            
            return {
                'text': rewritten_text,
                'word_count': len(rewritten_text.split()),
                'character_count': len(rewritten_text),
                'improvement_metrics': improvement_metrics,
                'modification_applied': modification_type,
                'style_applied': style_preference
            }
            
        except Exception as e:
            logger.error(f"Error in content generation: {e}")
            return {'error': f'Content generation failed: {str(e)}'}
    
    async def _enhance_content(self, text: str, analysis: Dict, target_audience: str, style_preference: str) -> str:
        """Enhance content while maintaining original meaning"""
        try:
            # Split into sentences for processing
            sentences = re.split(r'[.!?]+', text)
            enhanced_sentences = []
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                    
                # Apply enhancement based on style preference
                if style_preference == "professional":
                    enhanced = self._make_professional(sentence.strip())
                elif style_preference == "academic":
                    enhanced = self._make_academic(sentence.strip())
                elif style_preference == "conversational":
                    enhanced = self._make_conversational(sentence.strip())
                else:
                    enhanced = self._make_professional(sentence.strip())
                
                enhanced_sentences.append(enhanced)
            
            # Join sentences with proper punctuation
            enhanced_text = '. '.join(enhanced_sentences) + '.'
            
            # Apply target audience adjustments
            if target_audience == "technical":
                enhanced_text = self._add_technical_clarity(enhanced_text)
            elif target_audience == "casual":
                enhanced_text = self._add_casual_elements(enhanced_text)
            
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Error in content enhancement: {e}")
            return text  # Return original if enhancement fails
    
    async def _simplify_content(self, text: str, analysis: Dict, target_audience: str) -> str:
        """Simplify content for better understanding"""
        try:
            # Break down complex sentences
            sentences = re.split(r'[.!?]+', text)
            simplified_sentences = []
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                # Split long sentences
                if len(sentence.split()) > 20:
                    parts = self._break_long_sentence(sentence)
                    simplified_sentences.extend(parts)
                else:
                    simplified_sentences.append(sentence.strip())
            
            simplified_text = '. '.join(simplified_sentences) + '.'
            
            # Replace complex words with simpler alternatives
            simplified_text = self._replace_complex_words(simplified_text)
            
            return simplified_text
            
        except Exception as e:
            logger.error(f"Error in content simplification: {e}")
            return text
    
    async def _formalize_content(self, text: str, analysis: Dict, style_preference: str) -> str:
        """Make content more formal and professional"""
        try:
            # Apply formal language patterns
            formalized_text = text
            
            # Replace casual phrases with formal ones
            formal_replacements = {
                r'\b(okay|ok)\b': 'alright',
                r'\b(yeah|yep)\b': 'yes',
                r'\b(nope|nah)\b': 'no',
                r'\b(hey|hi)\b': 'hello',
                r'\b(awesome|cool)\b': 'excellent',
                r'\b(bad|terrible)\b': 'unfavorable',
                r'\b(good|great)\b': 'excellent',
                r'\b(thing|stuff)\b': 'element',
                r'\b(big|huge)\b': 'significant',
                r'\b(small|tiny)\b': 'minimal'
            }
            
            for pattern, replacement in formal_replacements.items():
                formalized_text = re.sub(pattern, replacement, formalized_text, flags=re.IGNORECASE)
            
            # Improve sentence structure
            sentences = re.split(r'[.!?]+', formalized_text)
            improved_sentences = []
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                improved = self._improve_sentence_structure(sentence.strip())
                improved_sentences.append(improved)
            
            formalized_text = '. '.join(improved_sentences) + '.'
            
            return formalized_text
            
        except Exception as e:
            logger.error(f"Error in content formalization: {e}")
            return text
    
    async def _casualize_content(self, text: str, analysis: Dict) -> str:
        """Make content more casual and conversational"""
        try:
            # Apply casual language patterns
            casualized_text = text
            
            # Replace formal phrases with casual ones
            casual_replacements = {
                r'\b(nevertheless|however)\b': 'but',
                r'\b(furthermore|additionally)\b': 'also',
                r'\b(therefore|thus)\b': 'so',
                r'\b(consequently|as a result)\b': 'so',
                r'\b(utilize|utilization)\b': 'use',
                r'\b(implement\w*)\b': 'use',
                r'\b(approximately)\b': 'about',
                r'\b(subsequently)\b': 'then',
                r'\b(nevertheless)\b': 'still',
                r'\b(consequently)\b': 'so'
            }
            
            for pattern, replacement in casual_replacements.items():
                casualized_text = re.sub(pattern, replacement, casualized_text, flags=re.IGNORECASE)
            
            # Add conversational elements
            casualized_text = self._add_conversational_elements(casualized_text)
            
            return casualized_text
            
        except Exception as e:
            logger.error(f"Error in content casualization: {e}")
            return text
    
    def _calculate_complexity_score(self, text: str, avg_sentence_length: float) -> float:
        """Calculate content complexity score"""
        try:
            # Factors: sentence length, word length, unique words ratio
            words = text.split()
            unique_words = len(set(words))
            total_words = len(words)
            
            # Average word length
            avg_word_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0
            
            # Complexity formula (0-100 scale)
            complexity = (
                (avg_sentence_length / 20) * 30 +  # Sentence length factor
                (avg_word_length / 8) * 40 +       # Word length factor
                (unique_words / total_words) * 30  # Vocabulary diversity
            )
            
            return min(100, max(0, complexity))
            
        except Exception as e:
            logger.error(f"Error calculating complexity score: {e}")
            return 50.0
    
    def _get_readability_level(self, complexity_score: float) -> str:
        """Get readability level based on complexity score"""
        if complexity_score < 30:
            return "Easy"
        elif complexity_score < 60:
            return "Moderate"
        else:
            return "Advanced"
    
    def _identify_main_topics(self, text: str) -> List[str]:
        """Identify main topics from the content"""
        try:
            # Simple keyword-based topic identification
            topics = []
            
            # Common topic indicators
            topic_indicators = {
                'data_structures': ['data structure', 'algorithm', 'array', 'linked list', 'tree', 'graph'],
                'programming': ['code', 'programming', 'coding', 'software', 'development'],
                'learning': ['learn', 'study', 'practice', 'master', 'understand', 'knowledge'],
                'interview': ['interview', 'job', 'career', 'employment', 'position'],
                'problem_solving': ['problem', 'solve', 'solution', 'approach', 'method']
            }
            
            text_lower = text.lower()
            for topic, keywords in topic_indicators.items():
                if any(keyword in text_lower for keyword in keywords):
                    topics.append(topic.replace('_', ' ').title())
            
            return topics[:3]  # Return top 3 topics
            
        except Exception as e:
            logger.error(f"Error identifying topics: {e}")
            return ["General"]
    
    def _detect_introduction(self, text: str) -> bool:
        """Detect if content has an introduction"""
        try:
            # Check first few sentences for introduction indicators
            sentences = re.split(r'[.!?]+', text)[:3]
            intro_indicators = ['welcome', 'introduction', 'overview', 'guide', 'tutorial', 'learn']
            
            first_sentences = ' '.join(sentences).lower()
            return any(indicator in first_sentences for indicator in intro_indicators)
            
        except Exception as e:
            logger.error(f"Error detecting introduction: {e}")
            return False
    
    def _detect_conclusion(self, text: str) -> bool:
        """Detect if content has a conclusion"""
        try:
            # Check last few sentences for conclusion indicators
            sentences = re.split(r'[.!?]+', text)[-3:]
            conclusion_indicators = ['conclusion', 'summary', 'finally', 'in conclusion', 'wrap up', 'end']
            
            last_sentences = ' '.join(sentences).lower()
            return any(indicator in last_sentences for indicator in conclusion_indicators)
            
        except Exception as e:
            logger.error(f"Error detecting conclusion: {e}")
            return False
    
    def _identify_sections(self, text: str) -> List[str]:
        """Identify main sections in the content"""
        try:
            # Simple section identification based on content breaks
            sections = []
            
            # Look for section indicators
            section_patterns = [
                r'\b(step \d+)\b',
                r'\b(part \d+)\b',
                r'\b(section \d+)\b',
                r'\b(phase \d+)\b',
                r'\b(tip \d+)\b'
            ]
            
            for pattern in section_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                sections.extend(matches)
            
            return sections[:5]  # Return top 5 sections
            
        except Exception as e:
            logger.error(f"Error identifying sections: {e}")
            return []
    
    def _make_professional(self, sentence: str) -> str:
        """Make a sentence more professional"""
        try:
            # Basic professional improvements
            improved = sentence
            
            # Capitalize first letter
            if improved and improved[0].islower():
                improved = improved[0].upper() + improved[1:]
            
            # Ensure proper punctuation
            if not improved.endswith(('.', '!', '?')):
                improved += '.'
            
            return improved
            
        except Exception as e:
            logger.error(f"Error making sentence professional: {e}")
            return sentence
    
    def _make_academic(self, sentence: str) -> str:
        """Make a sentence more academic"""
        try:
            # Basic academic improvements
            improved = sentence
            
            # Add academic connectors if appropriate
            academic_connectors = ['Furthermore,', 'Moreover,', 'Additionally,', 'In addition,', 'Furthermore,', 'Moreover,']
            
            # Ensure proper punctuation
            if not improved.endswith(('.', '!', '?')):
                improved += '.'
            
            return improved
            
        except Exception as e:
            logger.error(f"Error making sentence academic: {e}")
            return sentence
    
    def _make_conversational(self, sentence: str) -> str:
        """Make a sentence more conversational"""
        try:
            # Basic conversational improvements
            improved = sentence
            
            # Ensure proper punctuation
            if not improved.endswith(('.', '!', '?')):
                improved += '.'
            
            return improved
            
        except Exception as e:
            logger.error(f"Error making sentence conversational: {e}")
            return sentence
    
    def _add_technical_clarity(self, text: str) -> str:
        """Add technical clarity to content"""
        try:
            # Add technical explanations where appropriate
            technical_additions = {
                r'\b(algorithm)\b': 'algorithm (step-by-step procedure)',
                r'\b(data structure)\b': 'data structure (organized way to store data)',
                r'\b(complexity)\b': 'complexity (efficiency measure)'
            }
            
            for pattern, addition in technical_additions.items():
                text = re.sub(pattern, addition, text, flags=re.IGNORECASE)
            
            return text
            
        except Exception as e:
            logger.error(f"Error adding technical clarity: {e}")
            return text
    
    def _add_casual_elements(self, text: str) -> str:
        """Add casual elements to content"""
        try:
            # Add casual connectors
            casual_connectors = ['You know,', 'Well,', 'So,', 'Now,', 'Hey,', 'Look,']
            
            # Add to some sentences randomly
            sentences = re.split(r'[.!?]+', text)
            modified_sentences = []
            
            for i, sentence in enumerate(sentences):
                if sentence.strip() and i % 3 == 0:  # Every third sentence
                    connector = casual_connectors[i % len(casual_connectors)]
                    modified_sentences.append(f"{connector} {sentence.strip()}")
                else:
                    modified_sentences.append(sentence.strip())
            
            return '. '.join(modified_sentences) + '.'
            
        except Exception as e:
            logger.error(f"Error adding casual elements: {e}")
            return text
    
    def _break_long_sentence(self, sentence: str) -> List[str]:
        """Break a long sentence into shorter parts"""
        try:
            # Simple sentence breaking based on conjunctions
            conjunctions = [' and ', ' but ', ' or ', ' so ', ' because ', ' however ']
            
            parts = [sentence]
            for conjunction in conjunctions:
                new_parts = []
                for part in parts:
                    if conjunction in part:
                        split_parts = part.split(conjunction)
                        for i, split_part in enumerate(split_parts):
                            if i > 0:
                                new_parts.append(conjunction.strip() + split_part)
                            else:
                                new_parts.append(split_part)
                    else:
                        new_parts.append(part)
                parts = new_parts
            
            return [part.strip() for part in parts if part.strip()]
            
        except Exception as e:
            logger.error(f"Error breaking long sentence: {e}")
            return [sentence]
    
    def _replace_complex_words(self, text: str) -> str:
        """Replace complex words with simpler alternatives"""
        try:
            # Simple word replacement dictionary
            word_replacements = {
                'utilize': 'use',
                'implement': 'use',
                'facilitate': 'help',
                'subsequently': 'then',
                'consequently': 'so',
                'nevertheless': 'still',
                'approximately': 'about',
                'demonstrate': 'show',
                'indicate': 'show',
                'establish': 'set up'
            }
            
            for complex_word, simple_word in word_replacements.items():
                text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
            
            return text
            
        except Exception as e:
            logger.error(f"Error replacing complex words: {e}")
            return text
    
    def _improve_sentence_structure(self, sentence: str) -> str:
        """Improve sentence structure"""
        try:
            # Basic sentence structure improvements
            improved = sentence
            
            # Ensure proper capitalization
            if improved and improved[0].islower():
                improved = improved[0].upper() + improved[1:]
            
            # Ensure proper punctuation
            if not improved.endswith(('.', '!', '?')):
                improved += '.'
            
            return improved
            
        except Exception as e:
            logger.error(f"Error improving sentence structure: {e}")
            return sentence
    
    def _add_conversational_elements(self, text: str) -> str:
        """Add conversational elements to content"""
        try:
            # Add conversational connectors
            conversational_elements = ['You see,', 'Well,', 'So,', 'Now,', 'Hey,', 'Look,']
            
            # Add to some sentences
            sentences = re.split(r'[.!?]+', text)
            modified_sentences = []
            
            for i, sentence in enumerate(sentences):
                if sentence.strip() and i % 4 == 0:  # Every fourth sentence
                    element = conversational_elements[i % len(conversational_elements)]
                    modified_sentences.append(f"{element} {sentence.strip()}")
                else:
                    modified_sentences.append(sentence.strip())
            
            return '. '.join(modified_sentences) + '.'
            
        except Exception as e:
            logger.error(f"Error adding conversational elements: {e}")
            return text
    
    def _calculate_improvement_metrics(self, original_text: str, rewritten_text: str, analysis: Dict) -> Dict:
        """Calculate improvement metrics between original and rewritten content"""
        try:
            original_words = len(original_text.split())
            rewritten_words = len(rewritten_text.split())
            
            # Calculate various metrics
            word_count_change = rewritten_words - original_words
            word_count_change_percent = (word_count_change / original_words * 100) if original_words > 0 else 0
            
            # Readability improvement (simplified)
            original_complexity = analysis.get('text_statistics', {}).get('complexity_score', 50)
            rewritten_complexity = self._calculate_complexity_score(rewritten_text, 
                                                                 len(rewritten_text.split()) / max(1, len(re.split(r'[.!?]+', rewritten_text))))
            
            complexity_improvement = original_complexity - rewritten_complexity
            
            return {
                'word_count_change': word_count_change,
                'word_count_change_percent': round(word_count_change_percent, 2),
                'complexity_improvement': round(complexity_improvement, 2),
                'readability_improvement': 'Improved' if complexity_improvement > 0 else 'Maintained' if complexity_improvement == 0 else 'Adjusted'
            }
            
        except Exception as e:
            logger.error(f"Error calculating improvement metrics: {e}")
            return {'error': f'Metrics calculation failed: {str(e)}'}
    
    async def _save_rewriting_results(self, result: Dict):
        """Save rewriting results to file"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"content_rewriting_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Rewriting results saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving rewriting results: {e}")

    async def analyze_content_similarity(self, original_text: str, comparison_text: str) -> Dict:
        """Analyze similarity between two pieces of content"""
        try:
            logger.info("Starting content similarity analysis")
            
            # Calculate basic similarity metrics
            similarity_score = self._calculate_text_similarity(original_text, comparison_text)
            
            # Identify common phrases and patterns
            common_phrases = self._find_common_phrases(original_text, comparison_text)
            
            # Calculate word overlap
            word_overlap = self._calculate_word_overlap(original_text, comparison_text)
            
            # Determine similarity level
            similarity_level = self._get_similarity_level(similarity_score)
            
            result = {
                'similarity_score': round(similarity_score, 2),
                'similarity_level': similarity_level,
                'word_overlap_percentage': round(word_overlap, 2),
                'common_phrases': common_phrases,
                'risk_assessment': self._assess_similarity_risk(similarity_score),
                'recommendations': self._get_similarity_recommendations(similarity_score)
            }
            
            logger.info(f"Content similarity analysis completed. Score: {similarity_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error in content similarity analysis: {e}")
            return {'error': f'Similarity analysis failed: {str(e)}'}

    async def check_plagiarism(self, text: str) -> Dict:
        """Check content for potential plagiarism"""
        try:
            logger.info("Starting plagiarism check")
            
            # Basic plagiarism indicators
            plagiarism_indicators = self._check_plagiarism_indicators(text)
            
            # Content uniqueness analysis
            uniqueness_score = self._calculate_content_uniqueness(text)
            
            # Risk assessment
            risk_level = self._assess_plagiarism_risk(uniqueness_score, plagiarism_indicators)
            
            result = {
                'uniqueness_score': round(uniqueness_score, 2),
                'risk_level': risk_level,
                'plagiarism_indicators': plagiarism_indicators,
                'recommendations': self._get_plagiarism_recommendations(risk_level),
                'compliance_status': 'compliant' if risk_level == 'low' else 'review_required'
            }
            
            logger.info(f"Plagiarism check completed. Risk level: {risk_level}")
            return result
            
        except Exception as e:
            logger.error(f"Error in plagiarism check: {e}")
            return {'error': f'Plagiarism check failed: {str(e)}'}

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using basic metrics"""
        try:
            # Convert to lowercase and split into words
            words1 = set(re.findall(r'\b\w+\b', text1.lower()))
            words2 = set(re.findall(r'\b\w+\b', text2.lower()))
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            similarity = intersection / union
            return similarity * 100  # Convert to percentage
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0

    def _find_common_phrases(self, text1: str, text2: str) -> List[str]:
        """Find common phrases between two texts"""
        try:
            # Extract phrases (3-5 word sequences)
            phrases1 = self._extract_phrases(text1)
            phrases2 = self._extract_phrases(text2)
            
            # Find common phrases
            common = set(phrases1).intersection(set(phrases2))
            
            # Return most relevant common phrases
            return list(common)[:10]
            
        except Exception as e:
            logger.error(f"Error finding common phrases: {e}")
            return []

    def _extract_phrases(self, text: str) -> List[str]:
        """Extract phrases from text"""
        try:
            words = text.split()
            phrases = []
            
            # Extract 3-5 word phrases
            for i in range(len(words) - 2):
                for length in range(3, min(6, len(words) - i + 1)):
                    phrase = ' '.join(words[i:i + length])
                    if len(phrase) > 10:  # Only meaningful phrases
                        phrases.append(phrase)
            
            return phrases
            
        except Exception as e:
            logger.error(f"Error extracting phrases: {e}")
            return []

    def _calculate_word_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap percentage"""
        try:
            words1 = set(re.findall(r'\b\w+\b', text1.lower()))
            words2 = set(re.findall(r'\b\w+\b', text2.lower()))
            
            if not words1 or not words2:
                return 0.0
            
            overlap = len(words1.intersection(words2))
            total_unique = len(words1.union(words2))
            
            return (overlap / total_unique) * 100
            
        except Exception as e:
            logger.error(f"Error calculating word overlap: {e}")
            return 0.0

    def _get_similarity_level(self, similarity_score: float) -> str:
        """Get similarity level based on score"""
        if similarity_score < 20:
            return "Very Low"
        elif similarity_score < 40:
            return "Low"
        elif similarity_score < 60:
            return "Moderate"
        elif similarity_score < 80:
            return "High"
        else:
            return "Very High"

    def _assess_similarity_risk(self, similarity_score: float) -> str:
        """Assess risk based on similarity score"""
        if similarity_score < 30:
            return "Low Risk"
        elif similarity_score < 60:
            return "Medium Risk"
        else:
            return "High Risk"

    def _get_similarity_recommendations(self, similarity_score: float) -> List[str]:
        """Get recommendations based on similarity score"""
        recommendations = []
        
        if similarity_score > 70:
            recommendations.extend([
                "Consider significant content restructuring",
                "Review for potential copyright issues",
                "Ensure proper attribution if using similar content"
            ])
        elif similarity_score > 40:
            recommendations.extend([
                "Modify similar sections for better differentiation",
                "Add unique perspectives and examples",
                "Consider content reorganization"
            ])
        else:
            recommendations.extend([
                "Content appears sufficiently unique",
                "Continue with current approach",
                "Monitor for any unintended similarities"
            ])
        
        return recommendations

    def _check_plagiarism_indicators(self, text: str) -> Dict:
        """Check for common plagiarism indicators"""
        try:
            indicators = {
                'excessive_quotes': False,
                'inconsistent_writing_style': False,
                'sudden_topic_shifts': False,
                'unusual_vocabulary': False
            }
            
            # Check for excessive quotes
            quote_count = text.count('"') + text.count("'")
            if quote_count > len(text.split()) * 0.1:  # More than 10% quotes
                indicators['excessive_quotes'] = True
            
            # Check for inconsistent writing style (simplified)
            sentences = re.split(r'[.!?]+', text)
            if len(sentences) > 1:
                first_half = ' '.join(sentences[:len(sentences)//2])
                second_half = ' '.join(sentences[len(sentences)//2:])
                
                # Compare complexity
                complexity1 = self._calculate_complexity_score(first_half, len(first_half.split()) / max(1, len(re.split(r'[.!?]+', first_half))))
                complexity2 = self._calculate_complexity_score(second_half, len(second_half.split()) / max(1, len(re.split(r'[.!?]+', second_half))))
                
                if abs(complexity1 - complexity2) > 30:
                    indicators['inconsistent_writing_style'] = True
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error checking plagiarism indicators: {e}")
            return {}

    def _calculate_content_uniqueness(self, text: str) -> float:
        """Calculate content uniqueness score"""
        try:
            # Simple uniqueness calculation based on word variety
            words = re.findall(r'\b\w+\b', text.lower())
            unique_words = len(set(words))
            total_words = len(words)
            
            if total_words == 0:
                return 0.0
            
            # Uniqueness based on vocabulary diversity
            uniqueness = (unique_words / total_words) * 100
            
            # Adjust for content length (longer content tends to have more variety)
            if total_words > 100:
                uniqueness = min(100, uniqueness * 1.1)
            
            return uniqueness
            
        except Exception as e:
            logger.error(f"Error calculating content uniqueness: {e}")
            return 50.0

    def _assess_plagiarism_risk(self, uniqueness_score: float, indicators: Dict) -> str:
        """Assess overall plagiarism risk"""
        risk_score = 0
        
        # Base risk from uniqueness
        if uniqueness_score < 30:
            risk_score += 3
        elif uniqueness_score < 50:
            risk_score += 2
        elif uniqueness_score < 70:
            risk_score += 1
        
        # Add risk from indicators
        for indicator, value in indicators.items():
            if value:
                risk_score += 1
        
        # Determine risk level
        if risk_score <= 1:
            return "Low"
        elif risk_score <= 3:
            return "Medium"
        else:
            return "High"

    def _get_plagiarism_recommendations(self, risk_level: str) -> List[str]:
        """Get recommendations based on plagiarism risk level"""
        if risk_level == "Low":
            return [
                "Content appears original and unique",
                "Continue with current approach",
                "Maintain good writing practices"
            ]
        elif risk_level == "Medium":
            return [
                "Review content for potential similarities",
                "Add more unique perspectives and examples",
                "Consider content restructuring if needed"
            ]
        else:  # High risk
            return [
                "Significant review required",
                "Consider complete content rewrite",
                "Ensure proper attribution for any referenced content",
                "Consult with content creation guidelines"
            ]

# Create global instance
content_rewriter = ContentRewriter() 