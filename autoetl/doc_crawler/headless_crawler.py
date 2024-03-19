import time

from playwright.async_api import async_playwright
from prefect import get_run_logger, task

from autoetl.doc_crawler.config import DEFAULT_BROWSER_TYPE, DEFAULT_USER_AGENT


@task(retries=3)
async def render_page(
    url: str, user_agent: str = DEFAULT_USER_AGENT, screenshot_path: str | None = None
):
    logger = get_run_logger()
    logger.debug(f"browser visit {DEFAULT_BROWSER_TYPE} {url}")
    start_time = time.time()
    async with async_playwright() as p:
        browser_type = getattr(p, DEFAULT_BROWSER_TYPE)
        browser = await browser_type.launch()
        page = await browser.new_page(
            user_agent=user_agent,
        )
        await page.goto(url)

        # TODO add more specific checks for when to wait
        if "app.swaggerhub.com" in url:
            await page.wait_for_timeout(5000)
        else:
            await page.wait_for_timeout(2000)

        content = await page.content()
        if screenshot_path:
            await page.screenshot(path=screenshot_path)
        await browser.close()

    return {
        "request": {
            "url": url,
            "user_agent": user_agent,
            "browser_type": DEFAULT_BROWSER_TYPE,
        },
        "response": {
            # "headers": dict(response.headers),
            # "cookies": dict(response.cookies),
            # "status_code": response.status_code,
            "elapsed_seconds": time.time() - start_time,
            # "num_bytes": ,
            "content_length": len(content),
            # "redirects": response.history,
            # "charset": response.encoding,
            # "content_type": response.headers.get("content-type"),
            # "retry_count": retry_count,
        },
        "content": content,
    }
