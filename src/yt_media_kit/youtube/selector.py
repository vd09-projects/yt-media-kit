from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from yt_media_kit.core.config import TopVideosConfig
from yt_media_kit.core.utils import is_short


def select_top_videos(
    entries: List[Dict[str, Any]],
    cfg: TopVideosConfig,
) -> List[Dict[str, Any]]:

    cutoff_date: datetime | None = None
    if cfg.max_age_days is not None:
        cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=cfg.max_age_days)

    filtered = []
    for e in entries:
        if not cfg.include_shorts and is_short(e):
            continue
        if isinstance(e.get("view_count"), int) and e["view_count"] < cfg.min_view_count:
            continue
        if cfg.min_duration_seconds and isinstance(e.get("duration"), (int, float)):
            if e["duration"] < cfg.min_duration_seconds:
                continue
        if cutoff_date is not None:
            upload_date = e.get("upload_date")  # format: "YYYYMMDD"
            if upload_date and len(upload_date) == 8:
                video_date = datetime(
                    int(upload_date[:4]), int(upload_date[4:6]), int(upload_date[6:]),
                    tzinfo=timezone.utc,
                )
                if video_date < cutoff_date:
                    continue
        filtered.append(e)

    key = cfg.sort_by
    limit = min(cfg.count, len(filtered))
    return sorted(
        filtered,
        key=lambda x: x.get(key) or 0,
        reverse=True,
    )[: limit]