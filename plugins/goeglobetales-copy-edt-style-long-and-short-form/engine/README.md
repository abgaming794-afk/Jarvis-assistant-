# Unexplored Truth by Amrit - render engine (v1.0.0)

> New in 1.0.0: `examples/khilafat-india/` (full long-video engine: storyboard `kh.py`, 360p review renderer,
> resumable 16-chunk 4K renderer, Wikipedia doc-card capture without infobox, SFX + mix, AI image prompts, upload pack)
> and `thumbnail/cutout.py` + `thumbnail/thumb_photoreal.py` (photoreal thumbnail from a JSON config).

The code that made "Naya AXIS" (9 min, 4K 60 fps 10-bit). Copy it into a new project and adapt the storyboard;
do not rewrite it from scratch.

## Layout to create for a new video

```
$AB_ROOT/                      default /home/user/amrit-borii/
  brand/      <- engine/brand/*        (logo, subscribe animation, fonts)
  fonts/      <- engine/fonts/*        (Anton, Bebas Neue for thumbnails)
  host/       <- engine/host/*         (3D stickman; run `npm i` here, then serve $AB_ROOT on :8765)
  render_tmp/                          (chunk files, created automatically)
  <project>/                           e.g. naya-axis; set AB_PROJECT=<project>
    script/  research/  voice/  audio/sfx/  render/  thumbnail/
    visuals/engine/  <- engine/visuals/*  (core, widgets, full.py storyboard, render_full, India boundary)
    visuals/docs/    <- engine/docs/docshot2.js + captured pages
    visuals/photos/                     (licensed real photos)
    audio/mix_full.py  voice/align_full.py  voice/replace_vo_line.py
```

Env vars: `AB_ROOT` (workspace), `AB_PROJECT` (project folder name), `AB_MAPDATA` (Natural Earth + flags; by default it
is found inside the installed `map-shorts` plugin: `.../map-shorts/engine/data/`).

## Setup (cloud container)

```bash
pip install skia-python numpy shapely pillow
apt-get install -y libegl1 libgl1        # skia needs libEGL
cd $AB_ROOT/host && npm i                # three@0.169
```
Playwright + Chromium are preinstalled in Claude cloud sessions (`require('playwright')`).

## Files

| File | Job |
|---|---|
| `visuals/core.py` | palette, fonts, easing, text/pill/rrect, images, Natural Earth `WorldMap` with India's official boundary swapped in, Mercator camera (`fly`, `to_screen`), grain, vignette, watermark |
| `visuals/widgets.py` | flag circles (`FLAG_FOCUS` centres the emblem), ~20 flat icons, chapter card, stat card (auto-fit text), quote card, routes, pins, bar chart, split "ek taraf / doosri taraf" |
| `visuals/full.py` | the full storyboard of Naya AXIS: `@shot(t0,t1,trans)` scenes keyed to voice units (`us/ue/vin/kw`), doc cards, Hormuz lane, captions, chapter pauses (`CH_GAP`), SFX marks. CLI: `still <dir> t...`, `chunk i0 i1 out`, `sfx` |
| `visuals/render_full.py` | 16 chunks, 4 in parallel, skips chunks with `.done`; optional range `a b` for batches; then concat + mux + 1080p preview |
| `visuals/india_official.py` + `.geojson.json` | India as per Survey of India (PoK, Gilgit-Baltistan, Aksai Chin, Shaksgam) |
| `docs/docshot2.js` | Playwright capture of a Wikipedia passage at 3x with line rectangles for the highlighter (`node docshot2.js jobs.json outdir`) |
| `voice/align_full.py` | aligns the clean script to the user's VO (silence pauses + syllable DP) -> `full_units.json` |
| `voice/replace_vo_line.py` | swaps one re-recorded line into the VO (see its docstring) |
| `audio/mix_full.py` | VO + chapter-pause silences + SFX + original synth music bed with ducking -> 48 kHz WAV |
| `host/` | three.js toon stickman, gaming chair, desk, mic, monitor, neon "AMRIT BORI" + logo sign; amplitude lip sync; gestures; frame-by-frame via Playwright + swiftshader |
| `brand/` | logo maker, 4K alpha subscribe animation |
| `thumbnail/thumb.py` | 4K thumbnail: real photo, zoom-lens faces, red marker circles, network lines, Anton headline, India "?" badge |

## Render facts that matter

- Design space 1920x1080, drawn with `canvas.scale(2)` into a 3840x2160 surface; raw RGBA piped to
  `libx265 -preset fast -crf 17 -pix_fmt yuv420p10le -tag:v hvc1`.
