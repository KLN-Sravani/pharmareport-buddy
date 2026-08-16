import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import bundleJson from "@/data/report_bundle.json";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "PADER Review Console — Grounded Safety Reporting" },
      {
        name: "description",
        content:
          "Human review gate for an AI-drafted PADER: every figure traced to a deterministic analysis of the ICSR line listing.",
      },
      { property: "og:title", content: "PADER Review Console — Grounded Safety Reporting" },
      {
        property: "og:description",
        content:
          "Review AI-drafted periodic safety report sections against the exact evidence and prompts that produced them.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: ReviewConsole,
});

type Finding = { level: string; type: string; detail: string };
type Evidence = {
  id: string;
  title: string;
  kind: string;
  value: unknown;
  method: string;
  trace: Record<string, string[]>;
  notes: string[];
};
type Section = {
  title: string;
  text: string;
  packet: { system: string; user: string };
  evidence_ids: string[];
  findings: Finding[];
  model: string;
  review: { status: string; comment: string; reviewer: string | null };
};

const bundle = bundleJson as unknown as {
  spec: { title: string; report_type: string; product: string; version: string; sections: { id: string }[] };
  provenance: {
    dataset: { source_file: string; sha256: string; rows: number; unique_cases: number };
    spec_sha256: string;
    model: string;
    generated_at: string;
    pipeline_version: string;
  };
  evidence: Evidence[];
  sections: Record<string, Section>;
};

const STATUS_LABEL: Record<string, string> = {
  approved: "Approved",
  flagged: "Flagged",
  pending: "Pending review",
};

