from typing import Dict, List, Optional, Any
from loguru import logger
from config.settings import settings

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai not installed")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic not installed")


class SentimentAnalyzer:
    """Analyze sentiment of user feedback using LLM"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of user feedback
        
        Args:
            text: User feedback text
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            prompt = f"""
Analyze the sentiment of this user feedback:

"{text}"

Return your response as JSON with the following structure:
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.95,
    "emotion": "joy/frustration/disappointment/satisfaction/anger",
    "intensity": "low/medium/high",
    "key_phrases": ["phrase1", "phrase2"]
}}
"""
            
            try:
                if self.provider == "openai" and OPENAI_AVAILABLE:
                    response = self._analyze_with_openai(prompt)
                elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
                    response = self._analyze_with_anthropic(prompt)
                else:
                    response = self._analyze_fallback(text)
            except Exception:
                logger.warning("LLM API failed for sentiment, using heuristic fallback")
                response = self._analyze_fallback(text)
            
            logger.info(f"Sentiment analysis completed: {response.get('sentiment', 'unknown')}")
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return self._analyze_fallback(text)
    
    def _analyze_with_openai(self, prompt: str) -> Dict:
        """Analyze using OpenAI"""
        try:
            import json
            openai.api_key = settings.openai_api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_fallback_response(content)
                
        except Exception as e:
            logger.error(f"OpenAI sentiment analysis error: {e}")
            raise
    
    def _analyze_with_anthropic(self, prompt: str) -> Dict:
        """Analyze using Anthropic Claude"""
        try:
            import json
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            
            # Parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_fallback_response(content)
                
        except Exception as e:
            logger.error(f"Anthropic sentiment analysis error: {e}")
            raise
    
    def _analyze_fallback(self, text: str) -> Dict:
        """Fallback sentiment analysis using simple heuristics"""
        text_lower = text.lower()
        
        positive_words = ['good', 'great', 'excellent', 'love', 'amazing', 'perfect', 'awesome', 'happy']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'worst', 'disappointed', 'frustrated', 'angry']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            emotion = 'satisfaction'
        elif negative_count > positive_count:
            sentiment = 'negative'
            emotion = 'frustration'
        else:
            sentiment = 'neutral'
            emotion = 'neutral'
        
        return {
            'sentiment': sentiment,
            'confidence': 0.5,
            'emotion': emotion,
            'intensity': 'medium',
            'key_phrases': []
        }
    
    def _parse_fallback_response(self, content: str) -> Dict:
        """Parse non-JSON response"""
        return {
            'sentiment': 'neutral',
            'confidence': 0.5,
            'emotion': 'unknown',
            'intensity': 'medium',
            'key_phrases': [],
            'raw_response': content
        }


class TopicModeler:
    """Extract topics from user feedback using LLM"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
    
    def extract_topics(self, text: str) -> Dict[str, Any]:
        """
        Extract key topics from user feedback
        
        Args:
            text: User feedback text
            
        Returns:
            Dictionary with topic analysis results
        """
        try:
            prompt = f"""
Extract key topics from this feedback:

"{text}"

Return your response as JSON with the following structure:
{{
    "primary_topic": "recommendations",
    "secondary_topics": ["ui", "performance"],
    "topic_relevance_scores": {{"recommendations": 0.9, "ui": 0.6, "performance": 0.4}},
    "category": "feature/bug/content/general"
}}
"""
            
            try:
                if self.provider == "openai" and OPENAI_AVAILABLE:
                    response = self._extract_with_openai(prompt)
                elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
                    response = self._extract_with_anthropic(prompt)
                else:
                    response = self._extract_fallback(text)
            except Exception:
                logger.warning("LLM API failed for topics, using heuristic fallback")
                response = self._extract_fallback(text)
            
            logger.info(f"Topic extraction completed: {response.get('primary_topic', 'unknown')}")
            return response
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return self._extract_fallback(text)
    
    def _extract_with_openai(self, prompt: str) -> Dict:
        """Extract using OpenAI"""
        try:
            import json
            openai.api_key = settings.openai_api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a topic modeling expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_fallback_response(content)
                
        except Exception as e:
            logger.error(f"OpenAI topic extraction error: {e}")
            raise
    
    def _extract_with_anthropic(self, prompt: str) -> Dict:
        """Extract using Anthropic Claude"""
        try:
            import json
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_fallback_response(content)
                
        except Exception as e:
            logger.error(f"Anthropic topic extraction error: {e}")
            raise
    
    def _extract_fallback(self, text: str) -> Dict:
        """Fallback topic extraction using simple heuristics"""
        text_lower = text.lower()
        
        topic_keywords = {
            'recommendations': ['recommend', 'suggestion', 'discover', 'playlist'],
            'ui': ['interface', 'button', 'screen', 'navigation', 'design'],
            'performance': ['slow', 'crash', 'bug', 'lag', 'freeze'],
            'content': ['song', 'artist', 'album', 'music', 'audio'],
            'account': ['login', 'password', 'subscription', 'premium'],
            'feature': ['feature', 'function', 'option', 'setting']
        }
        
        scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[topic] = score / len(keywords)
        
        if scores:
            primary_topic = max(scores.keys(), key=lambda k: scores[k])
            secondary_topics = [k for k in sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[1:3]]
        else:
            primary_topic = 'general'
            secondary_topics = []
        
        return {
            'primary_topic': primary_topic,
            'secondary_topics': secondary_topics,
            'topic_relevance_scores': scores,
            'category': 'general'
        }
    
    def _parse_fallback_response(self, content: str) -> Dict:
        """Parse non-JSON response"""
        return {
            'primary_topic': 'general',
            'secondary_topics': [],
            'topic_relevance_scores': {},
            'category': 'general',
            'raw_response': content
        }


