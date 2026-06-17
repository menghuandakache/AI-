export interface KnowledgeItemData {
  id: string
  kb_id: string
  title: string
  content: string
  summary?: string
  category?: string
  tags: string[]
  status: string
  source_type: string
  source_file_id?: string
  created_by?: string
  updated_by?: string
  created_at?: string
  updated_at?: string
  chunk_count?: number
}
