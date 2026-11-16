"""AMRIT BORI Short - 'India ko India naam kisne diya?'  9:16, design 1080x1920 drawn x2 into 2160x3840.
Timing comes from voice/full_units.json (aligned VO). CLI:  python3 short_storyboard.py still OUTDIR t1 t2 ...
"""
import os, sys, json, math, re
os.environ.setdefault("AB_PROJECT", "new-short"); os.environ.setdefault("AB_ORIENT", "vertical")
from core import *
from core import _poly_path
from widgets import *
from shapely.geometry import shape
from PIL import Image

ROOT = PROJ
HERE = os.path.dirname(os.path.abspath(__file__))
from shapely.geometry import Polygon as _P, MultiPolygon as _MP
def _nohole(g): return _P(g.exterior) if g.geom_type == "Polygon" else _MP([_P(q.exterior) for q in g.geoms])
EMP = {k: _nohole(shape(v)) for k, v in json.load(open(os.path.join(HERE, "ancient.geojson.json"))).items()}
EMP_PATH = {k: _poly_path(g, 0) for k, g in EMP.items()}
COL = dict(PERSIA="#B8323A", GREEK="#2F6FB5", NOW="#FF9933", RIVER="#4FC3F7")
INDUS = json.load(open(os.path.join(HERE, "indus.json")))["INDUS"]
# South-Asian polities per era (historical-basemaps, approximate) - drawn in bhagwa shades in the historical scenes
_ERA_SKIP = {"Mon States", "Arakan", "Abbasid Caliphate", "Khmer Empire", "Emirate of the White Sheep Turks", "Pegu", "Ming Empire",
             "Muscat", "Hadramaut", "Ayutthaya", "Simhala", "Lambakannas", "Sinhalese kingdoms", "Nepal"}
ERAS = {k: [(f["name"], shape(f["geom"])) for f in v if f["name"] not in _ERA_SKIP]
        for k, v in json.load(open(os.path.join(HERE, "eras.geojson.json"))).items()}
ERA_PATH = {k: [(n, _poly_path(g, 0)) for n, g in v] for k, v in ERAS.items()}
ERA_LABEL = {"BC500": "c. 500 BCE ka naksha: Mahajanapada", "CE300": "c. 300 CE ka naksha", "CE900": "c. 900 CE ka naksha",
             "CE1492": "1492 ka naksha"}
BHAGWA = ["#FF9933", "#F28A22", "#FFB054", "#E67A16", "#FFA347", "#F59B3A"]

# ---------------------------------------------------------------- timing from the aligned VO (voice/full_units.json)
UN = json.load(open(ROOT + "voice/full_units.json"))["units"]
VO_DUR = json.load(open(ROOT + "voice/full_units.json"))["duration"]
SIL = [tuple(map(float, l.split())) for l in open(ROOT + "voice/full_sil.tsv") if l.strip()]
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
SCENES = [("hook", 0), ("river", 2), ("darius", 4), ("shift", 5), ("hindush", 6), ("notrel", 7), ("greek", 8), ("english", 11),
          ("hindustan", 12), ("columbus", 14), ("bharat", 16), ("article", 19), ("cta", 20)]
TAIL = 1.9
T_TOTAL = round(VO_DUR + TAIL, 2)
SC_T = {}
for n_, (k_, u_) in enumerate(SCENES):
    a_ = 0.0 if n_ == 0 else us(u_) - 0.12
    b_ = (us(SCENES[n_ + 1][1]) - 0.12) if n_ + 1 < len(SCENES) else T_TOTAL
    SC_T[k_] = (a_, b_)
def T(k): return SC_T[k]

# phrase captions straight from the VO text (<= ~4 words, split at commas), keywords in yellow
CAP_KEYS = {"india", "sindhu", "nadi", "tibet", "ladakh", "pakistan", "arabian", "sea", "2500", "persia", "darius", "s", "h", "hindu",
            "hindush", "jagah", "dharm", "greek", "indos", "latin", "english", "stan", "hindustan", "1492", "columbus", "america",
            "indians", "bharat", "rigveda", "bharata", "bharatavarsha", "samvidhan", "article", "1", "mitti", "comment", "subscribe", "naam"}
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

LOGO = None; CONST = None
RULER = {}
SCRIPT = {}
RULER_INFO = {  # name, line, credit, crop (x0,y0,x1,y1 as fractions)
    "darius": ("RAJA DARIUS I", "Behistun shilalekh ki asli nakkashi, c. 520 BCE", "Photo: Rumlu, public domain, Wikimedia Commons", (0.0, 0.02, 0.92, 0.66)),
    "columbus": ("CHRISTOPHER COLUMBUS", "Sebastiano del Piombo, 1519 - 'shayad Columbus' (pakka nahi)", "Metropolitan Museum of Art, public domain", (0.18, 0.02, 0.86, 0.56)),
}
def load():
    global LOGO, CONST
    if LOGO is None:
        LOGO = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_800.png").resize((200, 200)))
        CONST = sk_image(Image.open(ROOT + "visuals/photos/const.jpg").convert("RGB"))
        rv = Image.open(ROOT + "visuals/photos/rigveda.jpg").convert("RGB"); rv = rv.crop((0, 0, rv.width, int(rv.height * 0.47)))
        SCRIPT["rigveda"] = sk_image(rv); SCRIPT["purana"] = sk_image(Image.open(ROOT + "visuals/photos/purana.jpg").convert("RGB"))
        for k_, f_ in (("darius", "darius.jpg"), ("columbus", "columbus.jpg")):
            try: RULER[k_] = sk_image(Image.open(ROOT + "visuals/photos/" + f_).convert("RGB"))
            except Exception: RULER[k_] = None

MAP_CY = 820   # map vertical centre in design space (upper-middle, clear of Shorts UI)
def scr(cam, lon, lat):
    x, y = to_screen(cam, lon, lat); return x, y - DH / 2 + MAP_CY

# ---------------------------------------------------------------- symbol textures blended inside borders
FTEX = {}
FLAG_NOTE = {"PERSIA": "PRATIK: ACHAEMENID SHAHI BAAZ BANNER (andaazan chitran)",
             "GREEK": "PRATIK: GREEK MEANDER + ULLU (andaazan chitran)", "NOW": "TIRANGA"}
def _persia_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#9E1B24"))
    for i in range(-2, 16): cc.drawLine(i * 80, 0, i * 80 + h, h, paint("#FFFFFF", 18, stroke=8))
    cc.drawRect(skia.Rect(0, 0, w, h * 0.05), paint("#E8B84A")); cc.drawRect(skia.Rect(0, h * 0.95, w, h), paint("#E8B84A"))
    g = "#E8B84A"; cx, cy = w * 0.46, h * 0.5; k = min(w, h) / 420            # stylised falcon, wings spread
    for sx in (-1, 1):
        wg = skia.Path(); wg.moveTo(cx, cy - 10 * k)
        wg.cubicTo(cx + sx * 60 * k, cy - 70 * k, cx + sx * 140 * k, cy - 80 * k, cx + sx * 190 * k, cy - 60 * k)
        for j in range(5):
            yy = cy - 60 * k + j * 22 * k
            wg.lineTo(cx + sx * (190 - j * 22) * k, yy); wg.lineTo(cx + sx * (170 - j * 22) * k, yy + 14 * k)
        wg.lineTo(cx + sx * 20 * k, cy + 30 * k); wg.close(); cc.drawPath(wg, paint(g))
    cc.drawOval(skia.Rect(cx - 26 * k, cy - 40 * k, cx + 26 * k, cy + 70 * k), paint(g))
    cc.drawCircle(cx, cy - 58 * k, 22 * k, paint(g))
    bk = skia.Path(); bk.moveTo(cx + 18 * k, cy - 62 * k); bk.lineTo(cx + 40 * k, cy - 52 * k); bk.lineTo(cx + 16 * k, cy - 46 * k); bk.close()
    cc.drawPath(bk, paint("#C98A17"))
    tl = skia.Path(); tl.moveTo(cx - 22 * k, cy + 64 * k); tl.lineTo(cx, cy + 115 * k); tl.lineTo(cx + 22 * k, cy + 64 * k); tl.close(); cc.drawPath(tl, paint(g))
