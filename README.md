![Banner](/frontend/src/assets/🍿 _ _movies _⋆⋆⋆⋆⋆%20(5).png)
# Movies (V2)
#### A small full-stack app that imports your TMDB list into a PostgreSQL database and lets you browse movies, mark them as seen, and import cast + actor bios.

## Stack
- Frontend: React (Vite)
- Backend: FastAPI (Uvicorn)
- DB: PostgreSQL (Docker)
- Migrations: Flyway (Docker)
- Scraper: Selenium (Docker) used for TMDB list export (bypasses TMDB list API limits)

---
## Prerequisites
- Docker + Docker Compose
- Node.js (if you want to run frontend without Docker; optional)
- Git (optional)

---

## 1. Download the code
Option A (recommended): clone with Git:
```bash
git clone git@github.com:djarnis2/movies.git
cd movies
```
Option B: download ZIP from GitHub and unzip it, then open the folder.

## 2. TMDB account

You need to make an account at TMDB. Here you can make a list of movies or you can use my list as default. You will also need to get a token.

https://www.themoviedb.org/signup

Make your acount, apply for API key. Go through the process. Copy the `API Read Access Token` for later.



## 2. Make your own list

https://www.themoviedb.org/list/new


## 3. Create `.env` file in root folder
Create a file named `.env` in the root folder:

`POSTGRES_DB=movies_db` Or use your own databasename\
`POSTGRES_USER=movies_user` Or use your own username\
`POSTGRES_PASSWORD=*******` Use your own password

`VITE_MOVIES_API=http://localhost:8000` Or use another url
`TMDB_TOKEN=` Insert token 
`TMDB_LIST_ID=8531258` Or insert your own list ID

## 5. Start Docker

Run `docker compose up -d --build` from root folder\

What happens:

* Postgres starts and creates DB/user from POSTGRES_* (first run only)

* Flyway runs DB migrations

* Selenium starts (headless Chrome)

* Backend starts on http://localhost:8000

* Frontend starts on http://localhost:5173

## 5. Open the app 
Open your browser at http://localhost:5173 \

When the app is up and running, it will be empty at first. Go to the import page and import from list (leave blank to import from the list in env)

This will take some time, so be patient and wait until finished. There is a timer so you can see the import is at work.

After this you can choose to import actors and their bios. This will also take some time, especially bios if you choose more than 10 actors per movie

## 6. Make script for automatic start with docker desktop

In this script docker desktop is installed in the folder:\
`C:\Program Files\Docker\Docker\Docker`\
Change the script to the relevant folder.\

The project folder is:\
`C:\Projects\ReactProjects\movies`\
Also change this accordingly..

```bash
@echo off

:: Uses local variables
setlocal
:: Check if dokcer desktop is up, if the daemon responds
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Docker Desktop is not up.
    echo Shutting down all Docker Desktop related processes...
    taskkill /F /IM "Docker Desktop.exe"
    taskkill /F /IM "com.docker.backend.exe"
    taskkill /F /IM "com.docker.build.exe"
    taskkill /F /IM "com.docker.dev-envs.exe"
    echo All Docker-processes attempted to be terminated.

    :: Start Docker Desktop
    echo Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    pause
) else (
    echo Docker Desktop is already up.
)

:: Wait for Docker Desktop
:waitloop
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    timeout /t 2 >nul
    goto waitloop
)

:: Go to project folder
cd C:\Projects\ReactProjects\movies

:: Start Docker Containers
docker compose up -d

:: Open browser
start http://localhost:5173/

```

