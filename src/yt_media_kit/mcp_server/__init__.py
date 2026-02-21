"""
MCP server for yt-media-kit.

Startup
-------
Reads a base config.yaml (default: config/config.yaml, override via
--config <path> or the YT_MK_CONFIG env-var).  Each MCP tool can
override individual config fields through its arguments.

Run
---
    python -m yt_media_kit.mcp_server
    python -m yt_media_kit.mcp_server --config /path/to/config.yaml
    yt-mcp --config /path/to/config.yaml
"""
from __future__ import annotations

import argparse
import os

from yt_media_kit.core.config import load_config
from yt_media_kit.core.logging import setup_logger
from yt_media_kit.youtube.client import YouTubeClient

from yt_media_kit.mcp_server import context


def main() -> None:
    parser = argparse.ArgumentParser(description="yt-media-kit MCP server")
    parser.add_argument(
        "--config",
        default=os.environ.get("YT_MK_CONFIG", "config/config.yaml"),
        help="Path to base config YAML (default: config/config.yaml or $YT_MK_CONFIG)",
    )
    args, _ = parser.parse_known_args()

    context.cfg = load_config(args.config)
    context.logger = setup_logger(context.cfg.runtime.verbose)
    context.yt_client = YouTubeClient(context.logger, verbose=context.cfg.runtime.verbose)

    context.logger.info(f"yt-media-kit MCP server starting (config: {args.config})")

    # Import tools package here so tool registration happens after context is set.
    from yt_media_kit.mcp_server.tools import mcp
    mcp.run()


if __name__ == "__main__":
    main()
