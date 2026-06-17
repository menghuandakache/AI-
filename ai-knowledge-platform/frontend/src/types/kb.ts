export interface KnowledgeBaseItem {
  id: string
  name: string
  description?: string
  domain?: string
  owner_id?: string
  status: string
  created_by?: string
  created_at?: string
  updated_at?: string
  knowledge_count?: number
}
