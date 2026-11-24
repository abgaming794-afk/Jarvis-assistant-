# Effects recipes (Remotion, 30 fps)

> Engine default is 60 fps (skia, `engine/visuals/`): double these frame counts, or read them as seconds x 30.

All timings are in frames at 30 fps. Drive everything from `useCurrentFrame()` and `interpolate`/`spring`.

## Transitions

### Ink flash (chapter change), 14-20 frames
- Frames 0-6: black ink blobs expand from 3-5 seeds over the outgoing scene until the frame is covered.
- Frame 6-8: optional 2-frame white flash for punch.
- Frames 8-20: ink recedes from the edges to reveal the incoming scene.
- Build options: (a) SVG mask of several animated circles with `feTurbulence` + `feDisplacementMap` for ragged edges, applied as a CSS mask on the incoming scene; (b) a pre-rendered ink-splash clip with alpha, placed with `OffthreadVideo` over the cut. Prefer (b) for speed.
- Sound: low ink-splash/whoosh at frame 0, small tail at frame 12.

### 3D zoom-through (scene change), 12-16 frames
- Outgoing scene: scale up 1 -> 1.35, blur 0 -> 14px, opacity 1 -> 0 with a small tilt.
- Incoming scene: starts scale 0.8 and blurred, settles to 1.
- Alternate the tilt direction (+4 / -4 degrees) on each use so it never looks repeated. Overlap both scenes by 6 frames so there is never a black gap.

### Whip pan, 8-10 frames
- Horizontal motion blur and a fast slide between two scenes; use for map-to-map jumps.

### Glitch cut, 6-8 frames
- RGB channel split, horizontal slice offsets, 2 frames of scanlines. Use for reveals and contradictions.

## Image and 3D motion

### 2.5D parallax
- Split an image into 2-4 depth layers (foreground, subject, midground, background) using a depth-estimation or cutout tool, or use a single image on a plane with a subtle depth displacement.
- Place layers at different z in a `ThreeCanvas`, move the camera on a slow dolly (5-8% push over the scene) with a slight orbit (1-3 degrees).
- Add depth-of-field blur on background layers.

### Camera shake
- Seeded noise on camera position and rotation, amplitude 2-6 px, decays over 10 frames. Use on impact words.

### Speed ramp and freeze
- Slow to 40% then snap back for a key moment; or freeze a frame, desaturate and overlay a sketch-outline for emphasis.

## Paper and document effects

- Paper cutout: image with torn white border, small drop shadow, 1-3 degree rotation, slight wobble.
- Newspaper/halftone: halftone dot filter over an image, yellowed paper texture behind.
- Marker highlight: a rectangle sweeping left to right behind the key line, 10-12 frames, with a marker sound.
- Underline/circle: SVG path drawn with `strokeDashoffset`.
- Stamp: "CLASSIFIED", "DISPUTED", "CONFIRMED", "UNVERIFIED" scale from 1.8 -> 1 with a 3-frame shake and a thud. Use "DISPUTED" or "REPORTEDLY" for contested claims.
- Redaction bars sliding over text for secrecy topics.

## Text and numbers

- Kinetic typography: key words pop in with a short spring and a 2-frame overshoot; the rest of the line fades in.
- Typewriter reveal for dates and place names; cursor tick sound.
- Counters: count from 0 (or the old value) to the target in 24-36 frames with easing, then a 6-frame highlight pulse. Format large numbers with Indian digit grouping when speaking to an Indian audience, and show the unit.
- Lower thirds for names and places: slide in 8 frames, hold, slide out.
- Split screen / versus layouts for two-side comparisons, each side with its own source label.
- Timeline bar with milestones that light up as they are spoken.

## Atmosphere

- Film grain overlay at 6-10% opacity; vignette at 15-25%; subtle dust particles.
- Light leaks on transitions to warmer scenes (use sparingly).
- Color grade: one grade for the whole video (for example desaturated teal and orange). Maps stay clean and high-contrast on a dark background.
- Ambient music bed under the voice at -22 to -26 LUFS relative; duck 4-6 dB under narration.

## Sound pairing

| Effect | Sound |
|---|---|
| Ink flash | ink splash plus low whoosh |
| 3D zoom-through | soft whoosh |
| Stamp | thud |
| Counter | tick run, then a small hit at the final value |
| Marker highlight | marker squeak |
| Glitch | digital crackle |
| Paper cutout | paper rustle |
| Desk slam | impact plus 2 frames of camera shake |

Generate or source sound effects from licensed or self-made audio only.

## Performance

- SVG filters (`feTurbulence`, `feDisplacementMap`) are slow in headless rendering. Pre-render ink, grain and light leaks once, reuse as alpha video.
- Render long videos in chapter segments and concatenate.
- Use `OffthreadVideo` for video layers and `Img`/`staticFile` for images.
