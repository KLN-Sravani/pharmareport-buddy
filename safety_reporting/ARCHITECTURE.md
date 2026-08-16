# Architecture

```text
                       ┌──────────────────────────────────────────┐
   config/reports/     │  REPORT SPEC (JSON, data - not code)     │
   pader.json ────────▶│  report_type, model, global_instructions │
                       │  sections[]: id, title, requires[],      │
                       │              instructions, max_words     │
                       │  tables{}: section -> evidence to render │
                       └───────────────┬──────────────────────────┘
                                       │ declares what evidence is needed
                                       ▼
 ┌───────────┐   ┌──────────────┐   ┌──────────────────┐   ┌───────────────────┐
 │  ICSR CSV │──▶│ dataset.py   │──▶│  analyses.py     │──▶│ EVIDENCE SET      │
 │ 1,068 rows│   │ column map → │   │  registry of     │   │ id, title, value, │
 └───────────┘   │ canonical df │   │  deterministic   │   │ method, trace     │
                 │ + validation │   │  analyses (15)   │   │ (case ids)        │
                 └──────────────┘   └──────────────────┘   └─────────┬─────────┘
                        │                                            │
                        │ data-quality findings                      │
                        └────────────────────────────────────────────┤
                                                                     │
                                    ┌────────────── HUMAN GATE 1 ────┤  (analysis review:
                                    │                                │   validation output +
                                    ▼                                │   evidence register)
                       ┌────────────────────────┐                    │
   per section ───────▶│  packet.py             │◀───────────────────┘
                       │  system = global rules │   only the evidence ids
                       │  user   = period +     │   this section declared
                       │  scoped evidence +     │
                       │  section instruction   │
                       └───────────┬────────────┘
                                   ▼
                       ┌────────────────────────┐        ┌────────────────────┐
                       │  llm.py                │───────▶│ Lovable AI Gateway │
                       │  streamed chat call    │◀───────│ gemini-3-flash     │
                       └───────────┬────────────┘        └────────────────────┘
                                   ▼   draft text
                       ┌────────────────────────┐
                       │  verify.py             │  ungrounded number?
                       │  numbers ⊆ evidence    │  invented [E:id]?
                       │  citations valid       │  banned conclusion?
                       │  banned conclusions    │────▶ findings + auto-flag
                       └───────────┬────────────┘
                                   ▼
                         ────── HUMAN GATE 2 ──────   review.py: approve / flag + comment
                                   │                  (status stored in the bundle)
                                   ▼
                       ┌────────────────────────┐     out/PADER_report.md
                       │  render.py             │────▶ out/report_bundle.json
                       │  prose + tables +      │     out/case_index_full.csv
                       │  evidence register +   │
                       │  provenance appendix   │     /review page (UI mirror)
                       └────────────────────────┘
```

## Why this shape

- **Evidence is a first-class object, not a prompt string.** Analyses return
  value + method + case-id trace, so the same object serves the packet, the
  rendered tables, the evidence register and drill-down.
- **Sections declare dependencies (`requires`), they don't fetch data.** Sections
  and analyses stay decoupled and independently reusable.
- **The model sits in one narrow slot** (figures → prose) with a deterministic
  check on either side of it.
- **The report type is data.** Adding PSUR/PBRER means adding a spec file (and
  occasionally an analysis function), not a code path.
- **Provenance travels with the report**: dataset sha256, spec version + sha,
  model id, pipeline version, timestamp, gateway run ids per section.
