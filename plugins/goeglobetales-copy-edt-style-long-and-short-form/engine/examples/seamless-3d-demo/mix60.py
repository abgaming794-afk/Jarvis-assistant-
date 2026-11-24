"""Audio for the 1-minute demo: VO slice (Khilafat VO 397.55-456.4 s) + code-made SFX + soft minor music bed.
usage: python3 mix60.py   (reads sfx60.json from demo60.py sfx)  -> mix60.wav (48 kHz stereo, -14 LUFS after loudnorm)
All SFX are synthesised here (no samples, no licences)."""
import os, json, subprocess, wave
import numpy as np
from scipy.signal import lfilter, butter
HERE = os.path.dirname(os.path.abspath(__file__))
KHP = os.environ.get("KH_PROJ", "/home/user/Jarvis-assistant-/amrit-borii/khilafat-india/")
SR = 48000; RNG = np.random.default_rng(11)
import sys
JN = sys.argv[1] if len(sys.argv) > 1 else "sfx60.json"; OUTN = sys.argv[2] if len(sys.argv) > 2 else "mix60.wav"
J = json.load(open(os.path.join(HERE, JN))); END, T0, VO_END = J["end"], J["t0"], J["vo_end"]
n = int(END * SR); L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
tt = lambda s: np.arange(int(s * SR)) / SR
def nz(s): return RNG.uniform(-1, 1, int(s * SR))
def bp(x, lo, hi): b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
def lp(x, f): b, a = butter(2, f / (SR / 2)); return lfilter(b, a, x)
def hp(x, f): b, a = butter(2, f / (SR / 2), "high"); return lfilter(b, a, x)
def norm(x, p=0.9): return (x / (np.abs(x).max() + 1e-9) * p).astype(np.float32)

# ---------------------------------------------------------------- SFX
def whoosh(s=0.9):
    t = tt(s); x = nz(s); out = np.zeros_like(x)
    for i, (lo, hi) in enumerate(((300, 900), (700, 2000), (1500, 4000))):
        env = np.sin(np.pi * np.clip(t / s - i * 0.08, 0, 1)) ** 2; out += bp(x, lo, hi) * env
    return norm(out, 0.8)
def swish(): t = tt(0.45); return norm(bp(nz(0.45), 2000, 7000) * np.sin(np.pi * t / 0.45) ** 3, 0.7)
def pop():
    t = tt(0.16); f = 1100 * np.exp(-t * 22) + 260
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28), 0.8)
def pin():
    t = tt(0.35); click = hp(nz(0.35), 3000) * np.exp(-t * 120)
    tone = np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 14) * 0.5 + np.sin(2 * np.pi * 2640 * t) * np.exp(-t * 18) * 0.25
    return norm(click * 0.6 + tone, 0.75)
def chime():
    t = tt(1.6); y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((987.8, 1, 2.5), (1480, 0.5, 3.2), (1975.5, 0.3, 4.0), (2960, 0.15, 5)))
    return norm(y * np.clip(t / 0.004, 0, 1), 0.6)
def tick():                                           # timeline ratchet: 4 quick clicks
    one = np.concatenate([hp(nz(0.03), 2500) * np.exp(-tt(0.03) * 120), np.zeros(int(0.07 * SR))])
    return norm(np.concatenate([one] * 4), 0.55)
def paper():
    s = 0.7; t = tt(s); x = np.zeros(len(t))
    for _ in range(9):
        a = RNG.uniform(0, s - 0.08); ln = int(RNG.uniform(0.03, 0.09) * SR); i = int(a * SR)
        x[i:i + ln] += bp(nz(ln / SR), 1500, 6500) * np.hanning(ln) * RNG.uniform(0.4, 1)
    return norm(x + bp(nz(s), 800, 3000) * 0.15 * np.sin(np.pi * t / s), 0.7)
def stamp():
    t = tt(0.55); thud = np.sin(2 * np.pi * (120 * np.exp(-t * 10) + 48) * t) * np.exp(-t * 11)
    slap = bp(nz(0.55), 400, 3500) * np.exp(-t * 45)
    return norm(np.tanh((thud * 1.4 + slap) * 2.2), 0.95)
