import React, { useEffect, useState } from 'react'
import { ScrollText, RefreshCw } from 'lucide-react'
import { auditApi } from '../../services/api'
import { Card, CardHeader, Button, Badge } from '../../components/ui/primitives'

const fmt = (s) => { try { return new Date(s).toLocaleString('es-CL') } catch { return s } }

export default function AuditPage() {
  const [rows, setRows] = useState([])
  const load = () => auditApi.list(300).then((r) => setRows(r.data)).catch(() => {})
  useEffect(() => { load() }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ScrollText className="h-7 w-7 text-neon-400" />
          <div>
            <h1 className="font-display text-2xl font-bold text-gradient">Auditoría</h1>
            <p className="text-ink-400">Quién hizo qué y cuándo.</p>
          </div>
        </div>
        <Button variant="secondary" onClick={load}><RefreshCw className="h-4 w-4" /> Refrescar</Button>
      </div>

      <Card>
        <CardHeader title={`Acciones registradas (${rows.length})`} />
        <div className="overflow-x-auto p-5">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-white/10 text-left text-ink-400">
              <th className="py-2">Fecha</th><th>Usuario</th><th>Acción</th><th>Ruta</th><th>Estado</th>
            </tr></thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-b border-white/5">
                  <td className="py-2 whitespace-nowrap text-xs text-ink-400">{fmt(r.created_at)}</td>
                  <td className="text-ink-200">{r.user_email || '—'}</td>
                  <td className="text-ink-300">{r.action}</td>
                  <td className="font-mono text-xs text-ink-500">{r.method} {r.path}</td>
                  <td><Badge tone={r.status < 300 ? 'baja' : r.status < 500 ? 'media' : 'critica'}>{r.status}</Badge></td>
                </tr>
              ))}
              {!rows.length && <tr><td colSpan={5} className="py-3 text-ink-500">Sin registros aún.</td></tr>}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
