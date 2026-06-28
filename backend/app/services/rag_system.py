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


class RetrievalComponent:
    """Component for retrieving relevant context from vector database and knowledge base"""
    
    def __init__(self, vector_db, knowledge_base):
        self.vector_db = vector_db
        self.knowledge_base = knowledge_base
        self.top_k = settings.rag_top_k
    
    def retrieve_context(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve similar reviews and knowledge base context
        
        Args:
            query: Query text
            top_k: Number of results to retrieve (defaults to settings.rag_top_k)
            
        Returns:
            Dictionary with similar reviews and knowledge context
        """
        top_k = top_k or self.top_k
        
        try:
            # Retrieve similar reviews from vector database
            similar_reviews = self.vector_db.query(query, n_results=top_k)
            
            # Retrieve relevant knowledge base documents
            kb_docs = self.knowledge_base.search(query, top_k=top_k)
            
            context = {
                'similar_reviews': similar_reviews,
                'knowledge_context': kb_docs,
                'query': query
            }
            
            logger.info(f"Retrieved context: {len(similar_reviews.get('ids', [[]])[0])} reviews, {len(kb_docs)} KB docs")
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {'similar_reviews': {}, 'knowledge_context': [], 'query': query}


class AugmentationComponent:
    """Component for augmenting queries with retrieved context"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.temperature = settings.rag_temperature
    
    def augment_query(self, query: str, context: Dict[str, Any]) -> str:
        """
        Augment query with retrieved context for better analysis
        
        Args:
            query: Original query
            context: Retrieved context from retrieval component
            
        Returns:
            Augmented query with context
        """
        try:
            # Format similar reviews
            similar_reviews_text = self._format_reviews(context.get('similar_reviews', {}))
            
            # Format knowledge base documents
            kb_context_text = self._format_kb_docs(context.get('knowledge_context', []))
            
            # Create augmented prompt
            augmented_prompt = f"""
Based on the following user feedback context, analyze this query:

Query: {query}

Similar User Feedback:
{similar_reviews_text}

Knowledge Base Context:
{kb_context_text}

Provide insights about:
1. User sentiment
2. Key themes
3. Specific frustrations
4. Suggested improvements
"""
            
            logger.info("Query augmented with context")
            return augmented_prompt
            
        except Exception as e:
            logger.error(f"Error augmenting query: {e}")
            return query
    
    def _format_reviews(self, reviews_data: Dict) -> str:
        """Format retrieved reviews for prompt"""
        if not reviews_data or not reviews_data.get('documents'):
            return "No similar reviews found."
        
        formatted = []
        documents = reviews_data.get('documents', [[]])[0]
        metadatas = reviews_data.get('metadatas', [[]])[0]
        
        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            formatted.append(f"Review {i+1}: {doc[:200]}... (Source: {meta.get('source', 'unknown')})")
        
        return "\n".join(formatted)
    
    def _format_kb_docs(self, kb_docs: List[Dict]) -> str:
        """Format knowledge base documents for prompt"""
        if not kb_docs:
            return "No relevant knowledge base documents found."
        
        formatted = []
        for i, doc in enumerate(kb_docs):
            formatted.append(f"KB Doc {i+1} [{doc.get('category', 'general')}]: {doc.get('content', '')}")
        
        return "\n".join(formatted)


class GenerationComponent:
    """Component for generating insights using LLM"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.provider = settings.llm_provider
        self.model = settings.llm_model
    
    def generate_insights(self, query: str, augmented_context: str) -> Dict[str, Any]:
        """
        Generate comprehensive insights using LLM
        
        Args:
            query: Original query
            augmented_context: Augmented query with context
            
        Returns:
            Dictionary with generated insights
        """
        try:
            prompt = f"""
Generate comprehensive insights for the following analysis:

Query: {query}

Context:
{augmented_context}

Structure your response with:
- Key findings
- Supporting evidence
- Confidence scores (0-1)
- Actionable recommendations

Format your response as JSON with the following structure:
{{
    "key_findings": ["finding1", "finding2"],
    "supporting_evidence": ["evidence1", "evidence2"],
    "confidence_scores": {{"finding1": 0.8, "finding2": 0.9}},
    "actionable_recommendations": ["recommendation1", "recommendation2"]
}}
"""
            
            # Generate response based on provider
            if self.provider == "openai" and OPENAI_AVAILABLE:
                response = self._generate_openai(prompt)
            elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
                response = self._generate_anthropic(prompt)
            else:
                # Fallback to simple response
                response = self._generate_simple(prompt)
            
            logger.info("Insights generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                'key_findings': [],
                'supporting_evidence': [],
                'confidence_scores': {},
                'actionable_recommendations': [],
                'error': str(e)
            }
    
    def _generate_openai(self, prompt: str) -> Dict:
        """Generate using OpenAI"""
        try:
            import json
            openai.api_key = settings.openai_api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert analyst of user feedback for music streaming services."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    'key_findings': [content],
                    'supporting_evidence': [],
                    'confidence_scores': {},
                    'actionable_recommendations': []
                }
                
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    def _generate_anthropic(self, prompt: str) -> Dict:
        """Generate using Anthropic Claude"""
        try:
            import json
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            
            # Try to parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    'key_findings': [content],
                    'supporting_evidence': [],
                    'confidence_scores': {},
                    'actionable_recommendations': []
                }
                
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise
    
    def _generate_simple(self, prompt: str) -> Dict:
        """Simple fallback generation"""
        return {
            'key_findings': ['Analysis requires LLM configuration'],
            'supporting_evidence': [],
            'confidence_scores': {},
            'actionable_recommendations': ['Configure OpenAI or Anthropic API keys']
        }


class RAGSystem:
    """Complete RAG system combining retrieval, augmentation, and generation"""
    
    def __init__(self, vector_db, knowledge_base):
        self.vector_db = vector_db
        self.knowledge_base = knowledge_base
        
        # Initialize components
        self.retrieval = RetrievalComponent(vector_db, knowledge_base)
        
        # Initialize LLM client
        self.llm_client = self._init_llm_client()
        self.augmentation = AugmentationComponent(self.llm_client)
        self.generation = GenerationComponent(self.llm_client)
        
        logger.info("RAG system initialized")
    
    def _init_llm_client(self):
        """Initialize LLM client based on configuration"""
        # This is a placeholder - actual client initialization depends on provider
        return None
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Complete RAG analysis pipeline
        
        Args:
            query: Analysis query
            
        Returns:
            Complete analysis results
        """
        try:
            # Step 1: Retrieve context
            context = self.retrieval.retrieve_context(query)
            
            # Step 2: Augment query
            augmented_query = self.augmentation.augment_query(query, context)
            
            # Step 3: Generate insights
            insights = self.generation.generate_insights(query, augmented_query)
            
            # Combine results
            result = {
                'query': query,
                'context': context,
                'insights': insights,
                'timestamp': self._get_timestamp()
            }
            
            logger.info("RAG analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG analysis: {e}")
            return {
                'query': query,
                'context': {},
                'insights': {},
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def batch_analyze(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple queries in batch
        
        Args:
            queries: List of queries to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        
        for query in queries:
            try:
                result = self.analyze(query)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing query '{query}': {e}")
                results.append({
                    'query': query,
                    'error': str(e),
                    'timestamp': self._get_timestamp()
                })
        
        logger.info(f"Batch analysis completed: {len(results)} queries processed")
        return results
