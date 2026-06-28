"""
Diagnostic script to verify the dashboard data pipeline is working correctly.
Run: python scripts/diagnose_dashboard.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from app.database.connection import get_session
from app.database.models import (
    RawReview, ProcessedReview, SentimentAnalysis, TopicAnalysis, EntityAnalysis,
    PatternInsight, UserSegment, RootCauseAnalysisResult, UnmetNeed,
    Recommendation, GeneratedReport
)
from sqlalchemy import text, func

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def diagnose():
    """Run diagnostic checks on the pipeline."""
    db = get_session()
    issues = []
    warnings = []
    
    try:
        logger.info("=== DASHBOARD DATA PIPELINE DIAGNOSTICS ===\n")
        
        # 1. Raw Reviews Count
        logger.info("1. Checking Raw Reviews...")
        raw_count = db.query(func.count(RawReview.id)).scalar() or 0
        logger.info(f"   Raw reviews in database: {raw_count}")
        if raw_count == 0:
            issues.append("❌ No raw reviews found. Data collection may not have completed.")
        elif raw_count < 1000:
            warnings.append(f"⚠️  Only {raw_count} reviews found (expected ~10k)")
        else:
            logger.info(f"   ✅ {raw_count} reviews ready for analysis")
        
        # 2. ProcessedReview Count
        logger.info("\n2. Checking ProcessedReview Table...")
        try:
            processed_count = db.query(func.count(ProcessedReview.id)).scalar() or 0
            logger.info(f"   Processed reviews: {processed_count}")
            if processed_count == 0:
                warnings.append("⚠️  ProcessedReview table is empty. Batch processor hasn't run or needs data.")
            else:
                logger.info(f"   ✅ {processed_count} reviews processed")
        except Exception as e:
            issues.append(f"❌ ProcessedReview table error: {e}")
        
        # 3. Sentiment Analysis
        logger.info("\n3. Checking Sentiment Analysis...")
        sentiment_count = db.query(func.count(SentimentAnalysis.id)).scalar() or 0
        logger.info(f"   Sentiment analyses: {sentiment_count}")
        if sentiment_count == 0:
            issues.append("❌ No sentiment analysis found. LLM pipeline hasn't run.")
        else:
            sentiment_dist = db.execute(text("""
                SELECT sentiment, COUNT(*) as count
                FROM sentiment_analysis
                GROUP BY sentiment
                ORDER BY count DESC
            """))
            logger.info("   Sentiment distribution:")
            for row in sentiment_dist:
                logger.info(f"     - {row[0]}: {row[1]}")
        
        # 4. Topic Analysis
        logger.info("\n4. Checking Topic Analysis...")
        topic_count = db.query(func.count(TopicAnalysis.id)).scalar() or 0
        logger.info(f"   Topic analyses: {topic_count}")
        if topic_count > 0:
            top_topics = db.execute(text("""
                SELECT primary_topic, COUNT(*) as count
                FROM topic_analysis
                WHERE primary_topic IS NOT NULL
                GROUP BY primary_topic
                ORDER BY count DESC
                LIMIT 5
            """))
            logger.info("   Top topics:")
            for row in top_topics:
                logger.info(f"     - {row[0]}: {row[1]}")
        else:
            warnings.append("⚠️  No topics detected. Insights will be limited.")
        
        # 5. Pattern Insights
        logger.info("\n5. Checking Pattern Insights...")
        pattern_count = db.query(func.count(PatternInsight.id)).scalar() or 0
        logger.info(f"   Patterns detected: {pattern_count}")
        if pattern_count == 0:
            issues.append("❌ No patterns found. Run POST /api/insights/generate to generate.")
        else:
            patterns = db.execute(text("""
                SELECT pattern_type, COUNT(*) as count
                FROM pattern_insights
                GROUP BY pattern_type
                ORDER BY count DESC
            """))
            logger.info("   Pattern types:")
            for row in patterns:
                logger.info(f"     - {row[0]}: {row[1]}")
        
        # 6. User Segments
        logger.info("\n6. Checking User Segments...")
        segment_count = db.query(func.count(UserSegment.id)).scalar() or 0
        logger.info(f"   Segments created: {segment_count}")
        if segment_count == 0:
            issues.append("❌ No segments found. Run insight generation.")
        else:
            segments = db.execute(text("""
                SELECT segment_name, user_count
                FROM user_segments
                ORDER BY user_count DESC
                LIMIT 5
            """))
            logger.info("   Top segments:")
            for row in segments:
                logger.info(f"     - {row[0]}: {row[1]} users")
        
        # 7. Root Causes
        logger.info("\n7. Checking Root Cause Analysis...")
        rc_count = db.query(func.count(RootCauseAnalysisResult.id)).scalar() or 0
        logger.info(f"   Root causes analyzed: {rc_count}")
        if rc_count > 0:
            topics = db.execute(text("""
                SELECT issue_topic FROM root_cause_analysis LIMIT 3
            """))
            logger.info("   Topics analyzed:")
            for row in topics:
                logger.info(f"     - {row[0]}")
        
        # 8. Unmet Needs
        logger.info("\n8. Checking Unmet Needs...")
        need_count = db.query(func.count(UnmetNeed.id)).scalar() or 0
        logger.info(f"   Unmet needs identified: {need_count}")
        if need_count > 0:
            needs = db.execute(text("""
                SELECT need_description, priority_score
                FROM unmet_needs
                ORDER BY priority_score DESC
                LIMIT 3
            """))
            logger.info("   Top needs:")
            for row in needs:
                logger.info(f"     - {row[0]} (score: {row[1]})")
        
        # 9. Recommendations
        logger.info("\n9. Checking Recommendations...")
        rec_count = db.query(func.count(Recommendation.id)).scalar() or 0
        logger.info(f"   Recommendations generated: {rec_count}")
        if rec_count > 0:
            recs = db.execute(text("""
                SELECT title, priority, expected_impact
                FROM recommendations
                ORDER BY created_at DESC
                LIMIT 5
            """))
            logger.info("   Recent recommendations:")
            for row in recs:
                logger.info(f"     - {row[0]} ({row[1]} priority, {row[2]} impact)")
        
        # 10. Reports
        logger.info("\n10. Checking Generated Reports...")
        report_count = db.query(func.count(GeneratedReport.id)).scalar() or 0
        logger.info(f"   Reports generated: {report_count}")
        if report_count > 0:
            latest = db.execute(text("""
                SELECT created_at, template_type
                FROM generated_reports
                ORDER BY created_at DESC
                LIMIT 1
            """)).fetchone()
            if latest:
                logger.info(f"   Latest report: {latest[0]} ({latest[1]})")
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("DIAGNOSIS SUMMARY")
        logger.info("=" * 50)
        
        if issues:
            logger.error(f"\n❌ {len(issues)} Critical Issues:")
            for issue in issues:
                logger.error(f"   {issue}")
        
        if warnings:
            logger.warning(f"\n⚠️  {len(warnings)} Warnings:")
            for warning in warnings:
                logger.warning(f"   {warning}")
        
        if not issues and not warnings:
            logger.info("\n✅ All checks passed! Dashboard should be working correctly.")
        elif not issues:
            logger.info("\n✅ No critical issues. Warnings above may need attention.")
        
        # Recommendations
        if sentiment_count == 0 and raw_count > 0:
            logger.info("\n📝 Next Steps:")
            logger.info("   1. Ensure LLM keys are set in .env (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
            logger.info("   2. Run: python -m app.services.processor or POST /api/insights/generate")
            logger.info("   3. Wait for batch processing to complete")
            logger.info("   4. Run this script again to verify")
        
        if pattern_count == 0 and sentiment_count > 0:
            logger.info("\n📝 Next Steps:")
            logger.info("   1. Run: POST /api/insights/generate")
            logger.info("   2. Monitor logs for insight generation completion")
            logger.info("   3. Refresh dashboard")
        
        return len(issues) == 0
        
    except Exception as e:
        logger.error(f"Diagnostic failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = diagnose()
    sys.exit(0 if success else 1)
