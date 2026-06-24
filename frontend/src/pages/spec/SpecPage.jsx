import React, { useState } from 'react'
import { FileText, Sparkles, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { generationApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Textarea, Badge } from '../../components/ui/primitives'
import SapContextForm from '../../components/SapContextForm'

function List({ title, items }) {
  if (!items?.length) return null
  return (
    <div className="rounded-lg border border-ink-800 bg-ink-950/40 p-3">
      <p className="mb-1 text-sm font-semibold text-brand-300">{title}</p>
      <ul className="list-disc pl-5 text-sm text-ink-300">{items.map((x, i) => <li key={i}>{x}</li>)}</ul>
    </div>
  )
}

function Block({ title, children }) {
  if (!children) return null
  return (
    <div className="rounded-lg border border-ink-800 bg-ink-950/40 p-3">
      <p className="mb-1 text-sm font-semibold text-brand-300">{title}</p>
      <p className="whitespace-pre-wrap text-sm text-ink-300">{children}</p>
    </div>
  )
}

export default function SpecPage() {
  const { activeId, active } = useProject()
  const [ctx, setCtx] = useState({ sap_version: active?.sap_version || 'S4HANA', complexity: 'media' })
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [spec, setSpec] = useState(null)

  const gen = async () => {
    if (!description.trim()) return toast.error('Describe el requerimiento')
    setLoading(true)
    try {
      const { data } = await generationApi.spec({ description, sap_context: ctx, project_id: activeId, save: false })
      setSpec(data)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <FileText className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Especificación Técnica</h1>
          <p className="text-ink-400">Diseño funcional y técnico generado por IA.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardHeader title="Requerimiento" />
          <div className="space-y-4 p-5">
            <SapContextForm value={ctx} onChange={setCtx} />
            <Textarea label="Descripción" rows={6} value={description} onChange={(e) => setDescription(e.target.value)} />
            <Button onClick={gen} loading={loading} className="w-full"><Sparkles className="h-4 w-4" /> Generar especificación</Button>
            {activeId && (
              <a href={`/api/exports/documentation/${activeId}.pdf`} target="_blank" rel="noreferrer" className="block">
                <Button variant="secondary" className="w-full"><Download className="h-4 w-4" /> Documentación completa del proyecto</Button>
              </a>
            )}
          </div>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader title="Especificación" />
          <div className="space-y-3 p-5">
            {!spec && <p className="text-sm text-ink-500">La especificación aparecerá aquí.</p>}
            {spec && (
              <>
                <Block title="Descripción funcional">{spec.functional_description}</Block>
                <Block title="Objetivo técnico">{spec.technical_objective}</Block>
                <List title="Supuestos" items={spec.assumptions} />
                <List title="Objetos SAP involucrados" items={spec.sap_objects} />
                <List title="Tablas estándar" items={spec.standard_tables} />
                <List title="BAPIs sugeridas" items={spec.suggested_bapis} />
                <List title="BAdIs / User-Exits" items={spec.badis_user_exits} />
                <List title="Riesgos" items={spec.risks} />
                <List title="Dependencias" items={spec.dependencies} />
                <Block title="Performance">{spec.performance_notes}</Block>
                <Block title="Seguridad">{spec.security_notes}</Block>
                <Block title="Plan de transporte">{spec.transport_plan}</Block>
                <Block title="Plan de rollback">{spec.rollback_plan}</Block>
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
