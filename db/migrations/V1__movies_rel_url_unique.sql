-- Remove constrint on title and year
ALTER TABLE movies DROP CONSTRAINT IF EXISTS movies_title_year_key;

-- Delete doubles based on rel_url (keep lowest id)
DELETE FROM movies
WHERE id NOT IN (
  SELECT MIN(id)
  FROM movies
  GROUP BY rel_url
);

-- rel_url set to not null
ALTER TABLE movies ALTER COLUMN rel_url SET NOT NULL;

-- Unique constraint on rel_url
ALTER TABLE movies
  ADD CONSTRAINT movies_rel_url_key UNIQUE (rel_url);
