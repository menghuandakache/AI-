# 数据库设计文档

## 1. ER 关系

```
users (用户)
  │
  ├── knowledge_bases (知识库) ── knowledge_items (知识条目) ── knowledge_chunks (知识切片)
  │                                      │
  ├── agents (专家Agent) ────────────────┘
  │
  ├── documents (文档)
  │
  ├── qa_logs (问答日志) ── feedbacks (反馈)
  │
  └── audit_logs (审计日志)
```

## 2. 表设计

### 2.1 users (用户表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| username | varchar(100) | 用户名，唯一 |
| password_hash | varchar(255) | 密码哈希 |
| email | varchar(255) | 邮箱 |
| role | varchar(50) | 角色：admin / knowledge_admin / user |
| status | varchar(50) | 状态：active / inactive |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.2 knowledge_bases (知识库表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| name | varchar(200) | 知识库名称 |
| description | text | 描述 |
| domain | varchar(100) | 业务域 |
| owner_id | uuid | 负责人 |
| status | varchar(50) | enabled / disabled / deleted |
| created_by | uuid | 创建人 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.3 knowledge_items (知识条目表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| kb_id | uuid FK | 所属知识库 |
| title | varchar(500) | 标题 |
| content | text | 正文 |
| summary | text | 摘要 |
| category | varchar(100) | 分类 |
| tags | jsonb | 标签数组 |
| status | varchar(50) | draft / available / unavailable / deleted |
| source_type | varchar(50) | manual / document / ai_extract / dialogue |
| source_file_id | uuid | 来源文件 |
| created_by | uuid | 创建人 |
| updated_by | uuid | 更新人 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |
| deleted_at | timestamp | 软删除时间 |

### 2.4 knowledge_chunks (知识切片表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| knowledge_id | uuid FK | 所属知识条目 |
| kb_id | uuid | 所属知识库 (冗余) |
| chunk_text | text | 切片文本 |
| chunk_index | integer | 切片序号 |
| embedding | vector(1024) | bge-m3 向量 (pgvector) |
| metadata | jsonb | 来源信息 |
| token_count | integer | Token 数量 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.5 documents (文档表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| kb_id | uuid FK | 所属知识库 |
| filename | varchar(500) | 文件名 |
| file_path | varchar(1000) | 存储路径 |
| file_type | varchar(50) | pdf / docx / md |
| file_size | bigint | 文件大小 |
| parse_status | varchar(50) | uploaded / parsing / parsed / failed / imported |
| parse_error | text | 错误信息 |
| created_by | uuid | 上传人 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.6 agents (Agent 表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| name | varchar(200) | Agent 名称 |
| description | text | 描述 |
| kb_ids | jsonb | 绑定知识库列表 |
| prompt_config | text | 提示词配置 |
| answer_style | varchar(50) | 回答风格 |
| citation_policy | varchar(50) | 引用策略 |
| no_answer_policy | varchar(50) | 无答案策略 |
| status | varchar(50) | enabled / disabled |
| created_by | uuid | 创建人 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.7 qa_logs (问答日志表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| user_id | uuid | 提问者 |
| agent_id | uuid | Agent ID |
| kb_id | uuid | 知识库 ID |
| question | text | 用户问题 |
| answer | text | AI 回答 |
| retrieved_chunk_ids | jsonb | 召回 chunk 列表 |
| cited_knowledge_ids | jsonb | 引用知识列表 |
| status | varchar(50) | answered / no_answer / failed |
| feedback | varchar(50) | like / dislike / none |
| latency_ms | integer | 响应耗时(ms) |
| created_at | timestamp | 创建时间 |

### 2.8 feedbacks (反馈表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| qa_log_id | uuid | 问答日志 ID |
| user_id | uuid | 反馈者 |
| feedback_type | varchar(50) | like / dislike |
| feedback_reason | text | 反馈原因 |
| created_at | timestamp | 创建时间 |

### 2.9 audit_logs (审计日志表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| user_id | uuid | 操作人 |
| action | varchar(100) | 操作类型 |
| resource_type | varchar(100) | 资源类型 |
| resource_id | uuid | 资源 ID |
| detail | jsonb | 操作详情 |
| created_at | timestamp | 创建时间 |

## 3. 索引设计

```sql
-- knowledge_bases
CREATE INDEX idx_kb_status ON knowledge_bases(status);
CREATE INDEX idx_kb_domain ON knowledge_bases(domain);

-- knowledge_items
CREATE INDEX idx_knowledge_kb_id ON knowledge_items(kb_id);
CREATE INDEX idx_knowledge_status ON knowledge_items(status);
CREATE INDEX idx_knowledge_category ON knowledge_items(category);
CREATE INDEX idx_knowledge_created_at ON knowledge_items(created_at);

-- knowledge_chunks
CREATE INDEX idx_chunk_knowledge_id ON knowledge_chunks(knowledge_id);
CREATE INDEX idx_chunk_kb_id ON knowledge_chunks(kb_id);
-- pgvector IVFFlat index for similarity search
CREATE INDEX idx_chunk_embedding_ivfflat ON knowledge_chunks
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

## 4. 状态枚举

### 知识库状态
- `enabled` - 启用（可参与问答）
- `disabled` - 停用（不参与问答）
- `deleted` - 已删除（软删除）

### 知识条目状态
- `draft` - 草稿（不可检索）
- `available` - 可用（可检索、可问答）
- `unavailable` - 不可用（暂不可用）
- `deleted` - 已删除（软删除）

### 文档解析状态
- `uploaded` - 已上传
- `parsing` - 解析中
- `parsed` - 解析完成
- `failed` - 解析失败
- `imported` - 已导入

## 5. 数据流转关系

1. `knowledge_bases` ← `knowledge_items` ← `knowledge_chunks`
2. `knowledge_items.status = available` 时才能被检索
3. `knowledge_bases.status = enabled` 时其知识才能被检索
4. `knowledge_chunks` 是 RAG 检索的基本单元，从 chunk 回溯到 knowledge_item
5. `qa_logs` 记录每次问答的召回和引用信息
