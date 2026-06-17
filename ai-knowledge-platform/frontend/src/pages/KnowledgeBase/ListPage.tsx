import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Table, Space, Modal, Input, Select, Form, Card, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { getKnowledgeBases, createKnowledgeBase, updateKnowledgeBase, deleteKnowledgeBase, updateKnowledgeBaseStatus } from '../../api/kb'
import StatusTag from '../../components/StatusTag'
import { formatTime } from '../../utils/formatTime'

export default function KnowledgeBaseListPage() {
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<any>(null)
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['knowledge-bases'],
    queryFn: async () => {
      const res: any = await getKnowledgeBases()
      return res
    },
  })

  const createMut = useMutation({
    mutationFn: (vals: any) => editing ? updateKnowledgeBase(editing.id, vals) : createKnowledgeBase(vals),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge-bases'] })
      message.success(editing ? '更新成功' : '创建成功')
      setOpen(false)
      setEditing(null)
      form.resetFields()
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteKnowledgeBase(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge-bases'] })
      message.success('删除成功')
    },
  })

  const toggleStatus = async (id: string, currentStatus: string) => {
    const newStatus = currentStatus === 'enabled' ? 'disabled' : 'enabled'
    await updateKnowledgeBaseStatus(id, newStatus)
    queryClient.invalidateQueries({ queryKey: ['knowledge-bases'] })
    message.success('状态更新成功')
  }

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setOpen(true)
  }

  const openEdit = (record: any) => {
    setEditing(record)
    form.setFieldsValue(record)
    setOpen(true)
  }

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '业务域', dataIndex: 'domain', key: 'domain' },
    { title: '知识数量', dataIndex: 'knowledge_count', key: 'knowledge_count' },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (s: string) => <StatusTag status={s} />,
    },
    {
      title: '更新时间', dataIndex: 'updated_at', key: 'updated_at',
      render: (v: string) => formatTime(v),
    },
    {
      title: '操作', key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" onClick={() => navigate(`/knowledge-bases/${record.id}`)}>详情</Button>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Button size="small" onClick={() => toggleStatus(record.id, record.status)}>
            {record.status === 'enabled' ? '停用' : '启用'}
          </Button>
          <Button size="small" danger icon={<DeleteOutlined />} onClick={() => {
            Modal.confirm({
              title: '确认删除',
              content: `确定要删除知识库「${record.name}」吗？`,
              onOk: () => deleteMut.mutate(record.id),
            })
          }}>删除</Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>知识库管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新建知识库</Button>
      </div>

      <Table
        dataSource={data?.items || []}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 20 }}
      />

      <Modal
        title={editing ? '编辑知识库' : '新建知识库'}
        open={open}
        onCancel={() => { setOpen(false); setEditing(null) }}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={(vals) => createMut.mutate(vals)}>
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
            <Input placeholder="知识库名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="知识库描述" />
          </Form.Item>
          <Form.Item name="domain" label="业务域">
            <Select placeholder="选择业务域" allowClear options={[
              { value: 'Finance', label: '财务' },
              { value: 'HR', label: '人事' },
              { value: 'Legal', label: '法务' },
              { value: 'Procurement', label: '采购' },
              { value: 'Workplace', label: '职场' },
            ]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
