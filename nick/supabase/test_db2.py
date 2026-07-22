import os
import tempfile
from pathlib import Path

from db import add_file, add_question, get_filepath, get_questions, _create_user


def main() -> None:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    username = "dude"
    # add user to the database
    _create_user(username, "Dude")
    
    add_file(str(project_root / "Sample Files" / "Preamble to the Constitution.pdf"), username)

    

if __name__ == "__main__":
    main()
