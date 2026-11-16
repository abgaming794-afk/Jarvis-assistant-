"""Write full_sil.tsv (pause start/end per line) for align_full.py.  usage: python silences.py full_vo.mp3 [noise_db] [min_dur]"""
import re, subprocess, sys
src = sys.argv[1]; noise = sys.argv[2] if len(sys.argv) > 2 else "-35dB"; d = sys.argv[3] if len(sys.argv) > 3 else "0.18"
err = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
out, st = [], None
for l in err.splitlines():
    m = re.search(r"silence_start: ([\d\.]+)", l)
    if m: st = float(m.group(1))
    m = re.search(r"silence_end: ([\d\.]+)", l)
    if m and st is not None: out.append((st, float(m.group(1)))); st = None
open("full_sil.tsv", "w").write("".join(f"{a:.3f} {b:.3f}\n" for a, b in out))
print(len(out), "pauses -> full_sil.tsv")
