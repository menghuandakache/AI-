import { useEffect } from 'react'
import { useRoutes, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { routes } from './router/routes'

export default function App() {
  const { token } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (!token && location.pathname !== '/login') {
      navigate('/login', { replace: true })
    }
  }, [token, location.pathname, navigate])

  const element = useRoutes(routes)
  return element
}
