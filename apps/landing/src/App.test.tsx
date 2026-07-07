import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("landing App", () => {
  it("renders the hero headline and no external repository links", () => {
    render(<App />);
    expect(screen.getByText(/a question becomes a query/i)).toBeInTheDocument();

    const links = screen.queryAllByRole("link");
    for (const link of links) {
      const href = link.getAttribute("href") ?? "";
      expect(href).not.toMatch(/github\.com/i);
    }
  });

  it("renders every section heading", () => {
    render(<App />);
    expect(screen.getByText(/how it works/i)).toBeInTheDocument();
    expect(screen.getByText(/nine stages, one pipeline/i)).toBeInTheDocument();
    expect(screen.getByText(/^benchmark$/i)).toBeInTheDocument();
    expect(screen.getByText(/^architecture$/i)).toBeInTheDocument();
  });
});
