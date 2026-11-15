"""AMRIT BORI - 'Arab Khilafat India kyun nahi jeet paayi?' storyboard (4K60 10-bit).
Scenes are keyed to VO units found by their text (U("prefix")), so the same code works with placeholder timing
(voice/placeholder_units.py) and with the real aligned VO (voice/align_full.py -> full_units.json).
CLI:  still <outdir> t1 t2 ...   |  chunk i0 i1 out.mp4  |  sfx  |  demo_end"""
import os, sys, math, json, subprocess
os.environ.setdefault("AB_PROJECT", "khilafat-india"); os.environ.setdefault("FOOTNOTE_TOP", "1")
import numpy as np, skia
from PIL import Image, ImageFilter
from core import *
from widgets import *
from shapely.geometry import box, Polygon as SPoly
from shapely.ops import unary_union

ROOT = PROJ
UN = json.load(open(ROOT + "voice/full_units.json"))["units"]
SIL = [tuple(map(float, l.split())) for l in open(ROOT + "voice/full_sil.tsv")]
def U(prefix, occ=0):
    """index of the unit whose text starts with prefix (case-insensitive)"""
    hits = [i for i, u in enumerate(UN) if u["text"].lower().startswith(prefix.lower())]
    if len(hits) <= occ: raise KeyError(prefix)
    return hits[occ]
def us(i): return UN[i]["start"]
def ue(i): return UN[i]["end"]
def vin(i): return us(i) - 0.12
def kw(i, word, occ=0):
    txt = UN[i]["text"]; low = txt.lower(); p = -1
    for _ in range(occ + 1): p = low.find(word.lower(), p + 1)
    if p < 0: return us(i)
    est = us(i) + (ue(i) - us(i)) * p / max(1, len(txt))
    best = None
    for a, b in SIL:
        if us(i) < b < ue(i) and abs(b - est) < 0.35 and (best is None or abs(b - est) < abs(best - est)): best = b
    return (best if best else est) - 0.05

HOSTSEG = {"H1": (41.6, 53.9), "H2": (282.1, 291.7), "H3": (611.3, 619.45), "H4": (627.0, 633.6)}   # = host/prep_host.py
GREEN = "#2FA36B"; GREEN_D = "#1F7A4F"; SAFF = "#FF9933"; RED = PAL["axis"]; YEL = PAL["yel"]; NAVY = PAL["ocean"]

# ------------------------------------------------------------------ geography
PL = dict(spain=(-4.0, 40.0), damascus=(36.29, 33.51), medina=(39.61, 24.47), mecca=(39.83, 21.42), sindh=(68.6, 26.0),
          debal=(67.5, 24.75), kabul=(69.17, 34.53), india=(79.0, 22.0), atlantic=(-14.0, 34.0), samarkand=(66.96, 39.65),
          mahfuza=(68.9, 25.5), arabia=(45.0, 24.0), thane=(72.97, 19.2), bharuch=(72.98, 21.7))
WM = None; CALIPH = None; SINDH = None; IBERIA = None
def S(cam, key): return to_screen(cam, *PL[key])

def geo_path(g, tol=0.02):
    from core import _poly_path
    return _poly_path(g, tol)

def load_geo():
    """approximate Umayyad extent at its peak (c. 740), built from modern borders -> labelled 'andaazan naksha'"""
    global WM, CALIPH, SINDH, IBERIA, sindh_poly
    if WM is not None: return
    WM = WorldMap()
    G = WM.geoms
    full = ["ESP", "PRT", "MAR", "DZA", "TUN", "LBY", "EGY", "SAU", "YEM", "OMN", "ARE", "QAT", "BHR", "KWT", "IRQ", "SYR",
            "JOR", "LBN", "ISR", "PSX", "IRN", "TKM", "UZB", "AZE", "ARM"]
    parts = [G[k] for k in full if k in G]
    parts.append(G["AFG"].intersection(unary_union([box(60, 35.6, 75, 39), box(60, 29, 63.6, 39)])))   # Herat/Balkh, NOT Kabul-Zabul
    sindh_poly = SPoly([(66.65, 25.45), (67.15, 26.1), (67.4, 27.0), (67.3, 27.8), (68.0, 28.35), (68.9, 28.55), (69.6, 28.45),
                        (70.1, 28.1), (70.6, 27.7), (71.1, 27.0), (70.9, 26.4), (70.7, 25.7), (71.15, 24.6), (70.0, 24.15),
                        (68.8, 23.65), (68.2, 23.6), (67.3, 24.25), (66.85, 24.8)])
    multan_poly = SPoly([(69.6, 28.45), (70.1, 28.1), (71.0, 28.6), (72.0, 29.4), (71.9, 30.6), (70.4, 30.6), (69.9, 29.5)])
    makran = box(61.0, 24.5, 67.3, 27.9)
    parts.append(G["PAK"].intersection(unary_union([sindh_poly.buffer(0.15), multan_poly, makran])))   # Makran + Sindh + Multan (andaazan)
    parts.append(G["TJK"].intersection(box(66, 37, 70, 41)))
    CALIPH = unary_union(parts).buffer(0)
    SINDH = G["PAK"].intersection(sindh_poly.buffer(0.15))
    IBERIA = unary_union([G["ESP"], G["PRT"]])
    U_ = lambda ks: unary_union([G[k] for k in ks if k in G])
    REG.update({"caliph": CALIPH, "sindh": SINDH, "iberia": IBERIA, "india": G["IND"],
                "arabia": U_(["SAU", "YEM", "OMN", "ARE", "QAT", "KWT", "BHR"]), "syria": U_(["SYR", "LBN", "JOR", "ISR", "PSX"]),
                "iraq": G["IRQ"], "centralasia": U_(["UZB", "TKM", "TJK"]),
                "c_asia": CALIPH.intersection(box(34, 0, 80, 50)), "c_africa": CALIPH.intersection(box(-20, 0, 33.5, 31.6)),
                "c_europe": CALIPH.intersection(box(-20, 35.8, 10, 50))})
REG = {}

PATHS = {}
def gpath(name, scale):
    lvl = 0 if scale < 12 else (1 if scale < 60 else 2)
    key = (name, lvl)
    if key not in PATHS:
        g = REG[name]
        PATHS[key] = geo_path(g, (0.08, 0.02, 0.004)[lvl])
    return PATHS[key]

def draw_region(c, cam, name, col, a=255, stroke=None, glow=0):
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    c.save(); c.translate(DW / 2, DH / 2); c.scale(s, s); c.translate(-cx, -cy)
    p = gpath(name, s)
    if glow: c.drawPath(p, paint(col, int(a * 0.6), blur=glow / s * 0 + 0.0001) if False else paint(col, int(a * 0.35), stroke=glow / s))
    c.drawPath(p, paint(col, a))
    if stroke: c.drawPath(p, paint(stroke, int(a * 0.7), stroke=1.0 / s))
    c.restore()

