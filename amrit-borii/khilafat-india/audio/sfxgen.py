"""Code-made sound effects + a 32 s upbeat music loop (no API, no licence worries).
usage: python sfxgen.py [out_dir]      (default: <WORKSPACE>/cache/sfx)
The renderer calls make_all() automatically the first time it needs sounds.
Put your own .mp3/.wav files with the same names in <WORKSPACE>/sfx/ to replace them.
"""
import os
import sys
import wave

import numpy as np

SR = 44100
RNG = np.random.default_rng(7)


def _t(sec):
    return np.arange(int(sec * SR)) / SR


def _env(n, a=0.005, r=0.2, sus=None):
    t = np.arange(n) / SR
    att = np.clip(t / max(a, 1e-4), 0, 1)
    rel = np.exp(-t / max(r, 1e-4)) if sus is None else np.clip((len(t) / SR - t) / max(r, 1e-4), 0, 1)
    return att * rel


def _lowpass(x, alpha):
    """one-pole low-pass; alpha may be an array (0..1, higher = brighter)"""
    y = np.empty_like(x)
    acc = 0.0
    al = np.broadcast_to(alpha, x.shape)
    for i in range(len(x)):
        acc += al[i] * (x[i] - acc)
        y[i] = acc
    return y


def _noise(sec):
    return RNG.uniform(-1, 1, int(sec * SR)).astype(np.float32)


def _norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return (x / m * peak).astype(np.float32)


def whoosh(sec, start=0.02, end=0.35):
    n = _noise(sec)
    t = _t(sec)
    sweep = start + (end - start) * np.sin(np.pi * t / sec) ** 2
    y = _lowpass(n, sweep)
    y *= np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 1.5
    return _norm(y, 0.8)


def pop():
    t = _t(0.18)
    f = 900 * np.exp(-t * 18) + 300
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
    return _norm(y, 0.85)


def boom():
    t = _t(1.6)
    f = 70 * np.exp(-t * 2.2) + 38
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)
    click = _lowpass(_noise(1.6), 0.25) * np.exp(-t * 40) * 0.6
    return _norm(np.tanh((body + click) * 2.2), 0.95)


def ding():
    t = _t(1.0)
    y = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(1318.5, 1), (2637, 0.35), (3951, 0.12)])
    return _norm(y * np.exp(-t * 4.5) * np.clip(t / 0.003, 0, 1), 0.7)


def riser():
    t = _t(1.4)
    f = 200 * 2 ** (t / 1.4 * 3)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35
    air = _lowpass(_noise(1.4), 0.03 + 0.4 * (t / 1.4))
    y = (tone + air) * (t / 1.4) ** 2
    return _norm(y, 0.75)


def slide(up=True):
    t = _t(1.0)
    f = (400 + 900 * t) if up else (1300 - 900 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t) ** 0.6
    vib = 1 + 0.03 * np.sin(2 * np.pi * 7 * t)
    return _norm(y * vib, 0.6)


def glitch():
    out = np.zeros(int(0.6 * SR), np.float32)
    pos = 0
    while pos < len(out) - 2000:
        ln = int(RNG.integers(600, 3000))
        f = float(RNG.choice([180, 440, 880, 1760, 3000]))
        seg = np.sign(np.sin(2 * np.pi * f * np.arange(ln) / SR)) * RNG.uniform(0.3, 1)
        out[pos:pos + ln] += seg[: len(out) - pos]
        pos += ln + int(RNG.integers(0, 1500))
    return _norm(out * _env(len(out), 0.002, 0.4), 0.5)


def stamp():
    t = _t(0.45)
    thud = np.sin(2 * np.pi * (110 * np.exp(-t * 9) + 50) * t) * np.exp(-t * 14)
    slap = _lowpass(_noise(0.45), 0.5) * np.exp(-t * 55)
    return _norm(np.tanh((thud + slap * 1.2) * 2), 0.95)


def drag():
    t = _t(0.9)
    y = _lowpass(_noise(0.9), 0.12) * np.sin(np.pi * t / 0.9) ** 1.2
    return _norm(y, 0.6)


def music(sec=32.0, bpm=118):
    """bright, light 'facts' bed: kick, clap, hats, bass, plucked chords (I-V-vi-IV in C)"""
    n = int(sec * SR)
    mix = np.zeros(n, np.float32)
    beat = 60 / bpm
    step = beat / 4

    def put(sig, t0, gain):
        i = int(t0 * SR)
        m = min(len(sig), n - i)
        if m > 0:
            mix[i:i + m] += sig[:m] * gain

    tk = _t(0.35)
    kick = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-tk * 18) + 45) / SR) * np.exp(-tk * 9)
    clap = _lowpass(_noise(0.25), 0.6) * np.exp(-_t(0.25) * 22)
    hat = (_noise(0.06) - _lowpass(_noise(0.06), 0.3)) * np.exp(-_t(0.06) * 60)
    chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]   # C G Am F
    roots = [36, 31, 33, 29]

    def hz(m):
        return 440 * 2 ** ((m - 69) / 12)

    def pluck(m, ln=0.32):
        t = _t(ln)
        f = hz(m)
        return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 9)

    def bass(m, ln):
        t = _t(ln)
        f = hz(m)
        return np.tanh(2 * np.sin(2 * np.pi * f * t)) * np.exp(-t * 2.5) * np.clip(t / 0.01, 0, 1)

    bars = int(sec / (beat * 4))
    for b in range(bars):
        t_bar = b * beat * 4
        ch = chords[b % 4]
        for k in range(4):
            put(kick, t_bar + k * beat, 0.9)
            if k in (1, 3):
                put(clap, t_bar + k * beat, 0.45)
        for s in range(16):
            put(hat, t_bar + s * step, 0.18 if s % 2 else 0.1)
            if s % 2 == 0:
                put(bass(roots[b % 4], step * 1.8), t_bar + s * step, 0.35)
            if s in (0, 3, 6, 8, 11, 14):
                put(pluck(ch[(s // 3) % 3] + 12), t_bar + s * step, 0.22)
    # soft edges so the loop joins cleanly
    fade = int(0.02 * SR)
    mix[:fade] *= np.linspace(0, 1, fade)
    mix[-fade:] *= np.linspace(1, 0, fade)
    return _norm(mix, 0.8)


def _write(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def make_all(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    sounds = {
        "whoosh_fast": lambda: whoosh(0.7, 0.03, 0.45), "whoosh_long": lambda: whoosh(1.5, 0.02, 0.3),
        "pop": pop, "boom": boom, "ding": ding, "riser": riser, "glitch": glitch, "stamp": stamp,
        "drag": drag, "grow": lambda: slide(True), "shrink": lambda: slide(False), "music_geo": music,
    }
    for name, fn in sounds.items():
        p = os.path.join(out_dir, name + ".wav")
        if not os.path.exists(p):
            _write(p, fn())
    return out_dir


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import render as R
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R.WS, "cache", "sfx")
    print("sounds ->", make_all(d))
