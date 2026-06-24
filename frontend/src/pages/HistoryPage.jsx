import React, { useEffect, useState } from 'react'
import { History, Download, CheckCircle2, GitCompare } from 'lucide-react'
import { DiffEditor } from '@monaco-editor/react'
import toast from 'react-hot-toast'
import { generationApi } from '../services/api'
import { useProject } from '../context/ProjectContext'
import { useAuth } from '../context/AuthContext'
import { Card, CardHeader, Badge, Button } from '../components/ui/primitives'
import AbapEditor from '../components/AbapEditor'

export default function HistoryPage() {
  const { activeId } = useProject()
  const { can } = useAuth()
  const [artifacts, setArtifacts] = useState([])
  const [sel, setSel] = useState(null)
  const [versions, setVersions] = useState([])
  const [showDiff, setShowDiff] = useState(false)

  const reload = () => generationApi.artifacts(activeId).then((r) => setArtifacts(r.data)).catch(() => {})
  useEffect(() => { reload() }, [activeId])

  const open = async (id) => {
    const { data } = await generationApi.artifact(id)
    setSel(data); setShowDiff(false)
    generationApi.versions(id).then((r) => setVersions(r.data)).catch(() => setVersions([]))
  }

  const approve = async () => {
    try {
      const { data } = await generationApi.approve(sel.id)
      setSel(data); reload(); toast.success('Artefacto aprobado')
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  // versión previa para el diff (parent en la cadena)
  const parent = versions.find((v) => v.id === sel?.parent_id)

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <History className="h-7 w-7 text-brand-400" />
        <h1 className="text-2xl font-bold text-ink-50">Historial de Generaciones</h1>
      </div>
      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title={`Artefactos (${artifacts.length})`} />
          <div className="max-h-[600px] space-y-2 overflow-auto p-4">
            {artifacts.map((a) => (
              <button key={a.id} onClick={() => open(a.id)}
                className={`flex w-full items-center justify-between rounded-lg border p-3 text-left text-sm hover:bg-ink-800 ${sel?.id === a.id ? 'border-brand-600 bg-ink-800' : 'border-ink-800'}`}>
                <div>
                  <p className="font-medium text-ink-100">{a.name}</p>
                  <p className="text-xs text-ink-500">v{a.version} · {a.dev_type || 'código'}</p>
                </div>
                <Badge tone={a.status === 'approved' ? 'baja' : 'default'}>{a.status}</Badge>
              </button>
            ))}
            {!artifacts.length && <p className="text-sm text-ink-500">Sin generaciones aún.</p>}
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader
            title={sel?.name || 'Detalle'}
            subtitle={sel && `${sel.language} · v${sel.version} · ${sel.status}`}
            action={sel && (
              <div className="flex gap-2">
                {parent && (
                  <Button variant="ghost" onClick={() => setShowDiff((s) => !s)}>
                    <GitCompare className="h-4 w-4" /> {showDiff ? 'Código' : 'Diff'}
                  </Button>
                )}
                {can('approve') && sel.status !== 'approved' && (
                  <Button variant="secondary" onClick={approve}><CheckCircle2 className="h-4 w-4" /> Aprobar</Button>
                )}
                <a href={`/api/exports/artifact/${sel.id}.abap`} target="_blank" rel="noreferrer">
                  <Button variant="secondary"><Download className="h-4 w-4" /> .abap</Button>
                </a>
              </div>
            )}
          />
          <div className="p-5">
            {!sel && <p className="text-sm text-ink-500">Selecciona un artefacto.</p>}
            {sel && (
              <>
                {versions.length > 1 && (
                  <div className="mb-3 flex flex-wrap gap-1">
                    {versions.map((v) => (
                      <button key={v.id} onClick={() => open(v.id)}
                        className={`rounded px-2 py-1 text-xs ${v.id === sel.id ? 'bg-brand-600 text-white' : 'bg-ink-800 text-ink-300'}`}>
                        v{v.version}{v.status === 'approved' ? ' ✓' : ''}
                      </button>
                    ))}
                  </div>
                )}
                {showDiff && parent ? (
                  <div className="overflow-hidden rounded-lg border border-ink-700">
                    <DiffEditor height="380px" theme="vs-dark" language="abap"
                      original={parent.code} modified={sel.code}
                      options={{ readOnly: true, renderSideBySide: true, fontSize: 12, minimap: { enabled: false } }} />
                  </div>
                ) : (
                  <AbapEditor value={sel.code} readOnly height="380px" />
                )}
                {sel.explanation && <p className="mt-4 whitespace-pre-wrap text-sm text-ink-300">{sel.explanation}</p>}
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
