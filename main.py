"""CLI for a reproducible demo or a real Telegram public-group search."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
from types import SimpleNamespace

from finder import collect_groups, write_csv, write_report


DEMO_RESULTS = [
    ("Google Ads", [
        SimpleNamespace(id=101, title="Google Ads · Practice Lab", username="example_ads_practice_01", megagroup=True),
        SimpleNamespace(id=102, title="Ad Strategy News", username="example_ad_news_02", megagroup=False),
    ]),
    ("affiliate marketing", [
        SimpleNamespace(id=103, title="Affiliate Marketing Studio", username="example_affiliate_studio_03", megagroup=True),
        SimpleNamespace(id=101, title="Google Ads · Practice Lab", username="example_ads_practice_01", megagroup=True),
    ]),
    ("CPA marketing", [
        SimpleNamespace(id=104, title="CPA & Performance Forum", username="example_cpa_forum_04", megagroup=True),
        SimpleNamespace(id=105, title="Private test group", username=None, megagroup=True),
    ]),
]


async def search_live(queries: list[str], limit: int) -> list[tuple[str, list[object]]]:
    try:
        from telethon import TelegramClient, functions
    except ImportError as exc:
        raise SystemExit("Install live-mode dependency: python -m pip install -r requirements.txt") from exc
    api_id = os.environ.get("TG_API_ID", "")
    api_hash = os.environ.get("TG_API_HASH", "")
    if not api_id.isdecimal() or not api_hash:
        raise SystemExit("Set TG_API_ID and TG_API_HASH in your local environment before live mode.")

    results = []
    async with TelegramClient("telegram_finder", int(api_id), api_hash) as client:
        for query in queries:
            response = await client(functions.contacts.SearchRequest(q=query, limit=limit))
            results.append((query, list(response.chats)))
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search public Telegram groups and export CSV/HTML.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Use synthetic data; no Telegram account required.")
    mode.add_argument("--query", action="append", dest="queries", help="Search phrase; repeat for multiple phrases.")
    parser.add_argument("--limit", type=int, default=25, help="Maximum matches per live query (1–100).")
    parser.add_argument("--output", type=Path, default=Path("output/latest"), help="Output directory.")
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    if args.queries and any(len(query.strip()) < 3 for query in args.queries):
        parser.error("Each query must have at least 3 characters")
    return args


def main() -> None:
    args = parse_args()
    results = DEMO_RESULTS if args.demo else asyncio.run(search_live(args.queries, args.limit))
    groups = collect_groups(results, source="Synthetic demo" if args.demo else "Telegram public search")
    write_csv(groups, args.output / "groups.csv")
    write_report(groups, args.output / "report.html", demo=args.demo)
    print(f"Exported {len(groups)} public groups to {args.output.resolve()}")


if __name__ == "__main__":
    main()
