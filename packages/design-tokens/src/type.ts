// The mapping is the rule: natural language renders in the serif, SQL and
// schema always render in mono. Body and UI chrome use the sans family.
export const fonts = {
  display: '"Fraunces", "Georgia", serif',
  body: '"Geist Sans", "Inter", system-ui, sans-serif',
  mono: '"JetBrains Mono", "Menlo", monospace',
} as const;

export const fontSizes = {
  xs: "0.75rem",
  sm: "0.875rem",
  base: "1rem",
  lg: "1.125rem",
  xl: "1.5rem",
  "2xl": "2rem",
  "3xl": "2.75rem",
  "4xl": "3.5rem",
} as const;

export const fontWeights = {
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const;
