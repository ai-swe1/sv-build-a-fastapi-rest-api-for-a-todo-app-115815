from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

router = APIRouter(prefix="/todos", tags=["todos"])

# ---------- Pydantic Schemas ----------
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: Optional[bool] = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoOut(TodoBase):
    id: int

# ---------- Helper ----------
def get_db(request: Request) -> sqlite3.Connection:
    return request.app.state.db

# ---------- Routes ----------
@router.post("/", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate, request: Request):
    try:
        db = get_db(request)
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
            (todo.title, todo.description, int(todo.completed or False)),
        )
        db.commit()
        todo_id = cursor.lastrowid
        return TodoOut(id=todo_id, **todo.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[TodoOut])
async def list_todos(request: Request):
    try:
        db = get_db(request)
        rows = db.execute("SELECT * FROM todos").fetchall()
        return [
            TodoOut(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                completed=bool(row["completed"]),
            )
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{todo_id}", response_model=TodoOut)
async def get_todo(todo_id: int, request: Request):
    try:
        db = get_db(request)
        row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Todo not found")
        return TodoOut(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            completed=bool(row["completed"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{todo_id}", response_model=TodoOut)
async def update_todo(todo_id: int, todo: TodoUpdate, request: Request):
    try:
        db = get_db(request)
        existing = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Determine new values, falling back to existing ones
        new_title = todo.title if todo.title is not None else existing["title"]
        new_description = (
            todo.description if todo.description is not None else existing["description"]
        )
        new_completed = (
            int(todo.completed) if todo.completed is not None else existing["completed"]
        )

        db.execute(
            "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
            (new_title, new_description, new_completed, todo_id),
        )
        db.commit()

        return TodoOut(
            id=todo_id,
            title=new_title,
            description=new_description,
            completed=bool(new_completed),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, request: Request):
    try:
        db = get_db(request)
        cursor = db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
