/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      // colors: {
      //   primary: {
      //     // DEFAULT: '#4F46E5', // Indigo for buttons
      //     DEFAULT: '#000000', // Indigo for buttons
      //   },
      // },
    },
  },
  plugins: [],
}