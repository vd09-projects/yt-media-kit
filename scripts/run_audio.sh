#!/usr/bin/env bash
set -euo pipefail
python -m yt_media_kit.cli.audio "${1:-config/audio.yaml}"
