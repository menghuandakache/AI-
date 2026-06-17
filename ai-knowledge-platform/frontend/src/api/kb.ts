import request from './request'

export async function getKnowledgeBases(params?: Record<string, any>) {
  return request.get('/kb', { params })
}

export async function getKnowledgeBase(id: string) {
  return request.get(`/kb/${id}`)
}

export async function createKnowledgeBase(data: Record<string, any>) {
  return request.post('/kb', data)
}

export async function updateKnowledgeBase(id: string, data: Record<string, any>) {
  return request.put(`/kb/${id}`, data)
}

export async function deleteKnowledgeBase(id: string) {
  return request.delete(`/kb/${id}`)
}

export async function updateKnowledgeBaseStatus(id: string, status: string) {
  return request.patch(`/kb/${id}/status`, { status })
}

export async function getKnowledgeBaseOverview(id: string) {
  return request.get(`/kb/${id}/overview`)
}
