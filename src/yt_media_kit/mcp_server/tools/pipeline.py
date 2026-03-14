"""
Pipeline tools — full channel pipeline and audio-only pipeline.
"""
from __future__ import annotations

import dataclasses

from yt_media_kit.core.config import AudioConfig, AudioOnlyConfig
from yt_media_kit.mcp_server import context
from yt_media_kit.mcp_server.helpers import merge_output, merge_top_videos
from yt_media_kit.pipeline.audio_runner import run_audio_pipeline as _run_audio_pipeline
from yt_media_kit.pipeline.runner import run_pipeline as _run_pipeline

from . import mcp


@mcp.tool()
def run_pipeline(
    channels: list[str] | None = None,
    output_base_dir: str | None = None,
    count: int | None = None,
    sort_by: str | None = None,
    min_view_count: int | None = None,
    include_shorts: bool | None = None,
    min_duration_seconds: int | None = None,
    max_duration_seconds: int | None = None,
    max_age_days: int | None = None,
) -> str:
    """
    Run the full channel pipeline: discover top videos, download subtitles
    (and optionally audio) for each video.

    All arguments are optional — omitted fields fall back to the base config.yaml.

    Args:
        channels: YouTube channel URLs to process (overrides config channels).
        output_base_dir: Base directory for downloaded files.
        count: Max number of videos to process per channel.
        sort_by: Sort criterion — view_count | like_count | upload_date | duration.
        min_view_count: Minimum view count threshold.
        include_shorts: Whether to include YouTube Shorts.
        min_duration_seconds: Minimum video duration in seconds.
        max_duration_seconds: Maximum video duration in seconds.
        max_age_days: Only include videos uploaded within this many days (e.g. 30 = last month, 60 = last 2 months). None = all time.
    """
    cfg = dataclasses.replace(
        context.cfg,
        channels=channels if channels is not None else context.cfg.channels,
        top_videos=merge_top_videos(
            context.cfg.top_videos,
            count, sort_by, min_view_count,
            include_shorts, min_duration_seconds, max_duration_seconds,
            max_age_days,
        ),
        output=merge_output(context.cfg.output, output_base_dir),
    )
    ok = _run_pipeline(cfg, context.logger, context.yt_client)
    return (
        "Pipeline complete — all downloads succeeded."
        if ok
        else "Pipeline finished with some errors (check logs)."
    )


@mcp.tool()
def run_audio_pipeline(
    video_urls: list[str],
    output_base_dir: str | None = None,
    audio_format: str | None = None,
    quality: str | None = None,
) -> str:
    """
    Download audio for a list of explicit YouTube video URLs.

    Args:
        video_urls: One or more YouTube video URLs.
        output_base_dir: Base directory for downloaded files.
        audio_format: Audio codec — mp3 | wav | m4a | opus.
        quality: Bitrate in kbps, e.g. "128", "192", "320".
    """
    base_audio = context.cfg.audio or AudioConfig(enabled=True, format="mp3", quality="192")
    audio_cfg = AudioConfig(
        enabled=True,
        format=audio_format if audio_format is not None else base_audio.format,
        quality=quality if quality is not None else base_audio.quality,
    )
    audio_only_cfg = AudioOnlyConfig(
        videos=video_urls,
        audio=audio_cfg,
        output=merge_output(context.cfg.output, output_base_dir),
        runtime=context.cfg.runtime,
    )
    ok = _run_audio_pipeline(audio_only_cfg, context.logger, context.yt_client)
    return (
        "Audio pipeline complete."
        if ok
        else "Audio pipeline finished with some errors (check logs)."
    )
