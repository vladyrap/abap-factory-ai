import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '../../lib/cn'
import AnimatedNumber from '../AnimatedNumber'

export function Card({ className, children, ...props }) {
  return (
    <div className={cn('glass rounded-2xl shadow-card', className)} {...props}>
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, icon: Icon, action }) {
  return (
    <div className="hud-line flex items-start justify-between gap-3 border-b border-white/10 px-5 py-4">
      <div className="flex items-center gap-3">
        {Icon && (
          <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-neon-400/20 bg-neon-500/10 text-neon-400">
            <Icon className="h-[18px] w-[18px]" />
          </span>
        )}
        <div>
          <h3 className="font-display font-semibold tracking-tight text-ink-50">{title}</h3>
          {subtitle && <p className="text-sm text-ink-400">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}

const BTN = {
  primary: 'bg-gradient-to-r from-brand-600 to-neon-600 text-white shadow-glow-brand hover:brightness-110',
  secondary: 'bg-white/5 text-ink-100 border border-white/10 hover:border-neon-400/40 hover:bg-white/10',
  ghost: 'text-ink-300 hover:bg-white/5 hover:text-ink-100',
  danger: 'bg-gradient-to-r from-red-600 to-rose-600 text-white hover:brightness-110',
}

export function Button({ variant = 'primary', className, loading, children, ...props }) {
  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed',
        BTN[variant], className
      )}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />}
      {children}
    </motion.button>
  )
}

const BADGE = {
  baja: 'bg-emerald-500/10 text-emerald-300 border-emerald-400/30',
  media: 'bg-amber-500/10 text-amber-300 border-amber-400/30',
  alta: 'bg-orange-500/10 text-orange-300 border-orange-400/30',
  critica: 'bg-red-500/10 text-red-300 border-red-400/30',
  info: 'bg-neon-500/10 text-neon-400 border-neon-400/30',
  warning: 'bg-amber-500/10 text-amber-300 border-amber-400/30',
  error: 'bg-red-500/10 text-red-300 border-red-400/30',
  default: 'bg-white/5 text-ink-200 border-white/10',
}

export function Badge({ tone = 'default', children, className }) {
  return (
    <span className={cn('inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium', BADGE[tone] || BADGE.default, className)}>
      {children}
    </span>
  )
}

const fieldCls = 'w-full rounded-xl border border-white/10 bg-ink-950/60 px-3 py-2 text-sm text-ink-100 outline-none transition focus:border-neon-400/50 focus:shadow-glow'

export function Input({ className, label, ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm font-medium text-ink-300">{label}</span>}
      <input className={cn(fieldCls, className)} {...props} />
    </label>
  )
}

export function Textarea({ className, label, ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm font-medium text-ink-300">{label}</span>}
      <textarea className={cn(fieldCls, className)} {...props} />
    </label>
  )
}

export function Select({ className, label, options = [], ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1 block text-sm font-medium text-ink-300">{label}</span>}
      <select className={cn(fieldCls, className)} {...props}>
        {options.map((o) => (
          <option key={o.value ?? o} value={o.value ?? o} className="bg-ink-900">{o.label ?? o}</option>
        ))}
      </select>
    </label>
  )
}

export function Spinner({ className }) {
  return <span className={cn('inline-block h-5 w-5 animate-spin rounded-full border-2 border-white/10 border-t-neon-400', className)} />
}

const STAT_TONE = {
  brand: 'from-brand-500/15 text-brand-300',
  neon: 'from-neon-500/15 text-neon-400',
  plasma: 'from-plasma-500/15 text-plasma-400',
  amber: 'from-amber-500/15 text-amber-300',
}

export function Stat({ label, value, sub, icon: Icon, tone = 'neon', numeric = false, decimals = 0, prefix = '', suffix = '' }) {
  const toneCls = STAT_TONE[tone] || STAT_TONE.neon
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className={cn('glass glass-hover hud-line relative overflow-hidden rounded-2xl bg-gradient-to-br to-transparent p-5', toneCls)}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-ink-400">{label}</p>
        {Icon && <Icon className={cn('h-5 w-5', toneCls.split(' ')[1])} />}
      </div>
      <p className="mt-2 font-display text-3xl font-bold text-ink-50">
        {numeric ? <AnimatedNumber value={value} decimals={decimals} prefix={prefix} suffix={suffix} /> : value}
      </p>
      {sub && <p className="mt-1 text-xs text-ink-500">{sub}</p>}
    </motion.div>
  )
}
