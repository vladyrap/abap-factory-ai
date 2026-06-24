import React, { useState } from 'react'
import { Bug, Search, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { dumpsApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Textarea, Badge } from '../../components/ui/primitives'
import AbapEditor from '../../components/AbapEditor'

export default function DumpsPage() {
  const { activeId } = useProject()
  const [raw, setRaw] = useState('')
  const [loading, setLoading] = useState(false)
  const [res, setRes] = useState(null)

  const analyze = async () => {
    if (!raw.trim()) return toast.error('Pega el dump de ST22')
    setLoading(true)
    try {
      const { data } = await dumpsApi.analyze({ raw_dump: raw, project_id: activeId, save: !!activeId })
      setRes(data)
      toast.success('Dump analizado')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Bug className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Analizador de Dumps (ST22)</h1>
          <p className="text-ink-400">Pega el dump y obtén causa raíz, solución y código corregido.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Dump ST22" />
          <div className="space-y-4 p-5">
            <Textarea rows={16} value={raw} onChange={(e) => setRaw(e.target.value)}
              className="font-mono text-xs" placeholder="Pega aquí el dump completo de ST22…" />
            <Button onClick={analyze} loading={loading} className="w-full"><Search className="h-4 w-4" /> Analizar</Button>
          </div>
        </Card>

        <Card>
          <CardHeader
            title="Análisis"
            action={res?.id && (
              <a href={`/api/exports/dump/${res.id}.pdf`} target="_blank" rel="noreferrer">
                <Button variant="secondary"><Download className="h-4 w-4" /> PDF</Button>
              </a>
            )}
          />
          <div className="space-y-4 p-5">
            {!res && <p className="text-sm text-ink-500">El análisis aparecerá aquí.</p>}
            {res && (
              <>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone={res.severity}>{res.severity}</Badge>
                  <span className="font-mono text-sm text-brand-300">{res.dump_type}</span>
                </div>
                <div className="text-sm text-ink-400">
                  <p><b className="text-ink-200">Programa:</b> {res.program || '—'} · <b className="text-ink-200">Include:</b> {res.include || '—'} · <b className="text-ink-200">Línea:</b> {res.line || '—'}</p>
                </div>
                <Section title="Causa raíz">{res.root_cause}</Section>
                <Section title="Solución">{res.solution}</Section>
                {res.fixed_code && (
                  <div>
                    <p className="mb-1 text-sm font-semibold text-ink-200">Código corregido</p>
                    <AbapEditor value={res.fixed_code} readOnly height="220px" />
                  </div>
                )}
                {res.checklist?.length > 0 && (
                  <Section title="Checklist de revisión">
                    <ul className="list-disc pl-5">{res.checklist.map((c, i) => <li key={i}>{c}</li>)}</ul>
                  </Section>
                )}
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div className="rounded-lg border border-ink-800 bg-ink-950/40 p-3">
      <p className="mb-1 text-sm font-semibold text-brand-300">{title}</p>
      <div className="whitespace-pre-wrap text-sm text-ink-300">{children}</div>
    </div>
  )
}
