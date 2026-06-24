import React from 'react'
import { Select } from './ui/primitives'
import { useCatalog } from '../hooks/useCatalog'

// Selector de contexto SAP reutilizable. value es un objeto SapContext; onChange(patch).
export default function SapContextForm({ value, onChange, compact = false }) {
  const catalog = useCatalog()
  if (!catalog) return <p className="text-sm text-ink-500">Cargando catálogo…</p>

  const set = (k) => (e) => onChange({ ...value, [k]: e.target.value })

  return (
    <div className={`grid gap-3 ${compact ? 'grid-cols-2' : 'grid-cols-2 md:grid-cols-3'}`}>
      <Select label="Versión SAP" value={value.sap_version || ''} onChange={set('sap_version')}
        options={catalog.sap_versions.map((v) => ({ value: v.key, label: v.label }))} />
      <Select label="Módulo" value={value.module || ''} onChange={set('module')}
        options={[{ value: '', label: '—' }, ...catalog.modules.map((m) => ({ value: m, label: m }))]} />
      <Select label="Tipo de desarrollo" value={value.dev_type || ''} onChange={set('dev_type')}
        options={[{ value: '', label: '—' }, ...catalog.dev_types.map((d) => ({ value: d.key, label: d.label }))]} />
      <Select label="Complejidad" value={value.complexity || 'media'} onChange={set('complexity')}
        options={catalog.complexities} />
      <Select label="Ambiente" value={value.environment || 'DEV'} onChange={set('environment')}
        options={catalog.environments} />
      {!compact && (
        <Select label="Estándar" value={value.standard || ''} onChange={set('standard')}
          options={[{ value: '', label: '—' }, 'Clean ABAP', 'ABAP 7.40+', 'ABAP 7.50+', 'RAP', 'Legacy 4.6c']} />
      )}
    </div>
  )
}
