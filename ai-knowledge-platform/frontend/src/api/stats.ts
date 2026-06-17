import request from './request'

export async function getOverviewStats() {
  return request.get('/stats/overview')
}

export async function getHotKnowledge(limit?: number) {
  return request.get('/stats/hot-knowledge', { params: { limit } })
}

export async function getFeedbackStats() {
  return request.get('/stats/feedback')
}

export async function getNoAnswerQuestions(limit?: number) {
  return request.get('/stats/no-answer', { params: { limit } })
}

export async function getRecentQA(limit?: number) {
  return request.get('/stats/recent-qa', { params: { limit } })
}
