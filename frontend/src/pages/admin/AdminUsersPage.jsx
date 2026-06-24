import React, { useEffect, useState } from 'react'
import { Users, Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import { adminApi, authApi, rolesApi } from '../../services/api'
import { Card, CardHeader, Button, Input, Select, Badge } from '../../components/ui/primitives'

const ROLES = [
  { value: 'admin', label: 'Administrador' },
  { value: 'tech_lead', label: 'Líder técnico' },
  { value: 'consultant', label: 'Consultor ABAP' },
  { value: 'qa', label: 'QA' },
  { value: 'client_readonly', label: 'Cliente (solo lectura)' },
]

export default function AdminUsersPage() {
  const [users, setUsers] = useState([])
  const [dynRoles, setDynRoles] = useState([])
  const [form, setForm] = useState({ email: '', first_name: '', last_name: '', password: '', role: 'consultant' })

  const load = () => adminApi.listUsers().then((r) => setUsers(r.data)).catch(() => {})
  useEffect(() => {
    load()
    rolesApi.list().then((r) => setDynRoles(r.data)).catch(() => {})
  }, [])

  const assignRole = async (id, role_id) => {
    try { await adminApi.updateUser(id, { role_id: role_id ? Number(role_id) : null }); toast.success('Rol asignado'); load() }
    catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  const create = async () => {
    if (!form.email || !form.password) return toast.error('Email y contraseña requeridos')
    try {
      await authApi.createUser(form)
      toast.success('Usuario creado'); setForm({ email: '', first_name: '', last_name: '', password: '', role: 'consultant' }); load()
    } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  }

  const toggle = async (id) => { await adminApi.toggleActive(id); load() }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Users className="h-7 w-7 text-brand-400" />
        <h1 className="text-2xl font-bold text-ink-50">Administración de Usuarios</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Nuevo usuario" icon={Plus} />
          <div className="space-y-3 p-5">
            <Input label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Nombre" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
              <Input label="Apellido" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </div>
            <Input label="Contraseña" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <Select label="Rol" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} options={ROLES} />
            <Button onClick={create} className="w-full">Crear usuario</Button>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title={`Usuarios (${users.length})`} />
          <div className="p-5">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-ink-800 text-left text-ink-400">
                <th className="py-2">Usuario</th><th>Rol dinámico</th><th>Estado</th><th></th>
              </tr></thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-ink-900">
                    <td className="py-2">
                      <p className="text-ink-100">{u.first_name} {u.last_name}</p>
                      <p className="text-xs text-ink-500">{u.email} · base: {ROLES.find((r) => r.value === u.role)?.label || u.role}</p>
                    </td>
                    <td>
                      <Select value={u.role_id || ''} onChange={(e) => assignRole(u.id, e.target.value)}
                        options={[{ value: '', label: '(rol base)' }, ...dynRoles.map((r) => ({ value: r.id, label: r.name }))]} />
                    </td>
                    <td><Badge tone={u.is_active ? 'baja' : 'critica'}>{u.is_active ? 'activo' : 'inactivo'}</Badge></td>
                    <td className="text-right">
                      <Button variant="ghost" onClick={() => toggle(u.id)}>{u.is_active ? 'Desactivar' : 'Activar'}</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  )
}
