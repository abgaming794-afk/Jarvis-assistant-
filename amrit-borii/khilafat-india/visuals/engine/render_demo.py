"""Demo preview: 1080p H.264, 30 fps, 3 parallel chunks, then concat + mux with audio/full_mix.wav."""
import os, sys, subprocess
os.environ.setdefault("AB_PROJECT", "khilafat-india")
import kh
FPS = 30; END = kh.vo_to_video(kh.DEMO_END) + 1.0; N = int(END * FPS); P = 3
out = kh.AB_ROOT + "render_tmp/demo/"; os.makedirs(out, exist_ok=True)
if len(sys.argv) > 1 and sys.argv[1] == "one":
    i = int(sys.argv[2]); a, b = N * i // P, N * (i + 1) // P
    kh.encode_chunk(a, b, out + f"c{i}.mp4", fps=FPS, preview=True); sys.exit()
procs = [subprocess.Popen([sys.executable, __file__, "one", str(i)]) for i in range(P)]
for p in procs: p.wait()
open(out + "list.txt", "w").write("".join(f"file 'c{i}.mp4'\n" for i in range(P)))
final = kh.ROOT + "render/DEMO_khilafat_1080p.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", out + "list.txt", "-i", kh.ROOT + "audio/full_mix.wav",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
print("done", final, round(END, 2), "s")
