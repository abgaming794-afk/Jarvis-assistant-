"""AMRIT BORII Short - 'Indian Ocean ka naam India pe kyun?'  9:16, design 1080x1920 drawn x2 into 2160x3840.
Built from _head.py + _helpers_block.py + _tail.py (cat > short_storyboard.py).
Timing comes from voice/full_units.json (aligned VO). CLI:  python3 short_storyboard.py still OUTDIR t1 t2 ...
"""
import os, sys, json, math, re
os.environ.setdefault("AB_PROJECT", "ocean-naam"); os.environ.setdefault("AB_ORIENT", "vertical")
from core import *
from core import _poly_path
from widgets import *
from shapely.geometry import shape, Polygon
from PIL import Image

ROOT = PROJ
HERE = os.path.dirname(os.path.abspath(__file__))
EMP, EMP_PATH = {}, {}
COL = dict(NOW="#FF9933", RIVER="#4FC3F7", MAURYA="#C9A24A", SEA="#7FDBFF", RED="#FF6B6B", CHINA="#FF8A65", EURO="#8FB8FF")
# South-Asian polities per era (historical-basemaps, approximate) - drawn in bhagwa shades in the historical scenes
ERAS = {k: [(f["name"], shape(f["geom"])) for f in v] for k, v in json.load(open(os.path.join(HERE, "eras2.geojson.json"))).items()}
ERA_PATH = {k: [(n, _poly_path(g, 0)) for n, g in v] for k, v in ERAS.items()}
ERA_LABEL = {"CE100": "c. 100 CE ka naksha", "CE1400": "c. 1400 ka naksha", "CE1500": "c. 1500 ka naksha"}
BHAGWA = ["#FF9933", "#F28A22", "#FFB054", "#E67A16", "#FFA347", "#F59B3A"]
# rough Indian Ocean outline (land is drawn over it, so it may overlap coasts); used for the ocean glow
IO_POLY = Polygon([(32.3, 30.2), (35.5, 27), (43.5, 13.5), (48, 30.5), (57, 27.5), (62, 25.5), (67, 25), (72, 23), (77, 26),
                   (90, 24.5), (94.5, 19), (98.5, 15), (99, 6), (101.5, 2.5), (104.5, -4), (106, -7), (115, -9), (124, -10),
                   (129, -12), (131, -20), (138, -34), (146.9, -39), (146.9, -60), (20, -60), (20, -34.8), (27, -30),
                   (36, -10), (41, 2), (38, 15)])
IO_PATH = _poly_path(IO_POLY, 0)
# real ocean shapes (Natural Earth marine polygons, merged) + Europe outline: lit up on their words
OCEANS = {k: shape(v) for k, v in json.load(open(os.path.join(HERE, "oceans.geojson.json"))).items()}
OC_PATH = {k: _poly_path(g, 0) for k, g in OCEANS.items()}

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
SCENES = [("hook", 0), ("size", 3), ("others", 4), ("never", 9), ("sanskrit", 10), ("greek", 11), ("china", 12), ("europe", 13),
          ("latin", 14), ("why", 16), ("hindi", 19), ("cta", 20)]
TAIL = 1.9
T_TOTAL = round(VO_DUR + TAIL, 2)
SC_T = {}
for n_, (k_, u_) in enumerate(SCENES):
    a_ = 0.0 if n_ == 0 else us(u_) - 0.12
    b_ = (us(SCENES[n_ + 1][1]) - 0.12) if n_ + 1 < len(SCENES) else T_TOTAL
    SC_T[k_] = (a_, b_)
def T(k): return SC_T[k]

# phrase captions straight from the VO text (<= ~4 words, split at commas), keywords in yellow
CAP_KEYS = {"indian", "ocean", "india", "mahasagar", "paanch", "ek", "desh", "teesra", "7", "crore", "atlantic", "atlas", "pacific",
            "shaant", "arctic", "bhaalu", "southern", "dakshin", "hamesha", "sanskrit", "ratnakara", "ratnon", "2000", "greek",
            "periplus", "erythraean", "laal", "samudra", "1400", "china", "zheng", "he", "western", "paschim", "europe", "eastern",
            "poorab", "1515", "latin", "oceanus", "orientalis", "indicus", "poorbi", "teer", "beech", "hindi", "hind", "comment", "subscribe"}
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

LOGO = None
DOCS = {}
RULER = {}
RULER_INFO = {"zhenghe": ("ZHENG HE KE JAHAZ", "Wubei Zhi woodblock, 17vi sadi (maana jaata hai)",
                          "Wubei Zhi woodblock print - public domain (Wikimedia Commons)", (0.0, 0.0, 1.0, 1.0))}
CARY_CROP = (0.1, 0.5, 0.85, 0.98)   # set after looking at the map: region around the 'SOUTHERN OCEAN' label
def load():
    global LOGO
    if LOGO is None:
        LOGO = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_800.png").resize((200, 200)))
        for k_, f_, crop in (("periplus", "periplus_map.jpg", None), ("atlas", "atlas.jpg", (0.08, 0.0, 0.92, 0.47)),
                             ("pacifici", "maris_pacifici.jpg", None), ("ursa", "ursa_major.jpg", None),
                             ("cary", "cary1806.jpg", CARY_CROP), ("ramayana", "ramayana_lanka.jpg", None)):
            try:
                im = Image.open(ROOT + "visuals/photos/" + f_).convert("RGB")
                if crop: im = im.crop((int(crop[0] * im.width), int(crop[1] * im.height), int(crop[2] * im.width), int(crop[3] * im.height)))
                DOCS[k_] = sk_image(im)
            except Exception: DOCS[k_] = None
        try: RULER["zhenghe"] = sk_image(Image.open(ROOT + "visuals/photos/zhenghe_ships.gif").convert("RGB"))
        except Exception: RULER["zhenghe"] = None

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


# ================================================================ Indian Ocean Short: camera, scenes, frame, sfx
Y = PAL["yel"]
OC_GLOW = {"ATL": [(-35, 25, 38), (-15, -20, 30)], "PAC": [(-140, 5, 55), (165, 15, 32)], "ARC": [(0, 84, 40), (-150, 78, 30), (120, 80, 30)],
           "SOU": [(0, -66, 60), (120, -64, 60), (-120, -66, 60)], "IND": [(76, -12, 45), (62, 14, 15), (88, 12, 12)]}
PAC_HL = ()   # highlight boxes on the Maris Pacifici map (fractions), set after viewing
CARY_HL = ()

