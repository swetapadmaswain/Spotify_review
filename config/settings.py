from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/spotify_reviews"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "spotify_reviews"
    db_user: str = "user"
    db_password: str = "password"
    
    # App Store Configuration
    app_store_app_id: str = "324684580"
    app_store_api_key: Optional[str] = None
    
    # Play Store Configuration
    play_store_package_name: str = "com.spotify.music"
    
    # Reddit Configuration
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "SpotifyReviewAnalysis/1.0"
    
    # Twitter Configuration
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    
    # Facebook Configuration
    facebook_app_id: Optional[str] = None
    facebook_app_secret: Optional[str] = None
    facebook_access_token: Optional[str] = None
    
    # S3/MinIO Configuration
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_bucket: str = "spotify-reviews-raw"
    s3_region: str = "us-east-1"
    
    # API Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Data Collection Settings
    reviews_limit: int = 500
    batch_size: int = 500
    
    # Phase 2: AI Analysis Engine Settings
    # Vector Database
    vector_db_path: str = "./vector_db"
    vector_collection_name: str = "spotify_reviews"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    
    # Embedding Settings
    embedding_model: str = "text-embedding-3-small"  # OpenAI
    embedding_dimension: int = 1536
    local_embedding_model: str = "all-MiniLM-L6-v2"  # Fallback
    
    # RAG Settings
    rag_top_k: int = 5
    rag_temperature: float = 0.7
    
    # LLM Settings
    llm_provider: str = "openai"  # openai, anthropic, cohere
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    
    # Redis Configuration (for caching and Celery)
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Phase 4: Reporting & Dashboard
    api_auth_token: Optional[str] = None
    reports_output_dir: str = "./reports"
    dashboard_url: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
