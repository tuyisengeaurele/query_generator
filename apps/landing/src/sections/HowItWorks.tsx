import { ScrollReveal } from "../components/ScrollReveal";

const STEPS = [
  {
    title: "Ask in plain English",
    body: "Type a question the way you would ask a colleague. No SQL syntax, no table names required.",
  },
  {
    title: "The pipeline links it to your schema",
    body: "Schema linking picks the tables and columns the question actually needs, so the model prompt stays focused instead of dumping the whole database.",
  },
  {
    title: "SQL is generated, guarded, and run",
    body: "The model writes SQL. A parser rejects anything that is not a single read-only SELECT before it ever reaches the database.",
  },
  {
    title: "Failures trigger a rewrite, not a dead end",
    body: "If the query errors or comes back empty when it shouldn't, the pipeline feeds the error back to the model and tries again, up to three times.",
  },
];

export function HowItWorks() {
  return (
    <section className="mx-auto max-w-5xl px-6 py-20">
      <ScrollReveal>
        <h2 className="section-heading text-3xl text-text">How it works</h2>
      </ScrollReveal>
      <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2">
        {STEPS.map((step, index) => (
          <ScrollReveal key={step.title} delay={index * 0.08}>
            <div className="h-full rounded-xl border border-hairline bg-surface p-6">
              <span className="font-mono text-xs text-signal-cool">{String(index + 1).padStart(2, "0")}</span>
              <h3 className="mt-2 text-lg text-text">{step.title}</h3>
              <p className="mt-2 text-sm text-muted">{step.body}</p>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </section>
  );
}
