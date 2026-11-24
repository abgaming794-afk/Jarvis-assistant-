---
name: documentary-pipeline
description: Runs the full Unexplored Truth by Amrit long-form documentary pipeline for Hinglish geopolitics and history videos - topic, research, script, user-recorded or ElevenLabs voice-over, 2D flat map animation, real documents and AI-image cards, stickman host, 360p review then 4K 60fps 10-bit render, photoreal thumbnail and unlisted YouTube upload. Use when the user asks to make a long video, a documentary, a full geopolitics video, "naya documentary", "long video banao", or wants to continue a documentary project from any stage.
---

# Unexplored Truth by Amrit Documentary Pipeline

Produce one long-form (8-30 minute) Hinglish geopolitics or history documentary for the YouTube channel AMRIT BORI
(@itsamritbori), under the studio name "Unexplored Truth by Amrit". Work stage by stage. After each stage, send a short Hinglish summary and wait for approval before
spending credits or hours of render time.

The engine that made "Naya AXIS" is bundled in `${CLAUDE_PLUGIN_ROOT}/engine/` (read its README first). Reuse it:
copy it into the project and write a new storyboard (`full.py`) for the new script.

## Ground rules

- All messages to the user in short Hinglish (Roman script). The user reads on a phone and often asks "kitna baki hai":
  answer with a percentage and a time estimate, never just "chal raha hai".
- The user's standing preference: ask a clarifying question (AskUserQuestion, with a recommended option) before starting
  a new task. Then work without further questions.
- Every factual claim (dates, numbers, names, distances) needs a source in `research/DOSSIER.md`. Mark disputed claims.
  Re-read every script line against the dossier: a wrong line in the user's recording costs a re-record and a re-render
  (Naya AXIS had "chaar mein se teen deshon se India ke gehre rishte" - false for North Korea).
- Geopolitics: factual and balanced; show what each side says; no invented quotes.
- Never spend ElevenLabs or video-generation credits twice for the same output.
- Default output: 3840x2160, 60 fps, 10-bit HEVC, plus a 1080p H.264 preview. The user wants 4K kept ("4k hi rehne do").

## Stages

1. **Topic and angle.** vidIQ (`vidiq_keyword_research`, `vidiq_outliers`) for trend and competitor data, else web
   search with `yt-plan` / `yt-viral`. Offer 3-5 ranked topics with a hook each. Prefer trending, unique, high-CTR angles.
2. **Research dossier.** Timeline, verified facts, disputed claims, claim-to-source table. Save `research/DOSSIER.md`.
3. **Script.** Hook in 30 s, 5 chapters with names, open loops, verdict, outro with subscribe ask. Every sentence gets a
   visual cue (see `references/visuals-and-editing.md`: the user said "tumhare script mein visual clue bohut kam hai").
   Deliver `script/FULL_VO_CLEAN.txt`: clean narration only, no tags, ready for the user to record.
   Make a 2-minute demo first when the style is new; get approval before the full video.
4. **Voice-over.** Usually the user records it on ElevenLabs and uploads the MP3. Align it (`references/voiceover.md`).
5. **Host segments.** `stickman-host` skill: intro, mid-video and outro in the studio with the channel logo on the wall.
6. **Visuals.** Follow `references/visuals-and-editing.md` and the `documentary-effects` skill. Check stills of every
   scene (contact sheet) before rendering; fix overlaps, off-centre flags, text outside boxes.
7. **Render.** `references/render-4k.md`: chunked 4K render in batches under the 2-hour task limit, audio mix, preview.
8. **Thumbnail.** `thumbnail-maker` skill.
9. **Upload pack + upload.** `references/upload.md`: titles, description with chapters (shifted by chapter pauses),
   sources and credits, tags, pinned comment; upload through vidIQ after the user picks privacy.
10. **Final check.** On-screen numbers match the script, captions match the voice, chapter timestamps match the export,
   every source is in the description. Report mismatches plainly.

## Delivery

- Send the 1080p preview first (render display), then the 4K master in parts under 500 MiB (attach display), then the
  upload pack. Say what changed in a short list.
