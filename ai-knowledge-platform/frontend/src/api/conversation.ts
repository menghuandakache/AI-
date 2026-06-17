import request from './request'

export async function getConversations(agentId: string) {
  return request.get('/conversations', { params: { agent_id: agentId } })
}

export async function getConversation(convId: string) {
  return request.get(`/conversations/${convId}`)
}

export async function createConversation(agentId: string, title?: string) {
  return request.post('/conversations', { agent_id: agentId, title: title || '新对话' })
}

export async function deleteConversation(convId: string) {
  return request.delete(`/conversations/${convId}`)
}
