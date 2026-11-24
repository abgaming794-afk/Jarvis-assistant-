# Worked example: "Arab Khilafat India Kyun Nahi Jeet Paayi?" (10:46, 4K60, Nov 2026)

The code that made the Khilafat documentary (uploaded unlisted to AMRIT BORI). Reuse it as the starting point for the
next long video: copy the files into the new project and write the new storyboard in place of `kh.py`.

## Files

| File | What it does |
|---|---|
| `visuals/engine/kh.py` | Storyboard + renderer (skia, 1920x1080 design space scaled to 4K). VO units `U()`, `us`/`ue`/`vin`, `kw(unit, word)`, `vo_to_video(t)` (chapter gaps), `@shot(t0, t1)`, `photo_card`, `real_card(..., foot=)`, `portrait()` (REAL photo -> AI_IMG -> REAL_DOC Wikipedia card -> silhouette), `doc()` Wikipedia cards, chapter cards, QUIET list for the 2D host. CLI: `still <dir> <t...>`, `timeline`, `sfx`. |
| `visuals/engine/render_review.py` | Fast whole-video review: `AB_PREVIEW=360|480|720`, 30 fps, 4 parallel chunks -> `render/REVIEW_<res>p.mp4` (360p takes ~2.5 min). |
| `visuals/engine/render_full_kh.py` | Final: 4K60 10-bit HEVC in 16 chunks, 4 in parallel, resumable (`.done`). Run `0 8`, then `8 16` (~1.5 h each, under the 2 h task limit), then `final` (concat + -14 LUFS mix + 1080p preview). |
| `visuals/engine/thumb_kh.py` | Old 2D map thumbnail ("fauj vs dhaal"). |
| `visuals/engine/thumb_kh2.py` | Photoreal thumbnail v2 (project-bound version of `engine/thumbnail/thumb_photoreal.py`). |
| `visuals/engine/make_ytpage.py` | YouTube-page flip card. |
| `visuals/docs/docshot_noinfobox.js` | Playwright capture of Wikipedia text cards without the infobox: `node docshot_noinfobox.js jobsN.json .` -> `<key>.png/.json`. `jobs11.json` is an example job list. |
| `audio/sfxgen.py`, `audio/mix_kh.py` | SFX synthesis and the VO + SFX + music mix -> `audio/full_mix.wav`. |
| `AI_IMAGE_PROMPTS.md` | The 19 ChatGPT prompts (10 portraits, 8 scenes, 1 textbook) in the "purani painting" style. |
| `PHOTO_CREDITS.txt`, `UPLOAD_PACK.md` | Credits for every real image + the AI line; the final upload pack (titles, description, chapters, tags, pinned comment). |
| `thumbnail/thumb_config.json` + `src/` | Config and the two user-made ChatGPT images for `engine/thumbnail/thumb_photoreal.py`. |

## Run order

```bash
export AB_ROOT=/path/to/amrit-borii/ AB_PROJECT=<project>      # AB_ROOT default is wrong in a new checkout: always set both
python3 kh.py still stills 30 125 215 300                      # contact-sheet check of placements
python3 kh.py timeline && python3 kh.py sfx && python3 ../../audio/mix_kh.py
AB_PREVIEW=360 python3 render_review.py                        # user review first
python3 render_full_kh.py 0 8      # background, ~1.5 h
python3 render_full_kh.py 8 16     # background, ~1.5 h
python3 render_full_kh.py final
```

Import from Python: `sys.argv=['kh']; import kh` (with AB_ROOT and AB_PROJECT set).
