# Rig, studio set, lip sync, gestures

## Stack

- Remotion with `@remotion/three` (`ThreeCanvas`) and `three`.
- `@remotion/media-utils` (`useAudioData`, `visualizeAudio`) for audio-driven lip sync.
- Animate everything from `useCurrentFrame()`; never use real-time clocks, `requestAnimationFrame` or CSS animation, because Remotion renders frame by frame.

## Character rig

- Head: sphere. Neck: short cylinder. Torso: capsule. Hips: sphere.
- Limbs: capsules for upper arm, forearm, thigh, shin. Hands: small spheres plus optional 3 thin finger capsules for pointing and counting.
- Joints are nested `group` objects so rotating a parent moves the children (shoulder -> elbow -> wrist).
- Toon look: flat material colors plus a slightly larger back-face-only copy of each mesh in black (inverted hull) for a thick outline. Add a soft key light and a rim light in the channel accent color.
- Face: two eyes (white sphere plus black pupil), eyebrows as thin boxes, mouth as a flattened sphere or a dark ellipse on the face plane.
- Idle motion: breathing (torso scale +-1.5%), small head sway, blink every 2-5 seconds at random with a seeded generator so renders are repeatable.

## Studio set

- Gaming chair: seat and back from rounded boxes, headrest, armrests, 5-star base from cylinders, accent stripes in the channel color.
- Desk with a microphone on a boom arm, one or two monitors, keyboard.
- Back wall with acoustic panels, a neon sign reading "AMRIT BORII", soft RGB strip lights, a bookshelf or world-map poster.
- Three camera presets: wide (whole set), medium (waist up), close (head and shoulders). Move between presets with an eased interpolation of 12-18 frames, never a hard jump, except on a beat.
- Slight constant camera drift (parallax) so the shot never feels frozen.

## Lip sync (audio-driven)

1. Load the chapter audio with `useAudioData`.
2. Each frame, call `visualizeAudio` with 32 samples and take the average of the low-mid bins as `level` (0 to 1).
3. Smooth it: `open = prevOpen * 0.6 + level * 0.4`, with a minimum threshold (below it the mouth is closed).
4. Map `open` to mouth height (scale Y of the mouth ellipse) and slightly to mouth width. Add a small jaw drop on the head's lower half for strong syllables.
5. Pauses in the audio close the mouth within 2-3 frames. Add a tiny head nod on stressed peaks.
6. Optional upgrade: if word timestamps are available, switch mouth shape between a few presets (closed, wide "A", round "O", flat "E") at word starts; keep amplitude as the fallback.

State plainly to the user that this is amplitude-based sync, not exact per-shape phoneme sync.

## Gesture library

Implement each gesture as a function returning joint angles for a given progress `p` in 0..1, with ease-in (6 frames), hold, ease-out (8 frames). Gestures blend over the idle pose.

| Tag | Motion |
|---|---|
| point-left / point-right | Extend the arm toward the side where the map or graphic will appear, index finger out |
| open-palms | Both forearms lift, palms up, small outward push |
| count-1/2/3 | One hand raises with that many fingers extended |
| shrug | Shoulders up, palms up, head tilt |
| lean-in | Torso leans toward camera, camera preset moves to close |
| think | One hand to chin, head tilt, eyes look up |
| facepalm | Hand to forehead, head down |
| desk-slam | Fist down on desk with a small camera shake and impact SFX |
| nod | Head pitch down-up twice |

## Rendering

- Full-frame host: render with the studio background, H.264, 1920x1080, 30 fps.
- Overlay host: `npx remotion render <id> out/host.webm --codec=vp8 --image-format=png --pixel-format=yuva420p` for a transparent background.
- Check at least 3 still frames (idle, mid-gesture, close camera) before the full render. Check the mouth is closed during a known pause.
- Render long chapters in segments so one failed render does not cost the whole chapter.
