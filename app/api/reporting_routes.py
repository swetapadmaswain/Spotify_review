"""Phase 4 reporting, analytics, and recommendation API routes."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger

from app.api.auth import require_auth
from app.services.insight_store import InsightStore
from app.services.analytics_store import AnalyticsStore
from app.services.recommendation_engine import RecommendationEngine
from app.services.roadmap_integrator import RoadmapIntegrator
from app.services.report_generator import ReportGenerator

router = APIRouter(tags=["reporting"])

insight_store = InsightStore()
analytics_store = AnalyticsStore()
recommendation_engine = RecommendationEngine()
roadmap_integrator = RoadmapIntegrator()
report_generator = ReportGenerator()


class InsightRequest(BaseModel):
    insight_type: str
    filters: Optional[dict] = None


class RecommendationRequest(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = None


@router.get("/api/recommendations")
async def get_recommendations(_: bool = Depends(require_auth)):
    try:
        return {"success": True, "data": recommendation_engine.get_recommendations()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/recommendations/generate")
async def generate_recommendations(
    request: RecommendationRequest,
    _: bool = Depends(require_auth),
):
    try:
        data = recommendation_engine.generate(
            category=request.category,
            priority=request.priority,
        )
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/roadmap")
async def get_roadmap(_: bool = Depends(require_auth)):
    try:
        return {"success": True, "data": roadmap_integrator.get_roadmap_items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/sentiment-trends")
async def get_sentiment_trends(days: int = 30):
    try:
        return {"success": True, "data": analytics_store.get_sentiment_trends(days)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/topic-evolution")
async def get_topic_evolution(days: int = 30):
    try:
        return {"success": True, "data": analytics_store.get_topic_evolution(days)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/sentiment-distribution")
async def get_sentiment_distribution():
    try:
        return {"success": True, "data": analytics_store.get_sentiment_distribution()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/top-topics")
async def get_top_topics(limit: int = 10):
    try:
        return {"success": True, "data": analytics_store.get_top_topics(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/insights/query")
async def query_insights(request: InsightRequest, _: bool = Depends(require_auth)):
    try:
        data = insight_store.query(request.insight_type, request.filters)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/reports/latest")
async def get_latest_report(_: bool = Depends(require_auth)):
    try:
        report = report_generator.get_latest_report()
        if not report:
            report_content = report_generator.generate_comprehensive_report()
            return {"success": True, "data": report_content}
        return {"success": True, "data": report}
    except Exception as e:
        logger.error(f"Report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/reports/generate")
async def generate_report(template_type: str = "executive", _: bool = Depends(require_auth)):
    try:
        report = report_generator.generate_comprehensive_report()
        markdown = report_generator.render_report(template_type)
        path = report_generator.save_report_to_file(template_type)
        return {
            "success": True,
            "data": report,
            "markdown": markdown,
            "file_path": str(path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
