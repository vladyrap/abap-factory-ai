import React, { useEffect, useState } from 'react'
import { FolderKanban, Plus, Building2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { clientsApi, projectsApi } from '../../services/api'
import { useProject } from '../../context/ProjectContext'
import { useAuth } from '../../context/AuthContext'
import { useCatalog } from '../../hooks/useCatalog'
import { Card, CardHeader, Button, Input, Textarea, Select, Badge } from '../../components/ui/primitives'

export default function ProjectsPage() {
  const { reload, selectProject } = useProject()
  const { can } = useAuth()
  const catalog = useCatalog()
  const [clients, setClients] = useState([])
  const [projects, setProjects] = useState([])
  const [tab, setTab] = useState('projects')
  const [pForm, setPForm] = useState({ name: '', client_id: '', sap_version: 'S4HANA', description: '' })
  const [cForm, setCForm] = useState({ name: '', naming_convention: '', coding_standards: '', restrictions: '' })

  const load = () => {
    clientsApi.list().then((r) => setClients(r.data)).catch(() => {})
    projectsApi.list().then((r) => setProjects(r.data)).catch(() => {})
  }
  useEffect(() => { load() }, [])

  const createClient = async () => {
    if (!cForm.name) return toast.error('Nombre requerido')
    try { await clientsApi.create(cForm); toast.success('Cliente creado'); setCForm({ name: '', naming_convention: '', coding_standards: '', restrictions: '' }); load() }
    catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  const createProject = async () => {
    if (!pForm.name || !pForm.client_id) return toast.error('Nombre y cliente requeridos')
    try {
      const { data } = await projectsApi.create({ ...pForm, client_id: Number(pForm.client_id) })
      toast.success('Proyecto creado'); load(); reload(); selectProject(data.id)
      setPForm({ name: '', client_id: '', sap_version: 'S4HANA', description: '' })
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <FolderKanban className="h-7 w-7 text-brand-400" />
        <h1 className="text-2xl font-bold text-ink-50">Proyectos y Clientes</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {can('create') && (
          <Card>
            <CardHeader title="Crear" icon={Plus} action={
              <div className="flex gap-1 text-xs">
                <button onClick={() => setTab('projects')} className={`rounded px-2 py-1 ${tab === 'projects' ? 'bg-brand-600 text-white' : 'text-ink-400'}`}>Proyecto</button>
                <button onClick={() => setTab('clients')} className={`rounded px-2 py-1 ${tab === 'clients' ? 'bg-brand-600 text-white' : 'text-ink-400'}`}>Cliente</button>
              </div>
            } />
            <div className="space-y-3 p-5">
              {tab === 'projects' ? (
                <>
                  <Input label="Nombre proyecto" value={pForm.name} onChange={(e) => setPForm({ ...pForm, name: e.target.value })} />
                  <Select label="Cliente" value={pForm.client_id} onChange={(e) => setPForm({ ...pForm, client_id: e.target.value })}
                    options={[{ value: '', label: '— Selecciona —' }, ...clients.map((c) => ({ value: c.id, label: c.name }))]} />
                  <Select label="Versión SAP" value={pForm.sap_version} onChange={(e) => setPForm({ ...pForm, sap_version: e.target.value })}
                    options={(catalog?.sap_versions || []).map((v) => ({ value: v.key, label: v.label }))} />
                  <Textarea label="Descripción" rows={3} value={pForm.description} onChange={(e) => setPForm({ ...pForm, description: e.target.value })} />
                  <Button onClick={createProject} className="w-full">Crear proyecto</Button>
                </>
              ) : (
                <>
                  <Input label="Nombre cliente" value={cForm.name} onChange={(e) => setCForm({ ...cForm, name: e.target.value })} />
                  <Textarea label="Naming convention" rows={2} value={cForm.naming_convention} onChange={(e) => setCForm({ ...cForm, naming_convention: e.target.value })} />
                  <Textarea label="Estándares de código" rows={2} value={cForm.coding_standards} onChange={(e) => setCForm({ ...cForm, coding_standards: e.target.value })} />
                  <Textarea label="Restricciones" rows={2} value={cForm.restrictions} onChange={(e) => setCForm({ ...cForm, restrictions: e.target.value })} />
                  <Button onClick={createClient} className="w-full">Crear cliente</Button>
                </>
              )}
            </div>
          </Card>
        )}

        <Card className={can('create') ? 'lg:col-span-2' : 'lg:col-span-3'}>
          <CardHeader title="Proyectos" subtitle={`${projects.length} proyectos`} />
          <div className="grid gap-3 p-5 sm:grid-cols-2">
            {projects.map((p) => {
              const client = clients.find((c) => c.id === p.client_id)
              return (
                <button key={p.id} onClick={() => { selectProject(p.id); toast.success(`Proyecto activo: ${p.name}`) }}
                  className="rounded-xl border border-ink-800 p-4 text-left hover:border-brand-600 hover:bg-ink-800/50">
                  <div className="mb-1 flex items-center justify-between">
                    <span className="font-semibold text-ink-100">{p.name}</span>
                    <Badge>{p.sap_version}</Badge>
                  </div>
                  <p className="flex items-center gap-1 text-xs text-ink-500"><Building2 className="h-3 w-3" /> {client?.name || '—'}</p>
                  {p.description && <p className="mt-2 line-clamp-2 text-sm text-ink-400">{p.description}</p>}
                </button>
              )
            })}
            {!projects.length && <p className="text-sm text-ink-500">No hay proyectos.</p>}
          </div>
        </Card>
      </div>
    </div>
  )
}
