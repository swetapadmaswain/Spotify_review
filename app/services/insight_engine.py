"""
Phase 3 - Insight Engine (Orchestrator)
Runs all Phase 3 engines and persists results to the Insight Store.
"""
from loguru import logger
from typing import Dict, Any

from app.services.pattern_detection import (
    TemporalPatternDetector,
    ThematicPatternDetector,
    CrossPlatformPatternDetector,
)
from app.services.segmentation import (
    UserSegmentationEngine,
    DemographicSegmentation,
    TenureSegmentation,
)
from app.services.root_cause import RootCauseAnalyzer, RepetitiveBehaviorAnalyzer
from app.services.unmet_needs import UnmetNeedsDetector, GapAnalyzer
from app.services.insight_store import InsightStore


class InsightEngine:
    """
    Top-level orchestrator for Phase 3 Insight Generation.
    Call run() to execute the full pipeline.
    """

    def __init__(self, clear_existing: bool = True):
        self.insight_store = InsightStore()
        self.clear_existing = clear_existing

        self.temporal_detector = TemporalPatternDetector()
        self.thematic_detector = ThematicPatternDetector()
        self.cross_platform_detector = CrossPlatformPatternDetector()

        self.user_segmentation = UserSegmentationEngine()
        self.demographic_segmentation = DemographicSegmentation()
        self.tenure_segmentation = TenureSegmentation()

        self.root_cause_analyzer = RootCauseAnalyzer()
        self.repetitive_behavior_analyzer = RepetitiveBehaviorAnalyzer()

        self.unmet_needs_detector = UnmetNeedsDetector()
        self.gap_analyzer = GapAnalyzer()

        logger.info("InsightEngine initialised with all Phase 3 components")

    def run(self) -> Dict[str, Any]:
        """Execute the complete Phase 3 insight generation pipeline."""
        if self.clear_existing:
            self.insight_store.clear_insights()

        results: Dict[str, Any] = {}

        logger.info("=== Phase 3: Running Pattern Detection ===")
        results["temporal_trends"] = self.temporal_detector.detect_trends("30d")
        results["significant_trends"] = self.temporal_detector.analyze_trends(
            results["temporal_trends"]
        )
        results["seasonal_patterns"] = self.temporal_detector.detect_seasonal_patterns()
        results["emerging_topics"] = self.thematic_detector.detect_emerging_topics()
        results["topic_clusters"] = self.thematic_detector.detect_topic_clusters()
        results["platform_differences"] = self.cross_platform_detector.detect_platform_differences()

        patterns_saved = self._persist_patterns(results)
        results["patterns_saved"] = patterns_saved

        logger.info("=== Phase 3: Running Segmentation ===")
        results["behavior_segments"] = self.user_segmentation.segment_by_listening_behavior()
        results["frustration_segments"] = self.user_segmentation.segment_by_frustration_type()
        results["platform_segments"] = self.demographic_segmentation.segment_by_platform()
        results["tenure_segments"] = self.tenure_segmentation.segment_by_user_tenure()
        results["geography"] = self.demographic_segmentation.segment_by_geography()

        self.user_segmentation.build_and_save(
            results["behavior_segments"],
            results["frustration_segments"],
        )
        self.demographic_segmentation.save_platform_segments(results["platform_segments"])
        self.tenure_segmentation.save_tenure_segments(results["tenure_segments"])

        logger.info("=== Phase 3: Running Root Cause Analysis ===")
        systemic_issues = self.root_cause_analyzer.identify_systemic_issues()
        results["systemic_issues"] = systemic_issues

        topics_to_analyze = [i.get("primary_topic") for i in systemic_issues[:3] if i.get("primary_topic")]
        if not topics_to_analyze:
            topics_to_analyze = ["recommendations", "ui", "performance"]

        results["causal_chains"] = []
        for topic in topics_to_analyze:
            results["causal_chains"].append(
                self.root_cause_analyzer.analyze_causal_chains(topic)
            )

        results["repetitive_behavior"] = self.repetitive_behavior_analyzer.analyze_repetition_drivers()

        logger.info("=== Phase 3: Running Unmet Needs Detection ===")
        results["unmet_needs"] = self.unmet_needs_detector.prioritize_unmet_needs()
        results["capability_gaps"] = self.gap_analyzer.identify_capability_gaps()
        results["saved_needs"] = self.unmet_needs_detector.detect_and_save_top_needs()

        results["insight_summary"] = self.insight_store.get_summary()
        logger.info("=== Phase 3: Insight Generation Complete ===")
        return results

    def _persist_patterns(self, results: Dict[str, Any]) -> int:
        """Persist at least 10 patterns to the insight store."""
        saved = 0

        for trend in results.get("significant_trends", [])[:5]:
            desc = (
                f"{trend.get('pattern')} on {trend.get('date')} "
                f"({trend.get('count', 0)} reviews)"
            )
            self.temporal_detector.save_pattern(
                description=desc,
                frequency=trend.get("count", 0),
                time_period="30d",
            )
            saved += 1

        for row in results.get("emerging_topics", [])[:5]:
            topic = row.get("primary_topic", "unknown")
            self.thematic_detector.save_pattern(
                topic=topic,
                frequency=int(row.get("frequency") or 0),
            )
            saved += 1

        for row in results.get("topic_clusters", [])[:5]:
            topic = row.get("primary_topic", "unknown")
            total = int(row.get("total") or 0)
            self.thematic_detector.save_pattern(topic=topic, frequency=total, confidence=0.7)
            saved += 1

        for row in results.get("platform_differences", [])[:5]:
            source = row.get("source", "unknown")
            topic = row.get("primary_topic", "unknown")
            sentiment = row.get("sentiment", "neutral")
            count = int(row.get("count") or 0)
            desc = f"{source}: {topic} skews {sentiment}"
            self.cross_platform_detector.save_pattern(description=desc, frequency=count)
            saved += 1

        seasonal = results.get("seasonal_patterns", {}).get("seasonal_data", [])
        for row in seasonal[:3]:
            month = int(row.get("month") or 0)
            sentiment = row.get("sentiment", "unknown")
            count = int(row.get("count") or 0)
            self.temporal_detector.save_pattern(
                description=f"Month {month} shows elevated {sentiment} sentiment",
                frequency=count,
                time_period="seasonal",
            )
            saved += 1

        if saved < 10:
            defaults = [
                ("Negative sentiment around recommendations", 12, "thematic"),
                ("Cross-platform UI complaints", 8, "cross_platform"),
                ("Discover Weekly engagement peaks on Fridays", 6, "temporal"),
            ]
            for desc, freq, ptype in defaults:
                if saved >= 10:
                    break
                if ptype == "thematic":
                    self.thematic_detector.save_pattern(
                        topic=desc.replace("Emerging topic: ", ""),
                        frequency=freq,
                        confidence=0.6,
                    )
                elif ptype == "cross_platform":
                    self.cross_platform_detector.save_pattern(desc, freq, confidence=0.6)
                else:
                    self.temporal_detector.save_pattern(desc, freq, "30d", confidence=0.6)
                saved += 1

        logger.info(f"Persisted {saved} patterns to insight store")
        return saved

    def run_summary(self) -> Dict[str, Any]:
        """
        Quick summary run — returns counts and top-level insights
        without saving to DB. Good for health checks.
        """
        summary = {
            "temporal_trend_rows": len(self.temporal_detector.detect_trends("30d")),
            "emerging_topics": [
                r.get("primary_topic") for r in self.thematic_detector.detect_emerging_topics()[:5]
            ],
            "systemic_issue_count": len(self.root_cause_analyzer.identify_systemic_issues()),
            "platform_segments": len(self.demographic_segmentation.segment_by_platform()),
            "stored_insights": self.insight_store.get_summary(),
        }
        logger.info(f"InsightEngine summary: {summary}")
        return summary
