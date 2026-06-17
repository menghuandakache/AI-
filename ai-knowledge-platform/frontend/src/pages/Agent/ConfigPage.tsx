import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Form, Input, Select, Button, Card, Space, message, Spin } from 'antd'
import { getAgent, updateAgent } from '../../api/agent'
import { getKnowledgeBases } from '../../api/kb'
import { ANSWER_STYLES } from '../../utils/constants'

export default function AgentConfigPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form] = Form.useForm()

  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', id],
    queryFn: async () => {
      const res: any = await getAgent(id!)
      return res
    },
    enabled: !!id,
  })

  const { data: kbList } = useQuery({
    queryKey: ['kb-list-config'],
    queryFn: async () => {
      const res: any = await getKnowledgeBases({ page_size: 100 })
      return res?.items || []
    },
  })

  useEffect(() => {
    if (agent) form.setFieldsValue(agent)
  }, [agent, form])

  const updateMut = useMutation({
    mutationFn: (vals: any) => updateAgent(id!, vals),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      queryClient.invalidateQueries({ queryKey: ['agent', id] })
      message.success('配置已更新')
    },
  })

  if (isLoading) return <Spin style={{ display: 'block', margin: '100px auto' }} />

  return (
    <div>
      <h2>Agent 配置 - {agent?.name}</h2>
      <Card style={{ maxWidth: 800 }}>
        <Form form={form} layout="vertical" onFinish={(vals) => updateMut.mutate(vals)}>
          <Form.Item name="name" label="Agent名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="kb_ids" label="绑定知识库" rules={[{ required: true }]}>
            <Select mode="multiple" placeholder="选择知识库"
              options={(kbList as any[])?.map((k: any) => ({ value: k.id, label: k.name })) || []} />
          </Form.Item>
          <Form.Item name="answer_style" label="回答风格">
            <Select options={ANSWER_STYLES} />
          </Form.Item>
          <Form.Item name="citation_policy" label="引用策略">
            <Select options={[
              { value: 'required', label: '必须引用' },
              { value: 'preferred', label: '优先引用' },
              { value: 'none', label: '无需展示' },
            ]} />
          </Form.Item>
          <Form.Item name="no_answer_policy" label="无答案策略">
            <Select options={[
              { value: 'prompt', label: '提示无匹配知识' },
              { value: 'transfer', label: '转人工' },
              { value: 'recommend', label: '推荐相关问题' },
            ]} />
          </Form.Item>
          <Form.Item name="prompt_config" label="System Prompt">
            <Input.TextArea rows={6} placeholder="自定义Agent的system prompt" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">保存配置</Button>
              <Button onClick={() => navigate('/agents')}>返回列表</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
