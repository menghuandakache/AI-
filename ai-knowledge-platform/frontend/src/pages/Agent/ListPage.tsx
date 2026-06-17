import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Table, Space, Modal, Form, Input, Select, Card, message } from 'antd'
import { PlusOutlined, RobotOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { getAgents, createAgent, disableAgent, enableAgent, generateAgent } from '../../api/agent'
import { getKnowledgeBases } from '../../api/kb'
import StatusTag from '../../components/StatusTag'
import { formatTime } from '../../utils/formatTime'
import { ANSWER_STYLES } from '../../utils/constants'

export default function AgentListPage() {
  const [open, setOpen] = useState(false)
  const [genOpen, setGenOpen] = useState(false)
  const [form] = Form.useForm()
  const [genForm] = Form.useForm()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const res: any = await getAgents()
      return res
    },
  })

  const { data: kbList } = useQuery({
    queryKey: ['kb-list-agent'],
    queryFn: async () => {
      const res: any = await getKnowledgeBases({ page_size: 100 })
      return res?.items || []
    },
  })

  const createMut = useMutation({
    mutationFn: (vals: any) => createAgent(vals),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      message.success('创建成功')
      setOpen(false)
      form.resetFields()
    },
  })

  const disableMut = useMutation({
    mutationFn: (id: string) => disableAgent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      message.success('已停用')
    },
  })

  const enableMut = useMutation({
    mutationFn: (id: string) => enableAgent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      message.success('已启用')
    },
  })

  const genMut = useMutation({
    mutationFn: (vals: any) => generateAgent(vals),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      message.success('一键生成成功')
      setGenOpen(false)
      genForm.resetFields()
    },
  })

  const columns = [
    { title: 'Agent名称', dataIndex: 'name' },
    { title: '描述', dataIndex: 'description', ellipsis: true },
    {
      title: '状态', dataIndex: 'status', width: 80,
      render: (s: string) => <StatusTag status={s} />,
    },
    {
      title: '创建时间', dataIndex: 'created_at', width: 160,
      render: (v: string) => formatTime(v),
    },
    {
      title: '操作', key: 'actions', width: 280,
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" type="primary" icon={<RobotOutlined />}
            onClick={() => navigate(`/agents/${record.id}/chat`)}>问答</Button>
          <Button size="small" onClick={() => navigate(`/agents/${record.id}/config`)}>配置</Button>
          {record.status === 'disabled' ? (
            <Button size="small" type="primary"
              onClick={() => enableMut.mutate(record.id)}>启用</Button>
          ) : (
            <Button size="small" onClick={() => disableMut.mutate(record.id)}>停用</Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>专家Agent管理</h2>
        <Space>
          <Button icon={<ThunderboltOutlined />} onClick={() => setGenOpen(true)}>一键生成</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>创建Agent</Button>
        </Space>
      </div>

      <Table dataSource={data?.items || []} columns={columns} rowKey="id" loading={isLoading}
        pagination={{ pageSize: 20 }} />

      {/* Create Modal */}
      <Modal title="创建专家Agent" open={open}
        onCancel={() => setOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={(vals) => createMut.mutate(vals)}>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input placeholder="Agent名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} placeholder="描述Agent用途" />
          </Form.Item>
          <Form.Item name="kb_ids" label="绑定知识库" rules={[{ required: true }]}>
            <Select mode="multiple" placeholder="选择知识库"
              options={(kbList as any[])?.map((k: any) => ({ value: k.id, label: k.name })) || []} />
          </Form.Item>
          <Form.Item name="answer_style" label="回答风格">
            <Select options={ANSWER_STYLES} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Generate Modal */}
      <Modal title="一键生成专家Agent" open={genOpen}
        onCancel={() => setGenOpen(false)} onOk={() => genForm.submit()}>
        <Form form={genForm} layout="vertical" onFinish={(vals) => genMut.mutate(vals)}>
          <Form.Item name="kb_id" label="选择知识库" rules={[{ required: true }]}>
            <Select placeholder="选择知识库"
              options={(kbList as any[])?.map((k: any) => ({ value: k.id, label: k.name })) || []} />
          </Form.Item>
          <Form.Item name="name" label="Agent名称（可选）">
            <Input placeholder="留空则自动生成" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
