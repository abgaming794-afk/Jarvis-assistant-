"""AMRIT BORI Short - 'Bombay ya Mumbai - naam kahan se aaya?'  9:16, design 1080x1920 drawn x2 into 2160x3840.
Timing comes from voice/full_units.json (aligned VO). CLI:  python3 short_storyboard.py still OUTDIR t1 t2 ...
Built from _head.py + _helpers_block.py + _tail.py (cat ... > short_storyboard.py).
"""
import os, sys, json, math, re
os.environ.setdefault("AB_PROJECT", "mumbai-naam"); os.environ.setdefault("AB_ORIENT", "vertical")
from core import *
from core import _poly_path
from widgets import *
from shapely.geometry import shape, Polygon
from PIL import Image

ROOT = PROJ
HERE = os.path.dirname(os.path.abspath(__file__))
from shapely.geometry import Polygon as _P, MultiPolygon as _MP
def _nohole(g): return _P(g.exterior) if g.geom_type == "Polygon" else _MP([_P(q.exterior) for q in g.geoms])
EMP = {k: _nohole(shape(v)) for k, v in json.load(open(os.path.join(HERE, "ancient.geojson.json"))).items()}
EMP_PATH = {k: _poly_path(g, 0) for k, g in EMP.items()}
COL = dict(NOW="#FF9933", SEA="#4FC3F7", GOLD="#E8B84A", MAURYA="#E8B84A", PORT="#3B6FD8", ENG="#D8323A")

# South-Asian polities per era (historical-basemaps, approximate) - bhagwa shades in the historical scenes
_ERA_SKIP = {"Simhala", "Parthian Empire", "Safavid Empire", "Tibet", "Burmese kingdoms", "Pegu", "Shan states", "Saylan",
             "Aceh", "Khiva Khanate", "Bukara Khanate", "Ayutthaya", "Dutch East Indies", "Arakan", "Ava", "Post-Ming Warlords",
             "Ceylon", "Kandy", "Ceylon (Dutch)", "central Asian khanates", "Nepal", "Bhutan", "Lan Na", "Afghanistan", "Persia",
             "Manchu Empire", "Assam", "Burma", "Rattanakosin Kingdom", "Turan", "?", "Suren Kingdom", "Sikkim (Indian princely state)"}
ERAS = {k: [(f["name"], shape(f["geom"])) for f in v if f["name"] not in _ERA_SKIP]
        for k, v in json.load(open(os.path.join(HERE, "eras_mumbai.geojson.json"))).items()}
ERA_PATH = {k: [(n, _poly_path(g, 0)) for n, g in v] for k, v in ERAS.items()}
ERA_LABEL = {"CE200": "c. 200 CE ka naksha", "CE1530": "c. 1530 ka naksha", "CE1650": "c. 1650 ka naksha",
             "CE1815": "c. 1815 ka naksha"}
BHAGWA = ["#FF9933", "#F28A22", "#FFB054", "#E67A16", "#FFA347", "#F59B3A"]

# ---- the seven islands of Bombay (hand-traced, approximate; on screen "andaazan") lon, lat
ISLANDS = {
    "COLABA": [(72.8095, 18.8925), (72.8150, 18.8945), (72.8215, 18.9040), (72.8275, 18.9120), (72.8250, 18.9150),
               (72.8165, 18.9065), (72.8100, 18.8985)],
    "OLD WOMAN'S": [(72.8255, 18.9170), (72.8310, 18.9205), (72.8330, 18.9255), (72.8285, 18.9255), (72.8240, 18.9205)],
    "BOMBAY": [(72.8285, 18.9285), (72.8395, 18.9320), (72.8450, 18.9445), (72.8430, 18.9615), (72.8355, 18.9680),
               (72.8240, 18.9640), (72.8120, 18.9660), (72.8000, 18.9600), (72.7945, 18.9500), (72.8000, 18.9465),
               (72.8100, 18.9520), (72.8180, 18.9480), (72.8220, 18.9380)],
    "MAZAGAON": [(72.8465, 18.9550), (72.8520, 18.9600), (72.8525, 18.9720), (72.8455, 18.9745), (72.8420, 18.9650)],
    "PAREL": [(72.8320, 18.9780), (72.8450, 18.9820), (72.8500, 18.9950), (72.8480, 19.0120), (72.8400, 19.0220),
              (72.8320, 19.0180), (72.8280, 19.0000)],
    "WORLI": [(72.8120, 18.9900), (72.8180, 18.9930), (72.8220, 19.0050), (72.8200, 19.0220), (72.8140, 19.0250),
              (72.8100, 19.0120), (72.8090, 18.9980)],
    "MAHIM": [(72.8360, 19.0300), (72.8460, 19.0320), (72.8500, 19.0420), (72.8450, 19.0500), (72.8360, 19.0480),
              (72.8320, 19.0400)],
}
ISL_ORDER = ["COLABA", "OLD WOMAN'S", "BOMBAY", "MAZAGAON", "WORLI", "PAREL", "MAHIM"]
ISL_PATH = {k: _poly_path(Polygon(v), 0) for k, v in ISLANDS.items()}
ISL_MASK = _poly_path(Polygon([(72.70, 18.86), (72.80, 18.86), (72.88, 18.88), (72.905, 18.96), (72.89, 19.035), (72.865, 19.058),
                               (72.80, 19.062), (72.70, 19.062)]), 0)     # sea painted over today's reclaimed island
MERGED = _poly_path(Polygon(ISLANDS["COLABA"][:4] + [(72.8330, 18.9255), (72.8450, 18.9445), (72.8525, 18.9720), (72.8500, 18.9950),
                                                    (72.8500, 19.0420), (72.8450, 19.0500), (72.8360, 19.0480), (72.8200, 19.0300),
                                                    (72.8090, 18.9980), (72.8120, 18.9700), (72.7945, 18.9500), (72.8100, 18.9520),
                                                    (72.8180, 18.9480), (72.8220, 18.9380), (72.8165, 18.9065), (72.8100, 18.8985)]), 0)
VELLARD = [(72.8130, 18.9800), (72.8150, 18.9880)]     # Hornby Vellard (Worli - Mahalaxmi), approximate

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
SCENES = [("hook", 0), ("islands", 3), ("devi", 6), ("ptolemy", 9), ("portugal", 10), ("myth", 12), ("dowry", 14),
          ("company", 16), ("merge", 18), ("local", 19), ("rename", 20), ("cta", 21)]
TAIL = 1.9
T_TOTAL = round(VO_DUR + TAIL, 2)
SC_T = {}
for n_, (k_, u_) in enumerate(SCENES):
    a_ = 0.0 if n_ == 0 else us(u_) - 0.12
    b_ = (us(SCENES[n_ + 1][1]) - 0.12) if n_ + 1 < len(SCENES) else T_TOTAL
    SC_T[k_] = (a_, b_)
def T(k): return SC_T[k]

