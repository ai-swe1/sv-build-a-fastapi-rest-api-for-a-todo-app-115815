import json
import datetime
from typing import List, Optional
from backend import database
from backend.models import Todo

# Helper to convert DB row to TodoRead dict
def _row_to_dict(row: aiosqlite.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
        "tags": json.loads(row["tags"]),
        "created_at": datetime.datetime.fromisoformat(row["created_at"]),
        "updated_at": datetime.datetime.fromisoformat(row["updated_at"]),
    }

async def create_todo(data: dict) -> dict:
    try:
        conn = await database.get_connection()
        now = datetime.datetime.utcnow().isoformat()
        tags_json = json.dumps(data.get("tags", []))
        cursor = await conn.execute(
            """
            INSERT INTO todo (title, description, completed, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data.get("description"),
                int(data.get("completed", False)),
                tags_json,
                now,
                now,
            ),
        )
        await conn.commit()
        todo_id = cursor.lastrowid
        row = await conn.execute_fetchone("SELECT * FROM todo WHERE id = ?", (todo_id,))
        return _row_to_dict(row)
    except Exception as e:
        raise e

async def get_todo(todo_id: int) -> Optional[dict]:
    try:
        conn = await database.get_connection()
        row = await conn.execute_fetchone("SELECT * FROM todo WHERE id = ?", (todo_id,))
        if row is None:
            return None
        return _row_to_dict(row)
    except Exception as e:
        raise e

async def list_todos(skip: int = 0, limit: int = 100) -> List[dict]:
    try:
        conn = await database.get_connection()
        rows = await conn.execute_fetchall(
            "SELECT * FROM todo ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, skip)
        )
        return [_row_to_dict(r) for r in rows]
    except Exception as e:
        raise e

async def update_todo(todo_id: int, data: dict) -> Optional[dict]:
    try:
        conn = await database.get_connection()
        existing = await get_todo(todo_id)
        if not existing:
            return None
        # Prepare updated fields
        updated_fields = {
            "title": data.get("title", existing["title"]),
            "description": data.get("description", existing["description"]),
            "completed": int(data.get("completed", existing["completed"])),
            "tags": json.dumps(data.get("tags", existing["tags"])) ,
            "updated_at": datetime.datetime.utcnow().isoformat(),
        }
        await conn.execute(
            """
            UPDATE todo SET title = ?, description = ?, completed = ?, tags = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                updated_fields["title"],
                updated_fields["description"],
                updated_fields["completed"],
                updated_fields["tags"],
                updated_fields["updated_at"],
                todo_id,
            ),
        )
        await conn.commit()
        row = await conn.execute_fetchone("SELECT * FROM todo WHERE id = ?", (todo_id,))
        return _row_to_dict(row)
    except Exception as e:
        raise e

async def delete_todo(todo_id: int) -> bool:
    try:
        conn = await database.get_connection()
        await conn.execute("DELETE FROM todo WHERE id = ?", (todo_id,))
        await conn.commit()
        return True
    except Exception as e:
        raise e
