import os
import re
import sys
import requests
from dotenv import load_dotenv
from pathlib import Path
from db import get_connection, upsert_actor, upsert_movie_cast


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / "frontend" / ".env")

TMDB_TOKEN = os.getenv("TMDB_TOKEN")
TMDB_BASE = "https://api.themoviedb.org/3"

CAST_LIMIT = int(os.getenv("CAST_LIMIT", "20"))

if not TMDB_TOKEN:
    raise SystemExit("Missing TMDB_TOKEN")

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

def get_movies_with_cast_below(min_cast: int, limit: int = None):
    sql = """
    SELECT m.id, m.title, m.tmdb_id, m.rel_url, COUNT(mc.actor_id) AS cast_count
    FROM movies m
    LEFT JOIN movie_cast mc ON mc.movie_id = m.id
    GROUP BY m.id, m.title, m.tmdb_id, m.rel_url
    HAVING COUNT(mc.actor_id) < %s
    ORDER BY m.title
    """
    params = [min_cast]
    if limit is not None:
        sql += " LIMIT %s"
        params.append(limit)

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(params))
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

def get_existing_tmdb_person_ids(cur, movie_id: int) -> set[int]:
    cur.execute("""
        SELECT a.tmdb_person_id
        FROM movie_cast mc
        JOIN actors a ON a.id = mc.actor_id
        WHERE mc.movie_id = %s
        AND a.tmdb_person_id IS NOT NULL
                """, (movie_id,))
    return {row[0] for row in cur.fetchall()}

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

        movies = get_movies_with_cast_below(CAST_LIMIT, limit)
        print(f"Movies missing cast < {CAST_LIMIT}: {len(movies)}")

        stats = {
            "movies_total": len(movies),
            "movies_tmdb_missing_id": 0,
            "movies_no_cast_from_tmdb": 0,
            "movies_changed": 0,
            "movies_unchanged": 0,
            "actors_added_total": 0
        }

        changed_titles = []
        no_cast_titles = []

        with get_connection() as conn, conn.cursor() as cur:
            for m in movies:
                local_movie_id = m.get("id")
                title = m.get("title")
                existing = get_existing_tmdb_person_ids(cur, local_movie_id)

                tmdb_id = m.get("tmdb_id") or extract_tmdb_id(m.get("rel_url"))
                if not tmdb_id:
                    stats["movies_tmdb_missing_id"] += 1
                    continue

                
                credits = get_credits(tmdb_id)
                cast_list = credits.get("cast", [])
                if not cast_list:
                    stats["movies_no_cast_from_tmdb"] += 1
                    if len(no_cast_titles) < 5:
                        no_cast_titles.append(title)
                    continue

                start_count = len(existing)
                missing = max(0, CAST_LIMIT - start_count)

                added = 0
                for c in cast_list:
                    if added >= missing:
                        break

                    person_id = c.get("id")  # TMDB person id
                    name = (c.get("name") or "").strip()

                    profile_path = c.get("profile_path")
                    character_name = c.get("character")
                    order = c.get("order")

                    if not person_id or not name:
                        continue
                    if person_id in existing:
                        continue # skipping existing actors fetched

                    actor_db_id = upsert_actor(cur, person_id, name, profile_path)
                    upsert_movie_cast(cur, local_movie_id, actor_db_id, character_name, order)
                    existing.add(person_id)
                    added += 1

                stats["actors_added_total"] += added
                if added > 0:
                    stats["movies_changed"] += 1
                    if len(changed_titles) < 5:
                        changed_titles.append(f"{title} (+{added})")
                else:
                    stats["movies_unchanged"] += 1
                    
            conn.commit()
            print("\n=== CAST IMPORT SUMMARY ===")
            print(f"Target cast per movie: {CAST_LIMIT}")
            print(f"Movies considered (<{CAST_LIMIT} cast): {stats['movies_total']}")
            print(f"Movies changed: {stats['movies_changed']}")
            print(f"Movies unchanged: {stats['movies_unchanged']}")
            print(f"Total actors added: {stats['actors_added_total']}")
            print(f"Movies missing tmdb_id: {stats['movies_tmdb_missing_id']}")
            print(f"Movies where TMDB returned no cast: {stats['movies_no_cast_from_tmdb']}")

            if changed_titles:
                print("\nExamples changed:")
                for s in changed_titles:
                    print(" -", s)

            if no_cast_titles:
                print("\nExamples with no TMDB cast:")
                for s in no_cast_titles:
                    print(" -", s)


    elif mode == "bio":
        fill_missing_biographies(limit)
    
    else:
        raise SystemExit("Unknown mode. Use cast or bio")

if __name__ == "__main__":
    main()
