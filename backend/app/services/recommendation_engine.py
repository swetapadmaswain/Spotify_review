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
        # Increase context from 4000 to 8000 chars
        insights_json = json.dumps(insights, indent=2, default=str)
        context = insights_json[:8000]
        
        prompt = f"""
Based on these Spotify music discovery insights, generate 5-8 strategic recommendations as JSON array:

{context}

For each recommendation, provide:
- title: specific, actionable
- description: 1-2 sentences explaining the recommendation
- category: one of product|algorithm|ux|education
- priority: high|medium|low
- complexity: low|medium|high
- expected_impact: high|medium|low
- success_metrics: array of 2-3 measurable metrics
- dependencies: array of resources or teams needed

Return ONLY valid JSON array. Ensure diversity across categories and unique titles.
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
        segments = insights.get("segments", [])
        
        # Generate diverse recommendations based on actual insights
        recs = []
        
        # Algorithm recommendations based on patterns
        if patterns:
            for p in patterns[:3]:
                recs.append({
                    "title": f"Optimize {p.get('pattern_type', 'discovery')} patterns",
                    "description": p.get('pattern_description', 'Address detected usage pattern'),
                    "category": "algorithm",
                    "priority": "high" if p.get('frequency', 0) > 10 else "medium",
                    "complexity": "medium",
                    "expected_impact": "high",
                    "success_metrics": ["engagement rate", "user satisfaction"],
                    "dependencies": ["pattern detection system"],
                })
        
        # Product recommendations based on unmet needs
        if needs:
            for n in needs[:3]:
                recs.append({
                    "title": f"Address: {n.get('need_description', 'User need')[:50]}",
                    "description": n.get('need_description', 'Improve user experience'),
                    "category": "product",
                    "priority": "high" if n.get('priority_score', 0) > 0.7 else "medium",
                    "complexity": "medium",
                    "expected_impact": "high" if n.get('strategic_impact') == 'high' else "medium",
                    "success_metrics": ["feature adoption", "NPS"],
                    "dependencies": ["product development"],
                })
        
        # UX recommendations based on segments
        if segments:
            for s in segments[:2]:
                challenges = s.get('primary_challenges', [])
                if challenges:
                    recs.append({
                        "title": f"Improve UX for {s.get('segment_name', 'user segment')}",
                        "description": f"Address challenges: {', '.join(challenges[:2])}",
                        "category": "ux",
                        "priority": "medium",
                        "complexity": "low",
                        "expected_impact": "medium",
                        "success_metrics": ["task completion rate", "user satisfaction"],
                        "dependencies": ["UI/UX team"],
                    })
        
        # Add diverse fallback recommendations if insufficient data
        if len(recs) < 5:
            fallback_recs = [
                {
                    "title": "Enhance genre diversity in recommendations",
                    "description": "Expand Discover Weekly to surface underrepresented genres based on listening patterns.",
                    "category": "algorithm",
                    "priority": "high",
                    "complexity": "medium",
                    "expected_impact": "high",
                    "success_metrics": ["genre diversity score", "discovery rate"],
                    "dependencies": ["recommendation engine update"],
                },
                {
                    "title": "Implement smart playlist freshness controls",
                    "description": "Add user-configurable anti-repetition rules and freshness sliders to radio and shuffle modes.",
                    "category": "product",
                    "priority": "high",
                    "complexity": "medium",
                    "expected_impact": "high",
                    "success_metrics": ["skip rate reduction", "session length increase"],
                    "dependencies": ["playlist algorithm update"],
                },
                {
                    "title": "Launch mood-based discovery filters",
                    "description": "Add mood and activity-based entry points on the Discover tab for contextual music discovery.",
                    "category": "ux",
                    "priority": "medium",
                    "complexity": "medium",
                    "expected_impact": "high",
                    "success_metrics": ["discover tab engagement", "feature adoption"],
                    "dependencies": ["UI redesign", "mood classification model"],
                },
                {
                    "title": "Improve cross-device listening sync reliability",
                    "description": "Enhance real-time playlist and queue synchronization across mobile, desktop, and web platforms.",
                    "category": "product",
                    "priority": "high",
                    "complexity": "high",
                    "expected_impact": "medium",
                    "success_metrics": ["sync error rate", "cross-platform retention"],
                    "dependencies": ["backend infrastructure", "sync service"],
                },
                {
                    "title": "Add contextual onboarding for discovery features",
                    "description": "Implement smart in-app tips and tutorials for Release Radar, Discover Weekly, and genre browsing.",
                    "category": "education",
                    "priority": "low",
                    "complexity": "low",
                    "expected_impact": "medium",
                    "success_metrics": ["feature adoption rate", "user engagement"],
                    "dependencies": ["onboarding system"],
                },
            ]
            # Add only unique fallback recommendations
            existing_titles = {r.get('title') for r in recs}
            for fr in fallback_recs:
                if fr['title'] not in existing_titles and len(recs) < 8:
                    recs.append(fr)
        
        return self.prioritize_recommendations(recs[:8])

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
