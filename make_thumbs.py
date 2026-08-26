#!/usr/bin/env python3
"""Generate small thumbnails for the published gallery.

Usage:
    python3 make_thumbs.py [output_dir]     # default: _site

Writes <output_dir>/thumbs/<folder>/<image>.jpg, aiming for ~20 KB each,
mirroring the dataset folder structure, and copies annotation sidecars
(<image>.json) into <output_dir>/<folder>/ so the published gallery can
show them. Annotated boxes are also cropped from the full-resolution
originals into <output_dir>/cutouts/<folder>/<image>.<i>.jpg for the
landing-page slideshow. Used by the GitHub Pages workflow; not needed for
local browsing (the local gallery shows the originals).

Requires Pillow (the one non-stdlib dependency, CI-only).
"""

import io
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

import run_index

TARGET_BYTES = 20 * 1024
MAX_DIM = 512
CUTOUT_DIM = 320
CUTOUT_PAD = 0.2      # margin around the box, fraction of its size


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


def make_cutouts(src: Path, boxes, dst_dir: Path, name: str) -> int:
    made = 0
    im = None
    for i, b in enumerate(boxes):
        dst = dst_dir / f"{name}.{i}.jpg"
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            continue
        if im is None:
            im = ImageOps.exif_transpose(Image.open(src))
            if im.mode != "RGB":
                im = im.convert("RGB")
        W, H = im.size
        try:
            bw, bh = b["w"] * W, b["h"] * H
            pad_x, pad_y = bw * CUTOUT_PAD, bh * CUTOUT_PAD
            left = max(0, (b["x"] - b["w"] / 2) * W - pad_x)
            top = max(0, (b["y"] - b["h"] / 2) * H - pad_y)
            right = min(W, (b["x"] + b["w"] / 2) * W + pad_x)
            bottom = min(H, (b["y"] + b["h"] / 2) * H + pad_y)
            if right - left < 2 or bottom - top < 2:
                continue
            cut = im.crop((int(left), int(top), int(right), int(bottom)))
            cut.thumbnail((CUTOUT_DIM, CUTOUT_DIM))
            dst_dir.mkdir(parents=True, exist_ok=True)
            cut.save(dst, "JPEG", quality=80, optimize=True)
            made += 1
        except (KeyError, TypeError):
            continue
    return made


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_site")
    index = run_index.scan(run_index.ROOT)
    count = 0
    total_bytes = 0
    cutouts = 0
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
            ann = src_dir / (image["name"] + ".json")
            if ann.exists():
                ann_dst = out / folder["path"] / ann.name
                ann_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ann, ann_dst)
                try:
                    boxes = json.loads(ann.read_text(encoding="utf-8"))
                except ValueError:
                    boxes = []
                if isinstance(boxes, list) and boxes:
                    cutouts += make_cutouts(
                        src, boxes, out / "cutouts" / folder["path"], image["name"])
    print(f"thumbs: {count} images, {total_bytes / 1048576:.1f} MB total -> {out / 'thumbs'}")
    print(f"cutouts: {cutouts} new animal crops -> {out / 'cutouts'}")


if __name__ == "__main__":
    main()
