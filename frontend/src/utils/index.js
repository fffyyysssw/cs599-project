export const statusLabelMap = {
  draft: '草稿',
  pending: '待审批',
  approved: '已通过',
  rejected: '已驳回',
  returned: '已退回',
  waiting: '待流转',
}

export const statusTypeMap = {
  draft: 'info',
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  returned: 'info',
  waiting: '',
}

export const processLabelMap = {
  leave: '请假申请',
  reimbursement: '报销申请',
  purchase: '采购申请',
}

export const roleLabelMap = {
  employee: '员工',
  manager: '主管',
  finance: '财务',
  hr: 'HR',
  procurement: '采购',
  admin: '管理员',
  department_head: '部门负责人',
}

export const materialLabelMap = {
  invoice: '发票',
  sick_leave_certificate: '病假证明',
  quotation: '报价单',
  other: '其他材料',
}

export const actionLabelMap = {
  submit: '提交申请',
  approve: '审批通过',
  reject: '审批驳回',
  return: '审批退回',
  upload: '上传附件',
}

export function formatDateTime(value) {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  const hours = `${date.getHours()}`.padStart(2, '0')
  const minutes = `${date.getMinutes()}`.padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

export function getStatusLabel(status) {
  return statusLabelMap[status] || status || '--'
}

export function getStatusType(status) {
  return statusTypeMap[status] || 'info'
}

export function getProcessLabel(code) {
  return processLabelMap[code] || code || '--'
}

export function getRoleLabel(role) {
  return roleLabelMap[role] || role || '--'
}

export function getMaterialLabel(code) {
  return materialLabelMap[code] || code || '--'
}

export function buildDownloadUrl(path) {
  if (!path) return '#'
  if (path.startsWith('http')) return path
  return `/${path.replace(/^\/+/, '')}`
}

export function getActionLabel(action) {
  return actionLabelMap[action] || action || '--'
}
