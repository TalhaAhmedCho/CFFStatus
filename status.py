#!/usr/bin/env python3
"""Fetch Codeforces user status and post to Discord webhook."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


CONFIG_PATH = "users.json"
API_ENDPOINT = "https://codeforces.com/api/user.info"
DEFAULT_ONLINE_THRESHOLD_SECONDS = 300


@dataclass
class UserStatus:
    handle: str
    rating: int | None
    last_online_seconds: int
    online: bool


class ConfigError(RuntimeError):
    pass


def load_handles() -> List[str]:
    env_handles = os.getenv("CF_HANDLES", "").strip()
    if env_handles:
        return [handle.strip() for handle in env_handles.split(",") if handle.strip()]

    if Path(CONFIG_PATH).exists():
        try:
            data = json.loads(Path(CONFIG_PATH).read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {CONFIG_PATH}: {exc}") from exc
        handles = data.get("handles")
        if isinstance(handles, list):
            cleaned = [str(handle).strip() for handle in handles if str(handle).strip()]
            if cleaned:
                return cleaned
        raise ConfigError(
            f"{CONFIG_PATH} must contain a non-empty 'handles' list or set CF_HANDLES."
        )

    raise ConfigError(
        "No handles configured. Set CF_HANDLES or create users.json."
    )


def fetch_user_info(handles: Iterable[str]) -> List[dict]:
    query = {"handles": ";".join(handles)}
    url = f"{API_ENDPOINT}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(url, headers={"User-Agent": "cffstatus-bot"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to reach Codeforces API: {exc}") from exc

    if payload.get("status") != "OK":
        raise RuntimeError(f"Codeforces API error: {payload}")

    result = payload.get("result", [])
    if not isinstance(result, list):
        raise RuntimeError("Unexpected API response format.")
    return result


def build_statuses(users: Iterable[dict], now: int, threshold: int) -> List[UserStatus]:
    statuses: List[UserStatus] = []
    for user in users:
        handle = user.get("handle", "unknown")
        last_online = int(user.get("lastOnlineTimeSeconds", 0))
        rating = user.get("rating")
        online = (now - last_online) <= threshold
        statuses.append(
            UserStatus(
                handle=handle,
                rating=rating if isinstance(rating, int) else None,
                last_online_seconds=last_online,
                online=online,
            )
        )
    return statuses


def format_message(statuses: Iterable[UserStatus], now: int) -> str:
    lines = ["**Codeforces Status Update**", ""]
    for status in statuses:
        status_label = "🟢 Online" if status.online else "⚪ Offline"
        minutes_ago = max(0, (now - status.last_online_seconds) // 60)
        rating_label = f" (rating {status.rating})" if status.rating is not None else ""
        lines.append(
            f"- `{status.handle}`{rating_label}: {status_label} · last online {minutes_ago} min ago"
        )
    return "\n".join(lines)


def post_to_discord(webhook_url: str, message: str) -> None:
    payload = json.dumps({"content": message}).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status >= 400:
                raise RuntimeError(f"Discord webhook error: HTTP {response.status}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to send Discord webhook: {exc}") from exc


def main() -> int:
    try:
        handles = load_handles()
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    webhook_url = os.getenv("DISCORD_WEBHOOK")
    if not webhook_url:
        print("DISCORD_WEBHOOK is not set.", file=sys.stderr)
        return 1

    threshold = int(
        os.getenv("CF_ONLINE_THRESHOLD_SECONDS", DEFAULT_ONLINE_THRESHOLD_SECONDS)
    )
    now = int(time.time())
    users = fetch_user_info(handles)
    statuses = build_statuses(users, now, threshold)
    message = format_message(statuses, now)
    post_to_discord(webhook_url, message)
    print("Posted status update for:", ", ".join(handles))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
