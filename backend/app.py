"""
Vercel Entry Point - Self-Contained FastAPI App
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Spotify Review Discovery Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class InsightSummary(BaseModel):
    total_reviews: int
    pattern_count: int
    segment_count: int
    root_cause_count: int
    unmet_need_count: int
    key_findings: List[str]
    top_unmet_needs: List[str]

class Pattern(BaseModel):
    id: int
    pattern_type: str
    pattern_description: str
    frequency: int
    confidence: float

class Segment(BaseModel):
    id: int
    segment_name: str
    user_count: int
    avg_sentiment: str
    primary_challenges: List[str]

class RoadmapItem(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    quarter: str

class UnmetNeed(BaseModel):
    id: int
    need_description: str
    need_category: str
    request_count: int
    priority_score: float

class RootCause(BaseModel):
    id: int
    issue_topic: str
    root_causes: dict
    confidence: float

# Sample data for demo
sample_patterns = [
    Pattern(id=1, pattern_type="temporal", pattern_description="Increase in negative reviews after feature update", frequency=150, confidence=0.85),
    Pattern(id=2, pattern_type="thematic", pattern_description="Users want better search functionality", frequency=200, confidence=0.92),
]

sample_segments = [
    Segment(id=1, segment_name="Premium Users", user_count=1500, avg_sentiment="positive", primary_challenges=["Better offline mode"]),
    Segment(id=2, segment_name="Free Users", user_count=3500, avg_sentiment="mixed", primary_challenges=["Ads interruption", "Limited features"]),
]

sample_roadmap = [
    RoadmapItem(id=1, title="Offline Mode Enhancement", description="Improve offline playback quality", priority="high", quarter="Q3 2024"),
    RoadmapItem(id=2, title="Search Improvement", description="Add voice search and better filtering", priority="medium", quarter="Q4 2024"),
]

@app.get("/")
async def root():
    return {"status": "ok", "service": "Spotify Backend", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/insights/summary")
async def get_summary():
    return InsightSummary(
        total_reviews=10247,
        pattern_count=12,
        segment_count=7,
        root_cause_count=3,
        unmet_need_count=5,
        key_findings=["Users love the music library", "Pricing is competitive", "Recommendations need improvement"],
        top_unmet_needs=["Better offline mode", "Improved recommendations", "Fewer ads for free users"]
    )

@app.get("/api/insights/patterns")
async def get_patterns():
    return sample_patterns

@app.get("/api/insights/segments")
async def get_segments():
    return sample_segments

@app.get("/api/insights/root-causes")
async def get_root_causes():
    return [
        RootCause(id=1, issue_topic="Playback issues", root_causes={"network": 45, "device": 30, "server": 25}, confidence=0.88)
    ]

@app.get("/api/insights/unmet-needs")
async def get_unmet_needs():
    return [
        UnmetNeed(id=1, need_description="Better offline mode", need_category="feature", request_count=500, priority_score=0.95)
    ]

@app.get("/api/recommendations")
async def get_recommendations():
    return [
        {"id": 1, "title": "Improve Offline Mode", "description": "Enhance offline playback quality and reliability", "category": "feature", "priority": "high", "complexity": "medium", "expected_impact": "high"},
    ]

@app.get("/api/roadmap")
async def get_roadmap():
    return sample_roadmap

@app.get("/api/analytics/sentiment-trends")
async def get_sentiment_trends(days: int = 30):
    return [
        {"date": "2024-01-01", "sentiment": "positive", "count": 100},
        {"date": "2024-01-02", "sentiment": "negative", "count": 50},
    ]

@app.get("/api/analytics/topic-evolution")
async def get_topic_evolution(days: int = 30):
    return [
        {"date": "2024-01-01", "primary_topic": "Playback", "count": 100},
    ]

@app.get("/api/analytics/sentiment-distribution")
async def get_sentiment_distribution():
    return [
        {"sentiment": "positive", "count": 5000},
        {"sentiment": "negative", "count": 2000},
        {"sentiment": "neutral", "count": 3247},
    ]

@app.get("/api/analytics/top-topics")
async def get_top_topics(limit: int = 8):
    return [{"topic": "Playback", "count": 1000}, {"topic": "Search", "count": 800}]

@app.post("/api/insights/generate")
async def generate_insights(seed: bool = False):
    return {"status": "generated", "message": "Insights generated successfully"}

@app.post("/api/reports/generate")
async def generate_report():
    return {"file_path": "reports/spotify_review_analysis.pdf", "status": "success"}

handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
