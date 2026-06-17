import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, Descriptions, Button, Space, Spin, Tag, Table } from 'antd'
import { EditOutlined } from '@ant-design/icons'
import { getKnowledgeDetail, getKnowledgeChunks } from '../../api/knowledge'
import StatusTag from '../../components/StatusTag'
import MarkdownViewer from '../../components/MarkdownViewer'
import { formatTime } from '../../utils/formatTime'

export default function KnowledgeDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: knowledge, isLoading } = useQuery({
    queryKey: ['knowledge-detail', id],
    queryFn: async () => {
      const res: any = await getKnowledgeDetail(id!)
      return res
    },
    enabled: !!id,
  })

  const { data: chunks } = useQuery({
    queryKey: ['knowledge-chunks', id],
    queryFn: async () => {
      const res: any = await getKnowledgeChunks(id!)
      return res || []
    },
    enabled: !!id,
  })

  if (isLoading) return <Spin style={{ display: 'block', margin: '100px auto' }} />

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>{knowledge?.title || '知识详情'}</h2>
        <Space>
          <Button icon={<EditOutlined />} onClick={() => navigate(`/knowledge/${id}/edit`)}>编辑</Button>
        </Space>
      </div>

      <Card style={{ marginBottom: 24 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="标题">{knowledge?.title}</Descriptions.Item>
          <Descriptions.Item label="状态"><StatusTag status={knowledge?.status} /></Descriptions.Item>
          <Descriptions.Item label="分类">{knowledge?.category || '-'}</Descriptions.Item>
          <Descriptions.Item label="来源类型">{knowledge?.source_type || '-'}</Descriptions.Item>
          <Descriptions.Item label="标签">
            {(knowledge?.tags || []).map((t: string) => <Tag key={t}>{t}</Tag>)}
          </Descriptions.Item>
          <Descriptions.Item label="切片数">{knowledge?.chunk_count || 0}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatTime(knowledge?.created_at)}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{formatTime(knowledge?.updated_at)}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="正文内容" style={{ marginBottom: 24 }}>
        <MarkdownViewer content={knowledge?.content || ''} />
      </Card>

      {chunks && (chunks as any[]).length > 0 && (
        <Card title="知识切片">
          <Table
            dataSource={chunks as any[]}
            rowKey="id"
            pagination={false}
            size="small"
            columns={[
              { title: '序号', dataIndex: 'chunk_index', width: 60 },
              { title: '内容', dataIndex: 'chunk_text', ellipsis: true },
              { title: 'Token数', dataIndex: 'token_count', width: 80 },
            ]}
          />
        </Card>
      )}
    </div>
  )
}