def _greek_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#1F5FA8"))
    def meander(y0, sz):
        x = 0; p_ = paint("#FFFFFF", 255, stroke=sz * 0.18)
        while x < w:
            pa = skia.Path(); pa.moveTo(x, y0 + sz); pa.lineTo(x, y0); pa.lineTo(x + sz * 0.8, y0); pa.lineTo(x + sz * 0.8, y0 + sz * 0.6)
            pa.lineTo(x + sz * 0.4, y0 + sz * 0.6); pa.lineTo(x + sz * 0.4, y0 + sz * 0.3); cc.drawPath(pa, p_)
            cc.drawLine(x, y0 + sz, x + sz, y0 + sz, p_); x += sz
    sz = h * 0.12; meander(h * 0.04, sz); meander(h * 0.96 - sz, sz)
    cx, cy, r = w / 2, h / 2, min(w, h) * 0.22                                   # owl
    cc.drawOval(skia.Rect(cx - r * 0.8, cy - r, cx + r * 0.8, cy + r * 1.1), paint("#FFFFFF"))
    for sx in (-1, 1):
        cc.drawCircle(cx + sx * r * 0.33, cy - r * 0.35, r * 0.28, paint("#1F5FA8")); cc.drawCircle(cx + sx * r * 0.33, cy - r * 0.35, r * 0.12, paint("#FFFFFF"))
        e = skia.Path(); e.moveTo(cx + sx * r * 0.45, cy - r * 0.9); e.lineTo(cx + sx * r * 0.75, cy - r * 1.25); e.lineTo(cx + sx * r * 0.75, cy - r * 0.7); e.close()
        cc.drawPath(e, paint("#FFFFFF"))
    bk = skia.Path(); bk.moveTo(cx - r * 0.1, cy - r * 0.12); bk.lineTo(cx + r * 0.1, cy - r * 0.12); bk.lineTo(cx, cy + r * 0.12); bk.close(); cc.drawPath(bk, paint("#E8B84A"))
def _gr_flag(cc, w, h):                     # Greece (no PNG in the flag set): 9 stripes + canton cross
    for i in range(9): cc.drawRect(skia.Rect(0, i * h / 9, w, (i + 1) * h / 9 + 1), paint("#0D5EAF" if i % 2 == 0 else "#FFFFFF"))
    cw = h * 5 / 9; cc.drawRect(skia.Rect(0, 0, cw, cw), paint("#0D5EAF"))
    cc.drawRect(skia.Rect(cw * 0.4, 0, cw * 0.6, cw), paint("#FFFFFF")); cc.drawRect(skia.Rect(0, cw * 0.4, cw, cw * 0.6), paint("#FFFFFF"))
def _bs_flag(cc, w, h):                     # Bahamas
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#00778B")); cc.drawRect(skia.Rect(0, h / 3, w, 2 * h / 3), paint("#FFC72C"))
    tr = skia.Path(); tr.moveTo(0, 0); tr.lineTo(w * 0.42, h / 2); tr.lineTo(0, h); tr.close(); cc.drawPath(tr, paint("#000000"))
def flag_tex(key):
    if key not in FTEX and key.startswith("F_"):
        iso = key[2:]
        FTEX[key] = {"gr": lambda: _surf_img(900, 600, _gr_flag), "bs": lambda: _surf_img(1000, 500, _bs_flag)}.get(iso, lambda: _img_tex(iso))()
    if key not in FTEX:
        asp = lambda k_: EMP_PATH[k_].getBounds().height() / EMP_PATH[k_].getBounds().width()
        FTEX[key] = {"PERSIA": lambda: _surf_img(1000, int(1000 * asp("PERSIA")), _persia_tex),
                     "GREEK": lambda: _surf_img(700, int(700 * max(0.6, asp("GREEK"))), _greek_tex),
                     "NOW": lambda: _img_tex("in"),
                     "NOWV": lambda: _surf_img(900, int(900 * asp("NOW")), _tiranga_tex)}[key]()
    return FTEX[key]

def ruler(c, key, kbig, kbadge, col, t, bxy=(150, 950)):
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
    cx = lerp(540, bxy[0], m); cy = lerp(700, bxy[1], m)
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

def _surf_img(w, h, fn):
    sf = skia.Surface(w, h); cc = sf.getCanvas(); fn(cc, w, h); return sf.makeImageSnapshot()

def _chakra(cc, x, y, r, col, sw):
    cc.drawCircle(x, y, r, paint(col, 255, stroke=sw)); cc.drawCircle(x, y, r * 0.16, paint(col))
    for i in range(24):
        a_ = 2 * math.pi * i / 24
        cc.drawLine(x + math.cos(a_) * r * 0.16, y + math.sin(a_) * r * 0.16, x + math.cos(a_) * r, y + math.sin(a_) * r, paint(col, 255, stroke=sw * 0.45))

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

def wave_flag(c, path, key, t, a, s, center=None):
    """draws the flag texture inside `path` (canvas already in map coords), waving like cloth"""
    if a <= 0: return
    img = flag_tex(key); iw, ih = img.width(), img.height()
    b = path.getBounds(); bw, bh = b.width(), b.height()
    if key == "NOW" or key.startswith("F_"):      # real flags: keep proportions, cover the country box
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

def draw_emp(c, cam, key, a, fill_a=150, stroke=2.4, draw_k=1.0, col=None, t=0.0, flag=True):
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
    glow = paint(col, int(a * 0.5), stroke=(stroke + 4) / s, blur=4 / s)
    c.drawPath(out, glow); c.drawPath(out, paint("#FFF4D6", a, stroke=stroke / s))
    c.restore()

def base_map(c, cam, t, india_k=1.0, india_a=200, border_a=1.0):
    c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"]))
    c.save(); c.translate(0, MAP_CY - DH / 2)
    draw_map(c, WM, cam, fills={"IND": (COL["NOW"], int(india_a * india_k))}, border_a=border_a)
    c.restore()

def headline(c, s, k, col="#F1FAEE", y=230, size=92, sub=None):
    """word-by-word reveal: each word rises, un-blurs and settles with a soft overshoot; underline sweeps; sub types in"""
    if k <= 0: return
    size = min(size, size * 960 / max(1, text_w(s, size)))
    words = s.split(" "); sp = text_w(" ", size); ws = [text_w(w_, size) for w_ in words]
    tot = sum(ws) + sp * (len(words) - 1); x = DW / 2 - tot / 2; n = len(words)
    for i, (w_, ww) in enumerate(words and zip(words, ws)):
        p = clamp((k * (1 + 0.35 * (n - 1)) - 0.35 * i) / 1.0)
        if p > 0:
            e = back(p, 1.3) if p < 1 else 1.0
            al = int(255 * clamp(p * 1.8)); dy = (1 - e) * 46
            c.save(); c.translate(x + ww / 2, y + dy); sc = 0.86 + 0.14 * e; c.scale(sc, sc)
            text(c, w_, 0, 0, size, col, FT_BLACK, "c", al, shadow=True); c.restore()
        x += ww + sp
    uk = ease_out(seg(k, 0.35, 1.0)); w = tot * uk
    al = int(255 * clamp(k * 2))
    c.drawRect(skia.Rect(DW / 2 - w / 2, y + 22, DW / 2 + w / 2, y + 30), paint(PAL["axis"], al))
    if sub:
        sk = seg(k, 0.45, 1.0); nch = int(round(len(sub) * ease_out(sk)))
        if nch > 0: text(c, sub[:nch], DW / 2, y + 90, 44, PAL["yel"], FT_SEMI, "c", int(255 * clamp(sk * 3)))

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
    c.drawPath(path, paint(col, int(170 * al), stroke=7 / s, blur=4 / s))
    c.drawPath(path, paint("#FFF1C2", int(255 * al), stroke=1.8 / s))
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

def render_still(t, out):
    surf = skia.Surface(W4, H4); c = surf.getCanvas(); c.scale(SC, SC)
    frame(c, t)
    surf.makeImageSnapshot().save(out, skia.kPNG)


