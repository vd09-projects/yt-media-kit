import sys

from yt_media_kit.core.config import load_config
from yt_media_kit.core.logging import setup_logger
from yt_media_kit.youtube.client import YouTubeClient
from yt_media_kit.pipeline.runner import run_pipeline


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m yt_media_kit.cli.main <config.yaml>")
        sys.exit(1)

    cfg = load_config(sys.argv[1])
    logger = setup_logger(cfg.runtime.verbose)
    yt_client = YouTubeClient(logger, cfg.runtime.verbose)

    ok = run_pipeline(cfg, logger, yt_client)
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()