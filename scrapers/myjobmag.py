"""
MyJobMag scraper — server-side rendered, uses requests + BeautifulSoup.
Searches for tech jobs across Kenya posted today.
"""
import logging
import time
import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.myjobmag.co.ke"

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

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def parse_date(date_text: str) -> str | None:
    """
    Parse MyJobMag date strings like '1 April' or '31 March' into YYYY-MM-DD.
    Assumes the current year.
    """
    date_text = date_text.strip()
    current_year = datetime.now().year
    for fmt in ("%d %B", "%d %b"):
        try:
            parsed = datetime.strptime(f"{date_text} {current_year}", f"{fmt} %Y")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def is_today(date_str: str | None) -> bool:
    if not date_str:
        return False
    return date_str == datetime.now().strftime("%Y-%m-%d")


def fetch_page(query: str, page: int = 1) -> BeautifulSoup | None:
    url = f"{BASE_URL}/search/jobs?q={requests.utils.quote(query)}&currentpage={page}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"MyJobMag fetch error for '{query}' page {page}: {e}")
        return None


def parse_jobs(soup: BeautifulSoup, category: str) -> list[dict]:
    """
    Each job entry is a <ul> containing:
      <li class="mag-b"><h2><a href="/job/...">Title at Company</a></h2></li>
      <li class="job-item"><ul><li id="job-date">30 March</li></ul></li>
    """
    jobs = []
    for ul in soup.find_all("ul"):
        title_li = ul.find("li", class_="mag-b")
        if not title_li:
            continue

        link_tag = title_li.find("a", href=lambda h: h and h.startswith("/job/"))
        if not link_tag:
            continue

        full_title = link_tag.get_text(strip=True)
        if " at " in full_title:
            job_title, company = full_title.rsplit(" at ", 1)
        else:
            job_title = full_title
            company = ""

        job_url = BASE_URL + link_tag["href"]

        # Date is in <li id="job-date"> inside <li class="job-item">
        date_li = ul.find("li", id="job-date")
        date_str = parse_date(date_li.get_text()) if date_li else None

        # Location — check for a location tag, fallback to Kenya
        location_li = ul.find("li", id="job-location")
        if location_li:
            location = location_li.get_text(strip=True) or "Kenya"
        else:
            location = "Kenya"

        jobs.append({
            "Job Title": job_title.strip(),
            "Company": company.strip(),
            "Location": location,
            "Category": category,
            "Source": "MyJobMag",
            "Job URL": job_url,
            "Date Posted": date_str or "",
            "_date": date_str,
        })
    return jobs


def scrape(today_only: bool = True) -> list[dict]:
    """Scrape MyJobMag for all target job categories. Returns list of job dicts."""
    all_jobs = []
    seen_urls = set()

    for query, category in SEARCH_QUERIES:
        logger.info(f"MyJobMag: searching '{query}'...")
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
                seen_urls.add(job["Job URL"])
                job.pop("_date", None)
                all_jobs.append(job)
                found_today = True

            # Stop paginating if no today's jobs found on this page
            if today_only and not found_today:
                break

            # Check if there is a next page
            next_link = soup.find("a", href=lambda h: h and f"currentpage={page + 1}" in h)
            if not next_link:
                break

            page += 1
            time.sleep(random.uniform(1, 3))

        time.sleep(random.uniform(1, 2))

    logger.info(f"MyJobMag: found {len(all_jobs)} new job(s) today.")
    return all_jobs
