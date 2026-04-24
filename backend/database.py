import sqlite3
from fastapi import FastAPI

# SQLite database file name
DB_FILE = "todos.db"

async def connect(app: FastAPI) -> None:
    """Create a SQLite connection, store it in app.state, and ensure the todos table exists."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    app.state.db = conn
    # Create the todos table if it doesn't exist
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.commit()

async def disconnect(app: FastAPI) -> None:
    """Close the SQLite connection stored in app.state."""
    conn: sqlite3.Connection = app.state.db
    conn.close()