def marker():
    t = tt(0.8); f = 2300 + 250 * np.sin(2 * np.pi * 9 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + bp(nz(0.8), 3000, 6000) * 0.5
    return norm(y * np.sin(np.pi * t / 0.8) ** 0.7, 0.45)
def drum():
    t = tt(0.4); return norm(np.sin(2 * np.pi * (95 * np.exp(-t * 7) + 60) * t) * np.exp(-t * 9) + lp(nz(0.4), 900) * np.exp(-t * 30) * 0.4, 0.8)
def drum_big():
    t = tt(2.2); body = np.sin(2 * np.pi * (70 * np.exp(-t * 3) + 42) * t) * np.exp(-t * 2.4)
    skin = lp(nz(2.2), 1200) * np.exp(-t * 14) * 0.6; rev = lp(nz(2.2), 500) * np.exp(-t * 1.6) * 0.12
    return norm(np.tanh((body + skin + rev) * 1.8), 0.95)
def boom():
    t = tt(1.8); f = 62 * np.exp(-t * 2.0) + 34
    return norm(np.tanh((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) + lp(nz(1.8), 300) * np.exp(-t * 6) * 0.5) * 2), 0.95)
def riser():
    t = tt(1.3); f = 180 * 2 ** (t / 1.3 * 3)
    return norm((np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + hp(nz(1.3), 1500) * (t / 1.3)) * (t / 1.3) ** 2, 0.7)
def firework():
    s = 1.4; t = tt(s); x = np.zeros(len(t))
    x[:int(0.25 * SR)] += np.sin(2 * np.pi * (300 + 900 * tt(0.25) / 0.25) * tt(0.25)) * 0.2 * np.hanning(int(0.25 * SR))   # whistle up
    i0 = int(0.28 * SR); bang = int(0.3 * SR); x[i0:i0 + bang] += lp(nz(0.3), 2500) * np.exp(-tt(0.3) * 18) * 1.2
    for _ in range(70):                                   # crackle
        i = int(RNG.uniform(0.35, s - 0.02) * SR); ln = int(0.006 * SR); x[i:i + ln] += hp(nz(0.006), 3000) * RNG.uniform(0.2, 0.7)
    return norm(x, 0.8)
def battle(s=5.0):
    t = tt(s); rumble = lp(nz(s), 140) * 1.4; roar = bp(nz(s), 300, 1500) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t) ** 2) * 0.6
    x = rumble + roar
    for _ in range(26):                                   # sword clangs
        i = int(RNG.uniform(0.2, s - 0.4) * SR); ct = tt(0.35); f = RNG.uniform(1800, 3200)
        x[i:i + len(ct)] += (np.sin(2 * np.pi * f * ct) + 0.6 * np.sin(2 * np.pi * f * 1.51 * ct)) * np.exp(-ct * 16) * RNG.uniform(0.25, 0.6)
    for _ in range(8):                                    # war drums
        i = int(RNG.uniform(0.1, s - 0.5) * SR); d = drum(); x[i:i + len(d)] += d * 0.7
    return norm(x * np.clip(t / 0.6, 0, 1) * np.clip((s - t) / 1.2, 0, 1), 0.85)
LIB = dict(whoosh=whoosh(), swish=swish(), pop=pop(), pin=pin(), chime=chime(), tick=tick(), paper=paper(), stamp=stamp(),
           marker=marker(), drum=drum(), drum_big=drum_big(), boom=boom(), riser=riser(), firework=firework(), battle=battle())
import sys as _sys
_sys.path.insert(0, os.path.join(os.environ.get("UTA_PLUGIN", os.path.join(HERE, "..", "..", "..")), "engine", "audio"))
import battle_sfx
LIB.update(battle_sfx.build(SR))
UD = os.path.join(HERE, "sfx_user")                      # user-supplied SFX override the code-made ones by name
if os.path.isdir(UD):
    for fn in os.listdir(UD):
        nm, ext = os.path.splitext(fn)
        if ext.lower() in (".wav", ".mp3", ".ogg", ".m4a", ".flac"):
            raw_ = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(UD, fn), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
            a_ = np.frombuffer(raw_, np.float32).copy(); LIB[nm] = (a_ / (np.abs(a_).max() + 1e-9) * 0.9).astype(np.float32); print("user sfx:", nm)
