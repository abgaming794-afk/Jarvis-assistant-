"""Placeholder timing (~3 words/s, 0.3 s pause between units) until the real VO arrives."""
import re, json
TXT = open("../script/FULL_VO_CLEAN.txt").read()
units = []
for para in [p.strip() for p in TXT.split("\n") if p.strip()]:
    units += [p.strip() for p in re.split(r'(?<=[\.\?\!:…])\s+(?=[A-Z0-9"“])', para) if p.strip()]
t = 0.3; out = []; sil = []
for i, u in enumerate(units):
    d = max(0.7, len(u.split()) / 3.0 + 0.15 * u.count(","))
    out.append({"i": i, "text": u, "start": round(t, 2), "end": round(t + d, 2)}); t += d
    sil.append((t, t + 0.3)); t += 0.3
json.dump({"duration": round(t, 3), "units": out}, open("full_units.json", "w"), indent=1)
open("full_sil.tsv", "w").write("".join(f"{a:.3f} {b:.3f}\n" for a, b in sil))
print("placeholder", round(t, 2), "s,", len(units), "units")
