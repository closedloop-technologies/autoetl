import asyncio
from typing import Iterator, Optional

import requests
from autoetl.apis.models import API
from autoetl.apis.openapi_spec_2 import OpenAPIObject
from autoetl.doc_crawler.crawler_flow import crawl


def get_likely_openapi_spec(
    openapi_spec_url: Optional[str] = None,
    seed_urls: Optional[list[str]] = None,
) -> Iterator[tuple[str, dict, bool]]:
    """Finds the openapi spec from the openapi spec url or seed urls"""
    request = requests.get(openapi_spec_url)
    if request.status_code == 200:
        # content_type = dict(request.headers).get("Content-Type")
        data = request.json()
        if isinstance(data, dict):
            top_level_keys = set(data.keys())
            if "swaggar" in top_level_keys and "info" in top_level_keys:
                yield openapi_spec_url, data, True
                return
            else:
                yield openapi_spec_url, data, False
        else:
            yield openapi_spec_url, data, False
    else:
        for url in seed_urls:
            request = requests.get(url)
            if request.status_code == 200:
                # content_type = dict(request.headers).get("Content-Type")
                data = request.json()
                if isinstance(data, dict):
                    top_level_keys = set(data.keys())
                    if "swaggar" in top_level_keys and "info" in top_level_keys:
                        yield url, data, True
                        return
                    else:
                        yield url, data, False
                else:
                    yield url, data, False
            else:
                yield url, None, False


def main():
    url = API(
        id="petstore",
        name="Petstore",
        openapi_spec_url="https://petstore.swagger.io/v2/swagger.json",
        docs=["https://petstore.swagger.io/"],
    )
    # TODO Locate openapi spec
    seed_urls = url.seed_urls + [url.openapi_spec_url] + url.docs
    asyncio.run(crawl("petstore2", seed_urls))

    # for openapi_spec_url, spec, match_score in get_likely_openapi_spec(
    #     url.openapi_spec_url
    # ):
    #     # Save files to project directory
    #     print(spec)
    # TODO Create OpenAPIObject from openapi spec
    # Determine missing fields of OpenAPIObject
    # Build basic source graph from OpenAPIObject
    #


if __name__ == "__main__":
    main()
