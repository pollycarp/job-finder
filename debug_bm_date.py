"""Verify BrighterMonday date filtering is working correctly."""
from scrapers import brighter_monday

print("=== today_only=False (should show all jobs with their real dates) ===")
jobs = brighter_monday.scrape(today_only=False)
print(f"Total: {len(jobs)}")
for j in jobs[:8]:
    print(f"  [{j['Date Posted']}] {j['Job Title']} @ {j['Company']}")

print("\n=== today_only=True (should only show today's jobs) ===")
jobs_today = brighter_monday.scrape(today_only=True)
print(f"Total: {len(jobs_today)}")
for j in jobs_today:
    print(f"  [{j['Date Posted']}] {j['Job Title']} @ {j['Company']}")
