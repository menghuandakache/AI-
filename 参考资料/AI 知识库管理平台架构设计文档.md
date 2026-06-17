# AI 知识库管理平台架构设计文档

## 1. 项目定位

本项目定位为面向企业内部业务知识管理场景的 AI 知识库管理平台。平台围绕“知识生产、知识治理、知识检索、知识消费、反馈优化”构建完整闭环，使管理员能够将制度文档、流程说明、FAQ、操作指南等材料沉淀为结构化知识，普通用户能够通过专家 Agent 进行自然语言问答，系统能够基于知识库内容生成可追溯、可引用、可反馈的回答。

本项目首期以 MVP 为目标，不追求完整企业级复杂权限、复杂审核流、知识图谱、多模态理解和 Skill 市场，而是优先保证核心链路完整可运行：

```text
创建知识库
→ 创建知识条目 / 导入文档
→ 文本解析与切分
→ 生成 bge-m3 embedding
→ 写入 PostgreSQL + pgvector
→ 用户提问
→ 向量检索 / 关键词检索
→ 召回知识片段
→ 大模型生成回答
→ 展示引用来源
→ 用户反馈
→ 统计与后续优化
```

## 2. 总体技术选型

### 2.1 前端技术栈

| 技术                       | 用途                               |
| -------------------------- | ---------------------------------- |
| React                      | 构建前端单页应用                   |
| TypeScript                 | 提高类型约束和工程可维护性         |
| Vite                       | 前端构建工具，启动快，配置轻量     |
| Ant Design                 | 企业后台管理 UI 组件库             |
| React Router               | 前端路由管理                       |
| TanStack Query             | 接口请求、缓存、列表刷新、状态同步 |
| Axios                      | HTTP 请求封装                      |
| Markdown Editor            | 知识正文编辑                       |
| EventSource / fetch stream | 支持问答流式输出                   |

### 2.2 后端技术栈

| 技术                                  | 用途                                         |
| ------------------------------------- | -------------------------------------------- |
| FastAPI                               | 后端 API 服务框架                            |
| Pydantic                              | 请求参数、响应结果、配置校验                 |
| SQLAlchemy 2.0                        | ORM 数据访问                                 |
| Alembic                               | 数据库版本迁移                               |
| PostgreSQL                            | 业务数据存储                                 |
| pgvector                              | 向量存储与语义检索                           |
| Redis                                 | 缓存、任务队列 Broker                        |
| Celery                                | 文档解析、embedding 生成、索引更新等异步任务 |
| Uvicorn                               | ASGI 服务运行                                |
| python-jose                           | JWT 认证                                     |
| passlib / bcrypt                      | 密码加密                                     |
| PyMuPDF                               | PDF 文本解析                                 |
| python-docx                           | Word 文档解析                                |
| markdown                              | Markdown 文档解析                            |
| FlagEmbedding / sentence-transformers | 本地 bge-m3 embedding                        |
| OpenAI-compatible SDK                 | 调用大模型服务                               |

### 2.3 AI 能力选型

| 能力           | 选型                                                         |
| -------------- | ------------------------------------------------------------ |
| Embedding 模型 | bge-m3                                                       |
| 向量维度       | 默认按 bge-m3 dense embedding 维度配置，实际以模型运行输出为准 |
| 向量数据库     | PostgreSQL + pgvector                                        |
| 大模型         | OpenAI-compatible API / 阿里云百炼 / 火山方舟 / 本地 vLLM 均可 |
| RAG 实现方式   | 首期手写 RAG Pipeline，后期可接入 LangChain / LlamaIndex     |
| 检索策略       | MVP 使用关键词检索 + 向量检索，后续扩展混合检索与重排序      |

## 3. 系统总体架构

系统采用前后端分离架构，后端以 FastAPI 为核心，负责业务接口、权限控制、文档处理、索引构建、检索问答和日志统计。前端负责知识库管理、知识编辑、文档导入、Agent 问答和数据看板展示。异步任务由 Celery 处理，数据库使用 PostgreSQL 存储业务表和向量表。

```text
┌──────────────────────────────────────────────┐
│                 前端 React 应用               │
│  知识库管理 / 知识编辑 / 文档导入 / Agent问答  │
└──────────────────────┬───────────────────────┘
                       │ HTTP / SSE
                       ▼
┌──────────────────────────────────────────────┐
│                FastAPI 后端服务               │
│  Auth / KB / Knowledge / Document / Search    │
│  Agent / Chat / Feedback / Stats              │
└───────────────┬───────────────────┬──────────┘
                │                   │
                │ SQL / Vector SQL  │ Task
                ▼                   ▼
┌──────────────────────────┐   ┌──────────────────┐
│ PostgreSQL + pgvector     │   │ Redis + Celery    │
│ 业务表 / 向量表 / 日志表   │   │ 异步任务队列       │
└──────────────┬───────────┘   └─────────┬────────┘
               │                         │
               ▼                         ▼
┌──────────────────────────┐   ┌──────────────────┐
│ bge-m3 Embedding 服务      │   │ 文档解析 / 索引任务 │
└──────────────────────────┘   └──────────────────┘
               │
               ▼
┌──────────────────────────┐
│ LLM 服务                  │
│ RAG 答案生成 / 知识提炼    │
└──────────────────────────┘
```

## 4. 核心模块划分

系统按照业务能力拆分为 9 个核心模块。

| 模块             | 职责                                      | 首期是否实现 |
| ---------------- | ----------------------------------------- | ------------ |
| 用户与权限模块   | 登录、JWT、角色控制、基础权限校验         | 是           |
| 知识库管理模块   | 创建、编辑、启停、删除知识库              | 是           |
| 知识条目管理模块 | 创建、编辑、发布、停用、删除知识条目      | 是           |
| 文档导入模块     | 上传、解析、切分、生成草稿                | 是           |
| 向量索引模块     | 调用 bge-m3 生成 embedding，写入 pgvector | 是           |
| 检索模块         | 关键词检索、语义检索、TopK 召回           | 是           |
| Agent 问答模块   | 基于知识库进行 RAG 问答，展示引用来源     | 是           |
| 反馈与日志模块   | 记录问答日志、点赞点踩、引用知识          | 是           |
| 统计看板模块     | 展示知识数量、问答次数、反馈数、热门知识  | 简化实现     |

## 5. 业务流程设计

### 5.1 知识生产流程

```text
管理员创建知识库
→ 选择手动录入或文档导入
→ 生成知识条目草稿
→ 编辑标题、正文、分类、标签
→ 发布为可用知识
→ 系统生成切片和 embedding
→ 知识进入检索索引
```

说明：

1. 手动录入时，管理员填写标题、正文、分类、标签、状态。
2. 文档导入时，系统先保存原始文件，再解析文本。
3. 解析后的文本可以按章节、标题或固定长度切分。
4. 每个切分片段可以生成一个知识草稿，管理员确认后发布。
5. 发布后系统创建 chunk，并调用 bge-m3 生成 embedding。
6. 只有状态为 `available` 的知识进入正式检索范围。

### 5.2 知识管理流程

