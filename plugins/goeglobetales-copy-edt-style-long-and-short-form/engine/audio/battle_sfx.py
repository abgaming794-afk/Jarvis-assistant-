"""Code-made battle sound effects (no samples, no licences) - Unexplored Truth by Amrit 1.3.0.

build(SR) -> {name: mono float32 array}. Names used by battle_scenes.py sfx():
  bows/arrows : arrow_release, arrow_whistle, arrow_hit, volley, arrow_hits, javelin
  blades      : sword_clang, sword_scrape, shield_bash, clash_bed (dense melee: clangs + scrapes + bashes + grunts + roar)
  horses      : gallop_few, gallop_many, trot_many, neigh
  elephant    : elephant (trumpet)
  signals     : conch (Indian shankh), horn, nagara (Indian kettle drums), tabl (Arab drums), march_drum, footsteps
  voices      : warcry_in, warcry_ar, warcry_steppe, warcry_frank, warcry_berber (ululation), crowd_panic, groan, echo_shout
  impacts     : body_fly, fall_thud, boulder, rock_hit, ladder, ladder_fall, tent
  atmosphere  : slowmo, heat_drone, wind
War cries are wordless crowd shouts (no religious slogans)."""
import numpy as np
from scipy.signal import lfilter, butter

def build(SR=48000, seed=21):
    R = np.random.default_rng(seed)
    T = lambda s: np.arange(int(s * SR)) / SR
    N = lambda s: R.uniform(-1, 1, int(s * SR))
    def bp(x, lo, hi, o=2): b, a = butter(o, [max(20, lo) / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], "band"); return lfilter(b, a, x)
    def lp(x, f): b, a = butter(2, f / (SR / 2)); return lfilter(b, a, x)
    def hp(x, f): b, a = butter(2, f / (SR / 2), "high"); return lfilter(b, a, x)
    def norm(x, p=0.9): return (x / (np.abs(x).max() + 1e-9) * p).astype(np.float32)
    def place(out, sig, t, g=1.0):
        i = int(t * SR)
        if i < 0: sig = sig[-i:]; i = 0
        if i >= len(out) or len(sig) == 0: return
        e = min(len(out), i + len(sig)); out[i:e] += sig[:e - i] * g
    def env(n, a, r): t = np.arange(n) / SR; return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-t / max(r, 1e-4))
    def karplus(f, s, damp=0.996):
        n = int(s * SR); p = max(2, int(SR / f)); buf = R.uniform(-1, 1, p); out = np.zeros(n)
        for i in range(n): out[i] = buf[i % p]; buf[i % p] = damp * 0.5 * (buf[i % p] + buf[(i + 1) % p])
        return out
    def voice(f0, s, formants, vib=5.0, vib_d=0.02, contour=None, rough=0.0):
        t = T(s); f = f0 * (contour(t / s) if contour else 1.0) * (1 + vib_d * np.sin(2 * np.pi * vib * t + R.uniform(0, 6)))
        ph = np.cumsum(f) / SR; src = 2 * (ph % 1.0) - 1                                  # glottal-ish saw
        if rough: src *= 1 + rough * np.sin(2 * np.pi * 31 * t)
        out = sum(g * bp(src, F * 0.85, F * 1.15) for F, g in formants) + 0.05 * bp(N(s), 300, 3000)
        return out * np.clip(t / 0.12, 0, 1) * np.clip((s - t) / 0.25, 0, 1)
    def crowd(n, s, f_lo, f_hi, formants, contour=None, vib=5, vib_d=0.03, spread=0.5, rough=0.0):
        out = np.zeros(int((s + spread) * SR))
        for _ in range(n): place(out, voice(R.uniform(f_lo, f_hi), s * R.uniform(0.75, 1.0), formants, vib * R.uniform(0.8, 1.3), vib_d, contour, rough), R.uniform(0, spread), R.uniform(0.5, 1.0))
        return out + 0.25 * bp(N(len(out) / SR), 200, 1500) * np.clip(np.arange(len(out)) / SR / 0.3, 0, 1) * np.clip((len(out) / SR - np.arange(len(out)) / SR) / 0.5, 0, 1)
    L = {}
    # ---------------------------------------------------------------- bows and arrows
    L["arrow_release"] = norm(karplus(R.uniform(190, 240), 0.35, 0.993) * env(int(0.35 * SR), 0.001, 0.12) + hp(N(0.35), 3000) * env(int(0.35 * SR), 0.0005, 0.01), 0.8)
    def whistle(s=0.55):
        t = T(s); x = N(s); f = 6500 - 3200 * t / s; out = np.zeros_like(x)
        for i in range(0, len(x), 512):
            seg_ = x[i:i + 1024]; fc = f[min(i, len(f) - 1)]; out[i:i + len(seg_)] += bp(seg_, fc * 0.85, fc * 1.15)[:len(out[i:i + len(seg_)])] * 0.5
        return out * np.sin(np.pi * t / s) ** 2
    L["arrow_whistle"] = norm(whistle(), 0.6)
    def thunk(): t = T(0.18); return np.sin(2 * np.pi * (170 + 60 * np.exp(-t * 40)) * t) * np.exp(-t * 32) + bp(N(0.18), 900, 3200) * np.exp(-t * 70) * 0.8
    L["arrow_hit"] = norm(thunk(), 0.8)
    v = np.zeros(int(2.2 * SR))
    for i in range(16):
        place(v, L["arrow_release"], R.uniform(0, 0.5), 0.35); place(v, whistle(R.uniform(0.45, 0.7)), R.uniform(0.15, 0.8), 0.55)
        place(v, thunk(), R.uniform(0.9, 1.6), 0.45)
    L["volley"] = norm(v, 0.85)
    h = np.zeros(int(0.9 * SR))
    for i in range(9): place(h, thunk(), R.uniform(0, 0.7), R.uniform(0.4, 1.0))
    L["arrow_hits"] = norm(h, 0.8)
    t = T(0.6); jw = bp(N(0.6), 500, 2500) * np.sin(np.pi * np.clip(t / 0.45, 0, 1)) ** 2
    jv = np.zeros(int(0.9 * SR)); place(jv, jw, 0); place(jv, thunk(), 0.5, 0.9); L["javelin"] = norm(jv, 0.8)
    # ---------------------------------------------------------------- blades and shields
    def clang(f0=None, s=1.1):
        f0 = f0 or R.uniform(650, 1050); t = T(s)
        y = sum(a * np.sin(2 * np.pi * f0 * r * t + R.uniform(0, 6)) * np.exp(-t * d) for r, a, d in ((1, 1, 4.5), (2.32, 0.7, 6), (4.25, 0.5, 8), (6.63, 0.35, 11), (9.38, 0.2, 15)))
        return y + hp(N(s), 2500) * np.exp(-t * 90) * 1.5
    L["sword_clang"] = norm(clang(820) + 0.6 * np.concatenate([np.zeros(int(0.07 * SR)), clang(980)])[:int(1.1 * SR)], 0.9)
    def scrape(s=0.45): t = T(s); return bp(N(s), 2800, 7500) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t)) * np.sin(np.pi * t / s)
    L["sword_scrape"] = norm(scrape(), 0.6)
    def bash(): t = T(0.4); return np.sin(2 * np.pi * (95 * np.exp(-t * 6) + 55) * t) * np.exp(-t * 14) + bp(N(0.4), 180, 900) * np.exp(-t * 25) * 0.9
    L["shield_bash"] = norm(bash(), 0.95)
    def grunt(): return voice(R.uniform(95, 140), R.uniform(0.18, 0.32), ((600, 1.0), (1000, 0.6), (2400, 0.2)), contour=lambda x: 1.15 - 0.3 * x, rough=0.4)
    cb = np.zeros(int(3.6 * SR))
    for i in range(26): place(cb, clang(), R.uniform(0, 3.0), R.uniform(0.35, 0.9))
    for i in range(7): place(cb, scrape(R.uniform(0.3, 0.5)), R.uniform(0, 3.1), 0.4)
    for i in range(6): place(cb, bash(), R.uniform(0, 3.1), 0.6)
    for i in range(9): place(cb, grunt(), R.uniform(0, 3.2), 0.5)
    cb += 0.35 * bp(N(3.6), 150, 900) * np.clip(np.arange(len(cb)) / SR / 0.3, 0, 1) * np.clip((3.6 - np.arange(len(cb)) / SR) / 0.6, 0, 1)
    L["clash_bed"] = norm(cb, 0.9)
    # ---------------------------------------------------------------- horses
    def hoof(): t = T(0.12); return np.sin(2 * np.pi * (R.uniform(70, 110) * np.exp(-t * 10) + 45) * t) * np.exp(-t * 38) + bp(N(0.12), 400, 2200) * np.exp(-t * 55) * 0.6
    def gallop(s, horses, period=0.42, pattern=(0, 0.07, 0.17, 0.24)):
        out = np.zeros(int(s * SR))
        for hidx in range(horses):
            per = period * R.uniform(0.9, 1.1); off = R.uniform(0, per); g = R.uniform(0.4, 1.0)
            tt = off
            while tt < s:
                for p in pattern: place(out, hoof(), tt + p * per / 0.42 + R.uniform(-0.01, 0.01), g * R.uniform(0.6, 1.0))
                tt += per
        return out + (0.6 * lp(N(s), 160) * min(1, horses / 6))
    L["gallop_few"] = norm(gallop(3.0, 2), 0.85)
    L["gallop_many"] = norm(gallop(3.2, 10) * np.clip(np.arange(int(3.2 * SR)) / SR / 0.4, 0, 1) * np.clip((3.2 - np.arange(int(3.2 * SR)) / SR) / 0.6, 0, 1), 0.9)
    L["trot_many"] = norm(gallop(3.0, 8, period=0.6, pattern=(0, 0.3)), 0.75)
    def neigh():
        s = 1.25; t = T(s)
        f = np.where(t < 0.18, 520 + 600 * t / 0.18, 1120 - 650 * (t - 0.18) / (s - 0.18)) * (1 + 0.08 * np.sin(2 * np.pi * 17 * t) * (t > 0.18))
        src = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(4 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(6 * np.pi * np.cumsum(f) / SR)
        y = bp(src, 700, 3500) + 0.25 * bp(N(s), 1500, 5000)
        return y * np.clip(t / 0.03, 0, 1) * np.clip((s - t) / 0.4, 0, 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 17 * t))
    L["neigh"] = norm(neigh(), 0.7)
    # ---------------------------------------------------------------- elephant
    s = 1.4; t = T(s); f = np.interp(t, [0, 0.25, 0.9, 1.4], [330, 680, 560, 420])
    src = sum((1 / k) * np.sign(np.sin(2 * np.pi * k * np.cumsum(f) / SR)) for k in (1, 2, 3))
    el = bp(src, 500, 3200) * (1 + 0.35 * np.sin(2 * np.pi * 29 * t)) + 0.3 * bp(N(s), 800, 4000)
    L["elephant"] = norm(el * np.clip(t / 0.06, 0, 1) * np.clip((s - t) / 0.35, 0, 1), 0.85)
    # ---------------------------------------------------------------- signals: conch, horn, drums
    s = 2.2; t = T(s); f = 330 * (1 + 0.015 * np.clip((t - 1.6) / 0.6, 0, 1)) * (1 + 0.004 * np.sin(2 * np.pi * 5 * t))
    ph = np.cumsum(f) / SR; cn = np.sin(2 * np.pi * ph) + 0.45 * np.sin(4 * np.pi * ph) + 0.22 * np.sin(6 * np.pi * ph) + 0.4 * bp(N(s), 300, 1100)
    L["conch"] = norm(cn * np.clip(t / 0.3, 0, 1) * np.clip((s - t) / 0.5, 0, 1), 0.8)
    s = 1.8; t = T(s); f = 220 * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t)); ph = np.cumsum(f) / SR
    hn = sum((0.9 ** k) * np.sin(2 * np.pi * k * ph) for k in range(1, 9)) + 0.15 * bp(N(s), 200, 2000)
    L["horn"] = norm(lp(hn, 2500) * np.clip(t / 0.12, 0, 1) * np.clip((s - t) / 0.4, 0, 1), 0.75)
    def drum(f0, s=0.6, skin=0.5): t = T(s); return np.sin(2 * np.pi * (f0 * np.exp(-t * 4) + f0 * 0.6) * t) * np.exp(-t * 6) + lp(N(s), 1500) * np.exp(-t * 30) * skin
    def rhythm(f0, pat, s, skin=0.5):
        out = np.zeros(int(s * SR))
        for tt, g in pat: place(out, drum(f0 * R.uniform(0.95, 1.05), skin=skin), tt, g)
        return out
    L["nagara"] = norm(rhythm(75, [(0, 1), (0.5, 0.7), (0.75, 0.7), (1.0, 1), (1.5, 0.8), (1.75, 0.6), (2.0, 1)], 2.8, 0.6), 0.9)
    L["tabl"] = norm(rhythm(120, [(0, 1), (0.25, 0.5), (0.5, 0.8), (0.75, 0.5), (1.0, 1), (1.25, 0.5), (1.5, 0.8), (1.75, 0.5), (2.0, 1)], 2.6, 0.8), 0.85)
    L["march_drum"] = norm(rhythm(95, [(i * 0.5, 1.0 if i % 2 == 0 else 0.6) for i in range(9)], 4.6, 0.7), 0.85)
    fs = np.zeros(int(4.0 * SR))
    for i in range(16):
        for k in range(8): place(fs, bp(N(0.09), 300, 2500) * env(int(0.09 * SR), 0.002, 0.03), i * 0.25 + R.uniform(-0.03, 0.03), R.uniform(0.3, 0.8))
    L["footsteps"] = norm(fs, 0.6)
    # ---------------------------------------------------------------- voices: war cries, panic, groans
    A_ = ((750, 1.0), (1200, 0.7), (2600, 0.25)); O_ = ((450, 1.0), (800, 0.6), (2600, 0.15)); E_ = ((400, 1.0), (2000, 0.5), (2800, 0.25)); U_ = ((330, 1.0), (750, 0.5), (2400, 0.1))
    L["warcry_in"] = norm(crowd(26, 1.6, 100, 165, A_, contour=lambda x: 1.0 + 0.25 * np.clip(x * 3, 0, 1), vib_d=0.02), 0.85)         # deep "aaaa!"
    L["warcry_ar"] = norm(crowd(26, 1.5, 135, 200, E_, contour=lambda x: 0.9 + 0.35 * np.clip(x * 4, 0, 1) - 0.1 * x, vib_d=0.03), 0.85)  # higher yell
    L["warcry_steppe"] = norm(crowd(22, 1.5, 150, 230, U_, contour=lambda x: 1.0 + 0.4 * np.sin(np.pi * x), vib=8, vib_d=0.06), 0.85)    # whooping "uuu-hu"
    L["warcry_frank"] = norm(crowd(24, 1.4, 85, 130, O_, contour=lambda x: 1.0 + 0.15 * x, vib_d=0.015, rough=0.3), 0.85)              # low "hooo"
    L["warcry_berber"] = norm(crowd(18, 1.6, 300, 460, ((600, 1.0), (1800, 0.6), (2900, 0.3)), vib=9.5, vib_d=0.12), 0.8)              # ululation
    pn = np.zeros(int(2.4 * SR))
    for i in range(14): place(pn, voice(R.uniform(170, 300), R.uniform(0.35, 0.7), A_, contour=lambda x: 1.3 - 0.5 * x, vib_d=0.05), R.uniform(0, 1.8), R.uniform(0.4, 1))
    L["crowd_panic"] = norm(pn, 0.8)
    gr = np.zeros(int(1.6 * SR))
    for i in range(5): place(gr, voice(R.uniform(90, 130), R.uniform(0.6, 1.0), O_, contour=lambda x: 1.1 - 0.35 * x, rough=0.5), R.uniform(0, 0.6), R.uniform(0.5, 1))
    L["groan"] = norm(gr, 0.7)
    ec = np.zeros(int(3.2 * SR)); base = crowd(14, 1.0, 140, 220, U_, vib=8, vib_d=0.06)
    for d, g in ((0, 1.0), (0.35, 0.5), (0.7, 0.28), (1.05, 0.15)): place(ec, lp(base, 4000 - d * 2500), d, g)
    L["echo_shout"] = norm(ec, 0.8)
    # ---------------------------------------------------------------- impacts
    def rattle(s=0.35): out = np.zeros(int(s * SR)); [place(out, hp(N(0.006), 4000), R.uniform(0, s - 0.01), R.uniform(0.2, 0.7)) for _ in range(40)]; return out
    def thud(): t = T(0.5); return np.sin(2 * np.pi * (85 * np.exp(-t * 8) + 45) * t) * np.exp(-t * 10) + lp(N(0.5), 700) * np.exp(-t * 18) * 0.7
    bf = np.zeros(int(1.3 * SR)); t = T(0.5); place(bf, bp(N(0.5), 400, 2500) * np.sin(np.pi * t / 0.5) ** 2, 0, 0.6); place(bf, grunt(), 0.05, 0.6)
    place(bf, thud(), 0.75, 1.0); place(bf, rattle(), 0.76, 0.6); L["body_fly"] = norm(bf, 0.9)
    ft = np.zeros(int(0.8 * SR)); place(ft, thud(), 0); place(ft, rattle(), 0.01, 0.7); L["fall_thud"] = norm(ft, 0.9)
    s = 1.3; t = T(s); roll = lp(N(s), 220) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 6 * t))) * np.clip(t / 0.1, 0, 1)
    bo = np.zeros(int(1.8 * SR)); place(bo, roll, 0, 1.0); place(bo, thud() * 1.4, 0.9, 1.0); place(bo, bp(N(0.6), 200, 3000) * env(int(0.6 * SR), 0.001, 0.12), 0.9, 0.8)
    L["boulder"] = norm(bo, 0.95)
    rh = np.zeros(int(0.7 * SR)); place(rh, thud(), 0); place(rh, bp(N(0.3), 1500, 6000) * env(int(0.3 * SR), 0.0005, 0.05), 0, 0.7); L["rock_hit"] = norm(rh, 0.85)
    s = 0.9; t = T(s); f = 380 + 160 * np.sin(2 * np.pi * 1.3 * t); cr = bp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 600, 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / s)
    L["ladder"] = norm(cr, 0.5)
    lf = np.zeros(int(1.4 * SR)); place(lf, bp(N(0.6), 300, 2000) * np.sin(np.pi * T(0.6) / 0.6) ** 2, 0, 0.5)
    for i in range(6): place(lf, bp(N(0.12), 300, 1800) * env(int(0.12 * SR), 0.001, 0.04) + thud()[:int(0.12 * SR)] * 0.5, 0.55 + i * R.uniform(0.06, 0.12), R.uniform(0.5, 1))
    L["ladder_fall"] = norm(lf, 0.9)
    te = np.zeros(int(1.0 * SR))
    for i in range(10): place(te, bp(N(0.06), 400, 3500) * env(int(0.06 * SR), 0.002, 0.02), R.uniform(0, 0.6), R.uniform(0.3, 1))
    place(te, thud(), 0.55, 0.6); L["tent"] = norm(te, 0.8)
    # ---------------------------------------------------------------- atmosphere
    s = 1.0; t = T(s); f = 220 * np.exp(-t * 1.8); L["slowmo"] = norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / s) + 0.4 * lp(N(s), 300) * np.sin(np.pi * t / s), 0.8)
    s = 4.0; t = T(s); L["heat_drone"] = norm(lp(N(s), 400) * 0.6 + 0.2 * np.sin(2 * np.pi * 2400 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t)), 0.5)
    s = 4.0; t = T(s); L["wind"] = norm(bp(N(s), 250, 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * t)), 0.5)
    return {k: v.astype(np.float32) for k, v in L.items()}

if __name__ == "__main__":
    import sys, os, wave
    out = sys.argv[1] if len(sys.argv) > 1 else "battle_sfx"; os.makedirs(out, exist_ok=True); SR = 48000
    for k, v in build(SR).items():
        with wave.open(os.path.join(out, k + ".wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(v, -1, 1) * 32767).astype(np.int16).tobytes())
    print("wrote", out)
