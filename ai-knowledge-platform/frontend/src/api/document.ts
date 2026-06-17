import request from './request'

export async function uploadDocument(kbId: string, file: File) {
  const formData = new FormData()
  formData.append('kb_id', kbId)
  formData.append('file', file)
  return request.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export async function getDocumentList(params: {
  kb_id: string
  page?: number
  page_size?: number
}) {
  return request.get('/documents', { params })
}

export async function parseDocument(documentId: string, chunkMethod?: string) {
  return request.post(`/documents/${documentId}/parse`, {
    chunk_method: chunkMethod || 'auto',
  })
}

export async function getDocumentStatus(documentId: string) {
  return request.get(`/documents/${documentId}/status`)
}

export async function getDocumentDrafts(documentId: string) {
  return request.get(`/documents/${documentId}/drafts`)
}

export async function importDraftKnowledge(documentId: string, draftIds: string[]) {
  return request.post(`/documents/${documentId}/import`, { draft_ids: draftIds })
}
