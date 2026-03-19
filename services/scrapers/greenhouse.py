import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

import requests
import json
import logging
from datetime import datetime
from confluent_kafka import Producer
from packages.shared.models import RawEvent, EventSource, EventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "raw.events.jobs"

def get_producer():
    return Producer({"bootstrap.servers": KAFKA_BROKER})

def fetch_jobs(company: str) -> list:
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("jobs", [])
    except requests.RequestException as e:
        logger.error(f"Failed to fetch jobs for {company}: {e}")
        return []

def parse_job(job: dict, company: str) -> RawEvent:
    return RawEvent(
        source=EventSource.JOBS,
        entity_name=company,
        event_type=EventType.JOB_POSTED,
        raw_content=f"{job.get('title', '')} - {job.get('location', {}).get('name', '')}",
        url=job.get("absolute_url", ""),
        metadata={
            "job_id": str(job.get("id", "")),
            "title": job.get("title", ""),
            "location": job.get("location", {}).get("name", ""),
            "department": job.get("departments", [{}])[0].get("name", "") if job.get("departments") else "",
            "updated_at": job.get("updated_at", "")
        }
    )

def scrape_company(company: str, producer: Producer, seen_ids: set) -> int:
    jobs = fetch_jobs(company)
    new_count = 0

    for job in jobs:
        job_id = str(job.get("id", ""))
        if job_id in seen_ids:
            continue

        event = parse_job(job, company)
        producer.produce(
            TOPIC,
            key=company,
            value=event.model_dump_json(),
            callback=lambda err, msg: logger.error(f"Delivery failed: {err}") if err else None
        )
        seen_ids.add(job_id)
        new_count += 1

    producer.flush()
    logger.info(f"{company}: {new_count} new jobs published to Kafka")
    return new_count

if __name__ == "__main__":
    companies = ["vercel"]
    producer = get_producer()
    seen_ids = set()

    logger.info("Starting Greenhouse scraper...")
    for company in companies:
        scrape_company(company, producer, seen_ids)
    logger.info("Done.")