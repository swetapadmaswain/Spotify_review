from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger
from datetime import datetime

from app.connectors import (
    AppStoreConnector,
    PlayStoreConnector,
    RedditConnector,
    ForumConnector,
    SocialMediaConnector,
)
from app.database import get_db, init_db, DataCollectionRun
from app.services.service import DataQualityService, DeduplicationService
from app.api.insights_routes import router as insights_router
from app.api.reporting_routes import router as reporting_router
from app.api.monitoring import MetricsMiddleware, metrics_response
from config.settings import settings

app = FastAPI(title="Spotify Review Discovery Engine", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to handle content-length properly
@app.middleware("http")
async def add_content_length_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Initialize services
data_quality = DataQualityService()
deduplication = DeduplicationService()

init_db()
app.add_middleware(MetricsMiddleware)
app.include_router(insights_router)
app.include_router(reporting_router)


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return metrics_response()


class CollectionRequest(BaseModel):
    source: str
    limit: Optional[int] = 500
    category: Optional[str] = None
    query: Optional[str] = None


class CollectionResponse(BaseModel):
    success: bool
    source: str
    records_collected: int
    message: str
    data: Optional[List[dict]] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Spotify Review Discovery Engine",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/appstore/reviews", response_model=CollectionResponse)
async def fetch_appstore_reviews(request: CollectionRequest):
    """Fetch reviews from App Store"""
    logger.info(f"Fetching App Store reviews (limit: {request.limit})")
    
    try:
        connector = AppStoreConnector()
        reviews = connector.fetch_reviews(limit=request.limit)
        
        # Validate and clean
        validation = data_quality.validate_batch(reviews, 'appstore')
        cleaned_reviews = data_quality.clean_data(reviews, 'appstore')
        
        # Remove duplicates
        unique_reviews = deduplication.remove_duplicates(cleaned_reviews)
        
        # Log collection run
        db = get_db()
        collection_run = DataCollectionRun(
            source='appstore',
            records_collected=len(unique_reviews),
            status='completed'
        )
        db.add(collection_run)
        db.commit()
        
        return CollectionResponse(
            success=True,
            source='appstore',
            records_collected=len(unique_reviews),
            message=f"Successfully fetched {len(unique_reviews)} App Store reviews",
            data=unique_reviews
        )
        
    except Exception as e:
        logger.error(f"Error fetching App Store reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/playstore/reviews", response_model=CollectionResponse)
async def fetch_playstore_reviews(request: CollectionRequest):
    """Fetch reviews from Play Store"""
    logger.info(f"Fetching Play Store reviews (limit: {request.limit})")
    
    try:
        connector = PlayStoreConnector()
        reviews = connector.fetch_reviews(count=request.limit)
        
        # Validate and clean
        validation = data_quality.validate_batch(reviews, 'playstore')
        cleaned_reviews = data_quality.clean_data(reviews, 'playstore')
        
        # Remove duplicates
        unique_reviews = deduplication.remove_duplicates(cleaned_reviews)
        
        # Log collection run
        db = get_db()
        collection_run = DataCollectionRun(
            source='playstore',
            records_collected=len(unique_reviews),
            status='completed'
        )
        db.add(collection_run)
        db.commit()
        
        return CollectionResponse(
            success=True,
            source='playstore',
            records_collected=len(unique_reviews),
            message=f"Successfully fetched {len(unique_reviews)} Play Store reviews",
            data=unique_reviews
        )
        
    except Exception as e:
        logger.error(f"Error fetching Play Store reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reddit/posts", response_model=CollectionResponse)
async def fetch_reddit_posts(request: CollectionRequest):
    """Fetch posts from Reddit"""
    logger.info(f"Fetching Reddit posts from r/{request.category or 'spotify'} (limit: {request.limit})")
    
    try:
        connector = RedditConnector()
        subreddit = request.category or 'spotify'
        posts = connector.fetch_subreddit_posts(subreddit, limit=request.limit)
        
        # Validate and clean
        validation = data_quality.validate_batch(posts, 'reddit')
        cleaned_posts = data_quality.clean_data(posts, 'reddit')
        
        # Remove duplicates
        unique_posts = deduplication.remove_duplicates(cleaned_posts)
        
        # Log collection run
        db = get_db()
        collection_run = DataCollectionRun(
            source='reddit',
            records_collected=len(unique_posts),
            status='completed'
        )
        db.add(collection_run)
        db.commit()
        
        return CollectionResponse(
            success=True,
            source='reddit',
            records_collected=len(unique_posts),
            message=f"Successfully fetched {len(unique_posts)} Reddit posts",
            data=unique_posts
        )
        
    except Exception as e:
        logger.error(f"Error fetching Reddit posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/forum/threads", response_model=CollectionResponse)
async def fetch_forum_threads(request: CollectionRequest):
    """Fetch threads from Spotify Community Forums"""
    logger.info(f"Fetching forum threads from category: {request.category or 'discovery'} (limit: {request.limit})")
    
    try:
        connector = ForumConnector()
        category = request.category or 'discovery'
        threads = connector.scrape_threads(category, limit=request.limit)
        
        # Validate and clean
        validation = data_quality.validate_batch(threads, 'forum')
        cleaned_threads = data_quality.clean_data(threads, 'forum')
        
        # Remove duplicates
        unique_threads = deduplication.remove_duplicates(cleaned_threads)
        
        # Log collection run
        db = get_db()
        collection_run = DataCollectionRun(
            source='forum',
            records_collected=len(unique_threads),
            status='completed'
        )
        db.add(collection_run)
        db.commit()
        
        return CollectionResponse(
            success=True,
            source='forum',
            records_collected=len(unique_threads),
            message=f"Successfully fetched {len(unique_threads)} forum threads",
            data=unique_threads
        )
        
    except Exception as e:
        logger.error(f"Error fetching forum threads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/social/mentions", response_model=CollectionResponse)
async def fetch_social_mentions(request: CollectionRequest):
    """Fetch mentions from social media"""
    logger.info(f"Fetching social media mentions for query: {request.query or '#spotify'} (limit: {request.limit})")
    
    try:
        connector = SocialMediaConnector()
        query = request.query or '#spotify'
        mentions = connector.fetch_mentions(query, limit=request.limit)
        
        # Validate and clean
        validation = data_quality.validate_batch(mentions, 'twitter')
        cleaned_mentions = data_quality.clean_data(mentions, 'twitter')
        
        # Remove duplicates
        unique_mentions = deduplication.remove_duplicates(cleaned_mentions)
        
        # Log collection run
        db = get_db()
        collection_run = DataCollectionRun(
            source='social',
            records_collected=len(unique_mentions),
            status='completed'
        )
        db.add(collection_run)
        db.commit()
        
        return CollectionResponse(
            success=True,
            source='social',
            records_collected=len(unique_mentions),
            message=f"Successfully fetched {len(unique_mentions)} social media mentions",
            data=unique_mentions
        )
        
    except Exception as e:
        logger.error(f"Error fetching social media mentions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/collection/status")
async def get_collection_status():
    """Get status of recent collection runs"""
    try:
        db = get_db()
        runs = db.query(DataCollectionRun).order_by(DataCollectionRun.start_time.desc()).limit(20).all()
        
        return {
            "success": True,
            "runs": [
                {
                    "id": run.id,
                    "source": run.source,
                    "start_time": run.start_time.isoformat() if run.start_time else None,
                    "end_time": run.end_time.isoformat() if run.end_time else None,
                    "records_collected": run.records_collected,
                    "status": run.status,
                    "error_message": run.error_message
                }
                for run in runs
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching collection status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
