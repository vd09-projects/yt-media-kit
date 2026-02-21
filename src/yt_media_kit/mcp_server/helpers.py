"""Config merge helpers shared across tool modules."""
from __future__ import annotations

from yt_media_kit.core.config import OutputConfig, TopVideosConfig


def merge_top_videos(
    base: TopVideosConfig,
    count: int | None,
    sort_by: str | None,
    min_view_count: int | None,
    include_shorts: bool | None,
    min_duration_seconds: int | None,
    max_duration_seconds: int | None,
) -> TopVideosConfig:
    return TopVideosConfig(
        count=count if count is not None else base.count,
        sort_by=sort_by if sort_by is not None else base.sort_by,
        min_view_count=min_view_count if min_view_count is not None else base.min_view_count,
        include_shorts=include_shorts if include_shorts is not None else base.include_shorts,
        min_duration_seconds=(
            min_duration_seconds if min_duration_seconds is not None else base.min_duration_seconds
        ),
        max_duration_seconds=(
            max_duration_seconds if max_duration_seconds is not None else base.max_duration_seconds
        ),
        flat_extract=base.flat_extract,
    )


def merge_output(base: OutputConfig, output_base_dir: str | None) -> OutputConfig:
    if output_base_dir is None:
        return base
    return OutputConfig(
        base_dir=output_base_dir,
        shorts_subdir=base.shorts_subdir,
        regular_subdir=base.regular_subdir,
        filename_template=base.filename_template,
    )