- If something cannot be done here (blocked host, missing connector, no file upload), say so in one line and offer the
  fallback; do not stop the pipeline.

## New in 0.5.0 (use in long videos too)

- Shorts have their own skill (`shorts-pipeline`, command `/unexplored-truth-by-amrit:short`); this one is `/unexplored-truth-by-amrit:long`.
- `engine/visuals/core.py` reads `AB_ORIENT` (`vertical` = 9:16 Shorts; default landscape 16:9) and clamps alpha.
- Reusable from `engine/shorts/short_storyboard.py` (work in 16:9 too): `wave_flag` (flag or symbol waving inside an
  empire's border, `center=` to centre an emblem), `flag_tex` symbol textures (Ashoka Chakra, sher-o-khurshid banner,
  Chola tiger, Pandya fish, Chera bow), `ruler()` portrait card -> corner badge, `photo_card`, keyword-coloured
  `caption`, BCE-aware `timeline`, `cmp_bars` with ranges, `subscribe_btn`, `kw()` word timing,
  `rerender_chunks.py` for late fixes. Approx. borders: `empires.geojson.json`, `south_kingdoms.geojson.json`.
- User feedback: SFX at half loudness (-6 dB vs 0.4.0); no India logo badge - use the tiranga India map (in 0.6.0+ only in
  present-day scenes, see below);
  smaller kingdoms get waving flags, not logo badges; label symbols "PRATIK (andaazan)" and modern portraits
  "Aadhunik chitran".
- Pasted chat images do not reach the container: ask for a file attachment.

## New in 0.6.0 / 0.7.0 - the user's saved defaults (apply to long videos too)

Reference implementations are in `engine/shorts/short_storyboard_v2.py` (design space 1080x1920). They only use
`DW/DH`, the camera and `MAP_CY`, so they port to 16:9 (design 1920x1080): move the hard-coded y positions
(headline ~230, cards ~400-700, timeline 1220, captions 1390) to the landscape layout of `full.py`, and keep text in
the 16:9 safe area. Port each helper into the project's `full.py` the first time a long video needs it.

- **VO speed: 1x (normal) for long videos.** Do NOT speed it up; the 1.2x speed-up is only for Shorts.
- **Thin borders**: country borders thin soft blue (`core.draw_map`, already shared); `border_a=0.25` in historical
  scenes; thin highlight outlines (glow 7, line 1.8, `#FFF1C2`); empire outlines `stroke=2.4`.
- **Map of each scene's own time (user rule: "jis waqt jaisa map tha wohi lagao")**: today's tiranga India (`NOWV`)
  only in present-day scenes; ancient/river lead-in India solid bhagwa; historical scenes show that era's South-Asian
  polities from historical-basemaps in bhagwa shades (`eras.geojson.json`, `ERA_PATH`, `ERA_ON`, `BHAGWA`) with an
  on-screen chip "c. ... ka naksha (andaazan)". Fetch other eras from raw.githubusercontent.com/aourednik/
  historical-basemaps (world_bc500 ... world_1500 ...). Never reuse an empire border outside its era.
- **Flags of named countries, period-correct**: real waving flag inside the border on the country's word, only in
  present-day scenes (`CFLAGS`); in historical scenes the era's symbol with "PRATIK (andaazan)".
- **Text animation**: the hook's key word glides in letter by letter (rise + stretch + fade, shine sweep, "?" drop),
  question/answer lines pop word by word; every headline reveals word by word with an underline sweep and a typed
  subtitle (`headline()`, `word_row`, `flip` in v2). Chapter cards keep their own animation.
- **Rivers/routes**: draw source -> end with a glowing head and a dark casing so they read over flags; a travelling
  pulse on the words; keep them clear of on-screen text (`draw_river`).
