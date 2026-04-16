import request from './index'

export function createApplication(data) {
  return request.post('/applications', data)
}

export function getMyApplications(params) {
  return request.get('/applications/my', { params })
}

export function getApplicationDetail(id) {
  return request.get(`/applications/${id}`)
}

export function getDashboardStats() {
  return request.get('/dashboard/stats')
}
