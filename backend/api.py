from fastapi import FastAPI, HTTPException
from db import get_connection
from fastapi.middleware.cors import CORSMiddleware
from db import get_connection, init_schema      
import psycopg2

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

@app.get("/movies")
def list_movies():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, title, year, rating, description, poster_path, rel_url
            FROM movies
            ORDER BY title
        """)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

@app.get("/movies/{movie_id}")
def one_movie(movie_id: int):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, title, year, rating, description, poster_path, rel_url
            FROM movies WHERE id = %s
        """, (movie_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Movie not found")
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))

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