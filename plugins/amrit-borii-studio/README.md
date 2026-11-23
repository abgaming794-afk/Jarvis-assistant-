# AMRIT BORII Studio (v0.9.0)

Plugin for making long-form Hinglish geopolitics and history documentaries AND YouTube Shorts for the AMRIT BORI
YouTube channel.

## Install

```
/plugin install amrit-borii-studio --marketplace abgaming794-afk/Jarvis-assistant-
```
(The marketplace lives on the branch `claude/wonderful-darwin-svdaum` until it is merged; then use
`/plugin marketplace add abgaming794-afk/Jarvis-assistant-` followed by `/plugin install amrit-borii-studio@amrit-borii`.)

## Commands

- `/amrit-borii-studio:short [topic]` - a new Short (9:16, 4K vertical), topic to YouTube upload.
- `/amrit-borii-studio:long [topic]` - a new long-form documentary (16:9, 4K), stage by stage.
- Plain words work too: "naya short banao", "long video banao".

## Skills

- `shorts-pipeline`: the Short pipeline (vertical engine, flag maps, ruler cards, captions, mix, render, thumbnail, vidIQ upload).
- `documentary-pipeline`: the whole job in stages - topic, research, script with a visual for every point, voice-over
  alignment (or one-line fixes), visuals, 4K 60 fps 10-bit render in batches, thumbnail, upload pack and vidIQ upload.
- `documentary-effects`: the channel look - Google-Maps-style zoom, real document highlights, timeline, arrows,
  chapter cards with a VO pause, stamps, counters, sound pairing.
- `stickman-host`: the fixed 3D toon stickman on a gaming chair in the studio with the AMRIT BORI logo, lip sync, gestures.
- `thumbnail-maker`: 4K high-CTR thumbnails (real faces, marker circles, network lines, question headline, India badge).

## Engine

`engine/` holds the working code from "Naya AXIS" (skia renderer, storyboard, chunked 4K render, audio mix, VO
alignment and line replacement, Wikipedia capture, three.js host, logo and subscribe animation, thumbnail script).
Start with `engine/README.md`.

## What changed in 0.9.0

- Short "Solapur Mein Mila 15 Chakkar Ka Chakravyuh!": new engine `engine/shorts/short_storyboard_v4.py` (+ `v4_parts/`),
  worked example `engine/shorts/example-bhool-bhulaiya/`, thumbnail script `thumb_short_v4.py`, data `laby.geojson.json`.
- Every thing named in a line lights up on its word (state, landscape, object), with labels and image cards.
- Sizes said in the VO are shown: measurement lines + a human silhouette for scale.
- Objects with no free photo drawn realistically in code (`stone_laby` on a ground image), always labelled as a drawing;
  rules for checking user AI images (reject wrong names/material/landscape; strict prompt + negative prompt).
- People with no free photo: institution photo + "free-licence photo uplabdh nahi".
- vidIQ at 0 credits: web-news topic route; YouTube upload tools are free, so upload still works.
- Render fix: fixed 8 chunks + stale-chunk check + duration check in `render_short.py`.
- `align_full.py` spoken numbers: 2400, 15, 11, 120.

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
- Connectors: vidIQ (topics, upload), ElevenLabs (optional voice). Optional: HyperFrames, ai-video-editor, Kling.