# phrase captions straight from the VO text (<= ~4 words, split at commas), keywords in yellow
CAP_KEYS = {"bombay", "good", "bay", "nahi", "devi", "mandir", "saat", "dweep", "colaba", "mahim", "worli", "parel", "koli",
            "mumba", "maha", "amba", "aai", "maa", "mumbai", "2nd", "ptolemy", "heptanesia", "1534", "gujarat", "bahadur",
            "shah", "portugal", "bombaim", "bom", "baim", "khaadi", "galat", "1661", "dahej", "catherine", "england",
            "charles", "ii", "1668", "east", "india", "company", "10", "pound", "1845", "shehar", "marathi", "gujarati",
            "mambai", "1995", "shiv", "sena", "english", "videshi", "comment", "subscribe"}
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
RULER = {}
DOC = {}
RULER_INFO = {  # name, line, credit, crop (x0,y0,x1,y1 as fractions)
    "catherine": ("CATHERINE OF BRAGANZA", "Portugal ki rajkumari - Peter Lely ki painting, c. 1663-65", "Royal Collection, public domain", (0.22, 0.03, 0.78, 0.46)),
    "charles": ("RAJA CHARLES II", "England ke raja - J. M. Wright (ya studio), c. 1660s", "Royal Collection, public domain", (0.20, 0.02, 0.80, 0.50)),
    "bahadur": ("SULTAN BAHADUR SHAH", "Mughal painting, c. 1586-87 - baad ka chitran, asli portrait nahi", "LACMA, public domain", (0.25, 0.0, 0.95, 0.56)),
}
def _load_img(f, crop=None):
    try:
        im = Image.open(ROOT + "visuals/photos/" + f).convert("RGB")
        if crop: im = im.crop((int(crop[0] * im.width), int(crop[1] * im.height), int(crop[2] * im.width), int(crop[3] * im.height)))
        return sk_image(im)
    except Exception:
        return None
def load():
    global LOGO
    if LOGO is None:
        LOGO = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_800.png").resize((200, 200)))
        for k_ in ("catherine", "charles", "bahadur"): RULER[k_] = _load_img(k_ + ".jpg")
        DOC["ptolemy"] = _load_img("ptolemy_map.jpg")
        DOC["bahadur"] = _load_img("bahadur.jpg", (0.0, 0.0, 1.0, 0.72))
        DOC["b1672"] = _load_img("bombay1672.jpg")
        DOC["i1893"] = _load_img("islands1893.jpg", (0.22, 0.36, 0.78, 0.80))
        DOC["devi"] = _load_img("mumbadevi.jpg")

MAP_CY = 820   # map vertical centre in design space (upper-middle, clear of Shorts UI)
def scr(cam, lon, lat):
    x, y = to_screen(cam, lon, lat); return x, y - DH / 2 + MAP_CY

FTEX = {}
FLAG_NOTE = {"GUJ": "PRATIK: GUJARAT SULTANATE (andaazan chitran)", "PRT": "PRATIK: PORTUGAL SHAHI NISHAN (andaazan)",
             "ENG": "PRATIK: ENGLAND - ST GEORGE CROSS", "EIC": "PRATIK: EAST INDIA COMPANY ENSIGN (andaazan)", "NOW": "TIRANGA"}
# ---------------------------------------------------------------- symbol textures blended inside borders
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

def poll(c, k, t):
    items = [("INDIA", "#2F6FB5"), ("BHARAT", "#FF9933"), ("HINDUSTAN", "#2FA36B")]
    for i, (s_, col) in enumerate(items):
        kk = ease_out(seg(k, i * 0.18, 0.5 + i * 0.18))
        if kk <= 0: continue
        y = 520 + i * 150; al = int(255 * clamp(kk * 2)); x0 = 160 + (1 - kk) * 200
        rrect(c, x0, y - 55, 920, y + 55, 55, "#18253A", al, shadow=14)
        c.drawCircle(x0 + 58, y, 36, paint(col, al)); text(c, "ABC"[i], x0 + 58, y + 14, 40, "#FFFFFF", FT_BLACK, "c", al)
        text(c, s_, x0 + 120, y + 20, 56, "#F1FAEE", FT_BLACK, "l", al)



# ================================================================ Mumbai-naam: camera, timeline, scene helpers
SA = (78.5, 21.5, 22); MUM = (72.86, 19.0, 170); ISL = (72.826, 18.968, 4000); WIN = (74.0, 20.5, 38)
WIN2 = (70.5, 20.8, 36); EU = (31.0, 36.0, 9.5); MUM2 = (72.9, 19.05, 190); MAH = (76.0, 20.0, 34)
CAM_KEYS = [(0.0, (78, 22, 6)), (1.9, SA), (us(1), SA), (us(2) + 0.6, MUM), (T("islands")[0], MUM),
            (T("islands")[0] + 1.1, ISL), (T("ptolemy")[0], ISL), (T("ptolemy")[0] + 1.2, WIN), (T("portugal")[0], WIN),
            (T("portugal")[0] + 0.9, WIN2), (T("dowry")[0], WIN2), (T("dowry")[0] + 1.4, EU), (T("company")[0], EU),
            (T("company")[0] + 1.3, MUM2), (T("merge")[0], MUM2), (T("merge")[0] + 1.1, ISL), (T("rename")[0], ISL),
            (T("rename")[0] + 1.3, MAH)]
def cam_at(t):
    for (t0, a), (t1, b) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_io(seg(t, t0, t1))
            s = math.exp(lerp(math.log(a[2]), math.log(b[2]), k))
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k), s)
    return CAM_KEYS[-1][1] if t > CAM_KEYS[-1][0] else CAM_KEYS[0][1]

PL = dict(mum=(72.86, 18.98), guj=(71.8, 22.6), lisbon=(-9.14, 38.72), london=(-0.13, 51.5), sea_w=(61.5, 16.0),
          colaba=(72.818, 18.905), mahim=(72.842, 19.041), worli=(72.815, 19.008), parel=(72.840, 19.000),
          bombay=(72.822, 18.953), boats=(72.788, 18.975), vellard=(72.814, 18.984))

TL = [(150, "c.150"), (1534, "1534"), (1661, "1661"), (1845, "1845"), (1995, "1995")]
def timeline(c, year, k):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); x0, x1, y = 110, 970, 1220
    def X(yr):
        pts = [(0, x0), (1400, x0 + 170), (1900, x0 + 720), (2026, x1)]
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= yr <= b: return lerp(xa, xb, (yr - a) / (b - a))
        return x0 if yr < 0 else x1
    c.drawRoundRect(skia.Rect(x0, y - 4, x1, y + 4), 4, 4, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 4, X(year), y + 4), 4, 4, paint(PAL["yel"], al))
    for yr, lab in TL:
        on = abs(yr - year) < 12
        c.drawCircle(X(yr), y, 12 if on else 8, paint(PAL["yel"] if X(yr) <= X(year) + 1 else "#3E5068", al))
        text(c, lab, X(yr), y + 52, 30 if on else 24, "#F1FAEE" if on else PAL["muted"], FT_BLACK if on else FT_SEMI, "c", al)
    lab = f"c. {int(year)} CE" if year < 1000 else (f"{int(year)}" if year < 2025.5 else "AAJ")
    pill(c, lab, X(year), y - 50, 34, PAL["yel"], fg="#0F1B2D", a=al)

def year_at(t):
    i0, p0, d0, c0, m0, r0 = (T(k)[0] for k in ("islands", "portugal", "dowry", "company", "merge", "rename"))
    keys = [(0, 2026), (i0, 2026), (i0 + 1.3, 150), (p0, 150), (p0 + 1.0, 1534), (d0, 1534), (d0 + 0.9, 1661),
            (c0, 1661), (c0 + 0.6, 1668), (m0, 1668), (m0 + 1.2, 1845), (r0, 1845), (r0 + 1.1, 1995), (T("cta")[0], 1995)]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp(a, b, ease_io(seg(t, t0, t1)))
    return 1995

