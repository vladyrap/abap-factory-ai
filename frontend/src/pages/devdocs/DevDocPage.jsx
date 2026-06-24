import React, { useState } from 'react'
import { FileStack, Sparkles, Download, Boxes, ListOrdered } from 'lucide-react'
import toast from 'react-hot-toast'
import { devDocsApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Textarea, Badge } from '../../components/ui/primitives'
import SapContextForm from '../../components/SapContextForm'

const ACTION_TONE = { crear: 'baja', modificar: 'media', usar: 'info' }

export default function DevDocPage() {
  const { activeId, active } = useProject()
  const [ctx, setCtx] = useState({ sap_version: active?.sap_version || 'S4HANA', complexity: 'media' })
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [doc, setDoc] = useState(null)

  const generate = async () => {
    if (!description.trim()) return toast.error('Describe el desarrollo')
    setLoading(true)
    try {
      const { data } = await devDocsApi.generate({ description, sap_context: ctx, project_id: activeId, save: !!activeId })
      setDoc(data)
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <FileStack className="h-7 w-7 text-neon-400" />
        <div>
          <h1 className="font-display text-2xl font-bold text-gradient">Documento Técnico del Desarrollo</h1>
          <p className="text-ink-400">Cada objeto a crear/modificar con su nombre, y el paso a paso. Exportable a PDF.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardHeader title="Requerimiento" />
          <div className="space-y-4 p-5">
            <SapContextForm value={ctx} onChange={setCtx} />
            <Textarea label="Descripción del desarrollo" rows={6} value={description} onChange={(e) => setDescription(e.target.value)} />
            <Button onClick={generate} loading={loading} className="w-full"><Sparkles className="h-4 w-4" /> Generar documento</Button>
            {doc?.id && (
              <a href={`/api/exports/dev-doc/${doc.id}.pdf`} target="_blank" rel="noreferrer" className="block">
                <Button variant="secondary" className="w-full"><Download className="h-4 w-4" /> Descargar PDF paso a paso</Button>
              </a>
            )}
          </div>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader title={doc?.title || 'Documento'} subtitle={doc?.summary} />
          <div className="space-y-5 p-5">
            {!doc && <p className="text-sm text-ink-500">El documento técnico aparecerá aquí.</p>}
            {doc && (
              <>
                <div>
                  <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-brand-300"><Boxes className="h-4 w-4" /> Objetos ({doc.objects?.length || 0})</div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead><tr className="border-b border-white/10 text-left text-ink-400">
                        <th className="py-1.5">Acción</th><th>Nombre</th><th>Tipo</th><th>Paquete</th>
                      </tr></thead>
                      <tbody>
                        {(doc.objects || []).map((o, i) => (
                          <tr key={i} className="border-b border-white/5 align-top">
                            <td className="py-1.5"><Badge tone={ACTION_TONE[o.action] || 'default'}>{o.action}</Badge></td>
                            <td className="font-mono text-neon-300">{o.name}</td>
                            <td className="text-ink-300">{o.type}</td>
                            <td className="font-mono text-xs text-ink-400">{o.package || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div>
                  <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-brand-300"><ListOrdered className="h-4 w-4" /> Paso a paso</div>
                  <div className="space-y-2">
                    {(doc.steps || []).map((s, i) => (
                      <div key={i} className="rounded-lg border border-white/5 bg-white/[0.02] p-3 text-sm">
                        <p className="font-medium text-ink-100"><span className="text-neon-400">{s.n}.</span> {s.title}</p>
                        <p className="text-ink-400">{s.detail}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
