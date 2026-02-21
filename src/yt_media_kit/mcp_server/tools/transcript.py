"""
Transcript tools — convert local VTT files to plain text.
"""
from __future__ import annotations

import os

from yt_media_kit.mcp_server import context
from yt_media_kit.ops.vtt_to_text import extract_text_from_vtt, save_transcript_for_vtt

from . import mcp


@mcp.tool()
def vtt_to_text(vtt_path: str) -> str:
    """
    Convert a VTT subtitle file that exists on the server's local filesystem
    into a clean, deduplicated plain-text transcript.

    Use this tool whenever the user wants to read, convert, or extract text
    from a .vtt file. Do NOT attempt to read the file yourself — this tool
    handles parsing, deduplication, and saving the .txt output alongside the
    original .vtt. Returns the full transcript text so you can show it inline.

    Args:
        vtt_path: Absolute path to the .vtt file on the local filesystem.
    """
    if not os.path.isfile(vtt_path):
        return f"File not found: {vtt_path}"

    txt_path = save_transcript_for_vtt(vtt_path, context.logger)
    if txt_path:
        text = extract_text_from_vtt(vtt_path)
        preview = text[:500] + ("…" if len(text) > 500 else "")
        return f"Transcript saved to {txt_path}\n\n{preview}"
    return "VTT file was empty or could not be parsed."
