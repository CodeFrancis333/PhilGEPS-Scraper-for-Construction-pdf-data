"""
philgeps_boq_pdf_scraper.py                        2025-06-23
---------------------------------------------------------------------------
- Sweeps from ANCHOR_ID downward for BACKWARD_WINDOW IDs
- Accepts notice if Category = "Construction Projects" OR
  Title contains construction|building|structural
- If a BOQ attachment PDF exists, downloads and parses it
  otherwise (if Playwright is available) prints the whole page to PDF
- All PDFs are zipped; BOQ PDFs are also converted to CSV
- Keeps ZIP+CSV storage ≤ MAX_BYTES (20 GiB)
"""

# ---------- USER SETTINGS ------------------------------------------
ANCHOR_ID        = 10098537
BACKWARD_WINDOW  = 10000
MAX_MISSES_IN_A_ROW = 600

RAW_DIR          = "boq_raw"
CLEAN_DIR        = "boq_clean"
MAX_BYTES        = 20 * 1024**3
DELETE_RAW_PDF   = True
STOP_WHEN_FULL   = False
ROLLING_PRUNE    = not DELETE_RAW_PDF and not STOP_WHEN_FULL

USER_AGENT       = "PH-BOQ-Scraper (contact: sudocode693@gmail.com)"
SLEEP_SEC        = 1
TITLE_REGEX      = r"\b(construction|building|structural)\b"
# -------------------------------------------------------------------

import os, re, time, zipfile, traceback, requests, pandas as pd
from bs4 import BeautifulSoup
import tabula, camelot

# ----- Playwright import guard -------------------------------------
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    def sync_playwright():
        raise RuntimeError("Playwright is not installed; install with "
                           "`pip install playwright && playwright install chromium`")

# -------------------------------------------------------------------

TITLE_RE = re.compile(TITLE_REGEX, re.I)
ATTACH_RE = re.compile(r"(bill.*quantities|schedule.*prices|boq).*\.pdf$", re.I)

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)


def dir_size(*paths):
    return sum(os.path.getsize(os.path.join(r, f))
               for p in paths for r, _, fs in os.walk(p) for f in fs)


def maybe_prune():
    total = dir_size(RAW_DIR, CLEAN_DIR)
    if total <= MAX_BYTES:
        return
    zips = sorted((os.path.join(RAW_DIR, z) for z in os.listdir(RAW_DIR)
                   if z.endswith(".zip")), key=os.path.getmtime)
    for z in zips:
        if total <= MAX_BYTES:
            break
        total -= os.path.getsize(z)
        os.remove(z)
        print("Pruned", os.path.basename(z))


def parse_pdf(pdf):
    stem = os.path.splitext(os.path.basename(pdf))[0]
    try:
        dfs = tabula.read_pdf(pdf, pages="all", lattice=True, multiple_tables=True)
        if not dfs:
            raise ValueError
        df = pd.concat(dfs, ignore_index=True)
    except Exception:
        try:
            dfs = camelot.read_pdf(pdf, pages="all", flavor="stream")
            df = pd.concat([t.df for t in dfs], ignore_index=True)
        except Exception as e:
            print("Parse failed:", e)
            return
    df = df.dropna(how="all").loc[:, ~df.isna().all()]
    df.to_csv(os.path.join(CLEAN_DIR, f"{stem}.csv"), index=False)
    print("CSV saved")


def save_notice_pdf(url, out_path):
    if not PLAYWRIGHT_AVAILABLE:
        return False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.pdf(path=out_path, format="A4")
            browser.close()
        print("Page PDF saved")
        return True
    except Exception as e:
        print("Playwright error:", e)
        return False


def is_construction(soup):
    cat = soup.find(string=re.compile(r"Category", re.I))
    if cat:
        if cat.find_next().get_text(" ", strip=True).lower().startswith("construction projects"):
            return True
    title = soup.find(string=re.compile(r"Project\s*Title", re.I))
    if title and TITLE_RE.search(title.find_next().get_text(" ", strip=True)):
        return True
    return False


def process_id(bid, session):
    if len(bid) != 8 or not bid.isdigit():
        return False
    if STOP_WHEN_FULL and dir_size(RAW_DIR, CLEAN_DIR) >= MAX_BYTES:
        print("Storage cap reached. Stopping.")
        return None

    url = ("https://notices.philgeps.gov.ph/GEPSNONPILOT/Tender/"
           f"PrintableBidNoticeAbstractUI.aspx?refID={bid}")
    soup = BeautifulSoup(session.get(url, timeout=30).text, "html.parser")

    if not soup.find(string=re.compile(r"Project\s*Title", re.I)) \
       and not soup.find(string=re.compile(r"Category", re.I)):
        return False

    if not is_construction(soup):
        print("Skip", bid, "- not construction")
        return True

    link = next((a["href"] for a in soup.select("a")
                 if ATTACH_RE.search(a.get("href", ""))), None)

    if link:
        pdf_url = requests.compat.urljoin(url, link)
        size = int(session.head(pdf_url, timeout=30).headers.get("Content-Length", 0))
        if ROLLING_PRUNE and dir_size(RAW_DIR, CLEAN_DIR) + size > MAX_BYTES:
            maybe_prune()
        pdf_path = os.path.join(RAW_DIR, f"{bid}_{os.path.basename(link).replace(' ','_')}")
        print("Downloading BOQ PDF for", bid)
        with session.get(pdf_url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(pdf_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
        parse_pdf(pdf_path)
    else:
        if not PLAYWRIGHT_AVAILABLE:
            print("Skip", bid, "- no BOQ PDF and Playwright not available")
            return True
        pdf_path = os.path.join(RAW_DIR, f"{bid}_notice.pdf")
        print("Printing page for", bid)
        if not save_notice_pdf(url, pdf_path):
            return True

    zip_path = pdf_path + ".zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(pdf_path, arcname=os.path.basename(pdf_path))
    if DELETE_RAW_PDF:
        os.remove(pdf_path)
    return True


def scrape(anchor, window):
    ids = [str(i) for i in range(anchor, anchor - window - 1, -1)]
    ses = requests.Session()
    ses.headers["User-Agent"] = USER_AGENT
    misses = 0
    for bid in ids:
        try:
            res = process_id(bid, ses)
            if res is None:
                break
            if res is False:
                misses += 1
                if misses >= MAX_MISSES_IN_A_ROW:
                    print("Too many placeholders. Aborting.")
                    break
            else:
                misses = 0
            time.sleep(SLEEP_SEC)
        except KeyboardInterrupt:
            break
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    end_id = max(10000000, ANCHOR_ID - BACKWARD_WINDOW)
    print("Sweeping", ANCHOR_ID, "down to", end_id,
          "-", BACKWARD_WINDOW + 1, "IDs")
    scrape(ANCHOR_ID, BACKWARD_WINDOW)
