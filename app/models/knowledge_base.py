from typing import List, Dict, Optional
from loguru import logger


class KnowledgeBase:
    """Knowledge base for storing domain-specific documents and context"""
    
    def __init__(self):
        self.documents: List[Dict] = []
        self.indexed = False
        
        # Load default knowledge base documents
        self._load_default_documents()
    
    def _load_default_documents(self):
        """Load default knowledge base documents about music discovery"""
        default_docs = [
            {
                "id": "kb_001",
                "content": "Music discovery refers to the process by which users find new music that aligns with their preferences. This can happen through recommendations, playlists, radio features, or manual exploration.",
                "category": "general",
                "keywords": ["discovery", "recommendations", "playlists", "radio"]
            },
            {
                "id": "kb_002",
                "content": "Common music discovery features include: personalized playlists (Discover Weekly, Release Radar), algorithmic radio stations, genre browsing, and social sharing features.",
                "category": "features",
                "keywords": ["playlists", "radio", "genres", "sharing"]
            },
            {
                "id": "kb_003",
                "content": "Users often struggle with music discovery when recommendations feel repetitive, don't match their current mood, or fail to introduce them to truly new artists.",
                "category": "challenges",
                "keywords": ["repetitive", "mood", "new artists"]
            },
            {
                "id": "kb_004",
                "content": "Repetitive listening behavior can be driven by comfort, nostalgia, habit formation, or lack of appealing new content. It may also indicate satisfaction with existing content.",
                "category": "behavior",
                "keywords": ["repetition", "comfort", "nostalgia", "habit"]
            },
            {
                "id": "kb_005",
                "content": "Music recommendation algorithms typically use collaborative filtering, content-based filtering, or hybrid approaches to suggest music based on user history and preferences.",
                "category": "algorithms",
                "keywords": ["algorithms", "collaborative filtering", "content-based"]
            },
            {
                "id": "kb_006",
                "content": "User segments for music discovery include: casual listeners who prefer familiar hits, explorers who actively seek new music, mood-based listeners who choose by activity, and genre-focused listeners.",
                "category": "segments",
                "keywords": ["segments", "casual", "explorers", "mood", "genre"]
            },
            {
                "id": "kb_007",
                "content": "Common user frustrations with recommendations include: too much repetition, irrelevant suggestions, lack of diversity, poor context awareness, and inability to fine-tune preferences.",
                "category": "frustrations",
                "keywords": ["frustrations", "repetition", "irrelevant", "diversity"]
            },
            {
                "id": "kb_008",
                "content": "Unmet needs in music discovery often include: better mood matching, more serendipitous discoveries, improved genre exploration, and social discovery features.",
                "category": "unmet_needs",
                "keywords": ["unmet needs", "mood", "serendipity", "social"]
            }
        ]
        
        self.documents = default_docs
        logger.info(f"Loaded {len(self.documents)} default knowledge base documents")
    
    def add_document(self, document: Dict):
        """Add a document to the knowledge base"""
        self.documents.append(document)
        self.indexed = False
        logger.info(f"Added document: {document.get('id', 'unknown')}")
    
    def add_documents(self, documents: List[Dict]):
        """Add multiple documents to the knowledge base"""
        self.documents.extend(documents)
        self.indexed = False
        logger.info(f"Added {len(documents)} documents to knowledge base")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search the knowledge base for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        if not self.documents:
            return []
        
        # Simple keyword matching (can be enhanced with vector search)
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents:
            content = doc.get('content', '').lower()
            keywords = doc.get('keywords', [])
            
            # Calculate relevance score
            score = 0
            
            # Check for keyword matches
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 2
                if keyword.lower() in content:
                    score += 1
            
            # Check for content matches
            if query_lower in content:
                score += 3
            
            if score > 0:
                scored_docs.append((doc, score))
        
        # Sort by score and return top results
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        results = [doc for doc, score in scored_docs[:top_k]]
        logger.info(f"Knowledge base search returned {len(results)} results")
        
        return results
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        """Get a specific document by ID"""
        for doc in self.documents:
            if doc.get('id') == doc_id:
                return doc
        return None
    
    def get_documents_by_category(self, category: str) -> List[Dict]:
        """Get all documents in a specific category"""
        return [doc for doc in self.documents if doc.get('category') == category]
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories in the knowledge base"""
        categories = set(doc.get('category') for doc in self.documents if doc.get('category'))
        return list(categories)
    
    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        return {
            'total_documents': len(self.documents),
            'categories': self.get_all_categories(),
            'indexed': self.indexed
        }
