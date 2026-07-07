import { ScrollReveal } from "../components/ScrollReveal";

export function Architecture() {
  return (
    <section className="mx-auto max-w-5xl px-6 py-20">
      <ScrollReveal>
        <h2 className="section-heading text-3xl text-text">Architecture</h2>
        <p className="mt-3 max-w-2xl text-muted">
          A FastAPI service runs the pipeline against SQLAlchemy, so the same code path works against SQLite
          and Postgres. Three model provider adapters (Ollama, Groq, Anthropic) sit behind one interface,
          swappable by an environment variable. Every generated statement passes through a SQL parser before
          it touches a database connection, and that connection carries read-only grants as a second line of
          defense.
        </p>
      </ScrollReveal>
      <ScrollReveal delay={0.1}>
        <div className="mt-10 grid grid-cols-1 gap-4 font-mono text-sm sm:grid-cols-3">
          <div className="rounded-lg border border-hairline bg-surface p-4">
            <p className="text-signal-cool">apps/api</p>
            <p className="mt-1 text-muted">Pipeline, guardrails, execution, correction loop</p>
          </div>
          <div className="rounded-lg border border-hairline bg-surface p-4">
            <p className="text-signal-cool">apps/web</p>
            <p className="mt-1 text-muted">Demo console against a live Postgres schema</p>
          </div>
          <div className="rounded-lg border border-hairline bg-surface p-4">
            <p className="text-signal-cool">eval/</p>
            <p className="mt-1 text-muted">BIRD subset runner, scorer, ablation report</p>
          </div>
        </div>
      </ScrollReveal>
    </section>
  );
}
