"""
Phase 4 - Report Generator
Produces comprehensive insight reports from the insight store.
"""
import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional

from loguru import logger

from config.settings import settings
from app.database.connection import get_session
from app.database.models import GeneratedReport
from app.services.insight_store import InsightStore
from app.services.analytics_store import AnalyticsStore
from app.services.recommendation_engine import RecommendationEngine
from app.services.roadmap_integrator import RoadmapIntegrator


def _json_safe(obj: Any) -> Any:
    """Recursively convert non-JSON-serializable values."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


class ReportTemplate:
    """Render reports in executive, technical, or product formats."""

    def __init__(self, template_type: str = "executive"):
        self.template_type = template_type

    def render(self, data: Dict[str, Any]) -> str:
        if self.template_type == "executive":
            return self.render_executive(data)
        if self.template_type == "technical":
            return self.render_technical(data)
        if self.template_type == "product":
            return self.render_product(data)
        return self.render_executive(data)

    def render_executive(self, data: Dict[str, Any]) -> str:
        summary = data.get("executive_summary", {})
        findings = data.get("key_findings", [])
        recs = data.get("recommendations", [])[:3]
        lines = [
            "# Spotify Music Discovery — Executive Report",
            f"Generated: {data.get('generated_at', '')}",
            "",
            "## Executive Summary",
            summary.get("overview", ""),
            "",
            f"- Patterns detected: {summary.get('pattern_count', 0)}",
            f"- User segments: {summary.get('segment_count', 0)}",
            f"- Root causes analyzed: {summary.get('root_cause_count', 0)}",
            f"- Unmet needs: {summary.get('unmet_need_count', 0)}",
            "",
            "## Key Findings",
        ]
        for i, f in enumerate(findings[:10], 1):
            lines.append(f"{i}. {f}")
        lines.extend(["", "## Top Recommendations"])
        for rec in recs:
            lines.append(f"- **{rec.get('title')}** ({rec.get('priority')} priority)")
        return "\n".join(lines)

    def render_technical(self, data: Dict[str, Any]) -> str:
        lines = [
            "# Technical Insight Report",
            "",
            "## Pattern Analysis",
            json.dumps(data.get("pattern_analysis", {}), indent=2, default=str)[:3000],
            "",
            "## Root Causes",
            json.dumps(data.get("root_causes", []), indent=2, default=str)[:2000],
            "",
            "## Analytics",
            json.dumps(data.get("appendices", {}).get("analytics", {}), indent=2, default=str)[:2000],
        ]
        return "\n".join(lines)

    def render_product(self, data: Dict[str, Any]) -> str:
        lines = [
            "# Product Insight Report",
            "",
            "## User Segments",
        ]
        for seg in data.get("user_segments", [])[:8]:
            lines.append(f"- {seg.get('segment_name')}: {seg.get('user_count', 0)} users")
        lines.extend(["", "## Unmet Needs"])
        for need in data.get("unmet_needs", [])[:5]:
            lines.append(f"- {need.get('need_description')} (score: {need.get('priority_score')})")
        lines.extend(["", "## Roadmap"])
        for item in data.get("roadmap", [])[:5]:
            lines.append(f"- [{item.get('quarter')}] {item.get('title')}")
        return "\n".join(lines)


class ReportGenerator:
    """Generate comprehensive reports from insights and recommendations."""

    def __init__(self):
        self.insight_store = InsightStore()
        self.analytics_store = AnalyticsStore()
        self.recommendation_engine = RecommendationEngine()
        self.roadmap_integrator = RoadmapIntegrator()

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "executive_summary": self.generate_executive_summary(),
            "key_findings": self.generate_key_findings(),
            "pattern_analysis": self.generate_pattern_analysis(),
            "user_segments": self.generate_segment_analysis(),
            "root_causes": self.generate_root_cause_analysis(),
            "unmet_needs": self.generate_unmet_needs_analysis(),
            "recommendations": self.recommendation_engine.generate_recommendations(),
            "roadmap": self.roadmap_integrator.generate_roadmap_items(),
            "appendices": self.generate_appendices(),
        }
        self._persist_report(report)
        return report

    def generate_executive_summary(self) -> Dict[str, Any]:
        summary = self.insight_store.get_summary()
        sentiment = self.analytics_store.get_sentiment_distribution()
        dominant = sentiment[0]["sentiment"] if sentiment else "unknown"
        
        # Add total reviews count
        from app.database.connection import get_session
        from sqlalchemy import text
        db = get_session()
        try:
            result = db.execute(text("SELECT COUNT(*) as count FROM raw_reviews"))
            total_reviews = result.fetchone()[0] if result else 0
            summary["total_reviews"] = total_reviews
        finally:
            db.close()
        
        return {
            "overview": (
                f"Analysis of {summary.get('total_reviews', 0)} reviews revealed "
                f"{summary.get('pattern_count', 0)} patterns across "
                f"{summary.get('segment_count', 0)} user segments with "
                f"dominant {dominant} sentiment and critical discovery gaps."
            ),
            **summary,
        }

    def generate_key_findings(self) -> List[str]:
        summary = self.insight_store.get_summary()
        findings = list(summary.get("key_findings", []))
        needs = self.insight_store.get_unmet_needs(limit=3)
        for need in needs:
            findings.append(need.get("need_description", ""))
        root_causes = self.insight_store.get_root_causes(limit=2)
        for rc in root_causes:
            topic = rc.get("issue_topic", "")
            if topic:
                findings.append(f"Root cause analysis completed for: {topic}")
        return [f for f in findings if f][:10]

    def generate_pattern_analysis(self) -> Dict[str, Any]:
        patterns = self.insight_store.get_patterns()
        by_type: Dict[str, List] = {}
        for p in patterns:
            by_type.setdefault(p.get("pattern_type", "other"), []).append(p)
        return {"total": len(patterns), "by_type": by_type, "patterns": patterns[:20]}

    def generate_segment_analysis(self) -> List[Dict]:
        return self.insight_store.get_segments()

    def generate_root_cause_analysis(self) -> List[Dict]:
        return self.insight_store.get_root_causes()

    def generate_unmet_needs_analysis(self) -> List[Dict]:
        return self.insight_store.get_unmet_needs()

    def generate_appendices(self) -> Dict[str, Any]:
        return {
            "analytics": {
                "sentiment_trends": self.analytics_store.get_sentiment_trends(30),
                "topic_evolution": self.analytics_store.get_topic_evolution(30),
                "top_topics": self.analytics_store.get_top_topics(),
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

    def render_report(self, template_type: str = "executive") -> str:
        report = self.generate_comprehensive_report()
        return ReportTemplate(template_type).render(report)

    def save_report_to_file(self, template_type: str = "executive") -> Path:
        content = self.render_report(template_type)
        out_dir = Path(settings.reports_output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"report_{template_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        path = out_dir / filename
        path.write_text(content, encoding="utf-8")
        logger.info(f"Report saved to {path}")
        return path

    def _persist_report(self, report: Dict[str, Any]) -> None:
        db = get_session()
        try:
            db.add(GeneratedReport(
                report_type="comprehensive",
                template_type="comprehensive",
                content=_json_safe(report),
            ))
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error persisting report: {e}")
        finally:
            db.close()

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        db = get_session()
        try:
            row = db.query(GeneratedReport).order_by(GeneratedReport.created_at.desc()).first()
            if row:
                return {
                    "id": row.id,
                    "report_type": row.report_type,
                    "template_type": row.template_type,
                    "content": row.content,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
        finally:
            db.close()
        return None
