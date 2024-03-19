# An API endpoint created by the autoETL api has the following structure:
import datetime
from pathlib import Path
from typing import Optional, Set
from pydantic import BaseModel


class API(BaseModel):
    id: str
    name: str
    openapi_spec_url: Optional[str] = None
    docs: list[str] = []


class DocCrawl(BaseModel):
    id: str
    api_id: str
    seed_urls: list[str] = []
    url_prefixes: Optional[Set[str]] = None
    auth: Optional[dict[str, str]] = None
    max_crawl_depth: int = 3
    max_crawl_count: int = 100
    start_time: datetime.datetime | None = None
    storage_dir: Optional[str | Path] = None
