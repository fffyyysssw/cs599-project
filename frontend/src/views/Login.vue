<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { login } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { getRoleLabel } from '@/utils'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  username: 'zhangsan',
  password: '123456',
})

const demoAccounts = [
  { username: 'zhangsan', role: 'employee', department: '技术部' },
  { username: 'lisi', role: 'manager', department: '技术部' },
  { username: 'wangwu', role: 'finance', department: '财务部' },
  { username: 'zhaoliu', role: 'hr', department: '人力资源部' },
  { username: 'sunqi', role: 'procurement', department: '采购部' },
  { username: 'admin', role: 'admin', department: '管理层' },
]

function fillAccount(username) {
  form.username = username
  form.password = '123456'
}

async function handleLogin() {
  loading.value = true
  try {
    const response = await login(form)
    userStore.setAuth(response.data.access_token, response.data.user)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-shell">
    <div class="login-card page-card">
      <section class="intro-panel">
        <p class="intro-label">SmartFlow</p>
        <h1>AI 驱动的审批/办公流程助手</h1>
        <p class="intro-desc">
          覆盖请假、报销、采购三类审批场景，支持自然语言分析、动态表单预填、审批链路推荐与完整流转追踪。
        </p>

        <div class="feature-list">
          <span class="soft-chip">LangGraph 工作流</span>
          <span class="soft-chip">FastAPI + Vue 3</span>
          <span class="soft-chip">课程演示友好</span>
        </div>

        <div class="account-grid">
          <div
            v-for="account in demoAccounts"
            :key="account.username"
            class="account-item"
            @click="fillAccount(account.username)"
          >
            <strong>{{ account.username }}</strong>
            <p>{{ getRoleLabel(account.role) }} · {{ account.department }}</p>
          </div>
        </div>
      </section>

      <section class="form-panel">
        <div>
          <h2>登录系统</h2>
          <p>默认密码均为 `123456`，点击左侧账号可一键填充。</p>
        </div>

        <el-form label-position="top" @submit.prevent="handleLogin">
          <el-form-item label="用户名">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>

          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
          </el-form-item>

          <el-button type="primary" size="large" :loading="loading" class="login-button" @click="handleLogin">
            进入 SmartFlow
          </el-button>
        </el-form>
      </section>
    </div>
  </div>
</template>

<style scoped>
.login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.login-card {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  width: min(1120px, 100%);
  overflow: hidden;
}

.intro-panel {
  padding: 48px;
  background: linear-gradient(155deg, rgba(27, 89, 85, 0.98), rgba(20, 65, 63, 0.95));
  color: #fff9ef;
}

.intro-label {
  margin: 0 0 12px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: rgba(255, 249, 239, 0.72);
}

.intro-panel h1 {
  margin: 0;
  font-size: 42px;
  line-height: 1.2;
}

.intro-desc {
  margin: 18px 0 28px;
  line-height: 1.8;
  color: rgba(255, 249, 239, 0.84);
}

.feature-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 28px;
}

.account-grid {
  display: grid;
  gap: 12px;
}

.account-item {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 249, 239, 0.1);
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.account-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 249, 239, 0.16);
}

.account-item p {
  margin: 6px 0 0;
  color: rgba(255, 249, 239, 0.76);
}

.form-panel {
  display: grid;
  align-content: center;
  gap: 20px;
  padding: 48px;
  background: rgba(255, 252, 246, 0.96);
}

.form-panel h2 {
  margin: 0 0 8px;
  font-size: 30px;
}

.form-panel p {
  margin: 0;
  color: var(--muted);
}

.login-button {
  width: 100%;
  margin-top: 12px;
}

@media (max-width: 900px) {
  .login-card {
    grid-template-columns: 1fr;
  }

  .intro-panel,
  .form-panel {
    padding: 28px;
  }

  .intro-panel h1 {
    font-size: 34px;
  }
}
</style>
