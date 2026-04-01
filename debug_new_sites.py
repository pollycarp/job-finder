"""Test LinkedIn scraper."""
from scrapers import linkedin

jobs = linkedin.scrape(today_only=False)
print(f"\nTotal found: {len(jobs)}")
for j in jobs[:5]:
    print(f"  [{j['Date Posted']}] {j['Job Title']} @ {j['Company']} | {j['Location']}")
