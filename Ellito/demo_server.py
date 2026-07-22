from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import cgi
import json
import shutil
import sqlite3
import time

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "sample_uploads.db"
INDEX_PATH = BASE_DIR / "demo_index.html"
APP_JS_PATH = BASE_DIR / "demo_app.js"

UPLOAD_DIR.mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            size INTEGER,
            content_type TEXT,
            description TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


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

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO files (name, path, size, content_type, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            [original_name, str(stored_path), file_storage.file.tell(), file_storage.type, description],
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
