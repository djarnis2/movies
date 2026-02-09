from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time, re, db, requests, random, json, os, sys


SIZE_RE = re.compile(r"^/t/p/[^/]+/")

options = Options()
options.add_argument("--headless=new")  # use "new" for new Chrome headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "TMDB-scraper/1.0"})

db.init_schema()

tmdb_list = None
if len(sys.argv) >= 2:
    tmdb_list = sys.argv[1]

if not tmdb_list:
    tmdb_list = os.getenv("TMDB_LIST_ID")

if not tmdb_list:
    raise SystemExit("Missing TMDB_LIST_ID (env) and no listId argument provided")


limit = int(sys.argv[2]) if len(sys.argv) >= 3 else 0 # 0 = no limit

count = 0

remote_url = os.getenv("SELENIUM_REMOTE_URL") 
if remote_url:
    driver = webdriver.Remote(command_executor=remote_url, options=options)
else:
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

# ---------- helper for fetch_description_and_poster() --------

def get_with_retry(url: str, max_tries: int = 8, base_sleep: float = 2.0, timeout: int = 30):
    for attempt in range(1, max_tries + 1):
        r = SESSION.get(url, timeout=timeout)

        # 429: wait and retry (honor Retry-After if present)
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            if retry_after:
                sleep_s =  float(retry_after)
            else:
                sleep_s = base_sleep * (2 ** (attempt - 1))
            
            # add a bit of jitter
            sleep_s += random.uniform(0, 1.0)
            print(f" ⚠️ 429 from TMDB, sleeping {sleep_s:.1f}s (attempt {attempt}/{max_tries})")
            sleep_s = min(sleep_s, 60)
            time.sleep(sleep_s)
            continue

        r.raise_for_status()

        time.sleep(0.35 + random.random() * 0.65)
        return r

    raise RuntimeError(f"Too many requests (429) after {max_tries} tries: {url}")


# ---------- litle helper for synopsis ----------

def fetch_description_and_poster(rel_url: str) -> tuple[str, str | None, int | None]:
    url = f"https://www.themoviedb.org{rel_url}"
    r = get_with_retry(url, timeout=10)
    
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
throttle_hits = 0

print("Starting Selenium scraping...")

while True:
    url = f"https://www.themoviedb.org/list/{tmdb_list}?page={page}"
    print(f"Fetching page {page}: {url}")
    driver.get(url)
    html = driver.page_source.lower()

    if "temporarily throttled" in html or "wait and try again" in html:
        throttle_hits += 1
        sleep_s = min(30 * throttle_hits, 300)
        print(f"⚠️ TMDB throttled (429 page). Sleeping {sleep_s}s then retrying...")
        time.sleep(sleep_s)
        if throttle_hits >= 5:
            print("❌ Too many throttles. Aborting.")
            break
        continue
    throttle_hits = 0


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
        print("❌ No futher movie-rows found – stopping.")
        break

    if not rows:
        break
    
    added_movies_this_page = 0
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
        count += 1
        added_movies_this_page += 1

        if limit and count >= limit:
            break

    print(f"✅ Found {added_movies_this_page} movies on page {page} (total {count})")

    if limit and count >= limit:
        print(f"🛑 Limit reached ({limit}), stopping.")
        break

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
