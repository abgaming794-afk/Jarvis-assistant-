# Channel rules (always follow)

## 1. India map = full official map (MANDATORY)
Whenever India appears on any map, image, thumbnail or icon, show the **full official map of India**:
all of Jammu & Kashmir (including PoK / Gilgit-Baltistan and the Shaksgam tract), Ladakh including
Aksai Chin, and Arunachal Pradesh — as on Survey of India maps. Never show the cut "de-facto" outline.

- The engine enforces this automatically: `engine/data/india_full.geojson` is drawn on top of every map
  (`scenes.draw_india`, used by both map styles), whether or not India is highlighted.
- Ready-made transparent PNG: `assets/maps/india_full.png` (use it for stickers, thumbnails, overlays).
- When asking an AI image tool for a picture with an India map, always add: "full official map of India
  including all of Jammu and Kashmir, Ladakh with Aksai Chin, and Arunachal Pradesh".
- Do not use a map image from the web unless it shows the full official outline.
- Never crop the outline: a map `view` that shows India must reach at least 39°N (the J&K crown is at ~37°N) and use
  `cam: drift` (not dolly_in) so the camera push never cuts the top off. Check the last frame in the preview.

## 2. Facts
Every number, date and claim is checked against sources (research/FACTS.md). Dramatised dialogue is
allowed, but never invent quotes for real people presented as real quotes.

## 3. Style source
Copy the editing STYLE of the reference documentary-toon channel, never its characters, brand, script
or artwork.
