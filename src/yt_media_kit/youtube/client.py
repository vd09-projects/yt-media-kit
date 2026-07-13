import os
import glob
from typing import Dict, Any, List, Tuple
import yt_dlp

from yt_media_kit.core.utils import ensure_dir
from yt_media_kit.core.config import SubtitlesConfig, AudioConfig, OutputConfig


class _YtDlpLogger:
    """Routes all yt-dlp output to stderr via the app logger (never stdout)."""

    def __init__(self, logger):
        self._log = logger

    def debug(self, msg):
        self._log.debug(msg)

    def info(self, msg):
        self._log.info(msg)

    def warning(self, msg):
        self._log.warning(msg)

    def error(self, msg):
        self._log.error(msg)


class YouTubeClient:
    def __init__(self, logger, verbose: bool):
        self.logger = logger
        self.verbose = verbose
        self._ydl_logger = _YtDlpLogger(logger)

    def _ydl(self, opts: Any) -> yt_dlp.YoutubeDL:
        # Always inject our logger so yt-dlp never writes to stdout.
        opts.setdefault("logger", self._ydl_logger)
        opts["quiet"] = True          # suppress yt-dlp's own stdout printing
        opts["no_warnings"] = not self.verbose
        return yt_dlp.YoutubeDL(opts)

    def list_channel_videos(self, channel_url: str, flat: bool) -> List[Dict[str, Any]]:
        opts = {
            "skip_download": True,
            "extract_flat": "in_playlist" if flat else False,
            "ignoreerrors": True,
        }
        with self._ydl(opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            # A dead/renamed channel makes yt-dlp return None; guard so one
            # bad channel doesn't crash the whole discovery run.
            return [e for e in (info or {}).get("entries", []) if e]

    def download_subtitles(
        self,
        video_url: str,
        subs: SubtitlesConfig,
        out: OutputConfig,
        retries: int,
        is_short: bool = False,
    ) -> Tuple[bool, List[str]]:
        subdir = out.shorts_subdir if is_short else out.regular_subdir
        out_dir = os.path.join(out.base_dir, subdir)
        ensure_dir(out_dir)

        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": subs.download_auto,
            "subtitleslangs": subs.languages,
            "subtitlesformat": subs.format,
            "outtmpl": os.path.join(out_dir, out.filename_template),
            "quiet": not self.verbose,
            "ignoreerrors": True,
        }

        if subs.prefer_manual and not subs.download_auto:
            opts["writeautomaticsub"] = False

        for attempt in range(1, retries + 1):
            try:
                with self._ydl(opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)

                subtitle_paths: List[str] = []
                requested = info.get("requested_subtitles") or {}
                for sub in requested.values():
                    path = sub.get("filepath")
                    if path:
                        subtitle_paths.append(path)

                return True, subtitle_paths
            except Exception as e:
                self.logger.warning(f"Retry {attempt}/{retries} failed: {e}")

        return False, []

    def download_audio(
        self,
        video_url: str,
        audio_cfg: AudioConfig,
        out: OutputConfig,
        retries: int,
        is_short: bool = False,
    ) -> Tuple[bool, str | None]:
        subdir = out.shorts_subdir if is_short else out.regular_subdir
        out_dir = os.path.join(out.base_dir, subdir)
        ensure_dir(out_dir)

        opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(out_dir, out.filename_template),
            "quiet": not self.verbose,
            "ignoreerrors": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_cfg.format,
                    "preferredquality": audio_cfg.quality,
                }
            ],
        }

        for attempt in range(1, retries + 1):
            try:
                with self._ydl(opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)

                # yt-dlp replaces the extension after postprocessing
                filepath = info.get("requested_downloads", [{}])[0].get("filepath")
                return True, filepath
            except Exception as e:
                self.logger.warning(f"Audio retry {attempt}/{retries} failed: {e}")

        return False, None
