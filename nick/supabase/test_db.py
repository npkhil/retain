import os
import tempfile
from pathlib import Path

from db import add_file, add_question, get_filepath, get_questions


def main() -> None:
    username = os.getenv("TEST_DB_USERNAME", "alice")

    # Create a temporary file to add to the database.
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", prefix="testfile_") as tmp:
        tmp.write("This is a test file for the Supabase helper module.")
        tmp_path = Path(tmp.name)

    try:
        print(f"Adding file record for user '{username}' and path '{tmp_path}'...")
        file_id = add_file(str(tmp_path), username)
        print(f"Added file id: {file_id}")

        found_path = get_filepath(tmp_path.name, username)
        print(f"Retrieved path for '{tmp_path.name}': {found_path}")
        assert found_path == str(tmp_path.resolve()), "File path lookup did not return the expected value"

        question_text = "What is this temporary file?"
        answer_text = "It is a temporary test file created by test_db.py."

        print("Adding a question linked to the source file...")
        question_id = add_question(username, question_text, answer_text, source_file_path=str(tmp_path))
        print(f"Added question id: {question_id}")

        questions = get_questions(username)
        print(f"Retrieved {len(questions)} questions for user '{username}'.")
        assert any(q["question"] == question_text for q in questions), "Inserted question was not found"

        matching = [q for q in questions if q["question"] == question_text]
        assert matching, "No matching question found"

        question = matching[0]
        assert question["answer"] == answer_text, "Question answer did not match"
        assert question["source_file"] is not None, "Source file was not linked to the question"
        assert question["source_file"]["file_path"] == str(tmp_path.resolve()), "Question source file path mismatch"

        print("All tests passed.")
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass


if __name__ == "__main__":
    main()
