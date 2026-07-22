"""
This module contains functions for generating queries based on files pulled from the database.
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from huggingface_hub import InferenceClient
client = InferenceClient(api_key = os.getenv("HUGGINGFACE_API_TOKEN"))
MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

SAMPLE_FILES_DIR = Path(__file__).parent.parent / "Sample Files"

# stand-in for the real database until that layer exists. Keyed by filename,
# each entry holds the batch of questions already generated for that file so
# we don't pay to regenerate (or risk duplicating) them on every run.
DB_PATH = Path(__file__).parent.parent / "questions_db.json"

QUESTIONS_PER_FILE = 10  # how many questions to generate per file on first run

#temporarily hardcoded function that gets a file, once the db layer exists this should be replaced with a real lookup
def get_file() -> Path:
    return SAMPLE_FILES_DIR / "Igneous Rocks Slide 1.txt"

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

    prompt = (
        f"Based on the document below, generate {count} DISTINCT quiz questions "
        "that each test recall of a different key concept, along with each "
        "correct answer. Respond with ONLY a JSON array in this exact shape, "
        "no other text, no markdown fences: "
        '[{"question": "...", "answer": "..."}, ...]\n\n'
        f"Document:\n{document_text}"
    )

    response = client.chat.completions.create(
        model = MODEL,
        max_tokens = 2000,
        messages = [{"role": "user", "content": prompt}],
    )

    response_text = response.choices[0].message.content
    if not response_text:
        raise RuntimeError("Hugging Face API returned no text content")

    cleaned = response_text.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON from Hugging Face API response: {response_text}") from e

    if not isinstance(parsed, list):
        raise RuntimeError(f"Expected a JSON array of questions, got: {response_text}")

    return parsed


#main entrypoint: returns cached questions for a file if we have them, otherwise generates and stores a batch
def generate_question(
    file_path: Path | None = None,
    count: int = QUESTIONS_PER_FILE,
    force_regenerate: bool = False,
) -> list[GeneratedQuestion]:

    if file_path is None:
        file_path = get_file()

    db = _load_db()
    key = file_path.name

    if not force_regenerate and key in db and db[key]:
        return [GeneratedQuestion(**q) for q in db[key]]

    rawQuestions = generate_batch(file_path, count)

    questions = []
    for q in rawQuestions:
        if "question" not in q or "answer" not in q:
            continue
        questions.append(GeneratedQuestion(question = q["question"], answer = q["answer"], sourceFile = key))

    db[key] = [asdict(q) for q in questions]
    _save_db(db)

    return questions


#temporary to run
if __name__ == "__main__":
    questions = generate_question()
    for q in questions:
        print(q)