"""AMRIT BORI Short - 'India ka sabse bada naksha kab tha?'  9:16, design 1080x1920 drawn x2 into 2160x3840.
Timing comes from voice/units.json once the user's VO is aligned; until then a placeholder table (EST) is used.
CLI:  python3 naksha.py still OUTDIR t1 t2 ...
"""
import os, sys, json, math, re
os.environ.setdefault("AB_PROJECT", "new-short"); os.environ.setdefault("AB_ORIENT", "vertical")
from core import *
from core import _poly_path
from widgets import *
from shapely.geometry import shape
from PIL import Image

ROOT = PROJ
from shapely.geometry import Polygon as _P, MultiPolygon as _MP
def _nohole(g): return _P(g.exterior) if g.geom_type == "Polygon" else _MP([_P(q.exterior) for q in g.geoms])
EMP = {k: _nohole(shape(v)) for k, v in json.load(open(os.path.join(os.path.dirname(__file__), "empires.geojson.json"))).items()}
EMP.update({k: shape(v) for k, v in json.load(open(os.path.join(os.path.dirname(__file__), "south_kingdoms.geojson.json"))).items()})
EMP_PATH = {k: _poly_path(g, 0) for k, g in EMP.items()}
COL = dict(MAURYA="#E9B93C", MUGHAL="#2FA36B", RAJ="#D7263D", NOW="#FF9933", CHOLA="#C62828", PANDYA="#1E5AA8", CHERA="#2E7D32")

# ---------------------------------------------------------------- timing from the aligned VO (voice/full_units.json)
UN = json.load(open(ROOT + "voice/full_units.json"))["units"]
VO_DUR = json.load(open(ROOT + "voice/full_units.json"))["duration"]
SIL = [tuple(map(float, l.split())) for l in open(ROOT + "voice/full_sil.tsv")]
def us(i): return UN[i]["start"]
def ue(i): return UN[i]["end"]
def kw(i, word, occ=0):
    """approximate start of `word` inside unit i (char-proportional, snapped to an internal pause)"""
    txt = UN[i]["text"]; low = txt.lower(); p_ = -1
    for _ in range(occ + 1): p_ = low.find(word.lower(), p_ + 1)
    if p_ < 0: return us(i)
    est = us(i) + (ue(i) - us(i)) * p_ / max(1, len(txt))
    best = None
    for a_, b_ in SIL:
        if us(i) < b_ < ue(i) and abs(b_ - est) < 0.35 and (best is None or abs(b_ - est) < abs(best - est)): best = b_
    return (best if best else est) - 0.05
SCENES = [("hook", 0), ("tease", 1), ("now", 2), ("rewind", 3), ("maurya", 4), ("kandahar", 6), ("msize", 7), ("south", 10),
          ("mughal", 11), ("gsize", 14), ("raj", 15), ("raj4", 17), ("rsize", 18), ("aden", 19), ("colonial", 20), ("cta", 21)]
TAIL = 1.9
T_TOTAL = round(VO_DUR + TAIL, 2)
SC_T = {}
for n_, (k_, u_) in enumerate(SCENES):
    a_ = 0.0 if n_ == 0 else us(u_) - 0.12
    b_ = (us(SCENES[n_ + 1][1]) - 0.12) if n_ + 1 < len(SCENES) else T_TOTAL
    SC_T[k_] = (a_, b_)
def T(k): return SC_T[k]

# phrase captions straight from the VO text (<= ~4 words, split at commas), keywords in yellow
CAP_KEYS = {"sabse", "bada", "india", "32", "lakh", "87", "hazaar", "2300", "ashoka", "maurya", "afghanistan", "bengal", "kandahar",
            "greek", "aramaic", "34", "50", "behes", "chola", "pandya", "chera", "bahar", "1690", "aurangzeb", "mughal", "bangladesh",
            "deccan", "40", "british", "raj", "pakistan", "myanmar", "yemen", "aden", "1937", "angrezon", "comment", "subscribe", "kaun"}
CAPS = []
for u in UN:
    parts = []
    for clause in re.split(r"(?<=,)\s+", u["text"]):
        w_ = clause.split()
        while w_:
            n_ = 4 if len(w_) > 5 else len(w_)
            parts.append(" ".join(w_[:n_])); w_ = w_[n_:]
    tot = sum(len(x) + 1 for x in parts); t0 = u["start"]
    for x in parts:
        d_ = (u["end"] - u["start"]) * (len(x) + 1) / tot
        CAPS.append((t0, t0 + d_, x)); t0 += d_
LOGO = None; LION = None
def load():
    global LOGO, LION
    if LOGO is None:
        LOGO = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_800.png").resize((200, 200)))
        LION = sk_image(Image.open(ROOT + "visuals/photos/lion_capital.jpg").convert("RGB"))
        for k_, f_ in (("ashoka", "ashoka_relief.jpg"), ("aurangzeb", "aurangzeb.jpg"), ("george5", "george5.jpg")):
            try: RULER[k_] = sk_image(Image.open(ROOT + "visuals/photos/" + f_).convert("RGB"))
            except Exception: RULER[k_] = None

RULER = {}
RULER_INFO = {  # name, line, credit, crop (x0,y0,x1,y1 as fractions)
    "ashoka": ("SAMRAT ASHOKA", "Sanchi relief, c. 1st century BCE", "Photo: Photo Dharma, CC BY 2.0, Wikimedia Commons", (0.18, 0.0, 0.88, 0.80)),
    "aurangzeb": ("AURANGZEB", "Aadhunik chitran (Mughal daur ka asli portrait nahi)", "Image: channel ke paas se", (0.24, 0.0, 0.80, 0.70)),
    "george5": ("KING GEORGE V", "Emperor of India 1910-1936", "Photo: Bassano Ltd, 1923, Library of Congress (public domain)", (0.0, 0.0, 1.0, 0.75)),
}
def ruler(c, key, kbig, kbadge, col, t):
    """big framed portrait (kbig) that shrinks into a corner badge over the Arabian Sea (kbadge)"""
    img = RULER.get(key)
    if img is None or kbig <= 0: return
    name, line, credit, cr = RULER_INFO[key]
    iw, ih = img.width(), img.height()
    src = skia.Rect(cr[0] * iw, cr[1] * ih, cr[2] * iw, cr[3] * ih)
    asp = src.height() / src.width()
    m = ease_io(kbadge)
    w = lerp(470, 190, m); h = w * asp
    if h > lerp(620, 230, m): h = lerp(620, 230, m); w = h / asp
    cx = lerp(540, 150, m); cy = lerp(700, 950, m)
    al = int(255 * clamp(kbig * 2)); kk = back(clamp(kbig))
    if m < 0.01: c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(150 * clamp(kbig))))
    c.save(); c.translate(cx, cy); c.scale(kk, kk); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    pad = lerp(14, 8, m); capH = lerp(110, 52, m)
    rrect(c, l - pad, tp - pad, l + w + pad, tp + h + capH, lerp(20, 12, m), "#F4F1EA", al, shadow=26)
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(l, tp, l + w, tp + h), 8, 8), True)
    z = 1.0 + 0.05 * clamp((t % 6) / 6)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al, src=src); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, l + w, tp + h), 8, 8, paint(col, al, stroke=lerp(4, 3, m)))
    fit = lambda s_, size, fp: min(size, size * (w + pad - 10) / max(1, text_w(s_, size, fp)))
    text(c, name, cx, tp + h + lerp(48, 34, m), fit(name, lerp(40, 24, m), FT_BLACK), "#0F1B2D", FT_BLACK, "c", al)
    if m < 0.6:
        a2 = int(al * (1 - m / 0.6))
        text(c, line, cx, tp + h + 86, fit(line, 26, FT_SEMI), "#5B6472", FT_SEMI, "c", a2)
    c.restore()
    if m < 0.6: text(c, credit, cx, tp + h + capH + 40, 18, PAL["muted"], FT_SEMI, "c", int(al * (1 - m / 0.6)))