# ---------------------------------------------------------------- camera keys (lon, lat, px/deg)
SA = (79, 23, 24)
RIV = (73.5, 28, 40); PER = (52, 31, 16); SIN = (69.5, 27.5, 40); GRK = (47, 33, 14); EUR = (30, 42, 8.5)
HST = (62, 29, 15); ATL = (-40, 28, 7); IND = (80, 22, 22)
CAM_KEYS = [(0.0, (78, 22, 6)), (2.2, SA), (T("river")[0], SA), (T("river")[0] + 1.0, RIV), (T("darius")[0], RIV),
            (T("darius")[0] + 1.4, PER), (T("shift")[0], PER), (T("shift")[0] + 1.1, SIN), (T("greek")[0], SIN),
            (T("greek")[0] + 1.2, GRK), (T("english")[0], GRK), (T("english")[0] + 1.0, EUR), (T("hindustan")[0], EUR),
            (T("hindustan")[0] + 1.0, HST), (T("columbus")[0], HST), (T("columbus")[0] + 1.5, ATL), (T("bharat")[0], ATL),
            (T("bharat")[0] + 1.4, IND)]
def cam_at(t):
    for (t0, a), (t1, b) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_io(seg(t, t0, t1))
            s = math.exp(lerp(math.log(a[2]), math.log(b[2]), k))
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k), s)
    return CAM_KEYS[-1][1] if t > CAM_KEYS[-1][0] else CAM_KEYS[0][1]

PL = dict(tibet=(81.2, 31.2), ladakh=(77.6, 34.2), pak=(69.3, 30.2), arab=(66.0, 22.8), sindh=(68.6, 26.0), indus_lbl=(71.6, 31.6),
          persepolis=(52.9, 29.9), iran=(54.0, 32.5), greece=(22.5, 39.0), rome=(12.5, 41.9), england=(-1.5, 52.5),
          palos=(-6.9, 37.2), canary=(-15.5, 28.1), sansal=(-74.5, 24.1), ind=(79.0, 22.5), spain=(-4.0, 40.0))

# ---------------------------------------------------------------- timeline
TL = [(-516, "516 BCE"), (262, "262 CE"), (1492, "1492"), (2026, "AAJ")]
def timeline(c, year, k):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); x0, x1, y = 110, 970, 1220
    def X(yr):
        pts = [(-600, x0), (0, x0 + 260), (1000, x0 + 430), (1500, x0 + 620), (2026, x1)]
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= yr <= b: return lerp(xa, xb, (yr - a) / (b - a))
        return x0 if yr < -600 else x1
    c.drawRoundRect(skia.Rect(x0, y - 4, x1, y + 4), 4, 4, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 4, X(year), y + 4), 4, 4, paint(PAL["yel"], al))
    for yr, lab in TL:
        on = abs(yr - year) < 30
        c.drawCircle(X(yr), y, 12 if on else 8, paint(PAL["yel"] if X(yr) <= X(year) + 1 else "#3E5068", al))
        text(c, lab, X(yr), y + 52, 30 if on else 24, "#F1FAEE" if on else PAL["muted"], FT_BLACK if on else FT_SEMI, "c", al)
    lab = f"c. {-int(year)} BCE" if year < 0 else (f"{int(year)} CE" if year < 1000 else f"{int(year)}")
    pill(c, lab, X(year), y - 50, 34, PAL["yel"], fg="#0F1B2D", a=al)

def year_at(t):
    d0 = T("darius")[0]; g0 = T("greek")[0]; e0 = T("english")[0]; h0 = T("hindustan")[0]; c0 = T("columbus")[0]
    b0 = T("bharat")[0]; a0 = T("article")[0]
    keys = [(0, 2026), (d0, 2026), (d0 + 1.3, -516), (g0, -516), (g0 + 0.8, -440), (e0, -440), (e0 + 1.0, 900), (h0, 900),
            (h0 + 0.8, 262), (c0, 262), (c0 + 1.2, 1492), (b0, 1492), (b0 + 1.2, 2026), (a0, 2026), (a0 + 0.8, 1950), (T("cta")[0], 1950)]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp(a, b, ease_io(seg(t, t0, t1)))
    return 2026

# ---------------------------------------------------------------- the river
def draw_river(c, cam, k, a, t, glow=1.0, head=None):
    if a <= 0 or k <= 0: return
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    if "INDUS" not in EMP_PATH:
        p_ = skia.Path(); x0, y0 = cam_xy(*INDUS[0]); p_.moveTo(x0, y0)
        for q in INDUS[1:]: p_.lineTo(*cam_xy(*q))
        EMP_PATH["INDUS"] = p_
    pm = skia.PathMeasure(EMP_PATH["INDUS"], False); out = skia.Path(); L = pm.getLength()
    pm.getSegment(0, L * clamp(k), out, True)
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
    pul = 0.8 + 0.2 * math.sin(t * 5)
    c.drawPath(out, paint("#06101E", int(a * 0.75), stroke=10 / s, cap_round=True))        # dark casing: readable over tiranga/bhagwa
    c.drawPath(out, paint(COL["RIVER"], int(a * 0.45 * glow * pul), stroke=16 / s, blur=9 / s, cap_round=True))
    c.drawPath(out, paint("#BFEFFF", int(a), stroke=5 / s, cap_round=True))
    c.restore()
    if head is not None and 0 < head < 1:      # bright pulse travelling source -> sea over the full river
        tr = skia.Path(); pm2 = skia.PathMeasure(EMP_PATH["INDUS"], False)
        pm2.getSegment(L * max(0, head - 0.12), L * head, tr, True)
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
        c.drawPath(tr, paint("#FFFFFF", int(a), stroke=7 / s, cap_round=True)); c.restore()
        pos = pm2.getPosTan(L * head)
        if pos:
            px, py = (pos[0].x() - cx) * s + DW / 2, (pos[0].y() - cy) * s + MAP_CY
            c.drawCircle(px, py, 18, paint("#BFEFFF", int(a * 0.8), blur=8)); c.drawCircle(px, py, 7, paint("#FFFFFF", int(a)))
    if k < 1:                                   # glowing head of the river while it draws
        pos = pm.getPosTan(L * clamp(k))
        if pos:
            px, py = (pos[0].x() - cx) * s + DW / 2, (pos[0].y() - cy) * s + MAP_CY
            c.drawCircle(px, py, 14, paint("#FFFFFF", int(a * 0.9), blur=6)); c.drawCircle(px, py, 6, paint("#FFFFFF", int(a)))

# ---------------------------------------------------------------- big morphing word
def word_row(c, letters, cx, cy, size, a=255, glow=None):
    """letters: list of dicts {ch, w (width 0..1), al (0..1), col, dy, sy (flip scale)}; centred on cx"""
    if a <= 0: return
    ws = [text_w(L["ch"], size) * L.get("w", 1) for L in letters]
    x = cx - sum(ws) / 2
    if glow:
        tw = sum(ws); rrect(c, cx - tw / 2 - 40, cy - size * 0.95, cx + tw / 2 + 40, cy + size * 0.32, 26, "#0B1424", int(a * 0.82), shadow=20)
        c.drawRoundRect(skia.Rect(cx - tw / 2 - 40, cy - size * 0.95, cx + tw / 2 + 40, cy + size * 0.32), 26, 26, paint(glow, int(a * 0.9), stroke=4))
    for L, w_ in zip(letters, ws):
        al = int(a * clamp(L.get("al", 1)))
        if al > 0 and L.get("w", 1) > 0.02:
            lx = x + w_ / 2
            c.save(); c.translate(lx, cy - size * 0.33 + L.get("dy", 0)); c.scale(1, max(0.02, L.get("sy", 1))); c.rotate(L.get("rot", 0))
            text(c, L["ch"], 0, size * 0.33, size, L.get("col", "#F1FAEE"), FT_BLACK, "c", al, shadow=True)
            c.restore()
            if L.get("strike", 0) > 0:
                sk_ = L["strike"]; c.drawLine(lx - w_ * 0.6, cy - size * 0.7, lx - w_ * 0.6 + w_ * 1.2 * sk_, cy + size * 0.05, paint("#FF4D5E", al, stroke=10, cap_round=True))
        x += w_
