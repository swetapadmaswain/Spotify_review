"""
Run the Phase 3 Insight Generation pipeline.

Usage:
    python scripts/run_insights.py
    python scripts/run_insights.py --seed
    python scripts/run_insights.py --summary-only
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loguru import logger

from app.database.connection import init_db
from app.services.insight_engine import InsightEngine
from scripts.seed_sample_data import seed_sample_data


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 3 insight generation")
    parser.add_argument("--seed", action="store_true", help="Seed sample data before running")
    parser.add_argument("--force-seed", action="store_true", help="Replace existing data with seed")
    parser.add_argument("--summary-only", action="store_true", help="Health check without persisting")
    parser.add_argument("--no-clear", action="store_true", help="Do not clear existing insights")
    args = parser.parse_args()

    init_db()

    if args.seed or args.force_seed:
        seeded = seed_sample_data(force=args.force_seed)
        if seeded:
            logger.info(f"Seeded {seeded} sample reviews")

    engine = InsightEngine(clear_existing=not args.no_clear)

    if args.summary_only:
        summary = engine.run_summary()
        print(json.dumps(summary, indent=2, default=str))
        return 0

    results = engine.run()
    summary = results.get("insight_summary", {})

    print("\n" + "=" * 60)
    print("PHASE 3 - INSIGHT GENERATION COMPLETE")
    print("=" * 60)
    print(f"Patterns saved      : {results.get('patterns_saved', 0)}")
    print(f"User segments       : {summary.get('segment_count', 0)}")
    print(f"Root cause analyses : {summary.get('root_cause_count', 0)}")
    print(f"Unmet needs         : {summary.get('unmet_need_count', 0)}")
    print(f"\nKey findings:")
    for finding in summary.get("key_findings", [])[:5]:
        print(f"  - {finding}")
    print(f"\nTop unmet needs:")
    for need in summary.get("top_unmet_needs", []):
        print(f"  - {need}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
