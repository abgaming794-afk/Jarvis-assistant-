"""Mix for 'Arab Khilafat India': VO (with silent chapter gaps) + original synth music bed + SFX (half loudness).
Reads audio/timeline.json and audio/full_sfx.json written by `kh.py timeline` / `kh.py sfx`.
usage: python mix_kh.py [end_seconds_video]   -> audio/full_mix.wav (48 kHz stereo)"""
import os, sys, json, subprocess, wave, numpy as np
PROJ = os.path.join(os.environ.get("AB_ROOT", "/home/user/amrit-borii/"), os.environ.get("AB_PROJECT", "khilafat-india"), "")
SR = 48000
TL = json.load(open(PROJ + "audio/timeline.json"))
GAPS, G = TL["gaps"], TL["ch_gap"]
def vt(t, strict=True): return t + G * sum(1 for P in GAPS if (P < t if strict else P <= t))
def load(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
vo = load(PROJ + "voice/full_vo.mp3")
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else vt(len(vo) / SR) + 4.0
n = int(DUR * SR); L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
def put(sig, t, db, pan=0.0):
    i = int(t * SR)
    if i >= n or i < 0: return
    e = min(n, i + len(sig)); g = 10 ** (db / 20)
    L[i:e] += sig[:e - i] * g * (1 - max(0, pan)); R[i:e] += sig[:e - i] * g * (1 + min(0, pan))
edges = [0.0] + sorted(GAPS) + [len(vo) / SR]
for k in range(len(edges) - 1):
    a_, b_ = int(edges[k] * SR), int(edges[k + 1] * SR); put(vo[a_:b_], edges[k] + G * k, 0.0)
# SFX: storyboard names -> generated files; user asked for half loudness (-6 dB)
ALIAS = {"hit": "stamp", "build": "drag", "boom_low": "boom", "paper": "whoosh_long", "lock": "ding", "wind": "whoosh_long",
         "count": "grow", "scratch": "glitch", "whoosh": "whoosh_long"}
cache = {}
for name, t, g in json.load(open(PROJ + "audio/full_sfx.json")):
    f = ALIAS.get(name, name)
    if f not in cache: cache[f] = load(PROJ + f"audio/sfx/{f}.wav")
    put(cache[f], t, g - 6)
for P in GAPS:                                   # chapter card: whoosh + stamp in the silent gap
    for f, dt, g in (("whoosh_long", vt(P, False) - G, -20), ("stamp", vt(P, False) - G + 0.55, -18)):
        if f not in cache: cache[f] = load(PROJ + f"audio/sfx/{f}.wav")
        put(cache[f], dt, g - 6)
# ---- original music bed: slow minor progression (Dm - Bb - F - A), pads + low drone + soft pulse
tt = np.arange(n) / SR
def note(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[50, 53, 57], [46, 50, 53], [41, 45, 48], [45, 49, 52]]
bar = 4.0; mus = np.zeros(n, np.float32)
for ci in range(int(DUR / bar) + 1):
    t0 = ci * bar; i0 = int(t0 * SR); i1 = min(n, int((t0 + bar + 1.0) * SR))
    if i0 >= n: break
    st = tt[i0:i1] - t0
    env = np.clip(st / 1.2, 0, 1) * np.clip((bar + 1.0 - st) / 1.2, 0, 1)
    ch = chords[ci % 4]; s = np.zeros(i1 - i0)
    for m in ch:
        f = note(m + 12)
        s += 0.22 * np.sin(2 * np.pi * f * st) + 0.07 * np.sin(2 * np.pi * 2 * f * st + 0.3) + 0.05 * np.sin(2 * np.pi * f * 1.004 * st)
    s += 0.35 * np.sin(2 * np.pi * note(ch[0] - 12) * st)
    mus[i0:i1] += (s * env).astype(np.float32)
beat = 60 / 72
for k in range(int(DUR / beat)):
    i0 = int(k * beat * SR); ln = int(0.18 * SR)
    if i0 + ln >= n: break
    e = np.exp(-np.linspace(0, 8, ln)); mus[i0:i0 + ln] += (0.25 * np.sin(2 * np.pi * 52 * np.linspace(0, 0.18, ln)) * e).astype(np.float32)
mus /= np.abs(mus).max() + 1e-9
gain = np.full(n, -27.0)
gain[:int(0.8 * SR)] = -20
for P in GAPS: gain[int((vt(P, False) - G) * SR):int((vt(P, False) + 0.3) * SR)] = -17
for a, b in TL["hosts"]: gain[int(vt(a) * SR):int(vt(b, False) * SR)] = -25
end_vo = vt(TL["vo_end"], False); gain[int(end_vo * SR):] = -16
k = int(0.4 * SR); cs = np.concatenate([[0.0], np.cumsum(gain)]); lo = np.clip(np.arange(n) - k // 2, 0, n); hi = np.clip(np.arange(n) + k // 2, 0, n)
gk = (cs[hi] - cs[lo]) / np.maximum(1, hi - lo)          # moving average (fast)
mus *= (10 ** (gk / 20)).astype(np.float32)
mus *= np.clip((DUR - tt) / 1.5, 0, 1).astype(np.float32)
L += mus; R += mus * 0.97
peak = max(np.abs(L).max(), np.abs(R).max()); g = 0.89 / peak if peak > 0.89 else 1.0
stt = np.stack([L * g, R * g], 1)
with wave.open(PROJ + "audio/full_mix.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((stt.clip(-1, 1) * 32767).astype(np.int16).tobytes())
print("mix", round(DUR, 2), "s, peak", round(float(peak), 3))
