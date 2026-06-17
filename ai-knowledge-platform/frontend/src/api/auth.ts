import request from './request'

export async function login(username: string, password: string) {
  return request.post('/auth/login', { username, password })
}

export async function getMe() {
  return request.get('/auth/me')
}

export async function logout() {
  return request.post('/auth/logout')
}
