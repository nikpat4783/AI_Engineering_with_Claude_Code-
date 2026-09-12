import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from .reviewers import load_reviewers
from .audit import append_audit_event
from .config import RESULTS_DIR


def review_result(result_id: str, reviewer_id: str, decision: str, notes: str) -> int:
    reviewers = load_reviewers()
    is_valid, reviewer_name = reviewers.is_valid_reviewer(reviewer_id)

    if not is_valid:
        print(f"Error: Unknown reviewer '{reviewer_id}'", file=sys.stderr)
        return 1

    result_path = RESULTS_DIR / f"{result_id}.json"
    review_path = RESULTS_DIR / f"{result_id}.review.json"

    if not result_path.exists():
        print(f"Error: Result {result_id} not found", file=sys.stderr)
        return 1

    if review_path.exists():
        print(f"Error: Result {result_id} already reviewed. Use --amend to override.", file=sys.stderr)
        return 1

    review = {
        "reviewer_id": reviewer_id,
        "reviewer_name": reviewer_name,
        "decision": decision,
        "notes": notes,
        "reviewed_at": datetime.utcnow().isoformat()
    }

    with open(review_path, "w") as f:
        json.dump(review, f, indent=2)

    append_audit_event("review_decision", {
        "result_id": result_id,
        "reviewer_id": reviewer_id,
        "decision": decision
    })

    print(f"Result {result_id} reviewed by {reviewer_name}: {decision}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Triage CLI")
    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser("review", help="Review a triage result")
    review_parser.add_argument("result_id", help="Result ID")
    review_parser.add_argument("--reviewer", required=True, help="Reviewer ID")
    review_parser.add_argument("--decision", required=True, choices=["approve", "reject"], help="Decision")
    review_parser.add_argument("--notes", default="", help="Review notes")
    review_parser.add_argument("--amend", action="store_true", help="Override existing review")

    args = parser.parse_args()

    if args.command == "review":
        return review_result(args.result_id, args.reviewer, args.decision, args.notes)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
