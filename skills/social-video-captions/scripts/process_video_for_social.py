\
#!/usr/bin/env python3
"""Format a video for social platforms and burn subtitles generated from local audio transcription."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel


@dataclass(frozen=True)
class PlatformPreset:
    width: int
    height: int
    subtitle_margin_v: int
    subtitle_font_size: int


PLATFORMS = {
    "instagram-reel": PlatformPreset(width=1080, height=1920, subtitle_margin_v=220, subtitle_font_size=20),
    "stories": PlatformPreset(width=1080, height=1920, subtitle_margin_v=220, subtitle_font_size=20),
    "tiktok": PlatformPreset(width=1080, height=1920, subtitle_margin_v=220, subtitle_font_size=20),
    "youtube-shorts": PlatformPreset(width=1080, height=1920, subtitle_margin_v=180, subtitle_font_size=18),
    "instagram-feed": PlatformPreset(width=1080, height=1350, subtitle_margin_v=120, subtitle_font_size=18),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate local subtitles and format a video for social platforms.")
    parser.add_argument("--input-video", type=Path, required=True, help="Input video path.")
    parser.add_argument("--audio-file", type=Path, help="Optional external audio path. If omitted, extract from video.")
    parser.add_argument("--platform", choices=sorted(PLATFORMS.keys()), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--whisper-model", default="small", help="faster-whisper model size, e.g. tiny, base, small, medium.")
    parser.add_argument("--language", default="pt", help="Transcription language code, e.g. pt, en, es.")
    parser.add_argument("--font-size", type=int, help="Override subtitle font size.")
    parser.add_argument("--margin-v", type=int, help="Override subtitle bottom margin.")
    parser.add_argument("--crf", type=int, default=23)
    parser.add_argument("--preset", default="medium", help="ffmpeg x264 preset.")
    return parser.parse_args()


def require_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required binary not found in PATH: {name}")


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "Command failed.\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def extract_audio(video_path: Path, audio_path: Path) -> None:
    run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        str(audio_path),
    ])


def format_srt_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours = millis // 3_600_000
    millis %= 3_600_000
    minutes = millis // 60_000
    millis %= 60_000
    secs = millis // 1000
    millis %= 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def transcribe_to_srt(audio_path: Path, srt_path: Path, model_name: str, language: str) -> int:
    # Force CPU inference to avoid CUDA library issues in environments without GPU runtime.
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(str(audio_path), language=language, vad_filter=True)

    count = 0
    with srt_path.open("w", encoding="utf-8") as f:
        for index, segment in enumerate(segments, start=1):
            text = (segment.text or "").strip()
            if not text:
                continue
            count += 1
            f.write(f"{count}\n")
            f.write(f"{format_srt_timestamp(segment.start)} --> {format_srt_timestamp(segment.end)}\n")
            f.write(text + "\n\n")
    if count == 0:
        raise RuntimeError("No subtitle segments were generated from the audio.")
    return count


def escape_subtitle_path(path: Path) -> str:
    raw = str(path.resolve())
    return raw.replace("\\", "\\\\").replace(":", "\\:").replace("'", r"\'")


def build_filter(platform: PlatformPreset, srt_path: Path, font_size: int, margin_v: int) -> str:
    scale_pad = (
        f"scale={platform.width}:{platform.height}:force_original_aspect_ratio=decrease,"
        f"pad={platform.width}:{platform.height}:(ow-iw)/2:(oh-ih)/2"
    )
    subtitle_style = (
        f"Fontsize={font_size},"
        "PrimaryColour=&Hffffff&,"
        "OutlineColour=&H000000&,"
        "BorderStyle=1,"
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2,"
        f"MarginV={margin_v}"
    )
    subtitles = f"subtitles='{escape_subtitle_path(srt_path)}':force_style='{subtitle_style}'"
    return f"{scale_pad},{subtitles}"


def render_video(input_video: Path, output_video: Path, filter_graph: str, crf: int, preset: str) -> None:
    run([
        "ffmpeg", "-y",
        "-i", str(input_video),
        "-vf", filter_graph,
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_video),
    ])


def main() -> int:
    args = parse_args()
    require_binary("ffmpeg")

    preset = PLATFORMS[args.platform]
    font_size = args.font_size or preset.subtitle_font_size
    margin_v = args.margin_v or preset.subtitle_margin_v

    args.output_dir.mkdir(parents=True, exist_ok=True)

    work_audio = args.output_dir / "audio.wav"
    srt_path = args.output_dir / "captions.srt"
    output_video = args.output_dir / f"{args.platform}.mp4"

    if args.audio_file:
        audio_source = args.audio_file
    else:
        extract_audio(args.input_video, work_audio)
        audio_source = work_audio

    segment_count = transcribe_to_srt(
        audio_path=audio_source,
        srt_path=srt_path,
        model_name=args.whisper_model,
        language=args.language,
    )

    filter_graph = build_filter(
        platform=preset,
        srt_path=srt_path,
        font_size=font_size,
        margin_v=margin_v,
    )
    render_video(
        input_video=args.input_video,
        output_video=output_video,
        filter_graph=filter_graph,
        crf=args.crf,
        preset=args.preset,
    )

    result = {
        "ok": True,
        "platform": args.platform,
        "input_video": str(args.input_video.resolve()),
        "audio_used": str(audio_source.resolve()),
        "subtitle_file": str(srt_path.resolve()),
        "output_video": str(output_video.resolve()),
        "segments": segment_count,
        "dimensions": {
            "width": preset.width,
            "height": preset.height,
        },
    }

    # Keep JSON output for backwards-compatibility (other scripts may parse it).
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Also print a clear, human-friendly absolute path to the generated video.
    # This is useful when running the script manually.
    print(f"\n✅ Output video: {output_video.resolve()}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        error = {"ok": False, "error": str(exc)}
        print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