def flip(ch0, ch1, p, col0="#F1FAEE", col1=None):
    """letter that flips from ch0 to ch1 as p goes 0 -> 1"""
    col1 = col1 or PAL["yel"]
    return dict(ch=ch0 if p < 0.5 else ch1, sy=abs(math.cos(math.pi * clamp(p))), col=col0 if p < 0.5 else col1)
def Lw(ch, col="#F1FAEE", w=1, al=1, dy=0, rot=0, strike=0): return dict(ch=ch, col=col, w=w, al=al, dy=dy, rot=rot, strike=strike)

def chip(c, s, x, y, k, bg="#22304A", fg="#F1FAEE", size=34):
    label(c, s, x, y, k, col=fg, size=size, bg=bg)

def wiki_card(c, k, t, y0=900):
    """browser-frame card with the Wikipedia 'Hindush' etymology line; yellow highlighter on the spoken words"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); dy = (1 - ease_out(k)) * 120
    x0, y0, w, h = 120, y0 + dy, 840, 300
    rrect(c, x0, y0, x0 + w, y0 + h, 18, "#FFFFFF", al, shadow=28)
    rrect(c, x0, y0, x0 + w, y0 + 52, 18, "#E9ECF1", al)
    for i, cc in enumerate(("#FF5F57", "#FEBC2E", "#28C840")): c.drawCircle(x0 + 28 + i * 24, y0 + 26, 7, paint(cc, al))
    rrect(c, x0 + 110, y0 + 10, x0 + w - 20, y0 + 42, 16, "#FFFFFF", al)
    text(c, "en.wikipedia.org/wiki/Hindush", x0 + 130, y0 + 33, 19, "#5B6472", FT_SEMI, "l", al)
    text(c, "Hindush - Etymology", x0 + 28, y0 + 98, 32, "#0F1B2D", FT_BLACK, "l", al)
    c.drawRect(skia.Rect(x0 + 28, y0 + 112, x0 + w - 28, y0 + 114), paint("#C8CCD1", al))
    lines = ["It is widely accepted that the name Hindush", "derives from Sindhu, the Sanskrit name of", "the Indus River ..."]
    ws = kw(7, "jagah") - 0.2
    for i, ln in enumerate(lines):
        yy = y0 + 160 + i * 44
        if i in (0, 1):
            hk = ease_out(seg(t, ws + i * 0.45, ws + i * 0.45 + 0.5))
            hp = paint("#FFD166", int(210 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(x0 + 26, yy - 29, x0 + 26 + text_w(ln, 28, FT_SEMI) * hk + 6, yy + 9), hp)
        text(c, ln, x0 + 28, yy, 28, "#202122", FT_SEMI, "l", al)
    text(c, "Source: Wikipedia", x0 + w - 28, y0 + h - 18, 18, "#5B6472", FT_SEMI, "r", al)

def article_card(c, k, t):
    """Constitution: real preamble page (tilted, behind) + Article 1 text card with highlighter"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); kk = back(clamp(k))
    iw, ih = CONST.width(), CONST.height()
    c.save(); c.translate(300, 560); c.rotate(-6 * kk); c.scale(kk, kk)
    w = 330; h = w * ih / iw
    rrect(c, -w / 2 - 10, -h / 2 - 10, w / 2 + 10, h / 2 + 10, 10, "#F4F1EA", al, shadow=24)
    draw_img(c, CONST, -w / 2, -h / 2, w / 2, h / 2, al)
    c.restore()
    text(c, "Preamble page, 1950 - calligraphy: P. B. N. Raizada, art: Beohar R. Sinha (public domain)", DW / 2, 1110, 17, PAL["muted"], FT_SEMI, "c", al)
    dy = (1 - ease_out(k)) * 80
    x0, y0, w2, h2 = 400, 520 + dy, 620, 470
    rrect(c, x0, y0, x0 + w2, y0 + h2, 18, "#FBF7EC", al, shadow=30)
    c.drawRoundRect(skia.Rect(x0, y0, x0 + w2, y0 + h2), 18, 18, paint("#C9A24A", al, stroke=4))
    text(c, "THE CONSTITUTION OF INDIA", x0 + w2 / 2, y0 + 62, 30, "#5A3E10", FT_BLACK, "c", al)
    text(c, "PART I - THE UNION AND ITS TERRITORY", x0 + w2 / 2, y0 + 102, 20, "#7A6A50", FT_SEMI, "c", al)
    c.drawRect(skia.Rect(x0 + 40, y0 + 122, x0 + w2 - 40, y0 + 124), paint("#C9A24A", al))
    text(c, "1. Name and territory of the Union.", x0 + 40, y0 + 180, 27, "#202122", FT_BLACK, "l", al)
    lines = [("(1) India, that is Bharat,", True), ("shall be a Union of States.", False)]
    hs = kw(19, "India") - 0.1
    for i, (ln, hl) in enumerate(lines):
        yy = y0 + 260 + i * 60
        if hl:
            hk = ease_out(seg(t, hs, hs + 1.0)); x_s = x0 + 40 + text_w("(1) ", 40, FT_SEMI)
            hp = paint("#FFD166", int(220 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(x_s - 4, yy - 40, x_s + (text_w(ln, 40, FT_SEMI) - text_w("(1) ", 40, FT_SEMI)) * hk + 4, yy + 12), hp)
        text(c, ln, x0 + 40, yy, 40, "#202122", FT_SEMI, "l", al)
    text(c, "Article 1(1)", x0 + 40, y0 + h2 - 40, 24, "#7A6A50", FT_SEMI, "l", al)

def manuscript_card(c, img, k, t, cx, cy, w, ang, cap, sub, credit):
    """sacred-text document card: warm golden halo, gold double frame, slow push-in, caption + credit"""
    if k <= 0 or img is None: return
    al = int(255 * clamp(k * 2)); kk = back(clamp(k), 1.4)
    h = w * img.height() / img.width()
    halo = skia.GradientShader.MakeRadial(skia.Point(cx, cy), w * 0.95, [skia.ColorSetARGB(int(150 * clamp(k)), 255, 190, 90), skia.ColorSetARGB(0, 255, 160, 60)])
    hp = skia.Paint(); hp.setShader(halo); c.drawCircle(cx, cy, w * 0.95, hp)
    for i in range(10):                                   # a few drifting light motes
        a_ = i * 2.4 + t * 0.6; r_ = w * (0.55 + 0.08 * math.sin(i * 1.7 + t))
        mx, my = cx + math.cos(a_) * r_, cy + math.sin(a_) * r_ * 0.8
        c.drawCircle(mx, my, 3 + (i % 3), paint("#FFE2A8", int(160 * clamp(k) * (0.5 + 0.5 * math.sin(t * 3 + i))), blur=2))
    c.save(); c.translate(cx, cy); c.rotate(ang * kk); c.scale(kk, kk); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    rrect(c, l - 18, tp - 18, l + w + 18, tp + h + 104, 18, "#FBF3DF", al, shadow=30)
    c.drawRoundRect(skia.Rect(l - 10, tp - 10, l + w + 10, tp + h + 96), 12, 12, paint("#C9A24A", al, stroke=3))
    c.save(); c.clipRect(skia.Rect(l, tp, l + w, tp + h))
    z = 1.0 + 0.05 * clamp((t % 8) / 4)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al); c.restore()
    c.drawRect(skia.Rect(l, tp, l + w, tp + h), paint("#B8862B", al, stroke=4))
    text(c, cap, cx, tp + h + 50, 38, "#7A1E0E", FT_BLACK, "c", al)
    text(c, sub, cx, tp + h + 84, 26, "#B5651D", FT_BLACK, "c", al)
    c.restore()
    text(c, credit, cx, tp + h + 140, 17, "#DCE3EC", FT_SEMI, "c", int(al * 0.9), shadow=True)

