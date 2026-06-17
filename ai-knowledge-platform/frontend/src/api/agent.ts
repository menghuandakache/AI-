import request from './request'

export async function getAgents(params?: Record<string, any>) {
  return request.get('/agents', { params })
}

export async function getAgent(id: string) {
  return request.get(`/agents/${id}`)
}

export async function createAgent(data: Record<string, any>) {
  return request.post('/agents', data)
}

export async function updateAgent(id: string, data: Record<string, any>) {
  return request.put(`/agents/${id}`, data)
}

export async function disableAgent(id: string) {
  return request.patch(`/agents/${id}/disable`)
}

export async function enableAgent(id: string) {
  return request.patch(`/agents/${id}/enable`)
}

export async function generateAgent(data: { kb_id: string; name?: string }) {
  return request.post('/agents/generate', data)
}

export async function chatWithAgent(agentId: string, data: { question: string }) {
  return request.post(`/agents/${agentId}/chat`, data)
}
