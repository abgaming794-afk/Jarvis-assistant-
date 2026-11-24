---
name: stickman-host
description: Builds the 3D stickman on-camera host for Unexplored Truth by Amrit long videos - a toon stickman on a gaming chair in a YouTube studio with the channel logo and neon sign, hand gestures and voice-driven lip sync. Use when the user asks for the host, the stickman, "camera wala hissa", the studio scene, lip sync, or host segments in a documentary or explainer video.
---

# Stickman Host

The recurring on-screen host: a 3D toon stickman on a gaming chair in a YouTube studio, speaking the narration with
lip sync and gestures. The approved design is fixed - the user said "stickman ko pehle jaisa hi rakho". Reuse the
bundled build, do not redesign it.

## Bundled build (`${CLAUDE_PLUGIN_ROOT}/engine/host/`)

- `host.html`: three.js 0.169 scene. Toon materials with inverted-hull outlines; gaming chair, desk, boom mic,
  monitor (shows a frame from the video, `monitor.png`), back wall with neon "AMRIT BORI" sign and the channel logo
  sign. `window.renderFrame(state)` draws one frame; state = `{t, mouth, gestures[], camFrom, camTo, camK}`.
- `prep_host.py`: amplitude lip sync from the VO (band-pass 180-3200 Hz, RMS per frame, percentile normalisation,
  quick close on pauses) plus the segment list (time span, camera move, gestures) -> `host_frames.json`.
- `render_host.js <SEG> 2560 1440 <outdir>`: Playwright + Chromium with swiftshader WebGL, one JPEG per frame;
  resumable (skips existing frames). Serve the workspace first: `python3 -m http.server 8765` from `$AB_ROOT`.
- The storyboard composites these frames full-screen (scaled to 4K) for host shots.

Gestures available: `wave, palms, pointdown, count1, count2, shrug, think, salute, lean, nod` (side `L`/`R`).
Cameras: `wide, medium, close`, eased between presets.

## Workflow

1. Pick host segments: intro (hook + subscribe animation), one mid-video recap, outro. Maps and documents carry the
   factual middle.
2. Write the segment list in `prep_host.py` with gestures on the exact words (VO time from `full_units.json`), run it.
3. Render 3 test stills (idle, mid-gesture, close camera); check the mouth is closed in a known pause.
4. Render all frames (about 0.4-0.6 s per frame at 2560x1440 on swiftshader), then composite.

## Rules

- At most one gesture per sentence; return to idle between gestures.
- Cut away from the host at least every 10-15 seconds.
- Never imitate a real person's face; the host is a generic stickman.
- Say plainly that lip sync is amplitude based, not phoneme exact.
- `references/rig-and-lipsync.md` holds the original rig notes (Remotion variant) for reference.
