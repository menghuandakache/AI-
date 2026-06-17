import { useQuery } from '@tanstack/react-query'
import { Row, Col, Card, Statistic, Table, Tabs, Spin, Progress } from 'antd'
import {
  FileTextOutlined, CheckCircleOutlined, MessageOutlined,
  LikeOutlined, DislikeOutlined, WarningOutlined
} from '@ant-design/icons'
import { getOverviewStats, getHotKnowledge, getFeedbackStats, getNoAnswerQuestions, getRecentQA } from '../../api/stats'
import { formatTime } from '../../utils/formatTime'

export default function StatsPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats-overview'],
    queryFn: async () => {
      const res: any = await getOverviewStats()
      return res
    },
  })

  const { data: hotKnowledge } = useQuery({
    queryKey: ['stats-hot'],
    queryFn: async () => {
      const res: any = await getHotKnowledge(10)
      return res || []
    },
  })

  const { data: feedbackStats } = useQuery({
    queryKey: ['stats-feedback'],
    queryFn: async () => {
      const res: any = await getFeedbackStats()
      return res
    },
  })

  const { data: noAnswer } = useQuery({
    queryKey: ['stats-no-answer'],
    queryFn: async () => {
      const res: any = await getNoAnswerQuestions(20)
      return res || []
    },
  })

  const { data: recentQA } = useQuery({
    queryKey: ['stats-recent-qa'],
    queryFn: async () => {
      const res: any = await getRecentQA(20)
      return res || []
    },
  })

  if (isLoading) return <Spin style={{ display: 'block', margin: '100px auto' }} />

  const overviewTabs = [
    {
      key: 'overview',
      label: '总览',
      children: (
        <div>
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={8} md={4}>
              <Card>
                <Statistic title="知识总数" value={stats?.total_knowledge || 0} prefix={<FileTextOutlined />} />
              </Card>
            </Col>
            <Col xs={12} sm={8} md={4}>
              <Card>
                <Statistic title="可用知识" value={stats?.available_knowledge || 0} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#3f8600' }} />
              </Card>
            </Col>
            <Col xs={12} sm={8} md={4}>
              <Card>
                <Statistic title="知识库数" value={stats?.total_kb || 0} />
              </Card>
            </Col>
            <Col xs={12} sm={8} md={4}>
              <Card>
                <Statistic title="问答总数" value={stats?.total_qa || 0} prefix={<MessageOutlined />} />
              </Card>
            </Col>
            <Col xs={12} sm={8} md={4}>
              <Card>
                <Statistic title="点赞" value={stats?.like_count || 0} prefix={<LikeOutlined />} valueStyle={{ color: '#1677ff' }} />
              </Card>
            </Col>
            <Col xs={12} sm={8} md={4}>
              <Card>
                <Statistic title="点踩" value={stats?.dislike_count || 0} prefix={<DislikeOutlined />} valueStyle={{ color: '#ff4d4f' }} />
              </Card>
            </Col>
          </Row>
          {feedbackStats && (
            <Card title="满意度" style={{ marginBottom: 24 }}>
              <Progress type="circle" percent={feedbackStats.like_rate || 0}
                format={(p) => `${p?.toFixed(0)}%`} />
              <span style={{ marginLeft: 16, color: '#666' }}>
                好评率 ({feedbackStats.like_count}/{feedbackStats.total_feedback})
              </span>
            </Card>
          )}
        </div>
      ),
    },
    {
      key: 'hot',
      label: '热门知识',
      children: (
        <Table
          dataSource={hotKnowledge as any[]}
          rowKey="knowledge_id"
          pagination={false}
          columns={[
            { title: '知识标题', dataIndex: 'title', ellipsis: true },
            { title: '知识库', dataIndex: 'kb_name' },
            { title: '分类', dataIndex: 'category' },
            { title: '引用次数', dataIndex: 'cite_count' },
          ]}
        />
      ),
    },
    {
      key: 'no-answer',
      label: '无答案问题',
      children: (
        <Table
          dataSource={noAnswer as any[]}
          rowKey="question"
          pagination={false}
          columns={[
            { title: '问题', dataIndex: 'question', ellipsis: true },
            { title: '出现次数', dataIndex: 'count', width: 100 },
            { title: '最近时间', dataIndex: 'last_asked', width: 160, render: (v: string) => formatTime(v) },
          ]}
        />
      ),
    },
    {
      key: 'recent',
      label: '最近问答',
      children: (
        <Table
          dataSource={recentQA as any[]}
          rowKey="id"
          pagination={false}
          columns={[
            { title: '问题', dataIndex: 'question', ellipsis: true },
            { title: '状态', dataIndex: 'status', width: 80 },
            { title: '反馈', dataIndex: 'feedback', width: 60 },
            { title: '时间', dataIndex: 'created_at', width: 160, render: (v: string) => formatTime(v) },
          ]}
        />
      ),
    },
  ]

  return (
    <div>
      <h2>数据看板</h2>
      <Tabs items={overviewTabs} />
    </div>
  )
}
