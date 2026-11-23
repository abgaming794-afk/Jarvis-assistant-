---
name: shorts-pipeline
description: Makes one complete AMRIT BORII YouTube Short (9:16, 45-75 s, 4K 2160x3840 60 fps 10-bit) A to Z - trending topic from vidIQ, sourced dossier, Hinglish script, user-recorded VO (sped up 1.2x) alignment, map animation with period-correct maps and flags, named oceans/regions lit up on their words, ruler portrait cards, real image/document cards (gods, star maps, old maps, manuscripts), smooth letter-by-letter hook, word-synced captions, original music + SFX, chunked 4K render, vertical thumbnail and vidIQ upload. Use for "shorts banao", "naya short", "BORII studio shorts", "/amrit-borii-studio:short", or to continue a Short from any stage.
---

# AMRIT BORII Shorts Pipeline (v0.9.0)

Shorts made so far:
- "India ka SABSE BADA Naksha Kab Tha?" (Nov 2026) - `engine/shorts/example-naksha/`, engine `short_storyboard.py`.
- "India, Hindustan ya Bharat - Naam Kahan Se Aaya?" (Nov 2026, https://www.youtube.com/watch?v=dQhRw51QaNk) -
  `engine/shorts/example-india-naam/`, engine `short_storyboard_v2.py`.
- "Indian Ocean Ka Naam INDIA Pe Kyun Pada?" (Nov 2026, user uploaded it himself) - `engine/shorts/example-indian-ocean/`,
  engine `short_storyboard_v3.py` (parts in `engine/shorts/v3_parts/`).
- "Solapur Mein Mila 15 Chakkar Ka Chakravyuh!" (Nov 2026, uploaded unlisted via vidIQ,
  https://www.youtube.com/watch?v=O6aBrgAkbsE) - `engine/shorts/example-bhool-bhulaiya/`, engine
  **`short_storyboard_v4.py` (use this one as the starting point; its parts are in `engine/shorts/v4_parts/`)**.

The engine is in `${CLAUDE_PLUGIN_ROOT}/engine/shorts/`. Reuse it: copy it and rewrite only the storyboard scenes for
the new script. v2 is built as three parts that are concatenated (head = data/textures, helpers, tail = camera, scenes,
`frame()`, `sfx_events()`); keep that split in the project (`_head.py`, `_helpers_block.py`, `_tail.py` ->
`cat ... > short_storyboard.py`) so edits stay small. v3 adds (on top of v2): `oceans.geojson.json` (merged Natural
Earth marine polygons ATL/PAC/ARC/SOU/IND + EUROPE outline), `eras2.geojson.json` (South Asia c. 100 CE / 1400 / 1500),
`base_map2(..., glows=, ocs=)` (ocean highlights drawn under the land), `region_hl` (land region glow), `card()`
(real image/document card with auto-fit caption + red highlight boxes on parts of the image), `typed_card`,
`strike_chip`, `note`, `gem`, `teer` (arrow down a peninsula), `poll2` (options timed to words), `pop_words`.
Helpers: `engine/voice/make_placeholder.py` (placeholder timing before the VO arrives), `engine/shorts/contact.py`
(contact sheet of stills), `engine/shorts/getwm.sh` (Wikimedia thumbnail download with retries), `thumb_short_v3.py`.
v4 adds (on top of v3, see "What v4 adds" below): `laby.geojson.json` (Maharashtra admin-1, Crete, Roman Empire c. 100 CE),
`geo_hl` (glow any GEO shape), `card(..., maxh=)`, `laby()` (flat code labyrinth), `stone_laby()` (stones in perspective
on a ground photo), `dim_line()` (measurement line), `person()` (human silhouette for scale), `stone_card_img()`
(offscreen picture used as a card), `lonlat_route` + `poly_at` (ships moving along a route), `thumb_short_v4.py`
(labyrinth + coin with red marker circle + tiranga India panel). The `still` CLI also has `times` (prints units and
scene windows).

## Ground rules (from the user)

- Short Hinglish (Roman) messages; on every update say % done and time left.
- Ask clarifying questions first with AskUserQuestion (recommended option first): topic source, voice, format. Then
  work without more questions, except: topic pick, YouTube title + privacy (always the user's call), and anything
  ambiguous the user adds mid-way (ask with AskUserQuestion, e.g. "sabhi desho ye kaam kar dena" was ambiguous).
- Default format: 4K vertical 2160x3840, 60 fps, 10-bit HEVC; also a 1080p H.264 copy for phone review.
- **VO (Shorts only)**: the user records it on ElevenLabs ("Manish - Documentary") from `script/FULL_VO_CLEAN.txt` and uploads the
  MP3. **Default: speed it up 1.2x with pitch kept** (`ffmpeg -i orig_vo.mp3 -af atempo=1.2 full_vo.mp3`; also copy to
  `vo.mp3` for `mix_short.py`). So write ~165-200 words for a ~60-70 s Short.
- Every number/name needs a source in `research/DOSSIER.md`; disputed numbers are shown as a range with "behes".
- Never present a modern or AI picture as a period portrait: label it ("Aadhunik chitran ... asli portrait nahi").
  For a portrait whose identity is uncertain say so ("'shayad Columbus' (pakka nahi)").
- Historical flags that do not exist (Maurya, Mughal, Chola, Achaemenid, Greek city-states ...) are shown as a
  symbol/banner with an on-screen note "PRATIK ... (andaazan)"; never call them the real flag.
- Neutral wording on borders and religion: no "Akhand Bharat" framing; the Raj is called colonial rule; when an old
  word overlaps a religion name (Persian "Hindu" = place), say so in the VO ("jagah ka naam tha, dharm ka nahi").
- Images the user pastes in chat now arrive as files in the session `images/` folder (e.g. `.../images/2.webp`);
  MP3/other attachments arrive under `/root/.claude/uploads/<session>/`. Look at every image before using it.
- The user may say "main khud upload karunga": then skip Stage 9 and deliver the 4K master + thumbnail + UPLOAD_PACK
  (with the chosen title) as attachments. Do not upload anything.
- If vidIQ says "Not enough credits" (check `vidiq_balance` first, it is free), stop calling paid vidIQ tools, tell the
  user (with the reset date), and offer 4 topic ideas of your own (same series style) with AskUserQuestion. If the user
  answers "new trending topics dhundo", use WebSearch (`extended`) for the current month's India history /
  archaeology news and dated observances, and offer 4 options built from real news (say there are no vidIQ numbers).
- **Uploading needs no credits**: `vidiq_social_account_list`, `vidiq_upload_image`, `vidiq_video_upload`,
  `vidiq_social_post_draft_create/publish/status` cost 0 credits for YouTube, so the upload works even at 0 balance.
  A user who first said "main khud upload karunga" may later say "upload kar do": then do Stage 9 (show the draft,
  publish only after yes).
- When the user asks for changes, ask with AskUserQuestion only the parts that are really open (e.g. what to show for
  a name that has no god or person), with a recommended option first; then build a new 1080p preview before any 4K.

## Stages

1. **Topic.** `vidiq_outliers` (contentType short, language en or omit - Hindi is not indexed for Shorts) +
   `vidiq_keyword_research` (mode rising, niche). Offer 4 options with a hook and the breakout numbers; the user picks.
2. **Dossier.** In a cloud container `curl -A "Mozilla/5.0 ..." "https://en.wikipedia.org/w/index.php?title=<Page>&action=raw"`
   works and is the fastest way to grep facts and `File:` names (sleep 2-3 s between pages). commons.wikimedia.org,
   etymonline, wiktionary, archive.org and sanskrit-lexicon (Monier-Williams) were blocked; the Wikipedia API
   (`api.php`) answers 429 quickly. Get a file's licence/author/original URL with the `web-fetch` agent on
   `en.wikipedia.org/wiki/File:<name>`. Download with `engine/shorts/getwm.sh "File name.jpg" 1280 out.jpg`:
   upload.wikimedia.org only serves **standard thumbnail widths (e.g. 500, 960, 1280, 1920, 3840)**, any other width
   gives "Error 400, Use thumbnail sizes"; a thumbnail wider than the original also fails (then fetch the original
   URL, e.g. small GIFs). Wikipedia via WebFetch works. The Wikipedia API and upload.wikimedia.org rate-limit (429): send a
   generic User-Agent, use `/thumb/.../1280px-<file>` URLs, wait 15-30 s between tries; get a file's licence with
   WebFetch on `en.wikipedia.org/wiki/File:<name>`. Historical borders: `historical-basemaps` GeoJSON from
   raw.githubusercontent.com (A. Ourednik, GPL-3.0; files world_bc500, world_bc323, world_300, world_900, world_1492,
   world_1500 ...) - credit it, say "approximate borders". Rivers: Natural Earth `ne_50m_rivers_lake_centerlines`
   from raw.githubusercontent.com/nvkelso/natural-earth-vector (linemerge the segments, order source -> mouth).
3. **Script.** One fact per line, hook question in line 1, open question + comment ask + subscribe at the end. Write
   numbers as digits; add their spoken form to `NUM` in `engine/voice/align_full.py`. Deliver `FULL_VO_CLEAN.txt` +
   `SCRIPT.md` (visual cue per line). While waiting for the VO, build the storyboard on placeholder timing
   (units from the script at ~2.5 words/s) so only the alignment remains when the MP3 arrives:
   `python make_placeholder.py` in `<project>/voice/` writes `full_units.json` + `full_sil.tsv` (~3 words/s).
   Send `FULL_VO_CLEAN.txt` early, and if the user asks "text me do", paste the VO text in a code block with the spoken
   forms of the numbers as a fallback.
4. **VO alignment.** In `<project>/voice/`: speed up 1.2x (above), `python silences.py full_vo.mp3 -35dB 0.12`
   (shorter pauses after the speed-up), `python align_full.py`, copy `full_timing.json` to `full_units.json`.
   Ratios near 1.0 = lines match. After the speed-up, re-check every reveal: a word that lands at the very end of a
   unit may be visible for < 0.5 s - keep its card/word on screen 0.6-0.9 s into the next scene (v3: the hook answer
   "INDIAN OCEAN" stays until `T("size")[0] + 0.8` and the next headline starts 0.8 s later; the "INDIAN = DESH" chip
   stays 1 s into the next scene). Print `kw()` times for the key words before checking stills.
   **`kw()` is a substring search**: "Hind" also matches "Hindi" - pass a longer key ("Hind M") or `occ=1`.
5. **Storyboard.** Edit `SCENES`, `PL` places, `CAM_KEYS`, `year_at`/`TL`, `ERA_ON`, `CFLAGS` and the overlays in
   `frame()`. Key every reveal to a word with `kw(unit, "word")` (for a single letter pass it with spaces, `" H "`).
   Check 20+ stills (`python short_storyboard.py still DIR t...`) as a contact sheet before rendering.
6. **Mix.** `python mix_short.py` (VO + original synth bed ducked to -25 dB + code-made SFX from map-shorts
   `sfxgen.py make_all('audio/sfx')`). SFX at HALF loudness: keep `g - 8`. Then
   `ffmpeg -i audio/short_mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 audio/short_mix_norm.wav`.
7. **Render.** `python render_short.py preview 4` (1080p, ~6 min) -> send -> after OK `python render_short.py 4k 4`
   (~15-20 min for 72 s on 4 CPUs; run in background). Late change: `python rerender_chunks.py 3 4`.
   **v0.9 render fix**: chunks are always 8 (edges no longer depend on the process count) and `render/tmp_*/layout.txt`
   clears stale chunks when the length changes; the script checks the output duration. (In v0.8 a re-render with 3
   processes after one with 4 mixed old and new chunks into a 62.8 s video instead of 71.8 s.) After every render,
   still pull 5-9 frames with ffmpeg (`-ss t -frames:v 1`) and check the scene order before sending anything.
   Workers fork from the parent: edits made while a render runs are NOT picked up. Never more than 4 4K encoders.
   Container setup: `pip install skia-python numpy shapely pillow`; `apt-get update && apt-get install -y libegl1 libgl1`.
8. **Thumbnail.** `thumb_short_v3.py` (tiranga-letter word + map panel + name chain + real document) or `thumb_short_v2.py` pattern -> 2160x3840 JPG under 2 MB + master PNG (see thumbnail-maker).
9. **Upload.** `vidiq_social_account_list` -> `vidiq_upload_image` (no image, PUT the JPG, call again with transferId)
   -> `vidiq_video_upload` with `localFile` (write the returned command to a file with a quoted heredoc, `bash` it,
   then call again with uploadId) -> `vidiq_social_post_draft_create` (title, description from `UPLOAD_PACK.md`,
   tags, categoryId 27, thumbnailImageId, privacy asked). **YouTube refuses `<` or `>` in the description: write
   arrows as "→", never "->".** Show the draft -> publish only after the user says yes -> `vidiq_social_post_status`
   until `postUrl`. Pinned comment: the user pins it in YouTube Studio. Default privacy the user chose: unlisted.

## Visual language the user approved (9:16, design space 1080x1920)

- Layout: headline y~230 (+ subtitle), map centre y=820, timeline y=1220, captions y~1390, era chip y~1450,
  credits y~1505-1532. Nothing important below ~1550 (Shorts UI). Logo watermark top-right.
- **Thin borders**: country borders are thin (0.75 px / scale) soft blue `#8FB3D9` at 50% (`core.draw_map`,
  `border_a` dims them to 25% in historical scenes); highlight outlines thin (glow 7, line 1.8, `#FFF1C2`);
  empire outlines `stroke=2.4`.
- **Map of ITS time in every scene (user rule)**: today's India with the waving tiranga (`NOWV`) only in present-day
  scenes (hook, "aaj", Samvidhan, ending). In the river/ancient lead-in India is solid **bhagwa** (saffron). In each
  historical scene draw the South-Asian polities of that era from historical-basemaps in bhagwa shades (`BHAGWA`,
  `ERA_PATH`, `ERA_ON`), with a chip "c. ... ka naksha (andaazan)". Sri Lanka / Nepal / Myanmar polities stay
  uncoloured. Do not reuse an empire border outside its era (e.g. no Achaemenid border at 262 CE).
- **Flags of the named countries, period-correct**: a country named in the VO gets its real flag waving inside its
  border (`CFLAGS`, `F_<iso2>` textures; Greece/Bahamas drawn in code) - but only in present-day scenes. In
  historical scenes use the era's symbol with "PRATIK (andaazan)" instead of a modern flag.
- **Every place named in the VO lights up on its word**: `highlight_country`, `ring_highlight` (regions/seas),
  `spotlight` (one city). Labels must not sit on a highlight or another label.
- **Hook**: the key word glides in letter by letter (rise + stretch + fade, back-ease), tiranga-coloured letters for
  INDIA, a light shine sweeps across it, a "?" drops in on the question word, the question/answer lines pop in word
  by word, and a small water ripple under "nadi"-type answers. All other headlines reveal word by word
  (rise + overshoot) with an underline sweep and a typed subtitle (`headline()` in v2).
- **Rivers/routes**: draw cleanly from source to end with a glowing head, dark casing under the line so it reads over
  flags; in its own scene a bright pulse travels along it on the words. Keep them clear of the hook text.
- **Word morph cards**: `word_row`/`flip` for sound changes (S->H flip, a letter crossed out and falling, letters
  added in yellow), name chains as chips with arrows.
- **Ruler cards**: on the name a big framed portrait pops (map dims), then shrinks into a badge (`ruler(..., bxy=)`)
  placed clear of the timeline pill. Start the card one word early when the VO is fast.
- **Sacred texts / documents**: when a scripture or document is named, show its real public-domain manuscript/page
  in a `manuscript_card` (warm golden halo, gold double frame, light motes, caption + credit), e.g. Rigveda MS 2097,
  Bhagavata Purana folio (LACMA). Constitution: real preamble page + Article text card with highlighter
  (`article_card`). Wikipedia passages: browser card with yellow highlighter on the spoken words.
- **Named oceans/seas light up on their word (user rule)**: every ocean named in the VO glows over its real area
  (`ocs` list in `frame()` -> `base_map2`, drawn under the land so coasts stay crisp). Use a soft blurred fill + radial
  glows from the ocean's centre (`OC_GLOW`); never a hard outline - Natural Earth marine polygons have straight
  open-sea edges and look like boxes. Clip the Indian Ocean to 20E-147E. In the hook, all named oceans light up one
  after another on "paanch". The same ocean lights up again on each of its other names (Western/Eastern/Hind...).
- **Named land regions light up too** (e.g. "Europe"): `region_hl(c, cam, "EUROPE", k, t, col)` (continent outline,
  no political borders, so it is fine in historical scenes).
- **Gods / mythic names / sky objects get a real image card (user rule)**: on the word, a `card()` with a real photo
  of an ancient statue or a real old document - e.g. Atlas = Farnese Atlas statue (crop to globe+head+chest),
  Pacific = Ortelius "Maris Pacifici" 1589, Arctic (Bear) = Urania's Mirror "Ursa Major" c. 1825 star card,
  Southern Ocean = John Cary 1806 map with the "SOUTHERN OCEAN" label boxed. Place the card on the side away from the
  ocean being lit, one card at a time, each until the next name; hide the timeline while cards are up. Box the exact
  label on the image with `hls=[(fx0, fy0, fx1, fy1, k)]` (look at the image first to get the fractions).
- **A named language/tradition gets a primary document**: e.g. "Sanskrit mein Ratnakara" -> real Sanskrit manuscript
  page (Mewar Ramayana, British Library, PD) captioned "SANSKRIT GRANTH: ..." - never claim the word is on that page
  unless verified. A dictionary/source card is shown only if its entry was actually read (Monier-Williams was not
  reachable, so it was dropped and the user was told).
- **A person with no authentic portrait** (e.g. Zheng He): show a period depiction (Wubei Zhi woodblock of his ships)
  with `ruler()` (big card -> badge) and a note "asli portrait maujood nahi".
- CC BY-SA images: put the author + licence on the card and in the description (tell the user to keep it).
- Captions: <= 4 words from the VO text, keywords in yellow, pop in on the phrase.
- Bottom timeline with year chip that slides (BCE/CE supported); hide it behind full-screen cards.
- Ending: recap chips, poll card (A/B/C options), "COMMENT KARO", subscribe button with cursor click.


## What v4 adds (learned on the bhool-bhulaiya Short, user rules)

- **Every thing named in a line lights up on its own word** (user: "jo bola gaya hai use highlight karo"). Not only
  countries: a state (`geo_hl` on Natural Earth admin-1 from map-shorts `states.geojson`, + ring burst + label), a
  landscape word ("ghaas ka maidan": green glow + swaying grass blades + label + image card), an object ("patthar ki
  bhool-bhulaiya": it grows + label + card), a place (spotlight + label). Use `kw()` per word; captions colour these
  words yellow (add them to `CAP_KEYS`).
- **A size in the VO is shown, not just said** (user: "jo size bola gaya hai use dikhao"): `dim_line()` on both axes
  with the number ("50 FOOT" / "50 FT"), plus `person()` (~5.5 ft) for scale, timed to the number word.
- **Something with no free photo is drawn so it looks real**, not as dots: e.g. the Boramani labyrinth = `stone_laby()`
  (basalt stones with shadow and highlight, near stones bigger) on a ground image, rings building on the count word;
  always with the note "Chitran (andaaza) ... asli photo nahi". Use the same picture as a hook card (`stone_card_img()`).
- **AI images from the user**: check before use. Reject (and explain in short Hinglish) an image with a wrong place name
  or sign (the first one said "सोनापुर" instead of Solapur), the wrong material (hedge maze for a stone one) or the wrong
  landscape (hills for a flat plain); then give a strict prompt plus a negative prompt (no text, signs, maze, hills,
  people, buildings ...) and ask for the file again. Use the accepted image labelled "AI chitran - asli photo nahi" and
  credit it in the description as an AI illustration. The full prompt + negative prompt that worked are in
  `engine/shorts/example-bhool-bhulaiya/ASSETS.md`; short form:
  `Photorealistic wide landscape photo of a flat, semi-arid grassland on the Deccan plateau, Maharashtra, India, in the
  dry season ... dry golden-brown grass ... scattered small dark basalt stones ... Aspect ratio 4:3.`
- **A person with no free photo** (e.g. archaeologist Sachin Patil): news photos are copyrighted - show the institution
  (Deccan College building, CC BY-SA from Wiki Loves Monuments) with the note "<name> ki free-licence photo uplabdh
  nahi", and offer to use a photo the user has permission for.
- **Hook camera close**: zoom in enough that the named state is big (India at ~19.5 px/deg); the waving tiranga fades
  out when the camera is zoomed into a state (`zk = seg(scale, 20, 40)`) so no giant chakra fills the screen; India
  stays light saffron there.
- **No overlap at scene changes**: fade the hook word out before the next headline starts (`ho` ends at b0+0.2 and the
  next headline starts 0.3 s in). A card that would be up < 1 s gets extended across the scene boundary
  (e.g. the Kalambi card runs from "Kolhapur" to the next scene's "kode").
- **Research when news sites are blocked**: archaeology.org, timesofindia, heritagedaily, greekreporter, ancient-origins,
  gktoday and labyrinthos.net did not resolve from the container. WebSearch result summaries + Wikipedia raw pages
  (`action=raw`, they often cite the news) were enough; mark such facts [WS] in the dossier and keep hedged wording
  ("andaaza", "theory", "shayad", "X ya Y (behes)").
- historical-basemaps `world_100.geojson` gives the Roman Empire c. 100 CE (credit it); keep it in historical scenes only.

## Delivery

1080p preview (render) -> 4K master + upload pack (attach) -> thumbnail -> upload. Report the YouTube link.
Files live in an ephemeral container: always send the 4K master, thumbnail and upload pack as attachments.
