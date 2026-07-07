import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QueryConsole } from "../QueryConsole";

describe("QueryConsole", () => {
  it("calls onSubmit with the typed question", () => {
    const onSubmit = vi.fn();
    render(<QueryConsole onSubmit={onSubmit} isLoading={false} />);

    const textarea = screen.getByLabelText(/ask a question/i);
    fireEvent.change(textarea, { target: { value: "How many members are there?" } });
    fireEvent.click(screen.getByRole("button", { name: /run question/i }));

    expect(onSubmit).toHaveBeenCalledWith("How many members are there?");
  });

  it("fills the textarea when a starter chip is clicked", () => {
    render(<QueryConsole onSubmit={vi.fn()} isLoading={false} />);
    fireEvent.click(screen.getByText(/top 5 products/i));
    expect(screen.getByLabelText(/ask a question/i)).toHaveValue(
      "What are the top 5 products by total quantity sold?"
    );
  });

  it("disables the submit button while loading", () => {
    render(<QueryConsole onSubmit={vi.fn()} isLoading={true} />);
    expect(screen.getByRole("button", { name: /generating/i })).toBeDisabled();
  });
});
