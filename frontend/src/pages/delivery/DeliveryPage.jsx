import React, { useEffect, useState } from 'react'
import { GitBranch, Download, Save, Package, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import { connectionsApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { Card, CardHeader, Button, Input, Select } from '../../components/ui/primitives'

export default function DeliveryPage() {
  const { activeId, active } = useProject()
  const [conn, setConn] = useState({ kind: 'abapgit', branch: 'main' })

  useEffect(() => {
    if (!activeId) return
    connectionsApi.get(activeId).then((r) => setConn(r.data)).catch(() => {})
  }, [activeId])

  const save = async () => {
    if (!activeId) return toast.error('Selecciona un proyecto activo')
    try { await connectionsApi.set(activeId, conn); toast.success('Conexión guardada') }
    catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  const set = (k) => (e) => setConn({ ...conn, [k]: e.target.value })

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <GitBranch className="h-7 w-7 text-neon-400" />
        <div>
          <h1 className="font-display text-2xl font-bold text-gradient">Entrega & abapGit</h1>
          <p className="text-ink-400">Empaqueta el proyecto para abapGit y transpórtalo a SAP.</p>
        </div>
      </div>

      {!activeId && <Card className="p-5 text-sm text-ink-400">Selecciona un proyecto activo arriba para empaquetarlo.</Card>}

      {activeId && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader title="Descargas del proyecto" subtitle={active?.name} icon={Package} />
            <div className="space-y-3 p-5">
              <a href={`/api/exports/project/${activeId}/abapgit.zip`} target="_blank" rel="noreferrer" className="block">
                <Button className="w-full"><Download className="h-4 w-4" /> Paquete abapGit (.zip)</Button>
              </a>
              <a href={`/api/exports/documentation/${activeId}.pdf`} target="_blank" rel="noreferrer" className="block">
                <Button variant="secondary" className="w-full"><FileText className="h-4 w-4" /> Documentación completa (PDF)</Button>
              </a>
              <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 text-xs text-ink-400">
                <p className="mb-1 font-semibold text-ink-300">Cómo transportar</p>
                <ol className="list-decimal space-y-1 pl-4">
                  <li>Descarga el ZIP abapGit.</li>
                  <li>En tu repo abapGit (online/offline) impórtalo en la carpeta <code className="text-neon-300">src/</code>.</li>
                  <li>Haz <b>pull</b> desde abapGit en DEV y activa los objetos.</li>
                  <li>Asígnalos a la orden de transporte y transporta a QAS/PRD.</li>
                </ol>
              </div>
            </div>
          </Card>

          <Card>
            <CardHeader title="Destino abapGit / ADT" subtitle="Metadatos (sin credenciales)" />
            <div className="space-y-3 p-5">
              <Select label="Tipo" value={conn.kind || 'abapgit'} onChange={set('kind')}
                options={[{ value: 'abapgit', label: 'abapGit (repo git)' }, { value: 'adt', label: 'ADT / OData (informativo)' }]} />
              <Input label="URL del repositorio git" value={conn.repo_url || ''} onChange={set('repo_url')} placeholder="https://github.com/org/repo-abap.git" />
              <div className="grid grid-cols-2 gap-3">
                <Input label="Branch" value={conn.branch || 'main'} onChange={set('branch')} />
                <Input label="Paquete SAP" value={conn.sap_package || ''} onChange={set('sap_package')} placeholder="ZAB_FI" />
              </div>
              <Input label="Orden de transporte" value={conn.transport_request || ''} onChange={set('transport_request')} placeholder="DEVK900123" />
              <Button onClick={save} className="w-full"><Save className="h-4 w-4" /> Guardar destino</Button>
              <p className="text-xs text-ink-500">Las credenciales nunca se guardan aquí: el push real se hace por git desde tu repo abapGit.</p>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
