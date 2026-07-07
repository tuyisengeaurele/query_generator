import type { Config } from "tailwindcss";
import { colors, fonts } from "../../packages/design-tokens/src";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: colors.ink,
        surface: colors.surface,
        raised: colors.raised,
        hairline: colors.hairline,
        text: colors.text,
        muted: colors.muted,
        "signal-warm": colors.signalWarm,
        "signal-cool": colors.signalCool,
        ok: colors.ok,
        err: colors.err,
      },
      fontFamily: {
        display: [fonts.display],
        body: [fonts.body],
        mono: [fonts.mono],
      },
    },
  },
  plugins: [],
} satisfies Config;
