import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from services.scrapers.greenhouse import fetch_jobs, parse_job
from packages.shared.models import RawEvent, EventSource, EventType

def test_fetch_jobs():
    jobs = fetch_jobs("vercel")
    assert len(jobs) > 0, "No jobs returned for Notion"
    print(f"✓ Fetched {len(jobs)} jobs for Notion")
    print(f"  First job: {jobs[0].get('title')} — {jobs[0].get('location', {}).get('name')}")
    return jobs

def test_parse_job(jobs):
    job = jobs[0]
    event = parse_job(job, "notion")
    
    assert isinstance(event, RawEvent)
    assert event.source == EventSource.JOBS
    assert event.event_type == EventType.JOB_POSTED
    assert event.entity_name == "notion"
    assert event.url.startswith("http")
    assert "title" in event.metadata
    assert "job_id" in event.metadata
    
    print(f"✓ RawEvent created successfully")
    print(f"  id: {event.id}")
    print(f"  entity: {event.entity_name}")
    print(f"  content: {event.raw_content}")
    print(f"  url: {event.url}")
    print(f"  metadata: {event.metadata}")

def test_all_companies():
    from services.scrapers.greenhouse import fetch_jobs
    companies = ["vercel"]
    for company in companies:
        jobs = fetch_jobs(company)
        print(f"✓ {company}: {len(jobs)} jobs found")

if __name__ == "__main__":
    print("Running Greenhouse scraper tests...\n")
    jobs = test_fetch_jobs()
    print()
    test_parse_job(jobs)
    print()
    test_all_companies()
    print("\nAll tests passed.")