---
name: documentary-effects
description: Library of documentary motion and effect styles for Unexplored Truth by Amrit videos - 3D camera moves, 2.5D image parallax, ink flash transitions, cinematic dossier style (photo collage, image-filled titles, dossier book, marker circles, torn-paper reveals), animated maps, paper and stamp effects, kinetic text, counters, glitch, grain and sound-effect pairing. Use when the user asks for effects, transitions, animation style, map animation, ink flash, 3D motion, or to make a scene look like a polished explainer documentary.
---

# Documentary Effects

Apply a consistent set of motion and effect styles to scenes of a long-form geopolitics or history documentary. The aim is a recognizable channel look: every scene has motion, every transition has a purpose, nothing is noise.

## Workflow

1. For each scene in the approved script, pick the visual type (map, document, image, footage, graphic, host) and one effect family from the lists below.
2. Read the matching reference:
   - `references/effects-recipes.md` for transitions, image and 3D motion, paper, stamp, text, counters, glitch, grain, color grade and sound pairing.
   - `references/map-animation.md` for every map effect.
   - `references/cinematic-dossier-style.md` for the channel's default look (photo collage desk, image-filled titles, dossier book with marker circles, torn-paper split reveals, typographic portraits). Use this look by default.
3. Implement with the bundled skia engine (primary, `${CLAUDE_PLUGIN_ROOT}/engine/visuals/`), or Remotion / HyperFrames. Use pre-rendered alpha overlays for heavy effects such as ink, grain and light leaks, so renders stay fast.
4. Render stills of the first, middle and last frame of each effect and check them before the full render.

## Choosing effects

- Default look: cinematic dossier style (see its reference).
- Chapter change: chapter card (number + title, red underline) that animates in a 1.4 s VO pause; ink flash optional.
- Scene change inside a chapter: 3D zoom-through, whip pan or simple cut.
- Still image: 2.5D parallax with slow camera push.
- Document or news clipping: paper cutout with marker highlight and a stamp.
- Number or statistic: counter with a highlight pulse.
- Place or route: map animation.
- Moment of tension or reveal: glitch, screen shake or desk-slam from the host, with an impact sound.

## Rules

- Pick one look and keep it: one color grade, one font pair, one transition family per video. Keep at most 3 effect families on screen in a given minute.
- Reserve the ink flash for chapter changes so it keeps its impact.
- Every effect needs a sound (whoosh, ink splash, paper rustle, stamp thud, tick). Keep sound effects under the voice-over.
- Text must stay readable on a phone: large, high contrast, inside the safe area.
- Do not use effects that obscure a number or a map label while it is being spoken.
- Effects serve the story. If a scene needs no effect, use none.
- Real event photos of public figures are allowed only from public-domain or CC-licensed sources (Wikimedia Commons), credited on screen and in the description, never altered to change their meaning.
- Never use emoji glyphs in rendered text (they draw as a box); draw icons in code.
- The working implementation of these effects (skia, 4K) is in `${CLAUDE_PLUGIN_ROOT}/engine/visuals/`; Remotion/HyperFrames remain options.

## Flag maps and ruler cards (0.5.0)

- Fill every empire/kingdom on the map with its flag or symbol, waving like cloth, ~50% blend, clipped to its border;
  when borders morph, the flag morphs with them (`wave_flag` in `engine/shorts/short_storyboard.py`).
- On a ruler's name: big framed portrait with name + source line, then it shrinks into a corner badge for the era.
- Small kingdoms: zoom the camera in and give each region its own waving flag on its name (no logo badges).
- Highlight a country on its name (glow + pulse fill, `highlight_country`) and a city with a spotlight (`spotlight`).

## Period maps, thin borders, smooth text (0.6.0+)

- Each scene shows the map of its own time: bhagwa-shaded period polities in historical scenes, today's tiranga India
  only in present-day scenes; modern flags only in present-day scenes, era symbols ("PRATIK (andaazan)") otherwise.
- Thin soft-blue country borders; thin highlight outlines.
- Hook text letter by letter, headlines word by word; rivers drawn with a dark casing; real manuscript/document cards.
  Details and helper names: `documentary-pipeline` skill, section "New in 0.6.0 / 0.7.0".

> 1.1.0: the full story-then-proof kit (satellite/parchment maps, flag fill/peel, timeline ribbon, map mascots,
> stamps, pins, neon badges, iris, doc fly-in and doc pan with highlights) lives in `engine/visuals/storyproof.py`;
> see the `story-proof-style` skill.
