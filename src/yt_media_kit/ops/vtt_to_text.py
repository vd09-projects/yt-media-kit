import os
import re
import webvtt  # pip install webvtt-py


def _normalize_line(s: str) -> str:
    """Clean whitespace & weird characters."""
    s = s.replace("\u200b", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _dedupe_adjacent(lines: list[str]) -> list[str]:
    """
    Remove exactly identical adjacent lines.
    """
    deduped = []
    prev = None
    for l in lines:
        if l != prev:
            deduped.append(l)
        prev = l
    return deduped


def extract_clean_lines(vtt_path: str) -> list[str]:
    """
    Returns clean text lines from a VTT, without timestamps/overlap.
    """
    raw_lines = []
    for caption in webvtt.read(vtt_path):
        text = caption.text.strip()
        if not text:
            continue
        # split multi-line captions
        for ln in text.splitlines():
            line = _normalize_line(ln)
            if line:
                raw_lines.append(line)

    # Step 1: remove exact adjacent duplicates
    return _dedupe_adjacent(raw_lines)


def merge_lines_greedily(lines: list[str]) -> str:
    """
    Merge lines into one flowing transcript, removing internal repeats.
    """
    merged = []
    seen = set()

    for line in lines:
        if not merged:
            merged.append(line)
            seen.add(line)
            continue

        # if this exact text is already in merged text ignore it
        if line in seen:
            continue

        merged.append(line)
        seen.add(line)

    # join with spaces into a continuous text
    return " ".join(merged)


def extract_text_from_vtt(vtt_path: str) -> str:
    lines = extract_clean_lines(vtt_path)
    text = merge_lines_greedily(lines)
    return text.strip()


def save_transcript_for_vtt(vtt_path: str, logger) -> str | None:
    """
    Save transcript next to the VTT with same base name:
       video.en.vtt -> video.en.txt
    """
    base, _ = os.path.splitext(vtt_path)
    txt_path = base + ".txt"

    # logger.info(f"VDJI save_transcript_for_vtt txt_path={txt_path}")
    text = extract_text_from_vtt(vtt_path)
    if not text:
        return None
    # logger.info(f"VDJI save_transcript_for_vtt text exist txt_path={txt_path}")

    os.makedirs(os.path.dirname(txt_path) or ".", exist_ok=True)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")

    return txt_path