"""Fast whole-video review: 1280x720 (or AB_PREVIEW=480 -> 854x480) 30 fps, 4 parallel chunks -> render/REVIEW_<res>p.mp4"""
import os, sys, subprocess
os.environ["AB_PREVIEW"] = os.environ.get("AB_PREVIEW") if os.environ.get("AB_PREVIEW") in ("720", "480", "360") else "720"; os.environ.setdefault("AB_PROJECT", "khilafat-india")
RES = os.environ["AB_PREVIEW"]
import kh
FPS = 30; END = kh.vo_to_video(kh.VIDEO_END_VO); N = int(END * FPS); P = 4
TMP = kh.AB_ROOT + f"render_tmp/review{RES}/"; os.makedirs(TMP, exist_ok=True)
def chunk(i):
    a, b = N * i // P, N * (i + 1) // P
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{kh.W4}x{kh.H4}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", TMP + f"r{i}.mp4"], stdin=subprocess.PIPE)
    for f in range(a, b): ff.stdin.write(kh.render(f / FPS).tobytes())
    ff.stdin.close(); ff.wait()
if len(sys.argv) > 1: chunk(int(sys.argv[1])); sys.exit()
ps = [subprocess.Popen([sys.executable, __file__, str(i)]) for i in range(P)]
for p in ps: p.wait()
open(TMP + "list.txt", "w").write("".join(f"file 'r{i}.mp4'\n" for i in range(P)))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", TMP + "list.txt", "-i", kh.ROOT + "audio/full_mix.wav",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-shortest",
                "-movflags", "+faststart", kh.ROOT + f"render/REVIEW_{RES}p.mp4"], check=True)
print("review done", round(END, 1), "s")
