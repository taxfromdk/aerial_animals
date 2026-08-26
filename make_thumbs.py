#!/usr/bin/env python3
"""Generate small thumbnails for the published gallery.

Usage:
    python3 make_thumbs.py [output_dir]     # default: _site

Writes <output_dir>/thumbs/<folder>/<image>.jpg, aiming for ~20 KB each,
mirroring the dataset folder structure. Used by the GitHub Pages workflow;
not needed for local browsing (the local gallery shows the originals).

Requires Pillow (the one non-stdlib dependency, CI-only).
"""

import io
import sys
from pathlib import Path

from PIL import Image, ImageOps

import run_index

TARGET_BYTES = 20 * 1024
MAX_DIM = 512


def make_thumb(src: Path, dst: Path) -> int:
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.thumbnail((MAX_DIM, MAX_DIM))
    buf = io.BytesIO()
    for scale in (1.0, 0.8, 0.6):
        cur = im if scale == 1.0 else im.resize(
            (max(1, int(im.width * scale)), max(1, int(im.height * scale))))
        for quality in (75, 60, 45, 30):
            buf = io.BytesIO()
            cur.save(buf, "JPEG", quality=quality, optimize=True)
            if buf.tell() <= TARGET_BYTES:
                dst.write_bytes(buf.getvalue())
                return buf.tell()
    dst.write_bytes(buf.getvalue())
    return buf.tell()


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_site")
    index = run_index.scan(run_index.ROOT)
    count = 0
    total_bytes = 0
    for folder in index["folders"]:
        src_dir = run_index.ROOT / folder["path"]
        dst_dir = out / "thumbs" / folder["path"]
        dst_dir.mkdir(parents=True, exist_ok=True)
        for image in folder["images"]:
            src = src_dir / image["name"]
            dst = dst_dir / (image["name"] + ".jpg")
            if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                total_bytes += dst.stat().st_size
            else:
                total_bytes += make_thumb(src, dst)
            count += 1
    print(f"thumbs: {count} images, {total_bytes / 1048576:.1f} MB total -> {out / 'thumbs'}")


if __name__ == "__main__":
    main()
