"""Generate comprehensive insight report."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database.connection import init_db
from app.services.report_generator import ReportGenerator


def main():
    init_db()
    generator = ReportGenerator()
    report = generator.generate_comprehensive_report()
    path = generator.save_report_to_file("executive")

    print("Report generated successfully")
    print(f"  Patterns in report : {report['pattern_analysis']['total']}")
    print(f"  Recommendations    : {len(report['recommendations'])}")
    print(f"  Roadmap items      : {len(report['roadmap'])}")
    print(f"  Saved to           : {path}")


if __name__ == "__main__":
    main()
