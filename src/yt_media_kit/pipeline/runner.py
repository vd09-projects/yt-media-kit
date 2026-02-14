import concurrent.futures
import glob
import os
import re

from yt_media_kit.core.utils import entry_to_url, is_short
from yt_media_kit.youtube.selector import select_top_videos
from yt_media_kit.ops.subtitles import download_subtitles_op
from yt_media_kit.ops.vtt_to_text import save_transcript_for_vtt


def _find_video_dir(base_out_dir: str, video_id: str, logger) -> str | None:
    """
    Find output directory for a video using its ID.
    Matches: out/<channel>/<title> [<video_id>]/
    """
    # Avoid glob character-class semantics by scanning candidate folders ourselves
    # and looking for a literal "[<video_id>]" suffix.
    candidates = glob.glob(os.path.join(base_out_dir, "*", "*"))
    pattern = re.compile(rf"\[{re.escape(video_id)}\]$")
    matches = [c for c in candidates if pattern.search(os.path.basename(c))]
    logger.info(f"VDJI _find_video_dir candidates={len(candidates)} matches={matches}")
    return matches[0] if matches else None


def _convert_all_vtts_in_dir(video_dir: str, logger) -> None:
    """
    Convert every .vtt in the video directory to a same-name .txt.
    """
    try:
        files = os.listdir(video_dir)
    except OSError as e:
        logger.warning(f"Cannot list directory {video_dir}: {e}")
        return 

    # Case-insensitive match for ".vtt"
    vtt_files = sorted(
        [f for f in files if f.lower().endswith(".vtt")]
    )

    # logger.info(f"VDJI dir={video_dir}. files={files}")
    # logger.info(f"VDJI dir={video_dir}. vtt_files={vtt_files}")

    if not vtt_files:
        return

    for vtt_path in vtt_files:
        try:
            # logger.info(f"VDJI dir={video_dir}. vtt_path={vtt_path}")
            vtt_path = os.path.join(video_dir, vtt_path)
            save_transcript_for_vtt(vtt_path, logger)
        except Exception as e:
            logger.warning(f"Failed VTT->TXT for {vtt_path}: {e}")


def run_pipeline(cfg, logger, yt_client):
    success = 0
    failed = 0

    # We keep downloads concurrent, then do conversion per completed download.
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=cfg.runtime.concurrency
    ) as executor:

        futures: list[tuple[concurrent.futures.Future, str]] = []

        for channel in cfg.channels:
            logger.info(f"Processing channel: {channel}")

            entries = yt_client.list_channel_videos(channel, cfg.top_videos.flat_extract)
            top_videos = select_top_videos(entries, cfg.top_videos)

            for e in top_videos:
                url = entry_to_url(e)
                video_id = e.get("id") or e.get("url")  # flat extract commonly stores id in 'url'

                if not url or not video_id:
                    continue

                short = is_short(e)
                future = executor.submit(
                    download_subtitles_op,
                    yt_client,
                    url,
                    cfg.subtitles,
                    cfg.output,
                    cfg.runtime.retries,
                    is_short=short,
                )
                futures.append((future, video_id, short))

        for future, video_id, short in futures:
            ok, subtitle_paths = future.result()

            if ok:
                success += 1

                # Postprocess: VTT -> TXT (same base filename)
                if subtitle_paths:
                    for vtt_path in subtitle_paths:
                        try:
                            save_transcript_for_vtt(vtt_path, logger)
                        except Exception as e:
                            logger.warning(f"Failed VTT->TXT for {vtt_path}: {e}")
                else:
                    subdir = cfg.output.shorts_subdir if short else cfg.output.regular_subdir
                    out_dir = os.path.join(cfg.output.base_dir, subdir)
                    video_dir = _find_video_dir(out_dir, video_id, logger)
                    if video_dir:
                        _convert_all_vtts_in_dir(video_dir, logger)
                    else:
                        logger.warning(f"Could not locate output dir for video id={video_id}")

            else:
                failed += 1

    logger.info(f"Done | success={success}, failed={failed}")
    return failed == 0
