from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import csv, time, re, db, requests


SIZE_RE = re.compile(r"^/t/p/[^/]+/")

options = Options()
options.add_argument("--headless=new")  # brug "new" for ny Chrome headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

db.init_schema()

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# ---------- lille helper til årstal ----------
def extract_year_from_text(txt):
    # Matcher fx: "17. januar 2020", "25 December 1999", "3 april 2018"
    match = re.search(
    r'\b\d{1,2}[.\s\-]?\s?(januar|februar|marts|april|maj|juni|juli|august|september|oktober|november|december)\s((19|20)\d{2})\b',
    txt, re.IGNORECASE)
    if match:
        return match.group(2)  # årstallet
    return None

# ---------- lille helper til synopsis ----------
def fetch_description_and_poster(rel_url: str) -> tuple[str, str | None]:
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

    # 1) helst meta-tag (findes næsten altid)
    meta = soup.select_one("meta[property='og:image']")
    if meta:
        src = meta["content"]

    # 2) ellers <img class="poster">
    if not src:
        img = soup.select_one("img.poster")
        if img.get("srcset"):
            src = img["srcset"].split(",")[-1].split()[0].strip()
        else:
            src = img.get("src")
    # 3) lav ren /t/p/sti
    poster_path = None
    if src:
        rel = urlparse(src).path
        poster_path = SIZE_RE.sub("/t/p/", rel)
    

    return description, poster_path

results = []
batch = []
page = 1
print("Starter Selenium scraping...")

while True:
    url = f"https://www.themoviedb.org/list/8531258-my-movies?page={page}"
    print(f"Henter side {page}: {url}")
    driver.get(url)

    # Accepter cookies hvis nødvendigt
    try:
    # vent til de første filmrækker er til stede
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
            # titel + TMDB-link
            link  = row.find_element(By.CSS_SELECTOR, "a[href^='/movie/']")
        except NoSuchElementException:
            # ikke en filmrække, spring over
            continue
        
        title = link.text.strip()
        rel_url = link.get_attribute("href").replace(
            "https://www.themoviedb.org",""
        )


        txt   = row.text

        # --- år ---
        year_text  = extract_year_from_text(txt)
        year = int(year_text) if year_text else None

        # rating: (NR eller NN)
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

        # beskrivelse og poster
        description, poster_path = fetch_description_and_poster(rel_url)

        batch.append((
            title,
            year,
            rating or None,
            description,
            poster_path,
            rel_url
        ))

    print(f"✅ Fandt {len(rows)} film på side {page}")
    page += 1
    time.sleep(0.5)

driver.quit()



# Gem i db
db.insert_movies(batch)
batch.clear()

# Gem som CSV
# with open("tmdb_my_movies.csv", "w", newline='', encoding="utf-8") as csvfile:
#     writer = csv.DictWriter(csvfile, fieldnames=["Title", "Year", "Rating", "Description"])
#     writer.writeheader()
#     writer.writerows(results)

# print(f"\n✅ Færdig! {len(results)} film gemt i 'tmdb_my_movies.csv'")


