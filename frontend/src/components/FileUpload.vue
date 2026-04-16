<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { uploadFile } from '@/api/upload'
import { getMaterialLabel } from '@/utils'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  requiredMaterials: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

const uploadList = ref([])
const selectedMaterial = ref('other')
const uploading = ref(false)

const materialOptions = computed(() => {
  const defaults = ['invoice', 'sick_leave_certificate', 'quotation', 'other']
  const values = Array.from(new Set([...props.requiredMaterials, ...defaults]))
  return values.map((value) => ({
    label: getMaterialLabel(value),
    value,
  }))
})

watch(
  () => props.modelValue,
  (value) => {
    uploadList.value = Array.isArray(value) ? [...value] : []
  },
  { immediate: true, deep: true }
)

watch(
  () => props.requiredMaterials,
  (value) => {
    if (value?.length) {
      selectedMaterial.value = value[0]
    }
  },
  { immediate: true }
)

function emitChange() {
  emit('update:modelValue', [...uploadList.value])
}

function removeItem(id) {
  uploadList.value = uploadList.value.filter((item) => item.id !== id)
  emitChange()
}

function beforeUpload(file) {
  const isAllowed = /\.(jpg|jpeg|png|pdf|doc|docx|xls|xlsx)$/i.test(file.name)
  if (!isAllowed) {
    ElMessage.error('仅支持 jpg、png、pdf、doc、docx、xls、xlsx 文件')
    return false
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('上传文件不能超过 10MB')
    return false
  }
  return true
}

async function customUpload(option) {
  const formData = new FormData()
  formData.append('file', option.file)
  formData.append('material_type', selectedMaterial.value)
  uploading.value = true
  try {
    const response = await uploadFile(formData)
    uploadList.value.push(response.data)
    emitChange()
    ElMessage.success('附件上传成功')
    option.onSuccess(response.data)
  } catch (error) {
    ElMessage.error(error.message)
    option.onError(error)
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="upload-box">
    <div class="upload-toolbar">
      <el-select v-model="selectedMaterial" style="width: 180px">
        <el-option
          v-for="option in materialOptions"
          :key="option.value"
          :label="option.label"
          :value="option.value"
        />
      </el-select>

      <el-upload
        action="#"
        :show-file-list="false"
        :before-upload="beforeUpload"
        :http-request="customUpload"
        :disabled="uploading"
      >
        <el-button type="primary" :loading="uploading">上传附件</el-button>
      </el-upload>
    </div>

    <div v-if="requiredMaterials.length" class="required-line">
      <span class="soft-chip">
        必传材料：{{ requiredMaterials.map(getMaterialLabel).join('、') }}
      </span>
    </div>

    <el-table v-if="uploadList.length" :data="uploadList" border>
      <el-table-column prop="file_name" label="文件名" min-width="220" />
      <el-table-column label="材料类型" min-width="120">
        <template #default="{ row }">
          {{ getMaterialLabel(row.material_type) }}
        </template>
      </el-table-column>
      <el-table-column label="大小" width="120">
        <template #default="{ row }">
          {{ (row.file_size / 1024).toFixed(1) }} KB
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button link type="danger" @click="removeItem(row.id)">移除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div v-else class="empty-tip">暂未上传附件</div>
  </div>
</template>

<style scoped>
.upload-box {
  display: grid;
  gap: 14px;
}

.upload-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.required-line {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