```text
进入知识库
→ 查看知识条目列表
→ 按关键词 / 分类 / 标签 / 状态筛选
→ 编辑知识
→ 发布 / 停用 / 删除
→ 触发索引更新
```

说明：

1. 草稿知识不参与问答。
2. 不可用知识不参与问答。
3. 删除采用软删除，避免日志引用断裂。
4. 修改已发布知识后，应重新生成 chunk 和 embedding。
5. 停用知识后，检索时通过状态过滤排除。

### 5.3 文档导入流程

```text
上传文档
→ 保存文件
→ 创建 document 记录
→ 提交 Celery 解析任务
→ 提取纯文本
→ 清洗文本
→ 章节切分 / 固定长度切分
→ 生成知识草稿
→ 管理员确认
→ 发布知识
→ 生成向量索引
```

说明：

1. PDF 使用 PyMuPDF 解析。
2. Word 使用 python-docx 解析。
3. Markdown 直接读取并转为纯文本。
4. 文档解析失败时记录失败原因。
5. 首期不处理扫描版 PDF 的 OCR。
6. 首期不深度解析复杂表格。

### 5.4 智能问答流程

```text
用户选择专家 Agent
→ 输入问题
→ 根据 Agent 绑定的知识库确定检索范围
→ 对问题生成 query embedding
→ 从 pgvector 检索相似 chunk
→ 同时执行关键词检索
→ 合并候选结果
→ 过滤不可用知识和低相似度知识
→ 构造 RAG Prompt
→ 调用大模型生成答案
→ 返回 answer + sources
→ 写入 qa_logs
→ 用户点赞 / 点踩
```

说明：

1. 回答必须基于召回知识。
2. 如果没有召回到相关知识，直接返回无答案提示。
3. 引用来源需要回溯到知识条目、来源文件和 chunk。
4. 用户反馈写入日志，用于后续统计和知识优化。
5. 首期可先不做复杂多轮记忆，只保留当前轮问答。

## 6. 后端工程目录设计

后端目录建议如下：

```text
backend/
  app/
    main.py
    api/
      __init__.py
      deps.py
      routes/
        __init__.py
        auth.py
        users.py
        kb.py
        knowledge.py
        document.py
        search.py
        agent.py
        chat.py
        feedback.py
        stats.py
    core/
      __init__.py
      config.py
      database.py
      security.py
      logging.py
      exceptions.py
      constants.py
    models/
      __init__.py
      user.py
      knowledge_base.py
      knowledge_item.py
      knowledge_chunk.py
      document.py
      agent.py
      qa_log.py
      feedback.py
      audit_log.py
    schemas/
      __init__.py
      auth.py
      user.py
      kb.py
      knowledge.py
      document.py
      search.py
      agent.py
      chat.py
      feedback.py
      stats.py
    repositories/
      __init__.py
      user_repo.py
      kb_repo.py
      knowledge_repo.py
      chunk_repo.py
      document_repo.py
      agent_repo.py
      qa_repo.py
      stats_repo.py
    services/
      __init__.py
      auth_service.py
      kb_service.py
      knowledge_service.py
      document_service.py
      parser_service.py
      chunk_service.py
      embedding_service.py
      retrieval_service.py
      rag_service.py
      llm_service.py
      agent_service.py
      feedback_service.py
      stats_service.py
      audit_service.py
    tasks/
      __init__.py
      celery_app.py
      document_tasks.py
      embedding_tasks.py
      index_tasks.py
      cleanup_tasks.py
    prompts/
      rag_answer_prompt.txt
      no_answer_prompt.txt
      knowledge_extract_prompt.txt
      agent_generate_prompt.txt
    utils/
      __init__.py
      file_utils.py
      text_cleaner.py
      text_splitter.py
      hash_utils.py
      time_utils.py
      response_utils.py
    tests/
      test_auth.py
      test_kb.py
      test_knowledge.py
      test_document.py
      test_search.py
      test_chat.py
  alembic/
    versions/
    env.py
  scripts/
    init_db.py
    seed_data.py
    create_admin.py
    rebuild_embeddings.py
    clear_demo_data.py
  requirements.txt
  Dockerfile
  .env.example
```

## 7. 后端核心文件职责

### 7.1 `app/main.py`

负责 FastAPI 应用初始化。

主要功能：

1. 创建 FastAPI app。
2. 加载 CORS 配置。
3. 注册全局异常处理器。
4. 注册 API 路由。
5. 注册健康检查接口。
6. 初始化日志配置。
7. 提供 `/health` 接口检查服务状态。

示例职责：

```text
GET /health
返回：
- app status
- database status
- redis status
- embedding model status
```

### 7.2 `app/core/config.py`

负责系统配置管理。

主要功能：

1. 读取 `.env` 环境变量。
2. 配置数据库连接地址。
3. 配置 Redis 地址。
4. 配置 JWT 密钥和过期时间。
5. 配置上传文件目录。
6. 配置 embedding 模型路径。
7. 配置 LLM API 地址、模型名和 API Key。
8. 配置 TopK、相似度阈值、chunk size、chunk overlap。

核心配置项：

```text
DATABASE_URL
REDIS_URL
JWT_SECRET_KEY
UPLOAD_DIR
BGE_M3_MODEL_PATH
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL_NAME
CHUNK_SIZE
CHUNK_OVERLAP
RETRIEVAL_TOP_K
SIMILARITY_THRESHOLD
```

### 7.3 `app/core/database.py`

负责数据库连接。

主要功能：

1. 创建 SQLAlchemy engine。
2. 创建 SessionLocal。
3. 提供 `get_db()` 依赖。
4. 统一管理数据库会话生命周期。
5. 支持 Alembic 迁移。

### 7.4 `app/core/security.py`

负责认证与安全能力。

主要功能：

1. 密码哈希。
2. 密码校验。
3. JWT token 生成。
4. JWT token 解析。
5. 当前用户识别。
6. 角色权限判断。

### 7.5 `app/core/exceptions.py`

负责统一异常定义。

主要功能：

1. 定义业务异常 `BusinessException`。
2. 定义资源不存在异常。
3. 定义权限不足异常。
4. 定义参数校验异常。
5. 定义文件解析异常。
6. 定义模型调用异常。
7. 统一返回错误码和错误信息。

### 7.6 `app/models/`

`models` 目录存放数据库 ORM 模型，每个文件对应一类核心实体。

#### `user.py`

用户表模型。

字段：

```text
id
username
password_hash
email
role
status
created_at
updated_at
```

角色建议：

```text
admin
knowledge_admin
user
```

#### `knowledge_base.py`

知识库表模型。

字段：

```text
id
name
description
domain
owner_id
status
created_by
created_at
updated_at
```

状态：

```text
enabled
disabled
deleted
```

#### `knowledge_item.py`

知识条目表模型。

字段：

```text
id
kb_id
title
content
summary
category
tags
status
source_type
source_file_id
created_by
updated_by
created_at
updated_at
deleted_at
```

状态：

```text
draft
available
unavailable
deleted
```

来源类型：

```text
manual
document
ai_extract
dialogue
```

#### `knowledge_chunk.py`

知识切片表模型。

字段：

```text
id
knowledge_id
kb_id
chunk_text
chunk_index
embedding
metadata
token_count
created_at
updated_at
```

