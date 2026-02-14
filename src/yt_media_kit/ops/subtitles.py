from yt_media_kit.youtube.client import YouTubeClient
from yt_media_kit.core.config import SubtitlesConfig, OutputConfig


def download_subtitles_op(
    yt: YouTubeClient,
    video_url: str,
    subs_cfg: SubtitlesConfig,
    out_cfg: OutputConfig,
    retries: int,
    is_short: bool = False,
) -> tuple[bool, list[str]]:
    return yt.download_subtitles(video_url, subs_cfg, out_cfg, retries, is_short=is_short)
