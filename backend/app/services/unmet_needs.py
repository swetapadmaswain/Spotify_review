"""
Phase 3 - Unmet Needs Detector
Detects feature requests, prioritises them, and identifies capability gaps.
"""
from typing import Dict, List, Any
from loguru import logger
from sqlalchemy import text
from config.settings import settings
from app.database.connection import get_session
from app.database.models import UnmetNeed

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
        if settings.llm_provider == "openai" and OPENAI_AVAILABLE:
            openai.api_key = settings.openai_api_key
            response = openai.ChatCompletion.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
            return response.choices[0].message.content
        elif settings.llm_provider == "anthropic" and ANTHROPIC_AVAILABLE:
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model=settings.llm_model,
                max_tokens=settings.llm_max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    except Exception as e:
        logger.warning(f"LLM unavailable, using heuristic fallback: {e}")

    return (
        "Top unmet needs:\n"
        "1. Better genre diversity in recommendations (HIGH impact)\n"
        "2. Mood-based playlist generation (MEDIUM impact)\n"
        "3. Cross-platform listening history sync (HIGH impact)"
    )


class UnmetNeedsDetector:
    """Detect and prioritise unmet user needs from feedback data."""

    def __init__(self):
        pass

    def detect_feature_requests(self) -> List[Dict]:
        """Pull feature-related mentions from reviews and entity analysis."""
        db = get_session()
        try:
            # Try entity-based approach first
            result = db.execute(text("""
                SELECT
                    e.entities->>'music_features' AS feature,
                    COUNT(*) AS request_count,
                    AVG(CAST(s.confidence AS FLOAT)) AS avg_confidence,
                    t.primary_topic
                FROM entity_analysis e
                JOIN sentiment_analysis s ON e.review_id = s.review_id
                JOIN topic_analysis t ON e.review_id = t.review_id
                WHERE e.entities IS NOT NULL
                  AND e.entities->>'music_features' IS NOT NULL
                GROUP BY e.entities->>'music_features', t.primary_topic
                ORDER BY request_count DESC
                LIMIT 50
            """))
            rows = result.fetchall()
            keys = result.keys()
            requests = [dict(zip(keys, row)) for row in rows]
            
            if requests:
                logger.info(f"UnmetNeedsDetector: {len(requests)} feature request groups found from entities")
                return requests
                
            # Fallback: search review text for common feature request keywords
            result = db.execute(text("""
                SELECT
                    CASE 
                        WHEN r.review_text ILIKE '%recommend%' THEN 'Better recommendations'
                        WHEN r.review_text ILIKE '%playlist%' THEN 'Playlist features'
                        WHEN r.review_text ILIKE '%genre%' THEN 'Genre control'
                        WHEN r.review_text ILIKE '%discover%' THEN 'Discovery features'
                        WHEN r.review_text ILIKE '%mood%' THEN 'Mood-based features'
                        ELSE 'General improvements'
                    END AS feature,
                    COUNT(*) AS request_count,
                    MAX(t.primary_topic) AS primary_topic
                FROM raw_reviews r
                LEFT JOIN topic_analysis t ON r.id = t.review_id
                WHERE r.review_text IS NOT NULL
                GROUP BY feature
                ORDER BY request_count DESC
                LIMIT 20
            """))
            rows = result.fetchall()
            keys = result.keys()
            requests = [dict(zip(keys, row)) for row in rows]
            logger.info(f"UnmetNeedsDetector: {len(requests)} feature groups found from text search")
            return requests
            
        except Exception as e:
            logger.error(f"Error detecting feature requests: {e}")
            return []
        finally:
            db.close()

    def prioritize_unmet_needs(self) -> Dict[str, Any]:
        """Use LLM to prioritise detected needs by impact and frequency."""
        raw_needs = self.detect_feature_requests()
        context = str(raw_needs[:10]) if raw_needs else "No specific feature requests found in data yet."

        prompt = f"""
Prioritize these unmet user needs based on:
1. Frequency of requests
2. User sentiment (frustration level)
3. Strategic alignment with music discovery goals
4. Implementation feasibility

Unmet needs data:
{context}

Return a prioritized list with rationale for each.
"""
        prioritization = _call_llm(prompt)
        logger.info("UnmetNeedsDetector: prioritization complete")
        return {
            "raw_requests": raw_needs,
            "prioritization": prioritization
        }

    def save_unmet_need(self, description: str, category: str, request_count: int,
                        priority_score: float, strategic_impact: str) -> None:
        db = get_session()
        try:
            need = UnmetNeed(
                need_description=description,
                need_category=category,
                request_count=request_count,
                priority_score=priority_score,
                strategic_impact=strategic_impact
            )
            db.add(need)
            db.commit()
            logger.info(f"Saved unmet need: {description[:60]}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving unmet need: {e}")
        finally:
            db.close()

    def detect_and_save_top_needs(self) -> List[Dict]:
        """Detect top needs from data and persist at least 3 prioritized needs."""
        raw = self.detect_feature_requests()
        saved = []

        if raw:
            max_count = max(int(r.get("request_count") or 1) for r in raw)
            for i, row in enumerate(raw[:5]):
                feature = row.get("feature") or "unknown feature"
                count = int(row.get("request_count") or 0)
                score = round(0.5 + (count / max(max_count, 1)) * 0.5, 2)
                impact = "high" if score >= 0.8 else "medium" if score >= 0.6 else "low"
                self.save_unmet_need(
                    description=f"Users want improved {feature}",
                    category=row.get("primary_topic") or "feature",
                    request_count=count,
                    priority_score=score,
                    strategic_impact=impact,
                )
                saved.append({"feature": feature, "priority_score": score})
        else:
            defaults = [
                ("Better genre diversity in recommendations", "recommendations", 0, 0.9, "high"),
                ("Mood-based playlist generation", "feature", 0, 0.75, "medium"),
                ("Cross-platform listening history sync", "feature", 0, 0.85, "high"),
            ]
            for desc, cat, count, score, impact in defaults:
                self.save_unmet_need(desc, cat, count, score, impact)
                saved.append({"feature": desc, "priority_score": score})

        return saved


