# Merch Stock Alert Bot

A Python bot that checks whether a product name is listed on a page and sends a Telegram alert.

## Features

- Polls product listing pages on an interval.
- Supports JavaScript-rendered pages using Playwright.
- Sends Telegram alerts to one or more chat IDs.
- Prevents duplicate alerts until the item disappears and appears again.

## 1) Setup

```bash
cd "merch-stock-alert"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## 2) Configure environment

```bash
cp .env.example .env
```

Required `.env` keys:

- `TELEGRAM_BOT_TOKEN=<your_bot_token>`
- `TELEGRAM_CHAT_IDS=<comma separated chat ids>`

## 3) Configure target item

```bash
cp config/sites.json.example config/sites.json
```

Edit `config/sites.json`:

- `name`: Label used in logs and alerts.
- `url`: Listing page URL.
- `in_stock_selector`: Selector whose text contains product names.
- `use_js_render`: `true` when page is JS-rendered.
- `in_stock_keywords`: Exact product names to match.

## 4) Run

One-time check:

```bash
PYTHONPATH=src python main.py --once
```

Continuous mode every 2 minutes:

```bash
PYTHONPATH=src python main.py --interval 120
```

## 5) Run 24/7 on GitHub Actions

This project includes [`.github/workflows/stock-check.yml`](.github/workflows/stock-check.yml), which runs every 5 minutes in the cloud.

### Required one-time setup

1. Create a GitHub repository and push this project.
2. In the repository, open Settings -> Secrets and variables -> Actions -> New repository secret.
3. Add these secrets:
	- `TELEGRAM_BOT_TOKEN`
	- `TELEGRAM_CHAT_IDS`
	- `SUBJECT_PREFIX` (optional)
4. Open the Actions tab and run `Stock Check` once with `workflow_dispatch`.

After that, checks run automatically even when your laptop is off.
