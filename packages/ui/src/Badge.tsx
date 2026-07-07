import type { ReactNode } from "react";
import clsx from "clsx";

type BadgeTone = "warm" | "cool" | "ok" | "err" | "neutral";

interface BadgeProps {
  tone?: BadgeTone;
  children: ReactNode;
  className?: string;
}

const toneClass: Record<BadgeTone, string> = {
  warm: "qg-badge-warm",
  cool: "qg-badge-cool",
  ok: "qg-badge-ok",
  err: "qg-badge-err",
  neutral: "qg-badge-neutral",
};

export function Badge({ tone = "neutral", children, className }: BadgeProps) {
  return <span className={clsx("qg-badge", toneClass[tone], className)}>{children}</span>;
}
