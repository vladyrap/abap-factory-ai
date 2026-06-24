import React from 'react'
import { AlertTriangle, RotateCw } from 'lucide-react'

// Evita que un error en una pantalla tumbe toda la app (pantalla blanca).
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('UI error capturado por ErrorBoundary:', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center p-8 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-red-400/30 bg-red-500/10">
            <AlertTriangle className="h-8 w-8 text-red-400" />
          </div>
          <h2 className="mt-4 font-display text-xl font-bold text-ink-50">Algo salió mal en esta vista</h2>
          <p className="mt-1 max-w-md text-sm text-ink-400">
            El resto de la aplicación sigue funcionando. Puedes reintentar o volver al inicio.
          </p>
          <div className="mt-5 flex gap-3">
            <button onClick={() => this.setState({ error: null })}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-neon-600 px-4 py-2 text-sm font-medium text-white">
              <RotateCw className="h-4 w-4" /> Reintentar
            </button>
            <button onClick={() => { window.location.href = '/' }}
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink-200">
              Ir al inicio
            </button>
          </div>
          {import.meta.env.DEV && (
            <pre className="mt-6 max-w-xl overflow-auto rounded-lg border border-white/10 bg-ink-950/60 p-3 text-left text-xs text-red-300/80">
              {String(this.state.error?.stack || this.state.error)}
            </pre>
          )}
        </div>
      )
    }
    return this.props.children
  }
}
