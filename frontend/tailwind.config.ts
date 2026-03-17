import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Sci-Fi Dashboard Palette
        brand: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
        neon: {
          cyan: "#00e5ff",
          blue: "#00b2ff",
          pink: "#ff00e5",
          red: "#ff3d3d",
        },
        chess: {
          light: "rgba(255, 255, 255, 0.05)",
          dark: "rgba(0, 0, 0, 0.2)",
          highlight: "rgba(0, 229, 255, 0.3)",
          "last-move": "rgba(0, 229, 255, 0.2)",
          check: "rgba(255, 61, 61, 0.4)",
        },
        surface: {
          DEFAULT: "#020617",
          card: "rgba(15, 23, 42, 0.6)",
          border: "rgba(0, 229, 255, 0.1)",
          hover: "rgba(0, 229, 255, 0.05)",
        },
      },
      fontFamily: {
        sans: ["Rajdhani", "Inter", "system-ui", "sans-serif"],
        tech: ["Orbitron", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-out",
        "slide-up": "slideUp 0.5s ease-out",
        "pulse-cyan": "pulseCyan 2s infinite",
        "glow-slow": "glow 4s ease-in-out infinite",
        thinking: "thinking 1.5s ease-in-out infinite",
        "shimmer": "shimmer 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        pulseCyan: {
          "0%, 100%": { boxShadow: "0 0 5px rgba(0, 229, 255, 0.2), inset 0 0 5px rgba(0, 229, 255, 0.1)" },
          "50%": { boxShadow: "0 0 15px rgba(0, 229, 255, 0.4), inset 0 0 10px rgba(0, 229, 255, 0.2)" },
        },
        glow: {
          "0%, 100%": { opacity: "0.8" },
          "50%": { opacity: "1" },
        },
        thinking: {
          "0%, 100%": { opacity: "0.4", transform: "scale(0.98)" },
          "50%": { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      boxShadow: {
        card: "0 8px 32px 0 rgba(0, 0, 0, 0.8)",
        neon: "0 0 15px rgba(0, 229, 255, 0.4)",
        "neon-strong": "0 0 25px rgba(0, 229, 255, 0.6)",
        glass: "inset 0 0 20px 0 rgba(255, 255, 255, 0.05)",
      },
    },
  },
  plugins: [],
} satisfies Config;
