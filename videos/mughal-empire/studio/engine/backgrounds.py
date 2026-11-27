"""Painted-look backgrounds drawn in code. make(name, W, H, seed=0, tint=None) -> RGB image.

Every background is soft-focused (slight blur + vignette) so the sharp characters pop, like an
illustrated explainer. Names: see BACKGROUNDS at the bottom.
"""
import math, random, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import hexc, shade, mix


def _grad(W, H, stops):
    """Vertical gradient. stops = [(pos0..1, colour), ...]"""
    ys = np.linspace(0, 1, H)[:, None]
    out = np.zeros((H, 1, 3), np.float32)
    cols = [(p, np.array(hexc(c)[:3], np.float32)) for p, c in stops]
    for i in range(len(cols) - 1):
        p0, c0 = cols[i]
        p1, c1 = cols[i + 1]
        m = (ys >= p0) & (ys <= p1)
        t = ((ys - p0) / max(1e-6, p1 - p0))[..., None]
        out[m[:, 0]] = (c0 + (c1 - c0) * t)[m[:, 0]]
    out = np.repeat(out, W, axis=1)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")


def _vignette(img, strength=0.55):
    W, H = img.size
    y, x = np.ogrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / 1.41
    v = 1 - strength * np.clip(d, 0, 1) ** 2.2
    a = np.asarray(img.convert("RGB"), np.float32) * v[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGB")


def _glow(img, x, y, r, col, a=150):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([x - r, y - r, x + r, y + r], fill=hexc(col, a))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.6))
    img.alpha_composite(layer)


