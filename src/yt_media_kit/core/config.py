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


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return AppConfig(
        channels=raw["channels"],
        top_videos=TopVideosConfig(**raw["top_videos"]),
        subtitles=SubtitlesConfig(**raw["subtitles"]),
        output=OutputConfig(**raw["output"]),
        runtime=RuntimeConfig(**raw["runtime"]),
    )