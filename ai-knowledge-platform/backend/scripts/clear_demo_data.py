"""Script to clear all demo/seed data."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import (
    User, KnowledgeBase, KnowledgeItem, KnowledgeChunk,
    Document, Agent, QALog, Feedback, AuditLog,
)


def clear_all():
    """Clear all data from database."""
    db = SessionLocal()
    try:
        tables = [Feedback, AuditLog, QALog, KnowledgeChunk, KnowledgeItem,
                  Document, Agent, KnowledgeBase, User]

        for table in tables:
            count = db.query(table).delete()
            print(f"Cleared {count} rows from {table.__tablename__}")

        db.commit()
        print("All data cleared successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    confirm = input("This will delete ALL data. Type 'yes' to confirm: ")
    if confirm == "yes":
        clear_all()
    else:
        print("Aborted.")
