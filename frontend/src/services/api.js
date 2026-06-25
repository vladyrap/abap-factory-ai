import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({ baseURL: '/api', timeout: 120000 })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Evita repetir el mismo toast varias veces en ráfaga.
let _lastToast = 0
function notifyOnce(msg) {
  const now = Date.now()
  if (now - _lastToast > 1500) { toast.error(msg); _lastToast = now }
}

// ─── Refresh de access token (single-flight) ────────────────────────────────
let _refreshing = null
function tryRefresh() {
  const rt = localStorage.getItem('refresh_token')
  if (!rt) return Promise.resolve(null)
  if (!_refreshing) {
    _refreshing = axios.post('/api/auth/refresh', { refresh_token: rt })
      .then((r) => {
        localStorage.setItem('token', r.data.access_token)
        if (r.data.refresh_token) localStorage.setItem('refresh_token', r.data.refresh_token)
        if (r.data.user) localStorage.setItem('user', JSON.stringify(r.data.user))
        return r.data.access_token
      })
      .catch(() => null)
      .finally(() => { _refreshing = null })
  }
  return _refreshing
}

function forceLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  if (!location.pathname.startsWith('/login')) window.location.href = '/login'
}

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const status = err.response?.status
    const original = err.config || {}
    if (status === 401 && !original._retry && original.url && !original.url.includes('/auth/')) {
      // Intentar refrescar el access token una vez y reintentar la petición.
      original._retry = true
      const newToken = await tryRefresh()
      if (newToken) {
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      }
      forceLogout()
    } else if (status === 401 && original.url && !original.url.includes('/auth/login')) {
      forceLogout()
    } else if (status === 429 && !(original.url && original.url.includes('/auth/login'))) {
      notifyOnce(err.response?.data?.detail || 'Límite de uso alcanzado. Intenta más tarde.')
    } else if (status === 503) {
      // Servicio IA no configurado/temporal: lo maneja cada pantalla; no spamear toast global.
    } else if (status >= 500) {
      notifyOnce('Error del servidor. El equipo fue notificado.')
    } else if (err.code === 'ECONNABORTED') {
      notifyOnce('La solicitud tardó demasiado. Reintenta.')
    } else if (!err.response) {
      notifyOnce('Sin conexión con el servidor.')
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login: (data) => api.post('/auth/login', data),
  refresh: (refresh_token) => api.post('/auth/refresh', { refresh_token }),
  me: () => api.get('/auth/me'),
  createUser: (data) => api.post('/auth/users', data),
  twofaStatus: () => api.get('/auth/2fa/status'),
  twofaSetup: () => api.post('/auth/2fa/setup'),
  twofaEnable: (otp) => api.post('/auth/2fa/enable', { otp }),
  twofaDisable: (otp) => api.post('/auth/2fa/disable', { otp }),
}

export const auditApi = {
  list: (limit = 200) => api.get('/audit/', { params: { limit } }),
}

export const catalogApi = {
  get: () => api.get('/catalog/'),
}

export const clientsApi = {
  list: () => api.get('/clients/'),
  get: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.patch(`/clients/${id}`, data),
}

export const projectsApi = {
  list: (clientId) => api.get('/projects/', { params: clientId ? { client_id: clientId } : {} }),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.patch(`/projects/${id}`, data),
  requirements: (id) => api.get(`/projects/${id}/requirements`),
  createRequirement: (data) => api.post('/projects/requirements', data),
}

export const generationApi = {
  code: (data) => api.post('/generation/code', data),
  editor: (data) => api.post('/generation/editor', data),
  spec: (data) => api.post('/generation/spec', data),
  validate: (source_code) => api.post('/generation/validate', { source_code }),
  refine: (artifact_id, instruction) => api.post('/generation/refine', { artifact_id, instruction }),
  extractRequirement: (raw_text, project_id) => api.post('/generation/extract-requirement', { raw_text, project_id }),
  artifacts: (projectId) => api.get('/generation/artifacts', { params: projectId ? { project_id: projectId } : {} }),
  artifact: (id) => api.get(`/generation/artifacts/${id}`),
  versions: (id) => api.get(`/generation/artifacts/${id}/versions`),
  edit: (id, data) => api.patch(`/generation/artifacts/${id}`, data),
  approve: (id) => api.post(`/generation/artifacts/${id}/approve`),
}

export const jobsApi = {
  create: (data) => api.post('/jobs/', data),
  list: (projectId) => api.get('/jobs/', { params: projectId ? { project_id: projectId } : {} }),
  get: (id) => api.get(`/jobs/${id}`),
}

