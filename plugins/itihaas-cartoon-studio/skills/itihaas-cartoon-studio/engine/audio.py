"""Builds audio/mix.wav: voice + generated background music + sound effects (all original, made in code).

python audio.py <project> [--fps 30]
story.json: "music": "mystery" | "epic" | "sad" | "path/to/your.mp3", "music_volume": 0.12
Beat keys: "sfx": "whoosh|pop|cash|boom|ding|drum|tension|swoosh|crowd" (or a list).
"""
import os, sys, math, subprocess
import numpy as np
from common import load_json, ffmpeg_bin
from voice import read_wav

SR = 44100
LEAD = 0.06  # voice starts this long after the beat's first frame


def beat_starts(story, timing, fps):
    t, out = 0.0, []
    for b in story["beats"]:
        n = max(1, round(timing["beats"][b["id"]]["dur"] * fps))
        out.append((b, t, n / fps))
        t += n / fps
    return out, t


# ------------------------------------------------------------------ synth helpers
def _env(n, a=0.01, r=0.2):
    e = np.ones(n, np.float32)
    na, nr = min(n // 2, int(a * SR)), min(n // 2, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def _lp(x, k):
    """cheap low-pass: moving average of k samples"""
    if k <= 1:
        return x
    c = np.cumsum(np.insert(x, 0, 0))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([y, np.zeros(len(x) - len(y), np.float32)])


def note(f):
    return 440.0 * 2 ** ((f - 69) / 12)


def music(kind, length):
    rng = np.random.default_rng(11)
    n = int(length * SR)
    out = np.zeros(n, np.float32)
    t = np.arange(n) / SR
    progs = {
        "mystery": [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)],   # Am F C G
        "epic": [(50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)],      # Dm Bb F C
        "sad": [(57, 60, 64), (52, 55, 59), (53, 57, 60), (52, 56, 59)],       # Am Em F E
        "tension": [(50, 53, 57), (51, 54, 58), (50, 53, 57), (49, 52, 56)],
        "investigate": [(52, 55, 59), (48, 52, 55), (53, 57, 60), (50, 53, 57)],
    }
    prog = progs.get(kind, progs["mystery"])
    bar = 4.0 if kind != "tension" else 3.0
    nb = int(math.ceil(length / bar)) + 1
    for i in range(nb):
        s0 = int(i * bar * SR)
        seg = int((bar + 1.0) * SR)
        if s0 >= n:
            break
        seg = min(seg, n - s0)
        tt = np.arange(seg) / SR
        ch = prog[i % len(prog)]
        pad = np.zeros(seg, np.float32)
        for m in ch:
            for det in (-0.12, 0.12):
                f = note(m - 12) * (1 + det / 100)
                pad += 0.05 * np.sin(2 * np.pi * f * tt + rng.random() * 6)
                pad += 0.015 * np.sin(2 * np.pi * 2 * f * tt)
        bass = 0.09 * np.sin(2 * np.pi * note(ch[0] - 24) * tt)
        if kind == "investigate":  # pulsing 8th-note synth bass
            gate = (np.sin(2 * np.pi * 4.0 * tt) > -0.2).astype(np.float32)
            gate = _lp(gate, 400)
            saw = 2 * ((note(ch[0] - 24) * tt) % 1) - 1
            bass = 0.07 * _lp(saw.astype(np.float32), 30) * gate + 0.06 * np.sin(2 * np.pi * note(ch[0] - 24) * tt)
        e = _env(seg, 0.8, 1.0)
        out[s0:s0 + seg] += (pad + bass) * e
        # soft plucked arpeggio
        step = bar / 8
        for k in range(8):
            ps = s0 + int(k * step * SR)
            ln = int(0.9 * SR)
            if ps + ln >= n:
                break
            m = ch[[0, 1, 2, 1, 0, 2, 1, 2][k]] + 12
            tt2 = np.arange(ln) / SR
            pl = np.sin(2 * np.pi * note(m) * tt2) * np.exp(-tt2 * 5) * 0.035
            out[ps:ps + ln] += pl
        # pulse (ticking clock feel) for mystery/tension
        if kind in ("mystery", "tension", "epic"):
            for k in range(int(bar * 2)):
                ps = s0 + int(k * 0.5 * SR)
                ln = int(0.08 * SR)
                if ps + ln >= n:
                    break
                tk = rng.normal(0, 1, ln).astype(np.float32) * np.exp(-np.arange(ln) / SR * 60) * 0.02
                out[ps:ps + ln] += tk
        if kind == "epic":
            for k in (0, 2):
                ps = s0 + int(k * bar / 4 * SR)
                ln = int(0.5 * SR)
                if ps + ln < n:
                    tt3 = np.arange(ln) / SR
                    out[ps:ps + ln] += 0.18 * np.sin(2 * np.pi * 55 * tt3 * (1 - tt3)) * np.exp(-tt3 * 8)
    out = _lp(out, 6)
    return out / (np.abs(out).max() + 1e-6) * 0.6


