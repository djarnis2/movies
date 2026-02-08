CREATE TABLE IF NOT EXISTS movies (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  year INTEGER,
  rating TEXT,
  description TEXT,
  poster_path TEXT,
  rel_url TEXT NOT NULL
);

