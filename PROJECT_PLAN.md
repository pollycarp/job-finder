# Nairobi Tech Job Tracker — Phased Implementation Plan

## Project Overview

An autonomous system that scrapes daily tech job postings (Data Science, AI/ML, Frontend, Fullstack)
from Fuzu, MyJobMag, and Brighter Monday for Nairobi, Kenya. Runs every day at midnight (EAT),
saves results to Google Sheets, and requires zero manual intervention after deployment.

---

## Tool Stack

| Layer              | Tool                              | Cost |
|--------------------|-----------------------------------|------|
| Language           | Python 3.10+                      | Free |
| Scraping (static)  | requests + BeautifulSoup4         | Free |
| Scraping (dynamic) | playwright                        | Free |
| Google Sheets      | gspread + Google Sheets API       | Free |
| Scheduler/Runner   | GitHub Actions                    | Free (2,000 min/month) |
| Secrets management | GitHub Actions Secrets            | Free |
| Alerting           | GitHub email notifications        | Free |

---

## Google Sheet Column Schema

| Column      | Description                                      |
|-------------|--------------------------------------------------|
| Date Found  | Date the job was scraped                         |
| Job Title   | Position name                                    |
| Company     | Employer name                                    |
| Location    | e.g., Nairobi, Kenya                             |
| Category    | Data Science / ML / Frontend / Fullstack         |
| Source      | Fuzu / Myjobmag / BrighterMonday                 |
| Job URL     | Direct link to the listing                       |
| Date Posted | Posting date from the site (if available)        |

---

## Phase 1: Environment & Infrastructure Setup

**Goal:** Get a stable, free development and deployment environment ready.

### Steps:
1. Choose a free hosting platform — use GitHub Actions (free tier: 2,000 mins/month) as the
   scheduler and runner. No server needed.
2. Create a GitHub repository to house all project code.
3. Set up Python environment — Python 3.10+, pip, and venv.
4. Set up a Google Cloud project (free) and enable the Google Sheets API and Google Drive API.
5. Create a Google Service Account, download the JSON credentials key, and share your target
   Google Sheet with that service account email.
6. Store secrets (Google credentials JSON, Sheet ID) as GitHub Actions Secrets — never hardcoded.

### Deliverables:
- GitHub repo created and cloned locally
- Google Cloud project with Sheets API enabled
- Service account key downloaded
- GitHub Actions Secrets configured

---

## Phase 2: Google Sheets Integration Module

**Goal:** Build the module that writes job data to Google Sheets reliably.

### Steps:
1. Install gspread and google-auth libraries.
2. Write a `sheets_client.py` module that:
   - Authenticates via the service account key
   - Opens the target spreadsheet by ID
   - Appends rows to the correct sheet tab
   - Deduplicates jobs using the job URL as a unique key (reads existing URLs before writing)
3. Define the column schema (see table above).
4. Write unit tests for the Sheets module using mock data.

### Key Libraries:
- gspread
- google-auth
- pytest (for testing)

### Deliverables:
- `sheets_client.py` — authentication, read, write, deduplicate
- `tests/test_sheets.py` — unit tests with mock data
- Google Sheet created with correct headers

---

## Phase 3: Scraper Development — Site by Site

**Goal:** Build individual, robust scrapers for each of the three job boards.

### General Approach Per Scraper:
- Start with requests + BeautifulSoup4 (fast, lightweight)
- Fall back to playwright (headless browser, free) if the site is JavaScript-heavy/SPA
- Each scraper filters by: today's date, Nairobi location, and target job categories
- Randomized delays between requests (1–3 seconds) to avoid rate limiting
- Retry logic with exponential backoff (3 retries max)
- Graceful error handling — a failing scraper logs the error but does not crash the pipeline

### Target Job Categories:
- Data Science
- Artificial Intelligence / Machine Learning
- Frontend Developer
- Fullstack Developer

---

### Phase 3A — Brighter Monday Scraper

- URL pattern: https://www.brightermonday.co.ke/jobs/[category]?location=nairobi
- Categories to search: IT / Software, Data Science
- Parse job cards for: title, company, location, date posted, URL
- Filter to jobs posted today only

**Deliverable:** `scrapers/brighter_monday.py`

---

### Phase 3B — MyJobMag Scraper

- URL pattern: https://www.myjobmag.co.ke/jobs-in/nairobi
- Search across relevant tech categories
- Handle pagination if needed
- Filter to jobs posted today only

**Deliverable:** `scrapers/myjobmag.py`

---

### Phase 3C — JobWebKenya Scraper

> Note: Fuzu was replaced with JobWebKenya — Fuzu returns 403 Forbidden for all automated requests.

- URL pattern: https://jobwebkenya.com/?s={query} and https://jobwebkenya.com/page/{n}/?s={query}
- WordPress-based, server-side rendered (requests + BeautifulSoup)
- Filter by Nairobi location and today's date
- Filter to jobs posted today only

**Deliverable:** `scrapers/jobwebkenya.py`

---

## Phase 4: Orchestration Pipeline

**Goal:** Wire all scrapers together into a single runnable pipeline.

### Steps:
1. Create `main.py` — the entry point that:
   - Calls each scraper in sequence (or in parallel using concurrent.futures)
   - Aggregates all job results into a single list
   - Deduplicates across sources by URL
   - Passes results to the Sheets module
