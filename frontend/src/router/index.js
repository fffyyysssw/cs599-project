import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '@/layouts/MainLayout.vue'
import ApplicationDetail from '@/views/ApplicationDetail.vue'
import Dashboard from '@/views/Dashboard.vue'
import Login from '@/views/Login.vue'
import MyApplications from '@/views/MyApplications.vue'
import PendingApprovals from '@/views/PendingApprovals.vue'
import Rules from '@/views/Rules.vue'
import SmartApply from '@/views/SmartApply.vue'

function readUser() {
  try {
    return JSON.parse(localStorage.getItem('smartflow_user') || 'null')
  } catch {
    return null
  }
}

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true },
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { requiresAuth: true, title: '首页仪表盘' },
      },
      {
        path: '/smart-apply',
        name: 'SmartApply',
        component: SmartApply,
        meta: { requiresAuth: true, title: '智能发起' },
      },
      {
        path: '/my-applications',
        name: 'MyApplications',
        component: MyApplications,
        meta: { requiresAuth: true, title: '我的申请' },
      },
      {
        path: '/pending-approvals',
        name: 'PendingApprovals',
        component: PendingApprovals,
        meta: {
          requiresAuth: true,
          title: '待审批',
          roles: ['manager', 'finance', 'hr', 'procurement', 'admin'],
        },
      },
      {
        path: '/applications/:id',
        name: 'ApplicationDetail',
        component: ApplicationDetail,
        meta: { requiresAuth: true, title: '申请详情' },
      },
      {
        path: '/rules',
        name: 'Rules',
        component: Rules,
        meta: { requiresAuth: true, title: '规则查看' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('smartflow_token')
  const user = readUser()

  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }

  if (to.meta.roles && user && !to.meta.roles.includes(user.role)) {
    next('/dashboard')
    return
  }

  next()
})

export default router
