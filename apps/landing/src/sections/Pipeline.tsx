import { ScrollReveal } from "../components/ScrollReveal";

const STAGES = [
  "Schema introspection",
  "Schema linking",
  "Few-shot retrieval",
  "Prompt assembly",
  "Generation",
  "Guardrails",
  "Execution",
  "Self-correction",
  "Response",
];

export function Pipeline() {
  return (
    <section className="mx-auto max-w-5xl px-6 py-20">
      <ScrollReveal>
        <h2 className="section-heading text-3xl text-text">Nine stages, one pipeline</h2>
        <p className="mt-3 max-w-2xl text-muted">
          Each stage has one job. Schema linking does not generate SQL. Guardrails do not decide which tables
          matter. Splitting the work this way is what makes the self-correction loop possible: when execution
          fails, only the generation stage needs to run again, with the error attached.
        </p>
      </ScrollReveal>
      <div className="mt-10 flex flex-wrap gap-3">
        {STAGES.map((stage, index) => (
          <ScrollReveal key={stage} delay={index * 0.04}>
            <div className="flex items-center gap-2 rounded-full border border-hairline bg-surface px-4 py-2 font-mono text-sm text-text">
              <span className="text-signal-warm">{index + 1}</span>
              {stage}
            </div>
          </ScrollReveal>
        ))}
      </div>
    </section>
  );
}
