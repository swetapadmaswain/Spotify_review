"""
Phase 3 - Pattern Detection Engine
Detects temporal, thematic, and cross-platform patterns from the Analysis Store.
"""
from typing import Dict, List, Any

from loguru import logger

from app.database.connection import get_session
from app.database.models import PatternInsight
from app.services.analysis_store import AnalysisStore


class TemporalPatternDetector:
    """Detect sentiment trends and seasonal patterns over time."""

    def __init__(self):
        self.store = AnalysisStore()

    def detect_trends(self, time_window: str = "30d") -> List[Dict]:
        """Analyse daily sentiment distribution over the last N days."""
        days = int(time_window.rstrip("d")) if time_window.endswith("d") else 30
        query = f"""
        SELECT
            DATE(analyzed_at) AS date,
            sentiment,
            COUNT(*) AS count
        FROM sentiment_analysis
        WHERE analyzed_at >= NOW() - INTERVAL '{days} days'
        GROUP BY DATE(analyzed_at), sentiment
        ORDER BY DATE(analyzed_at)
        """
        results = self.store.execute(query)
        logger.info(f"TemporalPatternDetector: found {len(results)} rows over {days}d window")
        return results

    def analyze_trends(self, results: List[Dict]) -> List[Dict]:
        """Summarise significant sentiment shifts from raw trend rows."""
        if not results:
            return []

        by_date: Dict[str, Dict[str, int]] = {}
        for row in results:
            date_key = str(row.get("date", ""))
            sentiment = row.get("sentiment") or "unknown"
            by_date.setdefault(date_key, {})[sentiment] = row.get("count", 0)

        trends = []
        dates = sorted(by_date.keys())
        for date_key in dates:
            counts = by_date[date_key]
            total = sum(counts.values())
            negative = counts.get("negative", 0)
            positive = counts.get("positive", 0)
            if total and negative / total >= 0.5:
                trends.append({
                    "date": date_key,
                    "pattern": "negative_sentiment_spike",
                    "negative_share": round(negative / total, 2),
                    "count": total,
                })
            elif total and positive / total >= 0.6:
                trends.append({
                    "date": date_key,
                    "pattern": "positive_sentiment_peak",
                    "positive_share": round(positive / total, 2),
                    "count": total,
                })
        return trends

    def detect_seasonal_patterns(self) -> Dict[str, Any]:
        """Detect month-level seasonal patterns in sentiment."""
        query = """
        SELECT
            EXTRACT(MONTH FROM analyzed_at) AS month,
            sentiment,
            COUNT(*) AS count
        FROM sentiment_analysis
        GROUP BY EXTRACT(MONTH FROM analyzed_at), sentiment
        ORDER BY month
        """
        results = self.store.execute(query)
        logger.info(f"SeasonalPattern: {len(results)} rows")
        return {"seasonal_data": results}

    def save_pattern(self, description: str, frequency: int, time_period: str,
                     confidence: float = 0.7) -> None:
        db = get_session()
        try:
            db.add(PatternInsight(
                pattern_type="temporal",
                pattern_description=description,
                frequency=frequency,
                confidence=confidence,
                time_period=time_period,
            ))
            db.commit()
            logger.info(f"Saved temporal pattern: {description[:60]}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving temporal pattern: {e}")
        finally:
            db.close()


class ThematicPatternDetector:
    """Identify emerging and clustering topics in user feedback."""

    def __init__(self):
        self.store = AnalysisStore()

    def detect_emerging_topics(self, threshold: float = 0.05) -> List[Dict]:
        """Topics that appear in > threshold fraction of recent reviews."""
        query = """
        SELECT
            primary_topic,
            COUNT(*) AS frequency,
            COUNT(*) * 1.0 / NULLIF(
                (SELECT COUNT(*) FROM topic_analysis
                 WHERE analyzed_at >= NOW() - INTERVAL '7 days'), 0
            ) AS share
        FROM topic_analysis
        WHERE analyzed_at >= NOW() - INTERVAL '7 days'
          AND primary_topic IS NOT NULL
        GROUP BY primary_topic
        ORDER BY frequency DESC
        """
        results = self.store.execute(query)
        emerging = [r for r in results if (r.get("share") or 0) >= threshold]
        logger.info(f"ThematicPatternDetector: {len(emerging)} emerging topics")
        return emerging

    def detect_topic_clusters(self) -> List[Dict]:
        """Group topics by frequency across all time."""
        query = """
        SELECT
            t.primary_topic,
            COUNT(*) AS total,
            ARRAY_AGG(DISTINCT s.sentiment) AS sentiments
        FROM topic_analysis t
        JOIN sentiment_analysis s ON t.review_id = s.review_id
        WHERE t.primary_topic IS NOT NULL
        GROUP BY t.primary_topic
        ORDER BY total DESC
        LIMIT 20
        """
        results = self.store.execute(query)
        logger.info(f"TopicClusters: {len(results)} clusters")
        return results

    def save_pattern(self, topic: str, frequency: int, confidence: float = 0.75) -> None:
        db = get_session()
        try:
            db.add(PatternInsight(
                pattern_type="thematic",
                pattern_description=f"Emerging topic: {topic}",
                frequency=frequency,
                confidence=confidence,
                time_period="7d",
            ))
            db.commit()
            logger.info(f"Saved thematic pattern: {topic}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving thematic pattern: {e}")
        finally:
            db.close()


class CrossPlatformPatternDetector:
    """Compare sentiment and topics across different data sources."""

    def __init__(self):
        self.store = AnalysisStore()

    def detect_platform_differences(self) -> List[Dict]:
        """Compare topic+sentiment breakdown by source platform."""
        query = """
        SELECT
            r.source,
            t.primary_topic,
            s.sentiment,
            COUNT(*) AS count
        FROM topic_analysis t
        JOIN sentiment_analysis s ON t.review_id = s.review_id
        JOIN processed_reviews r ON t.review_id = r.id
        GROUP BY r.source, t.primary_topic, s.sentiment
        ORDER BY r.source, count DESC
        """
        results = self.store.execute(query)
        logger.info(f"CrossPlatformDetector: {len(results)} rows")
        return results

    def save_pattern(self, description: str, frequency: int, confidence: float = 0.65) -> None:
        db = get_session()
        try:
            db.add(PatternInsight(
                pattern_type="cross_platform",
                pattern_description=description,
                frequency=frequency,
                confidence=confidence,
                time_period="all_time",
            ))
            db.commit()
            logger.info(f"Saved cross-platform pattern: {description[:60]}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving cross-platform pattern: {e}")
        finally:
            db.close()
