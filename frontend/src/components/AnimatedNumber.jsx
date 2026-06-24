import React, { useEffect, useRef, useState } from 'react'

// Contador que anima desde 0 hasta value al montar / cambiar.
export default function AnimatedNumber({ value = 0, duration = 900, decimals = 0, prefix = '', suffix = '' }) {
  const [display, setDisplay] = useState(0)
  const raf = useRef()

  useEffect(() => {
    const target = Number(value) || 0
    const start = performance.now()
    const from = 0
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3) // easeOutCubic
      setDisplay(from + (target - from) * eased)
      if (t < 1) raf.current = requestAnimationFrame(tick)
    }
    raf.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf.current)
  }, [value, duration])

  const formatted = decimals > 0
    ? display.toFixed(decimals)
    : Math.round(display).toLocaleString('es-CL')

  return <span>{prefix}{formatted}{suffix}</span>
}
