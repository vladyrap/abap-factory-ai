import React from 'react'
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, FolderKanban, Wand2, Code2, Bug, ShieldCheck, Workflow, Brain,
  FlaskConical, ClipboardList, History, DollarSign, Users, Bot, LogOut, Cpu, FileText,
  ArrowRightLeft, Tags, FileStack, GitBranch,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useProject } from '../../context/ProjectContext'
import TechBackground from '../TechBackground'
import ErrorBoundary from '../ErrorBoundary'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/wizard', label: 'Flujo guiado', icon: Workflow, perm: 'create' },
  { to: '/projects', label: 'Proyectos', icon: FolderKanban, perm: 'projects' },
  { to: '/knowledge', label: 'Memoria cliente', icon: Brain, perm: 'create' },
  { to: '/generator', label: 'Generador ABAP', icon: Wand2, perm: 'create' },
  { to: '/migration', label: 'Migración S/4', icon: ArrowRightLeft, perm: 'create' },
  { to: '/naming', label: 'Nomenclaturas', icon: Tags, perm: 'create' },
  { to: '/dev-docs', label: 'Documento técnico', icon: FileStack, perm: 'create' },
  { to: '/spec', label: 'Especificación', icon: FileText, perm: 'create' },
  { to: '/editor', label: 'Editor ABAP', icon: Code2, perm: 'edit' },
  { to: '/dumps', label: 'Analizador Dumps', icon: Bug, perm: 'dumps' },
  { to: '/inspector', label: 'Code Inspector', icon: ShieldCheck, perm: 'create' },
  { to: '/tests', label: 'ABAP Unit', icon: FlaskConical, perm: 'tests' },
  { to: '/protocols', label: 'Protocolos', icon: ClipboardList, perm: 'tests' },
  { to: '/jobs', label: 'Procesos', icon: Cpu, perm: 'create' },
  { to: '/delivery', label: 'Entrega & abapGit', icon: GitBranch, perm: 'export' },
  { to: '/history', label: 'Historial', icon: History },
  { to: '/costs', label: 'Costos IA', icon: DollarSign, perm: 'costs' },
  { to: '/agents', label: 'Agentes IA', icon: Bot, perm: 'admin' },
  { to: '/admin', label: 'Usuarios', icon: Users, perm: 'admin' },
]

export default function AppLayout() {
  const { user, logout, can } = useAuth()
  const { projects, activeId, selectProject } = useProject()
  const navigate = useNavigate()
  const location = useLocation()

  const items = NAV.filter((n) => !n.perm || can(n.perm))

  return (
    <div className="flex min-h-screen text-ink-100">
      <TechBackground />

      {/* Sidebar */}
      <aside className="flex w-64 shrink-0 flex-col border-r border-white/10 bg-ink-950/60 backdrop-blur-xl">
        <div className="flex items-center gap-3 px-5 py-5">
          <motion.div
            animate={{ boxShadow: ['0 0 0 0 rgba(34,211,238,0.0)', '0 0 18px 2px rgba(34,211,238,0.25)', '0 0 0 0 rgba(34,211,238,0.0)'] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-neon-400/30 bg-gradient-to-br from-brand-600/30 to-neon-500/20"
          >
            <Cpu className="h-6 w-6 text-neon-400" />
          </motion.div>
          <div>
            <p className="font-display text-sm font-bold leading-tight text-ink-50">ABAP Factory</p>
            <p className="text-[11px] font-semibold tracking-[0.2em] text-gradient">AI CONSOLE</p>
          </div>
        </div>

        <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-2">
          {items.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.end}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'text-white' : 'text-ink-400 hover:bg-white/5 hover:text-ink-100'
                }`
              }>
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.span layoutId="nav-active"
                      className="absolute inset-0 -z-10 rounded-xl border border-neon-400/30 bg-gradient-to-r from-brand-600/25 to-neon-500/10 shadow-glow" />
                  )}
                  <n.icon className={`h-[18px] w-[18px] ${isActive ? 'text-neon-400' : ''}`} />
                  {n.label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 p-3">
          <button onClick={() => { logout(); navigate('/login') }}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-ink-400 transition hover:bg-red-500/10 hover:text-red-400">
            <LogOut className="h-[18px] w-[18px]" /> Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="hud-line sticky top-0 z-20 flex items-center justify-between border-b border-white/10 bg-ink-950/50 px-6 py-3 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <span className="text-xs font-medium uppercase tracking-wider text-ink-500">Proyecto</span>
            <div className="relative">
              <select
                value={activeId || ''}
                onChange={(e) => selectProject(Number(e.target.value))}
                className="rounded-xl border border-white/10 bg-ink-950/60 px-3 py-1.5 text-sm text-ink-100 outline-none transition focus:border-neon-400/50">
                <option value="">— Sin proyecto —</option>
                {projects.map((p) => <option key={p.id} value={p.id} className="bg-ink-900">{p.name}</option>)}
              </select>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden items-center gap-1.5 font-mono text-[11px] text-ink-500 sm:flex">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" /> sistema operativo
            </span>
            <div className="text-right">
              <p className="text-sm font-medium text-ink-100">{user?.first_name} {user?.last_name}</p>
              <p className="text-xs uppercase tracking-wider text-neon-400/80">{user?.role}</p>
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-neon-600 text-sm font-bold text-white shadow-glow-brand">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
          </div>
        </header>

        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.28 }}
          className="flex-1 overflow-auto p-6"
        >
          <ErrorBoundary key={location.pathname}>
            <Outlet />
          </ErrorBoundary>
        </motion.main>
      </div>
    </div>
  )
}
