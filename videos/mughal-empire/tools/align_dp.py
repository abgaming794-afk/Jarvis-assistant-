"""Offline cut finder: choose len(ids)-1 cut points among silences so each line's length matches its
character count (DP), preferring longer gaps. usage: python3 tools/align_dp.py <batch.wav> <batch.json> [--apply]"""
import json, os, re, subprocess, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wav, ids = sys.argv[1], json.load(open(sys.argv[2]))
beats = {b["id"]: b for b in json.load(open(P + "/story.json", encoding="utf-8"))["beats"]}
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav], capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "silencedetect=n=-34dB:d=0.1", "-f", "null", "-"], capture_output=True, text=True).stderr
sil = list(zip(map(float, re.findall(r"silence_start: ([\d.]+)", log)), map(float, re.findall(r"silence_end: ([\d.]+)", log))))
lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
cand = [((a + b) / 2, b - a) for a, b in sil if a > 0.05 and b < dur - 0.05]
w = lambda t: len(re.sub(r"[\s.,…—?!-]", "", t)) + 3 * len(re.findall(r"[.,…—?!]", t))   # chars + pause weight
W = [w(beats[i]["text"]) for i in ids]; rate = (dur - lead) / sum(W)
n, m = len(ids), len(cand)
INF = 1e18
# dp[k][j]: best cost with line k ending at candidate j
def seg_cost(t0, t1, k):
    exp = W[k] * rate; got = t1 - t0
    return ((got - exp) / exp) ** 2
dp = [[INF] * m for _ in range(n)]; bk = [[-1] * m for _ in range(n)]
for j in range(m):
    dp[0][j] = seg_cost(lead, cand[j][0], 0) - 0.6 * min(cand[j][1], 1.5)
for k in range(1, n - 1):
    for j in range(m):
        for i in range(j):
            if dp[k - 1][i] >= INF: continue
            c = dp[k - 1][i] + seg_cost(cand[i][0], cand[j][0], k) - 0.6 * min(cand[j][1], 1.5)
            if c < dp[k][j]: dp[k][j], bk[k][j] = c, i
best, bj = INF, -1
for j in range(m):
    if dp[n - 2][j] < INF:
        c = dp[n - 2][j] + seg_cost(cand[j][0], dur, n - 1)
        if c < best: best, bj = c, j
cuts = []; k, j = n - 2, bj
while k >= 0: cuts.append(cand[j][0]); j = bk[k][j]; k -= 1
cuts = cuts[::-1]
edges = [0.0] + cuts + [dur]
for i, b in enumerate(ids):
    print(f"{b:5s} {edges[i]:6.2f}-{edges[i+1]:6.2f}  got {edges[i+1]-edges[i]:4.1f}s  exp {W[i]*rate:4.1f}s  {beats[b]['text'][:40]}")
print("CUTS", " ".join(f"{c:.2f}" for c in cuts))
if "--apply" in sys.argv:
    subprocess.run([sys.executable, P + "/tools/recut.py", wav, sys.argv[2]] + [f"{c:.3f}" for c in cuts], check=True, capture_output=True)
    print("applied")
