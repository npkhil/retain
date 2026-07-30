-- Create tables for a dummy Supabase database using PostgreSQL

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  username text not null unique,
  full_name text not null,
  created_at timestamptz not null default now()
);

create table if not exists files (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  file_name text not null,
  file_path text not null,
  content text,
  created_at timestamptz not null default now()
);

create table if not exists questions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  source_file_id uuid references files(id) on delete set null,
  question text not null,
  answer text,
  created_at timestamptz not null default now()
);
