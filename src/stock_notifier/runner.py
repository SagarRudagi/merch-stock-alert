from __future__ import annotations

import argparse
import time
from pathlib import Path

from .config import load_app_config, load_sites
from .notifier import send_telegram_alert
from .scraper import check_stock


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check stock and send Telegram alerts")
    parser.add_argument(
        "--config",
        default="config/sites.json",
        help="Path to JSON site configuration file",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=120,
        help="Polling interval in seconds",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one check and exit",
    )
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[2]

    app_config = load_app_config(project_root)
    sites = load_sites(project_root / args.config)

    # Avoid duplicate notifications for the same site until stock goes out and returns.
    already_notified = {site.url: False for site in sites}

    while True:
        print("Checking stock...")
        for site in sites:
            result = check_stock(site)
            print(f"[{result.site_name}] {result.message}")

            if result.in_stock and not already_notified[site.url]:
                send_telegram_alert(
                    app_config=app_config,
                    product_name=result.site_name,
                    product_url=result.url,
                )
                already_notified[site.url] = True
                print(f"Alert sent for {result.site_name}")
            elif not result.in_stock:
                already_notified[site.url] = False

        if args.once:
            break

        time.sleep(args.interval)
