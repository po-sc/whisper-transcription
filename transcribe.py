#!/usr/bin/env python3
"""
Transcribe video/audio files to text using OpenAI Whisper.
Supports .mov, .mp4, .mp3, .wav, .m4a and other formats.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def convert_to_wav(input_path: Path, tmp_dir: str) -> Path:
    wav_path = Path(tmp_dir) / (input_path.stem + ".wav")
    result = subprocess.run(
        ["ffmpeg", "-i", str(input_path), "-vn", "-acodec", "pcm_s16le",
         "-ar", "16000", "-ac", "1", str(wav_path), "-y"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ffmpeg error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return wav_path


def transcribe(input_path: Path, model: str, language: str, output_path: Path | None):
    try:
        import whisper
    except ImportError:
        print("whisper not installed. Run: pip install openai-whisper", file=sys.stderr)
        sys.exit(1)

    video_exts = {".mov", ".mp4", ".avi", ".mkv", ".webm", ".m4v"}
    needs_conversion = input_path.suffix.lower() in video_exts

    print(f"Loading model '{model}'...")
    m = whisper.load_model(model)

    if needs_conversion:
        print("Extracting audio with ffmpeg...")
        with tempfile.TemporaryDirectory() as tmp:
            audio = convert_to_wav(input_path, tmp)
            print("Transcribing...")
            result = m.transcribe(str(audio), language=language)
    else:
        print("Transcribing...")
        result = m.transcribe(str(input_path), language=language)

    text = result["text"].strip()

    if output_path is None:
        output_path = input_path.with_suffix(".txt")

    output_path.write_text(text, encoding="utf-8")
    print(f"Saved → {output_path}")
    return text


def main():
    parser = argparse.ArgumentParser(description="Transcribe video/audio to text via Whisper")
    parser.add_argument("input", help="Input file (.mov, .mp4, .mp3, .wav, etc.)")
    parser.add_argument("-m", "--model", default="large",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model (default: large)")
    parser.add_argument("-l", "--language", default="ru",
                        help="Language code (default: ru). Use 'en', 'de', etc.")
    parser.add_argument("-o", "--output", default=None,
                        help="Output .txt file (default: same name as input)")
    parser.add_argument("--print", action="store_true", dest="print_text",
                        help="Also print transcript to stdout")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else None
    text = transcribe(input_path, args.model, args.language, output_path)

    if args.print_text:
        print("\n--- Transcript ---")
        print(text)


if __name__ == "__main__":
    main()
