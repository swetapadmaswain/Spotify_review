"""
Configuration Validation Script
Validates backend, dashboard, and Supabase setup
"""
import sys
import os
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level="INFO"
)

def check_python_packages():
    """Check if required Python packages are installed"""
    logger.info("\n" + "=" * 60)
    logger.info("1. CHECKING PYTHON PACKAGES")
    logger.info("=" * 60)
    
    required_packages = {
        'fastapi': 'FastAPI framework',
        'uvicorn': 'ASGI server',
        'sqlalchemy': 'ORM',
        'psycopg2': 'PostgreSQL driver',
        'loguru': 'Logging',
        'pydantic': 'Data validation',
    }
    
    optional_packages = {
        'supabase': 'Supabase client',
        'openai': 'OpenAI API',
        'anthropic': 'Anthropic API',
    }
    
    all_ok = True
    
    logger.info("\nRequired packages:")
    for package, description in required_packages.items():
        try:
            __import__(package)
            logger.info(f"  ✓ {package}: {description}")
        except ImportError:
            logger.error(f"  ✗ {package}: NOT INSTALLED - {description}")
            all_ok = False
    
    logger.info("\nOptional packages:")
    for package, description in optional_packages.items():
        try:
            __import__(package)
            logger.info(f"  ✓ {package}: {description}")
        except ImportError:
            logger.warning(f"  ⚠ {package}: NOT INSTALLED - {description} (optional)")
    
    return all_ok


def check_environment_variables():
    """Check required environment variables"""
    logger.info("\n" + "=" * 60)
    logger.info("2. CHECKING ENVIRONMENT VARIABLES")
    logger.info("=" * 60)
    
    # Load .env
    env_file = project_root / ".env"
    if not env_file.exists():
        logger.error(f"  ✗ .env file not found at {env_file}")
        return False
    
    # Parse .env
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    required_vars = {
        'DATABASE_URL': 'Database connection string',
        'API_HOST': 'Backend host',
        'API_PORT': 'Backend port',
        'DASHBOARD_URL': 'Dashboard URL',
    }
    
    optional_vars = {
        'SUPABASE_URL': 'Supabase REST API URL',
        'SUPABASE_KEY': 'Supabase API key',
        'OPENAI_API_KEY': 'OpenAI API key',
        'ANTHROPIC_API_KEY': 'Anthropic API key',
    }
    
    all_ok = True
    
    logger.info("\nRequired environment variables:")
    for var, description in required_vars.items():
        if var in env_vars:
            value = env_vars[var]
            if len(value) > 20:
                value = value[:20] + "..."
            logger.info(f"  ✓ {var}={value} ({description})")
        else:
            logger.error(f"  ✗ {var} NOT SET - {description}")
            all_ok = False
    
    logger.info("\nOptional environment variables:")
    for var, description in optional_vars.items():
        if var in env_vars:
            value = env_vars[var]
            if len(value) > 20:
                value = value[:20] + "..."
            logger.info(f"  ✓ {var}={value} ({description})")
        else:
            logger.warning(f"  ⚠ {var} NOT SET - {description} (optional)")
    
    return all_ok


def check_files_exist():
    """Check if required files exist"""
    logger.info("\n" + "=" * 60)
    logger.info("3. CHECKING REQUIRED FILES")
    logger.info("=" * 60)
    
    required_files = {
        'app/api/server.py': 'Backend server',
        'app/database/connection.py': 'Database connection',
        'app/database/models.py': 'Database models',
        'app/database/supabase_config.py': 'Supabase config',
        'dashboard/src/App.tsx': 'Dashboard main',
        'dashboard/src/api/client.ts': 'API client',
        'dashboard/.env': 'Dashboard env',
        'config/settings.py': 'Settings',
        'scripts/start_backend.py': 'Startup script',
    }
    
    all_ok = True
    
    logger.info("\nRequired files:")
    for filepath, description in required_files.items():
        full_path = project_root / filepath
        if full_path.exists():
            logger.info(f"  ✓ {filepath} ({description})")
        else:
            logger.error(f"  ✗ {filepath} NOT FOUND - {description}")
            all_ok = False
    
    return all_ok


