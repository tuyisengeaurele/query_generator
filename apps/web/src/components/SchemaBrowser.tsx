import { useEffect, useState } from "react";
import { Panel } from "@query-generator/ui";
import { fetchSchema, type TableSchema } from "../api";

export function SchemaBrowser() {
  const [tables, setTables] = useState<TableSchema[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSchema()
      .then(setTables)
      .catch(() => setError("Could not load the schema. Is the API running?"));
  }, []);

  return (
    <Panel title="Schema">
      {error && <p className="text-sm text-err">{error}</p>}
      {!error && !tables && <p className="text-sm text-muted">Loading schema...</p>}
      {tables && (
        <div className="flex flex-col gap-3">
          {tables.map((table) => (
            <details key={table.name} className="rounded-md border border-hairline bg-surface p-3">
              <summary className="cursor-pointer font-mono text-sm text-signal-cool">{table.name}</summary>
              <ul className="mt-2 flex flex-col gap-1 font-mono text-xs text-muted">
                {table.columns.map((column) => (
                  <li key={column.name}>
                    {column.name}
                    {column.primary_key ? " (pk)" : ""} <span className="text-hairline">{column.type}</span>
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </div>
      )}
    </Panel>
  );
}
