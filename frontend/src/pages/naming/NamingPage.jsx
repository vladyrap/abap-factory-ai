import React, { useEffect, useState } from 'react'
import { Tags, Plus, Trash2, Eye } from 'lucide-react'
import toast from 'react-hot-toast'
import { clientsApi, namingApi } from '../../services/api'
import { Card, CardHeader, Button, Input, Select, Badge } from '../../components/ui/primitives'

export default function NamingPage() {
  const [clients, setClients] = useState([])
  const [clientId, setClientId] = useState('')
  const [types, setTypes] = useState([])
  const [rules, setRules] = useState([])
  const [form, setForm] = useState({ object_type: 'table', pattern: 'Z{MODULE}_{NAME}', description: '' })
  const [preview, setPreview] = useState('')

  useEffect(() => {
    clientsApi.list().then((r) => { setClients(r.data); if (r.data[0]) setClientId(String(r.data[0].id)) }).catch(() => {})
    namingApi.objectTypes().then((r) => setTypes(r.data)).catch(() => {})
  }, [])
  const load = () => clientId && namingApi.list(clientId).then((r) => setRules(r.data)).catch(() => {})
  useEffect(() => { load() }, [clientId])

  // Preview en vivo del patrón
  useEffect(() => {
    if (!form.pattern) return setPreview('')
    namingApi.preview(form.pattern, { MODULE: 'FI', AREA: 'FI', NAME: 'ejemplo' })
      .then((r) => setPreview(r.data.name)).catch(() => setPreview(''))
  }, [form.pattern])

  const save = async () => {
    if (!clientId) return toast.error('Selecciona un cliente')
    try {
      await namingApi.save({ client_id: Number(clientId), ...form })
      toast.success('Regla guardada'); load()
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }
  const remove = async (id) => { await namingApi.remove(id); load() }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Tags className="h-7 w-7 text-neon-400" />
        <div>
          <h1 className="font-display text-2xl font-bold text-gradient">Nomenclaturas dinámicas</h1>
          <p className="text-ink-400">Cada empresa define sus patrones; el generador los aplica automáticamente.</p>
        </div>
      </div>

      <Select label="Cliente" value={clientId} onChange={(e) => setClientId(e.target.value)}
        options={clients.map((c) => ({ value: c.id, label: c.name }))} className="max-w-sm" />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Definir patrón" icon={Plus} />
          <div className="space-y-3 p-5">
            <Select label="Tipo de objeto" value={form.object_type} onChange={(e) => setForm({ ...form, object_type: e.target.value })}
              options={types} />
            <Input label="Patrón" value={form.pattern} onChange={(e) => setForm({ ...form, pattern: e.target.value })}
              placeholder="Z{MODULE}_{NAME}" className="font-mono" />
            <div className="flex items-center gap-2 rounded-lg border border-neon-400/20 bg-neon-500/5 px-3 py-2 text-sm">
              <Eye className="h-4 w-4 text-neon-400" /> <span className="text-ink-400">Ejemplo:</span>
              <span className="font-mono text-neon-300">{preview || '—'}</span>
            </div>
            <p className="text-xs text-ink-500">Marcadores: {'{MODULE}'}, {'{AREA}'}, {'{NAME}'} — se sustituyen al generar.</p>
            <Input label="Descripción (opcional)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            <Button onClick={save} className="w-full">Guardar regla</Button>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title={`Reglas del cliente (${rules.length})`} />
          <div className="p-5">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-white/10 text-left text-ink-400">
                <th className="py-2">Objeto</th><th>Patrón</th><th>Ejemplo</th><th></th>
              </tr></thead>
              <tbody>
                {rules.map((r) => (
                  <tr key={r.id} className="border-b border-white/5">
                    <td className="py-2"><Badge tone="info">{r.object_type}</Badge></td>
                    <td className="font-mono text-xs text-ink-300">{r.pattern}</td>
                    <td className="font-mono text-xs text-neon-300">{r.example}</td>
                    <td className="text-right"><button onClick={() => remove(r.id)} className="text-ink-500 hover:text-red-400"><Trash2 className="h-4 w-4" /></button></td>
                  </tr>
                ))}
                {!rules.length && <tr><td colSpan={4} className="py-3 text-ink-500">Sin reglas. Define patrones arriba.</td></tr>}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  )
}
