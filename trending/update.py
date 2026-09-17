"""Refresh README trending tools: GITHUB_TOKEN=... python3 trending/update.py."""

import json
import os
from pathlib import Path
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen


TOP_N = 5
README = Path(__file__).resolve().parents[1] / "README.md"
START = "<!-- trending:start -->"
END = "<!-- trending:end -->"


def discover(readme):
    directory = readme.split("\n## Directory\n", 1)[1].split("\n## ", 1)[0]
    seen = set()
    tools = []
    for name, repo in re.findall(
        r"^\|\s*\[([^\]]+)\]\(https://github\.com/([^/\s?#)]+/[^/\s?#)]+)/?\)",
        directory,
        re.MULTILINE,
    ):
        if repo.casefold() not in seen:
            seen.add(repo.casefold())
            tools.append((name, repo))
    return tools


def fetch(repo, endpoint, token):
    request = Request(
        f"https://api.github.com/repos/{repo}/stargazers/{endpoint}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "awesome-voice-typing-trending",
        },
    )
    for attempt in range(3):
        try:
            with urlopen(request, timeout=20) as response:
                return json.load(response)
        except (OSError, ValueError) as error:
            print(f"{repo} {endpoint}: {error}", file=sys.stderr)
            if attempt == 2:
                raise
            time.sleep(2)


def calculate(history, today):
    first_day = today - timedelta(days=30)
    gained = 0
    for week in history:
        week_start = datetime.fromtimestamp(week["week"], timezone.utc).date()
        for offset, count in enumerate(week["days"]):
            day = week_start + timedelta(days=offset)
            if first_day <= day < today:
                gained += count
    return gained


def render(rows, today):
    lines = [
        f"Based on stars gained in the last 30 days | Last updated: {today:%Y-%m-%d}",
        "",
        "| Tool | Stars gained (30 days) | Total stars | Growth |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, repo, gained, total in sorted(
        rows, key=lambda row: (-row[2], row[0].casefold())
    )[:TOP_N]:
        initial = total - gained
        growth = f"{gained / initial * 100:.1f}%" if initial > 0 else "—"
        lines.append(
            f"| [{name}](https://github.com/{repo}) | {gained:,} | {total:,} | {growth} |"
        )
    return "\n".join(lines)


def replace_block(readme, content):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain one trending:start and trending:end marker")
    start = readme.index(START) + len(START)
    end = readme.index(END)
    if end < start:
        raise ValueError("README trending markers are out of order")
    return readme[:start] + "\n\n" + content + "\n\n" + readme[end:]


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("Set GITHUB_TOKEN before running the updater")
    readme = README.read_text(encoding="utf-8")
    replace_block(readme, "")
    today = datetime.now(timezone.utc).date()
    rows = []
    for name, repo in discover(readme):
        try:
            history = fetch(repo, "history?per_page=6", token)
            total = fetch(repo, "count", token)["count"]
            rows.append((name, repo, calculate(history, today), total))
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"Skipping {repo}: {error}", file=sys.stderr)
    if not rows:
        print("No repository data available; README unchanged.", file=sys.stderr)
        return
    updated = replace_block(readme, render(rows, today))
    if updated != readme:
        README.write_text(updated, encoding="utf-8")
    print(f"Trending updated from {len(rows)} repositories.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, IndexError) as error:
        sys.exit(str(error))
