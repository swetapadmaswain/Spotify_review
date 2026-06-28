"""
Phase 4 - Analytics Store
Provides sentiment trends and topic evolution queries for the dashboard.
"""
from typing import Dict, List, Any

from loguru import logger

from app.services.analysis_store import AnalysisStore


class AnalyticsStore:
    """Analytics queries over the analysis store."""

    def __init__(self):
        self.store = AnalysisStore()

    def get_sentiment_trends(self, days: int = 30) -> List[Dict[str, Any]]:
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
        logger.info(f"Sentiment trends: {len(results)} rows over {days}d")
        return results

    def get_topic_evolution(self, days: int = 30) -> List[Dict[str, Any]]:
        query = f"""
        SELECT
            DATE(analyzed_at) AS date,
            primary_topic,
            COUNT(*) AS count
        FROM topic_analysis
        WHERE analyzed_at >= NOW() - INTERVAL '{days} days'
          AND primary_topic IS NOT NULL
        GROUP BY DATE(analyzed_at), primary_topic
        ORDER BY DATE(analyzed_at), count DESC
        """
        results = self.store.execute(query)
        logger.info(f"Topic evolution: {len(results)} rows over {days}d")
        return results

    def get_sentiment_distribution(self) -> List[Dict[str, Any]]:
        query = """
        SELECT sentiment, COUNT(*) AS count
        FROM sentiment_analysis
        GROUP BY sentiment
        ORDER BY count DESC
        """
        return self.store.execute(query)

    def get_top_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        query = f"""
        SELECT primary_topic, COUNT(*) AS count
        FROM topic_analysis
        WHERE primary_topic IS NOT NULL
        GROUP BY primary_topic
        ORDER BY count DESC
        LIMIT {limit}
        """
        return self.store.execute(query)
