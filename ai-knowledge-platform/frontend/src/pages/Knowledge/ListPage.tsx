import { useState, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Table, Space, Input, Select, Tag, Modal, message, Dropdown } from 'antd'
import { PlusOutlined, SearchOutlined, DeleteOutlined, CheckCircleOutlined, MinusCircleOutlined } from '@ant-design/icons'
import type { TableRowSelection } from 'antd/es/table/interface'
import { getKnowledgeList, deleteKnowledge, publishKnowledge, disableKnowledge } from '../../api/knowledge'
import { getKnowledgeBases } from '../../api/kb'
import StatusTag from '../../components/StatusTag'
import { formatTime } from '../../utils/formatTime'
import { CATEGORIES } from '../../utils/constants'

export default function KnowledgeListPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Persist filters in URL
  const keyword = searchParams.get('keyword') || ''
  const category = searchParams.get('category') || undefined
  const status = searchParams.get('status') || undefined
  const kbId = searchParams.get('kb_id') || undefined

  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])

  const updateFilter = (key: string, value: string | undefined) => {
    const newParams = new URLSearchParams(searchParams)
    if (value) newParams.set(key, value)
    else newParams.delete(key)
    setSearchParams(newParams, { replace: true })
  }

  const { data, isLoading } = useQuery({
    queryKey: ['knowledge-list', { keyword, category, status, kb_id: kbId }],
    queryFn: async () => {
      const res: any = await getKnowledgeList({ keyword, category, status, kb_id: kbId, page_size: 100 })
      return res
    },
  })

  const { data: kbList } = useQuery({
    queryKey: ['kb-list-for-filter'],
    queryFn: async () => {
      const res: any = await getKnowledgeBases({ page_size: 100 })
      return res?.items || []
    },
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['knowledge-list'] })
    setSelectedRowKeys([])
  }

  const publishMut = useMutation({
    mutationFn: (id: string) => publishKnowledge(id),
    onSuccess: () => { invalidate(); message.success('发布成功') },
  })

  const disableMut = useMutation({
    mutationFn: (id: string) => disableKnowledge(id),
    onSuccess: () => { invalidate(); message.success('已停用') },
  })

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteKnowledge(id),
    onSuccess: () => { invalidate(); message.success('删除成功') },
  })

  // Batch operations
  const handleBatchPublish = () => {
    Modal.confirm({
      title: '批量发布', content: `确定要发布选中的 ${selectedRowKeys.length} 条知识吗？`,
      onOk: () => {
        Promise.all(selectedRowKeys.map(id => publishKnowledge(id)))
          .then(() => { invalidate(); message.success(`已发布 ${selectedRowKeys.length} 条`) })
          .catch(() => message.error('部分发布失败'))
      },
    })
  }

  const handleBatchDisable = () => {
    Modal.confirm({
      title: '批量停用', content: `确定要停用选中的 ${selectedRowKeys.length} 条知识吗？`,
      onOk: () => {
        Promise.all(selectedRowKeys.map(id => disableKnowledge(id)))
          .then(() => { invalidate(); message.success(`已停用 ${selectedRowKeys.length} 条`) })
          .catch(() => message.error('部分停用失败'))
      },
    })
  }

  const handleBatchDelete = () => {
    Modal.confirm({
      title: '批量删除', content: `确定要删除选中的 ${selectedRowKeys.length} 条知识吗？此操作不可撤销！`,
      okButtonProps: { danger: true }, okText: '删除',
      onOk: () => {
        Promise.all(selectedRowKeys.map(id => deleteKnowledge(id)))
          .then(() => { invalidate(); message.success(`已删除 ${selectedRowKeys.length} 条`) })
          .catch(() => message.error('部分删除失败'))
      },
    })
  }

  const rowSelection: TableRowSelection<any> = {
    selectedRowKeys,
    onChange: (keys) => setSelectedRowKeys(keys as string[]),
    selections: [Table.SELECTION_ALL, Table.SELECTION_INVERT, Table.SELECTION_NONE],
  }

  const columns = [
    { title: '标题', dataIndex: 'title', ellipsis: true, width: 250 },
    {
      title: '知识库', dataIndex: 'kb_id', width: 120,
      render: (v: string) => {
        const kb = (kbList as any[])?.find((k: any) => k.id === v)
        return kb?.name || v
      },
    },
    { title: '分类', dataIndex: 'category', width: 100 },
    {
      title: '标签', dataIndex: 'tags', width: 200,
      render: (tags: string[]) => tags?.map(t => <Tag key={t}>{t}</Tag>) || null,
    },
    { title: '状态', dataIndex: 'status', width: 80, render: (s: string) => <StatusTag status={s} /> },
    { title: '更新时间', dataIndex: 'updated_at', width: 160, render: (v: string) => formatTime(v) },
    {
      title: '操作', key: 'actions', width: 220,
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" onClick={() => navigate(`/knowledge/${record.id}`)}>查看</Button>
          <Button size="small" onClick={() => navigate(`/knowledge/${record.id}/edit`)}>编辑</Button>
          {record.status === 'draft' && (
            <Button size="small" type="primary" onClick={() => publishMut.mutate(record.id)}>发布</Button>
          )}
          {record.status === 'available' && (
            <Button size="small" onClick={() => disableMut.mutate(record.id)}>停用</Button>
          )}
          <Button size="small" danger onClick={() => {
            Modal.confirm({
              title: '确认删除', content: `确定要删除「${record.title}」吗？`,
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
        <h2>知识条目管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/knowledge/new/edit')}>新建知识</Button>
      </div>

      <Space style={{ marginBottom: 16 }} wrap>
        <Input placeholder="搜索标题/正文" prefix={<SearchOutlined />} value={keyword}
          onChange={e => updateFilter('keyword', e.target.value || undefined)} style={{ width: 200 }} allowClear />
        <Select placeholder="知识库" value={kbId} onChange={v => updateFilter('kb_id', v)} allowClear style={{ width: 150 }}
          options={(kbList as any[])?.map((k: any) => ({ value: k.id, label: k.name })) || []} />
        <Select placeholder="分类" value={category} onChange={v => updateFilter('category', v)} allowClear style={{ width: 120 }}
          options={CATEGORIES.map(c => ({ value: c, label: c }))} />
        <Select placeholder="状态" value={status} onChange={v => updateFilter('status', v)} allowClear style={{ width: 100 }}
          options={[
            { value: 'draft', label: '草稿' },
            { value: 'available', label: '可用' },
            { value: 'unavailable', label: '不可用' },
          ]} />
      </Space>

      {/* Batch action bar */}
      {selectedRowKeys.length > 0 && (
        <div style={{
          marginBottom: 12, padding: '8px 16px', background: '#e6f4ff', borderRadius: 6,
          display: 'flex', alignItems: 'center', gap: 12,
        }}>
          <span>已选 <strong>{selectedRowKeys.length}</strong> 条</span>
          <Button size="small" type="primary" icon={<CheckCircleOutlined />} onClick={handleBatchPublish}>批量发布</Button>
          <Button size="small" icon={<MinusCircleOutlined />} onClick={handleBatchDisable}>批量停用</Button>
          <Button size="small" danger icon={<DeleteOutlined />} onClick={handleBatchDelete}>批量删除</Button>
          <Button size="small" onClick={() => setSelectedRowKeys([])}>取消选择</Button>
        </div>
      )}

      <Table
        dataSource={data?.items || []}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        rowSelection={rowSelection}
        pagination={{ pageSize: 50, showTotal: (t) => `共 ${t} 条` }}
        scroll={{ x: 1200 }}
      />
    </div>
  )
}