def _bokeh(img, n, cols, rmin, rmax, ymin=0.0, ymax=1.0, a=110, rnd=None):
    rnd = rnd or random.Random(1)
    W, H = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        r = rnd.uniform(rmin, rmax) * W
        x = rnd.uniform(0, W)
        y = rnd.uniform(ymin, ymax) * H
        d.ellipse([x - r, y - r, x + r, y + r], fill=hexc(rnd.choice(cols), rnd.randint(a // 2, a)))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(W * 0.004)))


def _arch(d, x, y, w, h, fill, outline=None, lw=0, cusp=True):
    """Indo-Islamic pointed arch opening: x,y = bottom-left."""
    pts = [(x, y), (x, y - h * 0.62)]
    for k in range(21):
        t = k / 20
        a = math.pi * (1 - t)
        px = x + w / 2 + math.cos(a) * w / 2
        py = y - h * 0.62 - math.sin(a) * h * 0.30 - (h * 0.08) * (1 - abs(2 * t - 1)) ** 3
        pts.append((px, py))
    pts += [(x + w, y - h * 0.62), (x + w, y)]
    d.polygon(pts, fill=fill, outline=outline, width=lw)


# --------------------------------------------------------------------------- scenes
def london(W, H, rnd):
    img = _grad(W, H, [(0, "#8a9bb0"), (0.55, "#c9c3b5"), (0.56, "#5b5552"), (1, "#3b3634")])
    d = ImageDraw.Draw(img)
    hz = int(H * 0.56)
    # far buildings
    x = -20
    while x < W:
        bw = rnd.randint(int(W * 0.05), int(W * 0.11))
        bh = rnd.randint(int(H * 0.12), int(H * 0.30))
        col = rnd.choice(["#6f6a6a", "#7b7471", "#686364"])
        d.rectangle([x, hz - bh, x + bw, hz], fill=col)
        d.polygon([(x - 4, hz - bh), (x + bw / 2, hz - bh - H * 0.05), (x + bw + 4, hz - bh)], fill=shade(col, 0.85))
        for wy in range(hz - bh + int(H * 0.03), hz - 6, int(H * 0.05)):
            for wx in range(x + 8, x + bw - 10, int(W * 0.022)):
                d.rectangle([wx, wy, wx + W * 0.009, wy + H * 0.022], fill="#e9c97a" if rnd.random() < .35 else "#4a4545")
        x += bw + rnd.randint(2, 18)
    # clock tower
    tx = int(W * 0.78)
    d.rectangle([tx, hz - H * 0.52, tx + W * 0.06, hz], fill="#5d5650")
    d.ellipse([tx + W * 0.008, hz - H * 0.46, tx + W * 0.052, hz - H * 0.46 + W * 0.044], fill="#efe6c8", outline="#3a3430", width=3)
    d.polygon([(tx - 6, hz - H * 0.52), (tx + W * 0.03, hz - H * 0.66), (tx + W * 0.06 + 6, hz - H * 0.52)], fill="#4a443f")
    # river / street
    d.rectangle([0, hz, W, H], fill="#4a4442")
    for k in range(9):
        y = hz + (H - hz) * (k / 9) ** 1.6
        d.line([(0, y), (W, y)], fill="#3e3937", width=2)
    for lx in (0.12, 0.4, 0.66):
        X = W * lx
        d.rectangle([X - 3, hz - H * 0.18, X + 3, H], fill="#2c2826")
        _glow(img, X, hz - H * 0.19, W * 0.025, "#ffd27a", 200)
    return img


def palace(W, H, rnd):
    img = _grad(W, H, [(0, "#3a1012"), (0.6, "#6e1f22"), (0.61, "#5a1a1b"), (1, "#2c0b0c")])
    d = ImageDraw.Draw(img)
    hz = int(H * 0.62)
    for k in range(6):
        x = W * (0.05 + k * 0.18)
        d.rectangle([x, H * 0.05, x + W * 0.05, hz], fill="#c99a3a")
        d.rectangle([x + W * 0.006, H * 0.05, x + W * 0.014, hz], fill="#e5c06a")
        d.rectangle([x - W * 0.01, hz - H * 0.03, x + W * 0.06, hz], fill="#a87a2a")
    # carpet perspective
    d.polygon([(W * 0.38, hz), (W * 0.62, hz), (W * 0.85, H), (W * 0.15, H)], fill="#9c1c22")
    d.polygon([(W * 0.40, hz), (W * 0.60, hz), (W * 0.80, H), (W * 0.20, H)], fill="#b5262c")
    for cx in (0.3, 0.7):
        _glow(img, W * cx, H * 0.12, W * 0.06, "#ffd27a", 170)
    _bokeh(img, 25, ["#ffcf6b", "#ffe2a0"], 0.004, 0.012, 0.0, 0.5, 140, rnd)
    return img


def court(W, H, rnd):
    img = _grad(W, H, [(0, "#d9a36a"), (0.62, "#c98a52"), (0.63, "#efe2c8"), (1, "#cdbb98")])
    d = ImageDraw.Draw(img)
    hz = int(H * 0.63)
    # back wall arches
    n = 5
    aw = W / n
    for k in range(n):
        x = k * aw + aw * 0.14
        _arch(d, x, hz, aw * 0.72, H * 0.52, "#7a3f22")
        _arch(d, x + aw * 0.06, hz, aw * 0.60, H * 0.44, "#a65a2c")
        d.rectangle([k * aw - aw * 0.03, H * 0.08, k * aw + aw * 0.06, hz], fill="#f1e2c4")
    d.rectangle([0, 0, W, H * 0.08], fill="#b5733f")
    for k in range(int(W / 40)):
        d.polygon([(k * 40, H * 0.08), (k * 40 + 20, H * 0.11), (k * 40 + 40, H * 0.08)], fill="#8f5530")
    # floor tiles
    for k in range(1, 8):
        y = hz + (H - hz) * (k / 8) ** 1.5
        d.line([(0, y), (W, y)], fill="#c9b48e", width=2)
    d.polygon([(W * 0.3, hz), (W * 0.7, hz), (W * 0.95, H), (W * 0.05, H)], fill="#9a2a2a")
    d.polygon([(W * 0.33, hz + 6), (W * 0.67, hz + 6), (W * 0.9, H), (W * 0.1, H)], outline="#e5c06a", width=4)
    for cx in (0.2, 0.5, 0.8):
        d.line([(W * cx, 0), (W * cx, H * 0.2)], fill="#5a3a20", width=3)
        _glow(img, W * cx, H * 0.22, W * 0.03, "#ffcf6b", 200)
    return img


def sea(W, H, rnd):
    img = _grad(W, H, [(0, "#f2b77a"), (0.38, "#f6d7a3"), (0.5, "#5f8fa6"), (1, "#1d4d68")])
    d = ImageDraw.Draw(img)
    hz = int(H * 0.5)
    _glow(img, W * 0.7, hz - H * 0.06, W * 0.08, "#fff1c0", 220)
    for k in range(40):
        y = hz + (H - hz) * (k / 40) ** 1.3
        x = rnd.uniform(0, W)
        L = W * (0.03 + 0.08 * k / 40)
        d.line([(x, y), (x + L, y)], fill=(255, 255, 255, 70), width=max(1, int(H * 0.003)))
    for sx, s in ((0.22, 1.0), (0.48, 0.6), (0.85, 0.45)):
        _ship(d, W * sx, hz + H * 0.03 * s, H * 0.25 * s)
    return img


def _ship(d, x, y, h, col="#3b2a20", sail="#f3ead6"):
    w = h * 1.1
    d.polygon([(x - w / 2, y - h * 0.18), (x + w / 2, y - h * 0.18), (x + w * 0.38, y), (x - w * 0.4, y)], fill=col)
    d.line([(x, y - h * 0.18), (x, y - h)], fill=col, width=max(2, int(h * 0.03)))
    d.line([(x - w * 0.25, y - h * 0.18), (x - w * 0.25, y - h * 0.8)], fill=col, width=max(2, int(h * 0.025)))
    d.polygon([(x + 4, y - h * 0.95), (x + w * 0.3, y - h * 0.6), (x + 4, y - h * 0.3)], fill=sail)
    d.polygon([(x - w * 0.25 + 3, y - h * 0.75), (x - w * 0.05, y - h * 0.5), (x - w * 0.25 + 3, y - h * 0.3)], fill=sail)
    d.polygon([(x, y - h), (x + h * 0.15, y - h * 0.95), (x, y - h * 0.9)], fill="#c0322b")


def port(W, H, rnd):
    img = sea(W, H, rnd)
    d = ImageDraw.Draw(img)
    y0 = H * 0.72
    d.rectangle([0, y0, W, H], fill="#7a5233")
    for k in range(14):
        d.line([(k * W / 14, y0), (k * W / 14, H)], fill="#5e3e26", width=3)
    for k in range(5):
        x = W * (0.05 + k * 0.08)
        d.rectangle([x, y0 - H * 0.08, x + W * 0.06, y0], fill="#a57944", outline="#5e3e26", width=3)
        d.line([(x, y0 - H * 0.08), (x + W * 0.06, y0)], fill="#5e3e26", width=2)
    return img


def battlefield(W, H, rnd):
    img = _grad(W, H, [(0, "#4a2a2a"), (0.35, "#c4542c"), (0.6, "#e8a05a"), (0.61, "#5a4a2a"), (1, "#2e2618")])
    d = ImageDraw.Draw(img)
    hz = int(H * 0.61)
    for k in range(3):
        pts = [(0, H)]
        for i in range(13):
            pts.append((i * W / 12, hz - H * (0.05 + 0.04 * k) - rnd.uniform(0, H * 0.05)))
        pts.append((W, H))
        d.polygon(pts, fill=["#6b4a2e", "#4f3820", "#3a2a18"][k])
    smoke = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for _ in range(18):
        r = rnd.uniform(0.04, 0.1) * W
        x = rnd.uniform(0, W)
        y = rnd.uniform(0.3, 0.6) * H
        sd.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(70, 60, 60, 120))
    img.alpha_composite(smoke.filter(ImageFilter.GaussianBlur(W * 0.02)))
    for _ in range(8):
        x = rnd.uniform(0.05, 0.95) * W
        y = hz + rnd.uniform(0, 0.08) * H
        d.line([(x, y), (x, y - H * 0.08)], fill="#2a1d14", width=3)
        d.polygon([(x, y - H * 0.08), (x + W * 0.03, y - H * 0.07), (x, y - H * 0.06)], fill=rnd.choice(["#c0322b", "#2f6d3a", "#e8c547"]))
    for _ in range(4):
        _glow(img, rnd.uniform(0, W), rnd.uniform(0.45, 0.65) * H, W * 0.03, "#ffb347", 200)
    return img


def war_room(W, H, rnd):
    img = _grad(W, H, [(0, "#1b1512"), (0.7, "#2e231c"), (1, "#14100d")])
    d = ImageDraw.Draw(img)
    d.rectangle([W * 0.1, H * 0.1, W * 0.45, H * 0.45], fill="#c9b38a", outline="#5a4020", width=6)
    for _ in range(6):
        x0, y0 = rnd.uniform(0.12, 0.43) * W, rnd.uniform(0.12, 0.43) * H
        d.line([(x0, y0), (x0 + rnd.uniform(-60, 60), y0 + rnd.uniform(-40, 40))], fill="#8a5a2a", width=3)
    d.ellipse([W * 0.28, H * 0.22, W * 0.3, H * 0.25], fill="#c0322b")
    d.rectangle([W * 0.6, H * 0.08, W * 0.9, H * 0.5], fill="#3a2a20")
    for k in range(5):
        d.line([(W * 0.6, H * (0.12 + k * 0.08)), (W * 0.9, H * (0.12 + k * 0.08))], fill="#2a1d14", width=4)
        for j in range(8):
            d.rectangle([W * (0.61 + j * 0.035), H * (0.12 + k * 0.08) - H * 0.06, W * (0.63 + j * 0.035), H * (0.12 + k * 0.08) - 2],
                        fill=rnd.choice(["#7a1f2b", "#2f5d3a", "#8a6a2a", "#3a4a6a"]))
    d.rectangle([0, H * 0.7, W, H], fill="#3b2a1e")
    _glow(img, W * 0.5, H * 0.35, W * 0.18, "#ffcf6b", 90)
    return img


def dinner(W, H, rnd):
    img = _grad(W, H, [(0, "#1c0f0c"), (0.7, "#3a1d16"), (1, "#1a0d0a")])
    _bokeh(img, 40, ["#ffcf6b", "#ffb347", "#ffe2a0"], 0.006, 0.025, 0.05, 0.7, 150, rnd)
    d = ImageDraw.Draw(img)
    for x in (0.08, 0.92):
        d.rectangle([W * x - W * 0.05, 0, W * x + W * 0.05, H * 0.8], fill="#5a1414")
    d.rectangle([0, H * 0.72, W, H], fill="#2a1410")
    return img


def village(W, H, rnd):
    img = _grad(W, H, [(0, "#e8c48a"), (0.5, "#f1d9a8"), (0.51, "#b89458"), (1, "#8a6a3a")])
    d = ImageDraw.Draw(img)
    hz = int(H * 0.51)
    _glow(img, W * 0.75, H * 0.2, W * 0.07, "#fff6d0", 230)
    for k in range(4):
        x = W * (0.08 + k * 0.24) + rnd.uniform(-20, 20)
        w, h = W * 0.13, H * 0.14
        d.rectangle([x, hz - h, x + w, hz + H * 0.02], fill="#b07a4a", outline="#6a4424", width=3)
        d.polygon([(x - w * 0.12, hz - h), (x + w / 2, hz - h - H * 0.11), (x + w * 1.12, hz - h)], fill="#c9a35a", outline="#7a5a2a")
        d.rectangle([x + w * 0.4, hz - h * 0.6, x + w * 0.6, hz + H * 0.02], fill="#4a2e18")
    for k in range(30):
        y = hz + (H - hz) * rnd.random()
        x = rnd.uniform(0, W)
        d.line([(x, y), (x + W * 0.03, y - 3)], fill="#9a7a42", width=2)
    for x in (W * 0.03, W * 0.97):
        d.line([(x, hz), (x + 8, hz - H * 0.2)], fill="#5a4020", width=5)
        for b in range(4):
            d.line([(x + 6, hz - H * (0.08 + b * .03)), (x + 6 + rnd.uniform(-50, 50), hz - H * (0.12 + b * .03))], fill="#5a4020", width=3)
    return img


def office(W, H, rnd):
    img = _grad(W, H, [(0, "#5a3a22"), (0.68, "#6e4a2c"), (0.69, "#3a2618"), (1, "#24180f")])
    d = ImageDraw.Draw(img)
    for k in range(7):
        x = k * W / 6
        d.rectangle([x - 4, 0, x + 4, H * 0.68], fill="#4a2e1a")
        d.rectangle([x + W * 0.02, H * 0.38, x + W / 6 - W * 0.02, H * 0.64], outline="#4a2e1a", width=4)
    # window
    d.rectangle([W * 0.36, H * 0.06, W * 0.64, H * 0.46], fill="#9fb0c0", outline="#3a2414", width=10)
    d.line([(W * 0.5, H * 0.06), (W * 0.5, H * 0.46)], fill="#3a2414", width=8)
    d.line([(W * 0.36, H * 0.26), (W * 0.64, H * 0.26)], fill="#3a2414", width=8)
    for k in range(5):
        d.rectangle([W * (0.37 + k * 0.055), H * (0.32 - 0.03 * (k % 2)), W * (0.41 + k * 0.055), H * 0.46], fill="#7b8590")
    # company flag-ish banner
    d.rectangle([W * 0.08, H * 0.08, W * 0.2, H * 0.3], fill="#f2efe6", outline="#3a2414", width=4)
    for k in range(6):
        d.rectangle([W * 0.08, H * (0.08 + k * 0.037), W * 0.2, H * (0.08 + k * 0.037 + 0.018)], fill="#c0322b")
    d.rectangle([W * 0.08, H * 0.08, W * 0.13, H * 0.17], fill="#f2efe6")
    d.rectangle([W * 0.1, H * 0.08, W * 0.11, H * 0.17], fill="#c0322b")
    d.rectangle([W * 0.08, H * 0.117, W * 0.13, H * 0.133], fill="#c0322b")
    _glow(img, W * 0.5, H * 0.26, W * 0.14, "#ffe9b0", 70)
    return img


def night(W, H, rnd):
    img = _grad(W, H, [(0, "#0b1430"), (0.7, "#1f2d55"), (0.71, "#141a2a"), (1, "#0a0d16")])
    d = ImageDraw.Draw(img)
    for _ in range(140):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 0.65) * H
        r = rnd.uniform(0.6, 2.2) * W / 1280
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 240, rnd.randint(120, 255)))
    _glow(img, W * 0.8, H * 0.18, W * 0.05, "#fff6d0", 220)
    d.ellipse([W * 0.78, H * 0.18 - W * 0.02, W * 0.82, H * 0.18 + W * 0.02], fill="#fff6d8")
    hz = H * 0.71
    for k in range(9):
        x = W * k / 8
        d.rectangle([x - W * 0.05, hz - H * 0.12, x + W * 0.05, hz], fill="#0d1020")
        d.chord([x - W * 0.04, hz - H * 0.2, x + W * 0.04, hz - H * 0.06], 180, 360, fill="#0d1020")
    return img


