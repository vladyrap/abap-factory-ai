import React, { useState, useEffect } from 'react'
import { Wand2, Sparkles, Download, FileText, ShieldAlert, Gauge, BookOpen, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import { generationApi, recipesApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Textarea, Badge, Select } from '../../components/ui/primitives'
import SapContextForm from '../../components/SapContextForm'
import AbapEditor from '../../components/AbapEditor'

function QualityBadge({ score, passed }) {
  if (score == null) return null
  const tone = score >= 80 ? 'baja' : score >= 50 ? 'media' : 'critica'
  return <Badge tone={tone}>Calidad {Math.round(score)}/100 {passed ? '✓' : ''}</Badge>
}

export default function GeneratorPage() {
  const { activeId, active } = useProject()
  const [ctx, setCtx] = useState({ sap_version: active?.sap_version || 'S4HANA', complexity: 'media', environment: 'DEV' })
  const [description, setDescription] = useState('')
  const [autoOptimize, setAutoOptimize] = useState(true)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [code, setCode] = useState('')
  const [recipes, setRecipes] = useState([])
  const [recipe, setRecipe] = useState(null)
  const [recipeVals, setRecipeVals] = useState({})

  useEffect(() => { recipesApi.list().then((r) => setRecipes(r.data)).catch(() => {}) }, [])

  const applyRecipe = (key) => {
    const r = recipes.find((x) => x.key === key)
    setRecipe(r || null); setRecipeVals({})
    if (r) setCtx((c) => ({ ...c, dev_type: r.dev_type, sap_version: r.sap_version }))
  }

  const buildFromRecipe = () => {
    if (!recipe) return
    let text = recipe.template
    recipe.fields.forEach((f) => { text = text.replaceAll(`{${f.key}}`, recipeVals[f.key] || `<${f.label}>`) })
    setDescription(text)
  }

  const generate = async () => {
    if (!description.trim()) return toast.error('Describe lo que necesitas desarrollar')
    setLoading(true)
    try {
      const { data } = await generationApi.code({
        description, sap_context: ctx, project_id: activeId, save: !!activeId,
        auto_optimize: autoOptimize, target_score: 80,
      })
      setResult(data)
      setCode(data.code)
      toast.success(`${data.agent_key} · ${data.provider}${autoOptimize ? ` · calidad ${Math.round(data.quality_score)}` : ''}`)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error al generar')
    } finally {
      setLoading(false)
    }
  }

  const criticals = (result?.lint?.findings || []).filter((f) => f.severity === 'critical' || f.severity === 'error')

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Wand2 className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Generador de Código ABAP</h1>
          <p className="text-ink-400">Receta o descripción libre → el sistema genera, valida y se autocorrige.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardHeader title="Contexto y requerimiento" subtitle={active ? active.name : 'Sin proyecto activo'} />
          <div className="space-y-4 p-5">
            <Select label="Receta (opcional)" value={recipe?.key || ''} onChange={(e) => applyRecipe(e.target.value)}
              options={[{ value: '', label: '— Descripción libre —' }, ...recipes.map((r) => ({ value: r.key, label: r.name }))]} />
            {recipe && (
              <div className="space-y-2 rounded-lg border border-brand-800/40 bg-brand-900/10 p-3">
                {recipe.fields.map((f) => (
                  <input key={f.key} placeholder={`${f.label} (ej: ${f.placeholder})`}
                    value={recipeVals[f.key] || ''} onChange={(e) => setRecipeVals({ ...recipeVals, [f.key]: e.target.value })}
                    className="w-full rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm text-ink-100 outline-none focus:border-brand-500" />
                ))}
                <Button variant="secondary" onClick={buildFromRecipe} className="w-full"><BookOpen className="h-4 w-4" /> Usar receta</Button>
              </div>
            )}
            <SapContextForm value={ctx} onChange={setCtx} />
            <Textarea label="Requerimiento" rows={5} value={description} onChange={(e) => setDescription(e.target.value)}
              placeholder="Ej: Report ALV que liste documentos FI por sociedad y rango de fechas." />
            <label className="flex items-center gap-2 text-sm text-ink-300">
              <input type="checkbox" checked={autoOptimize} onChange={(e) => setAutoOptimize(e.target.checked)} className="accent-brand-600" />
              <Zap className="h-4 w-4 text-amber-400" /> Auto-optimizar (genera y refina hasta pasar calidad)
            </label>
            <Button onClick={generate} loading={loading} className="w-full">
              <Sparkles className="h-4 w-4" /> Generar ABAP
            </Button>
          </div>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader
            title={result?.object_name || 'Código generado'}
            subtitle={result && `${result.language} · ${result.agent_key} · ${result.model}`}
            action={
              <div className="flex items-center gap-2">
                {result && <QualityBadge score={result.quality_score} passed={result.passed} />}
                {result?.used_knowledge && <Badge tone="info">memoria cliente</Badge>}
                {result?.artifact && (
                  <a href={`/api/exports/artifact/${result.artifact.id}.abap`} target="_blank" rel="noreferrer">
                    <Button variant="secondary"><Download className="h-4 w-4" /> .abap</Button>
                  </a>
                )}
              </div>
            }
          />
          <div className="p-5">
            {result ? (
              <>
                <AbapEditor value={code} onChange={setCode} height="320px" />

                {result.timeline?.length > 1 && (
                  <div className="mt-3 flex items-center gap-2 text-xs text-ink-400">
                    <Gauge className="h-4 w-4 text-amber-400" /> Auto-optimización:
                    {result.timeline.map((t, i) => (
                      <span key={i} className="rounded bg-ink-800 px-2 py-0.5">{t.stage} → {t.combined}</span>
                    ))}
                  </div>
                )}

                {criticals.length > 0 && (
                  <div className="mt-4 rounded-lg border border-red-800/40 bg-red-900/10 p-3">
                    <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-red-400"><ShieldAlert className="h-4 w-4" /> Guardrails ({criticals.length})</div>
                    {criticals.map((f, i) => (
                      <p key={i} className="text-xs text-ink-300"><b className="font-mono">{f.rule}</b> L{f.line}: {f.message}</p>
                    ))}
                  </div>
                )}

                {result.confidence_notes?.length > 0 && (
                  <div className="mt-4 rounded-lg border border-amber-800/40 bg-amber-900/10 p-3">
                    <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-amber-400"><ShieldAlert className="h-4 w-4" /> Verificar en sistema ({result.confidence_notes.length})</div>
                    {result.confidence_notes.map((n, i) => (
                      <p key={i} className="text-xs text-ink-300"><Badge tone={n.confidence === 'baja' ? 'critica' : n.confidence === 'media' ? 'media' : 'default'}>{n.confidence}</Badge> <b>{n.item}</b> — {n.reason}</p>
                    ))}
                  </div>
                )}

                {result.explanation && (
                  <div className="mt-4 rounded-lg border border-ink-800 bg-ink-950/50 p-4">
                    <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-brand-300"><FileText className="h-4 w-4" /> Explicación</div>
                    <p className="whitespace-pre-wrap text-sm text-ink-300">{result.explanation}</p>
                  </div>
                )}
              </>
            ) : (
              <div className="flex h-[320px] flex-col items-center justify-center text-ink-600">
                <Wand2 className="mb-3 h-12 w-12" />
                <p>El código ABAP generado aparecerá aquí.</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
