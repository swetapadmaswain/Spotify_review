from app.services.llm_pipeline import LLMProcessingPipeline
import json

pipeline = LLMProcessingPipeline()

reviews = [
    "The new Spotify update keeps crashing my phone and the UI is terrible now. I hate it.",
    "I love Discover Weekly! It always finds great new music for me.",
    "The algorithm stopped working after the latest update. My recommendations are way off now."
]

for review in reviews:
    result = pipeline.process_text(review)
    print("\n" + "="*60)
    print("REVIEW:", result["text"])
    print("-"*60)
    s = result["sentiment"]
    print(f"Sentiment   : {s['sentiment']} | Confidence: {s['confidence']} | Emotion: {s['emotion']} | Intensity: {s['intensity']}")
    t = result["topics"]
    print(f"Primary Topic   : {t['primary_topic']}")
    print(f"Secondary Topics: {t['secondary_topics']}")
    print(f"Relevance Scores: {t['topic_relevance_scores']}")
    e = result["entities"]
    print(f"Music Features  : {e.get('music_features', [])}")
    print(f"User Actions    : {e.get('user_actions', [])}")
    print(f"Emotions        : {e.get('emotions', [])}")
    print(f"Technical Terms : {e.get('technical_terms', [])}")
    print(f"Platform        : {e.get('platform_mentions', [])}")
