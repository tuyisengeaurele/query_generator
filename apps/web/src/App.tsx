import { useState } from "react";
import { Badge, Card } from "@query-generator/ui";
import { runQuery, type QueryResponse } from "./api";
import { QueryConsole } from "./components/QueryConsole";
import { SqlView } from "./components/SqlView";
import { ResultGrid } from "./components/ResultGrid";
import { CorrectionTrace } from "./components/CorrectionTrace";
import { SchemaBrowser } from "./components/SchemaBrowser";

export default function App() {
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [requestError, setRequestError] = useState<string | null>(null);

  async function handleSubmit(question: string) {
    setIsLoading(true);
    setRequestError(null);
    try {
      const response = await runQuery(question);
      setResult(response);
    } catch (err) {
      setRequestError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-ink px-6 py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="flex flex-col gap-1">
          <h1 className="font-display text-3xl text-text">Query generator demo</h1>
          <p className="text-sm text-muted">
            Ask a question about the cooperative sales data. Every query is generated, guarded, and run read-only.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[2fr_1fr]">
          <div className="flex flex-col gap-6">
            <Card>
              <QueryConsole onSubmit={handleSubmit} isLoading={isLoading} />
            </Card>

            {requestError && (
              <Card>
                <p className="text-sm text-err">{requestError}</p>
              </Card>
            )}

            {result && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone="cool">model: {result.model}</Badge>
                  <Badge tone={result.success ? "ok" : "err"}>{result.success ? "success" : "failed"}</Badge>
                  <Badge tone="neutral">{result.latency_ms}ms</Badge>
                  <Badge tone="neutral">
                    {result.attempt_count} attempt{result.attempt_count === 1 ? "" : "s"}
                  </Badge>
                </div>

                <Card>
                  <SqlView sql={result.sql} />
                </Card>

                <CorrectionTrace attempts={result.attempts} />

                <Card>
                  <ResultGrid columns={result.columns} rows={result.rows} error={result.success ? null : result.error} />
                </Card>
              </div>
            )}
          </div>

          <div>
            <Card>
              <SchemaBrowser />
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
