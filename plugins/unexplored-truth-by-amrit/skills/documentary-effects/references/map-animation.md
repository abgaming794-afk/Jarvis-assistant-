# Map animation

Use the `remotion-maps` skill from the Remotion plugin as the base. Use Natural Earth for coastlines, borders, rivers and lakes (check the licence and credit it in the description). Use a dark, high-contrast base map so labels stay readable on a phone.

## Effects

| Effect | How |
|---|---|
| Fly-over / camera zoom | Animate center and zoom with easing over 30-60 frames; start wide, end on the place being named |
| Route draw | SVG path with `strokeDashoffset` 1 -> 0 over 40-90 frames; moving dot or ship/plane icon along the path |
| Region highlight | Fill the country or region polygon with the accent color at 35-50% opacity, border pulse, other regions dimmed |
| Pulse rings | Concentric circles expanding from a point and fading, 2-3 rings, for capitals, attacks, bases, choke points |
| Distance line | Dashed line between two points with a label (km) fading in; measure with the great-circle formula |
| Disputed border | Dashed line in a distinct color with a "DISPUTED" tag; never draw a disputed border as settled |
| Influence spread | Region fill that grows over years with a year counter |
| True-size / compare | Drag a country outline over another to compare size |
| Choke point | Zoom to a narrow strait, highlight width, show ship-count or oil-share counter |
| Trade/energy flow | Animated arrows along routes with thickness showing volume |
| Pins and flags | Drop-in pin with a short bounce; flag from a licensed flag set |
| 3D globe | `ThreeCanvas` sphere with an equirectangular texture; rotate to the target, then flatten into the 2D map |
| Terrain | Hillshade or elevation raster behind the vectors for rivers and mountain topics (SRTM, licence to be checked) |

## Rules

- One map idea per scene. Hold the final state for at least 1 second so it can be read.
- Labels: large, white or accent color, with a dark halo; no more than 4 labels at once.
- Every number on the map comes from the research dossier and has a source.
- Keep the camera moving slowly even on the hold (1-2% drift).
- Sync the map event to the exact word in the voice-over: place name appears on the word, route starts on the verb.

## Learned on Naya AXIS (user feedback)

- Zoom like Google Maps: one continuous eased camera move world -> country -> city -> landmark, highlighting each level
  as it arrives. Never a white flash or hard cut between zoom steps.
- India always with the official boundary (`engine/visuals/india_official.geojson.json`, Survey of India).
- Moving objects stay on the right geography: ships on the sea lane (Hormuz), never over land.
- Supply stories: source country map, goods animated to the receiver, then what they become (machines -> factories).
- Labels small enough not to cover the action; a strait label is a tag, not a headline.
- Implementation: `WorldMap`, `draw_map`, `to_screen`, `cam_xy` in `engine/visuals/core.py`; `route`, `pin`,
  `flag_circle` in `widgets.py`; `HORMUZ_PATH` / `hormuz_xy` in `full.py` as the sea-lane example.
