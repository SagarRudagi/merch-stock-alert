from __future__ import annotations

import requests

from .config import AppConfig


def send_telegram_alert(
    app_config: AppConfig,
    product_name: str,
    product_url: str,
) -> None:
    if not app_config.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is required for Telegram notifications")
    if not app_config.telegram_chat_ids:
        raise ValueError("TELEGRAM_CHAT_IDS is required for Telegram notifications")

    api_url = f"https://api.telegram.org/bot{app_config.telegram_bot_token}/sendMessage"
    message = (
        f"{app_config.subject_prefix} {product_name} is listed now.\n"
        f"Link: {product_url}"
    )

    for chat_id in app_config.telegram_chat_ids:
        response = requests.post(
            api_url,
            json={"chat_id": chat_id, "text": message},
            timeout=20,
        )
        response.raise_for_status()
