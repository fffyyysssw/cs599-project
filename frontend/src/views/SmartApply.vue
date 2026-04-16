<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { analyzeText } from '@/api/ai'
import { createApplication } from '@/api/application'
import { getProcessTypeDetail } from '@/api/process'
import DynamicForm from '@/components/DynamicForm.vue'
import FileUpload from '@/components/FileUpload.vue'
import { getMaterialLabel, getProcessLabel, getRoleLabel } from '@/utils'

const router = useRouter()

const examples = [
  '我想请3天事假，4月13号到15号，因为家里有事',
  '我上周出差花了6000块住宿费，需要报销，发票号码是INV20260410001',
  '部门需要采购20台键盘，单价150元，总共3000元，供应商是罗技，用于新入职员工配发',
]

const naturalText = ref(examples[0])
const title = ref('')
const analyzing = ref(false)
const submitting = ref(false)
const analysis = ref(null)
const processDetail = ref(null)
const formModel = ref({})
const uploadedFiles = ref([])
const formRef = ref()

const routeLabels = computed(() => (analysis.value?.approval_route || []).map((item) => getRoleLabel(item)))
const confidencePercent = computed(() => Math.round((analysis.value?.confidence || 0) * 100))

function useExample(text) {
  naturalText.value = text
}

async function handleAnalyze() {
  if (!naturalText.value.trim()) {
    ElMessage.warning('请先输入审批需求')
    return
  }

  analyzing.value = true
  try {
    const analyzeResponse = await analyzeText({ text: naturalText.value })
    analysis.value = analyzeResponse.data
    title.value = analyzeResponse.data.title
    formModel.value = { ...analyzeResponse.data.extracted_fields }
    uploadedFiles.value = []

    const processResponse = await getProcessTypeDetail(analyzeResponse.data.process_type)
    processDetail.value = processResponse.data

    ElMessage.success('AI 分析完成')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    analyzing.value = false
  }
}

async function handleSubmit() {
  if (!analysis.value || !processDetail.value) {
    ElMessage.warning('请先完成 AI 分析')
    return
  }

  try {
    submitting.value = true
    await formRef.value?.validate()

    await createApplication({
      process_type: analysis.value.process_type,
      title: title.value,
      form_data: formModel.value,
      ai_analysis: analysis.value,
      attachment_ids: uploadedFiles.value.map((item) => item.id),
    })

    ElMessage.success('申请提交成功')
    router.push('/my-applications')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="page-shell apply-page">
    <div class="page-card hero-panel">
      <div class="hero-copy">
        <p class="soft-chip">项目亮点页面</p>
        <h2 class="section-title">用自然语言发起审批</h2>
        <p class="section-subtitle">
          输入一句完整描述，系统会自动识别流程类型、抽取字段、推荐审批链路，并帮你生成可提交的动态表单。
        </p>
      </div>

      <div class="example-list">
        <span>示例输入：</span>
        <el-button
          v-for="item in examples"
          :key="item"
          text
          class="example-btn"
          @click="useExample(item)"
        >
          {{ item }}
        </el-button>
      </div>
    </div>

    <div class="page-card editor-card">
      <el-input
        v-model="naturalText"
        type="textarea"
        :rows="5"
        placeholder="例如：我想请3天事假，4月13号到15号，因为家里有事"
      />

      <div class="editor-actions">
        <el-button type="primary" size="large" :loading="analyzing" @click="handleAnalyze">
          AI 分析
        </el-button>
      </div>
    </div>

    <div v-if="analysis" class="analysis-grid">
      <div class="page-card analysis-card">
        <div class="analysis-head">
          <div>
            <h3>AI 分析结果</h3>
            <p>{{ getProcessLabel(analysis.process_type) }} · 自动预填表单已就绪</p>
          </div>
          <el-progress :percentage="confidencePercent" :stroke-width="10" color="#1b5955" />
        </div>

        <div class="analysis-pills">
          <span class="soft-chip">识别类型：{{ getProcessLabel(analysis.process_type) }}</span>
          <span class="soft-chip">建议链路：{{ routeLabels.join(' → ') }}</span>
        </div>

        <div class="analysis-block">
          <h4>缺失字段</h4>
          <div v-if="analysis.missing_fields.length" class="badge-group">
            <el-tag v-for="item in analysis.missing_fields" :key="item" type="danger" round>
              {{ item }}
            </el-tag>
          </div>
          <div v-else class="empty-tip">没有缺失字段</div>
        </div>

        <div class="analysis-block">
          <h4>所需材料</h4>
          <div v-if="analysis.required_materials.length" class="badge-group">
            <el-tag v-for="item in analysis.required_materials" :key="item" type="warning" round>
              {{ getMaterialLabel(item) }}
            </el-tag>
          </div>
          <div v-else class="empty-tip">当前无需额外材料</div>
        </div>

        <div class="analysis-block">
          <h4>风险提示</h4>
          <el-alert
            v-for="item in analysis.risk_tips"
            :key="item"
            :title="item"
            type="warning"
            :closable="false"
            class="alert-item"
          />
          <div v-if="!analysis.risk_tips.length" class="empty-tip">暂未发现明显风险</div>
        </div>

        <div class="analysis-block">
          <h4>AI 摘要</h4>
          <p class="summary-text">{{ analysis.summary }}</p>
        </div>
      </div>

      <div class="page-card form-card">
        <div class="form-head">
          <div>
            <h3>动态表单</h3>
            <p>根据识别到的流程自动渲染，已预填可识别字段。</p>
          </div>
          <el-button text @click="router.push('/rules')">查看规则</el-button>
        </div>

        <el-form label-position="top">
          <el-form-item label="申请标题">
            <el-input v-model="title" placeholder="请输入申请标题" />
          </el-form-item>
        </el-form>

        <DynamicForm
          ref="formRef"
          v-model="formModel"
          :schema="processDetail?.form_schema"
          :missing-fields="analysis.missing_fields"
        />

        <div class="upload-section">
          <h4>附件上传</h4>
          <FileUpload v-model="uploadedFiles" :required-materials="analysis.required_materials" />
        </div>

        <div class="submit-actions">
          <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
            提交申请
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.apply-page {
  display: grid;
  gap: 18px;
}

.hero-panel,
.editor-card,
.analysis-card,
.form-card {
  padding: 24px;
}

.hero-panel {
  display: grid;
  gap: 20px;
}

.example-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--muted);
}

.example-btn {
  padding: 0;
  white-space: normal;
  text-align: left;
  color: var(--brand);
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: 18px;
}

.analysis-head,
.form-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

.analysis-head h3,
.form-head h3,
.analysis-block h4,
.upload-section h4 {
  margin: 0 0 8px;
}

.analysis-head p,
.form-head p {
  margin: 0;
  color: var(--muted);
}

.analysis-block + .analysis-block {
  margin-top: 22px;
}

.badge-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.alert-item + .alert-item {
  margin-top: 10px;
}

.summary-text {
  margin: 0;
  line-height: 1.8;
  color: var(--muted);
}

.upload-section {
  margin-top: 14px;
}

.submit-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 22px;
}

@media (max-width: 1024px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}
</style>
