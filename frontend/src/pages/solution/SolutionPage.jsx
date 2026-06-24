import React, { useState, useRef } from 'react'
import { Sparkles, Upload, Wand2, FileInput, ChevronDown, ChevronUp, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { solutionApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Textarea, Badge } from '../../components/ui/primitives'
import AbapEditor from '../../components/AbapEditor'

const TYPE_LABEL = {
  nuevo_desarrollo: 'Desarrollo nuevo', correccion_bug: 'Corrección de bug',
  mejora_enhancement: 'Mejora / enhancement', fix_dump: 'Fix de dump',
  migracion: 'Migración', ajuste: 'Ajuste',
}
const TYPE_TONE = {
  nuevo_desarrollo: 'info', correccion_bug: 'critica', mejora_enhancement: 'media',
  fix_dump: 'alta', migracion: 'info', ajuste: 'media',
}

export default function SolutionPage() {
  const { activeId } = useProject()
  const [requirement, setRequirement] = useState('')
  const [existing, setExisting] = useState('')
  const [showExisting, setShowExisting] = useState(false)
  const [loading, setLoading] = useState(false)
  const [res, setRes] = useState(null)
  const fileRef = useRef()

  const onFile = (e) => {
    const f = e.target.files?.[0]
    if (!f) return
    if (f.size > 2 * 1024 * 1024) return toast.error('Archivo muy grande (máx 2MB de texto)')
    const reader = new FileReader()
    reader.onload = () => setRequirement(String(reader.result || ''))
    reader.readAsText(f)
    toast.success(`Cargado: ${f.name}`)
  }

  const resolve = async () => {
    if (!requirement.trim()) return toast.error('Pega o sube el requerimiento funcional')
    setLoading(true); setRes(null)
    try {
      const { data } = await solutionApi.build({
        requirement_text: requirement, existing_code: existing || null,
        project_id: activeId, save: !!activeId,
      })
      setRes(data)
      toast.success(`Resuelto: ${TYPE_LABEL[data.solution_type] || data.solution_type}`)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally { setLoading(false) }
  }

  const cls = res?.classification

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Wand2 className="h-7 w-7 text-neon-400" />
        <div>
          <h1 className="font-display text-2xl font-bold text-gradient">Requerimiento → Solución</h1>
          <p className="text-ink-400">Pega o sube un requerimiento funcional; el sistema decide qué hacer y lo resuelve.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardHeader title="Requerimiento funcional" icon={FileInput} action={
            <>
              <input ref={fileRef} type="file" accept=".txt,.md,.csv,.log" className="hidden" onChange={onFile} />
              <Button variant="ghost" onClick={() => fileRef.current?.click()}><Upload className="h-4 w-4" /> Subir</Button>
            </>
          } />
          <div className="space-y-4 p-5">
            <Textarea rows={10} value={requirement} onChange={(e) => setRequirement(e.target.value)}
              placeholder="Pega aquí el correo, acta o especificación funcional. Ej: 'Cuando se graba un pedido con monto > X debe validar el centro de costo y mostrar error si...'" />

            <button onClick={() => setShowExisting((s) => !s)} className="flex items-center gap-1 text-sm text-ink-400 hover:text-ink-200">
              {showExisting ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              Código existente o dump (opcional — para fix/migración/corrección)
            </button>
            {showExisting && (
              <Textarea rows={8} value={existing} onChange={(e) => setExisting(e.target.value)}
                className="font-mono text-xs" placeholder="Pega el código a corregir/migrar, o el dump ST22…" />
            )}

            <Button onClick={resolve} loading={loading} className="w-full"><Sparkles className="h-4 w-4" /> Resolver</Button>
          </div>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader
            title={res?.object_name || 'Solución'}
            subtitle={cls?.title}
            action={
              <div className="flex items-center gap-2">
                {res && <Badge tone={TYPE_TONE[res.solution_type] || 'info'}>{TYPE_LABEL[res.solution_type] || res.solution_type}</Badge>}
                {res?.lint && <Badge tone={res.lint.score >= 80 ? 'baja' : res.lint.score >= 50 ? 'media' : 'critica'}>Calidad {res.lint.score}</Badge>}
                {res?.artifact_id && (
                  <a href={`/api/exports/artifact/${res.artifact_id}.abap`} target="_blank" rel="noreferrer">
                    <Button variant="secondary"><Download className="h-4 w-4" /> .abap</Button>
                  </a>
                )}
              </div>
            }
          />
          <div className="space-y-4 p-5">
            {!res && <p className="text-sm text-ink-500">La solución aparecerá aquí: tipo detectado, plan, código y explicación.</p>}
            {res && (
              <>
                {cls?.reasoning && (
                  <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 text-sm text-ink-300">
                    <span className="font-semibold text-neon-400">Diagnóstico:</span> {cls.reasoning}
                  </div>
                )}
                {cls?.steps?.length > 0 && (
                  <div>
                    <p className="mb-1 text-sm font-semibold text-brand-300">Plan</p>
                    <ol className="list-decimal space-y-1 pl-5 text-sm text-ink-300">{cls.steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
                  </div>
                )}
                {res.code && <AbapEditor value={res.code} readOnly height="300px" />}
                {res.changes?.length > 0 && (
                  <div className="rounded-lg border border-white/10 p-3">
                    <p className="mb-1 text-sm font-semibold text-brand-300">Cambios</p>
                    {res.changes.map((ch, i) => (
                      <div key={i} className="border-b border-white/5 py-1 text-xs last:border-0">
                        <p className="text-ink-400">{ch.reason}</p>
                        {ch.before && <p className="font-mono text-red-300/80">- {ch.before}</p>}
                        {ch.after && <p className="font-mono text-emerald-300/80">+ {ch.after}</p>}
                      </div>
                    ))}
                  </div>
                )}
                {res.explanation && (
                  <div className="rounded-lg border border-white/10 bg-ink-950/50 p-4 text-sm text-ink-300">
                    <p className="mb-1 font-semibold text-brand-300">Explicación</p>
                    <p className="whitespace-pre-wrap">{res.explanation}</p>
                  </div>
                )}
                {res.confidence_notes?.length > 0 && (
                  <div className="rounded-lg border border-amber-400/20 bg-amber-500/5 p-3">
                    <p className="mb-1 text-sm font-semibold text-amber-300">Verificar en sistema</p>
                    {res.confidence_notes.map((n, i) => (
                      <p key={i} className="text-xs text-ink-300"><b>{n.item}</b> — {n.reason}</p>
                    ))}
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
