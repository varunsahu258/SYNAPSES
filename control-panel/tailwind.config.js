/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      boxShadow: {
        dashboard: '0 24px 80px rgb(15 23 42 / 12%)',
      },
    },
  },
  plugins: [],
};