def base_map2(c, cam, t, india_a=200, border_a=1.0, glows=(), ocs=()):
    """ocean background, soft ocean glows + named-ocean highlights (under the land), then the land with India filled"""
    c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"]))
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    for key, col, a in ocs:
        if a <= 0: continue
        pul = 0.8 + 0.2 * math.sin(t * 5)
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
        c.drawPath(OC_PATH[key], paint(col, int(a * 0.5 * pul), blur=max(6, 18 / s)))
        c.clipPath(OC_PATH[key], doAntiAlias=True)
        for lo, la, R in OC_GLOW[key]:
            gx, gy = cam_xy(lo, la)
            sh = skia.GradientShader.MakeRadial(skia.Point(gx, gy), R, [hexc(col, int(min(255, a * 0.85 * pul))), hexc(col, int(a * 0.4)), hexc(col, 0)], [0.0, 0.55, 1.0])
            gp = skia.Paint(); gp.setShader(sh); c.drawCircle(gx, gy, R, gp)
        c.restore()
    for col, a in glows:
        if a <= 0: continue
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
        c.clipPath(IO_PATH, doAntiAlias=True)
        ox, oy = cam_xy(76, -12); pul = 0.85 + 0.15 * math.sin(t * 3)
        sh = skia.GradientShader.MakeRadial(skia.Point(ox, oy), 75, [hexc(col, int(a * 0.42 * pul)), hexc(col, int(a * 0.16)), hexc(col, 0)], [0.0, 0.6, 1.0])
        gp = skia.Paint(); gp.setShader(sh); c.drawPaint(gp)
        c.drawPath(IO_PATH, paint(col, int(a * 0.5), stroke=10 / s, blur=12 / s))
        c.restore()
    c.save(); c.translate(0, MAP_CY - DH / 2)
    draw_map(c, WM, cam, fills={"IND": (COL["NOW"], int(india_a))}, border_a=border_a)
    c.restore()

def region_hl(c, cam, key, k, t, col):
    """glowing highlight of a land region (e.g. Europe) drawn over the map"""
    if k <= 0: return
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]; pul = 0.8 + 0.2 * math.sin(t * 5)
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
    c.drawPath(OC_PATH[key], paint(col, int(110 * k * pul)))
    c.drawPath(OC_PATH[key], paint(col, int(200 * k), stroke=6 / s, blur=4 / s))
    c.drawPath(OC_PATH[key], paint("#FFFFFF", int(230 * k), stroke=1.4 / s))
    c.restore()

def card(c, img, k, t, cx, cy, w, cap, sub, credit, ang=0, hls=()):
    """real document/photo in the gold frame (halo, motes, slow push-in); caption text auto-fits the card width"""
    if k <= 0 or img is None: return
    al = int(255 * clamp(k * 2)); kk = back(clamp(k), 1.4)
    h = w * img.height() / img.width()
    halo = skia.GradientShader.MakeRadial(skia.Point(cx, cy), w * 0.9, [skia.ColorSetARGB(int(140 * clamp(k)), 255, 190, 90), skia.ColorSetARGB(0, 255, 160, 60)])
    hp = skia.Paint(); hp.setShader(halo); c.drawCircle(cx, cy, w * 0.9, hp)
    for i in range(8):
        a_ = i * 2.4 + t * 0.6; r_ = w * (0.55 + 0.08 * math.sin(i * 1.7 + t))
        c.drawCircle(cx + math.cos(a_) * r_, cy + math.sin(a_) * r_ * 0.8, 3 + (i % 3), paint("#FFE2A8", int(150 * clamp(k) * (0.5 + 0.5 * math.sin(t * 3 + i))), blur=2))
    c.save(); c.translate(cx, cy); c.rotate(ang * kk); c.scale(kk, kk); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    rrect(c, l - 16, tp - 16, l + w + 16, tp + h + 92, 16, "#FBF3DF", al, shadow=30)
    c.drawRoundRect(skia.Rect(l - 9, tp - 9, l + w + 9, tp + h + 85), 11, 11, paint("#C9A24A", al, stroke=3))
    c.save(); c.clipRect(skia.Rect(l, tp, l + w, tp + h))
    z = 1.0 + 0.05 * clamp((t % 8) / 4)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al); c.restore()
    c.drawRect(skia.Rect(l, tp, l + w, tp + h), paint("#B8862B", al, stroke=3))
    for fx0, fy0, fx1, fy1, hk in hls:
        if hk <= 0: continue
        x0, y0, x1, y1 = l + fx0 * w, tp + fy0 * h, l + fx1 * w, tp + fy1 * h
        c.drawRoundRect(skia.Rect(x0 - 6, y0 - 5, x0 - 6 + (x1 - x0 + 12) * ease_out(hk), y1 + 5), 9, 9, paint("#FF4D5E", al, stroke=4))
    fit = lambda s_, size: min(size, size * (w + 10) / max(1, text_w(s_, size, FT_BLACK)))
    text(c, cap, cx, tp + h + 44, fit(cap, 34), "#7A1E0E", FT_BLACK, "c", al)
    text(c, sub, cx, tp + h + 76, fit(sub, 23), "#B5651D", FT_BLACK, "c", al)
    c.restore()
    text(c, credit, cx, tp + h + 122, min(17, 17 * (w + 160) / max(1, text_w(credit, 17, FT_SEMI))), "#DCE3EC", FT_SEMI, "c", int(al * 0.9), shadow=True)

def note(c, s_, k, y0=1086):
    """small dark pill with a yellow dot (e.g. 'raasta andaazan')"""
    if k <= 0: return
    size = 22; w = text_w(s_, size, FT_SEMI); al = int(255 * clamp(k * 2))
    x0 = DW / 2 - (w + 50) / 2
    rrect(c, x0, y0, x0 + w + 50, y0 + 38, 19, "#0F1B2D", int(al * 0.85)); c.drawCircle(x0 + 20, y0 + 19, 6, paint(Y, al))
    text(c, s_, x0 + 36, y0 + 27, size, "#DCE3EC", FT_SEMI, "l", al)

def strike_chip(c, s_, x, y, k, sk, size=44):
    """chip with a red line drawn across it (sk 0..1)"""
    chip(c, s_, x, y, k, bg="#22304A", size=size)
    if sk > 0 and k > 0:
        w = text_w(s_, size) + 40
        c.drawLine(x - w / 2, y + 6, x - w / 2 + w * ease_out(sk), y - 18, paint("#FF4D5E", int(255 * clamp(k)), stroke=9, cap_round=True))

def gem(c, x, y, r, a, col="#FFE08A"):
    if a <= 0: return
    p_ = skia.Path(); p_.moveTo(x, y - r); p_.lineTo(x + r * 0.32, y - r * 0.32); p_.lineTo(x + r, y); p_.lineTo(x + r * 0.32, y + r * 0.32)
    p_.lineTo(x, y + r); p_.lineTo(x - r * 0.32, y + r * 0.32); p_.lineTo(x - r, y); p_.lineTo(x - r * 0.32, y - r * 0.32); p_.close()
    c.drawCircle(x, y, r * 0.9, paint(col, int(a * 0.35), blur=r * 0.5)); c.drawPath(p_, paint("#FFFFFF", int(a)))

