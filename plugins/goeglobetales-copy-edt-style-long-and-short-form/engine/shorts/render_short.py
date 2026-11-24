"""Chunked parallel render of the Short.  usage: render_short.py preview|4k [nproc]"""
import os, sys
import subprocess, math
os.environ.setdefault("AB_ORIENT", "vertical")
from multiprocessing import Process
sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.join(os.environ.get("AB_ROOT", "/home/user/amrit-borii/"), os.environ.get("AB_PROJECT", "new-short"), "")
MODE = sys.argv[1]; NP = int(sys.argv[2]) if len(sys.argv) > 2 else 4
FPS = 60
def work(i0, i1, out):
    import skia, short_storyboard as N
    W, H, sc = (1080, 1920, 1.0) if MODE == "preview" else (2160, 3840, 2.0)
    enc = (["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p"] if MODE == "preview" else
           ["-c:v", "libx265", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1", "-x265-params", "log-level=error"])
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + enc + [out],
                         stdin=subprocess.PIPE)
    sf = skia.Surface(W, H)
    for f in range(i0, i1):
        c = sf.getCanvas(); c.save(); c.scale(sc, sc); N.frame(c, f / FPS); c.restore()
        p.stdin.write(sf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: open(out + ".done", "w").write("ok")   # a killed encoder (e.g. out of memory) leaves no .done
if __name__ == "__main__":
    import short_storyboard as N
    total = int(math.ceil(N.T_TOTAL * FPS)); nch = NP * 2
    tmp = ROOT + f"render/tmp_{MODE}/"; os.makedirs(tmp, exist_ok=True)
    edges = [round(total * k / nch) for k in range(nch + 1)]
    jobs = [(edges[k], edges[k + 1], tmp + f"c{k:02d}.mp4") for k in range(nch)]
    todo = [j for j in jobs if not os.path.exists(j[2] + ".done")]
    for b in range(0, len(todo), NP):
        ps = [Process(target=work, args=j) for j in todo[b:b + NP]]
        [q.start() for q in ps]; [q.join() for q in ps]
        print(f"batch {b // NP + 1}/{math.ceil(len(todo) / NP)} done", flush=True)
    open(tmp + "list.txt", "w").write("".join(f"file '{j[2]}'\n" for j in jobs))
    out = ROOT + ("render/short_preview_1080p.mp4" if MODE == "preview" else "render/short_4k60_hevc10.mp4")
    ac = ["-c:a", "aac", "-b:a", "256k"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", tmp + "list.txt", "-i", ROOT + "audio/short_mix_norm.wav",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy"] + ac + ["-shortest", "-movflags", "+faststart", out], check=True)
    print("OUT", out)
