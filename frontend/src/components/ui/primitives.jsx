import React from 'react'
import { cn } from '../../lib/cn'
import AnimatedNumber from '../AnimatedNumber'

// ─── Panel / Card estilo VS Code (plano) ────────────────────────────────────
export function Card({ className, children, ...props }) {
  return (
    <div className={cn('rounded-[3px] border border-vs-border bg-vs-sidebar', className)} {...props}>
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, icon: Icon, action }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-vs-border px-4 py-2.5">
      <div className="flex items-center gap-2.5">
        {Icon && <Icon className="h-4 w-4 text-vs-muted" />}
        <div>
          <h3 className="text-[13px] font-semibold uppercase tracking-wide text-ink-200">{title}</h3>
          {subtitle && <p className="text-xs text-vs-muted">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}

// ─── Botones estilo VS Code ──────────────────────────────────────────────────
const BTN = {
  primary: 'bg-vs-button hover:bg-vs-buttonHover text-white',
  secondary: 'bg-[#3a3d41] hover:bg-[#45494e] text-ink-100',
  ghost: 'text-ink-200 hover:bg-vs-hover',
  danger: 'bg-vs-red/90 hover:bg-vs-red text-white',
}

export function Button({ variant = 'primary', className, loading, children, ...props }) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-[2px] px-3 py-1.5 text-[13px] font-normal transition disabled:opacity-50 disabled:cursor-not-allowed',
        BTN[variant], className
      )}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />}
      {children}
    </button>
  )
}

// ─── Badges (tonos VS Code) ──────────────────────────────────────────────────
const BADGE = {
  baja: 'bg-vs-green/15 text-vs-green border-vs-green/30',
  media: 'bg-vs-yellow/15 text-[#e2c08d] border-vs-yellow/30',
  alta: 'bg-vs-orange/15 text-vs-orange border-vs-orange/30',
  critica: 'bg-vs-red/15 text-[#f48771] border-vs-red/30',
  info: 'bg-vs-accent/15 text-vs-link border-vs-accent/40',
  warning: 'bg-vs-yellow/15 text-[#e2c08d] border-vs-yellow/30',
  error: 'bg-vs-red/15 text-[#f48771] border-vs-red/30',
  default: 'bg-white/5 text-ink-300 border-vs-border2',
}

export function Badge({ tone = 'default', children, className }) {
  return (
    <span className={cn('inline-flex items-center rounded-[2px] border px-1.5 py-0.5 text-[11px] font-medium', BADGE[tone] || BADGE.default, className)}>
      {children}
    </span>
  )
}

// ─── Inputs estilo VS Code ───────────────────────────────────────────────────
const fieldCls = 'w-full rounded-[2px] border border-vs-border2 bg-vs-input px-2.5 py-1.5 text-[13px] text-ink-100 outline-none transition focus:border-vs-accent placeholder:text-vs-muted'

export function Input({ className, label, ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-xs font-medium text-ink-300">{label}</span>}
      <input className={cn(fieldCls, className)} {...props} />
    </label>
  )
}

export function Textarea({ className, label, ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-xs font-medium text-ink-300">{label}</span>}
      <textarea className={cn(fieldCls, 'font-mono', className)} {...props} />
    </label>
  )
}

export function Select({ className, label, options = [], ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-xs font-medium text-ink-300">{label}</span>}
      <select className={cn(fieldCls, className)} {...props}>
        {options.map((o) => (
          <option key={o.value ?? o} value={o.value ?? o} className="bg-vs-input">{o.label ?? o}</option>
        ))}
      </select>
    </label>
  )
}

export function Spinner({ className }) {
  return <span className={cn('inline-block h-4 w-4 animate-spin rounded-full border-2 border-vs-border2 border-t-vs-accent', className)} />
}

// ─── Tarjeta de métrica (estilo panel VS Code) ──────────────────────────────
export function Stat({ label, value, sub, icon: Icon, tone = 'neon', numeric = false, decimals = 0, prefix = '', suffix = '' }) {
  const iconColor = { neon: 'text-vs-link', brand: 'text-vs-link', plasma: 'text-vs-purple', amber: 'text-vs-yellow' }[tone] || 'text-vs-link'
  return (
    <div className="rounded-[3px] border border-vs-border bg-vs-sidebar p-4">
      <div className="flex items-center justify-between">
        <p className="text-[11px] font-medium uppercase tracking-wide text-vs-muted">{label}</p>
        {Icon && <Icon className={cn('h-4 w-4', iconColor)} />}
      </div>
      <p className="mt-1.5 font-mono text-2xl font-semibold text-ink-100">
        {numeric ? <AnimatedNumber value={value} decimals={decimals} prefix={prefix} suffix={suffix} /> : value}
      </p>
      {sub && <p className="mt-0.5 text-[11px] text-vs-muted">{sub}</p>}
    </div>
  )
}
