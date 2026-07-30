"""Flask app: serves the frontend and exposes the upload -> generate -> quiz API."""

import time
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

import db
from query_gen import QUESTIONS_PER_FILE, generate_question

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# No login system in scope yet; every upload/question through the web UI is
# attributed to this single account so db.py's per-user schema still applies.
DEFAULT_USERNAME = "web-user"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.post("/api/upload")
def upload_file():
    if "file" not in request.files or not request.files["file"].filename:
        return jsonify({"error": "No file uploaded"}), 400

    upload = request.files["file"]
    stored_name = f"{int(time.time())}_{secure_filename(upload.filename)}"
    stored_path = UPLOAD_DIR / stored_name
    upload.save(stored_path)

    file_id = db.add_file(str(stored_path), DEFAULT_USERNAME)
    return jsonify({"file_id": str(file_id), "file_name": upload.filename})


@app.post("/api/questions/generate")
def generate_questions():
    body = request.get_json(silent=True) or {}
    file_id = body.get("file_id")
    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    count = int(body.get("count", QUESTIONS_PER_FILE))

    file_record = db.get_file_by_id(file_id)
    if file_record is None:
        return jsonify({"error": f"No file found for id {file_id}"}), 404

    questions = generate_question(Path(file_record["file_path"]), username=DEFAULT_USERNAME, count=count)
    return jsonify({"questions": [{"question": q.question, "answer": q.answer} for q in questions]})


@app.get("/api/questions")
def list_questions():
    username = request.args.get("username", DEFAULT_USERNAME)
    return jsonify({"questions": db.get_questions(username)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
