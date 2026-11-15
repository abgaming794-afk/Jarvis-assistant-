"""Placeholder timing until the real VO arrives: same unit split as align_full.py, duration from syllables.
Writes full_units.json + full_sil.tsv (fake pauses). Replace by running align_full.py on the real MP3."""
import re, json, os
PROJ = os.path.join(os.environ.get("AB_ROOT", "/home/user/amrit-borii/"), os.environ.get("AB_PROJECT", "khilafat-india"), "")
TXT = open(PROJ + "script/FULL_VO_CLEAN.txt").read()
units = []
for para in [p.strip() for p in TXT.split("\n") if p.strip()]:
    units += [p.strip() for p in re.split(r'(?<=[\.\?\!:…])\s+(?=[A-Z0-9"“])', para) if p.strip()]
def syl(w):
    g = re.findall(r"[aeiouy]+", w.lower()); return max(1, len(g))
NUMS = {"632": 7, "661": 7, "711": 6, "636": 7, "644": 7, "79": 4, "75": 4, "712": 6, "715": 6, "18": 3}
t = 0.6; out = []; sil = []
for i, u in enumerate(units):
    n = sum(NUMS.get(w.strip(".,:?"), syl(w)) for w in re.findall(r"[A-Za-z0-9\-]+", u))
    d = n / 5.6 + 0.15
    out.append(dict(i=i, text=u, start=round(t, 2), end=round(t + d, 2)))
    gap = 0.55 if u.endswith(("?", ".", "!")) else 0.3
    sil.append((round(t + d, 2), round(t + d + gap, 2))); t += d + gap
json.dump({"units": out, "placeholder": True}, open(PROJ + "voice/full_units.json", "w"), indent=1, ensure_ascii=False)
open(PROJ + "voice/full_sil.tsv", "w").write("\n".join(f"{a} {b}" for a, b in sil) + "\n")
print(len(out), "units, total", round(t, 1), "s")
for u in out[:24]: print(u["i"], u["start"], u["end"], u["text"][:60])
