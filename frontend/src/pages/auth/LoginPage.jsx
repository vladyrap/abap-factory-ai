import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Cpu, Terminal } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'
import { Button, Input } from '../../components/ui/primitives'

export default function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@abapfactory.ai')
  const [password, setPassword] = useState('demo1234')
  const [otp, setOtp] = useState('')
  const [otpRequired, setOtpRequired] = useState(false)
  const [loading, setLoading] = useState(false)

  if (user) return <div />

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password, otp)
      navigate('/')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail === 'otp_required') {
        setOtpRequired(true)
        toast('Ingresa el código de tu app de autenticación', { icon: '🔐' })
      } else if (detail === 'otp_invalid') {
        toast.error('Código 2FA inválido')
      } else if (err.response?.status === 429) {
        toast.error(detail || 'Demasiados intentos. Espera unos minutos.')
      } else {
        toast.error('Credenciales inválidas')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-vs-editor text-ink-200">
      {/* Title bar */}
      <div className="flex h-8 shrink-0 items-center justify-between border-b border-vs-border bg-vs-sidebar px-3 text-xs text-vs-muted">
        <span className="flex items-center gap-2"><Cpu className="h-3.5 w-3.5 text-vs-link" /> ABAP Factory AI — Iniciar sesión</span>
        <div className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
          <span className="h-3 w-3 rounded-full bg-[#28c840]" />
          <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center p-4">
        <div className="w-full max-w-sm rounded-[4px] border border-vs-border bg-vs-sidebar p-6">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-[4px] border border-vs-border2 bg-vs-editor">
              <Cpu className="h-6 w-6 text-vs-link" strokeWidth={1.5} />
            </div>
            <div>
              <h1 className="text-base font-semibold text-ink-100">ABAP Factory AI</h1>
              <p className="flex items-center gap-1.5 text-xs text-vs-muted">
                <Terminal className="h-3 w-3" /> Desarrollo ABAP asistido por IA
              </p>
            </div>
          </div>

          <form onSubmit={submit} className="space-y-3">
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Input label="Contraseña" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            {otpRequired && (
              <Input label="Código 2FA" inputMode="numeric" autoFocus value={otp}
                onChange={(e) => setOtp(e.target.value)} placeholder="123456" className="font-mono tracking-widest" />
            )}
            <Button type="submit" loading={loading} className="w-full">Iniciar sesión</Button>
          </form>

          <div className="mt-5 flex items-center justify-between border-t border-vs-border pt-3 font-mono text-[11px] text-vs-muted">
            <span>demo: admin@abapfactory.ai / demo1234</span>
            <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-vs-green" /> online</span>
          </div>
        </div>
      </div>
    </div>
  )
}