GEMS = [(62, 8), (66, 18), (70, 2), (84, 4), (88, 12), (91, 6), (73, -6), (80, -10), (60, -2), (95, -4), (68, -14), (86, -16), (76, 0), (57, 14)]

def doc_card(c, img, k, t, cx, cy, w, cap, sub, credit, hls=()):
    """real document/map in the gold manuscript frame (straight), with yellow highlighter boxes on parts of the image.
    hls: (fx0, fy0, fx1, fy1, k) as fractions of the image"""
    if k <= 0 or img is None: return
    manuscript_card(c, img, k, t, cx, cy, w, 0, cap, sub, credit)
    kk = back(clamp(k), 1.4); h = w * img.height() / img.width(); al = clamp(k * 2)
    l, tp = cx - w / 2, cy - h / 2
    c.save(); c.translate(cx, cy); c.scale(kk, kk); c.translate(-cx, -cy)
    for fx0, fy0, fx1, fy1, hk in hls:
        if hk <= 0: continue
        x0, y0, x1, y1 = l + fx0 * w, tp + fy0 * h, l + fx1 * w, tp + fy1 * h
        hp = paint("#FFD166", int(200 * al)); hp.setBlendMode(skia.BlendMode.kMultiply)
        c.drawRect(skia.Rect(x0, y0, x0 + (x1 - x0) * ease_out(hk), y1), hp)
        c.drawRoundRect(skia.Rect(x0 - 8, y0 - 6, x0 - 8 + (x1 - x0 + 16) * ease_out(hk), y1 + 6), 10, 10, paint("#FF4D5E", int(230 * al), stroke=4))
    c.restore()

def typed_card(c, lines, k_type, a, y0):
    """dark card where lines type in (k_type 0..1 over all characters); lines: (text, size, col)"""
    if a <= 0: return
    tot = sum(len(s_) for s_, _, _ in lines); n = int(round(tot * clamp(k_type)))
    hgt = sum(sz * 1.25 for _, sz, _ in lines) + 50
    wmax = max(text_w(s_, sz) for s_, sz, _ in lines) + 80
    rrect(c, DW / 2 - wmax / 2, y0, DW / 2 + wmax / 2, y0 + hgt, 24, "#0B1424", int(a * 0.85), shadow=20)
    c.drawRoundRect(skia.Rect(DW / 2 - wmax / 2, y0, DW / 2 + wmax / 2, y0 + hgt), 24, 24, paint(Y, int(a * 0.8), stroke=3))
    yy = y0 + 25
    for s_, sz, col in lines:
        yy += sz * 1.1
        m = max(0, min(len(s_), n)); n -= len(s_)
        if m > 0: text(c, s_[:m], DW / 2 - text_w(s_, sz) / 2, yy, sz, col, FT_BLACK, "l", int(a), shadow=True)
        if 0 < m < len(s_) and int(t_now() * 4) % 2 == 0:
            xx = DW / 2 - text_w(s_, sz) / 2 + text_w(s_[:m], sz) + 4
            c.drawRect(skia.Rect(xx, yy - sz * 0.75, xx + 5, yy + 4), paint(Y, int(a)))
        yy += sz * 0.15
_TNOW = [0.0]
def t_now(): return _TNOW[0]

def poll2(c, items, t):
    """items: (label, colour, t_on)"""
    for i, (s_, col, t0) in enumerate(items):
        kk = ease_out(seg(t, t0, t0 + 0.45))
        if kk <= 0: continue
        y = 520 + i * 150; al = int(255 * clamp(kk * 2)); x0 = 140 + (1 - kk) * 200
        rrect(c, x0, y - 55, 940, y + 55, 55, "#18253A", al, shadow=14)
        c.drawCircle(x0 + 58, y, 36, paint(col, al)); text(c, "ABC"[i], x0 + 58, y + 14, 40, "#FFFFFF", FT_BLACK, "c", al)
        size = min(54, 54 * (940 - x0 - 150) / max(1, text_w(s_, 54)))
        text(c, s_, x0 + 120, y + 19, size, "#F1FAEE", FT_BLACK, "l", al)

# ---------------------------------------------------------------- camera keys (lon, lat, px/deg)
WORLD = (10, 12, 2.75); IO = (80, -6, 8.5); SAN = (78, 8, 11); GRK = (56, 17, 12.5); CHN = (90, 14, 7.2)
EUR = (60, 22, 3.6); LAT = (78, -2, 7.5); WHY = (80, 13, 15)
CAM_KEYS = [(0.0, (10, 12, 2.3)), (2.0, WORLD), (kw(2, "Indian") - 0.1, WORLD), (kw(2, "Indian") + 1.2, IO),
            (T("others")[0], IO), (T("others")[0] + 1.0, WORLD), (T("never")[0] + 0.3, WORLD), (T("never")[0] + 1.4, IO),
            (T("sanskrit")[0], IO), (T("sanskrit")[0] + 1.0, SAN), (T("greek")[0], SAN), (T("greek")[0] + 1.1, GRK),
            (T("china")[0], GRK), (T("china")[0] + 1.2, CHN), (T("europe")[0], CHN), (T("europe")[0] + 1.0, EUR),
            (T("latin")[0], EUR), (T("latin")[0] + 1.1, LAT), (T("why")[0], LAT), (T("why")[0] + 1.1, WHY),
            (T("hindi")[0], WHY), (T("hindi")[0] + 1.0, IO)]
def cam_at(t):
    for (t0, a), (t1, b) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_io(seg(t, t0, t1))
            s = math.exp(lerp(math.log(a[2]), math.log(b[2]), k))
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k), s)
    return CAM_KEYS[-1][1] if t > CAM_KEYS[-1][0] else CAM_KEYS[0][1]

PL = dict(io=(74, -20), atl=(-32, 18), pac=(-136, 2), arc=(2, 79), sou=(62, -63), ind=(79, 22.5), arabsea=(64, 14), bob=(88.5, 14),
          kanya=(77.5, 8.1), io_lbl=(78, -4), area=(76, -30),
          berenice=(35.5, 23.9), aden=(45, 12.6), muziris=(76.2, 10.2), barygaza=(72.9, 21.7), egypt=(31, 27),
          suzhou=(120.6, 31.3), champa=(109.2, 13.8), malacca=(102.25, 2.2), calicut=(75.8, 11.25), hormuz=(56.3, 26.6),
          europe=(10, 49))

