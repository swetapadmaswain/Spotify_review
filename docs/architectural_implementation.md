# Phase-Wise Architectural Implementation: AI-Powered Review Discovery Engine

## Overview

This document provides a detailed architectural implementation plan for the AI-Powered Review Discovery Engine, broken down into 4 phases over 16 weeks. Each phase includes specific components, data flows, technology choices, and integration patterns.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Sources Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ App Store│ │Play Store│ │  Reddit  │ │  Forums  │ │Social  │ │
│  │ Reviews  │ │ Reviews  │ │Discussions│ │          │ │Media   │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
└───────┼────────────┼────────────┼────────────┼──────────┼──────┘
        │            │            │            │          │
┌───────┴────────────┴────────────┴────────────┴──────────┴──────┐
│                   Data Collection Layer                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           API Connectors & Web Scrapers                  │  │
│  │           (n8n/Zapier Workflows)                         │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────┘
                          │
┌─────────────────────────┴──────────────────────────────────────┐
│                   Data Processing Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Ingest  │  │  Clean   │  │  Normalize│  │  Store   │      │
│  │  Pipeline│  │  Pipeline│  │  Pipeline│  │  Layer   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼────────────┼────────────┼────────────┼───────────────┘
        │            │            │            │
┌───────┴────────────┴────────────┴────────────┴───────────────┐
│                   AI Analysis Layer                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              RAG System & LLM Processing                  │  │
│  │  (Claude/GPT Models + Vector Database)                    │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────┘
                          │
┌─────────────────────────┴──────────────────────────────────────┐
│                   Insight Generation Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Pattern  │  │ Segment  │  │ Root Cause│  │ Unmet    │      │
│  │ Detection│  │ Analysis │  │ Analysis │  │ Needs    │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼────────────┼────────────┼────────────┼───────────────┘
        │            │            │            │
┌───────┴────────────┴────────────┴────────────┴───────────────┐
│                   Reporting & Visualization Layer             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Dashboard, Reports, API Endpoints                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Data Collection Infrastructure (Weeks 1-4)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 1: Data Collection                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  App Store   │    │  Play Store  │    │    Reddit    │      │
│  │   API        │    │   API        │    │    API       │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │  n8n Workflow    │                          │
│                    │  Engine          │                          │
│                    │  - Schedulers    │                          │
│                    │  - Rate Limiting │                          │
│                    │  - Error Handling│                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │  Raw Data Store  │                          │
│                    │  (S3/MinIO)      │                          │
│                    │  - JSON/CSV      │                          │
│                    │  - Metadata      │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │  Data Quality   │                          │
│                    │  Service         │                          │
│                    │  - Validation    │                          │
│                    │  - Deduplication │                          │
│                    │  - Enrichment    │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │  Processed Data │                          │
│                    │  Store          │                          │
│                    │  (PostgreSQL)   │                          │
│                    └─────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### 1.1 API Connectors (Week 1-2)

**App Store Connector**
- **Technology**: Python + iTunes Search API / App Store Review API
- **Implementation**:
  ```python
  class AppStoreConnector:
      def __init__(self, app_id, api_key):
          self.app_id = app_id
          self.api_key = api_key
          self.base_url = "https://api.appstoreconnect/v1"
      
      def fetch_reviews(self, limit=500, offset=0):
          # Fetch reviews with pagination (limited to 500 to control token usage)
          # Handle rate limiting (50 requests/minute)
          # Return structured JSON
          pass
      
      def fetch_ratings(self):
          # Fetch rating distributions
          pass
  ```

**Play Store Connector**
- **Technology**: Python + Google Play Store API / scrapy
- **Implementation**:
  ```python
  class PlayStoreConnector:
      def __init__(self, package_name):
          self.package_name = package_name
          # Use google-play-scraper or official API
      
      def fetch_reviews(self, sort='newest', count=500):
          # Fetch reviews with sorting options (limited to 500 to control token usage)
          # Handle pagination
          pass
  ```

**Reddit Connector**
- **Technology**: Python + PRAW (Reddit API)
- **Implementation**:
  ```python
  class RedditConnector:
      def __init__(self, client_id, client_secret):
          self.reddit = praw.Reddit(
              client_id=client_id,
              client_secret=client_secret,
              user_agent='SpotifyReviewAnalysis/1.0'
          )
      
      def fetch_subreddit_posts(self, subreddit, limit=500):
          # Fetch posts from r/spotify, r/music (limited to 500 to control token usage)
          # Extract comments
          pass
      
      def fetch_comments(self, post_id):
          # Fetch all comments for a post
          pass
  ```

**Forum Connector**
- **Technology**: Python + BeautifulSoup / Scrapy
- **Target**: Spotify Community Forums
- **Implementation**:
  ```python
  class ForumConnector:
      def __init__(self, base_url):
          self.base_url = base_url
      
      def scrape_threads(self, category='discovery'):
          # Scrape forum threads
          # Handle authentication if required
          pass
  ```

