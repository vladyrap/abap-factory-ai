import React, { useEffect, useState } from 'react'
import { ShieldCheck, Smartphone, Lock, Unlock } from 'lucide-react'
import toast from 'react-hot-toast'
import { authApi } from '../../services/api'
import { Card, CardHeader, Button, Input, Badge } from '../../components/ui/primitives'

export default function SecurityPage() {
  const [enabled, setEnabled] = useState(false)
  const [setup, setSetup] = useState(null)   // {secret, otpauth_uri, qr_svg}
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)

  const refresh = () => authApi.twofaStatus().then((r) => setEnabled(r.data.enabled)).catch(() => {})
  useEffect(() => { refresh() }, [])

  const startSetup = async () => {
    setLoading(true)
    try { const { data } = await authApi.twofaSetup(); setSetup(data) }
    catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  const enable = async () => {
    try { await authApi.twofaEnable(otp); toast.success('2FA activado'); setSetup(null); setOtp(''); refresh() }
    catch (e) { toast.error(e.response?.data?.detail || 'Código inválido') }
  }

  const disable = async () => {
    try { await authApi.twofaDisable(otp); toast.success('2FA desactivado'); setOtp(''); refresh() }
    catch (e) { toast.error(e.response?.data?.detail || 'Código inválido') }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ShieldCheck className="h-7 w-7 text-neon-400" />
        <div>
          <h1 className="font-display text-2xl font-bold text-gradient">Seguridad de mi cuenta</h1>
          <p className="text-ink-400">Verificación en dos pasos (TOTP).</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader title="Autenticación en dos pasos (2FA)" icon={Smartphone}
          action={<Badge tone={enabled ? 'baja' : 'media'}>{enabled ? 'Activado' : 'Desactivado'}</Badge>} />
        <div className="space-y-4 p-5">
          {!enabled && !setup && (
            <>
              <p className="text-sm text-ink-400">Protege tu cuenta con Google Authenticator, Authy, Microsoft Authenticator, etc.</p>
              <Button onClick={startSetup} loading={loading}><Lock className="h-4 w-4" /> Activar 2FA</Button>
            </>
          )}

          {!enabled && setup && (
            <>
              <p className="text-sm text-ink-300">1. Escanea el QR con tu app de autenticación (o ingresa el código manual).</p>
              <div className="flex flex-wrap items-center gap-4">
                {setup.qr_svg
                  ? <div className="h-44 w-44 rounded-lg bg-white p-2" dangerouslySetInnerHTML={{ __html: setup.qr_svg }} />
                  : <div className="rounded-lg border border-white/10 p-4 text-xs text-ink-400">QR no disponible; usa el código manual.</div>}
                <div>
                  <p className="text-xs text-ink-500">Código manual:</p>
                  <p className="font-mono text-sm text-neon-300 break-all">{setup.secret}</p>
                </div>
              </div>
              <p className="text-sm text-ink-300">2. Ingresa el código de 6 dígitos para confirmar.</p>
              <div className="flex items-end gap-2">
                <Input label="Código 2FA" value={otp} onChange={(e) => setOtp(e.target.value)}
                  placeholder="123456" className="font-mono tracking-widest" />
                <Button onClick={enable}>Confirmar</Button>
              </div>
            </>
          )}

          {enabled && (
            <>
              <p className="text-sm text-ink-400">El 2FA está activo. Para desactivarlo, ingresa un código vigente.</p>
              <div className="flex items-end gap-2">
                <Input label="Código 2FA" value={otp} onChange={(e) => setOtp(e.target.value)}
                  placeholder="123456" className="font-mono tracking-widest" />
                <Button variant="danger" onClick={disable}><Unlock className="h-4 w-4" /> Desactivar</Button>
              </div>
            </>
          )}
        </div>
      </Card>
    </div>
  )
}