- Speed on a 4-CPU container: about 1 frame/s per process. 9 min at 60 fps = 32,100 frames = about 2.5 h with 4 processes.
- A background task is killed after 2 hours: render in batches (`render_full.py 0 8`, then `render_full.py`).
- A fix only needs the chunk(s) it touches: delete that chunk's `.done` (or split it in halves for speed) and re-run.
- Chunks are cut on frame boundaries and each starts with a keyframe, so `-f concat -c copy` joins them losslessly.
- SendUserFile limit is 500 MiB: split the master with `-c copy` (`-t` / `-ss` at about half).

## Shorts (9:16) - `shorts/` (v0.5.0)

Layout for a Short: copy `visuals/{core,widgets,india_official}.py` + `india_official.geojson.json` and everything in
`shorts/` into `<project>/visuals/engine/`; `export AB_ORIENT=vertical AB_PROJECT=<project>`.

| File | Job |
|---|---|
| `shorts/short_storyboard.py` | scenes keyed to VO units (`SCENES`, `kw`), camera keys, waving flag maps, ruler cards, captions, timeline, SFX list (`sfx_events`). CLI: `still DIR t...` |
| `shorts/render_short.py` | `preview` (1080p H.264) or `4k` (2160x3840 HEVC 10-bit) in 8 chunks, 4 processes, then mux with `audio/short_mix_norm.wav` |
| `shorts/rerender_chunks.py` | re-render chunks after a late fix (each split in two) and re-mux |
| `shorts/mix_short.py` | VO + original synth bed + SFX (half loudness) -> `audio/short_mix.wav` |
| `shorts/thumb_short.py` | vertical thumbnail (3 flag maps + 3 rulers + tiranga India map) |
| `shorts/empires.geojson.json`, `shorts/south_kingdoms.geojson.json` | approximate Maurya/Mughal/Raj and Chola/Pandya/Chera borders |
| `shorts/example-naksha/` | the finished example: script, dossier, credits, upload pack, thumbnail, style frames |

Speed: 71 s at 60 fps = 4,260 frames; 1080p preview ~6 min, 4K ~25 min on 4 CPUs.

### v0.6.0 additions (Short "India, Hindustan ya Bharat")

| File | Job |
|---|---|
| `shorts/short_storyboard_v2.py` | newer Short engine (start here): period maps in bhagwa shades (`ERA_ON`), period-correct flags (`CFLAGS`), letter-by-letter hook, word-by-word `headline()`, `word_row`/`flip` word morphs, river draw with casing + travelling pulse, `manuscript_card`, `article_card`, poll ending |
| `shorts/thumb_short_v2.py` | thumbnail: tiranga-letter headline, river map panel, name chain, two portrait circles |
| `shorts/eras.geojson.json` | South-Asian polities c. 500 BCE / 300 CE / 900 CE / 1492 (historical-basemaps, clipped) |
| `shorts/ancient.geojson.json`, `shorts/indus.json` | Achaemenid + Greek city-states c. 500 BCE; Indus line source -> mouth (Natural Earth) |
| `shorts/example-india-naam/` | script, dossier, upload pack, thumbnail of that Short |
| `visuals/core.py` | thin soft-blue country borders; `draw_map(..., border_a=)` to dim them in historical scenes |

### v0.8.0 additions (Short "Indian Ocean Ka Naam INDIA Pe Kyun Pada?")

| File | Job |
|---|---|
| `shorts/short_storyboard_v3.py`, `shorts/v3_parts/` | newest Short engine (start here): ocean highlights under the land (`base_map2(..., ocs=)`, `OC_GLOW`), `region_hl`, `card()` real image/document card with auto-fit caption + label boxes, `typed_card`, `strike_chip`, `note`, `gem`, `teer`, `poll2`; scenes for the Indian Ocean Short |
| `shorts/oceans.geojson.json` | ATL / PAC / ARC / SOU / IND merged from Natural Earth `ne_50m_geography_marine_polys` (IND clipped 20E-147E, ATL to 20E) + EUROPE outline |
| `shorts/eras2.geojson.json` | South-Asian polities c. 100 CE / 1400 / 1500 (historical-basemaps, clipped) |
| `shorts/thumb_short_v3.py` | thumbnail: INDIAN in tiranga letters + OCEAN, map panel with arrow, name chain, real 1597 map |
| `shorts/contact.py` | `python contact.py STILLS_DIR out.jpg 6` - labelled contact sheet of stills |
| `shorts/getwm.sh` | `getwm.sh "File name.jpg" 1280 out.jpg` - Wikimedia thumbnail (standard widths only) with back-off retries |
| `voice/make_placeholder.py` | placeholder `full_units.json` + `full_sil.tsv` from the script (~3 words/s) |
| `shorts/example-indian-ocean/` | script, dossier, upload pack (credits), thumbnail, style frames |
