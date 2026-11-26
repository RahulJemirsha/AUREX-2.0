import argparse, json
from .core import create_report, save_report

def main():
    parser = argparse.ArgumentParser(description="AUREX 2.0 repository research prototype")
    parser.add_argument("repository", help="Path to a local Git repository")
    parser.add_argument("--output", default="aurex-report.json")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    if args.limit < 1 or args.limit > 100:
        parser.error("--limit must be between 1 and 100")
    report = create_report(args.repository, args.limit)
    path = save_report(report, args.output)
    print(json.dumps(report["summary"], indent=2))
    print(f"Report written to: {path.resolve()}")

if __name__ == "__main__":
    main()
