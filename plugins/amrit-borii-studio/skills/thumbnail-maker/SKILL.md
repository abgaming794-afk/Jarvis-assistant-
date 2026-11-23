---
name: thumbnail-maker
description: Makes high-CTR 4K YouTube thumbnails for AMRIT BORII geopolitics documentaries using click psychology (real faces, curiosity gap, red marker circles, network lines, 2-3 word question headline, India stake as a tiranga India map). Use when the user asks for a thumbnail, "thumbnail banao", CTR, or A/B thumbnail variants.
---

# Thumbnail Maker

Code: `${CLAUDE_PLUGIN_ROOT}/engine/thumbnail/thumb.py` (skia, 3840x2160). It made the "NAYA AXIS?" thumbnail.

## Ask first (one AskUserQuestion)

- Concept: real photo + question stamp (recommended), flags/map with India in the middle, stickman host + map, or all
  three for YouTube "Test & Compare".
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
