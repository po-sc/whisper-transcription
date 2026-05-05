#!/usr/bin/env python3
"""
Transcribe video/audio files to text using OpenAI Whisper.
Supports .mov, .mp4, .mp3, .wav, .m4a, .aiff and other formats.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MODELS = {
    "tiny":             ("75 MB",   "fastest, low accuracy"),
    "base":             ("145 MB",  "fast, basic accuracy"),
    "small":            ("465 MB",  "good balance for short clips"),
    "medium":           ("1.5 GB",  "solid accuracy"),
    "turbo":            ("809 MB",  "large-v3-turbo: ~8x faster than large, near-identical accuracy ← recommended"),
    "large-v2":         ("3 GB",    "previous best model"),
    "large-v3":         ("3 GB",    "highest accuracy, slowest"),
}

VIDEO_EXTS = {".mov", ".mp4", ".avi", ".mkv", ".webm", ".m4v", ".m4a"}


def extract_audio(input_path: Path, tmp_dir: str) -> Path:
    wav_path = Path(tmp_dir) / (input_path.stem + ".wav")
    result = subprocess.run(
        ["ffmpeg", "-i", str(input_path), "-vn",
         "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
         str(wav_path), "-y", "-loglevel", "error"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ffmpeg error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return wav_path


def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def write_srt(segments, output_path: Path):
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        lines.append(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_vtt(segments, output_path: Path):
    lines = ["WEBVTT\n"]
    for seg in segments:
        start = format_timestamp(seg["start"]).replace(",", ".")
        end = format_timestamp(seg["end"]).replace(",", ".")
        lines.append(f"{start} --> {end}\n{seg['text'].strip()}\n")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_txt_with_timestamps(segments, output_path: Path):
    lines = []
    for seg in segments:
        h = int(seg["start"] // 3600)
        m = int((seg["start"] % 3600) // 60)
        s = int(seg["start"] % 60)
        ts = f"[{h:02d}:{m:02d}:{s:02d}]"
        lines.append(f"{ts} {seg['text'].strip()}")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def transcribe_file(input_path: Path, model, language: str, fmt: str, timestamps: bool):
    needs_extraction = input_path.suffix.lower() in VIDEO_EXTS

    if needs_extraction:
        print(f"  Extracting audio from {input_path.name}...")
        with tempfile.TemporaryDirectory() as tmp:
            audio = extract_audio(input_path, tmp)
            print(f"  Transcribing...")
            result = model.transcribe(str(audio), language=language)
    else:
        print(f"  Transcribing {input_path.name}...")
        result = model.transcribe(str(input_path), language=language)

    return result


def save_output(result, input_path: Path, fmt: str, output_path, timestamps: bool):
    ext = {"txt": ".txt", "srt": ".srt", "vtt": ".vtt", "json": ".json"}.get(fmt, ".txt")

    if output_path is None:
        output_path = input_path.with_suffix(ext)

    segments = result.get("segments", [])

    if fmt == "srt":
        write_srt(segments, output_path)
    elif fmt == "vtt":
        write_vtt(segments, output_path)
    elif fmt == "json":
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    elif timestamps and segments:
        write_txt_with_timestamps(segments, output_path)
    else:
        output_path.write_text(result["text"].strip(), encoding="utf-8")

    return output_path


def list_models():
    print("Available models:\n")
    for name, (size, desc) in MODELS.items():
        print(f"  {name:<18} {size:<10}  {desc}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe video/audio to text via OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python transcribe.py video.mov\n"
               "  python transcribe.py *.mp3 --model large-v3\n"
               "  python transcribe.py interview.mov --format srt --language en\n"
               "  python transcribe.py audio.mp3 --timestamps --print\n"
    )
    parser.add_argument("inputs", nargs="*", help="Input file(s)")
    parser.add_argument("-m", "--model", default="turbo",
                        choices=list(MODELS.keys()),
                        help="Whisper model (default: turbo)")
    parser.add_argument("-l", "--language", default="ru",
                        help="Language code: ru, en, de, fr, ... (default: ru)")
    parser.add_argument("-f", "--format", default="txt",
                        choices=["txt", "srt", "vtt", "json"],
                        dest="fmt",
                        help="Output format (default: txt)")
    parser.add_argument("-o", "--output", default=None,
                        help="Output file (only for single input)")
    parser.add_argument("-t", "--timestamps", action="store_true",
                        help="Include timestamps in txt output")
    parser.add_argument("--print", action="store_true", dest="print_text",
                        help="Print transcript to stdout after saving")
    parser.add_argument("--list-models", action="store_true",
                        help="Show available models with size and speed info")

    args = parser.parse_args()

    if args.list_models:
        list_models()
        return

    if not args.inputs:
        parser.print_help()
        return

    try:
        import whisper
    except ImportError:
        print("whisper not installed. Run: pip install openai-whisper", file=sys.stderr)
        sys.exit(1)

    files = [Path(p) for p in args.inputs]
    missing = [f for f in files if not f.exists()]
    if missing:
        for f in missing:
            print(f"File not found: {f}", file=sys.stderr)
        sys.exit(1)

    if args.output and len(files) > 1:
        print("--output can only be used with a single input file", file=sys.stderr)
        sys.exit(1)

    print(f"Loading model '{args.model}'...")
    model = whisper.load_model(args.model)

    for i, input_path in enumerate(files):
        if len(files) > 1:
            print(f"\n[{i+1}/{len(files)}] {input_path.name}")

        result = transcribe_file(input_path, model, args.language, args.fmt, args.timestamps)
        output_path = Path(args.output) if args.output else None
        out = save_output(result, input_path, args.fmt, output_path, args.timestamps)

        print(f"  Saved → {out}")

        if args.print_text:
            print(f"\n--- {input_path.name} ---")
            print(result["text"].strip())


if __name__ == "__main__":
    main()
