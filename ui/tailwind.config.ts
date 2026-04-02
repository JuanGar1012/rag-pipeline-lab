import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f4efe8",
        ink: "#18222f",
        coral: "#d8603a",
        teal: "#165d63",
        sand: "#fffaf1"
      },
      boxShadow: {
        panel: "0 20px 60px rgba(24, 34, 47, 0.08)"
      },
      fontFamily: {
        sans: ["Bahnschrift", "Trebuchet MS", "Segoe UI", "sans-serif"]
      }
    }
  },
  plugins: []
} satisfies Config;
