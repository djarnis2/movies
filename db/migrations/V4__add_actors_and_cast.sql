-- V3__add_actors_and_cast.sql

-- 1) Actors tabel
CREATE TABLE IF NOT EXISTS actors (
  id SERIAL PRIMARY KEY,
  tmdb_person_id INTEGER UNIQUE,
  name TEXT NOT NULL,
  profile_path TEXT
);

-- 2) Join tabel mellem movies og actors
CREATE TABLE IF NOT EXISTS movie_cast (
  movie_id INTEGER NOT NULL,
  actor_id INTEGER NOT NULL,
  character_name TEXT,
  cast_order INTEGER,

  PRIMARY KEY (movie_id, actor_id),

  CONSTRAINT fk_cast_movie
    FOREIGN KEY (movie_id)
    REFERENCES movies(id)
    ON DELETE CASCADE,

  CONSTRAINT fk_cast_actor
    FOREIGN KEY (actor_id)
    REFERENCES actors(id)
    ON DELETE CASCADE
);

-- 3) Indekser til hurtige joins
CREATE INDEX IF NOT EXISTS idx_movie_cast_movie_id ON movie_cast(movie_id);
CREATE INDEX IF NOT EXISTS idx_movie_cast_actor_id ON movie_cast(actor_id);

-- 4) Indeks til navnesøgning
CREATE INDEX IF NOT EXISTS idx_actors_name ON actors(name);

-- 5) (Valgfrit) Hvis du vil kunne søge robuste partial matches senere:
-- kræver pg_trgm extension:
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS idx_actors_name_trgm
--   ON actors USING GIN (name gin_trgm_ops);
