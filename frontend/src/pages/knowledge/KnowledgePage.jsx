import React, { useEffect, useState } from 'react'
import { Brain, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { clientsApi, knowledgeApi } from '../../services/api'
import { Card, CardHeader, Button, Input, Textarea, Select, Badge } from '../../components/ui/primitives'

const KINDS = [
  { value: 'z_object', label: 'Objeto Z (clase/report/FM)' },
  { value: 'ddic', label: 'Diccionario (tabla/estructura)' },
  { value: 'standard', label: 'Estándar / convención' },
  { value: 'snippet', label: 'Snippet de referencia' },
  { value: 'doc', label: 'Documento' },
]

export default function KnowledgePage() {
  const [clients, setClients] = useState([])
  const [clientId, setClientId] = useState('')
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ kind: 'z_object', title: '', content: '' })

  useEffect(() => { clientsApi.list().then((r) => { setClients(r.data); if (r.data[0]) setClientId(String(r.data[0].id)) }).catch(() => {}) }, [])
  const load = () => clientId && knowledgeApi.list(clientId).then((r) => setItems(r.data)).catch(() => {})
  useEffect(() => { load() }, [clientId])

  const add = async () => {
    if (!clientId) return toast.error('Selecciona un cliente')
    if (!form.title || !form.content) return toast.error('Título y contenido requeridos')
    try {
      await knowledgeApi.add({ client_id: Number(clientId), ...form })
      toast.success('Conocimiento agregado'); setForm({ kind: 'z_object', title: '', content: '' }); load()
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  const remove = async (id) => { await knowledgeApi.remove(id); load() }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Brain className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Memoria del Cliente (RAG)</h1>
          <p className="text-ink-400">El generador reutiliza estos objetos y estándares automáticamente.</p>
        </div>
      </div>

      <Select label="Cliente" value={clientId} onChange={(e) => setClientId(e.target.value)}
        options={clients.map((c) => ({ value: c.id, label: c.name }))} className="max-w-sm" />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Agregar conocimiento" icon={Plus} />
          <div className="space-y-3 p-5">
            <Select label="Tipo" value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })} options={KINDS} />
            <Input label="Título" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="ZCL_FI_TOOLS" />
            <Textarea label="Contenido" rows={8} value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })}
              placeholder="Pega la definición de la clase, la estructura de la tabla, el estándar de naming, etc." />
            <Button onClick={add} className="w-full">Agregar</Button>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title={`Conocimiento (${items.length})`} />
          <div className="space-y-2 p-5">
            {items.map((k) => (
              <div key={k.id} className="flex items-start justify-between rounded-lg border border-ink-800 p-3">
                <div>
                  <div className="flex items-center gap-2"><Badge tone="info">{k.kind}</Badge><span className="font-medium text-ink-100">{k.title}</span></div>
                  <p className="mt-1 text-xs text-ink-500">{k.preview}</p>
                </div>
                <button onClick={() => remove(k.id)} className="text-ink-500 hover:text-red-400"><Trash2 className="h-4 w-4" /></button>
              </div>
            ))}
            {!items.length && <p className="text-sm text-ink-500">Sin conocimiento aún para este cliente.</p>}
          </div>
        </Card>
      </div>
    </div>
  )
}
