"""Unit tests for the JobWebKenya scraper parser."""
from datetime import datetime
from bs4 import BeautifulSoup
import pytest

from scrapers.jobwebkenya import parse_jobs, parse_date, is_kenya


# --- parse_date ---

def test_parse_date_valid():
    assert parse_date("01/Apr/2026") == "2026-04-01"

def test_parse_date_another_valid():
    assert parse_date("28/Mar/2026") == "2026-03-28"

def test_parse_date_with_whitespace():
    assert parse_date("  15/Jan/2026  ") == "2026-01-15"

def test_parse_date_invalid_returns_none():
    assert parse_date("today") is None

def test_parse_date_empty_returns_none():
    assert parse_date("") is None


# --- is_kenya ---

def test_is_kenya_nairobi():
    assert is_kenya("Nairobi") is True

def test_is_kenya_kenya():
    assert is_kenya("Kenya") is True

def test_is_kenya_case_insensitive():
    assert is_kenya("NAIROBI, KENYA") is True

def test_is_kenya_other_country():
    assert is_kenya("Lagos, Nigeria") is False


# --- parse_jobs ---

MOCK_HTML = """
<html><body>
  <ol class="jobs">
    <li class="job">
      <div id="titlo">
        <strong>
          <a href="https://jobwebkenya.com/jobs/frontend-developer-gap-recruitment/">
            Frontend Developer at Gap Recruitment Services Limited
          </a>
        </strong>
      </div>
      <div id="location"><strong>Location:</strong> Nairobi</div>
      <div id="date"><span class="year">01/Apr/2026</span></div>
    </li>
    <li class="job">
      <div id="titlo">
        <strong>
          <a href="https://jobwebkenya.com/jobs/data-scientist-wfp/">
            Data Scientist at World Food Programme
          </a>
        </strong>
      </div>
      <div id="location"><strong>Location:</strong> Kenya</div>
      <div id="date"><span class="year">28/Mar/2026</span></div>
    </li>
  </ol>
</body></html>
"""

def test_parse_jobs_returns_correct_count():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Frontend")
    assert len(jobs) == 2

def test_parse_jobs_title_and_company_split():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Frontend")
    assert jobs[0]["Job Title"] == "Frontend Developer"
    assert jobs[0]["Company"] == "Gap Recruitment Services Limited"

def test_parse_jobs_url_is_absolute():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Frontend")
    assert jobs[0]["Job URL"].startswith("https://jobwebkenya.com")

def test_parse_jobs_date_parsed():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Frontend")
    assert jobs[0]["Date Posted"] == "2026-04-01"

def test_parse_jobs_source_is_jobwebkenya():
    soup = BeautifulSoup(MOCK_HTML, "html.parser")
    jobs = parse_jobs(soup, "Data Science")
    assert all(j["Source"] == "JobWebKenya" for j in jobs)

def test_parse_jobs_no_ol_jobs_returns_empty():
    soup = BeautifulSoup("<html><body><p>No jobs</p></body></html>", "html.parser")
    assert parse_jobs(soup, "Frontend") == []

def test_parse_jobs_missing_date_returns_empty_string():
    html = """
    <html><body><ol class="jobs">
      <li class="job">
        <div id="titlo"><strong><a href="https://jobwebkenya.com/jobs/dev/">Developer at Acme</a></strong></div>
        <div id="location"><strong>Location:</strong> Nairobi</div>
      </li>
    </ol></body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs = parse_jobs(soup, "Fullstack")
    assert jobs[0]["Date Posted"] == ""
