---
name: story-proof-style
description: The "story first, proof after" editing style for Unexplored Truth by Amrit Shorts and long videos - satellite map hook, glowing regions, flag fills and peels, timeline ribbon, wipe to a parchment map, map mascots with eyes and props, stamps, pins, neon badges, ink iris, story scenes on photoreal backgrounds, then the REAL document flies in and the camera pans to a marker-highlighted line. Use when the user asks for this style, "pehle animated story phir document me prove", "GeoGlobeTales / America Independent jaisa editing", map + zoom + 3D movement + PNG props, or any history explainer scene that must show evidence.
---

# Story-then-Proof Style (new in 1.1.0)

Learned from the reference the user sent ("How Did America Become Independent", see
`references/reference-breakdown.md` for the second-by-second analysis). Code: `${CLAUDE_PLUGIN_ROOT}/engine/visuals/
storyproof.py` (imports `core.py`). Worked demo (16 s, Khilafat topic): `engine/examples/storyproof-demo/demo.py`.

## Hard rule from the user

**Keep the channel's own 2D man.** Never copy the reference channel's characters (their round colonists/soldiers),
their footage, music or logo. Copy only the techniques. Map mascots (eyes / mouth / glove hands on a country shape)
are generic and allowed. Crowds: `crowd_silhouettes()` or the channel's own 2D man in groups.

## New in 1.2.0 - the user's rules for battles and maps

- **Every war / battle / event gets a 2D cartoon animated scene** (user: "jo jo yudh, event har scene ko samjhane ke
  liye real cinematic feel dene ke liye wo cheez zaroori hai"). Use `engine/visuals/battle2d.py`: `Battle(left, right,
  winner, t0, dur, t_clash, t_rout, volley=...)` choreographs approach -> arrow volley -> clash (camera zoom + shake,
  sparks) -> melee -> rout (losers flee, some fall) -> winners cheer; `winner=None` for indecisive battles. Units:
  `soldier()` (factions arab, arab_gen, chalukya, rajput, pratihara, frank, khazar, turk, byzantine, berber, syrian -
  built on the channel's own 2D man design), `horse()` riders, `elephant()` with `king_bust()` (royal umbrella),
  `arrow_volley`, `dust`, `sparks`, `speed_lines`. Sieges: see `siege()` in the two-minute demo (cartoon wall,
  ladders, rocks, ladders thrown back). Parades/marches: `Battle(..., linear=True)` with an empty other side.
- **Background of cartoon battles = photoreal** (user's choice): `prep_battle_bg(photo, tint=...)` blurs the photo into
  a distant bokeh and keeps a sharp ground strip; `battle_bg()` adds a slow push and dust haze. Label AI photos
  "AI chitran". Cartoon is clearly an illustration; no blood.
- **Maps in 3D** (user: "3d map animation bhi"): `map3d(c, draw_flat, tilt, rot)` lays any flat map (satellite or
  parchment) on the ground with perspective + sky + fog and returns M; `extrude(c, M, flat_path(cam, path), height,
  col)` raises regions/empires out of the ground (stagger states to show growth); `pin3d` standing pins with labels;
  `fire3d` burning fronts; project any lon/lat with `proj(M, *to_screen(cam, lon, lat))` for 3D marches.
- Worked example with all of it: `engine/examples/storyproof-demo/two-minute/` (2:05 on the real Khilafat VO).

## The beat grammar (use for every event in the script)

1. **Locate** - satellite map, camera flight in (`Satellite`, `cam_lerp`), region lights up on its word
   (`region_glow`), red pin with name + date (`pin_drop`).
2. **Who owns it** - flag/symbol fills the region (`flag_fill`, period-correct: Umayyad banner white, era maps per
   the documentary rules); celebration -> `fireworks`.
3. **When** - `timeline_ribbon` at the top; rewinds scroll with motion blur (`vel`).
4. **Explain** - hard wipe to the parchment map (`style_wipe` + `parchment_map`): mascots act (`googly_eyes`,
   `mascot_mouth`, `glove_hand`), props drop/pop (`prop_drop`, `pop_icon`: crown, tax items, pitchforks, torches,
   quill), arrows (`white_arrow`, `hand_arrow`), stamps with a hit (`stamp_slam` + `shake`), badges (`neon_badge`),
   flags peel off when power changes (`flag_peel`), alliances colour the world (`world_alliance`), troops march
   (`march`), battles get little flags (`flag_markers`).
5. **Story** - ink iris (`iris`) into a story scene (for wars: a full 2D cartoon battle, see above): photoreal background (real photo or the user's ChatGPT image,
   labelled "AI chitran") with a slow push and parallax (`story_scene`), the channel's 2D man acting, serif title +
   date (`serif_title`), quotes (`quote_line`), whip between shots (`whip_blur`).
6. **Proof** - right after the story of an event, the REAL artefact: `doc_fly` (Wikipedia card, manuscript, coin,
   inscription, painting, newspaper) then `doc_pan` across it with depth of field and a marker sweep on the exact
   sentence (Wikipedia captures from `docshot_noinfobox.js` give the line box in the JSON - use it). Lists of
   laws/taxes/demands: `parchment_list` (strike, stamp, green circle). Footnote the source on screen.

Pacing: a new visual every 1-2 s, a new scene every 3-6 s, the camera always drifting. Two map looks only
(satellite for hook/present, parchment for history). Serif titles (`SERIF_DISPLAY` Abril Fatface), serif labels
(`SERIF_TEXT` Playfair Display), dates small and yellow, few words on screen.

## Sound pairing (recommendations - the reference's audio was not analysed)

Ready-made, synthesised SFX library + VO-word-timed event list: `engine/examples/storyproof-demo/one-minute/`
(`demo60.py sfx` -> `mix60.py`). The user approved this approach: VO from the project, SFX made by Claude.


whoosh: camera flight, doc fly-in, whip; paper rustle: parchment, doc pan; thud + short low hit: stamp; pop: icons,
pins, eyes; sparkle crackle: fireworks; swish: style wipe; low boom: iris close; marker squeak: highlight. Keep SFX at
the channel's half loudness under the VO.

## Shorts (9:16)

Same functions work with `AB_ORIENT=vertical` (DW x DH = 1080 x 1920): put the timeline at y ~ 260, titles in the
upper third, the doc window 1000 px wide, `doc_pan` windows 9:16 (compute the window from the highlight box like the
demo does, with the aspect swapped).

## Checklist before a review render

- Every event: story beat AND proof beat (no claim without its artefact on screen).
- Flags/symbols period-correct; AI images labelled; real artefacts credited in PHOTO_CREDITS + description.
- Text inside the safe area, nothing under the YouTube duration stamp in Shorts captions, stamps never cover a face
  or the highlighted line.
- Stills contact sheet, then the 360p review (`render_review.py`).
