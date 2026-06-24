import React, { useState } from 'react'
import { Code2, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'
import { generationApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { useCatalog } from '../../hooks/useCatalog'
import { Card, CardHeader, Button, Badge } from '../../components/ui/primitives'
import AbapEditor from '../../components/AbapEditor'

const SAMPLE = `REPORT zab_demo.\nDATA lt_bkpf TYPE TABLE OF bkpf.\nSELECT * FROM bkpf INTO TABLE lt_bkpf.\nLOOP AT lt_bkpf INTO DATA(ls).\n  SELECT SINGLE * FROM bseg INTO @DATA(ls_bseg) WHERE belnr = @ls-belnr.\nENDLOOP.`

export default function EditorPage() {
  const { activeId } = useProject()
  const catalog = useCatalog()
  const [code, setCode] = useState(SAMPLE)
  const [loading, setLoading] = useState('')
  const [output, setOutput] = useState(null)

  const run = async (operation) => {
    if (!code.trim()) return toast.error('Pega código ABAP')
    setLoading(operation)
    try {
      const { data } = await generationApi.editor({ operation, source_code: code, project_id: activeId })
      setOutput({ operation, data })
      if (data.code) setCode(data.code)
      toast.success('Listo')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally {
      setLoading('')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Code2 className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Editor ABAP Inteligente</h1>
          <p className="text-ink-400">Edita, explica, refactoriza y migra código.</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {(catalog?.editor_ops || []).map((op) => (
          <Button key={op.key} variant="secondary" loading={loading === op.key} onClick={() => run(op.key)}>
            <Sparkles className="h-4 w-4" /> {op.label}
          </Button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Editor" subtitle="Pega o edita tu código ABAP" />
          <div className="p-4"><AbapEditor value={code} onChange={(v) => setCode(v || '')} height="460px" /></div>
        </Card>
        <Card>
          <CardHeader title="Resultado" subtitle={output ? output.operation : 'Ejecuta una acción'} />
          <div className="p-5">
            {!output && <p className="text-sm text-ink-500">El análisis o código resultante aparecerá aquí.</p>}
            {output?.data?.explanation && (
              <p className="mb-4 whitespace-pre-wrap text-sm text-ink-300">{output.data.explanation}</p>
            )}
            {output?.data?.lines?.length > 0 && (
              <div className="space-y-1">
                {output.data.lines.map((l, i) => (
                  <div key={i} className="flex gap-3 border-b border-ink-800 py-1.5 text-sm">
                    <Badge>L{l.line}</Badge>
                    <span className="text-ink-300">{l.text}</span>
                  </div>
                ))}
              </div>
            )}
            {output?.data?.notes && (
              <div className="rounded-lg border border-brand-800/40 bg-brand-900/10 p-4 text-sm text-ink-300">
                <strong className="text-brand-300">Cambios aplicados:</strong> {output.data.notes}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
