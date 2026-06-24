import React from 'react'

// Fondo futurista: grid técnico + blobs aurora animados. Puramente decorativo.
export default function TechBackground({ dense = false }) {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-ink-950" />
      <div className="absolute inset-0 tech-grid" />
      <div className="aurora-blob animate-aurora h-[40rem] w-[40rem] -left-40 -top-40 bg-brand-600/30" />
      <div className="aurora-blob animate-aurora-slow h-[34rem] w-[34rem] right-[-10rem] top-10 bg-neon-500/20" />
      {dense && (
        <div className="aurora-blob animate-aurora h-[30rem] w-[30rem] bottom-[-8rem] left-1/3 bg-plasma-500/20" />
      )}
      {/* viñeta */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_55%,rgba(7,11,20,0.9)_100%)]" />
    </div>
  )
}
