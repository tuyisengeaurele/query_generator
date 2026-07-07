import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CorrectionTrace } from "../CorrectionTrace";

describe("CorrectionTrace", () => {
  it("renders nothing when there was only one attempt", () => {
    const { container } = render(
      <CorrectionTrace attempts={[{ sql: "SELECT 1", success: true, error: null, timestamp: "now" }]} />
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("shows the attempt count and expands to reveal each attempt", () => {
    render(
      <CorrectionTrace
        attempts={[
          { sql: "SELECT * FROM memebrs", success: false, error: "no such table: memebrs", timestamp: "t1" },
          { sql: "SELECT * FROM members", success: true, error: null, timestamp: "t2" },
        ]}
      />
    );

    expect(screen.getByText(/2 attempts/i)).toBeInTheDocument();
    fireEvent.click(screen.getByText(/show/i));
    expect(screen.getByText("SELECT * FROM memebrs")).toBeInTheDocument();
    expect(screen.getByText(/no such table: memebrs/)).toBeInTheDocument();
  });
});
