import type { HTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

interface PanelProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  children: ReactNode;
}

export function Panel({ title, className, children, ...rest }: PanelProps) {
  return (
    <div className={clsx("qg-panel", className)} {...rest}>
      {title ? <h3 className="qg-panel-title">{title}</h3> : null}
      {children}
    </div>
  );
}
