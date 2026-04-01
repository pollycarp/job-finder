"""
JobWebKenya scraper — WordPress-based, uses requests + BeautifulSoup.
Searches for tech jobs in Nairobi posted today.
"""
import logging
import time
import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://jobwebkenya.com"

SEARCH_QUERIES = [
    ("data scientist",     "Data Science"),
    ("data analyst",       "Data Science"),
    ("machine learning",   "AI/ML"),
    ("AI engineer",        "AI/ML"),
    ("frontend developer", "Frontend"),
    ("fullstack developer","Fullstack"),
    ("full stack developer","Fullstack"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def parse_date(date_text: str) -> str | None:
    """
    Parse JobWebKenya date strings like '01/Apr/2026' into YYYY-MM-DD.
    """
    date_text = date_text.strip()
    try:
        parsed = datetime.strptime(date_text, "%d/%b/%Y")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return None


def is_today(date_str: str | None) -> bool:
    if not date_str:
        return False
    return date_str == datetime.now().strftime("%Y-%m-%d")


def is_kenya(location_text: str) -> bool:
    """JobWebKenya lists location as 'Kenya' rather than specific city."""
    text = location_text.lower()
    return "kenya" in text or "nairobi" in text


def fetch_page(query: str, page: int = 1) -> BeautifulSoup | None:
    if page == 1:
        url = f"{BASE_URL}/?s={requests.utils.quote(query)}"
    else:
        url = f"{BASE_URL}/page/{page}/?s={requests.utils.quote(query)}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 404:
            return None  # Last page reached — not an error
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"JobWebKenya fetch error for '{query}' page {page}: {e}")
        return None


def parse_jobs(soup: BeautifulSoup, category: str) -> list[dict]:
    """
    Each job entry is <li class="job"> inside <ol class="jobs"> with:
      <div id="titlo"><strong><a href="...">Title at Company</a></strong></div>
      <div id="location"><strong>Location:</strong> Kenya</div>
      <div id="date"><span class="year">28/Mar/2026</span></div>
    """
    jobs = []
    job_list = soup.find("ol", class_="jobs")
    if not job_list:
        return jobs

    for li in job_list.find_all("li", class_="job"):
        # Title and URL
        titlo = li.find("div", id="titlo")
        if not titlo:
            continue
        link_tag = titlo.find("a")
        if not link_tag:
            continue

        full_title = link_tag.get_text(strip=True)
        job_url = link_tag.get("href", "")

        if " at " in full_title:
            job_title, company = full_title.rsplit(" at ", 1)
        else:
            job_title = full_title
            company = ""

        # Location
        loc_div = li.find("div", id="location")
        location = loc_div.get_text(strip=True).replace("Location:", "").strip() if loc_div else "Kenya"

        # Date — inside <div id="date"><span class="year">28/Mar/2026</span>
        date_div = li.find("div", id="date")
        date_str = None
        if date_div:
            span = date_div.find("span", class_="year")
            raw_date = span.get_text(strip=True) if span else date_div.get_text(strip=True)
            date_str = parse_date(raw_date)

        jobs.append({
            "Job Title": job_title.strip(),
            "Company": company.strip(),
            "Location": location,
            "Category": category,
            "Source": "JobWebKenya",
            "Job URL": job_url,
            "Date Posted": date_str or "",
            "_date": date_str,
            "_location": location,
        })
    return jobs


def scrape(today_only: bool = True) -> list[dict]:
    """Scrape JobWebKenya for all target job categories. Returns list of job dicts."""
    all_jobs = []
    seen_urls = set()

    for query, category in SEARCH_QUERIES:
        logger.info(f"JobWebKenya: searching '{query}'...")
        page = 1

        while True:
            soup = fetch_page(query, page)
            if not soup:
                break

            jobs = parse_jobs(soup, category)
            if not jobs:
                break

            found_today = False
            for job in jobs:
                if job["Job URL"] in seen_urls:
                    continue
                if today_only and not is_today(job["_date"]):
                    continue
                if not is_kenya(job["_location"]):
                    continue
                seen_urls.add(job["Job URL"])
                job.pop("_date", None)
                job.pop("_location", None)
                all_jobs.append(job)
                found_today = True

            if today_only and not found_today:
                break

            # Check for next page link — JobWebKenya uses "Next »" or "»"
            next_link = soup.find("a", class_="next") or soup.find("a", string=lambda t: t and ("next" in t.lower() or "»" in t))
            if not next_link:
                break

            page += 1
            time.sleep(random.uniform(1, 3))

        time.sleep(random.uniform(1, 2))

    logger.info(f"JobWebKenya: found {len(all_jobs)} new job(s) today.")
    return all_jobs
