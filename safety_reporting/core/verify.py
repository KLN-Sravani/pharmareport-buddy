"""Automated grounding checks run on every generated section.

This is the cheap, deterministic half of evaluation: it cannot judge prose
quality, but it catches the failure mode that matters here - a number or a
safety conclusion the evidence does not support.
"""

from __future__ import annotations

import re

from .packet import Packet

# phrases that assert a conclusion no line listing can establish
BANNED_PATTERNS = [
    r"no (new )?safety (concern|signal|issue)s? (were |was )?(identified|detected|observed|found)",
    r"benefit[- ]risk (profile|balance) (remains|is) (favourable|favorable|positive|unchanged)",
    r"\bno action (is )?(required|necessary)\b",
    r"\bsafe and (well[- ]tolerated|effective)\b",
    r"\b(caused by|due to the drug|drug[- ]related causality)\b",
    r"\bconsistent with the (known|established) safety profile\b",
]

NUM_RE = re.compile(r"(?<![\w.])(\d+(?:,\d{3})*(?:\.\d+)?)(?![\w])")


def check(text: str, packet: Packet) -> list[dict]:
    findings: list[dict] = []

    for pattern in BANNED_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            findings.append(
                {
                    "level": "error",
                    "type": "unsupported_conclusion",
                    "detail": m.group(0),
                    "section": packet.section_id,
                }
            )

    for m in NUM_RE.finditer(text):
        raw = m.group(1).replace(",", "")
        norm = f"{float(raw):g}"
        if norm in packet.allowed_numbers:
            continue
        # tolerate percentages rounded to a whole number and year-month tokens
        if any(abs(float(raw) - float(a)) < 0.5 for a in packet.allowed_numbers if _isnum(a)):
            continue
        if re.fullmatch(r"(19|20)\d{2}", raw):
            continue
        findings.append(
            {
                "level": "error",
                "type": "ungrounded_number",
                "detail": m.group(1),
                "section": packet.section_id,
            }
        )

    cited = set(re.findall(r"\[E:([a-z_]+)\]", text))
    uncited = [e for e in packet.evidence_ids if e not in cited]
    if packet.evidence_ids and not cited:
        findings.append({"level": "error", "type": "no_citations", "detail": "", "section": packet.section_id})
    elif uncited:
        findings.append(
            {
                "level": "info",
                "type": "evidence_not_cited",
                "detail": ", ".join(uncited),
                "section": packet.section_id,
            }
        )
    for c in cited:
        if c not in packet.evidence_ids:
            findings.append(
                {"level": "error", "type": "invalid_citation", "detail": c, "section": packet.section_id}
            )
    return findings


def _isnum(v: str) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False
