import request from './index'

export function login(data) {
  return request.post('/auth/login', data)
}

export function fetchMe() {
  return request.get('/auth/me')
}
