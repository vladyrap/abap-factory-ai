import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Cpu, Terminal } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'
import { Button, Input } from '../../components/ui/primitives'
import TechBackground from '../../components/TechBackground'

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
    <div className="relative flex min-h-screen items-center justify-center p-4">
      <TechBackground dense />

      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="glass hud-line w-full max-w-md overflow-hidden rounded-3xl p-8 shadow-glow-brand"
      >
        <div className="mb-8 flex items-center gap-4">
          <motion.div
            animate={{ rotate: [0, 6, -6, 0] }} transition={{ duration: 6, repeat: Infinity }}
            className="flex h-14 w-14 items-center justify-center rounded-2xl border border-neon-400/30 bg-gradient-to-br from-brand-600/30 to-neon-500/20 shadow-glow"
          >
            <Cpu className="h-7 w-7 text-neon-400" />
          </motion.div>
          <div>
            <h1 className="font-display text-2xl font-bold tracking-tight text-gradient">ABAP Factory AI</h1>
            <p className="flex items-center gap-1.5 text-sm text-ink-400">
              <Terminal className="h-3.5 w-3.5" /> Desarrollo ABAP asistido por IA
            </p>
          </div>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Contraseña" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button type="submit" loading={loading} className="w-full animate-pulse-glow">Acceder a la consola</Button>
        </form>

        <div className="mt-6 flex items-center justify-between font-mono text-[11px] text-ink-500">
          <span>demo: admin@abapfactory.ai / demo1234</span>
          <span className="flex items-center gap-1.5"><span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" /> online</span>
        </div>
      </motion.div>
    </div>
  )
}