其中 `embedding` 使用 pgvector 类型。`metadata` 使用 JSONB，保存来源页码、章节、文件名、知识标题、分类、标签等信息。

#### `document.py`

文档表模型。

字段：

```text
id
kb_id
filename
file_path
file_type
file_size
parse_status
parse_error
created_by
created_at
updated_at
```

解析状态：

```text
uploaded
parsing
parsed
failed
imported
```

#### `agent.py`

专家 Agent 表模型。

字段：

```text
id
name
description
kb_ids
prompt_config
answer_style
citation_policy
no_answer_policy
status
created_by
created_at
updated_at
```

#### `qa_log.py`

问答日志表模型。

字段：

```text
id
user_id
agent_id
kb_id
question
answer
retrieved_chunk_ids
cited_knowledge_ids
status
latency_ms
created_at
```

回答状态：

```text
answered
no_answer
failed
```

#### `feedback.py`

反馈表模型。

字段：

```text
id
qa_log_id
user_id
feedback_type
feedback_reason
created_at
```

反馈类型：

```text
like
dislike
```

#### `audit_log.py`

审计日志表模型。

字段：

```text
id
user_id
action
resource_type
resource_id
detail
created_at
```

用于记录创建知识、发布知识、删除知识、文档导入等关键操作。

### 7.7 `app/schemas/`

`schemas` 目录存放 Pydantic 请求和响应模型，负责 API 入参校验和出参格式化。

#### `auth.py`

包含：

```text
LoginRequest
LoginResponse
TokenPayload
```

#### `kb.py`

包含：

```text
KnowledgeBaseCreate
KnowledgeBaseUpdate
KnowledgeBaseStatusUpdate
KnowledgeBaseResponse
KnowledgeBaseListResponse
```

#### `knowledge.py`

包含：

```text
KnowledgeCreate
KnowledgeUpdate
KnowledgePublishRequest
KnowledgeResponse
KnowledgeListQuery
KnowledgeListResponse
```

#### `document.py`

包含：

```text
DocumentUploadResponse
DocumentParseRequest
DocumentParseResponse
DocumentImportRequest
DocumentImportResponse
```

#### `search.py`

包含：

```text
KeywordSearchRequest
SemanticSearchRequest
HybridSearchRequest
SearchResultItem
SearchResponse
```

#### `agent.py`

包含：

```text
AgentCreate
AgentUpdate
AgentResponse
AgentListResponse
```

#### `chat.py`

包含：

```text
ChatRequest
ChatResponse
CitationSource
RetrievedChunk
```

#### `feedback.py`

包含：

```text
FeedbackCreate
FeedbackResponse
```

#### `stats.py`

包含：

```text
OverviewStatsResponse
HotKnowledgeItem
FeedbackStatsResponse
```

### 7.8 `app/repositories/`

`repositories` 目录负责数据库访问，避免 service 层直接写复杂 SQL。

#### `user_repo.py`

功能：

1. 根据用户名查询用户。
2. 创建用户。
3. 更新用户状态。
4. 查询用户角色。

#### `kb_repo.py`

功能：

1. 创建知识库。
2. 查询知识库列表。
3. 查询知识库详情。
4. 更新知识库。
5. 启用 / 停用知识库。
6. 软删除知识库。

#### `knowledge_repo.py`

功能：

1. 创建知识条目。
2. 查询知识列表。
3. 查询知识详情。
4. 更新知识条目。
5. 发布知识。
6. 停用知识。
7. 删除知识。
8. 根据筛选条件查询知识。

#### `chunk_repo.py`

功能：

1. 批量创建知识 chunk。
2. 删除某知识条目的旧 chunk。
3. 查询 chunk 详情。
4. 执行 pgvector 向量相似度检索。
5. 根据 kb_id、status、category、tags 过滤 chunk。
6. 更新 chunk metadata。

#### `document_repo.py`

功能：

1. 创建文档记录。
2. 更新文档解析状态。
3. 查询文档详情。
4. 查询文档导入历史。
5. 保存解析错误信息。

#### `agent_repo.py`

功能：

1. 创建 Agent。
2. 查询 Agent 列表。
3. 查询 Agent 详情。
4. 更新 Agent 配置。
5. 停用 Agent。

#### `qa_repo.py`

功能：

1. 创建问答日志。
2. 查询问答历史。
3. 更新问答反馈状态。
4. 查询低满意回答。
5. 查询无答案问题。

#### `stats_repo.py`

功能：

1. 统计知识总数。
2. 统计可用知识数。
3. 统计问答次数。
4. 统计点赞点踩数量。
5. 统计知识引用次数。
6. 查询热门知识排行。

### 7.9 `app/services/`

`services` 目录是业务逻辑核心层。

#### `auth_service.py`

功能：

1. 用户登录。
2. 密码校验。
3. 生成 JWT。
4. 获取当前用户信息。
5. 判断用户角色权限。

#### `kb_service.py`

功能：

1. 创建知识库时校验名称是否重复。
2. 编辑知识库信息。
3. 停用知识库时阻止其继续参与问答。
4. 删除知识库时检查是否存在未删除知识。
5. 返回知识库统计概览。

#### `knowledge_service.py`

功能：

1. 创建手动知识条目。
2. 编辑知识内容。
3. 发布知识并触发索引任务。
4. 停用知识并使其不再参与检索。
5. 删除知识并软删除关联 chunk。
6. 查询知识详情时返回来源信息和 chunk 信息。

#### `document_service.py`

功能：

1. 接收上传文件。
2. 校验文件类型和大小。
3. 保存到 uploads 目录。
4. 创建 document 记录。
5. 提交 Celery 解析任务。
6. 返回任务状态。

#### `parser_service.py`

功能：

1. 根据文件类型选择解析器。
2. PDF 调用 PyMuPDF 解析文本。
3. DOCX 调用 python-docx 解析文本。
4. Markdown 读取文本并清理格式。
5. 返回完整纯文本和章节结构。
6. 解析失败时抛出明确异常。

#### `chunk_service.py`

功能：

1. 清洗文本。
2. 按标题、章节、段落切分文本。
3. 如果无法识别结构，按固定长度切分。
4. 给每个 chunk 绑定 metadata。
5. 控制 chunk size 和 overlap。
6. 计算 token_count。
7. 生成知识草稿或正式知识 chunk。

#### `embedding_service.py`

功能：

1. 加载 bge-m3 模型。
2. 对 query 生成 embedding。
3. 对知识 chunk 批量生成 embedding。
4. 归一化向量。
5. 支持批处理，减少模型调用次数。
6. 提供 embedding 维度检查。
7. 后续可替换为远程 embedding API。

#### `retrieval_service.py`

功能：

1. 关键词检索。
2. 向量检索。
3. 混合检索。
4. TopK 召回。
5. 相似度阈值过滤。
6. 知识库范围过滤。
7. 状态过滤。
8. 标签、分类过滤。
9. 返回可引用的 chunk 和 knowledge item 信息。

MVP 检索策略：

```text
1. 使用 pgvector 根据 query embedding 召回 TopK chunk。
2. 使用 PostgreSQL ILIKE 或全文索引做关键词检索。
3. 合并两路结果。
4. 去重。
5. 按综合分数排序。
6. 取 Top 3 到 Top 5 进入 RAG prompt。
```

