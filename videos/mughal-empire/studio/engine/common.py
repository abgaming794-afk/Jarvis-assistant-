"""Shared helpers: paths, fonts, colours, easing, drawing pen."""
import os, json, math, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ENGINE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(ENGINE)
FONTS = os.path.join(SKILL, "assets", "fonts")
DATA = os.path.join(ENGINE, "data")

OUTLINE = (42, 26, 20, 255)


def hexc(c, a=255):
    """'#rrggbb' / (r,g,b) / (r,g,b,a) -> RGBA tuple."""
    if c is None:
        return None
    if isinstance(c, (tuple, list)):
        return tuple(c) if len(c) == 4 else (c[0], c[1], c[2], a)
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


def shade(c, f):
    """Darken (f<1) or lighten (f>1) a colour."""
    c = hexc(c)
    if f <= 1:
        return (int(c[0] * f), int(c[1] * f), int(c[2] * f), c[3])
    g = f - 1
    return (int(c[0] + (255 - c[0]) * g), int(c[1] + (255 - c[1]) * g), int(c[2] + (255 - c[2]) * g), c[3])


def mix(a, b, t):
    a, b = hexc(a), hexc(b)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


@functools.lru_cache(maxsize=64)
def font(size, weight="Black"):
    names = {"Black": "Montserrat-Black.ttf", "ExtraBold": "Montserrat-ExtraBold.ttf", "Bold": "Montserrat-Bold.ttf"}
    p = os.path.join(FONTS, names.get(weight, weight))
    if not os.path.exists(p):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        return ImageFont.truetype(p, max(6, int(size)))
    except OSError:
        return ImageFont.load_default()


@functools.lru_cache(maxsize=16)
def serif(size):
    p = os.path.join(FONTS, "TypoGrotesk-Bold.otf")
    if os.path.exists(p):
        return ImageFont.truetype(p, max(6, int(size)))
    return font(size, "Bold")


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp(t)
    return 3 * t * t - 2 * t * t * t


def back_out(t, s=1.70158):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------- pen
class Pen:
    """Draws in a fixed design space (units) onto a supersampled RGBA canvas."""

    def __init__(self, W, H, s, lw=6.0, outline=OUTLINE, ox=0.0, oy=0.0):
        self.W, self.H, self.s = W, H, s
        self.ox, self.oy = ox, oy
        self.img = Image.new("RGBA", (max(1, int(W * s)), max(1, int(H * s))), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.lw = lw
        self.ol = outline

    def _w(self, w):
        return max(1, int(round((self.lw if w is None else w) * self.s)))

    def box(self, cx, cy, rx, ry):
        s, ox, oy = self.s, self.ox, self.oy
        return [(cx - rx + ox) * s, (cy - ry + oy) * s, (cx + rx + ox) * s, (cy + ry + oy) * s]

    def ell(self, cx, cy, rx, ry, fill, ol=True, w=None):
        self.d.ellipse(self.box(cx, cy, rx, ry), fill=hexc(fill), outline=self.ol if ol else None,
                       width=self._w(w) if ol else 0)

    def poly(self, pts, fill, ol=True, w=None):
        s = self.s
        P = [((x + self.ox) * s, (y + self.oy) * s) for x, y in pts]
        self.d.polygon(P, fill=hexc(fill))
        if ol:
            self.d.line(P + [P[0]], fill=self.ol, width=self._w(w), joint="curve")
            r = self._w(w) / 2
            for x, y in P:
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=self.ol)

    def line(self, pts, fill=None, w=None, round_ends=True):
        s = self.s
        P = [((x + self.ox) * s, (y + self.oy) * s) for x, y in pts]
        col = hexc(fill) if fill is not None else self.ol
        W = self._w(w)
        self.d.line(P, fill=col, width=W, joint="curve")
        if round_ends:
            r = W / 2
            for x, y in (P[0], P[-1]):
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def capsule(self, p1, p2, w, fill, ol=True):
        if ol:
            self.line([p1, p2], self.ol, w + 2 * self.lw)
        self.line([p1, p2], fill, w)

    def rrect(self, x0, y0, x1, y1, r, fill, ol=True, w=None):
        s, ox, oy = self.s, self.ox, self.oy
        self.d.rounded_rectangle([(x0 + ox) * s, (y0 + oy) * s, (x1 + ox) * s, (y1 + oy) * s], radius=r * s, fill=hexc(fill),
                                 outline=self.ol if ol else None, width=self._w(w) if ol else 0)

    def arc(self, cx, cy, rx, ry, a0, a1, fill=None, w=None):
        self.d.arc(self.box(cx, cy, rx, ry), a0, a1, fill=hexc(fill) if fill else self.ol, width=self._w(w))

    def chord(self, cx, cy, rx, ry, a0, a1, fill, ol=True, w=None):
        self.d.chord(self.box(cx, cy, rx, ry), a0, a1, fill=hexc(fill), outline=self.ol if ol else None,
                     width=self._w(w) if ol else 0)

    def pie(self, cx, cy, rx, ry, a0, a1, fill, ol=True, w=None):
        self.d.pieslice(self.box(cx, cy, rx, ry), a0, a1, fill=hexc(fill), outline=self.ol if ol else None,
                        width=self._w(w) if ol else 0)

    def glow(self, cx, cy, r, color, alpha=120, blur=None):
        """Soft additive-looking glow blob (alpha composited)."""
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        c = hexc(color, alpha)
        d.ellipse(self.box(cx, cy, r, r), fill=c)
        layer = layer.filter(ImageFilter.GaussianBlur((blur or r * 0.5) * self.s))
        self.img.alpha_composite(layer)

    def overlay(self):
        """Returns (layer, draw) for semi-transparent drawing; call merge(layer) after."""
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        return layer, ImageDraw.Draw(layer)

    def merge(self, layer):
        self.img.alpha_composite(layer)
        self.d = ImageDraw.Draw(self.img)

    def result(self, out_h=None):
        if out_h is None:
            return self.img
        w = max(1, int(self.img.width * out_h / self.img.height))
        return self.img.resize((w, int(out_h)), Image.LANCZOS)


def load_json(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_json(p, obj):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def ffmpeg_bin():
    import shutil
    for name in ("ffmpeg",):
        p = shutil.which(name)
        if p:
            return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("ffmpeg not found: run doctor.py --fix")


def text_size(draw, txt, fnt, stroke=0):
    b = draw.textbbox((0, 0), txt, font=fnt, stroke_width=stroke)
    return b[2] - b[0], b[3] - b[1], b
