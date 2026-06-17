import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { login } from '../../api/auth'
import { useAuthStore } from '../../store/authStore'

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      const res: any = await login(values.username, values.password)
      setAuth(res.access_token, res.username, res.role, res.user_id)
      message.success('登录成功')
      navigate('/dashboard', { replace: true })
    } catch {
      // Error handled by interceptor
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <h3 style={{ textAlign: 'center', marginBottom: 24 }}>登录</h3>
      <Form onFinish={onFinish} size="large">
        <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
          <Input prefix={<UserOutlined />} placeholder="用户名" />
        </Form.Item>
        <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
          <Input.Password prefix={<LockOutlined />} placeholder="密码" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            登录
          </Button>
        </Form.Item>
      </Form>
      <div style={{ textAlign: 'center', color: '#999', fontSize: 12 }}>
        测试账号：admin / admin123
      </div>
    </Card>
  )
}