#### `llm_service.py`

功能：

1. 封装大模型 API 调用。
2. 支持普通输出和流式输出。
3. 统一处理 API Key、base_url、model_name。
4. 处理调用失败、超时、限流。
5. 提供 chat completion 接口。
6. 后续支持切换本地 vLLM 或云厂商模型。

#### `rag_service.py`

功能：

1. 接收用户问题和 Agent 配置。
2. 调用 retrieval_service 召回知识。
3. 判断是否无答案。
4. 组织 context。
5. 读取 prompt 模板。
6. 拼接 RAG Prompt。
7. 调用 llm_service 生成回答。
8. 解析引用来源。
9. 写入问答日志。
10. 返回答案、来源和状态。

#### `agent_service.py`

功能：

1. 创建专家 Agent。
2. 绑定一个或多个知识库。
3. 配置回答风格。
4. 配置引用策略。
5. 配置无答案策略。
6. 一键生成 Agent 名称、简介和提示词。
7. 查询 Agent 列表和详情。

#### `feedback_service.py`

功能：

1. 提交点赞。
2. 提交点踩。
3. 记录反馈原因。
4. 更新 qa_log 的 feedback 字段。
5. 为低满意回答统计提供数据。

#### `stats_service.py`

功能：

1. 返回首页统计卡片。
2. 返回知识库知识数量。
3. 返回问答次数。
4. 返回点赞点踩统计。
5. 返回热门知识。
6. 返回无答案问题列表。
7. 返回低满意回答列表。

#### `audit_service.py`

功能：

1. 记录关键操作日志。
2. 记录操作者。
3. 记录资源类型和资源 ID。
4. 保存操作前后状态。
5. 支持后续审计查询。

### 7.10 `app/tasks/`

`tasks` 目录存放异步任务。

#### `celery_app.py`

功能：

1. 创建 Celery 实例。
2. 配置 Redis broker。
3. 配置任务队列。
4. 配置任务重试策略。
5. 自动发现任务模块。

#### `document_tasks.py`

功能：

1. 异步解析文档。
2. 更新 document 状态为 `parsing`。
3. 调用 parser_service 提取文本。
4. 调用 chunk_service 切分文本。
5. 生成知识草稿。
6. 成功后状态改为 `parsed`。
7. 失败后状态改为 `failed` 并记录错误。

#### `embedding_tasks.py`

功能：

1. 对发布后的知识条目生成 chunk。
2. 批量调用 embedding_service。
3. 写入 knowledge_chunks。
4. 删除旧版本 chunk。
5. 更新索引状态。
6. 失败时支持重试。

#### `index_tasks.py`

功能：

1. 重新构建某个知识条目的索引。
2. 重新构建某个知识库的全部索引。
3. 支持管理员手动触发重建。
4. 用于修复 embedding 模型变更后的索引不一致。

#### `cleanup_tasks.py`

功能：

1. 清理临时上传文件。
2. 清理软删除知识的过期 chunk。
3. 清理失败任务产生的中间文件。
4. 后续可定时执行。

### 7.11 `app/prompts/`

`prompts` 目录存放提示词模板。

#### `rag_answer_prompt.txt`

用于普通 RAG 问答。

模板要求：

```text
你是企业内部知识库问答助手。
你必须严格基于给定知识片段回答问题。
如果知识片段不足以回答，请明确说明当前知识库中未找到相关内容。
回答应结构化，优先使用条目、步骤和注意事项。
回答结尾必须列出引用来源。
```

#### `no_answer_prompt.txt`

用于无答案提示。

功能：

1. 告知用户当前知识库无相关内容。
2. 建议用户更换关键词。
3. 支持提交反馈。
4. 不调用大模型也可直接返回。

#### `knowledge_extract_prompt.txt`

用于 AI 自动提炼知识候选项。

功能：

1. 从文档片段中提取知识标题。
2. 提取知识正文。
3. 识别知识类型。
4. 推荐标签。
5. 保留来源段落。
6. 要求不得补充原文不存在的信息。

#### `agent_generate_prompt.txt`

用于一键生成专家 Agent。

功能：

1. 根据知识库名称和描述生成 Agent 名称。
2. 生成 Agent 简介。
3. 生成 Agent system prompt。
4. 生成无答案策略。
5. 生成引用策略。

### 7.12 `app/utils/`

`utils` 目录存放通用工具函数。

#### `file_utils.py`

功能：

1. 生成安全文件名。
2. 校验文件类型。
3. 保存上传文件。
4. 获取文件扩展名。
5. 计算文件大小。
6. 删除临时文件。

#### `text_cleaner.py`

功能：

1. 去除多余空格。
2. 去除页眉页脚。
3. 去除重复换行。
4. 统一中英文标点。
5. 过滤无效字符。

#### `text_splitter.py`

功能：

1. 按标题切分。
2. 按段落切分。
3. 按固定长度切分。
4. 支持 chunk overlap。
5. 返回 chunk 列表和 chunk_index。

#### `hash_utils.py`

功能：

1. 计算文件 hash。
2. 计算文本 hash。
3. 用于判断重复上传和重复知识。

#### `time_utils.py`

功能：

1. 统一时间格式。
2. 处理时区。
3. 生成当前时间戳。

#### `response_utils.py`

功能：

1. 统一成功响应格式。
2. 统一分页响应格式。
3. 统一错误响应格式。

## 8. 前端工程目录设计

前端目录建议如下：

```text
frontend/
  src/
    main.tsx
    App.tsx
    router/
      index.tsx
      routes.tsx
    layouts/
      BasicLayout.tsx
      AuthLayout.tsx
    pages/
      Login/
        index.tsx
      Dashboard/
        index.tsx
        components/
          StatCards.tsx
          HotKnowledgeTable.tsx
      KnowledgeBase/
        ListPage.tsx
        DetailPage.tsx
        components/
          KnowledgeBaseForm.tsx
          KnowledgeBaseCard.tsx
      Knowledge/
        ListPage.tsx
        EditPage.tsx
        DetailPage.tsx
        components/
          KnowledgeForm.tsx
          KnowledgeStatusTag.tsx
          TagSelector.tsx
      DocumentImport/
        index.tsx
        components/
          UploadPanel.tsx
          ParseResult.tsx
          DraftKnowledgeTable.tsx
      Agent/
        ListPage.tsx
        ConfigPage.tsx
        ChatPage.tsx
        components/
          AgentForm.tsx
          ChatMessage.tsx
          CitationPanel.tsx
          FeedbackButtons.tsx
      Search/
        index.tsx
        components/
          SearchBox.tsx
          SearchResultList.tsx
      Stats/
        index.tsx
    api/
      request.ts
      auth.ts
      kb.ts
      knowledge.ts
      document.ts
      search.ts
      agent.ts
      chat.ts
      stats.ts
    types/
      auth.ts
      kb.ts
      knowledge.ts
      document.ts
      agent.ts
      chat.ts
      stats.ts
    store/
      authStore.ts
      appStore.ts
    hooks/
      useAuth.ts
      useKnowledgeBase.ts
      useChatStream.ts
    components/
      PageHeader.tsx
      StatusTag.tsx
      ConfirmButton.tsx
      MarkdownViewer.tsx
      MarkdownEditor.tsx
    utils/
      formatTime.ts
      constants.ts
      permission.ts
  package.json
  vite.config.ts
  tsconfig.json
  Dockerfile
  .env.example
```

