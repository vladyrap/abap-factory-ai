import React, { useState, useEffect } from 'react'
import { ShieldCheck, Play, Download, FileCode } from 'lucide-react'
import toast from 'react-hot-toast'
import { inspectorApi, generationApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Badge, Select } from '../../components/ui/primitives'
import AbapEditor from '../../components/AbapEditor'

function ScoreRing({ score }) {
  const tone = score >= 80 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : 'text-red-400'
  return (
    <div className="flex flex-col items-center">
      <div className={`text-4xl font-bold ${tone}`}>{Math.round(score)}</div>
      <div className="text-xs text-ink-500">/ 100</div>
    </div>
  )
}

export default function InspectorPage() {
  const { activeId } = useProject()
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [res, setRes] = useState(null)
  const [artifacts, setArtifacts] = useState([])
  const [artifactId, setArtifactId] = useState('')

  useEffect(() => {
    generationApi.artifacts(activeId).then((r) => setArtifacts(r.data)).catch(() => {})
  }, [activeId])

  const loadArtifact = async (id) => {
    setArtifactId(id)
    if (!id) return
    const { data } = await generationApi.artifact(id)
    setCode(data.code)
    toast.success(`Cargado: ${data.name}`)
  }

  const inspect = async () => {
    if (!code.trim()) return toast.error('Pega código ABAP')
    setLoading(true)
    try {
      const { data } = await inspectorApi.inspect({ source_code: code, project_id: activeId, save: !!activeId })
      setRes(data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ShieldCheck className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Code Inspector / ATC Advisor</h1>
          <p className="text-ink-400">Calidad, performance, seguridad y compatibilidad S/4HANA.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Código a revisar" subtitle="Carga un artefacto creado o pega tu propio código" icon={FileCode} />
          <div className="space-y-4 p-4">
            <Select value={artifactId} onChange={(e) => loadArtifact(e.target.value)}
              options={[{ value: '', label: '— Pegar código manualmente —' },
                        ...artifacts.map((a) => ({ value: a.id, label: `${a.name} (v${a.version})` }))]} />
            <AbapEditor value={code} onChange={(v) => setCode(v || '')} height="380px" />
            <Button onClick={inspect} loading={loading} className="w-full"><Play className="h-4 w-4" /> Inspeccionar</Button>
          </div>
        </Card>

        <Card>
          <CardHeader title="Resultado"
            action={res?.id && (
              <a href={`/api/exports/inspection/${res.id}.pdf`} target="_blank" rel="noreferrer">
                <Button variant="secondary"><Download className="h-4 w-4" /> PDF</Button>
              </a>
            )} />
          <div className="space-y-4 p-5">
            {!res && <p className="text-sm text-ink-500">El informe aparecerá aquí.</p>}
            {res && (
              <>
                <div className="flex items-center justify-between rounded-lg border border-ink-800 bg-ink-950/40 p-4">
                  <ScoreRing score={res.score || 0} />
                  <div className="text-right">
                    <p className="text-sm text-ink-400">Compatibilidad S/4HANA</p>
                    <Badge tone={res.s4hana_compatible === 'si' ? 'baja' : res.s4hana_compatible === 'parcial' ? 'media' : 'critica'}>
                      {res.s4hana_compatible || '—'}
                    </Badge>
                  </div>
                </div>
                <div>
                  <p className="mb-2 text-sm font-semibold text-ink-200">Hallazgos ({res.findings?.length || 0})</p>
                  <div className="space-y-2">
                    {(res.findings || []).map((f, i) => (
                      <div key={i} className="rounded-lg border border-ink-800 p-3 text-sm">
                        <div className="mb-1 flex items-center gap-2">
                          <Badge tone={f.severity}>{f.severity}</Badge>
                          <span className="font-mono text-xs text-ink-400">{f.rule} · L{f.line}</span>
                        </div>
                        <p className="text-ink-200">{f.message}</p>
                        {f.suggestion && <p className="mt-1 text-ink-400">💡 {f.suggestion}</p>}
                      </div>
                    ))}
                  </div>
                </div>
                {res.recommendation && (
                  <div className="rounded-lg border border-brand-800/40 bg-brand-900/10 p-4 text-sm text-ink-300">
                    {res.recommendation}
                  </div>
                )}
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
