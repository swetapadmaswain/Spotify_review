"""
Phase 4 - Recommendation Engine
Generates strategic recommendations from insight store data.
"""
import json
from typing import Dict, List, Any, Optional

from loguru import logger

from config.settings import settings
from app.database.connection import get_session
from app.database.models import Recommendation, RoadmapItem
from app.services.insight_store import InsightStore

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def _call_llm(prompt: str) -> str:
    try:
        if settings.llm_provider == "openai" and OPENAI_AVAILABLE and settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            response = openai.ChatCompletion.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
            return response.choices[0].message.content
        if settings.llm_provider == "anthropic" and ANTHROPIC_AVAILABLE and settings.anthropic_api_key:
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model=settings.llm_model,
                max_tokens=settings.llm_max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
    except Exception as e:
        logger.warning(f"LLM recommendation call failed: {e}")
    return ""


class RecommendationEngine:
    """Generate and persist strategic recommendations from insights."""

    def __init__(self):
        self.insight_store = InsightStore()

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        insights = self.insight_store.get_all_insights()
        prompt = f"""
Based on these Spotify music discovery insights, generate 5 strategic recommendations as JSON array:
{json.dumps(insights, indent=2, default=str)[:4000]}

Each item must have: title, description, category (product|algorithm|ux|education),
priority (high|medium|low), complexity (low|medium|high), expected_impact (high|medium|low),
success_metrics (array of strings), dependencies (array of strings).

Return ONLY valid JSON array.
"""
        raw = _call_llm(prompt)
        recommendations = self._parse_recommendations(raw, insights)
        self._save_recommendations(recommendations)
        return recommendations

    def get_recommendations(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        db = get_session()
        try:
            query = db.query(Recommendation)
            if category:
                query = query.filter(Recommendation.category == category)
            if priority:
                query = query.filter(Recommendation.priority == priority)
            rows = query.order_by(Recommendation.created_at.desc()).all()
            if rows:
                return [self._to_dict(r) for r in rows]
        finally:
            db.close()
        return self.generate_recommendations()

    def generate(self, category: Optional[str] = None, priority: Optional[str] = None) -> List[Dict]:
        recs = self.generate_recommendations()
        if category:
            recs = [r for r in recs if r.get("category") == category]
        if priority:
            recs = [r for r in recs if r.get("priority") == priority]
        return recs

    def prioritize_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        impact_order = {"high": 0, "medium": 1, "low": 2}
        complexity_order = {"low": 0, "medium": 1, "high": 2}

        def sort_key(rec: Dict) -> tuple:
            return (
                priority_order.get(rec.get("priority", "low"), 2),
                impact_order.get(rec.get("expected_impact", "low"), 2),
                complexity_order.get(rec.get("complexity", "high"), 2),
            )

        return sorted(recommendations, key=sort_key)

    def _parse_recommendations(self, raw: str, insights: Dict) -> List[Dict]:
        if raw:
            try:
                start = raw.find("[")
                end = raw.rfind("]") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(raw[start:end])
                    if isinstance(parsed, list) and parsed:
                        return self.prioritize_recommendations(parsed)
            except json.JSONDecodeError:
                pass

        return self._heuristic_recommendations(insights)

    def _heuristic_recommendations(self, insights: Dict) -> List[Dict]:
        needs = insights.get("unmet_needs", [])
        patterns = insights.get("patterns", [])
        recs = [
            {
                "title": "Improve recommendation genre diversity",
                "description": "Expand Discover Weekly and Daily Mix to surface underrepresented genres.",
                "category": "algorithm",
                "priority": "high",
                "complexity": "medium",
                "expected_impact": "high",
                "success_metrics": ["repeat-listen rate", "genre diversity score"],
                "dependencies": ["listening history signals"],
            },
            {
                "title": "Reduce repetitive playlist loops",
                "description": "Add freshness controls and anti-repetition rules to radio and shuffle.",
                "category": "product",
                "priority": "high",
                "complexity": "medium",
                "expected_impact": "high",
                "success_metrics": ["skip rate", "session length"],
                "dependencies": ["recommendation engine update"],
            },
            {
                "title": "Mood-based discovery entry point",
                "description": "Launch mood/activity filters on the Discover tab.",
                "category": "ux",
                "priority": "medium",
                "complexity": "medium",
                "expected_impact": "high",
                "success_metrics": ["discover tab engagement"],
                "dependencies": ["UI redesign"],
            },
            {
                "title": "Cross-device listening sync",
                "description": "Reliable playlist and queue sync across mobile and desktop.",
                "category": "product",
                "priority": "high",
                "complexity": "high",
                "expected_impact": "medium",
                "success_metrics": ["sync error rate", "NPS"],
                "dependencies": ["backend infrastructure"],
            },
            {
                "title": "Educate users on discovery features",
                "description": "In-app tips for Release Radar, Discover Weekly, and genre browsing.",
                "category": "education",
                "priority": "low",
                "complexity": "low",
                "expected_impact": "medium",
                "success_metrics": ["feature adoption rate"],
                "dependencies": [],
            },
        ]
        if needs:
            top = needs[0].get("need_description", "")
            if top:
                recs[0]["description"] = f"Address top unmet need: {top}"
        if patterns:
            recs[1]["description"] = (
                f"Respond to detected pattern: {patterns[0].get('pattern_description', '')[:120]}"
            )
        return self.prioritize_recommendations(recs)

    def _save_recommendations(self, recommendations: List[Dict]) -> None:
        db = get_session()
        try:
            db.query(RoadmapItem).delete()
            db.query(Recommendation).delete()
            for rec in recommendations:
                db.add(Recommendation(
                    title=rec.get("title", "Untitled"),
                    description=rec.get("description"),
                    category=rec.get("category"),
                    priority=rec.get("priority"),
                    complexity=rec.get("complexity"),
                    expected_impact=rec.get("expected_impact"),
                    success_metrics=rec.get("success_metrics", []),
                    dependencies=rec.get("dependencies", []),
                ))
            db.commit()
            logger.info(f"Saved {len(recommendations)} recommendations")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving recommendations: {e}")
        finally:
            db.close()

    @staticmethod
    def _to_dict(row: Recommendation) -> Dict:
        return {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "category": row.category,
            "priority": row.priority,
            "complexity": row.complexity,
            "expected_impact": row.expected_impact,
            "success_metrics": row.success_metrics,
            "dependencies": row.dependencies,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
