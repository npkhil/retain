from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import cgi
import json
import os
import shutil
import sqlite3
import time

try:
    import psycopg
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    psycopg = None

try:
    from upload_to_db import add_uploaded_file
except Exception:  # pragma: no cover - optional bridge import
    add_uploaded_file = None

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
INDEX_PATH = BASE_DIR / "demo_index.html"
APP_JS_PATH = BASE_DIR / "demo_app.js"
DB_PATH = BASE_DIR / "sample_uploads.db"
DB_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")
USE_POSTGRES = os.getenv("USE_POSTGRES", "1" if psycopg is not None else "0") == "1"

UPLOAD_DIR.mkdir(exist_ok=True)


def init_db():
    if USE_POSTGRES:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    create table if not exists users (
                      id uuid primary key default gen_random_uuid(),
                      username text not null unique,
                      full_name text not null,
                      created_at timestamptz not null default now()
                    )
                    """
                )
                cur.execute(
                    """
                    create table if not exists files (
                      id uuid primary key default gen_random_uuid(),
                      user_id uuid not null references users(id) on delete cascade,
                      file_name text not null,
                      file_path text not null,
                      content text,
                      created_at timestamptz not null default now()
                    )
                    """
                )
            conn.commit()
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        create table if not exists files (
            id integer primary key autoincrement,
            name text not null,
            path text not null,
            size integer,
            content_type text,
            description text,
            uploaded_at text default current_timestamp
        )
        """
    )
    conn.commit()
    conn.close()


def ensure_demo_user(conn):
    if not USE_POSTGRES:
        return None

    with conn.cursor() as cur:
        cur.execute("select id from users where username = %s", ("demo-upload",))
        row = cur.fetchone()
        if row:
            return row[0]

        cur.execute(
            "insert into users (username, full_name) values (%s, %s) returning id",
            ("demo-upload", "Demo Upload User"),
        )
        conn.commit()
        return cur.fetchone()[0]


class DemoUploadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(INDEX_PATH.read_bytes())
            return

        if self.path == "/demo_app.js":
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.end_headers()
            self.wfile.write(APP_JS_PATH.read_bytes())
            return

        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        self.send_error(404, "Not found")

    def do_POST(self):
        if self.path != "/upload":
            self.send_error(404, "Not found")
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self.send_error(400, "Expected multipart/form-data")
            return

        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": content_type,
                    "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
                },
            )
        except Exception as exc:
            self.send_error(400, f"Bad multipart body: {exc}")
            return

        file_item = form.getfirst("file")
        file_storage = form["file"] if "file" in form else None
        description = form.getfirst("description", "")

        if file_storage is None or not file_storage.filename:
            self.send_json(400, {"error": "No file uploaded"})
            return

        original_name = Path(file_storage.filename).name
        timestamp = int(time.time())
        stored_name = f"{timestamp}_{original_name}"
        stored_path = UPLOAD_DIR / stored_name

        with stored_path.open("wb") as out_file:
            shutil.copyfileobj(file_storage.file, out_file)

        if USE_POSTGRES:
            db_id = None
            if add_uploaded_file is not None:
                try:
                    db_id = add_uploaded_file(str(stored_path), "demo-upload", "Demo Upload User")
                except Exception as exc:
                    self.send_json(500, {
                        "error": f"Database insert failed: {exc}",
                        "name": original_name,
                        "path": str(stored_path),
                    })
                    return

            self.send_json(200, {
                "message": "upload saved",
                "id": str(db_id) if db_id is not None else "n/a",
                "name": original_name,
                "path": str(stored_path),
                "description": description,
            })
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            insert into files (name, path, size, content_type, description)
            values (?, ?, ?, ?, ?)
            """,
            (original_name, str(stored_path), stored_path.stat().st_size, "application/octet-stream", description or ""),
        )
        conn.commit()
        row_id = cur.lastrowid
        conn.close()

        self.send_json(200, {
            "message": "upload saved",
            "id": row_id,
            "name": original_name,
            "path": str(stored_path),
            "description": description,
        })

    def send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8001), DemoUploadHandler)
    print("Demo upload server running on http://127.0.0.1:8001")
    server.serve_forever()
