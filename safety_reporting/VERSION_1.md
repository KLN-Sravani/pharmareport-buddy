# Version 1 — what's implemented, and how V0 evolves

## Already in Version 0 (V1 items landed early because they were cheap)

- **Section dependencies** — each section declares `requires: [analysis_ids]`;
  the pipeline computes the union once and hands each section only its slice.
- **Configurable instructions** — global rules + per-section instructions + word
  limits live in the report spec, not in code. A second report type ships as a
  second JSON file.
- **Reusable analyses** — a keyed registry (`@analysis("seriousness_split")`);
  the same function already serves four sections and would serve a PSUR
  unchanged.
- **Versioning / provenance** — dataset sha256 + row/case counts, spec version
  and sha256, model id, pipeline version, generation timestamp and per-section
  gateway run id, all persisted in the bundle and printed in Appendix B.
- **Evidence tracing** — every figure carries `method` and the case IDs behind
  each bucket; the report cites `[E:id]` per sentence and Appendix A maps each id
  to its exact computation. The `/review` page renders section → evidence →
  packet.
- **Evaluation (deterministic half)** — `verify.py` fails a section on ungrounded
  numbers, invalid citations, and banned safety conclusions; failures auto-flag.

## Next increments, in the order I would build them

1. **Regeneration loop.** `pipeline --regenerate <section> [--note "..."]` re-runs
   one packet with the reviewer's comment appended as a correction instruction,
   diffs old vs new, and resets review status. Cheap, and it closes the loop the
   human gate currently opens.
2. **Analysis contracts.** Give each analysis a declared output schema and each
   section a check that its required analyses returned non-empty results, so a
   spec referencing a field a new data source lacks fails loudly at load time
   rather than producing a confidently empty sentence.
3. **Second report type (PSUR skeleton) as a spec-only change** — the real test
   of the abstraction. Expected delta: new spec JSON, 2-3 new analyses
   (cumulative counts, exposure, signal tabulation), zero pipeline edits. Any
   pipeline edit needed is a design bug worth fixing then.
4. **Evaluation beyond checks.** Three layers:
   - *golden fixtures*: a tiny CSV with hand-computed expected values, asserted
     against the analysis registry (protects the numbers forever);
   - *packet snapshot tests*: assert the exact prompt each section assembles, so
     prompt drift is a reviewable diff;
   - *LLM-as-judge on entailment only*: for each generated sentence, ask a second
     model "is this entailed by these evidence items, yes/no + which id", and
     report an entailment rate. Judging style is not worth the tokens; judging
     entailment complements the numeric checker.
5. **Multi-source evidence.** The column map in `dataset.py` becomes a per-source
   mapping file, so an exposure/sales table or a literature feed joins the same
   evidence set with no analysis rewriting.
6. **Storage + real review UI.** Move bundles into Lovable Cloud (report,
   section, evidence, review_event tables), so review is multi-user, auditable
   (who approved what, when, against which spec version) and reports are
   comparable across periods (previous-period delta becomes an analysis:
   `top_reactions_delta(previous_bundle)`).

## The lens

The only PADER-specific artefacts in the system are `config/reports/pader.json`
and a handful of analysis functions. If PSUR/PBRER/DSUR/CSR arrive, what changes
is: one spec file each, new analyses in the shared registry, and — where a report
needs a genuinely different renderer (e.g. DOCX with regulator-mandated section
numbering) — a second renderer behind the same bundle interface. The load,
packet, generate, verify, review and provenance path is report-type agnostic
today, and that is the part worth keeping.
