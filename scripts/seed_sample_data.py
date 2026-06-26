"""
Seed sample analyzed reviews for Phase 3 insight generation.
Run when no Phase 1/2 data exists yet.
"""
from datetime import datetime, timedelta
import random

from loguru import logger

from app.database.connection import init_db, get_session
from app.database.models import (
    ProcessedReview,
    SentimentAnalysis,
    TopicAnalysis,
    EntityAnalysis,
)


SAMPLE_REVIEWS = [
    ("appstore", "Discover Weekly is amazing!", "positive", "recommendations", "playlist"),
    ("appstore", "App keeps crashing after update", "negative", "performance", "bug"),
    ("playstore", "Same songs repeat every day", "negative", "recommendations", "repeat"),
    ("playstore", "Love the new UI redesign", "positive", "ui", "interface"),
    ("reddit", "Algorithm feels stale, need more genre diversity", "negative", "recommendations", "algorithm"),
    ("reddit", "Daily Mix is perfect for workouts", "positive", "recommendations", "playlist"),
    ("forum", "Cannot sync playlists across devices", "negative", "feature", "sync"),
    ("forum", "Radio mode plays the same artists", "negative", "recommendations", "radio"),
    ("social", "Spotify needs mood-based playlists", "neutral", "feature", "playlist"),
    ("social", "Discover Weekly found my new favorite band", "positive", "recommendations", "discovery"),
    ("appstore", "Recommendations are way off lately", "negative", "recommendations", "algorithm"),
    ("playstore", "Too many ads on free tier", "negative", "pricing", "ads"),
    ("reddit", "Release Radar never misses", "positive", "recommendations", "playlist"),
    ("forum", "Search is broken for obscure artists", "negative", "search", "bug"),
    ("social", "Wish I could filter by mood and energy", "neutral", "feature", "filter"),
    ("appstore", "Shuffle keeps repeating songs", "negative", "recommendations", "repeat"),
    ("playstore", "Offline mode works great", "positive", "feature", "offline"),
    ("reddit", "Made For You feels generic", "negative", "recommendations", "personalization"),
    ("forum", "Podcast recommendations are irrelevant", "negative", "recommendations", "podcast"),
    ("social", "Cross-platform sync is unreliable", "negative", "feature", "sync"),
    ("appstore", "Great sound quality on iOS", "positive", "audio", "quality"),
    ("playstore", "Battery drain is terrible", "negative", "performance", "battery"),
    ("reddit", "Need better indie artist discovery", "neutral", "recommendations", "discovery"),
    ("forum", "UI is cluttered after redesign", "negative", "ui", "interface"),
    ("social", "Spotify Wrapped was fun this year", "positive", "feature", "wrapped"),
    ("appstore", "Login issues on iPad", "negative", "performance", "bug"),
    ("playstore", "Family plan is worth it", "positive", "pricing", "subscription"),
    ("reddit", "Algorithm loops same 20 songs", "negative", "recommendations", "repeat"),
    ("forum", "Want collaborative playlist improvements", "neutral", "feature", "playlist"),
    ("social", "Discover tab needs better curation", "negative", "recommendations", "discovery"),
]


def seed_sample_data(force: bool = False) -> int:
    """Insert sample reviews with analysis if the database is empty."""
    init_db()
    db = get_session()
    try:
        existing = db.query(ProcessedReview).count()
        if existing > 0 and not force:
            logger.info(f"Database already has {existing} reviews; skipping seed")
            return 0

        if force:
            db.query(EntityAnalysis).delete()
            db.query(TopicAnalysis).delete()
            db.query(SentimentAnalysis).delete()
            db.query(ProcessedReview).delete()
            db.commit()

        base_date = datetime.utcnow() - timedelta(days=25)
        created = 0

        for i, (source, content, sentiment, topic, feature) in enumerate(SAMPLE_REVIEWS):
            review = ProcessedReview(
                source_id=f"seed-{i}",
                source=source,
                content=content,
                author=f"user_{i}",
                rating=random.choice([1, 2, 3, 4, 5]),
                version="8.9.0" if i % 2 == 0 else None,
                created_at=base_date + timedelta(days=i % 20),
            )
            db.add(review)
            db.flush()

            analyzed_at = base_date + timedelta(days=i % 20, hours=1)
            db.add(SentimentAnalysis(
                review_id=review.id,
                sentiment=sentiment,
                confidence=round(random.uniform(0.7, 0.95), 2),
                emotion="frustration" if sentiment == "negative" else "joy",
                intensity="high" if sentiment == "negative" else "medium",
                analyzed_at=analyzed_at,
            ))
            db.add(TopicAnalysis(
                review_id=review.id,
                primary_topic=topic,
                secondary_topics=["discovery", "user_experience"],
                relevance_scores={"primary": round(random.uniform(0.6, 0.95), 2)},
                analyzed_at=analyzed_at,
            ))
            db.add(EntityAnalysis(
                review_id=review.id,
                entities={
                    "music_features": feature,
                    "technical_terms": "bug" if sentiment == "negative" and topic == "performance" else None,
                    "user_actions": "skip" if "repeat" in content.lower() else "listen",
                },
                entity_types={"music_features": "feature"},
                analyzed_at=analyzed_at,
            ))
            created += 1

        db.commit()
        logger.info(f"Seeded {created} sample reviews with analysis data")
        return created
    except Exception as e:
        db.rollback()
        logger.error(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    count = seed_sample_data()
    print(f"Seeded {count} reviews")
