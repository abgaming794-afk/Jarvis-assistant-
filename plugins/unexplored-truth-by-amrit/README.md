# Unexplored Truth by Amrit (v1.2.0)

Studio plugin for the AMRIT BORI YouTube channel (@itsamritbori): long-form Hinglish history and geopolitics
documentaries and YouTube Shorts, from topic to unlisted upload. Successor of `amrit-borii-studio` (0.8.0), which
can stay installed side by side.

## Commands

- `/unexplored-truth-by-amrit:long [topic]` - a new long-form documentary (16:9, 4K), stage by stage.
- `/unexplored-truth-by-amrit:short [topic]` - a new Short (9:16, 4K vertical), topic to YouTube upload.
- `/unexplored-truth-by-amrit:thumbnail [title]` - premium photoreal thumbnail (Nitish Rajput / Dhruv Rathee style).
- `/unexplored-truth-by-amrit:story-style [event/topic]` - a scene in the story-then-proof style (map -> story -> real document).
- `/unexplored-truth-by-amrit:ai-images [project]` - ChatGPT prompts for everything with no real image, then place
  the images with the "AI chitran" label.
- Plain words work too: "naya short banao", "long video banao", "thumbnail banao", "prompt do".

## Skills

- `documentary-pipeline`: the whole long video in stages - topic, research, script with a visual for every point,
  voice-over alignment, visuals, 360p review, 4K 60 fps 10-bit render in batches, thumbnail, upload pack, vidIQ upload.
- `shorts-pipeline`: the Short pipeline (vertical engine, flag maps, ruler cards, captions, mix, render, thumbnail, upload).
- `ai-image-workflow` (new): real image -> ChatGPT image -> Wikipedia card -> silhouette, prompt writing in the
  "purani painting" or photoreal style, labels, respect and no-fake-artefact rules, placing the images.
- `story-proof-style` (new in 1.1.0): "pehle animated story, phir document mein saboot" - the editing grammar from the
  reference the user sent, with code in `engine/visuals/storyproof.py`.
- `documentary-effects`: the channel look - map zooms, document highlights, timeline, arrows, chapter cards, stamps.
- `stickman-host`: the 3D toon stickman host in the studio with the AMRIT BORI logo, lip sync, gestures.
- `thumbnail-maker`: photoreal news-documentary thumbnails (new default) plus the older map / real-face styles.

## Engine

`engine/` holds working code: the "Naya AXIS" engine (skia renderer, storyboard, chunked 4K render, audio mix, VO
alignment, Wikipedia capture, three.js host, logo, subscribe animation), the Shorts engines, and since 1.0.0 the
complete Khilafat long-video example (`engine/examples/khilafat-india/`) and the photoreal thumbnail tools
(`engine/thumbnail/cutout.py`, `thumb_photoreal.py`). Start with `engine/README.md`.

## What changed in 1.2.0

- New `engine/visuals/battle2d.py`: 2D cartoon battle kit on the channel's 2D man design - 11 period factions,
  soldiers (run / attack / block / shoot / hit / fall / flee / cheer), galloping riders, war elephant with the king and
  royal umbrella, arrow volleys, dust, sparks, speed lines, photoreal blurred battlefield backgrounds with tints, and
  the `Battle` choreographer (approach, volley, clash with camera zoom + shake, melee, rout, winner None, linear marches).
- 3D map animation in `storyproof.py`: `map3d` (tilt + orbit + sky + fog, edges kept off-screen), `extrude`
  (regions rise out of the ground), `pin3d`, `fire3d`, `flat_path`, `proj`.
- Two-minute demo on the real Khilafat VO with 11 cartoon battles/sieges, 3D maps, 163 synthesised SFX and real proofs
  (`engine/examples/storyproof-demo/two-minute/`). `mix60.py` now takes the event file and output name.
- Rule: every war/event gets a cartoon animated scene; battle backgrounds photoreal; maps 3D.

## What changed in 1.1.0 (style of the reference "How Did America Become Independent")

- New skill `story-proof-style` + `references/reference-breakdown.md` (second-by-second analysis of the reference).
- New module `engine/visuals/storyproof.py`: Blue Marble satellite basemap (Mercator crop), parchment map with paper
  grain, hard style wipe, region glow, flag fill sweep, flag peel with rolled edge, world alliance colouring,
  timeline ribbon with scroll blur, googly eyes / mouth / glove hands for map mascots, prop drop and icon pop,
  stamp slam + camera shake, pin drop with label + date, neon badges, white and hand-drawn arrows, ink iris,
  whip blur, serif title and quote reveals, real-document fly-in (3D tilt, motion ghosts) and doc pan with depth
  of field + marker highlights, parchment list (strike / stamp / circle), fireworks, marching units, flag markers,
  story scene with Ken Burns + parallax, crowd silhouettes.
