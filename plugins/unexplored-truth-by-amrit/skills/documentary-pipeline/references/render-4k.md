# 4K 60 fps 10-bit render

Engine: `${CLAUDE_PLUGIN_ROOT}/engine/visuals/` (skia-python). See `engine/README.md` for layout and setup.

## Steps

1. Stills first: `python3 full.py still <dir> <t1> <t2> ...` (video time), then tile them into a contact sheet with
   ffmpeg (`tile=4x5`) and inspect. Fix everything before the long render.
2. SFX list: `python3 full.py sfx` -> `audio/full_sfx.json`.
3. Audio: `python3 audio/mix_full.py` -> `audio/full_mix.wav` (VO with chapter-pause silences, SFX, music bed).
4. Video in batches (a background task dies at 2 hours):
   - `python3 render_full.py 0 8 > log 2>&1` (background), then `python3 render_full.py > log 2>&1` for the rest and
     the finalize step (concat, mux AAC 320k, faststart, 1080p preview).
   - About 1 frame/s per process on 4 CPUs; each batch of 4 chunks (about 33 s of video each) takes 32-40 min.
   - Report progress from chunk file sizes vs finished chunks (MB/chunk about 34) when the user asks "kitna baki".
5. Verify: `ffprobe` (hevc, 3840x2160, yuv420p10le, 60/1, duration), sample 20 frames from the preview into a
   contact sheet and look at it.
6. Deliver: preview (render), master split losslessly into 2 parts under 500 MiB
   (`ffmpeg -i master -t HALF -c copy p1.mp4`, `ffmpeg -ss HALF -i master -c copy p2.mp4`), upload pack.

## Fixes after the render

- Find the chunk: `B[i] = round(i * N / 16)`, `N = duration * 60`; frame = video time * 60.
- Re-render only those chunks; split a chunk in halves on 4 CPUs (`full.py chunk a m`, `full.py chunk m b`) and join
  with `-f concat -c copy`, keep the `.done` marker, then run `render_full.py` to finalize.
- Keep the old chunk as `cNN_old.mp4` until the new master is verified.

## Chapter pauses

`CH_GAP = 1.4` s at each chapter card. `remap(T)` converts video time to VO time and freezes the VO clock while the card
animates; `VIDEO_TOTAL = VO_TOTAL + CH_GAP * chapters`. `mix_full.py` must use the same `GAPS` list.

## 1.0.0 workflow (Khilafat example, `engine/examples/khilafat-india/visuals/engine/`)

- Review: `AB_PREVIEW=360 python3 render_review.py` (also 480/720) -> `render/REVIEW_360p.mp4`, 30 fps, 4 chunks,
  x264 veryfast, loudnorm mix. Send it before every 4K run.
- Final: `python3 render_full_kh.py 0 8` (background, timeout 2 h) -> `python3 render_full_kh.py 8 16` ->
  `python3 render_full_kh.py final`. Clear old chunks first when the storyboard changed:
  `rm -f render_tmp/full/*.done render_tmp/full/c*.mp4`. A late fix = delete only that chunk's `.done` + mp4, rerun
  the batch that holds it, then `final`. Chunk i covers frames `N*i//16 .. N*(i+1)//16`.
- Sizes for 10:46: master ~1.4 GB HEVC 10-bit, preview ~260 MB H.264.
