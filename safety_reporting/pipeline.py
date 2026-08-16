"""PADER prototype pipeline.

    load+validate -> deterministic analyses -> (human gate) -> per-section packet
    -> LLM draft -> automated grounding checks -> (human gate) -> render

Run:
    python -m safety_reporting.pipeline --data <csv> --spec <json> [--offline]
    python -m safety_reporting.review out/report_bundle.json --approve-all
    python -m safety_reporting.pipeline --render-only
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .core import analyses, dataset, packet as packet_mod, render, verify
from .core.llm import LLMError, generate

ROOT = Path(__file__).parent
OUT = ROOT / "out"
PIPELINE_VERSION = "0.1.0"


def collect_evidence(ds: dataset.Dataset, spec: dict) -> dict[str, analyses.AnalysisResult]:
    needed: list[str] = []
    for section in spec["sections"]:
        for a in section["requires"]:
            if a not in needed:
                needed.append(a)
    for ids in spec.get("tables", {}).values():
        for a in ids:
            if a not in needed:
                needed.append(a)
    return {a: analyses.run(ds, a, spec.get("params", {})) for a in needed}


def offline_draft(pkt: packet_mod.Packet) -> str:
    """Deterministic fallback so the pipeline runs without model access."""
    return (
        f"[Offline draft - model not called] Section '{pkt.section_id}' is grounded in "
        f"the following evidence: "
        + ", ".join(f"[E:{e}]" for e in pkt.evidence_ids)
        + ". Figures are available in the tables and evidence register below."
    )


def run(data_path: Path, spec_path: Path, offline: bool = False) -> dict:
    spec = json.loads(spec_path.read_text())
    spec_sha = hashlib.sha256(spec_path.read_bytes()).hexdigest()

    ds = dataset.load(data_path)
    print(f"loaded {ds.row_count} rows / {ds.case_count} cases from {data_path.name}")
    for issue in ds.validation:
        if issue["level"] != "ok":
            print(f"  validation {issue['level']}: {issue['check']} = {issue.get('count')}")

    evidence = collect_evidence(ds, spec)
    print(f"computed {len(evidence)} deterministic analyses")

    sections: dict[str, dict] = {}
    for section in spec["sections"]:
        pkt = packet_mod.build(spec, section, evidence)
        if offline:
            text, model_used, run_id = offline_draft(pkt), "offline", None
        else:
            try:
                res = generate(pkt.system_prompt, pkt.user_prompt, spec["model"])
                text, model_used, run_id = res["text"], res["model"], res["run_id"]
            except LLMError as exc:
                print(f"  ! {section['id']}: {exc} - falling back to offline draft")
                text, model_used, run_id = offline_draft(pkt), "offline", None
        findings = verify.check(text, pkt)
        errors = [f for f in findings if f["level"] == "error"]
        print(f"  section {section['id']}: {len(text.split())} words, {len(errors)} grounding error(s)")
        sections[section["id"]] = {
            "title": section["title"],
            "text": text,
            "packet": {"system": pkt.system_prompt, "user": pkt.user_prompt},
            "evidence_ids": pkt.evidence_ids,
            "findings": findings,
            "model": model_used,
            "run_id": run_id,
            # human gate: nothing is final until a reviewer acts on it
            "review": {"status": "flagged" if errors else "pending", "comment": "", "reviewer": None},
        }

    bundle = {
        "spec": spec,
        "provenance": {
            "dataset": ds.provenance,
            "spec_sha256": spec_sha,
            "model": spec["model"] if not offline else "offline",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pipeline_version": PIPELINE_VERSION,
        },
        "evidence": [e.to_dict() for e in evidence.values()],
        "sections": sections,
    }

    OUT.mkdir(exist_ok=True)
    (OUT / "report_bundle.json").write_text(json.dumps(bundle, indent=2, default=str))
    analyses.cases(ds).to_csv(OUT / "case_index_full.csv", index=False)
    write_report(bundle)
    return bundle


def write_report(bundle: dict) -> Path:
    path = OUT / "PADER_report.md"
    path.write_text(render.render_markdown(bundle))
    print(f"wrote {path}")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "Bisoprolol_icsr_sample_1068rows.csv"))
    ap.add_argument("--spec", default=str(ROOT / "config" / "reports" / "pader.json"))
    ap.add_argument("--offline", action="store_true", help="skip model calls")
    ap.add_argument("--render-only", action="store_true", help="re-render from the existing bundle")
    args = ap.parse_args()

    if args.render_only:
        write_report(json.loads((OUT / "report_bundle.json").read_text()))
        return
    run(Path(args.data), Path(args.spec), offline=args.offline)


if __name__ == "__main__":
    main()
