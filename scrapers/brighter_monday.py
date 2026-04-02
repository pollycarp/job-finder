"""
Brighter Monday scraper — JavaScript-rendered, uses Playwright headless browser.
Searches for tech jobs in Nairobi. No date is shown on listing cards, so all
collected jobs are marked with today's date. Deduplication in sheets_client.py
prevents re-adding jobs already saved from previous runs.
"""
import logging
import time
import random
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://www.brightermonday.co.ke"


def parse_relative_date(date_text: str) -> str | None:
    """
    Parse BrighterMonday relative date strings into YYYY-MM-DD.
    Only returns today's date for same-day postings, otherwise None.
    Examples: 'Today', '3 hours ago', '45 minutes ago', 'Just now', '1 day ago'
    Rejects: '1 week ago', '2 months ago', '4 weeks ago', etc.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    text = date_text.strip().lower()
    if not text:
        return None
    if "today" in text or "just now" in text or "minute" in text or "hour" in text:
        return today
    if "1 day ago" in text:
        return today
    return None


def is_today(date_str: str | None) -> bool:
    if not date_str:
        return False
    return date_str == datetime.now().strftime("%Y-%m-%d")

SEARCH_QUERIES = [
    ("data scientist",      "Data Science"),
    ("data analyst",        "Data Science"),
    ("machine learning",    "AI/ML"),
    ("AI engineer",         "AI/ML"),
    ("frontend developer",  "Frontend"),
    ("fullstack developer", "Fullstack"),
    ("full stack developer","Fullstack"),
    ("software engineer",   "Software Engineering"),
    ("backend developer",   "Backend"),
    ("cloud engineer",      "Cloud/DevOps"),
    ("DevOps",              "Cloud/DevOps"),
    ("cybersecurity",       "Cybersecurity"),
    ("ICT",                 "ICT"),
]

# Only scrape first N pages per query (most recent listings)
MAX_PAGES = 2


def scrape_query(page, query: str, category: str, seen_urls: set, today_only: bool = True) -> list[dict]:
    """Scrape a single search query using an open Playwright page."""
    jobs = []
    today = datetime.now().strftime("%Y-%m-%d")

    for page_num in range(1, MAX_PAGES + 1):
        url = (
            f"{BASE_URL}/jobs?q={query.replace(' ', '+')}&location=kenya"
            if page_num == 1
            else f"{BASE_URL}/jobs?q={query.replace(' ', '+')}&location=kenya&page={page_num}"
        )

        try:
            page.goto(url, wait_until="networkidle", timeout=45000)
        except Exception as e:
            logger.warning(f"BrighterMonday: page load issue for '{query}' page {page_num}: {e}")
            break

        # Wait for job links to appear
        try:
            page.wait_for_selector('a[data-cy="listing-title-link"]', timeout=15000)
        except Exception:
            logger.info(f"BrighterMonday: no listings found for '{query}' page {page_num}")
            break

        # Extract all job cards on this page
        cards_data = page.evaluate("""() => {
            const cards = document.querySelectorAll('div[data-cy="listing-cards-components"]');
            const results = [];

            cards.forEach(card => {
                const link = card.querySelector('a[data-cy="listing-title-link"]');
                if (!link) return;

                // Title
                const titleEl = link.querySelector('p.text-lg') || link.querySelector('p');
                const title = titleEl ? titleEl.innerText.trim() : link.getAttribute('title') || '';

                // URL
                const url = link.getAttribute('href') || '';

                // Inner card (2 levels up from link)
                const innerCard = link.parentElement?.parentElement;

                // Company
                const companyEl = innerCard?.querySelector('p.text-blue-700') ||
                                  innerCard?.querySelector('p.text-sm.text-blue-700');
                const company = companyEl ? companyEl.innerText.trim() : '';

                // Location — first span.mb-3
                const spans = innerCard?.querySelectorAll('span.mb-3');
                const location = spans?.length > 0 ? spans[0].innerText.trim() : 'Kenya';

                // Date — in .border-t bottom section, inside .ml-auto div
                const borderT = card.querySelector('.border-t');
                const datePEl = borderT?.querySelector('.ml-auto p');
                const dateText = datePEl ? datePEl.innerText.trim() : '';

                results.push({ title, url, company, location, dateText });
            });
            return results;
        }""")

        if not cards_data:
            break

        found_today = False
        for item in cards_data:
            job_url = item["url"]
            if not job_url or job_url in seen_urls:
                continue

            date_str = parse_relative_date(item.get("dateText", ""))

            if today_only and not date_str:
                continue  # Skip jobs older than today

            jobs.append({
                "Job Title": item["title"],
                "Company": item["company"],
                "Location": item["location"] or "Kenya",
                "Category": category,
                "Source": "BrighterMonday",
                "Job URL": job_url,
                "Date Posted": date_str or today,
            })
            seen_urls.add(job_url)
            found_today = True

        # Stop paginating if no today's jobs on this page
        if today_only and not found_today:
            break

        time.sleep(random.uniform(1, 2))

    return jobs


def scrape(today_only: bool = True) -> list[dict]:
    """
    Scrape Brighter Monday for all target job categories using Playwright.
    today_only is accepted for interface consistency but BrighterMonday cards
    don't expose a date — all collected jobs are stamped with today's date.
    """
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
            logger.info(f"BrighterMonday: searching '{query}'...")
            jobs = scrape_query(page, query, category, seen_urls, today_only)
            all_jobs.extend(jobs)
            logger.info(f"BrighterMonday: '{query}' → {len(jobs)} job(s)")
            time.sleep(random.uniform(2, 3))

        browser.close()

    logger.info(f"BrighterMonday: found {len(all_jobs)} total job(s).")
    return all_jobs
