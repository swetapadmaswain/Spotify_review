"""
Phase 3 - Segmentation Engine
Segments users by behaviour, demographics, and tenure.
"""
from typing import Dict, List, Any

from loguru import logger

from app.database.connection import get_session
from app.database.models import UserSegment
from app.services.analysis_store import AnalysisStore


def _save_segment(name: str, criteria: Dict, user_count: int,
                  challenges: List[str], avg_sentiment: str) -> None:
    db = get_session()
    try:
        db.add(UserSegment(
            segment_name=name,
            segment_criteria=criteria,
            user_count=user_count,
            primary_challenges=challenges,
            avg_sentiment=avg_sentiment,
        ))
        db.commit()
        logger.info(f"Saved segment: {name} ({user_count} users)")
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving segment: {e}")
    finally:
        db.close()


class UserSegmentationEngine:
    """Segment users by listening behaviour and frustration type."""

    def __init__(self):
        self.store = AnalysisStore()

    def segment_by_listening_behavior(self) -> List[Dict]:
        """Group reviews that mention listening behaviour entities."""
        query = """
        SELECT
            e.entities->>'music_features' AS behavior,
            COUNT(*) AS user_count,
            AVG(s.confidence) AS avg_confidence,
            MODE() WITHIN GROUP (ORDER BY s.sentiment) AS dominant_sentiment
        FROM entity_analysis e
        JOIN sentiment_analysis s ON e.review_id = s.review_id
        WHERE e.entities IS NOT NULL
          AND e.entities->>'music_features' IS NOT NULL
        GROUP BY e.entities->>'music_features'
        ORDER BY user_count DESC
        LIMIT 10
        """
        results = self.store.execute(query)
        logger.info(f"ListeningBehavior segments: {len(results)}")
        return results

    def segment_by_frustration_type(self) -> List[Dict]:
        """Group reviews by technical_terms entity (proxy for frustration type)."""
        query = """
        SELECT
            e.entities->>'technical_terms' AS frustration,
            COUNT(*) AS count,
            t.primary_topic
        FROM entity_analysis e
        JOIN topic_analysis t ON e.review_id = t.review_id
        WHERE e.entities IS NOT NULL
          AND e.entities->>'technical_terms' IS NOT NULL
        GROUP BY e.entities->>'technical_terms', t.primary_topic
        ORDER BY count DESC
        LIMIT 10
        """
        results = self.store.execute(query)
        logger.info(f"FrustrationType segments: {len(results)}")
        return results

    def build_and_save(self, behavior_segments: List[Dict],
                       frustration_segments: List[Dict]) -> None:
        """Persist segments derived from analysis data."""
        for row in behavior_segments[:5]:
            behavior = row.get("behavior") or "unknown"
            _save_segment(
                name=f"Listeners: {behavior}",
                criteria={"music_features": behavior},
                user_count=int(row.get("user_count") or 0),
                challenges=[row.get("dominant_sentiment", "mixed")],
                avg_sentiment=str(row.get("dominant_sentiment") or "neutral"),
            )

        for row in frustration_segments[:3]:
            frustration = row.get("frustration") or "unknown"
            _save_segment(
                name=f"Frustrated by: {frustration}",
                criteria={"technical_terms": frustration, "topic": row.get("primary_topic")},
                user_count=int(row.get("count") or 0),
                challenges=[frustration],
                avg_sentiment="negative",
            )

        if not behavior_segments and not frustration_segments:
            _save_segment(
                name="High-Frustration Users",
                criteria={"sentiment": "negative"},
                user_count=0,
                challenges=["crashes", "slow loading", "UI bugs"],
                avg_sentiment="negative",
            )
            _save_segment(
                name="Discovery Enthusiasts",
                criteria={"topic": "recommendations", "sentiment": "positive"},
                user_count=0,
                challenges=["too-few-genres", "stale playlists"],
                avg_sentiment="positive",
            )


class DemographicSegmentation:
    """Segment feedback by source platform."""

    def __init__(self):
        self.store = AnalysisStore()

    def segment_by_platform(self) -> List[Dict]:
        query = """
        SELECT
            r.source,
            s.sentiment,
            t.primary_topic,
            COUNT(*) AS count
        FROM sentiment_analysis s
        JOIN topic_analysis t ON s.review_id = t.review_id
        JOIN processed_reviews r ON s.review_id = r.id
        GROUP BY r.source, s.sentiment, t.primary_topic
        ORDER BY r.source, count DESC
        """
        results = self.store.execute(query)
        logger.info(f"PlatformSegments: {len(results)} rows")
        return results

    def save_platform_segments(self, platform_rows: List[Dict]) -> None:
        """Create one segment per platform with dominant sentiment."""
        by_source: Dict[str, Dict[str, Any]] = {}
        for row in platform_rows:
            source = row.get("source") or "unknown"
            entry = by_source.setdefault(source, {"count": 0, "sentiments": {}})
            count = int(row.get("count") or 0)
            entry["count"] += count
            sentiment = row.get("sentiment") or "neutral"
            entry["sentiments"][sentiment] = entry["sentiments"].get(sentiment, 0) + count

        for source, data in by_source.items():
            dominant = max(data["sentiments"], key=data["sentiments"].get, default="neutral")
            _save_segment(
                name=f"Platform: {source}",
                criteria={"source": source},
                user_count=data["count"],
                challenges=[],
                avg_sentiment=dominant,
            )

    def segment_by_geography(self) -> Dict:
        """Placeholder – geography data not yet in schema."""
        logger.info("Geography segmentation: no data available yet")
        return {"note": "Geography data not available in current schema"}


class TenureSegmentation:
    """Segment users by review metadata when tenure is available."""

    def __init__(self):
        self.store = AnalysisStore()

    def segment_by_user_tenure(self) -> List[Dict]:
        query = """
        SELECT
            CASE
                WHEN r.version IS NOT NULL AND r.version != '' THEN 'Active User'
                ELSE 'Unknown Tenure'
            END AS tenure_segment,
            t.primary_topic,
            s.sentiment,
            COUNT(*) AS count
        FROM topic_analysis t
        JOIN sentiment_analysis s ON t.review_id = s.review_id
        JOIN processed_reviews r ON t.review_id = r.id
        GROUP BY tenure_segment, t.primary_topic, s.sentiment
        ORDER BY count DESC
        LIMIT 20
        """
        results = self.store.execute(query)
        logger.info(f"TenureSegmentation: {len(results)} rows")
        return results

    def save_tenure_segments(self, tenure_rows: List[Dict]) -> None:
        by_tenure: Dict[str, int] = {}
        for row in tenure_rows:
            segment = row.get("tenure_segment") or "Unknown"
            by_tenure[segment] = by_tenure.get(segment, 0) + int(row.get("count") or 0)

        for segment, count in by_tenure.items():
            _save_segment(
                name=f"Tenure: {segment}",
                criteria={"tenure_segment": segment},
                user_count=count,
                challenges=[],
                avg_sentiment="mixed",
            )