# ---------------------------------------------------------------- timeline
TL = [(-400, "PRACHIN"), (60, "1st SADI"), (1410, "1405-33"), (1515, "1515"), (2026, "AAJ")]
def timeline(c, year, k):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); x0, x1, y = 110, 970, 1220
    def X(yr):
        pts = [(-600, 110), (0, 280), (1300, 420), (1450, 560), (1550, 700), (2026, 970)]
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= yr <= b: return lerp(xa, xb, (yr - a) / (b - a))
        return x0 if yr < -600 else x1
    c.drawRoundRect(skia.Rect(x0, y - 4, x1, y + 4), 4, 4, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 4, X(year), y + 4), 4, 4, paint(Y, al))
    for yr, lab in TL:
        on = abs(yr - year) < 30
        c.drawCircle(X(yr), y, 12 if on else 8, paint(Y if X(yr) <= X(year) + 1 else "#3E5068", al))
        text(c, lab, X(yr), y + 52, 28 if on else 22, "#F1FAEE" if on else PAL["muted"], FT_BLACK if on else FT_SEMI, "c", al)
    lab = "PRACHIN KAAL" if year < -300 else ("c. 1st SADI CE" if year < 300 else f"{int(year)}")
    pill(c, lab, X(year), y - 50, 34, Y, fg="#0F1B2D", a=al)

def year_at(t):
    n0, g0, c0, e0, l0, w0 = T("never")[0], T("greek")[0], T("china")[0], T("europe")[0], T("latin")[0], T("why")[0]
    keys = [(0, 2026), (n0 + 0.3, 2026), (n0 + 1.5, -400), (g0, -400), (g0 + 1.0, 60), (c0, 60), (c0 + 1.0, 1410), (e0, 1410),
            (e0 + 0.8, 1480), (l0, 1480), (l0 + 0.8, 1515), (w0, 1515), (w0 + 1.0, 2026)]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp(a, b, ease_io(seg(t, t0, t1)))
    return 2026

def pop_words(c, t, s_, t0, y, size, col, a_):
    ws = s_.split(" "); tw = sum(text_w(w_, size) for w_ in ws) + text_w(" ", size) * (len(ws) - 1); x = DW / 2 - tw / 2
    for i, w_ in enumerate(ws):
        p = seg(t, t0 + i * 0.11, t0 + i * 0.11 + 0.35); ww = text_w(w_, size)
        if p > 0:
            e = back(p, 2.0) if p < 1 else 1.0
            c.save(); c.translate(x + ww / 2, y + (1 - e) * 30); c.scale(0.7 + 0.3 * e, 0.7 + 0.3 * e)
            text(c, w_, 0, 0, size, col, FT_BLACK, "c", int(255 * clamp(p * 2) * a_), shadow=True); c.restore()
        x += ww + text_w(" ", size)

def teer(c, cam, k, t, a=255):
    """arrow tracing India from the north down the peninsula into the ocean"""
    if k <= 0: return
    pts = [scr(cam, *q) for q in [(76.5, 31), (78, 24), (78.2, 16), (77.5, 8.4), (77.4, 1.5)]]
    route(c, pts, ease_out(k), col="#FFFFFF", w=16, dash=False, a=int(a * 0.35), head=False)
    route(c, pts, ease_out(k), col=Y, w=8, dash=False, a=a, head=True)

