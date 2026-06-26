"""
Phase 4 - Roadmap Integrator
Maps recommendations to quarterly roadmap items.
"""
from typing import Dict, List, Any

from loguru import logger

from app.database.connection import get_session
from app.database.models import RoadmapItem, Recommendation
from app.services.recommendation_engine import RecommendationEngine


class RoadmapIntegrator:
    """Convert recommendations into product roadmap items."""

    def __init__(self):
        self.recommendation_engine = RecommendationEngine()

    def generate_roadmap_items(self) -> List[Dict[str, Any]]:
        recommendations = self.recommendation_engine.get_recommendations()
        items = []
        for rec in recommendations:
            items.append({
                "title": rec["title"],
                "description": rec.get("description"),
                "priority": rec.get("priority"),
                "estimated_effort": rec.get("complexity"),
                "success_metrics": rec.get("success_metrics", []),
                "dependencies": rec.get("dependencies", []),
                "quarter": self.map_to_quarter(rec.get("priority", "low"), rec.get("complexity", "high")),
                "recommendation_id": rec.get("id"),
            })
        self._save_roadmap_items(items)
        return items

    def map_to_quarter(self, priority: str, complexity: str) -> str:
        if priority == "high" and complexity in ("low", "medium"):
            return "Q1"
        if priority == "high":
            return "Q2"
        if priority == "medium":
            return "Q3"
        return "Q4"

    def get_roadmap_items(self) -> List[Dict[str, Any]]:
        db = get_session()
        try:
            rows = db.query(RoadmapItem).order_by(RoadmapItem.quarter).all()
            if rows:
                return [self._to_dict(r) for r in rows]
        finally:
            db.close()
        return self.generate_roadmap_items()

    def _save_roadmap_items(self, items: List[Dict]) -> None:
        db = get_session()
        try:
            db.query(RoadmapItem).delete()
            for item in items:
                db.add(RoadmapItem(
                    title=item["title"],
                    description=item.get("description"),
                    priority=item.get("priority"),
                    estimated_effort=item.get("estimated_effort"),
                    quarter=item.get("quarter"),
                    success_metrics=item.get("success_metrics", []),
                    dependencies=item.get("dependencies", []),
                    recommendation_id=item.get("recommendation_id"),
                ))
            db.commit()
            logger.info(f"Saved {len(items)} roadmap items")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving roadmap: {e}")
        finally:
            db.close()

    @staticmethod
    def _to_dict(row: RoadmapItem) -> Dict:
        return {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "priority": row.priority,
            "estimated_effort": row.estimated_effort,
            "quarter": row.quarter,
            "success_metrics": row.success_metrics,
            "dependencies": row.dependencies,
            "recommendation_id": row.recommendation_id,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
