import os, requests

token = os.getenv("TMDB_TOKEN")
print("token?", bool(token), "len=", (len(token) if token else 0))

h = {"Authorization": f"Bearer {token}"}

for tmdb_id in [1339509, 449911, 545575, 1431017]:
    r = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}", headers=h)
    print("\nID", tmdb_id, "status", r.status_code)
    if r.ok:
        j = r.json()
        print("title=", j.get("title"), "release_date=", j.get("release_date"))
    else:
        print("movie body:", r.text[:200])

    rc = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits", headers=h)
    if rc.ok:
        print("credits status", rc.status_code, "cast_len", len(rc.json().get("cast", [])))
    else:
        print("credits status", rc.status_code, "body", rc.text[:200])

