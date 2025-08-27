![Banner](/frontend/src/assets/🍿 _ _movies _⋆⋆⋆⋆⋆%20(5).png)
# Movies

## 1. Create `.env` file in root folder

`POSTGRES_DB=movies_db`\
`POSTGRES_USER=movies_user`\
`POSTGRES_PASSWORD=*******` # use your own password

`PG_HOST=localhost`\
`PG_PORT=5433`\
`PG_DB=${POSTGRES_DB}`\
`PG_USER=${POSTGRES_USER}`\
`PG_PASSWORD=${POSTGRES_PASSWORD}`

## 2. Start database

Run `docker compose up -d --build` from root folder\
Run `python tmdb_list_export.py` # to change list (see file line 77) ! This is a scraper (usefull because the api doesn't allow more than 20 movies)  and it will take about 40 sec per page (50 movies)

## 3. Install requirements for python

Go to backend and install the requirents:\
`cd backend` \
`pip install -r requirements.txt`

## 4. Start backend

Go back to root folder and start the backend from here (db.py is in root folder and is required for this step)\
`cd ..` \
`uvicorn backend.api:app --host 0.0.0.0 --port 8000`

## 5. Start frontend

Open a new terminal, go to frontend and start the fronted with:\
`cd frontend`\
`npm install`\
`npm run dev`

## 6. Open app in localhost

open page with:
`http://localhost:5175/`

## 7. Next time (quick start)

* `docker compose up -d`
* `uvicorn backend.api:app --host 0.0.0.0 --port 8000`
* `cd frontend`\
`npm install`\
`npm run dev`

## 8. The app keeps two lists

* A. The complete list of movies you own (Or mine, if you didn.t change list).\
* B. A smaller list with those movies you havn't seen -You can mark a movie as seen, to remove it from this list.\

The `seen_movies` list can be exported to `init_seen.sql`:
```bash
psql -U movies_user -d movies_db -p 5433 -c "COPY (SELECT 'INSERT INTO seen_movies (movie_id) VALUES (' || movie_id || ');' FROM seen_movies) TO STDOUT" > init_seen.sql
```

And it can then later be restored from that `init_seen.sql` file with:

```bash
psql -U movies_user -d movies_db -p 5433 -f init_seen.sql
```


## 9. Make your own list
https://www.themoviedb.org/list/new

# Known issues
The scraper currently sometimes causes doubles