**Social Media Connector**
- **Technology**: Python + Tweepy (Twitter), Facebook Graph API
- **Implementation**:
  ```python
  class SocialMediaConnector:
      def __init__(self, credentials):
          self.twitter_client = TwitterClient(credentials['twitter'])
          self.facebook_client = FacebookClient(credentials['facebook'])
      
      def fetch_mentions(self, query='#spotify', limit=500):
          # Fetch mentions and hashtags (limited to 500 to control token usage)
          pass
  ```

#### 1.2 Workflow Automation (Week 2-3)

**n8n Workflow Configuration**
- **Purpose**: Orchestrate data collection pipelines
- **Components**:
  - **Scheduler Nodes**: Run collection daily/weekly
  - **API Call Nodes**: Execute connector functions
  - **Transform Nodes**: Format data consistently
  - **Error Handling Nodes**: Retry failed requests
  - **Notification Nodes**: Alert on failures

**Sample n8n Workflow**:
```json
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 24}]
        }
      }
    },
    {
      "name": "Fetch App Store Reviews",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/api/appstore/reviews",
        "method": "GET"
      }
    },
    {
      "name": "Transform Data",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "return items.map(item => ({json: {...item.json, source: 'appstore'}}));"
      }
    },
    {
      "name": "Store in S3",
      "type": "n8n-nodes-base.awsS3",
      "parameters": {
        "operation": "upload",
        "bucketName": "spotify-reviews-raw"
      }
    }
  ]
}
```

#### 1.3 Data Storage (Week 3)

**Raw Data Storage**
- **Technology**: AWS S3 or MinIO (self-hosted)
- **Structure**:
  ```
  s3://spotify-reviews-raw/
  ├── appstore/
  │   ├── 2024-01-15/
  │   │   ├── reviews_001.json
  │   │   └── reviews_002.json
  ├── playstore/
  ├── reddit/
  ├── forums/
  └── social/
  ```

**Metadata Database**
- **Technology**: PostgreSQL
- **Schema**:
  ```sql
  CREATE TABLE data_collection_runs (
      id SERIAL PRIMARY KEY,
      source VARCHAR(50) NOT NULL,
      start_time TIMESTAMP NOT NULL,
      end_time TIMESTAMP,
      records_collected INTEGER,
      status VARCHAR(20),
      error_message TEXT
  );
  
  CREATE TABLE raw_data_metadata (
      id SERIAL PRIMARY KEY,
      source VARCHAR(50) NOT NULL,
      file_path VARCHAR(255) NOT NULL,
      record_count INTEGER,
      collection_date TIMESTAMP NOT NULL,
      processed BOOLEAN DEFAULT FALSE
  );
  ```

#### 1.4 Data Quality Service (Week 4)

**Validation Pipeline**
- **Technology**: Python + Great Expectations
- **Implementation**:
  ```python
  class DataQualityService:
      def __init__(self):
          self.expectations = self.load_expectations()
      
      def validate_batch(self, data, source):
          # Check for required fields
          # Validate data types
          # Check for duplicates
          # Validate text encoding
          pass
      
      def clean_data(self, data):
          # Remove HTML tags
          # Normalize text
          # Handle missing values
          pass
  ```

**Deduplication Service**
- **Technology**: Python + MinHash / SimHash
- **Implementation**:
  ```python
  class DeduplicationService:
      def __init__(self):
          self.hash_store = {}
      
      def is_duplicate(self, text, threshold=0.9):
          # Compute text hash
          # Compare with existing hashes
          # Return True if similar
          pass
  ```

### Data Flow

1. **Scheduled Trigger** → n8n workflow initiates
2. **API Connectors** → Fetch data from sources
3. **Transform Layer** → Standardize format
4. **Raw Storage** → Store in S3 with metadata
5. **Quality Check** → Validate and clean
6. **Processed Storage** → Store in PostgreSQL
7. **Status Update** → Log collection run status

### Security & Compliance

- **API Key Management**: AWS Secrets Manager or HashiCorp Vault
- **Rate Limiting**: Implement exponential backoff
- **Data Privacy**: Anonymize user identifiers
- **Terms of Service**: Respect robots.txt and API limits
- **Audit Logging**: Log all data access

### Deliverables

- [x] 5 API connectors implemented
- [x] n8n workflows configured
- [x] S3 bucket structure created
- [x] PostgreSQL schema deployed
- [x] Data quality pipeline operational
- [x] Compliance documentation completed

---

## Phase 2: AI Analysis Engine (Weeks 5-8)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 2: AI Analysis Engine                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Processed   │    │  Vector      │    │  Knowledge   │      │
│  │  Data Store  │───▶│  Embeddings  │◀───│  Base        │      │
│  │  (PostgreSQL)│    │  (ChromaDB)  │    │  (Documents) │      │
│  └──────────────┘    └──────┬───────┘    └──────────────┘      │
│                              │                                   │
│                    ┌──────────▼──────────┐                       │
│                    │   RAG System       │                       │
│                    │   - Retrieval       │                       │
│                    │   - Augmentation    │                       │
│                    │   - Generation      │                       │
│                    └──────────┬──────────┘                       │
│                              │                                   │
│                    ┌──────────▼──────────┐                       │
│                    │   LLM Processing    │                       │
│                    │   (Claude/GPT-4)    │                       │
│                    │   - Sentiment       │                       │
│                    │   - Topic Modeling  │                       │
│                    │   - Entity Extract   │                       │
│                    └──────────┬──────────┘                       │
│                              │                                   │
│                    ┌──────────▼──────────┐                       │
│                    │   Analysis Store    │                       │
│                    │   (PostgreSQL)      │                       │
│                    └─────────────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### 2.1 Vector Database Setup (Week 5)

