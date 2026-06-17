# RAG 检索问答设计文档

## 1. 文档解析

### 支持的格式
- PDF：使用 PyMuPDF 提取文本
- DOCX：使用 python-docx 提取段落
- Markdown：使用 markdown 库转换为 HTML 后提取纯文本

### 解析流程
```
上传文档 → 保存文件 → 创建 document 记录 → 解析文本 → 清洗 → 切分 → 生成草稿
```

## 2. 文本清洗

由 `text_cleaner.py` 提供：
- 去除多余空格和空白行
- 去除页眉页脚常见模式
- 统一中英文标点
- 过滤控制字符
- 去除页码和水印

## 3. 文本切片

### 切片策略
- **chunk_size**: 800-1000 中文字符
- **chunk_overlap**: 100-150 中文字符

### 切片方式
1. 按标题切分（#、##、### 等 Markdown 标题）
2. 按段落切分（空行分隔）
3. 按固定长度切分（兜底策略）

### metadata 示例
```json
{
  "knowledge_id": "uuid",
  "kb_id": "uuid",
  "title": "差旅报销材料要求",
  "category": "制度规范",
  "tags": ["报销", "差旅"],
  "source_type": "document",
  "source_file": "财务报销制度.pdf",
  "page": 3,
  "section": "第三章 报销材料"
}
```

## 4. Embedding 生成

### 模型配置
- 模型：bge-m3 (BAAI/bge-m3)
- 维度：1024
- 设备：CPU / GPU 可配置
- 批量大小：32（可配置）

### 流程
```
知识发布 → 删除旧 chunk → 重新切分 → 批量生成 embedding → 写入 pgvector
```

## 5. pgvector 检索

### 相似度计算
- 使用 pgvector 的余弦距离 `<=>` 运算符
- 转换公式：similarity = 1 - cosine_distance

### 向量检索 SQL
```sql
SELECT kc.*, 1 - (kc.embedding <=> :query_embedding::vector) AS similarity_score
FROM knowledge_chunks kc
JOIN knowledge_items ki ON kc.knowledge_id = ki.id
JOIN knowledge_bases kb ON kc.kb_id = kb.id
WHERE ki.status = 'available'
  AND kb.status = 'enabled'
  AND 1 - (kc.embedding <=> :query_embedding::vector) > :threshold
ORDER BY similarity_score DESC
LIMIT :top_k
```

## 6. 检索策略

### MVP 混合检索
1. 使用 bge-m3 生成 question embedding
2. 使用 pgvector 向量检索 TopK chunk
3. 使用 PostgreSQL ILIKE 做关键词检索
4. 合并两路结果
5. 按 KB、状态、相似度阈值过滤
6. 去重后按综合分数排序
7. 取 Top 3 - Top 5 进入 RAG prompt

## 7. RAG Prompt 设计

### System Prompt
```
你是企业内部知识库问答助手。
你必须严格基于给定知识片段回答问题。
如果知识片段不足以回答，请明确说明当前知识库中未找到相关内容。
回答应结构化，优先使用条目、步骤和注意事项。
回答结尾必须列出引用来源。
```

### User Message
```
问题：{question}

可用知识片段：
[1] {chunk_text_1}
来源：{title_1} / {source_file_1}

[2] {chunk_text_2}
来源：{title_2} / {source_file_2}

要求：
1. 只能基于上述知识片段回答。
2. 如果知识不足，请回答"当前知识库中未找到相关内容"。
3. 回答要结构化。
4. 必须列出引用来源。
```

## 8. 引用来源回溯

### 回溯链路
```
chunk → knowledge_item → document → 原始文件
```

### 引用信息包含
- knowledge_id (知识条目 ID)
- chunk_id (切片 ID)
- title (知识标题)
- source_file (来源文件)
- score (相似度分数)

## 9. 无答案策略

触发条件：
1. 检索结果为空
2. Top1 相似度低于阈值（默认 0.5）
3. 召回 chunk 全部来自不可用知识
4. 知识库已停用

返回：
```json
{
  "status": "no_answer",
  "answer": "当前知识库中未找到相关内容，建议更换关键词或联系知识管理员补充知识。",
  "sources": []
}
```

## 10. 流式输出

问答支持 SSE (Server-Sent Events) 流式输出：
- 先返回 sources（引用来源）
- 逐 token 推送 LLM 生成内容
- 最后发送 [DONE] 标记
- 前端使用 fetch + ReadableStream 接收
