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

## Annotations

Images can be annotated with bounding boxes directly in the gallery — no
tools to install. Open an image and simply drag to draw a box — crosshair
guide lines follow the cursor to make sizing easy. Drag an existing box to
reposition it. Click a box (or its chip in the bar below the image) to
select it, and **Delete** removes it. *Mark empty* — or just pressing
**Space** — records "reviewed, nothing in this image" and jumps straight to
the next image, so sweeping a mostly-empty folder is one keypress per
frame. Navigate with the **Prev/Next** buttons or arrow keys; neighboring
images are preloaded so stepping is instant. When zoomed in, **Shift+drag**
(or the arrow keys) pans; plain drag always draws. Boxes
are always rendered live from the annotation data as an overlay — never
baked into the images or thumbnails.

In the folder grid, tile borders show annotation status: green = has boxes,
blue = reviewed empty, dashed = browser draft not yet committed, and a
thick dashed border means your draft will overwrite an existing committed
file when merged.

Edits are saved instantly as drafts in your browser (localStorage). To get
them into the shared dataset:

1. Click **Download annotations** in the folder toolbar — you get
   `annotations.zip` whose folder structure mirrors this repository.
2. Unzip it at the repository root so each `<image>.json` lands next to its
   image.
3. Commit and push, or open a pull request.

The next deploy publishes them, and the gallery then shows them to everyone
(your own browser prefers your local draft over the repo version while a
draft exists — use *Discard draft* to go back to the committed state).

The format is one JSON file per image, named `<image>.json` next to the
image: a list of YOLO-style normalized boxes, where `x`/`y` is the box
center and all values are fractions of the image size:

    [
     {"label": "animal", "x": 0.512, "y": 0.401, "w": 0.113, "h": 0.208}
    ]

An empty list `[]` means the image was reviewed and contains no animals —
which is just as valuable as a box. There is a single class `animal` for
now; the label is stored by name, so more classes can be added later (in
`CLASSES` in `index.html`) without invalidating existing files.

To test annotations locally without committing anything: run
`python3 run_index.py --serve`, annotate in the browser (drafts live in
localStorage and survive reloads), download the zip, unzip it at the repo
root, and restart `--serve` — the index picks up the sidecar files and the
gallery now shows them as repo annotations.

## License

The contents of this repository are shared under
[Creative Commons Attribution 4.0](LICENSE.md) (CC BY 4.0) — use it, build
on it, credit the collection.