## 9. 前端核心文件职责

### 9.1 `src/main.tsx`

功能：

1. React 应用入口。
2. 挂载 App。
3. 注入 Router。
4. 注入 QueryClient。
5. 引入全局样式。

### 9.2 `src/App.tsx`

功能：

1. 管理全局布局。
2. 注册路由出口。
3. 控制登录态跳转。
4. 加载全局配置。

### 9.3 `src/router/`

#### `index.tsx`

功能：

1. 创建浏览器路由。
2. 定义登录页、后台页、问答页路由。
3. 实现权限路由拦截。

#### `routes.tsx`

功能：

1. 维护路由配置表。
2. 配置菜单名称、图标、路径。
3. 控制不同角色可见页面。

### 9.4 `src/layouts/`

#### `BasicLayout.tsx`

功能：

1. 后台主布局。
2. 左侧菜单。
3. 顶部用户信息。
4. 内容区。
5. 退出登录按钮。

#### `AuthLayout.tsx`

功能：

1. 登录页布局。
2. 居中展示登录表单。
3. 展示项目名称和介绍。

### 9.5 `src/pages/Login/index.tsx`

功能：

1. 登录表单。
2. 调用登录接口。
3. 保存 token。
4. 跳转后台首页。

### 9.6 `src/pages/Dashboard/index.tsx`

功能：

1. 展示知识总数。
2. 展示可用知识数。
3. 展示问答次数。
4. 展示点赞点踩数量。
5. 展示热门知识列表。
6. 展示最近问答记录。

### 9.7 `src/pages/KnowledgeBase/`

#### `ListPage.tsx`

功能：

1. 查询知识库列表。
2. 搜索知识库。
3. 创建知识库。
4. 编辑知识库。
5. 启用 / 停用知识库。
6. 删除知识库。
7. 进入知识库详情。

#### `DetailPage.tsx`

功能：

1. 展示知识库基础信息。
2. 展示知识数量。
3. 展示该知识库下知识条目。
4. 提供导入文档入口。
5. 提供创建 Agent 入口。

#### `KnowledgeBaseForm.tsx`

功能：

1. 创建和编辑知识库表单。
2. 字段包括名称、描述、业务域、负责人、状态。
3. 表单校验。
4. 提交后刷新列表。

### 9.8 `src/pages/Knowledge/`

#### `ListPage.tsx`

功能：

1. 展示知识条目列表。
2. 按关键词搜索。
3. 按分类筛选。
4. 按标签筛选。
5. 按状态筛选。
6. 创建知识。
7. 编辑知识。
8. 发布 / 停用 / 删除知识。

#### `EditPage.tsx`

功能：

1. 编辑知识标题。
2. 编辑知识正文。
3. 选择知识库。
4. 设置分类。
5. 设置标签。
6. 设置状态。
7. 保存草稿。
8. 发布知识。

#### `DetailPage.tsx`

功能：

1. 查看知识详情。
2. 查看来源文件。
3. 查看更新时间。
4. 查看关联 chunk。
5. 查看被引用次数。

### 9.9 `src/pages/DocumentImport/`

#### `index.tsx`

功能：

1. 选择目标知识库。
2. 上传 PDF / DOCX / Markdown。
3. 展示上传进度。
4. 展示解析状态。
5. 展示生成的知识草稿。
6. 支持编辑草稿。
7. 确认导入知识库。

#### `UploadPanel.tsx`

功能：

1. 文件拖拽上传。
2. 文件类型校验。
3. 文件大小校验。
4. 调用上传接口。

#### `ParseResult.tsx`

功能：

1. 展示文档解析结果。
2. 展示分段文本。
3. 展示解析错误信息。
4. 支持重新解析。

#### `DraftKnowledgeTable.tsx`

功能：

1. 展示生成的知识草稿。
2. 支持编辑标题。
3. 支持编辑正文。
4. 支持删除某条草稿。
5. 支持批量确认入库。

### 9.10 `src/pages/Agent/`

#### `ListPage.tsx`

功能：

1. 展示 Agent 列表。
2. 创建 Agent。
3. 编辑 Agent。
4. 启用 / 停用 Agent。
5. 进入问答页面。

#### `ConfigPage.tsx`

功能：

1. 配置 Agent 名称。
2. 配置 Agent 描述。
3. 绑定知识库。
4. 选择回答风格。
5. 配置引用策略。
6. 配置无答案策略。

#### `ChatPage.tsx`

功能：

1. 展示对话区。
2. 用户输入问题。
3. 调用 Agent 问答接口。
4. 支持流式输出。
5. 展示引用来源。
6. 点赞 / 点踩。
7. 展示无答案提示。

#### `CitationPanel.tsx`

功能：

1. 展示引用知识标题。
2. 展示来源文件。
3. 展示更新时间。
4. 点击后跳转知识详情。
5. 展示命中片段。

### 9.11 `src/api/`

`api` 目录负责统一封装后端接口。

#### `request.ts`

功能：

1. 创建 Axios 实例。
2. 注入 token。
3. 统一处理 401。
4. 统一处理错误提示。
5. 配置 baseURL。

#### `kb.ts`

封装知识库接口：

```text
getKnowledgeBases
createKnowledgeBase
updateKnowledgeBase
deleteKnowledgeBase
updateKnowledgeBaseStatus
```

#### `knowledge.ts`

封装知识条目接口：

```text
getKnowledgeList
getKnowledgeDetail
createKnowledge
updateKnowledge
publishKnowledge
disableKnowledge
deleteKnowledge
```

#### `document.ts`

封装文档接口：

```text
uploadDocument
parseDocument
getDocumentStatus
importDraftKnowledge
```

#### `search.ts`

封装检索接口：

```text
keywordSearch
semanticSearch
hybridSearch
```

#### `agent.ts`

封装 Agent 接口：

```text
getAgents
createAgent
updateAgent
disableAgent
generateAgent
```

#### `chat.ts`

封装问答接口：

```text
askAgent
askAgentStream
submitFeedback
getChatHistory
```

#### `stats.ts`

封装统计接口：

```text
getOverviewStats
getHotKnowledge
getFeedbackStats
getNoAnswerQuestions
```

## 10. 数据库设计

### 10.1 `users`

用户表。

| 字段          | 类型      | 说明     |
| ------------- | --------- | -------- |
| id            | uuid      | 用户 ID  |
| username      | varchar   | 用户名   |
| password_hash | varchar   | 密码哈希 |
| email         | varchar   | 邮箱     |
| role          | varchar   | 角色     |
| status        | varchar   | 状态     |
| created_at    | timestamp | 创建时间 |
| updated_at    | timestamp | 更新时间 |

### 10.2 `knowledge_bases`

知识库表。

