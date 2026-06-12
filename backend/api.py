from fastapi import FastAPI, HTTPException
from db import get_connection
from fastapi.middleware.cors import CORSMiddleware
from db import get_connection, init_schema      
import psycopg2
import subprocess
import os
from typing import Optional

app = FastAPI(title="My Movies API")
init_schema() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_tmdb_token():
    return os.getenv("TMDB_TOKEN")


@app.get("/movies")
def list_movies():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, title, year, rating, description, poster_path, rel_url, tmdb_id
            FROM movies
            ORDER BY title
        """)
        cols = [c[0] for c in cur.description]
        movies = [dict(zip(cols, row)) for row in cur.fetchall()]

        for movie in movies:
            cur.execute("""
                        SELECT 
                        a.name 
                        FROM movie_cast mc 
                        JOIN actors a ON a.id = mc.actor_id 
                        WHERE mc.movie_id = %s 
                        ORDER BY mc.cast_order 
                        LIMIT 10
                        """, (movie["id"],))
            movie["cast"] = [
                {"name": row[0]}
                for row in cur.fetchall()
            ]
        return movies


@app.get("/movies/{movie_id}")
def one_movie(movie_id: int):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT
                m.id, m.title, m.year, m.rating, m.description,
                m.poster_path, m.rel_url, m.tmdb_id,
                a.id AS actor_id, a.name AS actor_name, a.profile_path, a.biography,
                mc.character_name, mc.cast_order
            FROM movies m
            LEFT JOIN movie_cast mc ON mc.movie_id = m.id
            LEFT JOIN actors a ON a.id = mc.actor_id
            WHERE m.id = %s
            ORDER BY mc.cast_order NULLS LAST, a.name
        """, (movie_id,))

        rows = cur.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Movie not found")

        # base movie data fra første række
        first = rows[0]
        movie = {
            "id": first[0],
            "title": first[1],
            "year": first[2],
            "rating": first[3],
            "description": first[4],
            "poster_path": first[5],
            "rel_url": first[6],
            "tmdb_id": first[7],
            "cast": []
        }

        # build cast list
        for r in rows:
            actor_id = r[8]
            if actor_id is None:
                continue

            movie["cast"].append({
                "id": actor_id,
                "name": r[9],
                "profile_path": r[10],
                "biography": r[11],
                "character_name": r[12],
                "cast_order": r[13],
            })

        return movie


# ①  Hent alle sete film-id’er
@app.get("/seen")
def get_seen():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT movie_id FROM seen_movies")
        return [row[0] for row in cur.fetchall()]

# ②  Markér som set
@app.post("/seen/{movie_id}")
def add_seen(movie_id: int):
    with get_connection() as conn, conn.cursor() as cur:
        try:
            cur.execute("INSERT INTO seen_movies (movie_id) VALUES (%s)", (movie_id,))
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            pass
    return {"ok": True}

# ③  Fjern markering
@app.delete("/seen/{movie_id}")
def remove_seen(movie_id: int):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM seen_movies WHERE movie_id=%s", (movie_id,))
        conn.commit()
    return {"ok": True}

@app.post("/admin/import/list")
def import_list(listId: Optional[int] = None, limit: int = 0):
    """
    Docstring for import_list

    Trig import of movies from a TMDB list.
    limit=0 means 'no limit' (the script can ignore or interpret it)
    """
    token = get_tmdb_token()
    if not token:
        raise HTTPException(
            400,
            "Missing TMDB_TOKEN. Add it to docker-compose environment and restart."
        )
    
    if listId is None:
        env_list = os.getenv("TMDB_LIST_ID")
        if not env_list:
            raise HTTPException(
                400,
                "Missing listId and TMDB_LIST_ID is not set."
            )
        listId = int(env_list)

    cmd = ["python", "tmdb_list_export.py", str(listId)]
    if limit and limit > 0:
        cmd.append(str(limit))
    
    r = subprocess.run(
        cmd,
        env={**os.environ, "TMDB_TOKEN": token},
        capture_output=True,
        text=True,
        check=False,
    )

    return {
        "ok": r.returncode == 0,
        "code": r.returncode,
        "out": r.stdout[-2000:],
        "err": r.stderr[-2000:],
    }

@app.post("/admin/import/cast")
def import_cast(movieLimit: int = 50, castLimit: int = 10):
    token = get_tmdb_token()
    if not token:
        raise HTTPException(400, "Missing TMDB_TOKEN. Add it to docker-compose environment and restart.")
    r = subprocess.run(
        ["python", "import_cast.py", "cast", str(movieLimit)],
        env={**os.environ, "CAST_LIMIT": str(castLimit), "TMDB_TOKEN": token},
        capture_output=True,
        text=True,
        check=False,
    )
    return {"ok": r.returncode == 0, "code": r.returncode, "out": r.stdout[-2000:], "err": r.stderr[-2000:]}

@app.post("/admin/import/bio")
def import_bio(bioLimit: int = 50):
    token = get_tmdb_token()
    if not token:
        raise HTTPException(400, "Missing TMDB_TOKEN. Add it to docker-compose environment and restart.")

    r = subprocess.run(
        ["python", "import_cast.py", "bio", str(bioLimit)],
        env={**os.environ, "TMDB_TOKEN": token},
        capture_output=True,
        text=True,
        check=False,
    )
    return {"ok": r.returncode == 0, "code": r.returncode, "out": r.stdout[-2000:], "err": r.stderr[-2000:]}
