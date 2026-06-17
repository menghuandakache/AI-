# AI 知识库管理平台

企业级 AI 知识库管理与专家 Agent 问答平台。基于 FastAPI、React、PostgreSQL + pgvector 和 bge-m3 实现企业知识库管理平台，支持文档导入、知识条目治理、向量检索、RAG 问答、来源引用、用户反馈和基础统计，形成从知识生产到 Agent 消费的完整闭环。

## 功能列表

### 核心功能
- **知识库管理**：创建、编辑、启用/停用、删除知识库空间
- **知识条目管理**：创建、编辑、发布、停用、删除知识条目，支持分类和标签管理
- **文档导入**：支持 PDF / DOCX / Markdown 文档上传，自动解析文本并生成知识草稿
- **知识检索**：支持关键词检索、语义检索和混合检索
- **专家 Agent 问答**：基于知识库的智能问答，展示引用来源，支持流式输出
- **用户反馈**：点赞/点踩，记录问答日志
- **数据看板**：知识统计、热门知识、问答次数、满意度统计

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + TypeScript + Vite + Ant Design 5 + React Router 6 + TanStack Query |
| 后端 | FastAPI + Pydantic + SQLAlchemy 2.0 + Alembic |
| 数据库 | PostgreSQL 16 + pgvector |
| 缓存/队列 | Redis + Celery |
| Embedding | bge-m3 (sentence-transformers) |
| 大模型 | OpenAI-compatible API |
| 容器化 | Docker Compose |

## 系统架构

```
┌──────────────────────────────────────────┐
│              前端 React 应用              │
│  知识库管理 / 知识编辑 / 文档导入 / Agent问答 │
└──────────────────┬───────────────────────┘
                   │ HTTP / SSE
                   ▼
┌──────────────────────────────────────────┐
│             FastAPI 后端服务              │
│  Auth / KB / Knowledge / Document / Search│
│  Agent / Chat / Feedback / Stats         │
└───────────────┬───────────────────┬──────┘
                │                   │
                ▼                   ▼
┌──────────────────────────┐  ┌──────────────┐
│  PostgreSQL + pgvector    │  │ Redis + Celery│
│  业务表 / 向量表 / 日志表  │  │ 异步任务队列   │
└──────────────┬───────────┘  └───────┬──────┘
               │                      │
               ▼                      ▼
┌──────────────────────────┐  ┌──────────────┐
│  bge-m3 Embedding 服务    │  │ 文档解析任务   │
└──────────────────────────┘  └──────────────┘
```

## 本地启动方式

### 前置要求

- Docker & Docker Compose
- Python 3.11+ (本地开发)
- Node.js 20+ (本地开发)

### 方式一：Docker Compose 一键启动

```bash
# 1. 克隆项目
cd ai-knowledge-platform

# 2. 复制环境变量
cp .env.example .env

# 3. 编辑 .env 配置（LLM API Key 等）

# 4. 启动所有服务
docker compose up -d

# 5. 初始化数据库和种子数据
docker compose exec backend python scripts/seed_data.py
```

访问地址：
- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 方式二：本地开发启动

**后端：**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 启动 PostgreSQL 和 Redis
docker compose up -d postgres redis

# 初始化数据库
python scripts/init_db.py
python scripts/seed_data.py

# 启动后端服务
uvicorn app.main:app --reload --port 8000
```

**前端：**

```bash
cd frontend
npm install
npm run dev
```

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | user | user123 |

## 环境变量说明

关键环境变量（详见 `.env.example`）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | PostgreSQL 连接地址 | postgresql://knowledge_user:knowledge_pass@localhost:5432/ai_knowledge_platform |
| REDIS_URL | Redis 连接地址 | redis://localhost:6379/0 |
| JWT_SECRET_KEY | JWT 密钥 | (需修改) |
| LLM_BASE_URL | LLM API 地址 | https://api.openai.com/v1 |
| LLM_API_KEY | LLM API Key | (需配置) |
| LLM_MODEL_NAME | LLM 模型名 | gpt-3.5-turbo |
| BGE_M3_MODEL_PATH | Embedding 模型路径 | BAAI/bge-m3 |
| CHUNK_SIZE | 知识切片大小 | 800 |
| CHUNK_OVERLAP | 切片重叠大小 | 100 |
| RETRIEVAL_TOP_K | 检索返回 Top K | 5 |
| SIMILARITY_THRESHOLD | 相似度阈值 | 0.5 |

## 目录结构

```
ai-knowledge-platform/
├── backend/                  # 后端 FastAPI 项目
│   ├── app/
│   │   ├── main.py          # 应用入口
│   │   ├── api/             # API 路由
│   │   │   └── routes/      # 各模块路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── repositories/    # 数据访问层
│   │   ├── services/        # 业务逻辑层
│   │   ├── tasks/           # Celery 异步任务
│   │   ├── prompts/         # RAG Prompt 模板
│   │   └── utils/           # 工具函数
│   ├── alembic/             # 数据库迁移
│   └── scripts/             # 初始化脚本
├── frontend/                 # 前端 React 项目
│   └── src/
│       ├── pages/           # 页面组件
│       ├── api/             # API 调用层
│       ├── components/      # 通用组件
│       ├── hooks/           # 自定义 Hooks
│       ├── store/           # 状态管理
│       └── types/           # TypeScript 类型
├── docker/                   # Docker 配置
│   ├── postgres/
│   ├── redis/
│   └── nginx/
├── docs/                     # 项目文档
│   ├── architecture.md      # 架构设计文档
│   ├── api.md               # 接口文档
│   ├── database.md          # 数据库设计
│   ├── rag_design.md        # RAG 设计文档
│   └── demo_script.md       # 演示脚本
├── scripts/                  # 启停脚本
├── docker-compose.yml       # Docker Compose 配置
└── README.md
```

## 演示流程

1. 登录系统（admin / admin123）
2. 创建财务报销知识库
3. 手动创建一条知识条目
4. 上传一份制度文档
5. 查看解析出的知识草稿
6. 发布知识
7. 创建财务报销专家 Agent
8. 向 Agent 提问
9. 查看回答和引用来源
10. 点赞或点踩
11. 查看统计看板

## 后续规划

1. AI 自动提炼知识候选项
2. 高频无答案问题聚类
3. 低满意回答分析
4. 知识版本管理与变更对比
5. 多知识库联合问答
6. Skill/插件调用管理
7. 多模态知识理解
8. 知识质量评分与治理看板

## 项目亮点

- **完整业务闭环**：知识生产 → 治理 → 检索 → Agent 消费 → 反馈统计
- **RAG 链路可解释**：文档解析 → 文本切片 → embedding → 向量检索 → Prompt 拼接 → LLM 生成 → 引用回溯 → 无答案拒答
- **工程化数据模型**：区分 KnowledgeBase / KnowledgeItem / KnowledgeChunk / Agent / QALog
- **异步任务合理**：Celery + Redis 处理文档解析和 embedding 生成
- **模型可替换**：embedding_service 和 llm_service 独立封装
- **引用来源和防幻觉**：检索阈值、状态过滤、引用回溯
