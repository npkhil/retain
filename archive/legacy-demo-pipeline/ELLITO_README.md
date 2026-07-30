# Ellito

This folder contains my file uploader contribution.

## Files
- `index.html` — uploader UI that lets a user choose a file, set a bucket/folder, and submit the upload.
- `app.js` — frontend logic that uploads the file to Supabase Storage and inserts metadata into a `files` table.
- `config.example.js` — copy this file to `config.js` and fill in your Supabase project URL and anon key.
- `ellti` — placeholder file for my contributions.

## Setup

1. Copy `config.example.js` to `config.js`.
2. Set:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
3. Create a Supabase Storage bucket (for example `uploads`).
4. Create a `files` table in Supabase with the following example schema:

```sql
create table files (
  id uuid default gen_random_uuid() primary key,
  name text,
  path text,
  bucket text,
  size bigint,
  content_type text,
  description text,
  url text,
  created_at timestamptz default now()
);
```

## Run locally

```powershell
cd Ellito
python -m http.server 8000
```

Open `http://localhost:8000` and use the form to upload.

## Notes

- Do not commit `Ellito/config.js` with real credentials.
- If the bucket is private, use signed URLs instead of `getPublicUrl()`.
