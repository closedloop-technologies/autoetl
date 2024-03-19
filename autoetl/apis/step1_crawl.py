"""Given the endpoints and swaggar spec,
download the docs and swaggar spec for the API

The goal is to fill the storage_dir with the following:
1. likely swaggar spec candidates
2. relavant api docs

"""

from collections import defaultdict

from urllib.parse import urlparse
import asyncio
from pathlib import Path

from autoetl.apis.crawler import request_with_retry, is_valid_url, url_domain
import asyncio
import contextlib
import hashlib
import json
from pathlib import Path
from typing import Optional, Set
from prefect import task, flow

from autoetl.apis.crawler import is_valid_url, url_domain, request_with_retry

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from autoetl.apis.headless_crawler import render_page


@task
async def process_response(
    response: dict,
    url: str,
    storage_dir: Path,
    url_prefixes: Set[str],
):
    crawl_dir = Path(storage_dir) / "crawl"

    if response is None:
        return []

    url_hash = hashlib.md5(url.encode()).hexdigest()
    content_hash = hashlib.md5(response["content"].encode()).hexdigest()

    url_dir = crawl_dir / url_hash
    url_dir.mkdir(parents=True, exist_ok=True)

    with open(url_dir / f"{content_hash}.info", "w") as f:
        json.dump(
            {
                "response": response.get("response"),
                "request": response.get("request", {}),
            },
            f,
        )

    with open(url_dir / f"{content_hash}.data", "w") as f:
        f.write(response["content"])

    new_links = []
    if url.endswith(".json"):
        with contextlib.suppress(json.JSONDecodeError):
            openapi_spec_dir = Path(storage_dir) / "openapi_spec"
            openapi_spec_dir.mkdir(parents=True, exist_ok=True)

            data = json.loads(response["content"])
            if "openapi" in data or "swagger" in data:
                with open(openapi_spec_dir / f"{content_hash}.json", "w") as f:
                    json.dump(data, f)
            # TODO look at json schema for links
            # externalDocs, termsOfService, contact, license.url, info.description, host
            print(data)
    else:
        # Parse HTML to find new URLs
        soup = BeautifulSoup(response["content"], "html.parser")
        for a in soup.find_all("a", href=True):
            new_url = a["href"].split("#")[0]
            # Make the URL absolute
            new_url = urljoin(url, new_url)
            if is_valid_url(new_url) and new_url != url:
                new_links.append(
                    {
                        "source": url,
                        "target": new_url,
                        "text": a.text,
                        "xpath": None,  # TODO implement xpath
                        "source_hash": content_hash,
                        "follow": any(new_url.startswith(u) for u in url_prefixes),
                    }
                )
    return new_links


@flow(name="AutoETL Docs Crawler")
async def crawl(
    storage_dir: str | Path,
    seed_urls: list[str],
    url_prefixes: Optional[Set[str]] = None,
    auth: Optional[dict[str, str]] = None,
    max_crawl_depth: int = 3,
    max_crawl_count: int = 100,
):
    print("Crawling data from the web")
    if storage_dir is None:
        raise ValueError("storage_dir is required")
    if seed_urls is None or not seed_urls:
        raise ValueError("seed_urls is required")

    storage_dir = Path(storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)

    seed_urls = [str(url) for url in seed_urls if is_valid_url(url)]
    if not seed_urls:
        raise ValueError("No valid seed urls found")

    # Use the longest common prefix of the seed URLs
    url_prefixes = add_seeds_to_url_prefixes(seed_urls, url_prefixes)

    queue = asyncio.Queue()
    crawl_count = 0
    visited_urls = set()
    for url in seed_urls:
        if url not in visited_urls:
            visited_urls.add(url)
            print("enqueue", 0, url)
            await queue.put((url, 0))  # (url, depth)

    crawl_graph = []
    while not queue.empty():
        url, depth = await queue.get()
        crawl_count += 1
        if depth >= max_crawl_depth or crawl_count > max_crawl_count:
            continue

        if url.endswith(".json") or url.endswith(".yaml"):
            response = await request_with_retry(url, auth=auth)
        else:
            response = await render_page(url)

        new_url_links = await process_response(response, url, storage_dir, url_prefixes)
        crawl_graph += new_url_links
        for new_link in new_url_links:
            new_url = new_link.get("target")
            if new_url not in visited_urls and new_link.get("follow"):
                visited_urls.add(new_url)
                print("enqueue", depth + 1, new_url)
                await queue.put((new_url, depth + 1))

    # Save Crawl Graph
    with open(storage_dir / "crawl_graph.json", "w") as f:
        json.dump(crawl_graph, f)
    print("Crawling completed")


def add_seeds_to_url_prefixes(seed_urls, url_prefixes):
    shortest_prefix_calc = defaultdict(list)
    if url_prefixes is None:
        url_prefixes = set()
    for url in seed_urls + list(url_prefixes):
        shortest_prefix_calc[url_domain(url)].append(url)
    for domain in shortest_prefix_calc:
        u = urlparse(
            sorted(shortest_prefix_calc[domain], key=lambda x: len(x), reverse=False)[0]
        )
        new_path = "/".join(u.path.split("/")[:-1])
        shortest_prefix_calc[domain] = u._replace(path=new_path).geturl()
    url_prefixes = set(shortest_prefix_calc.values())
    return url_prefixes


if __name__ == "__main__":
    storage_dir = "data"
    seed_urls = ["https://app.swaggerhub.com/apis-docs/the-odds-api/odds-api/4"]
    url_prefixes = {
        "https://the-odds-api.com",
        "https://api.the-odds-api.com",
    }
    # auth = {"Authorization": "Bearer TOKEN"}
    max_crawl_depth = 3
    max_crawl_count = 100

    asyncio.run(
        crawl(
            storage_dir,
            seed_urls,
            url_prefixes=url_prefixes,
            auth=None,
            max_crawl_depth=max_crawl_depth,
            max_crawl_count=max_crawl_count,
        )
    )
