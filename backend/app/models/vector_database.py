import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
from loguru import logger
from config.settings import settings

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai not installed")


class VectorDatabase:
    """Vector database for storing and querying embeddings using ChromaDB"""
    
    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or settings.vector_db_path
        self.collection_name = settings.vector_collection_name
        self.embedding_dimension = settings.embedding_dimension
        self.embedding_model = settings.embedding_model
        self.local_embedding_model = settings.local_embedding_model
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        # Initialize embedding model
        self.embedding_model_instance = self._init_embedding_model()
        
        logger.info(f"Vector database initialized at {self.persist_directory}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
            return collection
        except:
            # Create new collection
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return collection
    
    def _init_embedding_model(self):
        """Initialize embedding model based on configuration"""
        # Try OpenAI embeddings first
        if OPENAI_AVAILABLE and settings.openai_api_key:
            try:
                openai.api_key = settings.openai_api_key
                logger.info(f"Using OpenAI embedding model: {self.embedding_model}")
                return "openai"
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI embeddings: {e}")
        
        # Fallback to local sentence transformers
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                model = SentenceTransformer(self.local_embedding_model)
                logger.info(f"Using local embedding model: {self.local_embedding_model}")
                return model
            except Exception as e:
                logger.warning(f"Failed to initialize sentence transformers: {e}")
        
        logger.error("No embedding model available")
        return None
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            if self.embedding_model_instance == "openai":
                return self._generate_openai_embeddings(texts)
            elif isinstance(self.embedding_model_instance, SentenceTransformer):
                return self._generate_local_embeddings(texts)
            else:
                raise ValueError("No valid embedding model available")
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            import openai
            response = openai.Embedding.create(
                model=self.embedding_model,
                input=texts
            )
            return [item['embedding'] for item in response['data']]
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    def _generate_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence transformers"""
        try:
            embeddings = self.embedding_model_instance.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Local embedding error: {e}")
            raise
    
    def add_embeddings(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        """
        Add embeddings to the collection
        
        Args:
            texts: List of text documents
            metadatas: List of metadata dictionaries
            ids: Optional list of IDs (will be generated if not provided)
        """
        if not texts:
            logger.warning("No texts provided for embedding")
            return
        
        try:
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}_{hash(text) % 1000000}" for i, text in enumerate(texts)]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} embeddings to collection")
            
        except Exception as e:
            logger.error(f"Error adding embeddings: {e}")
            raise
    
    def query(self, query_text: str, n_results: int = 10, where: Optional[Dict] = None) -> Dict:
        """
        Query the collection for similar documents
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Dictionary with query results
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query_text])[0]
            
            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"Query returned {len(results['ids'][0]) if results['ids'] else 0} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {'ids': [], 'documents': [], 'metadatas': [], 'distances': []}
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'count': count,
                'embedding_dimension': self.embedding_dimension,
                'embedding_model': self.embedding_model if self.embedding_model_instance == "openai" else self.local_embedding_model
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
    
    def persist(self):
        """Persist the database to disk"""
        # ChromaDB with duckdb+parquet automatically persists
        logger.info("Database persisted")
