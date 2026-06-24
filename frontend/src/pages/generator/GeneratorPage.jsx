import React, { useState } from 'react'
import { Wand2, Sparkles, Download, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import { generationApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Textarea, Badge } from '../../components/ui/primitives'
import SapContextForm from '../../components/SapContextForm'
import AbapEditor from '../../components/AbapEditor'

export default function GeneratorPage() {
  const { activeId, active } = useProject()
  const [ctx, setCtx] = useState({
    sap_version: active?.sap_version || 'S4HANA', complexity: 'media', environment: 'DEV',
  })
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [code, setCode] = useState('')

  const generate = async () => {
    if (!description.trim()) return toast.error('Describe lo que necesitas desarrollar')
    setLoading(true)
    try {
      const { data } = await generationApi.code({
        description, sap_context: ctx, project_id: activeId, save: !!activeId,
      })
      setResult(data)
      setCode(data.code)
      toast.success(`Generado por ${data.agent_key} (${data.provider})`)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error al generar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Wand2 className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Generador de Código ABAP</h1>
          <p className="text-ink-400">Describe el requerimiento y elige el contexto SAP.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Panel de configuración */}
        <Card className="lg:col-span-2">
          <CardHeader title="Contexto SAP" subtitle="Paso 1 · selecciona" />
          <div className="space-y-4 p-5">
            <SapContextForm value={ctx} onChange={setCtx} />
            <Textarea label="Requerimiento (paso 2)" rows={6} value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ej: Report ALV que liste documentos FI por sociedad y rango de fechas, con totales por clase de documento." />
            <Button onClick={generate} loading={loading} className="w-full">
              <Sparkles className="h-4 w-4" /> Generar ABAP
            </Button>
          </div>
        </Card>

        {/* Resultado */}
        <Card className="lg:col-span-3">
          <CardHeader
            title={result?.object_name || 'Código generado'}
            subtitle={result && `${result.language} · agente ${result.agent_key} · ${result.model}`}
            action={result?.artifact && (
              <a href={`/api/exports/artifact/${result.artifact.id}.abap`} target="_blank" rel="noreferrer">
                <Button variant="secondary"><Download className="h-4 w-4" /> .abap</Button>
              </a>
            )}
          />
          <div className="p-5">
            {result ? (
              <>
                <AbapEditor value={code} onChange={setCode} height="380px" />
                {result.explanation && (
                  <div className="mt-4 rounded-lg border border-ink-800 bg-ink-950/50 p-4">
                    <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-brand-300">
                      <FileText className="h-4 w-4" /> Explicación
                    </div>
                    <p className="whitespace-pre-wrap text-sm text-ink-300">{result.explanation}</p>
                  </div>
                )}
              </>
            ) : (
              <div className="flex h-[380px] flex-col items-center justify-center text-ink-600">
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
