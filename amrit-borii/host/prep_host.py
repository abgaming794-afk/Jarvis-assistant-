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
  "H1": dict(t0=44.55, t1=55.85, cam=[["wide", "medium", 44.55, 45.4]],
        g=[("wave", 44.9, 46.4, "R"), ("palms", 47.9, 49.7, ""), ("pointdown", 51.4, 53.5, "R"), ("lean", 53.6, 55.7, ""), ("nod", 54.9, 55.6, "")]),
  "H2": dict(t0=262.35, t1=271.65, cam=[["medium", "medium", 262.35, 262.4]],
        g=[("palms", 262.6, 263.9, ""), ("count1", 263.95, 265.05, "R"), ("count2", 265.15, 266.6, "R"), ("shrug", 267.3, 269.7, ""), ("pointdown", 270.35, 271.5, "R")]),
  "H3": dict(t0=512.5, t1=524.2, cam=[["close", "medium", 512.5, 513.3]],
        g=[("pointdown", 512.8, 515.4, "R"), ("think", 516.9, 519.7, "L"), ("wave", 520.1, 521.7, "R"), ("salute", 521.8, 523.6, "R")]),
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
