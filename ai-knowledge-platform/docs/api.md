# API 接口文档

## 基础信息

- 基础路径：`/api`
- 认证方式：Bearer Token (JWT)
- 文档地址：`/docs` (Swagger UI)

## 1. 认证接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/auth/login | 用户登录 | 否 |
| GET | /api/auth/me | 获取当前用户信息 | 是 |
| POST | /api/auth/logout | 退出登录 | 是 |

### POST /api/auth/login

请求：
```json
{
  "username": "admin",
  "password": "admin123"
}
```

响应：
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "username": "admin",
  "role": "admin",
  "user_id": "uuid"
}
```

## 2. 知识库接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/kb | 查询知识库列表 | 登录用户 |
| POST | /api/kb | 创建知识库 | admin |
| GET | /api/kb/{kb_id} | 查询知识库详情 | 登录用户 |
| PUT | /api/kb/{kb_id} | 更新知识库 | admin |
| DELETE | /api/kb/{kb_id} | 删除知识库 | admin |
| PATCH | /api/kb/{kb_id}/status | 修改状态 | admin |
| GET | /api/kb/{kb_id}/overview | 获取概览 | 登录用户 |

### POST /api/kb

请求：
```json
{
  "name": "财务报销知识库",
  "description": "公司财务报销相关制度",
  "domain": "Finance"
}
```

### GET /api/kb

查询参数：page, page_size, domain, status, keyword

响应：
```json
{
  "items": [...],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

## 3. 知识条目接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/knowledge | 查询知识列表 | 登录用户 |
| POST | /api/knowledge | 创建知识 | admin |
| GET | /api/knowledge/{id} | 查询知识详情 | 登录用户 |
| PUT | /api/knowledge/{id} | 更新知识 | admin |
| DELETE | /api/knowledge/{id} | 删除知识 | admin |
| PATCH | /api/knowledge/{id}/publish | 发布知识 | admin |
| PATCH | /api/knowledge/{id}/disable | 停用知识 | admin |
| GET | /api/knowledge/{id}/chunks | 查询切片 | 登录用户 |

### POST /api/knowledge

请求：
```json
{
  "kb_id": "uuid",
  "title": "差旅报销材料要求",
  "content": "员工差旅报销需提交...",
  "category": "制度规范",
  "tags": ["报销", "差旅"],
  "status": "draft"
}
```

### GET /api/knowledge

查询参数：kb_id, keyword, category, tags, status, page, page_size

## 4. 文档导入接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/documents/upload | 上传文档 | admin |
| POST | /api/documents/{id}/parse | 解析文档 | admin |
| GET | /api/documents/{id}/status | 查询状态 | 登录用户 |
| GET | /api/documents/{id}/drafts | 查询草稿 | 登录用户 |
| POST | /api/documents/{id}/import | 导入知识 | admin |

### POST /api/documents/upload

表单参数：kb_id (string), file (file)

### POST /api/documents/{id}/parse

响应：
```json
{
  "id": "uuid",
  "parse_status": "parsed",
  "message": "Document parsed, 5 knowledge drafts created",
  "draft_ids": ["..."]
}
```

## 5. 检索接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/search/keyword | 关键词检索 | 登录用户 |
| POST | /api/search/semantic | 语义检索 | 登录用户 |
| POST | /api/search/hybrid | 混合检索 | 登录用户 |

### POST /api/search/hybrid

请求：
```json
{
  "query": "差旅报销需要哪些材料",
  "kb_id": "uuid",
  "top_k": 5
}
```

响应：
```json
{
  "items": [
    {
      "knowledge_id": "uuid",
      "chunk_id": "uuid",
      "title": "差旅报销材料要求",
      "chunk_text": "...",
      "category": "制度规范",
      "tags": ["报销"],
      "score": 0.85,
      "kb_name": "财务报销知识库"
    }
  ],
  "total": 3,
  "query": "差旅报销需要哪些材料"
}
```

## 6. Agent 接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/agents | Agent 列表 | 登录用户 |
| POST | /api/agents | 创建 Agent | admin |
| GET | /api/agents/{id} | Agent 详情 | 登录用户 |
| PUT | /api/agents/{id} | 更新配置 | admin |
| PATCH | /api/agents/{id}/disable | 停用 | admin |
| POST | /api/agents/generate | 一键生成 | admin |
| POST | /api/agents/{id}/chat | 问答 | 登录用户 |
| POST | /api/agents/{id}/chat/stream | 流式问答 | 登录用户 |

### POST /api/agents/{id}/chat

请求：
```json
{
  "question": "差旅报销需要哪些材料？"
}
```

响应：
```json
{
  "id": "qa-log-uuid",
  "status": "answered",
  "answer": "根据当前知识库...",
  "sources": [
    {
      "knowledge_id": "uuid",
      "chunk_id": "uuid",
      "title": "差旅报销材料要求",
      "source_file": "财务报销制度.pdf",
      "score": 0.82
    }
  ]
}
```

## 7. 反馈接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/feedback | 提交反馈 | 登录用户 |
| GET | /api/feedback/qa/{qa_log_id} | 查询反馈 | 登录用户 |

### POST /api/feedback

请求：
```json
{
  "qa_log_id": "uuid",
  "feedback_type": "like",
  "feedback_reason": "回答准确"
}
```

## 8. 统计接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/stats/overview | 总览统计 | 登录用户 |
| GET | /api/stats/hot-knowledge | 热门知识 | 登录用户 |
| GET | /api/stats/feedback | 反馈统计 | 登录用户 |
| GET | /api/stats/no-answer | 无答案问题 | 登录用户 |
| GET | /api/stats/recent-qa | 最近问答 | 登录用户 |

## 错误码说明

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| AUTH_ERROR | 401 | 认证失败 |
| NOT_FOUND | 404 | 资源不存在 |
| PERMISSION_DENIED | 403 | 权限不足 |
| VALIDATION_ERROR | 422 | 参数校验失败 |
| DUPLICATE_RESOURCE | 409 | 资源重复 |
| FILE_PARSE_ERROR | 400 | 文件解析失败 |
| MODEL_CALL_ERROR | 500 | 模型调用失败 |
| INTERNAL_ERROR | 500 | 内部服务错误 |
