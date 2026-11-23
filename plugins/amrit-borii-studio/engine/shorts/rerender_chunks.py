"""Re-render chosen 4K chunks, each split in two (max 4 at once), then concat + mux again.
usage: rerender_chunks.py 3 4          (re-render these chunks after a change)
       rerender_chunks.py --resume 3 4 (only redo halves that failed or are missing)"""
import os, sys
import math, subprocess
os.environ.setdefault("AB_ORIENT", "vertical")
from multiprocessing import Process
RESUME = "--resume" in sys.argv
sys.argv = [sys.argv[0], "4k"] + [a for a in sys.argv[1:] if a != "--resume"]
import render_short as RS
import short_storyboard as N
ids = [int(x) for x in sys.argv[2:]]
total = int(math.ceil(N.T_TOTAL * RS.FPS)); nch = 8
tmp = RS.ROOT + "render/tmp_4k/"
edges = [round(total * k / nch) for k in range(nch + 1)]
subs = []
for k in ids:
    a, b = edges[k], edges[k + 1]; m = (a + b) // 2
    subs += [(a, m, tmp + f"c{k:02d}a.mp4"), (m, b, tmp + f"c{k:02d}b.mp4")]
def ok(f):   # finished and readable
    if not os.path.exists(f + ".done"): return False
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-f", "null", "-t", "0.1", "-"], capture_output=True)
    return r.returncode == 0
todo = [j for j in subs if not (RESUME and ok(j[2]))]
for f in [j[2] for j in todo]:
    if os.path.exists(f + ".done"): os.remove(f + ".done")
NP = 4   # 4K x265 encoders need ~2.5 GB each: never run more than 4 at once (14 at once ran out of memory)
for b0 in range(0, len(todo), NP):
    ps = [Process(target=RS.work, args=j) for j in todo[b0:b0 + NP]]
    [q.start() for q in ps]; [q.join() for q in ps]
    print(f"batch {b0 // NP + 1}/{(len(todo) + NP - 1) // NP} done", flush=True)
bad = [j[2] for j in subs if not ok(j[2])]
if bad: sys.exit("chunks failed, run again: " + " ".join(bad))
files = []
for k in range(nch):
    split = k in ids or os.path.exists(tmp + f"c{k:02d}a.mp4.done")   # keep chunks fixed by an earlier re-render
    files += [tmp + f"c{k:02d}a.mp4", tmp + f"c{k:02d}b.mp4"] if split else [tmp + f"c{k:02d}.mp4"]
open(tmp + "list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
out = RS.ROOT + "render/short_4k60_hevc10.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", tmp + "list.txt", "-i", RS.ROOT + "audio/short_mix_norm.wav",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out], check=True)
print("OUT", out, flush=True)
