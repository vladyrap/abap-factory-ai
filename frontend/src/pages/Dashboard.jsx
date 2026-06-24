import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
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

  const maxDump = Math.max(1, ...stats.frequent_dumps.map((d) => d.count))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold tracking-tight"><span className="text-gradient">Centro de control</span></h1>
        <p className="text-ink-400">{active ? `Proyecto: ${active.name}` : 'Vista global de todos los proyectos'}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Programas" value={stats.total_programs} numeric icon={Code2} tone="neon" />
        <Stat label="Dumps resueltos" value={stats.dumps_resolved} numeric icon={Bug} tone="brand" />
        <Stat label="Score promedio" value={stats.avg_quality_score ?? '—'} sub="Code Inspector" icon={ShieldCheck} tone="plasma" />
        <Stat label="Pruebas" value={stats.tests_generated} numeric icon={FlaskConical} tone="neon" />
        <Stat label="Hallazgos calidad" value={stats.inspector_findings} numeric icon={AlertTriangle} tone="amber" />
        <Stat label="Costo IA USD" value={stats.cost_usd} numeric decimals={2} prefix="$" icon={DollarSign} tone="neon" />
        <Stat label="Costo IA CLP" value={stats.cost_clp} numeric prefix="$" icon={DollarSign} tone="brand" />
        <Stat label="Horas ahorradas" value={stats.estimated_hours_saved} numeric decimals={1} sub="estimado" icon={Clock} tone="plasma" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Errores más frecuentes" subtitle="Top dumps analizados" icon={TrendingUp} />
          <div className="space-y-3 p-5">
            {stats.frequent_dumps.length === 0 && <p className="text-sm text-ink-500">Sin dumps analizados aún.</p>}
            {stats.frequent_dumps.map((d, i) => (
              <div key={d.type}>
                <div className="mb-1 flex items-center justify-between">
                  <span className="font-mono text-xs text-ink-300">{d.type}</span>
                  <Badge tone="warning">{d.count}</Badge>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                  <motion.div
                    initial={{ width: 0 }} animate={{ width: `${(d.count / maxDump) * 100}%` }}
                    transition={{ duration: 0.8, delay: i * 0.08 }}
                    className="h-full rounded-full bg-gradient-to-r from-brand-500 to-neon-400" />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <CardHeader title="Actividad reciente" icon={Code2} />
          <div className="space-y-2 p-5">
            {recent?.artifacts?.map((a) => (
              <div key={`a${a.id}`} className="flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] px-3 py-2 text-sm">
                <span className="text-ink-200">{a.name}</span>
                <Badge tone="info">{a.dev_type || 'código'}</Badge>
              </div>
            ))}
            {recent?.dumps?.map((d) => (
              <div key={`d${d.id}`} className="flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] px-3 py-2 text-sm">
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
