import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Input, Radio, Card, List, Tag, Space, Select, Spin, Empty } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import { keywordSearch, semanticSearch, hybridSearch } from '../../api/search'
import { getKnowledgeBases } from '../../api/kb'
import StatusTag from '../../components/StatusTag'

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const initialQ = searchParams.get('q') || ''
  const [query, setQuery] = useState(initialQ)
  const [mode, setMode] = useState<'keyword' | 'semantic' | 'hybrid'>('hybrid')
  const [kbId, setKbId] = useState<string | undefined>()

  const { data: kbList } = useQuery({
    queryKey: ['kb-list-search'],
    queryFn: async () => {
      const res: any = await getKnowledgeBases({ page_size: 100 })
      return res?.items || []
    },
  })

  const { data: results, isLoading } = useQuery({
    queryKey: ['search', { query, mode, kbId }],
    queryFn: async () => {
      if (!query.trim()) return []
      const searchFn = mode === 'keyword' ? keywordSearch : mode === 'semantic' ? semanticSearch : hybridSearch
      const res: any = await searchFn({ query, kb_id: kbId })
      return res?.items || []
    },
    enabled: query.length > 0,
  })

  return (
    <div>
      <h2>知识检索</h2>

      <Space style={{ marginBottom: 24 }} wrap>
        <Input.Search
          placeholder="输入搜索关键词..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          style={{ width: 400 }}
          size="large"
          enterButton
        />
        <Radio.Group value={mode} onChange={e => setMode(e.target.value)}>
          <Radio.Button value="keyword">关键词</Radio.Button>
          <Radio.Button value="semantic">语义</Radio.Button>
          <Radio.Button value="hybrid">混合</Radio.Button>
        </Radio.Group>
        <Select placeholder="选择知识库" value={kbId} onChange={setKbId}
          allowClear style={{ width: 150 }}
          options={(kbList as any[])?.map((k: any) => ({ value: k.id, label: k.name })) || []} />
      </Space>

      <Spin spinning={isLoading}>
        {!query ? (
          <Empty description="请输入搜索内容" />
        ) : results && results.length === 0 ? (
          <Empty description="未找到相关内容" />
        ) : (
          <List
            dataSource={results || []}
            renderItem={(item: any) => (
              <Card style={{ marginBottom: 12 }} size="small">
                <div style={{ fontWeight: 'bold', fontSize: 16, marginBottom: 8 }}>{item.title}</div>
                <div style={{ color: '#666', marginBottom: 8, lineHeight: 1.6 }}>
                  {item.chunk_text?.slice(0, 200)}{item.chunk_text?.length > 200 ? '...' : ''}
                </div>
                <Space wrap size={[4, 4]}>
                  {item.tags?.map((t: string) => <Tag key={t}>{t}</Tag>)}
                  {item.category && <Tag color="blue">{item.category}</Tag>}
                  {item.kb_name && <Tag color="green">{item.kb_name}</Tag>}
                  <span style={{ color: '#999', fontSize: 12 }}>
                    相关度: {(item.score * 100).toFixed(0)}%
                  </span>
                </Space>
              </Card>
            )}
          />
        )}
      </Spin>
    </div>
  )
}
