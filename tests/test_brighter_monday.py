"""Unit tests for the BrighterMonday scraper helper functions."""
from datetime import datetime
import pytest

from scrapers.brighter_monday import parse_relative_date, is_today


# --- parse_relative_date ---

def test_parse_relative_date_today():
    today = datetime.now().strftime("%Y-%m-%d")
    assert parse_relative_date("Today") == today

def test_parse_relative_date_just_now():
    today = datetime.now().strftime("%Y-%m-%d")
    assert parse_relative_date("Just now") == today

def test_parse_relative_date_hours_ago():
    today = datetime.now().strftime("%Y-%m-%d")
    assert parse_relative_date("3 hours ago") == today

def test_parse_relative_date_minutes_ago():
    today = datetime.now().strftime("%Y-%m-%d")
    assert parse_relative_date("45 minutes ago") == today

def test_parse_relative_date_1_day_ago():
    today = datetime.now().strftime("%Y-%m-%d")
    assert parse_relative_date("1 day ago") == today

def test_parse_relative_date_older_returns_none():
    assert parse_relative_date("5 days ago") is None

def test_parse_relative_date_empty_returns_none():
    assert parse_relative_date("") is None

def test_parse_relative_date_case_insensitive():
    today = datetime.now().strftime("%Y-%m-%d")
    assert parse_relative_date("TODAY") == today


# --- is_today ---

def test_is_today_true():
    today = datetime.now().strftime("%Y-%m-%d")
    assert is_today(today) is True

def test_is_today_false_old_date():
    assert is_today("2024-01-01") is False

def test_is_today_none():
    assert is_today(None) is False

def test_is_today_empty_string():
    assert is_today("") is False
