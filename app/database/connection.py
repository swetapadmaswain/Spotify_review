from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from loguru import logger
from config.settings import settings

Base = declarative_base()

engine = None
SessionLocal = None


def get_database_url() -> str:
    """
    Get database URL from settings.
    Supports both direct postgres URL and Supabase configuration
    """
    # If DATABASE_URL is explicitly set, use it
    if settings.database_url and settings.database_url != "postgresql://user:password@localhost:5432/spotify_reviews":
        return settings.database_url
    
    # Try to build from Supabase config
    if settings.supabase_url:
        try:
            from app.database.supabase_config import get_supabase_config
            config = get_supabase_config()
            url = config.get_connection_string()
            logger.info(f"Using Supabase PostgreSQL: {config.db_host}")
            return url
        except Exception as e:
            logger.warning(f"Could not use Supabase config: {e}, falling back to DATABASE_URL")
    
    # Fallback to settings
    return settings.database_url


def init_db():
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url, echo=False, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        from .models import Base
        Base.metadata.create_all(bind=engine)
        
        logger.info(f"✅ Database initialized successfully")
        logger.info(f"   Connection: {db_url[:50]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False


def get_session() -> Session:
    """Get a new database session. Prefer this over importing SessionLocal directly."""
    global SessionLocal

    if SessionLocal is None:
        init_db()

    return SessionLocal()


def get_db() -> Session:
    """Get database session"""
    try:
        return get_session()
    except Exception as e:
        logger.error(f"Error getting database session: {e}")
        raise


def close_db(db: Session):
    """Close database session"""
    try:
        db.close()
    except Exception as e:
        logger.error(f"Error closing database session: {e}")
