import os
from typing import Dict, Any


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def is_short(entry: Dict[str, Any]) -> bool:
    dur = entry.get("duration")
    url = entry.get("webpage_url") or entry.get("url") or ""
    return (isinstance(dur, int) and dur <= 60) or "/shorts/" in url


def entry_to_url(entry: Dict[str, Any]) -> str | None:
    if entry.get("webpage_url"):
        return entry["webpage_url"]
    if entry.get("url"):
        # return f"https://www.youtube.com/watch?v={entry['url']}"
        return entry['url']
    return None