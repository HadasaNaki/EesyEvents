/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        burgundy: {
          DEFAULT: '#800020',
          dark: '#4a0012',
          light: '#a31538',
        },
        beige: {
          DEFAULT: '#E8D7C1',
          light: '#f5efe6',
          dark: '#d4c5b0',
        },
        gold: {
          DEFAULT: '#D4AF37',
        }
      },
      fontFamily: {
        sans: ['Rubik', 'sans-serif'],
        round: ['Varela Round', 'sans-serif'],
      }
    },
  },
  plugins: [],
}