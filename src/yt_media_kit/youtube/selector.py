from typing import Dict, Any, List
from yt_media_kit.core.config import TopVideosConfig
from yt_media_kit.core.utils import is_short


def select_top_videos(
    entries: List[Dict[str, Any]],
    cfg: TopVideosConfig,
) -> List[Dict[str, Any]]:

    filtered = []
    for e in entries:
        if not cfg.include_shorts and is_short(e):
            continue
        if isinstance(e.get("view_count"), int) and e["view_count"] < cfg.min_view_count:
            continue
        if cfg.min_duration_seconds and isinstance(e.get("duration"), (int, float)):
            if e["duration"] < cfg.min_duration_seconds:
                continue
        filtered.append(e)

    key = cfg.sort_by
    limit = min(cfg.count, len(filtered))
    return sorted(
        filtered,
        key=lambda x: x.get(key) or 0,
        reverse=True,
    )[: limit]