def photo_card(c, img, k, t, cx=540, cy=760, w=520, cap="", sub="", credit=""):
    """real photo in a gold frame; pops in with a slow Ken Burns push"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); kk = back(k)
    h = w * img.height() / img.width()
    c.save(); c.translate(cx, cy); c.scale(kk, kk); c.rotate(-2.5 * (1 - k)); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    rrect(c, l - 14, tp - 14, l + w + 14, tp + h + 120, 20, "#F4F1EA", al, shadow=30)
    c.save(); r = skia.RRect.MakeRectXY(skia.Rect(l, tp, l + w, tp + h), 10, 10); c.clipRRect(r, True)
    z = 1.0 + 0.06 * clamp(t % 10 / 3.0)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, l + w, tp + h), 10, 10, paint(COL["MAURYA"], al, stroke=4))
    fit = lambda s_, size, fp: min(size, size * (w - 20) / max(1, text_w(s_, size, fp)))
    text(c, cap, cx, tp + h + 52, fit(cap, 36, FT_BLACK), "#0F1B2D", FT_BLACK, "c", al)
    text(c, sub, cx, tp + h + 88, fit(sub, 26, FT_SEMI), "#5B6472", FT_SEMI, "c", al)
    c.restore()
    if credit: text(c, credit, cx, tp + h + 150, 18, PAL["muted"], FT_SEMI, "c", al)

# ---------------------------------------------------------------- camera keys (lon, lat, px/deg)
SA = (80, 22, 24)
CAM_KEYS = [(0.0, (80, 20, 6)), (2.2, SA), (T("rewind")[0], SA), (T("maurya")[0], (78, 22, 24.5)),
            (T("kandahar")[0], (74, 26, 26)), (T("kandahar")[0] + 2.5, (72, 27, 30)), (T("msize")[0] + 0.5, (72, 27, 30)),
            (T("south")[0], (78, 20, 25)), (kw(10, "Chola") - 0.5, (77.7, 10.2, 128)), (T("south")[1] - 0.1, (77.7, 10.2, 136)),
            (T("mughal")[0] + 1.6, (78, 22, 24)),
            (T("raj")[0], (80, 22, 22)), (T("aden")[0], (80, 21, 21)), (T("aden")[0] + 1.4, (66, 20, 17)),
            (T("colonial")[0], (66, 20, 17)), (T("colonial")[0] + 1.2, (80, 22, 21))]
def cam_at(t):
    for (t0, a), (t1, b) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_io(seg(t, t0, t1))
            s = math.exp(lerp(math.log(a[2]), math.log(b[2]), k))
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k), s)
    return CAM_KEYS[-1][1] if t > CAM_KEYS[-1][0] else CAM_KEYS[0][1]
MAP_CY = 820   # map vertical centre in design space (upper-middle, clear of Shorts UI)

def scr(cam, lon, lat):
    x, y = to_screen(cam, lon, lat); return x, y - DH / 2 + MAP_CY


# ---------------------------------------------------------------- waving flag / emblem textures blended inside borders
FTEX = {}
FLAG_NOTE = {"MAURYA": "PRATIK: ASHOKA CHAKRA (us daur ka flag record mein nahi)",
             "MUGHAL": "PRATIK: SHER-O-KHURSHID BANNER (andaazan chitran)",
             "RAJ": "FLAG: UNION JACK (BRITISH RAJ)", "NOW": "TIRANGA",
             "SOUTH": "PRATIK: CHOLA BAAGH, PANDYA MACHHLI, CHERA DHANUSH (andaazan seemayein)"}
def _surf_img(w, h, fn):
    sf = skia.Surface(w, h); cc = sf.getCanvas(); fn(cc, w, h); return sf.makeImageSnapshot()
def _chakra(cc, x, y, r, col, sw):
    cc.drawCircle(x, y, r, paint(col, 255, stroke=sw)); cc.drawCircle(x, y, r * 0.16, paint(col))
    for i in range(24):
        a_ = 2 * math.pi * i / 24
        cc.drawLine(x + math.cos(a_) * r * 0.16, y + math.sin(a_) * r * 0.16, x + math.cos(a_) * r, y + math.sin(a_) * r, paint(col, 255, stroke=sw * 0.45))
def _maurya_tex(cc, w, h):
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, h)], [hexc("#F2C14E"), hexc("#C8781E")])
    p_ = skia.Paint(); p_.setShader(sh); cc.drawRect(skia.Rect(0, 0, w, h), p_)
    for i in range(-2, 14):                     # faint diagonal weave
        cc.drawLine(i * 90, 0, i * 90 + h, h, paint("#FFFFFF", 28, stroke=10))
    _chakra(cc, w / 2, h * 0.47, min(w, h) * 0.34, "#0B2A6F", 14)
def _mughal_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#1E7B47"))
    cx, cy = w * 0.5, h * 0.36; h0 = h; h = min(w, h) * 0.95
    for i in range(32):                          # sun rays
        a_ = 2 * math.pi * i / 32; r0, r1 = h * 0.17, h * (0.30 if i % 2 else 0.25)
        pa = skia.Path(); pa.moveTo(cx + math.cos(a_ - 0.06) * r0, cy + math.sin(a_ - 0.06) * r0)
        pa.lineTo(cx + math.cos(a_) * r1, cy + math.sin(a_) * r1); pa.lineTo(cx + math.cos(a_ + 0.06) * r0, cy + math.sin(a_ + 0.06) * r0); pa.close()
        cc.drawPath(pa, paint("#F2C14E"))
    cc.drawCircle(cx, cy, h * 0.17, paint("#F2C14E"))
    g = "#E0A526"; k = h / 400; bx, by = cx, h0 * 0.62     # simple lion silhouette walking left
    cc.drawRoundRect(skia.Rect(bx - 95 * k, by - 32 * k, bx + 75 * k, by + 18 * k), 26 * k, 26 * k, paint(g))
    for lx in (-80, -50, 40, 62): cc.drawRoundRect(skia.Rect(bx + lx * k, by, bx + (lx + 16) * k, by + 58 * k), 6 * k, 6 * k, paint(g))
    cc.drawCircle(bx - 100 * k, by - 42 * k, 40 * k, paint("#C98A17")); cc.drawCircle(bx - 110 * k, by - 44 * k, 25 * k, paint(g))
    tl = skia.Path(); tl.moveTo(bx + 72 * k, by - 18 * k); tl.quadTo(bx + 130 * k, by - 40 * k, bx + 118 * k, by - 85 * k)
    cc.drawPath(tl, paint(g, 255, stroke=8 * k, cap_round=True)); cc.drawCircle(bx + 118 * k, by - 88 * k, 9 * k, paint("#C98A17"))
    cc.drawRect(skia.Rect(0, h0 * 0.93, w, h0), paint("#F2C14E"))
def _kingdom_tex(kind, field):
    def fn(cc, w, h):
        cc.drawRect(skia.Rect(0, 0, w, h), paint(field))
        cc.drawRect(skia.Rect(0, 0, w, h * 0.06), paint("#F2C14E")); cc.drawRect(skia.Rect(0, h * 0.94, w, h), paint("#F2C14E"))
        emblem(cc, kind, w / 2, h / 2, min(w, h) * 0.36, 1.0, badge=False, bg=field)
    return fn
def _tiranga_tex(cc, w, h):
    """tiranga sized to India's box: bands fill India, a smaller chakra sits on mainland India's centre"""
    b = EMP_PATH["NOW"].getBounds(); bw, bh = b.width(), b.height()
    mx, my = cam_xy(78.6, 22.6)
    fx = (mx - (b.centerX() - bw * 1.06 / 2)) / (bw * 1.06); fy = (my - (b.centerY() - bh * 1.08 / 2)) / (bh * 1.08)
    cy = fy * h; band = h * 0.16
    cc.drawRect(skia.Rect(0, 0, w, cy - band), paint("#FF9933"))
    cc.drawRect(skia.Rect(0, cy - band, w, cy + band), paint("#FFFFFF"))
    cc.drawRect(skia.Rect(0, cy + band, w, h), paint("#138808"))
    _chakra(cc, fx * w, cy, band * 0.82, "#000080", max(3, band * 0.07))
def _img_tex(code):
    im = flag_img(code)
    return _surf_img(900, int(900 * im.height() / im.width()), lambda cc, w, h: draw_img(cc, im, 0, 0, w, h))
def flag_tex(key):
    if key not in FTEX:
        asp = lambda k_: EMP_PATH[k_].getBounds().height() / EMP_PATH[k_].getBounds().width()
        FTEX[key] = {"MAURYA": lambda: _surf_img(900, int(900 * asp("MAURYA")), _maurya_tex), "MUGHAL": lambda: _surf_img(900, int(900 * asp("MUGHAL")), _mughal_tex),
                     "RAJ": lambda: _img_tex("gb"), "NOW": lambda: _img_tex("in"),
                     "NOWV": lambda: _surf_img(900, int(900 * asp("NOW")), _tiranga_tex),
                     "CHOLA": lambda: _surf_img(700, int(700 * asp("CHOLA")), _kingdom_tex("tiger", "#B3261E")),
                     "PANDYA": lambda: _surf_img(700, int(700 * asp("PANDYA")), _kingdom_tex("fish", "#1D4F91")),
                     "CHERA": lambda: _surf_img(700, int(700 * asp("CHERA")), _kingdom_tex("bow", "#2F6B2F"))}[key]()
    return FTEX[key]

def wave_flag(c, path, key, t, a, s, center=None):
    """draws the flag texture inside `path` (canvas already in map coords), waving like cloth"""
    if a <= 0: return
    img = flag_tex(key); iw, ih = img.width(), img.height()
    b = path.getBounds(); bw, bh = b.width(), b.height()
    if key == "NOW":                              # tiranga: keep proportions, cover the box
        sc = max(bw / iw, bh / ih) * (1.08 if center is None else 1.45); w, h = iw * sc, ih * sc
    else:                                         # whole flag/emblem fits the empire box
        w = bw * 1.06; h = max(bh * 1.08, w * ih / iw)
    fx, fy = (b.centerX(), b.centerY()) if center is None else center
    x0, y0 = fx - w / 2, fy - h / 2
    c.save(); c.clipPath(path, doAntiAlias=True)
    lp = skia.Paint(); lp.setAlphaf(clamp(a / 255) * 0.5)
    c.saveLayer(skia.Rect(x0, y0 - h * 0.1, x0 + w, y0 + h * 1.1), lp)   # strips drawn opaque, blended once
    n = 140; amp = h * 0.022; pw = w / n
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n
        ph = 2 * math.pi * (u0 * 1.6 - t * 0.55)
        dy = math.sin(ph) * amp * (0.3 + 0.7 * u0)
        c.drawImageRect(img, skia.Rect(u0 * iw, 0, min(iw, u1 * iw + 2), ih), skia.Rect(x0 + u0 * w, y0 + dy, x0 + u1 * w + pw * 0.6, y0 + h + dy), SAMP, skia.Paint())
    cols, pos = [], []
    for i in range(n + 1):
        u = i / n; sh = math.cos(2 * math.pi * (u * 1.6 - t * 0.55))
        cols.append(skia.ColorSetARGB(int(abs(sh) * 40), 255, 255, 255) if sh > 0 else skia.ColorSetARGB(int(abs(sh) * 55), 0, 0, 0)); pos.append(u)
    gp = skia.Paint(); gp.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x0 + w, 0)], cols, pos))
    c.drawRect(skia.Rect(x0, y0 - amp * 2, x0 + w, y0 + h + amp * 2), gp)
    c.restore(); c.restore()

def flag_note(c, key, k, y0=1086):
    if k <= 0: return
    s_ = FLAG_NOTE[key]; size = 22; w = text_w(s_, size, FT_SEMI)
    al = int(255 * clamp(k * 2)); x1 = DW - 36
    if y0 != 1086: x1 = DW / 2 + (w + 36) / 2
    rrect(c, x1 - w - 36, y0, x1, y0 + 38, 19, "#0F1B2D", int(al * 0.8))
    c.drawCircle(x1 - w - 18, y0 + 19, 6, paint(PAL["yel"], al))
    text(c, s_, x1 - 14, y0 + 27, size, "#DCE3EC", FT_SEMI, "r", al)

def draw_emp(c, cam, key, a, fill_a=150, stroke=4, draw_k=1.0, col=None, t=0.0, flag=True):
    if a <= 0: return
    col = col or COL[key]
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
    path = EMP_PATH[key]
    c.drawPath(path, paint(col, int((fill_a * 0.55 if flag else fill_a) * a / 255)))
    if flag: wave_flag(c, path, key, t, a * clamp(draw_k * 1.5 - 0.5), s)
    pm = skia.PathMeasure(path, False); out = skia.Path()
    while True:                      # progressive outline draw
        L = pm.getLength(); pm.getSegment(0, L * clamp(draw_k), out, True)
        if not pm.nextContour(): break
    glow = paint(col, int(a * 0.5), stroke=(stroke + 8) / s, blur=6 / s)
    c.drawPath(out, glow); c.drawPath(out, paint("#FFF4D6", a, stroke=stroke / s))
    c.restore()

def base_map(c, cam, t, india_k=1.0, india_a=200):
    c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"]))
    c.save(); c.translate(0, MAP_CY - DH / 2)
    draw_map(c, WM, cam, fills={"IND": (COL["NOW"], int(india_a * india_k))})
    c.restore()

# ---------------------------------------------------------------- overlay widgets
def headline(c, s, k, col="#F1FAEE", y=230, size=92, sub=None):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); dy = (1 - ease_out(k)) * 40
    size = min(size, size * 960 / max(1, text_w(s, size)))
    text(c, s, DW / 2, y + dy, size, col, FT_BLACK, "c", al, shadow=True)
    w = text_w(s, size) * ease_out(seg(k, 0.3, 1))
    c.drawRect(skia.Rect(DW / 2 - w / 2, y + dy + 22, DW / 2 + w / 2, y + dy + 30), paint(PAL["axis"], al))
    if sub: text(c, sub, DW / 2, y + dy + 90, 44, PAL["yel"], FT_SEMI, "c", al)

def caption(c, s, k):
    if k <= 0 or not s: return
    al = int(255 * clamp(k * 3)); size = 62
    w = text_w(s, size)
    if w > 960: size *= 960 / w; w = 960
    kk = 0.85 + 0.15 * back(clamp(k))
    c.save(); c.translate(DW / 2, 1390); c.scale(kk, kk)
    rrect(c, -w / 2 - 24, -size * 0.95, w / 2 + 24, size * 0.38, 16, "#000000", int(al * 0.6))
    x = -w / 2
    for i, word in enumerate(s.split(" ")):
        key = re.sub(r"[^a-z0-9]", "", word.lower())
        col = PAL["yel"] if key in CAP_KEYS else "#FFFFFF"
        x += text(c, word + " ", x, 0, size, col, FT_BLACK, "l", al)
    c.restore()

TL = [(-250, "250 BCE"), (1690, "1690"), (1920, "1920"), (2026, "AAJ")]
def timeline(c, year, k):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); x0, x1, y = 110, 970, 1220
    def X(yr):  # piecewise so BCE fits
        pts = [(-300, x0), (1600, x0 + 300), (1800, x0 + 520), (2026, x1)]
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= yr <= b: return lerp(xa, xb, (yr - a) / (b - a))
        return x0 if yr < -300 else x1
    c.drawRoundRect(skia.Rect(x0, y - 4, x1, y + 4), 4, 4, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 4, X(year), y + 4), 4, 4, paint(PAL["yel"], al))
    for yr, lab in TL:
        on = abs(yr - year) < 30
        c.drawCircle(X(yr), y, 12 if on else 8, paint(PAL["yel"] if X(yr) <= X(year) + 1 else "#3E5068", al))
        text(c, lab, X(yr), y + 52, 30 if on else 24, "#F1FAEE" if on else PAL["muted"], FT_BLACK if on else FT_SEMI, "c", al)
    lab = f"{-int(year)} BCE" if year < 0 else f"{int(year)}"
    pill(c, lab, X(year), y - 50, 34, PAL["yel"], fg="#0F1B2D", a=al)

def year_at(t):
    y90 = kw(11, "1690"); yb = us(16)
    keys = [(0, 2026), (T("rewind")[0], 2026), (T("rewind")[1] - 0.3, -250), (y90 - 0.5, -250), (y90 + 0.4, 1690),
            (yb - 0.2, 1690), (yb + 0.8, 1920), (T("cta")[0], 1920), (T("cta")[0] + 1.0, 2026)]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp(a, b, ease_io(seg(t, t0, t1)))
    return 2026

def label(c, s, x, y, k, col="#F1FAEE", size=34, bg=PAL["ocean"]):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); kk = back(k)
    c.save(); c.translate(x, y); c.scale(kk, kk)
    pill(c, s, 0, 0, size, bg, fg=col, a=al, shadow=8)
    c.restore()

def arrow(c, p0, p1, k, col=PAL["yel"]):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 80
    route(c, [p0, (mx, my), p1], ease_out(k), col=col, w=6, dash=False)

def highlight_country(c, cam, code, k, t, col="#FFD166"):
    """glowing, pulsing highlight of a modern country (Natural Earth geometry) on the map"""
    if k <= 0: return
    key = "HL_" + code
    if key not in EMP_PATH: EMP_PATH[key] = _poly_path(WM.geoms[code], 0.01)
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]; pulse = 0.75 + 0.25 * math.sin(t * 6.0)
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
    path = EMP_PATH[key]; al = clamp(k)
    c.drawPath(path, paint(col, int(95 * al * pulse)))
    c.drawPath(path, paint(col, int(200 * al), stroke=14 / s, blur=8 / s))
    c.drawPath(path, paint("#FFFFFF", int(255 * al), stroke=3.5 / s))
    c.restore()

def spotlight(c, x, y, k, t, r0=95, col="#FFD166"):
    """darkens everything except a circle around (x, y), with a pulsing ring"""
    if k <= 0: return
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r0 * 3.2, [skia.ColorSetARGB(0, 0, 0, 0), skia.ColorSetARGB(int(165 * clamp(k)), 4, 8, 18)], [0.3, 1.0])
    p_ = skia.Paint(); p_.setShader(sh); c.drawRect(skia.Rect(0, 0, DW, DH), p_)
    rp = (t % 1.1) / 1.1
    c.drawCircle(x, y, r0 * (0.55 + 0.25 * ease_out(clamp(k))), paint(col, int(255 * clamp(k)), stroke=6))
    c.drawCircle(x, y, r0 * (0.6 + 0.9 * rp), paint(col, int(200 * clamp(k) * (1 - rp)), stroke=5))

def ring_highlight(c, x, y, r, k, t, col="#FFD166"):
    """region without a modern border (Bengal, Deccan...): soft glow disc + pulsing double ring, no darkening"""
    if k <= 0: return
    al = clamp(k); kk = back(al); rp = (t % 1.0)
    c.drawCircle(x, y, r * kk, paint(col, int(70 * al)))
    c.drawCircle(x, y, r * kk, paint(col, int(230 * al), stroke=6))
    c.drawCircle(x, y, r * (1.0 + 0.6 * rp), paint(col, int(180 * al * (1 - rp)), stroke=4))

def wiki_card(c, k, t):
    """browser-frame card; page capture goes in visuals/docs/kandahar.png when available"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); dy = (1 - ease_out(k)) * 120
    x0, y0, w, h = 270, 740 + dy, 780, 430
    rrect(c, x0, y0, x0 + w, y0 + h, 18, "#FFFFFF", al, shadow=28)
    rrect(c, x0, y0, x0 + w, y0 + 58, 18, "#E9ECF1", al)
    for i, cc in enumerate(("#FF5F57", "#FEBC2E", "#28C840")): c.drawCircle(x0 + 30 + i * 26, y0 + 29, 8, paint(cc, al))
    rrect(c, x0 + 120, y0 + 12, x0 + w - 20, y0 + 46, 17, "#FFFFFF", al)
    text(c, "en.wikipedia.org/wiki/Kandahar_Bilingual_Rock_Inscription", x0 + 140, y0 + 37, 19, "#5B6472", FT_SEMI, "l", al)
    text(c, "Kandahar Bilingual Rock Inscription", x0 + 30, y0 + 115, 34, "#0F1B2D", FT_BLACK, "l", al)
    c.drawRect(skia.Rect(x0 + 30, y0 + 132, x0 + w - 30, y0 + 134), paint("#C8CCD1", al))
    lines = ["The Kandahar Bilingual Rock Inscription", "was carved by the Mauryan emperor Ashoka", "(r. 268-232 BCE) ... around c. 260 BCE.",
             "It is written exclusively in the Greek", "and Aramaic languages."]
    for i, ln in enumerate(lines):
        yy = y0 + 190 + i * 48
        if i >= 3:
            ws = kw(6, "Greek") if i == 3 else kw(6, "Aramaic")
            hk = ease_out(seg(t, ws, ws + 0.6))
            hp = paint("#FFD166", int(210 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(x0 + 28, yy - 31, x0 + 28 + text_w(ln, 30, FT_SEMI) * hk + 6, yy + 10), hp)
        text(c, ln, x0 + 30, yy, 30, "#202122", FT_SEMI, "l", al)
    text(c, "Source: Wikipedia", x0 + w - 30, y0 + h - 24, 20, "#5B6472", FT_SEMI, "r", al)

def cmp_bars(c, k):
    items = [("AAJ KA BHARAT", 3.29, 3.29, COL["NOW"], "3.29M"), ("MAURYA", 3.4, 5.0, COL["MAURYA"], "3.4-5.0M"),
             ("MUGHAL", 4.0, 4.0, COL["MUGHAL"], "4.0M"), ("BRITISH RAJ", 4.99, 4.99, "#D7263D", "4.99M")]
    x, y, w, maxv = 110, 380, 700, 5.2
    for i, (lab, v0, v1, col, txt) in enumerate(items):
        kk = ease_out(seg(k, i * 0.15, 0.6 + i * 0.15)); yy = y + i * 150
        if kk <= 0: continue
        al = int(255 * clamp(kk * 2))
        text(c, lab, x, yy, 34, "#F1FAEE", FT_BLACK, "l", al)
        rrect(c, x, yy + 18, x + w, yy + 78, 30, "#22304A", al)
        rrect(c, x, yy + 18, x + w * v0 / maxv * kk, yy + 78, 30, col, al)
        if v1 > v0:
            p_ = paint(col, int(al * 0.45)); c.drawRoundRect(skia.Rect(x, yy + 18, x + w * v1 / maxv * kk, yy + 78), 30, 30, p_)
            c.drawRoundRect(skia.Rect(x, yy + 18, x + w * v1 / maxv * kk, yy + 78), 30, 30, paint(col, al, stroke=3))
        text(c, txt, x + w * v1 / maxv * kk + 18, yy + 64, 38, "#F1FAEE", FT_BLACK, "l", al)

def subscribe_btn(c, k, t, t_click):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); clicked = t >= t_click + 0.35
    kk = back(clamp(k)) * (1 - 0.08 * math.sin(math.pi * seg(t, t_click + 0.25, t_click + 0.45)))
    cx, cy = DW / 2, 1255
    c.save(); c.translate(cx, cy); c.scale(kk, kk)
    w = 420; bg = "#3A3F4B" if clicked else "#E62117"
    rrect(c, -w / 2, -44, w / 2, 44, 44, bg, al, shadow=14)
    text(c, "SUBSCRIBED" if clicked else "SUBSCRIBE", 22, 15, 40, "#FFFFFF", FT_BLACK, "c", al)
    bx = -w / 2 + 52                                   # bell
    pb = skia.Path(); pb.moveTo(bx - 14, 10); pb.quadTo(bx - 14, -20, bx, -20); pb.quadTo(bx + 14, -20, bx + 14, 10); pb.close()
    c.drawPath(pb, paint("#FFFFFF", al)); c.drawCircle(bx, 15, 5, paint("#FFFFFF", al))
    c.restore()
    if t < t_click + 0.9:                              # cursor slides in and clicks
        m = ease_out(seg(t, t_click - 0.4, t_click + 0.2)); px, py = lerp(cx + 330, cx + 60, m), lerp(cy + 170, cy + 18, m)
        pc = skia.Path(); pc.moveTo(px, py); pc.lineTo(px, py + 46); pc.lineTo(px + 12, py + 35); pc.lineTo(px + 22, py + 56)
        pc.lineTo(px + 30, py + 52); pc.lineTo(px + 20, py + 32); pc.lineTo(px + 36, py + 32); pc.close()
        c.drawPath(pc, paint("#FFFFFF", al)); c.drawPath(pc, paint("#000000", al, stroke=2.5))

