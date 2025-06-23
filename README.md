PhilGEPS BOQ Scraper

A Python 3.11 command‑line tool that bulk‑downloads Bill‑of‑Quantities (BOQ) files from the Philippine Government Electronic Procurement System (PhilGEPS). <br>
"Exports Construction Projects PDF automatically from PhilGEPS website."

Features
1. BOQ download & parse - Detects PDF/XLS BOQ attachments, converts them to tidy CSV (Tabula‑py → Camelot fallback). <br>
2. Playwright fallback - If a notice has no BOQ attachment, the entire page is printed to PDF headlessly. <br>
3. Polite scraping - Configurable sleep interval (SLEEP_SEC) and storage cap (20 GiB by default) to avoid hammering PhilGEPS. <br>
4. Category/title filter - Only grabs Construction Projects or titles containing construction, building, or structural. <br>
5. Rolling prune / hard stop - Keeps disk usage predictable on long runs.

Project Structure
philgeps_scraper/
├─ .venv/               # local virtual‑env (ignored by Git)
├─ boq_raw/             # downloaded PDFs or page‑print PDFs (git‑ignored)
├─ boq_clean/           # extracted CSVs (git‑ignored)
├─ philgeps_boq_pdf_scraper.py  # main script
├─ requirements.txt     # exact package pins
└─ README.md            # this file

Requirements
Python: 3.11 (Async‑safe Playwright & modern pandas)
Java: 8 u181 (Needed by Tabula‑py)
Playwright: 1.43.0 (Headless Chromium printing)
Chromium (Playwright): python -m playwright install chromium

All Python packages are pinned in requirements.txt.

Quick Start
# 1) clone & enter folder
git clone https://github.com/<your‑user>/philgeps_scraper.git
cd philgeps_scraper

# 2) create & activate venv (Windows example)
python -m venv .venv
.\.venv\Scripts\activate

# 3) install dependencies
pip install -r requirements.txt
python -m playwright install chromium

# 4) run a 300‑ID smoke test (edit constants in the script)
python philgeps_boq_pdf_scraper.py

The first log lines should look like:

Sweeping 11491800 down to 11491500 - 301 IDs
Downloading BOQ PDF for 11491742
PDF saved
CSV saved

Configuration
All tweakable constants live near the top of philgeps_boq_pdf_scraper.py.
ANCHOR_ID: First bidNoticeId to process (8 digits): e.g. 11491800
BACKWARD_WINDOW: How many IDs to scan below the anchor: 300 … 20000
SLEEP_SEC: Delay per thread between requests: 0.3 – 1
STOP_WHEN_FULL: Hard‑stop when disk cap hit: True for cron jobs
ROLLING_PRUNE: Delete oldest ZIPs once over cap: True when archiving

Contributing
Pull requests are welcome!  Please open an issue first if you plan major changes (multi‑process downloads, database back‑end, etc.) so we can discuss architecture.
