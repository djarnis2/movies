# db.py
import os, psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

_cfg = dict(
    host     = os.getenv("PG_HOST", "localhost"), # in docker network: pg
    port     = int(os.getenv("PG_PORT", 5432)),
    dbname   = os.getenv("PG_DB"),
    user     = os.getenv("PG_USER"),
    password = os.getenv("PG_PASSWORD")
)

def get_connection():
    """A central way to make (and maybe reuse) connection."""
    return psycopg2.connect(**_cfg)

def init_schema():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id          SERIAL PRIMARY KEY,
            title       TEXT,
            year        SMALLINT,
            rating      TEXT,
            description TEXT,
            poster_path TEXT,
            rel_url     TEXT NOT NULL,
            tmdb_id     INTEGER
        );

        CREATE UNIQUE INDEX IF NOT EXISTS ux_movies_rel_url ON movies(rel_url);

        CREATE TABLE IF NOT EXISTS seen_movies (
            movie_id INTEGER PRIMARY KEY
                     REFERENCES movies(id)
                     ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS actors (
            id SERIAL PRIMARY KEY,
            tmdb_person_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            profile_path TEXT,
            biography TEXT
        );

        CREATE TABLE IF NOT EXISTS movie_cast (
            movie_id INTEGER NOT NULL
                REFERENCES movies(id) ON DELETE CASCADE,
            actor_id INTEGER NOT NULL
                REFERENCES actors(id) ON DELETE CASCADE,
            character_name TEXT,
            cast_order INTEGER,
            PRIMARY KEY (movie_id, actor_id)
        );

        CREATE INDEX IF NOT EXISTS idx_movie_cast_movie_id ON movie_cast(movie_id);
        CREATE INDEX IF NOT EXISTS idx_movie_cast_actor_id ON movie_cast(actor_id);
        CREATE INDEX IF NOT EXISTS idx_actors_name ON actors(name);
        """)
        conn.commit()

def insert_movies(batch):
    """
    -- Example:
    batch = [
    ("Ad Astra", 2019, "61", "Roy McBride rejser ...", "/path.jpg", "/movie/419704-ad-astra"),
    ]
    """
    if not batch:
        return
    insert_sql = """
    INSERT INTO movies (title, year, rating, description, poster_path, rel_url)
    VALUES %s
    ON CONFLICT (rel_url) DO UPDATE
    SET
        title       = EXCLUDED.title,
        year        = COALESCE(EXCLUDED.year, movies.year),   -- kun opdatér hvis vi har et år
        rating      = COALESCE(EXCLUDED.rating, movies.rating),
        description = COALESCE(NULLIF(EXCLUDED.description, ''), movies.description),
        poster_path = COALESCE(EXCLUDED.poster_path, movies.poster_path)
    """
    with get_connection() as conn, conn.cursor() as cur:
        execute_values(cur, insert_sql, batch, page_size=50)
        conn.commit()

# db.py (tilføjelser)

def upsert_actor(cur, tmdb_person_id, name, profile_path=None, biography=None):
    cur.execute("""
        INSERT INTO actors (tmdb_person_id, name, profile_path, biography)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (tmdb_person_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            profile_path = COALESCE(EXCLUDED.profile_path, actors.profile_path),
            biography = COALESCE(EXCLUDED.biography, actors.biography)
        RETURNING id;
    """, (tmdb_person_id, name, profile_path, biography))
    return cur.fetchone()[0]


def upsert_movie_cast(cur, movie_id, actor_id, character_name=None, cast_order=None):
    cur.execute("""
        INSERT INTO movie_cast (movie_id, actor_id, character_name, cast_order)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (movie_id, actor_id)
        DO UPDATE SET
            character_name = COALESCE(EXCLUDED.character_name, movie_cast.character_name),
            cast_order = COALESCE(EXCLUDED.cast_order, movie_cast.cast_order)
    """, (movie_id, actor_id, character_name, cast_order))
