import os
from typing import Dict, List, Optional

import psycopg

DB_URL = os.getenv("SUPABASE_DB_URL", "postgresql://postgres:mysecretpassword@127.0.0.1:54322/mydb")


def get_connection():
    """Return a new PostgreSQL connection to the Supabase database."""
    return psycopg.connect(DB_URL)


def _get_user_id(conn: psycopg.Connection, username: str) -> Optional[str]:
    with conn.cursor() as cur:
        cur.execute("select id from users where username = %s", (username,))
        row = cur.fetchone()
        return row[0] if row else None


def _create_user(conn: psycopg.Connection, username: str, full_name: str = "") -> str:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "insert into users (username, full_name) values (%s, %s) returning id",
            (username, full_name or username),
        )
        conn.commit()
        return cur.fetchone()[0]


def _ensure_user(conn: psycopg.Connection, username: str, full_name: str = "") -> str:
    user_id = _get_user_id(conn, username)
    if user_id:
        return user_id
    return _create_user(conn, username, full_name)


def _read_file_content(path: str) -> Optional[str]:
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return None


def add_file(path: str, username: str, full_name: str = "") -> str:
    """Add a file record for the given username and return the inserted file id."""
    absolute_path = os.path.abspath(path)
    file_name = os.path.basename(absolute_path)
    content = _read_file_content(absolute_path)

    with get_connection() as conn:
        user_id = _ensure_user(conn, username, full_name)
        with conn.cursor() as cur:
            cur.execute(
                "insert into files (user_id, file_name, file_path, content) values (%s, %s, %s, %s) returning id",
                (user_id, file_name, absolute_path, content),
            )
            return cur.fetchone()[0]


def get_filepath(filename: str, username: str) -> Optional[str]:
    """Retrieve the stored file path for the given username and filename."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select f.file_path from files f join users u on f.user_id = u.id where u.username = %s and f.file_name = %s",
                (username, filename),
            )
            row = cur.fetchone()
            return row[0] if row else None


def _resolve_source_file_id(conn: psycopg.Connection, username: str, source_file_path: str) -> Optional[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select f.id from files f join users u on f.user_id = u.id where u.username = %s and f.file_path = %s",
            (username, os.path.abspath(source_file_path)),
        )
        row = cur.fetchone()
        return row[0] if row else None


def add_question(username: str, question: str, answer: Optional[str] = None, source_file_path: Optional[str] = None, full_name: str = "") -> str:
    """Add a question for the given username and optionally link it to a source file."""
    with get_connection() as conn:
        user_id = _ensure_user(conn, username, full_name)
        source_file_id = None
        if source_file_path:
            source_file_id = _resolve_source_file_id(conn, username, source_file_path)

        with conn.cursor() as cur:
            cur.execute(
                "insert into questions (user_id, source_file_id, question, answer) values (%s, %s, %s, %s) returning id",
                (user_id, source_file_id, question, answer),
            )
            return cur.fetchone()[0]


def get_questions(username: str) -> List[Dict[str, Optional[str]]]:
    """Return stored questions for the given username, including the linked source file if present."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select q.id, q.question, q.answer, q.created_at, f.file_name, f.file_path
                from questions q
                join users u on q.user_id = u.id
                left join files f on q.source_file_id = f.id
                where u.username = %s
                order by q.created_at
                """,
                (username,),
            )
            rows = cur.fetchall()

    results: List[Dict[str, Optional[str]]] = []
    for qid, question_text, answer, created_at, file_name, file_path in rows:
        source_file = None
        if file_name or file_path:
            source_file = {"file_name": file_name, "file_path": file_path}
        results.append(
            {
                "id": str(qid),
                "question": question_text,
                "answer": answer,
                "created_at": created_at.isoformat() if created_at else None,
                "source_file": source_file,
            }
        )
    return results


if __name__ == "__main__":
    print("This module provides helper functions for the Supabase Postgres schema.")
    print("Use add_file(), get_filepath(), add_question(), and get_questions() from your own script.")
