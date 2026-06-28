"""
Shared helper for running SQL queries against the Analysis Store (Phase 2 tables).
"""
from typing import Dict, List, Optional

from loguru import logger
from sqlalchemy import text

from app.database.connection import get_session


class AnalysisStore:
    """Execute read queries against sentiment, topic, entity, and review tables."""

    def execute(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        db = get_session()
        try:
            result = db.execute(text(query), params or {})
            rows = result.fetchall()
            keys = result.keys()
            data = [dict(zip(keys, row)) for row in rows]
            logger.debug(f"AnalysisStore query returned {len(data)} rows")
            return data
        except Exception as e:
            logger.error(f"AnalysisStore query error: {e}\nQuery: {query[:200]}")
            return []
        finally:
            db.close()
