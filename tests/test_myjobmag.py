"""Unit tests for the MyJobMag scraper parser."""
from datetime import datetime
from bs4 import BeautifulSoup
import pytest

from scrapers.myjobmag import parse_jobs, parse_date, is_today


# --- parse_date ---

def test_parse_date_full_month():
    assert parse_date("1 April") == f"{datetime.now().year}-04-01"

def test_parse_date_abbreviated_month():
    assert parse_date("15 Mar") == f"{datetime.now().year}-03-15"

def test_parse_date_with_whitespace():
    assert parse_date("  30 March  ") == f"{datetime.now().year}-03-30"

def test_parse_date_invalid_returns_none():
    assert parse_date("yesterday") is None

def test_parse_date_empty_returns_none():
    assert parse_date("") is None


# --- is_today ---

def test_is_today_true():
    today = datetime.now().strftime("%Y-%m-%d")
    assert is_today(today) is True

def test_is_today_false():
    assert is_today("2020-01-01") is False

def test_is_today_none():
    assert is_today(None) is False


# --- parse_jobs ---

MOCK_HTML = """
<html><body>
  <ul>
    <li class="mag-b">
      <h2><a href="/job/fullstack-developer-avenews">Fullstack Developer at Avenews</a></h2>
    </li>
    <li class="job-desc">Some description here</li>
    <li class="job-item">
      <ul>
        <li id="job-date">1 April</li>
      </ul>
    </li>
  </ul>
  <ul>
    <li class="mag-b">
      <h2><a href="/job/data-scientist-safaricom">Data Scientist at Safaricom PLC</a></h2>
    </li>
    <li class="job-item">
      <ul>
        <li id="job-date">28 March</li>
      </ul>
    </li>
  </ul>
</body></html>
"""

def test_parse_jobs_returns_correct_count():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Fullstack")
    assert len(jobs) == 2

def test_parse_jobs_title_and_company_split():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Fullstack")
    assert jobs[0]["Job Title"] == "Fullstack Developer"
    assert jobs[0]["Company"] == "Avenews"

def test_parse_jobs_url_is_absolute():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Fullstack")
    assert jobs[0]["Job URL"].startswith("https://www.myjobmag.co.ke")

def test_parse_jobs_date_parsed():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Fullstack")
    assert jobs[0]["Date Posted"] == f"{datetime.now().year}-04-01"

def test_parse_jobs_source_is_myjobmag():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Data Science")
    assert all(j["Source"] == "MyJobMag" for j in jobs)

def test_parse_jobs_location_is_nairobi():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Data Science")
    assert all("Nairobi" in j["Location"] for j in jobs)

def test_parse_jobs_no_cards_returns_empty():
    soup = BeautifulSoup("<html><body><p>No jobs</p></body></html>", "html.parser")
    assert parse_jobs(soup, "Data Science") == []

def test_parse_jobs_title_without_at_company():
    html = """
    <html><body><ul>
      <li class="mag-b"><h2><a href="/job/developer">Software Developer</a></h2></li>
      <li class="job-item"><ul><li id="job-date">1 April</li></ul></li>
    </ul></body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs = parse_jobs(soup, "Fullstack")
    assert jobs[0]["Job Title"] == "Software Developer"
    assert jobs[0]["Company"] == ""
