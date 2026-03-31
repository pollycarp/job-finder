import os
import json
import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "Date Found",
    "Job Title",
    "Company",
    "Location",
    "Category",
    "Source",
    "Job URL",
    "Date Posted",
]


def get_client():
    """Authenticate and return a gspread client using the service account credentials."""
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not credentials_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set.")

    # Supports both a file path and raw JSON string (used in GitHub Actions)
    try:
        credentials_data = json.loads(credentials_json)
    except json.JSONDecodeError:
        with open(credentials_json, "r") as f:
            credentials_data = json.load(f)

    creds = Credentials.from_service_account_info(credentials_data, scopes=SCOPES)
    return gspread.authorize(creds)


def get_sheet():
    """Open and return the target worksheet, creating headers if the sheet is empty."""
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID environment variable is not set.")

    client = get_client()
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.sheet1

    # Add headers if the sheet is empty
    existing = worksheet.get_all_values()
    if not existing:
        worksheet.append_row(HEADERS)
        logger.info("Headers written to sheet.")

    return worksheet


def get_existing_urls(worksheet):
    """Return a set of all job URLs already in the sheet (for deduplication)."""
    records = worksheet.get_all_records()
    return {row["Job URL"] for row in records if row.get("Job URL")}


def save_jobs(jobs: list[dict]) -> int:
    """
    Save a list of job dicts to Google Sheets, skipping duplicates.

    Each job dict must have keys matching HEADERS (case-sensitive).
    Returns the number of new rows written.
    """
    if not jobs:
        logger.info("No jobs to save.")
        return 0

    worksheet = get_sheet()
    existing_urls = get_existing_urls(worksheet)

    new_jobs = [job for job in jobs if job.get("Job URL") not in existing_urls]

    if not new_jobs:
        logger.info("All jobs already exist in the sheet. Nothing to write.")
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    rows = []
    for job in new_jobs:
        rows.append([
            today,
            job.get("Job Title", ""),
            job.get("Company", ""),
            job.get("Location", ""),
            job.get("Category", ""),
            job.get("Source", ""),
            job.get("Job URL", ""),
            job.get("Date Posted", ""),
        ])

    worksheet.append_rows(rows)
    logger.info(f"Wrote {len(rows)} new job(s) to Google Sheets.")
    return len(rows)
