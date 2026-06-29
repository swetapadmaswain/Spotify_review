import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client

app = FastAPI(title="Spotify Insights API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise Exception("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
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
        root_causes = db.table("root_cause_analysis_results").select("*").execute()
        unmet_needs = db.table("unmet_needs").select("*").execute()
        return {
            "success": True,
            "data": {
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
        result = db.table("root_cause_analysis_results").select("*").order("analyzed_at", desc=True).limit(20).execute()
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
        result = db.table("sentiment_analysis").select("sentiment_label").execute()
        counts = {}
        for row in (result.data or []):
            label = row.get("sentiment_label", "unknown")
            counts[label] = counts.get(label, 0) + 1
        return {"success": True, "data": counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/sentiment-trends")
async def get_sentiment_trends(days: int = 30):
    try:
        db = get_supabase()
        result = db.table("sentiment_analysis").select("*").limit(100).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
