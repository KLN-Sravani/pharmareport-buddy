"""Deterministic analysis registry.

Every number that can appear in a report is produced here, in Python, with an
exact answer and a list of the case IDs behind it. The LLM never computes.

Analyses are addressed by id ("total_cases", "top_reactions"). A report section
declares the ids it needs; adding a new report type means declaring different
ids, not writing new prose-generation code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from .dataset import Dataset


@dataclass
class AnalysisResult:
    id: str
    title: str
    kind: str  # "scalar" | "table" | "period"
    value: object  # scalar value, or list[dict] rows for tables
    method: str  # plain-language description of the exact computation
    trace: dict = field(default_factory=dict)  # key -> list of case ids (evidence)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "kind": self.kind,
            "value": self.value,
            "method": self.method,
            "trace": self.trace,
            "notes": self.notes,
        }


REGISTRY: dict[str, Callable[[Dataset, dict], AnalysisResult]] = {}


def analysis(analysis_id: str):
    def wrap(fn):
        REGISTRY[analysis_id] = fn
        fn.analysis_id = analysis_id
        return fn

    return wrap


def cases(ds: Dataset) -> pd.DataFrame:
    """Case-level view: one row per unique safetyreportid."""
    return ds.frame.sort_values("receipt_date").drop_duplicates("case_id", keep="first")


def _ids(frame: pd.DataFrame, limit: int = 50) -> list[str]:
    return frame["case_id"].astype(str).unique().tolist()[:limit]


# --------------------------------------------------------------------------- counts
@analysis("reporting_period")
def reporting_period(ds: Dataset, params: dict) -> AnalysisResult:
    dates = ds.frame["receipt_date"].dropna()
    start = params.get("period_start") or dates.min().date().isoformat()
    end = params.get("period_end") or dates.max().date().isoformat()
    return AnalysisResult(
        "reporting_period",
        "Reporting period covered by the dataset",
        "period",
        {"start": start, "end": end, "days": (pd.Timestamp(end) - pd.Timestamp(start)).days},
        "min/max of receiptdate across all rows (or configured override)",
    )


@analysis("total_cases")
def total_cases(ds: Dataset, params: dict) -> AnalysisResult:
    c = cases(ds)
    return AnalysisResult(
        "total_cases",
        "Total individual case safety reports",
        "scalar",
        int(len(c)),
        "count of unique safetyreportid values",
        trace={"all": _ids(c)},
        notes=[f"{ds.row_count} data rows collapse to {len(c)} cases (cases may have >1 reaction)"],
    )


@analysis("seriousness_split")
def seriousness_split(ds: Dataset, params: dict) -> AnalysisResult:
    c = cases(ds)
    serious = c[c["serious"] == "serious"]
    non = c[c["serious"] != "serious"]
    total = len(c) or 1
    return AnalysisResult(
        "seriousness_split",
        "Serious vs non-serious cases",
        "table",
        [
            {"seriousness": "serious", "cases": len(serious), "pct": round(100 * len(serious) / total, 1)},
            {"seriousness": "non-serious", "cases": len(non), "pct": round(100 * len(non) / total, 1)},
        ],
        "case-level count grouped by the `serious` field",
        trace={"serious": _ids(serious), "non-serious": _ids(non)},
    )


def _group(ds: Dataset, col: str, analysis_id: str, title: str, top: int | None = None) -> AnalysisResult:
    c = cases(ds)
    counts = c.groupby(col).size().sort_values(ascending=False)
    if top:
        counts = counts.head(top)
    total = len(c) or 1
    rows = [{col: k, "cases": int(v), "pct": round(100 * v / total, 1)} for k, v in counts.items()]
    trace = {str(k): _ids(c[c[col] == k]) for k in counts.index}
    return AnalysisResult(analysis_id, title, "table", rows, f"case-level count grouped by `{col}`", trace)


@analysis("by_age_band")
def by_age_band(ds: Dataset, params: dict) -> AnalysisResult:
    return _group(ds, "age_band", "by_age_band", "Cases by age group")


@analysis("by_sex")
def by_sex(ds: Dataset, params: dict) -> AnalysisResult:
    return _group(ds, "sex", "by_sex", "Cases by sex")


@analysis("by_country")
def by_country(ds: Dataset, params: dict) -> AnalysisResult:
    return _group(ds, "country", "by_country", "Cases by country of occurrence", top=params.get("top", 10))


@analysis("age_summary")
def age_summary(ds: Dataset, params: dict) -> AnalysisResult:
    ages = cases(ds)["age"].dropna()
    return AnalysisResult(
        "age_summary",
        "Age distribution summary",
        "scalar",
        {
            "n_with_age": int(len(ages)),
            "median": float(ages.median()) if len(ages) else None,
            "min": float(ages.min()) if len(ages) else None,
            "max": float(ages.max()) if len(ages) else None,
        },
        "median/min/max of patient_patientonsetage over cases with a recorded age",
    )


# ------------------------------------------------------------------------ reactions
@analysis("top_reactions")
def top_reactions(ds: Dataset, params: dict) -> AnalysisResult:
    top = params.get("top", 10)
    f = ds.frame
    counts = f.groupby("reaction")["case_id"].nunique().sort_values(ascending=False).head(top)
    total = cases(ds).shape[0] or 1
    rows = [{"reaction": k, "cases": int(v), "pct_of_cases": round(100 * v / total, 1)} for k, v in counts.items()]
    trace = {str(k): _ids(f[f["reaction"] == k]) for k in counts.index}
    return AnalysisResult(
        "top_reactions",
        f"Most frequently reported reactions (MedDRA PT, top {top})",
        "table",
        rows,
        "unique case count per reaction preferred term across all reaction rows",
        trace,
    )


@analysis("top_serious_reactions")
def top_serious_reactions(ds: Dataset, params: dict) -> AnalysisResult:
    top = params.get("top", 10)
    f = ds.frame[ds.frame["serious"] == "serious"]
    counts = f.groupby("reaction")["case_id"].nunique().sort_values(ascending=False).head(top)
    rows = [{"reaction": k, "serious_cases": int(v)} for k, v in counts.items()]
    trace = {str(k): _ids(f[f["reaction"] == k]) for k in counts.index}
    return AnalysisResult(
        "top_serious_reactions",
        f"Most frequently reported reactions in serious cases (top {top})",
        "table",
        rows,
        "unique case count per reaction, restricted to rows where serious == serious",
        trace,
    )


@analysis("outcomes")
def outcomes(ds: Dataset, params: dict) -> AnalysisResult:
    return _group(ds, "outcome", "outcomes", "Reported reaction outcomes (case level, first reaction)")


@analysis("fatal_cases")
def fatal_cases(ds: Dataset, params: dict) -> AnalysisResult:
    f = ds.frame
    fatal = f[(f["death_flag"].astype(str).str.strip() == "1") | (f["outcome"] == "fatal")]
    return AnalysisResult(
        "fatal_cases",
        "Cases with a fatal outcome or death seriousness criterion",
        "scalar",
        int(fatal["case_id"].nunique()),
        "unique cases where seriousnessdeath == 1 or reaction outcome == fatal",
        trace={"fatal": _ids(fatal)},
    )


@analysis("seriousness_criteria")
def seriousness_criteria(ds: Dataset, params: dict) -> AnalysisResult:
    f = ds.frame
    rows = []
    trace = {}
    for col, label in [
        ("death_flag", "death"),
        ("life_threatening_flag", "life-threatening"),
        ("hospitalization_flag", "hospitalisation"),
    ]:
        sub = f[f[col].astype(str).str.strip() == "1"]
        rows.append({"criterion": label, "cases": int(sub["case_id"].nunique())})
        trace[label] = _ids(sub)
    return AnalysisResult(
        "seriousness_criteria",
        "Serious cases by regulatory seriousness criterion",
        "table",
        rows,
        "unique case count per ICH seriousness flag column (a case may meet several)",
        trace,
        notes=["criteria are not mutually exclusive; they do not sum to total serious cases"],
    )


# ---------------------------------------------------------------------------- time
@analysis("monthly_trend")
def monthly_trend(ds: Dataset, params: dict) -> AnalysisResult:
    c = cases(ds).dropna(subset=["receipt_date"])
    counts = c.groupby(c["receipt_date"].dt.to_period("M")).size()
    rows = [{"month": str(k), "cases": int(v)} for k, v in counts.items()]
    trace = {str(k): _ids(c[c["receipt_date"].dt.to_period("M") == k]) for k in counts.index}
    half = len(rows) // 2 or 1
    first, second = sum(r["cases"] for r in rows[:half]), sum(r["cases"] for r in rows[half:])
    change = round(100 * (second - first) / first, 1) if first else None
    return AnalysisResult(
        "monthly_trend",
        "Cases received per calendar month",
        "table",
        rows,
        "case-level count grouped by month of receiptdate",
        trace,
        notes=[
            f"first half {first} cases vs second half {second} cases "
            f"({change:+}% change)" if change is not None else "insufficient data for half-period comparison"
        ],
    )


@analysis("data_quality")
def data_quality(ds: Dataset, params: dict) -> AnalysisResult:
    return AnalysisResult(
        "data_quality",
        "Data validation findings",
        "table",
        [i for i in ds.validation if i.get("count", 0)],
        "field-completeness and duplication checks run at load time",
    )


@analysis("case_index")
def case_index(ds: Dataset, params: dict) -> AnalysisResult:
    limit = params.get("limit", 25)
    c = cases(ds).sort_values("receipt_date")
    rows = [
        {
            "case_id": r.case_id,
            "receipt_date": r.receipt_date.date().isoformat() if pd.notna(r.receipt_date) else "",
            "country": r.country,
            "age": None if pd.isna(r.age) else int(r.age),
            "sex": r.sex,
            "reaction": r.reaction,
            "seriousness": r.serious,
            "outcome": r.outcome,
        }
        for r in c.head(limit).itertuples()
    ]
    return AnalysisResult(
        "case_index",
        f"Case listing (first {limit} of {len(c)} cases by receipt date)",
        "table",
        rows,
        "case-level rows sorted by receiptdate; full listing exported separately",
        notes=[f"full listing of {len(c)} cases exported to case_index_full.csv"],
    )


def run(ds: Dataset, analysis_id: str, params: dict | None = None) -> AnalysisResult:
    if analysis_id not in REGISTRY:
        raise KeyError(f"unknown analysis '{analysis_id}' (registered: {sorted(REGISTRY)})")
    return REGISTRY[analysis_id](ds, params or {})
