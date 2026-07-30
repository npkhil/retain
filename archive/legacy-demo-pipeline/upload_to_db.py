from __future__ import annotations

import argparse
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_MODULE_PATH = REPO_ROOT / "nick" / "supabase" / "db.py"


def load_db_module():
    """Load the existing db.py helper module from the nick/supabase folder."""
    spec = spec_from_file_location("nick_supabase_db", DB_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load database helper from: {DB_MODULE_PATH}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_uploaded_file(file_path: str, username: str, full_name: str = "") -> str:
    """Call the shared add_file function from nick/supabase/db.py."""
    db_module = load_db_module()

    resolved_path = Path(file_path).expanduser().resolve()
    if not resolved_path.is_file():
        raise FileNotFoundError(f"File not found: {resolved_path}")

    return str(db_module.add_file(str(resolved_path), username, full_name))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send a file path to the nick/supabase db.py add_file helper."
    )
    parser.add_argument("file_path", help="Absolute or relative path to the file to store")
    parser.add_argument("username", help="Username to associate with the uploaded file")
    parser.add_argument(
        "--full-name",
        default="",
        help="Optional display name for the user record",
    )
    args = parser.parse_args()

    try:
        file_id = add_uploaded_file(args.file_path, args.username, args.full_name)
        print(f"Inserted file record with id: {file_id}")
        return 0
    except Exception as exc:  # pragma: no cover - CLI-friendly error handling
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
