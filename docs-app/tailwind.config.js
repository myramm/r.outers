/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#0a0d14',
          card: '#101524',
          border: '#1f293d',
          hover: '#182035',
          cyan: '#00F2FE',
          pink: '#FF2A85',
          purple: '#9B51E0',
          yellow: '#FFD700',
          green: '#00E676',
          text: '#f3f4f6',
          muted: '#9ca3af'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'neon-cyan': '0 0 20px -3px rgba(0, 242, 254, 0.3)',
        'neon-pink': '0 0 20px -3px rgba(255, 42, 133, 0.3)',
        'neon-purple': '0 0 20px -3px rgba(155, 81, 224, 0.3)',
      }
    },
  },
  plugins: [],
}
