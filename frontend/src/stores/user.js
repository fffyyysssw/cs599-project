import { defineStore } from 'pinia'

import { fetchMe } from '@/api/auth'

const TOKEN_KEY = 'smartflow_token'
const USER_KEY = 'smartflow_user'

function safeParse(value) {
  try {
    return value ? JSON.parse(value) : null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    userInfo: safeParse(localStorage.getItem(USER_KEY)),
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    isEmployee: (state) => state.userInfo?.role === 'employee',
    displayName: (state) => state.userInfo?.real_name || '未登录用户',
  },
  actions: {
    setAuth(token, userInfo) {
      this.token = token
      this.userInfo = userInfo
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(userInfo))
    },
    clearAuth() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },
    async refreshProfile() {
      if (!this.token) {
        return null
      }
      const response = await fetchMe()
      this.userInfo = response.data
      localStorage.setItem(USER_KEY, JSON.stringify(response.data))
      return response.data
    },
  },
})