def fort(W, H, rnd):
    img = _grad(W, H, [(0, "#8cc3e0"), (0.5, "#d9ecf2"), (0.51, "#c08a5a"), (1, "#8a5a32")])
    d = ImageDraw.Draw(img)
    hz = H * 0.62
    d.rectangle([0, hz - H * 0.22, W, hz], fill="#b8603a")
    for k in range(int(W / 50) + 1):
        d.rectangle([k * 50, hz - H * 0.25, k * 50 + 30, hz - H * 0.22], fill="#b8603a")
    for x in (0.2, 0.5, 0.8):
        X = W * x
        d.rectangle([X - W * 0.06, hz - H * 0.38, X + W * 0.06, hz], fill="#a8502f")
        d.chord([X - W * 0.05, hz - H * 0.5, X + W * 0.05, hz - H * 0.3], 180, 360, fill="#f1e2c4")
        _arch(d, X - W * 0.02, hz - H * 0.05, W * 0.04, H * 0.18, "#5a2a18")
    d.rectangle([0, hz, W, H], fill="#a8784a")
    return img


def studio(W, H, rnd, base="#1d1a24", glowc="#5a4a7a"):
    img = _grad(W, H, [(0, shade(base, 0.8)), (1, base)])
    _glow(img, W * 0.5, H * 0.45, W * 0.35, glowc, 140)
    return img


