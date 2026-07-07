import { ScrollReveal } from "../components/ScrollReveal";
import { ablationResult } from "../data/ablation";

export function Benchmark() {
  return (
    <section className="mx-auto max-w-5xl px-6 py-20">
      <ScrollReveal>
        <h2 className="section-heading text-3xl text-text">Benchmark</h2>
        <p className="mt-3 max-w-2xl text-muted">
          Accuracy is measured against a subset of the BIRD dev set, a public text-to-SQL benchmark built from
          real databases with human-written gold queries. Execution accuracy runs the generated SQL and the
          gold SQL against the same database and compares the row sets, not the query text.
        </p>
      </ScrollReveal>

      <ScrollReveal delay={0.1}>
        {ablationResult.available ? (
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-hairline bg-surface p-6">
              <p className="text-sm text-muted">Correction disabled</p>
              <p className="mt-2 font-mono text-3xl text-text">
                {((ablationResult.correctionDisabledAccuracy ?? 0) * 100).toFixed(1)}%
              </p>
            </div>
            <div className="rounded-xl border border-hairline bg-surface p-6">
              <p className="text-sm text-muted">Correction enabled</p>
              <p className="mt-2 font-mono text-3xl text-signal-cool">
                {((ablationResult.correctionEnabledAccuracy ?? 0) * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        ) : (
          <div className="mt-8 rounded-xl border border-hairline bg-surface p-6">
            <p className="text-sm text-muted">
              The ablation run for this deployment has not completed yet. The harness itself is finished and
              runs against real BIRD databases; the results table appears here once a run has been recorded.
            </p>
          </div>
        )}
      </ScrollReveal>

      <ScrollReveal delay={0.18}>
        <p className="mt-6 max-w-2xl text-sm text-muted">
          Execution accuracy undercounts correct answers in one specific way: a query that answers the
          question correctly but returns columns in a different order, or with different aliases, fails a
          strict set comparison even though a person reading both results would call them the same answer.
          Practical accuracy, measured with a person reviewing the mismatches, runs higher than this number.
        </p>
      </ScrollReveal>
    </section>
  );
}
