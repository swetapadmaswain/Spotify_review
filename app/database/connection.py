from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from loguru import logger
from config.settings import settings

Base = declarative_base()

engine = None
SessionLocal = None


def init_db():
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    try:
        engine = create_engine(settings.database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        from .models import Base
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
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
