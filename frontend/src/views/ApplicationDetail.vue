<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'

import { getApplicationDetail } from '@/api/application'
import { approveStep, rejectStep, returnStep } from '@/api/approval'
import { getProcessTypeDetail } from '@/api/process'
import ApprovalTimeline from '@/components/ApprovalTimeline.vue'
import StatusTag from '@/components/StatusTag.vue'
import { useUserStore } from '@/stores/user'
import {
  getActionLabel,
  buildDownloadUrl,
  formatDateTime,
  getMaterialLabel,
  getProcessLabel,
  getRoleLabel,
} from '@/utils'

const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const actionLoading = ref(false)
const detail = ref(null)
const processDetail = ref(null)
const comment = ref('')

const currentPendingStep = computed(() =>
  detail.value?.approval_steps?.find((item) => item.status === 'pending') || null
)

const canOperate = computed(() => {
  const step = currentPendingStep.value
  const user = userStore.userInfo
  if (!step || !user) return false
  return user.role === 'admin' || step.approver?.id === user.id || (!step.approver && step.approver_role === user.role)
})

const detailFields = computed(() => {
  const schemaFields = processDetail.value?.form_schema?.fields || []
  return schemaFields.map((field) => ({
    label: field.label,
    value: detail.value?.form_data?.[field.key] ?? '--',
  }))
})

async function fetchDetail() {
  loading.value = true
  try {
    const response = await getApplicationDetail(route.params.id)
    detail.value = response.data
    const processResponse = await getProcessTypeDetail(response.data.process_type)
    processDetail.value = processResponse.data
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

async function handleAction(type) {
  if (!currentPendingStep.value) return
  if (!comment.value.trim()) {
    ElMessage.warning('请先填写审批意见')
    return
  }

  actionLoading.value = true
  try {
    const payload = { comment: comment.value }
    if (type === 'approve') {
      await approveStep(currentPendingStep.value.id, payload)
    } else if (type === 'reject') {
      await rejectStep(currentPendingStep.value.id, payload)
    } else {
      await returnStep(currentPendingStep.value.id, payload)
    }
    ElMessage.success('审批操作已提交')
    comment.value = ''
    await fetchDetail()
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    actionLoading.value = false
  }
}

onMounted(fetchDetail)
</script>

<template>
  <div class="page-shell detail-page" v-loading="loading">
    <div v-if="detail" class="detail-grid">
      <div class="page-card basic-card">
        <div class="basic-head">
          <div>
            <h2 class="section-title">{{ detail.title }}</h2>
            <p class="section-subtitle">申请编号：{{ detail.application_no }}</p>
          </div>
          <StatusTag :status="detail.status" />
        </div>

        <div class="meta-grid">
          <div class="meta-item">
            <span>流程类型</span>
            <strong>{{ getProcessLabel(detail.process_type) }}</strong>
          </div>
          <div class="meta-item">
            <span>申请人</span>
            <strong>{{ detail.applicant.real_name }}</strong>
          </div>
          <div class="meta-item">
            <span>所属部门</span>
            <strong>{{ detail.applicant.department }}</strong>
          </div>
          <div class="meta-item">
            <span>创建时间</span>
            <strong>{{ formatDateTime(detail.created_at) }}</strong>
          </div>
        </div>
      </div>

      <div class="page-card form-card">
        <h3>表单数据</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item v-for="item in detailFields" :key="item.label" :label="item.label">
            {{ item.value }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="page-card info-card">
        <h3>附件列表</h3>
        <div v-if="detail.attachments.length" class="attachment-list">
          <a
            v-for="item in detail.attachments"
            :key="item.id"
            :href="buildDownloadUrl(item.file_path)"
            target="_blank"
            class="attachment-item"
          >
            <strong>{{ item.file_name }}</strong>
            <span>{{ getMaterialLabel(item.material_type) }}</span>
          </a>
        </div>
        <div v-else class="empty-tip">暂无附件</div>
      </div>

      <div class="page-card info-card">
        <h3>AI 分析结果</h3>
        <div class="ai-meta">
          <span class="soft-chip">置信度：{{ Math.round((detail.ai_analysis?.confidence || 0) * 100) }}%</span>
          <span class="soft-chip">
            链路：{{ (detail.ai_analysis?.approval_route || []).map(getRoleLabel).join(' → ') || '--' }}
          </span>
        </div>
        <p class="summary-text">{{ detail.ai_analysis?.summary || '暂无 AI 摘要' }}</p>
      </div>

      <div class="page-card timeline-card">
        <h3>审批时间线</h3>
        <ApprovalTimeline :steps="detail.approval_steps" />
      </div>

      <div class="page-card timeline-card">
        <h3>操作日志</h3>
        <el-timeline v-if="detail.audit_logs.length">
          <el-timeline-item
            v-for="item in detail.audit_logs"
            :key="`${item.action}-${item.created_at}`"
            :timestamp="formatDateTime(item.created_at)"
          >
            {{ item.operator.real_name }} · {{ getActionLabel(item.action) }} · {{ item.detail }}
          </el-timeline-item>
        </el-timeline>
        <div v-else class="empty-tip">暂无操作日志</div>
      </div>

      <div v-if="canOperate" class="page-card action-card">
        <h3>审批操作</h3>
        <p class="section-subtitle">
          当前待处理节点：{{ getRoleLabel(currentPendingStep?.approver_role) }}
        </p>
        <el-input
          v-model="comment"
          type="textarea"
          :rows="4"
          placeholder="请输入审批意见"
        />
        <div class="action-row">
          <el-button type="success" :loading="actionLoading" @click="handleAction('approve')">通过</el-button>
          <el-button type="danger" plain :loading="actionLoading" @click="handleAction('reject')">驳回</el-button>
          <el-button type="warning" plain :loading="actionLoading" @click="handleAction('return')">退回</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-page {
  display: grid;
}

.detail-grid {
  display: grid;
  gap: 18px;
}

.basic-card,
.form-card,
.info-card,
.timeline-card,
.action-card {
  padding: 24px;
}

.basic-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.meta-item {
  padding: 16px;
  border: 1px solid rgba(229, 216, 197, 0.9);
  border-radius: 18px;
  background: rgba(255, 251, 244, 0.75);
}

.meta-item span,
.meta-item strong {
  display: block;
}

.meta-item span {
  margin-bottom: 8px;
  color: var(--muted);
}

.attachment-list {
  display: grid;
  gap: 12px;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid rgba(229, 216, 197, 0.9);
  border-radius: 18px;
  background: rgba(255, 251, 244, 0.75);
}

.attachment-item span {
  color: var(--muted);
}

.ai-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.summary-text {
  margin: 0;
  line-height: 1.8;
  color: var(--muted);
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

@media (max-width: 1024px) {
  .meta-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
