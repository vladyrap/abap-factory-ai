import React, { createContext, useContext, useState, useEffect } from 'react'
import { authApi } from '../services/api'

const AuthContext = createContext(null)

// Permisos por rol (cliente: solo lectura)
const PERMS = {
  admin: ['create', 'edit', 'approve', 'dumps', 'tests', 'export', 'projects', 'costs', 'admin'],
  tech_lead: ['create', 'edit', 'approve', 'dumps', 'tests', 'export', 'projects', 'costs'],
  consultant: ['create', 'edit', 'dumps', 'tests', 'export', 'projects'],
  qa: ['tests', 'dumps', 'export'],
  client_readonly: ['export'],
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
        .then((r) => setUser(r.data))
        .catch(() => { localStorage.removeItem('token'); localStorage.removeItem('user') })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const { data } = await authApi.login({ email, password })
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const can = (perm) => !!user && (PERMS[user.role] || []).includes(perm)

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, can }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
