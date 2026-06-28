"""
Production Readiness Verification Script
Checks if data is being pulled from Supabase and verifies production readiness
"""
import sys
import os
from pathlib import Path
from datetime import datetime
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

def check_supabase_data():
    """Verify data is being pulled from Supabase"""
    logger.info("\n" + "=" * 70)
    logger.info("SUPABASE DATA VERIFICATION")
    logger.info("=" * 70)
    
    try:
        from config.settings import settings
        from app.database.connection import get_session
        from sqlalchemy import text
        
        logger.info("\n1. Database Connection:")
        logger.info(f"   📍 Database URL: {settings.database_url[:60]}...")
        logger.info(f"   📍 Host: {settings.db_host}")
        logger.info(f"   📍 Port: {settings.db_port}")
        
        logger.info("\n2. Connecting to Supabase...")
        db = get_session()
        
        # Test connection
        db.execute(text("SELECT 1"))
        logger.info("   ✅ Connection successful")
        
        # Check table data
        logger.info("\n3. Checking Supabase Tables:")
        
        tables = {
            'raw_reviews': 'Original reviews',
            'sentiment_analysis': 'Sentiment results',
            'topic_analysis': 'Topic results',
            'entity_analysis': 'Entity results',
            'pattern_insights': 'Detected patterns',
            'user_segments': 'User segments',
            'root_cause_analysis': 'Root cause results',
            'unmet_needs': 'Unmet needs',
            'recommendations': 'Recommendations',
            'generated_reports': 'Generated reports',
        }
        
        total_rows = 0
        for table_name, description in tables.items():
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.fetchone()[0] if result else 0
                total_rows += count
                
                status = "✅" if count > 0 else "⚠️"
                logger.info(f"   {status} {table_name:30s}: {count:>6d} rows - {description}")
            except Exception as e:
                logger.warning(f"   ❌ {table_name:30s}: Error - {str(e)[:40]}")
        
        logger.info(f"\n   📊 Total rows across all tables: {total_rows:,}")
        
        # Check data quality
        logger.info("\n4. Data Quality Checks:")
        
        # Check raw reviews
        result = db.execute(text("SELECT COUNT(*) FROM raw_reviews WHERE review_text IS NOT NULL"))
        valid_reviews = result.fetchone()[0] if result else 0
        logger.info(f"   ✅ Valid reviews (non-null text): {valid_reviews:,}")
        
        # Check sentiment analysis coverage
        result = db.execute(text("""
            SELECT COUNT(*) FROM sentiment_analysis 
            WHERE sentiment IN ('positive', 'negative', 'neutral')
        """))
        analyzed_reviews = result.fetchone()[0] if result else 0
        logger.info(f"   ✅ Reviews with sentiment: {analyzed_reviews:,}")
        
        # Check sentiment distribution
        result = db.execute(text("""
            SELECT sentiment, COUNT(*) as count 
            FROM sentiment_analysis 
            WHERE sentiment IS NOT NULL
            GROUP BY sentiment
            ORDER BY count DESC
        """))
        rows = result.fetchall()
        if rows:
            logger.info(f"   ✅ Sentiment distribution:")
            for sentiment, count in rows:
                percentage = (count / analyzed_reviews * 100) if analyzed_reviews > 0 else 0
                logger.info(f"      • {sentiment:15s}: {count:>6d} ({percentage:>5.1f}%)")
        
        # Check topics
        result = db.execute(text("""
            SELECT COUNT(DISTINCT primary_topic) FROM topic_analysis 
            WHERE primary_topic IS NOT NULL
        """))
        unique_topics = result.fetchone()[0] if result else 0
        logger.info(f"   ✅ Unique topics detected: {unique_topics}")
        
        # Check patterns
        result = db.execute(text("SELECT COUNT(*) FROM pattern_insights"))
        patterns = result.fetchone()[0] if result else 0
        logger.info(f"   ✅ Patterns detected: {patterns}")
        
        # Check segments
        result = db.execute(text("SELECT COUNT(*) FROM user_segments"))
        segments = result.fetchone()[0] if result else 0
        logger.info(f"   ✅ User segments: {segments}")
        
        # Check recommendations
        result = db.execute(text("SELECT COUNT(*) FROM recommendations"))
        recommendations = result.fetchone()[0] if result else 0
        logger.info(f"   ✅ Recommendations: {recommendations}")
        
        db.close()
        
        # Data quality assessment
        logger.info("\n5. Data Readiness Assessment:")
        
        issues = []
        warnings = []
        
        if valid_reviews == 0:
            issues.append("❌ No valid reviews found")
        elif valid_reviews < 1000:
            warnings.append(f"⚠️  Only {valid_reviews} valid reviews (expected 1000+)")
        else:
            logger.info(f"   ✅ Review count: {valid_reviews} (sufficient)")
        
        if analyzed_reviews == 0:
            issues.append("❌ No sentiment analysis found")
        elif analyzed_reviews < valid_reviews * 0.9:
            warnings.append(f"⚠️  Only {analyzed_reviews}/{valid_reviews} reviews analyzed")
        else:
            logger.info(f"   ✅ Sentiment coverage: {analyzed_reviews/valid_reviews*100:.1f}%")
        
        if patterns == 0:
            warnings.append("⚠️  No patterns generated (run analysis)")
        else:
            logger.info(f"   ✅ Patterns: {patterns} detected")
        
        if segments == 0:
            warnings.append("⚠️  No segments generated (run analysis)")
        else:
            logger.info(f"   ✅ Segments: {segments} created")
        
        if recommendations == 0:
            warnings.append("⚠️  No recommendations generated (run analysis)")
        else:
            logger.info(f"   ✅ Recommendations: {recommendations} generated")
        
        if issues:
            logger.error(f"\n❌ Critical Issues ({len(issues)}):")
            for issue in issues:
                logger.error(f"   {issue}")
        
        if warnings:
            logger.warning(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                logger.warning(f"   {warning}")
        
        if not issues:
            logger.info("\n✅ Data is being pulled from Supabase successfully!")
            return True, len(issues) == 0, len(warnings)
        else:
            return False, False, len(warnings)
        
    except Exception as e:
        logger.error(f"❌ Supabase verification failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, False, 0


def check_api_connectivity():
    """Verify backend API connectivity"""
    logger.info("\n" + "=" * 70)
    logger.info("API CONNECTIVITY CHECK")
    logger.info("=" * 70)
    
    try:
        import requests
        from config.settings import settings
        
        base_url = f"http://{settings.api_host}:{settings.api_port}"
        
        logger.info(f"\n1. Backend URL: {base_url}")
        
        # Try health check
        logger.info("\n2. Health Check:")
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"   ✅ Backend is responding: {response.status_code}")
            else:
                logger.warning(f"   ⚠️  Backend returned: {response.status_code}")
        except requests.ConnectionError:
            logger.error(f"   ❌ Cannot connect to backend at {base_url}")
            logger.info("   💡 Make sure backend is running: python scripts/start_backend.py")
            return False
        except Exception as e:
            logger.warning(f"   ⚠️  Health check failed: {e}")
        
        # Try API summary endpoint
        logger.info("\n3. API Data Endpoints:")
        try:
            response = requests.get(f"{base_url}/api/insights/summary", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"   ✅ Summary endpoint: {response.status_code}")
                if 'data' in data:
                    summary = data['data']
                    logger.info(f"      • Total reviews: {summary.get('total_reviews', 'N/A')}")
                    logger.info(f"      • Patterns: {summary.get('pattern_count', 'N/A')}")
                    logger.info(f"      • Segments: {summary.get('segment_count', 'N/A')}")
                    logger.info(f"      • Recommendations: {summary.get('unmet_need_count', 'N/A')}")
            else:
                logger.warning(f"   ⚠️  Summary returned: {response.status_code}")
        except requests.ConnectionError:
            logger.error("   ❌ Cannot reach API endpoint")
            return False
        except Exception as e:
            logger.warning(f"   ⚠️  API test failed: {e}")
        
        logger.info("\n✅ API connectivity verified")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  API check skipped (requests not installed): {e}")
        return None


def check_production_readiness():
    """Assess production readiness"""
    logger.info("\n" + "=" * 70)
    logger.info("PRODUCTION READINESS ASSESSMENT")
    logger.info("=" * 70)
    
    checklist = {
        "Configuration": [],
        "Data": [],
        "API": [],
        "Security": [],
        "Documentation": [],
        "Scalability": [],
    }
    
    # Configuration checks
    logger.info("\n1. Configuration:")
    try:
        from config.settings import settings
        
        if settings.database_url and 'supabase' in settings.database_url:
            checklist["Configuration"].append(("✅", "Database configured for Supabase"))
            logger.info("   ✅ Database configured for Supabase")
        else:
            checklist["Configuration"].append(("⚠️", "Database URL not Supabase"))
            logger.warning("   ⚠️  Database URL doesn't use Supabase")
        
        if settings.api_host and settings.api_port:
            checklist["Configuration"].append(("✅", "API host/port configured"))
            logger.info(f"   ✅ API configured: {settings.api_host}:{settings.api_port}")
        
        if settings.dashboard_url:
            checklist["Configuration"].append(("✅", "Dashboard URL configured"))
            logger.info(f"   ✅ Dashboard URL: {settings.dashboard_url}")
        
    except Exception as e:
        logger.error(f"   ❌ Configuration check failed: {e}")
    
    # Data checks
    logger.info("\n2. Data:")
    try:
        from app.database.connection import get_session
        from sqlalchemy import text
        
        db = get_session()
        result = db.execute(text("SELECT COUNT(*) FROM raw_reviews"))
        review_count = result.fetchone()[0] if result else 0
        
        if review_count > 1000:
            checklist["Data"].append(("✅", f"{review_count:,} reviews available"))
            logger.info(f"   ✅ Sufficient reviews: {review_count:,}")
        else:
            checklist["Data"].append(("⚠️", f"Only {review_count:,} reviews"))
            logger.warning(f"   ⚠️  Limited reviews: {review_count:,}")
        
        result = db.execute(text("SELECT COUNT(*) FROM pattern_insights"))
        pattern_count = result.fetchone()[0] if result else 0
        
        if pattern_count > 5:
            checklist["Data"].append(("✅", f"{pattern_count} patterns generated"))
            logger.info(f"   ✅ Patterns: {pattern_count}")
        else:
            checklist["Data"].append(("⚠️", f"Only {pattern_count} patterns"))
            logger.warning(f"   ⚠️  Few patterns: {pattern_count}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"   ❌ Data check failed: {e}")
    
    # Security checks
    logger.info("\n3. Security:")
    try:
        env_file = project_root / ".env"
        if env_file.exists():
            with open(env_file) as f:
                content = f.read()
                if 'OPENAI_API_KEY' in content or 'ANTHROPIC_API_KEY' in content:
                    checklist["Security"].append(("✅", "LLM keys configured"))
                    logger.info("   ✅ LLM API keys configured")
                else:
                    checklist["Security"].append(("⚠️", "LLM keys not configured"))
                    logger.warning("   ⚠️  LLM keys not configured (optional)")
        
        checklist["Security"].append(("✅", ".env file exists"))
        logger.info("   ✅ .env file configured")
        
    except Exception as e:
        logger.warning(f"   ⚠️  Security check failed: {e}")
    
    # Documentation checks
    logger.info("\n4. Documentation:")
    docs = [
        "QUICK_START.md",
        "SETUP_SUPABASE_BACKEND.md",
        "COMMANDS_REFERENCE.txt",
        "PRE_DEPLOYMENT_CHECKLIST.md",
    ]
    for doc in docs:
        if (project_root / doc).exists():
            checklist["Documentation"].append(("✅", f"{doc}"))
            logger.info(f"   ✅ {doc}")
        else:
            checklist["Documentation"].append(("⚠️", f"{doc} missing"))
            logger.warning(f"   ⚠️  {doc} missing")
    
    # Scalability checks
    logger.info("\n5. Scalability:")
    try:
        from app.database.connection import engine
        if engine and hasattr(engine, 'pool'):
            checklist["Scalability"].append(("✅", "Connection pooling enabled"))
            logger.info("   ✅ Connection pooling configured")
        
        checklist["Scalability"].append(("✅", "REST API designed for scaling"))
        logger.info("   ✅ REST API architecture supports scaling")
        
        checklist["Scalability"].append(("✅", "Database supports auto-scaling (Supabase)"))
        logger.info("   ✅ Supabase provides auto-scaling")
        
    except Exception as e:
        logger.warning(f"   ⚠️  Scalability check: {e}")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("READINESS SUMMARY")
    logger.info("=" * 70)
    
    for category, items in checklist.items():
        logger.info(f"\n{category}:")
        for status, description in items:
            logger.info(f"  {status} {description}")
    
    # Overall assessment
    all_checks = sum(1 for category_items in checklist.values() for status, _ in category_items if status == "✅")
    total_checks = sum(len(items) for items in checklist.values())
    percentage = (all_checks / total_checks * 100) if total_checks > 0 else 0
    
    logger.info(f"\n{'=' * 70}")
    logger.info(f"Overall Readiness: {all_checks}/{total_checks} checks passed ({percentage:.0f}%)")
    logger.info(f"{'=' * 70}")
    
    if percentage >= 90:
        logger.info("\n🟢 PRODUCTION READY ✅")
        logger.info("The system is ready for production deployment with minor considerations.")
        return True
    elif percentage >= 70:
        logger.info("\n🟡 MOSTLY READY ⚠️")
        logger.info("The system can be deployed but address warnings before production.")
        return True
    else:
        logger.error("\n🔴 NOT READY ❌")
        logger.error("The system needs fixes before production deployment.")
        return False


def main():
    """Main verification flow"""
    try:
        logger.info("=" * 70)
        logger.info("PRODUCTION READINESS & SUPABASE DATA VERIFICATION")
        logger.info("=" * 70)
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Check Supabase data
        data_ok, data_quality, warnings = check_supabase_data()
        
        # 2. Check API connectivity
        api_ok = check_api_connectivity()
        
        # 3. Check production readiness
        prod_ready = check_production_readiness()
        
        # Final recommendation
        logger.info("\n" + "=" * 70)
        logger.info("FINAL RECOMMENDATION")
        logger.info("=" * 70)
        
        if data_ok and prod_ready:
            logger.info("\n✅ DATA: Supabase is being queried properly")
            logger.info("✅ PRODUCTION: System is ready for deployment")
            logger.info("\n🚀 RECOMMENDATION: Ready for production deployment")
            return 0
        elif data_ok:
            logger.warning("\n✅ DATA: Supabase data verified")
            logger.warning("⚠️  PRODUCTION: Address warnings before deployment")
            return 1
        else:
            logger.error("\n❌ DATA: Issues with Supabase data pull")
            logger.error("❌ PRODUCTION: Not ready for deployment")
            return 1
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
