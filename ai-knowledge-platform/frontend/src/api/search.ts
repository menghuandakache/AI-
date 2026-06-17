import request from './request'

export async function keywordSearch(data: { query: string; kb_id?: string }) {
  return request.post('/search/keyword', data)
}

export async function semanticSearch(data: { query: string; kb_id?: string; top_k?: number }) {
  return request.post('/search/semantic', data)
}

export async function hybridSearch(data: { query: string; kb_id?: string; top_k?: number }) {
  return request.post('/search/hybrid', data)
}
