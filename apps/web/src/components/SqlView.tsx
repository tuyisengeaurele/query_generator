import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { colors } from "@query-generator/design-tokens";
import { Panel } from "@query-generator/ui";

const highlightTheme = {
  'code[class*="language-"]': { color: colors.text, fontFamily: "JetBrains Mono, monospace" },
  'pre[class*="language-"]': { background: colors.ink, border: `1px solid ${colors.hairline}` },
  comment: { color: colors.muted },
  keyword: { color: colors.signalWarm },
  function: { color: colors.signalCool },
  string: { color: colors.ok },
  number: { color: colors.signalCool },
  operator: { color: colors.muted },
};

interface SqlViewProps {
  sql: string;
}

export function SqlView({ sql }: SqlViewProps) {
  return (
    <Panel title="Generated SQL">
      <SyntaxHighlighter language="sql" style={highlightTheme} customStyle={{ borderRadius: 8, fontSize: "0.875rem" }}>
        {sql}
      </SyntaxHighlighter>
    </Panel>
  );
}
