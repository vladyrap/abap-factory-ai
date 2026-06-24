import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  createUser: (data) => api.post('/auth/users', data),
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
  update: (key, data) => api.put(`/agents/${key}`, data),
}

export const adminApi = {
  listUsers: () => api.get('/admin/users'),
  updateUser: (id, data) => api.patch(`/admin/users/${id}`, data),
  toggleActive: (id) => api.put(`/admin/users/${id}/toggle-active`),
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
}

export default api