| 字段        | 类型      | 说明                         |
| ----------- | --------- | ---------------------------- |
| id          | uuid      | 知识库 ID                    |
| name        | varchar   | 知识库名称                   |
| description | text      | 描述                         |
| domain      | varchar   | 业务域                       |
| owner_id    | uuid      | 负责人                       |
| status      | varchar   | enabled / disabled / deleted |
| created_by  | uuid      | 创建人                       |
| created_at  | timestamp | 创建时间                     |
| updated_at  | timestamp | 更新时间                     |

索引：

```text
idx_kb_status
idx_kb_domain
idx_kb_owner
```

### 10.3 `knowledge_items`

知识条目表。

| 字段           | 类型      | 说明                                      |
| -------------- | --------- | ----------------------------------------- |
| id             | uuid      | 知识 ID                                   |
| kb_id          | uuid      | 所属知识库                                |
| title          | varchar   | 标题                                      |
| content        | text      | 正文                                      |
| summary        | text      | 摘要                                      |
| category       | varchar   | 分类                                      |
| tags           | jsonb     | 标签                                      |
| status         | varchar   | draft / available / unavailable / deleted |
| source_type    | varchar   | manual / document / ai_extract            |
| source_file_id | uuid      | 来源文件                                  |
| created_by     | uuid      | 创建人                                    |
| updated_by     | uuid      | 更新人                                    |
| created_at     | timestamp | 创建时间                                  |
| updated_at     | timestamp | 更新时间                                  |
| deleted_at     | timestamp | 删除时间                                  |

索引：

```text
idx_knowledge_kb_id
idx_knowledge_status
idx_knowledge_category
idx_knowledge_tags
idx_knowledge_created_at
```

### 10.4 `knowledge_chunks`

知识切片表。

| 字段         | 类型      | 说明                     |
| ------------ | --------- | ------------------------ |
| id           | uuid      | chunk ID                 |
| knowledge_id | uuid      | 所属知识条目             |
| kb_id        | uuid      | 所属知识库               |
| chunk_text   | text      | 切片文本                 |
| chunk_index  | int       | 切片序号                 |
| embedding    | vector    | bge-m3 向量              |
| metadata     | jsonb     | 来源、页码、章节、标签等 |
| token_count  | int       | token 数                 |
| created_at   | timestamp | 创建时间                 |
| updated_at   | timestamp | 更新时间                 |

索引：

```text
idx_chunk_knowledge_id
idx_chunk_kb_id
idx_chunk_metadata
idx_chunk_embedding_ivfflat 或 hnsw
```

说明：

1. `knowledge_items` 面向知识管理。
2. `knowledge_chunks` 面向检索问答。
3. 一个知识条目可以对应多个 chunk。
4. 回答引用时从 chunk 回溯到 knowledge item。
5. metadata 中保存来源文件、页码、章节标题、分类、标签等。

### 10.5 `documents`

文档表。

| 字段         | 类型      | 说明                                            |
| ------------ | --------- | ----------------------------------------------- |
| id           | uuid      | 文档 ID                                         |
| kb_id        | uuid      | 所属知识库                                      |
| filename     | varchar   | 原始文件名                                      |
| file_path    | varchar   | 文件存储路径                                    |
| file_type    | varchar   | pdf / docx / md                                 |
| file_size    | bigint    | 文件大小                                        |
| parse_status | varchar   | uploaded / parsing / parsed / failed / imported |
| parse_error  | text      | 解析错误                                        |
| created_by   | uuid      | 上传人                                          |
| created_at   | timestamp | 创建时间                                        |
| updated_at   | timestamp | 更新时间                                        |

### 10.6 `agents`

Agent 表。

| 字段             | 类型      | 说明               |
| ---------------- | --------- | ------------------ |
| id               | uuid      | Agent ID           |
| name             | varchar   | Agent 名称         |
| description      | text      | Agent 描述         |
| kb_ids           | jsonb     | 绑定知识库         |
| prompt_config    | text      | 提示词配置         |
| answer_style     | varchar   | 回答风格           |
| citation_policy  | varchar   | 引用策略           |
| no_answer_policy | varchar   | 无答案策略         |
| status           | varchar   | enabled / disabled |
| created_by       | uuid      | 创建人             |
| created_at       | timestamp | 创建时间           |
| updated_at       | timestamp | 更新时间           |

### 10.7 `qa_logs`

问答日志表。

| 字段                | 类型      | 说明                          |
| ------------------- | --------- | ----------------------------- |
| id                  | uuid      | 日志 ID                       |
| user_id             | uuid      | 用户 ID                       |
| agent_id            | uuid      | Agent ID                      |
| kb_id               | uuid      | 知识库 ID                     |
| question            | text      | 用户问题                      |
| answer              | text      | AI 回答                       |
| retrieved_chunk_ids | jsonb     | 召回 chunk                    |
| cited_knowledge_ids | jsonb     | 引用知识                      |
| status              | varchar   | answered / no_answer / failed |
| feedback            | varchar   | like / dislike / none         |
| latency_ms          | int       | 响应耗时                      |
| created_at          | timestamp | 创建时间                      |

### 10.8 `feedbacks`

反馈表。

| 字段            | 类型      | 说明           |
| --------------- | --------- | -------------- |
| id              | uuid      | 反馈 ID        |
| qa_log_id       | uuid      | 问答日志 ID    |
| user_id         | uuid      | 用户 ID        |
| feedback_type   | varchar   | like / dislike |
| feedback_reason | text      | 反馈原因       |
| created_at      | timestamp | 创建时间       |

### 10.9 `audit_logs`

审计日志表。

| 字段          | 类型      | 说明     |
| ------------- | --------- | -------- |
| id            | uuid      | 日志 ID  |
| user_id       | uuid      | 操作人   |
| action        | varchar   | 操作类型 |
| resource_type | varchar   | 资源类型 |
| resource_id   | uuid      | 资源 ID  |
| detail        | jsonb     | 操作详情 |
| created_at    | timestamp | 创建时间 |

## 11. API 设计

### 11.1 认证接口

```text
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout
```

### 11.2 知识库接口

```text
GET    /api/kb
POST   /api/kb
GET    /api/kb/{kb_id}
PUT    /api/kb/{kb_id}
DELETE /api/kb/{kb_id}
PATCH  /api/kb/{kb_id}/status
GET    /api/kb/{kb_id}/overview
```

### 11.3 知识条目接口

```text
GET    /api/knowledge
POST   /api/knowledge
GET    /api/knowledge/{knowledge_id}
PUT    /api/knowledge/{knowledge_id}
DELETE /api/knowledge/{knowledge_id}
PATCH  /api/knowledge/{knowledge_id}/publish
PATCH  /api/knowledge/{knowledge_id}/disable
GET    /api/knowledge/{knowledge_id}/chunks
```

### 11.4 文档导入接口

```text
POST /api/documents/upload
POST /api/documents/{document_id}/parse
GET  /api/documents/{document_id}/status
GET  /api/documents/{document_id}/drafts
POST /api/documents/{document_id}/import
```

### 11.5 检索接口

```text
POST /api/search/keyword
POST /api/search/semantic
POST /api/search/hybrid
```

### 11.6 Agent 接口