export const recipesApi = {
  list: () => api.get('/recipes/'),
}

export const migrationApi = {
  migrate: (data) => api.post('/migration/migrate', data),
  list: (projectId) => api.get('/migration/', { params: projectId ? { project_id: projectId } : {} }),
  get: (id) => api.get(`/migration/${id}`),
}

export const namingApi = {
  objectTypes: () => api.get('/naming/object-types'),
  list: (clientId) => api.get(`/naming/client/${clientId}`),
  save: (data) => api.post('/naming/', data),
  preview: (pattern, variables) => api.post('/naming/preview', { pattern, variables }),
  remove: (id) => api.delete(`/naming/${id}`),
}

export const devDocsApi = {
  generate: (data) => api.post('/dev-docs/generate', data),
  list: (projectId) => api.get('/dev-docs/', { params: projectId ? { project_id: projectId } : {} }),
  get: (id) => api.get(`/dev-docs/${id}`),
}

export const connectionsApi = {
  get: (projectId) => api.get(`/connections/project/${projectId}`),
  set: (projectId, data) => api.put(`/connections/project/${projectId}`, data),
}

export const solutionApi = {
  build: (data) => api.post('/solution/build', data),
  extractFile: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/solution/extract-file', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}

export const knowledgeApi = {
  list: (clientId) => api.get(`/knowledge/client/${clientId}`),
  add: (data) => api.post('/knowledge/', data),
  remove: (id) => api.delete(`/knowledge/${id}`),
}

export const dumpsApi = {
  analyze: (data) => api.post('/dumps/analyze', data),
  list: (projectId) => api.get('/dumps/', { params: projectId ? { project_id: projectId } : {} }),
  get: (id) => api.get(`/dumps/${id}`),
}

export const inspectorApi = {
  inspect: (data) => api.post('/inspector/inspect', data),
  list: (projectId) => api.get('/inspector/', { params: projectId ? { project_id: projectId } : {} }),
}

export const testsApi = {
  unit: (data) => api.post('/tests/unit', data),
  protocol: (data) => api.post('/tests/protocol', data),
  suites: (projectId) => api.get('/tests/suites', { params: projectId ? { project_id: projectId } : {} }),
  protocols: (projectId) => api.get('/tests/protocols', { params: projectId ? { project_id: projectId } : {} }),
  getProtocol: (id) => api.get(`/tests/protocols/${id}`),
}

export const dashboardApi = {
  stats: (projectId) => api.get('/dashboard/stats', { params: projectId ? { project_id: projectId } : {} }),
  recent: () => api.get('/dashboard/recent'),
}

export const costsApi = {
  summary: () => api.get('/costs/summary'),
  history: (limit = 100) => api.get('/costs/history', { params: { limit } }),
}

export const agentsApi = {
  list: () => api.get('/agents/'),
  providersStatus: () => api.get('/agents/providers/status'),
  create: (data) => api.post('/agents/', data),
  update: (key, data) => api.put(`/agents/${key}`, data),
  remove: (key) => api.delete(`/agents/${key}`),
}

export const adminApi = {
  listUsers: () => api.get('/admin/users'),
  updateUser: (id, data) => api.patch(`/admin/users/${id}`, data),
  toggleActive: (id) => api.put(`/admin/users/${id}/toggle-active`),
}

export const rolesApi = {
  list: () => api.get('/roles/'),
  permissions: () => api.get('/roles/permissions'),
  create: (data) => api.post('/roles/', data),
  update: (id, data) => api.patch(`/roles/${id}`, data),
  remove: (id) => api.delete(`/roles/${id}`),
}

// URLs de exportación (descarga directa con token vía fetch en componente)
export const exportUrls = {
  abap: (id) => `/api/exports/artifact/${id}.abap`,
  spec: (id) => `/api/exports/spec/${id}.pdf`,
  dump: (id) => `/api/exports/dump/${id}.pdf`,
  inspection: (id) => `/api/exports/inspection/${id}.pdf`,
  protocol: (id) => `/api/exports/protocol/${id}.xlsx`,
  documentation: (projectId, requirementId) =>
    `/api/exports/documentation/${projectId}.pdf${requirementId ? `?requirement_id=${requirementId}` : ''}`,
  migration: (id) => `/api/exports/migration/${id}.pdf`,
  devDoc: (id) => `/api/exports/dev-doc/${id}.pdf`,
  abapgit: (projectId) => `/api/exports/project/${projectId}/abapgit.zip`,
}

export default api
