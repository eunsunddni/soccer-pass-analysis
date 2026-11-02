"""Create a small inspection sample from a SoccerTrack v2 GSR JSON file.

Usage:
    python -m pip install ijson
    python extract_gsr_sample.py path/to/118577_1st.json

Reads the source incrementally. The sampled images and annotations are
independent previews and do not necessarily represent matching frames.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import ijson


def read_first(path: Path, prefix: str, count: int) -> list:
    with path.open("rb") as fp:
        return list(itertools.islice(ijson.items(fp, prefix, use_float=True), count))


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview a large SoccerTrack v2 GSR JSON without loading it into RAM")
    parser.add_argument("input", type=Path, help="Path to the original *_1st.json or *_2nd.json")
    parser.add_argument("--images", type=int, default=30, help="Number of image metadata entries (default: 30)")
    parser.add_argument("--annotations", type=int, default=500, help="Number of annotation records (default: 500)")
    parser.add_argument("--output", type=Path, default=None, help="Where to save the sample JSON")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Input file does not exist: {args.input}")
    if args.images < 0 or args.annotations < 0:
        parser.error("Sample sizes cannot be negative")

    output = args.output or args.input.with_name(args.input.stem + "_sample.json")
    print("Reading metadata...", flush=True)
    info = read_first(args.input, "info", 1)
    print("Reading image records...", flush=True)
    images = read_first(args.input, "images.item", args.images)
    print("Reading annotation records...", flush=True)
    annotations = read_first(args.input, "annotations.item", args.annotations)
    sample = {
        "info": info[0] if info else {},
        "images": images,
        "annotations": annotations,
        "_note": "Partial inspection sample, not a complete frame/time slice.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fp:
        json.dump(sample, fp, ensure_ascii=False, indent=2)
    print(f"Saved: {output} ({output.stat().st_size / 1024:.1f} KiB)")
    print(f"Sample records: {len(images)} images, {len(annotations)} annotations")


if __name__ == "__main__":
    main()
