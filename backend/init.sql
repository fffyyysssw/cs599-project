CREATE DATABASE IF NOT EXISTS smartflow DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smartflow;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  real_name VARCHAR(50) NOT NULL,
  role VARCHAR(20) NOT NULL,
  department VARCHAR(50) NOT NULL,
  email VARCHAR(100) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS process_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(30) NOT NULL UNIQUE,
  name VARCHAR(50) NOT NULL,
  description TEXT NULL,
  form_schema JSON NOT NULL,
  rules JSON NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS applications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_no VARCHAR(30) NOT NULL UNIQUE,
  title VARCHAR(200) NOT NULL,
  process_type VARCHAR(30) NOT NULL,
  applicant_id INT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  form_data JSON NOT NULL,
  ai_analysis JSON NULL,
  current_step INT NOT NULL DEFAULT 1,
  total_steps INT NOT NULL,
  remark TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_applications_applicant_id (applicant_id),
  INDEX idx_applications_status (status),
  INDEX idx_applications_process_type (process_type),
  CONSTRAINT fk_applications_process_type FOREIGN KEY (process_type) REFERENCES process_types(code),
  CONSTRAINT fk_applications_applicant FOREIGN KEY (applicant_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS approval_steps (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_id INT NOT NULL,
  step_order INT NOT NULL,
  approver_role VARCHAR(20) NOT NULL,
  approver_id INT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'waiting',
  comment TEXT NULL,
  operated_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_application_step (application_id, step_order),
  INDEX idx_approval_steps_approver_id (approver_id),
  INDEX idx_approval_steps_status (status),
  CONSTRAINT fk_approval_steps_application FOREIGN KEY (application_id) REFERENCES applications(id),
  CONSTRAINT fk_approval_steps_approver FOREIGN KEY (approver_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS attachments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_id INT NULL,
  file_name VARCHAR(200) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  file_size INT NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  material_type VARCHAR(50) NULL,
  uploaded_by INT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_attachments_application_id (application_id),
  CONSTRAINT fk_attachments_application FOREIGN KEY (application_id) REFERENCES applications(id),
  CONSTRAINT fk_attachments_uploaded_by FOREIGN KEY (uploaded_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_id INT NOT NULL,
  step_id INT NULL,
  operator_id INT NOT NULL,
  action VARCHAR(30) NOT NULL,
  detail TEXT NULL,
  ip_address VARCHAR(45) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_audit_logs_application_id (application_id),
  INDEX idx_audit_logs_operator_id (operator_id),
  INDEX idx_audit_logs_created_at (created_at),
  CONSTRAINT fk_audit_logs_application FOREIGN KEY (application_id) REFERENCES applications(id),
  CONSTRAINT fk_audit_logs_step FOREIGN KEY (step_id) REFERENCES approval_steps(id),
  CONSTRAINT fk_audit_logs_operator FOREIGN KEY (operator_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (id, username, password_hash, real_name, role, department, email, is_active, created_at, updated_at) VALUES
  (1, 'zhangsan', 'sha256$8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '张三', 'employee', '技术部', NULL, 1, '2026-03-25 09:00:00', '2026-03-25 09:00:00'),
  (2, 'lisi', 'sha256$8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '李四', 'manager', '技术部', NULL, 1, '2026-03-25 09:00:00', '2026-03-25 09:00:00'),
  (3, 'wangwu', 'sha256$8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '王五', 'finance', '财务部', NULL, 1, '2026-03-25 09:00:00', '2026-03-25 09:00:00'),
  (4, 'zhaoliu', 'sha256$8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '赵六', 'hr', '人力资源部', NULL, 1, '2026-03-25 09:00:00', '2026-03-25 09:00:00'),
  (5, 'sunqi', 'sha256$8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '孙七', 'procurement', '采购部', NULL, 1, '2026-03-25 09:00:00', '2026-03-25 09:00:00'),
  (6, 'admin', 'sha256$8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '管理员', 'admin', '管理层', NULL, 1, '2026-03-25 09:00:00', '2026-03-25 09:00:00')
ON DUPLICATE KEY UPDATE
  password_hash = VALUES(password_hash),
  real_name = VALUES(real_name),
  role = VALUES(role),
  department = VALUES(department),
  is_active = VALUES(is_active),
  updated_at = VALUES(updated_at);

INSERT INTO process_types (id, code, name, description, form_schema, rules, is_active) VALUES
  (
    1,
    'leave',
    '请假申请',
    '支持事假、病假、年假、婚假、产假、丧假等请假流程。',
    '{"fields":[{"key":"leave_type","label":"请假类型","type":"select","required":true,"options":["事假","病假","年假","婚假","产假","丧假"]},{"key":"start_date","label":"开始日期","type":"date","required":true},{"key":"end_date","label":"结束日期","type":"date","required":true},{"key":"days","label":"天数","type":"number","required":true,"min":0.5},{"key":"reason","label":"请假原因","type":"textarea","required":true},{"key":"handover_person","label":"工作交接人","type":"text","required":false}]}',
    '{"approval_rules":[{"max_days":1,"route":["manager"]},{"min_days":1,"max_days":3,"route":["manager","hr"]},{"min_days":3,"route":["manager","department_head","hr"]}],"required_material_rules":[{"leave_type":"病假","min_days":2,"material":"sick_leave_certificate"}],"supported_types":["事假","病假","年假","婚假","产假","丧假"]}',
    1
  ),
  (
    2,
    'reimbursement',
    '报销申请',
    '支持差旅、餐饮、交通、办公用品、通讯等报销场景。',
    '{"fields":[{"key":"reimbursement_type","label":"报销类型","type":"select","required":true,"options":["差旅","餐饮","交通","办公用品","通讯","其他"]},{"key":"amount","label":"报销金额(元)","type":"number","required":true,"min":0.01},{"key":"expense_date","label":"消费日期","type":"date","required":true},{"key":"reason","label":"报销事由","type":"textarea","required":true},{"key":"invoice_no","label":"发票号码","type":"text","required":false}]}',
    '{"approval_rules":[{"max_amount":1000,"route":["manager"]},{"min_amount":1000,"max_amount":5000,"route":["manager","finance"]},{"min_amount":5000,"route":["manager","department_head","finance"]}],"required_materials":["invoice"],"supported_types":["差旅","餐饮","交通","办公用品","通讯","其他"]}',
    1
  ),
  (
    3,
    'purchase',
    '采购申请',
    '支持办公采购、设备采购、耗材采购等采购流程。',
    '{"fields":[{"key":"item_name","label":"采购物品","type":"text","required":true},{"key":"quantity","label":"数量","type":"number","required":true,"min":1},{"key":"unit_price","label":"单价(元)","type":"number","required":true,"min":0.01},{"key":"total_amount","label":"总金额(元)","type":"number","required":true,"computed":"quantity * unit_price"},{"key":"purpose","label":"采购用途","type":"textarea","required":true},{"key":"supplier","label":"供应商","type":"text","required":false}]}',
    '{"approval_rules":[{"max_amount":2000,"route":["manager"]},{"min_amount":2000,"max_amount":5000,"route":["manager","procurement"]},{"min_amount":5000,"route":["manager","department_head","procurement","finance"]}],"required_material_rules":[{"min_amount":3000,"material":"quotation"}]}',
    1
  )
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  description = VALUES(description),
  form_schema = VALUES(form_schema),
  rules = VALUES(rules),
  is_active = VALUES(is_active);

INSERT INTO applications (id, application_no, title, process_type, applicant_id, status, form_data, ai_analysis, current_step, total_steps, remark, created_at, updated_at) VALUES
  (
    1,
    'LV20260325001',
    '事假申请-3天',
    'leave',
    1,
    'pending',
    '{"leave_type":"事假","start_date":"2026-04-13","end_date":"2026-04-15","days":3,"reason":"家里有事","handover_person":"王小明"}',
    '{"process_type":"leave","confidence":0.95,"title":"事假申请-3天","extracted_fields":{"leave_type":"事假","start_date":"2026-04-13","end_date":"2026-04-15","days":3,"reason":"家里有事"},"missing_fields":["handover_person"],"required_materials":[],"approval_route":["manager","hr"],"risk_tips":[],"summary":"申请人提交3天事假申请，仍需补充工作交接人信息。"}',
    1,
    2,
    '课程演示数据',
    '2026-03-25 09:00:00',
    '2026-03-25 09:00:00'
  ),
  (
    2,
    'RB20260325001',
    '差旅报销-800元',
    'reimbursement',
    1,
    'approved',
    '{"reimbursement_type":"差旅","amount":800,"expense_date":"2026-03-20","reason":"客户拜访交通费用","invoice_no":"INV20260320001"}',
    '{"process_type":"reimbursement","confidence":0.93,"title":"差旅报销-800元","extracted_fields":{"reimbursement_type":"差旅","amount":800,"expense_date":"2026-03-20","reason":"客户拜访交通费用","invoice_no":"INV20260320001"},"missing_fields":[],"required_materials":["invoice"],"approval_route":["manager"],"risk_tips":["报销必须上传发票"],"summary":"申请人提交差旅报销800元，主管已审批通过。"}',
    1,
    1,
    '课程演示数据',
    '2026-03-25 09:00:00',
    '2026-03-25 09:00:00'
  ),
  (
    3,
    'PC20260325001',
    '采购申请-键盘20件',
    'purchase',
    1,
    'rejected',
    '{"item_name":"键盘","quantity":20,"unit_price":225,"total_amount":4500,"purpose":"项目组设备更新","supplier":"罗技"}',
    '{"process_type":"purchase","confidence":0.97,"title":"采购申请-键盘20台","extracted_fields":{"item_name":"键盘","quantity":20,"unit_price":225,"total_amount":4500,"purpose":"项目组设备更新","supplier":"罗技"},"missing_fields":[],"required_materials":["quotation"],"approval_route":["manager","procurement"],"risk_tips":["采购金额超过3000元，需要上传报价单"],"summary":"采购申请金额4500元，采购已驳回。"}',
    2,
    2,
    '课程演示数据',
    '2026-03-25 09:00:00',
    '2026-03-25 09:00:00'
  ),
  (
    4,
    'RB20260325002',
    '差旅报销-6000元',
    'reimbursement',
    2,
    'pending',
    '{"reimbursement_type":"差旅","amount":6000,"expense_date":"2026-03-18","reason":"出差住宿费","invoice_no":"INV20260318001"}',
    '{"process_type":"reimbursement","confidence":0.92,"title":"差旅报销-6000元","extracted_fields":{"reimbursement_type":"差旅","amount":6000,"expense_date":"2026-03-18","reason":"出差住宿费","invoice_no":"INV20260318001"},"missing_fields":[],"required_materials":["invoice"],"approval_route":["manager","department_head","finance"],"risk_tips":["报销金额超过5000元，需要部门负责人额外审批"],"summary":"申请人提交差旅报销6000元，当前待财务审批。"}',
    3,
    3,
    '课程演示数据',
    '2026-03-25 09:00:00',
    '2026-03-25 09:00:00'
  ),
  (
    5,
    'LV20260325002',
    '病假申请-4天',
    'leave',
    5,
    'returned',
    '{"leave_type":"病假","start_date":"2026-03-26","end_date":"2026-03-29","days":4,"reason":"身体不适","handover_person":"周同学"}',
    '{"process_type":"leave","confidence":0.94,"title":"病假申请-4天","extracted_fields":{"leave_type":"病假","start_date":"2026-03-26","end_date":"2026-03-29","days":4,"reason":"身体不适","handover_person":"周同学"},"missing_fields":[],"required_materials":["sick_leave_certificate"],"approval_route":["manager","department_head","hr"],"risk_tips":["病假超过2天，请上传病假证明"],"summary":"病假申请已被退回，申请人需补充材料后重新提交。"}',
    1,
    3,
    '课程演示数据',
    '2026-03-25 09:00:00',
    '2026-03-25 09:00:00'
  )
ON DUPLICATE KEY UPDATE
  title = VALUES(title),
  status = VALUES(status),
  form_data = VALUES(form_data),
  ai_analysis = VALUES(ai_analysis),
  current_step = VALUES(current_step),
  total_steps = VALUES(total_steps),
  remark = VALUES(remark),
  updated_at = VALUES(updated_at);

INSERT INTO approval_steps (id, application_id, step_order, approver_role, approver_id, status, comment, operated_at, created_at) VALUES
  (1, 1, 1, 'manager', 2, 'pending', NULL, NULL, '2026-03-25 09:00:00'),
  (2, 1, 2, 'hr', 4, 'waiting', NULL, NULL, '2026-03-25 09:00:00'),
  (3, 2, 1, 'manager', 2, 'approved', '同意报销', '2026-03-25 10:00:00', '2026-03-25 09:00:00'),
  (4, 3, 1, 'manager', 2, 'approved', '同意进入采购审批', '2026-03-25 10:30:00', '2026-03-25 09:00:00'),
  (5, 3, 2, 'procurement', 5, 'rejected', '供应商报价偏高，请重新询价', '2026-03-25 11:00:00', '2026-03-25 09:00:00'),
  (6, 4, 1, 'manager', 6, 'approved', '已审阅', '2026-03-25 09:30:00', '2026-03-25 09:00:00'),
  (7, 4, 2, 'department_head', 6, 'approved', '同意报销', '2026-03-25 09:45:00', '2026-03-25 09:00:00'),
  (8, 4, 3, 'finance', 3, 'pending', NULL, NULL, '2026-03-25 09:00:00'),
  (9, 5, 1, 'manager', 6, 'returned', '请补充更完整的病假证明', '2026-03-25 11:30:00', '2026-03-25 09:00:00'),
  (10, 5, 2, 'department_head', 6, 'waiting', NULL, NULL, '2026-03-25 09:00:00'),
  (11, 5, 3, 'hr', 4, 'waiting', NULL, NULL, '2026-03-25 09:00:00')
ON DUPLICATE KEY UPDATE
  approver_role = VALUES(approver_role),
  approver_id = VALUES(approver_id),
  status = VALUES(status),
  comment = VALUES(comment),
  operated_at = VALUES(operated_at);

INSERT INTO attachments (id, application_id, file_name, file_path, file_size, file_type, material_type, uploaded_by, created_at) VALUES
  (1, 2, '发票_差旅.pdf', 'uploads/2026-03-25/invoice_demo.pdf', 102400, 'application/pdf', 'invoice', 1, '2026-03-25 09:00:00'),
  (2, 3, '报价单_键盘.pdf', 'uploads/2026-03-25/quotation_demo.pdf', 204800, 'application/pdf', 'quotation', 1, '2026-03-25 09:00:00'),
  (3, 4, '发票_住宿.pdf', 'uploads/2026-03-25/invoice_hotel_demo.pdf', 307200, 'application/pdf', 'invoice', 2, '2026-03-25 09:00:00'),
  (4, 5, '病假证明.pdf', 'uploads/2026-03-25/sick_leave_demo.pdf', 256000, 'application/pdf', 'sick_leave_certificate', 5, '2026-03-25 09:00:00');

INSERT INTO audit_logs (id, application_id, step_id, operator_id, action, detail, ip_address, created_at) VALUES
  (1, 1, NULL, 1, 'submit', '提交申请', NULL, '2026-03-25 09:00:00'),
  (2, 2, NULL, 1, 'submit', '提交申请', NULL, '2026-03-25 09:00:00'),
  (3, 2, 3, 2, 'approve', '同意报销', NULL, '2026-03-25 10:00:00'),
  (4, 3, NULL, 1, 'submit', '提交申请', NULL, '2026-03-25 09:00:00'),
  (5, 3, 4, 2, 'approve', '同意进入采购审批', NULL, '2026-03-25 10:30:00'),
  (6, 3, 5, 5, 'reject', '供应商报价偏高，请重新询价', NULL, '2026-03-25 11:00:00'),
  (7, 4, NULL, 2, 'submit', '提交申请', NULL, '2026-03-25 09:00:00'),
  (8, 4, 6, 6, 'approve', '已审阅', NULL, '2026-03-25 09:30:00'),
  (9, 4, 7, 6, 'approve', '同意报销', NULL, '2026-03-25 09:45:00'),
  (10, 5, NULL, 5, 'submit', '提交申请', NULL, '2026-03-25 09:00:00'),
  (11, 5, 9, 6, 'return', '请补充更完整的病假证明', NULL, '2026-03-25 11:30:00');
