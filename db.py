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
    """Run one time at upstart: secure table and unique constraints."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id          SERIAL PRIMARY KEY,
            title       TEXT,
            year        SMALLINT,
            rating      TEXT,
            description TEXT,
            poster_path TEXT,
            rel_url     TEXT
        );
        CREATE TABLE IF NOT EXISTS seen_movies (
            movie_id INTEGER PRIMARY KEY
                       REFERENCES movies(id)      -- add FK-relation
                       ON DELETE CASCADE         -- remove “seen” if film is deleted.
        );
                    
        -- Make sure rel_url is NOT NULL
        DO $$
        BEGIN
            BEGIN
                ALTER TABLE movies ALTER column rel_url SET NOT NULL;
            EXCEPTION WHEN others THEN
                -- ignore if already set
                NULL;
            END;
        END$$;
                    
        -- idempotent UNIQUE index
        CREATE UNIQUE INDEX IF NOT EXISTS ux_movies_rel_url ON movies(rel_url);
        """)
        conn.commit()

def insert_movies(batch):
    """
    batch = [
        ("Ad Astra", 2019, "61", "Roy McBride rejser ..."),
        ...
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
