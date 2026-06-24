import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Cpu } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'
import { Button, Input } from '../../components/ui/primitives'

export default function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@abapfactory.ai')
  const [password, setPassword] = useState('demo1234')
  const [loading, setLoading] = useState(false)

  if (user) return <div />

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch {
      toast.error('Credenciales inválidas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-ink-950 via-ink-900 to-brand-900/40 p-4">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md rounded-2xl border border-ink-800 bg-ink-900/70 p-8 backdrop-blur">
        <div className="mb-8 flex items-center gap-3">
          <Cpu className="h-10 w-10 text-brand-500" />
          <div>
            <h1 className="text-xl font-bold text-ink-50">ABAP Factory AI</h1>
            <p className="text-sm text-ink-400">Plataforma de desarrollo ABAP asistido por IA</p>
          </div>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Contraseña" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button type="submit" loading={loading} className="w-full">Ingresar</Button>
        </form>
        <p className="mt-6 text-center text-xs text-ink-500">Demo: admin@abapfactory.ai / demo1234</p>
      </motion.div>
    </div>
  )
}