```text
GET    /api/agents
POST   /api/agents
GET    /api/agents/{agent_id}
PUT    /api/agents/{agent_id}
PATCH  /api/agents/{agent_id}/disable
POST   /api/agents/generate
POST   /api/agents/{agent_id}/chat
POST   /api/agents/{agent_id}/chat/stream
```

### 11.7 反馈接口

```text
POST /api/feedback
GET  /api/feedback/qa/{qa_log_id}
```

### 11.8 统计接口

```text
GET /api/stats/overview
GET /api/stats/hot-knowledge
GET /api/stats/feedback
GET /api/stats/no-answer
GET /api/stats/recent-qa
```

## 12. RAG 检索问答设计

### 12.1 入库阶段

```text
知识正文
→ text_cleaner 清洗
→ text_splitter 切片
→ embedding_service 生成向量
→ chunk_repo 写入 knowledge_chunks
```

切片策略：

```text
chunk_size = 800 到 1000 中文字符
chunk_overlap = 100 到 150 中文字符
```

metadata 示例：

```json
{
  "knowledge_id": "xxx",
  "kb_id": "xxx",
  "title": "差旅报销材料要求",
  "category": "制度规范",
  "tags": ["报销", "差旅"],
  "source_type": "document",
  "source_file": "财务报销制度.pdf",
  "page": 3,
  "section": "第三章 报销材料"
}
```

### 12.2 检索阶段

输入：

```text
question
kb_id / agent_id
top_k
similarity_threshold
```

处理：

```text
1. 使用 bge-m3 生成 question embedding。
2. 使用 pgvector 查询相似 chunk。
3. 过滤 kb_id。
4. 过滤 knowledge_items.status = available。
5. 过滤 knowledge_bases.status = enabled。
6. 过滤相似度低于阈值的结果。
7. 取 TopK。
8. 返回 chunk_text、score、knowledge_id、title、source_file。
```

### 12.3 生成阶段

RAG Prompt 结构：

```text
System:
你是企业内部知识库问答助手，必须严格基于知识库内容回答。

User:
问题：{question}

可用知识片段：
[1] {chunk_text_1}
来源：{title_1} / {source_file_1}

[2] {chunk_text_2}
来源：{title_2} / {source_file_2}

要求：
1. 只能基于上述知识片段回答。
2. 如果知识不足，请回答“当前知识库中未找到相关内容”。
3. 回答要结构化。
4. 必须列出引用来源。
```

输出：

```json
{
  "status": "answered",
  "answer": "根据当前知识库，差旅报销需要提交以下材料：...",
  "sources": [
    {
      "knowledge_id": "xxx",
      "chunk_id": "xxx",
      "title": "差旅报销材料要求",
      "source_file": "财务报销制度.pdf",
      "score": 0.82
    }
  ]
}
```

### 12.4 无答案策略

当满足任一条件时返回无答案：

```text
1. 检索结果为空。
2. Top1 相似度低于阈值。
3. 召回 chunk 全部来自不可用知识。
4. 知识库已停用。
```

返回：

```json
{
  "status": "no_answer",
  "answer": "当前知识库中未找到相关内容，建议更换关键词或联系知识管理员补充知识。",
  "sources": []
}
```

## 13. 异步任务设计

### 13.1 为什么需要异步任务

文档解析、文本切片、embedding 生成、索引重建都可能耗时较长。如果全部放在 HTTP 请求中同步执行，用户上传文档后页面会长时间等待，接口也容易超时。因此系统采用 Celery + Redis 将耗时任务异步化。

### 13.2 任务队列划分

```text
document_queue
- 文档解析任务

embedding_queue
- embedding 生成任务

index_queue
- 索引重建任务

maintenance_queue
- 清理任务
```

### 13.3 文档解析任务状态流转

```text
uploaded
→ parsing
→ parsed
→ imported
```

失败时：

```text
uploaded
→ parsing
→ failed
```

### 13.4 知识发布后的索引任务

```text
管理员点击发布
→ knowledge status = available
→ 创建 embedding task
→ 删除旧 chunk
→ 重新切片
→ 生成 embedding
→ 写入 pgvector
→ 索引完成
```

## 14. 部署目录设计

项目根目录建议如下：

```text
ai-knowledge-platform/
  backend/
  frontend/
  docker/
    postgres/
      init.sql
    redis/
    nginx/
      nginx.conf
  docs/
    architecture.md
    api.md
    database.md
    rag_design.md
    demo_script.md
  scripts/
    dev_start.sh
    dev_stop.sh
    reset_db.sh
    build_all.sh
  uploads/
    .gitkeep
  docker-compose.yml
  README.md
  .env.example
  .gitignore
```

## 15. 根目录文件职责

### 15.1 `docker-compose.yml`

负责一键启动完整 Demo。

包含服务：

```text
frontend
backend
postgres
redis
celery_worker
```

可选服务：

```text
nginx
embedding_service
```

### 15.2 `.env.example`

提供环境变量模板。

包含：

```text
DATABASE_URL
REDIS_URL
JWT_SECRET_KEY
UPLOAD_DIR
BGE_M3_MODEL_PATH
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL_NAME
```

### 15.3 `README.md`

必须包含：

```text
1. 项目简介
2. 功能列表
3. 技术栈
4. 系统架构图
5. 本地启动方式
6. 环境变量说明
7. 测试账号
8. 目录结构
9. 演示流程
10. 后续规划
```

### 15.4 `docs/architecture.md`

即本文档，说明系统架构、模块职责、目录结构、技术选型和核心流程。

### 15.5 `docs/api.md`

记录接口文档。

内容：

```text
1. 接口路径
2. 请求方法
3. 请求参数
4. 响应示例
5. 错误码
```

### 15.6 `docs/database.md`

记录数据库设计。

内容：

```text
1. ER 关系
2. 表字段
3. 索引设计
4. 状态枚举
5. 数据流转关系
```

### 15.7 `docs/rag_design.md`

记录 RAG 细节。

内容：

```text
1. 文档解析
2. 文本切片
3. embedding 生成
4. pgvector 检索
5. prompt 设计
6. 引用来源回溯
7. 无答案策略
```

### 15.8 `docs/demo_script.md`

记录答辩演示脚本。

建议演示流程：

```text
1. 登录系统。
2. 创建财务报销知识库。
3. 手动创建一条知识。
4. 上传一份制度文档。
5. 查看解析出的知识草稿。
6. 发布知识。
7. 创建财务报销专家 Agent。
8. 向 Agent 提问。
9. 查看回答和引用来源。
10. 点赞或点踩。
11. 查看统计看板。
```

## 16. 开发阶段规划

### 16.1 第一阶段：基础工程骨架

目标：完成前后端基础项目和数据库连接。

任务：

```text
1. 创建 FastAPI 项目。
2. 创建 React 项目。
3. 配置 PostgreSQL + pgvector。
4. 配置 Redis。
5. 配置 Docker Compose。
6. 实现登录接口。
7. 实现基础 Layout。
8. 实现健康检查。
```

交付结果：

```text
前端能打开
后端 /docs 可访问
数据库可连接
Redis 可连接
Docker Compose 可启动
```

### 16.2 第二阶段：知识库与知识条目管理