2. Add structured logging (Python logging module) — every run produces a timestamped log.
3. Add a run summary report (e.g., "Found 12 new jobs: 4 from Fuzu, 5 from BrighterMonday, 3 from MyJobMag").
4. Handle the edge case of zero results gracefully (log it, don't write empty rows).

### Key Libraries:
- Python standard library (logging, concurrent.futures)
- python-dotenv (for local development environment variables)

### Deliverables:
- `main.py` — full pipeline orchestrator
- `requirements.txt` — all dependencies pinned
- `.env.example` — template for local environment variables

---

## Phase 5: Scheduling with GitHub Actions

**Goal:** Make the system run automatically every day at midnight Nairobi time (EAT = UTC+3, so 9 PM UTC).

### Steps:
1. Create `.github/workflows/job_scraper.yml` with the following schedule:
   ```yaml
   on:
     schedule:
       - cron: '0 21 * * *'   # 9 PM UTC = Midnight Nairobi time (EAT)
     workflow_dispatch:         # Also allow manual runs for testing
   ```
2. The workflow:
   - Checks out the repository
   - Sets up Python
   - Installs dependencies from requirements.txt
   - Injects secrets as environment variables
   - Runs python main.py
   - Uploads the log file as a workflow artifact (viewable in GitHub UI)
3. Test with workflow_dispatch (manual trigger) to confirm end-to-end flow before relying on the schedule.

### Deliverables:
- `.github/workflows/job_scraper.yml`
- Confirmed manual run success in GitHub Actions UI

---

## Phase 6: Error Alerting & Notifications

**Goal:** Get notified if the pipeline fails without manually checking GitHub every day.

### Options (all free):

**Option A — GitHub Email Notifications (Zero setup, recommended first)**
- GitHub automatically emails you if a scheduled workflow fails
- Enable in: GitHub account Settings > Notifications > Actions

**Option B — Telegram Bot**
- Create a free Telegram bot via @BotFather
- Add a GitHub Actions step to POST to the Telegram API on success or failure
- Sends a daily summary message directly to your Telegram

**Option C — Gmail via SMTP**
- Use Python's smtplib with a Gmail App Password
- Email yourself a formatted daily summary after each run

### Recommendation:
Start with Option A (GitHub failure emails, zero effort). Add Option B (Telegram) later
if you want daily success summaries, not just failure alerts.

### Deliverables:
- GitHub failure notifications enabled
- (Optional) `notifier.py` — Telegram or email notification module
- (Optional) GitHub Actions step added to call notifier after pipeline completes

---

## Phase 7: Testing & Validation

**Goal:** Confirm everything works correctly before going fully autonomous.

### Test Checklist:
1. Unit tests — Test each scraper's HTML parser with saved/mocked HTML snapshots
2. Integration test — Run the full pipeline manually, verify rows appear in Google Sheets
3. Date filter test — Confirm only today's jobs are captured (not older listings)
4. Deduplication test — Run twice in a row, confirm no duplicate rows are added
5. Failure resilience test — Simulate one scraper failing, confirm others still run and data is saved
6. Timezone test — Confirm cron schedule fires at the correct local Nairobi time (midnight EAT)

### Deliverables:
- `tests/` directory with all test files
- All tests passing locally and in GitHub Actions
- At least 2 successful scheduled runs confirmed

---

## Phase 8: Deployment & Handoff

**Goal:** Push to production and make the system truly set-and-forget.

### Steps:
1. Push all code to the GitHub repository's main branch.
2. Confirm all GitHub Actions Secrets are set:
   - GOOGLE_CREDENTIALS_JSON (contents of service account key file)
   - GOOGLE_SHEET_ID (the ID from the Google Sheet URL)
3. Trigger one final manual run via workflow_dispatch, verify the Google Sheet is populated correctly.
4. Enable GitHub failure notifications in your account settings.
5. Monitor the first 3–5 scheduled runs to confirm reliability.
6. Update README.md with column meanings and how to add new job categories or sites.

### From this point, the system is fully autonomous.
It will run at midnight Nairobi time every day, scrape the three sites, filter for today's
relevant tech jobs, deduplicate, and append to your Google Sheet — with no manual intervention needed.

---

## Recommended Build Order

Phase 2 → Phase 3A → Phase 4 (partial) → Phase 5 (test with one scraper) →
Phase 3B → Phase 3C → Phase 4 (complete) → Phase 6 → Phase 7 → Phase 8

Start with one scraper and get the full pipeline working end-to-end first, then add the
other two scrapers. This avoids building three scrapers only to discover a Sheets or
scheduling issue late in the process.

---

## Project File Structure (Final)

```
GetHiredAI/
├── .github/
│   └── workflows/
│       └── job_scraper.yml       # GitHub Actions schedule & pipeline
├── scrapers/
│   ├── __init__.py
│   ├── brighter_monday.py        # Brighter Monday scraper
│   ├── myjobmag.py               # MyJobMag scraper
│   └── fuzu.py                   # Fuzu scraper
├── tests/
│   ├── test_sheets.py
│   ├── test_brighter_monday.py
│   ├── test_myjobmag.py
│   └── test_fuzu.py
├── main.py                       # Pipeline orchestrator (entry point)
├── sheets_client.py              # Google Sheets read/write module
├── notifier.py                   # (Optional) Telegram/email alerts
├── requirements.txt              # Pinned dependencies
├── .env.example                  # Template for local env vars
├── PROJECT_PLAN.md               # This file
└── README.md                     # Setup and usage instructions
```

---

*Plan created: 2026-04-01*
