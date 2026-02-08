import os
import re
import sys
import requests
from dotenv import load_dotenv
from pathlib import Path
from db import get_connection, upsert_actor, upsert_movie_cast


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / "frontend" / ".env")

TMDB_TOKEN = os.getenv("TMDB_TOKEN") or os.getenv("VITE_TMDB_V4_TOKEN")
TMDB_BASE = "https://api.themoviedb.org/3"

CAST_LIMIT = int(os.getenv("CAST_LIMIT", "20"))

if not TMDB_TOKEN:
    raise SystemExit("Missing VITE_TMDB_V4_TOKEN in frontend .env/.env.local")

print("Token loaded OK (length):", len(TMDB_TOKEN))



def extract_tmdb_id(rel_url: str):
    # fx /movie/530915-1917
    m = re.match(r"^/movie/(\d+)", rel_url or "")
    return int(m.group(1)) if m else None


def get_credits(tmdb_id: int):
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}"}
    r = requests.get(f"{TMDB_BASE}/movie/{tmdb_id}/credits", headers=headers)
    if r.status_code != 200:
        print("TMDB credits error:", r.status_code, r.text[:200])
    r.raise_for_status()
    return r.json()

def get_movies_missing_cast(limit: int = None):
    sql = """
    SELECT id, title, tmdb_id, rel_url
    FROM movies m
    WHERE NOT EXISTS (
        SELECT 1 FROM movie_cast mc
        WHERE mc.movie_id = m.id
      )
    ORDER BY title
    """
    params = None
    if limit is not None:
        sql += " LIMIT %s"
        params = (limit,)

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_person(person_id: int):
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}"}
    r = requests.get(f"{TMDB_BASE}/person/{person_id}", headers=headers)
    r.raise_for_status()
    return r.json()


def get_actors_missing_bio(limit: int = None):
    sql = """
    SELECT id, tmdb_person_id, name, profile_path
    FROM actors
    WHERE (biography IS NULL OR biography = '')
        AND tmdb_person_id IS NOT NULL
    ORDER BY name
    """
    params = None
    if limit is not None:
        sql += " LIMIT %s"
        params = (limit,)
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

def fill_missing_biographies(limit: int = None):
    actors = get_actors_missing_bio(limit)
    print(f"Actors missing biography: {len(actors)}")

    with get_connection() as conn, conn.cursor() as cur:
        for a in actors:
            tmdb_person_id = a["tmdb_person_id"]
            name = a["name"]
            profile_path = a.get("profile_path")

            try:
                data = get_person(tmdb_person_id)
                bio = (data.get("biography") or "").strip()

                # save bio in DB with upsert_actor
                upsert_actor(cur, tmdb_person_id, name, profile_path, biography=bio)
                print(f" updated bioi: {name} ({tmdb_person_id})")
            except Exception as e:
                print(f" FAIL: {name} ({tmdb_person_id}) -> {e}")
        conn.commit()

def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "cast").lower()
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if mode == "cast":

        movies = get_movies_missing_cast(limit)
        print(f"Movies missing cast: {len(movies)}")

        with get_connection() as conn, conn.cursor() as cur:
            for m in movies:
                local_movie_id = m.get("id")
                title = m.get("title")

                tmdb_id = m.get("tmdb_id") or extract_tmdb_id(m.get("rel_url"))
                if not tmdb_id:
                    print(f"SKIP: no tmdb_id for {title}")
                    continue

                credits = get_credits(tmdb_id)
                cast = credits.get("cast", [])[:CAST_LIMIT]
                if not cast:
                    print(f"  -> No cast returned from TMDB for tmdb_id={tmdb_id}")

                print(f"\n{title} (tmdb_id={tmdb_id})")

                for c in cast:
                    person_id = c.get("id")  # TMDB person id
                    name = c.get("name") or ""
                    profile_path = c.get("profile_path")
                    character_name = c.get("character")
                    order = c.get("order")

                    print(f"  - {name} as {character_name}")

                    if not person_id or not name:
                        continue

                    actor_db_id = upsert_actor(cur, person_id, name, profile_path)
                    upsert_movie_cast(cur, local_movie_id, actor_db_id, character_name, order)
                    
            conn.commit()
    elif mode == "bio":
        fill_missing_biographies(limit)
    
    else:
        raise SystemExit("Unknown mode. Use cast or bio")

if __name__ == "__main__":
    main()
