"""Context assembly: what the model actually sees for one section.

A packet is deliberately small: the section's own instruction, the evidence
items that section declared (and nothing else), each with an id the model must
cite. The raw CSV is never sent. Case IDs (the trace) are never sent either -
they are only used by the renderer/UI for evidence drill-down.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .analyses import AnalysisResult


@dataclass
class Packet:
    section_id: str
    system_prompt: str
    user_prompt: str
    evidence_ids: list[str]
    allowed_numbers: set[str]


def _fmt(a: AnalysisResult) -> str:
    head = f"[E:{a.id}] {a.title}\n  method: {a.method}"
    if a.kind == "table":
        rows = "\n".join("  - " + json.dumps(r, default=str) for r in a.value)  # type: ignore[union-attr]
        body = rows or "  (no rows)"
    else:
        body = "  value: " + json.dumps(a.value, default=str)
    notes = "".join(f"\n  note: {n}" for n in a.notes)
    return f"{head}\n{body}{notes}"


def _numbers(a: AnalysisResult) -> set[str]:
    out: set[str] = set()

    def walk(v):
        if isinstance(v, bool):
            return
        if isinstance(v, (int, float)):
            out.add(f"{v:g}")
        elif isinstance(v, str):
            # numbers embedded in labels ("45-64", "2025-03", "75+") are grounded too
            for tok in re.findall(r"\d+(?:\.\d+)?", v):
                out.add(f"{float(tok):g}")
        elif isinstance(v, dict):
            [walk(x) for x in v.values()]
        elif isinstance(v, list):
            [walk(x) for x in v]

    walk(a.value)
    walk(a.title)
    for n in a.notes:
        for tok in n.replace("%", " ").replace("(", " ").replace(")", " ").split():
            t = tok.strip("+,.").lstrip("+-")
            if t.replace(".", "", 1).isdigit():
                out.add(f"{float(t):g}")
    return out


def build(report_spec: dict, section: dict, evidence: dict[str, AnalysisResult]) -> Packet:
    ev = [evidence[i] for i in section["requires"] if i in evidence]
    period = evidence.get("reporting_period")
    period_line = ""
    if period:
        period_line = f"Reporting period: {period.value['start']} to {period.value['end']}\n"  # type: ignore[index]

    system = "\n".join(report_spec["global_instructions"])

    user = (
        f"Report type: {report_spec['report_type']} - {report_spec['title']}\n"
        f"Product: {report_spec['product']}\n"
        f"{period_line}"
        f"Section: {section['title']}\n\n"
        f"Approved evidence (the ONLY facts you may use):\n"
        + ("\n".join(_fmt(a) for a in ev) if ev else "(none - this section has no supporting evidence)")
        + f"\n\nSection instruction: {section['instructions']}\n"
        f"Hard limit: {section['max_words']} words."
    )

    allowed: set[str] = set()
    for a in ev:
        allowed |= _numbers(a)
    return Packet(section["id"], system, user, [a.id for a in ev], allowed)
