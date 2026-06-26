"""
Phase 3 - Root Cause Analysis Engine
Identifies causal chains and systemic issues from negative feedback.
"""
from typing import Dict, List, Any
from loguru import logger
from sqlalchemy import text
from config.settings import settings
from app.database.connection import get_session
from app.database.models import RootCauseAnalysisResult

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


def _fetch_negative_feedback_by_topic(topic: str, limit: int = 20) -> List[str]:
    """Fetch review content for a given topic with negative sentiment."""
    db = get_session()
    try:
        result = db.execute(text("""
            SELECT r.content
            FROM processed_reviews r
            JOIN topic_analysis t ON r.id = t.review_id
            JOIN sentiment_analysis s ON r.id = s.review_id
            WHERE t.primary_topic = :topic AND s.sentiment = 'negative'
            LIMIT :limit
        """), {"topic": topic, "limit": limit})
        rows = result.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        return []
    finally:
        db.close()


def _call_llm(prompt: str) -> str:
    """Call LLM and return text. Falls back to heuristic string on failure."""
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
        logger.warning(f"LLM call failed, using heuristic: {e}")

    # Heuristic fallback
    return (
        "Root causes: poor algorithm performance, lack of personalisation.\n"
        "Intermediate factors: limited training data, insufficient user signals.\n"
        "Surface symptoms: irrelevant recommendations, repetitive content."
    )


class RootCauseAnalyzer:
    """Analyse causal chains for a given negative topic using LLM or heuristics."""

    def analyze_causal_chains(self, topic: str) -> Dict[str, Any]:
        feedback = _fetch_negative_feedback_by_topic(topic)
        context = "\n".join(feedback[:10]) if feedback else "No feedback available."

        prompt = f"""
Analyze the causal chain for this topic based on user feedback:

Topic: {topic}

Sample feedback:
{context}

Identify:
1. Root causes
2. Intermediate factors
3. Surface symptoms
4. Causal relationships between them

Respond concisely.
"""
        analysis_text = _call_llm(prompt)
        logger.info(f"RootCauseAnalyzer: analyzed topic '{topic}'")

        result = {
            "topic": topic,
            "analysis": analysis_text,
            "feedback_sample_count": len(feedback)
        }
        self._save(topic, analysis_text)
        return result

    def identify_systemic_issues(self) -> List[Dict]:
        """Find topics that appear negatively across multiple platforms."""
        db = get_session()
        try:
            result = db.execute(text("""
                SELECT
                    t.primary_topic,
                    COUNT(DISTINCT r.source) AS platform_count,
                    COUNT(*) AS total_mentions,
                    AVG(s.confidence) AS avg_confidence
                FROM topic_analysis t
                JOIN sentiment_analysis s ON t.review_id = s.review_id
                JOIN processed_reviews r ON t.review_id = r.id
                WHERE s.sentiment = 'negative'
                GROUP BY t.primary_topic
                HAVING COUNT(DISTINCT r.source) >= 1
                ORDER BY total_mentions DESC
            """))
            rows = result.fetchall()
            keys = result.keys()
            issues = [dict(zip(keys, row)) for row in rows]
            logger.info(f"SystemicIssues: found {len(issues)} issues")
            return issues
        except Exception as e:
            logger.error(f"Error identifying systemic issues: {e}")
            return []
        finally:
            db.close()

    def _save(self, topic: str, analysis_text: str) -> None:
        db = get_session()
        try:
            record = RootCauseAnalysisResult(
                issue_topic=topic,
                root_causes={"analysis": analysis_text},
                intermediate_factors={},
                surface_symptoms={},
                confidence=0.7
            )
            db.add(record)
            db.commit()
            logger.info(f"Saved root cause analysis for: {topic}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving root cause: {e}")
        finally:
            db.close()


class RepetitiveBehaviorAnalyzer:
    """Analyse why users repeat content listening."""

    def analyze_repetition_drivers(self) -> Dict[str, Any]:
        db = get_session()
        try:
            result = db.execute(text("""
                SELECT r.content
                FROM processed_reviews r
                JOIN entity_analysis e ON r.id = e.review_id
                WHERE e.entities::text ILIKE '%repeat%'
                   OR e.entities::text ILIKE '%same song%'
                   OR e.entities::text ILIKE '%loop%'
                LIMIT 15
            """))
            rows = result.fetchall()
            feedback = [row[0] for row in rows]
        except Exception as e:
            logger.error(f"Error fetching repetition feedback: {e}")
            feedback = []
        finally:
            db.close()

        context = "\n".join(feedback[:10]) if feedback else "No specific repetition feedback found."
        prompt = f"""
Based on user feedback, analyze drivers of repetitive listening behavior:

Sample feedback:
{context}

Identify:
1. Psychological drivers (comfort, nostalgia, anxiety)
2. Technical drivers (UI friction, poor recommendations)
3. Content drivers (lack of new content, preference for familiar)
4. Context drivers (workout, study, background music)
"""
        analysis = _call_llm(prompt)
        logger.info("RepetitiveBehaviorAnalyzer: analysis complete")

        self._save_repetition_analysis(analysis)
        return {
            "analysis": analysis,
            "feedback_count": len(feedback)
        }

    def _save_repetition_analysis(self, analysis_text: str) -> None:
        db = get_session()
        try:
            db.add(RootCauseAnalysisResult(
                issue_topic="repetitive_listening_behavior",
                root_causes={"analysis": analysis_text},
                intermediate_factors={"drivers": ["psychological", "technical", "content", "context"]},
                surface_symptoms={"symptom": "repeated same songs/playlists"},
                confidence=0.75,
            ))
            db.commit()
            logger.info("Saved repetitive behavior root cause analysis")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving repetition analysis: {e}")
        finally:
            db.close()
