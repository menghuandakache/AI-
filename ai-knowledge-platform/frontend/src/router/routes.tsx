import { Navigate } from 'react-router-dom'
import { AppstoreOutlined, FileTextOutlined, RobotOutlined, SearchOutlined, BarChartOutlined, DashboardOutlined, UploadOutlined, SettingOutlined } from '@ant-design/icons'
import BasicLayout from '../layouts/BasicLayout'
import AuthLayout from '../layouts/AuthLayout'
import Login from '../pages/Login'
import Dashboard from '../pages/Dashboard'
import KnowledgeBaseList from '../pages/KnowledgeBase/ListPage'
import KnowledgeBaseDetail from '../pages/KnowledgeBase/DetailPage'
import KnowledgeList from '../pages/Knowledge/ListPage'
import KnowledgeEdit from '../pages/Knowledge/EditPage'
import KnowledgeDetail from '../pages/Knowledge/DetailPage'
import DocumentImport from '../pages/DocumentImport'
import AgentList from '../pages/Agent/ListPage'
import AgentConfig from '../pages/Agent/ConfigPage'
import AgentChat from '../pages/Agent/ChatPage'
import SearchPage from '../pages/Search'
import StatsPage from '../pages/Stats'
import ModelConfigPage from '../pages/Settings/ModelConfigPage'

export interface RouteConfig {
  path: string
  name: string
  icon?: React.ReactNode
  element?: React.ReactNode
  hideInMenu?: boolean
  roles?: string[]
}

export const menuRoutes: RouteConfig[] = [
  { path: '/dashboard', name: '工作台', icon: <DashboardOutlined /> },
  { path: '/knowledge-bases', name: '知识库', icon: <AppstoreOutlined /> },
  { path: '/knowledge', name: '知识条目', icon: <FileTextOutlined /> },
  { path: '/document-import', name: '文档导入', icon: <UploadOutlined /> },
  { path: '/agents', name: '专家Agent', icon: <RobotOutlined /> },
  { path: '/search', name: '知识检索', icon: <SearchOutlined /> },
  { path: '/stats', name: '数据看板', icon: <BarChartOutlined /> },
  { path: '/settings', name: '模型配置', icon: <SettingOutlined /> },
]

export const routes = [
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <Login /> },
    ],
  },
  {
    element: <BasicLayout />,
    children: [
      { path: '/', element: <Navigate to="/dashboard" replace /> },
      ...menuRoutes.map(r => ({
        path: r.path,
        element: getElementForRoute(r.path),
      })),
      { path: '/knowledge-bases/:id', element: <KnowledgeBaseDetail /> },
      { path: '/knowledge/:id/edit', element: <KnowledgeEdit /> },
      { path: '/knowledge/:id', element: <KnowledgeDetail /> },
      { path: '/agents/:id/config', element: <AgentConfig /> },
      { path: '/agents/:id/chat', element: <AgentChat /> },
    ],
  },
]

function getElementForRoute(path: string): React.ReactNode {
  const map: Record<string, React.ReactNode> = {
    '/dashboard': <Dashboard />,
    '/knowledge-bases': <KnowledgeBaseList />,
    '/knowledge': <KnowledgeList />,
    '/document-import': <DocumentImport />,
    '/agents': <AgentList />,
    '/search': <SearchPage />,
    '/stats': <StatsPage />,
    '/settings': <ModelConfigPage />,
  }
  return map[path] || <div>Page not found</div>
}
