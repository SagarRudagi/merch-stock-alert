from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .config import SiteConfig


@dataclass
class StockCheckResult:
    site_name: str
    url: str
    in_stock: bool
    message: str


def _fetch_rendered_text(site: SiteConfig) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is required for use_js_render=true. Install with: "
            "pip install playwright && playwright install chromium"
        ) from exc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(site.url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        text = page.inner_text(site.in_stock_selector)
        browser.close()
    return text.lower()


def check_stock(site: SiteConfig, timeout_seconds: int = 20) -> StockCheckResult:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(site.url, headers=headers, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.RequestException as exc:
        return StockCheckResult(
            site_name=site.name,
            url=site.url,
            in_stock=False,
            message=f"Failed to fetch page: {exc}",
        )

    soup = BeautifulSoup(response.text, "html.parser")
    node: Optional[object] = soup.select_one(site.in_stock_selector)

    if node is None:
        return StockCheckResult(
            site_name=site.name,
            url=site.url,
            in_stock=False,
            message=(
                "Selector not found. Update 'in_stock_selector' for this site. "
                f"Selector used: {site.in_stock_selector}"
            ),
        )

    text = node.get_text(" ", strip=True).lower()  # type: ignore[attr-defined]

    if site.use_js_render:
        try:
            text = _fetch_rendered_text(site)
        except Exception as exc:
            return StockCheckResult(
                site_name=site.name,
                url=site.url,
                in_stock=False,
                message=f"JS render failed: {exc}",
            )

    is_listed = any(keyword in text for keyword in site.in_stock_keywords)
    state = "LISTED" if is_listed else "NOT LISTED"
    return StockCheckResult(
        site_name=site.name,
        url=site.url,
        in_stock=is_listed,
        message=f"{state}. Checked selector text for configured item keywords.",
    )
