"""Short mix: VO + original synth music bed (ducked) + code-made SFX -> 48 kHz stereo WAV."""
import os, sys, json, subprocess, wave, numpy as np
os.environ.setdefault("AB_ORIENT", "vertical")
ROOT = "/home/user/Jarvis-assistant-/shorts/panipat/"
sys.path.insert(0, ROOT + "visuals")
import panipat as N
N.VO_DUR = N.VO_END
SR = 48000; DUR = N.END; n = int(DUR * SR)
ALIAS = dict(click="pop")
SFX_GAIN = 20 * np.log10(0.20)                                   # all SFX at 20% (user)
def make_marker(path, sr=48000, seed=4):
    """real felt-tip marker on paper: two quick strokes of grainy band-passed friction noise + faint squeak."""
    rng = np.random.default_rng(seed); out = []
    for dur, gap in ((0.30, 0.06), (0.26, 0.0)):
        n_ = int(dur * sr); x = rng.normal(0, 1, n_)
        X = np.fft.rfft(x); f = np.fft.rfftfreq(n_, 1 / sr)
        X *= np.exp(-((np.log(f + 1) - np.log(3800)) ** 2) / (2 * 0.45 ** 2))            # 2-7 kHz felt friction
        x = np.fft.irfft(X, n_); x /= np.abs(x).max() + 1e-9
        grain = np.repeat(rng.uniform(0.55, 1.0, n_ // 240 + 1), 240)[:n_]                # paper fibres
        tt_ = np.arange(n_) / sr; env = np.sin(np.pi * np.clip(tt_ / dur, 0, 1)) ** 0.6
        sq = 0.06 * np.sin(2 * np.pi * (1650 + 300 * tt_ / dur) * tt_) * env              # tiny squeak
        out.append((x * grain * env + sq) * 0.8); out.append(np.zeros(int(gap * sr)))
    sig = np.concatenate(out).astype(np.float32)
    import wave as _w
    with _w.open(path, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((sig.clip(-1, 1) * 32767).astype(np.int16).tobytes())
make_marker(ROOT + "audio/sfx/marker.wav")
def load(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
def put(sig, t, db, pan=0.0):
    i = int(t * SR)
    if i >= n or i < 0: return
    e = min(n, i + len(sig)); g = 10 ** (db / 20)
    L[i:e] += sig[:e - i] * g * (1 - max(0, pan)); R[i:e] += sig[:e - i] * g * (1 + min(0, pan))
if os.path.exists(ROOT + "voice/vo.mp3"): put(load(ROOT + "voice/vo.mp3"), 0.0, 0.0)
cache = {}
USER = {os.path.splitext(f)[0]: os.path.join(ROOT, "audio/sfx_user", f) for f in os.listdir(ROOT + "audio/sfx_user")} if os.path.isdir(ROOT + "audio/sfx_user") else {}
for name, t, g in N.sfx_events():
    if name in USER: src = USER[name]                       # battle sounds only from the user's own files
    elif os.path.exists(ROOT + f"audio/sfx/{ALIAS.get(name, name)}.wav"): src = ROOT + f"audio/sfx/{ALIAS.get(name, name)}.wav"
    else: continue
    if name not in cache: cache[name] = load(src)
    put(cache[name], t, g - 8 + SFX_GAIN)   # SFX at half loudness (-6 dB) on user request
# music: Am - F - C - G pads + bass + soft pulse (original synthesis, from the AMRIT BORII engine)
tt = np.arange(n) / SR
def note(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]; bar = 3.2
mus = np.zeros(n, np.float32)
for ci in range(int(DUR / bar) + 1):
    t0 = ci * bar; i0 = int(t0 * SR); i1 = min(n, int((t0 + bar + 1.0) * SR))
    if i0 >= n: break
    st_ = tt[i0:i1] - t0; env = np.clip(st_ / 1.0, 0, 1) * np.clip((bar + 1.0 - st_) / 1.0, 0, 1)
    ch = chords[ci % 4]; s = np.zeros(i1 - i0)
    for m in ch:
        f = note(m); s += 0.22 * np.sin(2 * np.pi * f * st_) + 0.08 * np.sin(2 * np.pi * 2 * f * st_ + 0.3) + 0.05 * np.sin(2 * np.pi * f * 1.003 * st_)
    s += 0.35 * np.sin(2 * np.pi * note(ch[0] - 24) * st_)
    mus[i0:i1] += (s * env).astype(np.float32)
beat = 60 / 92
for k in range(int(DUR / beat)):
    i0 = int(k * beat * SR); ln = int(0.16 * SR)
    if i0 + ln >= n: break
    e = np.exp(-np.linspace(0, 8, ln)); mus[i0:i0 + ln] += (0.3 * np.sin(2 * np.pi * 55 * np.linspace(0, 0.16, ln)) * e).astype(np.float32)
mus /= np.abs(mus).max() + 1e-9
gain = np.full(n, -25.0)
gain[:int(0.4 * SR)] = -18; gain[int(N.VO_DUR * SR):] = -15
k = int(0.4 * SR); gk = np.convolve(gain, np.ones(k) / k, mode="same")
mus *= (10 ** (gk / 20)).astype(np.float32)
mus *= np.clip((DUR - tt) / 1.2, 0, 1).astype(np.float32) * np.clip(tt / 0.3, 0, 1).astype(np.float32)
L += mus; R += mus * 0.97
peak = max(np.abs(L).max(), np.abs(R).max()); g = 0.89 / peak if peak > 0.89 else 1.0
st = np.stack([L * g, R * g], 1)
with wave.open(ROOT + "audio/short_mix.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st.clip(-1, 1) * 32767).astype(np.int16).tobytes())
print("mix done", round(DUR, 2), "s, peak", round(float(peak), 3), len(N.sfx_events()), "sfx")
