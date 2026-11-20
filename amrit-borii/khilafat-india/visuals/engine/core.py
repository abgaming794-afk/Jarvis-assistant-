"""Shared 2D-flat drawing core (skia) for the AMRIT BORI 'Naya Axis' documentary.
Design space is 1920x1080; everything is drawn with canvas.scale(SC) to the 4K surface."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import json, math
import numpy as np
import skia
from shapely.geometry import shape, Polygon, MultiPolygon

VERTICAL = _os.environ.get("AB_ORIENT", "landscape") == "vertical"   # AB_ORIENT=vertical -> Shorts (9:16)
W4, H4 = (2160, 3840) if VERTICAL else (3840, 2160)
if _os.environ.get("AB_PREVIEW") == "720": W4, H4 = (720, 1280) if VERTICAL else (1280, 720)   # fast review renders
if _os.environ.get("AB_PREVIEW") == "480": W4, H4 = (480, 854) if VERTICAL else (854, 480)
DW, DH = (1080, 1920) if VERTICAL else (1920, 1080)
SC = W4 / DW

GEO = MAPDATA + "countries10m.geojson"
OFFICIAL = PROJ + "visuals/engine/india_official.geojson.json"
FT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

def hexc(h, a=255):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(ch * 2 for ch in h)
    return skia.ColorSetARGB(int(max(0, min(255, a))), int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

PAL = dict(ocean="#0F1B2D", land="#2B3A4F", border="#3E5068", CHN="#DE2910", RUS="#2C5DAA",
           IRN="#239F40", PRK="#9B1B30", IND="#FF9933", axis="#E63946", yel="#FFD166", txt="#F1FAEE", muted="#8A9BB0")

_TF = {}
def font(path, size):
    if path not in _TF:
        _TF[path] = skia.Typeface.MakeFromFile(path)
    return skia.Font(_TF[path], size)

def paint(col, a=255, stroke=None, cap_round=False, blur=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(hexc(col, a) if isinstance(col, str) else col)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        if cap_round: p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p

# ---------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease_io(x): return 0.5 - 0.5 * math.cos(math.pi * clamp(x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3
def back(x, s=1.70158):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    x = x - 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, k): return a + (b - a) * k

# ---------------- text
def text(c, s, x, y, size, col="#F1FAEE", fpath=FT_BLACK, align="l", a=255, shadow=False):
    f = font(fpath, size)
    w = f.measureText(s)
    if align == "c": x -= w / 2
    elif align == "r": x -= w
    if shadow:
        c.drawString(s, x + size * 0.04, y + size * 0.06, f, paint("#000000", int(a * 0.55)))
    c.drawString(s, x, y, f, paint(col, a))
    return w

def text_w(s, size, fpath=FT_BLACK): return font(fpath, size).measureText(s)

# ---------------- shapes
def rrect(c, l, t, r, b, rad, col, a=255, shadow=0):
    if shadow:
        c.drawRoundRect(skia.Rect(l + shadow * 0.4, t + shadow * 0.8, r + shadow * 0.4, b + shadow * 0.8), rad, rad,
                        paint("#000000", int(140 * a / 255), blur=shadow))
    c.drawRoundRect(skia.Rect(l, t, r, b), rad, rad, paint(col, a))

def pill(c, s, cx, cy, size, bg, fg="#F1FAEE", a=255, padx=None, fpath=FT_BLACK, shadow=10):
    w = text_w(s, size, fpath); padx = padx or size * 0.55; h = size * 1.45
    rrect(c, cx - w / 2 - padx, cy - h / 2, cx + w / 2 + padx, cy + h / 2, h / 2, bg, a, shadow)
    text(c, s, cx, cy + size * 0.36, size, fg, fpath, "c", a)
    return w + 2 * padx

# ---------------- images
def sk_image(pil_img):
    arr = np.asarray(pil_img.convert("RGBA"), dtype=np.uint8).copy()
    return skia.Image.fromarray(arr, colorType=skia.ColorType.kRGBA_8888_ColorType)

SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
def draw_img(c, img, l, t, r, b, a=255, src=None):
    p = skia.Paint(AntiAlias=True); p.setAlphaf(a / 255)
    src = src or skia.Rect(0, 0, img.width(), img.height())
    c.drawImageRect(img, src, skia.Rect(l, t, r, b), SAMP, p)

# ---------------- map
def merc_y(lat):
    lat = max(-85, min(85, lat))
    return math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))

ORIGIN = (116.3913, merc_y(39.9031))   # Tiananmen Square: path coords are relative to this (float precision)

def _poly_path(geom, tol):
    path = skia.Path(); path.setFillType(skia.PathFillType.kEvenOdd)
    g = geom.simplify(tol, preserve_topology=False) if tol else geom
    polys = [g] if isinstance(g, Polygon) else list(getattr(g, "geoms", []))
    for p in polys:
        if p.is_empty: continue
        for ring in [p.exterior] + list(p.interiors):
            pts = [(x - ORIGIN[0], -(merc_y(y) - ORIGIN[1])) for x, y in ring.coords]
            if len(pts) < 3: continue
            path.moveTo(*pts[0])
            for q in pts[1:]: path.lineTo(*q)
            path.close()
    return path

class WorldMap:
    LEVELS = [(0, 0.12), (12, 0.04), (40, 0.01), (150, 0.002), (600, 0.0004), (3000, 0.0)]
    def __init__(self):
        feats = json.load(open(GEO))["features"]
        off = {k: shape(v) for k, v in json.load(open(OFFICIAL)).items()}
        repl = {"IND": off["IND_OFFICIAL"], "PAK": off["PAK_ADMIN"], "CHN": off["CHN_ADMIN"]}
        self.geoms = {}
        for f in feats:
            code = f["properties"].get("ADM0_A3")
            g = repl.get(code, shape(f["geometry"]))
            if code in self.geoms: g = self.geoms[code].union(g)
            self.geoms[code] = g
        self.cache = {}
    def paths(self, scale):
        lvl = max(i for i, (s, _) in enumerate(self.LEVELS) if scale >= s)
        if lvl not in self.cache:
            tol = self.LEVELS[lvl][1]
            self.cache[lvl] = {k: _poly_path(g, tol) for k, g in self.geoms.items()}
        return self.cache[lvl]

def cam_xy(lon, lat):
    return lon - ORIGIN[0], -(merc_y(lat) - ORIGIN[1])

def to_screen(cam, lon, lat):
    """cam = (center_lon, center_lat, scale px-per-degree in design space)"""
    cx, cy = cam_xy(cam[0], cam[1]); x, y = cam_xy(lon, lat)
    return DW / 2 + (x - cx) * cam[2], DH / 2 + (y - cy) * cam[2]

def draw_map(c, wm, cam, fills=None, alpha=255, border=True):
    fills = fills or {}
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    c.save()
    c.translate(DW / 2, DH / 2); c.scale(s, s); c.translate(-cx, -cy)
    P = wm.paths(s)
    land = paint(PAL["land"], alpha)
    bp = paint(PAL["border"], alpha, stroke=1.4 / s)
    for code, path in P.items():
        f = fills.get(code)
        if f is None:
            c.drawPath(path, land)
        else:
            col, a = (f if isinstance(f, tuple) else (f, 255))
            c.drawPath(path, land)
            if a > 0: c.drawPath(path, paint(col, int(a * alpha / 255)))
        if border: c.drawPath(path, bp)
    c.restore()

# ---------------- film grain / vignette
_rng = np.random.default_rng(7)
_GRAIN = [(_rng.integers(0, 255, (540, 960), dtype=np.uint8)) for _ in range(6)]
_GR_IMG = []
def grain(c, t, amount=10):
    if not _GR_IMG:
        for g in _GRAIN:
            a = np.zeros((540, 960, 4), np.uint8); a[..., 0:3] = g[..., None]; a[..., 3] = 255
            _GR_IMG.append(skia.Image.fromarray(a, colorType=skia.ColorType.kRGBA_8888_ColorType))
    img = _GR_IMG[int(t * 24) % len(_GR_IMG)]
    p = skia.Paint(); p.setAlphaf(amount / 255); p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(img, skia.Rect(0, 0, 960, 540), skia.Rect(0, 0, DW, DH), skia.SamplingOptions(), p)

def vignette(c, strength=150):
    shader = skia.GradientShader.MakeRadial(skia.Point(DW / 2, DH / 2), DW * 0.75,
                                            [skia.ColorSetARGB(0, 0, 0, 0), skia.ColorSetARGB(strength, 0, 0, 0)], [0.55, 1.0])
    p = skia.Paint(); p.setShader(shader); c.drawRect(skia.Rect(0, 0, DW, DH), p)

import os as _os
def footnote(c, s, a=255):
    if _os.environ.get("FOOTNOTE_TOP") == "1":
        w = text_w(s, 19, FT_SEMI)
        c.drawRoundRect(skia.Rect(26, 18, 54 + w, 50), 10, 10, paint("#0F1B2D", int(150 * a / 255)))
        text(c, s, 40, 40, 19, "#9FB0C6", FT_SEMI, "l", a)
    else:
        text(c, s, 40, DH - 30, 20, PAL["muted"], FT_SEMI, "l", a)

def watermark(c, logo_img, a=150):
    draw_img(c, logo_img, DW - 112, DH - 112, DW - 32, DH - 32, a)
