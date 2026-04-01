"""
Main pipeline — runs all scrapers and saves results to Google Sheets.
"""
import logging
import sys
from datetime import datetime

import sheets_client
from scrapers import brighter_monday, myjobmag, jobwebkenya

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def run():
    start = datetime.now()
    logger.info("=" * 50)
    logger.info(f"Job scraper started at {start.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    all_jobs = []
    results = {}

    scrapers = [
        ("MyJobMag",      myjobmag.scrape),
        ("JobWebKenya",   jobwebkenya.scrape),
        ("BrighterMonday",brighter_monday.scrape),
    ]

    for name, scrape_fn in scrapers:
        try:
            logger.info(f"Running {name} scraper...")
            jobs = scrape_fn(today_only=True)
            results[name] = len(jobs)
            all_jobs.extend(jobs)
            logger.info(f"{name}: {len(jobs)} job(s) found.")
        except Exception as e:
            logger.error(f"{name} scraper failed: {e}", exc_info=True)
            results[name] = 0

    logger.info("-" * 50)
    logger.info(f"Total jobs collected: {len(all_jobs)}")

    if all_jobs:
        try:
            written = sheets_client.save_jobs(all_jobs)
            logger.info(f"Google Sheets: {written} new row(s) written.")
        except Exception as e:
            logger.error(f"Failed to save to Google Sheets: {e}", exc_info=True)
            sys.exit(1)
    else:
        logger.info("No jobs found today. Nothing written to sheet.")

    elapsed = (datetime.now() - start).seconds
    logger.info("=" * 50)
    logger.info("Run summary:")
    for name, count in results.items():
        logger.info(f"  {name}: {count} job(s)")
    logger.info(f"  Total written to sheet: {written if all_jobs else 0}")
    logger.info(f"  Duration: {elapsed}s")
    logger.info("=" * 50)


if __name__ == "__main__":
    run()
