"""
Discovery tools — browse and filter channel videos without downloading.
"""
from __future__ import annotations

import os
from collections import defaultdict

from yt_media_kit.mcp_server import context
from yt_media_kit.mcp_server.helpers import merge_top_videos
from yt_media_kit.youtube.selector import select_top_videos

from . import mcp

_KEEP = {
    "id", "title", "url", "webpage_url",
    "view_count", "like_count", "duration",
    "upload_date", "channel", "channel_url",
}


@mcp.tool()
def list_channel_videos(
    channel_url: str,
    count: int | None = None,
    sort_by: str | None = None,
    min_view_count: int | None = None,
    include_shorts: bool | None = None,
    min_duration_seconds: int | None = None,
    max_duration_seconds: int | None = None,
) -> list[dict]:
    """
    Discover and filter top videos from a YouTube channel without downloading anything.
    Returns a list of video metadata dicts.

    Args:
        channel_url: YouTube channel or playlist URL.
        count: Max number of videos to return.
        sort_by: Sort criterion — view_count | like_count | upload_date | duration.
        min_view_count: Minimum view count threshold.
        include_shorts: Whether to include YouTube Shorts.
        min_duration_seconds: Minimum video duration in seconds.
        max_duration_seconds: Maximum video duration in seconds.
    """
    tv_cfg = merge_top_videos(
        context.cfg.top_videos,
        count, sort_by, min_view_count,
        include_shorts, min_duration_seconds, max_duration_seconds,
    )
    entries = context.yt_client.list_channel_videos(channel_url, tv_cfg.flat_extract)
    top = select_top_videos(entries, tv_cfg)
    return [{k: v for k, v in e.items() if k in _KEEP} for e in top]


@mcp.tool()
def list_downloaded_files(
    extensions: list[str] | None = None,
    output_base_dir: str | None = None,
) -> list[dict]:
    """
    Scan the output directory and return all downloaded files, grouped by extension.
    Useful for seeing what has already been downloaded before running a pipeline.

    Args:
        extensions: Filter by file extensions, e.g. ["vtt", "txt", "mp3"].
                    Omit to return every file found.
        output_base_dir: Directory to scan. Defaults to the configured output base_dir.
    """
    base_dir = output_base_dir or context.cfg.output.base_dir

    if not os.path.isdir(base_dir):
        return []

    filter_exts = {e.lstrip(".").lower() for e in extensions} if extensions else None

    results: list[dict] = []
    for root, _, files in os.walk(base_dir):
        for fname in files:
            ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            if filter_exts and ext not in filter_exts:
                continue
            full_path = os.path.join(root, fname)
            results.append({
                "path": full_path,
                "filename": fname,
                "extension": ext,
                "size_bytes": os.path.getsize(full_path),
                "subdir": os.path.relpath(root, base_dir),
            })

    return sorted(results, key=lambda f: f["path"])
