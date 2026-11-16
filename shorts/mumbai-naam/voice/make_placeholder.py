"""Placeholder timing from the script (~3.0 words/s after the 1.2x speed-up) until the real VO arrives."""
import re, json
TXT = open("../script/FULL_VO_CLEAN.txt").read()
units = []
for para in [p.strip() for p in TXT.split("\n") if p.strip()]:
    units += [p.strip() for p in re.split(r'(?<=[\.\?\!:…])\s+(?=[A-Z0-9"“])', para) if p.strip()]
t = 0.25; out = []; sil = [(0.0, 0.25)]
for i, u in enumerate(units):
    d = max(0.7, len(u.split()) / 3.0)
    out.append({"i": i, "text": u, "start": round(t, 2), "end": round(t + d, 2)})
    gap = 0.32
    sil.append((round(t + d, 2), round(t + d + gap, 2))); t += d + gap
json.dump({"duration": round(t, 3), "units": out}, open("full_units.json", "w"), indent=1, ensure_ascii=False)
open("full_sil.tsv", "w").write("\n".join(f"{a} {b}" for a, b in sil) + "\n")
for o in out: print(o["i"], o["start"], o["end"], o["text"])
print("dur", round(t, 2))
