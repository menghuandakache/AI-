"""RAG service - orchestrates retrieval and answer generation."""
import json
import os
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.repositories.qa_repo import QARepository

settings = get_settings()


class RAGService:
    """Handles the complete RAG pipeline: retrieve → construct prompt → generate → log."""

    def __init__(self, db: Session):
        self.db = db
        self.retrieval = RetrievalService(db)
        self.qa_repo = QARepository(db)

    def _get_model_config(self, llm_config_id: str = None) -> dict | None:
        """Fetch model config from DB if an ID is given."""
        if not llm_config_id:
            # Try default
            from app.repositories.model_config_repo import ModelConfigRepository
            repo = ModelConfigRepository(self.db)
            cfg = repo.get_default()
            return self._cfg_to_dict(cfg) if cfg else None
        from app.repositories.model_config_repo import ModelConfigRepository
        repo = ModelConfigRepository(self.db)
        cfg = repo.get_by_id(llm_config_id)
        return self._cfg_to_dict(cfg) if cfg else None

    def _cfg_to_dict(self, cfg) -> dict:
        return {"base_url": cfg.base_url, "api_key": cfg.api_key, "model_name": cfg.model_name}

    def answer(self, question: str, kb_id: str = None, agent_id: str = None,
               user_id: str = None, citation_policy: str = "required",
               llm_config_id: str = None, conversation_id: str = None) -> dict:
        """Run the full RAG pipeline and return answer with sources."""
        import time
        start_time = time.time()

        # Step 1: Retrieve relevant knowledge chunks
        retrieved = self.retrieval.hybrid_search(question, kb_id=kb_id)
        if not retrieved:
            # No relevant knowledge found
            answer = "当前知识库中未找到相关内容，建议更换关键词或联系知识管理员补充知识。"
            qa_log = self._log_qa(user_id, agent_id, kb_id, question, answer,
                                  [], [], "no_answer", start_time,
                                  conversation_id=conversation_id)
            return {
                "id": str(qa_log.id),
                "status": "no_answer",
                "answer": answer,
                "sources": [],
                "question": question,
                "created_at": qa_log.created_at,
            }

        # Step 2: Construct RAG prompt
        system_prompt = self._load_prompt("rag_answer_prompt.txt")
        context_parts = []
        sources = []

        for i, r in enumerate(retrieved):
            context_parts.append(
                f"[{i + 1}] {r['chunk_text']}\n"
                f"来源：{r['title']}"
                f"{' / ' + r.get('source_file', '') if r.get('source_file') else ''}"
            )
            sources.append({
                "knowledge_id": r["knowledge_id"],
                "chunk_id": r.get("chunk_id"),
                "title": r["title"],
                "source_file": r.get("source_file", ""),
                "score": r["score"],
            })

        context = "\n\n".join(context_parts)
        user_message = f"""问题：{question}

可用知识片段：
{context}

要求：
1. 只能基于上述知识片段回答。
2. 如果知识不足，请回答"当前知识库中未找到相关内容"。
3. 回答要结构化。
4. 必须列出引用来源。"""

        # Step 3: Call LLM with dynamic model config
        model_cfg = self._get_model_config(llm_config_id)
        llm = LLMService(model_cfg)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = llm.chat(messages, stream=False)
            answer = response.choices[0].message.content
            status = "answered"
        except Exception as e:
            answer = f"模型调用失败：{str(e)}"
            status = "failed"

        # Step 4: Log QA
        chunk_ids = [s.get("chunk_id") for s in sources if s.get("chunk_id")]
        knowledge_ids = [s["knowledge_id"] for s in sources]
        qa_log = self._log_qa(
            user_id, agent_id, kb_id, question, answer,
            chunk_ids, knowledge_ids, status, start_time,
            conversation_id=conversation_id,
        )

        return {
            "id": str(qa_log.id),
            "status": status,
            "answer": answer,
            "sources": sources,
            "question": question,
            "created_at": qa_log.created_at,
        }

    def answer_stream(self, question: str, kb_id: str = None, agent_id: str = None,
                      user_id: str = None, llm_config_id: str = None, conversation_id: str = None):
        """Stream the RAG answer via SSE."""
        import time
        start_time = time.time()

        # Retrieve
        retrieved = self.retrieval.hybrid_search(question, kb_id=kb_id)

        if not retrieved:
            no_answer = "当前知识库中未找到相关内容，建议更换关键词或联系知识管理员补充知识。"
            yield f"data: {json.dumps({'status': 'no_answer', 'answer': no_answer, 'sources': []})}\n\n"
            yield "data: [DONE]\n\n"
            return

        # Build context
        system_prompt = self._load_prompt("rag_answer_prompt.txt")
        context_parts = []
        sources = []

        for i, r in enumerate(retrieved):
            context_parts.append(
                f"[{i + 1}] {r['chunk_text']}\n"
                f"来源：{r['title']}"
                f"{' / ' + r.get('source_file', '') if r.get('source_file') else ''}"
            )
            sources.append({
                "knowledge_id": r["knowledge_id"],
                "chunk_id": r.get("chunk_id"),
                "title": r["title"],
                "source_file": r.get("source_file", ""),
                "score": r["score"],
            })

        context = "\n\n".join(context_parts)
        user_message = f"""问题：{question}

可用知识片段：
{context}

要求：
1. 只能基于上述知识片段回答。
2. 如果知识不足，请回答"当前知识库中未找到相关内容"。
3. 回答要结构化。
4. 必须列出引用来源。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Stream LLM response with dynamic model
        model_cfg_stream = self._get_model_config(llm_config_id)
        llm_stream = LLMService(model_cfg_stream)
        yield f"data: {json.dumps({'status': 'streaming', 'sources': sources})}\n\n"

        full_answer = ""
        try:
            for token in llm_stream.chat_stream(messages):
                full_answer += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        # Log QA
        chunk_ids = [s.get("chunk_id") for s in sources if s.get("chunk_id")]
        knowledge_ids = [s["knowledge_id"] for s in sources]
        self._log_qa(user_id, agent_id, kb_id, question, full_answer,
                     chunk_ids, knowledge_ids, "answered", start_time,
                     conversation_id=conversation_id)

        yield "data: [DONE]\n\n"

    def _log_qa(self, user_id, agent_id, kb_id, question, answer,
                chunk_ids, knowledge_ids, status, start_time,
                conversation_id=None) -> any:
        import time
        latency_ms = int((time.time() - start_time) * 1000)
        return self.qa_repo.create(
            user_id=user_id,
            agent_id=agent_id,
            kb_id=kb_id,
            question=question,
            answer=answer,
            retrieved_chunk_ids=chunk_ids,
            cited_knowledge_ids=knowledge_ids,
            status=status,
            latency_ms=latency_ms,
            conversation_id=conversation_id,
        )

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt template from the prompts directory."""
        prompt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        file_path = os.path.join(prompt_dir, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "你是企业内部知识库问答助手。你必须严格基于给定知识片段回答问题。"
