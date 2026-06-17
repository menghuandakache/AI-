import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Table, Space, Modal, Form, Input, Switch, Card, message, Popconfirm } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SettingOutlined } from '@ant-design/icons'
import { getModelConfigs, createModelConfig, updateModelConfig, deleteModelConfig } from '../../api/models'
import { formatTime } from '../../utils/formatTime'

export default function ModelConfigPage() {
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<any>(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['model-configs'],
    queryFn: async () => {
      const res: any = await getModelConfigs()
      return res
    },
  })

  const saveMut = useMutation({
    mutationFn: (vals: any) => editing
      ? updateModelConfig(editing.id, vals)
      : createModelConfig(vals),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['model-configs'] })
      message.success(editing ? '更新成功' : '添加成功')
      setOpen(false)
      setEditing(null)
      form.resetFields()
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteModelConfig(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['model-configs'] })
      message.success('删除成功')
    },
  })

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ is_default: false })
    setOpen(true)
  }

  const openEdit = (record: any) => {
    setEditing(record)
    form.setFieldsValue(record)
    setOpen(true)
  }

  const columns = [
    { title: '标签', dataIndex: 'label', key: 'label' },
    { title: '模型名', dataIndex: 'model_name', key: 'model_name' },
    { title: 'API 地址', dataIndex: 'base_url', key: 'base_url', ellipsis: true },
    {
      title: '默认', dataIndex: 'is_default', key: 'is_default', width: 60,
      render: (v: boolean) => v ? '✅' : '-',
    },
    {
      title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 150,
      render: (v: string) => formatTime(v),
    },
    {
      title: '操作', key: 'actions', width: 150,
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除？" onConfirm={() => deleteMut.mutate(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2><SettingOutlined /> 模型配置管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>添加模型</Button>
      </div>

      <Card>
        <p style={{ color: '#666', marginBottom: 16 }}>
          在这里配置大模型 API 的连接信息。配置后在 Agent 对话页面可以选择使用哪个模型。
        </p>
        <Table
          dataSource={data?.items || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 20 }}
        />
      </Card>

      <Modal
        title={editing ? '编辑模型配置' : '添加模型配置'}
        open={open}
        onCancel={() => { setOpen(false); setEditing(null) }}
        onOk={() => form.submit()}
        width={560}
      >
        <Form form={form} layout="vertical" onFinish={(vals) => saveMut.mutate(vals)}>
          <Form.Item name="label" label="显示名称" rules={[{ required: true, message: '请输入' }]}>
            <Input placeholder="例如：GPT-4o / 通义千问 / DeepSeek" />
          </Form.Item>
          <Form.Item name="model_name" label="模型名称" rules={[{ required: true, message: '请输入' }]}>
            <Input placeholder="例如：gpt-4o / qwen-turbo / deepseek-chat" />
          </Form.Item>
          <Form.Item name="base_url" label="API 地址" rules={[{ required: true, message: '请输入' }]}>
            <Input placeholder="例如：https://api.openai.com/v1" />
          </Form.Item>
          <Form.Item name="api_key" label="API Key" rules={[{ required: true, message: '请输入' }]}>
            <Input.Password placeholder="sk-..." />
          </Form.Item>
          <Form.Item name="is_default" label="设为默认" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
