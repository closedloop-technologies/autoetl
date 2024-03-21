import datetime
from pathlib import Path
from typing import Optional, Set

import yaml
from autoetl.apis.crud import get_api
from autoetl.apis.models import DocCrawl
from autoetl.helpers import cuid_generator


def create_doccrawl(
    api_id: str,
    fdir: Path | str,
    seed_urls: list[str] = None,
    url_prefixes: Optional[Set[str]] = None,
    auth: Optional[dict[str, str]] = None,
    max_crawl_depth: int = 3,
    max_crawl_count: int = 100,
    start_time: datetime.datetime | None = None,
):
    if seed_urls is None:
        seed_urls = []
    start_time = start_time or datetime.datetime.now(datetime.timezone.utc)
    if fdir is None:
        raise ValueError("fdir cannot be None")
    if api_id is None or not api_id:
        raise ValueError("api_id cannot be None")
    fdir = Path(fdir)
    if not get_api(api_id, fdir):
        raise ValueError(f"API with id {api_id} does not exist")

    doccrawl_id = cuid_generator()
    doccrawl_fdir = fdir / "apis" / api_id / "docs" / f"crawl-{doccrawl_id}"
    c = DocCrawl(
        id=doccrawl_id,
        api_id=api_id,
        seed_urls=seed_urls,
        url_prefixes=url_prefixes,
        auth=auth,
        max_crawl_depth=max_crawl_depth,
        max_crawl_count=max_crawl_count,
        start_time=datetime.datetime.now(datetime.timezone.utc),
        storage_dir=doccrawl_fdir,
    )
    spec_path = doccrawl_fdir / "spec.yaml"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    with open(spec_path, "w") as fh:
        data = c.model_dump()
        data["storage_dir"] = str(data["storage_dir"])
        yaml.safe_dump(data, fh)
    return c


def list_doccrawls(fdir: Path | str, api_id: str) -> list[DocCrawl]:
    fdir = Path(fdir)
    if not get_api(api_id, fdir):
        raise ValueError(f"API with id {api_id} does not exist")
    return [
        DocCrawl(**d)
        for d in yaml.safe_load_all(
            (fdir / "apis" / api_id / "docs").rglob("crawl-*/spec.yaml")
        )
    ]
