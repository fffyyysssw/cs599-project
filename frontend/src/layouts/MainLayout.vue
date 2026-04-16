<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useUserStore } from '@/stores/user'
import { getRoleLabel } from '@/utils'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const collapsed = ref(false)

const menuItems = computed(() => {
  const items = [
    { path: '/dashboard', label: '首页仪表盘' },
    { path: '/smart-apply', label: '智能发起' },
    { path: '/my-applications', label: '我的申请' },
    { path: '/rules', label: '规则查看' },
  ]

  if (userStore.userInfo?.role !== 'employee') {
    items.splice(3, 0, { path: '/pending-approvals', label: '待审批' })
  }
  return items
})

const pageTitle = computed(() => route.meta.title || 'SmartFlow')

function updateCollapse() {
  collapsed.value = window.innerWidth < 960
}

function handleLogout() {
  userStore.clearAuth()
  router.push('/login')
}

onMounted(() => {
  updateCollapse()
  window.addEventListener('resize', updateCollapse)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateCollapse)
})
</script>

<template>
  <el-container class="layout-shell">
    <el-aside :width="collapsed ? '88px' : '240px'" class="layout-aside">
      <div class="brand-block">
        <div class="brand-mark">SF</div>
        <div v-if="!collapsed" class="brand-copy">
          <strong>SmartFlow</strong>
          <span>AI 驱动审批助手</span>
        </div>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="collapsed"
        router
        class="layout-menu"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div>
          <h1 class="header-title">{{ pageTitle }}</h1>
          <p class="header-subtitle">围绕请假、报销、采购三类业务流程设计</p>
        </div>

        <el-dropdown>
          <div class="user-badge">
            <div>
              <strong>{{ userStore.userInfo?.real_name || '访客' }}</strong>
              <p>{{ getRoleLabel(userStore.userInfo?.role) }} · {{ userStore.userInfo?.department || '--' }}</p>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/dashboard')">返回首页</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-shell {
  min-height: 100vh;
}

.layout-aside {
  padding: 20px 16px;
  background: linear-gradient(180deg, #204f4b 0%, #173d3b 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  color: #fff9ef;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: rgba(255, 249, 239, 0.14);
  font-weight: 700;
  letter-spacing: 1px;
}

.brand-copy {
  display: grid;
  gap: 2px;
}

.brand-copy span {
  font-size: 12px;
  color: rgba(255, 249, 239, 0.76);
}

.layout-menu {
  border-right: none;
  background: transparent;
}

:deep(.layout-menu .el-menu-item) {
  margin-bottom: 8px;
  border-radius: 14px;
  color: rgba(255, 249, 239, 0.88);
}

:deep(.layout-menu .el-menu-item.is-active) {
  background: rgba(255, 249, 239, 0.14);
  color: #fffdf8;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: auto;
  padding: 24px 28px 8px;
}

.header-title {
  margin: 0;
  font-size: 28px;
}

.header-subtitle {
  margin: 6px 0 0;
  color: var(--muted);
}

.user-badge {
  min-width: 180px;
  padding: 12px 16px;
  border: 1px solid rgba(229, 216, 197, 0.9);
  border-radius: 18px;
  background: rgba(255, 252, 246, 0.9);
  box-shadow: var(--shadow);
  cursor: pointer;
}

.user-badge p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.layout-main {
  padding: 0;
}

@media (max-width: 768px) {
  .layout-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .user-badge {
    width: 100%;
  }
}
</style>
