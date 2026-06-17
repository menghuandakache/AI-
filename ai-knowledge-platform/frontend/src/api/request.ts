import axios from 'axios'
import { message } from 'antd'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
})

request.interceptors.request.use(
  (config) => {
    const stored = localStorage.getItem('akp-auth')
    if (stored) {
      try {
        const { state } = JSON.parse(stored)
        if (state?.token) {
          config.headers.Authorization = `Bearer ${state.token}`
        }
      } catch {}
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.message || error.message || 'Network error'
    if (error.response?.status === 401) {
      localStorage.removeItem('akp-auth')
      window.location.href = '/login'
      message.error('Login expired, please login again')
    } else {
      message.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request