def fly(c0, c1, k):
    """smooth camera move; zooms out a little in the middle for long moves (Google-Maps style)"""
    lon = lerp(c0[0], c1[0], k); lat = lerp(c0[1], c1[1], k)
    ls = lerp(math.log(c0[2]), math.log(c1[2]), k)
    d = math.hypot(c1[0] - c0[0], c1[1] - c0[1]) * min(c0[2], c1[2]) / DW
    dip = min(0.55, 0.35 * d) * math.sin(math.pi * k)
    return (lon, lat, math.exp(ls) * (1 - dip))

def camlerp(t, keys):
    cam = keys[0][2]
    for t0, t1, c0, c1 in keys:
        if t >= t0: cam = fly(c0, c1, ease_io(seg(t, t0, t1)))
    return cam

def bg(c, cam=None, fills=None, alpha=255):
    c.clear(hexc(NAVY))
    if cam: draw_map(c, WM, cam, fills or {}, alpha)

def dim(c, a): c.drawRect(skia.Rect(0, 0, DW, DH), paint(NAVY, int(a)))

# every highlighted place gets its own colour (user: "alag colour joro"); outlines are thin, no yellow glow
REGCOL = {"iberia": "#3A86FF", "centralasia": "#9B5DE5", "india": "#FF9933", "arabia": "#00BBF9", "syria": "#F15BB5",
          "sindh": "#FF6B6B", "iraq": "#F8961E", "c_asia": "#00BBF9", "c_africa": "#F8961E", "c_europe": "#3A86FF", "caliph": GREEN}
def lighten(h, f=0.45):
    h = h.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(int(v + (255 - v) * f) for v in (r, g, b))
def hl(c, cam, name, t, t0, col=None, fill=None, dur=99.0):
    """highlight a region when its name is spoken: own-colour fill fades in (soft breathing) + thin light outline"""
    k = seg(t, t0 - 0.1, t0 + 0.35) * (1 - seg(t, t0 + dur, t0 + dur + 0.4))
    if k <= 0: return
    fc = REGCOL.get(name, SAFF); pulse = 0.5 + 0.5 * math.sin((t - t0) * 4)
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    c.save(); c.translate(DW / 2, DH / 2); c.scale(s, s); c.translate(-cx, -cy)
    pth = gpath(name, s)
    c.drawPath(pth, paint(fc, int((190 + 40 * pulse) * k)))
    c.drawPath(pth, paint(lighten(fc), int(230 * k), stroke=1.2 / s))
    c.restore()

_BOUNDS = {}
def float_map(c, t, t0, name, ttl, sub, x, y, w=440, h=330, t1=None, fill=SAFF, pad=0.9, ctx=None):
    """floating 'map of that time' card: slides in on the spoken name, bobs gently, shows the region highlighted
    inside its wider context (ctx: extra degrees of context; default from region size)"""
    k = back(seg(t, t0 - 0.15, t0 + 0.45)); kout = seg(t, t1, t1 + 0.4) if t1 else 0
    if k <= 0 or kout >= 1: return
    al = int(255 * clamp(seg(t, t0 - 0.15, t0 + 0.2) * 1.4) * (1 - kout))
    if name not in _BOUNDS: _BOUNDS[name] = REG[name].bounds
    b0, b1, b2, b3 = _BOUNDS[name]; cl, ca = (b0 + b2) / 2, (b1 + b3) / 2
    span = max(b2 - b0, (b3 - b1) * 1.3) * (1 + 2 * pad) + (ctx or 0)
    cam = (cl, ca, (w - 20) / span)
    bob = math.sin((t - t0) * 2.2) * 6; ang = math.sin((t - t0) * 1.3) * 1.2 - 2 * (1 - clamp(k))
    c.save(); c.translate(x + w / 2, y + h / 2 + bob + (1 - clamp(k)) * 120 + kout * 60); c.rotate(ang); c.scale(clamp(k, 0, 1.2), clamp(k, 0, 1.2))
    c.drawRoundRect(skia.Rect(-w / 2 + 10, -h / 2 + 22, w / 2 + 10, h / 2 + 22), 20, 20, paint("#000000", int(al * 0.55), blur=22))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 20, "#0B1424", al)
    c.save(); p = skia.Path(); p.addRoundRect(skia.Rect(-w / 2 + 10, -h / 2 + 56, w / 2 - 10, h / 2 - 10), 14, 14); c.clipPath(p, doAntiAlias=True)
    c.translate(-DW / 2 * 0 - w / 2 + 10 - (DW / 2 - (w - 20) / 2) + DW / 2 - (w - 20) / 2, 0) if False else None
    c.translate(-(DW / 2), -(DH / 2) + 23)
    c.saveLayerAlpha(None, al)
    draw_map(c, WM, cam, {}, 255)
    hl(c, cam, name, t, t0 + 0.25, YEL, fill)
    c.restore(); c.restore()
    c.drawRoundRect(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), 20, 20, paint("#3E5068", al, stroke=1.5))
    c.drawCircle(-w / 2 + 28, -h / 2 + 30, 9, paint(REGCOL.get(name, SAFF), al))
    text(c, ttl, -w / 2 + 46, -h / 2 + 40, 28, "#F1FAEE", FT_BLACK, "l", al)
    if sub: text(c, sub, w / 2 - 18, h / 2 - 20, 18, "#C9D1DC", FT_SEMI, "r", al)
    c.restore()

# ------------------------------------------------------------------ small widgets
def title(c, s, x, y, size, k, col="#F1FAEE", a=255):
    if k <= 0: return
    kk = back(k); c.save(); c.translate(x, y); c.scale(kk, kk); text(c, s, 0, 0, size, col, FT_BLACK, "c", int(a * clamp(k * 1.5)), shadow=True); c.restore()

def label(c, s, x, y, k, size=30, col="#F1FAEE", bgc=NAVY, border=YEL):
    if k <= 0: return
    al = int(255 * clamp(k * 1.6)); w = text_w(s, size, FT_BLACK) + 30; dy = (1 - ease_out(k)) * 14
    rrect(c, x - w / 2, y - size * 0.95 + dy, x + w / 2, y + size * 0.5 + dy, 10, bgc, al, shadow=8)
    c.drawRoundRect(skia.Rect(x - w / 2, y - size * 0.95 + dy, x + w / 2, y + size * 0.5 + dy), 10, 10, paint(border, al, stroke=2.5))
    text(c, s, x, y + size * 0.12 + dy, size, col, FT_BLACK, "c", al)

def tag_note(c, s, x, y, k, col="#9FB0C6"):
    if k <= 0: return
    text(c, s, x, y, 20, col, FT_SEMI, "c", int(220 * clamp(k * 1.5)))

