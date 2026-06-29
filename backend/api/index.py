import os
from collections import Counter
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client

POSITIVE_WORDS = ['good', 'great', 'excellent', 'love', 'amazing', 'best', 'awesome', 'fantastic', 'wonderful', 'perfect']
NEGATIVE_WORDS = ['bad', 'terrible', 'hate', 'worst', 'awful', 'poor', 'disappointing', 'frustrating', 'annoying', 'broken']

TOPIC_KEYWORDS = {
    'recommendation': ['recommend', 'algorithm', 'discover', 'radio', 'playlist'],
    'ui_ux': ['interface', 'design', 'layout', 'navigation', 'button'],
    'performance': ['slow', 'crash', 'lag', 'freeze', 'loading'],
    'content': ['song', 'artist', 'album', 'music', 'audio'],
    'features': ['feature', 'function', 'option', 'setting', 'tool'],
}

TOPIC_LABELS = {
    'recommendation': 'Music Recommendations',
    'ui_ux': 'User Interface & Experience',
    'performance': 'App Performance & Stability',
    'content': 'Music Content & Catalog',
    'features': 'Features & Functionality',
    'general': 'General Feedback',
}

CATEGORY_MAP = {
    'recommendation': 'product', 'ui_ux': 'design', 'performance': 'engineering',
    'content': 'content', 'features': 'product', 'general': 'product',
}