def emblem(c, kind, x, y, r, k, t=0.0, badge=True, bg=None):
    """circular dynasty badge with a code-drawn emblem: tiger (Chola), fish (Pandya), bow (Chera)"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); kk = back(clamp(k), 2.0)
    bg = bg or {"tiger": "#A61E1E", "fish": "#1D4F91", "bow": "#2F6B2F"}[kind]; gold = "#F2C14E"
    c.save(); c.translate(x, y); c.scale(kk, kk)
    if badge:
        c.drawCircle(4, 7, r + 6, paint("#000000", int(al * 0.45), blur=10))
        c.drawCircle(0, 0, r + 6, paint(gold, al)); c.drawCircle(0, 0, r, paint(bg, al))
    u = r / 50.0
    if kind == "tiger":                                   # tiger face
        for sx in (-1, 1):
            e = skia.Path(); e.moveTo(sx * 30 * u, -18 * u); e.lineTo(sx * 36 * u, -40 * u); e.lineTo(sx * 14 * u, -30 * u); e.close()
            c.drawPath(e, paint("#F28C28", al))
        c.drawOval(skia.Rect(-32 * u, -32 * u, 32 * u, 30 * u), paint("#F28C28", al))
        c.drawOval(skia.Rect(-20 * u, 2 * u, 20 * u, 26 * u), paint("#FFF3E0", al))
        for sx in (-1, 1):
            for j in range(3):
                st = skia.Path(); yy = (-6 + j * 9) * u
                st.moveTo(sx * 32 * u, yy); st.quadTo(sx * 22 * u, yy + 2 * u, sx * 18 * u, yy + 6 * u)
                c.drawPath(st, paint("#1A1A1A", al, stroke=3.2 * u, cap_round=True))
            c.drawCircle(sx * 11 * u, -6 * u, 4 * u, paint("#1A1A1A", al))
        for j in (-1, 0, 1):
            fs = skia.Path(); fs.moveTo(j * 8 * u, -31 * u); fs.lineTo(j * 6 * u, -18 * u)
            c.drawPath(fs, paint("#1A1A1A", al, stroke=3.2 * u, cap_round=True))
        nz = skia.Path(); nz.moveTo(-6 * u, 6 * u); nz.lineTo(6 * u, 6 * u); nz.lineTo(0, 13 * u); nz.close(); c.drawPath(nz, paint("#3A1F1F", al))
    elif kind == "fish":                                  # Pandya double fish, facing each other
        for sx in (-1, 1):
            c.save(); c.scale(sx, 1)
            f = skia.Path(); f.moveTo(-4 * u, 0); f.cubicTo(-12 * u, -16 * u, -30 * u, -14 * u, -36 * u, -3 * u)
            f.lineTo(-46 * u, -14 * u); f.lineTo(-44 * u, 0); f.lineTo(-46 * u, 14 * u); f.lineTo(-36 * u, 3 * u)
            f.cubicTo(-30 * u, 14 * u, -12 * u, 16 * u, -4 * u, 0); f.close()
            c.save(); c.translate(0, -14 * u * (1 if sx > 0 else -1) * 0 ); c.rotate(-70); c.drawPath(f, paint(gold, al)); c.drawCircle(-12 * u, -3 * u, 2.6 * u, paint(bg, al)); c.restore()
            c.restore()
    else:                                                 # Chera bow and arrow
        bw = skia.Path(); bw.moveTo(-8 * u, -38 * u); bw.quadTo(30 * u, 0, -8 * u, 38 * u)
        c.drawPath(bw, paint(gold, al, stroke=6 * u, cap_round=True))
        c.drawLine(-8 * u, -38 * u, -8 * u, 38 * u, paint("#FFF3E0", al, stroke=2 * u))
        c.drawLine(-34 * u, 0, 30 * u, 0, paint("#FFF3E0", al, stroke=3.5 * u, cap_round=True))
        ah = skia.Path(); ah.moveTo(38 * u, 0); ah.lineTo(26 * u, -7 * u); ah.lineTo(26 * u, 7 * u); ah.close(); c.drawPath(ah, paint("#FFF3E0", al))
        for dy in (-5, 5): c.drawLine(-34 * u, 0, -40 * u, dy * u, paint("#FFF3E0", al, stroke=2.5 * u))
    c.restore()

PL = dict(patna=(85.14, 25.6), kandahar=(65.7, 31.6), afg=(66.5, 34.0), bengal=(88.5, 23.5), chola=(79.13, 10.79),
          pandya=(78.12, 9.93), chera=(76.3, 10.3), bangla=(90.3, 23.8), deccan=(77.0, 17.0), kabul=(69.2, 34.5),
          pak=(69.5, 29.5), mya=(96.6, 19.2), ind=(79.0, 22.5), bombay=(72.88, 19.07), aden=(45.03, 12.8))

# ---------------------------------------------------------------- frame
WM = None
def frame(c, t):
    global WM
    load()
    if WM is None: WM = WorldMap()
    cam = cam_at(t)
    def S(k): return scr(cam, *PL[k])
    def act(k, pad_in=0.0, pad_out=0.0):
        a, b = T(k); return a - pad_in <= t < b + pad_out
    def kin(k, d=0.5, off=0.0): return seg(t, T(k)[0] + off, T(k)[0] + off + d)

    yr = year_at(t)
    rw0, rw1 = T("rewind"); cta0 = T("cta")[0]; mg0 = T("mughal")[0]; br0 = us(16) - 0.2
    india_a = 200 * (1 - 0.75 * seg(t, rw0, rw1)) if t < cta0 else 200 * seg(t, cta0, cta0 + 1.0)
    base_map(c, cam, t, 1.0, india_a)
    now_a = 255 * seg(t, T("now")[0], T("now")[0] + 0.8) * (1 - seg(t, rw0, rw0 + 1.0)) + 255 * seg(t, cta0, cta0 + 0.8)
    if now_a > 0:
        if "NOW" not in EMP_PATH: EMP_PATH["NOW"] = _poly_path(WM.geoms["IND"], 0.01)
        cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
        wave_flag(c, EMP_PATH["NOW"], "NOWV", t, now_a, s_); c.restore()   # bands fill India, smaller chakra on mainland centre

    # empire layers with cross-fade morphs, keyed to the words
    m0 = T("maurya")[0]
    m_a = 255 * seg(t, m0, m0 + 1.6) * (1 - seg(t, mg0, mg0 + 1.4))
    g_a = 255 * seg(t, mg0 + 0.2, mg0 + 1.6) * (1 - seg(t, br0, br0 + 1.0))
    r_a = 255 * seg(t, br0 + 0.1, br0 + 1.1) * (1 - seg(t, cta0, cta0 + 0.8))
    if act("tease"):
        fl = int((t - T("tease")[0]) * 4) % 3
        draw_emp(c, cam, ["MAURYA", "MUGHAL", "RAJ"][fl], 200, fill_a=40, stroke=3, flag=False)
    if m_a > 0: draw_emp(c, cam, "MAURYA", m_a, draw_k=seg(t, m0, m0 + 1.6), t=t)
    if g_a > 0: draw_emp(c, cam, "MUGHAL", g_a, t=t)
    if r_a > 0:
        col = COL["RAJ"] if t < T("colonial")[0] else "#7A5560"
        draw_emp(c, cam, "RAJ", r_a, fill_a=150 - 70 * seg(t, *T("colonial")), col=col, t=t)

    def at(t0, d=0.45): return seg(t, t0, t0 + d)
    # Afghanistan highlight on the word (Maurya: through the Kandahar scene; Mughal: until 'Bangladesh')
    ha = at(kw(5, "Afghanistan") - 0.15, 0.4) * (1 - seg(t, T("kandahar")[1] - 0.4, T("kandahar")[1]))
    hb = at(kw(13, "Afghanistan") - 0.15, 0.4) * (1 - seg(t, kw(13, "Bangladesh"), kw(13, "Bangladesh") + 0.5))
    if ha > 0 or hb > 0: highlight_country(c, cam, "AFG", max(ha, hb), t)
    # every place named in the VO lights up on its word
    if act("mughal"):
        kb = kw(13, "Bangladesh")
        highlight_country(c, cam, "BGD", at(kb - 0.15, 0.35) * (1 - seg(t, T("mughal")[1] - 0.3, T("mughal")[1])), t)
    if act("raj4"):
        ws = [("IND", "India"), ("PAK", "Pakistan"), ("BGD", "Bangladesh"), ("MMR", "Myanmar")]
        t_all = kw(17, "sab") - 0.1; endk = 1 - seg(t, T("raj4")[1] - 0.3, T("raj4")[1])
        for j, (code, w) in enumerate(ws):
            t0 = kw(17, w) - 0.15; t1 = kw(17, ws[j + 1][1]) - 0.1 if j + 1 < len(ws) else t_all
            solo = at(t0, 0.3) * (1 - seg(t, t1, t1 + 0.25))
            highlight_country(c, cam, code, max(solo, at(t_all, 0.35)) * endk, t)
    if act("aden"):
        highlight_country(c, cam, "YEM", at(kw(19, "Yemen") - 0.15, 0.35) * (1 - seg(t, T("aden")[1] - 0.3, T("aden")[1])), t)
    # scene overlays
    if t < T("now")[0]:
        if t < T("tease")[0]: headline(c, "SABSE BADA NAKSHA?", seg(t, 0.2, 0.9), y=230)
        ic_question(c, *S("ind"), 220 * back(at(kw(0, "sabse"), 0.6)), a=int(255 * (1 - seg(t, T("tease")[0] - 0.3, T("tease")[0] + 0.1))))
    if act("tease"):
        headline(c, "JAWAB CHAUNKA DEGA!", kin("tease"), col=PAL["yel"])
    if act("now"):
        headline(c, "AAJ KA BHARAT", kin("now"))
        stat_card(c, 190, 340, 700, 230, counter_text(0, 3.29, seg(t, kw(2, "32"), kw(2, "square")), "{:.2f}M km²"),
                  "LAGBHAG 32.9 LAKH SQ KM", at(kw(2, "lagbhag") - 0.2, 0.6), col=COL["NOW"])
    if rw0 <= t < T("south")[1]:
        headline(c, "MAURYA SAMRAJYA", at(kw(4, "Maurya") - 0.2, 0.6), col=COL["MAURYA"], sub="Samrat Ashoka, c. 250 BCE")
    if act("rewind"):
        headline(c, "2300 SAAL PEECHE...", kin("rewind"), col=PAL["yel"])
        lk = kin("rewind", 0.5, 0.3) * (1 - seg(t, rw1 - 0.3, rw1))
        if lk > 0:
            c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(150 * lk)))
            photo_card(c, LION, lk, t - rw0, cx=540, cy=660, w=320, cap="ASHOKA KA LION CAPITAL",
                       sub="Sarnath, c. 250 BCE - aaj Bharat ka rashtriya chinh", credit="Photo: Chrisi1964, CC BY-SA 4.0, Wikimedia Commons")
    if act("maurya"):
        pin(c, *S("patna"), "PATALIPUTRA", at(us(5) - 0.1, 0.5), size=30, t=t, side="l")
        ka, kb = kw(5, "Afghanistan"), kw(5, "Bengal")
        arrow(c, S("patna"), S("afg"), at(ka, 0.7)); label(c, "AFGHANISTAN", S("afg")[0], S("afg")[1] - 60, at(ka + 0.4))
        ring_highlight(c, *S("bengal"), 62, at(kb - 0.1, 0.4) * (1 - seg(t, T("maurya")[1] - 0.3, T("maurya")[1])), t)
        arrow(c, S("patna"), S("bengal"), at(kb - 0.1, 0.5)); label(c, "BENGAL", S("bengal")[0] - 10, S("bengal")[1] + 100, at(kb + 0.2))
    if act("kandahar"):
        spotlight(c, *S("kandahar"), at(kw(6, "Kandahar") - 0.15, 0.5) * (1 - seg(t, T("kandahar")[1] - 0.4, T("kandahar")[1])), t)
        pin(c, *S("kandahar"), "KANDAHAR", at(kw(6, "Kandahar") - 0.1), size=36, t=t, side="r")
        wiki_card(c, at(kw(6, "Ashoka") - 0.2, 0.6) * (1 - seg(t, T("kandahar")[1] - 0.3, T("kandahar")[1])), t)
    if act("msize"):
        label(c, "SIZE?", DW / 2, 470, at(us(7) - 0.1, 0.35) * (1 - at(us(8) - 0.2, 0.2)), col="#0F1B2D", bg=PAL["yel"], size=64)
        stat_card(c, 165, 360, 750, 250, "3.4 - 5.0M km²", "34 SE 50 LAKH SQ KM", at(us(8) - 0.15, 0.6), col=COL["MAURYA"],
                  tag=None, sub="Taagepera 1979 / Turchin 2006")
        sk = at(kw(9, "historians") - 0.1, 0.4)
        if sk > 0: stamp(c, "HISTORIANS MEIN BEHES", DW / 2, 735, 46, PAL["axis"], sk)
    if act("south", 0, 0.6):
        out_k = 1 - seg(t, T("south")[1] - 0.2, T("south")[1] + 0.6)
        for nm, kind in (("CHOLA", "tiger"), ("PANDYA", "fish"), ("CHERA", "bow")):
            kk = at(kw(10, nm.capitalize()) - 0.1, 0.6) * out_k
            if kk <= 0: continue
            draw_emp(c, cam, nm, 255 * kk, fill_a=170, stroke=3, draw_k=kk, t=t)
            g_ = EMP[nm].representative_point(); x, y = scr(cam, g_.x, g_.y)
            label(c, nm, x + {"CHOLA": 20, "PANDYA": 20, "CHERA": -10}[nm], y + {"CHOLA": 105, "PANDYA": 125, "CHERA": 90}[nm], kk, col="#FFFFFF", bg="#0F1B2D", size=32)
        label(c, "MAURYA KE BAHAR", DW / 2, 400, at(kw(10, "bahar") - 0.1, 0.5) * out_k, col="#0F1B2D", bg=PAL["yel"], size=36)
        flag_note(c, "SOUTH", at(kw(10, "Chola") + 0.3) * out_k, y0=450)
    if mg0 <= t < T("gsize")[1]:
        headline(c, "MUGHAL SAMRAJYA", at(kw(12, "Mughal") - 0.2, 0.6), col=COL["MUGHAL"], sub="Aurangzeb, 1690")
        if t < us(12) - 0.2: headline(c, "PHIR AAYA 1690", at(mg0, 0.5), col=PAL["yel"])
    if act("mughal"):
        label(c, "AFGHANISTAN", S("kabul")[0], S("kabul")[1] - 40, at(kw(13, "Afghanistan") - 0.05))
        label(c, "BANGLADESH", S("bangla")[0] + 60, S("bangla")[1] - 85, at(kw(13, "Bangladesh") - 0.05))
        ring_highlight(c, *S("deccan"), 85, at(kw(13, "Deccan") - 0.15, 0.4) * (1 - seg(t, T("mughal")[1] - 0.3, T("mughal")[1])), t)
        label(c, "DECCAN", S("deccan")[0], S("deccan")[1], at(kw(13, "Deccan") - 0.05))
    if act("gsize"):
        stat_card(c, 190, 360, 700, 230, counter_text(0, 4.0, seg(t, kw(14, "40") - 0.3, kw(14, "square")), "{:.1f}M km²"),
                  "LAGBHAG 40 LAKH SQ KM", kin("gsize", 0.6), col=COL["MUGHAL"])
    if act("raj") and t < br0:
        headline(c, "AUR SABSE BADA?", kin("raj"), col=PAL["yel"])
    if br0 <= t < T("colonial")[1]:
        headline(c, "BRITISH RAJ", at(br0, 0.5), col="#FF5A6E", sub="SABSE BADA - c. 1920")
    if act("raj4"):
        for i, (k_, nm, fc) in enumerate((("ind", "INDIA", "in"), ("pak", "PAKISTAN", "pk"), ("bangla", "BANGLADESH", "bd"), ("mya", "MYANMAR", "mm"))):
            kk = at(kw(17, nm.capitalize() if nm != "INDIA" else "India") - 0.1, 0.4); x, y = S(k_)
            flag_circle(c, fc, x, y - 10, 34, k=back(kk))
            text(c, nm, x, y + 60, 26, "#FFFFFF", FT_BLACK, "c", int(255 * clamp(kk)), shadow=True)
        label(c, "SAB EK HI NAKSHA", DW / 2, 400, at(kw(17, "sab") - 0.1), col="#0F1B2D", bg=PAL["yel"], size=40)
    if act("rsize"):
        stat_card(c, 165, 360, 750, 250, "~5.0M km²", "LAGBHAG 50 LAKH SQ KM", at(us(18) - 0.15, 0.6), col="#FF5A6E", sub="British Raj (Wikipedia)")
    if act("aden"):
        p0, p1 = S("bombay"), S("aden")
        route(c, [p0, ((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 120), p1], ease_out(at(kw(19, "Yemen") - 0.3, 0.9)), col=PAL["yel"], w=5)
        pin(c, *p0, "BOMBAY", at(T("aden")[0] + 0.5), size=28, t=t)
        ring_highlight(c, *p1, 55, at(kw(19, "Aden") - 0.15, 0.45) * (1 - seg(t, T("aden")[1] - 0.3, T("aden")[1])), t)
        pin(c, *p1, "ADEN (YEMEN)", at(kw(19, "Aden") - 0.1), size=30, t=t, side="r")
        label(c, "1839 - 1937", p1[0] + 110, p1[1] + 70, at(kw(19, "1937") - 0.1, 0.5), col="#0F1B2D", bg=PAL["yel"], size=34)
        label(c, "BRITISH INDIA KA HISSA", DW / 2, 400, at(kw(19, "British") - 0.1), col="#FFFFFF", bg=PAL["axis"], size=38)
    if act("colonial"):
        flag_circle(c, "gb", DW / 2, 640, 70, k=back(kin("colonial", 0.5)))
        stamp(c, "COLONIAL RULE", 610, 990, 60, PAL["axis"], at(kw(20, "angrezon") - 0.1, 0.4))
    if act("cta", 0, 1):
        k = kin("cta", 0.6)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(200 * k)))
        headline(c, "AAPKE HISAAB SE?", k, y=230)
        cmp_bars(c, seg(t, cta0 + 0.3, cta0 + 2.2))
        label(c, "MAURYA  YA  MUGHAL?", DW / 2, 1040, at(us(22) - 0.1, 0.5), col="#0F1B2D", bg=PAL["yel"], size=46)
        label(c, "COMMENT KARO", DW / 2, 1140, at(kw(23, "Comment") - 0.1, 0.5), col="#FFFFFF", bg=PAL["axis"], size=40)
        subscribe_btn(c, at(kw(23, "subscribe") - 0.4, 0.5), t, kw(23, "subscribe"))

    if m_a > 60 and us(5) + 0.4 < t < T("kandahar")[0] or T("msize")[0] < t < T("msize")[1]: flag_note(c, "MAURYA", m_a / 255)
    if g_a > 60 and t > us(13) + 0.3: flag_note(c, "MUGHAL", g_a / 255)
    if r_a > 60 and us(17) + 0.4 < t < T("aden")[0]: flag_note(c, "RAJ", r_a / 255)
    # rulers: big card on the name, then a badge over the Arabian Sea for the rest of the era
    a0 = us(4) - 0.1
    if a0 <= t < T("south")[1]:
        ruler(c, "ashoka", at(a0, 0.4) * (1 - seg(t, T("south")[1] - 0.3, T("south")[1])), seg(t, us(5) - 0.45, us(5) + 0.1), COL["MAURYA"], t)
    g0 = us(12) - 0.1
    if g0 <= t < T("gsize")[1]:
        ruler(c, "aurangzeb", at(g0, 0.4) * (1 - seg(t, T("gsize")[1] - 0.3, T("gsize")[1])), seg(t, us(13) - 0.45, us(13) + 0.1), COL["MUGHAL"], t)
    r0 = us(16) + 0.2
    if r0 <= t < T("aden")[0]:
        ruler(c, "george5", at(r0, 0.4) * (1 - seg(t, T("aden")[0] - 0.3, T("aden")[0])), seg(t, us(17) - 0.3, us(17) + 0.25), "#FF5A6E", t)
    if T("colonial")[0] <= t < T("colonial")[1]:
        ruler(c, "george5", seg(t, T("colonial")[0], T("colonial")[0] + 0.3), 1.0, "#FF5A6E", t)

    if 0.6 < t < cta0:
        timeline(c, yr, seg(t, 0.6, 1.2))
    for a, b, cap in CAPS:
        if a - 0.05 <= t < b + 0.12: caption(c, cap, seg(t, a - 0.05, a + 0.08)); break
    if t > 2.0 and not act("kandahar") and t < T("cta")[0]:
        text(c, "Approx. historical borders: historical-basemaps (A. Ourednik)", DW / 2, 1505, 19, PAL["muted"], FT_SEMI, "c", 210)
        text(c, "Natural Earth; India boundary as per Survey of India", DW / 2, 1532, 19, PAL["muted"], FT_SEMI, "c", 210)
    draw_img(c, LOGO, DW - 150, 40, DW - 40, 150, 200)
    grain(c, t, 8); vignette(c, 120)

def render_still(t, out):
    surf = skia.Surface(W4, H4); c = surf.getCanvas(); c.scale(SC, SC)
    frame(c, t)
    surf.makeImageSnapshot().save(out, skia.kPNG)

if __name__ == "__main__":
    if sys.argv[1] == "still":
        od = sys.argv[2]; os.makedirs(od, exist_ok=True)
        for ts in sys.argv[3:]:
            render_still(float(ts), f"{od}/s_{float(ts):06.2f}.png"); print("ok", ts)

def sfx_events():
    """(name, time, gain_db) keyed to the same word times as the visuals"""
    E = [("whoosh_long", 0.15, -14), ("pop", kw(0, "sabse"), -12), ("glitch", T("tease")[0] + 0.05, -16)]
    for k_ in ("now", "rewind", "maurya", "kandahar", "msize", "south", "mughal", "gsize", "raj", "raj4", "rsize", "aden", "colonial", "cta"):
        E.append(("whoosh_fast", T(k_)[0], -19))
    E += [("pop", kw(2, "lagbhag"), -15), ("ding", kw(2, "square"), -18), ("riser", T("rewind")[0] + 0.1, -16), ("pop", T("rewind")[0] + 0.4, -15),
          ("pop", us(4) - 0.05, -14), ("drag", us(4) + 0.3, -18), ("pop", us(5) - 0.1, -17), ("whoosh_fast", kw(5, "Afghanistan"), -20),
          ("whoosh_fast", kw(5, "Bengal"), -20), ("pop", kw(6, "Kandahar") - 0.1, -15), ("pop", kw(6, "Ashoka") - 0.2, -16),
          ("drag", kw(6, "Greek"), -20), ("pop", us(7) - 0.1, -13), ("pop", us(8) - 0.15, -14), ("stamp", kw(9, "historians") - 0.1, -10),
          ("pop", kw(10, "Chola"), -16), ("pop", kw(10, "Pandya"), -16), ("pop", kw(10, "Chera"), -16), ("stamp", kw(10, "bahar") - 0.1, -13),
          ("whoosh_long", T("mughal")[0] + 0.1, -16), ("ding", kw(11, "1690"), -16), ("pop", us(12) - 0.1, -14),
          ("pop", kw(13, "Afghanistan"), -17), ("pop", kw(13, "Bangladesh"), -17), ("pop", kw(13, "Deccan"), -17), ("pop", us(14), -14),
          ("riser", T("raj")[0], -15), ("boom", us(16) - 0.2, -11), ("whoosh_long", us(16) - 0.2, -14), ("pop", us(16) + 0.2, -14)]
    for nm in ("India", "Pakistan", "Bangladesh", "Myanmar"): E.append(("pop", kw(17, nm) - 0.1, -16))
    E += [("stamp", kw(17, "sab") - 0.1, -14), ("pop", us(18) - 0.15, -14), ("whoosh_long", T("aden")[0] + 0.1, -15),
          ("pop", kw(19, "Aden") - 0.1, -14), ("ding", kw(19, "1937") - 0.1, -16), ("stamp", kw(20, "angrezon") - 0.1, -10),
          ("boom", kw(20, "angrezon") - 0.1, -18), ("pop", T("cta")[0] + 0.4, -16), ("pop", us(22) - 0.1, -13),
          ("pop", kw(23, "Comment") - 0.1, -14), ("ding", kw(23, "subscribe") + 0.35, -12)]
    return sorted(E, key=lambda e: e[1])
