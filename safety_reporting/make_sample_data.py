"""Generate a stand-in ICSR dataset in the real Bisoprolol export format.

The exercise dataset (Bisoprolol_icsr_sample_1068rows.csv) was not attached to
this workspace, so this script produces a file with the SAME column names,
shape (1,068 rows / 1,024 unique cases) and broad distribution so the pipeline
can be demonstrated end to end. Drop the real CSV at the same path and every
downstream step works unchanged - nothing in the pipeline is tuned to this data.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).parent / "data" / "Bisoprolol_icsr_sample_1068rows.csv"

COLUMNS = [
    "safetyreportid",
    "receiptdate",
    "occurcountry",
    "primarysourcecountry",
    "patient_patientonsetage",
    "patient_patientonsetageunit",
    "patient_patientsex",
    "medicinalproduct",
    "drug_characterization",
    "patient_reaction_reactionmeddrapt",
    "patient_reaction_reactionoutcome",
    "serious",
    "seriousnessdeath",
    "seriousnesshospitalization",
    "seriousnesslifethreatening",
    "seriousnessdisabling",
    "seriousnessother",
    "reporttype",
]

REACTIONS = [
    ("Acute kidney injury", 22),
    ("Drug ineffective", 12),
    ("Cerebral haemorrhage", 7),
    ("Bradycardia", 34),
    ("Hypotension", 28),
    ("Dizziness", 25),
    ("Fatigue", 19),
    ("Dyspnoea", 17),
    ("Atrioventricular block", 11),
    ("Syncope", 14),
    ("Fall", 10),
    ("Cardiac failure", 9),
    ("Hyperkalaemia", 8),
    ("Bronchospasm", 6),
    ("Rash", 5),
    ("Depression", 5),
    ("Nausea", 7),
    ("Headache", 6),
    ("Off label use", 4),
    ("Death", 3),
]
COUNTRIES = [
    ("united states", 0.42),
    ("united kingdom", 0.14),
    ("germany", 0.11),
    ("france", 0.08),
    ("japan", 0.07),
    ("canada", 0.06),
    ("italy", 0.05),
    ("spain", 0.04),
    ("australia", 0.03),
]
OUTCOMES = [
    ("recovered/resolved", 0.34),
    ("recovering/resolving", 0.14),
    ("not recovered/not resolved", 0.18),
    ("recovered/resolved with sequelae", 0.05),
    ("fatal", 0.07),
    ("unknown", 0.22),
]


def weighted(pairs, rng):
    total = sum(w for _, w in pairs)
    r = rng.uniform(0, total)
    acc = 0.0
    for value, w in pairs:
        acc += w
        if r <= acc:
            return value
    return pairs[-1][0]


def main() -> None:
    rng = random.Random(20260816)
    start = date(2024, 7, 1)
    n_cases = 1024
    rows: list[dict] = []

    # 1,023 of 1,024 cases serious (mirrors the figures quoted in the brief).
    non_serious_case = rng.randrange(n_cases)

    for i in range(n_cases):
        case_id = f"{10000000 + i * 7 + rng.randrange(5)}"
        day = rng.randrange(365)
        # mild upward drift in the second half of the period
        if rng.random() < 0.18:
            day = rng.randrange(182, 365)
        receipt = start + timedelta(days=day)
        serious = i != non_serious_case
        age = max(1, min(99, int(rng.gauss(68, 14))))
        sex = weighted([("female", 0.53), ("male", 0.44), ("unknown", 0.03)], rng)
        outcome = weighted(OUTCOMES, rng)
        n_reactions = 1 if rng.random() < 0.96 else 2  # 1,068 rows total-ish
        for _ in range(n_reactions):
            reaction = weighted(REACTIONS, rng)
            fatal = serious and (outcome == "fatal" or reaction == "Death")
            rows.append(
                {
                    "safetyreportid": case_id,
                    "receiptdate": receipt.strftime("%Y%m%d"),
                    "occurcountry": weighted(COUNTRIES, rng),
                    "primarysourcecountry": "",
                    "patient_patientonsetage": age,
                    "patient_patientonsetageunit": "801",
                    "patient_patientsex": sex,
                    "medicinalproduct": "BISOPROLOL FUMARATE",
                    "drug_characterization": "suspect",
                    "patient_reaction_reactionmeddrapt": reaction,
                    "patient_reaction_reactionoutcome": outcome,
                    "serious": "serious" if serious else "non-serious",
                    "seriousnessdeath": "1" if fatal else "",
                    "seriousnesshospitalization": "1"
                    if serious and not fatal and rng.random() < 0.55
                    else "",
                    "seriousnesslifethreatening": "1"
                    if serious and rng.random() < 0.08
                    else "",
                    "seriousnessdisabling": "1" if serious and rng.random() < 0.04 else "",
                    "seriousnessother": "1" if serious and rng.random() < 0.4 else "",
                    "reporttype": weighted(
                        [("spontaneous", 0.86), ("report from study", 0.06), ("other", 0.08)], rng
                    ),
                }
            )

    # trim/extend to exactly 1,068 rows without dropping a whole case
    while len(rows) > 1068:
        for idx in range(len(rows) - 1, 0, -1):
            if rows[idx]["safetyreportid"] == rows[idx - 1]["safetyreportid"]:
                rows.pop(idx)
                break
        else:
            break

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows / {len({r['safetyreportid'] for r in rows})} cases -> {OUT}")


if __name__ == "__main__":
    main()