**ChromaDB Configuration**
- **Purpose**: Store vector embeddings for semantic search
- **Implementation**:
  ```python
  import chromadb
  from chromadb.config import Settings
  
  class VectorDatabase:
      def __init__(self):
          self.client = chromadb.Client(
              Settings(
                  chroma_db_impl="duckdb+parquet",
                  persist_directory="./vector_db"
              )
          )
          self.collection = self.client.create_collection(
              name="spotify_reviews",
              metadata={"hnsw:space": "cosine"}
          )
      
      def add_embeddings(self, texts, metadatas):
          # Generate embeddings using OpenAI/ Cohere
          embeddings = self.generate_embeddings(texts)
          self.collection.add(
              embeddings=embeddings,
              documents=texts,
              metadatas=metadatas,
              ids=[str(i) for i in range(len(texts))]
          )
      
      def query(self, query_text, n_results=10):
          # Semantic search
          query_embedding = self.generate_embeddings([query_text])
          return self.collection.query(
              query_embeddings=query_embedding,
              n_results=n_results
          )
  ```

**Embedding Model Selection**
- **Primary**: OpenAI text-embedding-3-small (cost-effective)
- **Backup**: Cohere embed-english-v3.0
- **Local Option**: Sentence Transformers (all-MiniLM-L6-v2)

#### 2.2 RAG System Implementation (Week 5-6)

**Retrieval Component**
```python
class RetrievalComponent:
    def __init__(self, vector_db, knowledge_base):
        self.vector_db = vector_db
        self.knowledge_base = knowledge_base
    
    def retrieve_context(self, query, top_k=5):
        # Retrieve similar reviews
        results = self.vector_db.query(query, n_results=top_k)
        
        # Retrieve relevant knowledge base documents
        kb_docs = self.knowledge_base.search(query)
        
        return {
            'similar_reviews': results,
            'knowledge_context': kb_docs
        }
```

**Augmentation Component**
```python
class AugmentationComponent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def augment_query(self, query, context):
        prompt = f"""
        Based on the following user feedback context, analyze this query:
        
        Query: {query}
        
        Context:
        {context}
        
        Provide insights about:
        1. User sentiment
        2. Key themes
        3. Specific frustrations
        4. Suggested improvements
        """
        return self.llm_client.generate(prompt)
```

**Generation Component**
```python
class GenerationComponent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def generate_insights(self, query, augmented_context):
        prompt = f"""
        Generate comprehensive insights for the following analysis:
        
        Query: {query}
        Augmented Context: {augmented_context}
        
        Structure your response with:
        - Key findings
        - Supporting evidence
        - Confidence scores
        - Actionable recommendations
        """
        return self.llm_client.generate(prompt)
```

#### 2.3 LLM Processing Pipeline (Week 6-7)

**Sentiment Analysis**
```python
class SentimentAnalyzer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def analyze_sentiment(self, text):
        prompt = f"""
        Analyze the sentiment of this user feedback:
        
        "{text}"
        
        Return:
        - sentiment (positive/negative/neutral)
        - confidence (0-1)
        - emotion (joy, frustration, disappointment, etc.)
        - intensity (low/medium/high)
        """
        return self.llm_client.generate(prompt)
```

**Topic Modeling**
```python
class TopicModeler:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def extract_topics(self, text):
        prompt = f"""
        Extract key topics from this feedback:
        
        "{text}"
        
        Return topics as:
        - primary_topic
        - secondary_topics
        - topic_relevance_scores
        """
        return self.llm_client.generate(prompt)
```

**Entity Extraction**
```python
class EntityExtractor:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def extract_entities(self, text):
        prompt = f"""
        Extract entities from this feedback:
        
        "{text}"
        
        Identify:
        - music_features (playlist, radio, recommendations)
        - user_actions (skip, save, share)
        - emotions (frustrated, happy, bored)
        - technical_terms (algorithm, UI, bug)
        """
        return self.llm_client.generate(prompt)
```

#### 2.4 Automated Workflows (Week 7-8)

**Batch Processing Pipeline**
```python
class BatchProcessor:
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.rag_system = RAGSystem()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_modeler = TopicModeler()
        self.entity_extractor = EntityExtractor()
    
    def process_batch(self, batch_size=500):
        # Fetch unprocessed reviews (limited to 500 to control token usage)
        reviews = self.fetch_unprocessed_reviews(limit=batch_size)
        
        for review in reviews:
            # Generate embeddings
            self.vector_db.add_embeddings([review['text']], [review['metadata']])
            
            # Run analysis
            sentiment = self.sentiment_analyzer.analyze_sentiment(review['text'])
            topics = self.topic_modeler.extract_topics(review['text'])
            entities = self.entity_extractor.extract_entities(review['text'])
            
            # Store results
            self.store_analysis_results(review['id'], {
                'sentiment': sentiment,
                'topics': topics,
                'entities': entities
           })
```

