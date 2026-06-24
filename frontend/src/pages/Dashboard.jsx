import React, { useEffect, useState } from 'react'
import {
  Code2, Bug, ShieldCheck, FlaskConical, DollarSign, Clock, TrendingUp, AlertTriangle,
} from 'lucide-react'
import { dashboardApi } from '../services/api'
import { useProject } from '../context/ProjectContext'
import { Card, CardHeader, Stat, Spinner, Badge } from '../components/ui/primitives'

export default function Dashboard() {
  const { activeId, active } = useProject()
  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState(null)

  useEffect(() => {
    dashboardApi.stats(activeId).then((r) => setStats(r.data)).catch(() => {})
    dashboardApi.recent().then((r) => setRecent(r.data)).catch(() => {})
  }, [activeId])

  if (!stats) return <div className="flex h-64 items-center justify-center"><Spinner className="h-8 w-8" /></div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink-50">Dashboard</h1>
        <p className="text-ink-400">{active ? `Proyecto: ${active.name}` : 'Vista global de todos los proyectos'}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Programas generados" value={stats.total_programs} icon={Code2} />
        <Stat label="Dumps resueltos" value={stats.dumps_resolved} icon={Bug} />
        <Stat label="Score promedio" value={stats.avg_quality_score ?? '—'} sub="Code Inspector" icon={ShieldCheck} />
        <Stat label="Pruebas generadas" value={stats.tests_generated} icon={FlaskConical} />
        <Stat label="Hallazgos calidad" value={stats.inspector_findings} icon={AlertTriangle} />
        <Stat label="Costo IA (USD)" value={`$${stats.cost_usd}`} icon={DollarSign} />
        <Stat label="Costo IA (CLP)" value={`$${Number(stats.cost_clp).toLocaleString('es-CL')}`} icon={DollarSign} />
        <Stat label="Horas ahorradas" value={stats.estimated_hours_saved} sub="estimado" icon={Clock} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Errores más frecuentes" icon={TrendingUp} />
          <div className="p-5">
            {stats.frequent_dumps.length === 0 && <p className="text-sm text-ink-500">Sin dumps analizados aún.</p>}
            {stats.frequent_dumps.map((d) => (
              <div key={d.type} className="flex items-center justify-between border-b border-ink-800 py-2 last:border-0">
                <span className="font-mono text-sm text-ink-200">{d.type}</span>
                <Badge tone="warning">{d.count}</Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <CardHeader title="Actividad reciente" icon={Code2} />
          <div className="p-5 space-y-2">
            {recent?.artifacts?.map((a) => (
              <div key={`a${a.id}`} className="flex items-center justify-between text-sm">
                <span className="text-ink-200">{a.name}</span>
                <Badge>{a.dev_type || 'código'}</Badge>
              </div>
            ))}
            {recent?.dumps?.map((d) => (
              <div key={`d${d.id}`} className="flex items-center justify-between text-sm">
                <span className="font-mono text-ink-300">{d.dump_type}</span>
                <Badge tone={d.severity}>{d.severity}</Badge>
              </div>
            ))}
            {!recent?.artifacts?.length && !recent?.dumps?.length && (
              <p className="text-sm text-ink-500">Sin actividad todavía.</p>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
