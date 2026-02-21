"""
Shared runtime state — populated once in main() before any tool is called.
All tool modules import from here rather than holding their own globals.
"""
from __future__ import annotations

from typing import Any

from yt_media_kit.core.config import AppConfig
from yt_media_kit.youtube.client import YouTubeClient

# Declared without initial values; assigned in __init__.main() at startup.
cfg: AppConfig
yt_client: YouTubeClient
logger: Any