def sfx(name):
    rng = np.random.default_rng(abs(hash(name)) % 1000)
    if name in ("whoosh", "swoosh"):
        ln = int(0.55 * SR)
        x = rng.normal(0, 1, ln).astype(np.float32)
        y = _lp(x, 8) * np.sin(np.linspace(0, np.pi, ln)) ** 2
        return y / (np.abs(y).max() + 1e-6) * 0.45
    if name == "pop":
        ln = int(0.12 * SR)
        tt = np.arange(ln) / SR
        return (np.sin(2 * np.pi * (900 - 4000 * tt) * tt) * np.exp(-tt * 40) * 0.5).astype(np.float32)
    if name in ("cash", "ding", "coin"):
        ln = int(0.9 * SR)
        tt = np.arange(ln) / SR
        y = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in ((1975, 6), (2637, 8), (3951, 10)))
        if name == "cash":
            y[: int(0.08 * SR)] += rng.normal(0, 0.6, int(0.08 * SR))
        return (y / (np.abs(y).max() + 1e-6) * 0.35).astype(np.float32)
    if name in ("boom", "cannon"):
        ln = int(1.4 * SR)
        tt = np.arange(ln) / SR
        y = np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt * 3) + _lp(rng.normal(0, 1, ln), 30) * np.exp(-tt * 4) * 2
        return (y / (np.abs(y).max() + 1e-6) * 0.8).astype(np.float32)
    if name == "drum":
        ln = int(0.6 * SR)
        tt = np.arange(ln) / SR
        y = np.sin(2 * np.pi * (110 - 60 * tt) * tt) * np.exp(-tt * 9)
        return (y * 0.7).astype(np.float32)
    if name == "tension":
        ln = int(2.0 * SR)
        tt = np.arange(ln) / SR
        y = sum(np.sin(2 * np.pi * f * tt) for f in (110, 116.5, 220.3)) * np.linspace(0, 1, ln) ** 2
        return (y / (np.abs(y).max() + 1e-6) * 0.3).astype(np.float32)
    if name == "stamp":
        ln = int(0.35 * SR)
        tt = np.arange(ln) / SR
        y = np.sin(2 * np.pi * (140 - 80 * tt) * tt) * np.exp(-tt * 22) + rng.normal(0, 1, ln) * np.exp(-tt * 60) * .6
        return (y / (np.abs(y).max() + 1e-6) * 0.7).astype(np.float32)
    if name in ("type", "typing"):
        ln = int(1.2 * SR)
        y = np.zeros(ln, np.float32)
        t0 = 0
        while t0 < ln - 2000:
            k = int(0.012 * SR)
            y[t0:t0 + k] += (rng.normal(0, 1, k) * np.exp(-np.arange(k) / SR * 400)).astype(np.float32)
            t0 += int(rng.uniform(0.06, 0.13) * SR)
        return y / (np.abs(y).max() + 1e-6) * 0.22
    if name in ("page", "paper"):
        ln = int(0.45 * SR)
        y = _lp(rng.normal(0, 1, ln).astype(np.float32), 3) * np.sin(np.linspace(0, np.pi, ln)) ** 3
        return y / (np.abs(y).max() + 1e-6) * 0.25
    if name == "click":
        ln = int(0.03 * SR)
        y = rng.normal(0, 1, ln) * np.exp(-np.arange(ln) / SR * 300)
        return (y * 0.4).astype(np.float32)
    if name == "riser":
        ln = int(1.5 * SR)
        tt = np.arange(ln) / SR
        y = np.sin(2 * np.pi * (200 + 500 * tt ** 2) * tt) * (tt / tt[-1]) ** 2
        return (y * 0.18).astype(np.float32)
    if name == "crowd":
        ln = int(1.6 * SR)
        y = _lp(rng.normal(0, 1, ln).astype(np.float32), 20) * _env(ln, 0.3, 0.6)
        return y / (np.abs(y).max() + 1e-6) * 0.3
    return np.zeros(1, np.float32)


