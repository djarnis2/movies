-- Add tmdb_id column
ALTER TABLE movies ADD COLUMN IF NOT EXISTS tmdb_id INTEGER;

-- Populate tmdb_id from rel_url
UPDATE movies
SET tmdb_id = CAST(substring(rel_url from '^/movie/([0-9]+)(?:-|$)') AS INTEGER)
WHERE tmdb_id IS NULL;

-- Optional index
CREATE INDEX IF NOT EXISTS idx_movies_tmdb_id ON movies(tmdb_id);
