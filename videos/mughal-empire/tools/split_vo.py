"""Split one continuous recording into audio/own/<beat id>.wav using silence gaps.
usage: python3 tools/split_vo.py <recording> [min_silence_s=0.9] [noise_db=-38]"""
import json, os, re, subprocess, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]; gap = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
db = sys.argv[3] if len(sys.argv) > 3 else "-38"
ids = [b["id"] for b in json.load(open(P + "/story.json", encoding="utf-8"))["beats"]]
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", f"silencedetect=n={db}dB:d={gap}", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", log).groups()[2]) + 60 * int(re.search(r"Duration: (\d+):(\d+)", log).group(2)) + 3600 * int(re.search(r"Duration: (\d+)", log).group(1))
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
# speech segments = gaps between silences
segs, t = [], 0.0
for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
    if s - t > 0.25: segs.append((t, s))
    t = e
if dur - t > 0.25: segs.append((t, dur))
print(f"found {len(segs)} speech segments for {len(ids)} beats")
if len(segs) != len(ids):
    print("COUNT MISMATCH - adjust min_silence (arg 2) or noise level (arg 3)"); 
    for i, (a, b) in enumerate(segs): print(f"  {i+1:2d} {a:7.2f}-{b:7.2f} ({b-a:.1f}s)")
    sys.exit(1)
os.makedirs(P + "/audio/own", exist_ok=True)
for bid, (a, b) in zip(ids, segs):
    a, b = max(0, a - 0.08), min(dur, b + 0.15)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
                    "-af", "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "1",
                    f"{P}/audio/own/{bid}.wav"], check=True)
    print(bid, f"{b-a:.1f}s")
