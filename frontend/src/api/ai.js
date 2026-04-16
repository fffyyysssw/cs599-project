import request from './index'

export function analyzeText(data) {
  return request.post('/ai/analyze', data)
}