**Real-time Analysis Pipeline**
```python
class RealTimeProcessor:
    def __init__(self):
        self.rag_system = RAGSystem()
    
    def analyze_new_review(self, review):
        # Immediate analysis for new reviews
        context = self.rag_system.retrieve_context(review['text'])
        insights = self.rag_system.augment_query(review['text'], context)
        
        return insights
```

### Analysis Store Schema

```sql
CREATE TABLE sentiment_analysis (
    id SERIAL PRIMARY KEY,
    review_id INTEGER REFERENCES raw_data(id),
    sentiment VARCHAR(20),
    confidence FLOAT,
    emotion VARCHAR(50),
    intensity VARCHAR(20),
    analyzed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE topic_analysis (
    id SERIAL PRIMARY KEY,
    review_id INTEGER REFERENCES raw_data(id),
    primary_topic VARCHAR(100),
    secondary_topics JSONB,
    relevance_scores JSONB,
    analyzed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE entity_analysis (
    id SERIAL PRIMARY KEY,
    review_id INTEGER REFERENCES raw_data(id),
    entities JSONB,
    entity_types JSONB,
    analyzed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE rag_cache (
    id SERIAL PRIMARY KEY,
    query TEXT,
    context JSONB,
    response JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Performance Optimization

- **Batch Processing**: Process 500 reviews at a time to control token usage
- **Caching**: Cache RAG responses for similar queries
- **Async Processing**: Use Celery for background tasks
- **Rate Limiting**: Implement LLM API rate limiting
- **Cost Management**: Use smaller models for initial filtering

### Deliverables

- [x] Vector database configured and populated
- [x] RAG system implemented with retrieval, augmentation, generation
- [x] LLM processing pipeline operational
- [x] Sentiment, topic, and entity extraction working
- [x] Batch and real-time processing pipelines
- [x] Analysis store schema deployed

---

## Phase 3: Insight Generation (Weeks 9-12)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 3: Insight Generation                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Analysis    │    │  Pattern     │    │  Segmentation│      │
│  │  Store       │───▶│  Detection   │───▶│  Engine      │      │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘      │
│                              │                   │               │
│                    ┌─────────▼─────────┐       │               │
│                    │  Root Cause       │       │               │
│                    │  Analysis Engine   │       │               │
│                    └─────────┬─────────┘       │               │
│                              │                   │               │
│                    ┌─────────▼─────────┐       │               │
│                    │  Unmet Needs      │◀──────┘               │
│                    │  Detector         │                       │
│                    └─────────┬─────────┘                       │
│                              │                                   │
│                    ┌─────────▼─────────┐                       │
│                    │  Insight Store    │                       │
│                    │  (PostgreSQL)     │                       │
│                    └───────────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### 3.1 Pattern Detection Engine (Week 9)

**Temporal Pattern Detection**
```python
class TemporalPatternDetector:
    def __init__(self):
        self.analysis_store = AnalysisStore()
    
    def detect_trends(self, time_window='30d'):
        # Analyze sentiment trends over time
        query = """
        SELECT 
            DATE(analyzed_at) as date,
            sentiment,
            COUNT(*) as count
        FROM sentiment_analysis
        WHERE analyzed_at >= NOW() - INTERVAL '30 days'
        GROUP BY date, sentiment
        ORDER BY date
        """
        results = self.analysis_store.execute(query)
        
        # Identify significant trends
        trends = self.analyze_trends(results)
        return trends
    
    def detect_seasonal_patterns(self):
        # Identify seasonal patterns in feedback
        pass
```

**Thematic Pattern Detection**
```python
class ThematicPatternDetector:
    def __init__(self):
        self.analysis_store = AnalysisStore()
    
    def detect_emerging_topics(self, threshold=0.05):
        # Identify topics gaining traction
        query = """
        SELECT 
            primary_topic,
            COUNT(*) as frequency,
            AVG(relevance_scores->'primary') as avg_relevance
        FROM topic_analysis
        WHERE analyzed_at >= NOW() - INTERVAL '7 days'
        GROUP BY primary_topic
        HAVING COUNT(*) > (SELECT COUNT(*) * 0.05 FROM topic_analysis)
        ORDER BY frequency DESC
        """
        return self.analysis_store.execute(query)
    
    def detect_topic_clusters(self):
        # Cluster related topics
        pass
```

**Cross-Platform Pattern Detection**
```python
class CrossPlatformPatternDetector:
    def __init__(self):
        self.analysis_store = AnalysisStore()
    
    def detect_platform_differences(self):
        # Compare patterns across platforms
        query = """
        SELECT 
            r.source,
            t.primary_topic,
            s.sentiment,
            COUNT(*) as count
        FROM topic_analysis t
        JOIN sentiment_analysis s ON t.review_id = s.review_id
        JOIN raw_data r ON t.review_id = r.id
        GROUP BY r.source, t.primary_topic, s.sentiment
        """
        return self.analysis_store.execute(query)
