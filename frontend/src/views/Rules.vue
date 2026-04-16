<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { getProcessTypes } from '@/api/process'
import { getMaterialLabel, getProcessLabel, getRoleLabel } from '@/utils'

const loading = ref(false)
const processTypes = ref([])

const extraNotes = {
  leave: [
    '病假超过 2 天需上传病假证明。',
    '请假天数按开始日期和结束日期含首尾计算。',
    '支持事假、病假、年假、婚假、产假、丧假。',
  ],
  reimbursement: [
    '报销必须上传发票。',
    '金额保留两位小数。',
    '发票金额应与报销金额一致或大于报销金额。',
  ],
  purchase: [
    '采购金额超过 3000 元必须上传报价单。',
    '总金额 = 数量 × 单价。',
    '数量和单价均不可为负数。',
  ],
}

const cards = computed(() =>
  processTypes.value.map((item) => {
    const rules = item.rules || {}
    const approvalRules = (rules.approval_rules || []).map((rule) => {
      if (item.code === 'leave') {
        if (rule.max_days === 1) {
          return { condition: '请假 ≤ 1 天', route: rule.route.map(getRoleLabel).join(' → ') }
        }
        if (rule.max_days === 3) {
          return { condition: '1 天 < 请假 ≤ 3 天', route: rule.route.map(getRoleLabel).join(' → ') }
        }
        return { condition: '请假 > 3 天', route: rule.route.map(getRoleLabel).join(' → ') }
      }
      if (item.code === 'reimbursement') {
        if (rule.max_amount === 1000) {
          return { condition: '金额 ≤ 1000 元', route: rule.route.map(getRoleLabel).join(' → ') }
        }
        if (rule.max_amount === 5000) {
          return { condition: '1000 元 < 金额 ≤ 5000 元', route: rule.route.map(getRoleLabel).join(' → ') }
        }
        return { condition: '金额 > 5000 元', route: rule.route.map(getRoleLabel).join(' → ') }
      }
      if (rule.max_amount === 2000) {
        return { condition: '金额 ≤ 2000 元', route: rule.route.map(getRoleLabel).join(' → ') }
      }
      if (rule.max_amount === 5000) {
        return { condition: '2000 元 < 金额 ≤ 5000 元', route: rule.route.map(getRoleLabel).join(' → ') }
      }
      return { condition: '金额 > 5000 元', route: rule.route.map(getRoleLabel).join(' → ') }
    })

    const materialRules = [
      ...(rules.required_materials || []),
      ...((rules.required_material_rules || []).map((rule) => rule.material)),
    ]

    return {
      ...item,
      approvalRules,
      materialRules: Array.from(new Set(materialRules)),
      extraNotes: extraNotes[item.code] || [],
    }
  })
)

async function fetchRules() {
  loading.value = true
  try {
    const response = await getProcessTypes()
    processTypes.value = response.data
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

onMounted(fetchRules)
</script>

<template>
  <div class="page-shell rules-page" v-loading="loading">
    <div class="page-card heading-card">
      <h2 class="section-title">审批规则查看</h2>
      <p class="section-subtitle">
        所有请假、报销、采购规则均按需求文档实现，下面展示审批链路与材料要求。
      </p>
    </div>

    <div class="rules-grid">
      <div v-for="card in cards" :key="card.code" class="page-card rule-card">
        <div class="rule-head">
          <div>
            <h3>{{ getProcessLabel(card.code) }}</h3>
            <p>{{ card.description }}</p>
          </div>
          <span class="soft-chip">{{ card.form_schema?.fields?.length || 0 }} 个字段</span>
        </div>

        <el-table :data="card.approvalRules" border>
          <el-table-column prop="condition" label="条件" min-width="160" />
          <el-table-column prop="route" label="审批链路" min-width="220" />
        </el-table>

        <div class="rule-section">
          <h4>材料要求</h4>
          <div v-if="card.materialRules.length" class="badge-group">
            <el-tag v-for="item in card.materialRules" :key="item" type="warning" round>
              {{ getMaterialLabel(item) }}
            </el-tag>
          </div>
          <div v-else class="empty-tip">当前流程没有固定必传材料</div>
        </div>

        <div class="rule-section">
          <h4>附加规则</h4>
          <ul class="notes-list">
            <li v-for="note in card.extraNotes" :key="note">{{ note }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rules-page {
  display: grid;
  gap: 18px;
}

.heading-card,
.rule-card {
  padding: 24px;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.rule-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.rule-head h3 {
  margin: 0 0 6px;
}

.rule-head p {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}

.rule-section {
  margin-top: 18px;
}

.rule-section h4 {
  margin: 0 0 10px;
}

.badge-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.notes-list {
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
  line-height: 1.8;
}

@media (max-width: 1200px) {
  .rules-grid {
    grid-template-columns: 1fr;
  }
}
</style>
