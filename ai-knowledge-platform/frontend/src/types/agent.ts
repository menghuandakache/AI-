export interface AgentItem {
  id: string
  name: string
  description?: string
  kb_ids: string[]
  prompt_config?: string
  answer_style: string
  citation_policy: string
  no_answer_policy: string
  status: string
  created_by?: string
  created_at?: string
  updated_at?: string
}
