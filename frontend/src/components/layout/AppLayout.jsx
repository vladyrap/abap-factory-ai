import React from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, FolderKanban, Wand2, Code2, Bug, ShieldCheck, Workflow, Brain,
  FlaskConical, ClipboardList, History, DollarSign, Users, Bot, LogOut, Cpu, FileText,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useProject } from '../../context/ProjectContext'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/wizard', label: 'Flujo guiado', icon: Workflow, perm: 'create' },
  { to: '/projects', label: 'Proyectos', icon: FolderKanban, perm: 'projects' },
  { to: '/knowledge', label: 'Memoria cliente', icon: Brain, perm: 'create' },
  { to: '/generator', label: 'Generador ABAP', icon: Wand2, perm: 'create' },
  { to: '/spec', label: 'Especificación', icon: FileText, perm: 'create' },
  { to: '/editor', label: 'Editor ABAP', icon: Code2, perm: 'edit' },
  { to: '/dumps', label: 'Analizador Dumps', icon: Bug, perm: 'dumps' },
  { to: '/inspector', label: 'Code Inspector', icon: ShieldCheck, perm: 'create' },
  { to: '/tests', label: 'ABAP Unit', icon: FlaskConical, perm: 'tests' },
  { to: '/protocols', label: 'Protocolos', icon: ClipboardList, perm: 'tests' },
  { to: '/jobs', label: 'Procesos', icon: Cpu, perm: 'create' },
  { to: '/history', label: 'Historial', icon: History },
  { to: '/costs', label: 'Costos IA', icon: DollarSign, perm: 'costs' },
  { to: '/agents', label: 'Agentes IA', icon: Bot, perm: 'admin' },
  { to: '/admin', label: 'Usuarios', icon: Users, perm: 'admin' },
]

export default function AppLayout() {
  const { user, logout, can } = useAuth()
  const { projects, activeId, selectProject } = useProject()
  const navigate = useNavigate()

  const items = NAV.filter((n) => !n.perm || can(n.perm))

  return (
    <div className="flex min-h-screen bg-ink-950 text-ink-100">
      {/* Sidebar */}
      <aside className="flex w-64 shrink-0 flex-col border-r border-ink-800 bg-ink-900/50">
        <div className="flex items-center gap-2 px-5 py-5">
          <Cpu className="h-7 w-7 text-brand-500" />
          <div>
            <p className="text-sm font-bold leading-tight text-ink-50">ABAP Factory</p>
            <p className="text-[11px] font-medium tracking-wide text-brand-400">AI</p>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {items.map((n) => (
            <NavLink
              key={n.to} to={n.to} end={n.end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-brand-600/20 text-brand-300' : 'text-ink-400 hover:bg-ink-800 hover:text-ink-100'
                }`
              }
            >
              <n.icon className="h-[18px] w-[18px]" />
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-ink-800 p-3">
          <button onClick={() => { logout(); navigate('/login') }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-ink-400 hover:bg-ink-800 hover:text-red-400">
            <LogOut className="h-[18px] w-[18px]" /> Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-ink-800 bg-ink-900/30 px-6 py-3">
          <div className="flex items-center gap-3">
            <span className="text-sm text-ink-400">Proyecto activo:</span>
            <select
              value={activeId || ''}
              onChange={(e) => selectProject(Number(e.target.value))}
              className="rounded-lg border border-ink-700 bg-ink-950 px-3 py-1.5 text-sm text-ink-100 outline-none focus:border-brand-500"
            >
              <option value="">— Sin proyecto —</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium text-ink-100">{user?.first_name} {user?.last_name}</p>
              <p className="text-xs text-ink-500">{user?.role}</p>
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
          </div>
        </header>
        <motion.main
          key={window.location.pathname}
          initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}
          className="flex-1 overflow-auto p-6"
        >
          <Outlet />
        </motion.main>
      </div>
    </div>
  )
}
