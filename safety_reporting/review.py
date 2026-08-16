"""Human review gate.

Nothing in the bundle is 'final' until a reviewer approves it. Sections whose
automated grounding checks failed start as `flagged`; everything else starts as
`pending`. The renderer prints the status of every section, so an unreviewed
report is visibly unreviewed.

    python -m safety_reporting.review --list
    python -m safety_reporting.review --approve narrative_summary
    python -m safety_reporting.review --flag trends --comment "check month labels"
    python -m safety_reporting.review --approve-all --reviewer "A. Reviewer"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import OUT, write_report

BUNDLE = OUT / "report_bundle.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=str(BUNDLE))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--approve", action="append", default=[])
    ap.add_argument("--flag", action="append", default=[])
    ap.add_argument("--approve-all", action="store_true")
    ap.add_argument("--comment", default="")
    ap.add_argument("--reviewer", default="local reviewer")
    args = ap.parse_args()

    path = Path(args.bundle)
    bundle = json.loads(path.read_text())
    sections = bundle["sections"]

    if args.list or not (args.approve or args.flag or args.approve_all):
        for sid, s in sections.items():
            errs = sum(1 for f in s["findings"] if f["level"] == "error")
            print(f"{s['review']['status']:>9}  {sid:<20} {errs} error(s)  {s['title']}")
        return

    targets = list(sections) if args.approve_all else args.approve
    for sid in targets:
        errs = [f for f in sections[sid]["findings"] if f["level"] == "error"]
        if errs and not args.approve:
            print(f"  ! {sid} has {len(errs)} grounding error(s); approve it explicitly to override")
            continue
        sections[sid]["review"] = {"status": "approved", "comment": args.comment, "reviewer": args.reviewer}
        print(f"approved {sid}")
    for sid in args.flag:
        sections[sid]["review"] = {"status": "flagged", "comment": args.comment, "reviewer": args.reviewer}
        print(f"flagged {sid}")

    path.write_text(json.dumps(bundle, indent=2, default=str))
    write_report(bundle)


if __name__ == "__main__":
    main()
