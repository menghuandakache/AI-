import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Form, Input, Select, Button, Card, Space, message, Spin, Segmented } from 'antd'
import { EditOutlined, EyeOutlined, AppstoreOutlined } from '@ant-design/icons'
import { getKnowledgeDetail, createKnowledge, updateKnowledge } from '../../api/knowledge'
import { getKnowledgeBases } from '../../api/kb'
import { CATEGORIES } from '../../utils/constants'
import MarkdownViewer from '../../components/MarkdownViewer'

type ViewMode = 'split' | 'edit' | 'preview'

export default function KnowledgeEditPage() {
  const { id } = useParams<{ id: string }>()
  const isNew = !id || id === 'new'
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('split')
  const [contentPreview, setContentPreview] = useState('')

  const { data: kbList } = useQuery({
    queryKey: ['kb-list-edit'],
    queryFn: async () => {
      const res: any = await getKnowledgeBases({ page_size: 100 })
      return res?.items || []
    },
  })

  const { data: knowledge, isLoading: detailLoading } = useQuery({
    queryKey: ['knowledge-detail', id],
    queryFn: async () => {
      const res: any = await getKnowledgeDetail(id!)
      return res
    },
    enabled: !isNew,
  })

  useEffect(() => {
    if (knowledge && !isNew) {
      form.setFieldsValue(knowledge)
      setContentPreview(knowledge.content || '')
    }
  }, [knowledge, isNew, form])

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      if (isNew) {
        await createKnowledge({ ...values, status: 'draft' })
        message.success('创建成功')
      } else {
        await updateKnowledge(id!, values)
        message.success('更新成功')
      }
      queryClient.invalidateQueries({ queryKey: ['knowledge-list'] })
      navigate('/knowledge')
    } catch {
      // handled by interceptor
    } finally {
      setLoading(false)
    }
  }

  if (!isNew && detailLoading) return <Spin style={{ display: 'block', margin: '100px auto' }} />

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>{isNew ? '新建知识' : '编辑知识'}</h2>
        <Segmented
          value={viewMode}
          onChange={(v) => setViewMode(v as ViewMode)}
          options={[
            { label: <><EditOutlined /> 编辑</>, value: 'edit' },
            { label: <><AppstoreOutlined /> 分屏</>, value: 'split' },
            { label: <><EyeOutlined /> 预览</>, value: 'preview' },
          ]}
        />
      </div>
      <Card style={{ maxWidth: viewMode === 'split' ? '100%' : 900 }}>
        <Form form={form} layout="vertical" onFinish={onFinish}
          initialValues={{ tags: [], status: 'draft' }}>
          <Form.Item name="kb_id" label="所属知识库" rules={[{ required: true, message: '请选择知识库' }]}>
            <Select placeholder="选择知识库" options={(kbList as any[])?.map((k: any) => ({ value: k.id, label: k.name })) || []} />
          </Form.Item>
          <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input placeholder="知识标题" maxLength={500} />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Select placeholder="选择分类" allowClear options={CATEGORIES.map(c => ({ value: c, label: c }))} />
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Select mode="tags" placeholder="输入标签后回车" />
          </Form.Item>
          <Form.Item name="summary" label="摘要">
            <Input.TextArea rows={2} placeholder="知识摘要（可选）" />
          </Form.Item>

          {/* Markdown editor with live preview */}
          <Form.Item name="content" label="正文" rules={[{ required: true, message: '请输入正文' }]}>
            {viewMode === 'split' ? (
              <div style={{ display: 'flex', gap: 16, minHeight: 420 }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ marginBottom: 4, color: '#999', fontSize: 12 }}>编辑</div>
                  <Input.TextArea
                    style={{ flex: 1, fontFamily: 'monospace', fontSize: 14, resize: 'none' }}
                    placeholder="知识正文内容，支持 Markdown 格式"
                    onChange={(e) => setContentPreview(e.target.value)}
                  />
                </div>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                  <div style={{ marginBottom: 4, color: '#999', fontSize: 12 }}>预览</div>
                  <div style={{
                    flex: 1, border: '1px solid #d9d9d9', borderRadius: 6, padding: '12px 16px',
                    overflow: 'auto', background: '#fafafa',
                  }}>
                    {contentPreview ? (
                      <MarkdownViewer content={contentPreview} />
                    ) : (
                      <span style={{ color: '#ccc' }}>在左侧输入内容后此处实时预览...</span>
                    )}
                  </div>
                </div>
              </div>
            ) : viewMode === 'edit' ? (
              <Input.TextArea
                rows={20}
                placeholder="知识正文内容，支持 Markdown 格式"
                style={{ fontFamily: 'monospace', fontSize: 14 }}
                onChange={(e) => setContentPreview(e.target.value)}
              />
            ) : (
              <div style={{ border: '1px solid #d9d9d9', borderRadius: 6, padding: '12px 16px', minHeight: 300, background: '#fafafa' }}>
                {contentPreview ? (
                  <MarkdownViewer content={contentPreview} />
                ) : (
                  <span style={{ color: '#ccc' }}>暂无内容</span>
                )}
              </div>
            )}
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>保存</Button>
              <Button onClick={() => navigate(-1)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