```

#### 3.2 Segmentation Engine (Week 9-10)

**User Behavior Segmentation**
```python
class UserSegmentationEngine:
    def __init__(self):
        self.analysis_store = AnalysisStore()
    
    def segment_by_listening_behavior(self):
        # Segment users based on listening patterns mentioned
        query = """
        SELECT 
            e.entities->'listening_behavior' as behavior,
            COUNT(*) as user_count,
            AVG(s.confidence) as avg_confidence
        FROM entity_analysis e
        JOIN sentiment_analysis s ON e.review_id = s.review_id
        WHERE e.entities ? 'listening_behavior'
        GROUP BY behavior
        ORDER BY user_count DESC
        """
        return self.analysis_store.execute(query)
    
    def segment_by_frustration_type(self):
        # Segment by type of frustration
        query = """
        SELECT 
            e.entities->'frustration_type' as frustration,
            COUNT(*) as count,
            t.primary_topic
        FROM entity_analysis e
        JOIN topic_analysis t ON e.review_id = t.review_id
        WHERE e.entities ? 'frustration_type'
        GROUP BY frustration, t.primary_topic
        """
        return self.analysis_store.execute(query)
```

**Demographic Segmentation**
```python
class DemographicSegmentation:
    def __init__(self):
        self.analysis_store = AnalysisStore()
    
    def segment_by_platform(self):
        # Segment by platform (iOS vs Android)
        query = """
        SELECT 
            r.source,
            s.sentiment,
            t.primary_topic,
            COUNT(*) as count
        FROM sentiment_analysis s
        JOIN topic_analysis t ON s.review_id = t.review_id
        JOIN raw_data r ON s.review_id = r.id
        GROUP BY r.source, s.sentiment, t.primary_topic
        """
        return self.analysis_store.execute(query)
    
    def segment_by_geography(self):
        # Segment by geographic region (if available)
        pass
```

**Tenure-Based Segmentation**
```python
class TenureSegmentation:
    def __init__(self):
        self.analysis_store = AnalysisStore()
    
    def segment_by_user_tenure(self):
        # Segment new vs long-term users
        query = """
        SELECT 
            CASE 
                WHEN r.metadata->>'user_tenure' = 'new' THEN 'New User'
                WHEN r.metadata->>'user_tenure' = 'long_term' THEN 'Long-term User'
                ELSE 'Unknown'
            END as tenure_segment,
            t.primary_topic,
            s.sentiment,
            COUNT(*) as count
        FROM topic_analysis t
        JOIN sentiment_analysis s ON t.review_id = s.review_id
        JOIN raw_data r ON s.review_id = r.id
        GROUP BY tenure_segment, t.primary_topic, s.sentiment
        """
        return self.analysis_store.execute(query)
```

#### 3.3 Root Cause Analysis Engine (Week 10-11)

**Causal Chain Analysis**
```python
class RootCauseAnalyzer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.analysis_store = AnalysisStore()
    
    def analyze_causal_chains(self, topic):
        # Identify causal relationships
        prompt = f"""
        Analyze the causal chain for this topic based on user feedback:
        
        Topic: {topic}
        
        Identify:
        1. Root causes
        2. Intermediate factors
        3. Surface symptoms
        4. Causal relationships between them
        """
        
        # Fetch relevant feedback
        feedback = self.fetch_feedback_by_topic(topic)
        
        # Generate causal analysis
        analysis = self.llm_client.generate(prompt, context=feedback)
        return analysis
    
    def identify_systemic_issues(self):
        # Identify issues affecting multiple areas
        query = """
        SELECT 
            t.primary_topic,
            COUNT(DISTINCT r.source) as platform_count,
            COUNT(*) as total_mentions,
            AVG(s.confidence) as avg_confidence
        FROM topic_analysis t
        JOIN sentiment_analysis s ON t.review_id = s.review_id
        JOIN raw_data r ON s.review_id = r.id
        WHERE s.sentiment = 'negative'
        GROUP BY t.primary_topic
        HAVING COUNT(DISTINCT r.source) >= 3
        ORDER BY total_mentions DESC
        """
        return self.analysis_store.execute(query)
```

**Repetitive Behavior Analysis**
```python
class RepetitiveBehaviorAnalyzer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def analyze_repetition_drivers(self):
        # Analyze why users repeat content
        prompt = """
        Based on user feedback, analyze the drivers of repetitive listening behavior:
        
        Identify:
        1. Psychological drivers (comfort, nostalgia, anxiety)
        2. Technical drivers (UI friction, poor recommendations)
        3. Content drivers (lack of new content, preference for familiar)
        4. Context drivers (workout, study, background music)
        """
        
        # Fetch relevant feedback
        feedback = self.fetch_repetition_feedback()
        
        analysis = self.llm_client.generate(prompt, context=feedback)
        return analysis
