import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      keyframes: {
        "border-pulse": {
          "0%, 100%": {
            borderColor: "#2a3142",
            boxShadow: "0 0 0 0 rgba(124, 106, 247, 0)",
          },
          "50%": {
            borderColor: "#7c6af7",
            boxShadow: "0 0 0 1px rgba(124, 106, 247, 0.35)",
          },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        "border-pulse": "border-pulse 2s ease-in-out infinite",
        shimmer: "shimmer 1.8s ease-in-out infinite",
      },
      colors: {
        background: "#000000",
        surface: "#12151c",
        border: "#2a3142",
        muted: "#8b95a8",
        accent: "#7c6af7",
        pass: "#3dd68c",
        fail: "#f07178",
        warn: "#ffb454",
      },
    },
  },
  plugins: [],
};

export default config;
