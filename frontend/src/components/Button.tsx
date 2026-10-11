import type { ButtonHTMLAttributes, ReactNode } from "react";

export function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary"; children: ReactNode }) {
  const look =
    variant === "primary"
      ? "bg-[#4F46E5] text-white hover:bg-[#4338CA]"
      : "bg-white text-[#0F172A] border border-[#E2E8F0] hover:bg-slate-50";
  return (
    <button
      type="button"
      className={`inline-flex items-center justify-center rounded-2xl px-5 py-3 text-base font-semibold disabled:opacity-60 ${look} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
