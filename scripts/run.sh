#!/usr/bin/env bash
set -euo pipefail
python -m yt_media_kit.cli.main "${1:-config/config.example.yaml}"