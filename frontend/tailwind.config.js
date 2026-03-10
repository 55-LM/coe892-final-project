/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Supply Mono', 'Consolas', 'Monaco', 'monospace'],
        mono: ['Supply Mono', 'Consolas', 'Monaco', 'monospace'],
        header: ['Supply Mono', 'Consolas', 'monospace'],
        title: ['Supply Mono', 'Consolas', 'monospace'],
      },
      colors: {
        primary: { 500: '#71717a', 600: '#52525b', 700: '#3f3f46' },
      },
    },
  },
  plugins: [],
}
