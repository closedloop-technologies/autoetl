import asyncio
from functools import lru_cache
from typing import (
    IO,
    Any,
    AsyncIterable,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)
from urllib.parse import urlparse

import httpx
from prefect import flow, get_run_logger, task
from ratelimit import limits, sleep_and_retry
from rich import print

from autoetl.doc_crawler.config import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RATE_LIMIT,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
)

# From httpx._types.py
RequestContent = Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]
RequestData = Mapping[str, Any]
FileContent = Union[IO[bytes], bytes, str]
FileTypes = Union[
    FileContent,
    Tuple[Optional[str], FileContent],
    Tuple[Optional[str], FileContent, Optional[str]],
    Tuple[Optional[str], FileContent, Optional[str], Mapping[str, str]],
]
RequestFiles = Union[Mapping[str, FileTypes], Sequence[Tuple[str, FileTypes]]]
# End from httpx._types.py


def is_valid_url(url: str) -> bool:
    """Check if a URL has a valid syntax."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def url_domain(url: str) -> str:
    """Get the domain from a URL."""
    return urlparse(url).netloc


def _format_request_object(request_obj):
    d = request_obj.__dict__
    if "stream" in d:
        del d["stream"]
    d["headers"] = dict(d["headers"])
    d["url"] = str(d["url"])
    for k in list(d.keys()):
        if k.startswith("_"):
            del d[k]
    return d


def _format_response_object(retry_count, response):
    return {
        "headers": dict(response.headers),
        "cookies": dict(response.cookies),
        "status_code": response.status_code,
        "elapsed_seconds": response.elapsed.total_seconds(),
        "num_bytes": response.num_bytes_downloaded,
        "redirects": response.history,
        "charset": response.encoding,
        "content_type": response.headers.get("content-type"),
        "retry_count": retry_count,
    }


@sleep_and_retry
@limits(calls=DEFAULT_RATE_LIMIT, period=1)
@lru_cache(maxsize=128)
async def _request_with_retry(
    url: str,
    verb: str = "GET",
    timeout: int = DEFAULT_TIMEOUT,
    follow_redirects: bool = True,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    user_agent: str = DEFAULT_USER_AGENT,
    auth: httpx.Auth = None,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    retry_count=0,
):
    """Get the content of a URL with retry and exponential backoff."""
    verb = verb.upper()
    logger = get_run_logger()
    logger.debug(f"request {verb} {url}")
    if verb not in ["GET", "HEAD", "POST", "PATCH", "PUT", "DELETE"]:
        raise ValueError(f"Unsupported verb: {verb}")

    try:
        async with httpx.AsyncClient(auth=auth) as client:
            if verb in {"GET", "HEAD"}:
                response = await getattr(client, verb.lower())(
                    url,
                    headers={"User-Agent": user_agent},
                    timeout=timeout,
                    follow_redirects=follow_redirects,
                )
            else:  # POST, PATCH, PUT, DELETE
                client.post(url, data={"key": "value"})
                response = await getattr(client, verb.lower())(
                    url,
                    headers={"User-Agent": user_agent},
                    timeout=timeout,
                    follow_redirects=follow_redirects,
                    content=content,
                    data=data,
                    files=files,
                )
            response.raise_for_status()
            return {
                "request": _format_request_object(response.request),
                "response": _format_response_object(retry_count, response),
                "content": response.text,
            }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(
                    f"Max retries reached for URL: {url}. Raising exception..."
                )
                raise e
            backoff_time = backoff_factor * (2 ** (retry_count - 1))
            logger.warning(
                f"Request failed with status code 429. Retrying in {backoff_time} seconds..."
            )
            await asyncio.sleep(backoff_time)
            return await request_with_retry(
                url,
                verb,
                timeout,
                follow_redirects,
                max_retries,
                backoff_factor,
                user_agent,
                auth,
                content,
                data,
                files,
                retry_count,
            )
        else:
            logger.error(
                f"Request failed with status code {e.response.status_code} for URL: {url}"
            )
            return {
                "request": _format_request_object(e.request),
                "response": _format_response_object(retry_count, response),
                "error_code": e.response.status_code,
                "error_message": str(e),
            }
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        logger.error(f"Request failed due to {type(e).__name__} for URL: {url}")
        return {
            "request": _format_request_object(e.request),
            "error_code": str(type(e).__name__),
            "error_message": str(e),
        }


@task()  # Retry is handled in _request_with_retry
async def request_with_retry(
    url: str,
    verb: str = "GET",
    timeout: int = DEFAULT_TIMEOUT,
    follow_redirects: bool = True,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    user_agent: str = DEFAULT_USER_AGENT,
    auth: httpx.Auth = None,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    retry_count=0,
):
    return await _request_with_retry(
        url=url,
        verb=verb,
        timeout=timeout,
        follow_redirects=follow_redirects,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        user_agent=user_agent,
        auth=auth,
        content=content,
        data=data,
        files=files,
        retry_count=retry_count,
    )


@flow()
async def main():
    result = await request_with_retry("https://api.ogtags.dev/openapi.json")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
