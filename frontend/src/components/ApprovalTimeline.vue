<script setup>
import StatusTag from './StatusTag.vue'
import { formatDateTime, getRoleLabel } from '@/utils'

defineProps({
  steps: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <el-timeline v-if="steps.length">
    <el-timeline-item
      v-for="step in steps"
      :key="step.id"
      :timestamp="formatDateTime(step.operated_at || step.created_at)"
      placement="top"
      hollow
    >
      <div class="timeline-card">
        <div class="timeline-head">
          <strong>第 {{ step.step_order }} 步 · {{ getRoleLabel(step.approver_role) }}</strong>
          <StatusTag :status="step.status" />
        </div>
        <p class="timeline-line">
          审批人：{{ step.approver?.real_name || getRoleLabel(step.approver_role) }}
        </p>
        <p class="timeline-line">
          审批意见：{{ step.comment || '暂无' }}
        </p>
      </div>
    </el-timeline-item>
  </el-timeline>
  <div v-else class="empty-tip">暂无审批记录</div>
</template>

<style scoped>
.timeline-card {
  padding: 14px 16px;
  background: rgba(255, 251, 244, 0.86);
  border: 1px solid rgba(229, 216, 197, 0.9);
  border-radius: 18px;
}

.timeline-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.timeline-line {
  margin: 6px 0 0;
  color: var(--muted);
}
</style>
