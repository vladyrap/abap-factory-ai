import React, { createContext, useContext, useState, useEffect } from 'react'
import { authApi } from '../services/api'

const AuthContext = createContext(null)

// Mapeo de claves "gruesas" del menú a permisos granulares del backend.
const COARSE_MAP = {
  create: 'code.generate', edit: 'code.edit', approve: 'code.approve',
  projects: 'project.manage', dumps: 'dump.analyze', tests: 'tests.generate',
  costs: 'costs.view', admin: 'users.manage', export: 'export.run',
  roles: 'roles.manage',
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      authApi.me()
        .then((r) => { setUser(r.data); localStorage.setItem('user', JSON.stringify(r.data)) })
        .catch(() => { localStorage.removeItem('token'); localStorage.removeItem('user') })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password, otp) => {
    const { data } = await authApi.login({ email, password, otp: otp || undefined })
    localStorage.setItem('token', data.access_token)
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setUser(null)
  }

  // Permiso granular directo
  const hasPerm = (key) => {
    const perms = user?.permissions || []
    return perms.includes('*') || perms.includes(key)
  }

  // Permiso "grueso" (compatibilidad con el menú y pantallas existentes)
  const can = (coarse) => hasPerm(COARSE_MAP[coarse] || coarse)

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, can, hasPerm }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
