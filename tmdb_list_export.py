from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import csv, time, re, db, requests
import json


SIZE_RE = re.compile(r"^/t/p/[^/]+/")

options = Options()
options.add_argument("--headless=new")  # use "new" for new Chrome headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

db.init_schema()

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

YEAR_ANY_RE = re.compile(r'\b(19|20)\d{2}\b')

# ---------- litle helper for year ----------
def extract_year_from_text(txt:str) -> int | None:
    # Matches 4-digits ie 1920 or 2001"
    m = YEAR_ANY_RE.search(txt or "")
    if not m:
        return None
    y = int(m.group(0))
    return y if 1900 <= y <= 2100 else None

# ---------- litle helper for synopsis ----------
def fetch_description_and_poster(rel_url: str) -> tuple[str, str | None, int | None]:
    url = f"https://www.themoviedb.org{rel_url}"
    r = requests.get(url, timeout=10,
                     headers={"User-Agent": "TMDB-scraper/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # --- description / overview ---
    p = soup.select_one("div.overview p")
    description = p.get_text(strip=True) if p else ""

    # --- poster path ---

    src = None

    # 1) prefer meta-tag (almost always exist)
    meta = soup.select_one("meta[property='og:image']")
    if meta and meta.get('content'):
        src = meta["content"]

    # 2) or <img class="poster">
    if not src:
        img = soup.select_one("img.poster")
        if img:
            if img.get("srcset"):
                src = img["srcset"].split(",")[-1].split()[0].strip()
            else:
                src = img.get("src")

    # 3) make clean /t/p/sti
    poster_path = None
    if src:
        rel = urlparse(src).path
        poster_path = SIZE_RE.sub("/t/p/", rel)
    
    # 4) -- get year from description
    year_detail = None
    
    for sc in soup.select("script[type='application/ld+json']"):
        try:
            data = json.loads(sc.string or "")
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for it in items:
            if isinstance(it, dict) and it.get("@type") == "Movie":
                date_str = (
                    it.get("datePublished")
                    or it.get("dateCreated")
                    or (it.get("releasedEvent") or {}).get("startDate")
                    or ""
                )
                y = extract_year_from_text(date_str)
                if y:
                    year_detail = y
                    break
        if year_detail:
            break
            
    # last fallback: first year on page
    if year_detail is None:
        y = extract_year_from_text(soup.get_text(" ", strip=True))
        if y:
            year_detail = y
    
    return description, poster_path, year_detail

results = []
batch = []
page = 1
print("Starter Selenium scraping...")

while True:
    url = f"https://www.themoviedb.org/list/8531258-my-movies?page={page}"
    print(f"Henter side {page}: {url}")
    driver.get(url)

    # Accept cookies if necessary
    try:
    # Wait until the first film-rows are present
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".list_items > div[id]")
            )
        )
        rows = driver.find_elements(By.CSS_SELECTOR, ".list_items div[id][class*='table-row']")
    except:
        print("❌ Ingen filmrækker fundet – stopper.")
        break

    if not rows:
        break
    
    for row in rows:
        try:
            # title + TMDB-link
            link  = row.find_element(By.CSS_SELECTOR, "a[href^='/movie/']")
        except NoSuchElementException:
            # if no film-row, skip
            continue
        
        title = link.text.strip()
        rel_url = link.get_attribute("href").replace(
            "https://www.themoviedb.org",""
        )


        txt   = row.text

        # --- year ---
        year_from_list  = extract_year_from_text(txt)

        # rating: (NR or NN)
        rating = ""
        try:
            # 1) normal icon-r
            icon   = row.find_element(By.CSS_SELECTOR, "span[class*='icon-r']")
            m = re.search(r'icon-r(\d+)', icon.get_attribute("class") or "")
            if m:
                rating = m.group(1) 
        except NoSuchElementException:
            pass
        
        if rating == "":
            try:
                row.find_element(By.CSS_SELECTOR, "span[class*='icon-nr']")
                rating = "NR"
            except NoSuchElementException:
                pass

        # description and poster
        description, poster_path, year_detail = fetch_description_and_poster(rel_url)
        year_final = year_from_list or year_detail

        batch.append((
            title,
            year_final,
            rating or None,
            description,
            poster_path,
            rel_url
        ))

    print(f"✅ Found {len(rows)} films on page {page}")
    page += 1
    time.sleep(0.5)

driver.quit()



# Save in db
db.insert_movies(batch)
batch.clear()

# Save as CSV
# with open("tmdb_my_movies.csv", "w", newline='', encoding="utf-8") as csvfile:
#     writer = csv.DictWriter(csvfile, fieldnames=["Title", "Year", "Rating", "Description"])
#     writer.writeheader()
#     writer.writerows(results)

# print(f"\n✅ Done! {len(results)} films saved in 'tmdb_my_movies.csv'")
