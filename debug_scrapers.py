"""
Debug script — runs scrapers with today_only=False to verify they can read job data.
Prints the first 5 jobs found per source with their dates.
Run this once to confirm scrapers are working, then delete it.
"""
from scrapers import myjobmag, jobwebkenya, brighter_monday

print("\n=== MyJobMag (today_only=False) ===")
jobs = myjobmag.scrape(today_only=False)
print(f"Total found: {len(jobs)}")
for job in jobs[:5]:
    print(f"  [{job['Date Posted']}] {job['Job Title']} @ {job['Company']}")

print("\n=== JobWebKenya (today_only=False) ===")
jobs = jobwebkenya.scrape(today_only=False)
print(f"Total found: {len(jobs)}")
for job in jobs[:5]:
    print(f"  [{job['Date Posted']}] {job['Job Title']} @ {job['Company']}")

print("\n=== BrighterMonday (today_only=False) ===")
jobs = brighter_monday.scrape(today_only=False)
print(f"Total found: {len(jobs)}")
for job in jobs[:5]:
    print(f"  [{job['Date Posted']}] {job['Job Title']} @ {job['Company']}")
