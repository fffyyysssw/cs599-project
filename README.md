# SmartFlow：AI 驱动的审批/办公流程助手

SmartFlow 是一个面向企业审批场景的全栈演示项目，覆盖请假、报销、采购三类流程。系统支持用户以自然语言描述需求，由 AI 自动识别流程类型、抽取字段、检查材料、推荐审批链路，并驱动后续审批流转与详情展示。

## 技术栈

- 前端：Vue 3 + Vite + Element Plus + Pinia + Vue Router + Axios
- 后端：FastAPI + SQLAlchemy 2.0 + Pydantic V2 + Uvicorn
- AI：LangGraph + OpenAI 兼容接口 / 本地 Mock 规则模式
- 数据库：SQLite（默认）/ MySQL 8.0+
- 认证：JWT HS256

## 项目目录结构

```text
smartflow/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   ├── uploads/
│   ├── .env.example
│   ├── init.sql
│   ├── init_db.py
│   ├── requirements.txt
│   └── seed_data.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── utils/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.js
│   ├── .env.development
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

## 快速启动

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python seed_data.py
uvicorn app.main:app --reload --port 8000
```

Windows PowerShell 可使用：

```powershell
cd backend
pip install -r requirements.txt
Copy-Item .env.example .env
python init_db.py
python seed_data.py
uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问地址

- 前端：http://localhost:5173
- 后端：http://localhost:8000
- 接口文档：http://localhost:8000/docs

## 演示账号

| 用户名 | 密码 | 角色 | 部门 | 姓名 |
|------|------|------|------|------|
| zhangsan | 123456 | employee | 技术部 | 张三 |
| lisi | 123456 | manager | 技术部 | 李四 |
| wangwu | 123456 | finance | 财务部 | 王五 |
| zhaoliu | 123456 | hr | 人力资源部 | 赵六 |
| sunqi | 123456 | procurement | 采购部 | 孙七 |
| admin | 123456 | admin | 管理层 | 管理员 |

## 演示流程

1. 使用 `zhangsan / 123456` 登录。
2. 进入“智能发起”，输入一段自然语言需求。
3. 点击“AI 分析”，查看识别类型、链路、材料与摘要。
4. 自动生成动态表单后补充缺失字段并上传附件。
5. 提交申请后，进入“我的申请”查看状态。
6. 切换为 `lisi / 123456`、`wangwu / 123456` 等账号进入“待审批”处理流程。
7. 在“申请详情”中查看审批时间线、附件与操作日志。

## API 列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户 |
| POST | `/api/ai/analyze` | AI 分析自然语言 |
| GET | `/api/process-types` | 获取流程类型列表 |
| GET | `/api/process-types/{code}` | 获取流程类型详情 |
| POST | `/api/applications` | 创建申请 |
| GET | `/api/applications/my` | 获取我的申请 |
| GET | `/api/applications/{id}` | 获取申请详情 |
| GET | `/api/approvals/pending` | 获取待审批列表 |
| POST | `/api/approvals/{id}/approve` | 审批通过 |
| POST | `/api/approvals/{id}/reject` | 审批驳回 |
| POST | `/api/approvals/{id}/return` | 审批退回 |
| POST | `/api/upload` | 上传附件 |
| GET | `/api/dashboard/stats` | 仪表盘统计 |

## 如何切换到真实 LLM

编辑 [backend/.env.example](/c:/Users/70669/Desktop/1/backend/.env.example) 对应生成的 `.env`：

```env
LLM_API_KEY=你的真实 Key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

- 当 `LLM_API_KEY` 为空时，系统自动启用 Mock 规则模式。
- 当 `LLM_API_KEY` 存在时，LangGraph 节点会优先调用真实 OpenAI 兼容接口。

## 如何切换 MySQL

编辑 `.env` 中的 `DATABASE_URL`：

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/smartflow?charset=utf8mb4
```

然后重新执行：

```bash
cd backend
python init_db.py
python seed_data.py
```

## 联调检查点

- 前端所有接口统一走 `src/api/` 模块，请求拦截器会自动注入 `Authorization: Bearer <token>`。
- 401 响应会自动清理本地 token 并回到登录页。
- “智能发起”页的动态表单字段与后端 `form_schema` 保持一致。
- 审批通过后，后端会自动将下一步 `waiting` 流转为 `pending`。
- 详情页兼容三类流程的不同表单字段、附件列表和审批时间线。

## 常见问题排查

### 1. 前端提示跨域错误

- 确认后端通过 `uvicorn app.main:app --reload --port 8000` 启动。
- 确认 `.env` 中 `CORS_ORIGINS` 包含 `http://localhost:5173`。

### 2. 登录后立刻 401

- 检查 `SECRET_KEY` 是否改动后未重新登录。
- 清除浏览器本地 `smartflow_token` 和 `smartflow_user` 后重新登录。

### 3. SQLite 被锁住

- 关闭重复启动的后端进程。
- 删除占用数据库的旧调试进程后重新运行 `python seed_data.py`。

### 4. 端口被占用

- 前端可改 [frontend/vite.config.js](/c:/Users/70669/Desktop/1/frontend/vite.config.js) 中 `server.port`。
- 后端可改 `.env` 中 `PORT`，或直接用 `uvicorn app.main:app --reload --port 8001`。

### 5. 没有 LLM Key 能否演示

- 可以。项目默认支持 Mock 规则模式，`/api/ai/analyze` 在无 Key 时仍可完整运行。
