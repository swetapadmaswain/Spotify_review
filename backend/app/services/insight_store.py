"""
Phase 3 - Insight Store
Read and write persisted insight artifacts (patterns, segments, root causes, unmet needs).
"""
from typing import Dict, List, Any, Optional

from loguru import logger

from app.database.connection import get_session
from app.database.models import (
    PatternInsight,
    UserSegment,
    RootCauseAnalysisResult,
    UnmetNeed,
)


class InsightStore:
    """Query and summarise Phase 3 insight tables."""

    def get_patterns(self, pattern_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        db = get_session()
        try:
            query = db.query(PatternInsight)
            if pattern_type:
                query = query.filter(PatternInsight.pattern_type == pattern_type)
            rows = query.order_by(PatternInsight.discovered_at.desc()).limit(limit).all()
            return [self._pattern_to_dict(r) for r in rows]
        finally:
            db.close()

    def get_segments(self, limit: int = 50) -> List[Dict]:
        db = get_session()
        try:
            rows = db.query(UserSegment).order_by(UserSegment.created_at.desc()).limit(limit).all()
            return [self._segment_to_dict(r) for r in rows]
        finally:
            db.close()

    def get_root_causes(self, limit: int = 20) -> List[Dict]:
        db = get_session()
        try:
            rows = (
                db.query(RootCauseAnalysisResult)
                .order_by(RootCauseAnalysisResult.analyzed_at.desc())
                .limit(limit)
                .all()
            )
            return [self._root_cause_to_dict(r) for r in rows]
        finally:
            db.close()

    def get_unmet_needs(self, limit: int = 20) -> List[Dict]:
        db = get_session()
        try:
            rows = (
                db.query(UnmetNeed)
                .order_by(UnmetNeed.priority_score.desc())
                .limit(limit)
                .all()
            )
            return [self._unmet_need_to_dict(r) for r in rows]
        finally:
            db.close()

    def get_summary(self) -> Dict[str, Any]:
        db = get_session()
        try:
            pattern_count = db.query(PatternInsight).count()
            segment_count = db.query(UserSegment).count()
            root_cause_count = db.query(RootCauseAnalysisResult).count()
            unmet_need_count = db.query(UnmetNeed).count()

            top_patterns = (
                db.query(PatternInsight)
                .order_by(PatternInsight.frequency.desc())
                .limit(5)
                .all()
            )
            top_needs = (
                db.query(UnmetNeed)
                .order_by(UnmetNeed.priority_score.desc())
                .limit(3)
                .all()
            )

            # Remove duplicates while preserving order
            key_findings = list(dict.fromkeys(
                p.pattern_description for p in top_patterns if p.pattern_description
            ))
            top_unmet_needs = list(dict.fromkeys(
                n.need_description for n in top_needs if n.need_description
            ))

            return {
                "pattern_count": pattern_count,
                "segment_count": segment_count,
                "root_cause_count": root_cause_count,
                "unmet_need_count": unmet_need_count,
                "key_findings": key_findings,
                "top_unmet_needs": top_unmet_needs,
            }
        finally:
            db.close()

    def get_all_insights(self) -> Dict[str, Any]:
        return {
            "patterns": self.get_patterns(),
            "segments": self.get_segments(),
            "root_causes": self.get_root_causes(),
            "unmet_needs": self.get_unmet_needs(),
            "summary": self.get_summary(),
        }

    def query(self, insight_type: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Query insights by type with optional filters."""
        filters = filters or {}
        getters = {
            "patterns": self.get_patterns,
            "segments": self.get_segments,
            "root_causes": self.get_root_causes,
            "unmet_needs": self.get_unmet_needs,
        }
        if insight_type == "summary":
            return [self.get_summary()]
        if insight_type not in getters:
            return []

        data = getters[insight_type]()
        for key, value in filters.items():
            data = [row for row in data if str(row.get(key, "")).lower() == str(value).lower()]
        return data

    def clear_insights(self) -> None:
        """Remove existing insight rows before a fresh pipeline run."""
        db = get_session()
        try:
            db.query(PatternInsight).delete()
            db.query(UserSegment).delete()
            db.query(RootCauseAnalysisResult).delete()
            db.query(UnmetNeed).delete()
            db.commit()
            logger.info("Cleared existing insight store records")
        except Exception as e:
            db.rollback()
            logger.error(f"Error clearing insights: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def _pattern_to_dict(row: PatternInsight) -> Dict:
        return {
            "id": row.id,
            "pattern_type": row.pattern_type,
            "pattern_description": row.pattern_description,
            "frequency": row.frequency,
            "confidence": row.confidence,
            "time_period": row.time_period,
            "discovered_at": row.discovered_at.isoformat() if row.discovered_at else None,
        }

    @staticmethod
    def _segment_to_dict(row: UserSegment) -> Dict:
        return {
            "id": row.id,
            "segment_name": row.segment_name,
            "segment_criteria": row.segment_criteria,
            "user_count": row.user_count,
            "primary_challenges": row.primary_challenges,
            "avg_sentiment": row.avg_sentiment,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }

    @staticmethod
    def _root_cause_to_dict(row: RootCauseAnalysisResult) -> Dict:
        return {
            "id": row.id,
            "issue_topic": row.issue_topic,
            "root_causes": row.root_causes,
            "intermediate_factors": row.intermediate_factors,
            "surface_symptoms": row.surface_symptoms,
            "confidence": row.confidence,
            "analyzed_at": row.analyzed_at.isoformat() if row.analyzed_at else None,
        }

    @staticmethod
    def _unmet_need_to_dict(row: UnmetNeed) -> Dict:
        return {
            "id": row.id,
            "need_description": row.need_description,
            "need_category": row.need_category,
            "request_count": row.request_count,
            "priority_score": row.priority_score,
            "strategic_impact": row.strategic_impact,
            "identified_at": row.identified_at.isoformat() if row.identified_at else None,
        }
