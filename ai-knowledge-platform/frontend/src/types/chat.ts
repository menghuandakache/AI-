export interface ChatMessage {
  id?: string
  role: 'user' | 'assistant'
  content: string
  sources?: CitationSource[]
  created_at?: string
}

export interface CitationSource {
  knowledge_id: string
  chunk_id?: string
  title: string
  source_file?: string
  score: number
}
