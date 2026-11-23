"""Full mix: VO + documentary music bed (synth, original) + SFX. 48 kHz stereo WAV."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import json, subprocess, wave, numpy as np
ROOT = PROJ + ""
SR = 48000; DUR = 535.0; n = int(DUR * SR)
GAPS = [55.85, 104.7, 161.72, 271.55, 370.97]; G = 1.4
def vt(t, strict=True):
    """VO time -> video time (pauses inserted at chapter cards)"""
    return t + G * sum(1 for P in GAPS if (P < t if strict else P <= t))
def load(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
def put(sig, t, db, pan=0.0):
    i = int(t * SR)
    if i >= n or i < 0: return
    e = min(n, i + len(sig)); g = 10 ** (db / 20)
    L[i:e] += sig[:e - i] * g * (1 - max(0, pan)); R[i:e] += sig[:e - i] * g * (1 + min(0, pan))
# voice
vo = load(ROOT + "voice/full_vo_fixed.wav")
edges = [0.0] + GAPS + [len(vo) / SR]
for k in range(len(edges) - 1):
    a_, b_ = int(edges[k] * SR), int(edges[k + 1] * SR)
    put(vo[a_:b_], edges[k] + G * k, 0.0)
# SFX
cache = {}
for name, t, g in json.load(open(ROOT + "audio/full_sfx.json")):
    if name not in cache: cache[name] = load(ROOT + f"audio/sfx/{name}.wav")
    put(cache[name], vt(t), g - 2)
# scene-1 SFX (same as the demo)
TIM = {b["beat"]: b["visual_in"] for b in json.load(open(ROOT + "voice/scene1_full_timing.json"))["beats"]}
EV = json.load(open(ROOT + "voice/scene1_full_timing.json"))["events"]
for name, t, g in [("whoosh_long", 1.1, -16), ("pop", 2.0, -16), ("whoosh_fast", TIM["1.2"], -15), ("pop", TIM["1.2"] + 0.5, -14), ("riser", TIM["1.3"] - 0.1, -18),
                   ("whoosh_fast", TIM["1.4"], -15), ("whoosh_fast", TIM["1.5"] - 0.3, -15), ("pop", TIM["1.5"], -20), ("pop", EV["putin_name"], -20),
                   ("pop", EV["kim_name"], -20), ("drag", TIM["1.8"], -16), ("pop", EV["pez_name"], -16), ("stamp", EV["ek_saath"], -10), ("boom", EV["ek_saath"], -17)]:
    if name not in cache: cache[name] = load(ROOT + f"audio/sfx/{name}.wav")
    put(cache[name], t, g)
# ---- music bed: slow minor progression (Am - F - C - G), pads + soft pulse, original synthesis
tt = np.arange(n) / SR
def note(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]   # Am F C G
bar = 4.0                                                           # seconds per chord
mus = np.zeros(n, np.float32)
for ci in range(int(DUR / bar) + 1):
    t0 = ci * bar; i0 = int(t0 * SR); i1 = min(n, int((t0 + bar + 1.0) * SR))
    if i0 >= n: break
    seg_t = tt[i0:i1] - t0
    env = np.clip(seg_t / 1.2, 0, 1) * np.clip((bar + 1.0 - seg_t) / 1.2, 0, 1)
    ch = chords[ci % 4]; s = np.zeros(i1 - i0)
    for m in ch:
        f = note(m)
        s += 0.22 * np.sin(2 * np.pi * f * seg_t) + 0.08 * np.sin(2 * np.pi * 2 * f * seg_t + 0.3) + 0.05 * np.sin(2 * np.pi * f * 1.003 * seg_t)
    s += 0.35 * np.sin(2 * np.pi * note(ch[0] - 24) * seg_t)          # bass
    mus[i0:i1] += (s * env).astype(np.float32)
# soft pulse (heartbeat-like) at 70 bpm
beat = 60 / 70
for k in range(int(DUR / beat)):
    i0 = int(k * beat * SR); ln = int(0.18 * SR)
    if i0 + ln >= n: break
    e = np.exp(-np.linspace(0, 8, ln)); mus[i0:i0 + ln] += (0.25 * np.sin(2 * np.pi * 55 * np.linspace(0, 0.18, ln)) * e).astype(np.float32)
mus /= np.abs(mus).max() + 1e-9
# loudness automation: under VO -27 dB; louder on chapter cards / host / end card
gain = np.full(n, -27.0)
for a, b, g in [(0, 1.0, -20), (55.85, 58.2, -18), (104.7, 107.9, -18), (161.72, 165.7, -18), (271.55, 275.7, -18), (370.97, 375.2, -18),
                (44.55, 55.85, -25), (262.35, 271.65, -25), (512.5, 524.2, -24), (524.2, 528.0, -16)]:
    gain[int(vt(a) * SR):int(vt(b, False) * SR)] = g
k = int(0.4 * SR); gk = np.convolve(gain, np.ones(k) / k, mode="same")
mus *= (10 ** (gk / 20)).astype(np.float32)
fade = np.clip((DUR - tt) / 1.5, 0, 1); mus *= fade.astype(np.float32)
L += mus; R += mus * 0.97
peak = max(np.abs(L).max(), np.abs(R).max()); g = 0.89 / peak if peak > 0.89 else 1.0
st = np.stack([L * g, R * g], 1)
with wave.open(ROOT + "audio/full_mix.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st.clip(-1, 1) * 32767).astype(np.int16).tobytes())
print("mix done, peak", round(float(peak), 3))
