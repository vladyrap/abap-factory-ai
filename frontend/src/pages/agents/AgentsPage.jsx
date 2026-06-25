import React, { useEffect, useState } from 'react'
import { Bot, Save, CheckCircle2, XCircle, Plus, Trash2, Lock } from 'lucide-react'
import toast from 'react-hot-toast'
import { agentsApi } from '../../services/api'
import { Card, CardHeader, Button, Select, Input, Textarea, Badge } from '../../components/ui/primitives'

const PROVIDERS = [
  { value: 'claude', label: 'Claude (Anthropic)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'gemini', label: 'Gemini (Google · gratis)' },
]
const BLANK = { key: '', name: '', description: '', provider: 'gemini', model: '', temperature: 0.2, max_tokens: 4000, system_prompt: '', is_active: true }

export default function AgentsPage() {
  const [agents, setAgents] = useState([])
  const [providers, setProviders] = useState({})
  const [edit, setEdit] = useState(null)
  const [isNew, setIsNew] = useState(false)

  const load = () => {
    agentsApi.list().then((r) => setAgents(r.data)).catch(() => {})
    agentsApi.providersStatus().then((r) => setProviders(r.data)).catch(() => {})
  }
  useEffect(() => { load() }, [])

  const openNew = () => { setEdit({ ...BLANK }); setIsNew(true) }
  const openEdit = (a) => { setEdit({ ...a, model: a.model === '(default del proveedor)' ? '' : a.model }); setIsNew(false) }

  const save = async () => {
    try {
      if (isNew) {
        await agentsApi.create({
          key: edit.key, name: edit.name, description: edit.description, provider: edit.provider,
          model: edit.model || null, temperature: Number(edit.temperature),
          max_tokens: Number(edit.max_tokens), system_prompt: edit.system_prompt,
        })
        toast.success('Agente creado')
      } else {
        await agentsApi.update(edit.key, {
          name: edit.name, description: edit.description, provider: edit.provider, model: edit.model || null,
          temperature: Number(edit.temperature), max_tokens: Number(edit.max_tokens),
          system_prompt: edit.system_prompt, is_active: edit.is_active,
        })
        toast.success('Agente actualizado')
      }
      setEdit(null); load()
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  const remove = async (a) => {
    try { await agentsApi.remove(a.key); toast.success('Agente eliminado'); load() }
    catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bot className="h-6 w-6 text-vs-link" />
          <div>
            <h1 className="text-base font-semibold uppercase tracking-wide text-ink-100">Agentes IA</h1>
            <p className="text-xs text-vs-muted">Crea, edita y elimina agentes dinámicamente.</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <ProviderBadge name="Claude" ok={providers.claude} />
          <ProviderBadge name="OpenAI" ok={providers.openai} />
          <ProviderBadge name="Gemini" ok={providers.gemini} />
          <Button onClick={openNew}><Plus className="h-4 w-4" /> Nuevo agente</Button>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {agents.map((a) => (
          <Card key={a.key}>
            <CardHeader title={a.name} subtitle={a.description}
              action={
                <div className="flex items-center gap-1.5">
                  {a.is_system ? <Badge tone="info"><Lock className="mr-1 inline h-3 w-3" />sistema</Badge> : <Badge>custom</Badge>}
                  {!a.is_active && <Badge tone="critica">off</Badge>}
                </div>
              } />
            <div className="space-y-2 p-4 text-[13px]">
              <div className="flex flex-wrap gap-1.5">
                <Badge>{a.key}</Badge>
                <Badge tone="info">{a.provider}</Badge>
                <Badge>{a.model}</Badge>
                <Badge>temp {a.temperature}</Badge>
              </div>
              <p className="line-clamp-2 text-xs text-vs-muted">{a.system_prompt}</p>
              <div className="flex gap-2 pt-1">
                <Button variant="secondary" onClick={() => openEdit(a)}>Editar</Button>
                {!a.is_system && <Button variant="ghost" onClick={() => remove(a)}><Trash2 className="h-4 w-4" /> Eliminar</Button>}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {edit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={() => setEdit(null)}>
          <Card className="max-h-[90vh] w-full max-w-2xl overflow-auto" onClick={(e) => e.stopPropagation()}>
            <CardHeader title={isNew ? 'Nuevo agente' : `Editar: ${edit.name}`} />
            <div className="space-y-3 p-5">
              <div className="grid grid-cols-2 gap-3">
                <Input label="Key (identificador)" value={edit.key} disabled={!isNew}
                  onChange={(e) => setEdit({ ...edit, key: e.target.value })} placeholder="abap_forms" className="font-mono" />
                <Input label="Nombre" value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} />
              </div>
              <Input label="Descripción" value={edit.description || ''} onChange={(e) => setEdit({ ...edit, description: e.target.value })} />
              <div className="grid grid-cols-3 gap-3">
                <Select label="Proveedor" value={edit.provider} onChange={(e) => setEdit({ ...edit, provider: e.target.value })} options={PROVIDERS} />
                <Input label="Modelo (opcional)" value={edit.model || ''} onChange={(e) => setEdit({ ...edit, model: e.target.value })} placeholder="(default)" />
                <Input label="Temperatura" type="number" step="0.1" value={edit.temperature} onChange={(e) => setEdit({ ...edit, temperature: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Input label="Max tokens" type="number" value={edit.max_tokens} onChange={(e) => setEdit({ ...edit, max_tokens: e.target.value })} />
                {!isNew && (
                  <label className="flex items-end gap-2 pb-1.5 text-sm text-ink-300">
                    <input type="checkbox" checked={edit.is_active} onChange={(e) => setEdit({ ...edit, is_active: e.target.checked })} className="accent-vs-button" />
                    Activo
                  </label>
                )}
              </div>
              <Textarea label="System prompt (especialidad)" rows={9} value={edit.system_prompt}
                onChange={(e) => setEdit({ ...edit, system_prompt: e.target.value })}
                placeholder="Eres un especialista en…" />
              <div className="flex justify-end gap-2">
                <Button variant="ghost" onClick={() => setEdit(null)}>Cancelar</Button>
                <Button onClick={save}><Save className="h-4 w-4" /> Guardar</Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}

function ProviderBadge({ name, ok }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-[2px] border px-2 py-1 text-xs ${ok ? 'border-vs-green/30 bg-vs-green/10 text-vs-green' : 'border-vs-border2 bg-white/5 text-vs-muted'}`}>
      {ok ? <CheckCircle2 className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />} {name}
    </span>
  )
}
