/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#4F46E5",
          hover: "#4338CA",
          active: "#3730A3",
          focus: "#6366F1",
        },
        selection: "#2563EB",
        canvas: "#F8FAFC",
        module: "#F1F5F9",
        line: "#E2E8F0",
        authentic: {
          DEFAULT: "#10B981",
          bg: "#ECFDF5",
          text: "#059669",
          border: "#A7F3D0",
        },
        manipulated: {
          DEFAULT: "#EF4444",
          bg: "#FEF2F2",
          text: "#DC2626",
          border: "#FECACA",
        },
        indeterminate: {
          DEFAULT: "#F59E0B",
          bg: "#FFFBEB",
          text: "#D97706",
          border: "#FDE68A",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "headline-xl": ["32px", { lineHeight: "40px", fontWeight: "700", letterSpacing: "-0.02em" }],
        "headline-lg": ["24px", { lineHeight: "32px", fontWeight: "600", letterSpacing: "-0.015em" }],
        "headline-md": ["18px", { lineHeight: "26px", fontWeight: "600", letterSpacing: "-0.01em" }],
        "body-md": ["14px", { lineHeight: "20px" }],
        "body-sm": ["12px", { lineHeight: "18px" }],
        "mono-md": ["12px", { lineHeight: "16px", fontWeight: "500" }],
        caption: ["11px", { lineHeight: "14px", fontWeight: "700", letterSpacing: "0.06em" }],
      },
      boxShadow: {
        l1: "0 1px 3px rgba(15,23,42,0.04), 0 1px 2px rgba(15,23,42,0.02)",
        l2: "0 4px 6px -1px rgba(15,23,42,0.06), 0 2px 4px -2px rgba(15,23,42,0.04)",
        l3: "0 12px 24px -4px rgba(15,23,42,0.08), 0 4px 8px -2px rgba(15,23,42,0.03)",
      },
      borderRadius: {
        control: "4px",
        card: "8px",
      },
    },
  },
  plugins: [],
};