def in_map(c, cam):
    cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_); return s_

def era_layer(c, cam, ek, ea):
    if ea <= 0: return
    s_ = in_map(c, cam)
    for j, (nm, pth) in enumerate(ERA_PATH[ek]):
        c.drawPath(pth, paint(BHAGWA[j % len(BHAGWA)], int(165 * ea)))
        c.drawPath(pth, paint("#FFE7C2", int(140 * ea), stroke=1.0 / s_))
    c.restore()

def draw_islands(c, cam, t, mask_a, rise, hl=None, merge_k=0.0, vel_k=0.0):
    """sea over today's reclaimed island, the seven islands rising one by one, optional highlight + reclamation"""
    if mask_a <= 0: return
    s_ = in_map(c, cam)
    c.drawPath(ISL_MASK, paint(PAL["ocean"], int(255 * mask_a)))
    if merge_k > 0:                                  # reclaimed land fills in between the islands
        c.drawPath(MERGED, paint("#C9A86A", int(235 * ease_out(merge_k) * mask_a)))
        c.drawPath(MERGED, paint("#FFF1C2", int(200 * merge_k * mask_a), stroke=1.6 / s_))
    for i, nm in enumerate(ISL_ORDER):
        k = clamp(rise[i] if isinstance(rise, (list, tuple)) else rise)
        if k <= 0: continue
        e = back(k, 1.6); p = ISL_PATH[nm]; b = p.getBounds()
        c.save(); c.translate(b.centerX(), b.centerY()); c.scale(e, e); c.translate(-b.centerX(), -b.centerY())
        on = hl is not None and hl.get(nm, 0) > 0
        c.drawPath(p, paint("#E8C27A" if not on else "#FFD166", int(255 * clamp(k * 2) * mask_a)))
        c.drawPath(p, paint("#7A5520", int(200 * clamp(k * 2) * mask_a), stroke=1.4 / s_))
        if on:
            hk = hl[nm]; pul = 0.75 + 0.25 * math.sin(t * 6)
            c.drawPath(p, paint("#FFD166", int(170 * hk * pul), stroke=8 / s_, blur=5 / s_))
            c.drawPath(p, paint("#FFF1C2", int(255 * hk), stroke=2.2 / s_))
        c.restore()
    if vel_k > 0:
        (x0, y0), (x1, y1) = cam_xy(*VELLARD[0]), cam_xy(*VELLARD[1])
        c.drawLine(x0, y0, lerp(x0, x1, ease_out(vel_k)), lerp(y0, y1, ease_out(vel_k)), paint("#FFFFFF", int(255 * mask_a), stroke=4 / s_, cap_round=True))
    c.restore()

def temple_icon(c, x, y, s, a=255, col="#FFD166"):
    """small temple (shikhara) icon"""
    if a <= 0: return
    p = skia.Path(); p.moveTo(x - 0.55 * s, y); p.lineTo(x - 0.55 * s, y - 0.35 * s); p.lineTo(x - 0.3 * s, y - 0.35 * s)
    p.quadTo(x - 0.25 * s, y - 0.95 * s, x, y - 1.15 * s); p.quadTo(x + 0.25 * s, y - 0.95 * s, x + 0.3 * s, y - 0.35 * s)
    p.lineTo(x + 0.55 * s, y - 0.35 * s); p.lineTo(x + 0.55 * s, y); p.close()
    c.drawPath(p, paint(col, a)); c.drawPath(p, paint("#5A3E10", a, stroke=max(2, s * 0.05)))
    c.drawRect(skia.Rect(x - 0.12 * s, y - 0.3 * s, x + 0.12 * s, y), paint("#5A3E10", a))
    c.drawLine(x, y - 1.15 * s, x, y - 1.45 * s, paint("#5A3E10", a, stroke=max(2, s * 0.04)))
    fl = skia.Path(); fl.moveTo(x, y - 1.45 * s); fl.lineTo(x + 0.28 * s, y - 1.37 * s); fl.lineTo(x, y - 1.29 * s); fl.close()
    c.drawPath(fl, paint("#FF7A1A", a))

# ---- period symbols (never called real national flags)
def _guj_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#1F6B45")); cc.drawRect(skia.Rect(0, 0, w, h), paint("#E8B84A", 255, stroke=h * 0.12))
    for i in range(3): cc.drawCircle(w * (0.3 + 0.2 * i), h / 2, h * 0.09, paint("#E8B84A"))
def _prt_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#F4F1EA"))
    sw, sh = w * 0.34, h * 0.66; l, tp = w / 2 - sw / 2, h / 2 - sh / 2
    sp = skia.Path(); sp.moveTo(l, tp); sp.lineTo(l + sw, tp); sp.lineTo(l + sw, tp + sh * 0.7); sp.quadTo(l + sw, tp + sh, l + sw / 2, tp + sh)
    sp.quadTo(l, tp + sh, l, tp + sh * 0.7); sp.close(); cc.drawPath(sp, paint("#C8102E"))
    i = sw * 0.16; ip = skia.Path(); ip.moveTo(l + i, tp + i); ip.lineTo(l + sw - i, tp + i); ip.lineTo(l + sw - i, tp + sh * 0.68)
    ip.quadTo(l + sw - i, tp + sh - i, l + sw / 2, tp + sh - i); ip.quadTo(l + i, tp + sh - i, l + i, tp + sh * 0.68); ip.close(); cc.drawPath(ip, paint("#FFFFFF"))
    for k_ in range(6):
        a_ = k_ / 6 * 2 * math.pi; cc.drawRect(skia.Rect(w / 2 + math.cos(a_) * sw * 0.42 - 4, h / 2 + math.sin(a_) * sh * 0.38 - 4, w / 2 + math.cos(a_) * sw * 0.42 + 4, h / 2 + math.sin(a_) * sh * 0.38 + 4), paint("#FFD166"))
    q = sw * 0.11
    for dx, dy in ((0, -1.4), (-1.3, 0), (0, 0), (1.3, 0), (0, 1.4)):
        cx, cy = w / 2 + dx * q * 1.2, h / 2 + dy * q * 1.2
        cc.drawRect(skia.Rect(cx - q / 2, cy - q / 2, cx + q / 2, cy + q / 2), paint("#1F4FA8"))
def _eng_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#FFFFFF"))
    cc.drawRect(skia.Rect(w * 0.42, 0, w * 0.58, h), paint("#CE1124")); cc.drawRect(skia.Rect(0, h * 0.38, w, h * 0.62), paint("#CE1124"))
def _eic_tex(cc, w, h):
    for i in range(13): cc.drawRect(skia.Rect(0, i * h / 13, w, (i + 1) * h / 13 + 1), paint("#CE1124" if i % 2 == 0 else "#FFFFFF"))
    cw, ch = w * 0.4, h * 7 / 13; cc.drawRect(skia.Rect(0, 0, cw, ch), paint("#FFFFFF"))
    cc.drawRect(skia.Rect(cw * 0.42, 0, cw * 0.58, ch), paint("#CE1124")); cc.drawRect(skia.Rect(0, ch * 0.4, cw, ch * 0.6), paint("#CE1124"))
