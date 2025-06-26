# movies
create .env file in movies folder with:\
\
`POSTGRES_DB=movies_db\
POSTGRES_USER=movies_user\
POSTGRES_PASSWORD=******* (add password)\
\
PG_HOST=localhost\
PG_PORT=5433\
PG_DB=${POSTGRES_DB}\
PG_USER=${POSTGRES_USER}\
PG_PASSWORD=${POSTGRES_PASSWORD}\`


\
First run `docker compose up -d --build` from movies folder\
then run `python tmdb_list_export.py` to get my movie list (to change list see file)\
The seen movies list can be saved with:\
`psql -U movies_user -d movies_db -p 5433 -c "COPY (SELECT 'INSERT INTO seen_movies (movie_id) VALUES (' || movie_id || ');' FROM seen_movies) TO STDOUT" > init_seen.sql`\
\
Go to frontend\
`npm install`\
`npm run dev`
