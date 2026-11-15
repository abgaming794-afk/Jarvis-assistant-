import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import json, subprocess, numpy as np
SR = 48000; FPS = 60
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", PROJ + "voice/full_vo.mp3", "-ac", "1", "-ar", str(SR),
                      "-af", "highpass=f=180,lowpass=f=3200", "-f", "f32le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32)
hop = SR // FPS
n = len(a) // hop
rms = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-7
db = 20 * np.log10(rms)
lo, hi = np.percentile(db, 30), np.percentile(db, 97)
lvl = np.clip((db - (lo + 4)) / (hi - lo - 4), 0, 1)
mouth = np.zeros(n); o = 0
for i in range(n):
    target = lvl[i] if lvl[i] > 0.08 else 0
    o = o * 0.55 + target * 0.45 if target > o else o * 0.45 + target * 0.55   # quick close on pauses
    mouth[i] = min(1, o * 1.15)
SEG = {
  "H1": dict(t0=41.6, t1=53.9, cam=[["wide", "medium", 41.6, 42.5]],
        g=[("wave", 41.9, 43.6, "R"), ("palms", 46.3, 48.6, ""), ("pointdown", 49.7, 51.0, "R"), ("lean", 51.6, 53.4, "")]),
  "H2": dict(t0=282.1, t1=291.7, cam=[["medium", "close", 282.1, 283.4]],
        g=[("lean", 282.3, 283.6, ""), ("palms", 284.4, 286.4, ""), ("pointdown", 287.0, 289.0, "R"), ("nod", 290.0, 291.0, "")]),
  "H3": dict(t0=611.3, t1=619.45, cam=[["close", "medium", 611.3, 612.2]],
        g=[("palms", 611.6, 612.5, ""), ("think", 612.8, 615.2, "L"), ("pointdown", 615.6, 617.3, "R"), ("count1", 617.4, 618.2, "R"), ("count2", 618.3, 619.3, "R")]),
  "H4": dict(t0=627.0, t1=633.6, cam=[["medium", "wide", 627.0, 628.0]],
        g=[("pointdown", 627.3, 629.2, "R"), ("wave", 629.6, 631.5, "R"), ("salute", 631.6, 633.3, "R")]),
}
out = {}
for k, s in SEG.items():
    frames = []
    for f in range(int(round(s["t0"] * FPS)), int(round(s["t1"] * FPS))):
        t = f / FPS
        cf, ct, c0, c1 = s["cam"][0]
        frames.append({"f": f, "t": t, "mouth": round(float(mouth[min(f, n - 1)]), 3),
                       "gestures": [{"type": g[0], "t0": g[1], "t1": g[2], "side": g[3]} for g in s["g"]],
                       "camFrom": cf, "camTo": ct, "camK": max(0, min(1, (t - c0) / max(1e-3, c1 - c0)))})
    out[k] = frames
json.dump(out, open("host_frames.json", "w"))
print({k: len(v) for k, v in out.items()})
