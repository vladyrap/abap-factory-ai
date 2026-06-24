import React, { useState } from 'react'
import { Workflow, Check, Loader2, Sparkles, Bug, Download, FileText, ShieldCheck, FlaskConical } from 'lucide-react'
import toast from 'react-hot-toast'
import {
  projectsApi, generationApi, testsApi, inspectorApi, dumpsApi,
} from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Textarea, Input, Badge } from '../../components/ui/primitives'
import SapContextForm from '../../components/SapContextForm'
import AbapEditor from '../../components/AbapEditor'

const STEPS = ['Contexto', 'Requerimiento', 'Generación', 'Dump', 'Exportar']

export default function WizardPage() {
  const { activeId, active } = useProject()
  const [step, setStep] = useState(0)
  const [ctx, setCtx] = useState({ sap_version: active?.sap_version || 'S4HANA', complexity: 'media', environment: 'DEV' })
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [progress, setProgress] = useState([])      // [{label, status}]
  const [result, setResult] = useState(null)         // {requirementId, spec, artifact, code, tests, inspection}
  const [dump, setDump] = useState('')
  const [dumpRes, setDumpRes] = useState(null)
  const [busy, setBusy] = useState(false)

  const mark = (label, status) =>
    setProgress((p) => {
      const i = p.findIndex((x) => x.label === label)
      if (i === -1) return [...p, { label, status }]
      const copy = [...p]; copy[i] = { label, status }; return copy
    })

  const runFlow = async () => {
    if (!activeId) return toast.error('Selecciona un proyecto activo arriba')
    if (!title.trim() || !description.trim()) return toast.error('Completa título y descripción')
    setBusy(true); setProgress([]); setResult(null); setStep(2)
    try {
      // Requerimiento
      mark('Creando requerimiento', 'run')
      const { data: req } = await projectsApi.createRequirement({
        project_id: activeId, title, description, sap_version: ctx.sap_version,
        module: ctx.module, dev_type: ctx.dev_type, complexity: ctx.complexity,
      })
      mark('Creando requerimiento', 'done')

      // Spec
      mark('Diseño técnico (spec)', 'run')
      const { data: spec } = await generationApi.spec({
        description, sap_context: ctx, project_id: activeId, requirement_id: req.id, save: true,
      })
      mark('Diseño técnico (spec)', 'done')

      // Código
      mark('Generando código ABAP', 'run')
      const { data: gen } = await generationApi.code({
        description, sap_context: ctx, project_id: activeId, requirement_id: req.id, save: true,
      })
      mark('Generando código ABAP', 'done')

      // Pruebas + Inspector en paralelo
      mark('Pruebas ABAP Unit', 'run')
      mark('Code Inspector', 'run')
      const [testsR, insR] = await Promise.allSettled([
        testsApi.unit({ source_code: gen.code, sap_context: ctx, project_id: activeId, code_artifact_id: gen.artifact?.id, save: true }),
        inspectorApi.inspect({ source_code: gen.code, sap_context: ctx, project_id: activeId, code_artifact_id: gen.artifact?.id, save: true }),
      ])
      mark('Pruebas ABAP Unit', testsR.status === 'fulfilled' ? 'done' : 'err')
      mark('Code Inspector', insR.status === 'fulfilled' ? 'done' : 'err')

      setResult({
        requirementId: req.id,
        spec, artifact: gen.artifact, code: gen.code, explanation: gen.explanation,
        tests: testsR.status === 'fulfilled' ? testsR.value.data : null,
        inspection: insR.status === 'fulfilled' ? insR.value.data : null,
      })
      toast.success('Flujo completado')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error en el flujo')
    } finally {
      setBusy(false)
    }
  }

  const analyzeDump = async () => {
    if (!dump.trim()) return toast.error('Pega el dump')
    setBusy(true)
    try {
      const { data } = await dumpsApi.analyze({ raw_dump: dump, project_id: activeId, save: true })
      setDumpRes(data)
      toast.success('Dump analizado')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally { setBusy(false) }
  }

  const applyFix = async () => {
    if (!result?.artifact || !dumpRes?.fixed_code) return
    try {
      const { data } = await generationApi.edit(result.artifact.id, {
        code: dumpRes.fixed_code, explanation: `Corrección de dump ${dumpRes.dump_type}`,
      })
      setResult((r) => ({ ...r, artifact: data, code: data.code }))
      toast.success(`Nueva versión v${data.version} creada`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Workflow className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Flujo de Desarrollo Guiado</h1>
          <p className="text-ink-400">Contexto → Requerimiento → Generación → Dump → Exportar</p>
        </div>
      </div>

      {/* Stepper */}
      <div className="flex items-center gap-2">
        {STEPS.map((s, i) => (
          <button key={s} onClick={() => setStep(i)}
            className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm ${i === step ? 'bg-brand-600 text-white' : i < step ? 'bg-ink-800 text-emerald-400' : 'bg-ink-900 text-ink-500'}`}>
            {i < step ? <Check className="h-4 w-4" /> : <span className="font-mono">{i + 1}</span>} {s}
          </button>
        ))}
      </div>

      {step <= 1 && (
        <Card>
          <CardHeader title="Paso 1 y 2 · Contexto y requerimiento" subtitle={active ? `Proyecto: ${active.name}` : 'Selecciona un proyecto activo arriba'} />
          <div className="space-y-4 p-5">
            <SapContextForm value={ctx} onChange={setCtx} />
            <Input label="Título del requerimiento" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ej: Report de partidas abiertas FI" />
            <Textarea label="Descripción" rows={5} value={description} onChange={(e) => setDescription(e.target.value)} />
            <Button onClick={runFlow} loading={busy}><Sparkles className="h-4 w-4" /> Ejecutar flujo completo</Button>
          </div>
        </Card>
      )}

      {step === 2 && (
        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <CardHeader title="Progreso" />
            <div className="space-y-2 p-5">
              {progress.length === 0 && <p className="text-sm text-ink-500">Ejecuta el flujo en el paso 1.</p>}
              {progress.map((p) => (
                <div key={p.label} className="flex items-center gap-2 text-sm">
                  {p.status === 'run' && <Loader2 className="h-4 w-4 animate-spin text-brand-400" />}
                  {p.status === 'done' && <Check className="h-4 w-4 text-emerald-400" />}
                  {p.status === 'err' && <span className="text-red-400">✕</span>}
                  <span className="text-ink-300">{p.label}</span>
                </div>
              ))}
              {result && (
                <div className="mt-4 flex flex-col gap-2">
                  <Button variant="secondary" onClick={() => setStep(3)}><Bug className="h-4 w-4" /> Ir a Dump</Button>
                  <Button variant="secondary" onClick={() => setStep(4)}><Download className="h-4 w-4" /> Ir a Exportar</Button>
                </div>
              )}
            </div>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader title={result?.artifact?.name || 'Resultado'} subtitle={result && 'Código + spec + pruebas + calidad'} />
            <div className="space-y-4 p-5">
              {!result && <p className="text-sm text-ink-500">Los resultados aparecerán aquí.</p>}
              {result && (
                <>
                  <AbapEditor value={result.code} readOnly height="280px" />
                  <div className="grid gap-3 sm:grid-cols-3">
                    <MiniCard icon={ShieldCheck} label="Score calidad" value={result.inspection?.score ?? '—'} />
                    <MiniCard icon={FlaskConical} label="Casos de prueba" value={result.tests?.cases?.length ?? '—'} />
                    <MiniCard icon={FileText} label="Riesgos" value={result.spec?.risks?.length ?? '—'} />
                  </div>
                  {result.spec?.risks?.length > 0 && (
                    <div className="rounded-lg border border-ink-800 p-3">
                      <p className="mb-1 text-sm font-semibold text-brand-300">Riesgos detectados</p>
                      <ul className="list-disc pl-5 text-sm text-ink-300">{result.spec.risks.map((r, i) => <li key={i}>{r}</li>)}</ul>
                    </div>
                  )}
                </>
              )}
            </div>
          </Card>
        </div>
      )}

      {step === 3 && (
        <Card>
          <CardHeader title="Paso 4 y 5 · Analizar dump y corregir" />
          <div className="grid gap-4 p-5 lg:grid-cols-2">
            <div className="space-y-3">
              <Textarea rows={12} value={dump} onChange={(e) => setDump(e.target.value)} className="font-mono text-xs" placeholder="Pega un dump ST22 relacionado…" />
              <Button onClick={analyzeDump} loading={busy}><Bug className="h-4 w-4" /> Analizar</Button>
            </div>
            <div className="space-y-3">
              {!dumpRes && <p className="text-sm text-ink-500">El análisis aparecerá aquí.</p>}
              {dumpRes && (
                <>
                  <div className="flex items-center gap-2"><Badge tone={dumpRes.severity}>{dumpRes.severity}</Badge><span className="font-mono text-sm text-brand-300">{dumpRes.dump_type}</span></div>
                  <p className="text-sm text-ink-300">{dumpRes.root_cause}</p>
                  {dumpRes.fixed_code && <AbapEditor value={dumpRes.fixed_code} readOnly height="200px" />}
                  {result?.artifact && dumpRes.fixed_code && (
                    <Button onClick={applyFix}><Sparkles className="h-4 w-4" /> Aplicar como nueva versión</Button>
                  )}
                </>
              )}
            </div>
          </div>
        </Card>
      )}

      {step === 4 && (
        <Card>
          <CardHeader title="Paso 6 · Exportar documentación" />
          <div className="flex flex-wrap gap-3 p-5">
            {result?.artifact && (
              <a href={`/api/exports/artifact/${result.artifact.id}.abap`} target="_blank" rel="noreferrer">
                <Button variant="secondary"><Download className="h-4 w-4" /> Código .abap</Button>
              </a>
            )}
            {result?.spec?.id && (
              <a href={`/api/exports/spec/${result.spec.id}.pdf`} target="_blank" rel="noreferrer">
                <Button variant="secondary"><FileText className="h-4 w-4" /> Spec PDF</Button>
              </a>
            )}
            {activeId && (
              <a href={`/api/exports/documentation/${activeId}.pdf${result?.requirementId ? `?requirement_id=${result.requirementId}` : ''}`} target="_blank" rel="noreferrer">
                <Button><Download className="h-4 w-4" /> Documentación completa (PDF)</Button>
              </a>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}

function MiniCard({ icon: Icon, label, value }) {
  return (
    <div className="rounded-lg border border-ink-800 bg-ink-950/40 p-3">
      <div className="flex items-center gap-2 text-ink-400"><Icon className="h-4 w-4" /><span className="text-xs">{label}</span></div>
      <p className="mt-1 text-xl font-bold text-ink-50">{value}</p>
    </div>
  )
}