function StatusPill({ status }: { status: string }) {
  const tone =
    status === "approved"
      ? "bg-success/12 text-success border-success/30"
      : status === "flagged"
        ? "bg-destructive/10 text-destructive border-destructive/30"
        : "bg-muted text-muted-foreground border-border";
  return (
    <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-medium tracking-wide ${tone}`}>
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}

function EvidenceValue({ item }: { item: Evidence }) {
  if (item.kind === "table" && Array.isArray(item.value) && item.value.length > 0) {
    const rows = item.value as Record<string, unknown>[];
    const cols = Object.keys(rows[0] as Record<string, unknown>);
    return (
      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full text-xs">
          <thead className="bg-muted/60">
            <tr>
              {cols.map((c) => (
                <th key={c} className="px-3 py-1.5 text-left font-medium text-muted-foreground">
                  {c.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 12).map((r, i) => (
              <tr key={i} className="border-t border-border/70">
                {cols.map((c) => (
                  <td key={c} className="px-3 py-1.5 tabular-nums">
                    {String(r[c] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  return (
    <pre className="overflow-x-auto rounded-md border border-border bg-muted/40 px-3 py-2 text-xs">
      {JSON.stringify(item.value, null, 2)}
    </pre>
  );
}

function ReviewConsole() {
  const sectionIds = bundle.spec.sections.map((s) => s.id);
  const [active, setActive] = useState<string>(sectionIds[0] as string);
  const [state, setState] = useState<Record<string, { status: string; comment: string }>>(() =>
    Object.fromEntries(
      sectionIds.map((id) => [
        id,
        {
          status: (bundle.sections[id] as Section).review.status,
          comment: (bundle.sections[id] as Section).review.comment,
        },
      ]),
    ),
  );
  const [showPacket, setShowPacket] = useState(false);
  const [openEvidence, setOpenEvidence] = useState<string | null>(null);

  const evidenceById = useMemo(
    () => Object.fromEntries(bundle.evidence.map((e) => [e.id, e])) as Record<string, Evidence>,
    [],
  );
  const section = bundle.sections[active] as Section;
  const current = state[active] as { status: string; comment: string };
  const approved = sectionIds.filter((id) => state[id]?.status === "approved").length;

  const setStatus = (status: string) =>
    setState((s) => ({ ...s, [active]: { ...(s[active] as { status: string; comment: string }), status } }));

  // highlight [E:id] citations inline
  const parts: string[] = section.text.split(/(\[E:[a-z_]+(?:,\s*E:[a-z_]+)*\])/g);

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-card">
        <div className="mx-auto max-w-6xl px-6 py-7">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-accent">
            {bundle.spec.report_type} · spec v{bundle.spec.version} · human review gate
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">{bundle.spec.title}</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {bundle.spec.product} · {bundle.provenance.dataset.rows} rows ·{" "}
            {bundle.provenance.dataset.unique_cases} unique cases · model{" "}
            <code className="text-xs">{bundle.provenance.model}</code>
          </p>
          <p className="mt-3 text-xs text-muted-foreground">
            {approved} of {sectionIds.length} sections approved. Nothing is final until every section is
            approved by a reviewer.
          </p>
        </div>
      </header>

      <div className="mx-auto grid max-w-6xl gap-6 px-6 py-8 lg:grid-cols-[260px_1fr]">
        <nav className="space-y-1">
          {sectionIds.map((id) => (
            <button
              key={id}
              onClick={() => setActive(id)}
              className={`w-full rounded-md border px-3 py-2 text-left text-sm transition-colors ${
                id === active
                  ? "border-accent/40 bg-accent/10 text-foreground"
                  : "border-transparent text-muted-foreground hover:bg-muted"
              }`}
            >
              <span className="block truncate">{(bundle.sections[id] as Section).title}</span>
              <span className="mt-1 block">
                <StatusPill status={state[id]?.status ?? "pending"} />
              </span>
            </button>
          ))}
        </nav>

        <div className="space-y-6">
          <article className="rounded-lg border border-border bg-card p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-semibold">{section.title}</h2>
              <StatusPill status={current.status} />
            </div>

            <p className="mt-4 whitespace-pre-wrap text-[15px] leading-relaxed">
              {parts.map((p: string, i: number) =>
                p.startsWith("[E:") ? (
                  <button
                    key={i}
                    onClick={() =>
                      setOpenEvidence(
                        (p.replace(/[[\]]/g, "").split(",")[0] ?? "").replace("E:", "").trim(),
                      )
                    }
                    className="mx-0.5 rounded bg-accent/12 px-1 py-0.5 align-baseline font-mono text-[11px] text-accent hover:bg-accent/20"
                  >
                    {p}
                  </button>
                ) : (
                  <span key={i}>{p}</span>
                ),
              )}
            </p>

            {section.findings.length > 0 && (
              <ul className="mt-5 space-y-1.5">
                {section.findings.map((f: Finding, i: number) => (
                  <li
                    key={i}
                    className={`rounded-md border px-3 py-2 text-xs ${
                      f.level === "error"
                        ? "border-destructive/30 bg-destructive/8 text-destructive"
                        : "border-border bg-muted/50 text-muted-foreground"
                    }`}
                  >
                    <span className="font-medium">{f.type}</span>
                    {f.detail ? `: ${f.detail}` : ""}
                  </li>
                ))}
              </ul>
            )}

            <div className="mt-6 flex flex-wrap items-center gap-2 border-t border-border pt-5">
              <button
                onClick={() => setStatus("approved")}
                className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Approve section
              </button>
              <button
                onClick={() => setStatus("flagged")}
                className="rounded-md border border-destructive/40 px-3 py-1.5 text-sm font-medium text-destructive hover:bg-destructive/8"
              >
                Flag for rework
              </button>
              <input
                value={current.comment}
                onChange={(e) =>
                  setState((s) => ({
                    ...s,
                    [active]: { ...(s[active] as { status: string; comment: string }), comment: e.target.value },
                  }))
                }
                placeholder="Reviewer comment"
                className="min-w-[200px] flex-1 rounded-md border border-input bg-background px-3 py-1.5 text-sm outline-none focus:border-accent"
              />
            </div>
            <p className="mt-2 text-[11px] text-muted-foreground">
              Prototype: decisions are held in the browser. The authoritative gate is
              <code className="mx-1">python -m safety_reporting.review</code>, which writes reviewer, comment
              and status back into the report bundle.
            </p>
          </article>

          <section className="rounded-lg border border-border bg-card p-6">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Evidence used by this section
            </h3>
            <div className="mt-4 space-y-3">
              {section.evidence_ids.map((id: string) => {
                const item = evidenceById[id] as Evidence;
                const open = openEvidence === id;
                return (
                  <div key={id} className="rounded-md border border-border">
                    <button
                      onClick={() => setOpenEvidence(open ? null : id)}
                      className="flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left"
                    >
                      <span className="text-sm">
                        <code className="font-mono text-xs text-accent">[E:{id}]</code>{" "}
                        <span className="text-foreground">{item.title}</span>
                      </span>
                      <span className="text-xs text-muted-foreground">{open ? "hide" : "show"}</span>
                    </button>
                    {open && (
                      <div className="space-y-3 border-t border-border px-4 py-3">
                        <p className="text-xs text-muted-foreground">
                          <span className="font-medium text-foreground">Computed by:</span> {item.method}
                        </p>
                        <EvidenceValue item={item} />
                        {item.notes.map((n) => (
                          <p key={n} className="text-xs text-muted-foreground">
                            Note: {n}
                          </p>
                        ))}
                        {Object.keys(item.trace).length > 0 && (
                          <p className="text-xs text-muted-foreground">
                            <span className="font-medium text-foreground">Traced case IDs</span> (
                            {Object.keys(item.trace).length} group
                            {Object.keys(item.trace).length > 1 ? "s" : ""}):{" "}
                            <code className="text-[11px]">
                              {Object.entries(item.trace)
                                .slice(0, 2)
                                .map(([k, v]) => `${k}: ${v.slice(0, 5).join(", ")}…`)
                                .join(" | ")}
                            </code>
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
              {section.evidence_ids.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No evidence is available for this section — the section text says so rather than filling
                  the gap.
                </p>
              )}
            </div>
          </section>

          <section className="rounded-lg border border-border bg-card p-6">
            <button
              onClick={() => setShowPacket((v) => !v)}
              className="text-sm font-semibold uppercase tracking-wide text-muted-foreground hover:text-foreground"
            >
              {showPacket ? "Hide" : "Show"} the exact context packet sent to the model
            </button>
            {showPacket && (
              <div className="mt-4 space-y-4">
                <div>
                  <p className="mb-1 text-xs font-medium text-muted-foreground">System instruction</p>
                  <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-muted/40 p-3 text-[11px] leading-relaxed">
                    {section.packet.system}
                  </pre>
                </div>
                <div>
                  <p className="mb-1 text-xs font-medium text-muted-foreground">
                    Assembled user message (scoped evidence only — never the raw CSV)
                  </p>
                  <pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-muted/40 p-3 text-[11px] leading-relaxed">
                    {section.packet.user}
                  </pre>
                </div>
              </div>
            )}
          </section>

          <section className="rounded-lg border border-border bg-card p-6">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Provenance
            </h3>
            <dl className="mt-3 grid gap-x-8 gap-y-1.5 text-xs sm:grid-cols-2">
              {Object.entries({
                ...bundle.provenance.dataset,
                spec_sha256: bundle.provenance.spec_sha256.slice(0, 16),
                model: bundle.provenance.model,
                generated: bundle.provenance.generated_at,
                pipeline: bundle.provenance.pipeline_version,
              }).map(([k, v]) => (
                <div key={k} className="flex justify-between gap-4 border-b border-border/60 py-1">
                  <dt className="text-muted-foreground">{k.replace(/_/g, " ")}</dt>
                  <dd className="truncate font-mono text-[11px]">{String(v)}</dd>
                </div>
              ))}
            </dl>
          </section>
        </div>
      </div>
    </main>
  );
}
