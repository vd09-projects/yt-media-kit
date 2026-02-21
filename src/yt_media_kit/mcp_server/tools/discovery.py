"""
Discovery tools — browse and filter channel videos without downloading.
"""
from __future__ import annotations

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