def check_dashboard_env():
    """Check dashboard environment configuration"""
    logger.info("\n" + "=" * 60)
    logger.info("4. CHECKING DASHBOARD CONFIGURATION")
    logger.info("=" * 60)
    
    dashboard_env = project_root / "dashboard" / ".env"
    if not dashboard_env.exists():
        logger.error(f"  ✗ dashboard/.env not found")
        return False
    
    env_vars = {}
    with open(dashboard_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    required = ['VITE_API_URL']
    
    logger.info("\nDashboard .env configuration:")
    all_ok = True
    for var in required:
        if var in env_vars:
            value = env_vars[var]
            logger.info(f"  ✓ {var}={value}")
        else:
            logger.error(f"  ✗ {var} NOT SET in dashboard/.env")
            all_ok = False
    
    return all_ok


def check_database_connection():
    """Check database connection"""
    logger.info("\n" + "=" * 60)
    logger.info("5. CHECKING DATABASE CONNECTION")
    logger.info("=" * 60)
    
    try:
        from config.settings import settings
        from app.database.connection import init_db, get_session
        from sqlalchemy import text
        
        logger.info(f"\nDatabase URL: {settings.database_url[:50]}...")
        
        logger.info("Attempting connection...")
        if not init_db():
            logger.error("  ✗ Failed to initialize database")
            return False
        
        logger.info("  ✓ Database connection established")
        
        # Check tables
        logger.info("\nChecking tables...")
        db = get_session()
        
        tables_to_check = [
            'raw_reviews',
            'sentiment_analysis',
            'pattern_insights',
            'user_segments',
            'recommendations',
        ]
        
        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                logger.info(f"  ✓ {table}: {count} rows")
            except Exception as e:
                logger.warning(f"  ⚠ {table}: Unable to query")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Database connection failed: {e}")
        return False


def check_api_endpoints():
    """Check if API endpoints are defined"""
    logger.info("\n" + "=" * 60)
    logger.info("6. CHECKING API ENDPOINTS")
    logger.info("=" * 60)
    
    try:
        from app.api.insights_routes import router as insights_router
        from app.api.reporting_routes import router as reporting_router
        
        logger.info("\nInsights endpoints:")
        endpoints = [
            'GET /api/insights/summary',
            'GET /api/insights/patterns',
            'GET /api/insights/segments',
            'GET /api/insights/root-causes',
            'GET /api/insights/unmet-needs',
            'POST /api/insights/generate',
        ]
        
        for endpoint in endpoints:
            logger.info(f"  ✓ {endpoint}")
        
        logger.info("\nReporting endpoints:")
        endpoints = [
            'GET /api/analytics/sentiment-trends',
            'GET /api/analytics/topic-evolution',
            'GET /api/analytics/sentiment-distribution',
            'GET /api/recommendations',
            'POST /api/reports/generate',
        ]
        
        for endpoint in endpoints:
            logger.info(f"  ✓ {endpoint}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Error checking endpoints: {e}")
        return False


def generate_summary():
    """Generate validation summary"""
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    results = {
        "Python Packages": check_python_packages(),
        "Environment Variables": check_environment_variables(),
        "Required Files": check_files_exist(),
        "Dashboard Config": check_dashboard_env(),
        "API Endpoints": check_api_endpoints(),
        "Database Connection": check_database_connection(),
    }
    
    logger.info("\nValidation Results:")
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status} - {check}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n✅ ALL VALIDATIONS PASSED!")
        logger.info("\nNext steps:")
        logger.info("  1. Start backend: python scripts/start_backend.py")
        logger.info("  2. Start dashboard: cd dashboard && npm run dev")
        logger.info("  3. Open http://localhost:5173")
    else:
        logger.error("\n❌ SOME VALIDATIONS FAILED")
        logger.error("\nPlease fix the issues above and run again:")
        logger.error("  python scripts/validate_setup.py")
    
    return all_passed


def main():
    """Main validation flow"""
    try:
        logger.info("=" * 60)
        logger.info("CONFIGURATION VALIDATION")
        logger.info("=" * 60)
        
        all_passed = generate_summary()
        
        return 0 if all_passed else 1
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