目标：完成后台管理基础 CRUD。

任务：

```text
1. 实现知识库创建、编辑、启停、删除。
2. 实现知识条目创建、编辑、发布、停用、删除。
3. 实现分类和标签字段。
4. 实现知识列表筛选。
5. 实现知识编辑页面。
```

交付结果：

```text
管理员可以创建知识库
管理员可以录入知识
知识有草稿、可用、不可用状态
```

### 16.3 第三阶段：文档导入

目标：完成 PDF / DOCX / Markdown 解析和草稿生成。

任务：

```text
1. 实现文件上传。
2. 实现 document 记录。
3. 实现 PDF 解析。
4. 实现 DOCX 解析。
5. 实现 Markdown 解析。
6. 实现文本清洗。
7. 实现文本切分。
8. 实现草稿知识生成。
9. 实现解析状态展示。
```

交付结果：

```text
上传文档后能生成知识草稿
管理员可以编辑草稿并导入知识库
```

### 16.4 第四阶段：Embedding 与向量检索

目标：完成 bge-m3 embedding 和 pgvector 检索。

任务：

```text
1. 加载 bge-m3 模型。
2. 实现文本 embedding。
3. 实现 query embedding。
4. 设计 knowledge_chunks 表。
5. 写入 chunk embedding。
6. 实现向量检索 SQL。
7. 实现关键词检索。
8. 实现混合检索初版。
```

交付结果：

```text
用户输入问题后可以召回相关知识片段
检索结果包含标题、摘要、来源和相似度
```

### 16.5 第五阶段：Agent 问答

目标：完成 RAG 问答闭环。

任务：

```text
1. 实现 Agent 创建。
2. 实现 Agent 绑定知识库。
3. 实现 chat 接口。
4. 实现 RAG prompt。
5. 实现 LLM 调用。
6. 实现引用来源返回。
7. 实现无答案拒答。
8. 实现问答日志记录。
9. 实现前端聊天页面。
```

交付结果：

```text
用户可以选择 Agent 提问
AI 基于知识库回答
回答展示引用来源
无相关知识时不编造
```

### 16.6 第六阶段：反馈与统计

目标：完成基础数据闭环。

任务：

```text
1. 实现点赞点踩。
2. 实现问答历史。
3. 统计知识总数。
4. 统计可用知识数。
5. 统计问答次数。
6. 统计知识引用次数。
7. 展示热门知识。
8. 展示低满意回答。
```

交付结果：

```text
管理员可以看到系统使用情况
用户反馈可以被记录
后续知识优化有数据依据
```

### 16.7 第七阶段：加分能力

目标：增强项目亮点。

优先加分项：

```text
1. AI 自动提炼知识候选项。
2. 一键生成专家 Agent。
3. 无答案问题统计。
4. 简单知识热度看板。
```

暂缓加分项：

```text
1. 多模态图片理解。
2. 复杂审核流。
3. Skill 市场。
4. 知识图谱。
5. 多 Agent 协同。
```

## 17. 项目亮点设计

为了让该项目更适合写进简历，需要重点突出以下工程亮点。

### 17.1 业务闭环完整

项目不是简单 Chatbot，而是完整覆盖：

```text
知识生产
→ 知识治理
→ 知识检索
→ Agent 消费
→ 反馈统计
```

### 17.2 RAG 链路可解释

系统支持：

```text
文档解析
文本切片
embedding 生成
pgvector 检索
TopK 召回
Prompt 拼接
LLM 生成
引用来源回溯
无答案拒答
```

### 17.3 数据模型工程化

系统区分：

```text
KnowledgeBase：知识空间
KnowledgeItem：知识管理单元
KnowledgeChunk：RAG 检索单元
Agent：知识消费入口
QALog：问答与反馈闭环
```

### 17.4 异步任务合理

通过 Celery + Redis 处理文档解析和 embedding 生成，避免接口阻塞，体现后端工程能力。

### 17.5 模型与数据库可替换

系统将 embedding_service 和 llm_service 独立封装，后续可以替换：

```text
本地 bge-m3
远程 embedding API
OpenAI-compatible LLM
本地 vLLM
云厂商模型
```

### 17.6 引用来源和无答案策略

系统通过检索阈值、知识状态过滤、引用来源回溯减少幻觉，保证回答可信。

## 18. 简历项目描述建议

项目名称：

```text
企业级 AI 知识库管理与专家 Agent 问答平台
```

一句话描述：

```text
基于 FastAPI、React、PostgreSQL + pgvector 和 bge-m3 实现企业知识库管理平台，支持文档导入、知识条目治理、向量检索、RAG 问答、来源引用、用户反馈和基础统计，形成从知识生产到 Agent 消费的完整闭环。
```

技术栈描述：

```text
FastAPI / React / TypeScript / PostgreSQL / pgvector / Redis / Celery / bge-m3 / RAG / Docker
```

核心职责描述：

```text
1. 设计知识库、知识条目、知识切片、Agent、问答日志等核心数据模型，实现业务数据与向量索引统一管理。
2. 基于 bge-m3 生成知识切片 embedding，并使用 PostgreSQL + pgvector 实现语义检索。
3. 构建 RAG 问答链路，实现问题向量化、TopK 召回、Prompt 拼接、大模型生成和引用来源回溯。
4. 使用 Celery + Redis 将文档解析、文本切分、embedding 生成等耗时任务异步化，提高系统响应体验。
5. 实现问答日志、点赞点踩、知识引用次数和热门知识统计，为知识优化提供数据基础。
```

## 19. 首期验收标准

首期完成后，系统应满足以下标准：

```text
1. 可以本地通过 Docker Compose 启动。
2. 管理员可以登录系统。
3. 管理员可以创建知识库。
4. 管理员可以创建、编辑、发布、停用、删除知识。
5. 管理员可以上传 PDF / DOCX / Markdown 文档。
6. 系统可以解析文档并生成知识草稿。
7. 系统可以对可用知识生成 bge-m3 embedding。
8. 用户可以通过关键词检索知识。
9. 用户可以通过语义检索知识。
10. 用户可以创建或选择专家 Agent。
11. Agent 可以基于知识库回答问题。
12. 回答可以展示引用来源。
13. 无相关知识时系统不编造答案。
14. 用户可以点赞或点踩回答。
15. 管理员可以查看基础统计。
16. README、架构文档、接口文档完整。
```

## 20. 后续扩展方向

MVP 完成后，可以继续扩展：

```text
1. AI 自动提炼知识候选项。
2. 高频无答案问题聚类。
3. 低满意回答分析。
4. 知识版本管理。
5. 知识冲突检测。
6. 过期知识提醒。
7. 多知识库联合问答。
8. Skill 调用接口。
9. 权限过滤增强。
10. OCR 和表格解析。
```

## 21.前端样式参考

![image-20260616112418058](C:\Users\17624\AppData\Roaming\Typora\typora-user-images\image-20260616112418058.png)

![image-20260616112432899](C:\Users\17624\AppData\Roaming\Typora\typora-user-images\image-20260616112432899.png)

![image-20260616112456264](C:\Users\17624\AppData\Roaming\Typora\typora-user-images\image-20260616112456264.png)