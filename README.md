<h1>PhilGEPS BOQ Scraper</h1>

A Python 3.11 command‑line tool that bulk‑downloads Bill‑of‑Quantities (BOQ) files from the Philippine Government Electronic Procurement System (PhilGEPS). <br>
<em>"Exports Construction Projects PDF automatically from PhilGEPS website."</em>

<h2>Features</h2>
1. BOQ download & parse - Detects PDF/XLS BOQ attachments, converts them to tidy CSV (Tabula‑py → Camelot fallback). <br>
2. Playwright fallback - If a notice has no BOQ attachment, the entire page is printed to PDF headlessly. <br>
3. Polite scraping - Configurable sleep interval (SLEEP_SEC) and storage cap (20 GiB by default) to avoid hammering PhilGEPS. <br>
4. Category/title filter - Only grabs Construction Projects or titles containing construction, building, or structural. <br>
5. Rolling prune / hard stop - Keeps disk usage predictable on long runs.

<h2>Project Structure</h2>
philgeps_scraper/ <br>
├─ .venv/               # local virtual‑env (ignored by Git)<br>
├─ boq_raw/             # downloaded PDFs or page‑print PDFs (git‑ignored)<br>
├─ boq_clean/           # extracted CSVs (git‑ignored)<br>
├─ philgeps_boq_pdf_scraper.py  # main script<br>
├─ requirements.txt     # exact package pins<br>
└─ README.md            # this file<br>

<h2>Requirements</h2>
Python: 3.11 (Async‑safe Playwright & modern pandas)
Java: 8 u181 (Needed by Tabula‑py)
Playwright: 1.43.0 (Headless Chromium printing)
Chromium (Playwright): python -m playwright install chromium

All Python packages are pinned in requirements.txt.

<h2>Quick Start</h2>
<pre>
  
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
</pre>

The first log lines should look like:
<pre><strong>
Sweeping 11491800 down to 11491500 - 301 IDs
Downloading BOQ PDF for 11491742
PDF saved
CSV saved
</strong></pre>

<h3>Configuration</h3>
<em>All tweakable constants live near the top of philgeps_boq_pdf_scraper.py.<br></em>
ANCHOR_ID: First bidNoticeId to process (8 digits): e.g. 11491800<br>
BACKWARD_WINDOW: How many IDs to scan below the anchor: 300 … 20000<br>
SLEEP_SEC: Delay per thread between requests: 0.3 – 1<br>
STOP_WHEN_FULL: Hard‑stop when disk cap hit: True for cron jobs<br>
ROLLING_PRUNE: Delete oldest ZIPs once over cap: True when archiving<br>

Contributing
Pull requests are welcome!  Please open an issue first if you plan major changes (multi‑process downloads, database back‑end, etc.) so we can discuss architecture.