# ---------------------------------------------------------------- frame
WM = None
def frame(c, t):
    global WM
    load(); _TNOW[0] = t
    if WM is None: WM = WorldMap()
    cam = cam_at(t)
    def S(k): return scr(cam, *PL[k])
    def act(k, pad_in=0.0, pad_out=0.0):
        a, b = T(k); return a - pad_in <= t < b + pad_out
    def kin(k, d=0.5, off=0.0): return seg(t, T(k)[0] + off, T(k)[0] + off + d)
    def at(t0, d=0.45): return seg(t, t0, t0 + d)
    def out(k, d=0.3): return 1 - seg(t, T(k)[1] - d, T(k)[1])

    yr = year_at(t)
    cta0 = T("cta")[0]; s0 = T("sanskrit")[0]; g0 = T("greek")[0]; w0 = T("why")[0]
    # map of ITS time (user rule): tiranga India in the present-day scenes, solid bhagwa India in the Sanskrit lead-in,
    # period polities (historical-basemaps) in bhagwa shades in the historical scenes
    hist = seg(t, g0 - 0.3, g0 + 0.5) * (1 - seg(t, w0, w0 + 0.8))
    india_a = (200 + 30 * seg(t, s0, s0 + 0.8)) * (1 - hist)
    gl = []
    gl.append(("#4FC3F7", 255 * seg(t, kw(2, "Ocean") - 0.2, kw(2, "Ocean") + 0.6) * (1 - seg(t, T("others")[0], T("others")[0] + 0.6))))
    gl.append(("#FFD166", 200 * seg(t, kw(10, "Ratnakara") - 0.2, kw(10, "Ratnakara") + 0.6) * (1 - seg(t, g0 - 0.2, g0 + 0.4))))
    gl.append(("#FF4D5E", 190 * seg(t, kw(11, "Laal") - 0.3, kw(11, "Laal") + 0.5) * (1 - seg(t, T("china")[0] - 0.2, T("china")[0] + 0.4))))
    gl.append(("#4FC3F7", 230 * seg(t, kw(14, "Indicus") - 0.2, kw(14, "Indicus") + 0.6) * (1 - seg(t, w0, w0 + 0.5))))
    gl.append(("#4FC3F7", 255 * seg(t, kw(18, "beech") - 0.3, kw(18, "beech") + 0.5) * (1 - seg(t, cta0, cta0 + 0.6))))
    SEA = COL["SEA"]; ti0 = kw(2, "Indian") - 0.12; oe = T("others")
    ocs = []
    for i, key in enumerate(("PAC", "ATL", "IND", "ARC", "SOU")):      # hook: the five oceans light up on "paanch"
        tp_ = kw(0, "paanch") - 0.1 + i * 0.13
        ocs.append((key, SEA, 230 * at(tp_, 0.35) * (1 - seg(t, ti0 - 0.3, ti0))))
    ocs.append(("IND", "#FFD166", 255 * at(ti0, 0.4) * (1 - seg(t, T("size")[1] - 0.3, T("size")[1]))))
    for key, u_, w1 in (("ATL", 5, "Atlantic"), ("PAC", 6, "Pacific"), ("ARC", 7, "Arctic"), ("SOU", 8, "Southern")):
        ocs.append((key, SEA, 255 * at(kw(u_, w1) - 0.15, 0.35) * (1 - 0.45 * seg(t, ue(u_), ue(u_) + 0.3)) * (1 - seg(t, oe[1] - 0.1, oe[1] + 0.3))))
    ocs.append(("IND", "#FF9933", 255 * at(kw(8, "dakshin") + 0.1, 0.35) * (1 - seg(t, T("never")[0] + 0.6, T("never")[0] + 1.0))))
    ocs.append(("IND", COL["CHINA"], 240 * at(kw(12, "Western") - 0.15, 0.35) * (1 - seg(t, T("china")[1] - 0.2, T("china")[1] + 0.2))))
    ocs.append(("IND", COL["EURO"], 240 * at(kw(13, "Eastern") - 0.15, 0.35) * (1 - seg(t, T("europe")[1] - 0.2, T("europe")[1] + 0.2))))
    ocs.append(("IND", "#FF9933", 240 * at(kw(19, "Hind M") - 0.15, 0.35) * (1 - seg(t, T("hindi")[1] - 0.2, T("hindi")[1] + 0.3))))
    base_map2(c, cam, t, india_a, border_a=1 - 0.75 * hist, glows=gl, ocs=ocs)
    now_a = 255 * (1 - seg(t, s0, s0 + 0.8)) + 255 * seg(t, w0, w0 + 0.8)
    if now_a > 0:
        if "NOW" not in EMP_PATH: EMP_PATH["NOW"] = _poly_path(WM.geoms["IND"], 0.01)
        cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
        wave_flag(c, EMP_PATH["NOW"], "NOWV", t, min(255, now_a), s_); c.restore()
    c0_, e0_ = T("china")[0], T("europe")[0]
    ERA_ON = [("CE100", g0 - 0.3, c0_ + 0.3), ("CE1400", c0_, e0_ + 0.3), ("CE1500", e0_, w0 + 0.4)]
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

    # ================= hook: "OCEAN?" letter by letter, 5 oceans pulse, then "INDIAN OCEAN" with tiranga letters
    if t < T("size")[0] + 0.8:
        ho = 1 - seg(t, T("size")[0] + 0.5, T("size")[0] + 0.8)
        ti = kw(2, "Indian") - 0.12
        qd = seg(t, kw(1, "kaunsa") - 0.1, kw(1, "kaunsa") + 0.45)
        an = seg(t, ti, ti + 0.7)
        L = []
        tir = ["#FF9933", "#FF9933", "#FFFFFF", "#FFFFFF", "#3FB950", "#3FB950"]
        for i, ch in enumerate("INDIAN"):
            p = seg(t, ti + i * 0.06, ti + i * 0.06 + 0.5); e = back(p, 1.6) if p < 1 else 1.0
            L.append(dict(ch=ch, w=ease_out(p), al=clamp(p * 1.6), dy=-(1 - e) * 90, col=tir[i], sy=0.55 + 0.45 * e))
        L.append(dict(ch=" ", w=ease_out(an), al=0))
        for i, ch in enumerate("OCEAN"):
            p = seg(t, 0.12 + i * 0.1, 0.72 + i * 0.1); e = back(p, 1.6) if p < 1 else 1.0
            L.append(dict(ch=ch, al=clamp(p * 1.6), dy=(1 - e) * 90, col="#7FDBFF", sy=0.55 + 0.45 * e))
        L.append(dict(ch="?", w=ease_out(qd) * (1 - ease_out(an)), al=qd * (1 - an), dy=-(1 - back(qd, 2.2)) * 120 if qd < 1 else 0,
                      col=Y, rot=(1 - qd) * -25))
        word_row(c, L, DW / 2, 300, lerp(170, 112, ease_io(an)), 255 * ease_io(seg(t, 0.05, 0.6)) * ho, glow=Y if t < ti else "#FF9933")
        sh = seg(t, 0.95, 1.6)
        if 0 < sh < 1:
            bw = text_w("OCEAN", 170); x0 = DW / 2 - bw / 2 - 60 + (bw + 120) * ease_io(sh)
            g_ = skia.GradientShader.MakeLinear([skia.Point(x0 - 60, 0), skia.Point(x0 + 60, 0)],
                                                [skia.ColorSetARGB(0, 255, 255, 255), skia.ColorSetARGB(int(150 * ho), 255, 255, 255), skia.ColorSetARGB(0, 255, 255, 255)])
            pp = skia.Paint(); pp.setShader(g_); pp.setBlendMode(skia.BlendMode.kPlus)
            c.save(); c.skew(-0.25, 0); c.translate(75, 0); c.drawRect(skia.Rect(x0 - 60, 150, x0 + 60, 340), pp); c.restore()
        q1 = 1 - seg(t, ti - 0.3, ti)
        if q1 > 0: pop_words(c, t, "5 MAHASAGAR. SIRF 1 PE DESH KA NAAM!", kw(0, "sirf") - 0.2, 408, 44, "#F1FAEE", q1 * ho)
        if t > ti:
            pop_words(c, t, "INDIA KE NAAM PE!", ti + 0.3, 408, 60, "#FF9933", ho)
            rk = seg(t, ti + 0.3, ti + 1.2)
            if rk > 0:
                pw = skia.Path(); x0, x1 = DW / 2 - 240, DW / 2 - 240 + 480 * ease_out(rk)
                for xx in range(int(x0), int(x1), 6):
                    yy = 442 + 7 * math.sin((xx - x0) / 34 - t * 8)
                    (pw.moveTo if xx == int(x0) else pw.lineTo)(xx, yy)
                c.drawPath(pw, paint("#7FDBFF", int(230 * ho), stroke=6, cap_round=True))
                c.drawPath(pw, paint("#7FDBFF", int(110 * ho), stroke=16, blur=8, cap_round=True))
    # ================= size
    if act("size"):
        e = out("size")
        headline(c, "TEESRA SABSE BADA", kin("size", 0.5, 0.8), col="#7FDBFF", sub="duniya ke mahasagar mein #3")
        label(c, "INDIAN OCEAN", *S("io_lbl"), at(us(3)) * e, col="#0F1B2D", bg="#7FDBFF", size=38)
        label(c, "~7.06 CRORE KM²", S("area")[0], S("area")[1], at(kw(3, "7") - 0.1) * e, col="#0F1B2D", bg=Y, size=44)
        label(c, "DHARTI KA ~20% PAANI", S("area")[0], S("area")[1] + 90, at(kw(3, "kilometre") - 0.1) * e, size=32)
    # ================= others: every other ocean's name, on its word
    if act("others", 0, 0.3):
        e = 1 - seg(t, T("others")[1] - 0.1, T("others")[1] + 0.3)
        headline(c, "BAAKI NAAM KAHAN SE?", kin("others"), col=Y)
        OC = [("atl", 5, "Atlantic", "ATLANTIC", "Atlas", "ATLAS: GREEK DEVTA"), ("pac", 6, "Pacific", "PACIFIC", "shaant", "SHAANT SAMUDRA"),
              ("arc", 7, "Arctic", "ARCTIC", "Bhaalu", "BHAALU TAARE"), ("sou", 8, "Southern", "SOUTHERN", "dakshin", "DAKSHIN")]
        for key, u_, w1, nm, w2, mean in OC:
            x, y = S(key); k1 = at(kw(u_, w1) - 0.15, 0.4) * e
            label(c, nm, x, y - 30, k1, col="#0F1B2D", bg="#7FDBFF", size=30)
            label(c, mean, x, y + 30, at(kw(u_, w2) - 0.15, 0.4) * e, col="#0F1B2D", bg=Y, size=26)
        def win(t0, t1): return at(t0, 0.35) * (1 - seg(t, t1 - 0.2, t1))
        card(c, DOCS.get("atlas"), win(kw(5, "Atlas") - 0.2, kw(6, "Pacific") - 0.05), t, 790, 640, 340,
             "ATLAS - GREEK DEVTA", "Farnese Atlas murti, 2nd sadi CE (Naples)", "Photo: Gabriel Seah, CC BY-SA 3.0 (cropped)")
        card(c, DOCS.get("pacifici"), win(kw(6, "Pacific") + 0.2, kw(7, "Arctic") - 0.05), t, 740, 640, 560,
             "MARIS PACIFICI = SHAANT SAMUDRA", "Abraham Ortelius ka naksha, 1589", "Abraham Ortelius, 1589 - public domain (Wikimedia Commons)", hls=[(0.61, 0.03, 0.855, 0.08, seg(t, kw(6, "Pacific") + 0.45, kw(6, "Pacific") + 0.85)), (0.21, 0.31, 0.62, 0.375, seg(t, kw(6, "shaant") - 0.1, kw(6, "shaant") + 0.4))])
        card(c, DOCS.get("ursa"), win(kw(7, "Bhaalu") - 0.25, kw(8, "Southern") - 0.05), t, 540, 990, 520,
             "URSA MAJOR = BADA BHAALU", "Taara-card, Urania's Mirror, c. 1825", "Sidney Hall, Urania's Mirror (LoC; restoration A. Cuerden) - public domain")
        card(c, DOCS.get("cary"), win(kw(8, "Southern") + 0.1, T("never")[0] + 0.3), t, 540, 520, 560,
             "'SOUTHERN OCEAN' = DAKSHIN KA SAMUDRA", "John Cary ka naksha, 1806", "John Cary, 1806 (Geographicus) - public domain", hls=[(0.09, 0.81, 0.91, 0.94, seg(t, kw(8, "Southern") + 0.35, kw(8, "Southern") + 0.85))])
    ti_ = kw(8, "dakshin") + 0.1                      # INDIAN = the only country name; stays into the next scene
    if ti_ <= t < T("never")[0] + 1.0:
        e2 = 1 - seg(t, T("never")[0] + 0.6, T("never")[0] + 1.0)
        x, y = S("io")
        label(c, "INDIAN", x, y - 70, at(ti_, 0.4) * e2, col="#0F1B2D", bg="#FF9933", size=32)
        label(c, "= DESH: INDIA", x + (190 if cam[2] < 4 else 0), y + (0 if cam[2] < 4 else 64), at(ti_ + 0.15, 0.4) * e2, col="#0F1B2D", bg=Y, size=28)
    # ================= never
    if act("never"):
        headline(c, "HAMESHA NAHI THA!", kin("never"), col="#FF6B75", sub="naam badalte rahe")
        strike_chip(c, "INDIAN OCEAN", DW / 2, 405, at(us(9) + 0.1, 0.4) * out("never"), seg(t, kw(9, "nahi") - 0.1, kw(9, "nahi") + 0.4))
    # ================= sanskrit
    if act("sanskrit"):
        e = out("sanskrit"); tr_ = kw(10, "Ratnakara")
        chip(c, "SANSKRIT NAAM", DW / 2, 230, kin("sanskrit") * (1 - at(tr_ - 0.3, 0.3)), bg="#C46A12", size=48)
        headline(c, "RATNAKARA", at(tr_ - 0.2, 1.2) * e, col="#FFD166", size=124, sub="ratnon ki khaan")
        card(c, DOCS.get("ramayana"), at(kw(10, "Sanskrit") - 0.1, 0.4) * (1 - seg(t, T("greek")[0] + 0.3, T("greek")[0] + 0.7)), t, 540, 760, 640,
             "SANSKRIT GRANTH: RAMAYANA", "Mewar pandulipi, 1649-53 - samudra ke paar Lanka", "Sahibdin, Mewar Ramayana, British Library Add MS 15297(1) - public domain")
        ga = at(kw(10, "ratnon") - 0.4, 0.5) * e
        for i, (lo, la) in enumerate(GEMS):
            x, y = S("io") if False else scr(cam, lo, la)
            tw_ = 0.5 + 0.5 * math.sin(t * 5 + i * 1.9)
            gem(c, x, y, 12 + 8 * tw_, 255 * ga * (0.4 + 0.6 * tw_))
    # ================= greek: Periplus, Erythraean Sea
    if act("greek"):
        e = out("greek"); te_ = kw(11, "Erythraean"); tp_ = kw(11, "Periplus")
        if t < te_ - 0.2: headline(c, "GREEK VYAPARI", kin("greek", 0.5, 0.1), col="#6FA8FF", sub="lagbhag 2000 saal pehle")
        else: headline(c, "ERYTHRAEAN SEA", at(te_ - 0.2, 1.0) * e, col=COL["RED"], sub="yaani Laal Samudra")
        rk_ = at(kw(11, "vyapariyon") - 0.3, 1.2)
        p0, p1, p2, p3 = S("berenice"), S("aden"), S("muziris"), S("barygaza")
        route(c, [p0, p1, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 40), p2], ease_out(rk_), col=Y, w=5, a=int(255 * e))
        route(c, [p1, ((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2 + 20), p3], ease_out(seg(rk_, 0.4, 1)), col=Y, w=4, a=int(255 * e))
        dk = at(tp_ - 0.15, 0.5) * e
        label(c, "EGYPT", S("egypt")[0], S("egypt")[1] - 20, at(kw(11, "vyapariyon") - 0.2) * e * (1 - dk), size=28)
        label(c, "MUZIRIS (KERALA)", p2[0] + 30, p2[1] + 60, at(kw(11, "vyapariyon") + 0.6) * e * (1 - dk), size=26)
        dk = at(tp_ - 0.15, 0.5) * e
        doc_card(c, DOCS.get("periplus"), dk, t, 540, 770, 720, "PERIPLUS PAR BANA NAKSHA", "Abraham Ortelius, 1597",
                 "Abraham Ortelius, 1597 - public domain (Wikimedia Commons)",
                 hls=[(0.33, 0.465, 0.76, 0.535, seg(t, te_ - 0.05, te_ + 0.45)), (0.36, 0.545, 0.77, 0.605, seg(t, te_ + 0.35, te_ + 0.85))])
        chip(c, "ERYTHRA (GREEK) = LAAL", DW / 2, 405, at(kw(11, "Laal") - 0.15, 0.4) * e, bg=COL["RED"], fg="#0F1B2D", size=34)
    # ================= china: Zheng He, Western Ocean
    if act("china", 0, 0.2):
        e = 1 - seg(t, T("china")[1] - 0.1, T("china")[1] + 0.2)
        headline(c, "ZHENG HE, 1405-1433", kin("china", 0.5, 0.2), col=COL["CHINA"], sub="China ke admiral ki yatraen")
        pts = [S(k_) for k_ in ("suzhou", "champa", "malacca", "calicut", "hormuz")]
        route(c, pts, ease_out(seg(t, kw(12, "China") - 0.2, kw(12, "Western") - 0.1)), col=COL["CHINA"], w=5, a=int(255 * e))
        spot = at(kw(12, "China") - 0.15, 0.4) * e
        ring_highlight(c, *S("suzhou"), 34, spot, t, col=COL["CHINA"])
        label(c, "MING CHINA", S("suzhou")[0] - 40, S("suzhou")[1] - 62, spot, size=28)
        label(c, "CALICUT", S("calicut")[0] - 120, S("calicut")[1] - 10, at(kw(12, "Zheng") + 0.3) * e, size=26)
        tw_ = kw(12, "Western")
        a0, a1 = scr(cam, 98, 1), scr(cam, 60, 1)
        route(c, [a0, ((a0[0] + a1[0]) / 2, a0[1] - 30), a1], ease_out(at(tw_ - 0.15, 0.6)), col=Y, w=12, dash=False, a=int(255 * e))
        label(c, "WESTERN OCEAN", (a0[0] + a1[0]) / 2, a0[1] + 62, at(tw_ - 0.05) * e, col="#0F1B2D", bg=Y, size=36)
        label(c, "= PASCHIM KA SAMUDRA", (a0[0] + a1[0]) / 2, a0[1] + 125, at(kw(12, "paschim") - 0.1) * e, size=30)
        note(c, "Raasta andaazan - Zheng He ka asli portrait maujood nahi", at(kw(12, "China")) * e, y0=345)
        r0z = kw(12, "China") - 0.1
        if r0z <= t: ruler(c, "zhenghe", at(r0z, 0.4) * e, seg(t, kw(12, "Western") - 0.75, kw(12, "Western") - 0.3), COL["CHINA"], t, bxy=(150, 560))
    # ================= europe: Eastern Ocean (opposite name)
    if act("europe"):
        e = out("europe"); tE = kw(13, "Eastern")
        headline(c, "EK SAMUDRA, ULTE NAAM", kin("europe", 0.5, 0.1), col=Y)
        c0, c1 = scr(cam, 118, 28), scr(cam, 88, -10)
        route(c, [c0, ((c0[0] + c1[0]) / 2 + 40, (c0[1] + c1[1]) / 2), c1], 1.0, col=COL["CHINA"], w=8, dash=False, a=int(255 * kin("europe") * e))
        label(c, "CHINA: WESTERN", c0[0] - 60, c0[1] - 60, kin("europe") * e, col="#0F1B2D", bg=COL["CHINA"], size=28)
        e0, e1 = scr(cam, 8, 47), scr(cam, 62, -10)
        route(c, [e0, ((e0[0] + e1[0]) / 2 - 60, (e0[1] + e1[1]) / 2), e1], ease_out(at(kw(13, "Europe") - 0.1, 0.8)), col=COL["EURO"], w=8, dash=False, a=int(255 * e))
        region_hl(c, cam, "EUROPE", at(kw(13, "Europe") - 0.15, 0.4) * e, t, COL["EURO"])
        label(c, "EUROPE", e0[0] + 10, e0[1] - 55, at(kw(13, "Europe") - 0.15) * e, size=30)
        label(c, "EUROPE: EASTERN", e1[0] - 80, e1[1] + 70, at(tE - 0.1) * e, col="#0F1B2D", bg=COL["EURO"], size=30)
        label(c, "= POORAB KA SAMUDRA", e1[0] - 80, e1[1] + 135, at(kw(13, "poorab") - 0.1) * e, size=26)
    # ================= latin 1515
    if act("latin"):
        e = out("latin")
        headline(c, "1515: LATIN NAAM", kin("latin", 0.5, 0.2), col=Y)
        tk = seg(t, kw(14, "Oceanus") - 0.15, kw(14, "Indicus") + 0.35)
        typed_card(c, [("OCEANUS ORIENTALIS", 58, "#F1FAEE"), ("INDICUS", 92, Y)], tk, 255 * at(kw(14, "Oceanus") - 0.3, 0.3) * e, 360)
        chip(c, "INDICUS = INDIA KA", DW / 2 - 200, 640, at(kw(15, "India") - 0.15, 0.4) * e, bg=Y, fg="#0F1B2D", size=32)
        chip(c, "ORIENTALIS = POORBI", DW / 2 + 210, 640, at(kw(15, "poorbi") - 0.15, 0.4) * e, bg="#22304A", size=32)
        label(c, "OCEANUS INDICUS", S("io_lbl")[0], S("io_lbl")[1] + 40, at(kw(14, "Indicus")) * e, col="#0F1B2D", bg="#7FDBFF", size=34)
    # ================= why India
    if act("why"):
        e = out("why")
        headline(c, "KYUN INDIA?", kin("why"), col="#FF9933", sub="naksha dekho")
        teer(c, cam, at(kw(18, "teer") - 0.3, 1.0), t, int(255 * e))
        ka = at(kw(18, "samudra") - 0.2, 0.4) * e
        ring_highlight(c, *S("arabsea"), 60, ka, t, col="#7FDBFF")
        ring_highlight(c, *S("bob"), 60, ka, t + 0.4, col="#7FDBFF")
        label(c, "ARABIAN SEA", S("arabsea")[0] - 30, S("arabsea")[1] + 100, ka, col="#7FDBFF", size=28)
        label(c, "BAY OF BENGAL", S("bob")[0] + 10, S("bob")[1] + 100, ka, col="#7FDBFF", size=28)
        chip(c, "PRAYADWEEP: 3 TARAF SAMUDRA", DW / 2, 1110, at(kw(18, "beech") - 0.1, 0.4) * e, bg=Y, fg="#0F1B2D", size=30)
    # ================= hindi name
    if act("hindi"):
        e = out("hindi"); th = kw(19, "Hind M")
        if t < th - 0.2: headline(c, "AAJ HINDI MEIN", kin("hindi"), col="#F1FAEE")
        else: headline(c, "HIND MAHASAGAR", at(th - 0.2, 0.9) * e, col="#FF9933", size=112, sub="hamara apna naam")
        label(c, "HIND MAHASAGAR", S("io_lbl")[0], S("io_lbl")[1] + 30, at(th) * e, col="#0F1B2D", bg="#FF9933", size=40)
    # ================= CTA
    if act("cta", 0, 1):
        k = kin("cta", 0.6)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(205 * k)))
        if t < us(21) - 0.1:
            headline(c, "EK DESH, POORA MAHASAGAR", k, y=230)
            chain = [("RATNAKARA", (540, 400), "#C46A12"), ("ERYTHRAEAN SEA", (540, 510), "#B8323A"), ("WESTERN / EASTERN OCEAN", (540, 620), "#22304A"),
                     ("OCEANUS INDICUS", (540, 730), "#1E4F7A"), ("INDIAN OCEAN", (540, 870), Y)]
            for j, (s_, (x, y), bg) in enumerate(chain):
                kk = at(us(20) + 0.1 + j * 0.32, 0.35)
                if j and kk > 0:
                    (xa, ya) = chain[j - 1][1]
                    route(c, [(xa, ya + 22), (x, y - 40)], ease_out(kk), col=Y, w=4, dash=False)
                chip(c, s_, x, y, kk, bg=bg, fg="#0F1B2D" if j == 4 else "#F1FAEE", size=52 if j == 4 else 32)
        else:
            headline(c, "AAPKO KAUNSA PASAND?", at(us(21) - 0.1, 0.4), y=230)
            poll2(c, [("RATNAKARA", "#C46A12", kw(22, "Ratnakara") - 0.15), ("HIND MAHASAGAR", "#FF9933", kw(22, "Hind") - 0.15),
                      ("INDIAN OCEAN", "#2F6FB5", kw(22, "Indian") - 0.15)], t)
            label(c, "COMMENT KARO", DW / 2, 1040, at(kw(23, "Comment") - 0.1, 0.5), col="#FFFFFF", bg=PAL["axis"], size=44)
            subscribe_btn(c, at(kw(23, "subscribe") - 0.4, 0.5), t, kw(23, "subscribe"))

    if era_now and t < w0:
        s_ = ERA_LABEL[era_now] + " (andaazan)"; w_ = text_w(s_, 22, FT_SEMI)
        x0_ = DW / 2 - (w_ + 50) / 2
        rrect(c, x0_, 1432, x0_ + w_ + 50, 1470, 19, "#3A2410", 215); c.drawCircle(x0_ + 20, 1451, 7, paint("#FF9933"))
        text(c, s_, x0_ + 36, 1459, 22, "#FFE7C2", FT_SEMI, "l", 255)
    doc_up = (act("greek") and t > kw(11, "Periplus") - 0.3) or act("others", 0, 0.3) or act("sanskrit") or (act("greek") and t < T("greek")[0] + 0.7)
    if 0.6 < t < cta0 and not doc_up:
        timeline(c, yr, seg(t, 0.6, 1.2))
    for a, b, cap in CAPS:
        if a - 0.05 <= t < b + 0.12: caption(c, cap, seg(t, a - 0.05, a + 0.08)); break
    if 2.0 < t < cta0:
        if g0 - 0.3 < t < w0 + 0.3:
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
    ti = kw(2, "Indian") - 0.12
    E = [("whoosh_long", 0.15, -14), ("pop", kw(1, "kaunsa"), -12), ("boom", ti, -13), ("ding", ti + 0.3, -15)]
    for i in range(5): E.append(("pop", kw(0, "paanch") - 0.1 + i * 0.13, -19))
    for k_ in ("size", "others", "never", "sanskrit", "greek", "china", "europe", "latin", "why", "hindi", "cta"):
        E.append(("whoosh_fast", T(k_)[0], -19))
    E += [("pop", kw(3, "7") - 0.1, -14), ("pop", kw(3, "kilometre") - 0.1, -16)]
    for u_, w1, w2 in ((5, "Atlantic", "Atlas"), (6, "Pacific", "shaant"), (7, "Arctic", "Bhaalu"), (8, "Southern", "dakshin")):
        E += [("pop", kw(u_, w1) - 0.1, -15), ("pop", kw(u_, w2) - 0.1, -17)]
    E += [("ding", kw(8, "dakshin") + 0.1, -13), ("riser", T("never")[0], -16), ("glitch", kw(9, "nahi") - 0.1, -14),
          ("ding", kw(10, "Ratnakara") - 0.15, -14), ("pop", kw(10, "ratnon") - 0.3, -16),
          ("drag", kw(11, "vyapariyon") - 0.3, -18), ("pop", kw(11, "Periplus") - 0.15, -13), ("drag", kw(11, "Erythraean") - 0.05, -16),
          ("pop", kw(11, "Laal") - 0.15, -15), ("drag", kw(12, "China") - 0.2, -18), ("pop", kw(12, "China") - 0.15, -16),
          ("whoosh_fast", kw(12, "Western") - 0.15, -16), ("pop", kw(12, "paschim") - 0.1, -17),
          ("whoosh_fast", kw(13, "Europe") - 0.1, -17), ("stamp", kw(13, "Eastern") - 0.1, -14), ("pop", kw(13, "poorab") - 0.1, -17),
          ("riser", T("latin")[0], -17), ("ding", kw(14, "Indicus") - 0.1, -13), ("pop", kw(15, "India") - 0.15, -15),
          ("pop", kw(15, "poorbi") - 0.15, -16), ("drag", kw(18, "teer") - 0.3, -15), ("pop", kw(18, "samudra") - 0.2, -16),
          ("boom", kw(19, "Hind M") - 0.2, -12)]
    for j in range(5): E.append(("pop", us(20) + 0.1 + j * 0.32, -17))
    E += [("pop", us(21) - 0.1, -15), ("pop", kw(22, "Ratnakara") - 0.15, -16), ("pop", kw(22, "Hind") - 0.15, -16),
          ("pop", kw(22, "Indian") - 0.15, -16), ("pop", kw(23, "Comment") - 0.1, -14), ("ding", kw(23, "subscribe") + 0.35, -12)]
    E += [("pop", kw(5, "Atlas") - 0.2, -14), ("pop", kw(6, "Pacific") + 0.2, -14), ("pop", kw(7, "Bhaalu") - 0.25, -14),
          ("pop", kw(8, "Southern") + 0.1, -14), ("pop", kw(10, "Sanskrit") - 0.1, -14), ("whoosh_fast", kw(12, "China") - 0.15, -16),
          ("glitch", kw(13, "Europe") - 0.15, -18)]
    return sorted(E, key=lambda e: e[1])
