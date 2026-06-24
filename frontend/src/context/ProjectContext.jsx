import React, { createContext, useContext, useState, useEffect } from 'react'
import { projectsApi } from '../services/api'

const ProjectContext = createContext(null)

export function ProjectProvider({ children }) {
  const [projects, setProjects] = useState([])
  const [activeId, setActiveId] = useState(() => {
    const s = localStorage.getItem('activeProjectId')
    return s ? Number(s) : null
  })

  const reload = () => projectsApi.list().then((r) => {
    setProjects(r.data)
    if (!activeId && r.data.length) selectProject(r.data[0].id)
  }).catch(() => {})

  useEffect(() => { reload() }, [])

  const selectProject = (id) => {
    setActiveId(id)
    localStorage.setItem('activeProjectId', String(id))
  }

  const active = projects.find((p) => p.id === activeId) || null

  return (
    <ProjectContext.Provider value={{ projects, active, activeId, selectProject, reload }}>
      {children}
    </ProjectContext.Provider>
  )
}

export const useProject = () => useContext(ProjectContext)
