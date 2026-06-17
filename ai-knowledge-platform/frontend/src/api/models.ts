import request from './request'

export async function getModelConfigs() {
  return request.get('/models')
}

export async function createModelConfig(data: Record<string, any>) {
  return request.post('/models', data)
}

export async function updateModelConfig(id: string, data: Record<string, any>) {
  return request.put(`/models/${id}`, data)
}

export async function deleteModelConfig(id: string) {
  return request.delete(`/models/${id}`)
}
