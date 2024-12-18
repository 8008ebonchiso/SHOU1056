from fastapi import (
    FastAPI,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List  # Listを追加
import sqlite3

app = FastAPI()

# CORSの設定（変更なし）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース初期化（変更なし）
def init_db():
    with sqlite3.connect("todos.db") as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                completed BOOLEAN DEFAULT FALSE
            )
        """
        )

init_db()

# モデルの定義を更新
class Todo(BaseModel):
    title: str
    quantity: int = 1
    completed: Optional[bool] = False

class TodoResponse(Todo):
    id: int

# レスポンスモデルのリストを指定
@app.get("/todos", response_model=List[TodoResponse])
def get_todos():
    with sqlite3.connect("todos.db") as conn:
        conn.row_factory = sqlite3.Row  # 列名でアクセスできるように設定
        todos = conn.execute("SELECT * FROM todos").fetchall()
        return [dict(todo) for todo in todos]

@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: Todo):
    with sqlite3.connect("todos.db") as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title, quantity, completed) VALUES (?, ?, ?)",
            (todo.title, todo.quantity, todo.completed),
        )
        todo_id = cursor.lastrowid
        return {"id": todo_id, "title": todo.title, "quantity": todo.quantity, "completed": todo.completed}

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    with sqlite3.connect("todos.db") as conn:
        conn.row_factory = sqlite3.Row
        todo = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return dict(todo)

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: Todo):
    with sqlite3.connect("todos.db") as conn:
        cursor = conn.execute(
            "UPDATE todos SET title = ?, quantity = ?, completed = ? WHERE id = ?",
            (todo.title, todo.quantity, todo.completed, todo_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"id": todo_id, "title": todo.title, "quantity": todo.quantity, "completed": todo.completed}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with sqlite3.connect("todos.db") as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"message": "Todo deleted"}
        