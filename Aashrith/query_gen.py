"""
This module contains functions for generating queries based on files pulled from the database.
"""

import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
# Adds the parent directory of this script's folder to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from nick.supabase.db import get_filepath, add_question, get_questions

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import anthropic
client = anthropic.Anthropic(api_key = os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"

SAMPLE_FILES_DIR = Path(__file__).parent.parent / "Sample Files"

# stand-in for the real database until that layer exists. Keyed by filename,
# each entry holds the batch of questions already generated for that file so
# we don't pay to regenerate (or risk duplicating) them on every run.
DB_PATH = Path(__file__).parent.parent / "questions_db.json"

QUESTIONS_PER_FILE = 10  # how many questions to generate per file on first run

#temporarily hardcoded function that gets a file, once the db layer exists this should be replaced with a real lookup
def get_file() -> Path:
    return Path(get_filepath("1784769015_Topics covered.txt", "dude"))

#question generation object
@dataclass
class GeneratedQuestion:
    question: str
    answer: str
    sourceFile: str


def _load_db() -> dict:
    if DB_PATH.exists():
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_db(db: dict) -> None:
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent = 2)


#calls the api once to generate `count` distinct questions for a file, instead of one call per question
def generate_batch(file_path: Path, count: int) -> list[dict]:
    document_text = file_path.read_text(encoding = "utf-8")

    response = client.messages.create(
        model = MODEL,
        max_tokens = 2000,
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": document_text,
                        # Caches the document text. If we regenerate more questions
                        # for this same file within the cache window (5 min by
                        # default), Claude re-reads it at ~10% of normal input
                        # cost instead of full price.
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Based on this document, generate {count} DISTINCT quiz questions "
                            "that each test recall of a different key concept, along with each "
                            "correct answer. Respond with ONLY a JSON array in this exact shape, "
                            "no other text, no markdown fences: "
                            '[{"question": "...", "answer": "..."}, ...]'
                        ),
                    },
                ],
            }
        ],
    )

    text_block = next((b for b in response.content if b.type == "text"), None)
    if text_block is None:
        raise RuntimeError("Claude API returned no text content")

    cleaned = text_block.text.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON from Claude API response: {text_block.text}") from e

    if not isinstance(parsed, list):
        raise RuntimeError(f"Expected a JSON array of questions, got: {text_block.text}")

    return parsed


#main entrypoint: returns cached questions for a file if we have them, otherwise generates and stores a batch
def generate_question(
    file_path: Path | None = None,
    count: int = QUESTIONS_PER_FILE,
    force_regenerate: bool = False,
) -> list[GeneratedQuestion]:

    if file_path is None:
        file_path = get_file()

    # db = _load_db()
    # key = file_path.name

    # if not force_regenerate and key in db and db[key]:
    #     return [GeneratedQuestion(**q) for q in db[key]]

    rawQuestions = generate_batch(file_path, count)

    questions = []
    for q in rawQuestions:
        if "question" not in q or "answer" not in q:
            continue
        questions.append(GeneratedQuestion(question = q["question"], answer = q["answer"], sourceFile = file_path))
        add_question("dude", q["question"], q["answer"], source_file_path = str(file_path))

    # db[key] = [asdict(q) for q in questions]
    # _save_db(db)

    return questions


#temporary to run
if __name__ == "__main__":
    questions = generate_question()
    for q in questions:
        print(q)