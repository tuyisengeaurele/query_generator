// Fixed palette. No purple, violet, or indigo anywhere, including gradients and shadows.
export const colors = {
  ink: "#0C0E10",
  surface: "#15181B",
  raised: "#1D2125",
  hairline: "#2A2F34",
  text: "#ECEBE7",
  muted: "#8A9199",
  signalWarm: "#E8A13C",
  signalCool: "#57C7B4",
  ok: "#5FB878",
  err: "#E0575B",
} as const;

export type ColorToken = keyof typeof colors;
