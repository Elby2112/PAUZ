/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#5E8FA8",      // Soft Blue — headers, buttons
        secondary: "#E6E8EA",    // Warm Grey — cards, containers
        accent: "#B49FCC",       // Muted Lavender — highlights
        textColor: "#2E2E35",    // Dark Charcoal — main text
        background: "#F4F6F7",   // Off-White — backgrounds
      },
      fontFamily: {
        heading: ['var(--font-heading)', 'sans-serif'],
        body: ['var(--font-body)', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