def arrow(c, p0, p1, k, col=YEL, w=7, bend=0.18):
    if k <= 0: return
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    nx, ny = -(p1[1] - p0[1]), (p1[0] - p0[0])
    route(c, [p0, (mx + nx * bend, my + ny * bend), p1], ease_out(k), col, w, dash=False)

def timeline(c, t, year, k=1.0, y0=None, span=(600, 800), label_s=None, step=10, big_every=50, start=None, bracket=None):
    """bottom timeline: ticks every `step` years (labels every `big_every`), red progress from `start` (default: left end)
    to the current year with a chip; bracket=(y_from, y_to, text, k) draws a span marker above the line"""
    if k <= 0: return
    al = int(255 * clamp(k * 1.5)); y = y0 or 930
    x0, x1 = 300, 1620; a0, a1 = span
    X = lambda yr: lerp(x0, x1, (clamp(yr, a0, a1) - a0) / (a1 - a0))
    c.drawLine(x0, y, x1, y, paint("#5B6E8C", al, stroke=3))
    for yr in range(a0, a1 + 1, step):
        x = X(yr); big = yr % big_every == 0
        c.drawLine(x, y - (12 if big else 6), x, y + (12 if big else 6), paint("#8A9BB0", al, stroke=2))
        if big: text(c, str(yr), x, y + 38, 20, "#8A9BB0", FT_SEMI, "c", al)
    xs = X(start) if start is not None else x0; x = X(year)
    if start is not None: c.drawCircle(xs, y, 8, paint(RED, al))
    c.drawLine(xs, y, x, y, paint(RED, al, stroke=6))
    if bracket and bracket[3] > 0:
        bk = ease_out(bracket[3]); ba = int(al * clamp(bracket[3] * 1.5)); bx0, bx1 = X(bracket[0]), X(bracket[1])
        bx1 = lerp(bx0, bx1, bk)
        bp = paint(YEL, ba, stroke=4, cap_round=True)
        c.drawLine(bx0, y - 78, bx1, y - 78, bp); c.drawLine(bx0, y - 90, bx0, y - 66, bp); c.drawLine(bx1, y - 90, bx1, y - 66, bp)
        text(c, bracket[2], (bx0 + bx1) / 2, y - 92, 28, YEL, FT_BLACK, "c", ba)
    pill(c, label_s or f"{int(round(year))}", x, y - 40, 30, RED, a=al, shadow=6)

def fort(c, x, y, s, k, col="#C9B48A", a=255):
    """fortress builds up brick by brick (k 0..1)"""
    if k <= 0: return
    kk = s / 100; rows = 6
    for r in range(rows):
        kr = ease_out(seg(k, r / rows, (r + 1) / rows))
        if kr <= 0: continue
        yy = y + 40 * kk - (r + 1) * 12 * kk
        for j in range(8):
            off = 6 * kk if r % 2 else 0
            bx = x - 50 * kk + j * 12.5 * kk + off
            if bx > x + 44 * kk: continue
            c.drawRect(skia.Rect(bx, yy + (1 - kr) * -30 * kk, bx + 11.5 * kk, yy + 11 * kk + (1 - kr) * -30 * kk), paint(col, int(a * kr)))
    kt = ease_out(seg(k, 0.85, 1.0))
    for j in range(5):
        if kt > 0:
            c.drawRect(skia.Rect(x - 50 * kk + j * 22 * kk, y + 40 * kk - 84 * kk, x - 38 * kk + j * 22 * kk, y + 40 * kk - 72 * kk), paint(col, int(a * kt)))
    c.drawRect(skia.Rect(x - 9 * kk, y + 14 * kk, x + 9 * kk, y + 40 * kk), paint("#3A2F22", int(a * ease_out(seg(k, 0.5, 0.7)))))

def shield(c, x, y, s, col="#C9D1DC", a=255, k=1.0):
    if k <= 0: return
    kk = s / 100 * back(k)
    p = skia.Path(); p.moveTo(x, y - 46 * kk); p.lineTo(x + 38 * kk, y - 32 * kk); p.lineTo(x + 34 * kk, y + 10 * kk)
    p.quadTo(x + 24 * kk, y + 36 * kk, x, y + 50 * kk); p.quadTo(x - 24 * kk, y + 36 * kk, x - 34 * kk, y + 10 * kk); p.lineTo(x - 38 * kk, y - 32 * kk); p.close()
    c.drawPath(p, paint(col, a)); c.drawPath(p, paint("#0F1B2D", a, stroke=4 * kk))
    c.drawLine(x, y - 36 * kk, x, y + 38 * kk, paint("#0F1B2D", int(a * 0.4), stroke=4 * kk))

def crown(c, x, y, s, col=YEL, a=255):
    k = s / 100
    p = skia.Path(); p.moveTo(x - 45 * k, y + 25 * k); p.lineTo(x - 50 * k, y - 25 * k); p.lineTo(x - 22 * k, y); p.lineTo(x, y - 35 * k)
    p.lineTo(x + 22 * k, y); p.lineTo(x + 50 * k, y - 25 * k); p.lineTo(x + 45 * k, y + 25 * k); p.close()
    c.drawPath(p, paint(col, a))
    for dx in (-50, 0, 50): c.drawCircle(x + dx * k, y - (25 if dx else 35) * k - 6 * k, 7 * k, paint(col, a))

def lock(c, x, y, s, open_k=0.0, col=YEL, a=255):
    k = s / 100
    rrect(c, x - 36 * k, y - 6 * k, x + 36 * k, y + 46 * k, 8 * k, col, a)
    sh = skia.Path(); lift = 22 * k * ease_out(open_k)
    sh.addArc(skia.Rect(x - 24 * k, y - 48 * k - lift, x + 24 * k, y + 0 * k - lift), 180, 180)
    c.drawPath(sh, paint(col, a, stroke=9 * k))
    c.drawLine(x - 24 * k, y - 24 * k - lift, x - 24 * k, y - 4 * k - (lift if open_k < 0.5 else 0), paint(col, a, stroke=9 * k))
    c.drawLine(x + 24 * k, y - 24 * k - lift, x + 24 * k, y - 4 * k, paint(col, a, stroke=9 * k))
    c.drawCircle(x, y + 16 * k, 7 * k, paint(NAVY, a)); c.drawRect(skia.Rect(x - 3 * k, y + 18 * k, x + 3 * k, y + 32 * k), paint(NAVY, a))

