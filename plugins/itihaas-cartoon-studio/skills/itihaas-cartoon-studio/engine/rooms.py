"""Crisp flat-vector sets with cinematic lighting (documentary-toon look).

make(name, W, H, light="auto", seed=0) -> RGB image. FLOOR (fraction of H) is where characters stand.
Each set is drawn in a 1920x1080 design space then lit: ambient darkening + warm/cool light pools +
vignette + fine grain.
"""
import math, random, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import hexc, shade, mix, font

OL = (34, 26, 24, 255)
FLOOR = {"default": 0.80}


class Set:
    def __init__(self, W, H, seed=0):
        self.W, self.H = W, H
        self.k = W / 1920.0
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        self.d = ImageDraw.Draw(self.img)
        self.rnd = random.Random(seed)
        self.lights = []  # (x, y, r, colour, strength)
        self.ambient = 0.0

    def P(self, x, y):
        return (x * self.k, y * self.k)

    def rect(self, x0, y0, x1, y1, fill, ol=True, w=3, r=0):
        k = self.k
        box = [x0 * k, y0 * k, x1 * k, y1 * k]
        if r:
            self.d.rounded_rectangle(box, radius=r * k, fill=hexc(fill), outline=OL if ol else None,
                                     width=max(1, int(w * k)) if ol else 0)
        else:
            self.d.rectangle(box, fill=hexc(fill), outline=OL if ol else None, width=max(1, int(w * k)) if ol else 0)

    def poly(self, pts, fill, ol=True, w=3):
        P = [self.P(*p) for p in pts]
        self.d.polygon(P, fill=hexc(fill))
        if ol:
            self.d.line(P + [P[0]], fill=OL, width=max(1, int(w * self.k)), joint="curve")

    def ell(self, cx, cy, rx, ry, fill, ol=True, w=3):
        k = self.k
        self.d.ellipse([(cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k], fill=hexc(fill),
                       outline=OL if ol else None, width=max(1, int(w * k)) if ol else 0)

    def line(self, pts, fill=OL, w=3):
        self.d.line([self.P(*p) for p in pts], fill=hexc(fill), width=max(1, int(w * self.k)))

    def grad(self, x0, y0, x1, y1, c0, c1):
        k = self.k
        h = max(1, int((y1 - y0) * k))
        w = max(1, int((x1 - x0) * k))
        a = np.linspace(0, 1, h)[:, None, None]
        c0, c1 = np.array(hexc(c0), np.float32), np.array(hexc(c1), np.float32)
        arr = (c0 + (c1 - c0) * a).repeat(w, axis=1).astype(np.uint8)
        self.img.paste(Image.fromarray(arr, "RGBA"), (int(x0 * k), int(y0 * k)))
        self.d = ImageDraw.Draw(self.img)

    def text(self, x, y, s, size, fill, anchor="mm", weight="Bold"):
        self.d.text(self.P(x, y), s, font=font(size * self.k, weight), fill=hexc(fill), anchor=anchor)

    def light(self, x, y, r, col="#ffd98a", s=0.8):
        self.lights.append((x, y, r, col, s))

    # ------------------------------------------------------------------ reusable furniture
    def window_blinds(self, x, y, w, h, sky=("#0d1a33", "#24365e"), city=True, sunset=False):
        self.rect(x - 10, y - 10, x + w + 10, y + h + 10, "#2a2426")
        if sunset:
            sky = ("#5a3a6a", "#f0a35a")
        self.grad(x, y, x + w, y + h, *sky)
        if city:
            r = self.rnd
            bx = x
            while bx < x + w:
                bw = r.randint(40, 90)
                bh = r.randint(int(h * .25), int(h * .7))
                self.rect(bx, y + h - bh, min(x + w, bx + bw), y + h, "#141a2a" if not sunset else "#3a2a3a", ol=False)
                for wy in range(int(y + h - bh + 12), int(y + h - 8), 22):
                    for wx in range(int(bx + 8), int(min(x + w, bx + bw) - 10), 18):
                        if r.random() < 0.3:
                            self.rect(wx, wy, wx + 7, wy + 9, "#f6d27a", ol=False)
                bx += bw + r.randint(4, 14)
        for k in range(0, int(h), 26):
            self.line([(x, y + k), (x + w, y + k)], "#00000055", 4)
        self.line([(x + w / 2, y), (x + w / 2, y + h)], "#2a2426", 10)

    def clock(self, x, y, r=46):
        self.ell(x, y, r, r, "#f4efe4", w=5)
        self.line([(x, y), (x, y - r * 0.6)], OL, 5)
        self.line([(x, y), (x + r * 0.45, y + r * 0.1)], OL, 5)

    def frame(self, x, y, w, h, inner="#c9b48a", kind="map"):
        self.rect(x, y, x + w, y + h, "#5a3f2a", w=4)
        self.rect(x + 12, y + 12, x + w - 12, y + h - 12, inner, w=2)
        if kind == "map":
            r = self.rnd
            for _ in range(5):
                px, py = r.uniform(x + 30, x + w - 30), r.uniform(y + 30, y + h - 30)
                self.ell(px, py, 7, 7, "#c0322b", w=2)
            self.poly([(x + w * .3, y + h * .3), (x + w * .5, y + h * .25), (x + w * .6, y + h * .55),
                       (x + w * .4, y + h * .7)], "#e8dcc0", w=2)
        elif kind == "portrait":
            self.ell(x + w / 2, y + h * .42, w * .2, w * .2, "#d9b48a", w=2)
            self.rect(x + w * .25, y + h * .62, x + w * .75, y + h - 14, "#3a2a2a", ol=False)

    def bookshelf(self, x, y, w, h):
        self.rect(x, y, x + w, y + h, "#4a3222", w=4)
        r = self.rnd
        for sy in range(int(y + 20), int(y + h - 20), 90):
            self.line([(x, sy + 80), (x + w, sy + 80)], "#2e1f15", 8)
            bx = x + 12
            while bx < x + w - 30:
                bw = r.randint(14, 26)
                bh = r.randint(50, 72)
                self.rect(bx, sy + 80 - bh, bx + bw, sy + 80, r.choice(["#7a2a2a", "#2f4d6a", "#6a5a2a", "#3f5a3a", "#5a3a5a", "#8a6a3a"]), w=2)
                bx += bw + 3

    def desk(self, x, y, w, h=60, col="#5a3a24", legs=True):
        self.rect(x, y, x + w, y + h, col, w=4)
        self.rect(x, y, x + w, y + 14, shade(col, 1.2), ol=False)
        if legs:
            self.rect(x + 20, y + h, x + 50, 1080, shade(col, 0.8), w=3)
            self.rect(x + w - 50, y + h, x + w - 20, 1080, shade(col, 0.8), w=3)

    def banker_lamp(self, x, y):
        self.rect(x - 8, y - 70, x + 8, y, "#b8902a", w=2)
        self.ell(x, y, 40, 10, "#b8902a", w=2)
        self.poly([(x - 70, y - 70), (x + 70, y - 70), (x + 54, y - 110), (x - 54, y - 110)], "#2f7d4e", w=3)
        self.light(x, y - 40, 420, "#ffe3a0", 0.95)

    def ceiling_lamp(self, x, y, col="#c0322b"):
        self.line([(x, 0), (x, y - 40)], OL, 4)
        self.poly([(x - 60, y), (x + 60, y), (x + 30, y - 44), (x - 30, y - 44)], col, w=3)
        self.light(x, y + 120, 360, "#ffe3a0", 0.7)

    def plant(self, x, y, s=1.0):
        self.poly([(x - 34 * s, y - 70 * s), (x + 34 * s, y - 70 * s), (x + 24 * s, y), (x - 24 * s, y)], "#b8603a", w=3)
        for a in (-60, -30, 0, 30, 60):
            ang = math.radians(a - 90)
            ex, ey = x + math.cos(ang) * 120 * s, y - 70 * s + math.sin(ang) * 120 * s
            self.poly([(x, y - 70 * s), (ex - 14 * s, ey), (ex + 14 * s, ey)], "#3f7d4e", w=2)

    def arch(self, x, y, w, h, fill, ol=True):
        pts = [(x, y), (x, y - h * 0.6)]
        for k in range(17):
            t = k / 16
            a = math.pi * (1 - t)
            pts.append((x + w / 2 + math.cos(a) * w / 2, y - h * 0.6 - math.sin(a) * h * 0.32 - h * 0.08 * (1 - abs(2 * t - 1)) ** 3))
        pts += [(x + w, y - h * 0.6), (x + w, y)]
        self.poly(pts, fill, ol)

    def finish(self, ambient=0.35, vignette=0.55, grain=6, tint=None):
        W, H = self.W, self.H
        base = np.asarray(self.img.convert("RGB"), np.float32) / 255.0
        lightmap = np.full((H, W), 1.0 - ambient, np.float32)
        add = np.zeros((H, W, 3), np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        for (x, y, r, col, s) in self.lights:
            X, Y, Rr = x * self.k, y * self.k, r * self.k
            d2 = ((xx - X) ** 2 + (yy - Y) ** 2) / (Rr * Rr)
            g = np.exp(-d2 * 2.2) * s
            lightmap += g * ambient * 1.3
            c = np.array(hexc(col)[:3], np.float32) / 255.0
            add += g[..., None] * c[None, None, :] * 0.12
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.41
        vig = 1 - vignette * np.clip(d, 0, 1) ** 2.0
        out = base * np.clip(lightmap, 0, 1.25)[..., None] * vig[..., None] + add
        if tint:
            t = np.array(hexc(tint)[:3], np.float32) / 255.0
            out = out * (0.85 + 0.15 * t)
        if grain:
            out += np.random.default_rng(5).normal(0, grain / 255.0, (H, W, 1)).astype(np.float32)
        return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGB")


# ============================================================================ sets
def study_night(s):
    s.grad(0, 0, 1920, 860, "#1d2638", "#2a3348")
    s.rect(0, 600, 1920, 860, "#232b3d", ol=False)
    s.line([(0, 600), (1920, 600)], "#151b28", 6)
    s.window_blinds(1180, 120, 560, 420)
    s.frame(260, 150, 420, 300, kind="map")
    s.clock(860, 170)
    s.bookshelf(20, 260, 200, 600)
    s.rect(0, 860, 1920, 1080, "#1a1414", ol=False)
    s.desk(380, 760, 1160, 70, "#4a3020")
    s.banker_lamp(620, 760)
    for k in range(3):
        s.rect(900 + k * 40, 740 - k * 6, 1080 + k * 40, 760 - k * 6, "#efe6d0", w=2)
    s.rect(1250, 700, 1330, 760, "#b8902a", w=3)
    return dict(ambient=0.5, vignette=0.6)


def office_day(s):
    s.grad(0, 0, 1920, 800, "#e9e2d2", "#d9d0bd")
    s.rect(0, 800, 1920, 1080, "#b9a98e", ol=False)
    s.line([(0, 800), (1920, 800)], "#8a7a62", 6)
    for x in (300, 820, 1340):
        s.window_blinds(x, 120, 380, 360, sky=("#9fc7e6", "#d8ecf6"), city=False)
    s.rect(1500, 520, 1840, 760, "#f7f7f4", w=4)
    for k in range(4):
        s.line([(1530, 560 + k * 40), (1720 - k * 30, 560 + k * 40)], "#3a5f8a", 4)
    s.plant(180, 800, 1.2)
    s.light(960, 200, 900, "#fff4d6", 0.5)
    return dict(ambient=0.18, vignette=0.4)


def hallway(s):
    s.rect(0, 0, 1920, 1080, "#141820", ol=False)
    s.poly([(0, 0), (760, 380), (760, 700), (0, 1080)], "#232a36", ol=False)
    s.poly([(1920, 0), (1160, 380), (1160, 700), (1920, 1080)], "#1f2530", ol=False)
    s.poly([(0, 1080), (760, 700), (1160, 700), (1920, 1080)], "#2a2a2e", ol=False)
    s.rect(760, 380, 1160, 700, "#0d1016", ol=False)
    for k, t in enumerate((0.15, 0.45, 0.75)):
        x = 960 + (0 - 960) * (1 - t) * 0.0
        y = 380 * t + 0 * (1 - t)
        s.rect(900 - 120 * (1 - t), y + 10, 1020 + 120 * (1 - t), y + 24, "#e9e2c4", ol=False)
        s.light(960, y + 200 + 300 * (1 - t), 320 * (1.4 - t), "#e9f0ff", 0.8)
    for side in (-1, 1):
        for t in (0.3, 0.6):
            x = 960 + side * (200 + 760 * (1 - t))
            s.rect(x - 40 * (1 - t) - 30, 420 - 300 * (1 - t), x + 40 * (1 - t) + 30, 690 + 300 * (1 - t), "#3a2e26", w=3)
    return dict(ambient=0.55, vignette=0.7)


def company_hall(s):
    s.grad(0, 0, 1920, 780, "#5a3a24", "#4a2e1c")
    for x in range(0, 1920, 240):
        s.rect(x + 20, 420, x + 220, 740, "#6a4630", w=3)
    s.rect(0, 380, 1920, 410, "#3a2416", ol=False)
    s.frame(300, 100, 260, 260, kind="portrait")
    s.frame(1360, 100, 260, 260, kind="portrait")
    s.rect(780, 80, 1140, 330, "#f2efe6", w=5)
    for k in range(6):
        s.rect(780, 80 + k * 42, 1140, 80 + k * 42 + 21, "#c0322b", ol=False)
    s.rect(780, 80, 930, 206, "#f2efe6", ol=False)
    s.rect(845, 80, 865, 206, "#c0322b", ol=False)
    s.rect(780, 133, 930, 153, "#c0322b", ol=False)
    s.rect(0, 780, 1920, 1080, "#3a2618", ol=False)
    for x in (560, 1360):
        s.line([(x, 0), (x, 60)], OL, 4)
        s.ell(x, 80, 70, 24, "#c9a227", w=3)
        s.light(x, 140, 420, "#ffd98a", 0.85)
    return dict(ambient=0.45, vignette=0.55)


def mughal_court(s):
    s.grad(0, 0, 1920, 760, "#e8b58a", "#d99a6a")
    for k in range(5):
        x = 60 + k * 380
        s.rect(x - 30, 120, x + 30, 760, "#f3e6cc", w=3)
        s.arch(x + 40, 760, 300, 560, "#b8603a")
        s.arch(x + 70, 760, 240, 470, "#8a3f22")
    s.rect(0, 60, 1920, 120, "#c9784a", w=3)
    for x in range(0, 1920, 64):
        s.poly([(x, 120), (x + 32, 150), (x + 64, 120)], "#a85a32", w=2)
    s.rect(0, 760, 1920, 1080, "#efe2c8", ol=False)
    for k in range(1, 6):
        s.line([(0, 760 + k * 60), (1920, 760 + k * 60)], "#d6c6a2", 3)
    s.poly([(600, 760), (1320, 760), (1600, 1080), (320, 1080)], "#9a2a2a", w=3)
    s.poly([(640, 776), (1280, 776), (1540, 1080), (380, 1080)], "#b5362e", ol=False)
    s.rect(780, 600, 1140, 760, "#c9a227", w=4)
    s.rect(800, 520, 1120, 610, "#7a1f2b", w=3)
    s.poly([(760, 260), (1160, 260), (1100, 160), (820, 160)], "#c9a227", w=3)
    for x in (300, 960, 1620):
        s.line([(x, 0), (x, 200)], OL, 3)
        s.ell(x, 220, 22, 30, "#e8c547", w=3)
        s.light(x, 240, 300, "#ffcf6b", 0.8)
    s.light(960, 500, 700, "#fff1d0", 0.5)
    return dict(ambient=0.25, vignette=0.5)


def palace_room(s):
    s.grad(0, 0, 1920, 800, "#5a1416", "#3e0e10")
    for x in (0, 1660):
        s.rect(x, 0, x + 260, 820, "#8a1a1e", w=3)
        for k in range(4):
            s.line([(x + 40 + k * 60, 0), (x + 30 + k * 60, 820)], "#6a1214", 4)
    for x in (420, 1300):
        s.frame(x, 140, 200, 260, kind="portrait")
    s.rect(0, 800, 1920, 1080, "#2a1a12", ol=False)
    s.poly([(760, 800), (1160, 800), (1400, 1080), (520, 1080)], "#9c1c22", ol=False)
    s.rect(860, 360, 1060, 800, "#c9a227", w=4, r=60)
    s.rect(890, 400, 1030, 700, "#7a1f2b", w=3, r=40)
    s.light(960, 120, 600, "#ffd98a", 0.8)
    return dict(ambient=0.45, vignette=0.6)


def london_street(s):
    s.grad(0, 0, 1920, 640, "#8a97a8", "#c9c3b5")
    r = s.rnd
    x = -20
    while x < 1920:
        w = r.randint(220, 340)
        h = r.randint(380, 560)
        col = r.choice(["#8a4a3a", "#7a5a4a", "#9a7a5a", "#6a5a52"])
        s.rect(x, 780 - h, x + w, 780, col, w=3)
        s.poly([(x - 10, 780 - h), (x + w / 2, 780 - h - 70), (x + w + 10, 780 - h)], "#4a4040", w=3)
        for wy in range(780 - h + 40, 700, 110):
            for wx in range(x + 30, x + w - 60, 90):
                lit = r.random() < 0.35
                s.rect(wx, wy, wx + 50, wy + 70, "#f3d27a" if lit else "#2a3040", w=2)
                if lit:
                    s.light(wx + 25, wy + 35, 90, "#ffd98a", 0.5)
        s.rect(x + w / 2 - 34, 680, x + w / 2 + 34, 780, "#3a2a20", w=2)
        x += w + 6
    s.rect(0, 780, 1920, 1080, "#5a5452", ol=False)
    for k in range(0, 1920, 60):
        for j in range(800, 1080, 40):
            s.rect(k + (j // 40 % 2) * 30, j, k + (j // 40 % 2) * 30 + 54, j + 34, "#625b58", ol=False)
    for lx in (300, 1100, 1700):
        s.rect(lx - 7, 470, lx + 7, 900, "#1e1a1a", ol=False)
        s.poly([(lx - 26, 470), (lx + 26, 470), (lx + 16, 420), (lx - 16, 420)], "#2a2626", w=2)
        s.light(lx, 450, 260, "#ffd98a", 0.9)
    return dict(ambient=0.3, vignette=0.5)


def bazaar(s):
    s.grad(0, 0, 1920, 500, "#f1c48a", "#f6dcae")
    for k in range(4):
        x = 40 + k * 480
        s.rect(x, 300, x + 420, 820, "#d99a5a", w=3)
        s.arch(x + 60, 820, 300, 440, "#6a3a22")
        for j in range(6):
            s.poly([(x - 10 + j * 74, 300), (x + 64 + j * 74, 300), (x + 64 + j * 74, 360), (x - 10 + j * 74, 380)],
                   ["#c0322b", "#e8c547"][j % 2], w=2)
        for j, c in enumerate(["#d9822b", "#b3202a", "#e8c547", "#6a8a3a"]):
            s.ell(x + 110 + j * 70, 800, 34, 26, c, w=2)
    s.rect(0, 820, 1920, 1080, "#c9a072", ol=False)
    s.light(1500, 100, 900, "#fff1c0", 0.6)
    return dict(ambient=0.15, vignette=0.45)


def port(s):
    s.grad(0, 0, 1920, 560, "#f2b77a", "#f6d7a3")
    s.grad(0, 560, 1920, 820, "#4f8aa6", "#2a5d7a")
    for k in range(30):
        x = s.rnd.uniform(0, 1920)
        y = s.rnd.uniform(580, 800)
        s.line([(x, y), (x + 60, y)], "#ffffff66", 3)
    for x, sc in ((500, 1.0), (1150, 0.75), (1650, 0.55)):
        _ship(s, x, 640, 420 * sc)
    s.rect(0, 800, 1920, 1080, "#7a5233", ol=False)
    for k in range(0, 1920, 120):
        s.line([(k, 800), (k, 1080)], "#5e3e26", 4)
    for k in range(4):
        s.rect(60 + k * 130, 700, 180 + k * 130, 800, "#a57944", w=3)
    s.light(1500, 420, 500, "#fff1c0", 0.6)
    return dict(ambient=0.15, vignette=0.45)


def _ship(s, x, y, h):
    w = h * 1.2
    s.poly([(x - w / 2, y - h * .18), (x + w / 2, y - h * .2), (x + w * .38, y + h * .05), (x - w * .4, y + h * .05)], "#5a3a22", w=3)
    s.line([(x, y - h * .18), (x, y - h)], "#3a2414", 6)
    s.line([(x - w * .25, y - h * .18), (x - w * .25, y - h * .8)], "#3a2414", 5)
    s.poly([(x + 6, y - h * .95), (x + w * .3, y - h * .6), (x + 6, y - h * .3)], "#f3ead6", w=2)
    s.poly([(x - w * .25 + 4, y - h * .75), (x - w * .05, y - h * .5), (x - w * .25 + 4, y - h * .3)], "#f3ead6", w=2)
    s.poly([(x, y - h), (x + h * .15, y - h * .95), (x, y - h * .9)], "#c0322b", w=2)


def sea(s):
    s.grad(0, 0, 1920, 520, "#16223a", "#3a4a6a")
    s.ell(1500, 160, 50, 50, "#fff3d0", ol=False)
    s.light(1500, 160, 300, "#e9f0ff", 0.7)
    s.grad(0, 520, 1920, 1080, "#1d3a52", "#0d1a28")
    for k in range(60):
        x, y = s.rnd.uniform(0, 1920), s.rnd.uniform(540, 1060)
        s.line([(x, y), (x + 40 + (y - 520) / 8, y)], "#ffffff40", 3)
    _ship(s, 900, 700, 520)
    return dict(ambient=0.35, vignette=0.6)


def battlefield(s):
    s.grad(0, 0, 1920, 620, "#3a2a3a", "#e07a3a")
    for k, c in enumerate(("#5a4a3a", "#4a3a2a", "#3a2c1e")):
        pts = [(0, 1080)] + [(i * 160, 620 + k * 40 - s.rnd.uniform(0, 60)) for i in range(13)] + [(1920, 1080)]
        s.poly(pts, c, ol=False)
    for x in (300, 520, 1500):
        s.poly([(x - 90, 720), (x + 90, 720), (x, 600)], "#e9dcc0", w=3)
    for x in (900, 1300):
        s.rect(x - 70, 760, x + 40, 790, "#2a2a30", w=2)
        s.ell(x - 50, 800, 26, 26, "#5a3a22", w=2)
    for _ in range(6):
        x, y = s.rnd.uniform(0, 1920), s.rnd.uniform(500, 760)
        s.light(x, y, 160, "#ffb060", 0.8)
    smoke = Image.new("RGBA", s.img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for _ in range(14):
        x, y, r = s.rnd.uniform(0, s.W), s.rnd.uniform(.35, .7) * s.H, s.rnd.uniform(.05, .11) * s.W
        sd.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(80, 70, 70, 110))
    s.img.alpha_composite(smoke.filter(ImageFilter.GaussianBlur(s.W * .015)))
    s.d = ImageDraw.Draw(s.img)
    return dict(ambient=0.3, vignette=0.55)


def war_tent(s):
    s.grad(0, 0, 1920, 1080, "#5a4630", "#3a2c1e")
    s.poly([(0, 0), (960, 0), (0, 700)], "#6a543a", ol=False)
    s.poly([(1920, 0), (960, 0), (1920, 700)], "#62503a", ol=False)
    s.line([(960, 0), (960, 760)], "#3a2a1a", 10)
    s.rect(0, 780, 1920, 1080, "#2e2216", ol=False)
    s.rect(500, 700, 1420, 780, "#6a4a2a", w=4)
    s.rect(620, 660, 1300, 712, "#e3d2a6", w=3)
    for k in range(5):
        s.ell(700 + k * 120, 685, 8, 8, "#c0322b", w=2)
    s.line([(1100, 120), (1100, 260)], OL, 3)
    s.ell(1100, 290, 30, 40, "#e8c547", w=3)
    s.light(1100, 300, 600, "#ffcf6b", 1.0)
    return dict(ambient=0.55, vignette=0.6)


def village(s):
    s.grad(0, 0, 1920, 600, "#e8c48a", "#f3dcae")
    s.ell(1500, 200, 80, 80, "#fff3d0", ol=False)
    s.rect(0, 600, 1920, 1080, "#c4a060", ol=False)
    for k in range(4):
        x = 120 + k * 460
        s.rect(x, 420, x + 300, 640, "#b07a4a", w=3)
        s.poly([(x - 40, 420), (x + 150, 300), (x + 340, 420)], "#c9a35a", w=3)
        s.rect(x + 120, 520, x + 180, 640, "#4a2e18", w=2)
    s.ell(1700, 760, 80, 26, "#8a8a8a", w=3)
    for _ in range(40):
        x, y = s.rnd.uniform(0, 1920), s.rnd.uniform(680, 1060)
        s.line([(x, y), (x + 40, y - 4)], "#a8844a", 3)
    s.light(1500, 200, 900, "#fff1c0", 0.5)
    return dict(ambient=0.12, vignette=0.45)


def fort(s):
    s.grad(0, 0, 1920, 560, "#8cc3e0", "#d9ecf2")
    s.rect(0, 420, 1920, 800, "#b8603a", w=3)
    for x in range(0, 1920, 70):
        s.rect(x, 390, x + 44, 420, "#b8603a", w=2)
    for x in (300, 960, 1620):
        s.rect(x - 130, 250, x + 130, 800, "#a8502f", w=3)
        s.poly([(x - 110, 250), (x + 110, 250), (x, 120)], "#f1e2c4", w=3)
        s.arch(x - 50, 800, 100, 300, "#4a2414")
    s.rect(0, 800, 1920, 1080, "#a8784a", ol=False)
    return dict(ambient=0.08, vignette=0.4)


def prison(s):
    s.grad(0, 0, 1920, 820, "#2a2e36", "#20242a")
    for k in range(0, 1920, 160):
        for j in range(0, 820, 80):
            s.rect(k + (j // 80 % 2) * 80, j, k + (j // 80 % 2) * 80 + 156, j + 76, "#2e333c", w=2)
    s.rect(820, 160, 1100, 360, "#111418", w=4)
    for k in range(5):
        s.line([(850 + k * 55, 160), (850 + k * 55, 360)], "#5a5f6a", 10)
    s.light(960, 260, 500, "#cfe0ff", 0.9)
    s.rect(0, 820, 1920, 1080, "#1a1c20", ol=False)
    return dict(ambient=0.6, vignette=0.7)


def parliament(s):
    s.grad(0, 0, 1920, 640, "#4a3222", "#3a2618")
    for x in range(0, 1920, 120):
        s.rect(x + 10, 100, x + 110, 560, "#5a3c28", w=2)
        s.arch(x + 20, 300, 80, 180, "#2a1a10", ol=False)
    for k in range(3):
        y = 640 + k * 110
        s.rect(0, y, 1920, y + 70, "#2f5d3a", w=3)
        s.rect(0, y + 70, 1920, y + 110, "#3a2618", ol=False)
    s.light(960, 80, 900, "#ffe3a0", 0.6)
    return dict(ambient=0.4, vignette=0.55)


def senate(s):
    s.grad(0, 0, 1920, 820, "#5a1a22", "#3a1016")
    for k in range(0, 1920, 90):
        s.line([(k, 0), (k + 10, 820)], "#4a1218", 6)
    s.ell(960, 300, 170, 170, "#c9a227", w=5)
    s.ell(960, 300, 130, 130, "#1d2a4a", w=3)
    s.text(960, 300, "SEAL", 46, "#e8c547")
    for x in (640, 1280):
        s.line([(x, 160), (x, 760)], "#c9a227", 8)
        s.poly([(x, 170), (x + 130, 190), (x + 130, 300), (x, 280)], "#efe9dc", w=2)
    s.rect(0, 820, 1920, 1080, "#2a1a14", ol=False)
    s.rect(660, 640, 1260, 840, "#5a3a24", w=4)
    s.light(960, 200, 700, "#ffe3a0", 0.6)
    return dict(ambient=0.4, vignette=0.55)


def black(s):
    s.rect(0, 0, 1920, 1080, "#050505", ol=False)
    return dict(ambient=0.0, vignette=0.0, grain=0)


def desk_top(s):
    s.grad(0, 0, 1920, 1080, "#3a2a1e", "#2a1d14")
    for k in range(0, 1080, 70):
        s.line([(0, k), (1920, k + 20)], "#33241a", 4)
    s.light(960, 480, 900, "#ffe3a0", 0.9)
    return dict(ambient=0.5, vignette=0.65)


def corkboard(s):
    s.grad(0, 0, 1920, 1080, "#a87a4a", "#8a5f36")
    s.rect(0, 0, 1920, 50, "#5a3a22", ol=False)
    s.rect(0, 1030, 1920, 1080, "#5a3a22", ol=False)
    return dict(ambient=0.35, vignette=0.6)


def map_room(s):
    s.grad(0, 0, 1920, 1080, "#14202e", "#0d141e")
    s.light(960, 400, 900, "#bfe0ff", 0.5)
    return dict(ambient=0.3, vignette=0.6)


SETS = {k: v for k, v in dict(globals()).items() if callable(v) and not k.startswith("_") and k not in
        ("Set", "hexc", "shade", "mix", "font", "make")}
FLOORS = {"black": 0.9, "desk_top": 0.95, "corkboard": 0.95}


def floor(name):
    return FLOORS.get(name, 0.86)


@functools.lru_cache(maxsize=24)
def make(name, W, H, seed=0):
    fn = SETS.get(name)
    if fn is None:
        raise KeyError(f"unknown set '{name}'. Use one of: {', '.join(SETS)}")
    s = Set(W, H, seed or (sum(map(ord, name)) % 997))
    cfg = fn(s) or {}
    return s.finish(cfg.get("ambient", 0.35), cfg.get("vignette", 0.55), cfg.get("grain", 5))


if __name__ == "__main__":
    import sys
    names = list(SETS)
    tw, th = 480, 270
    cols = 4
    sheet = Image.new("RGB", (cols * tw, ((len(names) + cols - 1) // cols) * th))
    for i, n in enumerate(names):
        sheet.paste(make(n, tw, th), ((i % cols) * tw, (i // cols) * th))
        ImageDraw.Draw(sheet).text(((i % cols) * tw + 6, (i // cols) * th + 6), n, fill=(255, 255, 0))
    sheet.save(sys.argv[1] if len(sys.argv) > 1 else "rooms.jpg")
