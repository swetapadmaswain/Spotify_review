"""Phase 3 insight API routes."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger

from app.services.insight_store import InsightStore
from app.services.insight_engine import InsightEngine

router = APIRouter(prefix="/api/insights", tags=["insights"])
insight_store = InsightStore()


@router.get("/summary")
async def get_insights_summary():
    """Executive summary of generated insights."""
    try:
        return {"success": True, "data": insight_store.get_summary()}
    except Exception as e:
        logger.error(f"Error fetching insight summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns")
async def get_patterns():
    """Get all detected patterns."""
    try:
        return {"success": True, "data": insight_store.get_patterns()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/segments")
async def get_segments():
    """Get user segments."""
    try:
        return {"success": True, "data": insight_store.get_segments()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/root-causes")
async def get_root_causes():
    """Get root cause analyses."""
    try:
        return {"success": True, "data": insight_store.get_root_causes()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unmet-needs")
async def get_unmet_needs():
    """Get prioritized unmet needs."""
    try:
        return {"success": True, "data": insight_store.get_unmet_needs()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_insights(background_tasks: BackgroundTasks, seed: bool = False):
    """Trigger the Phase 3 insight generation pipeline."""
    try:
        if seed:
            from scripts.seed_sample_data import seed_sample_data
            seed_sample_data()

        def _run():
            InsightEngine().run()

        background_tasks.add_task(_run)
        return {"success": True, "message": "Insight generation started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
