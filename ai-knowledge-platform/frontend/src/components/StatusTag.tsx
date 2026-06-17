import { Tag } from 'antd'

const statusColors: Record<string, string> = {
  enabled: 'green',
  disabled: 'red',
  deleted: 'default',
  draft: 'orange',
  available: 'green',
  unavailable: 'red',
  active: 'blue',
  inactive: 'default',
  uploaded: 'default',
  parsing: 'processing',
  parsed: 'cyan',
  failed: 'red',
  imported: 'green',
}

const statusLabels: Record<string, string> = {
  enabled: '启用',
  disabled: '停用',
  deleted: '已删除',
  draft: '草稿',
  available: '可用',
  unavailable: '不可用',
  active: '活跃',
  inactive: '未激活',
  uploaded: '已上传',
  parsing: '解析中',
  parsed: '已解析',
  failed: '失败',
  imported: '已导入',
  answered: '已回答',
  no_answer: '无答案',
  like: '赞',
  dislike: '踩',
}

export default function StatusTag({ status }: { status: string }) {
  return (
    <Tag color={statusColors[status] || 'default'}>
      {statusLabels[status] || status}
    </Tag>
  )
}
