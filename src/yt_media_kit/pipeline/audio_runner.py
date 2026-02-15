import concurrent.futures

from yt_media_kit.ops.audio import download_audio_op


def run_audio_pipeline(cfg, logger, yt_client):
    success = 0
    failed = 0

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=cfg.runtime.concurrency
    ) as executor:

        futures = []

        for url in cfg.videos:
            logger.info(f"Queuing audio download: {url}")
            future = executor.submit(
                download_audio_op,
                yt_client,
                url,
                cfg.audio,
                cfg.output,
                cfg.runtime.retries,
                is_short=False,
            )
            futures.append((future, url))

        for future, url in futures:
            ok, filepath = future.result()
            if ok:
                success += 1
                logger.info(f"Audio downloaded: {filepath}")
            else:
                failed += 1
                logger.warning(f"Audio download failed: {url}")

    logger.info(f"Done | audio: success={success} failed={failed}")
    return failed == 0
