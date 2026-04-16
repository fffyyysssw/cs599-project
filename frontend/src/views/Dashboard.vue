<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { getDashboardStats } from '@/api/application'
import StatusTag from '@/components/StatusTag.vue'
import { useUserStore } from '@/stores/user'
import { formatDateTime, getProcessLabel, getRoleLabel } from '@/utils'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const stats = ref({
  my_pending: 0,
  my_approved: 0,
  my_rejected: 0,
  need_my_approval: 0,
  recent_applications: [],
})

const cards = computed(() => [
  {
    title: '我的待处理',
    value: stats.value.my_pending,
    description: '已提交且仍在审批中的申请',
  },
  {
    title: '已通过',
    value: stats.value.my_approved,
    description: '审批链路已经全部完成',
  },
  {
    title: '已驳回',
    value: stats.value.my_rejected,
    description: '被驳回后不可继续流转',
  },
  {
    title: '待我审批',
    value: stats.value.need_my_approval,
    description: '当前轮到我处理的审批任务',
  },
])

async function fetchStats() {
  loading.value = true
  try {
    const response = await getDashboardStats()
    stats.value = response.data
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

function goDetail(row) {
  router.push(`/applications/${row.id}`)
}

onMounted(fetchStats)
</script>

<template>
  <div class="page-shell dashboard-page">
    <div class="hero-card page-card">
      <div>
        <p class="soft-chip">当前身份：{{ getRoleLabel(userStore.userInfo?.role) }}</p>
        <h2 class="section-title">欢迎回来，{{ userStore.userInfo?.real_name }}</h2>
        <p class="section-subtitle">
          这里汇总了你的审批状态与最近申请，适合快速切入今天的工作流。
        </p>
      </div>
      <el-button type="primary" size="large" @click="router.push('/smart-apply')">
        发起新的智能申请
      </el-button>
    </div>

    <div class="data-grid summary-grid">
      <div v-for="card in cards" :key="card.title" class="summary-card page-card">
        <p>{{ card.title }}</p>
        <strong>{{ card.value }}</strong>
        <span>{{ card.description }}</span>
      </div>
    </div>

    <div class="page-card table-card">
      <div class="table-head">
        <div>
          <h3>最近申请</h3>
          <p>点击记录可直接查看完整审批详情</p>
        </div>
        <el-button text @click="fetchStats" :loading="loading">刷新数据</el-button>
      </div>

      <el-table :data="stats.recent_applications" v-loading="loading" @row-click="goDetail">
        <el-table-column prop="application_no" label="申请编号" min-width="180" />
        <el-table-column prop="title" label="标题" min-width="220" />
        <el-table-column label="流程类型" min-width="120">
          <template #default="{ row }">
            {{ getProcessLabel(row.process_type) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <StatusTag :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 18px;
}

.hero-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
}

.summary-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.summary-card {
  display: grid;
  gap: 10px;
  padding: 24px;
}

.summary-card p,
.summary-card span {
  margin: 0;
}

.summary-card strong {
  font-size: 40px;
  line-height: 1;
  color: var(--brand);
}

.summary-card span {
  color: var(--muted);
  line-height: 1.7;
}

.table-card {
  padding: 24px;
}

.table-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.table-head h3 {
  margin: 0 0 6px;
}

.table-head p {
  margin: 0;
  color: var(--muted);
}

@media (max-width: 1024px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-card {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
