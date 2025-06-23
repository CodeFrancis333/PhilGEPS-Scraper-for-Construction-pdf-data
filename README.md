<h1>PhilGEPS BOQ Scraper</h1>

<p>A Python 3.11 command‑line tool that bulk‑downloads PDF files from the Philippine Government Electronic Procurement System (PhilGEPS). <br></p>
<em>"Exports Construction Projects PDF automatically from PhilGEPS website."</em>

<h2>Features</h2>
<ol>
<li><strong>BOQ download & parse:</strong> Detects PDF/XLS BOQ attachments, converts them to tidy CSV (Tabula‑py → Camelot fallback). </li>
<li><strong>Playwright fallback:</strong> If a notice has no BOQ attachment, the entire page is printed to PDF headlessly. </li>
<li><strong>Polite scraping:</strong> Configurable sleep interval (SLEEP_SEC) and storage cap (20 GiB by default) to avoid hammering PhilGEPS. </li>
<li><strong>Category/title filter:</strong> Only grabs Construction Projects or titles containing construction, building, or structural. </li>
</ol>

<h2>Project Structure</h2>
philgeps_scraper/ <br>
├─ .venv/               # local virtual‑env (ignored by Git)<br>
├─ boq_raw/             # downloaded PDFs or page‑print PDFs (git‑ignored)<br>
├─ boq_clean/           # extracted CSVs (git‑ignored)<br>
├─ philgeps_boq_pdf_scraper.py  # main script<br>
├─ requirements.txt     # exact package pins<br>
└─ README.md            # this file<br>

<h2>Requirements</h2>
<ul>
<li><strong>Python:</strong> 3.11 (Async‑safe Playwright & modern pandas)</li>
<li><strong>Java:</strong> 8 u181 (Needed by Tabula‑py)</li>
<li><strong>Playwright:</strong> 1.43.0 (Headless Chromium printing)</li>
<li><strong>Chromium (Playwright):</strong> python -m playwright install chromium</li>
</ul>

All Python packages are pinned in requirements.txt.

<h2>Quick Start</h2>
<pre>
  
# 1) clone & enter folder
git clone (https://github.com/CodeFrancis333/PhilGEPS-Scraper-for-Construction-pdf-data.git)
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
<ul>
<li><strong>ANCHOR_ID:</strong> First bidNoticeId to process (8 digits): <em>e.g. 11491800</em></li>
<li><strong>BACKWARD_WINDOW:</strong> How many IDs to scan below the anchor: <em>300 … 20000</em></li>
<li><strong>SLEEP_SEC:</strong> Delay per thread between requests: <em>0.3 – 1</em></li>
<li><strong>STOP_WHEN_FULL:</strong> Hard‑stop when disk cap hit: <em>True for cron jobs</em></li>
<li><strong>ROLLING_PRUNE:</strong> Delete oldest ZIPs once over cap: <em>True when archiving</em></li>
</ul>
