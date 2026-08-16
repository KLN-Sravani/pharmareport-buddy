# Regulatory Safety Reporting — Version 0

A small, config-driven system that turns an ICSR line listing into a controlled,
traceable periodic safety report. PADER is the first report type it knows about,
not the thing it is built around.

## Run it

```bash
python safety_reporting/make_sample_data.py           # only needed if you don't have the real CSV
python -m safety_reporting.pipeline                   # load → analyse → draft → verify → render
python -m safety_reporting.review --list              # human gate
python -m safety_reporting.review --approve trends --reviewer "J. Smith"
python -m safety_reporting.review --flag narrative_summary --comment "invented threshold"
python -m safety_reporting.pipeline --offline         # runs the whole flow with no model calls
```

Outputs land in `safety_reporting/out/`:

| file | what it is |
|---|---|
| `PADER_report.md` | the generated report (deliverable #2) |
| `report_bundle.json` | everything: evidence, per-section packets, prompts, findings, review state, provenance |
| `case_index_full.csv` | full case listing referenced by the report |

**Dataset note:** the exercise CSV (`Bisoprolol_icsr_sample_1068rows.csv`) was not
attached to this workspace, so `make_sample_data.py` writes a stand-in with the
same column names, 1,068 rows / 1,024 unique cases and 1,023 serious cases. Drop
the real file at `safety_reporting/data/Bisoprolol_icsr_sample_1068rows.csv` and
re-run — nothing in the pipeline is tuned to the synthetic data.

## Architecture

See `ARCHITECTURE.md`. In one line:

```
CSV → canonical frame (+validation) → deterministic analyses (evidence, with case-id traces)
    → human gate → per-section context packet → LLM draft → automated grounding checks
    → human gate (approve/flag) → renderer
```

## Where AI is used, and where it deliberately isn't

| Step | Who does it | Why |
|---|---|---|
| Parsing, normalisation, validation | Python | Exactness; an LLM adds only risk |
| Every count, %, top-N, trend | Python (`core/analyses.py`) | The model must never do arithmetic over 1,068 rows |
| Choosing which evidence a section needs | Config (`config/reports/pader.json`) | Reviewable, diffable, and reusable across report types |
| Turning approved figures into regulatory prose | LLM | The one job it is actually good at |
| Checking the prose against the evidence | Python (`core/verify.py`) | Deterministic guardrail on a stochastic step |
| Deciding what is final | Human (`review.py`) | Regulatory accountability isn't delegable |

**No agent loop, no RAG, no vector store.** There is nothing to retrieve: the
evidence set is small, enumerable and computed on demand. An agent choosing tools
at runtime would make the same eight calls every time, non-deterministically. The
"planning" is the report spec, and it is data.

Model: `google/gemini-3-flash-preview` via the Lovable AI Gateway
(OpenAI-compatible chat completions, streamed), temperature 0.1. The model id
lives in the report spec, so a different report type can use a different model.

## Context engineering

Two layers, on purpose:

- **System prompt** = the rules that are true for *every* section of this report
  type: only stated evidence, no safety conclusions, cite `[E:id]`, neutral tone,
  Markdown body only. Written once in the spec's `global_instructions`.
- **User prompt** = assembled per section: report/product/period header, *only*
  the evidence items that section declared, each rendered as
  `[E:id] title / method / rows / notes`, then the section-specific instruction
  and a word limit.

What is deliberately **not** in the packet: the raw CSV, other sections' evidence,
prior sections' text, the case-id traces (those stay server-side for drill-down),
and any prose about pharmacovigilance in general.

Real packet for section 2, as sent (from `report_bundle.json`):

```
Report type: PADER - Periodic Adverse Drug Experience Report (PADER) - simplified
Product: Bisoprolol fumarate
Reporting period: 2024-07-01 to 2025-06-30
Section: 2. Narrative Summary and Analysis

Approved evidence (the ONLY facts you may use):
[E:total_cases] Total individual case safety reports
  method: count of unique safetyreportid values
  value: 1024
  note: 1067 data rows collapse to 1024 cases (cases may have >1 reaction)
[E:seriousness_split] Serious vs non-serious cases
  method: case-level count grouped by the `serious` field
  - {"seriousness": "serious", "cases": 1023, "pct": 99.9}
  - {"seriousness": "non-serious", "cases": 1, "pct": 0.1}
[E:top_reactions] Most frequently reported reactions (MedDRA PT, top 10)
  method: unique case count per reaction preferred term across all reaction rows
  - {"reaction": "Hypotension", "cases": 150, "pct_of_cases": 14.6}
  ...

Section instruction: Summarise the case volume, the serious/non-serious split
with percentages, and the most frequently reported reactions. Do not interpret
clinical significance. 3-5 sentences.
Hard limit: 160 words.
```

## Grounding and traceability

1. Each analysis result carries `method` (the exact computation in words) and
   `trace` (the case IDs behind every bucket).
2. The packet exposes each result under an id; the model must cite `[E:id]`.
3. `core/verify.py` re-reads the draft and fails it on:
   - a number not present in that section's evidence (with tolerance for rounding,
     years, `15-day`, and numbers inside evidence labels),
   - an invented or missing `[E:id]` citation,
   - banned conclusion phrasing ("no new safety concerns were identified",
     "benefit-risk remains favourable", causality language …).
4. Failing sections are auto-set to `flagged` and cannot be silently approved.

It works: in the shipped run, section 2 was flagged because the model wrote
"reported in more than **5%** of cases" — a threshold that appears nowhere in the
evidence. Every other number in the report traces to a Python computation.
That flag is left in the delivered report on purpose.

## Human control

`review.py` is the gate. Sections start `pending` (or `flagged` if checks failed);
`--approve` / `--flag [--comment]` records reviewer + comment into the bundle and
re-renders. The rendered report prints each section's review status, so an
unreviewed report is visibly unreviewed rather than quietly passing as final.
A UI version of the same gate is at `/review` in the app in this repo (read-only
view of the shipped bundle: sections, status, evidence and packets).

## Generalisation — what survives a PSUR/PBRER/DSUR request

Unchanged: `dataset.py`, `analyses.py`, `packet.py`, `llm.py`, `verify.py`,
`render.py`, `review.py`, `pipeline.py` — i.e. all of the code.
Changed: a new JSON spec in `config/reports/`, declaring its sections, each
section's `requires` ids, its instructions and word limits, plus any *new*
analysis functions its sections need (a new `@analysis("...")` function, ~10
lines, immediately reusable by every other report type).

Concretely: a PBRER's "Cumulative Exposure" section needs a new analysis and a
new data source mapping; its "Serious Cases" section reuses `seriousness_split`,
`seriousness_criteria` and `fatal_cases` verbatim. A new report type is a
config + registry change, not a new pipeline.

## Known limitations

- Case-level aggregation keeps the first row per `safetyreportid`; outcome/country
  at case level therefore reflect the first reaction row. Reaction analyses use
  all rows, deduplicated by case.
- No listedness/expectedness fields in the data → true 15-day expedited
  reportability cannot be computed; the report says so instead of guessing.
- No exposure/denominator data → no reporting rates; the trend section is
  explicitly framed as reporting frequency, not risk.
- Grounding checks are numeric + phrase-based. They catch fabricated figures and
  boilerplate reassurance, not subtle mischaracterisation — hence the human gate.
- No deduplication of clinically duplicate cases (only exact `safetyreportid`).
- Section text is not regenerated automatically when flagged; that is a
  Version 1 item (`--regenerate <section>`).
- Sequential generation; no retry/backoff on gateway 429s.
