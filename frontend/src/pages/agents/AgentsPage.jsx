import React, { useEffect, useState } from 'react'
import { Bot, Save, CheckCircle2, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { agentsApi } from '../../services/api'
import { Card, CardHeader, Button, Select, Input, Textarea, Badge } from '../../components/ui/primitives'

export default function AgentsPage() {
  const [agents, setAgents] = useState([])
  const [providers, setProviders] = useState({})
  const [edit, setEdit] = useState(null)

  const load = () => {
    agentsApi.list().then((r) => setAgents(r.data)).catch(() => {})
    agentsApi.providersStatus().then((r) => setProviders(r.data)).catch(() => {})
  }
  useEffect(() => { load() }, [])

  const save = async () => {
    try {
      await agentsApi.update(edit.key, {
        provider: edit.provider, model: edit.model, temperature: Number(edit.temperature),
        max_tokens: Number(edit.max_tokens), system_prompt: edit.system_prompt, is_active: edit.is_active,
      })
      toast.success('Agente actualizado'); setEdit(null); load()
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bot className="h-7 w-7 text-brand-400" />
          <h1 className="text-2xl font-bold text-ink-50">Configuración de Agentes IA</h1>
        </div>
        <div className="flex gap-2">
          <ProviderBadge name="Claude" ok={providers.claude} />
          <ProviderBadge name="OpenAI" ok={providers.openai} />
          <ProviderBadge name="Gemini" ok={providers.gemini} />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {agents.map((a) => (
          <Card key={a.key}>
            <CardHeader title={a.name} subtitle={a.description}
              action={<Badge tone={a.customized ? 'info' : 'default'}>{a.customized ? 'custom' : 'default'}</Badge>} />
            <div className="space-y-2 p-5 text-sm">
              <div className="flex gap-2">
                <Badge>{a.provider}</Badge>
                <Badge tone="info">{a.model}</Badge>
                <Badge>temp {a.temperature}</Badge>
              </div>
              <p className="line-clamp-3 text-xs text-ink-500">{a.system_prompt}</p>
              <Button variant="secondary" onClick={() => setEdit({ ...a })} className="mt-2">Editar</Button>
            </div>
          </Card>
        ))}
      </div>

      {edit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={() => setEdit(null)}>
          <Card className="w-full max-w-2xl" onClick={(e) => e.stopPropagation()}>
            <CardHeader title={`Editar: ${edit.name}`} />
            <div className="space-y-3 p-5">
              <div className="grid grid-cols-2 gap-3">
                <Select label="Proveedor" value={edit.provider} onChange={(e) => setEdit({ ...edit, provider: e.target.value })}
                  options={[{ value: 'claude', label: 'Claude (Anthropic)' }, { value: 'openai', label: 'OpenAI' }, { value: 'gemini', label: 'Gemini (Google · gratis)' }]} />
                <Input label="Modelo" value={edit.model} onChange={(e) => setEdit({ ...edit, model: e.target.value })} />
                <Input label="Temperatura" type="number" step="0.1" value={edit.temperature} onChange={(e) => setEdit({ ...edit, temperature: e.target.value })} />
                <Input label="Max tokens" type="number" value={edit.max_tokens} onChange={(e) => setEdit({ ...edit, max_tokens: e.target.value })} />
              </div>
              <Textarea label="System prompt" rows={8} value={edit.system_prompt} onChange={(e) => setEdit({ ...edit, system_prompt: e.target.value })} />
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
    <span className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm ${ok ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400' : 'border-ink-700 bg-ink-800 text-ink-500'}`}>
      {ok ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />} {name}
    </span>
  )
}