MANU = None
def manuscript_img():
    """a prop page with blurred, unreadable script-like lines (not real text)"""
    global MANU
    if MANU is None:
        rng = np.random.default_rng(3); W, H = 900, 1100
        im = Image.new("RGBA", (W, H), (233, 220, 190, 255))
        from PIL import ImageDraw
        d = ImageDraw.Draw(im)
        for r in range(15):
            y = 120 + r * 62; x = W - 90
            while x > 110:
                wl = int(rng.integers(30, 120)); d.rounded_rectangle([x - wl, y, x, y + 14], 7, fill=(90, 62, 40, 230))
                if rng.random() < 0.5: d.ellipse([x - wl // 2, y - 14, x - wl // 2 + 8, y - 6], fill=(90, 62, 40, 200))
                x -= wl + int(rng.integers(14, 30))
        d.rectangle([40, 40, W - 40, H - 40], outline=(150, 110, 70, 255), width=6)
        im = im.filter(ImageFilter.GaussianBlur(2.2))
        MANU = sk_image(im)
    return MANU

def manuscript(c, cx, cy, w, k, cover_k=0.0, lock_k=0.0, lock_open=0.0, ang=-3, hl_k=0.0):
    if k <= 0: return
    img = manuscript_img(); h = w * img.height() / img.width(); al = int(255 * clamp(k * 1.5))
    c.save(); c.translate(cx, cy + (1 - ease_out(k)) * 80); c.rotate(ang)
    c.drawRect(skia.Rect(-w / 2 + 10, -h / 2 + 18, w / 2 + 10, h / 2 + 18), paint("#000000", int(al * 0.5), blur=18))
    draw_img(c, img, -w / 2, -h / 2, w / 2, h / 2, al)
    ly = -h / 2 + h * (120 + 7 * 62) / 1100
    if hl_k > 0:
        hp = paint(YEL, int(170 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
        c.drawRect(skia.Rect(-w / 2 + 50, ly - 18, -w / 2 + 50 + (w - 100) * ease_out(hl_k), ly + 30), hp)
    if cover_k > 0:
        cw = (w - 90) * ease_out(cover_k)
        rrect(c, w / 2 - 45 - cw, ly - 22, w / 2 - 45, ly + 34, 10, "#111827", int(al * 0.95))
    if lock_k > 0:
        kk = back(lock_k); c.save(); c.translate(0, ly + 6); c.scale(kk, kk)
        lock(c, 0, -6, 70, lock_open); pill(c, "CH 4", 95, 14, 26, RED, shadow=0); c.restore()
    c.restore()

def slots(c, t, unlocked, k=1.0, y=520, red4=0.0, labels=None, open_t=None):
    """four 'RAAZ' slots; unlocked = how many are open (float for animation)"""
    if k <= 0: return
    labels = labels or ["RAAZ 1", "RAAZ 2", "RAAZ 3", "RAAZ 4"]
    for i in range(4):
        kk = back(seg(k, i * 0.12, 0.5 + i * 0.12))
        if kk <= 0: continue
        x = 960 + (i - 1.5) * 380
        c.save(); c.translate(x, y); c.scale(kk, kk)
        hot = (i == 3 and red4 > 0)
        col = RED if hot else "#2B3A4F"
        rrect(c, -160, -150, 160, 150, 24, "#16223A", 255, shadow=18)
        c.drawRoundRect(skia.Rect(-160, -150, 160, 150), 24, 24, paint(col if hot else "#3E5068", 255, stroke=4 + 3 * red4 * (0.5 + 0.5 * math.sin(t * 8)) if hot else 4))
        lock(c, 0, -20, 90, clamp(unlocked - i), RED if hot else YEL)
        text(c, labels[i], 0, 110, 34, "#F1FAEE", FT_BLACK, "c")
        if hot: text(c, "GALATFEHMI?", 0, -118, 26, RED, FT_BLACK, "c", int(255 * red4))
        c.restore()

def host_placeholder(c, t, lt):
    """until the 3D host is rendered (needs the real VO for lip-sync) show the studio as a card"""
    c.clear(hexc("#0B1424"))
    rrect(c, 160, 120, 1760, 900, 30, "#121F36", 255, shadow=30)
    title(c, "AMRIT BORI", 960, 420, 120, seg(lt, 0.1, 0.6), YEL)
    text(c, "[ 3D HOST SEGMENT - final render mein stickman studio ]", 960, 560, 36, "#8A9BB0", FT_SEMI, "c")
    if LOGO: draw_img(c, LOGO, 860, 600, 1060, 800, 255)

# ------------------------------------------------------------------ shots
SHOTS = []; SFX = []
def shot(t0, t1, trans="fade"):
    def deco(fn): SHOTS.append((t0, t1, fn, trans)); SFX.append(("whoosh_fast", t0, -25)); return fn
    return deco
def SFX_MARK(t, name, g=-22):
    if not any(abs(t - x[1]) < 0.05 and x[0] == name for x in SFX): SFX.append((name, t, g))

LOGO = None
def load_assets():
    global LOGO
    if LOGO is not None: return
    load_geo()
    LOGO = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_800.png").resize((300, 300)))

W_CAM = (28.0, 31.0, 9.5)           # caliphate overview
IB_CAM = (-4.0, 39.5, 34.0)          # Iberia
SI_CAM = (68.7, 25.6, 95.0)          # Sindh close

# ---- HOOK ------------------------------------------------------------------------------------------
u_spain = U("Ek fauj ne"); u_wahi = U("Wahi khilafat"); u_lekin = U("Lekin Hindustan ke darwaze")
u_naam = U("Naam rakha"); u_mah = U("Al-Mahfuza."); u_mat = U("Matlab"); u_jo = U("Jo fauj Spain")
u_aur = U("Aur ye main nahi"); u_ye = U("Ye ek Arab itihaskar"); u_wo = U("Wo line main"); u_pehle = U("Lekin pehle samajhna")
u_iske = U("Iske peeche"); u_chautha = U("Aur chautha raaz"); u_namaste = U("Namaste doston"); u_chalo = U("Chalo, waqt")
u_632 = U("Saal 632")

@shot(0.0, vin(u_wahi), "cut")
def s01(c, t):
    k = ease_out(seg(t, 0.25, 2.2))
    cam = fly((-4.0, 39.5, 26.0), IB_CAM, ease_io(seg(t, 0, 3.0)))
    bg(c, cam)
    draw_region(c, cam, "iberia", GREEN, int(230 * k), stroke="#7CE0A8")
    stat_card(c, 1180, 300, 520, 300, "~5 SAAL", "lagbhag poora Spain", seg(t, kw(u_spain, "paanch") - 0.1, kw(u_spain, "paanch") + 0.5), YEL)
    ky = ease_io(seg(t, kw(u_spain, "paanch") - 0.1, ue(u_spain) + 0.3))          # 711 -> 716 while "paanch saal" is said
    timeline(c, t, lerp(711, 716, ky), seg(t, 0.2, 0.7), span=(708, 720), step=1, big_every=1, start=711,
             bracket=(711, 716, "5 SAAL", seg(t, ue(u_spain) + 0.1, ue(u_spain) + 0.7)))
    hl(c, cam, "iberia", t, kw(u_spain, "Spain"))
    float_map(c, t, kw(u_spain, "Spain"), "iberia", "SPAIN · 711", "Visigoth rajya, andaazan", 110, 150, 420, 320, fill=GREEN, ctx=4)
    footnote(c, "Map: Natural Earth · andaazan seema")
    SFX_MARK(0.3, "hit", -16)

@shot(vin(u_wahi), vin(u_lekin))
def s02(c, t):
    k = seg(t, vin(u_wahi), vin(u_wahi) + 2.4)
    cam = fly(IB_CAM, W_CAM, ease_io(k))
    bg(c, cam)
    draw_region(c, cam, "caliph", GREEN, int(215 * ease_out(seg(t, vin(u_wahi) + 0.4, vin(u_wahi) + 2.2))), stroke="#7CE0A8")
    title(c, "UMAYYAD KHILAFAT", 960, 170, 64, seg(t, vin(u_wahi) + 1.0, vin(u_wahi) + 1.6), "#F1FAEE")
    tag_note(c, "andaazan naksha, c. 740 CE", 960, 210, seg(t, vin(u_wahi) + 1.4, vin(u_wahi) + 2.0))
    for key, word, side in (("atlantic", "Atlantic", -1), ("samarkand", "Central Asia", 1)):
        kk = seg(t, kw(u_wahi, word), kw(u_wahi, word) + 0.4)
        x, y = S(cam, key); label(c, word.upper(), x, y - 30, kk, 28)
    hl(c, cam, "centralasia", t, kw(u_wahi, "Central Asia"))
    float_map(c, t, kw(u_wahi, "Central Asia"), "centralasia", "CENTRAL ASIA", "Transoxiana, c. 740 (andaazan)", 1400, 560, 420, 320, fill=GREEN)

@shot(vin(u_lekin), vin(u_naam))
def s03(c, t):
    k = seg(t, vin(u_lekin), vin(u_lekin) + 2.6)
    cam = fly(W_CAM, SI_CAM, ease_io(k))
    bg(c, cam)
    draw_region(c, cam, "caliph", GREEN, 120)
    draw_region(c, cam, "sindh", GREEN, 200, stroke="#7CE0A8")
    x, y = S(cam, "mahfuza")
    fort(c, x, y, 210 * cam[2] / SI_CAM[2], seg(t, kw(u_lekin, "naya shehar") - 0.6, kw(u_lekin, "naya shehar") + 1.2))
    label(c, "SINDH", *S(cam, "sindh"), seg(t, vin(u_lekin) + 2.0, vin(u_lekin) + 2.4), 30)
    hl(c, cam, "india", t, kw(u_lekin, "Hindustan"), SAFF, dur=1.6)
    float_map(c, t, kw(u_lekin, "Hindustan"), "india", "HINDUSTAN · 8vi SADI", "kai alag rajya (andaazan)", 1400, 140, 420, 330, fill=SAFF, pad=0.25)
    SFX_MARK(kw(u_lekin, "naya shehar"), "build", -20)

@shot(vin(u_naam), vin(u_jo))
def s04(c, t):
    bg(c, SI_CAM)
    draw_region(c, SI_CAM, "sindh", GREEN, 200, stroke="#7CE0A8")
    x, y = S(SI_CAM, "mahfuza"); fort(c, x, y, 210, 1.0)
    dim(c, 150)
    word = "AL-MAHFUZA"; n = int(len(word) * clamp(seg(t, us(u_mah) - 0.1, us(u_mah) + 0.6)))
    text(c, word[:n], 960, 300, 150, YEL, FT_BLACK, "c", shadow=True)
    title(c, "= SURAKSHIT", 960, 420, 80, seg(t, kw(u_mat, "surakshit") - 0.1, kw(u_mat, "surakshit") + 0.4), "#F1FAEE")
    tag_note(c, "al-Baladhuri, Futuh al-Buldan", 960, 475, seg(t, us(u_mat) + 0.3, us(u_mat) + 0.8))
    SFX_MARK(us(u_mah), "boom_low", -18)

@shot(vin(u_jo), vin(u_aur))
def s05(c, t):
    c.clear(hexc(NAVY))
    kL = ease_out(seg(t, vin(u_jo), vin(u_jo) + 0.6)); kR = ease_out(seg(t, kw(u_jo, "yahan") - 0.2, kw(u_jo, "yahan") + 0.5))
    for i, kk in enumerate((kL, kR)):
        if kk <= 0: continue
        x0 = 100 + i * 880; dy = (1 - kk) * 60
        rrect(c, x0, 170 + dy, x0 + 840, 840 + dy, 26, "#16223A", int(255 * kk), shadow=20)
        c.drawRoundRect(skia.Rect(x0, 170 + dy, x0 + 840, 840 + dy), 26, 26, paint(GREEN if i == 0 else RED, int(255 * kk), stroke=4))
    if kL > 0:
        cam = (-4.0, 40.0, 36.0)
        c.save(); c.clipRect(skia.Rect(120, 190, 920, 820)); c.translate(-440 + 100, (1 - kL) * 60)
        draw_map(c, WM, cam, {}, int(255 * kL)); draw_region(c, cam, "iberia", GREEN, int(230 * kL), stroke="#7CE0A8"); c.restore()
        crown(c, 520, 330 + (1 - kL) * 60, 90, YEL, int(255 * kL))
        text(c, "SPAIN: JEET", 520, 790 + (1 - kL) * 60, 46, "#F1FAEE", FT_BLACK, "c", int(255 * kL))
    if kR > 0:
        fort(c, 1400, 500, 170, 1.0, a=int(255 * kR))
        for j in range(10):
            ang = j / 10 * math.tau + t * 0.15
            shield(c, 1400 + 250 * math.cos(ang), 520 + 190 * math.sin(ang), 46, SAFF, int(255 * kR), back(seg(t, kw(u_jo, "yahan") + j * 0.05, kw(u_jo, "yahan") + 0.4 + j * 0.05)))
        text(c, "SINDH: SURAKSHIT JAGAH?", 1400, 790, 42, "#F1FAEE", FT_BLACK, "c", int(255 * kR))
    SFX_MARK(kw(u_jo, "yahan"), "pop", -22)

@shot(vin(u_aur), vin(u_iske))
def s06(c, t):
    c.clear(hexc("#141019"))
    k = seg(t, vin(u_aur), vin(u_aur) + 0.8)
    cover = seg(t, kw(u_ye, "khud") - 0.2, kw(u_ye, "khud") + 0.5)
    lk = seg(t, kw(u_wo, "dikhaunga") - 0.3, kw(u_wo, "dikhaunga") + 0.3)
    manuscript(c, 960, 520, 620, k, cover_k=cover, lock_k=lk)
    pill(c, "AL-BALADHURI · 9vi SADI", 960, 960 - 60, 30, "#5B4636", a=int(255 * clamp(seg(t, us(u_ye), us(u_ye) + 0.5) * 1.5)), shadow=6) if t > us(u_ye) else None
    if t > vin(u_pehle):
        title(c, "PEHLE: YE NAUBAT AAYI KYUN?", 960, 150, 56, seg(t, vin(u_pehle), vin(u_pehle) + 0.5), YEL)
    SFX_MARK(us(u_aur), "paper", -20); SFX_MARK(kw(u_wo, "dikhaunga"), "lock", -18)

@shot(vin(u_iske), HOSTSEG["H1"][0])
def s07(c, t):
    c.clear(hexc(NAVY))
    slots(c, t, 0, seg(t, vin(u_iske), vin(u_iske) + 1.2), 520, red4=seg(t, kw(u_chautha, "chautha") - 0.1, kw(u_chautha, "chautha") + 0.4))
    title(c, "4 RAAZ", 960, 230, 80, seg(t, vin(u_iske), vin(u_iske) + 0.5), YEL)
    fade = seg(t, ue(u_chautha) - 0.1, ue(u_chautha) + 0.4)
    if fade > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(255 * fade)))
    SFX_MARK(kw(u_chautha, "chautha"), "riser", -20)

_HF = {}
def host_frame(c, key, t):
    d = AB_ROOT + f"render_tmp/host_{key}/"
    f = int(round(t * 60)); a, b = HOSTSEG[key]
    f = max(int(round(a * 60)), min(int(round(b * 60)) - 1, f))
    for ff in (f, f - 1, f + 1, f - 2):
        p = d + f"f{ff:06d}.jpg"
        if os.path.exists(p):
            if p not in _HF:
                if len(_HF) > 8: _HF.clear()
                _HF[p] = sk_image(Image.open(p))
            draw_img(c, _HF[p], 0, 0, DW, DH); return True
    host_placeholder(c, t, t - a); return False

def subscribe_btn(c, t, t0, x=1500, y=880):
    """red SUBSCRIBE button pops, cursor clicks it, turns grey 'SUBSCRIBED' + bell"""
    lt = t - t0
    if lt < 0 or lt > 4.2: return
    k = back(seg(lt, 0, 0.35)) * (1 - ease_in(seg(lt, 3.7, 4.2)))
    if k <= 0: return
    clicked = lt > 1.3
    c.save(); c.translate(x, y); c.scale(k, k)
    w = 330
    rrect(c, -w / 2, -42, w / 2, 42, 42, "#5B6472" if clicked else "#E62117", 255, shadow=16)
    text(c, "SUBSCRIBED" if clicked else "SUBSCRIBE", 0 - 20, 13, 36, "#FFFFFF", FT_BLACK, "c")
    bx = w / 2 + 60; ring = math.sin(lt * 25) * 14 * seg(lt, 1.5, 1.6) * (1 - seg(lt, 2.4, 2.6))
    c.save(); c.translate(bx, 0); c.rotate(ring)
    rrect(c, -46, -42, 46, 42, 42, "#F1FAEE", 255, shadow=12)
    bp = skia.Path(); bp.moveTo(-16, 14); bp.lineTo(-16, -4); bp.cubicTo(-16, -22, 16, -22, 16, -4); bp.lineTo(16, 14); bp.close()
    c.drawPath(bp, paint("#0F1B2D")); c.drawRect(skia.Rect(-20, 12, 20, 18), paint("#0F1B2D")); c.drawCircle(0, 22, 5, paint("#0F1B2D"))
    c.restore()
    cx = lerp(260, 40, ease_io(seg(lt, 0.4, 1.2))); cy = lerp(160, 20, ease_io(seg(lt, 0.4, 1.2)))
    if lt > 1.6: cx = lerp(40, bx, ease_io(seg(lt, 1.6, 2.0))); cy = 20
    cp = skia.Path(); cp.moveTo(cx, cy); cp.lineTo(cx, cy + 44); cp.lineTo(cx + 12, cy + 33); cp.lineTo(cx + 30, cy + 33); cp.close()
    c.drawPath(cp, paint("#FFFFFF")); c.drawPath(cp, paint("#000000", 255, stroke=3))
    c.restore()

@shot(HOSTSEG["H1"][0], vin(u_632), "cut")
def h1(c, t):
    host_frame(c, "H1", t)
    subscribe_btn(c, t, kw(U("Naye ho toh"), "subscribe") - 0.4)
    SFX_MARK(kw(U("Naye ho toh"), "subscribe") + 0.9, "pop", -20)

# ---- CHAPTER 1 -------------------------------------------------------------------------------------
CH_GAP = 1.4
GAPS = []
def chapter(num, ttl, unit):
    """chapter card plays in an inserted silent gap before `unit`"""
    GAPS.append(vin(unit))

u_632 = U("Saal 632"); u_pai = U("Paigambar"); u_toof = U("Aur uske baad Arab"); u_661 = U("661 mein"); u_raj = U("Rajdhani")
u_charam = U("Apne charam"); u_teen = U("Teen mahadweep"); u_711 = U("Aur saal 711"); u_sirf = U("Sirf 79"); u_ek = U("Ek taraf Spain")
u_doo = U("Doosri taraf Sindh"); u_gir = U("Spain gir gaya"); u_ab = U("Ab nazar thi"); u_min = U("Lekin ek minute"); u_india75 = U("India par pehli nazar")
CHAPTERS = [(1, "79 SAAL KA TOOFAN", u_632)]
for n_, ttl_, u_ in CHAPTERS: chapter(n_, ttl_, u_)

AR_CAM = (42.0, 25.0, 22.0)
@shot(vin(u_632), vin(u_toof), "cut")
def s08(c, t):
    cam = fly((42.0, 25.0, 14.0), AR_CAM, ease_io(seg(t, vin(u_632), vin(u_632) + 2.0)))
    bg(c, cam)
    for key, nm, i in (("medina", "MEDINA", 0), ("mecca", "MECCA", 1)):
        x, y = S(cam, key); pin(c, x, y, nm, seg(t, vin(u_pai) + i * 0.3, vin(u_pai) + 0.6 + i * 0.3), YEL, size=30, side="r", t=t)
    timeline(c, t, 632, seg(t, vin(u_632), vin(u_632) + 0.5), span=(620, 780))

WAVES = [("SAU", 0), ("YEM", 0), ("OMN", 0), ("ARE", 0.1), ("SYR", 0.25), ("JOR", 0.25), ("IRQ", 0.35), ("EGY", 0.45), ("LBY", 0.6), ("IRN", 0.6), ("TUN", 0.75), ("DZA", 0.85), ("MAR", 0.95), ("TKM", 0.85), ("UZB", 0.95)]
@shot(vin(u_toof), vin(u_661))
def s09(c, t):
    cam = fly(AR_CAM, (30.0, 30.0, 8.0), ease_io(seg(t, vin(u_toof), vin(u_toof) + 3.0)))
    k = seg(t, kw(u_toof, "toofan") - 0.3, ue(u_toof) + 0.8)
    fills = {code: (GREEN, int(210 * ease_out(seg(k, d, d + 0.3)))) for code, d in WAVES}
    bg(c, cam, fills)
    for r in range(3):
        rr = ((t - vin(u_toof)) * 0.6 + r / 3) % 1
        x, y = S(cam, "arabia"); c.drawCircle(x, y, 40 + 900 * rr, paint("#7CE0A8", int(120 * (1 - rr)), stroke=4))
    timeline(c, t, lerp(632, 700, ease_io(k)), 1.0, span=(620, 780))
    tag_note(c, "andaazan, aadhunik seemaon par", 960, 880, 1)
    hl(c, cam, "arabia", t, kw(u_toof, "Arab"))
    float_map(c, t, kw(u_toof, "Arab"), "arabia", "ARAB · 632", "Arab prayadweep", 1420, 130, 400, 300, fill=GREEN, pad=0.4)
    SFX_MARK(kw(u_toof, "toofan"), "wind", -22)

@shot(vin(u_661), vin(u_charam))
def s10(c, t):
    cam = (36.0, 31.0, 18.0)
    bg(c, cam); draw_region(c, cam, "caliph", GREEN, 170, stroke="#7CE0A8")
    x, y = S(cam, "damascus"); pin(c, x, y, "DAMASCUS", seg(t, kw(u_raj, "Rajdhani"), kw(u_raj, "Rajdhani") + 0.5) if True else 0, YEL, size=34, t=t)
    pill(c, "UMAYYAD KHILAFAT", 960, 170, 46, GREEN_D, a=int(255 * clamp(seg(t, kw(u_661, "Umayyad") - 0.1, kw(u_661, "Umayyad") + 0.4) * 1.5))) if t > kw(u_661, "Umayyad") - 0.1 else None
    timeline(c, t, 661, 1.0, span=(620, 780))
    hl(c, cam, "syria", t, kw(u_raj, "Rajdhani") + 0.3)
    float_map(c, t, kw(U("Damascus."), "Damascus"), "syria", "DAMASCUS · 661", "Sham (Syria), andaazan", 1400, 520, 420, 320, fill=GREEN, pad=0.6)

@shot(vin(u_charam), vin(u_teen))
def s11(c, t):
    bg(c, W_CAM); draw_region(c, W_CAM, "caliph", GREEN, 200, stroke="#7CE0A8")
    dim(c, 90)
    k = seg(t, kw(u_charam, "ek crore") - 0.2, kw(u_charam, "ek crore") + 1.2)
    v = lerp(0, 1.1, ease_out(k))
    stat_card(c, 620, 280, 680, 330, f"{v:.1f} CRORE+ km²", "Umayyad khilafat, charam par", seg(t, kw(u_charam, "ek crore") - 0.3, kw(u_charam, "ek crore") + 0.2), YEL, sub="Wikipedia: 1.1-1.5 crore km²")
    SFX_MARK(kw(u_charam, "ek crore"), "count", -22)

CONT = [("ASIA", (62.0, 42.0), "Asia"), ("AFRICA", (10.0, 24.0), "Africa"), ("EUROPE", (-4.0, 44.0), "Europe")]
@shot(vin(u_teen), vin(u_711))
def s12(c, t):
    bg(c, W_CAM); draw_region(c, W_CAM, "caliph", GREEN, 200, stroke="#7CE0A8")
    for nm, ll, word in CONT:
        hl(c, W_CAM, {"ASIA": "c_asia", "AFRICA": "c_africa", "EUROPE": "c_europe"}[nm], t, kw(u_teen, word), YEL, "#5FD39A")
        x, y = to_screen(W_CAM, *ll); label(c, nm, x, y, seg(t, kw(u_teen, word) - 0.1, kw(u_teen, word) + 0.3), 40, border=GREEN)
    title(c, "TEEN MAHADWEEP", 960, 170, 60, seg(t, vin(u_teen), vin(u_teen) + 0.5), YEL)

@shot(vin(u_711), vin(u_gir))
def s13(c, t):
    bg(c, W_CAM); draw_region(c, W_CAM, "caliph", GREEN, 110)
    k = seg(t, vin(u_711), us(u_sirf) + 0.8)
    timeline(c, t, lerp(632, 711, ease_io(k)), 1.0, span=(620, 780))
    stat_card(c, 1380, 140, 400, 220, "79 SAAL", "632 se 711", seg(t, kw(u_sirf, "79") - 0.1, kw(u_sirf, "79") + 0.4), YEL)
    src = S(W_CAM, "damascus")
    arrow(c, src, S(W_CAM, "spain"), seg(t, kw(u_ek, "Spain") - 0.3, kw(u_ek, "Spain") + 0.5), YEL, 8, 0.2)
    arrow(c, src, S(W_CAM, "sindh"), seg(t, kw(u_doo, "Sindh") - 0.3, kw(u_doo, "Sindh") + 0.5), YEL, 8, -0.2)
    if t > kw(u_ek, "Spain"): draw_region(c, W_CAM, "iberia", GREEN, int(240 * seg(t, kw(u_ek, "Spain"), kw(u_ek, "Spain") + 0.5)), stroke="#FFFFFF")
    if t > kw(u_doo, "Sindh"): draw_region(c, W_CAM, "sindh", GREEN, int(240 * seg(t, kw(u_doo, "Sindh"), kw(u_doo, "Sindh") + 0.5)), stroke="#FFFFFF")
    label(c, "SPAIN", *[a + b for a, b in zip(S(W_CAM, "spain"), (0, -40))], seg(t, kw(u_ek, "Spain"), kw(u_ek, "Spain") + 0.3), 30)
    label(c, "SINDH", *[a + b for a, b in zip(S(W_CAM, "sindh"), (0, -40))], seg(t, kw(u_doo, "Sindh"), kw(u_doo, "Sindh") + 0.3), 30)
    float_map(c, t, kw(u_ek, "Spain"), "iberia", "SPAIN · 711", "Visigoth rajya (andaazan)", 90, 140, 380, 290, fill=GREEN, ctx=4)
    float_map(c, t, kw(u_doo, "Sindh"), "sindh", "SINDH · 711", "Raja Dahir ka rajya (andaazan)", 90, 470, 380, 290, fill=GREEN, ctx=3)
    SFX_MARK(kw(u_ek, "Spain"), "whoosh", -20); SFX_MARK(kw(u_doo, "Sindh"), "whoosh", -20)

IN_CAM = (72.0, 24.0, 22.0)
@shot(vin(u_gir), vin(u_min))
def s14(c, t):
    cam = fly(W_CAM, IN_CAM, ease_io(seg(t, kw(u_ab, "Sindh") - 0.6, ue(u_ab) + 0.4)))
    glow = 0.5 + 0.5 * math.sin(t * 3)
    bg(c, cam, {"IND": (SAFF, int(140 + 60 * glow * seg(t, kw(u_ab, "Hindustan") - 0.3, kw(u_ab, "Hindustan") + 0.3)))})
    draw_region(c, cam, "caliph", GREEN, 150); draw_region(c, cam, "iberia", GREEN, 230)
    hl(c, cam, "sindh", t, kw(u_ab, "Sindh"), YEL)
    hl(c, cam, "india", t, kw(u_ab, "Hindustan"), SAFF)
    label(c, "HINDUSTAN", *S(cam, "india"), seg(t, kw(u_ab, "Hindustan") - 0.1, kw(u_ab, "Hindustan") + 0.4), 40, border=SAFF)
    float_map(c, t, kw(u_ab, "Hindustan"), "india", "HINDUSTAN · 711", "kai alag rajya (andaazan)", 1420, 150, 400, 320, fill=SAFF, pad=0.25)
    tag_note(c, "India boundary as per Survey of India", 960, 1060 - 120, seg(t, kw(u_ab, "Hindustan"), kw(u_ab, "Hindustan") + 0.5))

@shot(vin(u_min), ue(u_india75) + 0.6, "cut")
def s15(c, t):
    bg(c, IN_CAM, {"IND": (SAFF, 140)}); draw_region(c, IN_CAM, "caliph", GREEN, 150)
    k = seg(t, kw(u_india75, "75") - 0.2, ue(u_india75))
    jit = (1 - seg(t, us(u_min), us(u_min) + 0.25)) * 18
    c.translate(jit * math.sin(t * 90), 0)
    timeline(c, t, lerp(711, 636, ease_io(k)), 1.0, span=(620, 780))
    stat_card(c, 760, 200, 400, 220, "75 SAAL", "aur pehle", seg(t, kw(u_india75, "75") - 0.1, kw(u_india75, "75") + 0.4), RED)
    title(c, "LEKIN EK MINUTE...", 960, 520, 70, seg(t, us(u_min), us(u_min) + 0.4), YEL)
    SFX_MARK(us(u_min), "scratch", -16)

DEMO_END = ue(u_india75) + 0.6

# ------------------------------------------------------------------ captions
CAPS = []
def build_caps():
    for i, u in enumerate(UN):
        words = u["text"].split(); chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 6 or w.endswith((",", ".", "?", ":", "!")) and len(cur) >= 3:
                chunks.append(" ".join(cur)); cur = []
        if cur: chunks.append(" ".join(cur))
        tot = sum(len(ch) for ch in chunks); acc = u["start"]
        for ch in chunks:
            d = (u["end"] - u["start"]) * len(ch) / tot; CAPS.append((acc, acc + d, ch)); acc += d
build_caps()
def captions(c, t):
    if in_host(t): return
    for a, b, s in CAPS:
        if a - 0.05 <= t < b + 0.15:
            k = seg(t, a - 0.05, a + 0.1); w = text_w(s, 40, FT_BLACK)
            rrect(c, 960 - w / 2 - 26, 990, 960 + w / 2 + 26, 1050, 14, "#000000", int(150 * k))
            text(c, s, 960, 1033, 40, "#FFFFFF", FT_BLACK, "c", int(255 * k)); return

HOSTS = [(HOSTSEG["H1"][0], vin(u_632))]
def in_host(t): return any(a <= t < b for a, b in HOSTS)

# ------------------------------------------------------------------ frame
SHOTS.sort(key=lambda s: s[0])
def find(t):
    for i, (a, b, fn, tr) in enumerate(SHOTS):
        if a <= t < b: return i
    return None

GAPINFO = None
def remap(T):
    off = 0.0
    for k, P in enumerate(GAPS):
        vs = P + off
        if T < vs: return T - off, None
        if T < vs + CH_GAP: return P, (k, T - vs)
        off += CH_GAP
    return T - off, None

def render(T):
    global GAPINFO
    t, GAPINFO = remap(T)
    load_assets()
    surf = skia.Surface(W4, H4); c = surf.getCanvas(); c.scale(SC, SC)
    if GAPINFO is not None:
        n, ttl, _ = CHAPTERS[GAPINFO[0]]
        chapter_card(c, GAPINFO[1], 0, n, ttl)
    else:
        i = find(t)
        if i is None: c.clear(hexc(NAVY))
        else:
            a, b, fn, tr = SHOTS[i]; TR = 0.35
            if tr == "fade" and t < a + TR and i > 0 and SHOTS[i - 1][1] >= a - 0.01:
                SHOTS[i - 1][2](c, t)
                k = ease_io(seg(t, a, a + TR)); s = lerp(1.04, 1.0, k)
                c.save(); c.translate(960, 540); c.scale(s, s); c.translate(-960, -540); c.saveLayerAlpha(None, int(255 * k)); fn(c, t); c.restore(); c.restore()
            else:
                c.save(); fn(c, t); c.restore()
        captions(c, t)
        if not in_host(t) and t > 0.4: watermark(c, LOGO, 140)
    vignette(c, 100); grain(c, T, 12)
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

def vo_to_video(t):
    return t + CH_GAP * sum(1 for P in GAPS if P <= t)

def still(T, out, scale=0.5):
    Image.fromarray(render(T)).convert("RGB").resize((int(3840 * scale), int(2160 * scale)), Image.LANCZOS).save(out)

def encode_chunk(i0, i1, out, fps=60, preview=False):
    if preview:
        args = ["-vf", "scale=1920:1080", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p"]
    else:
        args = ["-c:v", "libx265", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p10le", "-x265-params", "log-level=error:pools=1", "-tag:v", "hvc1"]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W4}x{H4}", "-r", str(fps), "-i", "-"] + args + [out], stdin=subprocess.PIPE)
    for i in range(i0, i1): ff.stdin.write(render(i / fps).tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for tt in sys.argv[3:]: still(float(tt), f"{sys.argv[2]}/f_{float(tt):07.2f}.png")
    elif cmd == "chunk":
        encode_chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], preview=len(sys.argv) > 5 and sys.argv[5] == "preview")
    elif cmd == "demo_end":
        print(round(vo_to_video(DEMO_END), 2))
    elif cmd == "timeline":
        json.dump({"gaps": GAPS, "ch_gap": CH_GAP, "hosts": [[a, b] for a, b in HOSTS], "demo_end": DEMO_END,
                   "vo_end": UN[-1]["end"]}, open(ROOT + "audio/timeline.json", "w")); print("ok")
    elif cmd == "sfx":
        load_assets(); surf = skia.Surface(DW, DH); cc = surf.getCanvas()
        for a, b, fn, tr in SHOTS:
            for tt in np.arange(a + 0.01, b, 0.1): fn(cc, float(tt))
        ev = sorted([(n, round(vo_to_video(tt), 3), g) for n, tt, g in SFX], key=lambda x: x[1])
        json.dump(ev, open(ROOT + "audio/full_sfx.json", "w")); print(len(ev), "sfx events")
