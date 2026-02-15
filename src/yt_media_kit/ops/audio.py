from yt_media_kit.youtube.client import YouTubeClient
from yt_media_kit.core.config import AudioConfig, OutputConfig


def download_audio_op(
    yt: YouTubeClient,
    video_url: str,
    audio_cfg: AudioConfig,
    out_cfg: OutputConfig,
    retries: int,
    is_short: bool = False,
) -> tuple[bool, str | None]:
    return yt.download_audio(video_url, audio_cfg, out_cfg, retries, is_short=is_short)
