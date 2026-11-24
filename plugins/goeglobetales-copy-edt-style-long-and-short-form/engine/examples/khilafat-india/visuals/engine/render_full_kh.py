"""Full render: 4K60 10-bit HEVC in 16 chunks (4 parallel, resumable via .done), optional batch range `a b`;
`final` = concat + mux (loudness-normalised mix) + 1080p H.264 preview."""
import os, sys, subprocess
os.environ.setdefault("AB_PROJECT", "khilafat-india")
import kh
FPS = 60; END = kh.vo_to_video(kh.VIDEO_END_VO); N = int(END * FPS); P = 16
TMP = kh.AB_ROOT + "render_tmp/full/"; os.makedirs(TMP, exist_ok=True)
rng = lambda i: (N * i // P, N * (i + 1) // P)
if len(sys.argv) > 1 and sys.argv[1] == "one":
    i = int(sys.argv[2]); a, b = rng(i); kh.encode_chunk(a, b, TMP + f"c{i:02d}.mp4", fps=FPS); open(TMP + f"c{i:02d}.done", "w").write("ok"); sys.exit()
if len(sys.argv) > 1 and sys.argv[1] == "final":
    open(TMP + "list.txt", "w").write("".join(f"file 'c{i:02d}.mp4'\n" for i in range(P)))
    R = kh.ROOT + "render/"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", kh.ROOT + "audio/full_mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", TMP + "mix_norm.wav"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", TMP + "list.txt", "-i", TMP + "mix_norm.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", R + "KHILAFAT_4K60_master.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", R + "KHILAFAT_4K60_master.mp4", "-vf", "scale=1920:1080", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", R + "KHILAFAT_1080p_preview.mp4"], check=True)
    print("final done", round(END, 2)); sys.exit()
a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, P)
todo = [i for i in range(a, b) if not os.path.exists(TMP + f"c{i:02d}.done")]
running = []
while todo or running:
    while todo and len(running) < 4:
        i = todo.pop(0); running.append((i, subprocess.Popen([sys.executable, __file__, "one", str(i)])))
    for i, p in list(running):
        if p.poll() is not None: running.remove((i, p)); print("chunk", i, "done", flush=True)
    import time; time.sleep(5)
print("batch", a, b, "done", N, "frames total", flush=True)
