from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, SQLModel

class TodoBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    tags: Optional[str] = Field(default="[]", description="JSON‑encoded list of strings")

class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TodoCreate(TodoBase):
    tags: Optional[List[str]] = []

class TodoRead(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[str]

class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None