class GapAnalyzer:
    """Identify gaps between user expectations and current Spotify capabilities."""

    def identify_capability_gaps(self) -> Dict[str, Any]:
        """LLM-powered gap analysis using discovery-related feedback."""
        db = get_session()
        try:
            # Get up to 200 relevant reviews
            result = db.execute(text("""
                SELECT r.review_text AS content
                FROM raw_reviews r
                LEFT JOIN topic_analysis t ON r.id = t.review_id
                WHERE t.primary_topic IN ('recommendations', 'content', 'feature', 'discovery')
                   OR r.review_text ILIKE '%discover%'
                   OR r.review_text ILIKE '%recommend%'
                   OR r.review_text ILIKE '%feature%'
                LIMIT 200
            """))
            rows = result.fetchall()
            feedback = [row[0] for row in rows] if rows else []
        except Exception as e:
            logger.error(f"Error fetching discovery feedback: {e}")
            feedback = []
        finally:
            db.close()

        context = "\n---\n".join(feedback[:50]) if feedback else "No discovery-related feedback yet."

        prompt = f"""
Analyze user feedback to identify capability gaps in Spotify's music discovery (analyzed {len(feedback)} reviews):

Sample feedback:
{context}

Compare:
1. What users want to do (explicit requests)
2. What current features allow (implied limitations)
3. Where the gaps exist (unsolved problems)

Focus on music discovery capabilities. Be specific and cite patterns from the data.
"""
        gap_analysis = _call_llm(prompt)
        logger.info(f"GapAnalyzer: gap analysis complete using {len(feedback)} reviews")
        return {
            "feedback_count": len(feedback),
            "gap_analysis": gap_analysis
        }