def poll(c, k, t):
    items = [("INDIA", "#2F6FB5"), ("BHARAT", "#FF9933"), ("HINDUSTAN", "#2FA36B")]
    for i, (s_, col) in enumerate(items):
        kk = ease_out(seg(k, i * 0.18, 0.5 + i * 0.18))
        if kk <= 0: continue
        y = 520 + i * 150; al = int(255 * clamp(kk * 2)); x0 = 160 + (1 - kk) * 200
        rrect(c, x0, y - 55, 920, y + 55, 55, "#18253A", al, shadow=14)
        c.drawCircle(x0 + 58, y, 36, paint(col, al)); text(c, "ABC"[i], x0 + 58, y + 14, 40, "#FFFFFF", FT_BLACK, "c", al)
        text(c, s_, x0 + 120, y + 20, 56, "#F1FAEE", FT_BLACK, "l", al)

def subscribe_btn(c, k, t, t_click):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); clicked = t >= t_click + 0.35
    kk = back(clamp(k)) * (1 - 0.08 * math.sin(math.pi * seg(t, t_click + 0.25, t_click + 0.45)))
    cx, cy = DW / 2, 1255
    c.save(); c.translate(cx, cy); c.scale(kk, kk)
    w = 420; bg = "#3A3F4B" if clicked else "#E62117"
    rrect(c, -w / 2, -44, w / 2, 44, 44, bg, al, shadow=14)
    text(c, "SUBSCRIBED" if clicked else "SUBSCRIBE", 22, 15, 40, "#FFFFFF", FT_BLACK, "c", al)
    bx = -w / 2 + 52
    pb = skia.Path(); pb.moveTo(bx - 14, 10); pb.quadTo(bx - 14, -20, bx, -20); pb.quadTo(bx + 14, -20, bx + 14, 10); pb.close()
    c.drawPath(pb, paint("#FFFFFF", al)); c.drawCircle(bx, 15, 5, paint("#FFFFFF", al))
    c.restore()
    if t < t_click + 0.9:
        m = ease_out(seg(t, t_click - 0.4, t_click + 0.2)); px, py = lerp(cx + 330, cx + 60, m), lerp(cy + 170, cy + 18, m)
        pc = skia.Path(); pc.moveTo(px, py); pc.lineTo(px, py + 46); pc.lineTo(px + 12, py + 35); pc.lineTo(px + 22, py + 56)
        pc.lineTo(px + 30, py + 52); pc.lineTo(px + 20, py + 32); pc.lineTo(px + 36, py + 32); pc.close()
        c.drawPath(pc, paint("#FFFFFF", al)); c.drawPath(pc, paint("#000000", al, stroke=2.5))

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
    def at(t0, d=0.45): return seg(t, t0, t0 + d)
    def out(k, d=0.3): return 1 - seg(t, T(k)[1] - d, T(k)[1])
    Y = PAL["yel"]

    yr = year_at(t)
    cta0 = T("cta")[0]; d0 = T("darius")[0]; b0 = T("bharat")[0]
    # each scene shows the map of ITS time (user request): today's tiranga India in the modern scenes,
    # solid bhagwa India in the Sindhu scene, period polities (historical-basemaps) in bhagwa shades in the historical scenes
    r0_ = T("river")[0]
    hist = seg(t, d0 - 0.3, d0 + 0.5) * (1 - seg(t, b0, b0 + 0.8))
    india_a = (200 + 30 * seg(t, r0_, r0_ + 0.8)) * (1 - hist)
    base_map(c, cam, t, 1.0, india_a, border_a=1 - 0.75 * hist)
    now_a = 255 * (1 - seg(t, r0_, r0_ + 0.8)) + 255 * seg(t, kw(17, "Bharat") - 0.2, kw(17, "Bharat") + 0.6)
    if now_a > 0:
        if "NOW" not in EMP_PATH: EMP_PATH["NOW"] = _poly_path(WM.geoms["IND"], 0.01)
        cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
        wave_flag(c, EMP_PATH["NOW"], "NOWV", t, min(255, now_a), s_); c.restore()
    e0, h0_, c0_ = T("english")[0], T("hindustan")[0], T("columbus")[0]
    ERA_ON = [("BC500", d0 - 0.3, e0 + 0.3), ("CE900", e0, h0_ + 0.3), ("CE300", h0_, c0_ + 0.3), ("CE1492", c0_, b0 + 0.4)]
    era_now = None
    for ek, ta, tb in ERA_ON:
        ea = seg(t, ta, ta + 0.6) * (1 - seg(t, tb - 0.3, tb + 0.3))
        if ea <= 0: continue
        if ea > 0.5: era_now = ek
        cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
        for j, (nm, pth) in enumerate(ERA_PATH[ek]):
            c.drawPath(pth, paint(BHAGWA[j % len(BHAGWA)], int(175 * ea)))
            c.drawPath(pth, paint("#FFE7C2", int(150 * ea), stroke=1.0 / s_))
        c.restore()

    # ancient empires (approximate borders) with waving symbol banners
    p_a = 255 * seg(t, kw(4, "Persia") - 0.2, kw(4, "Persia") + 1.2) * (1 - seg(t, T("shift")[0] + 0.6, T("shift")[0] + 1.4))
    if p_a > 0: draw_emp(c, cam, "PERSIA", p_a, draw_k=seg(t, kw(4, "Persia") - 0.2, kw(4, "Persia") + 1.4), t=t)
    g_a = 255 * seg(t, kw(8, "Greek") - 0.2, kw(8, "Greek") + 0.8) * (1 - seg(t, T("english")[0] + 0.3, T("english")[0] + 1.0))
    if g_a > 0: draw_emp(c, cam, "GREEK", g_a, fill_a=170, stroke=3, draw_k=seg(t, kw(8, "Greek") - 0.2, kw(8, "Greek") + 0.8), t=t)

    # real flag waving inside every country named in the VO, from its word to the end of that scene (user request)
    CFLAGS = [("PAK", "pk", kw(3, "Pakistan") - 0.15, T("river")[1]),
              ]   # modern flags only in modern scenes; historical scenes use period symbols
    for code3, iso, t_on, t_off in CFLAGS:
        if t_on <= t < t_off:
            fk = at(t_on, 0.45) * (1 - seg(t, t_off - 0.3, t_off))
            key = "HL_" + code3
            if key not in EMP_PATH: EMP_PATH[key] = _poly_path(WM.geoms[code3], 0.01)
            cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
            c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
            wave_flag(c, EMP_PATH[key], "F_" + iso, t, 255 * fk * 1.6, s_); c.restore()
            highlight_country(c, cam, code3, fk * 0.35, t)          # thin outline keeps the flag readable

    # the Indus: flashes on "nadi", draws source -> sea in the river scene, stays as a thin line through the Greek part
    # hook: on "nadi" the river draws cleanly from its Tibet source to the sea and stays; in the river scene a bright
    # pulse travels source -> sea along it, keyed to "Tibet ... Arabian Sea"
    hk_ = seg(t, kw(1, "nadi") - 0.15, kw(1, "nadi") + 0.95)
    rk = seg(t, kw(3, "Tibet") - 0.3, kw(3, "Sea") + 0.3)
    r_a = 255 * (1 - 0.55 * seg(t, T("darius")[0], T("darius")[0] + 1)) * (1 - seg(t, T("english")[0], T("english")[0] + 0.8))
    if hk_ > 0 and r_a > 0: draw_river(c, cam, max(0.01, hk_), r_a, t, head=rk if act("river") else None)

    # ---- every place lights up on its word
    if act("river"):
        e = out("river")
        ring_highlight(c, *S("tibet"), 48, at(kw(3, "Tibet") - 0.15, 0.4) * (1 - seg(t, kw(3, "Ladakh") + 0.3, kw(3, "Ladakh") + 0.6)), t)
        ring_highlight(c, *S("ladakh"), 48, at(kw(3, "Ladakh") - 0.15, 0.4) * (1 - seg(t, kw(3, "Pakistan"), kw(3, "Pakistan") + 0.3)), t)
        highlight_country(c, cam, "PAK", at(kw(3, "Pakistan") - 0.15, 0.4) * (1 - seg(t, kw(3, "Arabian"), kw(3, "Arabian") + 0.3)), t)
        ring_highlight(c, *S("arab"), 70, at(kw(3, "Arabian") - 0.15, 0.4) * e, t, col="#7FDBFF")
        label(c, "TIBET", S("tibet")[0] + 20, S("tibet")[1] + 85, at(kw(3, "Tibet") - 0.05) * e)
        label(c, "LADAKH", S("ladakh")[0] + 30, S("ladakh")[1] - 75, at(kw(3, "Ladakh") - 0.05) * e)
        label(c, "PAKISTAN", S("pak")[0] - 110, S("pak")[1] - 215, at(kw(3, "Pakistan") - 0.05) * e)
        label(c, "ARABIAN SEA", S("arab")[0] + 40, S("arab")[1] + 110, at(kw(3, "Arabian") - 0.05) * e, col="#7FDBFF")
        label(c, "SINDHU (INDUS)", S("indus_lbl")[0] + 150, S("indus_lbl")[1] + 20, at(us(2) + 0.2) * e, col="#0F1B2D", bg="#7FDBFF", size=36)
    if act("darius"):
        highlight_country(c, cam, "IRN", at(kw(4, "Persia") - 0.15, 0.4) * (1 - seg(t, kw(4, "Darius") - 0.3, kw(4, "Darius"))), t)
        label(c, "PERSIA (AAJ KA IRAN)", S("iran")[0], S("iran")[1] - 70, at(kw(4, "Persia") + 0.1) * out("darius"))
        p0, p1 = S("persepolis"), S("sindh")
        route(c, [p0, ((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 110), p1], ease_out(at(kw(4, "Sindhu") + 0.2, 0.6)), col=Y, w=6)
        ring_highlight(c, *p1, 40, at(kw(4, "jeeta") - 0.2, 0.4) * out("darius"), t)
    if act("shift", 0, 0) or act("hindush") or act("notrel"):
        hk = at(kw(6, "Hindush") - 0.15, 0.4) * (1 - seg(t, T("notrel")[1] - 0.3, T("notrel")[1]))
        ring_highlight(c, *S("sindh"), 70, hk, t)
        pin(c, *S("sindh"), "HINDUSH (andaazan)", hk, size=30, t=t, side="r")

    # ---- scene overlays
    if t < T("river")[0]:
        # hook: big "INDIA" glides in letter by letter (rise + stretch + fade), a light shine sweeps across it,
        # the "?" drops in on "kisne", the question builds word by word, then "JAWAB: EK NADI!" with a water ripple
        ho = 1 - seg(t, T("river")[0] - 0.35, T("river")[0])
        qd = seg(t, kw(0, "kisne") - 0.1, kw(0, "kisne") + 0.45)
        L = []
        for i, ch in enumerate("INDIA"):
            p = seg(t, 0.12 + i * 0.1, 0.12 + i * 0.1 + 0.6); e = back(p, 1.6) if p < 1 else 1.0
            L.append(dict(ch=ch, al=clamp(p * 1.6), dy=(1 - e) * 90, col="#FF9933" if i < 2 else ("#FFFFFF" if i < 4 else "#3FB950"), sy=0.55 + 0.45 * e))
        L.append(dict(ch="?", w=ease_out(qd), al=qd, dy=-(1 - back(qd, 2.2)) * 120 if qd < 1 else 0, col=Y, rot=(1 - qd) * -25))
        word_row(c, L, DW / 2, 300, 170, 255 * ease_io(seg(t, 0.05, 0.6)) * ho, glow=Y if t < kw(1, "nadi") - 0.2 else "#7FDBFF")
        sh = seg(t, 0.95, 1.6)                                    # shine sweep across the word
        if 0 < sh < 1:
            bw = text_w("INDIA", 170); x0 = DW / 2 - bw / 2 - 60 + (bw + 120) * ease_io(sh)
            g_ = skia.GradientShader.MakeLinear([skia.Point(x0 - 60, 0), skia.Point(x0 + 60, 0)],
                                                [skia.ColorSetARGB(0, 255, 255, 255), skia.ColorSetARGB(int(150 * ho), 255, 255, 255), skia.ColorSetARGB(0, 255, 255, 255)])
            pp = skia.Paint(); pp.setShader(g_); pp.setBlendMode(skia.BlendMode.kPlus)
            c.save(); c.skew(-0.25, 0); c.translate(75, 0); c.drawRect(skia.Rect(x0 - 60, 150, x0 + 60, 340), pp); c.restore()
        def pop_words(s_, t0, y, size, col, a_):
            ws = s_.split(" "); tw = sum(text_w(w_, size) for w_ in ws) + text_w(" ", size) * (len(ws) - 1); x = DW / 2 - tw / 2
            for i, w_ in enumerate(ws):
                p = seg(t, t0 + i * 0.11, t0 + i * 0.11 + 0.35); ww = text_w(w_, size)
                if p > 0:
                    e = back(p, 2.0) if p < 1 else 1.0
                    c.save(); c.translate(x + ww / 2, y + (1 - e) * 30); c.scale(0.7 + 0.3 * e, 0.7 + 0.3 * e)
                    text(c, w_, 0, 0, size, col, FT_BLACK, "c", int(255 * clamp(p * 2) * a_), shadow=True); c.restore()
                x += ww + text_w(" ", size)
        q1 = 1 - seg(t, us(1) - 0.3, us(1))
        if q1 > 0 and ho > 0: pop_words("YE NAAM KISNE DIYA?", kw(0, "naam") - 0.25, 408, 56, "#F1FAEE", q1 * ho)
        if t > kw(1, "nadi") - 0.3 and ho > 0:
            pop_words("JAWAB: EK NADI!", kw(1, "Jawab") - 0.1 if t < kw(1, "nadi") else kw(1, "Jawab") - 0.1, 408, 64, "#7FDBFF", ho * seg(t, us(1) - 0.3, us(1)))
            rk = seg(t, kw(1, "nadi") - 0.1, kw(1, "nadi") + 0.9)          # water ripple under the answer
            if rk > 0:
                pw = skia.Path(); x0, x1 = DW / 2 - 240, DW / 2 - 240 + 480 * ease_out(rk)
                for xx in range(int(x0), int(x1), 6):
                    yy = 440 + 7 * math.sin((xx - x0) / 34 - t * 8)
                    (pw.moveTo if xx == int(x0) else pw.lineTo)(xx, yy)
                c.drawPath(pw, paint("#7FDBFF", int(230 * ho), stroke=6, cap_round=True))
                c.drawPath(pw, paint("#7FDBFF", int(110 * ho), stroke=16, blur=8, cap_round=True))
        ic_question(c, *S("ind"), 220 * back(at(kw(0, "naam"), 0.6)), a=int(255 * (1 - seg(t, us(1) - 0.2, us(1) + 0.2))))
    if act("river"):
        headline(c, "SINDHU NADI", kin("river"), col="#7FDBFF", sub="Tibet se Arabian Sea tak")
    if act("darius"):
        headline(c, "c. 516 BCE: PERSIA", kin("darius", 0.5, 0.2), col="#FF6B75", sub="Raja Darius ne Sindhu ghaati jeeti")
    if act("shift") or act("hindush"):
        headline(c, "S BANA H", kin("shift"), col=Y, sub="Purani Persian mein")
        a_ = 255 * kin("shift", 0.5, 0.2) * (1 - seg(t, T("hindush")[1] - 0.3, T("hindush")[1]))
        pf = seg(t, kw(5, " H ") - 0.1, kw(5, " H ") + 0.4)         # S flips into H on the spoken "H"
        dh = seg(t, kw(6, "Hindu") - 0.1, kw(6, "Hindu") + 0.35)    # 'dh' -> 'd'
        sh = seg(t, kw(6, "Hindush") - 0.1, kw(6, "Hindush") + 0.35)
        L = [flip("S", "H", pf), Lw("I"), Lw("N"), Lw("D"), Lw("H", w=1 - dh, al=1 - dh * 1.5), Lw("U"),
             Lw("S", Y, w=sh, al=sh), Lw("H", Y, w=sh, al=sh)]
        word_row(c, L, DW / 2, 470, 120, a_, glow=Y)
        chip(c, "PURANI PERSIAN:  S  >  H", DW / 2, 585, at(kw(5, "Persian") - 0.1) * (1 - seg(t, us(6) - 0.2, us(6))), bg=Y, fg="#0F1B2D", size=32)
    if act("notrel"):
        headline(c, "SIRF JAGAH KA NAAM", kin("notrel"), col=Y)
        chip(c, "JAGAH KA NAAM  ✓", DW / 2 - 215, 345, at(kw(7, "jagah") - 0.1), bg="#2FA36B", size=36)
        chip(c, "DHARM NAHI  ✗", DW / 2 + 240, 345, at(kw(7, "dharm") - 0.1), bg=PAL["axis"], size=36)
        wiki_card(c, at(us(7) + 0.1, 0.6) * out("notrel"), t, y0=410)
    if act("greek", 0, 0.9):
        gout = 1 - seg(t, T("greek")[1] + 0.55, T("greek")[1] + 0.85)
        headline(c, "PHIR AAYE GREEK", kin("greek", 0.5, 0.1), col="#6FA8FF", sub="Herodotus, c. 440 BCE")
        a_ = 255 * at(us(9) - 0.2, 0.4) * gout
        hf = seg(t, kw(9, " H ") - 0.05, kw(9, " H ") + 0.7)          # H crossed out, falls and collapses
        io = seg(t, kw(10, "Indos") - 0.1, kw(10, "Indos") + 0.4)
        ia = seg(t, kw(10, "India") - 0.1, kw(10, "India") + 0.4)
        L = [Lw("H", "#FF4D5E" if hf > 0.05 else "#F1FAEE", w=1 - seg(hf, 0.5, 1), al=1 - seg(hf, 0.4, 1), dy=ease_in(hf) * 140, rot=hf * 35, strike=seg(hf, 0, 0.35)),
             Lw("I"), Lw("N"), Lw("D"), Lw("U", w=1 - io, al=1 - io * 1.4), flip("O", "I", ia, "#6FA8FF", Y) | dict(w=io, al=io),
             flip("S", "A", ia, "#6FA8FF", Y) | dict(w=io, al=io)]
        word_row(c, L, DW / 2, 470, 130, a_, glow="#6FA8FF")
        highlight_country(c, cam, "GRC", at(kw(8, "Greek") - 0.15, 0.4) * (1 - seg(t, us(9), us(9) + 0.4)), t, col="#9CC3FF")
        label(c, "GREECE", S("greece")[0], S("greece")[1] + 70, at(kw(8, "Greek")) * out("greek", 0.5))
        label(c, "INDOS = SINDHU NADI", S("sindh")[0] - 40, S("sindh")[1] + 90, at(kw(10, "Indos")) * (1 - at(kw(10, "India") - 0.1, 0.3)), col="#0F1B2D", bg="#7FDBFF", size=30)
        label(c, "INDIA = NADI KE PAAR KI ZAMEEN", DW / 2, 600, at(kw(10, "India")) * gout, col="#0F1B2D", bg=Y, size=32)
    if act("english"):
        headline(c, "SAFAR EK NAAM KA", kin("english", 0.4, 0.75), col=Y)
        chain = [("SINDHU", 0, us(11) + 0.6), ("HINDU", 1, us(11) + 0.75), ("INDOS", 2, us(11) + 0.9),
                 ("INDIA (LATIN)", 3, max(kw(11, "Latin") - 0.1, us(11) + 1.05)), ("INDIA (ENGLISH)", 4, max(kw(11, "English") - 0.1, us(11) + 1.3))]
        pos = [(205, 400), (540, 400), (875, 400), (330, 510), (750, 510)]
        for j, (s_, i_, t0) in enumerate(chain):
            kk = at(t0, 0.35) * out("english")
            if j and kk > 0:
                (xa, ya), (xb, yb) = pos[j - 1], pos[j]
                if ya == yb: route(c, [(xa + 120, ya), (xb - 120, yb)], ease_out(kk), col=Y, w=4, dash=False)
            chip(c, s_, *pos[j], kk, bg=Y if j >= 3 else "#22304A", fg="#0F1B2D" if j >= 3 else "#F1FAEE", size=34 if j < 3 else 32)
        highlight_country(c, cam, "ITA", at(kw(11, "Latin") - 0.15, 0.35) * (1 - seg(t, kw(11, "English") - 0.1, kw(11, "English") + 0.2)), t)
        highlight_country(c, cam, "GBR", at(kw(11, "English") - 0.15, 0.35) * out("english"), t)
        label(c, "ROME (LATIN)", S("rome")[0] + 40, S("rome")[1] + 80, at(kw(11, "Latin")) * out("english"))
        label(c, "ENGLAND, 9vi SADI", S("england")[0] - 10, S("england")[1] - 135, at(kw(11, "English")) * out("english"))
    if act("hindustan"):
        headline(c, "HINDU + STAN", kin("hindustan"), col="#FF6B75", sub="Shapur I ka shilalekh, c. 262 CE")
        a_ = 255 * kin("hindustan", 0.5, 0.2) * out("hindustan")
        sk_ = seg(t, kw(12, "stan") - 0.1, kw(12, "stan") + 0.4)
        L = [Lw(ch) for ch in "HINDU"] + [Lw(ch, Y, w=ease_out(sk_), al=sk_) for ch in "STAN"]
        word_row(c, L, DW / 2, 480, 112, a_, glow="#FF6B75" if t < us(13) else Y)
        chip(c, "STAN = ZAMEEN", DW / 2, 600, at(kw(12, "zameen") - 0.1) * out("hindustan"), bg=Y, fg="#0F1B2D")
        highlight_country(c, cam, "IRN", at(kw(12, "Persian") - 0.15, 0.4) * (1 - seg(t, us(13) - 0.2, us(13) + 0.2)), t, col="#FF8A92")
        highlight_country(c, cam, "IND", at(us(13) - 0.1, 0.4) * out("hindustan"), t)
        label(c, "PERSIA (SASANI DAUR)", S("iran")[0], S("iran")[1] - 60, at(kw(12, "Persian")) * out("hindustan"))
        label(c, "HINDUSTAN", S("ind")[0] + 40, S("ind")[1] - 300, at(us(13) + 0.1) * out("hindustan"), col="#0F1B2D", bg=Y, size=36)
    if act("columbus"):
        headline(c, "1492: COLUMBUS", kin("columbus", 0.5, 0.3), col=Y)
        p0, p1, p2 = S("palos"), S("canary"), S("sansal")
        rk_ = at(kw(14, "America") - 1.2, 1.6)
        route(c, [p0, p1, ((p1[0] + p2[0]) / 2, p1[1] - 40), p2], ease_out(rk_), col=Y, w=5)
        highlight_country(c, cam, "ESP", at(T("columbus")[0] + 1.0, 0.4) * (1 - seg(t, kw(14, "America"), kw(14, "America") + 0.4)), t)
        label(c, "SPAIN", p0[0] + 60, p0[1] - 95, at(T("columbus")[0] + 1.1) * out("columbus"))
        ring_highlight(c, *p2, 60, at(kw(14, "America") - 0.15, 0.4) * out("columbus"), t)
        label(c, "AMERICA (BAHAMAS)", p2[0] + 30, p2[1] + 100, at(kw(14, "America") - 0.05) * out("columbus"))
        label(c, "SOCHA: \"YE INDIA HAI!\"", DW / 2, 400, at(kw(14, "India") - 0.1) * (1 - seg(t, us(15) - 0.1, us(15) + 0.2)), col="#0F1B2D", bg=Y, size=40)
        if t > us(15) - 0.2:
            stamp(c, "INDIANS", DW / 2, 430, 74, PAL["axis"], at(kw(15, "Indians") - 0.1, 0.4))
            text(c, "Aaj: Native Americans / Indigenous peoples", DW / 2, 540, 28, "#DCE3EC", FT_SEMI, "c", int(255 * at(kw(15, "Indians") + 0.3) * out("columbus")), shadow=True)
    if act("bharat"):
        k1 = at(kw(18, "Rigveda") - 0.2, 0.5) * out("bharat", 0.25); k2 = at(kw(18, "Puranon") - 0.2, 0.5) * out("bharat", 0.25)
        if max(k1, k2) > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(150 * max(k1, k2))))
        if t < us(17) - 0.1: headline(c, "HAMARA APNA NAAM?", kin("bharat"), col=Y)
        else: headline(c, "BHARAT", at(us(17) - 0.1, 0.4), col="#FF9933", size=120)
        k1 = at(kw(18, "Rigveda") - 0.2, 0.5) * out("bharat", 0.25); k2 = at(kw(18, "Puranon") - 0.2, 0.5) * out("bharat", 0.25)
        manuscript_card(c, SCRIPT["rigveda"], k1, t, 290, 690, 440, -3, "RIGVEDA", "BHARATA KABILA",
                        "Rigveda pandulipi, 19vi sadi (public domain)")
        manuscript_card(c, SCRIPT["purana"], k2, t, 790, 760, 440, 3, "PURAN", "BHARATAVARSHA",
                        "Bhagavata Purana, 18vi sadi, LACMA (public domain)")
    if act("article"):
        k_ = kin("article", 0.5) * out("article", 0.25)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(170 * k_)))
        headline(c, "SAMVIDHAN, ARTICLE 1", k_, col=Y)
        article_card(c, k_, t)
    if act("cta", 0, 1):
        k = kin("cta", 0.6)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(205 * k)))
        if t < us(21) - 0.1:
            headline(c, "EK NADI, TEEN NAAM", k, y=230)
            r1 = at(us(20) + 0.1, 0.4); r2 = at(kw(20, "mitti") - 0.15, 0.4)
            chip(c, "SINDHU NADI  >  INDIA, HINDUSTAN", DW / 2, 560, r1, bg="#1E4F7A", size=40)
            chip(c, "APNI MITTI  >  BHARAT", DW / 2, 720, r2, bg="#C46A12", size=44)
        else:
            headline(c, "AAPKO KAUNSA PASAND?", at(us(21) - 0.1, 0.4), y=230)
            poll(c, seg(t, us(21) - 0.1, us(21) + 1.2), t)
            label(c, "COMMENT KARO", DW / 2, 1040, at(kw(22, "Comment") - 0.1, 0.5), col="#FFFFFF", bg=PAL["axis"], size=44)
            subscribe_btn(c, at(kw(22, "subscribe") - 0.4, 0.5), t, kw(22, "subscribe"))

    if era_now and not act("article"):
        ek_ = era_now; s_ = ERA_LABEL[ek_] + " (andaazan)"; w_ = text_w(s_, 22, FT_SEMI)
        x0_ = DW / 2 - (w_ + 50) / 2
        rrect(c, x0_, 1432, x0_ + w_ + 50, 1470, 19, "#3A2410", 215); c.drawCircle(x0_ + 20, 1451, 7, paint("#FF9933"))
        text(c, s_, x0_ + 36, 1459, 22, "#FFE7C2", FT_SEMI, "l", 255)
    # symbol notes (never call them real flags)
    if p_a > 60 and t > kw(4, "Persia") + 0.6: flag_note(c, "PERSIA", p_a / 255)
    if g_a > 60 and t > kw(8, "Greek") + 0.5: flag_note(c, "GREEK", g_a / 255)
    # rulers: big card on the name, then a badge for the rest of the scene
    r0 = kw(4, "raja") - 0.1
    if r0 <= t < T("darius")[1]:
        ruler(c, "darius", at(r0, 0.4) * out("darius"), seg(t, kw(4, "Sindhu") - 0.05, kw(4, "Sindhu") + 0.4), "#FF6B75", t, bxy=(150, 860))
    r1 = us(14) + 0.15
    if r1 <= t < T("columbus")[1]:
        ruler(c, "columbus", at(r1, 0.4) * out("columbus"), seg(t, kw(14, "America") + 0.2, kw(14, "America") + 0.65), Y, t, bxy=(900, 880))

    if 0.6 < t < cta0 and not act("article") and not act("notrel"):
        timeline(c, yr, seg(t, 0.6, 1.2))
    for a, b, cap in CAPS:
        if a - 0.05 <= t < b + 0.12: caption(c, cap, seg(t, a - 0.05, a + 0.08)); break
    if 2.0 < t < cta0 and not act("article") and not act("notrel"):
        text(c, "Approx. historical borders: historical-basemaps (A. Ourednik)", DW / 2, 1505, 19, PAL["muted"], FT_SEMI, "c", 210)
        text(c, "Natural Earth; India boundary as per Survey of India", DW / 2, 1532, 19, PAL["muted"], FT_SEMI, "c", 210)
    draw_img(c, LOGO, DW - 150, 40, DW - 40, 150, 200)
    grain(c, t, 8); vignette(c, 120)

