"""Load + validate an ICSR line-listing into a canonical frame.

Anything downstream (analyses, packets, report) sees canonical column names, so
a new data source only needs a new mapping entry - not new analysis code.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# canonical name -> candidate source columns (first match wins)
COLUMN_MAP: dict[str, list[str]] = {
    "case_id": ["safetyreportid", "case_id", "caseid"],
    "receipt_date": ["receiptdate", "receivedate", "report_date"],
    "country": ["occurcountry", "primarysourcecountry", "country"],
    "age": ["patient_patientonsetage", "age"],
    "sex": ["patient_patientsex", "sex"],
    "product": ["medicinalproduct", "product"],
    "reaction": ["patient_reaction_reactionmeddrapt", "reaction"],
    "outcome": ["patient_reaction_reactionoutcome", "outcome"],
    "serious": ["serious", "seriousness"],
    "death_flag": ["seriousnessdeath"],
    "hospitalization_flag": ["seriousnesshospitalization"],
    "life_threatening_flag": ["seriousnesslifethreatening"],
    "report_type": ["reporttype"],
}

SEX_MAP = {"1": "male", "2": "female", "0": "unknown", "male": "male", "female": "female"}
AGE_BANDS = [(0, 17, "0-17"), (18, 44, "18-44"), (45, 64, "45-64"), (65, 74, "65-74"), (75, 200, "75+")]


@dataclass
class Dataset:
    frame: pd.DataFrame
    source_path: str
    sha256: str
    row_count: int
    case_count: int
    validation: list[dict] = field(default_factory=list)

    @property
    def provenance(self) -> dict:
        return {
            "source_file": Path(self.source_path).name,
            "sha256": self.sha256,
            "rows": self.row_count,
            "unique_cases": self.case_count,
        }


def _band(age) -> str:
    if pd.isna(age):
        return "unknown"
    for lo, hi, label in AGE_BANDS:
        if lo <= age <= hi:
            return label
    return "unknown"


def load(path: str | Path) -> Dataset:
    path = Path(path)
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    df = pd.DataFrame()
    issues: list[dict] = []
    for canonical, candidates in COLUMN_MAP.items():
        for c in candidates:
            if c in raw.columns:
                df[canonical] = raw[c]
                break
        else:
            df[canonical] = ""
            issues.append({"level": "warning", "check": f"missing_column:{canonical}"})

    df["case_id"] = df["case_id"].astype(str).str.strip()
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["sex"] = df["sex"].str.strip().str.lower().map(lambda v: SEX_MAP.get(v, "unknown"))
    df["country"] = df["country"].str.strip().str.lower().replace("", "unknown")
    df["reaction"] = df["reaction"].str.strip()
    df["outcome"] = df["outcome"].str.strip().str.lower().replace("", "unknown")
    df["serious"] = df["serious"].str.strip().str.lower().map(
        lambda v: "serious" if v in {"serious", "1", "yes", "y", "true"} else "non-serious"
    )
    df["receipt_date"] = pd.to_datetime(df["receipt_date"], format="mixed", errors="coerce")
    df["age_band"] = df["age"].map(_band)

    # data-quality checks surfaced in the report, never silently swallowed
    def check(name: str, count: int, level: str = "warning") -> None:
        issues.append({"level": level if count else "ok", "check": name, "count": int(count)})

    check("rows_missing_case_id", (df["case_id"] == "").sum(), "error")
    check("rows_missing_reaction", (df["reaction"] == "").sum())
    check("rows_missing_receipt_date", df["receipt_date"].isna().sum())
    check("rows_missing_age", df["age"].isna().sum())
    check("rows_unknown_sex", (df["sex"] == "unknown").sum())
    check("duplicate_rows", df.duplicated().sum())

    return Dataset(
        frame=df,
        source_path=str(path),
        sha256=digest,
        row_count=len(df),
        case_count=df["case_id"].nunique(),
        validation=issues,
    )
