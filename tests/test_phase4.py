"""Phase 4 reporting and recommendations tests."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database.connection import init_db, get_session
from app.database.models import Recommendation, RoadmapItem, GeneratedReport
from app.services.insight_engine import InsightEngine
from app.services.report_generator import ReportGenerator, ReportTemplate
from app.services.recommendation_engine import RecommendationEngine
from app.services.roadmap_integrator import RoadmapIntegrator
from app.services.analytics_store import AnalyticsStore
from scripts.seed_sample_data import seed_sample_data


@pytest.fixture(scope="module")
def seeded_with_insights():
    init_db()
    seed_sample_data(force=True)
    InsightEngine(clear_existing=True).run()
    yield


def test_analytics_store(seeded_with_insights):
    store = AnalyticsStore()
    trends = store.get_sentiment_trends(30)
    topics = store.get_topic_evolution(30)
    assert isinstance(trends, list)
    assert isinstance(topics, list)


def test_recommendation_engine(seeded_with_insights):
    engine = RecommendationEngine()
    recs = engine.generate_recommendations()
    assert len(recs) >= 3
    assert all("title" in r and "priority" in r for r in recs)


def test_roadmap_integrator(seeded_with_insights):
    integrator = RoadmapIntegrator()
    items = integrator.generate_roadmap_items()
    assert len(items) >= 3
    assert all("quarter" in item for item in items)


def test_report_generator(seeded_with_insights):
    generator = ReportGenerator()
    report = generator.generate_comprehensive_report()
    assert "executive_summary" in report
    assert "key_findings" in report
    assert len(report["key_findings"]) >= 1
    assert len(report["recommendations"]) >= 3

    markdown = ReportTemplate("executive").render(report)
    assert "Executive" in markdown or "executive" in markdown.lower()


def test_report_persisted(seeded_with_insights):
    generator = ReportGenerator()
    generator.generate_comprehensive_report()
    latest = generator.get_latest_report()
    assert latest is not None
    assert "content" in latest

    db = get_session()
    try:
        assert db.query(Recommendation).count() >= 3
        assert db.query(RoadmapItem).count() >= 3
        assert db.query(GeneratedReport).count() >= 1
    finally:
        db.close()
