# Database schema

Retain stores data in a hosted Supabase Postgres project, connected to via a plain
`SUPABASE_DB_URL` connection string (see the root `.env.example`) — there is no local
Docker/Supabase-CLI stack in this repo; a leftover local-Postgres scaffold is kept in
`archive/local-docker-postgres/` for reference but isn't part of the real setup.

## Files

- `migrations/1_init.sql` — schema for `users`, `files`, and `questions`.
- `seed.sql` — optional dummy data for local testing.

## Schema

- `users` — `username` (unique), `full_name`.
- `files` — an uploaded document: `file_name`, `file_path`, extracted `content`, owned by a `user_id`.
- `questions` — a generated quiz question: `question`, `answer`, linked to the `user_id` and the `source_file_id` it was generated from.

## Applying the schema

Point `psql` (or the Supabase SQL editor) at the same database your `.env`'s
`SUPABASE_DB_URL` uses:

```bash
psql "$SUPABASE_DB_URL" -f db/migrations/1_init.sql
psql "$SUPABASE_DB_URL" -f db/seed.sql   # optional sample data
```

`backend/db.py` is the only code that talks to this database directly.