os.makedirs(os.path.join(HERE, "sfx"), exist_ok=True)
for k, v in LIB.items():
    with wave.open(os.path.join(HERE, "sfx", k + ".wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((v * 32767).astype(np.int16).tobytes())

def put(sig, t, db, pan=0.0):
    i = int(t * SR)
    if i >= n or i + len(sig) <= 0: return
    if i < 0: sig = sig[-i:]; i = 0
    e = min(n, i + len(sig)); g = 10 ** (db / 20)
    L[i:e] += sig[:e - i] * g * (1 - max(0, pan)); R[i:e] += sig[:e - i] * g * (1 + min(0, pan))

# ---------------------------------------------------------------- VO slice
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(T0), "-t", str(VO_END - T0 + 0.3), "-i", KHP + "voice/full_vo.mp3",
                      "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
vo = np.frombuffer(raw, np.float32).copy(); fade = int(0.04 * SR); vo[:fade] *= np.linspace(0, 1, fade); vo[-fade * 4:] *= np.linspace(1, 0, fade * 4)
put(vo, 0.0, 0.0)
# ---------------------------------------------------------------- SFX (channel rule: half loudness under VO)
SL = np.zeros(n, np.float32); SRR = np.zeros(n, np.float32)
def put_sfx(sig, t, db, pan):
    i = int(t * SR)
    if i >= n or i + len(sig) <= 0: return
    if i < 0: sig = sig[-i:]; i = 0
    e = min(n, i + len(sig)); g = 10 ** (db / 20)
    SL[i:e] += sig[:e - i] * g * (1 - max(0, pan)); SRR[i:e] += sig[:e - i] * g * (1 + min(0, pan))
for name, t, g in J["events"]:
    put_sfx(LIB[name], t, g - 4, RNG.uniform(-0.3, 0.3))
ve = np.abs(L).astype(np.float64); k_ = int(0.25 * SR); cs = np.concatenate([[0.0], np.cumsum(ve)])
lo = np.clip(np.arange(n) - k_ // 2, 0, n); hi = np.clip(np.arange(n) + k_ // 2, 0, n); vel = (cs[hi] - cs[lo]) / np.maximum(1, hi - lo)
duck = 10 ** (-6 * np.clip(vel / (np.percentile(vel, 90) + 1e-9), 0, 1) / 20)          # up to -6 dB while the VO speaks
L += (SL * duck).astype(np.float32); R += (SRR * duck).astype(np.float32)
# ---------------------------------------------------------------- music bed: slow minor pads (Dm - Bb - F - A) + soft pulse
T = np.arange(n) / SR; mus = np.zeros(n)
note = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [[50, 53, 57], [46, 50, 53], [41, 45, 48], [45, 49, 52]]; bar = 4.0
for ci in range(int(END / bar) + 1):
    t0 = ci * bar; i0 = int(t0 * SR); i1 = min(n, int((t0 + bar + 1.0) * SR))
    if i0 >= n: break
    st = T[i0:i1] - t0; env = np.clip(st / 1.2, 0, 1) * np.clip((bar + 1.0 - st) / 1.2, 0, 1); s = np.zeros(i1 - i0)
    for m in chords[ci % 4]:
        f = note(m + 12); s += 0.22 * np.sin(2 * np.pi * f * st) + 0.06 * np.sin(2 * np.pi * 2 * f * st + 0.3) + 0.05 * np.sin(2 * np.pi * f * 1.004 * st)
    s += 0.35 * np.sin(2 * np.pi * note(chords[ci % 4][0] - 12) * st); mus[i0:i1] += s * env
beat = 60 / 76
for k in range(int(END / beat)):
    i0 = int(k * beat * SR); ln = int(0.18 * SR)
    if i0 + ln >= n: break
    mus[i0:i0 + ln] += 0.22 * np.sin(2 * np.pi * 52 * np.arange(ln) / SR) * np.exp(-np.linspace(0, 8, ln))
mus = mus / (np.abs(mus).max() + 1e-9) * 10 ** (-25 / 20) * np.clip(T / 1.0, 0, 1) * np.clip((END - T) / 1.5, 0, 1)
L += mus.astype(np.float32); R += (mus * 0.97).astype(np.float32)
pk = max(np.abs(L).max(), np.abs(R).max()); g = 0.89 / pk if pk > 0.89 else 1.0
tmp = os.path.join(HERE, "mix60_raw.wav")
with wave.open(tmp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([L * g, R * g], 1).clip(-1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", os.path.join(HERE, OUTN)], check=True)
print("mix ok", round(END, 2), "s, events", len(J["events"]))
