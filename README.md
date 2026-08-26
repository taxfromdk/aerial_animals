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

Drop your capture folders into place following the convention, e.g.
`2026/Team_7/capture_1/`, commit, and push (or open a pull request if you
don't have push access — contributions are welcome). That's it: on every
push to `main`, a GitHub Actions workflow rebuilds the index, regenerates
thumbnails, and redeploys the site. No manual indexing step.

For local browsing, `run_index.py --serve` rebuilds the index automatically
on startup, so new images show up there too without extra steps.

## How publishing works

The originals total gigabytes, so the published site doesn't contain them.
The Pages workflow ([.github/workflows/pages.yml](.github/workflows/pages.yml))
builds a small static site instead:

- `run_index.py` maps every image into `index.json`
- `make_thumbs.py` renders a ~20 KB thumbnail per image (the only step with
  a dependency, Pillow, installed in CI only)
- the gallery, index, and thumbnails (a few MB in total) are deployed to Pages

On the published site, the grid shows the thumbnails; opening an image loads
the full-resolution original straight from the git repository via
`raw.githubusercontent.com`. Locally, the gallery serves your actual files
directly and thumbnails are never needed.

## License

The contents of this repository are shared under
[Creative Commons Attribution 4.0](LICENSE.md) (CC BY 4.0) — use it, build
on it, credit the collection.
