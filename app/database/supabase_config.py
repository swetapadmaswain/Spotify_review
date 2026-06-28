"""
Supabase Configuration Module
Handles all Supabase-specific configurations and utilities
"""
from typing import Optional
from loguru import logger
from config.settings import settings

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase Python client not available. Install with: pip install supabase")


class SupabaseConfig:
    """Configuration and utilities for Supabase connection"""
    
    _instance: Optional['SupabaseConfig'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase configuration"""
        if not SUPABASE_AVAILABLE:
            logger.error("Supabase client not installed")
            raise ImportError("Please install supabase: pip install supabase")
        
        self.url = settings.supabase_url
        self.key = settings.supabase_key
        self.db_host = settings.db_host
        self.db_port = settings.db_port
        self.db_name = settings.db_name
        self.db_user = settings.db_user
        self.db_password = settings.db_password
        
        if not self.url or not self.key:
            logger.error("Supabase URL or Key not configured in settings")
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        logger.info(f"Supabase config initialized for: {self.url}")
    
    @property
    def client(self) -> Client:
        """Get or create Supabase client (for REST API, real-time, etc.)"""
        if self._client is None:
            self._client = create_client(self.url, self.key)
            logger.info("Supabase client created successfully")
        return self._client
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string for SQLAlchemy"""
        return (
            f"postgresql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    def verify_connection(self) -> bool:
        """Verify connection to Supabase"""
        try:
            # Test PostgreSQL connection
            from sqlalchemy import create_engine, text
            engine = create_engine(self.get_connection_string())
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ PostgreSQL connection verified")
            
            # Test Supabase REST API
            response = self.client.auth.get_session()
            logger.info("✅ Supabase REST API connection verified")
            
            return True
        except Exception as e:
            logger.error(f"❌ Supabase connection verification failed: {e}")
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table"""
        try:
            from app.database.connection import get_session
            from sqlalchemy import text
            db = get_session()
            result = db.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
            count = result.fetchone()[0]
            db.close()
            return count
        except Exception as e:
            logger.error(f"Error getting count for {table_name}: {e}")
            return 0


def get_supabase_config() -> SupabaseConfig:
    """Get singleton Supabase configuration instance"""
    return SupabaseConfig()


def verify_supabase() -> bool:
    """Verify Supabase is properly configured and connected"""
    try:
        config = get_supabase_config()
        return config.verify_connection()
    except Exception as e:
        logger.error(f"Supabase verification failed: {e}")
        return False
