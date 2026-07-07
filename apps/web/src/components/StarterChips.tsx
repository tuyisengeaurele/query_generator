const STARTER_QUESTIONS = [
  "How many members does each cooperative have?",
  "What are the top 5 products by total quantity sold?",
  "Which orders have not been fully paid?",
  "What is the total revenue per cooperative this year?",
  "Show the 10 most recent orders with the member name.",
];

interface StarterChipsProps {
  onSelect: (question: string) => void;
  disabled: boolean;
}

export function StarterChips({ onSelect, disabled }: StarterChipsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {STARTER_QUESTIONS.map((question) => (
        <button
          key={question}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(question)}
          className="rounded-full border border-hairline px-3 py-1.5 text-sm text-muted transition-colors hover:border-signal-warm hover:text-text disabled:cursor-not-allowed disabled:opacity-50"
        >
          {question}
        </button>
      ))}
    </div>
  );
}
