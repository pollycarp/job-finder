from scrapers import brighter_monday

jobs = brighter_monday.scrape(today_only=False)
print(f"Total: {len(jobs)}")
for j in jobs[:5]:
    print(f"  {j['Job Title']} @ {j['Company']} | {j['Location']}")
