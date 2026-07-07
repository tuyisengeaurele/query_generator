import type { HTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  raised?: boolean;
  children: ReactNode;
}

export function Card({ raised = false, className, children, ...rest }: CardProps) {
  return (
    <div className={clsx("qg-card", raised && "qg-card-raised", className)} {...rest}>
      {children}
    </div>
  );
}