if __name__ == "__main__":
    if sys.argv[1] == "still":
        od = sys.argv[2]; os.makedirs(od, exist_ok=True)
        for ts in sys.argv[3:]:
            render_still(float(ts), f"{od}/s_{float(ts):06.2f}.png"); print("ok", ts)

def sfx_events():
    """(name, time, gain_db) keyed to the same word times as the visuals"""
    E = [("whoosh_long", 0.15, -14), ("pop", kw(0, "naam"), -12), ("ding", kw(1, "nadi") - 0.1, -15)]
    for k_ in ("river", "darius", "shift", "hindush", "notrel", "greek", "english", "hindustan", "columbus", "bharat", "article", "cta"):
        E.append(("whoosh_fast", T(k_)[0], -19))
    E += [("drag", kw(3, "Tibet") - 0.3, -18)]
    for w in ("Tibet", "Ladakh", "Pakistan", "Arabian"): E.append(("pop", kw(3, w) - 0.1, -16))
    E += [("riser", T("darius")[0] + 0.1, -16), ("pop", kw(4, "Persia") - 0.1, -15), ("pop", kw(4, "raja") - 0.1, -13),
          ("whoosh_fast", kw(4, "Sindhu") - 0.2, -19), ("stamp", kw(4, "jeeta") - 0.1, -15),
          ("glitch", kw(5, " H ") - 0.05, -14), ("pop", kw(6, "Hindu") - 0.1, -15), ("ding", kw(6, "Hindush") - 0.1, -15),
          ("pop", kw(7, "jagah") - 0.1, -15), ("pop", kw(7, "dharm") - 0.1, -15),
          ("pop", kw(8, "Greek") - 0.1, -14), ("drag", kw(9, " H ") - 0.05, -14), ("pop", kw(10, "Indos") - 0.1, -15),
          ("ding", kw(10, "India") - 0.1, -13), ("pop", us(11), -17), ("pop", kw(11, "Latin") - 0.1, -16), ("pop", kw(11, "English") - 0.1, -16),
          ("pop", kw(12, "stan") - 0.1, -14), ("ding", us(13) - 0.1, -14), ("whoosh_long", T("columbus")[0] + 0.1, -14),
          ("pop", us(14) + 0.15, -13), ("pop", kw(14, "America") - 0.1, -15), ("pop", kw(14, "India") - 0.1, -15),
          ("stamp", kw(15, "Indians") - 0.1, -11), ("riser", T("bharat")[0], -16), ("boom", us(17) - 0.1, -12),
          ("pop", kw(18, "Rigveda") - 0.1, -15), ("pop", kw(18, "Puranon") - 0.2, -15), ("drag", kw(19, "India") - 0.1, -17),
          ("pop", us(20) + 0.1, -15), ("pop", kw(20, "mitti") - 0.15, -14), ("pop", us(21) - 0.1, -15), ("pop", us(21) + 0.1, -17),
          ("pop", us(21) + 0.3, -17), ("pop", kw(22, "Comment") - 0.1, -14), ("ding", kw(22, "subscribe") + 0.35, -12)]
    return sorted(E, key=lambda e: e[1])
