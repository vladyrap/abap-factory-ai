import React, { useEffect, useState, useRef } from 'react'
import { Cpu, Play, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { jobsApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Badge } from '../../components/ui/primitives'

const TYPES = [
  { key: 'batch_inspect', label: 'Re-inspeccionar todo el proyecto', desc: 'Corre Code Inspector sobre cada artefacto generado.' },
  { key: 'batch_generate', label: 'Generar requerimientos pendientes', desc: 'Genera código para cada requerimiento en estado draft.' },
]

const TONE = { pending: 'default', running: 'info', done: 'baja', error: 'critica' }

export default function JobsPage() {
  const { activeId } = useProject()
  const [jobs, setJobs] = useState([])
  const timer = useRef(null)

  const load = () => jobsApi.list(activeId).then((r) => setJobs(r.data)).catch(() => {})

  useEffect(() => {
    load()
    timer.current = setInterval(load, 4000)   // refresco automático del estado
    return () => clearInterval(timer.current)
  }, [activeId])

  const launch = async (job_type) => {
    if (!activeId) return toast.error('Selecciona un proyecto activo')
    try {
      await jobsApi.create({ project_id: activeId, job_type })
      toast.success('Proceso encolado')
      load()
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Cpu className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Procesos Asíncronos</h1>
          <p className="text-ink-400">Trabajos por lote ejecutados en background (APScheduler).</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {TYPES.map((t) => (
          <Card key={t.key} className="p-5">
            <p className="font-semibold text-ink-100">{t.label}</p>
            <p className="mb-3 text-sm text-ink-400">{t.desc}</p>
            <Button onClick={() => launch(t.key)}><Play className="h-4 w-4" /> Lanzar</Button>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader title="Historial de procesos" icon={RefreshCw} />
        <div className="p-5">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-ink-800 text-left text-ink-400">
              <th className="py-2">Tipo</th><th>Estado</th><th>Progreso</th><th>Resultado</th>
            </tr></thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id} className="border-b border-ink-900">
                  <td className="py-2 font-mono text-xs text-ink-300">{j.job_type}</td>
                  <td><Badge tone={TONE[j.status]}>{j.status}</Badge></td>
                  <td className="text-ink-400">{j.processed}/{j.total || '?'}</td>
                  <td className="text-ink-400">{j.error ? <span className="text-red-400">{j.error}</span> : (j.result?.avg_score != null ? `Score prom: ${j.result.avg_score}` : (j.result?.generated ? `${j.result.generated.length} generados` : '—'))}</td>
                </tr>
              ))}
              {!jobs.length && <tr><td colSpan={4} className="py-3 text-ink-500">Sin procesos.</td></tr>}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
