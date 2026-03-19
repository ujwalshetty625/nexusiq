from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid

class EventSource(str, Enum):
    GITHUB = "github"
    JOBS = "jobs"
    HACKER_NEWS = "hacker_news"
    REDDIT = "reddit"
    REVIEWS = "reviews"
    NEWS = "news"
    PATENTS = "patents"

class EventType(str, Enum):
    JOB_POSTED = "job_posted"
    COMMIT = "commit"
    REPO_CREATED = "repo_created"
    MENTION = "mention"
    REVIEW = "review"
    ARTICLE = "article"
    PATENT_FILED = "patent_filed"
    RELEASE = "release"

class RawEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: EventSource
    entity_name: str
    event_type: EventType
    raw_content: str
    url: str
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)

    class Config:
        use_enum_values = True