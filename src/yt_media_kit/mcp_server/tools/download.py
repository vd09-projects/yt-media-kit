"""
Download tools — subtitles and audio for individual videos.
"""
from __future__ import annotations

from yt_media_kit.core.config import AudioConfig, SubtitlesConfig
from yt_media_kit.mcp_server import context
from yt_media_kit.mcp_server.helpers import merge_output
from yt_media_kit.ops.vtt_to_text import save_transcript_for_vtt

from . import mcp


@mcp.tool()
def download_subtitles(
    video_url: str,
    output_base_dir: str | None = None,
    languages: list[str] | None = None,
    subtitle_format: str | None = None,
) -> str:
    """
    Download subtitles for a single YouTube video and convert VTT to plain text.

    Args:
        video_url: YouTube video URL.
        output_base_dir: Base directory for downloaded files.
        languages: Language codes to download, e.g. ["en", "es"].
        subtitle_format: Subtitle format — vtt | srt.
    """
    subs_cfg = SubtitlesConfig(
        languages=languages if languages is not None else context.cfg.subtitles.languages,
        prefer_manual=context.cfg.subtitles.prefer_manual,
        download_auto=context.cfg.subtitles.download_auto,
        format=subtitle_format if subtitle_format is not None else context.cfg.subtitles.format,
    )
    out_cfg = merge_output(context.cfg.output, output_base_dir)

    ok, subtitle_paths = context.yt_client.download_subtitles(
        video_url, subs_cfg, out_cfg, context.cfg.runtime.retries
    )
    if not ok:
        return f"Failed to download subtitles for {video_url}"

    transcripts = []
    for vtt_path in subtitle_paths:
        txt_path = save_transcript_for_vtt(vtt_path, context.logger)
        if txt_path:
            transcripts.append(txt_path)

    if transcripts:
        return f"Subtitles downloaded and transcripts saved: {', '.join(transcripts)}"
    elif subtitle_paths:
        return f"Subtitles downloaded: {', '.join(subtitle_paths)} (no transcript generated)"
    else:
        return "Subtitles downloaded (paths not returned by yt-dlp)"


@mcp.tool()
def download_audio(
    video_url: str,
    output_base_dir: str | None = None,
    audio_format: str | None = None,
    quality: str | None = None,
) -> str:
    """
    Download audio for a single YouTube video.

    Args:
        video_url: YouTube video URL.
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
    out_cfg = merge_output(context.cfg.output, output_base_dir)

    ok, filepath = context.yt_client.download_audio(
        video_url, audio_cfg, out_cfg, context.cfg.runtime.retries
    )
    if ok and filepath:
        return f"Audio downloaded: {filepath}"
    elif ok:
        return "Audio downloaded successfully."
    else:
        return f"Failed to download audio for {video_url}"