```

#### 3.4 Unmet Needs Detector (Week 11-12)

**Feature Request Analysis**
```python
class UnmetNeedsDetector:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.analysis_store = AnalysisStore()
    
    def detect_feature_requests(self):
        # Identify requested features
        query = """
        SELECT 
            e.entities->'feature_request' as feature,
            COUNT(*) as request_count,
            AVG(s.confidence) as avg_confidence,
            t.primary_topic
        FROM entity_analysis e
        JOIN sentiment_analysis s ON e.review_id = s.review_id
        JOIN topic_analysis t ON e.review_id = t.review_id
        WHERE e.entities ? 'feature_request'
        GROUP BY feature, t.primary_topic
        ORDER BY request_count DESC
        """
        return self.analysis_store.execute(query)
    
    def prioritize_unmet_needs(self):
        # Prioritize by impact and frequency
        prompt = """
        Prioritize these unmet needs based on:
        1. Frequency of requests
        2. User sentiment (frustration level)
        3. Strategic alignment with discovery goals
        4. Implementation feasibility
        
        Return prioritized list with rationale.
        """
        
        unmet_needs = self.detect_feature_requests()
        prioritization = self.llm_client.generate(prompt, context=unmet_needs)
        return prioritization
```

**Gap Analysis**
```python
class GapAnalyzer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def identify_capability_gaps(self):
        # Identify gaps between user needs and current capabilities
        prompt = """
        Analyze user feedback to identify capability gaps:
        
        Compare:
        1. What users want to do
        2. What current features allow
        3. Where the gaps exist
        
        Focus on music discovery capabilities.
        """
        
        feedback = self.fetch_discovery_feedback()
        gap_analysis = self.llm_client.generate(prompt, context=feedback)
        return gap_analysis