def load_any(path, length):
    tmp = path + ".mix.wav"
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", path, "-t", str(length),
                    "-ar", str(SR), "-ac", "1", tmp], check=True)
    a, _ = read_wav(tmp)
    os.remove(tmp)
    return a


def main():
    proj = os.path.abspath(sys.argv[1])
    fps = int(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 30
    story = load_json(os.path.join(proj, "story.json"))
    timing = load_json(os.path.join(proj, "audio", "timing.json"))
    starts, total = beat_starts(story, timing, fps)
    n = int((total + 0.5) * SR)
    voice = np.zeros(n, np.float32)
    fx = np.zeros(n, np.float32)
    prev_type = None
    for b, t0, d in starts:
        a, _ = read_wav(os.path.join(proj, "audio", "beats", f"{b['id']}.wav"))
        s = int((t0 + LEAD) * SR)
        voice[s:s + len(a)] += a[: max(0, n - s)]
        names = b.get("sfx", [])
        if isinstance(names, str):
            names = [names]
        sc = b.get("scene", {})
        typ = sc.get("type", "set" if story.get("style", "toon") == "toon" else "chars")
        timed = [(nm, 0.0) for nm in names]
        if story.get("auto_sfx", True):
            if (b.get("transition") or sc.get("transition")) == "whip":
                timed.append(("whoosh", 0.0))
            if typ == "black":
                timed.append(("type", 0.05))
            if typ in ("memo", "newspaper"):
                timed.append(("page", 0.0))
            if typ == "memo" and sc.get("stamp"):
                timed.append(("stamp", d * 0.6))
            if sc.get("big") or sc.get("text") or typ in ("title", "number"):
                timed.append(("pop", 0.2))
            if sc.get("lower"):
                timed.append(("swoosh", 0.3))
            if typ == "map":
                timed.append(("click", 0.3))
        for nm, off in timed:
            y = sfx(nm)
            s2 = int(max(0, t0 + off - (0.25 if nm in ("whoosh",) and off == 0 else 0)) * SR)
            fx[s2:s2 + len(y)] += y[: max(0, n - s2)]
        prev_type = typ
    mk = story.get("music", "mystery")
    if mk and mk != "none":
        m = load_any(os.path.join(proj, mk), total + 0.5) if os.path.exists(os.path.join(proj, str(mk))) else music(mk, total + 0.5)
        m = m[:n] if len(m) >= n else np.pad(m, (0, n - len(m)))
        # duck under the voice
        env = _lp(np.abs(voice), 4000)
        env = env / (env.max() + 1e-6)
        vol = float(story.get("music_volume", 0.14))
        gain = vol * (1 - 0.45 * np.clip(env * 3, 0, 1))
        m = m * gain
    else:
        m = 0
    mix = voice * 0.95 + fx * 0.6 + m
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    out = os.path.join(proj, "audio", "mix.wav")
    import wave
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(f"AUDIO OK: {out} ({total:.1f}s)")


if __name__ == "__main__":
    main()
