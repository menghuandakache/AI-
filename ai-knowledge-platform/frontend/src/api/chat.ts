import request from './request'

export async function askQuestion(data: { question: string; kb_id?: string; agent_id?: string }) {
  return request.post('/chat/ask', data)
}

export function getAskStreamUrl() {
  return `${import.meta.env.VITE_API_BASE_URL || '/api'}/chat/ask/stream`
}

export function getAgentChatStreamUrl(agentId: string) {
  return `${import.meta.env.VITE_API_BASE_URL || '/api'}/agents/${agentId}/chat/stream`
}

export async function submitFeedback(data: { qa_log_id: string; feedback_type: string; feedback_reason?: string }) {
  return request.post('/feedback', data)
}

export async function getChatHistory(params?: Record<string, any>) {
  return request.get('/chat/history', { params })
}
