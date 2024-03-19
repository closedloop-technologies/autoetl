# An API endpoint created by the autoETL api has the following structure:
from typing import Optional
from pydantic import BaseModel


class API(BaseModel):
    id: str
    name: str
    seed_urls: list[str] = []
    openapi_spec_url: Optional[str] = None
    docs: list[str] = []