SYM = {"GUJ": _guj_tex, "PRT": _prt_tex, "ENG": _eng_tex, "EIC": _eic_tex}
def sym_flag(c, key, x, y, w, k, t):
    """small waving period symbol on a pole at (x, y) = top of the pole"""
    if k <= 0: return
    if key not in FTEX: FTEX[key] = _surf_img(600, 400, SYM[key])
    img = FTEX[key]; al = clamp(k); h = w * 2 / 3; kk = back(al)
    c.save(); c.translate(x, y); c.scale(kk, kk)
    c.drawLine(0, -4, 0, h * 1.9, paint("#DCE3EC", int(255 * al), stroke=4, cap_round=True))
    n = 40
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n; dy = math.sin(2 * math.pi * (u0 * 1.3 - t * 0.9)) * h * 0.06 * u0
        c.drawImageRect(img, skia.Rect(u0 * 600, 0, min(600, u1 * 600 + 2), 400), skia.Rect(u0 * w, dy, u1 * w + 1, h + dy), SAMP, paint("#FFFFFF", int(255 * al)))
    c.restore()

def pop_words(c, t, s_, t0, y, size, col, a_, gap=0.11):
    ws = s_.split(" "); tw = sum(text_w(w_, size) for w_ in ws) + text_w(" ", size) * (len(ws) - 1); x = DW / 2 - tw / 2
    for i, w_ in enumerate(ws):
        p = seg(t, t0 + i * gap, t0 + i * gap + 0.35); ww = text_w(w_, size)
        if p > 0 and a_ > 0:
            e = back(p, 2.0) if p < 1 else 1.0
            c.save(); c.translate(x + ww / 2, y + (1 - e) * 30); c.scale(0.7 + 0.3 * e, 0.7 + 0.3 * e)
            text(c, w_, 0, 0, size, col, FT_BLACK, "c", int(255 * clamp(p * 2) * a_), shadow=True); c.restore()
        x += ww + text_w(" ", size)
    return tw

