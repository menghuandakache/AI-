// API base URL
export const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

// Knowledge categories
export const CATEGORIES = ['制度规范', '操作指南', '业务流程', '常见问题FAQ', '术语解释', '案例经验', '接口文档', '风险合规']

// Answer styles
export const ANSWER_STYLES = [
  { value: 'concise', label: '简洁' },
  { value: 'detailed', label: '详细' },
  { value: 'procedural', label: '流程化' },
  { value: 'service', label: '客服式' },
]
