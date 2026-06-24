import React from 'react'
import { cn } from '../../lib/cn'

export function Card({ className, children, ...props }) {
  return (
    <div className={cn('rounded-xl border border-ink-800 bg-ink-900/60 backdrop-blur', className)} {...props}>
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, icon: Icon, action }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-ink-800 px-5 py-4">
      <div className="flex items-center gap-3">
        {Icon && <Icon className="h-5 w-5 text-brand-400" />}
        <div>
          <h3 className="font-semibold text-ink-50">{title}</h3>
          {subtitle && <p className="text-sm text-ink-400">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}

const BTN = {
  primary: 'bg-brand-600 hover:bg-brand-500 text-white',
  secondary: 'bg-ink-800 hover:bg-ink-700 text-ink-100 border border-ink-700',
  ghost: 'hover:bg-ink-800 text-ink-300',
  danger: 'bg-red-600 hover:bg-red-500 text-white',
}

export function Button({ variant = 'primary', className, loading, children, ...props }) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed',
        BTN[variant], className
      )}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />}
      {children}
    </button>
  )
}

const BADGE = {
  baja: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  media: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  alta: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
  critica: 'bg-red-500/15 text-red-400 border-red-500/30',
  info: 'bg-sky-500/15 text-sky-400 border-sky-500/30',
  warning: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  error: 'bg-red-500/15 text-red-400 border-red-500/30',
  default: 'bg-ink-700/50 text-ink-200 border-ink-600',
}

export function Badge({ tone = 'default', children, className }) {
  return (
    <span className={cn('inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium', BADGE[tone] || BADGE.default, className)}>
      {children}
    </span>
  )
}

export function Input({ className, label, ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm font-medium text-ink-300">{label}</span>}
      <input className={cn('w-full rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm text-ink-100 outline-none focus:border-brand-500', className)} {...props} />
    </label>
  )
}

export function Textarea({ className, label, ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm font-medium text-ink-300">{label}</span>}
      <textarea className={cn('w-full rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm text-ink-100 outline-none focus:border-brand-500', className)} {...props} />
    </label>
  )
}

export function Select({ className, label, options = [], ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm font-medium text-ink-300">{label}</span>}
      <select className={cn('w-full rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm text-ink-100 outline-none focus:border-brand-500', className)} {...props}>
        {options.map((o) => (
          <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? o}</option>
        ))}
      </select>
    </label>
  )
}

export function Spinner({ className }) {
  return <span className={cn('inline-block h-5 w-5 animate-spin rounded-full border-2 border-ink-600 border-t-brand-500', className)} />
}

export function Stat({ label, value, sub, icon: Icon, tone = 'brand' }) {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-ink-400">{label}</p>
        {Icon && <Icon className={cn('h-5 w-5', tone === 'brand' ? 'text-brand-400' : 'text-ink-400')} />}
      </div>
      <p className="mt-2 text-2xl font-bold text-ink-50">{value}</p>
      {sub && <p className="mt-1 text-xs text-ink-500">{sub}</p>}
    </Card>
  )
}
