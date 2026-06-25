import React from 'react'
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FolderKanban, Wand2, Code2, Bug, ShieldCheck, Workflow, Brain,
  FlaskConical, ClipboardList, History, DollarSign, Users, Bot, LogOut, Cpu, FileText,
  ArrowRightLeft, Tags, FileStack, GitBranch, Sparkles, ShieldHalf, ScrollText,
  Files, Settings, GitFork, Circle,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useProject } from '../../context/ProjectContext'
import ErrorBoundary from '../ErrorBoundary'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/solution', label: 'Requerimiento → Solución', icon: Sparkles, perm: 'create' },
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
  { to: '/roles', label: 'Roles y permisos', icon: ShieldHalf, perm: 'roles' },
  { to: '/audit', label: 'Auditoría', icon: ScrollText, perm: 'audit.view' },
  { to: '/security', label: 'Seguridad (2FA)', icon: ShieldCheck },
]

// Iconos de la barra de actividades (estilo VS Code)
const ACTIVITY = [
  { to: '/', icon: LayoutDashboard, title: 'Dashboard', end: true },
  { to: '/solution', icon: Sparkles, title: 'Requerimiento → Solución', perm: 'create' },
  { to: '/generator', icon: Wand2, title: 'Generador', perm: 'create' },
  { to: '/editor', icon: Code2, title: 'Editor', perm: 'edit' },
  { to: '/migration', icon: ArrowRightLeft, title: 'Migración', perm: 'create' },
  { to: '/delivery', icon: GitFork, title: 'Entrega & abapGit', perm: 'export' },
  { to: '/roles', icon: ShieldHalf, title: 'Roles', perm: 'roles' },
]

export default function AppLayout() {
  const { user, logout, can } = useAuth()
  const { projects, activeId, selectProject } = useProject()
  const navigate = useNavigate()
  const location = useLocation()

  const items = NAV.filter((n) => !n.perm || can(n.perm))
  const activity = ACTIVITY.filter((n) => !n.perm || can(n.perm))
  const current = [...NAV].sort((a, b) => b.to.length - a.to.length)
    .find((n) => (n.to === '/' ? location.pathname === '/' : location.pathname.startsWith(n.to)))
  const aiOk = false // se refleja en barra de estado vía health si se desea

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-vs-editor text-ink-200">
      {/* Title bar */}
      <div className="flex h-8 shrink-0 items-center justify-between border-b border-vs-border bg-vs-sidebar px-3 text-xs text-vs-muted">
        <div className="flex items-center gap-2">
          <Cpu className="h-3.5 w-3.5 text-vs-link" />
          <span className="text-ink-300">ABAP Factory AI</span>
          <span className="text-vs-muted">— {current?.label || 'Visual'}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
          <span className="h-3 w-3 rounded-full bg-[#28c840]" />
          <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
        </div>
      </div>

      <div className="flex min-h-0 flex-1">
        {/* Activity bar */}
        <div className="flex w-12 shrink-0 flex-col items-center justify-between bg-vs-activity py-2">
          <div className="flex flex-col items-center gap-1">
            {activity.map((a) => (
              <NavLink key={a.to} to={a.to} end={a.end} title={a.title}
                className={({ isActive }) =>
                  `relative flex h-10 w-12 items-center justify-center ${isActive ? 'text-white' : 'text-[#858585] hover:text-white'}`}>
                {({ isActive }) => (
                  <>
                    {isActive && <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 bg-white" />}
                    <a.icon className="h-6 w-6" strokeWidth={1.5} />
                  </>
                )}
              </NavLink>
            ))}
          </div>
          <div className="flex flex-col items-center gap-2">
            <NavLink to="/security" title="Seguridad (2FA)"
              className={({ isActive }) => `flex h-10 w-12 items-center justify-center ${isActive ? 'text-white' : 'text-[#858585] hover:text-white'}`}>
              <Settings className="h-6 w-6" strokeWidth={1.5} />
            </NavLink>
            <div title={`${user?.first_name} ${user?.last_name}`}
              className="flex h-7 w-7 items-center justify-center rounded-full bg-vs-button text-[11px] font-semibold text-white">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
          </div>
        </div>

        {/* Sidebar / Explorer */}
        <aside className="flex w-60 shrink-0 flex-col border-r border-vs-border bg-vs-sidebar">
          <div className="flex items-center justify-between px-4 py-2 text-[11px] font-semibold uppercase tracking-wide text-vs-muted">
            <span className="flex items-center gap-1.5"><Files className="h-3.5 w-3.5" /> Explorador</span>
          </div>

          {/* Workspace / proyecto activo */}
          <div className="px-3 pb-2">
            <select
              value={activeId || ''}
              onChange={(e) => selectProject(Number(e.target.value))}
              title="Proyecto activo"
              className="w-full rounded-[2px] border border-vs-border2 bg-vs-input px-2 py-1 text-xs text-ink-100 outline-none focus:border-vs-accent">
              <option value="">— Sin proyecto —</option>
              {projects.map((p) => <option key={p.id} value={p.id} className="bg-vs-input">{p.name}</option>)}
            </select>
          </div>

          <nav className="flex-1 overflow-y-auto pb-2">
            {items.map((n) => (
              <NavLink key={n.to} to={n.to} end={n.end}
                className={({ isActive }) =>
                  `flex items-center gap-2 py-[5px] pl-4 pr-3 text-[13px] ${
                    isActive ? 'bg-vs-selection text-white' : 'text-ink-200 hover:bg-vs-hover'
                  }`}>
                <n.icon className="h-4 w-4 shrink-0 text-vs-muted" strokeWidth={1.5} />
                <span className="truncate">{n.label}</span>
              </NavLink>
            ))}
          </nav>

          <button onClick={() => { logout(); navigate('/login') }}
            className="flex items-center gap-2 border-t border-vs-border px-4 py-2 text-[13px] text-ink-300 hover:bg-vs-hover hover:text-vs-red">
            <LogOut className="h-4 w-4" strokeWidth={1.5} /> Cerrar sesión
          </button>
        </aside>

        {/* Editor region */}
        <div className="flex min-w-0 flex-1 flex-col bg-vs-editor">
          {/* Tab bar */}
          <div className="flex h-9 shrink-0 items-stretch border-b border-vs-border bg-vs-sidebar">
            <div className="flex items-center gap-2 border-r border-vs-border bg-vs-editor px-3 text-[13px] text-ink-100">
              {current?.icon && <current.icon className="h-4 w-4 text-vs-link" strokeWidth={1.5} />}
              <span>{current?.label || 'Inicio'}</span>
              <Circle className="ml-1 h-2 w-2 fill-current text-ink-400" />
            </div>
          </div>

          <main className="min-h-0 flex-1 overflow-auto p-5">
            <ErrorBoundary key={location.pathname}>
              <Outlet />
            </ErrorBoundary>
          </main>
        </div>
      </div>

      {/* Status bar */}
      <div className="flex h-6 shrink-0 items-center justify-between bg-vs-statusbar px-3 text-[11px] text-white">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1"><GitBranch className="h-3.5 w-3.5" /> master</span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-white/90" /> {projects.find((p) => p.id === activeId)?.name || 'sin proyecto'}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="uppercase">{user?.role}</span>
          <span>UTF-8</span>
          <span>ABAP</span>
          <span className="font-semibold">ABAP Factory AI</span>
        </div>
      </div>
    </div>
  )
}
