"""Seed demo data for development."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.config import get_settings
from app.repositories.user_repo import UserRepository
from app.repositories.kb_repo import KnowledgeBaseRepository
from app.repositories.knowledge_repo import KnowledgeRepository
from app.repositories.agent_repo import AgentRepository

settings = get_settings()


def seed():
    """Seed initial demo data."""
    db = SessionLocal()
    try:
        print("Seeding demo data...")

        # Create admin
        user_repo = UserRepository(db)
        admin = user_repo.get_by_username(settings.DEFAULT_ADMIN_USERNAME)
        if not admin:
            admin = user_repo.create(
                username=settings.DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                email=settings.DEFAULT_ADMIN_EMAIL,
                role="admin",
            )
            print("Created admin user")

        admin_id = str(admin.id)

        # Create demo user
        demo_user = user_repo.get_by_username("user")
        if not demo_user:
            demo_user = user_repo.create(
                username="user",
                password_hash=hash_password("user123"),
                email="user@example.com",
                role="user",
            )
            print("Created demo user")

        # Create sample knowledge base
        kb_repo = KnowledgeBaseRepository(db)
        kb = kb_repo.create(
            name="财务报销知识库",
            description="公司财务报销相关制度、流程和FAQ",
            domain="Finance",
            owner_id=admin_id,
            created_by=admin_id,
        )
        print(f"Created knowledge base: {kb.name}")

        # Create sample knowledge items
        knowledge_repo = KnowledgeRepository(db)
        sample_knowledge = [
            {
                "title": "差旅报销材料要求",
                "content": "员工差旅报销需提交以下材料：\n1. 出差申请单（需部门负责人审批）\n2. 交通票据（机票、火车票、出租车发票）\n3. 住宿发票（需开具公司抬头）\n4. 出差行程单\n5. 费用明细表\n\n注意事项：\n- 所有票据需为原件，电子发票需打印\n- 住宿超过500元/晚需提前申请\n- 境外出差需额外提交汇率换算表",
                "category": "制度规范",
                "tags": ["报销", "差旅"],
            },
            {
                "title": "采购审批流程说明",
                "content": "公司采购审批流程分为以下步骤：\n1. 提交采购申请单\n   - 金额 < 5000元：部门经理审批\n   - 金额 5000-50000元：部门经理 + 财务总监审批\n   - 金额 > 50000元：部门经理 + 财务总监 + CEO审批\n2. 供应商选择（至少三家比价）\n3. 合同签订（法务审核）\n4. 货物验收\n5. 付款申请",
                "category": "业务流程",
                "tags": ["采购", "审批"],
            },
            {
                "title": "常见报销问题FAQ",
                "content": "Q: 报销单提交后多久能到账？\nA: 财务审核通过后3-5个工作日内到账。\n\nQ: 电子发票是否可以报销？\nA: 可以，需打印后附在报销单后。\n\nQ: 加班餐费是否可以报销？\nA: 工作日加班超过20:00可报销餐费，上限50元/人。\n\nQ: 报销单填错了怎么办？\nA: 可在系统中撤回修改，或联系财务退回。",
                "category": "常见问题FAQ",
                "tags": ["报销", "FAQ"],
            },
        ]

        for item in sample_knowledge:
            knowledge = knowledge_repo.create(
                kb_id=str(kb.id),
                title=item["title"],
                content=item["content"],
                category=item["category"],
                tags=item["tags"],
                status="available",
                source_type="manual",
                created_by=admin_id,
            )
            print(f"Created knowledge: {knowledge.title}")

        # Create sample Agent
        agent_repo = AgentRepository(db)
        agent = agent_repo.create(
            name="财务报销专家助手",
            description="基于财务报销知识库的智能问答助手，可回答报销流程、审批条件、材料要求等各类问题。",
            kb_ids=[str(kb.id)],
            prompt_config="你是财务报销专家助手，专注于回答公司财务报销相关问题。请基于知识库内容提供准确、结构化的回答。",
            answer_style="detailed",
            citation_policy="required",
            no_answer_policy="prompt",
            created_by=admin_id,
        )
        print(f"Created agent: {agent.name}")

        print("\n=== Demo data seeded successfully! ===")
        print(f"\nTest accounts:")
        print(f"  Admin: {settings.DEFAULT_ADMIN_USERNAME} / {settings.DEFAULT_ADMIN_PASSWORD}")
        print(f"  User:  user / user123")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
