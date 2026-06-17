import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export function useAuth() {
  const { token, username, role, logout } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!token) {
      navigate('/login')
    }
  }, [token, navigate])

  return { token, username, role, logout, isLoggedIn: !!token }
}