- Fonts (OFL): Abril Fatface (serif titles), Playfair Display (serif labels).
- Demo: `engine/examples/storyproof-demo/demo.py` (16 s, Khilafat topic, ends on the real Wikipedia line).
- `core.py` falls back to the bundled India boundary when the project has none.
- Rule: the channel keeps its own 2D man; never copy another channel's characters, footage or music.

## What changed in 1.0.0 (from "Arab Khilafat India Kyun Nahi Jeet Paayi?", Nov 2026)

- New name: "Unexplored Truth by Amrit" (plugin `unexplored-truth-by-amrit`); new commands `thumbnail`, `ai-images`.
- AI image workflow: 19-prompt example (10 portraits, 8 scenes, textbook) in the "purani painting" style; every AI
  image labelled "AI chitran · asli tasveer nahi"; portrait priority real -> AI -> Wikipedia card -> silhouette;
  never depict the Prophet / Sahaba, no AI likeness of living people, no fake coins / inscriptions / temples.
- Wikipedia text cards without the infobox (`docshot_noinfobox.js`); fallback when Wikimedia rate-limits (429).
- 360p whole-video review (~2.5 min) before every 4K run; resumable 16-chunk 4K60 10-bit render in two background
  batches + `final` (-14 LUFS, 1080p preview).
- Chapter timestamps computed from the storyboard; upload pack synced to the final export.
- Photoreal thumbnail: cut-out of a photoreal face + cinematic battle background, red marker circle and arrow,
  tiranga India map with "?", corner AI label (`cutout.py`, `thumb_photoreal.py`, JSON config).
- Direct unlisted YouTube upload of the 1.4 GB 4K master through vidIQ (`localFile`), draft -> approval -> publish ->
  status polling; thumbnail swap costs 5 vidIQ credits (Studio steps when credits are out).
- Files over 500 MiB cannot be sent in chat: preview in chat, master to YouTube.

## What changed in 0.8.0

- Short "Indian Ocean Ka Naam INDIA Pe Kyun Pada?": new engine `engine/shorts/short_storyboard_v3.py` (+ `v3_parts/`),
  worked example `engine/shorts/example-indian-ocean/`.
- Named oceans light up on their word over their real area (Natural Earth marine polygons, soft glow, no box edges);
  land regions (Europe) light up too.
- Real image/document cards for gods, sky objects, old maps and manuscripts (`card()` with auto-fit caption and boxes
  around the exact label on the image); people without an authentic portrait shown via a labelled period depiction.
- New data: `oceans.geojson.json`, `eras2.geojson.json` (South Asia c. 100 CE / 1400 / 1500).
- New helpers: placeholder VO timing, contact sheet, Wikimedia downloader (standard thumbnail widths only), thumbnail v3.
- Rules: vidIQ out of credits -> own topic ideas; user may upload himself; `kw()` substring pitfall; short VO units.

## What changed in 0.5.0

- New `shorts-pipeline` skill + `short` / `long` commands.
- `engine/shorts/`: vertical storyboard engine (waving flags inside borders, ruler portrait cards, kingdom flags,
  word-synced captions, BCE timeline, comparison bars, subscribe click), chunked 4K render + chunk re-render,
  VO+music+SFX mix (SFX at half loudness), vertical thumbnail, approximate empire/kingdom borders, worked example.
- `core.py` orientation switch (`AB_ORIENT=vertical`) and alpha clamp; `voice/silences.py`; aligner notes.
- User feedback rules: no India logo badge (tiranga map instead), symbols labelled "PRATIK", modern portraits labelled.

## What changed in 0.4.0

- Bundled render engine and thumbnail script; real-photo and real-document rules; India official boundary.
- Rules from the user's feedback: visual per point, word-synced labels, centred flags, no overlaps, text inside boxes,
  ships on sea lanes, 1.4 s chapter pause, Hinglish progress updates with time left.
- New `thumbnail-maker` skill; render-4k and upload references; one-line VO fix workflow.

## Needs (installed separately)

- Plugin `map-shorts` (Natural Earth data and flag set used by the engine).
- Python: skia-python, numpy, pillow; scipy for `engine/thumbnail/cutout.py` (`pip install scipy`).
- Connectors: vidIQ (topics, upload, thumbnail swap), ElevenLabs (optional voice). Optional: HyperFrames, ai-video-editor, Kling.
- ChatGPT (or any image model) on the user side for the AI images.
