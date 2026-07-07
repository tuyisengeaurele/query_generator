import { Panel } from "@query-generator/ui";

interface ResultGridProps {
  columns: string[] | null;
  rows: Record<string, unknown>[] | null;
  error: string | null;
}

export function ResultGrid({ columns, rows, error }: ResultGridProps) {
  if (error) {
    return (
      <Panel title="Result">
        <p className="rounded-lg border border-err bg-surface p-4 font-mono text-sm text-err">{error}</p>
      </Panel>
    );
  }

  if (!columns || !rows) {
    return null;
  }

  if (rows.length === 0) {
    return (
      <Panel title="Result">
        <p className="text-sm text-muted">Query ran successfully and returned no rows.</p>
      </Panel>
    );
  }

  return (
    <Panel title={`Result (${rows.length} row${rows.length === 1 ? "" : "s"})`}>
      <div className="overflow-x-auto rounded-lg border border-hairline">
        <table className="w-full border-collapse font-mono text-sm">
          <thead>
            <tr className="border-b border-hairline bg-raised text-signal-cool">
              {columns.map((column) => (
                <th key={column} className="px-3 py-2 text-left font-medium">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index} className="border-b border-hairline last:border-0">
                {columns.map((column) => (
                  <td key={column} className="px-3 py-2 text-text">
                    {String(row[column] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
