"""
LinkedIn Kenya scraper — JavaScript-rendered, uses Playwright headless browser.
Uses LinkedIn's public job search (no login required).
Searches for tech jobs across Kenya posted today.
"""
import logging
import time
import random
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://www.linkedin.com/jobs/search"

SEARCH_QUERIES = [
    ("data scientist",     "Data Science"),
    ("data analyst",       "Data Science"),
    ("machine learning",   "AI/ML"),
    ("AI engineer",        "AI/ML"),
    ("frontend developer", "Frontend"),
    ("fullstack developer","Fullstack"),
    ("full stack developer","Fullstack"),
    ("software engineer",  "Software Engineering"),
    ("backend developer",  "Backend"),
    ("cloud engineer",     "Cloud/DevOps"),
    ("DevOps",             "Cloud/DevOps"),
    ("cybersecurity",      "Cybersecurity"),
    ("ICT",                "ICT"),
]

# LinkedIn shows 25 jobs per page, scrape first 2 pages max
MAX_PAGES = 2
JOBS_PER_PAGE = 25


def is_today(date_str: str | None) -> bool:
    if not date_str:
        return False
    return date_str == datetime.now().strftime("%Y-%m-%d")


def scrape_query(page, query: str, category: str, seen_urls: set, today_only: bool = True) -> list[dict]:
    """Scrape a single search query using an open Playwright page."""
    jobs = []

    for page_num in range(MAX_PAGES):
        start = page_num * JOBS_PER_PAGE
        url = (
            f"{BASE_URL}/?keywords={query.replace(' ', '+')}"
            f"&location=Kenya&start={start}"
        )

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"LinkedIn: page load issue for '{query}' page {page_num + 1}: {e}")
            break

        # Wait for job cards to load
        try:
            page.wait_for_selector(".job-search-card", timeout=15000)
        except Exception:
            logger.info(f"LinkedIn: no listings found for '{query}' page {page_num + 1}")
            break

        cards_data = page.evaluate("""() => {
            const cards = document.querySelectorAll('div.job-search-card');
            const results = [];

            cards.forEach(card => {
                // Title
                const titleEl = card.querySelector('h3.base-search-card__title');
                const title = titleEl ? titleEl.innerText.trim() : '';

                // URL
                const linkEl = card.querySelector('a.base-card__full-link');
                const url = linkEl ? linkEl.getAttribute('href') : '';

                // Company
                const companyEl = card.querySelector('h4.base-search-card__subtitle a');
                const company = companyEl ? companyEl.innerText.trim() : '';

                // Location
                const locationEl = card.querySelector('span.job-search-card__location');
                const location = locationEl ? locationEl.innerText.trim() : 'Kenya';

                // Date — use datetime attribute for exact date
                const timeEl = card.querySelector('time.job-search-card__listdate');
                const date = timeEl ? timeEl.getAttribute('datetime') : '';

                if (title && url) {
                    results.push({ title, url, company, location, date });
                }
            });

            return results;
        }""")

        if not cards_data:
            break

        found_new = False
        for item in cards_data:
            job_url = item["url"].split("?")[0]  # Strip tracking params
            if not job_url or job_url in seen_urls:
                continue
            if today_only and not is_today(item["date"]):
                continue

            jobs.append({
                "Job Title": item["title"],
                "Company": item["company"],
                "Location": item["location"],
                "Category": category,
                "Source": "LinkedIn",
                "Job URL": job_url,
                "Date Posted": item["date"],
            })
            seen_urls.add(job_url)
            found_new = True

        # Stop paginating if no matching jobs on this page
        if today_only and not found_new:
            break

        time.sleep(random.uniform(2, 3))

    return jobs


def scrape(today_only: bool = True) -> list[dict]:
    """Scrape LinkedIn Kenya for all target job categories using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright is not installed. Run: playwright install chromium")
        return []

    all_jobs = []
    seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        for query, category in SEARCH_QUERIES:
            logger.info(f"LinkedIn: searching '{query}'...")
            jobs = scrape_query(page, query, category, seen_urls, today_only)
            all_jobs.extend(jobs)
            logger.info(f"LinkedIn: '{query}' → {len(jobs)} job(s)")
            time.sleep(random.uniform(2, 3))

        browser.close()

    logger.info(f"LinkedIn: found {len(all_jobs)} total job(s).")
    return all_jobs
