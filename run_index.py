#!/usr/bin/env python3
"""Generate index.json mapping all images in subfolders, for index.html to browse.

Usage:
    python3 run_index.py            # (re)generate index.json
    python3 run_index.py --serve    # regenerate, then serve the gallery on http://localhost:8000
    python3 run_index.py --serve 9090

CI options (used by the GitHub Pages workflow):
    --thumb-base URL    gallery loads grid previews from URL<path>.jpg thumbnails
    --source-base URL   gallery loads full-size images from URL<path>

Re-run whenever folders or images are added; the index is recomputed from
scratch on every run. Zero dependencies (Python 3 standard library only).
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "index.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".avif"}
SKIP_DIRS = {".git", ".svn", "__pycache__", "node_modules", "_site"}


def natural_key(name: str):
    """Sort img_2 before img_10."""
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", name)]


def scan(root: Path) -> dict:
    folders = []
    total_images = 0

    dirs = [root]
    while dirs:
        current = dirs.pop()
        images = []
        for entry in sorted(current.iterdir(), key=lambda p: natural_key(p.name)):
            if entry.is_dir():
                if entry.name not in SKIP_DIRS and not entry.name.startswith("."):
                    dirs.append(entry)
            elif entry.suffix.lower() in IMAGE_EXTENSIONS:
                images.append({
                    "name": entry.name,
                    "size": entry.stat().st_size,
                })
        # root-level images (banner, site assets) are not part of the dataset
        if images and current != root:
            folders.append({
                "path": current.relative_to(root).as_posix(),
                "count": len(images),
                "images": images,
            })
            total_images += len(images)

    folders.sort(key=lambda f: natural_key(f["path"]))
    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_images": total_images,
        "total_folders": len(folders),
        "folders": folders,
    }


def get_flag(name: str):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def main():
    index = scan(ROOT)
    for key, flag in (("thumb_base", "--thumb-base"), ("source_base", "--source-base")):
        value = get_flag(flag)
        if value:
            index[key] = value
    INDEX_FILE.write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    print(f"index.json: {index['total_images']} images in {index['total_folders']} folders")

    if "--serve" in sys.argv:
        import http.server

        port = next((int(a) for a in sys.argv[1:] if a.isdigit()), 8000)

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **kw):
                super().__init__(*a, directory=str(ROOT), **kw)

            def log_message(self, *a):
                pass

        with http.server.ThreadingHTTPServer(("", port), Handler) as server:
            print(f"Serving gallery at http://localhost:{port}/  (Ctrl-C to stop)")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
