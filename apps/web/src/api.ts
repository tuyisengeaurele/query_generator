export interface Attempt {
  sql: string;
  success: boolean;
  error: string | null;
  timestamp: string;
}

export interface QueryResponse {
  sql: string;
  success: boolean;
  columns: string[] | null;
  rows: Record<string, unknown>[] | null;
  error: string | null;
  attempts: Attempt[];
  model: string;
  attempt_count: number;
  latency_ms: number;
}

export interface TableSchema {
  name: string;
  columns: { name: string; type: string; primary_key: boolean }[];
}

export async function runQuery(question: string): Promise<QueryResponse> {
  const response = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error(`request failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchSchema(): Promise<TableSchema[]> {
  const response = await fetch("/api/schema");
  if (!response.ok) {
    throw new Error(`request failed with status ${response.status}`);
  }
  return response.json();
}
