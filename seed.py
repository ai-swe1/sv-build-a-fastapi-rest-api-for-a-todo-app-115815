"""Seed script for the Todo application.

Run with:
    python seed.py
"""

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Todo

# Adjust the DATABASE_URL to match your environment
DATABASE_URL = "sqlite:///todos.db"  # For quick local testing; replace with Postgres/MySQL URL as needed

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

def seed():
    Base.metadata.create_all(engine)  # Ensure tables exist (idempotent)
    session = Session()
    try:
        # Check if data already exists to keep seed idempotent
        existing = session.query(Todo).first()
        if existing:
            print("Seed data already present; skipping.")
            return

        sample_todos = [
            Todo(
                title="Buy groceries",
                description="Milk, Bread, Eggs, Cheese",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Todo(
                title="Read a book",
                description="Finish reading 'Clean Architecture'",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Todo(
                title="Walk the dog",
                description=None,
                completed=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]
        session.add_all(sample_todos)
        session.commit()
        print("Seed data inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error during seeding: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed()
