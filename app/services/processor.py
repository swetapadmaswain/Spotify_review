from loguru import logger
from app.models.vector_database import VectorDatabase
from app.models.knowledge_base import KnowledgeBase
from app.services.rag_system import RAGSystem
from app.services.llm_pipeline import LLMProcessingPipeline
from app.database.connection import SessionLocal
from app.database.models import ProcessedReview, SentimentAnalysis, TopicAnalysis, EntityAnalysis

class BatchProcessor:
    """Batch process reviews through the AI pipeline"""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.llm_pipeline = LLMProcessingPipeline()
        self.db = SessionLocal()
        logger.info("BatchProcessor initialized")

    def process_batch(self, batch_size=500):
        """Fetch unprocessed reviews and run them through the analysis pipeline"""
        try:
            # Fetch reviews that haven't been processed for sentiment yet
            reviews = self.db.query(ProcessedReview).filter(
                ProcessedReview.id.notin_(
                    self.db.query(SentimentAnalysis.review_id)
                )
            ).limit(batch_size).all()
            
            if not reviews:
                logger.info("No unprocessed reviews found.")
                return 0

            logger.info(f"Processing batch of {len(reviews)} reviews")
            
            for review in reviews:
                # 1. Generate embeddings and store in Vector DB
                metadata = {
                    "source": review.source or "unknown",
                    "author": review.author or "anonymous",
                    "date": str(review.created_at) if review.created_at else ""
                }
                self.vector_db.add_embeddings(
                    texts=[review.content],
                    metadatas=[metadata],
                    ids=[str(review.id)]
                )
                
                # 2. Run analysis via LLM Pipeline
                result = self.llm_pipeline.process_text(review.content)
                
                # 3. Store results in Database
                
                # Sentiment
                sentiment_data = result.get('sentiment', {})
                sentiment_record = SentimentAnalysis(
                    review_id=review.id,
                    sentiment=sentiment_data.get('sentiment'),
                    confidence=sentiment_data.get('confidence'),
                    emotion=sentiment_data.get('emotion'),
                    intensity=sentiment_data.get('intensity')
                )
                self.db.add(sentiment_record)
                
                # Topics
                topic_data = result.get('topics', {})
                topic_record = TopicAnalysis(
                    review_id=review.id,
                    primary_topic=topic_data.get('primary_topic'),
                    secondary_topics=topic_data.get('secondary_topics', []),
                    relevance_scores=topic_data.get('topic_relevance_scores', {})
                )
                self.db.add(topic_record)
                
                # Entities
                entity_data = result.get('entities', {})
                entity_record = EntityAnalysis(
                    review_id=review.id,
                    entities=entity_data,
                    entity_types={}  # Future expansion if specific typing is added
                )
                self.db.add(entity_record)
                
            self.db.commit()
            logger.info("Batch processing completed and saved to database.")
            return len(reviews)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing batch: {e}")
            raise
        finally:
            self.db.close()


class RealTimeProcessor:
    """Analyze real-time reviews using RAG and LLMs"""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.knowledge_base = KnowledgeBase()
        self.rag_system = RAGSystem(self.vector_db, self.knowledge_base)
        logger.info("RealTimeProcessor initialized")
    
    def analyze_new_review(self, review_text: str):
        """Immediately analyze a new review and return insights"""
        try:
            logger.info("Analyzing new review in real-time...")
            
            # Step 1: Retrieve context based on the new review
            context = self.rag_system.retrieval.retrieve_context(review_text)
            
            # Step 2: Augment query
            augmented_query = self.rag_system.augmentation.augment_query(review_text, context)
            
            # Step 3: Generate insights
            insights = self.rag_system.generation.generate_insights(review_text, augmented_query)
            
            return {
                "review_text": review_text,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error in RealTimeProcessor: {e}")
            return {"error": str(e)}
