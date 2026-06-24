import { useState, useEffect } from 'react'
import { catalogApi } from '../services/api'

let _cache = null

export function useCatalog() {
  const [catalog, setCatalog] = useState(_cache)
  useEffect(() => {
    if (_cache) return
    catalogApi.get().then((r) => { _cache = r.data; setCatalog(r.data) }).catch(() => {})
  }, [])
  return catalog
}
