import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parents[2] / "support_desk.db"


def initialize_database() -> None:
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL
                           )
        """)
        connection.commit()

def save_message(
    conversation_id: str,
    role: str,
    content: str,
) -> None:
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content),
        )
        connection.commit()

def get_messages(conversation_id: str) -> list[dict[str, str]]:
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

        return [
            {"role": row["role"], "content": row["content"]}
            for row in rows
        ]
