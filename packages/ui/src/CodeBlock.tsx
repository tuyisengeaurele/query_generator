interface CodeBlockProps {
  code: string;
  label?: string;
}

// SQL, schema, and data always render in mono, per the design rule that
// separates the human question side from the machine SQL side.
export function CodeBlock({ code, label }: CodeBlockProps) {
  return (
    <div className="qg-code-block">
      {label ? <div className="qg-code-block-label">{label}</div> : null}
      <pre className="qg-code-block-pre">
        <code>{code}</code>
      </pre>
    </div>
  );
}
