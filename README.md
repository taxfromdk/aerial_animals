# Aerial Animals

A shared, growing collection of aerial images of animals, captured by student
teams across years. The goal is to pool what each team collects so that future
teams can get a feel for what this kind of data actually looks like — lighting,
altitude, motion blur, how small the animals really are — and use that to build
more interesting detectors, instead of starting from zero every year.

Browse the collection here: **https://taxfromdk.github.io/aerial_animals/**

## How the data is organized

Images live in plain folders, one level per concept:

```
<year>/<team>/<capture session>/<images>
e.g.  2026/Team_5/capture_16/img_2.jpg
```

Nothing about the layout is enforced beyond "images in subfolders" — the
indexer picks up whatever structure is there. Keeping to the
year/team/capture convention is what makes the collection navigable, though.

## Browsing the gallery

The repo is its own viewer. `index.html` is a static gallery that reads
`index.json` (a machine-generated map of every image) and displays the actual
image files — no copies, no generated thumbnails.

To browse locally:

```
python3 run_index.py --serve        # builds index.json, serves on :8000
python3 run_index.py --serve 9090   # ... or another port
```

The gallery is deliberately gentle on the server: image tiles start as
placeholders and only load when you hover them (or press *Load previews on
this page*), at most a few requests at a time. Click a tile for a full-size
viewer with zoom, pan, and keyboard navigation.

## Adding new images

1. Drop your capture folders into place, e.g. `2026/Team_7/capture_1/`.
2. Rebuild the index: `python3 run_index.py`
   (zero dependencies — any Python 3 will do)
3. Commit the new folders **and** the updated `index.json`.

The index is recomputed from scratch each run, so renames and deletions are
picked up too.

## Hosting on GitHub Pages

Everything is static, so Pages can serve the whole thing: enable Pages for
the repository (deploy from the `main` branch, root folder) and the gallery
is live at the Pages URL. Just remember that `index.json` must be rebuilt and
committed whenever images change — Pages serves whatever is in the repo.

## Roadmap

- **Annotation tool** — the next step is a lightweight annotation tool in the
  same zero-dependency spirit, so images can be labeled (species, bounding
  boxes) and the collection can evolve from "example imagery" into a real,
  usable detection dataset.

## License

The contents of this repository are shared under
[Creative Commons Attribution 4.0](LICENSE.md) (CC BY 4.0) — use it, build
on it, credit the collection.