class EntityExtractor:
    """Extract entities from user feedback using LLM"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from user feedback
        
        Args:
            text: User feedback text
            
        Returns:
            Dictionary with extracted entities
        """
        try:
            prompt = f"""
Extract entities from this feedback:

"{text}"

Identify and return as JSON:
{{
    "music_features": ["playlist", "radio", "recommendations"],
    "user_actions": ["skip", "save", "share", "like"],
    "emotions": ["frustrated", "happy", "bored", "excited"],
    "technical_terms": ["algorithm", "UI", "bug", "crash"],
    "platform_mentions": ["ios", "android", "desktop", "web"]
}}
"""
            
            try:
                if self.provider == "openai" and OPENAI_AVAILABLE:
                    response = self._extract_with_openai(prompt)
                elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
                    response = self._extract_with_anthropic(prompt)
                else:
                    response = self._extract_fallback(text)
            except Exception:
                logger.warning("LLM API failed for entities, using heuristic fallback")
                response = self._extract_fallback(text)
            
            logger.info(f"Entity extraction completed")
            return response
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return self._extract_fallback(text)
    
    def _extract_with_openai(self, prompt: str) -> Dict:
        """Extract using OpenAI"""
        try:
            import json
            openai.api_key = settings.openai_api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an entity extraction expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_fallback_response(content)
                
        except Exception as e:
            logger.error(f"OpenAI entity extraction error: {e}")
            raise
    
    def _extract_with_anthropic(self, prompt: str) -> Dict:
        """Extract using Anthropic Claude"""
        try:
            import json
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_fallback_response(content)
                
        except Exception as e:
            logger.error(f"Anthropic entity extraction error: {e}")
            raise
    
    def _extract_fallback(self, text: str) -> Dict:
        """Fallback entity extraction using simple heuristics"""
        text_lower = text.lower()
        
        entity_patterns = {
            'music_features': ['playlist', 'radio', 'discover weekly', 'release radar', 'shuffle', 'repeat'],
            'user_actions': ['skip', 'save', 'share', 'like', 'follow', 'unfollow', 'download'],
            'emotions': ['frustrated', 'happy', 'bored', 'excited', 'annoyed', 'satisfied', 'disappointed'],
            'technical_terms': ['algorithm', 'ui', 'bug', 'crash', 'lag', 'freeze', 'loading'],
            'platform_mentions': ['ios', 'android', 'desktop', 'web', 'iphone', 'ipad']
        }
        
        entities = {}
        for entity_type, patterns in entity_patterns.items():
            found = [pattern for pattern in patterns if pattern in text_lower]
            entities[entity_type] = found
        
        return entities
    
    def _parse_fallback_response(self, content: str) -> Dict:
        """Parse non-JSON response"""
        return {
            'music_features': [],
            'user_actions': [],
            'emotions': [],
            'technical_terms': [],
            'platform_mentions': [],
            'raw_response': content
        }


class LLMProcessingPipeline:
    """Complete LLM processing pipeline combining sentiment, topic, and entity analysis"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_modeler = TopicModeler()
        self.entity_extractor = EntityExtractor()
        
        logger.info("LLM processing pipeline initialized")
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text through complete LLM pipeline
        
        Args:
            text: User feedback text
            
        Returns:
            Dictionary with all analysis results
        """
        try:
            # Run all analyses
            sentiment = self.sentiment_analyzer.analyze_sentiment(text)
            topics = self.topic_modeler.extract_topics(text)
            entities = self.entity_extractor.extract_entities(text)
            
            # Combine results
            result = {
                'text': text,
                'sentiment': sentiment,
                'topics': topics,
                'entities': entities,
                'processed_at': self._get_timestamp()
            }
            
            logger.info("LLM pipeline processing completed")
            return result
            
        except Exception as e:
            logger.error(f"Error in LLM pipeline: {e}")
            return {
                'text': text,
                'sentiment': {},
                'topics': {},
                'entities': {},
                'error': str(e),
                'processed_at': self._get_timestamp()
            }
    
    def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple texts in batch
        
        Args:
            texts: List of texts to process
            
        Returns:
            List of analysis results
        """
        results = []
        
        for text in texts:
            try:
                result = self.process_text(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing text: {e}")
                results.append({
                    'text': text,
                    'error': str(e),
                    'processed_at': self._get_timestamp()
                })
        
        logger.info(f"Batch processing completed: {len(results)} texts processed")
        return results
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
