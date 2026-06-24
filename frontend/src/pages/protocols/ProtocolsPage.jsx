import React, { useEffect, useState } from 'react'
import { ClipboardList, Plus, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { testsApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { useCatalog } from '../../hooks/useCatalog'
import { Card, CardHeader, Button, Textarea, Select, Input, Badge } from '../../components/ui/primitives'

export default function ProtocolsPage() {
  const { activeId } = useProject()
  const catalog = useCatalog()
  const [list, setList] = useState([])
  const [form, setForm] = useState({ name: '', protocol_type: 'funcional', description: '' })
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null)

  const reload = () => testsApi.protocols(activeId).then((r) => setList(r.data)).catch(() => {})
  useEffect(() => { reload() }, [activeId])

  const create = async () => {
    if (!form.description.trim()) return toast.error('Describe el desarrollo a probar')
    setLoading(true)
    try {
      const { data } = await testsApi.protocol({ ...form, project_id: activeId, save: !!activeId })
      setSelected(data)
      toast.success('Protocolo generado')
      reload()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ClipboardList className="h-7 w-7 text-brand-400" />
        <h1 className="text-2xl font-bold text-ink-50">Protocolos de Prueba</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Nuevo protocolo" icon={Plus} />
          <div className="space-y-3 p-5">
            <Input label="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <Select label="Tipo" value={form.protocol_type} onChange={(e) => setForm({ ...form, protocol_type: e.target.value })}
              options={catalog?.protocol_types || []} />
            <Textarea label="Descripción del desarrollo" rows={5} value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })} />
            <Button onClick={create} loading={loading} className="w-full">Generar casos</Button>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title={selected ? `Casos (${selected.cases?.length || 0})` : 'Protocolos guardados'}
            action={selected?.id && (
              <a href={`/api/exports/protocol/${selected.id}.xlsx`} target="_blank" rel="noreferrer">
                <Button variant="secondary"><Download className="h-4 w-4" /> Excel</Button>
              </a>
            )} />
          <div className="p-5">
            {selected ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead><tr className="border-b border-ink-800 text-left text-ink-400">
                    <th className="py-2 pr-3">ID</th><th className="pr-3">Caso</th><th className="pr-3">Esperado</th><th>Estado</th>
                  </tr></thead>
                  <tbody>
                    {(selected.cases || []).map((c, i) => (
                      <tr key={i} className="border-b border-ink-900 align-top">
                        <td className="py-2 pr-3 font-mono text-xs text-brand-300">{c.case_id}</td>
                        <td className="pr-3 text-ink-200">{c.name}</td>
                        <td className="pr-3 text-ink-400">{c.expected_result}</td>
                        <td><Badge tone="media">{c.status || 'pendiente'}</Badge></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : list.length ? (
              <div className="space-y-2">
                {list.map((p) => (
                  <button key={p.id} onClick={() => testsApi.getProtocol(p.id).then((r) => setSelected(r.data))}
                    className="flex w-full items-center justify-between rounded-lg border border-ink-800 p-3 text-left hover:bg-ink-800">
                    <span className="text-ink-200">{p.name}</span>
                    <Badge>{p.protocol_type}</Badge>
                  </button>
                ))}
              </div>
            ) : <p className="text-sm text-ink-500">Aún no hay protocolos.</p>}
          </div>
        </Card>
      </div>
    </div>
  )
}
