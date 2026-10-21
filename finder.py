"""Pure result processing and exports for public Telegram group search."""

from __future__ import annotations

import csv
import html
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


@dataclass(frozen=True)
class Group:
    id: int
    title: str
    username: str
    matched_queries: tuple[str, ...]
    source: str = "Telegram public search"

    @property
    def url(self) -> str:
        return f"https://t.me/{quote(self.username)}"


def collect_groups(search_results: list[tuple[str, list[object]]], *, source: str = "Telegram public search") -> list[Group]:
    """Keep public supergroups only; merge query matches by Telegram chat ID."""
    found: dict[int, Group] = {}
    for query, chats in search_results:
        for chat in chats:
            if not getattr(chat, "megagroup", False):
                continue
            username = getattr(chat, "username", None)
            if not username:
                continue
            chat_id = int(getattr(chat, "id"))
            previous = found.get(chat_id)
            matches = previous.matched_queries if previous else ()
            if query not in matches:
                matches += (query,)
            found[chat_id] = Group(
                id=chat_id,
                title=str(getattr(chat, "title", "")) or username,
                username=username,
                matched_queries=matches,
                source=source,
            )
    return sorted(found.values(), key=lambda group: (group.title.casefold(), group.id))


def write_csv(groups: list[Group], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["title", "username", "url", "matched_queries", "source"])
        for group in groups:
            writer.writerow([group.title, group.username, group.url, "; ".join(group.matched_queries), group.source])


def write_report(groups: list[Group], destination: Path, *, demo: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(
        "<tr>"
        f"<td><strong>{html.escape(group.title)}</strong><small>@{html.escape(group.username)}</small></td>"
        f"<td>{html.escape(', '.join(group.matched_queries))}</td>"
        f"<td><a href=\"{html.escape(group.url, quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">Open ↗</a></td>"
        "</tr>"
        for group in groups
    )
    if not rows:
        rows = '<tr><td colspan="3" class="empty">No public groups found for these queries.</td></tr>'
    badge = "SYNTHETIC DEMO DATA" if demo else "TELEGRAM PUBLIC SEARCH"
    note = "These entries are fictional examples, not verified Telegram groups." if demo else "Telegram search is limited; verify each group manually."
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Public group discovery · Telegram</title>
<style>
:root{{--ink:#13283b;--muted:#65778a;--line:#dce8f0;--paper:#fff;--sky:#eaf6fa;--teal:#097f87;--mint:#dcf4e8}}
*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(135deg,#e9f5f7,#f6fbfc 55%,#eaf5ed);color:var(--ink);font:16px/1.5 'Segoe UI',Arial,sans-serif}}
.shell{{max-width:1020px;margin:48px auto;padding:0 24px}}.top{{display:flex;align-items:center;gap:12px;color:var(--teal);font-size:14px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}}
.mark{{width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:var(--teal);color:#fff;font-size:18px;letter-spacing:0}}
h1{{font-size:clamp(34px,5vw,58px);line-height:1.05;letter-spacing:-.055em;margin:28px 0 12px}}.lead{{color:var(--muted);max-width:650px;margin:0 0 28px}}
.summary{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px}}.tile{{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:17px 20px;min-width:180px;box-shadow:0 8px 30px #16304408}}
.tile b{{display:block;font-size:28px;line-height:1.1}}.tile span{{color:var(--muted);font-size:13px}}.badge{{display:inline-block;background:var(--mint);border-radius:99px;color:#166353;padding:8px 13px;font-size:12px;font-weight:800;letter-spacing:.08em}}
.panel{{overflow:hidden;background:var(--paper);border:1px solid var(--line);border-radius:20px;box-shadow:0 16px 50px #1630440b}}
.panel-head{{padding:22px 26px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:15px}}h2{{font-size:19px;margin:0}}.panel-head span{{color:var(--muted);font-size:13px}}
table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:17px 26px;border-bottom:1px solid #edf2f5}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.09em;background:#f8fbfc}}tr:last-child td{{border-bottom:0}}td small{{display:block;color:var(--muted);margin-top:3px}}a{{color:var(--teal);font-weight:700;text-decoration:none}}a:hover{{text-decoration:underline}}.empty{{text-align:center;color:var(--muted);padding:40px}}footer{{color:var(--muted);font-size:13px;margin:18px 2px 40px}}
@media(max-width:600px){{.shell{{margin:25px auto;padding:0 14px}}th,td{{padding:14px 11px;font-size:13px}}.panel-head{{padding:18px}}.tile{{flex:1}}}}
</style></head><body><main class="shell"><div class="top"><span class="mark">↗</span> Public discovery / Telegram</div>
<h1>Find the right<br>conversations.</h1><p class="lead">A focused export of public Telegram groups discovered from multiple search phrases, with duplicate results combined.</p>
<div class="summary"><div class="tile"><b>{len(groups)}</b><span>public groups</span></div><div class="tile"><b>{len({q for g in groups for q in g.matched_queries})}</b><span>matched queries</span></div><div class="tile"><span class="badge">{badge}</span></div></div>
<section class="panel"><div class="panel-head"><h2>Search results</h2><span>Public groups only</span></div><table><thead><tr><th>Group</th><th>Matched query</th><th>Link</th></tr></thead><tbody>{rows}</tbody></table></section>
<footer>{html.escape(note)} No members or messages are collected.</footer></main></body></html>"""
    destination.write_text(page, encoding="utf-8")
