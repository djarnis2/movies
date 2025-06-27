# db.py
import os, psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

_cfg = dict(
    host     = os.getenv("PG_HOST", "localhost"),
    port     = int(os.getenv("PG_PORT", 5432)),
    dbname   = os.getenv("PG_DB"),
    user     = os.getenv("PG_USER"),
    password = os.getenv("PG_PASSWORD")
)

def get_connection():
    """Én central måde at oprette (og evt. genbruge) forbindelsen på."""
    return psycopg2.connect(**_cfg)

def init_schema():
    """Kør én gang ved start: sikrer tabel og unikke constraints."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id          SERIAL PRIMARY KEY,
            title       TEXT,
            year        SMALLINT,
            rating      TEXT,
            description TEXT,
            poster_path TEXT,
            rel_url         TEXT,
            UNIQUE (title, year)
        );
        CREATE TABLE IF NOT EXISTS seen_movies (
            movie_id INTEGER PRIMARY KEY
                       REFERENCES movies(id)      -- læg FK-relation på med det samme
                       ON DELETE CASCADE         -- fjern “seen” hvis filmen slettes
        );
        """)

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
    ON CONFLICT (title, year) DO NOTHING
    """
    with get_connection() as conn, conn.cursor() as cur:
        execute_values(cur, insert_sql, batch, page_size=50)
        conn.commit()
