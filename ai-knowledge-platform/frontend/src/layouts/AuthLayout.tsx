import { Outlet } from 'react-router-dom'
import { Layout, Typography, Space } from 'antd'
import { BookOutlined } from '@ant-design/icons'

const { Content } = Layout
const { Title, Text } = Typography

export default function AuthLayout() {
  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Content style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ textAlign: 'center', maxWidth: 400, width: '100%' }}>
          <div style={{ marginBottom: 32 }}>
            <Space align="center">
              <BookOutlined style={{ fontSize: 36, color: '#1677ff' }} />
              <Title level={2} style={{ margin: 0 }}>AI 知识库管理平台</Title>
            </Space>
            <Text type="secondary">企业级知识管理与智能问答平台</Text>
          </div>
          <Outlet />
        </div>
      </Content>
    </Layout>
  )
}
