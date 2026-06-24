import React, { useState } from 'react'
import { ArrowRightLeft, Play, Download, AlertTriangle, Columns, GitCompare } from 'lucide-react'
import { DiffEditor } from '@monaco-editor/react'
import toast from 'react-hot-toast'
import { migrationApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { useCatalog } from '../../hooks/useCatalog'
import { Card, CardHeader, Button, Select, Badge } from '../../components/ui/primitives'
import AbapEditor from '../../components/AbapEditor'

export default function MigrationPage() {
  const { activeId } = useProject()
  const catalog = useCatalog()
  const [source, setSource] = useState('')
  const [target, setTarget] = useState('S4HANA')
  const [loading, setLoading] = useState(false)
  const [res, setRes] = useState(null)
  const [diff, setDiff] = useState(false)

  const migrate = async () => {
    if (!source.trim()) return toast.error('Pega el código ECC')
    setLoading(true)
    try {
      const { data } = await migrationApi.migrate({ source_code: source, target, project_id: activeId, save: !!activeId })
      setRes(data)
      toast.success(`Migrado · compatibilidad ${data.compatibility || '—'}`)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ArrowRightLeft className="h-7 w-7 text-neon-400" />
        <div>
          <h1 className="font-display text-2xl font-bold text-gradient">Migración ECC → S/4HANA / ABAP Cloud</h1>
          <p className="text-ink-400">Pega código ECC y obtén la versión modernizada con cada cambio explicado.</p>
        </div>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <Select label="Destino" value={target} onChange={(e) => setTarget(e.target.value)}
          options={(catalog?.migration_targets || []).map((t) => ({ value: t.key, label: t.label }))} className="max-w-md" />
        <Button onClick={migrate} loading={loading}><Play className="h-4 w-4" /> Migrar</Button>
        {res && (
          <Button variant="secondary" onClick={() => setDiff((d) => !d)}>
            {diff ? <Columns className="h-4 w-4" /> : <GitCompare className="h-4 w-4" />} {diff ? 'Lado a lado' : 'Ver diff'}
          </Button>
        )}
        {res?.id && (
          <a href={`/api/exports/migration/${res.id}.pdf`} target="_blank" rel="noreferrer">
            <Button variant="secondary"><Download className="h-4 w-4" /> Informe PDF</Button>
          </a>
        )}
      </div>

      {diff && res ? (
        <Card>
          <CardHeader title="Diff ECC → S/4" subtitle="Izquierda: ECC original · Derecha: migrado" icon={GitCompare} />
          <div className="p-4">
            <div className="overflow-hidden rounded-lg border border-white/10">
              <DiffEditor height="460px" theme="vs-dark" language="abap"
                original={source} modified={res.migrated_code || ''}
                options={{ readOnly: true, renderSideBySide: true, fontSize: 12, minimap: { enabled: false } }} />
            </div>
          </div>
        </Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader title="Código ECC (origen)" />
            <div className="p-4"><AbapEditor value={source} onChange={(v) => setSource(v || '')} height="440px" /></div>
          </Card>
          <Card>
            <CardHeader title="Código migrado"
              action={res && <Badge tone={res.compatibility === 'ok' ? 'baja' : res.compatibility === 'parcial' ? 'media' : 'critica'}>{res.compatibility}</Badge>} />
            <div className="p-4">
              {res ? <AbapEditor value={res.migrated_code || ''} readOnly height="440px" />
                : <div className="flex h-[440px] items-center justify-center text-ink-600">El código migrado aparecerá aquí.</div>}
            </div>
          </Card>
        </div>
      )}

      {res && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader title={`Cambios aplicados (${res.changes?.length || 0})`} />
            <div className="max-h-96 space-y-2 overflow-auto p-5">
              {(res.changes || []).map((ch, i) => (
                <div key={i} className="rounded-lg border border-white/5 bg-white/[0.02] p-3 text-sm">
                  <Badge tone="info">{ch.area}</Badge>
                  <p className="mt-1 text-ink-300">{ch.reason}</p>
                  <p className="mt-1 font-mono text-xs text-red-300/80">- {ch.before}</p>
                  <p className="font-mono text-xs text-emerald-300/80">+ {ch.after}</p>
                </div>
              ))}
              {!res.changes?.length && <p className="text-sm text-ink-500">Sin cambios listados.</p>}
            </div>
          </Card>
          <Card>
            <CardHeader title="Simplification items y pasos manuales" icon={AlertTriangle} />
            <div className="space-y-3 p-5">
              {(res.simplification_items || []).map((s, i) => (
                <div key={i} className="rounded-lg border border-amber-400/20 bg-amber-500/5 p-3 text-sm">
                  <b className="text-amber-300">{s.item}</b> <span className="font-mono text-xs text-ink-400">{s.table}</span>
                  <p className="text-ink-300">{s.note}</p>
                </div>
              ))}
              {res.manual_steps?.length > 0 && (
                <div>
                  <p className="mb-1 text-sm font-semibold text-ink-200">Pasos manuales</p>
                  <ul className="list-disc pl-5 text-sm text-ink-300">{res.manual_steps.map((m, i) => <li key={i}>{m}</li>)}</ul>
                </div>
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
