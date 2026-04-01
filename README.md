# Job Finder — Kenya Tech Job Tracker

An autonomous system that scrapes daily tech job postings across Kenya from multiple job boards,
saves them to Google Sheets, and sends each new job to a WhatsApp group. Runs every day at
midnight Nairobi time (EAT) via GitHub Actions with zero manual intervention required.

---

## What It Does

- Scrapes **3 job boards** every day at midnight (EAT)
- Filters for **4 tech job categories** across Kenya
- Saves new jobs to a **Google Sheet** (deduplicates — no repeats ever)
- Sends each new job as a **WhatsApp message** to your group

---

## Target Job Categories

| Category | Search Terms |
|----------|-------------|
| Data Science | Data Scientist, Data Analyst |
| AI / Machine Learning | Machine Learning, AI Engineer |
| Frontend Development | Frontend Developer |
| Fullstack Development | Fullstack Developer, Full Stack Developer |

---

## Job Sources

| Site | Method | Coverage |
|------|--------|----------|
| [MyJobMag](https://www.myjobmag.co.ke) | requests + BeautifulSoup | Kenya-wide |
| [JobWebKenya](https://jobwebkenya.com) | requests + BeautifulSoup | Kenya-wide |
| [Brighter Monday](https://www.brightermonday.co.ke) | Playwright (headless browser) | Kenya-wide |

---

## Google Sheet Columns

| Column | Description |
|--------|-------------|
| Date Found | Date the job was scraped |
| Job Title | Position name |
| Company | Employer name |
| Location | City/region (e.g. Nairobi, Mombasa, Kisumu) or Kenya if unspecified |
| Category | Data Science / AI/ML / Frontend / Fullstack |
| Source | MyJobMag / JobWebKenya / BrighterMonday |
| Job URL | Direct link to the job listing |
| Date Posted | Date the job was posted on the site |

---

## WhatsApp Message Format

Each new job is sent as a separate message in this format:

```
*Job Title:* Senior Data Scientist
*Company:* Safaricom PLC
*Location:* Nairobi
*Link to the job:* https://...
```

---

## Project Structure

```
job-finder/
├── .github/
│   └── workflows/
│       └── job_scraper.yml       # GitHub Actions — runs daily at 9 PM UTC (midnight EAT)
├── scrapers/
│   ├── __init__.py
│   ├── myjobmag.py               # MyJobMag scraper
│   ├── jobwebkenya.py            # JobWebKenya scraper
│   └── brighter_monday.py        # Brighter Monday scraper (Playwright)
├── tests/
│   ├── test_sheets.py            # Google Sheets module tests
│   ├── test_myjobmag.py          # MyJobMag parser tests
│   ├── test_jobwebkenya.py       # JobWebKenya parser tests
│   └── test_brighter_monday.py   # Brighter Monday helper tests
├── main.py                       # Pipeline entry point
├── sheets_client.py              # Google Sheets read/write/deduplicate
├── whatsapp_notifier.py          # WhatsApp notifications via Green API
├── requirements.txt              # Python dependencies
├── .env.example                  # Template for local environment variables
└── PROJECT_PLAN.md               # Full phased implementation plan
```

---

## Local Development Setup

```bash
# 1. Clone the repo
git clone https://github.com/pollycarp/job-finder.git
cd job-finder

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Set up environment variables
cp .env.example .env
# Fill in your values in .env

# 6. Run the pipeline
python main.py

# 7. Run tests
pytest tests/ -v
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_SHEET_ID` | ID from the Google Sheet URL |
| `GOOGLE_CREDENTIALS_JSON` | Path to service account JSON (local) or full JSON contents (GitHub Actions) |
| `GREEN_API_INSTANCE_ID` | Green API instance ID |
| `GREEN_API_TOKEN` | Green API token |
| `WHATSAPP_GROUP_CHAT_ID` | WhatsApp group chat ID in format `XXXXXXXXXX@g.us` |

---

## GitHub Actions Secrets Required

Add these in your repo under **Settings → Secrets and variables → Actions**:

- `GOOGLE_SHEET_ID`
- `GOOGLE_CREDENTIALS_JSON`
- `GREEN_API_INSTANCE_ID`
- `GREEN_API_TOKEN`
- `WHATSAPP_GROUP_CHAT_ID`

---

## Schedule

Runs automatically every day at **9 PM UTC = Midnight Nairobi time (EAT)**.

To trigger a manual run: **GitHub → Actions → Daily Job Scraper → Run workflow**

---

## Test Suite

48 unit tests covering all scrapers and the Sheets module.

```bash
pytest tests/ -v
```

---

## Adding a New Job Category

1. Add a new search query tuple to the `SEARCH_QUERIES` list in each scraper file:
   ```python
   ("devops engineer", "DevOps"),
   ```
2. Push to `main` — the next scheduled run will include it automatically.

## Adding a New Job Site

1. Create a new scraper file in `scrapers/` following the same pattern as existing scrapers
2. Import and add it to the `scrapers` list in `main.py`
3. Write tests in `tests/`
4. Push to `main`
