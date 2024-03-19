import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from autoetl.doc_crawler.httpx_crawler import is_valid_url

FULL_URL_PATTERN = re.compile(
    r"https?://"  # Scheme
    r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"  # Domain
    r"(?::\d+)?"  # Optional port
    r"(?:/[^/\s()]*)*"  # Optional path excluding whitespace and parentheses
    r"(?:\?[^\s]*)?"  # Optional query
    r"(?:#[^\s]*)?"  # Optional fragment
)


# This pattern matches a leading slash followed by any characters not including a slash or whitespace,
# potentially followed by more segments of slash-separated characters.
# It does not explicitly exclude full URLs but simplifies the match to likely URL paths.
PATH_URL_PATTERN = re.compile(r"/[^/\s()\[\]]+(?:/[^/\s()\[\]]+)*")


def get_links_json(data, url, url_prefixes, content_hash):
    # TODO look at json schema for links
    # Recursively look for links in the values of the json
    if isinstance(data, list):
        for item in data:
            yield from get_links_json(item, url, url_prefixes, content_hash)
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                yield from get_links_json(v, url, url_prefixes, content_hash)
                continue
            elif not isinstance(v, str):
                continue
            # Use regex to find URLs in the string
            full_urls = set([])
            for new_url in re.findall(FULL_URL_PATTERN, v):
                new_url = new_url.split("#")[0]  # remove fragments
                full_urls.add(new_url)
                if is_valid_url(new_url) and new_url != url:
                    yield {
                        "source": url,
                        "target": new_url,
                        "text": k,
                        "xpath": None,  # TODO implement xpath
                        "source_hash": content_hash,
                        "follow": any(new_url.startswith(u) for u in url_prefixes),
                    }
            for new_url in re.findall(PATH_URL_PATTERN, v):
                # check if new_url is a subset of a known full url
                if any(new_url in u for u in full_urls):
                    continue
                # likly parsing error which includes the host and part of the protocol
                if new_url.startswith("/") and f"/{new_url}" in v:
                    continue
                # check if path is actually part of a url fragment
                if f"#{new_url}" in v:
                    continue
                new_url = urljoin(url, new_url)
                if is_valid_url(new_url) and new_url != url:
                    yield {
                        "source": url,
                        "target": new_url,
                        "text": k,
                        "xpath": None,  # TODO implement xpath
                        "source_hash": content_hash,
                        "follow": any(new_url.startswith(u) for u in url_prefixes),
                    }


def get_links_from_html(content, url, url_prefixes, content_hash):
    soup = BeautifulSoup(content, "html.parser")
    for a in soup.find_all("a", href=True):
        new_url = a["href"].split("#")[0]
        # Make the URL absolute
        new_url = urljoin(url, new_url)
        if is_valid_url(new_url) and new_url != url:
            yield {
                "source": url,
                "target": new_url,
                "text": a.text,
                "xpath": None,  # TODO implement xpath
                "source_hash": content_hash,
                "follow": any(new_url.startswith(u) for u in url_prefixes),
            }
