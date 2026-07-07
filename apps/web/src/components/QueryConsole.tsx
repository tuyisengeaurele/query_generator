import { FormEvent, useState } from "react";
import { Button } from "@query-generator/ui";
import { StarterChips } from "./StarterChips";

interface QueryConsoleProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

export function QueryConsole({ onSubmit, isLoading }: QueryConsoleProps) {
  const [question, setQuestion] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (trimmed && !isLoading) {
      onSubmit(trimmed);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <label htmlFor="question-input" className="text-sm text-muted">
          Ask a question about the cooperative sales data
        </label>
        <textarea
          id="question-input"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="How many members does each cooperative have?"
          rows={3}
          className="w-full resize-none rounded-lg border border-hairline bg-surface px-4 py-3 font-display text-lg text-text placeholder:text-muted focus:border-signal-warm focus:outline-none"
        />
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted">Read-only. Every query runs through the safety guardrails.</span>
          <Button type="submit" disabled={isLoading || !question.trim()}>
            {isLoading ? "Generating..." : "Run question"}
          </Button>
        </div>
      </form>
      <StarterChips onSelect={setQuestion} disabled={isLoading} />
    </div>
  );
}
