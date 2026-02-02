import os
import glob
from typing import Dict, Any, List, Tuple
import yt_dlp

from yt_media_kit.core.utils import ensure_dir
from yt_media_kit.core.config import SubtitlesConfig, OutputConfig


class YouTubeClient:
    def __init__(self, logger, verbose: bool):
        self.logger = logger
        self.verbose = verbose

    def _ydl(self, opts: Dict[str, Any]) -> yt_dlp.YoutubeDL:
        return yt_dlp.YoutubeDL(opts)

    def list_channel_videos(self, channel_url: str, flat: bool) -> List[Dict[str, Any]]:
        opts = {
            "quiet": not self.verbose,
            "skip_download": True,
            "extract_flat": "in_playlist" if flat else False,
            "dump_single_json": True,
            "forcejson": True,
            "ignoreerrors": True,
        }
        with self._ydl(opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            return [e for e in info.get("entries", []) if e]

    def download_subtitles(
        self,
        video_url: str,
        subs: SubtitlesConfig,
        out: OutputConfig,
        retries: int,
    ) -> Tuple[bool, List[str]]:
        ensure_dir(out.base_dir)

        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": subs.download_auto,
            "subtitleslangs": subs.languages,
            "subtitlesformat": subs.format,
            "outtmpl": os.path.join(out.base_dir, out.filename_template),
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
