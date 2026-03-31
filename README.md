# Job Finder — Nairobi Tech Job Tracker

Autonomous system that scrapes daily tech job postings from Fuzu, MyJobMag, and Brighter Monday
for Nairobi, Kenya. Runs every day at midnight (EAT) via GitHub Actions and saves results to Google Sheets.

## Target Job Categories
- Data Science
- Artificial Intelligence / Machine Learning
- Frontend Developer
- Fullstack Developer

## Google Sheet Columns
| Column      | Description                              |
|-------------|------------------------------------------|
| Date Found  | Date the job was scraped                 |
| Job Title   | Position name                            |
| Company     | Employer name                            |
| Location    | e.g., Nairobi, Kenya                     |
| Category    | Data Science / ML / Frontend / Fullstack |
| Source      | Fuzu / Myjobmag / BrighterMonday         |
| Job URL     | Direct link to the listing               |
| Date Posted | Posting date from the site               |

## Project Structure
```
job-finder/
├── .github/workflows/job_scraper.yml   # Scheduled GitHub Actions pipeline
├── scrapers/
│   ├── brighter_monday.py
│   ├── myjobmag.py
│   └── fuzu.py
├── tests/
├── main.py                             # Pipeline entry point
├── sheets_client.py                    # Google Sheets integration
├── requirements.txt
└── .env.example
```

## Local Development Setup
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Fill in your values
python main.py
```

## GitHub Actions Secrets Required
- `GOOGLE_SHEET_ID` — ID from the Google Sheet URL
- `GOOGLE_CREDENTIALS_JSON` — Full contents of the service account JSON key file
