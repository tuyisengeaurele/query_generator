import { useState } from "react";
import { Badge } from "@query-generator/ui";
import type { Attempt } from "../api";

interface CorrectionTraceProps {
  attempts: Attempt[];
}

export function CorrectionTrace({ attempts }: CorrectionTraceProps) {
  const [expanded, setExpanded] = useState(false);

  if (attempts.length <= 1) {
    return null;
  }

  return (
    <div className="rounded-lg border border-hairline bg-surface p-4">
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="flex w-full items-center justify-between text-left text-sm text-muted hover:text-text"
      >
        <span>
          Self-correction ran {attempts.length} attempt{attempts.length === 1 ? "" : "s"} before finishing
        </span>
        <span>{expanded ? "Hide" : "Show"}</span>
      </button>
      {expanded && (
        <ol className="mt-3 flex flex-col gap-3">
          {attempts.map((attempt, index) => (
            <li key={index} className="rounded-md border border-hairline bg-ink p-3">
              <div className="mb-1 flex items-center gap-2">
                <Badge tone={attempt.success ? "ok" : "err"}>
                  attempt {index + 1}: {attempt.success ? "succeeded" : "failed"}
                </Badge>
              </div>
              <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs text-muted">{attempt.sql}</pre>
              {attempt.error && <p className="mt-1 font-mono text-xs text-err">{attempt.error}</p>}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
