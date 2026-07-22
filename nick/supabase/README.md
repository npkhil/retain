# Supabase Dummy Database

This folder contains a simple Supabase-style database scaffold for development and testing.

## Files

- `config.toml` — basic Supabase local project configuration.
- `migrations/1_init.sql` — schema definitions for `users` (identified by username), `files`, and `questions`.
- `seed.sql` — dummy data for `users`, `files`, and `questions`.

The `questions` table now includes `source_file_id`, which references the `files` table as the source file for each generated question.

## Usage

If you have the Supabase CLI installed:

```bash
cd nick/supabase
supabase start
supabase db reset --project-ref local
supabase db push
psql postgres://postgres:postgres@localhost:54322/postgres -f seed.sql
```

Or use PostgreSQL directly with Docker Compose:

```bash
cd nick/supabase
docker compose up -d
psql postgres://postgres:postgres@localhost:54322/postgres -f seed.sql
```

This scaffold is designed for PostgreSQL, including the SQL schema and sample data.
