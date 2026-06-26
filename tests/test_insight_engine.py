"""Phase 3 insight engine tests."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database.connection import init_db, get_session
from app.database.models import (
    PatternInsight,
    UserSegment,
    RootCauseAnalysisResult,
    UnmetNeed,
)
from app.services.insight_engine import InsightEngine
from app.services.insight_store import InsightStore
from scripts.seed_sample_data import seed_sample_data


@pytest.fixture(scope="module")
def seeded_db():
    init_db()
    seed_sample_data(force=True)
    yield
    db = get_session()
    try:
        db.query(UnmetNeed).delete()
        db.query(RootCauseAnalysisResult).delete()
        db.query(UserSegment).delete()
        db.query(PatternInsight).delete()
    finally:
        db.commit()
        db.close()


def test_insight_engine_initialises():
    engine = InsightEngine(clear_existing=False)
    assert engine.temporal_detector is not None
    assert engine.unmet_needs_detector is not None


def test_run_summary_with_data(seeded_db):
    engine = InsightEngine(clear_existing=False)
    summary = engine.run_summary()
    assert summary["temporal_trend_rows"] >= 0
    assert "emerging_topics" in summary


def test_full_pipeline_meets_deliverables(seeded_db):
    engine = InsightEngine(clear_existing=True)
    results = engine.run()

    assert results["patterns_saved"] >= 10

    store = InsightStore()
    summary = store.get_summary()
    assert summary["pattern_count"] >= 10
    assert summary["segment_count"] >= 1
    assert summary["root_cause_count"] >= 1
    assert summary["unmet_need_count"] >= 3
    assert len(summary["top_unmet_needs"]) >= 3


def test_insight_store_queries(seeded_db):
    InsightEngine(clear_existing=True).run()
    store = InsightStore()

    patterns = store.get_patterns()
    segments = store.get_segments()
    root_causes = store.get_root_causes()
    unmet_needs = store.get_unmet_needs()

    assert isinstance(patterns, list)
    assert isinstance(segments, list)
    assert isinstance(root_causes, list)
    assert len(unmet_needs) >= 3
