/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ivory: "#F8F6F2",
        paper: "#EFEAE4",
        accent: "#C84B2F",
        ink: "#211E1C",
        muted: "#71615A",
        line: "#E6DDD5",
      },
      boxShadow: {
        soft: "0 18px 40px rgba(60, 36, 22, 0.08)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
