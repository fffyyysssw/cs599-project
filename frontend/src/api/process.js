import request from './index'

export function getProcessTypes() {
  return request.get('/process-types')
}

export function getProcessTypeDetail(code) {
  return request.get(`/process-types/${code}`)
}
