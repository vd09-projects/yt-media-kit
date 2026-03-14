from dataclasses import dataclass
from typing import List, Optional
import yaml


@dataclass(frozen=True)
class TopVideosConfig:
    count: int
    sort_by: str
    min_view_count: int
    include_shorts: bool
    min_duration_seconds: int
    max_duration_seconds: Optional[int]
    flat_extract: bool
    max_age_days: Optional[int] = None  # None = no limit (all time)


@dataclass(frozen=True)
class SubtitlesConfig:
    languages: List[str]
    prefer_manual: bool
    download_auto: bool
    format: str


@dataclass(frozen=True)
class OutputConfig:
    base_dir: str
    shorts_subdir: str
    regular_subdir: str
    filename_template: str


@dataclass(frozen=True)
class AudioConfig:
    enabled: bool
    format: str
    quality: str


@dataclass(frozen=True)
class RuntimeConfig:
    concurrency: int
    retries: int
    verbose: bool


@dataclass(frozen=True)
class AppConfig:
    channels: List[str]
    top_videos: TopVideosConfig
    subtitles: SubtitlesConfig
    output: OutputConfig
    runtime: RuntimeConfig
    audio: Optional[AudioConfig] = None


@dataclass(frozen=True)
class AudioOnlyConfig:
    videos: List[str]
    audio: AudioConfig
    output: OutputConfig
    runtime: RuntimeConfig


def load_audio_config(path: str) -> AudioOnlyConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return AudioOnlyConfig(
        videos=raw["videos"],
        audio=AudioConfig(**raw["audio"]),
        output=OutputConfig(**raw["output"]),
        runtime=RuntimeConfig(**raw["runtime"]),
    )


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    audio_cfg = None
    if "audio" in raw:
        audio_cfg = AudioConfig(**raw["audio"])

    return AppConfig(
        channels=raw["channels"],
        top_videos=TopVideosConfig(**raw["top_videos"]),
        subtitles=SubtitlesConfig(**raw["subtitles"]),
        output=OutputConfig(**raw["output"]),
        runtime=RuntimeConfig(**raw["runtime"]),
        audio=audio_cfg,
    )