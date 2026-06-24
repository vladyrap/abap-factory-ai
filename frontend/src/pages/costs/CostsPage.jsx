import React, { useEffect, useState } from 'react'
import { DollarSign } from 'lucide-react'
import { costsApi } from '../../services/api'
import { Card, CardHeader, Stat, Spinner } from '../../components/ui/primitives'

function Table({ title, rows, keyLabel }) {
  return (
    <Card>
      <CardHeader title={title} />
      <div className="p-5">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-ink-800 text-left text-ink-400">
            <th className="py-2">{keyLabel}</th><th className="text-right">Llamadas</th><th className="text-right">USD</th>
          </tr></thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-b border-ink-900">
                <td className="py-2 text-ink-200">{r.label}</td>
                <td className="text-right text-ink-400">{r.calls}</td>
                <td className="text-right font-mono text-brand-300">${r.usd}</td>
              </tr>
            ))}
            {!rows.length && <tr><td colSpan={3} className="py-3 text-ink-500">Sin datos.</td></tr>}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

export default function CostsPage() {
  const [s, setS] = useState(null)
  useEffect(() => { costsApi.summary().then((r) => setS(r.data)).catch(() => {}) }, [])
  if (!s) return <div className="flex h-64 items-center justify-center"><Spinner className="h-8 w-8" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <DollarSign className="h-7 w-7 text-brand-400" />
        <h1 className="text-2xl font-bold text-ink-50">Costos de IA</h1>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Total USD" value={`$${s.total_usd}`} icon={DollarSign} />
        <Stat label="Total CLP" value={`$${Number(s.total_clp).toLocaleString('es-CL')}`} icon={DollarSign} />
        <Stat label="Llamadas IA" value={s.total_calls} />
        <Stat label="Tokens (in/out)" value={`${(s.total_tokens_in / 1000).toFixed(1)}k / ${(s.total_tokens_out / 1000).toFixed(1)}k`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Table title="Por proveedor" keyLabel="Proveedor" rows={s.by_provider.map((x) => ({ label: x.provider, calls: x.calls, usd: x.usd }))} />
        <Table title="Por operación" keyLabel="Operación" rows={s.by_operation.map((x) => ({ label: x.operation, calls: x.calls, usd: x.usd }))} />
        <Table title="Por usuario" keyLabel="Usuario" rows={s.by_user.map((x) => ({ label: x.user, calls: x.calls, usd: x.usd }))} />
        <Table title="Por proyecto" keyLabel="Proyecto" rows={s.by_project.map((x) => ({ label: x.project, calls: x.calls, usd: x.usd }))} />
      </div>
    </div>
  )
}
