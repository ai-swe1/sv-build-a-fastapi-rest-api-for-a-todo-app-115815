from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class TodoCreateSchema(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = False
    tags: Optional[List[str]] = []

class TodoReadSchema(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TodoUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None
