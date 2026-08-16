"""Render an approved report bundle to Markdown."""

from __future__ import annotations

from typing import Any


def _table(rows: list[dict]) -> str:
    if not rows:
        return "_(no rows)_\n"
    cols = list(rows[0].keys())
    head = "| " + " | ".join(c.replace("_", " ") for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = "\n".join("| " + " | ".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + " |" for r in rows)
    return f"{head}\n{sep}\n{body}\n"


def render_markdown(bundle: dict[str, Any]) -> str:
    spec = bundle["spec"]
    prov = bundle["provenance"]
    ev = {e["id"]: e for e in bundle["evidence"]}
    out: list[str] = []

    out.append(f"# {spec['title']}")
    out.append(f"**Product:** {spec['product']}  ")
    period = ev.get("reporting_period", {}).get("value", {})
    out.append(f"**Reporting period:** {period.get('start','?')} to {period.get('end','?')}  ")
    out.append(f"**Report type:** {spec['report_type']} (spec v{spec['version']})  ")
    out.append(f"**Regulatory basis:** {spec['regulatory_basis']}")
    out.append("")
    out.append(
        "> Prototype output. Every figure below is computed in Python from the source line "
        "listing; narrative text is model-drafted from those figures only and is marked with "
        "the evidence ids it cites."
    )
    out.append("")

    for section in spec["sections"]:
        sid = section["id"]
        sec = bundle["sections"][sid]
        out.append(f"## {section['title']}")
        status = sec["review"]["status"]
        badge = {"approved": "APPROVED", "flagged": "FLAGGED", "pending": "PENDING REVIEW"}[status]
        out.append(f"_Review status: **{badge}**_" + (f" — {sec['review']['comment']}" if sec["review"].get("comment") else ""))
        out.append("")
        out.append(sec["text"])
        out.append("")
        for tid in spec.get("tables", {}).get(sid, []):
            item = ev.get(tid)
            if not item:
                continue
            out.append(f"**{item['title']}** `[E:{item['id']}]`")
            out.append("")
            out.append(_table(item["value"]) if item["kind"] == "table" else f"`{item['value']}`\n")
        if sec["findings"]:
            out.append("**Automated grounding checks:**")
            for f in sec["findings"]:
                out.append(f"- `{f['level']}` {f['type']}{': ' + f['detail'] if f['detail'] else ''}")
            out.append("")

    out.append("## Appendix A — Evidence register")
    out.append("")
    out.append("Every evidence id cited above, with the exact computation behind it.")
    out.append("")
    out.append(
        _table(
            [
                {
                    "evidence id": e["id"],
                    "title": e["title"],
                    "method (deterministic Python)": e["method"],
                    "traced cases": sum(len(v) for v in e.get("trace", {}).values()) or "-",
                }
                for e in bundle["evidence"]
            ]
        )
    )
    out.append("## Appendix B — Provenance")
    out.append("")
    out.append(
        _table(
            [
                {"key": k, "value": str(v)}
                for k, v in {
                    **prov["dataset"],
                    "report_spec": f"{spec['report_type']} v{spec['version']}",
                    "spec_sha256": prov["spec_sha256"][:16],
                    "model": prov["model"],
                    "generated_at": prov["generated_at"],
                    "pipeline_version": prov["pipeline_version"],
                }.items()
            ]
        )
    )
    return "\n".join(out)
