"""YouTube transcript extraction using yt-dlp."""

import asyncio
import subprocess
import json
import re
from typing import Optional


async def extract_transcript(url: str) -> str:
    """
    Extract transcript from YouTube video.

    Args:
        url: YouTube video URL

    Returns:
        Video transcript as plain text
    """
    # Extract video ID from URL
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {url}")

    # Try to get transcript using yt-dlp
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: _get_transcript_yt_dlp(url)
        )
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to extract transcript: {str(e)}")


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.

    Args:
        url: YouTube URL

    Returns:
        Video ID or None
    """
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/)([^&?\s]+)',
        r'(?:youtube\.com/watch\?v=)([^&?\s]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def _get_transcript_yt_dlp(url: str) -> str:
    """
    Get transcript using yt-dlp.

    Args:
        url: YouTube video URL

    Returns:
        Transcript text
    """
    try:
        # First, try to get auto-generated subtitles
        result = subprocess.run(
            [
                "yt-dlp",
                "--skip-download",
                "--write-auto-sub",
                "--sub-lang", "en",
                "--sub-format", "vtt",
                "--output", "-",
                "--print", "%(subtitles)j",
                url
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            # Try alternative approach - get info and subtitles
            result = subprocess.run(
                [
                    "yt-dlp",
                    "--skip-download",
                    "--dump-json",
                    url
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                info = json.loads(result.stdout)

                # Check for automatic captions
                auto_captions = info.get("automatic_captions", {})
                if "en" in auto_captions:
                    # Get the VTT URL and download it
                    for fmt in auto_captions["en"]:
                        if fmt.get("ext") == "vtt":
                            vtt_url = fmt.get("url")
                            if vtt_url:
                                return _download_and_parse_vtt(vtt_url)

                # Check for manual subtitles
                subtitles = info.get("subtitles", {})
                if "en" in subtitles:
                    for fmt in subtitles["en"]:
                        if fmt.get("ext") == "vtt":
                            vtt_url = fmt.get("url")
                            if vtt_url:
                                return _download_and_parse_vtt(vtt_url)

                # If no subtitles, return description or title
                description = info.get("description", "")
                title = info.get("title", "Video")

                if description:
                    return f"Title: {title}\n\nDescription:\n{description}\n\n(No transcript available)"
                else:
                    return f"Title: {title}\n\n(No transcript available)"

        # Parse VTT output if we got it
        return _parse_vtt(result.stdout)

    except subprocess.TimeoutExpired:
        raise RuntimeError("Transcript extraction timed out")
    except Exception as e:
        raise RuntimeError(f"yt-dlp error: {str(e)}")


def _download_and_parse_vtt(vtt_url: str) -> str:
    """Download VTT file and parse it."""
    import urllib.request

    try:
        with urllib.request.urlopen(vtt_url, timeout=30) as response:
            vtt_content = response.read().decode('utf-8')
            return _parse_vtt(vtt_content)
    except Exception as e:
        raise RuntimeError(f"Failed to download VTT: {str(e)}")


def _parse_vtt(vtt_content: str) -> str:
    """
    Parse VTT subtitle content to plain text.

    Args:
        vtt_content: VTT file content

    Returns:
        Plain text transcript
    """
    lines = []
    seen_lines = set()

    for line in vtt_content.split('\n'):
        # Skip VTT headers, timestamps, and empty lines
        line = line.strip()
        if not line:
            continue
        if line.startswith('WEBVTT'):
            continue
        if line.startswith('Kind:') or line.startswith('Language:'):
            continue
        if re.match(r'^\d{2}:\d{2}', line):  # Timestamp
            continue
        if re.match(r'^\d+$', line):  # Cue number
            continue

        # Remove HTML tags
        line = re.sub(r'<[^>]+>', '', line)

        # Skip duplicates (common in auto-generated captions)
        if line in seen_lines:
            continue
        seen_lines.add(line)

        lines.append(line)

    return ' '.join(lines)
