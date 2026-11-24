---
name: seamless-3d-style
description: The default editing style of this plugin for long videos and Shorts - one continuous 3D camera shot (no cuts) over a 3D map, the ruler's flag blended into the land it held plus floating period flags, pop-up scene cards that rise from the place and hand over seamlessly to full-frame 2D cartoon battles (period-correct armies, a unique choreography per war, real photo of the place as background), and source documents that flip in over the map or the scene with a 3D camera move and word-by-word highlights synced to the voice-over. Use for any history/geopolitics video, "seamless", "3D map", "pop-up", "document flip", "GeoGlobeTales style", or when the user asks for battles, flags on territories or VO-synced highlights.
---

# Seamless 3D one-shot style

Built with the user on the Khilafat demo (Nov 2026), every rule below is a user correction. Worked example:
`${CLAUDE_PLUGIN_ROOT}/engine/examples/seamless-3d-demo/demo_seam.py` (2:05 on the real Khilafat VO).
Code: `engine/visuals/cam3d.py` (camera, map, flags, pop-ups, document cards), `battle2d.py` (period armies),
`battle_scenes.py` (12 battle choreographies), `engine/audio/battle_sfx.py` (code-made fallback SFX).

## Rules from the user

1. **No cuts, no black/iris transitions.** One camera path (`KF` keyframes -> `camera(t)`) runs from the first to the
   last frame. Scene changes happen through camera motion: fly -> dive to the place -> the scene card rises
   (`popup`, rise 0.75 s) -> it morphs to the exact full frame (fill 0.35 s) -> the full-frame scene takes over on the
   same pixels -> at the end it shrinks back (0.35 s) and folds into the map (0.45 s) -> the camera flies on.
   Long flights arc upward like a plane. Only the very end fades out.
2. **Real 3D map motion** (not extruded "highlight" blocks): `Cam(lon, lat, dist, pitch, yaw)` is a pinhole camera over
   the map plane; draw the parchment / satellite through `on_map()`; tilt 45-60 deg, slow yaw drift, dives to 6-9 deg
   distance at events. Satellite at the opening cross-fades into the parchment while flying.
3. **Ruler's flag blended into the territory** at that moment (`flag_region`): the land takes the flag colour
   (multiply), the whole flag sits in the middle, cloth waves move across, glowing edge, sweep reveal; plus a small
   floating flag on a pole (`float_flag`) with the ruler's name. Territories are rough extents cut from modern
   outlines with shapely (`Bx`, `_uu` in the demo) - say "andaazan" on screen or in the description. Period banners:
   Umayyad plain white, Chalukya/Pratihara varaha, Mewar sun, Turgesh wolf, Byzantine purple-gold, Frank red-yellow.
4. **Every war is a 2D cartoon battle with its own choreography and period armies** (see `battle_scenes.py`), on a
   **real photo of that place** (`place_bg`: Wikipedia lead image of the place, light blur, ground strip; credit it;
   avoid buildings newer than the event, e.g. no 15th-century Gwalior palace for 851).
5. **Documents**: capture the source with one highlight phrase per narrated word (`docshot_noinfobox.js`, `hl` list),
   flip the card in over whatever is on screen (`doc_card`, swings away from the camera), move the 3D camera to the
   line being spoken, and sweep each highlight exactly when the VO says the matching word (`doc_vo(key, t_in, t_out,
   [(phrase_index, kw(unit, word))])`). Zoom is capped so the full line width stays inside the frame (no text cut off).
   Flip out before the next beat. If an old printed source (archive.org) is blocked, use the Wikipedia passage that
   quotes it and say so.
6. **The blue 2D man was removed** from the Khilafat demo at the user's request - do not put him into story videos
   unless the user asks.
7. **Battle SFX come from the user.** Code-made battle sounds were not good enough; `demo_seam.py sfx` only keeps
   battle events whose sound file the user supplied in `sfx_user/<name>.wav|mp3` (list: `SFX_NEEDED.md`). UI sounds
   (whoosh, paper flip, stamp, pin, marker) stay code-made. SFX are ducked up to -6 dB while the VO speaks.

## Build order for a new video

VO units -> keyframes for the camera (one per beat, dive keyframes from `add_scene_kf`) -> territories + flag timings
in `map_layer` -> scenes table `SC` (scene object, lon, lat, a, b, title, date) -> documents `DOCS_ON` with word sync
-> overlays (titles, timeline, stamps) -> stills at every transition -> 360p review -> SFX list for the user ->
4K render in parallel chunks.
