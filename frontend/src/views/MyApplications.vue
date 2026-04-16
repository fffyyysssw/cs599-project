<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { getMyApplications } from '@/api/application'
import StatusTag from '@/components/StatusTag.vue'
import { formatDateTime, getProcessLabel } from '@/utils'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const filters = reactive({
  page: 1,
  page_size: 10,
  status: '',
  process_type: '',
})

async function fetchData() {
  loading.value = true
  try {
    const response = await getMyApplications({
      page: filters.page,
      page_size: filters.page_size,
      status: filters.status || undefined,
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

function handleSearch() {
  filters.page = 1
  fetchData()
}

function resetFilters() {
  filters.status = ''
  filters.process_type = ''
  filters.page = 1
  fetchData()
}

function handleRowClick(row) {
  router.push(`/applications/${row.id}`)
}

onMounted(fetchData)
</script>

<template>
  <div class="page-shell page-grid">
    <div class="page-card filter-card">
      <div>
        <h2 class="section-title">我的申请</h2>
        <p class="section-subtitle">按状态与流程类型快速筛选，点击表格行查看详情。</p>
      </div>

      <div class="filter-row">
        <el-select v-model="filters.status" clearable placeholder="按状态筛选" style="width: 180px">
          <el-option label="待审批" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
          <el-option label="已退回" value="returned" />
        </el-select>

        <el-select v-model="filters.process_type" clearable placeholder="按流程筛选" style="width: 180px">
          <el-option label="请假申请" value="leave" />
          <el-option label="报销申请" value="reimbursement" />
          <el-option label="采购申请" value="purchase" />
        </el-select>

        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <div class="page-card table-card">
      <el-table :data="tableData" v-loading="loading" @row-click="handleRowClick">
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
        <el-table-column label="当前步骤" width="120">
          <template #default="{ row }">
            {{ row.current_step }} / {{ row.total_steps }}
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
