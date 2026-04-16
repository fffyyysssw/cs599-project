<script setup>
import { computed } from 'vue'

import { getStatusLabel, getStatusType } from '@/utils'

const props = defineProps({
  status: {
    type: String,
    default: '',
  },
})

const label = computed(() => getStatusLabel(props.status))
const type = computed(() => getStatusType(props.status))
</script>

<template>
  <el-tag :type="type" effect="light" round>
    {{ label }}
  </el-tag>
</template>