```

### Insight Store Schema

```sql
CREATE TABLE pattern_insights (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50),
    pattern_description TEXT,
    frequency INTEGER,
    confidence FLOAT,
    time_period VARCHAR(20),
    discovered_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_segments (
    id SERIAL PRIMARY KEY,
    segment_name VARCHAR(100),
    segment_criteria JSONB,
    user_count INTEGER,
    primary_challenges TEXT[],
    avg_sentiment VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE root_cause_analysis (
    id SERIAL PRIMARY KEY,
    issue_topic VARCHAR(100),
    root_causes JSONB,
    intermediate_factors JSONB,
    surface_symptoms JSONB,
    confidence FLOAT,
    analyzed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE unmet_needs (
    id SERIAL PRIMARY KEY,
    need_description TEXT,
    need_category VARCHAR(50),
    request_count INTEGER,
    priority_score FLOAT,
    strategic_impact VARCHAR(20),
    identified_at TIMESTAMP DEFAULT NOW()
);
```

### Deliverables

- [x] Pattern detection engine operational
- [x] User segmentation engine implemented
- [x] Root cause analysis working
- [x] Unmet needs detector functional
- [x] Insight store schema deployed
- [x] At least 10 patterns identified
- [x] User segments defined
- [x] Root causes of repetitive behavior identified
- [x] 3+ major unmet needs prioritized

---

## Phase 4: Reporting and Recommendations (Weeks 13-16)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  Phase 4: Reporting & Recommendations            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Insight     │    │  Report      │    │  Dashboard   │      │
│  │  Store       │───▶│  Generator   │───▶│  Server      │      │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘      │
│                              │                   │               │
│                    ┌─────────▼─────────┐       │               │
│                    │  Recommendation  │       │               │
│                    │  Engine          │       │               │
│                    └─────────┬─────────┘       │               │
│                              │                   │               │
│                    ┌─────────▼─────────┐       │               │
│                    │  API Layer        │◀──────┘               │
│                    │  (FastAPI)         │                       │
│                    └─────────┬─────────┘                       │
│                              │                                   │
│                    ┌─────────▼─────────┐                       │
│                    │  Stakeholders      │                       │
│                    │  - Product Team    │                       │
│                    │  - Engineering     │                       │
│                    │  - Leadership      │                       │
│                    └───────────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### 4.1 Report Generator (Week 13)

**Comprehensive Report Generation**
```python
class ReportGenerator:
    def __init__(self):
        self.insight_store = InsightStore()
        self.recommendation_engine = RecommendationEngine()
    
    def generate_comprehensive_report(self):
        report = {
            'executive_summary': self.generate_executive_summary(),
            'key_findings': self.generate_key_findings(),
            'pattern_analysis': self.generate_pattern_analysis(),
            'user_segments': self.generate_segment_analysis(),
            'root_causes': self.generate_root_cause_analysis(),
            'unmet_needs': self.generate_unmet_needs_analysis(),
            'recommendations': self.recommendation_engine.generate_recommendations(),
            'appendices': self.generate_appendices()
        }
        return report
    
    def generate_executive_summary(self):
        # High-level summary for leadership
        pass
    
    def generate_key_findings(self):
        # Top 10 most important findings
        pass
```

**Automated Report Templates**
```python
class ReportTemplate:
    def __init__(self, template_type):
        self.template_type = template_type
    
    def render(self, data):
        if self.template_type == 'executive':
            return self.render_executive(data)
        elif self.template_type == 'technical':
            return self.render_technical(data)
        elif self.template_type == 'product':
            return self.render_product(data)
```

#### 4.2 Dashboard Server (Week 13-14)

**Technology Stack**
- **Backend**: FastAPI
- **Frontend**: React + TypeScript
- **Charts**: Recharts / D3.js
- **Styling**: TailwindCSS

**API Endpoints**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Spotify Review Analysis Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/insights/summary")
async def get_insights_summary():
    """Get executive summary of insights"""
    return insight_store.get_summary()

@app.get("/api/insights/patterns")
async def get_patterns():
    """Get all detected patterns"""
    return insight_store.get_patterns()

@app.get("/api/insights/segments")
async def get_segments():
    """Get user segments"""
    return insight_store.get_segments()

@app.get("/api/insights/unmet-needs")
async def get_unmet_needs():
    """Get prioritized unmet needs"""
    return insight_store.get_unmet_needs()

@app.get("/api/recommendations")
async def get_recommendations():
    """Get strategic recommendations"""
    return recommendation_engine.get_recommendations()

@app.get("/api/analytics/sentiment-trends")
async def get_sentiment_trends(days=30):
    """Get sentiment trends over time"""
    return analytics_store.get_sentiment_trends(days)

@app.get("/api/analytics/topic-evolution")
async def get_topic_evolution(days=30):
    """Get topic evolution over time"""
    return analytics_store.get_topic_evolution(days)
```

**Dashboard Components**

**Executive Dashboard**
```typescript
// React Component
const ExecutiveDashboard: React.FC = () => {
    const [summary, setSummary] = useState(null);
    const [trends, setTrends] = useState(null);
    
    useEffect(() => {
        fetch('/api/insights/summary')
            .then(res => res.json())
            .then(setSummary);
        
        fetch('/api/analytics/sentiment-trends')
            .then(res => res.json())
            .then(setTrends);
    }, []);
    
    return (
        <div className="dashboard">
            <h1>Music Discovery Insights</h1>
            <SummaryCards data={summary} />
            <SentimentTrendChart data={trends} />
            <KeyFindingsList findings={summary?.key_findings} />
        </div>
    );
};
```

**Pattern Analysis Dashboard**
```typescript
const PatternDashboard: React.FC = () => {
    const [patterns, setPatterns] = useState(null);
    
    return (
        <div className="pattern-dashboard">
            <h2>Pattern Analysis</h2>
            <PatternFrequencyChart data={patterns} />
            <CrossPlatformComparison data={patterns} />
            <TemporalPatternView data={patterns} />
        </div>
    );
};
```

**Segment Analysis Dashboard**
```typescript
const SegmentDashboard: React.FC = () => {
    const [segments, setSegments] = useState(null);
    
    return (
        <div className="segment-dashboard">
            <h2>User Segments</h2>
            <SegmentDistributionChart data={segments} />
            <SegmentComparisonTable data={segments} />
            <SegmentDetailViews data={segments} />
        </div>
    );
};
```

#### 4.3 Recommendation Engine (Week 14-15)

**Strategic Recommendation Generation**
```python
class RecommendationEngine:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.insight_store = InsightStore()
    
    def generate_recommendations(self):
        # Generate strategic recommendations based on insights
        insights = self.insight_store.get_all_insights()
        
        prompt = f"""
        Based on the following insights, generate strategic recommendations:
        
        Insights:
        {json.dumps(insights, indent=2)}
        
        Generate recommendations for:
        1. Product features (short-term, medium-term, long-term)
        2. Algorithm improvements
        3. UX/UI changes
        4. User education initiatives
        
        For each recommendation, include:
        - Priority (high/medium/low)
        - Expected impact on discovery
        - Implementation complexity
        - Success metrics
        """
        
        recommendations = self.llm_client.generate(prompt)
        return self.parse_recommendations(recommendations)
    
    def prioritize_recommendations(self, recommendations):
        # Prioritize by impact and feasibility
        pass
```

**Product Roadmap Integration**
```python
class RoadmapIntegrator:
    def __init__(self):
        self.recommendation_engine = RecommendationEngine()
    
    def generate_roadmap_items(self):
        recommendations = self.recommendation_engine.generate_recommendations()
        
        roadmap_items = []
        for rec in recommendations:
            item = {
                'title': rec['title'],
                'description': rec['description'],
                'priority': rec['priority'],
                'estimated_effort': rec['complexity'],
                'success_metrics': rec['metrics'],
                'dependencies': rec.get('dependencies', []),
                'quarter': self.map_to_quarter(rec['priority'], rec['complexity'])
            }
            roadmap_items.append(item)
        
        return roadmap_items
```

#### 4.4 API Layer (Week 15-16)

**REST API Implementation**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class InsightRequest(BaseModel):
    insight_type: str
    filters: Optional[dict] = None

class RecommendationRequest(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = None

@app.post("/api/insights/query")
async def query_insights(request: InsightRequest):
    """Query insights with filters"""
    try:
        insights = insight_store.query(
            insight_type=request.insight_type,
            filters=request.filters
        )
        return {"success": True, "data": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/generate")
async def generate_recommendations(request: RecommendationRequest):
    """Generate targeted recommendations"""
    try:
        recommendations = recommendation_engine.generate(
            category=request.category,
            priority=request.priority
        )
        return {"success": True, "data": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}
```

**Authentication & Authorization**
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.get("/api/insights/summary")
async def get_insights_summary(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Protected endpoint requiring authentication"""
    user = authenticate_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return insight_store.get_summary()
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Production Deployment                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Load        │    │  API         │    │  Dashboard   │      │
│  │  Balancer    │───▶│  Server      │───▶│  Frontend    │      │
│  │  (Nginx)     │    │  (FastAPI)   │    │  (React)     │      │
│  └──────────────┘    └──────┬───────┘    └──────────────┘      │
│                              │                                   │
│                    ┌─────────▼─────────┐                       │
│                    │  Application      │                       │
│                    │  Server          │                       │
│                    │  (Gunicorn)      │                       │
│                    └─────────┬─────────┘                       │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐            │
│         │                    │                    │            │
│  ┌──────▼──────┐    ┌───────▼──────┐    ┌────────▼────┐       │
│  │ PostgreSQL  │    │  Vector DB   │    │   Redis     │       │
│  │ (Primary)   │    │  (ChromaDB)  │    │  (Cache)    │       │
│  └─────────────┘    └──────────────┘    └─────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Monitoring & Alerting

**System Monitoring**
```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
insight_requests_total = Counter('insight_requests_total', 'Total insight requests')
insight_request_duration = Histogram('insight_request_duration_seconds', 'Insight request duration')

@app.middleware("http")
async def monitor_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    insight_requests_total.inc()
    insight_request_duration.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()
```

**Alerting Configuration**
```yaml
# Prometheus Alert Rules
groups:
  - name: spotify_insights_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(insight_errors_total[5m]) > 0.1
        annotations:
          summary: "High error rate in insight generation"
      
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, insight_request_duration_seconds) > 5
        annotations:
          summary: "Slow response times detected"
```

### Deliverables

- [x] Comprehensive insight report generated
- [x] Interactive dashboard deployed
- [x] API endpoints operational
- [x] Strategic recommendations documented
- [x] Product roadmap items created
- [x] System monitoring configured
- [x] Authentication implemented
- [x] Production deployment completed

---

## Integration & Data Flow Summary

### End-to-End Data Flow

```
1. Data Collection (Phase 1)
   └─> Sources → API Connectors → n8n Workflows → Raw Storage

2. Data Processing (Phase 1)
   └─> Raw Storage → Quality Service → Processed Storage

3. AI Analysis (Phase 2)
   └─> Processed Storage → Vector Embeddings → RAG System → LLM Processing → Analysis Store

4. Insight Generation (Phase 3)
   └─> Analysis Store → Pattern Detection → Segmentation → Root Cause Analysis → Insight Store

5. Reporting (Phase 4)
   └─> Insight Store → Report Generator → Dashboard → API → Stakeholders
```

### Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data Collection | Python, n8n, Zapier | API connectors, workflow automation |
| Storage | PostgreSQL, S3/MinIO | Data persistence |
| AI/ML | Claude, GPT-4, ChromaDB | LLM processing, vector storage |
| Analysis | Python, Great Expectations | Data quality, pattern detection |
| API | FastAPI | REST API endpoints |
| Frontend | React, TypeScript, TailwindCSS | Dashboard UI |
| Deployment | Docker, Nginx, Gunicorn | Production deployment |
| Monitoring | Prometheus, Grafana | System monitoring |

### Security Considerations

- **API Keys**: Stored in AWS Secrets Manager
- **Data Encryption**: TLS in transit, AES-256 at rest
- **Access Control**: Role-based access control (RBAC)
- **Audit Logging**: All data access logged
- **Rate Limiting**: API rate limiting implemented
- **Data Privacy**: User data anonymized

### Scalability Considerations

- **Horizontal Scaling**: Stateless API servers
- **Database Scaling**: Read replicas for analytics queries
- **Caching**: Redis for frequently accessed data
- **Queue Processing**: Celery for background tasks
- **Load Balancing**: Nginx for API server distribution

---

## Conclusion

This architectural implementation provides a comprehensive, phased approach to building the AI-Powered Review Discovery Engine. Each phase builds upon the previous one, ensuring a solid foundation for data-driven insights that will inform Spotify's strategic goal of increasing meaningful music discovery and reducing repetitive listening behavior.

The system is designed to be:
- **Scalable**: Handles increasing data volumes
- **Maintainable**: Modular architecture with clear separation of concerns
- **Extensible**: Easy to add new data sources and analysis capabilities
- **Secure**: Implements industry-standard security practices
- **Compliant**: Respects data privacy and platform terms of service
