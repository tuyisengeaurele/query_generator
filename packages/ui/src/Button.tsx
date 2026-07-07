import type { ButtonHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

type ButtonVariant = "primary" | "secondary" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: ReactNode;
}

const variantClass: Record<ButtonVariant, string> = {
  primary: "qg-button-primary",
  secondary: "qg-button-secondary",
  ghost: "qg-button-ghost",
};

export function Button({ variant = "primary", className, children, ...rest }: ButtonProps) {
  return (
    <button className={clsx("qg-button", variantClass[variant], className)} {...rest}>
      {children}
    </button>
  );
}
