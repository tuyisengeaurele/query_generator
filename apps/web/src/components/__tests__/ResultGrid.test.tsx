import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResultGrid } from "../ResultGrid";

describe("ResultGrid", () => {
  it("renders an error message when the query failed", () => {
    render(<ResultGrid columns={null} rows={null} error="no such table: memebrs" />);
    expect(screen.getByText(/no such table: memebrs/)).toBeInTheDocument();
  });

  it("renders a table with columns and rows", () => {
    render(
      <ResultGrid
        columns={["id", "full_name"]}
        rows={[{ id: 1, full_name: "Alice Uwase" }]}
        error={null}
      />
    );
    expect(screen.getByText("full_name")).toBeInTheDocument();
    expect(screen.getByText("Alice Uwase")).toBeInTheDocument();
  });

  it("renders an empty state when the query returned no rows", () => {
    render(<ResultGrid columns={["id"]} rows={[]} error={null} />);
    expect(screen.getByText(/returned no rows/i)).toBeInTheDocument();
  });
});
