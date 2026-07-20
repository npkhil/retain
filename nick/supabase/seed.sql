-- Seed dummy data into the Supabase database

insert into users (email, full_name) values
  ('alice@example.com', 'Alice Doe'),
  ('bob@example.com', 'Bob Smith');

insert into files (user_id, file_name, file_path, content) values
  ((select id from users where email = 'alice@example.com'), 'resume.pdf', '/files/alice/resume.pdf', 'Dummy resume content'),
  ((select id from users where email = 'alice@example.com'), 'photo.png', '/files/alice/photo.png', 'Dummy photo metadata'),
  ((select id from users where email = 'bob@example.com'), 'notes.txt', '/files/bob/notes.txt', 'Dummy notes content');

insert into questions (user_id, question_text, answer_text) values
  ((select id from users where email = 'alice@example.com'), 'What is the status of my project?', 'Your project is currently active and on track.'),
  ((select id from users where email = 'alice@example.com'), 'How many files do I have?', 'You have 2 files in your account.'),
  ((select id from users where email = 'bob@example.com'), 'When is my next due date?', 'The next due date is in 10 days.');
