<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { getPendingApprovals } from '@/api/approval'
import StatusTag from '@/components/StatusTag.vue'
import { formatDateTime, getProcessLabel } from '@/utils'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const filters = reactive({
  page: 1,
  page_size: 10,
  process_type: '',
})

async function fetchData() {
  loading.value = true
  try {
    const response = await getPendingApprovals({
      page: filters.page,
      page_size: filters.page_size,
      process_type: filters.process_type || undefined,
    })
    tableData.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

function goDetail(row) {
  router.push(`/applications/${row.id}`)
}

onMounted(fetchData)
</script>

<template>
  <div class="page-shell page-grid">
    <div class="page-card filter-card">
      <div>
        <h2 class="section-title">待审批</h2>
        <p class="section-subtitle">这里只展示当前轮到你处理的审批任务。</p>
      </div>

      <div class="filter-row">
        <el-select v-model="filters.process_type" clearable placeholder="按流程筛选" style="width: 180px">
          <el-option label="请假申请" value="leave" />
          <el-option label="报销申请" value="reimbursement" />
          <el-option label="采购申请" value="purchase" />
        </el-select>

        <el-button type="primary" @click="filters.page = 1; fetchData()">查询</el-button>
      </div>
    </div>

    <div class="page-card table-card">
      <el-table :data="tableData" v-loading="loading" @row-click="goDetail">
        <el-table-column prop="application_no" label="申请编号" min-width="180" />
        <el-table-column prop="title" label="标题" min-width="220" />
        <el-table-column label="流程类型" min-width="120">
          <template #default="{ row }">
            {{ getProcessLabel(row.process_type) }}
          </template>
        </el-table-column>
        <el-table-column label="申请人" min-width="160">
          <template #default="{ row }">
            {{ row.applicant?.real_name }} · {{ row.applicant?.department }}
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

      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          layout="total, prev, pager, next"
          :total="total"
          @current-change="fetchData"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-grid {
  display: grid;
  gap: 18px;
}

.filter-card,
.table-card {
  padding: 24px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
