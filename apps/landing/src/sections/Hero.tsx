import { motion, useReducedMotion } from "framer-motion";

const QUESTION = "How many members does each cooperative have?";
const SCHEMA_TABLES = ["cooperatives", "members"];
const SQL_LINES = [
  "SELECT c.name, COUNT(m.id) AS member_count",
  "FROM cooperatives c",
  "JOIN members m ON m.cooperative_id = c.id",
  "GROUP BY c.name",
  "ORDER BY member_count DESC",
];
const RESULT_ROWS = [
  { name: "Kigali Growers", member_count: 3 },
  { name: "Musanze Highlands", member_count: 2 },
  { name: "Huye Valley Farmers", member_count: 2 },
];

const EASE = [0.16, 1, 0.3, 1] as const;

export function Hero() {
  const reducedMotion = useReducedMotion();
  const delayScale = reducedMotion ? 0 : 1;

  return (
    <section className="mx-auto flex max-w-5xl flex-col gap-10 px-6 pb-20 pt-24">
      <div className="flex flex-col gap-5">
        <span className="w-fit rounded-full border border-hairline px-3 py-1 text-xs uppercase tracking-widest text-signal-cool">
          Natural language to SQL
        </span>
        <h1 className="section-heading text-4xl leading-tight text-text sm:text-5xl">
          A question becomes a query.
          <br />
          Every time, safely.
        </h1>
        <p className="max-w-2xl text-lg text-muted">
          Type a question in plain English. The pipeline links it to the right tables, writes SQL, guards it
          against anything destructive, and runs it against a real database.
        </p>
      </div>

      <div className="rounded-xl border border-hairline bg-surface p-6">
        <motion.p
          initial={reducedMotion ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: EASE }}
          className="section-heading text-xl text-signal-warm"
        >
          "{QUESTION}"
        </motion.p>

        <div className="mt-5 flex flex-wrap gap-2">
          {SCHEMA_TABLES.map((table, index) => (
            <motion.span
              key={table}
              initial={reducedMotion ? false : { opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.35, ease: EASE, delay: (0.5 + index * 0.15) * delayScale }}
              className="rounded-md border border-signal-cool px-2 py-1 font-mono text-xs text-signal-cool"
            >
              {table}
            </motion.span>
          ))}
        </div>

        <motion.pre
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 1.0 * delayScale }}
          className="mt-5 overflow-x-auto rounded-lg border border-hairline bg-ink p-4 font-mono text-sm text-text"
        >
          {SQL_LINES.map((line, index) => (
            <motion.div
              key={line}
              initial={reducedMotion ? false : { opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, ease: EASE, delay: (1.1 + index * 0.12) * delayScale }}
            >
              {line}
            </motion.div>
          ))}
        </motion.pre>

        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: EASE, delay: 2.0 * delayScale }}
          className="mt-5 overflow-hidden rounded-lg border border-hairline"
        >
          <table className="w-full border-collapse font-mono text-sm">
            <thead>
              <tr className="border-b border-hairline bg-raised text-signal-cool">
                <th className="px-3 py-2 text-left font-medium">name</th>
                <th className="px-3 py-2 text-left font-medium">member_count</th>
              </tr>
            </thead>
            <tbody>
              {RESULT_ROWS.map((row) => (
                <tr key={row.name} className="border-b border-hairline last:border-0">
                  <td className="px-3 py-2">{row.name}</td>
                  <td className="px-3 py-2">{row.member_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      </div>
    </section>
  );
}
