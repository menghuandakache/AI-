export interface DocumentItem {
  id: string
  kb_id: string
  filename: string
  file_type: string
  file_size: number | null
  parse_status: 'uploaded' | 'parsing' | 'parsed' | 'failed' | 'imported'
  parse_error: string | null
  created_by: string | null
  created_at: string
  updated_at: string
  draft_count: number
}

export interface DocumentListResponse {
  items: DocumentItem[]
  total: number
  page: number
  page_size: number
}

export interface DocumentParseAsyncResponse {
  id: string
  parse_status: string
  message: string
  task_id: string | null
}

export interface DraftKnowledgeItem {
  id: string
  title: string
  content: string
  chunk_index: number
  category: string | null
  tags: string[]
}