app = FastAPI(title="Spotify Insights API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_supabase():
    url = (os.environ.get("SUPABASE_URL") or "").strip()
    key = (os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    if not url or not key:
        raise Exception("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    return create_client(url, key)


def get_supabase_admin():
    """Client with service-role key for write operations (bypasses RLS)."""
    url = (os.environ.get("SUPABASE_URL") or "").strip()
    key = (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or "").strip()
    if not url or not key:
        raise Exception("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    return create_client(url, key)


@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Spotify Review Discovery Engine",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/insights/summary")
async def get_summary():
    try:
        db = get_supabase()
        patterns = db.table("pattern_insights").select("*").execute()
        segments = db.table("user_segments").select("*").execute()
        root_causes = db.table("root_cause_analysis").select("*").execute()
        unmet_needs = db.table("unmet_needs").select("*").execute()
        reviews = db.table("raw_reviews").select("id", count="exact").limit(1).execute()
        total_reviews = reviews.count if reviews.count is not None else len(reviews.data or [])
        return {
            "success": True,
            "data": {
                "total_reviews": total_reviews,
                "pattern_count": len(patterns.data),
                "segment_count": len(segments.data),
                "root_cause_count": len(root_causes.data),
                "unmet_need_count": len(unmet_needs.data),
                "key_findings": [p["pattern_description"] for p in (patterns.data or [])[:5] if p.get("pattern_description")],
                "top_unmet_needs": [n["need_description"] for n in (unmet_needs.data or [])[:3] if n.get("need_description")],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights/patterns")
async def get_patterns():
    try:
        db = get_supabase()
        result = db.table("pattern_insights").select("*").order("discovered_at", desc=True).limit(50).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights/segments")
async def get_segments():
    try:
        db = get_supabase()
        result = db.table("user_segments").select("*").order("created_at", desc=True).limit(50).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights/root-causes")
async def get_root_causes():
    try:
        db = get_supabase()
        result = db.table("root_cause_analysis").select("*").order("analyzed_at", desc=True).limit(20).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights/unmet-needs")
async def get_unmet_needs():
    try:
        db = get_supabase()
        result = db.table("unmet_needs").select("*").order("priority_score", desc=True).limit(20).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations")
async def get_recommendations():
    try:
        db = get_supabase()
        result = db.table("recommendations").select("*").execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/roadmap")
async def get_roadmap():
    try:
        db = get_supabase()
        result = db.table("roadmap_items").select("*").execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/sentiment-distribution")
async def get_sentiment_distribution():
    try:
        db = get_supabase()
        result = db.table("sentiment_analysis").select("sentiment").execute()
        counts = {}
        for row in (result.data or []):
            label = row.get("sentiment", "unknown")
            counts[label] = counts.get(label, 0) + 1
        data = [{"sentiment": k, "count": v} for k, v in counts.items()]
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _fetch_all(db, table, columns):
    """Fetch all rows from a table with pagination (PostgREST caps at 1000/page)."""
    rows = []
    page = 0
    page_size = 1000
    while True:
        start = page * page_size
        end = start + page_size - 1
        result = db.table(table).select(columns).range(start, end).execute()
        batch = result.data or []
        rows.extend(batch)
        if len(batch) < page_size:
            break
        page += 1
    return rows


@app.get("/api/analytics/sentiment-trends")
async def get_sentiment_trends(days: int = 30):
    try:
        db = get_supabase()
        rows = _fetch_all(db, "sentiment_analysis", "sentiment,analyzed_at")
        counts = {}
        for row in rows:
            date = (row.get("analyzed_at") or "")[:10]
            sentiment = row.get("sentiment", "unknown")
            key = (date, sentiment)
            counts[key] = counts.get(key, 0) + 1
        data = [{"date": d, "sentiment": s, "count": c} for (d, s), c in counts.items()]
        data.sort(key=lambda x: x["date"])
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/topic-evolution")
async def get_topic_evolution(days: int = 30):
    try:
        db = get_supabase()
        rows = _fetch_all(db, "topic_analysis", "primary_topic,analyzed_at")
        counts = {}
        for row in rows:
            date = (row.get("analyzed_at") or "")[:10]
            topic = row.get("primary_topic", "general")
            key = (date, topic)
            counts[key] = counts.get(key, 0) + 1
        data = [{"date": d, "primary_topic": t, "count": c} for (d, t), c in counts.items()]
        data.sort(key=lambda x: x["date"])
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/top-topics")
async def get_top_topics(limit: int = 10):
    try:
        db = get_supabase()
        result = db.table("pattern_insights").select("pattern_type,frequency").order("frequency", desc=True).limit(limit).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _analyze_sentiment(text):
    t = (text or "").lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for w in NEGATIVE_WORDS if w in t)
    if pos > neg:
        return 'positive', min(0.9, 0.5 + pos * 0.1)
    if neg > pos:
        return 'negative', min(0.9, 0.5 + neg * 0.1)
    return 'neutral', 0.5


def _extract_topic(text):
    t = (text or "").lower()
    scores = {topic: sum(1 for k in kws if k in t) for topic, kws in TOPIC_KEYWORDS.items()}
    scores = {k: v for k, v in scores.items() if v > 0}
    if scores:
        primary = max(scores.items(), key=lambda x: x[1])[0]
        return primary, list(scores.keys()), scores
    return 'general', [], {}


def _clear(db, table):
    try:
        db.table(table).delete().neq('id', 0).execute()
    except Exception:
        pass


def _generate_insight_tables(db):
    """Regenerate the dedicated insight tables from analyzed data."""
    for tbl in ['roadmap_items', 'recommendations', 'unmet_needs',
                'root_cause_analysis', 'user_segments', 'pattern_insights']:
        _clear(db, tbl)

    sentiments = [r['sentiment'] for r in _fetch_all(db, 'sentiment_analysis', 'sentiment')]
    topics = [r['primary_topic'] for r in _fetch_all(db, 'topic_analysis', 'primary_topic')]
    topic_counts = Counter(topics)
    sentiment_counts = Counter(sentiments)
    total = len(sentiments) or len(topics) or 1
    negative_total = sentiment_counts.get('negative', 0)

    for topic, count in topic_counts.most_common():
        label = TOPIC_LABELS.get(topic, topic.title())
        db.table('pattern_insights').insert({
            'pattern_type': 'thematic',
            'pattern_description': f"{label} mentioned in {count} reviews ({round(count / total * 100)}% of feedback)",
            'frequency': count,
            'confidence': round(min(0.95, 0.5 + count / total), 2),
            'time_period': 'all_time',
        }).execute()

    for topic, count in topic_counts.most_common(4):
        label = TOPIC_LABELS.get(topic, topic.title())
        db.table('user_segments').insert({
            'segment_name': f"{label} Users",
            'segment_criteria': {'primary_topic': topic},
            'user_count': count,
            'primary_challenges': [label],
            'avg_sentiment': sentiment_counts.most_common(1)[0][0] if sentiment_counts else 'neutral',
        }).execute()

    for i, (topic, count) in enumerate(topic_counts.most_common(5)):
        label = TOPIC_LABELS.get(topic, topic.title())
        db.table('unmet_needs').insert({
            'need_description': f"Improve {label.lower()} based on recurring user feedback",
            'need_category': CATEGORY_MAP.get(topic, 'product'),
            'request_count': count,
            'priority_score': round(min(1.0, count / total + (0.2 if i == 0 else 0)), 2),
            'strategic_impact': 'high' if i == 0 else ('medium' if i < 3 else 'low'),
        }).execute()

    if topic_counts:
        top_topic, top_count = topic_counts.most_common(1)[0]
        label = TOPIC_LABELS.get(top_topic, top_topic.title())
        db.table('root_cause_analysis').insert({
            'issue_topic': label,
            'root_causes': {'analysis': f"{label} is the most discussed area with {top_count} mentions. "
                                        f"Negative sentiment appears in {negative_total} reviews overall."},
            'intermediate_factors': {'factors': f"Recurring mentions of {label.lower()} suggest unmet expectations."},
            'surface_symptoms': {'symptoms': f"{top_count} reviews reference {label.lower()}."},
            'confidence': 0.75,
        }).execute()

    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    for i, (topic, count) in enumerate(topic_counts.most_common(4)):
        label = TOPIC_LABELS.get(topic, topic.title())
        priority = 'high' if i == 0 else ('medium' if i < 3 else 'low')
        rec_id = None
        rec = db.table('recommendations').insert({
            'title': f"Enhance {label}",
            'description': f"Prioritize improvements to {label.lower()} — referenced in {count} reviews.",
            'category': CATEGORY_MAP.get(topic, 'product'),
            'priority': priority,
            'complexity': 'medium',
            'expected_impact': 'high' if i == 0 else 'medium',
            'success_metrics': [f"Reduction in negative {label.lower()} feedback"],
            'dependencies': [],
        }).execute()
        if rec.data:
            rec_id = rec.data[0]['id']
        db.table('roadmap_items').insert({
            'title': f"Enhance {label}",
            'description': f"Roadmap item addressing {label.lower()} feedback.",
            'priority': priority,
            'estimated_effort': 'medium',
            'quarter': quarters[i % 4],
            'success_metrics': [f"Improved {label.lower()} satisfaction"],
            'dependencies': [],
            'recommendation_id': rec_id,
        }).execute()

    return {
        'patterns': len(topic_counts),
        'segments': min(4, len(topic_counts)),
        'unmet_needs': min(5, len(topic_counts)),
        'recommendations': min(4, len(topic_counts)),
    }


@app.post("/api/insights/generate")
async def generate_insights(payload: Optional[dict] = None):
    try:
        db = get_supabase_admin()
        # Analyze any not-yet-analyzed reviews (bounded to avoid timeouts)
        analyzed_ids = {r['review_id'] for r in _fetch_all(db, 'sentiment_analysis', 'review_id')}
        reviews = _fetch_all(db, 'raw_reviews', 'id,review_text')
        pending = [r for r in reviews if r['id'] not in analyzed_ids][:800]
        analyzed_count = 0
        for review in pending:
            try:
                label, score = _analyze_sentiment(review.get('review_text'))
                db.table('sentiment_analysis').insert({
                    'review_id': review['id'],
                    'sentiment': label,
                    'confidence': score,
                    'emotion': label,
                    'intensity': 'medium' if score > 0.6 else 'low',
                }).execute()
                primary, secondary, scores = _extract_topic(review.get('review_text'))
                db.table('topic_analysis').insert({
                    'review_id': review['id'],
                    'primary_topic': primary,
                    'secondary_topics': secondary,
                    'relevance_scores': scores,
                }).execute()
                analyzed_count += 1
            except Exception as e:
                # Log but continue with other reviews
                print(f"Error analyzing review {review.get('id')}: {e}")

        summary = _generate_insight_tables(db)
        return {
            "success": True,
            "data": {
                "analyzed_reviews": analyzed_count,
                "remaining": max(0, len(reviews) - len(analyzed_ids) - analyzed_count),
                **summary,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports")
async def get_reports():
    try:
        db = get_supabase()
        result = db.table('generated_reports').select('id,created_at,report_type,template_type').order('created_at', desc=True).limit(20).execute()
        return {"success": True, "data": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/{report_id}")
async def get_report(report_id: int):
    try:
        db = get_supabase()
        result = db.table('generated_reports').select('*').eq('id', report_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Report not found")
        return {"success": True, "data": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reports/generate")
async def generate_report(payload: Optional[dict] = None):
    try:
        db = get_supabase_admin()
        patterns = _fetch_all(db, 'pattern_insights', 'pattern_description,frequency')
        segments = _fetch_all(db, 'user_segments', 'segment_name,user_count')
        unmet = _fetch_all(db, 'unmet_needs', 'need_description,priority_score')
        recs = _fetch_all(db, 'recommendations', 'title,priority')
        sentiments = Counter(r['sentiment'] for r in _fetch_all(db, 'sentiment_analysis', 'sentiment'))

        content = {
            "generated_at": datetime.now().isoformat(),
            "total_reviews": sum(sentiments.values()),
            "sentiment_breakdown": dict(sentiments),
            "pattern_count": len(patterns),
            "segment_count": len(segments),
            "top_patterns": [p.get('pattern_description') for p in patterns[:5]],
            "top_unmet_needs": [u.get('need_description') for u in
                                sorted(unmet, key=lambda x: x.get('priority_score', 0), reverse=True)[:5]],
            "recommendations": [r.get('title') for r in recs[:5]],
        }

        file_path = "report (stored in database)"
        try:
            result = db.table('generated_reports').insert({
                'report_type': 'comprehensive',
                'template_type': 'executive',
                'content': content,
            }).execute()
            if result.data:
                file_path = f"generated_reports/#{result.data[0]['id']}"
        except Exception as e:
            # Table may not exist; still return the report content
            file_path = f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        return {"success": True, "data": {"file_path": file_path, "status": "completed", "report": content}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
