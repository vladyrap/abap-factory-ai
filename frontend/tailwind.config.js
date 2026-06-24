/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Paleta enterprise SAP Fiori + consola sci-fi
        brand: {
          50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 300: '#93c5fd',
          400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8',
          800: '#1e40af', 900: '#1e3a5f',
        },
        // Acento neón cian
        neon: {
          400: '#22d3ee', 500: '#06b6d4', 600: '#0891b2',
        },
        plasma: {
          400: '#a855f7', 500: '#8b5cf6',
        },
        ink: {
          50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0', 300: '#cbd5e1',
          400: '#94a3b8', 500: '#64748b', 600: '#475569', 700: '#334155',
          800: '#1e293b', 900: '#0f172a', 950: '#070b14',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', 'monospace'],
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(34,211,238,0.18), 0 0 24px -4px rgba(34,211,238,0.35)',
        'glow-brand': '0 0 0 1px rgba(37,99,235,0.25), 0 0 28px -6px rgba(59,130,246,0.5)',
        card: '0 1px 0 0 rgba(255,255,255,0.04) inset, 0 18px 40px -24px rgba(0,0,0,0.8)',
      },
      keyframes: {
        aurora: {
          '0%,100%': { transform: 'translate(0,0) scale(1)', opacity: '0.6' },
          '50%': { transform: 'translate(6%,4%) scale(1.15)', opacity: '0.9' },
        },
        floaty: {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        pulseGlow: {
          '0%,100%': { boxShadow: '0 0 0 0 rgba(34,211,238,0.35)' },
          '50%': { boxShadow: '0 0 22px 4px rgba(34,211,238,0.18)' },
        },
      },
      animation: {
        aurora: 'aurora 14s ease-in-out infinite',
        'aurora-slow': 'aurora 22s ease-in-out infinite',
        floaty: 'floaty 6s ease-in-out infinite',
        shimmer: 'shimmer 2.2s linear infinite',
        scan: 'scan 4s linear infinite',
        'pulse-glow': 'pulseGlow 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
