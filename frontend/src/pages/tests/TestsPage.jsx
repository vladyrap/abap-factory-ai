import React, { useState } from 'react'
import { FlaskConical, Play } from 'lucide-react'
import toast from 'react-hot-toast'
import { testsApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Badge } from '../../components/ui/primitives'
import AbapEditor from '../../components/AbapEditor'

export default function TestsPage() {
  const { activeId } = useProject()
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [res, setRes] = useState(null)

  const gen = async () => {
    if (!code.trim()) return toast.error('Pega el código a probar')
    setLoading(true)
    try {
      const { data } = await testsApi.unit({ source_code: code, project_id: activeId, save: !!activeId })
      setRes(data)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <FlaskConical className="h-7 w-7 text-brand-400" />
        <div>
          <h1 className="text-2xl font-bold text-ink-50">Generador de Pruebas ABAP Unit</h1>
          <p className="text-ink-400">Clases de test GIVEN/WHEN/THEN, mocks y cobertura.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Código bajo prueba" />
          <div className="space-y-4 p-4">
            <AbapEditor value={code} onChange={(v) => setCode(v || '')} height="420px" />
            <Button onClick={gen} loading={loading} className="w-full"><Play className="h-4 w-4" /> Generar ABAP Unit</Button>
          </div>
        </Card>

        <Card>
          <CardHeader title="Suite generada" subtitle={res && `Cobertura esperada: ${res.expected_coverage || '—'}`} />
          <div className="space-y-4 p-5">
            {!res && <p className="text-sm text-ink-500">La clase de test aparecerá aquí.</p>}
            {res && (
              <>
                {res.test_code && <AbapEditor value={res.test_code} readOnly height="280px" />}
                <div>
                  <p className="mb-2 text-sm font-semibold text-ink-200">Casos ({res.cases?.length || 0})</p>
                  <div className="space-y-2">
                    {(res.cases || []).map((c, i) => (
                      <div key={i} className="rounded-lg border border-ink-800 p-3 text-sm">
                        <div className="mb-1 flex items-center gap-2">
                          <Badge>{c.type}</Badge>
                          <span className="font-medium text-ink-100">{c.name}</span>
                        </div>
                        <p className="text-ink-400"><b>Given:</b> {c.given}</p>
                        <p className="text-ink-400"><b>When:</b> {c.when}</p>
                        <p className="text-ink-400"><b>Then:</b> {c.then}</p>
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
