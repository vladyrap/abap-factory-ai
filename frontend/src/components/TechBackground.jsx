import React from 'react'

// Fondo plano estilo "editor" de VS Code (reemplaza la aurora anterior).
export default function TechBackground() {
  return <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 bg-vs-editor" />
}
