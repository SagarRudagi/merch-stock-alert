from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv


@dataclass
class SiteConfig:
    name: str
    url: str
    in_stock_selector: str
    use_js_render: bool
    in_stock_keywords: List[str]


@dataclass
class AppConfig:
    telegram_bot_token: str
    telegram_chat_ids: List[str]
    subject_prefix: str


def load_app_config(project_root: Path) -> AppConfig:
    load_dotenv(project_root / ".env")

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_ids = [
        chat_id.strip()
        for chat_id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",")
        if chat_id.strip()
    ]
    subject_prefix = os.getenv("SUBJECT_PREFIX", "[Stock Alert]")

    missing_telegram = []
    if not telegram_bot_token:
        missing_telegram.append("TELEGRAM_BOT_TOKEN")
    if not telegram_chat_ids:
        missing_telegram.append("TELEGRAM_CHAT_IDS")
    if missing_telegram:
        raise ValueError(
            "Missing required Telegram environment variables: "
            + ", ".join(missing_telegram)
        )

    return AppConfig(
        telegram_bot_token=telegram_bot_token,
        telegram_chat_ids=telegram_chat_ids,
        subject_prefix=subject_prefix,
    )


def load_sites(config_path: Path) -> List[SiteConfig]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    sites: List[SiteConfig] = []

    for site in data:
        sites.append(
            SiteConfig(
                name=site["name"],
                url=site["url"],
                in_stock_selector=site["in_stock_selector"],
                use_js_render=site.get("use_js_render", False),
                in_stock_keywords=[kw.lower() for kw in site.get("in_stock_keywords", [])],
            )
        )

    if not sites:
        raise ValueError("No sites configured. Add at least one item in sites.json")

    return sites
