"""Initialize database - create all tables."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import (
    User, KnowledgeBase, KnowledgeItem, KnowledgeChunk,
    Document, Agent, QALog, Feedback, AuditLog,
)


def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_database()
