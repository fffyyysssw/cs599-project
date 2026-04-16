<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  schema: {
    type: Object,
    default: () => ({ fields: [] }),
  },
  modelValue: {
    type: Object,
    default: () => ({}),
  },
  missingFields: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

const formRef = ref()
const formState = reactive({})

const missingFieldSet = computed(() => new Set(props.missingFields))

const formRules = computed(() => {
  const rules = {}
  for (const field of props.schema?.fields || []) {
    if (!field.required) continue
    rules[field.key] = [
      {
        required: true,
        message: `请填写${field.label}`,
        trigger: field.type === 'select' || field.type === 'date' ? 'change' : 'blur',
      },
    ]
  }
  return rules
})

function syncForm(values = {}) {
  const next = {}
  for (const field of props.schema?.fields || []) {
    next[field.key] = values[field.key] ?? ''
  }
  Object.keys(formState).forEach((key) => {
    delete formState[key]
  })
  Object.entries(next).forEach(([key, value]) => {
    formState[key] = value
  })
}

watch(
  () => [props.schema, props.modelValue],
  () => syncForm(props.modelValue),
  { immediate: true, deep: true }
)

watch(
  formState,
  () => {
    emit('update:modelValue', { ...formState })
  },
  { deep: true }
)

watch(
  () => [formState.quantity, formState.unit_price],
  ([quantity, unitPrice]) => {
    if (quantity !== '' && unitPrice !== '' && quantity !== undefined && unitPrice !== undefined) {
      const total = Number(quantity) * Number(unitPrice)
      if (!Number.isNaN(total) && 'total_amount' in formState) {
        formState.total_amount = Number(total.toFixed(2))
      }
    }
  }
)

async function validate() {
  if (!formRef.value) return true
  return formRef.value.validate()
}

defineExpose({
  validate,
  getFormData: () => ({ ...formState }),
  resetForm: syncForm,
})
</script>

<template>
  <el-form ref="formRef" :model="formState" :rules="formRules" label-position="top" class="dynamic-form">
    <el-row :gutter="18">
      <el-col
        v-for="field in schema?.fields || []"
        :key="field.key"
        :xs="24"
        :sm="field.type === 'textarea' ? 24 : 12"
      >
        <el-form-item :prop="field.key">
          <template #label>
            <span :class="{ 'field-missing': missingFieldSet.has(field.key) }">
              {{ field.label }}
              <span v-if="field.required">*</span>
            </span>
          </template>

          <el-input
            v-if="field.type === 'text'"
            v-model="formState[field.key]"
            :placeholder="`请输入${field.label}`"
          />

          <el-input-number
            v-else-if="field.type === 'number'"
            v-model="formState[field.key]"
            :controls-position="'right'"
            :min="field.min || 0"
            :precision="field.key === 'unit_price' || field.key === 'amount' || field.key === 'total_amount' ? 2 : 0"
            :step="field.key === 'unit_price' || field.key === 'amount' || field.key === 'total_amount' ? 0.01 : 1"
            :placeholder="`请输入${field.label}`"
            :disabled="Boolean(field.computed)"
            style="width: 100%"
          />

          <el-select
            v-else-if="field.type === 'select'"
            v-model="formState[field.key]"
            :placeholder="`请选择${field.label}`"
            style="width: 100%"
          >
            <el-option
              v-for="option in field.options || []"
              :key="option"
              :label="option"
              :value="option"
            />
          </el-select>

          <el-date-picker
            v-else-if="field.type === 'date'"
            v-model="formState[field.key]"
            value-format="YYYY-MM-DD"
            type="date"
            :placeholder="`请选择${field.label}`"
            style="width: 100%"
          />

          <el-input
            v-else-if="field.type === 'textarea'"
            v-model="formState[field.key]"
            :rows="4"
            type="textarea"
            :placeholder="`请输入${field.label}`"
          />

          <div v-if="missingFieldSet.has(field.key)" class="hint-text">
            AI 检测到该字段仍需补充
          </div>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
</template>

<style scoped>
.dynamic-form {
  padding-top: 8px;
}

.hint-text {
  margin-top: 6px;
  font-size: 12px;
  color: #cf3d35;
}
</style>
