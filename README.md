# Public Telegram Group Finder

A small, honest portfolio example: search Telegram's public directory for groups by several queries, remove duplicate results, and export a CSV plus a browsable HTML report. It uses the Telegram **user API** through Telethon; the Bot API cannot perform this global search.

The search is a **limited sample of Telegram's results**, not a complete directory of every group about a topic. Only public supergroups with a username are exported. Broadcast channels, users, private chats, member lists, and messages are excluded. The tool never joins a group or sends a message.

## Try it without an account

```powershell
python main.py --demo --output output/demo
```

Open `output/demo/report.html` or inspect `output/demo/groups.csv`. All demo records are synthetic and labeled as such.

## Search live Telegram

Create an API ID and API hash for your own Telegram account at [my.telegram.org](https://my.telegram.org). Set them locally as environment variables; do not commit them or the session file:

```powershell
$env:TG_API_ID = "your_api_id"
$env:TG_API_HASH = "your_api_hash"
python main.py --query "Google Ads" --query "affiliate marketing" --query "CPA marketing" --limit 25 --output output/live
```

On first use, Telethon will ask for your phone number and Telegram login code interactively. The session is saved locally as `telegram_finder.session` and ignored by Git. Search results depend on Telegram's index, query wording, account, and API limits. `--limit` is a per-query upper bound, not a promise of that many matches. The code deliberately makes requests sequentially; Telegram may still impose rate limits. No automated retry or account rotation is used.

CSV fields: `title`, `username`, `url`, `matched_queries`, `source`. The report escapes all titles and links before rendering. Review results manually before using them as prospect data.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Project scope

This is a working sample for discovering public **groups** and preparing a clean shortlist. A production assignment would still need agreed search phrases, quality criteria, desired volume, and manual validation. It does not scrape a hidden Telegram database or claim exhaustive coverage.
