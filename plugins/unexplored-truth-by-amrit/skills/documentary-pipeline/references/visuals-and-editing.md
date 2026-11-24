# Visuals and editing rules (learned from the user's feedback on Naya AXIS)

Style: 2D flat animation on a dark navy base, every point explained with its own visual. The code for all of this is in
`${CLAUDE_PLUGIN_ROOT}/engine/visuals/` (`core.py`, `widgets.py`, example storyboard `full.py`).

## One visual for every point

- Every sentence of the VO gets a visual clue: map move, icon, document, stat card, chart, arrow, flag, photo.
  Change the visual at least every 4-8 seconds. If a sentence names two sides ("ek taraf ... doosri taraf"), draw
  arrows from the speaker/centre to both sides on those exact words.
- Sync to the word, not the sentence: labels, flags and stamps appear on the keyword (`kw(unit, "word")` in full.py).
  When the user says an animation came "thoda pehle", move it to the keyword time.
- Where a document is mentioned, show the real document page; where a place is mentioned, show it on the map; where a
  number is said, show the number.

## Maps

- Open on the world map, then a continuous Google-Maps-style zoom to the place (world -> country -> city -> landmark).
  No white flash or cut between zoom steps: one camera move with eased zoom, highlight each level as it is reached
  (e.g. China -> Beijing -> Tiananmen Square).
- India's boundary always as per the Survey of India (bundled `india_official.geojson.json`); credit "Natural Earth;
  India boundary as per Survey of India".
- Ships, routes and flows follow the real lane (Hormuz ships move on the water lane, never over Iran's land).
  Keep labels small and clear of the action ("HORMUZ" was too big).
- Shipping/supply stories: show the source country map and animate the goods moving to the receiver
  (CNC machines China -> Russia, then the tank and missile factories they feed).

## Timeline

- An animated timeline at the bottom for dated events (years tick, the date chip slides in and highlights).

## Real documents

- Capture real pages with `engine/docs/docshot2.js` (Playwright, viewport 760, scale 3) - Wikipedia works from the
  cloud container; most news sites are blocked by the network policy, so ask before relying on them.
- Show the screenshot inside a browser frame (URL bar with the real URL), auto-zoom to the passage, sweep a yellow
  multiply highlighter over the key lines in time with the VO.
- News-card frames, deal papers and treaty cards contain the real page screenshot inside the same frame design.
- A paper that is only a prop ("kaagaz par kya likha hai?") gets realistic text that is blurred, not lorem ipsum.

## Real photos

- Real event photos are wanted (e.g. the 3 Sep 2025 Tiananmen photo). Use only public-domain or CC-licensed files
  (Wikimedia Commons; use 3840/1920/1280 px thumbnail URLs - full-size files get HTTP 429), credit them on screen
  and in the description, and never alter them to change their meaning.
- AI-generated images are labelled "AI illustration" and never presented as real.

## Cards, flags, layout

- Flag circles: the emblem centred (use `FLAG_FOCUS`), never a map PNG inside the circle.
- Titles never touch flags or icons: keep at least 30 px (design space) between a title and the flag/logo below or beside it.
- Text must fit its box: auto-fit the size (`stat_card` does), never let text spill out or cover a pill.
- Bar charts: flag sits left of its bar with a gap; nothing touches.
- Captions bottom-centre, titles above y=895 so they never collide with captions.

## Chapters

- Chapter card animates fully in silence: insert a 1.4 s pause in the VO at every chapter card (`CH_GAP` time remap in
  full.py; `mix_full.py` inserts the same silence). Shift every chapter timestamp in the description accordingly.

## Brand

- Channel logo on the studio wall and as a small corner watermark; subscribe animation (4K alpha overlay from
  `engine/brand/subscribe_anim.py`) in the intro host segment and the end card.

## Sound and music

- SFX on every transition and reveal (whoosh, pop, stamp, boom, riser, drag), under the voice.
- Music: original synthesized bed (no copyrighted tracks), ducked to about -27 dB under the VO, louder on chapter
  cards, host segments and end card.

## Before the full render

- Render a contact sheet of 20+ stills across the timeline and inspect it. The user checks screenshots closely:
  centring, gaps, overlaps, label size, text inside boxes, objects on the right geography.
- Missing glyphs render as a small box ("tofu"): never use emoji in `text()`; draw icons in code (`swords`, `tick`, etc.).
