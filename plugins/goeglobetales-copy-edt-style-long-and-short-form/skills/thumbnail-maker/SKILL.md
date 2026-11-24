---
name: thumbnail-maker
description: Makes high-CTR 4K YouTube thumbnails for Unexplored Truth by Amrit geopolitics documentaries using click psychology (real faces, curiosity gap, red marker circles, network lines, 2-3 word question headline, India stake as a tiranga India map). Use when the user asks for a thumbnail, "thumbnail banao", CTR, or A/B thumbnail variants.
---

# Thumbnail Maker

## Photoreal style (new in 1.0.0 - the user's favourite)

The user wants thumbnails that "dekhne mein real lagein" and look premium, like Nitish Rajput, Dhruv Rathee and
Saqlain Khan. Tools: `${CLAUDE_PLUGIN_ROOT}/engine/thumbnail/cutout.py` + `thumb_photoreal.py` (JSON config).
Worked example: `engine/examples/khilafat-india/thumbnail/` (config + the two ChatGPT images -> "ARAB RUK GAYE?").

1. Explain once: events before photography have no real photo, so "real-looking" = photoreal AI images (or a collage
   of the real coins/buildings/paintings). Ask face (own photo / photoreal AI key person / none), background
   (photoreal AI scene / real-photo collage / both) and headline (2-3 words, ends with "?", matches the title).
2. Give two ChatGPT prompts: (a) photoreal head-and-shoulders portrait, expression that fits the question (worried,
   determined), looking toward the side where the conflict is, Rembrandt light, **plain solid dark charcoal
   background**; (b) 16:9 cinematic scene with the two sides left/right and the top-left/upper-middle sky empty for
   text, golden-hour, teal-orange grade. End both with "No text, no logos, no watermark".
3. `python3 cutout.py portrait.jpg cut.png 14 900` -> check `cut_check.png` on red (raise/lower tolerance by 4).
4. Write the config: portrait side + scale + position (the AI frame crops the shoulder: `fade_edge_px` feathers that
   edge, the bottom fades into the dark floor), 2 headline lines (white + yellow `#FFD23F`), red marker `circle`
   on the thing the question is about, `arrow` from the headline to it, optional `india_map` with "?", `ai_label`.
5. Run `thumb_photoreal.py config.json`, look at the 1280 JPG and the 360 px check, adjust, deliver
   (4K JPG < 2 MB render display; master PNG + 1280 attach).
6. Replace it on YouTube only after the user approves: `vidiq_update_video_thumbnail` costs 5 vidIQ credits; the
   `thumbnail` field takes an HTTPS URL (the pushed file's raw.githubusercontent.com URL works). When credits are out,
   give the 3 YouTube Studio steps (Content -> video -> Details -> Thumbnail -> Upload file -> Save; needs a verified
   channel: Settings -> Channel -> Feature eligibility).

Code: `${CLAUDE_PLUGIN_ROOT}/engine/thumbnail/thumb.py` (skia, 3840x2160). It made the "NAYA AXIS?" thumbnail.

## Ask first (one AskUserQuestion)

- Concept: **photoreal news-documentary look (recommended since 1.0.0, see below)**, real photo + question stamp,
  flags/map with India in the middle, stickman host + map, or several for YouTube "Test & Compare".
- Whose face: the user's own photo, a photoreal AI face of the story's key person (user makes it in ChatGPT), or none.
- Headline language: Hinglish Roman (recommended), Devanagari, English.

## Psychology that the design uses

1. Real faces of the real people, from a licensed real photo: faces are the first thing the eye lands on; real beats AI.
2. Zoom-lens circles on the faces (1.3x) with a white ring and a hand-drawn red marker circle: the "investigation" look,
   and faces stay readable at phone size.
3. Red dashed network lines between the faces: a hidden-alliance feel that asks "what links them?".
4. Headline of 2-3 words ending in "?", huge (Anton), white + yellow with a black outline and shadow:
   an open loop that only the video closes. It must match the title, never contradict it.
5. Viewer stake: India's map filled with the tiranga (chakra on mainland centre) with a yellow "?" ("mere desh ka kya?").
   The user does NOT want a round India flag logo/badge.
6. Contrast: dark navy grade, faces brighter than the background, yellow/white/red accents only.
7. Max 3 ideas on screen; nothing important in the bottom-right corner (the duration stamp covers it); check at
   360 px wide (mobile feed) before delivering.

## Honesty rules

- No fake quotes, fake events, or doctored meaning; question marks for claims under debate.
- Photos only from public-domain / CC sources, credited in the description.
- Never promise a CTR number ("200%"): say the design follows tested patterns and that title, topic and audience
  decide CTR too. Offer A/B variants instead.

## Output

- `*_4K.jpg` (3840x2160, quality 95, under 2 MB: YouTube's upload limit), `*_4K_master.png` (16-bit, lossless), and
  a 1280x720 JPG. "10-bit" does not apply to images: YouTube converts thumbnails to 8-bit JPG; say so if asked.
- Send the 4K JPG with render display, the master and 1280 file as attachments.

## Shorts (vertical) - added in 0.5.0

- `engine/shorts/thumb_short.py`: 2160x3840 JPG (< 2 MB) + master PNG. Layout the user approved: 3-line Anton
  headline ("INDIA KA / SABSE BADA / NAKSHA?"), three map panels each with its waving flag/symbol and the ruler's face
  in a zoom circle beside it (red marker loop on the key one, dashed links), tiranga India map with "?" at the bottom.
- Draw the vignette before the headline so the text stays bright; fit each map fully inside its panel.
- YouTube applies custom thumbnails only on verified channels; the Shorts feed often shows a video frame instead.
