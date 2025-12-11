/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./view/**/*.{ts,tsx}",
    "./index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0b5ac1',
        secondary: '#f1b100',
        success: '#02a63e',
        danger: '#bf0f0c',
        warning: '#e32600',
      },
      fontFamily: {
        arabic: ['Tajawal', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
