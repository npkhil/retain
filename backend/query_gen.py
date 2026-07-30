"""
This module contains functions for generating quiz questions from a document via the Claude API.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from db import add_question
from text_extract import extract_text

import anthropic
client = anthropic.Anthropic(api_key = os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"

QUESTIONS_PER_FILE = 10  # how many questions to generate per file by default

#question generation object
@dataclass
class GeneratedQuestion:
    question: str
    answer: str
    sourceFile: str


#calls the api once to generate `count` distinct questions for a file, instead of one call per question
def generate_batch(file_path: Path, count: int) -> list[dict]:
    document_text = extract_text(file_path)

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


#main entrypoint: generates a batch of questions for a file and persists them for the given user
def generate_question(
    file_path: Path,
    username: str,
    count: int = QUESTIONS_PER_FILE,
) -> list[GeneratedQuestion]:
    raw_questions = generate_batch(file_path, count)

    questions = []
    for q in raw_questions:
        if "question" not in q or "answer" not in q:
            continue
        questions.append(GeneratedQuestion(question = q["question"], answer = q["answer"], sourceFile = str(file_path)))
        add_question(username, q["question"], q["answer"], source_file_path = str(file_path))

    return questions


if __name__ == "__main__":
    sample_file = Path(__file__).parent.parent / "sample-data" / "Preamble to the Constitution.pdf"
    for q in generate_question(sample_file, username = "cli-test"):
        print(q)