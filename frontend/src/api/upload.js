import request from './index'

export function uploadFile(formData) {
  return request.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}
