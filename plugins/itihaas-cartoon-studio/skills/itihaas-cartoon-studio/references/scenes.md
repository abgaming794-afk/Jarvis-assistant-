# story.json — complete reference

One file describes the whole video. A **beat** = one line of voice = one shot (aim 2.5–5 s).
Full working example: `examples/eic-founding.json`.

```json
{
  "title": "East India Company Kaise Bani?",
  "style": "toon",                    // toon (default) | bighead (old waist-up style)
  "res": "1080",                       // 360 | 480 | 720 | 1080 (preview: 360, phone/Termux: 720)
  "music": "investigate",              // investigate | mystery | epic | sad | tension | none | path/to/own.mp3
  "music_volume": 0.11, "sfx_volume": 0.2, "pause": 0.12,
  "auto_transitions": true,            // gives every beat a seamless transition unless it sets one
  "voice": {"engine": "edge", "voice": "hi-IN-MadhurNeural", "rate": "+6%", "pitch": "-6Hz"},
  "speakers": {"N": {}, "V1": {"pitch": "-16Hz"}, "Q": {"voice": "hi-IN-SwaraNeural"}},
  "cast": {"queen": {"preset": "queen_elizabeth"}, "clive": {"preset": "british_officer"}},
  "description": "...", "tags": ["..."], "pinned_comment": "...",
  "sources": [{"t": "Book / article", "url": "https://..."}],
  "beats": [ { "id": "s01", "speaker": "N", "text": "हिंदी narration…", "chapter": "London, 1599",
               "transition": "whip_right", "into": [0.5, 0.6], "sfx": ["boom"], "scene": { ... } } ]
}
```

## Beat keys
| key | meaning |
|---|---|
| `id` | unique, `s01`… (also the file name for own/ElevenLabs recordings: `audio/own/s01.mp3`) |
| `speaker` | key into `speakers` (N = narrator; characters V1, V2, Q …). Dialogue beats should set `"talk": true` on that character |
| `text` | what is spoken (Devanagari Hindi; numbers/years in words: "सत्रह सौ सत्तावन") |
| `chapter` | starts a YouTube chapter |
| `transition` | cut, whip_left, whip_right, whip_up, zoom_through, push_left, push_right, flash, fade, blur, iris, glitch |
| `into` | [x, y] point the zoom_through/iris travels into |
| `sfx` | extra sounds: whoosh, swoosh, pop, cash, ding, boom, drum, tension, riser, stamp, type, page, click, crowd |

## Scene types (`scene.type`)
### `set` (default) — a lit vector room with full-body characters
`bg`: study_night, office_day, hallway, company_hall, mughal_court, palace_room, london_street, bazaar, port, sea,
battlefield, war_tent, village, fort, prison, parliament, senate, desk_top, corkboard, map_room, black.
`cam`: auto, dolly_in, dolly_out, truck_left, truck_right, crane_up, crane_down, orbit_left, orbit_right, push_fast,
drift, punch, shake, static. `zoom` (1.0–1.6) + `focus` [x,y] = medium/close framing of the same set.

**chars** (list): `who` (cast key or preset), `x`, `h` (height, fraction of frame; 0.46 standing, 0.6 seated close),
`y` (shift down), `expr` (neutral happy laugh proud smug scheming thinking angry shout shocked sad worried),
`pose` (idle point up wave cheer chin think hold give shrug fist cross type hips bow head), `face` left|right,
`gesture` [list of poses cycled], `talk` (mouth follows the voice), `hold` (prop in hand) + `hold_size`,
`to` (walk to x) + `walk_time`, `enter` pop|left|right, `delay`, `jump`, `shake`, `dim`, `label` (tag above head),
`close` (big close-up), `back` (seen from behind — foreground over-the-shoulder heads), `seated` (clipped at the table).

**Depth & storytelling devices** (all optional, any `set`):
- `window` {rect, sign, sign_color, street[], mullions[], wall, glass} — shot through a shop window with a mirrored street reflection
- `table` {y, x0, x1, items[cup|bottle|ketchup|box|<prop>], steam} — table in front of seated characters
- `board` {text "LINE ONE [RED WORD]|LINE TWO", rect, at, time} — dialogue hand-written on a banner as it is spoken
- `days_left` {x, y, w, n, title, circle_at} · `month_cal` {x, y, w, title, icon, at, time, upto}
- `bubble` {from, x, y, prop | text, at, out} · `emph` [{x, y, r, at}] · `swoosh` [{x, y, r, a0, a1, color, at}]
- `popup` {name, x, at, h, rot} — prop rising into frame close to camera (charter, notepad, menu_card, letter)
- `names` [{t, x, y, at, bar}] — typed name tags · `lower` {name, role} · `caption` "PLACE, YEAR"
- `big` {t "{n} SIPAHI", count, y} — counting number · `props` [{name, x, y, h, anim, label, layer}]
- `stickers` [{name | img, side, anim pop|slide|drop|spin|rain, h, at, out, pulse, label}] — premium cut-outs, no border
- `fg` [pillar, curtain, plant, lamp_post, crates, grass, desk_corner, crowd, bars, bokeh] (auto per set)
- `source` "Book (year)" + `source_by` "Archive · licence" — premium SOURCE credit (use on every fact shot)

### `black` — hand-written line typed on black (left aligned). `t`, `size`, `align`
### `map` — `view` [lon0, lat0, lon1, lat1], `highlight` {ISO3: colour}, `routes` [{from, via[], to, mover, delay, time, color}],
`pins` [{lon, lat, label, delay}], `labels` [{lon, lat, t, size, color}]. India is ALWAYS drawn with its full official outline.
### `topdown` — table from above: `cups` [[x,y]], `people` [{x, y, color, hair}], `paper` {x, y, w, draw chip|ship|map|square, at, note},
`hands` [{from left|right|top|bottom, to [x,y], item coin_bag|cash|<prop>, label "£100", at, release, sleeve}], `merge` {at, to, label}
### `realdoc` — REAL archival scan as a 3D sheet: `img` (assets/docs/...), `crop`, `highlights` [{rect, at, time}], `focus`,
`yaw`/`pitch`/`roll`/`push` [start, end], `curl`, `tone` sepia|ink, `source`, `source_by`. Add the file to assets/docs/credits.json.
### `memo` — hand-written note/letter in 3D: `title`, `lines`, `highlight`, `stamp`, `sticky`
### `newspaper` — `name`, `date`, `headline`, `who` (portrait)
### `chart` — `bars` [{label, value, text, color}]
### `split` — `left` {scene}, `right` {scene}, optional `right2` {scene} + `swap_at`

## Rules that make it look like the reference
- Something moves every moment: never write a beat without characters, props or camera moving.
- 2.5–5 s per beat, 8-word sentences, a black type-on card every ~10 beats, chapter cards in black.
- Re-use one set from 2–3 angles (wide → over-the-shoulder → close) for a dialogue.
- Show money/objects being HANDLED (hands, tables), not floating; numbers get a counter or a label.
- Every fact shot gets `source`; proof moments use `realdoc` with a real public-domain scan.
