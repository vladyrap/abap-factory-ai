import React, { useEffect, useState } from 'react'
import { ShieldHalf, Plus, Trash2, Save, Lock } from 'lucide-react'
import toast from 'react-hot-toast'
import { rolesApi } from '../../services/api'
import { Card, CardHeader, Button, Input, Badge } from '../../components/ui/primitives'

export default function RolesPage() {
  const [groups, setGroups] = useState({})
  const [roles, setRoles] = useState([])
  const [editing, setEditing] = useState(null)  // {id?, name, description, permissions:Set}

  const load = () => rolesApi.list().then((r) => setRoles(r.data)).catch(() => {})
  useEffect(() => {
    rolesApi.permissions().then((r) => setGroups(r.data.groups)).catch(() => {})
    load()
  }, [])

  const startNew = () => setEditing({ name: '', description: '', permissions: new Set() })
  const startEdit = (role) => setEditing({
    id: role.id, name: role.name, description: role.description || '',
    is_system: role.is_system, permissions: new Set(role.permissions || []),
  })

  const togglePerm = (key) => setEditing((e) => {
    const next = new Set(e.permissions)
    next.has(key) ? next.delete(key) : next.add(key)
    return { ...e, permissions: next }
  })
  const toggleAll = () => setEditing((e) => {
    const has = e.permissions.has('*')
    return { ...e, permissions: has ? new Set() : new Set(['*']) }
  })

  const save = async () => {
    if (!editing.name.trim()) return toast.error('Nombre requerido')
    const payload = { name: editing.name, description: editing.description, permissions: [...editing.permissions] }
    try {
      if (editing.id) await rolesApi.update(editing.id, payload)
      else await rolesApi.create(payload)
      toast.success('Rol guardado'); setEditing(null); load()
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  const remove = async (role) => {
    try { await rolesApi.remove(role.id); toast.success('Rol eliminado'); load() }
    catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  const superuser = editing?.permissions?.has('*')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShieldHalf className="h-7 w-7 text-neon-400" />
          <div>
            <h1 className="font-display text-2xl font-bold text-gradient">Roles y permisos</h1>
            <p className="text-ink-400">Crea roles a medida con permisos a bajo nivel.</p>
          </div>
        </div>
        <Button onClick={startNew}><Plus className="h-4 w-4" /> Nuevo rol</Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className={editing ? 'lg:col-span-1' : 'lg:col-span-3'}>
          <CardHeader title={`Roles (${roles.length})`} />
          <div className="space-y-2 p-5">
            {roles.map((r) => (
              <div key={r.id} className="flex items-center justify-between rounded-lg border border-white/10 p-3">
                <button onClick={() => startEdit(r)} className="text-left">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-ink-100">{r.name}</span>
                    {r.is_system && <Badge tone="info"><Lock className="mr-1 inline h-3 w-3" />sistema</Badge>}
                    {(r.permissions || []).includes('*') && <Badge tone="critica">total</Badge>}
                  </div>
                  <p className="text-xs text-ink-500">{r.description} · {(r.permissions || []).includes('*') ? 'todos' : (r.permissions || []).length} permisos</p>
                </button>
                {!r.is_system && (
                  <button onClick={() => remove(r)} className="text-ink-500 hover:text-red-400"><Trash2 className="h-4 w-4" /></button>
                )}
              </div>
            ))}
          </div>
        </Card>

        {editing && (
          <Card className="lg:col-span-2">
            <CardHeader title={editing.id ? `Editar rol` : 'Nuevo rol'}
              action={<Button onClick={save}><Save className="h-4 w-4" /> Guardar</Button>} />
            <div className="space-y-4 p-5">
              <div className="grid grid-cols-2 gap-3">
                <Input label="Nombre" value={editing.name} disabled={editing.is_system}
                  onChange={(e) => setEditing({ ...editing, name: e.target.value })} />
                <Input label="Descripción" value={editing.description}
                  onChange={(e) => setEditing({ ...editing, description: e.target.value })} />
              </div>

              <label className="flex items-center gap-2 rounded-lg border border-red-400/20 bg-red-500/5 px-3 py-2 text-sm text-ink-200">
                <input type="checkbox" checked={superuser} onChange={toggleAll} className="accent-red-500" />
                Acceso total (superusuario) — otorga todos los permisos
              </label>

              {!superuser && Object.entries(groups).map(([group, items]) => (
                <div key={group}>
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-neon-400">{group}</p>
                  <div className="grid grid-cols-2 gap-2">
                    {items.map((p) => (
                      <label key={p.key} className="flex items-center gap-2 rounded-lg border border-white/10 px-2 py-1.5 text-sm text-ink-300">
                        <input type="checkbox" checked={editing.permissions.has(p.key)}
                          onChange={() => togglePerm(p.key)} className="accent-brand-600" />
                        {p.label} <span className="ml-auto font-mono text-[10px] text-ink-600">{p.key}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