def wiki_card2(c, k, t, y0, hs):
    """browser card: Wikipedia 'Mumbai - Etymology', yellow highlighter on 'with no scientific basis' from time hs"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); dy = (1 - ease_out(k)) * 120
    x0, y0, w, h = 100, y0 + dy, 880, 330
    rrect(c, x0, y0, x0 + w, y0 + h, 18, "#FFFFFF", al, shadow=28)
    rrect(c, x0, y0, x0 + w, y0 + 52, 18, "#E9ECF1", al)
    for i, cc in enumerate(("#FF5F57", "#FEBC2E", "#28C840")): c.drawCircle(x0 + 28 + i * 24, y0 + 26, 7, paint(cc, al))
    rrect(c, x0 + 110, y0 + 10, x0 + w - 20, y0 + 42, 16, "#FFFFFF", al)
    text(c, "en.wikipedia.org/wiki/Mumbai#Etymology", x0 + 130, y0 + 33, 19, "#5B6472", FT_SEMI, "l", al)
    text(c, "Mumbai - Etymology", x0 + 28, y0 + 98, 32, "#0F1B2D", FT_BLACK, "l", al)
    c.drawRect(skia.Rect(x0 + 28, y0 + 112, x0 + w - 28, y0 + 114), paint("#C8CCD1", al))
    lines = [("Some Anglophone authors have suggested this", None), ("came from a supposed phrase bom baim,", None),
             ("\"good little bay\", ", "with no scientific basis.")]
    for i, (ln, hl) in enumerate(lines):
        yy = y0 + 160 + i * 44
        text(c, ln, x0 + 28, yy, 28, "#202122", FT_SEMI, "l", al)
        if hl:
            xs = x0 + 28 + text_w(ln, 28, FT_SEMI); hk = ease_out(seg(t, hs, hs + 0.7))
            hp = paint("#FFD166", int(220 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(xs - 4, yy - 29, xs + (text_w(hl, 28, FT_SEMI) + 6) * hk, yy + 9), hp)
            text(c, hl, xs, yy, 28, "#202122", FT_BLACK, "l", al)
    text(c, "Source: Wikipedia (Shirodkar 1998; J. P. Machado)", x0 + w - 28, y0 + h - 18, 18, "#5B6472", FT_SEMI, "r", al)

def poll(c, k, t):
    items = [("BOMBAY", "#2F6FB5"), ("MUMBAI", "#FF9933"), ("DONO", "#2FA36B")]
    for i, (s_, col) in enumerate(items):
        kk = ease_out(seg(k, i * 0.18, 0.5 + i * 0.18))
        if kk <= 0: continue
        y = 520 + i * 150; al = int(255 * clamp(kk * 2)); x0 = 160 + (1 - kk) * 200
        rrect(c, x0, y - 55, 920, y + 55, 55, "#18253A", al, shadow=14)
        c.drawCircle(x0 + 58, y, 36, paint(col, al)); text(c, "ABC"[i], x0 + 58, y + 14, 40, "#FFFFFF", FT_BLACK, "c", al)
        text(c, s_, x0 + 120, y + 20, 56, "#F1FAEE", FT_BLACK, "l", al)

def era_chip(c, s_):
    w_ = text_w(s_, 22, FT_SEMI); x0_ = DW / 2 - (w_ + 50) / 2
    rrect(c, x0_, 1432, x0_ + w_ + 50, 1470, 19, "#3A2410", 215); c.drawCircle(x0_ + 20, 1451, 7, paint("#FF9933"))
    text(c, s_, x0_ + 36, 1459, 22, "#FFE7C2", FT_SEMI, "l", 255)

def sign_board(c, k, flip_k, t):
    """green road-sign that flips from BOMBAY to MUMBAI"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); kk = back(clamp(k)); cx, cy = DW / 2, 520
    sy = abs(math.cos(math.pi * clamp(flip_k)))
    word = "BOMBAY" if flip_k < 0.5 else "MUMBAI"
    c.save(); c.translate(cx, cy); c.scale(kk, kk * max(0.03, sy))
    rrect(c, -330, -110, 330, 110, 22, "#0E6B3A", al, shadow=24)
    c.drawRoundRect(skia.Rect(-314, -94, 314, 94), 16, 16, paint("#FFFFFF", al, stroke=6))
    text(c, word, 0, 42, 118, "#FFFFFF", FT_BLACK, "c", al)
    c.restore()
    c.drawLine(cx - 200, cy + 110 * kk, cx - 200, cy + 230, paint("#9AA5B4", al, stroke=12))
    c.drawLine(cx + 200, cy + 110 * kk, cx + 200, cy + 230, paint("#9AA5B4", al, stroke=12))

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
    i0, d0, p0, dw0, c0, m0, r0, cta0 = (T(k)[0] for k in ("islands", "devi", "portugal", "dowry", "company", "merge", "rename", "cta"))

    # ---- base map: tiranga India in present-day scenes only; historical scenes dim modern borders
    hist = seg(t, i0 + 0.2, i0 + 1.0) * (1 - seg(t, r0, r0 + 0.8))
    base_map(c, cam, t, 1.0, 200 * (1 - hist), border_a=1 - 0.75 * hist)
    now_a = 255 * (1 - hist) * (1 - 0.6 * clamp((cam[2] - 40) / 100))
    if now_a > 0:
        if "NOW" not in EMP_PATH: EMP_PATH["NOW"] = _poly_path(WM.geoms["IND"], 0.01)
        s_ = in_map(c, cam); wave_flag(c, EMP_PATH["NOW"], "NOWV", t, now_a, s_); c.restore()
    # period polities (bhagwa) - only at zooms where the approximate borders read well
    ERA_ON = [("CE200", T("ptolemy")[0], p0 + 0.3), ("CE1530", p0, dw0 + 0.3), ("CE1650", dw0, m0 + 0.2)]
    era_now = None
    for ek, ta, tb in ERA_ON:
        ea = seg(t, ta, ta + 0.6) * (1 - seg(t, tb - 0.3, tb + 0.3))
        if ea > 0.5: era_now = ek
        era_layer(c, cam, ek, ea)
    # the seven islands (islands / devi scenes) and the merged island (merge / local)
    isl_a = seg(t, i0 + 0.5, i0 + 1.3) * (1 - seg(t, T("ptolemy")[0], T("ptolemy")[0] + 0.6)) + \
            seg(t, m0 + 0.3, m0 + 1.0) * (1 - seg(t, r0, r0 + 0.7))
    if isl_a > 0:
        rise = [at(i0 + 0.6 + 0.12 * j, 0.45) if t < T("ptolemy")[0] + 1 else 1.0 for j in range(7)]
        hl = {}
        for nm, w_ in (("COLABA", "Colaba"), ("MAHIM", "Mahim"), ("WORLI", "Worli"), ("PAREL", "Parel")):
            hl[nm] = at(kw(4, w_) - 0.1, 0.3) * (1 - seg(t, ue(4) + 0.6, ue(4) + 0.9))
        mk = seg(t, us(18) + 0.4, kw(18, "1845") + 0.3) if t > m0 else 0.0
        vk = seg(t, kw(18, "samundar") - 0.1, kw(18, "samundar") + 0.6) if t > m0 else 0.0
        draw_islands(c, cam, t, isl_a, rise, hl, mk, vk)

    # ================================================================ scene overlays
    if t < i0:                                           # ---- HOOK
        ho = 1 - seg(t, i0 - 0.35, i0)
        sp_k = at(kw(0, "Bombay") - 0.1, 0.5) * ho
        spotlight(c, *S("mum"), sp_k, t, r0=80)
        label(c, "MUMBAI (BOMBAY)", S("mum")[0] + 10, S("mum")[1] + 110, at(kw(0, "Bombay") + 0.2) * ho, col="#0F1B2D", bg=Y, size=34)
        L = []
        for i, ch in enumerate("BOMBAY"):
            p = seg(t, 0.12 + i * 0.09, 0.12 + i * 0.09 + 0.6); e = back(p, 1.6) if p < 1 else 1.0
            L.append(dict(ch=ch, al=clamp(p * 1.6), dy=(1 - e) * 90, col="#F1FAEE", sy=0.55 + 0.45 * e))
        qd = seg(t, kw(0, "Good") - 0.1, kw(0, "Good") + 0.45)
        L.append(dict(ch="?", w=ease_out(qd), al=qd, dy=-(1 - back(qd, 2.2)) * 120 if qd < 1 else 0, col=Y, rot=(1 - qd) * -25))
        word_row(c, L, DW / 2, 300, 165, 255 * ease_io(seg(t, 0.05, 0.6)) * ho, glow=Y if t < us(2) - 0.2 else "#FFB054")
        sh = seg(t, 0.95, 1.6)
        if 0 < sh < 1:
            bw = text_w("BOMBAY", 165); x0 = DW / 2 - bw / 2 - 60 + (bw + 120) * ease_io(sh)
            g_ = skia.GradientShader.MakeLinear([skia.Point(x0 - 60, 0), skia.Point(x0 + 60, 0)],
                                                [skia.ColorSetARGB(0, 255, 255, 255), skia.ColorSetARGB(int(150 * ho), 255, 255, 255), skia.ColorSetARGB(0, 255, 255, 255)])
            pp = skia.Paint(); pp.setShader(g_); pp.setBlendMode(skia.BlendMode.kPlus)
            c.save(); c.skew(-0.25, 0); c.translate(75, 0); c.drawRect(skia.Rect(x0 - 60, 150, x0 + 60, 340), pp); c.restore()
        q1 = 1 - seg(t, us(2) - 0.3, us(2))
        if q1 > 0:
            tw = pop_words(c, t, "MATLAB = \"GOOD BAY\"?", kw(0, "matlab") - 0.25, 420, 58, "#F1FAEE", q1 * ho)
            sk_ = at(us(1) - 0.05, 0.3)
            if sk_ > 0: c.drawLine(DW / 2 - tw / 2 - 10, 400, DW / 2 - tw / 2 - 10 + (tw + 20) * sk_, 400, paint("#FF4D5E", int(255 * q1), stroke=9, cap_round=True))
            stamp(c, "NAHI!", DW / 2, 540, 70, PAL["axis"], at(us(1) - 0.05, 0.35) * q1)
        if t > us(2) - 0.3:
            ak = seg(t, us(2) - 0.3, us(2)) * ho
            pop_words(c, t, "JAWAB: EK DEVI KA MANDIR", kw(2, "jawab") - 0.1, 420, 56, "#FFD166", ak)
            dk = at(kw(2, "devi") - 0.15, 0.5) * ho
            if dk > 0:
                x, y = S("mum")
                c.drawCircle(x, y - 40, 120 * ease_out(dk), paint("#FFD166", int(90 * dk), blur=30))
                temple_icon(c, x, y - 10, 90 * back(dk), int(255 * clamp(dk * 2)))
                rp = (t % 1.0); c.drawCircle(x, y - 40, 60 + 90 * rp, paint("#FFD166", int(180 * dk * (1 - rp)), stroke=4))
    if act("islands"):                                   # ---- SAAT DWEEP
        headline(c, "KABHI SAAT DWEEP THE", kin("islands", 0.5, 0.2), col=Y, sub="Aaj ke Mumbai ki jagah")
        n7 = sum(1 for j in range(7) if t > i0 + 0.6 + 0.12 * j + 0.2)
        if n7: chip(c, f"{n7} DWEEP", 905, 1110, at(i0 + 0.7) * out("islands"), bg=Y, fg="#0F1B2D", size=34)
        for nm, w_, key, dx, dy in (("COLABA", "Colaba", "colaba", -170, 30), ("MAHIM", "Mahim", "mahim", 150, -20),
                                    ("WORLI", "Worli", "worli", -150, -60), ("PAREL", "Parel", "parel", 170, 10)):
            x, y = S(key); label(c, nm, x + dx, y + dy, at(kw(4, w_) - 0.05) * out("islands"), size=32)
        bk = at(kw(5, "Koli") - 0.2, 0.5) * out("islands")
        if bk > 0:
            bx, by = S("boats")
            for j, (ox, oy) in enumerate(((-70, -130), (-120, 10), (-60, 150))):
                ic_ship(c, bx + ox + 6 * math.sin(t * 2 + j), by + oy, 34 * back(bk), col="#DCE3EC", a=int(255 * clamp(bk * 2)))
            label(c, "KOLI MACHHUARE", bx - 40, by - 270, bk, col="#0F1B2D", bg="#7FDBFF", size=32)
    if act("devi"):                                      # ---- MUMBA DEVI
        k_ = kin("devi", 0.5) * out("devi", 0.25)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(170 * k_)))
        headline(c, "MUMBA DEVI", kin("devi", 0.4), col="#FFB054", size=96)
        if DOC.get("devi") is not None:
            manuscript_card(c, DOC["devi"], at(kw(6, "Mumba") - 0.3, 0.5) * out("devi", 0.25), t, 540, 600, 360, -2,
                            "MUMBA DEVI", "KOLI KULDEVI KA MANDIR", "Photo: Magiceye (Flickr), CC BY-SA 2.0")
        c1 = at(kw(7, "Maha") - 0.15) * (1 - seg(t, us(8) - 0.2, us(8)))
        c2 = at(kw(7, "Aai") - 0.15) * (1 - seg(t, us(8) - 0.2, us(8)))
        chip(c, "MUMBA = MAHA AMBA (MAHAN MAA)", DW / 2, 1040, c1, bg="#C46A12", size=34)
        chip(c, "AAI = MAA (MARATHI)", DW / 2, 1118, c2, bg="#22304A", size=34)
        if t > us(8) - 0.2:
            a_ = 255 * at(us(8) - 0.2, 0.4) * out("devi", 0.25)
            pk = seg(t, kw(8, "Aai") - 0.1, kw(8, "Aai") + 0.35)
            bk = seg(t, kw(8, "bana") - 0.05, kw(8, "bana") + 0.5)
            L = [Lw(ch, "#FFB054") for ch in "MUMBA"] + [Lw("+", "#F1FAEE", w=pk * (1 - bk), al=pk * (1 - bk))] + \
                [Lw("A", "#F1FAEE", w=pk * (1 - bk), al=pk * (1 - bk * 1.5)), Lw("A", "#F1FAEE", w=pk * (1 - bk), al=pk * (1 - bk * 1.5)),
                 Lw("I", Y if bk > 0.5 else "#F1FAEE", w=pk, al=pk)]
            word_row(c, L, DW / 2, 1080, 120, a_, glow=Y if bk > 0.5 else "#FFB054")
    if act("ptolemy"):                                   # ---- PTOLEMY / HEPTANESIA
        k_ = kin("ptolemy", 0.5) * out("ptolemy", 0.25)
        mk = at(kw(9, "Ptolemy") - 0.4, 0.5) * out("ptolemy", 0.25)
        if mk > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(140 * mk)))
        headline(c, "c. 150 CE: PTOLEMY", kin("ptolemy", 0.5, 0.1), col="#6FA8FF")
        manuscript_card(c, DOC["ptolemy"], mk, t, 540, 620, 820, -1.5, "PTOLEMY KA NAKSHA", "GEOGRAPHIA - 15vi SADI KI PRATI",
                        "British Library, Harley MS 7182 (public domain)")
        hk = at(kw(9, "Heptanesia") - 0.15, 0.4) * out("ptolemy", 0.25)
        if hk > 0:
            sk_ = seg(t, kw(9, "saat") - 0.1, kw(9, "saat") + 0.4)
            L = [Lw(ch, "#6FA8FF") for ch in "HEPTA"] + [Lw(ch, "#F1FAEE") for ch in "NESIA"]
            word_row(c, L, DW / 2, 1110, 92, 255 * hk, glow="#6FA8FF")
            chip(c, "HEPTA = 7  +  NESOS = DWEEP", DW / 2, 1010 - 0, sk_ * out("ptolemy", 0.25), bg=Y, fg="#0F1B2D", size=32)
    if act("portugal"):                                  # ---- 1534 PORTUGAL
        gk = at(kw(10, "Gujarat") - 0.15, 0.4) * out("portugal")
        ring_highlight(c, *S("guj"), 70, gk * (1 - 0.6 * seg(t, kw(10, "Portugal"), kw(10, "Portugal") + 0.4)), t)
        label(c, "GUJARAT SULTANATE", S("guj")[0] + 40, S("guj")[1] - 100, gk * (1 - seg(t, kw(11, "Bombaim") - 0.6, kw(11, "Bombaim") - 0.3)), size=32)
        sym_flag(c, "GUJ", S("guj")[0] + 180, S("guj")[1] - 40, 90, gk, t)
        pk = at(kw(10, "Portugal") - 0.25, 1.0) * out("portugal")
        p0_, p1_ = S("sea_w"), S("mum")
        route(c, [p0_, ((p0_[0] + p1_[0]) / 2, p1_[1] - 120), p1_], ease_out(pk), col="#6FA8FF", w=6)
        if pk > 0:
            ic_ship(c, lerp(p0_[0], p1_[0], ease_out(pk)), lerp(p0_[1], p1_[1], ease_out(pk)) - 50 * math.sin(math.pi * ease_out(pk)), 40, col="#F1FAEE", a=int(255 * clamp(pk * 3)))
            label(c, "PORTUGAL KE JAHAZ", p0_[0] + 150, p0_[1] + 90, at(kw(10, "Portugal")) * out("portugal"), col="#0F1B2D", bg="#9CC3FF", size=30)
            sym_flag(c, "PRT", p0_[0] + 40, p0_[1] - 170, 100, at(kw(10, "Portugal")) * out("portugal"), t)
        spotlight(c, *S("mum"), at(kw(10, "dweep") - 0.1, 0.4) * out("portugal") * 0.6, t, r0=50)
        headline(c, "1534: PORTUGAL", kin("portugal", 0.5, 0.2), col="#6FA8FF", sub="Sandhi 1534, kabza 1535")
        bk = at(kw(11, "Bombaim") - 0.45, 0.4) * out("portugal")
        if bk > 0:
            L = []
            for i, ch in enumerate("BOMBAIM"):
                p = seg(t, kw(11, "Bombaim") - 0.25 + i * 0.07, kw(11, "Bombaim") - 0.25 + i * 0.07 + 0.4)
                L.append(dict(ch=ch, al=p, w=1, dy=(1 - ease_out(p)) * -40, col="#9CC3FF", rot=(1 - p) * 20))
            word_row(c, L, DW / 2, 470, 120, 255 * bk, glow="#6FA8FF")
            chip(c, "PORTUGUESE LEKH: \"BOMBAIM\"", DW / 2, 580, at(kw(11, "likhte") - 0.1) * out("portugal"), bg="#22304A", size=30)
    if act("myth"):                                      # ---- BOM BAIM MYTH
        k_ = kin("myth", 0.5) * out("myth", 0.25)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(170 * k_)))
        headline(c, "\"GOOD BAY\" WALI KAHANI", kin("myth", 0.5), col=Y)
        L = [Lw(ch, "#9CC3FF") for ch in "BOM"] + [Lw(" ")] + [Lw(ch, "#9CC3FF") for ch in "BAIM"]
        word_row(c, L, DW / 2, 430, 110, 255 * kin("myth", 0.4, 0.1) * out("myth", 0.25), glow="#6FA8FF")
        chip(c, "BOM = ACHHA", DW / 2 - 220, 545, at(kw(12, "achhi") - 0.15) * out("myth", 0.25), bg="#22304A", size=32)
        chip(c, "BAIM = KHAADI?", DW / 2 + 220, 545, at(kw(12, "khaadi") - 0.15) * out("myth", 0.25), bg="#22304A", size=32)
        wiki_card2(c, at(us(13) - 0.1, 0.6) * out("myth", 0.25), t, 620, kw(13, "jaankaar") - 0.1)
        stamp(c, "MYTH", 800, 1060, 70, PAL["axis"], at(kw(13, "ise") - 0.1, 0.35) * out("myth", 0.25))
    if act("dowry"):                                     # ---- 1661 DOWRY
        e = out("dowry")
        lk = at(dw0 + 1.2, 0.4) * e
        ring_highlight(c, *S("lisbon"), 34, lk, t, col="#9CC3FF"); ring_highlight(c, *S("london"), 34, lk, t, col="#FF8A92")
        label(c, "PORTUGAL", S("lisbon")[0] - 30, S("lisbon")[1] + 70, lk, size=28)
        label(c, "ENGLAND", S("london")[0] + 10, S("london")[1] - 70, lk, size=28)
        sym_flag(c, "PRT", S("lisbon")[0] + 40, S("lisbon")[1] - 20, 70, lk, t)
        sym_flag(c, "ENG", S("london")[0] + 90, S("london")[1] - 60, 80, lk, t)
        spotlight(c, *S("mum"), lk * 0.5, t, r0=40)
        label(c, "BOMBAY", S("mum")[0] + 20, S("mum")[1] + 70, lk, col="#0F1B2D", bg=Y, size=28)
        headline(c, "1661: DAHEJ MEIN DWEEP!", kin("dowry", 0.5, 0.2), col="#FF8A92")
        dk = at(kw(14, "dahej") - 0.3, 1.3) * e
        p0_, p1_ = S("mum"), S("london")
        rr = route(c, [p0_, ((p0_[0] + p1_[0]) / 2 + 60, min(p0_[1], p1_[1]) - 60), p1_], ease_out(dk), col=Y, w=6)
        label(c, "DAHEJ, 1661", (p0_[0] + p1_[0]) / 2 + 120, (p0_[1] + p1_[1]) / 2 - 40, at(kw(14, "dahej")) * e, col="#0F1B2D", bg=Y, size=32)
        hk = at(kw(15, "shaadi") - 0.1, 0.4) * e
        if hk > 0:                                       # heart between the two portrait badges
            x, y, s = DW / 2, 1010, 34 * back(hk)
            hp = skia.Path(); hp.moveTo(x, y + s); hp.cubicTo(x - 2.2 * s, y - 0.4 * s, x - 0.9 * s, y - 1.8 * s, x, y - 0.6 * s)
            hp.cubicTo(x + 0.9 * s, y - 1.8 * s, x + 2.2 * s, y - 0.4 * s, x, y + s); c.drawPath(hp, paint("#FF4D5E", int(255 * clamp(hk * 2))))
            text(c, "SHAADI, 1662", DW / 2, 1085, 26, "#F1FAEE", FT_BLACK, "c", int(255 * hk), shadow=True)
    if act("company"):                                   # ---- 1668 EAST INDIA COMPANY
        headline(c, "1668: EAST INDIA COMPANY", kin("company", 0.5, 0.2), col="#FF8A92")
        dk = at(kw(16, "East") - 0.3, 0.5) * (1 - seg(t, us(17) - 0.25, us(17)))
        if dk > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(130 * dk)))
        manuscript_card(c, DOC["b1672"], dk, t, 290, 640, 320, -3, "BOMBAY, 1672", "JOHN FRYER KA NAKSHA",
                        "Bombay Gazetteer 1896 / British Library (public domain)")
        sk_ = at(kw(16, "10") - 0.2, 0.6) * (1 - seg(t, us(17) - 0.25, us(17)))
        if sk_ > 0:
            v = int(round(lerp(0, 10, ease_out(seg(t, kw(16, "10") - 0.2, kw(16, "10") + 0.5)))))
            stat_card(c, 610, 400, 400, 270, f"£{v}", "SAALANA KIRAYA", sk_, col=Y)
        ek = at(kw(16, "Company") - 0.2) * (1 - seg(t, us(17) - 0.25, us(17)))
        sym_flag(c, "EIC", 700, 760, 150, ek, t)
        if ek > 0: text(c, "EAST INDIA COMPANY", 810, 1000, 28, "#F1FAEE", FT_BLACK, "c", int(255 * ek), shadow=True)
    if act("company", 0, 0.8) and t > us(17) - 0.3:
        if True:
            hold = 1 - seg(t, T("company")[1] + 0.5, T("company")[1] + 0.8)
            a_ = 255 * at(us(17) - 0.3, 0.4) * hold
            yk = seg(t, kw(17, "Bombay") - 0.1, kw(17, "Bombay") + 0.5)
            L = [Lw(ch, "#9CC3FF") for ch in "BOMBA"] + \
                [Lw("I", "#FF4D5E" if yk > 0.05 else "#9CC3FF", w=1 - seg(yk, 0.5, 1), al=1 - seg(yk, 0.4, 1), dy=ease_in(yk) * 120, rot=yk * 35, strike=seg(yk, 0, 0.35)),
                 flip("M", "Y", seg(yk, 0.3, 1), "#9CC3FF", Y)]
            word_row(c, L, DW / 2, 600, 140, a_, glow="#FF8A92")
            chip(c, "ANGREZI ROOP: BOMBAY", DW / 2, 730, at(kw(17, "Bombay") + 0.2) * hold, bg=Y, fg="#0F1B2D", size=34)
    if act("merge"):                                     # ---- SAAT DWEEP, EK SHEHAR
        headline(c, "SAAT DWEEP, EK SHEHAR", kin("merge", 0.5, 0.2), col=Y, sub="Samundar bhar ke zameen banayi")
        x, y = S("vellard")
        label(c, "HORNBY VELLARD, 1782-84", x - 60, y - 70, at(kw(18, "samundar") + 0.2) * out("merge"), size=26)
        chip(c, "1838-1845 TAK (behes)", DW / 2, 1110, at(kw(18, "1845") - 0.1) * out("merge"), bg=Y, fg="#0F1B2D", size=32)
    if act("local"):                                     # ---- LOCAL NAAM
        k_ = kin("local", 0.4) * out("local", 0.25)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(120 * k_)))
        headline(c, "LOCAL NAAM: MUMBAI", kin("local", 0.4), col="#FFB054")
        chip(c, "MARATHI:  MUMBAI", DW / 2, 430, at(kw(19, "Marathi") - 0.1) * out("local", 0.25), bg="#C46A12", size=40)
        chip(c, "GUJARATI:  MUMBAI / MAMBAI", DW / 2, 530, at(kw(19, "Gujarati") - 0.1) * out("local", 0.25), bg="#C46A12", size=40)
        chip(c, "HINDI:  BAMBAI", DW / 2, 630, at(kw(19, "Mambai") + 0.1) * out("local", 0.25), bg="#22304A", size=34)
        text(c, "Purane lekh: 1516 \"Maiambu\" (Barbosa) - 1762 \"Manbai\" (Mirat-i Ahmadi)", DW / 2, 720, 24, "#DCE3EC", FT_SEMI, "c",
             int(255 * at(kw(19, "hi raha") - 0.1) * out("local", 0.25)), shadow=True)
    if act("rename"):                                    # ---- 1995
        spotlight(c, *S("mum"), at(kw(20, "sarkar") - 0.1) * out("rename") * 0.6, t, r0=45)
        headline(c, "1995: OFFICIAL NAAM MUMBAI", kin("rename", 0.5, 0.2), col="#FF9933")
        sign_board(c, at(r0 + 0.4, 0.5) * out("rename"), seg(t, kw(20, "Mumbai") - 0.1, kw(20, "Mumbai") + 0.4), t)
        chip(c, "SHIV SENA (MAHARASHTRA SARKAR) KI MAANG", DW / 2, 790, at(kw(20, "Shiv") - 0.1) * out("rename"), bg="#22304A", size=28)
    if act("cta", 0, 1):                                 # ---- CTA
        k = kin("cta", 0.6)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(205 * k)))
        if t < us(22) - 0.1:
            headline(c, "EK SHEHAR, DO NAAM", k, y=230)
            r1 = at(us(21) + 0.1, 0.4); r2 = at(kw(21, "Bombay") - 0.15, 0.4)
            temple_icon(c, 160, 600, 60, int(255 * clamp(r1 * 2)))
            chip(c, "MUMBA AAI  >  MUMBAI", DW / 2 + 40, 565, r1, bg="#C46A12", size=44)
            chip(c, "BOMBAIM  >  BOMBAY", DW / 2 + 40, 725, r2, bg="#1E4F7A", size=44)
            text(c, "devi ka naam", DW / 2 + 40, 640, 28, "#FFE7C2", FT_SEMI, "c", int(255 * r1))
            text(c, "videshi roop", DW / 2 + 40, 800, 28, "#CFE4FF", FT_SEMI, "c", int(255 * r2))
        else:
            headline(c, "AAP KYA BOLTE HO?", at(us(22) - 0.1, 0.4), y=230)
            poll(c, seg(t, us(22) - 0.1, us(22) + 1.2), t)
            label(c, "COMMENT KARO", DW / 2, 1040, at(kw(23, "Comment") - 0.1, 0.5), col="#FFFFFF", bg=PAL["axis"], size=44)
            subscribe_btn(c, at(kw(23, "subscribe") - 0.4, 0.5), t, kw(23, "subscribe"))

    # ---- rulers: big card on the name, then a badge for the rest of the scene
    rb = kw(10, "Bahadur") - 0.35
    if rb <= t < T("portugal")[1]:
        ruler(c, "bahadur", at(rb, 0.4) * out("portugal"), seg(t, kw(10, "Portugal") - 0.2, kw(10, "Portugal") + 0.25), "#6FD38F", t, bxy=(915, 990))
    rc = kw(15, "Catherine") - 0.4
    if rc <= t < T("dowry")[1]:
        ruler(c, "catherine", at(rc, 0.4) * out("dowry"), seg(t, kw(15, "England") - 0.3, kw(15, "England") + 0.1), "#9CC3FF", t, bxy=(250, 990))
    rh = kw(15, "Charles") - 0.45
    if rh <= t < T("dowry")[1]:
        ruler(c, "charles", at(rh, 0.4) * out("dowry"), seg(t, ue(15) - 0.15, ue(15) + 0.3), "#FF8A92", t, bxy=(830, 990))
    # ---- period symbol notes (never called real flags)
    note = None
    if act("portugal") and t > kw(10, "Portugal") + 0.3: note = "PRT"
    elif act("portugal") and t > kw(10, "Gujarat") + 0.3: note = "GUJ"
    elif act("dowry") and t > dw0 + 1.6: note = "ENG"
    elif act("company") and t > kw(16, "Company") + 0.2 and t < us(17) - 0.3: note = "EIC"
    if note: flag_note(c, note, 1.0)
    # ---- era chip
    chip_s = None
    if act("islands") or act("devi"): chip_s = "Saat dweep, c. 150 CE (andaazan)"
    elif act("merge") or act("local"): chip_s = "Dweep jodne ka kaam, 1782-1845 (andaazan)"
    elif era_now: chip_s = ERA_LABEL[era_now] + " (andaazan)"
    if chip_s and not act("myth"): era_chip(c, chip_s)

    if 0.6 < t < cta0 and not act("myth") and not act("devi"):
        timeline(c, yr, seg(t, 0.6, 1.2))
    for a, b, cap in CAPS:
        if a - 0.05 <= t < b + 0.12: caption(c, cap, seg(t, a - 0.05, a + 0.08)); break
    if 2.0 < t < cta0 and not act("myth") and not act("devi"):
        text(c, "Approx. borders: historical-basemaps (A. Ourednik); dweep: andaazan", DW / 2, 1505, 19, PAL["muted"], FT_SEMI, "c", 210)
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
    E = [("whoosh_long", 0.15, -14), ("pop", kw(0, "Good") - 0.1, -12), ("stamp", us(1) - 0.05, -11), ("ding", kw(2, "devi") - 0.1, -14)]
    for k_ in ("islands", "devi", "ptolemy", "portugal", "myth", "dowry", "company", "merge", "local", "rename", "cta"):
        E.append(("whoosh_fast", T(k_)[0], -19))
    E += [("riser", T("islands")[0] + 0.1, -16)]
    for j in range(7): E.append(("pop", T("islands")[0] + 0.6 + 0.12 * j, -20))
    for w in ("Colaba", "Mahim", "Worli", "Parel"): E.append(("pop", kw(4, w) - 0.1, -16))
    E += [("pop", kw(5, "Koli") - 0.2, -16), ("pop", kw(6, "Mumba") - 0.3, -14), ("pop", kw(7, "Maha") - 0.15, -15),
          ("pop", kw(7, "Aai") - 0.15, -15), ("ding", kw(8, "bana") - 0.05, -13),
          ("pop", kw(9, "Ptolemy") - 0.4, -14), ("pop", kw(9, "Heptanesia") - 0.15, -15), ("ding", kw(9, "saat") - 0.1, -15),
          ("pop", kw(10, "Gujarat") - 0.15, -15), ("pop", kw(10, "Bahadur") - 0.35, -13), ("drag", kw(10, "Portugal") - 0.25, -16),
          ("pop", kw(11, "Bombaim") - 0.25, -15), ("pop", kw(12, "achhi") - 0.15, -15), ("pop", kw(12, "khaadi") - 0.15, -15),
          ("drag", kw(13, "jaankaar") - 0.1, -17), ("stamp", kw(13, "ise") - 0.1, -11),
          ("riser", T("dowry")[0], -16), ("whoosh_long", kw(14, "dahej") - 0.3, -15), ("pop", kw(15, "Catherine") - 0.4, -13),
          ("pop", kw(15, "Charles") - 0.45, -13), ("ding", kw(15, "shaadi") - 0.1, -15),
          ("pop", kw(16, "East") - 0.3, -14), ("pop", kw(16, "10") - 0.2, -13), ("glitch", kw(17, "Bombay") - 0.1, -14),
          ("drag", kw(18, "samundar") - 0.1, -15), ("ding", kw(18, "1845") - 0.1, -14),
          ("pop", kw(19, "Marathi") - 0.1, -15), ("pop", kw(19, "Gujarati") - 0.1, -15), ("pop", kw(19, "Mambai") + 0.1, -16),
          ("boom", T("rename")[0] + 0.1, -13), ("glitch", kw(20, "Mumbai") - 0.1, -13), ("pop", kw(20, "Shiv") - 0.1, -16),
          ("pop", us(21) + 0.1, -15), ("pop", kw(21, "Bombay") - 0.15, -14), ("pop", us(22) - 0.1, -15), ("pop", us(22) + 0.1, -17),
          ("pop", us(22) + 0.3, -17), ("pop", kw(23, "Comment") - 0.1, -14), ("ding", kw(23, "subscribe") + 0.35, -12)]
    return sorted(E, key=lambda e: e[1])
