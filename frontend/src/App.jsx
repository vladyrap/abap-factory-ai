import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ProjectProvider } from './context/ProjectContext'
import { Spinner } from './components/ui/primitives'
import AppLayout from './components/layout/AppLayout'

import LoginPage from './pages/auth/LoginPage'
import Dashboard from './pages/Dashboard'
import WizardPage from './pages/wizard/WizardPage'
import ProjectsPage from './pages/projects/ProjectsPage'
import KnowledgePage from './pages/knowledge/KnowledgePage'
import GeneratorPage from './pages/generator/GeneratorPage'
import SpecPage from './pages/spec/SpecPage'
import JobsPage from './pages/jobs/JobsPage'
import EditorPage from './pages/editor/EditorPage'
import DumpsPage from './pages/dumps/DumpsPage'
import InspectorPage from './pages/inspector/InspectorPage'
import TestsPage from './pages/tests/TestsPage'
import ProtocolsPage from './pages/protocols/ProtocolsPage'
import HistoryPage from './pages/HistoryPage'
import CostsPage from './pages/costs/CostsPage'
import AdminUsersPage from './pages/admin/AdminUsersPage'
import AgentsPage from './pages/agents/AgentsPage'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex min-h-screen items-center justify-center bg-ink-950"><Spinner className="h-9 w-9" /></div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Protected><ProjectProvider><AppLayout /></ProjectProvider></Protected>}>
          <Route index element={<Dashboard />} />
          <Route path="wizard" element={<WizardPage />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="generator" element={<GeneratorPage />} />
          <Route path="spec" element={<SpecPage />} />
          <Route path="editor" element={<EditorPage />} />
          <Route path="jobs" element={<JobsPage />} />
          <Route path="dumps" element={<DumpsPage />} />
          <Route path="inspector" element={<InspectorPage />} />
          <Route path="tests" element={<TestsPage />} />
          <Route path="protocols" element={<ProtocolsPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="costs" element={<CostsPage />} />
          <Route path="agents" element={<AgentsPage />} />
          <Route path="admin" element={<AdminUsersPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
