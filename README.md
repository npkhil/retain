# Retain

Upload a document, and Retain generates quiz questions from its content via the
Claude API so you can test recall instead of just re-reading.

Contributors: Elliott Paschane, Nicholas Khil, Aashrith Nujella

## How it works

1. Upload a file through the web UI.
2. The backend saves it, extracts its text, and stores it in Postgres (`backend/db.py`).
3. Claude generates quiz questions from the extracted text (`backend/query_gen.py`) and
   they're persisted alongside the source file.
4. The frontend renders them as a flip-card quiz: reveal the answer, then move to the next one.

## Layout

- `backend/` — Flask app (`app.py`), the Postgres data layer (`db.py`), question
  generation (`query_gen.py`), and shared PDF/text extraction (`text_extract.py`).
- `frontend/` — static upload + quiz UI (`index.html`, `app.js`, `style.css`), no build step.
- `db/` — schema (`migrations/1_init.sql`), seed data, and setup notes.
- `sample-data/` — example documents for trying the pipeline out.
- `archive/` — superseded implementations and old test artifacts, kept for reference. See `archive/README.md`.

## Setup

1. Create and activate a virtualenv, then install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY` and `SUPABASE_DB_URL`
   (a Postgres connection string — see `db/README.md` for schema setup).
3. Run the app:
   ```bash
   python backend/app.py
   ```
4. Open `http://127.0.0.1:5001/` and upload a file from `sample-data/` to try it out.

```
        ,  .
       c(\/|
       /  o `-.
      |    --'
    _-_    (_
   /`` `---' \     /
/  `---. \ \-'\__./
\  ( -< -'-'|\_.-/'
|  `-.`. ,`(
|   /`'----'\
\\_/ | | | | \
  `-~~\~~|~/~~'
       \ |/
        \|\_,
      ,_/  '
```
------------------------------------------------
