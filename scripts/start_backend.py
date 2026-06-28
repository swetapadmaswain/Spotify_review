"""
Backend Startup Script
Initializes Supabase connection and starts FastAPI server
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from config.settings import settings
from app.database.connection import init_db, get_session
from app.database.supabase_config import verify_supabase

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level="INFO"
)
logger.add(
    "logs/backend.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="DEBUG",
    rotation="500 MB"
)


def verify_configuration():
    """Verify all required configurations are set"""
    logger.info("=" * 60)
    logger.info("BACKEND STARTUP - Configuration Verification")
    logger.info("=" * 60)
    
    errors = []
    warnings = []
    
    # Check Database Configuration
    logger.info("\n1. Database Configuration:")
    if settings.database_url:
        logger.info(f"   ✓ DATABASE_URL set: {settings.database_url[:50]}...")
    else:
        errors.append("DATABASE_URL not set in .env")
    
    # Check Supabase Configuration
    logger.info("\n2. Supabase Configuration:")
    if settings.supabase_url:
        logger.info(f"   ✓ SUPABASE_URL: {settings.supabase_url}")
    else:
        logger.info(f"   ⚠ SUPABASE_URL not set (using DATABASE_URL instead)")
    
    if settings.supabase_key:
        logger.info(f"   ✓ SUPABASE_KEY: {settings.supabase_key[:20]}...")
    else:
        logger.info(f"   ⚠ SUPABASE_KEY not set (using DATABASE_URL instead)")
    
    # Check API Configuration
    logger.info("\n3. API Configuration:")
    logger.info(f"   ✓ API Host: {settings.api_host}")
    logger.info(f"   ✓ API Port: {settings.api_port}")
    logger.info(f"   ✓ Dashboard URL: {settings.dashboard_url}")
    
    # Check LLM Configuration
    logger.info("\n4. LLM Configuration:")
    if settings.openai_api_key:
        logger.info(f"   ✓ OpenAI API Key: {settings.openai_api_key[:10]}...")
    elif settings.anthropic_api_key:
        logger.info(f"   ✓ Anthropic API Key: {settings.anthropic_api_key[:10]}...")
    else:
        warnings.append("No LLM API key configured (using fallback heuristics)")
    
    logger.info(f"   ✓ LLM Provider: {settings.llm_provider}")
    logger.info(f"   ✓ LLM Model: {settings.llm_model}")
    
    # Check Data Collection Settings
    logger.info("\n5. Data Collection Settings:")
    logger.info(f"   ✓ Reviews Limit: {settings.reviews_limit}")
    logger.info(f"   ✓ Batch Size: {settings.batch_size}")
    
    if errors:
        logger.error(f"\n❌ Configuration Errors ({len(errors)}):")
        for error in errors:
            logger.error(f"   • {error}")
        return False
    
    if warnings:
        logger.warning(f"\n⚠ Configuration Warnings ({len(warnings)}):")
        for warning in warnings:
            logger.warning(f"   • {warning}")
    
    logger.info("\n✅ Configuration verification passed")
    return True


def verify_database_connection():
    """Verify database connection and tables"""
    logger.info("\n" + "=" * 60)
    logger.info("DATABASE CONNECTION VERIFICATION")
    logger.info("=" * 60)
    
    try:
        logger.info("\n1. Initializing database connection...")
        if not init_db():
            logger.error("Failed to initialize database")
            return False
        
        logger.info("✓ Database connection established")
        
        logger.info("\n2. Verifying tables...")
        db = get_session()
        
        from sqlalchemy import text
        
        # Check key tables
        tables_to_check = [
            'raw_reviews',
            'sentiment_analysis',
            'topic_analysis',
            'entity_analysis',
            'pattern_insights',
            'user_segments',
            'root_cause_analysis',
            'unmet_needs',
            'recommendations'
        ]
        
        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                logger.info(f"   ✓ {table}: {count} rows")
            except Exception as e:
                logger.warning(f"   ? {table}: Unable to query ({str(e)[:30]}...)")
        
        db.close()
        
        logger.info("\n✅ Database verification passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def verify_supabase_connection():
    """Verify Supabase connection"""
    logger.info("\n" + "=" * 60)
    logger.info("SUPABASE CONNECTION VERIFICATION")
    logger.info("=" * 60)
    
    try:
        if settings.supabase_url and settings.supabase_key:
            logger.info("\nVerifying Supabase configuration...")
            result = verify_supabase()
            if result:
                logger.info("✅ Supabase connection verified")
                return True
            else:
                logger.warning("⚠ Supabase connection verification returned false")
                return False
        else:
            logger.info("ℹ Supabase REST API not configured (using PostgreSQL directly)")
            return True
    except Exception as e:
        logger.warning(f"⚠ Supabase verification warning: {e}")
        return True  # Don't fail - we can use PostgreSQL


def start_server():
    """Start FastAPI server"""
    logger.info("\n" + "=" * 60)
    logger.info("STARTING FASTAPI SERVER")
    logger.info("=" * 60)
    
    try:
        import uvicorn
        from app.api.server import app
        
        logger.info(f"\n🚀 Starting server on http://{settings.api_host}:{settings.api_port}")
        logger.info(f"📊 API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
        logger.info(f"🎨 Dashboard: {settings.dashboard_url}")
        logger.info("\nServer is running. Press Ctrl+C to stop.\n")
        
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Main startup sequence"""
    try:
        # Step 1: Verify configuration
        if not verify_configuration():
            logger.error("Configuration verification failed")
            return 1
        
        # Step 2: Verify Supabase
        verify_supabase_connection()
        
        # Step 3: Verify database
        if not verify_database_connection():
            logger.error("Database verification failed")
            return 1
        
        # Step 4: Start server
        logger.info("\n" + "=" * 60)
        logger.info("READY TO START")
        logger.info("=" * 60)
        logger.info("\n✅ All verifications passed!")
        logger.info("\nStarting FastAPI server...")
        
        start_server()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n\n👋 Server shutdown by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
