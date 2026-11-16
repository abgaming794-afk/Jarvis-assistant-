"""Align full VO to script sentences: pauses (candidates) + syllable-nuclei counting (DP).
Run inside <project>/voice/ with full_vo.mp3 and full_sil.tsv (make it with silences.py). Add new numbers to NUM
(spoken Hinglish form) so syllable counts stay right. Output: full_timing.json -> copy to full_units.json."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import re, json, subprocess, numpy as np

SR = 16000
TXT = open(PROJ + "script/FULL_VO_CLEAN.txt").read()

# ---- units: sentences / clauses ending in . ? ! : (keep quotes together)
raw = [p.strip() for p in TXT.split("\n") if p.strip()]
units = []
for para in raw:
    parts = re.split(r'(?<=[\.\?\!:…])\s+(?=[A-Z0-9"“])', para)
    units += [p.strip() for p in parts if p.strip()]

NUM = {"32": "battees", "87": "sattaasi", "2300": "teis sau", "34": "chauntees", "50": "pachaas", "1690": "solah sau nabbe", "1937": "unnees sau saintees", "1961": "unnees sau iksath", "2002": "two thousand two", "2021": "two thousand twenty one", "2022": "two thousand twenty two",
       "2023": "two thousand twenty three", "2024": "two thousand twenty four", "2025": "two thousand twenty five",
       "2026": "two thousand twenty six", "2026-27": "two thousand twenty six twenty seven", "1.75": "one point seven five",
       "148": "one forty eight", "620": "six sau bees", "170": "ek sau sattar", "40": "chaalees", "60": "saath", "70": "sattar",
       "90": "nabbe", "65": "painsath", "21": "ikkees", "18": "atthaarah", "28": "atthaais", "3": "teen", "4": "chaar", "20": "bees",
       "25": "pachchees", "1": "one", "2": "two", "5": "paanch", "S-400": "S four hundred", "2nd": "second", "1534": "pandrah sau chauntees", "1661": "solah sau iksath", "II": "the second", "1668": "solah sau atthaasath", "10": "das", "1845": "atthaarah sau paintaalees", "1995": "unnees sau pachaanave"}
def spoken(u):
    w = re.findall(r"[A-Za-z0-9\.\-]+", u)
    out = []
    for x in w:
        x2 = x.strip(".-")
        out.append(NUM.get(x2, x2))
    return " ".join(out)
def syl(word):
    word = word.lower()
    g = re.findall(r"[aeiouy]+", word)
    n = len(g)
    if word.endswith("e") and n > 1 and not word.endswith(("ee", "ie", "ye")): n -= 1
    return max(1, n)
T = [sum(syl(w) for w in spoken(u).split()) for u in units]

# ---- audio: envelope + syllable nuclei
raw_a = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "full_vo.mp3", "-ac", "1", "-ar", str(SR), "-af", "highpass=f=250,lowpass=f=3500",
                        "-f", "f32le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw_a, np.float32)
hop = 160  # 10 ms
env = np.sqrt(np.convolve(a ** 2, np.ones(400) / 400, mode="same"))[::hop]
k = np.hanning(9); k /= k.sum(); env = np.convolve(env, k, mode="same")
db = 20 * np.log10(env + 1e-6)
thr = np.percentile(db, 35) + 6
peaks = []
for i in range(2, len(db) - 2):
    if db[i] > thr and db[i] >= db[i - 1] and db[i] > db[i + 1]:
        lo = min(db[max(0, i - 12):i].min(), db[i + 1:i + 13].min())
        if db[i] - lo > 2.5 and (not peaks or i - peaks[-1] > 9):
            peaks.append(i)
pk = np.array(peaks) / 100.0
DUR = len(a) / SR
sil = [tuple(map(float, l.split())) for l in open("full_sil.tsv")]
s_start = sil[0][1] if sil[0][0] < 0.05 else 0.0
s_end = sil[-1][0] if sil[-1][1] > DUR - 0.05 else DUR
cand = [((x + y) / 2, y - x, x, y) for x, y in sil if s_start + 0.05 < x and y < s_end - 0.05]
C = [c[0] for c in cand]
def npk(t0, t1): return int(((pk >= t0) & (pk < t1)).sum())
rate = npk(s_start, s_end) / sum(T)
print(f"units={len(units)} cands={len(C)} peaks={len(pk)} text_syl={sum(T)} rate={rate:.3f}")

# ---- DP: boundary after unit i -> candidate j
U, N = len(units), len(C)
INF = 1e18
def cost(t0, t1, i, j=None):
    A_ = npk(t0, t1); e = rate * T[i]
    c = (A_ - e) ** 2 / (e + 3)
    if j is not None: c -= 1.2 * min(cand[j][1], 0.8)
    return c
dp = np.full((U - 1, N), INF); bk = np.full((U - 1, N), -1, int)
for j in range(N): dp[0, j] = cost(s_start, C[j], 0, j)
for i in range(1, U - 1):
    best = INF; arg = -1
    for j in range(N):
        # incremental: dp[i][j] = min_{q<j} dp[i-1][q] + cost(C[q], C[j], i, j); restrict q to window for speed
        lo = max(0, j - 14)
        vals = [(dp[i - 1, q] + cost(C[q], C[j], i, j), q) for q in range(lo, j) if dp[i - 1, q] < INF]
        if vals:
            v, q = min(vals); dp[i, j] = v; bk[i, j] = q
end = [dp[U - 2, j] + cost(C[j], s_end, U - 1) for j in range(N)]
j = int(np.argmin(end)); idx = [0] * (U - 1)
for i in range(U - 2, -1, -1): idx[i] = j; j = bk[i, j]
bounds = [s_start] + [C[q] for q in idx] + [s_end]
# speech start/end per unit = after the pause / before the next pause
out = []
for i, u in enumerate(units):
    st = s_start if i == 0 else cand[idx[i - 1]][3]
    en = s_end if i == U - 1 else cand[idx[i]][2]
    A_ = npk(st, en)
    out.append({"i": i, "text": u, "start": round(st, 2), "end": round(en, 2), "syl_text": T[i], "syl_audio": A_,
                "ratio": round(A_ / (rate * T[i]), 2)})
json.dump({"duration": round(DUR, 3), "units": out}, open("full_timing.json", "w"), indent=1, ensure_ascii=False)
for o in out:
    flag = " <<" if o["ratio"] < 0.6 or o["ratio"] > 1.5 else ""
    print(f'{o["i"]:3d} {o["start"]:7.2f}-{o["end"]:7.2f} r={o["ratio"]:.2f}{flag}  {o["text"][:70]}')
