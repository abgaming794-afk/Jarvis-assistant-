---
name: ai-image-workflow
description: Fills every gap where no real image exists (historical rulers, generals, historians, battles, scenes, textbooks) for Unexplored Truth by Amrit videos - checks real public-domain images and Wikipedia cards first, writes ChatGPT image prompts in the channel's "purani painting" or photoreal style, places the images the user sends back with the mandatory "AI chitran" label, and keeps the religious-respect and no-fake-artefact rules. Use when the user says "real image nahi mila", "prompt do", "ChatGPT se bana lunga", sends generated images to place in a video, or asks for portraits of people with no authentic picture.
---

# AI Image Workflow (Khilafat, Nov 2026)

The user generates images in ChatGPT himself; Claude writes the prompts, then places the results. Worked example:
`${CLAUDE_PLUGIN_ROOT}/engine/examples/khilafat-india/` (`AI_IMAGE_PROMPTS.md`, `kh.py` `AI_IMG` / `portrait()`).

## 1. Real first, AI last

For every named person, place, object or document, in this order:
1. **Real image** (public domain / CC from Wikimedia Commons): coins, inscriptions, buildings, manuscripts, period
   paintings. Credit each one in `visuals/photos/PHOTO_CREDITS.txt` and in the description.
2. **AI image** the user made (below), labelled.
3. **Wikipedia text card** (`docshot_noinfobox.js`, `REAL_DOC` map): the article's own lines, highlighted.
4. **Silhouette** with the name.

`portrait()` in `kh.py` implements exactly this priority (`REAL` -> `AI_IMG` -> `REAL_DOC` -> silhouette).
Wikimedia often answers 429 / robot-policy: back off 15-30 s, use standard thumbnail widths, and do NOT restart a
downloader that already ran 2 hours; switch to doc cards or AI prompts instead.

## 2. Ask first (one AskUserQuestion)

- Style: **"Purani painting (Recommended)"** (Mughal/Persian miniature or oil painting look, matches the 2D map
  video), "Photoreal" (thumbnails, cinematic scenes), "Mixed".
- What to do with a running render (stop it, or let it finish and re-render the changed chunks).

## 3. Writing the prompts (`AI_IMAGE_PROMPTS.md`)

- One numbered prompt per missing item, grouped: portraits, scenes, special (textbook, letters...). Give the file key
  next to each (`mbq_ai`, `army_destruction_ai`...) so placement is mechanical.
- Portrait prompt: era + region + role + age, period-correct clothes/armour/headgear, expression that fits the beat,
  head-and-shoulders, **plain solid dark background** (easy cut-out), 4:5 portrait. Scene prompt: 16:9, what is on the
  left/right, light, time of day, "keep the top-left empty for text" when it is a thumbnail background.
- Always end with: "No text, no logos, no watermark, no modern objects."
- Period facts: the Umayyad banner was plain WHITE; Rajput/Pratihara armies with round shields and spears; no saffron
  "Hindu flag" in 8th-century scenes unless sourced.

## 4. Hard rules (never break)

- **Never write prompts for or generate** the Prophet, his family or the Sahaba (including Khalifa Umar I and II),
  not even as a silhouette face: use text, title cards, maps or real buildings (Masjid-e-Nabawi, Green Dome) instead.
  Only if the user supplies his own symbolic image (face hidden by light, as in the Khilafat video) place it with
  the caption "AI CHITRAN · PRATIK (asli tasveer nahi)" next to a real photo of the place; never make one yourself.
- **No AI likeness of a living person** (e.g. historian Khalid Blankinship): use his book cover or a name card.
- **No fake artefacts**: never AI-generate coins, inscriptions, copper plates, manuscripts or temples that exist in
  reality (Navsari plate, Kailasa): show the real one or a doc card.
- **Every AI image carries the label** `AI chitran · asli tasveer nahi` (card caption) and footnote
  `AI se bani tasveer (kalpanik)`; thumbnails carry a small corner label. List every AI file in `PHOTO_CREDITS.txt`
  and the description's AI line; tick "Altered or synthetic content" in YouTube Studio.

## 5. Placing what the user sends

- Pasted chat images arrive under the session's `images/` folder (webp): convert to JPG/PNG into
  `visuals/photos/<key>.jpg`. Portraits come ~1122x1402, scenes ~1672x941.
- Portraits: add to `AI_IMG = {"NAME": "key"}`; `real_card()` draws them with `AI_CAP` / `AI_FOOT`.
- Scenes: `photo_card(c, key, x, y, w, h, t, k, cap, credit, t0, kout)` timed with `kw(unit, word)` / `us()` so the
  card appears on the spoken word and fades before the next beat; keep the fallback (old 2D drawing) when the file
  is missing.
- Check overlaps in a still contact sheet (`kh.py still`), then a 360p review (`render_review.py`) before any 4K run.
  Typical fixes from Khilafat: shrink a doc card that hides another card, move a portrait (Ghori to x=900), remove a
  QUIET host entry that collides with a big card, keep stamps small (size 26).
- Re-render only the chunks whose time range changed when the 4K chunks already exist.
