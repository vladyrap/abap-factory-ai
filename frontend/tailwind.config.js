/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Paleta Visual Studio Code (Dark+)
        vs: {
          editor: '#1e1e1e',
          sidebar: '#252526',
          activity: '#333333',
          input: '#3c3c3c',
          widget: '#252526',
          border: '#2d2d2d',
          border2: '#454545',
          tabactive: '#1e1e1e',
          tabinactive: '#2d2d2d',
          statusbar: '#007acc',
          accent: '#007acc',
          button: '#0e639c',
          buttonHover: '#1177bb',
          selection: '#094771',
          hover: '#2a2d2e',
          link: '#3794ff',
          text: '#cccccc',
          muted: '#858585',
          green: '#4ec9b0',
          yellow: '#cca700',
          red: '#f14c4c',
          purple: '#c586c0',
          orange: '#ce9178',
        },
        // 'ink' remapeado a los grises de VS Code (cascada a todas las pantallas)
        ink: {
          50: '#ffffff', 100: '#e8e8e8', 200: '#cccccc', 300: '#bbbbbb',
          400: '#858585', 500: '#6e6e6e', 600: '#454545', 700: '#3c3c3c',
          800: '#2d2d2d', 900: '#252526', 950: '#1e1e1e',
        },
        // 'brand' y 'neon' remapeados al azul de VS Code
        brand: {
          50: '#e6f1fb', 100: '#cfe6f8', 200: '#9fcdf0', 300: '#5aa6e0',
          400: '#3794ff', 500: '#1177bb', 600: '#0e639c', 700: '#094771',
          800: '#04395e', 900: '#042f4d',
        },
        neon: { 400: '#4fc1ff', 500: '#007acc', 600: '#0e639c' },
        plasma: { 400: '#c586c0', 500: '#b66ab0' },
      },
      fontFamily: {
        sans: ['"Segoe UI"', 'system-ui', 'Roboto', 'sans-serif'],
        display: ['"Segoe UI"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', '"Courier New"', 'monospace'],
      },
      boxShadow: {
        glow: '0 2px 8px rgba(0,0,0,0.35)',
        'glow-brand': '0 2px 8px rgba(0,0,0,0.4)',
        card: '0 2px 6px rgba(0,0,0,0.3)',
      },
      keyframes: {
        spinx: { '0%': { transform: 'rotate(0)' }, '100%': { transform: 'rotate(360deg)' } },
      },
      animation: {
        'pulse-glow': 'none',
        aurora: 'none',
        'aurora-slow': 'none',
      },
    },
  },
  plugins: [],
}
