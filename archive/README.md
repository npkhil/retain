# Archive

Superseded code and test artifacts from before the repo was reorganized into
`backend/` + `frontend/` + `db/`. Nothing here was deleted — it's kept for reference,
but none of it is used by the live app.

- `supabase-storage-upload/` — Elliott's original upload UI that talked directly to
  Supabase Storage from the browser (`supabase-js`). Superseded because the project
  standardized on the local-Postgres path (`backend/db.py`), which stores file content
  in the DB and is what question generation actually reads from.
- `legacy-demo-pipeline/` — the earlier stdlib `http.server` + `cgi`-based upload demo
  (server, HTML, JS, and the `upload_to_db.py` bridge script). Replaced by `backend/app.py`
  (Flask) and `frontend/`.
- `local-docker-postgres/` — a local Supabase/Postgres Docker Compose scaffold that was
  never actually used; `.env`'s `SUPABASE_DB_URL` connects to a hosted Supabase Postgres
  instance instead. Kept in case a local dev database is wanted later.
- `legacy-test-uploads/` — files that got uploaded while testing the old demo pipeline.
- `questions_db.json` — an early JSON-file cache for generated questions, from before
  questions were persisted in Postgres.
- `requirements-aashrith.txt` — a near-duplicate of the root `requirements.txt`, now consolidated.
- `placeholders/` — empty placeholder files (`ellti`, `nick-temp`) with no content.
