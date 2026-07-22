-- Seed dummy data into the Supabase database

insert into users (username, full_name) values
  ('alice', 'Alice Doe'),
  ('bob', 'Bob Smith');

insert into files (user_id, file_name, file_path, content) values
  ((select id from users where username = 'alice'), 'resume.pdf', '/files/alice/resume.pdf', 'Dummy resume content'),
  ((select id from users where username = 'alice'), 'photo.png', '/files/alice/photo.png', 'Dummy photo metadata'),
  ((select id from users where username = 'bob'), 'notes.txt', '/files/bob/notes.txt', 'Dummy notes content');

insert into questions (user_id, source_file_id, question, answer) values
  ((select id from users where username = 'alice'), (select id from files where file_name = 'resume.pdf' and user_id = (select id from users where username = 'alice')), 'What is the status of my project?', 'Your project is currently active and on track.'),
  ((select id from users where username = 'alice'), (select id from files where file_name = 'photo.png' and user_id = (select id from users where username = 'alice')), 'How many files do I have?', 'You have 2 files in your account.'),
  ((select id from users where username = 'bob'), (select id from files where file_name = 'notes.txt' and user_id = (select id from users where username = 'bob')), 'When is my next due date?', 'The next due date is in 10 days.');
