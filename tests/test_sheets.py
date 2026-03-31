"""
Unit tests for sheets_client.py using mocks — no real Google Sheets connection needed.
"""
from unittest.mock import MagicMock, patch
import pytest

import sheets_client


MOCK_JOBS = [
    {
        "Job Title": "Data Scientist",
        "Company": "Safaricom",
        "Location": "Nairobi, Kenya",
        "Category": "Data Science",
        "Source": "BrighterMonday",
        "Job URL": "https://brightermonday.co.ke/jobs/1",
        "Date Posted": "2026-04-01",
    },
    {
        "Job Title": "Frontend Developer",
        "Company": "Andela",
        "Location": "Nairobi, Kenya",
        "Category": "Frontend",
        "Source": "Fuzu",
        "Job URL": "https://fuzu.com/jobs/2",
        "Date Posted": "2026-04-01",
    },
]


@patch("sheets_client.get_sheet")
def test_save_jobs_writes_new_jobs(mock_get_sheet):
    """New jobs should be written to the sheet."""
    mock_ws = MagicMock()
    mock_ws.get_all_records.return_value = []  # Sheet is empty
    mock_get_sheet.return_value = mock_ws

    result = sheets_client.save_jobs(MOCK_JOBS)

    assert result == 2
    mock_ws.append_rows.assert_called_once()


@patch("sheets_client.get_sheet")
def test_save_jobs_skips_duplicates(mock_get_sheet):
    """Jobs with URLs already in the sheet should be skipped."""
    mock_ws = MagicMock()
    mock_ws.get_all_records.return_value = [
        {"Job URL": "https://brightermonday.co.ke/jobs/1"}
    ]
    mock_get_sheet.return_value = mock_ws

    result = sheets_client.save_jobs(MOCK_JOBS)

    # Only 1 new job (the Fuzu one), the BrighterMonday one is a duplicate
    assert result == 1


@patch("sheets_client.get_sheet")
def test_save_jobs_all_duplicates(mock_get_sheet):
    """If all jobs are duplicates, nothing should be written."""
    mock_ws = MagicMock()
    mock_ws.get_all_records.return_value = [
        {"Job URL": "https://brightermonday.co.ke/jobs/1"},
        {"Job URL": "https://fuzu.com/jobs/2"},
    ]
    mock_get_sheet.return_value = mock_ws

    result = sheets_client.save_jobs(MOCK_JOBS)

    assert result == 0
    mock_ws.append_rows.assert_not_called()


@patch("sheets_client.get_sheet")
def test_save_jobs_empty_list(mock_get_sheet):
    """Passing an empty list should return 0 and not touch the sheet."""
    mock_ws = MagicMock()
    mock_get_sheet.return_value = mock_ws

    result = sheets_client.save_jobs([])

    assert result == 0
    mock_ws.append_rows.assert_not_called()
