"""Full render: 16 chunks (4 parallel) -> concat -> mux audio -> 4K master + 1080p preview. Restartable (skips done chunks)."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import subprocess, os, sys, time
from concurrent.futures import ThreadPoolExecutor
ROOT = PROJ + ""
OUT = ROOT + "render/"; TMP = AB_ROOT + "render_tmp/"
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
FPS = 60; DUR = 535.0; N = int(DUR * FPS); P = 16
B = [round(i * N / P) for i in range(P + 1)]
here = os.path.dirname(os.path.abspath(__file__))
def job(i):
    out = f"{TMP}c{i:02d}.mp4"
    if os.path.exists(out + ".done"): return i, 0
    t0 = time.time()
    r = subprocess.run([sys.executable, "full.py", "chunk", str(B[i]), str(B[i + 1]), out], cwd=here, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0: print("chunk", i, "FAILED", r.stderr[-800:], flush=True); return i, -1
    open(out + ".done", "w").write("ok"); print(f"chunk {i} done in {time.time() - t0:.0f}s", flush=True); return i, 1
t0 = time.time()
RANGE = range(int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else range(P)
with ThreadPoolExecutor(4) as ex: res = list(ex.map(job, RANGE))
if len(sys.argv) > 2 and int(sys.argv[2]) < P: print('partial range done', flush=True); sys.exit(0)
if any(r[1] == -1 for r in res): sys.exit("some chunks failed")
open(TMP + "list.txt", "w").write("".join(f"file 'c{i:02d}.mp4'\n" for i in range(P)))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", TMP + "list.txt", "-c", "copy", TMP + "video.mp4"], check=True)
master = OUT + "AMRIT_BORI_Naya_Axis_4K60_10bit.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", TMP + "video.mp4", "-i", ROOT + "audio/full_mix.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                "-shortest", "-movflags", "+faststart", master], check=True)
prev = OUT + "AMRIT_BORI_Naya_Axis_preview_1080p.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", master, "-vf", "scale=1920:1080:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", prev], check=True)
print("ALL DONE in", round(time.time() - t0), "s", flush=True)
