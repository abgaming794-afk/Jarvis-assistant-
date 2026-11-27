"""Premium real-document shots: an archival scan shown as a physical sheet in 3D.

scene {"type": "realdoc",
       "img": "assets/docs/<file>.jpg",            # real, verifiable source (public domain / licensed)
       "crop": [x0, y0, x1, y1],                    # part of the page to use (fractions)
       "highlights": [{"rect": [x0, y0, x1, y1], "at": 1.2, "time": .8}],   # marker sweeps (page fractions)
       "focus": [x, y],                             # page point the camera drifts towards
       "yaw": [-24, -8], "pitch": [12, 4], "roll": [-3, -1],   # degrees at start / end
       "push": [1.0, 1.55],                         # zoom from / to
       "curl": true,                                # animated corner curl
       "tone": "sepia",                             # sepia | ink | none
       "source": "A Collection of Charters and Statutes relating to the East India Company (1817)",
       "source_by": "Wikimedia Commons · Public domain",
       "bg": "desk_top"}
Also: draw_source(fr, text, by, t) — the premium source credit used by any scene that sets "source".
"""
import math, functools, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageChops
from common import hexc, clamp, ease_out, ease_in_out, lerp, font, serif, SKILL


def _coeffs(dst, src):
    """PIL PERSPECTIVE coefficients mapping output (dst) points to input (src) points."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def project(w, h, yaw, pitch, roll, scale, cx, cy, f=1800.0):
    """Corners of a w*h sheet rotated in 3D and projected (perspective) around screen point cx, cy."""
    ya, pa, ra = math.radians(yaw), math.radians(pitch), math.radians(roll)
    out = []
    for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        x, y = x * math.cos(ra) - y * math.sin(ra), x * math.sin(ra) + y * math.cos(ra)
        z = 0.0
        x, z = x * math.cos(ya) + z * math.sin(ya), -x * math.sin(ya) + z * math.cos(ya)
        y, z = y * math.cos(pa) - z * math.sin(pa), y * math.sin(pa) + z * math.cos(pa)
        k = f / (f + z)
        out.append((cx + x * k * scale, cy + y * k * scale))
    return out


@functools.lru_cache(maxsize=8)
def paper(path, crop, tone, W):
    im = Image.open(path).convert("L")
    if crop:
        x0, y0, x1, y1 = crop
        im = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
    im = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255.0
    a = np.clip((a - .12) / .82, 0, 1)                       # clean the scan: deeper ink, brighter paper
    h, w = a.shape
    rng = np.random.default_rng(7)
    fib = rng.normal(0, 1, (h // 4 + 1, w // 4 + 1)).astype(np.float32)
    fib = np.asarray(Image.fromarray(((fib * 18) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255 - .5
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / (w * .08)
    age = .78 + .22 * np.clip(edge, 0, 1)                    # darker, older edges
    if tone == "sepia":
        pc = np.array([238, 226, 198], np.float32) / 255     # paper
        ic = np.array([52, 36, 24], np.float32) / 255        # ink
    elif tone == "ink":
        pc, ic = np.array([244, 241, 232], np.float32) / 255, np.array([22, 22, 28], np.float32) / 255
    else:
        pc, ic = np.array([1, 1, 1], np.float32), np.array([0, 0, 0], np.float32)
    rgb = ic + (pc - ic) * a[..., None]
    rgb = rgb * (age[..., None] + fib[..., None] * .06)
    out = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    return out


def _highlight(pg, hl, t):
    W, H = pg.size
    k = ease_in_out(clamp((t - hl.get("at", 1.0)) / hl.get("time", .8)))
    if k <= 0:
        return pg
    x0, y0, x1, y1 = hl["rect"]
    lay = Image.new("RGBA", pg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    xe = x0 + (x1 - x0) * k
    pad = (y1 - y0) * H * .25
    d.rounded_rectangle([x0 * W - pad, y0 * H - pad * .4, xe * W + pad * .3, y1 * H + pad * .4], radius=pad,
                        fill=hexc(hl.get("color", "#ffd84a"), 255))
    lay = lay.filter(ImageFilter.GaussianBlur(W / 900))
    # multiply blend so the ink stays visible through the marker
    base = pg.convert("RGB")
    mul = ImageChops.multiply(base, Image.alpha_composite(Image.new("RGBA", pg.size, (255, 255, 255, 255)), lay).convert("RGB"))
    m = lay.getchannel("A").point(lambda v: int(v * .78))
    out = pg.copy()
    out.paste(mul, (0, 0), m)
    return out


def _curl(pg, k):
    """Bottom-right corner gently curling up (k 0..1)."""
    if k <= 0.01:
        return pg
    W, H = pg.size
    s = W * .16 * k
    out = pg.copy()
    mask = Image.new("L", pg.size, 255)
    ImageDraw.Draw(mask).polygon([(W, H - s), (W, H), (W - s, H)], fill=0)
    out.putalpha(ImageChops.multiply(out.getchannel("A"), mask))
    # flap: reflected triangle with a soft gradient (underside of the paper)
    flap = Image.new("RGBA", pg.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(flap)
    tri = [(W - s, H), (W, H - s), (W - s * .92, H - s * .92)]
    sh = Image.new("RGBA", pg.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(p[0] - s * .06, p[1] - s * .02) for p in tri], fill=(0, 0, 0, 110))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(s * .08 + 1)))
    grad = Image.linear_gradient("L").rotate(45, expand=False).resize(pg.size)
    fd.polygon(tri, fill=(226, 212, 182, 255))
    shade = Image.new("RGBA", pg.size, (120, 100, 70, 0))
    shade.putalpha(ImageChops.multiply(grad.point(lambda v: int(v * .45)), flap.getchannel("A")))
    flap.alpha_composite(shade)
    fd = ImageDraw.Draw(flap)
    fd.line([tri[0], tri[1]], fill=(150, 130, 100, 255), width=max(1, W // 600))
    out.alpha_composite(flap)
    return out


def draw_source(fr, text, by="", t=1.0, at=.6):
    """Source credit, top-right (secondary information): small Inter, gold label, soft top shade."""
    if not text or t < at:
        return
    from toonshot import hand
    W, H = fr.size
    u = H / 1080
    k = ease_out(clamp((t - at) / .6))
    lab = hand(int(15 * u), "oswald")
    f1 = hand(int(21 * u), "oswald")
    f2 = hand(int(16 * u), "body")
    band = Image.new("L", (1, 256))
    band.putdata([int(min(255, max(0, (196 - i) * 1.3))) for i in range(256)])
    band = band.resize((W, int(170 * u)))
    dark = Image.new("RGBA", band.size, (8, 6, 6, 0))
    dark.putalpha(band.point(lambda v: int(v * .55 * k)))
    fr.alpha_composite(dark, (0, 0))
    lay = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    xr = W - 40 * u + (1 - k) * 30 * u
    y = 30 * u
    gold = (214, 178, 96, int(255 * k))
    white = (244, 240, 230, int(255 * k))
    d.text((xr, y), "Srot", font=lab, fill=gold, anchor="ra")
    d.text((xr, y + 22 * u), text, font=f1, fill=white, anchor="ra")
    if by:
        d.text((xr, y + 50 * u), by, font=f2, fill=(210, 204, 192, int(225 * k)), anchor="ra")
    fr.alpha_composite(lay)


def place_3d(can, pg, t, dur, sc):
    """Put a page image into the canvas as a physical sheet: 3D yaw/pitch/roll, push towards focus,
    rise-in, contact shadow, light falloff and a gently curling corner."""
    CW, CH = can.size
    if sc.get("curl", True):
        kc = (.55 + .45 * math.sin(min(1.0, t / max(.5, dur)) * math.pi * .5)) * ease_out(clamp(t / .7))
        pg = _curl(pg, kc)
    p = 1 - (1 - clamp(t / dur)) ** 2.2
    yaw = lerp(*sc.get("yaw", [-22, -8]), p)
    pitch = lerp(*sc.get("pitch", [12, 4]), p)
    roll = lerp(*sc.get("roll", [-3, -1]), p)
    push = lerp(*sc.get("push", [1.0, 1.35]), p)
    fx, fy = sc.get("focus", [.5, .5])
    enter = ease_out(clamp(t / .55))
    cx = CW * sc.get("x", .5) - (fx - .5) * pg.width * (push - 1)
    cy = CH / 2 - (fy - .5) * pg.height * (push - 1) + (1 - enter) * CH * .6
    corners = project(pg.width, pg.height, yaw, pitch, roll, push, cx, cy)
    src = [(0, 0), (pg.width, 0), (pg.width, pg.height), (0, pg.height)]
    warped = pg.transform((CW, CH), Image.PERSPECTIVE, _coeffs(corners, src), Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    sh = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + CW * .012, y + CH * .02) for x, y in corners], fill=(0, 0, 0, 150))
    can.alpha_composite(sh.filter(ImageFilter.GaussianBlur(CW / 90)))
    lay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    lay.putalpha(Image.linear_gradient("L").rotate(90).resize((CW, CH)).point(lambda v: int(v * .22)))
    lit = Image.composite(lay, Image.new("RGBA", (CW, CH), (0, 0, 0, 0)), warped.getchannel("A"))
    can.alpha_composite(warped)
    can.alpha_composite(lit)


class DocShot:
    def __init__(self, sc, CW, CH, dur):
        self.sc, self.CW, self.CH, self.dur = sc, CW, CH, dur

    def draw(self, can, t):
        sc, CW, CH = self.sc, self.CW, self.CH
        path = sc["img"] if os.path.isabs(sc["img"]) else os.path.join(SKILL, sc["img"])
        pw = int(CW * sc.get("w", .5))
        pg = paper(path, tuple(sc.get("crop") or ()), sc.get("tone", "sepia"), pw)
        for hl in sc.get("highlights", []):
            pg = _highlight(pg, hl, t)
        place_3d(can, pg, t, self.dur, sc)