- **Sacred texts and documents**: when a scripture or document is named, show its real public-domain manuscript/page in
  a `manuscript_card` (golden halo, gold frame, caption + credit) or `article_card` (page + highlighted text). Get files
  from upload.wikimedia.org `/thumb/.../1280px-<file>` with a generic User-Agent and 15-30 s back-off on 429; check the
  licence on `en.wikipedia.org/wiki/File:<name>`; label uncertain identities ("shayad ..., pakka nahi").
- **Neutral wording**: when an old word overlaps a religion name (Persian "Hindu" = place), say so in the VO.
- **Upload**: default privacy unlisted (still confirm); the user picks the title; YouTube refuses `<` `>` in the
  description, so write arrows as "→".
- When the user adds something ambiguous mid-way, ask with AskUserQuestion before building it.

## New in 1.0.0 - learned on "Arab Khilafat India Kyun Nahi Jeet Paayi?" (Nov 2026)

Worked example with all code: `${CLAUDE_PLUGIN_ROOT}/engine/examples/khilafat-india/` (read its README).

- **Real image for every name** (user: "jo jo real raja aur real elements ka real image nahi mila..."): follow the
  `ai-image-workflow` skill - real public-domain image -> user's ChatGPT image labelled "AI chitran · asli tasveer
  nahi" -> Wikipedia text card -> silhouette. Every place named gets highlighted with its flag/symbol on the word.
- **Respect rules**: never prompt or generate the Prophet, his family or the Sahaba (Khalifa Umar I/II included); no AI likeness of
  a living historian; no AI copies of real artefacts (coins, copper plates, inscriptions, temples).
- **Review before 4K** (user: "pehle 360p me review dijiye"): `render_review.py` with `AB_PREVIEW=360` (~2.5 min for
  10 min of video) after every batch of changes; send it with render display; the 4K run starts only after the user
  says so ("4k 60 fps 10 bit render kar do").
- **4K render**: `render_full_kh.py` - 16 chunks, 4 parallel, resumable `.done` files; batches `0 8` and `8 16` in the
  background (~1.5 h each, the task limit is 2 h), then `final` (concat, -14 LUFS loudnorm, AAC, faststart, 1080p
  preview). Verify with ffprobe (hevc, 3840x2160, yuv420p10le, 60/1) and an 8-frame contact sheet.
- **Env pitfall**: always export `AB_ROOT` (the folder holding `brand/`, `fonts/`, `render_tmp/`) and `AB_PROJECT`;
  the default AB_ROOT does not exist in a fresh checkout and `import kh` fails with FileNotFoundError.
- **Chapter timestamps**: compute from the storyboard, not by hand - chapter start = `vo_to_video(us(u)) - CH_GAP`
  (card start); other markers = `vin(unit)`. Update `UPLOAD_PACK.md` from the final export before upload.
- **Delivery size**: files over 500 MiB cannot be sent in chat. The 4K master (~1.4 GB for 11 min) goes straight to
  YouTube instead (user: "mere channel me khud upload kar do unlisted karke"): see `references/upload.md`. Send the
  1080p preview (~260 MB) in chat.
- **Thumbnail**: default to the photoreal style (`thumbnail-maker`, "Photoreal style").
- **Progress messages**: short Hinglish, always "% done, ~time left"; after each background batch finishes, start the
  next one immediately and report.

## New in 1.1.0 - story-then-proof style (default editing style)

Use the `story-proof-style` skill for every event: locate (satellite + glow + pin) -> owner (flag fill) -> when
(timeline) -> explain (parchment map, mascots, props, stamps) -> story scene (photoreal background + the channel's own
2D man) -> PROOF (real document flies in, camera pans, marker highlight). Code: `engine/visuals/storyproof.py`,
demo `engine/examples/storyproof-demo/`. Never copy another channel's characters; keep the channel's 2D man.

## New in 1.2.0 - cartoon battles + 3D maps (default)

Every war/battle/event is shown as a 2D cartoon battle (`engine/visuals/battle2d.py`) on a blurred photoreal
battlefield, and map scenes use the 3D map (`map3d`, `extrude`, `pin3d`, `fire3d` in `storyproof.py`). See the
`story-proof-style` skill and `engine/examples/storyproof-demo/two-minute/`.
