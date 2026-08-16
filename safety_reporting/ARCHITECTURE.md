# Architecture

```text
                        ┌──────────────────────────────────────────┐
   config/reports/      │  REPORT SPEC (JSON, data - not code)     │
   pader.json ─────────>│  report_type, model, global_instructions │
                        │  sections[]: id, title, requires[],      │
                        │              instructions, max_words     │
                        │  tables{}: section -> evidence to render │
                        └───────────────┬──────────────────────────┘
                                        │ declares what evidence is needed
                                        ▼
 ┌───────────┐   ┌──────────────┐   ┌──────────────────┐   ┌───────────────────┐
 │  ICSR CSV │──>│ dataset.py   │──>│ analyses.py      │──>│ EVIDENCE SET      │
 │ 1,068 rows│   │ column map ->│   │  registry of     │   │ id, title, value, │
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
                        ┌────────────────────────┐                   │
   per section ────────>│ packet.py              │<──────────────────┘
                        │  system = global rules │   only the evidence ids
                        │  user   = period +     │   this section declared
                        │  scoped evidence +     │
                        │  section instruction   │
                        └───────────┬────────────┘
                                    ▼
                        ┌────────────────────────┐        ┌────────────────────┐
                        │ llm.py                 │───────>│ Lovable AI Gateway │
                        │  streamed chat call    │<───────│ gemini-3-flash     │
                        └───────────┬────────────┘        └────────────────────┘
                                    ▼   draft text
                        ┌────────────────────────┐
                        │ verify.py              │   ungrounded number?
                        │  numbers ⊆ evidence    │   invented [E:id]?
                        │  citations valid       │   banned conclusion?
                        │  banned conclusions    │────> findings + auto-flag
                        └───────────┬────────────┘
                                    ▼
                         ────── HUMAN GATE 2 ──────   review.py: approve / flag + comment
                                    │                  (status stored in the bundle)
                                    ▼
                        ┌────────────────────────┐   out/PADER_report.md
                        │ render.py              │──> out/report_bundle.json
                        │  prose + tables +      │    out/case_index_full.csv
                        │  evidence register +   │
                        │  provenance appendix   │    /review page (UI mirror)
                        └────────────────────────┘
