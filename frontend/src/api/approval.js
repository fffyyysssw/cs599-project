import request from './index'

export function getPendingApprovals(params) {
  return request.get('/approvals/pending', { params })
}

export function approveStep(id, data) {
  return request.post(`/approvals/${id}/approve`, data)
}

export function rejectStep(id, data) {
  return request.post(`/approvals/${id}/reject`, data)
}

export function returnStep(id, data) {
  return request.post(`/approvals/${id}/return`, data)
}
