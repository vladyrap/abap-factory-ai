import React, { useEffect, useState } from 'react'
import { KeyRound, CheckCircle2, XCircle, Save, Zap, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'
import { aiSettingsApi } from '../../services/api'
import { Card, CardHeader, Button, Input, Select, Badge } from '../../components/ui/primitives'

export default function AiCredentialsPage() {
  const [data, setData] = useState(null)
  const [drafts, setDrafts] = useState({})       // key -> nuevo valor a guardar
  const [open, setOpen] = useState({})           // key -> guía abierta
  const [busy, setBusy] = useState('')

  const load = () => aiSettingsApi.get().then((r) => setData(r.data)).catch(() => {})
  useEffect(() => { load() }, [])

  const saveKey = async (p) => {
    const field = { anthropic: 'anthropic_api_key', openai: 'openai_api_key', gemini: 'gemini_api_key' }[p]
    setBusy(p)
    try {
      await aiSettingsApi.update({ [field]: drafts[p] ?? '' })
      toast.success('Credencial guardada')
      setDrafts((d) => ({ ...d, [p]: '' })); load()
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
    finally { setBusy('') }
  }

  const test = async (p) => {
    setBusy(p + '_test')
    try {
      const { data: r } = await aiSettingsApi.test(p)
      toast.success(`OK · ${r.model}: "${r.reply}"`)
    } catch (e) { toast.error(e.response?.data?.detail || 'Falló la prueba') }
    finally { setBusy('') }
  }

  const setDefault = async (p) => {
    try { await aiSettingsApi.update({ default_provider: p }); toast.success('Proveedor por defecto actualizado'); load() }
    catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  if (!data) return <p className="text-sm text-vs-muted">Cargando…</p>

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <KeyRound className="h-6 w-6 text-vs-link" />
        <div>
          <h1 className="text-base font-semibold uppercase tracking-wide text-ink-100">Credenciales IA</h1>
          <p className="text-xs text-vs-muted">Carga las API keys de los proveedores. Se guardan cifradas; nunca se muestran completas.</p>
        </div>
      </div>

      <Card className="max-w-xl">
        <CardHeader title="Proveedor por defecto" />
        <div className="flex items-center gap-3 p-4">
          <Select value={data.default_provider} onChange={(e) => setDefault(e.target.value)}
            options={data.providers.map((p) => ({ value: p.key === 'anthropic' ? 'claude' : p.key, label: p.name }))} className="max-w-xs" />
          <span className="text-xs text-vs-muted">Se usa cuando un agente no especifica proveedor.</span>
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-3">
        {data.providers.map((p) => (
          <Card key={p.key}>
            <CardHeader title={p.name}
              action={
                <div className="flex items-center gap-1.5">
                  {p.free && <Badge tone="baja">gratis</Badge>}
                  {p.configured
                    ? <Badge tone="baja"><CheckCircle2 className="mr-1 inline h-3 w-3" />{p.source}</Badge>
                    : <Badge tone="critica"><XCircle className="mr-1 inline h-3 w-3" />sin clave</Badge>}
                </div>
              } />
            <div className="space-y-3 p-4">
              {p.configured && <p className="font-mono text-xs text-vs-muted">Actual: {p.masked}</p>}
              <Input type="password" label="Nueva API key" placeholder="pega aquí la clave"
                value={drafts[p.key] || ''} onChange={(e) => setDrafts({ ...drafts, [p.key]: e.target.value })} />
              <div className="flex gap-2">
                <Button onClick={() => saveKey(p.key)} loading={busy === p.key}><Save className="h-4 w-4" /> Guardar</Button>
                {p.configured && <Button variant="secondary" onClick={() => test(p.key)} loading={busy === p.key + '_test'}><Zap className="h-4 w-4" /> Probar</Button>}
              </div>

              <button onClick={() => setOpen({ ...open, [p.key]: !open[p.key] })}
                className="flex items-center gap-1 text-xs text-vs-link hover:underline">
                {open[p.key] ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                ¿Cómo obtener la key? (paso a paso)
              </button>
              {open[p.key] && (
                <div className="rounded-[3px] border border-vs-border bg-vs-editor p-3 text-xs text-ink-300">
                  <a href={p.get_key_url} target="_blank" rel="noreferrer" className="mb-2 inline-flex items-center gap-1 text-vs-link hover:underline">
                    <ExternalLink className="h-3 w-3" /> {p.get_key_url}
                  </a>
                  <ol className="list-decimal space-y-1 pl-4">
                    {p.steps.map((s, i) => <li key={i}>{s}</li>)}
                  </ol>
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