def parchment(W, H, rnd):
    img = _grad(W, H, [(0, "#e9d6a6"), (1, "#d4b77c")])
    a = np.asarray(img, np.float32)
    noise = np.random.default_rng(3).normal(0, 9, (H, W, 1))
    a[..., :3] += noise
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    return img


BACKGROUNDS = {
    "london": london, "palace": palace, "court": court, "sea": sea, "port": port, "battlefield": battlefield,
    "war_room": war_room, "dinner": dinner, "village": village, "office": office, "night": night, "fort": fort,
    "parchment": parchment,
    "studio_dark": lambda W, H, r: studio(W, H, r),
    "studio_red": lambda W, H, r: studio(W, H, r, "#2a0d0f", "#a3233a"),
    "studio_gold": lambda W, H, r: studio(W, H, r, "#2a1d0d", "#c9a227"),
    "studio_blue": lambda W, H, r: studio(W, H, r, "#0d1a2a", "#2f6d8a"),
}


@functools.lru_cache(maxsize=24)
def make(name, W, H, seed=0, blur=True):
    fn = BACKGROUNDS.get(name)
    if fn is None:
        raise KeyError(f"unknown background '{name}'. Use one of: {', '.join(BACKGROUNDS)}")
    rnd = random.Random(seed or hash(name) % 1000)
    img = fn(W, H, rnd).convert("RGBA")
    if blur and not name.startswith("studio") and name != "parchment":
        img = img.filter(ImageFilter.GaussianBlur(max(1.0, W / 520)))
    return _vignette(img, 0.5 if name != "parchment" else 0.35).convert("RGB")


if __name__ == "__main__":
    import sys
    names = list(BACKGROUNDS)
    tw, th = 480, 270
    cols = 4
    sheet = Image.new("RGB", (cols * tw, ((len(names) + cols - 1) // cols) * th))
    for i, n in enumerate(names):
        sheet.paste(make(n, tw, th), ((i % cols) * tw, (i // cols) * th))
        ImageDraw.Draw(sheet).text(((i % cols) * tw + 6, (i // cols) * th + 6), n, fill=(255, 255, 255))
    sheet.save(sys.argv[1] if len(sys.argv) > 1 else "bg_sheet.jpg")
