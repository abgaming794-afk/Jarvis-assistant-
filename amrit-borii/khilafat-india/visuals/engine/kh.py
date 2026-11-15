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
HOSTS = []
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
                "c_europe": CALIPH.intersection(box(-20, 35.8, 10, 50)), "desert": CALIPH.intersection(box(61.2, 23, 72.5, 31)), "c_west": CALIPH.intersection(box(-20, 20, -1.0, 44))})
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

# ---------------------------------------------------------------- symbolic banners (8th-century flags are not recorded:
# labelled PRATIK/andaazan; Umayyad white and Abbasid black banners are documented)
BANNER = {"iberia": ("#8B1E2D", "cross", "#E9C46A", "VISIGOTH SPAIN"), "sindh": ("#D9822B", "sun", "#FFE8A3", "SINDH · CHACH VANSH"),
          "india": ("TIRANGA", None, None, "HINDUSTAN"), "arabia": ("#FFFFFF", None, None, "ARAB"),
          "syria": ("#FFFFFF", None, None, "DAMASCUS (SHAM)"), "iraq": ("#FFFFFF", None, None, "IRAQ"),
          "centralasia": ("#FFFFFF", None, None, "CENTRAL ASIA"), "c_asia": None, "c_africa": None, "c_europe": None,
          "umayyad": ("#FFFFFF", None, None, "UMAYYAD KHILAFAT"), "abbasid": ("#111111", None, None, "ABBASI KHILAFAT"),
          "kabul": ("#B23A48", "sun", "#F1FAEE", "TURK SHAHI"), "zabul": ("#2A9D8F", "sun", "#F1FAEE", "ZUNBIL"),
          "gujarat": ("#C2185B", "star", "#FFD166", "CHALUKYA"), "rajasthan": ("#D35400", "sun", "#FFE8A3", "MORI / GURJARA"),
          "mp": ("#6A4C93", "star", "#FFD166", "MALWA"), "pratihara": ("#C0392B", "sun", "#FFE8A3", "PRATIHARA"),
          "desert": None, "caliph": ("#FFFFFF", None, None, "UMAYYAD KHILAFAT"), "raidzone": None, "c_west": None,
          "kashmir": ("#B5179E", None, None, "KASHMIR · KARKOTA"), "kannauj": ("#4CC9F0", None, None, "KANNAUJ"),
          "deccan": ("#43AA8B", None, None, "CHALUKYA (BADAMI)"), "east": ("#F9C74F", None, None, "GAUDA · MAGADHA"),
          "south": ("#F94144", None, None, "PALLAVA"), "kamarupa": ("#4D908E", None, None, "KAMARUPA")}
_BTEX = {}
def banner_tex(key):
    """plain flag in the region's own colour (user: "har jhande ko uska colour do"); the Umayyad/khilafat banner is
    white and the Abbasid banner black - those two colours are documented"""
    col = {"umayyad": "#1F9D5C", "caliph": "#1F9D5C", "abbasid": "#111111"}.get(key) or REGCOL.get(key, "#FFFFFF")
    if col in _BTEX: return _BTEX[col]
    sf = skia.Surface(600, 400); cc = sf.getCanvas(); cc.clear(hexc(col))
    if col not in ("#FFFFFF", "#111111"): cc.drawRect(skia.Rect(0, 340, 600, 400), paint(lighten(col, 0.35)))
    _BTEX[col] = sf.makeImageSnapshot(); return _BTEX[col]
    bgc, emb, ec, _ = BANNER[key]
    if bgc == "TIRANGA": _BTEX[key] = flag_img("in"); return _BTEX[key]
    W_, H_ = 600, 400; sf = skia.Surface(W_, H_); cc = sf.getCanvas(); cc.clear(hexc(bgc))
    if emb == "cross":
        cc.drawRect(skia.Rect(270, 70, 330, 330), paint(ec)); cc.drawRect(skia.Rect(170, 150, 430, 210), paint(ec))
    elif emb == "sun":
        cc.drawCircle(300, 200, 70, paint(ec))
        for i in range(12):
            an = i / 12 * math.tau; cc.drawLine(300 + 90 * math.cos(an), 200 + 90 * math.sin(an), 300 + 130 * math.cos(an), 200 + 130 * math.sin(an), paint(ec, 255, stroke=14, cap_round=True))
    elif emb == "star":
        pth = skia.Path()
        for i in range(16):
            r_ = 120 if i % 2 == 0 else 55; an = i / 16 * math.tau - math.pi / 2
            (pth.moveTo if i == 0 else pth.lineTo)(300 + r_ * math.cos(an), 200 + r_ * math.sin(an))
        pth.close(); cc.drawPath(pth, paint(ec))
    _BTEX[key] = sf.makeImageSnapshot(); return _BTEX[key]

def cloth(c, img, x0, y0, w, h, t, a=255, n=48, amp_k=0.05):
    """draw img waving like cloth into the box (vertical strips with a travelling sine + light/dark shading)"""
    iw, ih = img.width(), img.height(); amp = h * amp_k; pw = w / n
    lp = skia.Paint(); lp.setAlphaf(clamp(a / 255)); c.saveLayer(skia.Rect(x0 - 4, y0 - amp * 2, x0 + w + 4, y0 + h + amp * 2), lp)
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n; dy = math.sin(2 * math.pi * (u0 * 1.4 - t * 0.8)) * amp * u0
        c.drawImageRect(img, skia.Rect(u0 * iw, 0, min(iw, u1 * iw + 1), ih), skia.Rect(x0 + u0 * w, y0 + dy, x0 + u1 * w + pw * 0.5, y0 + h + dy), SAMP, skia.Paint())
    cols, pos = [], []
    for i in range(n + 1):
        u = i / n; sh = math.cos(2 * math.pi * (u * 1.4 - t * 0.8)) * u
        cols.append(skia.ColorSetARGB(int(abs(sh) * 60), 255, 255, 255) if sh > 0 else skia.ColorSetARGB(int(abs(sh) * 80), 0, 0, 0)); pos.append(u)
    gp = skia.Paint(); gp.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x0 + w, 0)], cols, pos))
    gp.setBlendMode(skia.BlendMode.kSrcATop); c.drawRect(skia.Rect(x0, y0 - amp * 2, x0 + w, y0 + h + amp * 2), gp)
    c.restore()

_RP = {}
def rep_point(name):
    if name not in _RP: p_ = REG[name].representative_point(); _RP[name] = (p_.x, p_.y)
    return _RP[name]

def pole_flag(c, x, y, key, t, k, size=1.0, show_label=True):
    """floating flag on a pole that rises in, bobs gently and waves"""
    if k <= 0 or not BANNER.get(key): return
    kk = ease_out(clamp(k)); al = int(255 * clamp(k * 1.6)); bob = math.sin(t * 2.0 + x * 0.01) * 5
    sw = math.sin(t * 1.3 + y * 0.01) * 1.5
    c.save(); c.translate(x, y + bob + (1 - kk) * 40); c.rotate(sw); c.scale(size, size)
    c.drawCircle(0, 0, 7, paint("#000000", int(al * 0.4), blur=4))
    c.drawLine(0, 0, 0, -150, paint("#E5E7EB", al, stroke=4, cap_round=True)); c.drawCircle(0, -152, 6, paint("#E9C46A", al))
    img = banner_tex(key); fw = 120; fh = fw * img.height() / img.width()
    c.drawRect(skia.Rect(4, -146 + 6, 4 + fw, -146 + fh + 10), paint("#000000", int(al * 0.25), blur=6))
    cloth(c, img, 2, -146, fw, fh, t, al, 30, 0.08)
    if show_label:
        lab = BANNER[key][3]; fs = 17; tw = text_w(lab, fs, FT_SEMI)
        rrect(c, -tw / 2 - 12 + 60, 14, tw / 2 + 12 + 60, 42, 14, "#0B1424", int(al * 0.85))
        text(c, lab, 60, 34, fs, "#E5E7EB", FT_SEMI, "c", al)
    c.restore()

def lighten(h, f=0.45):
    h = h.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(int(v + (255 - v) * f) for v in (r, g, b))
REGCOL = {"iberia": "#3A86FF", "centralasia": "#9B5DE5", "india": "#FF9933", "arabia": "#00BBF9", "syria": "#F15BB5",
          "sindh": "#FF6B6B", "iraq": "#F8961E", "c_asia": "#00BBF9", "c_africa": "#F8961E", "c_europe": "#3A86FF", "caliph": GREEN, "c_west": "#3A86FF"}
def hl(c, cam, name, t, t0, col=None, fill=None, dur=99.0, flag=None, flag_at=None, flag_label=True, pole=True):
    """highlight a region when its name is spoken: own-colour fill + the region's banner waving inside its border
    (cloth), thin light outline, and a floating pole flag above it"""
    if t0 <= 0: dur = 1e9                                   # t0 = 0 means "lit for the whole shot"
    k = seg(t, t0 - 0.1, t0 + 0.45) * (1 - seg(t, t0 + dur, t0 + dur + 0.4))
    if k <= 0: return
    fc = REGCOL.get(name, SAFF); fk = flag or name; ban = BANNER.get(fk)
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    c.save(); c.translate(DW / 2, DH / 2); c.scale(s, s); c.translate(-cx, -cy)
    pth = gpath(name, s)
    c.drawPath(pth, paint(fc, int(205 * k)))
    if ban:
        b_ = pth.getBounds(); img = banner_tex(fk); w_ = b_.width() * 1.04; h_ = max(b_.height() * 1.06, w_ * img.height() / img.width())
        c.save(); c.clipPath(pth, doAntiAlias=True)
        cloth(c, img, b_.centerX() - w_ / 2, b_.centerY() - h_ / 2, w_, h_, t, int(120 * k), 60, 0.03)
        c.restore()
    c.drawPath(pth, paint(lighten(fc), int(230 * k), stroke=1.2 / s))
    c.restore()
    if ban and pole:
        lo, la = flag_at or rep_point(name); x, y = to_screen(cam, lo, la)
        if -100 < x < DW + 100 and -100 < y < DH + 200:
            pole_flag(c, x, y, fk, t, seg(t, t0 + 0.1, t0 + 0.7) * (1 - seg(t, t0 + dur, t0 + dur + 0.4)), 1.0, flag_label)

def float_map(*a, **kw_):
    """map cards removed on user feedback ('map card nahi chahiye') - floating flags (hl) replace them"""
    return


_PH = {}
def photo(key):
    if key not in _PH:
        pth = next((ROOT + f"visuals/photos/{key}{ext}" for ext in (".jpg", ".png") if os.path.exists(ROOT + f"visuals/photos/{key}{ext}")), None)
        _PH[key] = sk_image(Image.open(pth).convert("RGB")) if pth else None
    return _PH[key]
def photo_card(c, key, x, y, w, h, t, k, cap="", credit="", t0=0.0, kout=0.0):
    """real photo in a thin frame: glides up + fades in, slow Ken Burns zoom, caption + credit strip"""
    img = photo(key)
    if img is None or k <= 0 or kout >= 1: return
    ke = ease_out(clamp(k)); al = int(255 * clamp(k * 1.4) * (1 - kout)); dy = (1 - ke) * 40 + kout * 30
    y += dy
    c.drawRoundRect(skia.Rect(x + 6, y + 16, x + w + 6, y + h + 16), 18, 18, paint("#000000", int(al * 0.5), blur=24))
    rrect(c, x - 8, y - 8, x + w + 8, y + h + 60, 18, "#0B1424", al)
    iw, ih = img.width(), img.height(); z = 1.0 + 0.08 * clamp((t - t0) / 8.0)
    sc = max(w / iw, h / ih) * z; sw, sh = w / sc, h / sc; sx, sy = (iw - sw) / 2, (ih - sh) / 2
    c.save(); pp = skia.Path(); pp.addRoundRect(skia.Rect(x, y, x + w, y + h), 12, 12); c.clipPath(pp, doAntiAlias=True)
    draw_img(c, img, x, y, x + w, y + h, al, src=skia.Rect(sx, sy, sx + sw, sy + sh)); c.restore()
    c.drawRoundRect(skia.Rect(x, y, x + w, y + h), 12, 12, paint("#FFFFFF", int(al * 0.18), stroke=1.2))
    if cap: text(c, cap, x + 6, y + h + 34, min(24, 24 * (w - 10) / max(1, text_w(cap, 24, FT_SEMI))), "#E5E7EB", FT_SEMI, "l", al)
    if credit: text(c, credit, x + w - 2, y + h + 54, 14, "#8A9BB0", FT_SEMI, "r", al)


# ---------------------------------------------------------------- Baladhuri at his desk (2D flat, "Aadhunik chitran")
_SCRIPT = {}
def script_line(i, w):
    """one line of flowing Arabic-like pen strokes (decorative, not real text), drawn right-to-left"""
    if (i, w) not in _SCRIPT:
        rng = np.random.default_rng(40 + i); pts = []; x = 0.0
        while x < w:
            seg_w = rng.uniform(26, 70); amp = rng.uniform(4, 12)
            for j in range(10):
                u = j / 9; pts.append((x + u * seg_w, math.sin(u * math.pi * rng.uniform(1, 3)) * amp * (1 if j % 3 else -0.6)))
            x += seg_w + rng.uniform(6, 16)
        _SCRIPT[(i, w)] = pts
    return _SCRIPT[(i, w)]

def scholar_scene(c, tv, zoom_k, write_k, cover_k=0.0, lock_k=0.0, lock_open=0.0):
    """FRONT view: scholar behind his desk writing on a page in front of him; camera starts close on the page
    (looking down, 3D tilt) and pulls back to show him (zoom_k 0..1)"""
    c.clear(hexc("#1A1410"))
    z = lerp(2.9, 1.4, ease_io(zoom_k)); px, py = 960, lerp(722, 610, ease_io(zoom_k))
    m = skia.Matrix(); m.setAll(1, 0, 0, 0, 1, 0, 0, lerp(-0.0005, 0.0, ease_io(zoom_k)), 1)
    c.save(); c.translate(960, 540); c.scale(z, z); c.concat(m); c.translate(-px, -py)
    rg = skia.GradientShader.MakeRadial(skia.Point(1250, 420), 1000, [hexc("#5A3F25"), hexc("#1A1410")], [0.0, 1.0])
    bgp = skia.Paint(); bgp.setShader(rg); c.drawRect(skia.Rect(-600, -400, 2600, 1600), bgp)
    for i in range(7):                                                                                       # arched niches
        x0 = 120 + i * 250; c.drawRect(skia.Rect(x0, 180, x0 + 150, 470), paint("#3B2A1B", 130)); c.drawOval(skia.Rect(x0, 120, x0 + 150, 240), paint("#3B2A1B", 130))
    # scholar (generic figure, front view, upright head)
    rb = skia.Path(); rb.moveTo(700, 900); rb.lineTo(770, 575); rb.quadTo(960, 520, 1150, 575); rb.lineTo(1220, 900); rb.close()
    c.drawPath(rb, paint("#2F5D50"))
    vp = skia.Path(); vp.moveTo(915, 560); vp.lineTo(960, 640); vp.lineTo(1005, 560); vp.close(); c.drawPath(vp, paint("#E6DCC8"))   # collar
    c.drawRect(skia.Rect(932, 500, 988, 565), paint("#B88A5E"))                                               # neck
    c.drawOval(skia.Rect(892, 360, 1028, 520), paint("#C99A6B"))                                              # face
    for ex in (930, 990):
        c.drawCircle(ex, 438, 6, paint("#1A1410")); c.drawLine(ex - 14, 420, ex + 14, 418, paint("#3B2F2A", 255, stroke=5, cap_round=True))   # eyes + brows
    c.drawLine(960, 445, 955, 470, paint("#8A6A4A", 255, stroke=4, cap_round=True))                           # nose
    bd = skia.Path(); bd.moveTo(895, 455); bd.quadTo(898, 560, 960, 600); bd.quadTo(1022, 560, 1025, 455)
    bd.quadTo(1000, 500, 960, 498); bd.quadTo(920, 500, 895, 455); bd.close(); c.drawPath(bd, paint("#6B5A4E"))   # beard (below the chin)
    c.drawArc(skia.Rect(926, 470, 960, 488), 20, 140, False, paint("#4E4038", 255, stroke=6, cap_round=True))
    c.drawArc(skia.Rect(960, 470, 994, 488), 20, 140, False, paint("#4E4038", 255, stroke=6, cap_round=True))    # moustache
    c.drawOval(skia.Rect(880, 300, 1040, 410), paint("#F1EBDD"))                                              # turban dome (on top)
    c.drawRoundRect(skia.Rect(884, 370, 1036, 410), 18, 18, paint("#E2D6BE"))                                  # turban band
    for k_ in range(3): c.drawLine(900 + k_ * 40, 378, 930 + k_ * 40, 404, paint("#CDBF9F", 255, stroke=3))
    # desk: top surface seen slightly from above (page lies FLAT on it) + front panel
    top = skia.Path(); top.moveTo(560, 672); top.lineTo(1360, 672); top.lineTo(1430, 762); top.lineTo(490, 762); top.close()
    c.drawPath(top, paint("#6B4429")); c.drawRect(skia.Rect(490, 762, 1430, 790), paint("#5A381F"))
    c.drawRect(skia.Rect(530, 790, 1390, 1030), paint("#4A3020"))
    for k_ in range(3): c.drawRect(skia.Rect(580 + k_ * 270, 820, 810 + k_ * 270, 990), paint("#553722"))
    pg = skia.Path(); pg.moveTo(800, 684); pg.lineTo(1120, 684); pg.lineTo(1158, 752); pg.lineTo(762, 752); pg.close()
    c.drawPath(pg, paint("#000000", 70, blur=6)); c.drawPath(pg, paint("#EADCBE")); c.drawPath(pg, paint("#B89B6A", 255, stroke=1.6))
    fl = 0.85 + 0.15 * math.sin(tv * 11) * math.sin(tv * 3.7)                                                  # oil lamp
    c.drawCircle(1290, 650, 150, paint("#FFB347", int(45 * fl), blur=60)); c.drawOval(skia.Rect(1250, 700, 1330, 726), paint("#B8862B"))
    fp = skia.Path(); fp.moveTo(1290, 650 - 30 * fl); fp.quadTo(1308, 680, 1290, 700); fp.quadTo(1272, 680, 1290, 650 - 30 * fl); c.drawPath(fp, paint("#FFD27A"))
    nL = 4; tip = None
    for i in range(nL):
        kk = clamp(write_k * nL - i)
        if kk <= 0: break
        yy = 697 + i * 14; f_ = (yy - 684) / 68; xl, xr = lerp(800, 762, f_) + 16, lerp(1120, 1158, f_) - 16
        pts = script_line(i, xr - xl); path = skia.Path(); first = True; npts = max(2, int(len(pts) * kk))
        for (x_, y_) in pts[:npts]:
            X, Y = xr - x_, yy + y_ * 0.24
            if X < xl: break
            (path.moveTo if first else path.lineTo)(X, Y); first = False; tip = (X, Y)
        c.drawPath(path, paint("#3B2414", 255, stroke=1.7, cap_round=True))
    if cover_k > 0:
        yk = 697 + 2 * 14; cw = 350 * ease_out(cover_k); rrect(c, 1140 - cw, yk - 6, 1142, yk + 6, 3, "#111827", 240)
    if lock_k > 0:
        c.save(); c.translate(960, 708); c.scale(0.4 * back(lock_k), 0.4 * back(lock_k)); lock(c, 0, -10, 90, lock_open); pill(c, "CH 4", 110, 20, 30, RED, shadow=0); c.restore()
    # hands: left holds the page, right writes with the quill (tip follows the newest stroke)
    c.drawLine(790, 620, 830, 738, paint("#2F5D50", 255, stroke=32, cap_round=True)); c.drawCircle(834, 740, 16, paint("#C99A6B"))
    tx, ty = tip if tip and write_k < 0.999 else (1060, 730)
    c.drawLine(1120, 620, tx + 18, ty + 14, paint("#2F5D50", 255, stroke=32, cap_round=True))
    c.drawCircle(tx + 14, ty + 10, 17, paint("#C99A6B"))
    qp = skia.Path(); qp.moveTo(tx, ty); qp.quadTo(tx + 14, ty - 60, tx + 52, ty - 110); qp.quadTo(tx + 22, ty - 52, tx, ty); c.drawPath(qp, paint("#F5F0E6"))
    c.restore()

# ---------------------------------------------------------------- channel page phone (3D flip + scroll), subscribe overlay, thinking man
def phone_page(c, t, cx, cy, h, k_in, scroll_k, k_out=0.0):
    """the AMRIT BORI channel page inside a phone: flips in around the Y axis (3D), scrolls, flips out"""
    img = photo("yt/page")
    if img is None or k_in <= 0 or k_out >= 1: return
    w = h * 0.47; ang = lerp(-80, 0, ease_out(k_in)) + lerp(0, 80, ease_in(k_out))
    ca = math.cos(math.radians(ang)); persp = math.sin(math.radians(ang)) * 0.0011
    al = int(255 * clamp(k_in * 2) * (1 - k_out))
    c.save(); c.translate(cx, cy)
    m = skia.Matrix(); m.setAll(ca, 0, 0, 0, 1, 0, persp, 0, 1); c.concat(m)
    c.drawRoundRect(skia.Rect(-w / 2 + 10, -h / 2 + 24, w / 2 + 10, h / 2 + 24), 46, 46, paint("#000000", int(al * 0.5), blur=30))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 46, "#050505", al); c.drawRoundRect(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), 46, 46, paint("#3A3A3A", al, stroke=3))
    sx0, sy0, sw, sh = -w / 2 + 14, -h / 2 + 14, w - 28, h - 28
    iw, ih = img.width(), img.height(); scale = sw / iw; vis = sh / scale; top = (ih - vis) * ease_io(clamp(scroll_k))
    c.save(); pp = skia.Path(); pp.addRoundRect(skia.Rect(sx0, sy0, sx0 + sw, sy0 + sh), 36, 36); c.clipPath(pp, doAntiAlias=True)
    draw_img(c, img, sx0, sy0, sx0 + sw, sy0 + sh, al, src=skia.Rect(0, top, iw, top + vis)); c.restore()
    c.drawRoundRect(skia.Rect(-38, -h / 2 + 22, 38, -h / 2 + 40), 9, 9, paint("#000000", al))
    c.restore()

_SUB = {}
def sub_overlay(c, t, t0):
    """the channel's own subscribe animation (brand/subscribe_anim.py, alpha frames) played from t0"""
    i = int((t - t0) * 60)
    if i < 0 or i >= 276: return
    pth = AB_ROOT + f"render_tmp/subscribe/f{i:04d}.png"
    if not os.path.exists(pth): return
    if pth not in _SUB:
        if len(_SUB) > 6: _SUB.clear()
        _SUB[pth] = sk_image(Image.open(pth))
    draw_img(c, _SUB[pth], 0, 0, DW, DH)

def thinker(c, x, y, s, t, k):
    """2D flat man scratching his head, thought bubble with '?'"""
    if k <= 0: return
    al = int(255 * clamp(k * 1.6)); kk = s / 100; dy = (1 - ease_out(k)) * 30
    c.save(); c.translate(x, y + dy)
    c.drawRoundRect(skia.Rect(-55 * kk, 10 * kk, 55 * kk, 170 * kk), 40 * kk, 40 * kk, paint("#4C6EF5", al))       # body
    c.drawCircle(0, -40 * kk, 48 * kk, paint("#E0B084", al))                                                  # head
    c.drawArc(skia.Rect(-48 * kk, -95 * kk, 48 * kk, -10 * kk), 180, 180, True, paint("#2B2B2B", al))         # hair
    for ex in (-16, 16): c.drawCircle(ex * kk, -40 * kk, 5 * kk, paint("#1A1A1A", al))
    c.drawLine(-12 * kk, -14 * kk, 12 * kk, -18 * kk, paint("#1A1A1A", al, stroke=4 * kk, cap_round=True))   # unsure mouth
    sc = math.sin(t * 9) * 6 * kk                                                                          # scratching arm
    c.drawLine(40 * kk, 30 * kk, 70 * kk, -30 * kk, paint("#4C6EF5", al, stroke=24 * kk, cap_round=True))
    c.drawLine(70 * kk, -30 * kk, 38 * kk + sc, -70 * kk, paint("#4C6EF5", al, stroke=22 * kk, cap_round=True))
    c.drawCircle(38 * kk + sc, -74 * kk, 14 * kk, paint("#E0B084", al))
    c.drawLine(-40 * kk, 30 * kk, -48 * kk, 120 * kk, paint("#4C6EF5", al, stroke=24 * kk, cap_round=True))
    for i, (bx, by, br) in enumerate(((-70, -100, 8), (-95, -135, 12))): c.drawCircle(bx * kk, by * kk, br * kk, paint("#F1FAEE", al))
    c.drawOval(skia.Rect(-210 * kk, -250 * kk, -60 * kk, -150 * kk), paint("#F1FAEE", al))
    text(c, "?", -135 * kk, -175 * kk, 70 * kk, "#0F1B2D", FT_BLACK, "c", al)
    c.restore()

def circle_x(c, x, y, r, k, col=RED):
    if k <= 0: return
    p_ = skia.Path(); p_.addArc(skia.Rect(x - r, y - r, x + r, y + r), -90, 360 * ease_out(seg(k, 0, 0.5)))
    c.drawPath(p_, paint(col, 255, stroke=r * 0.14, cap_round=True))
    kx = seg(k, 0.4, 1.0)
    for i, (dx, dy) in enumerate(((1, 1), (1, -1))):
        kk = ease_out(seg(kx, i * 0.4, 0.6 + i * 0.4)); q = r * 0.55
        if kk > 0: c.drawLine(x - q * dx, y - q * dy, x - q * dx + 2 * q * dx * kk, y - q * dy + 2 * q * dy * kk, paint(col, 255, stroke=r * 0.14, cap_round=True))

def chapter_card(c, lt, t0, num, ttl, dur=2.0):
    """premium chapter card: dark gradient, soft light sweep, CHAPTER 0N tracks in, title letters glide in, underline grows"""
    c.clear(hexc("#0B1220"))
    rg = skia.GradientShader.MakeRadial(skia.Point(960, 560), 900, [hexc("#1B2A44"), hexc("#0B1220")], [0.0, 1.0])
    p_ = skia.Paint(); p_.setShader(rg); c.drawRect(skia.Rect(0, 0, DW, DH), p_)
    sw = ease_io(seg(lt, 0.0, 1.4)); sx = lerp(-400, 2300, sw)
    lg = skia.GradientShader.MakeLinear([skia.Point(sx - 300, 0), skia.Point(sx + 300, 0)], [skia.ColorSetARGB(0, 255, 255, 255), skia.ColorSetARGB(28, 255, 255, 255), skia.ColorSetARGB(0, 255, 255, 255)], [0, 0.5, 1])
    p2 = skia.Paint(); p2.setShader(lg); c.drawRect(skia.Rect(0, 0, DW, DH), p2)
    z = lerp(1.04, 1.0, ease_out(seg(lt, 0, dur))); c.save(); c.translate(960, 540); c.scale(z, z); c.translate(-960, -540)
    title(c, f"CHAPTER {num:02d}", 960, 450, 36, seg(lt, 0.1, 0.8), YEL)
    title(c, ttl, 960, 580, 104, seg(lt, 0.3, 1.3), "#F1FAEE")
    w = text_w(ttl, 104) * ease_out(seg(lt, 0.9, 1.6)); c.drawRect(skia.Rect(960 - w / 2, 616, 960 + w / 2, 622), paint(RED))
    fade = seg(lt, dur - 0.25, dur); c.restore()
    if fade > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint("#0B1220", int(255 * fade)))


def conquer(c, cam, name, t, t0, dur=1.1, flag_at=None, flag_size=0.9):
    """same conquest look as the opening scene: region fills south -> north in khilafat green with a waving cloth,
    then the army plants the khilafat flag (drop + dust ring)"""
    k = ease_io(seg(t, t0, t0 + dur))
    if k > 0:
        b_ = REG[name].bounds; ys = to_screen(cam, 0, b_[1] - 0.3)[1]; ye = to_screen(cam, 0, b_[3] + 0.3)[1]; yc = lerp(ys, ye, k)
        c.save(); c.clipRect(skia.Rect(0, yc, DW, DH))
        cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
        c.save(); c.translate(DW / 2, DH / 2); c.scale(s_, s_); c.translate(-cx_, -cy_)
        pth = gpath(name, s_); c.drawPath(pth, paint(GREEN, 235)); c.drawPath(pth, paint("#BFF0D4", 230, stroke=1.2 / s_)); c.restore()
        if k < 1:
            xl = to_screen(cam, b_[0] - 0.5, 0)[0]; xr = to_screen(cam, b_[2] + 0.5, 0)[0]
            c.drawLine(xl, yc, xr, yc, paint("#BFF0D4", int(160 * (1 - k)), stroke=2))
        c.restore()
    kf = seg(t, t0 + dur * 0.7, t0 + dur + 0.6)
    if kf > 0:
        lo, la = flag_at or rep_point(name); x, y = to_screen(cam, lo, la)
        rp = seg(t, t0 + dur + 0.1, t0 + dur + 0.8)
        if 0 < rp < 1: c.drawOval(skia.Rect(x - 70 * rp, y - 18 * rp, x + 70 * rp, y + 18 * rp), paint("#E9DCC0", int(180 * (1 - rp)), stroke=3))
        c.save(); c.translate(0, (1 - ease_out(kf)) * -120); pole_flag(c, x, y, "umayyad", t, clamp(kf * 1.5), flag_size, False); c.restore()


def army_into_spain(c, cam, t, t0, dur=1.6):
    """the opening scene's army, replayed: crosses at Gibraltar, fans out across Spain (marching soldiers)"""
    ka = seg(t, t0, t0 + dur * 0.45)
    land = [to_screen(cam, -5.9, 35.2), to_screen(cam, -5.4, 36.4), to_screen(cam, -5.0, 37.4)]
    r_ = route(c, land, ease_io(ka), RED, 8, dash=False) if ka > 0 else None
    if r_ and ka < 1:
        for j in range(5):
            f_ = ease_io(ka) - j * 0.08
            if f_ > 0: sx, sy, _ = along(*r_, f_); ic_soldier(c, sx, sy - 12, 48, t + j * 0.2, "#F1FAEE", 255)
    for i, (lo, la) in enumerate(((-4.02, 39.86), (-9.14, 38.72), (-5.57, 42.6), (-0.88, 41.65))):
        kk = seg(t, t0 + dur * 0.4 + i * 0.12, t0 + dur + i * 0.1)
        if kk <= 0: continue
        r2 = route(c, [land[-1], to_screen(cam, lo, la)], ease_io(kk), RED, 6, dash=False)
        if r2 and kk < 1: sx, sy, _ = along(*r2, ease_io(kk)); ic_soldier(c, sx, sy - 12, 44, t, "#F1FAEE", 255)


def duck_soldier(c, x, y, s, duck, t, a=255, face=1):
    """2D soldier who ducks his head and raises a round shield over it (duck 0 = upright, 1 = crouched, head down)"""
    k = s / 100; d = ease_io(clamp(duck)); al = a
    body_h = lerp(70, 44, d) * k; hip_y = y - lerp(40, 26, d) * k
    lean = lerp(0, 18, d) * k * face
    for sgn in (-1, 1):                                                                         # legs (bent when crouched)
        kx = x + sgn * 12 * k; knee = (kx + sgn * 6 * k + d * 14 * k * face, y - lerp(20, 12, d) * k)
        c.drawLine(kx, hip_y, knee[0], knee[1], paint("#5B4636", al, stroke=12 * k, cap_round=True))
        c.drawLine(knee[0], knee[1], kx + sgn * 4 * k, y, paint("#5B4636", al, stroke=12 * k, cap_round=True))
    top = (x + lean, hip_y - body_h)
    c.drawLine(x, hip_y, top[0], top[1], paint("#8B2E2E", al, stroke=30 * k, cap_round=True))      # torso / tunic
    hx, hy = top[0] + lerp(0, 16, d) * k * face, top[1] - lerp(22, 6, d) * k                    # head drops forward
    c.drawCircle(hx, hy, 15 * k, paint("#C99A6B", al)); c.drawArc(skia.Rect(hx - 16 * k, hy - 19 * k, hx + 16 * k, hy + 6 * k), 180, 180, True, paint("#7A8BA3", al))
    sx, sy = hx + lerp(26, 6, d) * k * face, hy - lerp(-10, 22, d) * k                         # shield goes up over the head
    c.drawOval(skia.Rect(sx - 26 * k, sy - 22 * k, sx + 26 * k, sy + 22 * k), paint(SAFF, al)); c.drawOval(skia.Rect(sx - 26 * k, sy - 22 * k, sx + 26 * k, sy + 22 * k), paint("#7A4A1E", al, stroke=3 * k))
    c.drawCircle(sx, sy, 5 * k, paint("#7A4A1E", al))


def civilian(c, x, y, s, col, a=255, t=0.0):
    k = s / 100; bob = math.sin(t * 3 + x) * 2 * k
    c.drawRoundRect(skia.Rect(x - 16 * k, y - 50 * k + bob, x + 16 * k, y + 6 * k + bob), 12 * k, 12 * k, paint(col, a))
    c.drawCircle(x, y - 64 * k + bob, 14 * k, paint("#D9A877", a))
    for sgn in (-1, 1): c.drawLine(x + sgn * 7 * k, y + 4 * k, x + sgn * 9 * k, y + 40 * k, paint("#5B4636", a, stroke=8 * k, cap_round=True))

def skirmish(c, cx, cy, t, k, n=4):
    """two lines of 2D soldiers charge and collide; sparks fly where they meet (no sword icons)"""
    if k <= 0: return
    meet = ease_out(clamp(k * 1.6))
    for j in range(n):
        y = cy + (j - (n - 1) / 2) * 62
        ic_soldier(c, cx - 260 + 205 * meet - (j % 2) * 26, y, 60, t * 9 + j, "#F1FAEE", 255)            # Arab side
        ic_soldier(c, cx + 260 - 205 * meet + (j % 2) * 26, y, 60, t * 9 + j + 1, "#E8B4A0", 255)        # defenders
        if meet > 0.85:
            ph = (t * 3 + j * 0.37) % 1
            clash(c, cx, y - 20, ph, 0.45)

# ---------------------------------------------------------------- premium text animation
def title(c, s, x, y, size, k, col="#F1FAEE", a=255):
    """per-letter reveal: each glyph fades in and glides up with a soft stagger; tracking settles from wide to normal"""
    if k <= 0: return
    f = font(FT_BLACK, size); n = max(1, len(s)); trk = size * 0.06 * (1 - ease_out(clamp(k * 1.3)))
    ws = [f.measureText(ch) for ch in s]; total = sum(ws) + trk * (n - 1); xx = x - total / 2
    sh = paint("#000000", int(a * 0.45 * clamp(k * 1.5)), blur=size * 0.08)
    for i, ch in enumerate(s):
        kk = ease_out(seg(k, i / n * 0.45, i / n * 0.45 + 0.55))
        if kk > 0 and ch != " ":
            dy = (1 - kk) * size * 0.35
            c.drawString(ch, xx + size * 0.03, y + dy + size * 0.06, f, sh)
            c.drawString(ch, xx, y + dy, f, paint(col, int(a * kk)))
        xx += ws[i] + trk

def label(c, s, x, y, k, size=30, col="#F1FAEE", bgc="#0B1424", border=None):
    """glass pill: fades + glides up, accent dot in the region colour (no heavy yellow border)"""
    if k <= 0: return
    ke = ease_out(clamp(k)); al = int(255 * clamp(k * 1.6)); w = text_w(s, size, FT_BLACK) + 44; dy = (1 - ke) * 16
    h0, h1 = y - size * 0.95 + dy, y + size * 0.5 + dy
    c.drawRoundRect(skia.Rect(x - w / 2 + 2, h0 + 6, x + w / 2 + 2, h1 + 6), 12, 12, paint("#000000", int(al * 0.35), blur=10))
    rrect(c, x - w / 2, h0, x + w / 2, h1, 12, bgc, int(al * 0.88))
    c.drawRoundRect(skia.Rect(x - w / 2, h0, x + w / 2, h1), 12, 12, paint("#FFFFFF", int(al * 0.12), stroke=1.2))
    c.drawCircle(x - w / 2 + 16, (h0 + h1) / 2, 5, paint(border or YEL, al))
    text(c, s, x + 8, y + size * 0.12 + dy, size, col, FT_BLACK, "c", al)

def stat_card(c, x, y, w, h, big, lab, k, col=YEL, tag=None, sub=None, a=255):
    """smooth premium stat card: glides up + fades, thin border, number tracks in"""
    if k <= 0: return
    ke = ease_out(clamp(k)); al = int(a * clamp(k * 1.4)); dy = (1 - ke) * 30
    c.save(); c.translate(0, dy)
    c.drawRoundRect(skia.Rect(x + 4, y + 12, x + w + 4, y + h + 12), 22, 22, paint("#000000", int(al * 0.45), blur=22))
    rrect(c, x, y, x + w, y + h, 22, "#111B2E", al)
    c.drawRoundRect(skia.Rect(x, y, x + w, y + h), 22, 22, paint("#FFFFFF", int(al * 0.10), stroke=1.2))
    c.drawRect(skia.Rect(x + 28, y + h * 0.18, x + 34, y + h * 0.82), paint(col, al))
    fit = lambda s_, size, fp: min(size, size * (w - 70) / max(1, text_w(s_, size, fp)))
    bs = fit(big, h * 0.36, FT_BLACK); c.save(); c.clipRect(skia.Rect(x, y, x + w, y + h * 0.6))
    text(c, big, x + w / 2 + 6, y + h * 0.52 + (1 - ease_out(seg(k, 0.1, 0.8))) * h * 0.25, bs, col, FT_BLACK, "c", al); c.restore()
    text(c, lab, x + w / 2 + 6, y + h * 0.77, fit(lab, h * 0.11, FT_SEMI), "#E5E7EB", FT_SEMI, "c", int(al * ease_out(seg(k, 0.3, 1.0))))
    if sub: text(c, sub, x + w / 2 + 6, y + h * 0.91, fit(sub, h * 0.08, FT_SEMI), PAL["muted"], FT_SEMI, "c", int(al * ease_out(seg(k, 0.4, 1.0))))
    c.restore()

def tag_note(c, s, x, y, k, col="#9FB0C6"):
    if k <= 0: return
    text(c, s, x, y, 20, col, FT_SEMI, "c", int(220 * clamp(k * 1.5)))

def arrow(c, p0, p1, k, col=YEL, w=7, bend=0.18, army=None):
    """curved arrow; army arrows (any colour but yellow) carry a column of marching 2D soldiers while advancing"""
    if k <= 0: return
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    nx, ny = -(p1[1] - p0[1]), (p1[0] - p0[0])
    r_ = route(c, [p0, (mx + nx * bend, my + ny * bend), p1], ease_out(k), col, w, dash=False)
    if (army if army is not None else col != YEL) and r_ and k < 0.999:
        L = r_[1]; n = max(2, min(6, int(L / 60))); size = 30 + w * 3
        for q in range(n):
            f_ = ease_out(k) - q * 0.06
            if f_ > 0.02: sx, sy, _ = along(*r_, f_); ic_soldier(c, sx, sy - size * 0.25, size, k * 9 + q * 0.4, "#F1FAEE", 255)

def clash(c, x, y, k, s=1.0):
    """battle impact: white flash, yellow sparks, crossed swords"""
    if k <= 0 or k >= 1: return
    for r in range(10):
        an = r / 10 * math.tau; d0 = (18 + 70 * ease_out(k)) * s
        c.drawLine(x + d0 * math.cos(an), y + d0 * math.sin(an), x + (d0 + 24 * s) * math.cos(an), y + (d0 + 24 * s) * math.sin(an), paint(YEL, int(255 * (1 - k)), stroke=5 * s, cap_round=True))
    c.drawCircle(x, y, (28 + 40 * k) * s, paint("#FFFFFF", int(160 * (1 - k)), blur=12))

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
        ok = clamp(unlocked - i)
        lock(c, 0, -20, 90, ok, GREEN if ok > 0.5 else (RED if hot else YEL))
        if ok > 0.5: c.drawRoundRect(skia.Rect(-160, -150, 160, 150), 24, 24, paint(GREEN, int(255 * (ok - 0.5) * 2), stroke=4))
        lab = labels[i]; words = lab.split()
        if text_w(lab, 32) > 290 and len(words) > 1:
            h_ = (len(words) + 1) // 2; l1, l2 = " ".join(words[:h_]), " ".join(words[h_:])
            fs = min(30, 290 * 30 / max(text_w(l1, 30), text_w(l2, 30)))
            text(c, l1, 0, 92, fs, "#F1FAEE", FT_BLACK, "c"); text(c, l2, 0, 92 + fs * 1.15, fs, "#F1FAEE", FT_BLACK, "c")
        else:
            text(c, lab, 0, 110, min(34, 34 * 290 / max(1, text_w(lab, 34))), "#F1FAEE", FT_BLACK, "c")
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
    tv = vt_now(t)                                    # video time: keeps running through the hold after this line
    HP = ue(u_spain) - 0.2                            # flag planting lands right as the line ends (no pause)
    cam = fly((-4.0, 39.5, 26.0), IB_CAM, ease_io(seg(t, 0, 3.0)))
    bg(c, cam)
    k_conq = ease_io(seg(tv, vo_to_video(kw(u_spain, "paanch") - 0.1), HP + 0.5))           # south -> north conquest sweep
    hl(c, cam, "iberia", t, 0.25, dur=max(0.1, kw(u_spain, "paanch") + 0.6 - 0.25))   # Visigoth Spain before the conquest
    if k_conq > 0:
        ys = to_screen(cam, -4, 35.8)[1]; ye = to_screen(cam, -4, 44.2)[1]; yc = lerp(ys, ye, k_conq)
        c.save(); c.clipRect(skia.Rect(0, yc, DW, DH))
        cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
        c.save(); c.translate(DW / 2, DH / 2); c.scale(s_, s_); c.translate(-cx_, -cy_)
        pth = gpath("iberia", s_); c.drawPath(pth, paint(GREEN, 225))
        b_ = pth.getBounds(); img = banner_tex("umayyad"); w_ = b_.width() * 1.04; h_ = max(b_.height() * 1.06, w_ * img.height() / img.width())
        c.save(); c.clipPath(pth, doAntiAlias=True); cloth(c, img, b_.centerX() - w_ / 2, b_.centerY() - h_ / 2, w_, h_, tv, 110, 60, 0.03); c.restore()
        c.drawPath(pth, paint("#BFF0D4", 220, stroke=1.2 / s_)); c.restore()
        xl = to_screen(cam, -9.8, 40)[0]; xr = to_screen(cam, 3.6, 40)[0]
        c.drawLine(xl, yc, xr, yc, paint("#BFF0D4", int(140 * (1 - k_conq)), stroke=2))
        c.restore()
    kp = seg(t, kw(u_spain, "paanch") - 0.15, kw(u_spain, "paanch") + 0.7)
    title(c, "5 SAAL", 330, 470, 120, kp, YEL)
    title(c, "lagbhag poora Spain", 330, 530, 34, seg(t, kw(u_spain, "Spain") - 0.3, kw(u_spain, "Spain") + 0.5), "#E5E7EB")
    photo_card(c, "guarrazar", 1440, 150, 300, 430, t, seg(t, kw(u_spain, "Spain") - 0.4, kw(u_spain, "Spain") + 0.3), "Visigoth Spain ka shahi khazana",
               "Guarrazar, 7vi sadi · Public domain, Wikimedia Commons", t0=kw(u_spain, "Spain"))
    timeline(c, t, lerp(711, 716, k_conq), seg(t, 0.2, 0.7), span=(708, 720), step=1, big_every=1, start=711,
             bracket=(711, 716, "5 SAAL", seg(tv, HP - 0.3, HP + 0.3)))
    # "Ek fauj ne...": Umayyad army (Tariq ibn Ziyad, 711) crosses at Gibraltar, then fans out across Spain
    ka = seg(t, kw(u_spain, "fauj") - 0.3, kw(u_spain, "paanch") + 0.2)
    land = [to_screen(cam, -5.9, 35.2), to_screen(cam, -5.4, 36.4), to_screen(cam, -5.0, 37.4)]
    r_ = route(c, land, ease_io(ka), RED, 9, dash=False) if ka > 0 else None
    if r_:
        pm, L = r_
        for j in range(7):
            f_ = ease_io(ka) - j * 0.07
            if f_ > 0:
                sx, sy, _ = along(pm, L, f_); ic_soldier(c, sx + (j % 2) * 22 - 11, sy - 14, 62, tv + j * 0.2, "#F1FAEE", 255)
    TARGETS = [(-4.02, 39.86, "TOLEDO"), (-9.14, 38.72, None), (-5.57, 42.6, None), (-0.88, 41.65, None)]
    for i, (lo, la, nm) in enumerate(TARGETS):
        kk = seg(tv, vo_to_video(kw(u_spain, "paanch")) + i * 0.25, HP + 0.2 + i * 0.15)
        if kk <= 0: continue
        r2 = route(c, [land[-1], to_screen(cam, lo, la)], ease_io(kk), RED, 7, dash=False)
        if r2 and kk < 1:
            sx, sy, _ = along(*r2, ease_io(kk)); ic_soldier(c, sx, sy - 14, 54, tv, "#F1FAEE", 255)
    label(c, "UMAYYAD FAUJ · TARIQ IBN ZIYAD", *to_screen(cam, -9.6, 35.6), seg(t, kw(u_spain, "fauj") - 0.1, kw(u_spain, "fauj") + 0.4), 26, border=RED)
    tag_note(c, "711 CE", *to_screen(cam, -9.6, 34.9), seg(t, kw(u_spain, "fauj"), kw(u_spain, "fauj") + 0.4), "#E5E7EB")
    # the army plants the (pure white) Umayyad banner at Toledo during the silent beat
    kf = seg(tv, HP - 0.35, HP + 0.45)
    if kf > 0:
        x, y = to_screen(cam, -4.02, 39.86)
        rp = seg(tv, HP + 0.05, HP + 0.8)
        if 0 < rp < 1: c.drawOval(skia.Rect(x - 90 * rp, y - 22 * rp, x + 90 * rp, y + 22 * rp), paint("#E9DCC0", int(180 * (1 - rp)), stroke=4))
        c.save(); c.translate(0, (1 - ease_out(kf)) * -160); pole_flag(c, x, y, "umayyad", tv, clamp(kf * 1.5), 1.25, False); c.restore()
        label(c, "UMAYYAD KA JHANDA GADA", x + 40, y + 70, seg(tv, HP + 0.2, HP + 0.6), 26, border="#F4F1EA")
    SFX_MARK(kw(u_spain, "fauj") - 0.2, "whoosh_long", -18); SFX_MARK(HP + 0.05, "stamp", -14); SFX_MARK(HP + 0.05, "boom", -20)
    footnote(c, "Map: Natural Earth · andaazan seema")
    SFX_MARK(0.3, "hit", -16)

@shot(vin(u_wahi), vin(u_lekin))
def s02(c, t):
    k = seg(t, vin(u_wahi), vin(u_wahi) + 2.4)
    cam = fly(IB_CAM, W_CAM, ease_io(k))
    bg(c, cam)
    draw_region(c, cam, "caliph", GREEN, int(215 * ease_out(seg(t, vin(u_wahi) + 0.4, vin(u_wahi) + 2.2))), stroke="#7CE0A8")
    hl(c, cam, "caliph", t, kw(u_wahi, "khilafat"), flag_at=(28.0, 28.5))           # the rulers' banner over their whole realm
    hl(c, cam, "c_west", t, kw(u_wahi, "Atlantic"))
    title(c, "UMAYYAD KHILAFAT", 960, 170, 64, seg(t, vin(u_wahi) + 1.0, vin(u_wahi) + 1.6), "#F1FAEE")
    tag_note(c, "andaazan naksha, c. 740 CE", 960, 210, seg(t, vin(u_wahi) + 1.4, vin(u_wahi) + 2.0))
    for key, word, side in (("atlantic", "Atlantic", -1),):
        kk = seg(t, kw(u_wahi, word), kw(u_wahi, word) + 0.4)
        x, y = S(cam, key); label(c, word.upper(), x, y - 30, kk, 28)
    hl(c, cam, "centralasia", t, kw(u_wahi, "Central Asia"), pole=False)
    photo_card(c, "umayyad_mosque", 1300, 560, 520, 300, t, seg(t, vin(u_wahi) + 0.3, vin(u_wahi) + 1.0), "Umayyad Masjid, Damascus (khilafat ki rajdhani)",
               "Photo: Bernard Gagnon · CC BY-SA 3.0 · Wikimedia Commons", t0=vin(u_wahi))
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
    photo_card(c, "banbhore", 90, 560, 520, 290, t, seg(t, kw(u_lekin, "Hindustan") - 0.2, kw(u_lekin, "Hindustan") + 0.5), "Banbhore, Sindh: jise Debal maana jaata hai",
               "Photo: Engr.aly · CC BY-SA 4.0 · Wikimedia Commons", t0=kw(u_lekin, "Hindustan"), kout=seg(t, kw(u_lekin, "naya shehar") - 0.5, kw(u_lekin, "naya shehar")))
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
        draw_map(c, WM, cam, {}, int(255 * kL)); draw_region(c, cam, "iberia", REGCOL["iberia"], int(220 * kL))      # Visigoth Spain
        t0 = vin(u_jo) + 0.15                                                                                        # the conquest, replayed
        conquer(c, cam, "iberia", t, t0 + 0.6, 1.0, flag_at=(-4.02, 39.86), flag_size=0.9)
        army_into_spain(c, cam, t, t0, 1.4)
        c.restore()
        SFX_MARK(t0, "whoosh_long", -20); SFX_MARK(t0 + 1.7, "stamp", -18)
        text(c, "SPAIN: JEET", 520, 790 + (1 - kL) * 60, 46, "#F1FAEE", FT_BLACK, "c", int(255 * kL))
    if kR > 0:
        fort(c, 1400, 470, 170, 1.0, a=int(255 * kR))
        # "sar chhupane ki surakshit jagah": soldiers duck their heads under shields and hurry into the fort
        t1 = kw(u_jo, "sar"); gate = (1400, 560)
        for j in range(6):
            side = -1 if j % 2 == 0 else 1; row = j // 2
            x_start = 1400 + side * (330 - row * 40); y_ = 700 - row * 18
            kk = seg(t, t1 - 0.3 + j * 0.12, t1 + 1.6 + j * 0.12)
            x = lerp(x_start, gate[0] + side * 30, ease_in_out(kk) if False else ease_io(kk)); yy = lerp(y_, gate[1] + 70, ease_io(kk))
            duck = seg(t, t1 - 0.2 + j * 0.08, t1 + 0.3 + j * 0.08)
            al = int(255 * kR * (1 - seg(kk, 0.88, 1.0)))
            if al > 0: duck_soldier(c, x, yy, 100, duck, t, al, face=-side)
        kq = seg(t, kw(u_jo, "surakshit") - 0.1, kw(u_jo, "surakshit") + 0.4)
        if kq > 0: ic_question(c, 1640, 290, 80 * back(kq), int(255 * clamp(kq * 1.5)), YEL)
        text(c, "SINDH: SURAKSHIT JAGAH?", 1400, 790, 42, "#F1FAEE", FT_BLACK, "c", int(255 * kR))
    SFX_MARK(kw(u_jo, "yahan"), "pop", -22); SFX_MARK(kw(u_jo, "sar") - 0.2, "drag", -20)

@shot(vin(u_aur), vin(u_iske))
def s06(c, t):
    tv = vt_now(t); HPW = vo_to_video(vin(u_wo) - 0.02)          # end of the silent beat after "khud likha hai"
    zk = seg(tv, vo_to_video(kw(u_ye, "itihaskar") - 0.3), HPW)     # 3D pull-back from the page to the scholar
    wk = seg(tv, vo_to_video(vin(u_aur)), HPW - 0.2)
    scholar_scene(c, tv, zk, wk, cover_k=seg(t, kw(u_wo, "line") - 0.1, kw(u_wo, "line") + 0.5),
                  lock_k=seg(t, kw(u_wo, "dikhaunga") - 0.3, kw(u_wo, "dikhaunga") + 0.3))
    kl = seg(tv, HPW - 0.8, HPW - 0.2)
    if kl > 0:
        label(c, "AL-BALADHURI · 9vi SADI", 330, 210, kl, 30, border="#E9C46A")
        tag_note(c, "Aadhunik chitran · 'Futuh al-Buldan' ka lekhak", 330, 250, kl, "#E5E7EB")
    if t > vin(u_pehle):
        title(c, "PEHLE:", 330, 430, 54, seg(t, vin(u_pehle), vin(u_pehle) + 0.5), YEL)
        title(c, "YE NAUBAT", 330, 500, 54, seg(t, vin(u_pehle) + 0.15, vin(u_pehle) + 0.65), YEL)
        title(c, "AAYI KYUN?", 330, 570, 54, seg(t, vin(u_pehle) + 0.3, vin(u_pehle) + 0.8), YEL)
    SFX_MARK(us(u_aur), "paper", -20); SFX_MARK(kw(u_wo, "dikhaunga"), "lock", -18); SFX_MARK(kw(u_ye, "itihaskar") - 0.3, "whoosh_long", -20)

@shot(vin(u_iske), HOSTSEG["H1"][0])
def s07(c, t):
    c.clear(hexc(NAVY))
    slots(c, t, 0, seg(t, vin(u_iske), vin(u_iske) + 1.2), 520, red4=seg(t, kw(u_chautha, "chautha") - 0.1, kw(u_chautha, "chautha") + 0.4))
    title(c, "4 RAAZ", 960, 230, 80, seg(t, vin(u_iske), vin(u_iske) + 0.5), YEL)
    kt = seg(vt_now(t), vo_to_video(kw(u_chautha, "log") - 0.3), vo_to_video(kw(u_chautha, "log") + 0.2))
    if kt > 0:
        dim(c, 225 * kt); thinker(c, 780, 600, 160, vt_now(t), kt)
        circle_x(c, 1200, 600, 150, seg(vt_now(t), vo_to_video(kw(u_chautha, "galat") - 0.1), vo_to_video(kw(u_chautha, "galat")) + 0.7))
        title(c, "ZYADATAR LOG GALAT SAMAJHTE HAIN", 960, 900 - 40, 44, kt, "#F1FAEE")
    VH = vo_to_video(HOSTSEG["H1"][0] - 0.06); fade = seg(vt_now(t), VH - 0.35, VH)
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

HOSTS.append((HOSTSEG["H1"][0], vin(u_632)))
@shot(HOSTSEG["H1"][0], vin(u_632), "cut")
def h1(c, t):
    host_frame(c, "H1", t)
    u_y = U("Yahan wo itihaas"); u_n = U("Naye ho toh")
    phone_page(c, t, 1560, 540, 900, seg(t, kw(u_namaste, "AMRIT") - 0.6, kw(u_namaste, "AMRIT") + 0.2), seg(t, us(u_y) + 0.2, ue(u_y) - 0.1),
               seg(t, kw(u_n, "subscribe") - 0.5, kw(u_n, "subscribe") - 0.1))
    sub_overlay(c, t, kw(u_n, "subscribe") - 0.6)
    SFX_MARK(kw(U("Naye ho toh"), "subscribe") + 0.9, "pop", -20)

# ---- CHAPTER 1 -------------------------------------------------------------------------------------
CH_GAP = 2.0                     # silent chapter card (user: "animation hone ke baad thoda ruk ke bolna")
GAPS = []                        # (VO time P, seconds, kind "ch"/"hold", chapter index)
def hold(P, dur):
    """silent beat after a big animation: VO pauses, the shot keeps animating on video time (CUR_T)"""
    GAPS.append((P, dur, "hold", 0))
def chapter(num, ttl, unit):
    """chapter card plays in an inserted silent gap before `unit`"""
    GAPS.append((vin(unit), CH_GAP, "ch", num - 1))

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
    # "inteqaal" (passing away) shown symbolically, no human figure: a lamp over Medina slowly goes out, smoke rises, light fades
    ti = kw(u_pai, "inteqaal"); kin = seg(t, vin(u_pai), vin(u_pai) + 0.5); kout = ease_io(seg(t, ti - 0.2, ti + 0.9))
    if kin > 0:
        x, y = S(cam, "medina"); lx, ly = x + 330, y - 110
        glow = (1 - kout) * (0.85 + 0.15 * math.sin(t * 9) * math.sin(t * 3.1))
        c.drawCircle(lx, ly - 40, 220, paint("#FFC870", int(80 * kin * glow), blur=70))
        c.drawCircle(x, y, 120, paint("#FFF1C1", int(60 * kin * glow), blur=40))
        c.drawOval(skia.Rect(lx - 70, ly + 10, lx + 70, ly + 48), paint("#B8862B", int(255 * kin))); c.drawOval(skia.Rect(lx - 46, ly + 2, lx + 46, ly + 22), paint("#8A6420", int(255 * kin)))
        fh = 70 * (1 - kout) * (0.9 + 0.1 * math.sin(t * 13))
        if fh > 2:
            fp = skia.Path(); fp.moveTo(lx, ly + 4 - fh); fp.quadTo(lx + 22, ly - fh * 0.3, lx, ly + 6); fp.quadTo(lx - 22, ly - fh * 0.3, lx, ly + 4 - fh)
            c.drawPath(fp, paint("#FFD27A", int(255 * kin))); c.drawCircle(lx, ly - fh * 0.25, fh * 0.18, paint("#FFF6D8", int(220 * kin)))
        ks = seg(t, ti + 0.5, ti + 2.0)                                                              # smoke after the flame goes out
        for j in range(4):
            u = (ks * 1.3 - j * 0.18)
            if 0 < u < 1:
                sp = skia.Path(); sx0 = lx; sy0 = ly
                sp.moveTo(sx0, sy0)
                for q in range(1, 9):
                    v = q / 8 * u; sp.lineTo(sx0 + math.sin(v * 9 + j + t * 1.5) * 18 * v, sy0 - 170 * v)
                c.drawPath(sp, paint("#C9D1DC", int(150 * (1 - u)), stroke=5, cap_round=True, blur=2))
        dim(c, 90 * kout)
        # the real place: the Green Dome over his grave in Masjid-e-Nabawi (photo, no depiction of any person)
        photo_card(c, "green_dome", 640, 250, 640, 400, t, seg(t, ti - 0.1, ti + 0.6), "Hara Gumbad, Masjid-e-Nabawi, Madina",
                   "Wikimedia Commons (credit: PHOTO_CREDITS)", t0=ti)
    photo_card(c, "prophet_ai", 90, 190, 520, 416, t, seg(t, kw(u_pai, "Paigambar") - 0.2, kw(u_pai, "Paigambar") + 0.5),
               "AI CHITRAN · PRATIK (asli tasveer nahi)", "Channel dwara di gayi AI image", t0=us(u_pai))
    photo_card(c, "nabawi", 1260, 170, 560, 330, t, seg(t, kw(u_pai, "Paigambar") - 0.2, kw(u_pai, "Paigambar") + 0.5), "Masjid-e-Nabawi, Madina",
               "Wikimedia Commons (credit: PHOTO_CREDITS)", t0=us(u_pai), kout=seg(t, kw(u_pai, "inteqaal") - 0.3, kw(u_pai, "inteqaal")))
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
    photo_card(c, "umayyad_coin", 120, 300, 300, 300, t, seg(t, kw(u_661, "Umayyad") - 0.2, kw(u_661, "Umayyad") + 0.5), "Umayyad sone ka dinar (695)",
               "Khalifa Abd al-Malik · Public domain · Wikimedia Commons", t0=kw(u_661, "Umayyad"))
    hl(c, cam, "syria", t, kw(u_raj, "Rajdhani") + 0.3, flag_label=False)
    photo_card(c, "umayyad_mosque", 1280, 420, 540, 310, t, seg(t, kw(U("Damascus."), "Damascus") - 0.1, kw(U("Damascus."), "Damascus") + 0.5), "Umayyad Masjid, Damascus",
               "Photo: Bernard Gagnon · CC BY-SA 3.0 · Wikimedia Commons", t0=us(U("Damascus.")))
    float_map(c, t, kw(U("Damascus."), "Damascus"), "syria", "DAMASCUS · 661", "Sham (Syria), andaazan", 1400, 520, 420, 320, fill=GREEN, pad=0.6)

@shot(vin(u_charam), vin(u_teen))
def s11(c, t):
    bg(c, W_CAM); draw_region(c, W_CAM, "caliph", GREEN, 200, stroke="#7CE0A8")
    hl(c, W_CAM, "caliph", t, kw(u_charam, "saamrajya"), flag_at=(28.0, 28.5))
    k = seg(t, kw(u_charam, "ek crore") - 0.2, kw(u_charam, "ek crore") + 1.2)
    v = lerp(0, 1.1, ease_out(k))
    if k > 0:
        title(c, f"{v:.1f} CRORE+ km²", 400, 790, 78, seg(t, kw(u_charam, "ek crore") - 0.3, kw(u_charam, "ek crore") + 0.4), YEL)
        title(c, "Umayyad khilafat, charam par", 400, 840, 30, seg(t, kw(u_charam, "ek crore"), kw(u_charam, "ek crore") + 0.6), "#E5E7EB")
        tag_note(c, "Wikipedia: 1.1-1.5 crore km²", 400, 875, seg(t, kw(u_charam, "ek crore") + 0.3, kw(u_charam, "ek crore") + 0.9))
    SFX_MARK(kw(u_charam, "ek crore"), "count", -22)

CONT = [("ASIA", (62.0, 42.0), "Asia"), ("AFRICA", (10.0, 24.0), "Africa"), ("EUROPE", (-4.0, 44.0), "Europe")]
@shot(vin(u_teen), vin(u_711))
def s12(c, t):
    bg(c, W_CAM); draw_region(c, W_CAM, "caliph", GREEN, 200, stroke="#7CE0A8")
    for nm, ll, word in CONT:
        u_aae = U("Asia, Africa")
        hl(c, W_CAM, {"ASIA": "c_asia", "AFRICA": "c_africa", "EUROPE": "c_europe"}[nm], t, kw(u_aae, word), YEL, "#5FD39A", pole=False)
        x, y = to_screen(W_CAM, *ll); label(c, nm, x, y, seg(t, kw(u_aae, word) - 0.1, kw(u_aae, word) + 0.3), 40, border=REGCOL[{"ASIA": "c_asia", "AFRICA": "c_africa", "EUROPE": "c_europe"}[nm]])
    title(c, "TEEN MAHADWEEP", 960, 170, 60, seg(t, vin(u_teen), vin(u_teen) + 0.5), YEL)

@shot(vin(u_711), vin(u_gir))
def s13(c, t):
    bg(c, W_CAM); draw_region(c, W_CAM, "caliph", GREEN, 110)
    k = seg(t, vin(u_711), us(u_sirf) + 0.8)
    timeline(c, t, lerp(632, 711, ease_io(k)), 1.0, span=(620, 780))
    stat_card(c, 1380, 140, 400, 220, "79 SAAL", "632 se 711", seg(t, kw(u_sirf, "79") - 0.1, kw(u_sirf, "79") + 0.4), YEL)
    src = S(W_CAM, "damascus")
    for j_, (dst, bend, uu, word, nm) in enumerate(((S(W_CAM, "spain"), 0.2, u_ek, "Spain", "HAMLA 1 · SPAIN"), (S(W_CAM, "sindh"), -0.2, u_doo, "Sindh", "HAMLA 2 · SINDH"))):
        kk = seg(t, kw(u_sirf, "do hamle") - 0.2 + j_ * 0.15, kw(uu, word) + 0.3)
        if kk <= 0: continue
        mx, my = (src[0] + dst[0]) / 2 - (dst[1] - src[1]) * bend, (src[1] + dst[1]) / 2 + (dst[0] - src[0]) * bend
        r_ = route(c, [src, (mx, my), dst], ease_io(kk), RED, 9, dash=False)
        if r_ and kk < 1:
            for q in range(5):
                f_ = ease_io(kk) - q * 0.05
                if f_ > 0: sx, sy, _ = along(*r_, f_); ic_soldier(c, sx, sy - 12, 40, t + q * 0.3, "#F1FAEE", 255)
        kb = seg(t, kw(uu, word) + 0.25, kw(uu, word) + 0.9)
        if 0 < kb < 1:                                          # clash burst on arrival
            for r in range(10):
                an = r / 10 * math.tau; d0 = 20 + 70 * ease_out(kb)
                c.drawLine(dst[0] + d0 * math.cos(an), dst[1] + d0 * math.sin(an), dst[0] + (d0 + 26) * math.cos(an), dst[1] + (d0 + 26) * math.sin(an), paint(YEL, int(255 * (1 - kb)), stroke=5, cap_round=True))
            c.drawCircle(dst[0], dst[1], 30 + 40 * kb, paint("#FFFFFF", int(160 * (1 - kb)), blur=12))
        if kb > 0: swords(c, dst[0], dst[1] - 70, 46, seg(t, kw(uu, word) + 0.25, kw(uu, word) + 0.6), "#F1FAEE")
        label(c, nm, dst[0] + (-60 if j_ == 0 else 60), dst[1] + 70, seg(t, kw(uu, word) + 0.2, kw(uu, word) + 0.5), 26, border=RED)
        SFX_MARK(kw(uu, word) + 0.25, "boom", -20)
    title(c, "EK SAAL · DO HAMLE", 960, 170, 56, seg(t, kw(u_sirf, "do hamle") - 0.2, kw(u_sirf, "do hamle") + 0.5), "#F1FAEE") if t < kw(u_ek, "Spain") + 2 else None
    conquer(c, W_CAM, "iberia", t, kw(u_ek, "Spain") + 0.2, 0.9, flag_at=(-4.02, 39.86), flag_size=0.75)
    conquer(c, W_CAM, "sindh", t, kw(u_doo, "Sindh") - 0.05, 0.6, flag_at=(68.6, 26.4), flag_size=0.75)
    SFX_MARK(kw(u_ek, "Spain") + 1.2, "stamp", -18); SFX_MARK(kw(u_doo, "Sindh") + 1.2, "stamp", -18)
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
    draw_region(c, cam, "caliph", GREEN, 150)
    conquer(c, cam, "iberia", t, kw(u_ek, "Spain") + 0.2, 0.9, flag_at=(-4.02, 39.86), flag_size=0.75)      # planted flags stay up
    conquer(c, cam, "sindh", t, kw(u_doo, "Sindh") - 0.05, 0.6, flag_at=(68.6, 26.4), flag_size=0.75)
    hl(c, cam, "sindh", t, kw(u_ab, "Sindh"), YEL, pole=False)
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

# ======================================================================= helpers for the chapters
PL.update(dict(oman=(57.5, 23.0), debal2=(67.4, 24.7), aror=(68.95, 27.7), multan=(71.47, 30.2), kufa=(44.4, 32.03),
               basra=(47.8, 30.5), mosul=(43.13, 36.34), gujarat=(71.5, 22.6), rajasthan=(73.8, 26.6), kannauj=(79.92, 27.05),
               makran=(63.5, 26.0), indus=(69.8, 28.6), brahmanabad=(68.75, 25.88)))
INDUS = [(74.5, 35.6), (72.8, 34.0), (71.6, 33.0), (71.0, 31.0), (70.6, 29.0), (69.4, 28.0), (68.4, 26.8), (68.3, 25.4), (67.9, 24.6), (67.4, 24.0)]
DOCS = {}
def load_docs():
    if DOCS: return
    d = ROOT + "visuals/docs/"
    for f in os.listdir(d):
        if f.endswith(".json") and not f.startswith("jobs"):
            k = f[:-5]; j = json.load(open(d + f)); im = Image.open(d + k + ".png").convert("RGBA")
            DOCS[k] = (sk_image(im), im.size, [[(l["x0"], l["y"], l["x1"], l["h"]) for l in L] for L in j["lines"] if L], j["url"].replace("https://", ""))

def doc(c, key, x0, y0, w, h, t, k, hl_t0, hl_dur=1.2, focus=0):
    """real Wikipedia passage in a browser frame; yellow highlighter sweeps the key line(s) from hl_t0"""
    if k <= 0: return
    load_docs(); img, (iw, ih), lines, url = DOCS[key]; al = int(255 * clamp(k * 1.5)); dy = (1 - ease_out(k)) * 70
    y0 += dy; bar = 54
    rrect(c, x0, y0, x0 + w, y0 + h, 18, "#FFFFFF", al, shadow=28)
    c.save(); c.clipRect(skia.Rect(x0, y0, x0 + w, y0 + bar)); c.drawRoundRect(skia.Rect(x0, y0, x0 + w, y0 + bar + 20), 18, 18, paint("#E7EAF0", al)); c.restore()
    for i, col in enumerate(("#FF5F57", "#FEBC2E", "#28C840")): c.drawCircle(x0 + 30 + i * 26, y0 + bar / 2, 8, paint(col, al))
    rrect(c, x0 + 120, y0 + 12, x0 + w - 24, y0 + bar - 12, 15, "#FFFFFF", al)
    text(c, url if len(url) < 64 else url[:61] + "...", x0 + 140, y0 + bar / 2 + 9, 21, "#3C4656", FT_SEMI, "l", al)
    vw, vh = w, h - bar; s = vw / iw
    L = lines[focus] if lines else [(0, ih / 2, 1, 1)]; fy = (L[0][1] + L[-1][1] + L[-1][3]) / 2
    ty = y0 + bar + (vh - ih * s) / 2 if ih * s <= vh else max(y0 + bar + vh - ih * s, min(y0 + bar, y0 + bar + vh / 2 - fy * s))
    c.save(); c.clipRect(skia.Rect(x0, y0 + bar, x0 + vw, y0 + h)); c.translate(x0, ty); c.scale(s, s)
    draw_img(c, img, 0, 0, iw, ih, al)
    for li, Ls in enumerate(lines):
        n = len(Ls)
        for i, (lx0, ly, lx1, lh) in enumerate(Ls):
            kk = seg(t, hl_t0 + i * hl_dur / n, hl_t0 + (i + 1) * hl_dur / n)
            if kk <= 0: continue
            hp = paint("#FFD166", int(150 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(lx0 - 8, ly - 10, lx0 - 8 + (lx1 - lx0 + 16) * ease_out(kk), ly + lh + 10), hp)
    c.restore()

def portrait(c, name, x, y, k, grey=0.0, col="#C9A46A", hat="turban", w=300, h=360):
    """generic silhouette bust card - 'Aadhunik chitran' (no real likeness)"""
    if k <= 0: return
    kk = back(k); al = int(255 * clamp(k * 1.5))
    c.save(); c.translate(x, y); c.scale(kk, kk)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 22, "#16223A", al, shadow=20)
    skin = "#8A9BB0" if grey > 0.5 else "#D9A877"; robe = "#5B6472" if grey > 0.5 else col
    c.save(); c.clipRect(skia.Rect(-w / 2 + 8, -h / 2 + 8, w / 2 - 8, h / 2 - 70))
    c.drawOval(skia.Rect(-110, 40, 110, 260), paint(robe, al))
    c.drawCircle(0, -20, 62, paint(skin, al))
    if hat == "turban":
        c.drawOval(skia.Rect(-70, -100, 70, -30), paint("#F1FAEE" if grey < 0.5 else "#AAB4C2", al))
    elif hat == "crown":
        crown(c, 0, -88, 70, YEL if grey < 0.5 else "#AAB4C2", al)
    elif hat == "helmet":
        c.drawOval(skia.Rect(-66, -96, 66, -18), paint("#7A8BA3", al)); c.drawRect(skia.Rect(-4, -110, 4, -90), paint("#7A8BA3", al))
    c.restore()
    if grey > 0: c.drawRect(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), paint("#0F1B2D", int(110 * grey * al / 255)))
    fs = min(30, 30 * (w - 30) / max(1, text_w(name, 30)))
    text(c, name, 0, h / 2 - 34, fs, "#F1FAEE", FT_BLACK, "c", al)
    text(c, "Aadhunik chitran", 0, h / 2 - 10, 16, "#8A9BB0", FT_SEMI, "c", al)
    c.restore()

def name_card(c, name, sub, x, y, k, col=GREEN):
    """text-only card (used for revered figures: no face is drawn)"""
    if k <= 0: return
    kk = back(k); al = int(255 * clamp(k * 1.5)); w = max(text_w(name, 44) + 80, 380)
    c.save(); c.translate(x, y); c.scale(kk, kk)
    rrect(c, -w / 2, -70, w / 2, 70, 20, "#16223A", al, shadow=18); c.drawRoundRect(skia.Rect(-w / 2, -70, w / 2, 70), 20, 20, paint(col, al, stroke=2))
    text(c, name, 0, 4, 44, "#F1FAEE", FT_BLACK, "c", al); text(c, sub, 0, 46, 22, "#9FB0C6", FT_SEMI, "c", al)
    c.restore()

def xmark(c, x, y, s, k, col=RED):
    if k <= 0: return
    for i, (dx, dy) in enumerate(((1, 1), (1, -1))):
        kk = ease_out(seg(k, i * 0.3, 0.6 + i * 0.3))
        c.drawLine(x - s * dx, y - s * dy, x - s * dx + 2 * s * dx * kk, y - s * dy + 2 * s * dy * kk, paint(col, 255, stroke=s * 0.22, cap_round=True))

def swords(c, x, y, s, k, col="#F1FAEE"):
    if k <= 0: return
    kk = back(k)
    for sgn in (-1, 1):
        c.save(); c.translate(x, y); c.rotate(sgn * 45); c.scale(kk, kk)
        c.drawRect(skia.Rect(-s * 0.06, -s, s * 0.06, s * 0.55), paint(col)); c.drawRect(skia.Rect(-s * 0.28, s * 0.5, s * 0.28, s * 0.62), paint(col))
        c.drawRect(skia.Rect(-s * 0.07, s * 0.62, s * 0.07, s * 0.95), paint("#C9971E")); c.restore()

def boat(c, x, y, s, a=255, col="#C9D1DC", sail="#E9DCC0"):
    k = s / 100
    p = skia.Path(); p.moveTo(x - 50 * k, y); p.lineTo(x + 50 * k, y); p.lineTo(x + 34 * k, y + 18 * k); p.lineTo(x - 36 * k, y + 18 * k); p.close()
    c.drawPath(p, paint("#8B5E3C", a)); c.drawLine(x, y, x, y - 60 * k, paint("#5A3B22", a, stroke=4 * k))
    sp = skia.Path(); sp.moveTo(x + 3 * k, y - 58 * k); sp.lineTo(x + 40 * k, y - 8 * k); sp.lineTo(x + 3 * k, y - 8 * k); sp.close(); c.drawPath(sp, paint(sail, a))

def elephant(c, x, y, s, a=255, col="#9AA5B4"):
    k = s / 100
    c.drawOval(skia.Rect(x - 55 * k, y - 35 * k, x + 35 * k, y + 20 * k), paint(col, a))
    c.drawCircle(x + 42 * k, y - 22 * k, 24 * k, paint(col, a))
    tr = skia.Path(); tr.moveTo(x + 60 * k, y - 18 * k); tr.quadTo(x + 78 * k, y + 10 * k, x + 64 * k, y + 34 * k); c.drawPath(tr, paint(col, a, stroke=10 * k, cap_round=True))
    for dx in (-42, -18, 6, 24): c.drawRect(skia.Rect(x + dx * k, y + 10 * k, x + (dx + 13) * k, y + 46 * k), paint(col, a))
    c.drawOval(skia.Rect(x + 30 * k, y - 34 * k, x + 44 * k, y - 6 * k), paint("#7D8796", a))
    rrect(c, x - 30 * k, y - 56 * k, x + 10 * k, y - 34 * k, 6 * k, "#B23A48", a)

def camel(c, x, y, s, a=255, col="#C69C6D"):
    k = s / 100
    p = skia.Path(); p.moveTo(x - 45 * k, y); p.quadTo(x - 30 * k, y - 45 * k, x - 12 * k, y - 10 * k); p.quadTo(x + 2 * k, y - 45 * k, x + 22 * k, y - 4 * k)
    p.lineTo(x + 40 * k, y - 30 * k); p.lineTo(x + 52 * k, y - 26 * k); p.lineTo(x + 34 * k, y + 8 * k); p.lineTo(x - 45 * k, y + 8 * k); p.close()
    c.drawPath(p, paint(col, a))
    for dx in (-38, -26, 14, 26): c.drawRect(skia.Rect(x + dx * k, y + 6 * k, x + (dx + 7) * k, y + 42 * k), paint(col, a))

def horse(c, x, y, s, a=255, col="#A0705A"):
    k = s / 100
    c.drawOval(skia.Rect(x - 45 * k, y - 22 * k, x + 30 * k, y + 14 * k), paint(col, a))
    nk = skia.Path(); nk.moveTo(x + 18 * k, y - 12 * k); nk.lineTo(x + 40 * k, y - 50 * k); nk.lineTo(x + 58 * k, y - 40 * k); nk.lineTo(x + 34 * k, y - 4 * k); nk.close()
    c.drawPath(nk, paint(col, a))
    for dx in (-38, -26, 12, 22): c.drawRect(skia.Rect(x + dx * k, y + 8 * k, x + (dx + 7) * k, y + 46 * k), paint(col, a))
    c.drawCircle(x - 6 * k, y - 40 * k, 12 * k, paint("#C9D1DC", a)); c.drawRect(skia.Rect(x - 12 * k, y - 30 * k, x, y - 14 * k), paint("#C9D1DC", a))

def catapult(c, x, y, s, a=255, arm=0.0):
    k = s / 100
    c.drawRect(skia.Rect(x - 40 * k, y + 10 * k, x + 40 * k, y + 20 * k), paint("#8B5E3C", a))
    for dx in (-30, 30): c.drawCircle(x + dx * k, y + 24 * k, 9 * k, paint("#5A3B22", a))
    c.drawLine(x, y + 10 * k, x - 10 * k, y - 20 * k, paint("#8B5E3C", a, stroke=7 * k))
    ang = lerp(-35, 60, arm); c.save(); c.translate(x - 10 * k, y - 20 * k); c.rotate(ang)
    c.drawLine(0, 0, -50 * k, 0, paint("#A0705A", a, stroke=6 * k, cap_round=True)); c.drawCircle(-52 * k, -6 * k, 9 * k, paint("#6B7280", a)); c.restore()

def scroll(c, x, y, s, a=255, txt=""):
    k = s / 100
    rrect(c, x - 60 * k, y - 40 * k, x + 60 * k, y + 40 * k, 6 * k, "#E9DCC0", a, shadow=10)
    for dx in (-60, 60): c.drawOval(skia.Rect(x + dx * k - 10 * k, y - 46 * k, x + dx * k + 10 * k, y + 46 * k), paint("#C9B48A", a))
    if txt: text(c, txt, x, y + 8 * k, min(26 * k, 108 * k / max(1, text_w(txt, 1))), "#5A3B22", FT_BLACK, "c", a)

def handshake(c, x, y, s, a=255):
    k = s / 100
    for sgn, col in ((-1, "#D9A877"), (1, "#C08A5A")):
        rrect(c, x + sgn * 70 * k - 30 * k, y - 14 * k, x + sgn * 10 * k + 30 * k * (sgn < 0), y + 14 * k, 12 * k, col, a)
    c.drawOval(skia.Rect(x - 26 * k, y - 22 * k, x + 26 * k, y + 22 * k), paint("#E2B48A", a))

def gate(c, x, y, s, open_k=0.0, a=255):
    """fortress gate; doors swing open with open_k"""
    k = s / 100
    rrect(c, x - 80 * k, y - 90 * k, x + 80 * k, y + 70 * k, 10 * k, "#5B4636", a)
    for j in range(5): c.drawRect(skia.Rect(x - 80 * k + j * 36 * k, y - 110 * k, x - 64 * k + j * 36 * k, y - 90 * k), paint("#5B4636", a))
    ow = 50 * k * (1 - ease_io(open_k))
    c.drawRect(skia.Rect(x - 50 * k, y - 50 * k, x + 50 * k, y + 70 * k), paint("#0B1424", a))
    for sgn in (-1, 1):
        x0 = x + sgn * 50 * k; x1 = x0 - sgn * ow
        c.drawRect(skia.Rect(min(x0, x1), y - 50 * k, max(x0, x1), y + 70 * k), paint("#8B5E3C", a))
    if open_k < 0.05: c.drawRect(skia.Rect(x - 50 * k, y + 2 * k, x + 50 * k, y + 12 * k), paint("#3A2F22", a))

def bookmark(c, x, y, s, a=255, col=YEL):
    k = s / 100; p = skia.Path(); p.moveTo(x - 22 * k, y - 34 * k); p.lineTo(x + 22 * k, y - 34 * k); p.lineTo(x + 22 * k, y + 34 * k)
    p.lineTo(x, y + 18 * k); p.lineTo(x - 22 * k, y + 34 * k); p.close(); c.drawPath(p, paint(col, a))

def river(c, cam, pts, k, col="#4FC3F7", w=5, a=255):
    sp = [to_screen(cam, *p) for p in pts]
    route(c, sp, k, col, w, dash=False, a=a, head=False)

def pin_at(c, cam, key, label_s, t, t0, col=YEL, size=30, side="r"):
    x, y = S(cam, key); pin(c, x, y, label_s, seg(t, t0 - 0.1, t0 + 0.4), col, size=size, side=side, t=t)

# ======================================================================= CHAPTER 1 (rest)
u_636 = U("Saal 636"); u_thane = U("Thane, Bharuch"); u_twist = U("Aur twist ye"); u_644 = U("644 mein"); u_kyun = U("Kyun?")
u_unki = U("Unki nazar"); u_yaad = U("Ye baat yaad rakhna")
SEA_CAM = (66.0, 21.8, 52.0)
@shot(ue(u_india75) + 0.6, vin(u_twist), "cut")
def s16(c, t):
    bg(c, SEA_CAM)
    timeline(c, t, 636, 1.0, span=(620, 780))
    src = S(SEA_CAM, "oman")
    for i, (key, nm) in enumerate((("thane", "THANE"), ("bharuch", "BHARUCH"), ("debal", "DEBAL"))):
        t0 = kw(u_thane, nm.title()); dst = S(SEA_CAM, key)
        kk = seg(t, vin(u_636) + 0.6 + i * 0.4, t0 + 0.1)
        if kk > 0:
            mx, my = (src[0] + dst[0]) / 2, (src[1] + dst[1]) / 2 + 120
            route(c, [src, (mx, my), dst], ease_out(kk), "#9FB0C6", 4, dash=True, head=False)
            bx = lerp(lerp(src[0], mx, ease_out(kk)), lerp(mx, dst[0], ease_out(kk)), ease_out(kk)); by = lerp(lerp(src[1], my, ease_out(kk)), lerp(my, dst[1], ease_out(kk)), ease_out(kk))
            boat(c, bx, by - 6, 60)
        pin_at(c, SEA_CAM, key, nm, t, t0, YEL, 30, "l" if key != "debal" else "r")
    title(c, "SAMUNDAR SE 3 HAMLE", 960, 150, 56, seg(t, vin(u_636), vin(u_636) + 0.5), "#F1FAEE")
    SFX_MARK(vin(u_636) + 0.6, "whoosh", -22)

@shot(vin(u_twist), vin(u_644))
def s17(c, t):
    bg(c, SEA_CAM); dim(c, 150)
    doc(c, "umar_sanction", 300, 200, 1320, 420, t, seg(t, vin(u_twist), vin(u_twist) + 0.6), kw(u_twist, "Umar") - 0.1, 1.4)
    label(c, "KHALIFA UMAR · doosre khalifa (634-644)", 960, 700, seg(t, kw(u_twist, "Umar") - 0.2, kw(u_twist, "Umar") + 0.3), 30, border=GREEN)
    stamp(c, "IJAAZAT NAHI", 960, 840, 72, RED, seg(t, kw(u_twist, "ijaazat") - 0.1, kw(u_twist, "ijaazat") + 0.35))
    SFX_MARK(kw(u_twist, "ijaazat"), "stamp", -18)

IND_CAM = (66.5, 27.5, 30.0)
@shot(vin(u_644), vin(u_kyun))
def s18(c, t):
    bg(c, IND_CAM)
    timeline(c, t, 644, 1.0, span=(620, 780))
    river(c, IND_CAM, INDUS, seg(t, vin(u_644), vin(u_644) + 1.5), "#4FC3F7", 7)
    x, y = S(IND_CAM, "indus"); label(c, "SINDHU NADI", x + 150, y - 40, seg(t, kw(u_644, "Sindhu") - 0.1, kw(u_644, "Sindhu") + 0.3), 30, border="#4FC3F7")
    p0 = S(IND_CAM, "makran"); p1 = to_screen(IND_CAM, 67.6, 26.4)
    arrow(c, p0, p1, seg(t, vin(u_644) + 0.4, kw(u_644, "pahunchi") + 0.2), GREEN, 9, -0.1)
    stamp(c, "NADI PAAR NAHI", 960, 220, 64, RED, seg(t, kw(u_644, "nadi paar") - 0.1, kw(u_644, "nadi paar") + 0.35))
    SFX_MARK(kw(u_644, "nadi paar"), "stamp", -18)

@shot(vin(u_kyun), vin(U("711.")) - 0.0)
def s19(c, t):
    bg(c, IND_CAM)
    k = seg(t, kw(u_unki, "kharaab") - 0.3, kw(u_unki, "kharaab") + 0.6)
    if k > 0:
        cx_, cy_ = cam_xy(IND_CAM[0], IND_CAM[1]); sc_ = IND_CAM[2]
        c.save(); c.translate(DW / 2, DH / 2); c.scale(sc_, sc_); c.translate(-cx_, -cy_)
        pth = gpath("desert", sc_); c.drawPath(pth, paint("#C8A26A", int(200 * k))); c.clipPath(pth, doAntiAlias=True)
        rng = np.random.default_rng(5)
        for _ in range(140):
            px, py = cam_xy(rng.uniform(58, 72.5), rng.uniform(23, 31)); L = rng.uniform(0.4, 1.4); a_ = rng.uniform(0, math.pi)
            c.drawLine(px, py, px + L * math.cos(a_), py + L * math.sin(a_), paint("#7A5A32", int(170 * k), stroke=1.6 / sc_))
        c.restore()
        label(c, "MAKRAN + SINDH: REGISTAAN", *to_screen(IND_CAM, 64.5, 30.0), k, 28, border="#C8A26A")
    title(c, "KYUN?", 960, 200, 90, seg(t, vin(u_kyun), vin(u_kyun) + 0.3), YEL)
    name_card(c, '"KHARAAB, GAREEB ZAMEEN"', "Khalifa Umar ki raay", 960, 760, seg(t, kw(u_unki, "kharaab") - 0.1, kw(u_unki, "kharaab") + 0.4), "#C8A26A")
    kb = seg(t, kw(u_yaad, "yaad"), kw(u_yaad, "yaad") + 0.8)
    if kb > 0:
        bx = lerp(960, 1840, ease_io(kb)); by = lerp(520, 90, ease_io(kb)); bookmark(c, bx, by, lerp(140, 60, ease_io(kb)))
    SFX_MARK(kw(u_yaad, "yaad"), "ding", -20)

# ======================================================================= CHAPTER 2: 15 SAAL KA GENERAL
u_711b = U("711."); u_iraq = U("Iraq ka sakht"); u_kamaan = U("Sindh par hamle ki kamaan"); u_mbq = U("Muhammad bin Qasim.")
u_umr = U("Umar?"); u_pandrah = U("Sirf pandrah"); u_saath = U("Saath mein chhe"); u_samu = U("Aur samundar ke raaste")
u_pehla = U("Pehla nishaana"); u_debal = U("Debal, aaj ke"); u_debgir = U("Debal girta"); u_mandir = U("Mandir toda")
u_712 = U("712, Aror"); u_dahir = U("Raja Dahir"); u_khatam = U("Sindh ka raja khatam"); u_multan = U("Phir Multan")
u_do = U("Do mahine"); u_par = U("Par is jeet"); u_hukum = U("Hajjaj ka hukum"); u_ablag = U("Ab lag raha tha")
u_palat = U("Aur yahin kahani"); u_715 = U("715 mein"); u_wapas = U("Aur Muhammad bin Qasim ko wapas"); u_usi = U("Usi saal, 18 July")
u_cheen = U("Aur Indian raja Aror"); u_offer = U("Phir Khalifa Umar doosre"); u_islam = U("Islam qubool"); u_hulli = U("Sindh ke raja Hullishah")
u_pakka = U("Lekin Sindh se aage pakka"); u_abtak = U("Ab tak nahi"); u_north = U("Aur iski pehli wajah")
CHAPTERS.append((2, "15 SAAL KA GENERAL", u_711b)); chapter(2, "15 SAAL KA GENERAL", u_711b)
IQ_CAM = (52.0, 29.0, 16.0)
@shot(vin(u_711b), vin(u_kamaan), "cut")
def s20(c, t):
    bg(c, IQ_CAM)
    timeline(c, t, 711, 1.0, span=(620, 780))
    hl(c, IQ_CAM, "iraq", t, kw(u_iraq, "Iraq"))
    pin_at(c, IQ_CAM, "kufa", "KUFA", t, kw(u_iraq, "Iraq") + 0.3, YEL, 26)
    float_map(c, t, kw(u_iraq, "Iraq"), "iraq", "IRAQ · 711", "Hajjaj ka subah (andaazan)", 1400, 140, 420, 320, pad=0.5)
    portrait(c, "HAJJAJ BIN YUSUF", 420, 520, seg(t, kw(u_iraq, "Hajjaj") - 0.1, kw(u_iraq, "Hajjaj") + 0.4), col="#3D6B4F", hat="turban")

@shot(vin(u_kamaan), vin(u_saath))
def s21(c, t):
    bg(c, IQ_CAM); dim(c, 120)
    portrait(c, "MUHAMMAD BIN QASIM", 760, 520, seg(t, us(u_mbq) - 0.2, us(u_mbq) + 0.3), col="#7A4E2D", hat="helmet")
    stat_card(c, 1080, 360, 460, 300, "15-17 SAAL", "kamaan milte waqt umar", seg(t, kw(u_pandrah, "pandrah") - 0.1, kw(u_pandrah, "pandrah") + 0.4), YEL)
    title(c, "UMAR?", 1310, 300, 60, seg(t, us(u_umr), us(u_umr) + 0.3), YEL) if t < us(u_pandrah) + 0.2 else None
    hl(c, IQ_CAM, "sindh", t, kw(u_kamaan, "Sindh"))
    arrow(c, S(IQ_CAM, "basra"), to_screen(IQ_CAM, 66.0, 25.5), seg(t, vin(u_kamaan) + 0.3, kw(u_kamaan, "kamaan") + 0.6), GREEN, 8, 0.12)

@shot(vin(u_saath), vin(u_samu))
def s22(c, t):
    c.clear(hexc(NAVY))
    groups = [("horse", 6000, "SYRIAN GHUDSAWAAR", "ghudsawaar", "#3A86FF"), ("camel", 6000, "OONT-SAWAAR", "oont-sawaar", "#F8961E"), ("camel", 3000, "SAAMAAN WALE OONT", "saamaan", "#9B5DE5")]
    for i, (ic, num, lab, word, col) in enumerate(groups):
        t0 = kw(u_saath, word) - 0.5; k = seg(t, t0, t0 + 0.6)
        if k <= 0: continue
        cx, cy, R = 400 + i * 560, 480, 210; al = int(255 * clamp(k * 1.5))
        c.drawCircle(cx, cy, R * back(k), paint("#16223A", al)); c.drawCircle(cx, cy, R * back(k), paint(col, al, stroke=5))
        p_ = skia.Path(); p_.addArc(skia.Rect(cx - R - 14, cy - R - 14, cx + R + 14, cy + R + 14), -90, 360 * ease_out(seg(t, t0, t0 + 1.2))); c.drawPath(p_, paint(col, al, stroke=8, cap_round=True))
        n_icons = 12 if num == 6000 else 7
        for j in range(n_icons):                                   # icons gather into the circle
            ring = 0 if j < 1 else (1 if j < 7 else 2); idx = j - (0 if ring == 0 else (1 if ring == 1 else 7))
            cnt = 1 if ring == 0 else (6 if ring == 1 else 6); rr = (0, 92, 160)[ring]
            an = idx / cnt * math.tau + ring * 0.4; kj = ease_out(seg(t, t0 + j * 0.05, t0 + 0.5 + j * 0.05))
            x = cx + rr * math.cos(an) * kj + (1 - kj) * (cx - 600 if i == 0 else 0); y = cy + rr * 0.78 * math.sin(an) * kj + (1 - kj) * 300
            if kj > 0: (horse if ic == "horse" else camel)(c, x, y + 10, 52, int(255 * kj))
        nn = int(num * ease_out(seg(t, t0, t0 + 1.0)))
        title(c, f"{nn:,}", cx, cy + R + 100, 80, k, YEL); title(c, lab, cx, cy + R + 150, 28, seg(t, t0 + 0.2, t0 + 0.8), "#F1FAEE")
    SFX_MARK(kw(u_saath, "ghudsawaar") - 0.5, "count", -22)

@shot(vin(u_samu), vin(u_pehla))
def s23(c, t):
    bg(c, SEA_CAM)
    src = S(SEA_CAM, "basra") if False else to_screen(SEA_CAM, 56.5, 25.0); dst = S(SEA_CAM, "debal")
    k = ease_io(seg(t, vin(u_samu), ue(u_samu)))
    route(c, [src, ((src[0] + dst[0]) / 2, src[1] + 60), dst], k, "#9FB0C6", 4, True, head=False)
    bx, by = lerp(src[0], dst[0], k), lerp(src[1], dst[1], k) + math.sin(k * math.pi) * 60
    boat(c, bx, by, 80)
    for j in range(5):
        kj = seg(t, kw(u_samu, "paanch") + j * 0.08, kw(u_samu, "paanch") + 0.3 + j * 0.08)
        if kj > 0: catapult(c, 560 + j * 200, 860, 80, int(255 * kj), arm=seg(t, kw(u_samu, "patthar"), kw(u_samu, "patthar") + 0.4) if j == 2 else 0)
    label(c, "5 MANJANIQ", 960, 740, seg(t, kw(u_samu, "paanch"), kw(u_samu, "paanch") + 0.3), 34)

DB_CAM = (67.4, 25.0, 140.0)
@shot(vin(u_pehla), vin(u_712))
def s24(c, t):
    cam = fly((64.0, 23.0, 30.0), DB_CAM, ease_io(seg(t, vin(u_pehla), us(u_debal) + 1.0)))
    bg(c, cam); hl(c, cam, "sindh", t, kw(u_debal, "Debal"))
    x, y = S(cam, "debal2"); pin(c, x, y, "DEBAL (andaazan sthaan)", seg(t, kw(u_debal, "Debal"), kw(u_debal, "Debal") + 0.4), YEL, size=30, t=t)
    kc = seg(t, kw(u_debal, "Karachi") - 0.1, kw(u_debal, "Karachi") + 0.4)
    if kc > 0: tag_note(c, "aaj ka Karachi paas mein", x, y + 60, kc, "#C9D1DC")
    photo_card(c, "banbhore", 120, 420, 600, 340, t, seg(t, kw(u_debal, "Karachi") - 0.2, kw(u_debal, "Karachi") + 0.4), "Banbhore: Debal ki sambhavit jagah",
               "Photo: Engr.aly · CC BY-SA 4.0 · Wikimedia Commons", t0=us(u_debal), kout=seg(t, us(u_mandir) - 0.3, us(u_mandir)))
    stamp(c, "DEBAL GIRA", 1430, 220, 56, RED, seg(t, us(u_debgir) - 0.1, us(u_debgir) + 0.3) * (1 - seg(t, us(u_mandir), us(u_mandir) + 0.3)))
    SFX_MARK(us(u_debgir), "stamp", -18)
    doc(c, "mbq_debal", 1020, 300, 820, 420, t, seg(t, us(u_mandir) - 0.2, us(u_mandir) + 0.3), us(u_mandir) + 0.3, 1.4)

AR_CAM2 = (69.0, 27.0, 70.0)
@shot(vin(u_712), vin(u_multan))
def s25(c, t):
    bg(c, AR_CAM2); hl(c, AR_CAM2, "sindh", t, vin(u_712))
    timeline(c, t, 712, 1.0, span=(620, 780))
    pin_at(c, AR_CAM2, "aror", "AROR", t, kw(u_712, "Aror"), YEL, 30)
    doc(c, "raja_dahir", 1080, 150, 790, 330, t, seg(t, us(u_dahir) - 0.3, us(u_dahir) + 0.3), us(u_khatam) - 0.2, 1.6)
    th = kw(u_dahir, "teer") + 0.25                                       # arrow hits
    fall = ease_in(seg(t, th + 0.1, th + 0.9)); dimk = seg(t, us(u_khatam), us(u_khatam) + 0.4)
    ex, ey = 860, 690; elephant(c, ex, ey, 170, int(255 * (1 - 0.5 * dimk)))
    for j in range(6):                                                    # Arab army (archers) facing Dahir from the west
        ic_soldier(c, 250 + (j % 3) * 85, 650 + (j // 3) * 90, 78, t * 0.5 + j, "#F1FAEE", int(255 * seg(t, vin(u_712), vin(u_712) + 0.6)), walk=False)
    label(c, "ARAB FAUJ", 335, 560, seg(t, vin(u_712), vin(u_712) + 0.6), 24, border=GREEN)
    rx, ry = ex - 10, ey - 118                                            # 2D Raja Dahir (Aadhunik chitran) on the howdah
    c.save(); c.translate(rx, ry + fall * 120); c.rotate(-fall * 70)
    c.drawRoundRect(skia.Rect(-20, -10, 20, 50), 14, 14, paint("#B23A48")); c.drawCircle(0, -26, 18, paint("#D9A877"))
    crown(c, 0, -48, 30, YEL, 255); c.drawLine(18, 6, 44, -14 + fall * 30, paint("#B23A48", 255, stroke=10, cap_round=True))
    c.restore()
    label(c, "RAJA DAHIR · Aadhunik chitran", ex, ey + 140, seg(t, us(u_dahir) - 0.2, us(u_dahir) + 0.3), 24, border="#B23A48")
    ka = seg(t, th - 0.55, th)                                            # the arrow flies in from the left
    if 0 < ka < 1:
        ax, ay = lerp(470, rx - 16, ease_in(ka)), lerp(610, ry - 6, ease_in(ka)) - math.sin(ka * math.pi) * 90
        c.drawLine(ax - 60, ay - 18, ax, ay, paint("#F1FAEE", 255, stroke=5, cap_round=True))
        hp = skia.Path(); hp.moveTo(ax + 12, ay + 4); hp.lineTo(ax - 8, ay - 10); hp.lineTo(ax - 4, ay + 10); hp.close(); c.drawPath(hp, paint("#C9D1DC"))
    if t >= th and t < th + 0.9:
        c.save(); c.translate(rx, ry + fall * 120); c.rotate(-fall * 70); c.drawLine(-50, -30, -8, -2, paint("#F1FAEE", 255, stroke=5, cap_round=True)); c.restore()
    clash(c, rx, ry, seg(t, th, th + 0.7), 0.9)
    date_k = seg(t, us(u_khatam), us(u_khatam) + 0.4)
    if date_k > 0: pill(c, "20 JUNE 712 · RAJA DAHIR KI MAUT", ex, ey + 200, 28, RED, a=int(255 * clamp(date_k * 1.5)))
    conquer(c, AR_CAM2, "sindh", t, us(u_khatam), 0.9, flag_at=(68.95, 27.7), flag_size=0.9)
    SFX_MARK(th - 0.5, "whoosh_fast", -18); SFX_MARK(th, "hit", -16); SFX_MARK(us(u_khatam), "boom", -20)

@shot(vin(u_multan), vin(u_par))
def s26(c, t):
    bg(c, AR_CAM2); hl(c, AR_CAM2, "sindh", t, 0, flag="umayyad")
    x, y = S(AR_CAM2, "multan"); fort(c, x, y - 10, 90, seg(t, vin(u_multan), vin(u_multan) + 0.8))
    for j in range(8):                                                                 # besieging soldiers close in
        an = j / 8 * math.tau; d0 = lerp(220, 120, ease_io(seg(t, us(u_do), kw(u_do, "dhokhe"))))
        ic_soldier(c, x + d0 * math.cos(an), y + 0.6 * d0 * math.sin(an), 34, t + j, "#F1FAEE", int(255 * seg(t, vin(u_multan) + 0.3, vin(u_multan) + 0.8)))
    pin(c, x, y, "MULTAN", seg(t, kw(u_multan, "Multan"), kw(u_multan, "Multan") + 0.4), YEL, size=30, t=t)
    k = seg(t, us(u_do), kw(u_do, "dhokhe"))
    rrect(c, 1250, 300, 1700, 560, 24, "#16223A", int(255 * clamp(seg(t, us(u_do) - 0.2, us(u_do)) * 1.5)), shadow=16)
    if t > us(u_do) - 0.2:
        c.drawArc(skia.Rect(1300, 340, 1480, 520), -90, 360 * ease_out(k), False, paint(YEL, 255, stroke=14, cap_round=True))
        text(c, "2", 1390, 455, 70, YEL, FT_BLACK, "c"); text(c, "MAHINE", 1590, 445, 40, "#F1FAEE", FT_BLACK, "c")
    ic_chain(c, 1260, 640, 1690, 640, seg(t, kw(u_do, "dhokhe") - 0.2, kw(u_do, "dhokhe") + 0.3), "#C9D1DC", 255, broken=t > kw(u_do, "dhokhe"))
    clash(c, x, y, seg(t, kw(u_do, "dhokhe"), kw(u_do, "dhokhe") + 0.8))
    kf = seg(t, kw(u_do, "dhokhe") + 0.4, kw(u_do, "dhokhe") + 1.0)
    if kf > 0: c.save(); c.translate(0, (1 - ease_out(kf)) * -100); pole_flag(c, x, y, "umayyad", t, clamp(kf * 1.5), 0.8, False); c.restore()
    SFX_MARK(kw(u_do, "dhokhe"), "glitch", -20)

@shot(vin(u_par), vin(u_ablag))
def s27(c, t):
    c.clear(hexc("#1A1F2E"))
    if t < vin(u_hukum) + 0.2:                                               # "jeet ka ek doosra paksh bhi tha"
        doc(c, "mbq_protection", 330, 140, 1260, 600, t, seg(t, vin(u_par), vin(u_par) + 0.6), kw(u_par, "doosra") - 0.2, 2.2)
        title(c, "JEET KA DOOSRA PAKSH", 960, 830, 56, seg(t, kw(u_par, "doosra") - 0.2, kw(u_par, "doosra") + 0.5), YEL)
        return
    kd = seg(t, vin(u_hukum), vin(u_hukum) + 0.5)
    doc(c, "hajjaj_order", 260, 90, 1400, 400, t, kd, kw(u_hukum, "ladein") - 0.3, 3.4)
    title(c, "HAJJAJ KA HUKUM", 960, 540, 44, kd, YEL)
    # 2D Hajjaj (Aadhunik chitran) gives the order
    hx, hy = 190, 760; pk = ease_out(seg(t, us(u_hukum) - 0.2, us(u_hukum) + 0.4))
    rb = skia.Path(); rb.moveTo(hx - 55, hy + 180); rb.lineTo(hx - 40, hy + 16); rb.quadTo(hx, hy - 8, hx + 40, hy + 16); rb.lineTo(hx + 55, hy + 180); rb.close()
    c.drawPath(rb, paint("#3D6B4F")); c.drawCircle(hx, hy - 26, 32, paint("#C99A6B"))
    bd = skia.Path(); bd.moveTo(hx - 27, hy - 22); bd.quadTo(hx, hy + 32, hx + 27, hy - 22); bd.quadTo(hx, hy - 4, hx - 27, hy - 22); c.drawPath(bd, paint("#3B2F2A"))
    c.drawOval(skia.Rect(hx - 35, hy - 72, hx + 35, hy - 40), paint("#F1EBDD"))
    ang = lerp(70, -15, pk); ax2 = hx + 30 + 90 * math.cos(math.radians(ang)); ay2 = hy + 24 + 90 * math.sin(math.radians(ang))
    c.drawLine(hx + 28, hy + 24, ax2, ay2, paint("#3D6B4F", 255, stroke=20, cap_round=True)); c.drawCircle(ax2, ay2, 10, paint("#C99A6B"))
    tag_note(c, "Hajjaj · Aadhunik chitran", hx, hy + 210, kd, "#E5E7EB")
    # "jo ladein unhe maaro": a real skirmish
    kl = seg(t, kw(u_hukum, "ladein") - 0.1, kw(u_hukum, "ladein") + 0.9)
    skirmish(c, 720, 780, t, kl)
    if kl > 0: pill(c, "JO LADEIN: MAARO", 720, 640, 30, RED, a=int(255 * clamp(kl * 2)))
    # "jo na ladein unhe aman do": civilians under a protecting dome
    ka = seg(t, kw(u_hukum, "na ladein") - 0.1, kw(u_hukum, "na ladein") + 0.6)
    if ka > 0:
        for j, col in enumerate(("#E76F51", "#2A9D8F", "#F4A261", "#9B5DE5", "#E9C46A")):
            civilian(c, 1310 + j * 70, 860, 90, col, int(255 * clamp(ka * 1.5)), t)
        R = 210 * ease_out(seg(t, kw(u_hukum, "aman") - 0.2, kw(u_hukum, "aman") + 0.5))
        if R > 2:
            dp = skia.Path(); dp.addArc(skia.Rect(1450 - R, 870 - R, 1450 + R, 870 + R), 180, 180)
            c.drawPath(dp, paint(GREEN, 70)); c.drawPath(dp, paint("#BFF0D4", 220, stroke=4))
        pill(c, "JO NA LADEIN: AMAN", 1450, 640, 30, GREEN, a=int(255 * clamp(ka * 2)))
    SFX_MARK(kw(u_hukum, "ladein"), "boom", -20); SFX_MARK(kw(u_hukum, "aman"), "ding", -20)

@shot(vin(u_ablag), vin(u_715))
def s28(c, t):
    bg(c, IN_CAM); hl(c, IN_CAM, "sindh", t, 0, flag="umayyad"); hl(c, IN_CAM, "india", t, kw(u_ablag, "Hindustan"))
    src = S(IN_CAM, "sindh")
    for i, key in enumerate(("gujarat", "rajasthan", "kannauj")):
        arrow(c, src, S(IN_CAM, key), seg(t, vin(u_ablag) + 0.2 + i * 0.3, vin(u_ablag) + 1.2 + i * 0.3), GREEN, 7, 0.15 - i * 0.1)
    d = seg(t, us(u_palat), us(u_palat) + 0.6)
    if d > 0: dim(c, 200 * d); title(c, "LEKIN...", 960, 560, 110, d, RED)
    SFX_MARK(us(u_palat), "riser", -18)

@shot(vin(u_715), vin(u_cheen))
def s29(c, t):
    cam = fly((40.0, 33.0, 18.0), (53.0, 31.0, 12.5), ease_io(seg(t, vin(u_715), vin(u_715) + 1.2)))
    bg(c, cam); hl(c, cam, "syria", t, kw(u_715, "Damascus"), flag_label=False); draw_region(c, cam, "sindh", GREEN, 160)
    timeline(c, t, 715, 1.0, span=(620, 780))
    pin_at(c, cam, "damascus", "DAMASCUS", t, kw(u_715, "Damascus"), YEL, 28)
    doc(c, "sulayman_recall", 1080, 110, 800, 360, t, seg(t, kw(u_715, "Sulayman") - 0.2, kw(u_715, "Sulayman") + 0.4) * (1 - seg(t, us(u_usi), us(u_usi) + 0.4)), kw(u_715, "Sulayman") + 0.3, 1.6)
    label(c, "KHALIFA SULAYMAN · 715", 1480, 500, seg(t, kw(u_715, "Sulayman"), kw(u_715, "Sulayman") + 0.4) * (1 - seg(t, us(u_usi), us(u_usi) + 0.4)), 26, border=GREEN)
    # the caliph's order rides out: a messenger gallops from Damascus to Sindh with the scroll
    p0, p1 = S(cam, "damascus"), S(cam, "sindh"); km = ease_io(seg(t, us(u_wapas) - 0.2, kw(u_wapas, "wapas") + 0.5))
    if km > 0:
        mid = ((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 120)
        r_ = route(c, [p0, mid, p1], km, YEL, 5, dash=True, head=False)
        if r_ and km < 1:
            mx, my, _ = along(*r_, km); horse(c, mx, my - 6, 64); scroll(c, mx + 14, my - 62, 34)
    ks = seg(t, kw(u_wapas, "wapas") + 0.4, kw(u_wapas, "wapas") + 0.9)
    if ks > 0: scroll(c, p1[0], p1[1] - 120, 150 * back(ks), int(255 * clamp(ks * 1.5)), "WAPAS BULAAO")
    portrait(c, "MUHAMMAD BIN QASIM", 330, 560, seg(t, us(u_wapas) - 0.2, us(u_wapas) + 0.3), grey=seg(t, kw(u_usi, "maut"), kw(u_usi, "maut") + 0.5), col="#7A4E2D", hat="helmet")
    pin_at(c, cam, "mosul", "MOSUL", t, kw(u_usi, "Mosul"), RED, 26)
    if t > kw(u_usi, "18"): pill(c, "18 JULY 715 · MOSUL", 330, 800, 30, RED, a=int(255 * clamp(seg(t, kw(u_usi, "18"), kw(u_usi, "18") + 0.4) * 1.5)))
    SFX_MARK(us(u_wapas), "whoosh_long", -18)

@shot(vin(u_cheen), vin(u_offer))
def s30(c, t):
    bg(c, AR_CAM2)
    k = ease_io(seg(t, vin(u_cheen) + 0.3, ue(u_cheen)))
    draw_region(c, AR_CAM2, "sindh", GREEN, int(220 * (1 - 0.65 * k)))
    x, y = S(AR_CAM2, "aror"); pin(c, x, y, "AROR", 1.0, SAFF if t > kw(u_cheen, "Aror") else YEL, size=30, t=t)
    stamp(c, "WAPAS!", 1400, 300, 80, SAFF, seg(t, kw(u_cheen, "wapas") - 0.1, kw(u_cheen, "wapas") + 0.3))
    SFX_MARK(kw(u_cheen, "wapas"), "stamp", -18)

# ---------------------------------------------------------------- helpers for chapter 2 end / chapter 3 (user list, points 1-9)
def throne(c, x, y, s, col="#E9C46A", a=255):
    """raj-gaddi: gold high-backed seat with a red cushion (feet of the seat at y)"""
    k = s / 100
    c.drawRoundRect(skia.Rect(x - 34 * k, y - 120 * k, x + 34 * k, y - 40 * k), 26 * k, 26 * k, paint(col, a))
    c.drawRoundRect(skia.Rect(x - 24 * k, y - 110 * k, x + 24 * k, y - 48 * k), 18 * k, 18 * k, paint("#9B2226", a))
    c.drawCircle(x, y - 128 * k, 9 * k, paint(col, a))
    rrect(c, x - 46 * k, y - 46 * k, x + 46 * k, y - 26 * k, 6 * k, col, a)
    rrect(c, x - 40 * k, y - 58 * k, x + 40 * k, y - 44 * k, 6 * k, "#C1121F", a)
    for dx in (-38, 38): c.drawLine(x + dx * k, y - 28 * k, x + dx * k, y, paint(col, a, stroke=9 * k, cap_round=True))
    for dx in (-50, 50): c.drawCircle(x + dx * k, y - 52 * k, 8 * k, paint(col, a))

def king_fig(c, x, y, s, bow, t, robe="#9B2226", a=255, face=1):
    """2D king in side view (faces `face`), feet at y; bow 0..1 = bends forward from the hip, head down, hand on chest"""
    k = s / 100; b = ease_io(clamp(bow)); breathe = math.sin(t * 2.2 + x * 0.01) * 1.5 * k
    hip = (x, y - 78 * k)
    rp = skia.Path(); rp.moveTo(x - 24 * k, hip[1]); rp.lineTo(x + 24 * k, hip[1]); rp.lineTo(x + 38 * k, y); rp.lineTo(x - 38 * k, y); rp.close()
    c.drawPath(rp, paint(robe, a)); c.drawPath(rp, paint("#000000", int(a * 0.25), stroke=2 * k))
    c.drawRect(skia.Rect(x - 38 * k, y - 8 * k, x + 38 * k, y), paint("#E9C46A", a))
    c.save(); c.translate(*hip); c.rotate(face * 34 * b)
    c.drawRoundRect(skia.Rect(-22 * k, -66 * k + breathe, 22 * k, 6 * k), 16 * k, 16 * k, paint(robe, a))
    c.drawLine(-16 * k, -60 * k, 16 * k, -4 * k, paint("#E9C46A", a, stroke=6 * k))                     # sash
    hx, hy = face * 6 * k, -86 * k + breathe
    c.save(); c.translate(hx, hy + 10 * k); c.rotate(face * 16 * b); c.translate(-hx, -(hy + 10 * k))
    c.drawCircle(hx, hy, 17 * k, paint("#C99A6B", a))
    c.drawArc(skia.Rect(hx - 6 * k + face * 4 * k, hy - 2 * k, hx + 16 * k * face + face * 4 * k, hy + 20 * k), 0, 180, True, paint("#3A2A1E", a))  # beard
    crown(c, hx, hy - 22 * k, 30 * k, "#E9C46A", a)
    c.restore()
    # arm: hangs, then folds to the chest while bowing
    sx_, sy_ = face * 4 * k, -56 * k
    ex, ey = sx_ + face * lerp(6, 18, b) * k, sy_ + lerp(30, 22, b) * k
    hx2, hy2 = lerp(sx_ + face * 8 * k, sx_ - face * 4 * k, b), lerp(sy_ + 60 * k, sy_ + 12 * k, b)
    c.drawLine(sx_, sy_, ex, ey, paint(robe, a, stroke=13 * k, cap_round=True)); c.drawLine(ex, ey, hx2, hy2, paint(robe, a, stroke=12 * k, cap_round=True))
    c.drawCircle(hx2, hy2, 7 * k, paint("#C99A6B", a))
    c.restore()

def march(c, pts, k, t, col="#F1FAEE", w=6, n=6, size=46, a=255, dash=False, face=1, line=True):
    """route drawn up to k with a column of 2D soldiers walking at its tip (face -1 = walking leftwards)"""
    if k <= 0: return None
    r_ = route(c, pts, ease_io(k), col if line else "#000000", w, dash=dash, a=a if line else 0, head=line)
    if not r_ or k >= 0.999: return r_
    for q in range(n):
        f_ = ease_io(k) - q * 0.035
        if f_ <= 0.01: continue
        sx, sy, _ = along(*r_, f_)
        c.save(); c.translate(sx, 0)
        if face < 0: c.scale(-1, 1)
        ic_soldier(c, 0, sy - size * 0.25 + (q % 2) * 6, size, t * 1.3 + q * 0.4, "#F1FAEE", a); c.restore()
    return r_

def army_block(c, x0, y0, rows, cols, s, t, k, flag_col="#1F9D5C", a=255):
    """a big formation marching to the right: rows recede (smaller, higher), whole block slides in, banners in front"""
    if k <= 0: return
    ke = ease_out(clamp(k)); al = int(a * clamp(k * 1.6)); slide = (1 - ke) * -700 + (t % 1000) * 0
    for r in range(rows - 1, -1, -1):
        sc = s * (0.72 + 0.28 * (r / max(1, rows - 1))); yy = y0 + r * s * 0.55; dx = (rows - 1 - r) * s * 0.18
        for q in range(cols):
            xx = x0 + slide + dx + q * sc * 0.62 + math.sin(t * 9 + q + r) * 1.5
            ic_soldier(c, xx, yy, sc, t * 1.4 + q * 0.3 + r * 0.5, "#F1FAEE", al)
        if r in (0, rows - 1):
            fx = x0 + slide + dx + cols * sc * 0.62 + 10; fy = yy - sc * 0.4
            c.drawLine(fx, fy, fx, fy - sc * 1.3, paint("#D9D9D9", al, stroke=4, cap_round=True))
            img = banner_tex("umayyad"); fw = sc * 0.8
            cloth(c, img, fx + 2, fy - sc * 1.3, fw, fw * img.height() / img.width(), t, al, 20, 0.08)
    for j in range(16):                                                                    # dust behind the march
        ph = (t * 0.6 + j * 0.13) % 1; dx_ = x0 + slide - 40 - ph * 160; dy_ = y0 + rows * s * 0.55 - 10 - (j % 4) * 14
        c.drawCircle(dx_, dy_, 10 + ph * 26, paint("#C8A26A", int(al * 0.18 * (1 - ph)), blur=8))

def fallen(c, x, y, s, t, fk, col_f="#8A94A3", face=1, a=255):
    """soldier who drops (rotates down and greys out) as fk goes 0 -> 1"""
    fe = ease_in(clamp(fk)); c.save(); c.translate(x, y); c.rotate(face * 86 * fe); c.translate(-x, -y)
    ic_soldier(c, x, y, s, t if fk <= 0 else 0, "#F1FAEE" if fk < 0.4 else col_f, int(a * (1 - 0.45 * clamp(fk))), walk=fk <= 0)
    c.restore()

# =================================================================== s31: khalifa's letters to the kings of Hind
OF_CAM0 = (57.0, 28.5, 15.0); OF_CAM1 = (75.0, 27.5, 40.0)
OFFER_K = ["sindh", "kashmir", "rajasthan", "kannauj", "gujarat", "mp"]
@shot(vin(u_offer), vin(u_pakka))
def s31(c, t):
    _state_regions()
    t0 = kw(u_offer, "offer"); cam = fly(OF_CAM0, OF_CAM1, ease_io(seg(t, t0 + 0.2, t0 + 1.7))); bg(c, cam)
    draw_region(c, cam, "caliph", GREEN, 120)
    xd, yd = S(cam, "damascus"); pin(c, xd, yd, "DAMASCUS", seg(t, vin(u_offer), vin(u_offer) + 0.4), YEL, size=30, t=t)
    gk = seg(t, kw(u_islam, "gaddi") - 0.1, kw(u_islam, "gaddi") + 0.5)
    kb = seg(t, us(u_hulli) - 0.2, us(u_hulli) + 0.4)
    for j, rg in enumerate(OFFER_K):
        ta = t0 + 0.15 + j * 0.22 + 1.25                                                    # letter lands
        hl(c, cam, rg, t, ta, pole=False)
        if rg == "sindh":
            ka = seg(t, kw(u_hulli, "maana") - 0.3, kw(u_hulli, "maana") + 0.3)
            if ka > 0: draw_region(c, cam, "sindh", GREEN, int(215 * ka))
    for j, rg in enumerate(OFFER_K):
        ta = t0 + 0.15 + j * 0.22 + 1.25; lo, la = rep_point(rg); x, y = to_screen(cam, lo, la)
        kk = seg(t, ta - 1.25, ta)
        if 0 < kk < 1:                                                                      # the farmaan flies from Damascus
            sx, sy = S(cam, "damascus")
            scroll(c, lerp(sx, x, ease_io(kk)), lerp(sy, y, ease_io(kk)) - math.sin(kk * math.pi) * 160, 46)
        ki = seg(t, ta, ta + 0.4)
        if 0 < ki < 1: c.drawCircle(x, y, 20 + 90 * ki, paint("#FFFFFF", int(200 * (1 - ki)), stroke=4))
        if gk > 0: throne(c, x - 52, y + 34, 44 * back(seg(gk, j * 0.08, 0.6 + j * 0.08)), a=int(255 * clamp(gk * 2)))
        if gk > 0: crown(c, x - 52, y - 46 + math.sin(t * 2.5 + j) * 4, 26 * back(seg(gk, 0.1 + j * 0.08, 0.7 + j * 0.08)), YEL, int(255 * clamp(gk * 2)))
        pole_flag(c, x + 4, y + 30, "umayyad" if rg == "sindh" and t > kw(u_hulli, "maana") else rg, t, seg(t, ta + 0.1, ta + 0.6), 0.72, False)
        if t > ta: text(c, BANNER[rg][3], x + 48, y + 56, 17, "#F1FAEE", FT_BLACK, "c", int(230 * seg(t, ta, ta + 0.4) * (1 - 0.6 * kb)), shadow=True)
    name_card(c, "KHALIFA UMAR II", "717-720", 420, 220, seg(t, vin(u_offer), vin(u_offer) + 0.5) * (1 - seg(t, t0 + 1.4, t0 + 1.8)))
    title(c, "SHART: ISLAM QUBOOL KARO", 960, 112, 44, seg(t, us(u_islam) - 0.1, us(u_islam) + 0.4) * (1 - kb), "#F1FAEE")
    title(c, "BADLE MEIN: GADDI BANI RAHEGI", 960, 168, 40, gk * (1 - kb), YEL)
    tag_note(c, "Baladhuri: Hind ke rajaon ko patra · rajya aur seemayein andaazan", 960, 1010, seg(t, t0 + 1.0, t0 + 1.5) * (1 - kb))
    if kb > 0:                                                                              # the kings accept: bow together
        dim(c, 215 * kb)
        floor = 900; rrect(c, 120, floor - 6, 1800, floor + 8, 6, "#E9C46A", int(120 * kb))
        tb = kw(u_hulli, "maana") - 0.7
        kings = [(330, 100, "#F8961E", 0.18), (560, 100, "#F15BB5", 0.09), (830, 128, "#FF6B6B", 0.0)]
        for i, (kx, ks, col, dl) in enumerate(kings):
            kin = seg(t, us(u_hulli) - 0.2 + i * 0.1, us(u_hulli) + 0.4 + i * 0.1)
            king_fig(c, kx + (1 - ease_out(kin)) * -120, floor, ks * 1.15, seg(t, tb + dl, tb + dl + 0.8), t, col, int(255 * clamp(kin * 1.6)))
        kp = seg(t, us(u_hulli), us(u_hulli) + 0.5)                                          # the farmaan they accept
        if kp > 0:
            for r in range(10):
                an = r / 10 * math.tau + t * 0.3
                c.drawLine(1320 + 60 * math.cos(an), 640 + 60 * math.sin(an), 1320 + 150 * math.cos(an), 640 + 150 * math.sin(an), paint(YEL, int(70 * kp), stroke=6, cap_round=True))
            scroll(c, 1320, 640, 170 * back(kp), int(255 * clamp(kp * 1.5)), "FARMAAN")
        label(c, "HULLISHAH (JAISIAH) · SINDH", 830, 960, seg(t, kw(u_hulli, "Hullishah") - 0.1, kw(u_hulli, "Hullishah") + 0.4), 30, border=GREEN)
        label(c, "KUCH AUR RAJA", 445, 960, seg(t, kw(u_hulli, "kuch") - 0.1, kw(u_hulli, "kuch") + 0.4), 26, border="#9FB0C6")
        title(c, "MAAN LIYA", 1320, 860, 54, seg(t, kw(u_hulli, "maana") - 0.1, kw(u_hulli, "maana") + 0.4), GREEN)
    SFX_MARK(t0 + 0.2, "whoosh_long", -20); SFX_MARK(kw(u_islam, "gaddi"), "ding", -20); SFX_MARK(kw(u_hulli, "maana"), "stamp", -20)

# =================================================================== s32: every free kingdom beyond Sindh
IND_ALL = (80.5, 23.0, 25.0)
AZAD = ["rajasthan", "gujarat", "mp", "kannauj", "kashmir", "deccan", "east", "south", "kamarupa"]
KB_CAM0 = (69.0, 27.5, 26.0); KB_CAM1 = (68.5, 33.5, 30.0)
@shot(vin(u_pakka), vin(U("India mein ghusne")))
def s32(c, t):
    _state_regions()
    cam = fly(IND_ALL, KB_CAM1, ease_io(seg(t, kw(u_north, "north") - 0.5, ue(u_north) + 0.5)))
    bg(c, cam); draw_region(c, cam, "caliph", GREEN, 140); draw_region(c, cam, "sindh", GREEN, 215)
    ta = kw(u_pakka, "aage")
    for j, rg in enumerate(AZAD): hl(c, cam, rg, t, ta + j * 0.1, pole=False)
    for j, rg in enumerate(AZAD):
        lo, la = rep_point(rg); x, y = to_screen(cam, lo, la); kf = seg(t, ta + j * 0.1 + 0.1, ta + j * 0.1 + 0.6)
        pole_flag(c, x, y + 26, rg, t, kf, 0.62, False)
        text(c, BANNER[rg][3], x + 36, y + 50, 16, "#F1FAEE", FT_BLACK, "c", int(230 * kf), shadow=True)
    xs, ys = S(cam, "sindh"); pole_flag(c, xs - 10, ys + 20, "umayyad", t, 1.0, 0.62, False)
    title(c, "SINDH SE AAGE PAKKA QABZA?", 960, 110, 50, seg(t, vin(u_pakka), vin(u_pakka) + 0.5), "#F1FAEE")
    pill(c, "AZAD RAJYA · c. 720", 1600, 980, 26, "#0B1424", a=int(255 * seg(t, ta + 0.6, ta + 1.0) * (1 - seg(t, kw(u_north, "north") - 0.5, kw(u_north, "north")))))
    stamp(c, "AB TAK NAHI", 1420, 300, 60, RED, seg(t, us(u_abtak) - 0.1, us(u_abtak) + 0.3))
    kg = seg(t, kw(u_north, "north"), ue(u_north) + 0.4)
    if kg > 0:
        x, y = S(cam, "kabul"); dim(c, 90 * kg); gate(c, x, y - 40, 120 * ease_out(kg), 0, int(255 * kg))
    SFX_MARK(ta, "whoosh_long", -20)

# =================================================================== CHAPTER 3: KABUL KA BAND DARWAZA
PL.update(dict(khyber=(71.1, 34.1), punjab=(73.6, 31.2), ghazni=(68.42, 33.55), bust=(64.36, 31.58), sistan=(61.6, 31.0),
               thar=(71.4, 27.2), zabul=(66.5, 32.2), herat=(62.2, 34.35), iran_c=(55.5, 32.5)))
def _extra_regions():
    if "kabul" in REG: return
    G = WM.geoms; afg = G["AFG"].difference(CALIPH)
    REG["kabul"] = afg.intersection(box(67.6, 33.3, 75, 38)); REG["zabul"] = afg.intersection(box(60, 29, 69.5, 33.6))
    REGCOL.update({"kabul": "#E76F51", "zabul": "#2A9D8F", "desert": "#C8A26A"})
u_ghus = U("India mein ghusne"); u_kk = U("Kabul, phir Khyber"); u_baad = U("Baad ke zyadatar"); u_band = U("Lekin Arabon ke liye ye darwaza")
u_yaad2 = U("Aur yaad rakhna, ye darwaza"); u_do_raaj = U("Wahan the do raaj"); u_ts = U("Kabul mein Turk Shahi"); u_665 = U("665 mein")
u_bagh = U("Aur shehar ne jaldi"); u_698 = U("698."); u_bheji = U("Hajjaj ne ek fauj bheji"); u_aod = U('"Army of Destruction"')
u_tab = U("Tabaahi ki fauj"); u_hukm2 = U("Hukum tha: qile"); u_nat = U("Nateeja?"); u_5000 = U("Sirf paanch hazaar")
u_peac = U("Agle saal chaalis"); u_ulta = U("Aur wo ulta"); u_200 = U("Kabul aur Zabul ne"); u_870 = U("Zunbilon ki aakhri")
u_r1 = U("Raaz number ek"); u_r1b = U("Kabul-Zabul ki deewar."); u_bacha = U("Toh Arabon ke paas bacha"); u_makr = U("Makran ka registaan")
u_yumar = U("Yaad hai Umar"); u_kg = U("Kharaab, gareeb"); u_r2 = U("Raaz number do"); u_sirf_r = U("Lekin sirf registaan"); u_asli = U("Asli jawab")
CHAPTERS.append((3, "KABUL KA BAND DARWAZA", u_ghus)); chapter(3, "KABUL KA BAND DARWAZA", u_ghus)
RAAZ = ["KABUL-ZABUL KI DEEWAR", "REGISTAAN KA RAASTA", "BAAR-BAAR KA JAWAB", "KHILAFAT KHUD TOOT RAHI THI"]
def raaz_labels(n_open): return [RAAZ[i] if i < n_open else f"RAAZ {i + 1}" for i in range(4)]
IND_FLAG = (76.3, 30.4)
NW_CAM = (68.5, 32.0, 46.0)
@shot(vin(u_ghus), vin(u_do_raaj), "cut")
def s33(c, t):
    _extra_regions()
    bg(c, NW_CAM)
    hl(c, NW_CAM, "india", t, kw(u_ghus, "India"), flag_at=IND_FLAG)                       # India stays lit while the road is explained
    title(c, "SABSE AASAAN RAASTA?", 960, 150, 56, seg(t, vin(u_ghus), vin(u_ghus) + 0.5), YEL)
    pts = [S(NW_CAM, "kabul"), S(NW_CAM, "khyber"), S(NW_CAM, "punjab")]
    route(c, pts, seg(t, kw(u_kk, "Kabul") - 0.1, kw(u_kk, "Khyber") + 0.6), YEL, 8, dash=False)
    pin_at(c, NW_CAM, "kabul", "KABUL", t, kw(u_kk, "Kabul"), YEL, 30, "l")
    pin_at(c, NW_CAM, "khyber", "KHYBER", t, kw(u_kk, "Khyber"), YEL, 28)
    km = seg(t, kw(u_kk, "Khyber") + 0.2, ue(u_baad) + 0.2)                                # an army walks the road into India
    if 0 < km < 1:
        march(c, [(pts[0][0] - 140, pts[0][1] - 40)] + pts + [(pts[2][0] + 160, pts[2][1] + 120)], km, t, n=7, size=44, line=False)
    if 0 < km < 1: pill(c, "BAAD KE HAMLAWAR · ISI RAASTE SE", 1180, 980, 26, "#0B1424", a=int(255 * seg(km, 0.15, 0.3) * (1 - seg(km, 0.9, 1.0))))
    for j in range(4):                                   # ghost arrows: later invaders on the same road
        kj = seg(t, vin(u_baad) + j * 0.35, vin(u_baad) + 1.2 + j * 0.35)
        if 0 < kj < 1:
            o = (j - 1.5) * 18; route(c, [(p[0] + o, p[1] + o) for p in pts], kj, "#9FB0C6", 4, dash=True, a=int(200 * (1 - kj)))
    kg = seg(t, kw(u_band, "band") - 0.2, kw(u_band, "band") + 0.2)
    x, y = S(NW_CAM, "kabul")
    ka = seg(t, vin(u_band), kw(u_band, "band"))                                            # Arab column runs into the shut gate
    if ka > 0:
        gx = x + 0; ex = lerp(x - 420, gx - 70, ease_out(ka)) - 30 * seg(t, kw(u_band, "band"), kw(u_band, "band") + 0.4)
        for q in range(5): ic_soldier(c, ex - q * 40, y + 60 + (q % 2) * 10, 46, t * 1.3 + q, "#F1FAEE", int(255 * (1 - seg(t, ue(u_band), ue(u_band) + 0.4))))
        if t < ue(u_band) + 0.4: pole_flag(c, ex - 210, y + 80, "umayyad", t, ka * (1 - seg(t, ue(u_band), ue(u_band) + 0.4)), 0.55, False)
    if kg > 0:
        gate(c, x, y - 30, 110 * back(kg), 0); SFX_MARK(kw(u_band, "band"), "stamp", -16)
        xmark(c, x - 110, y + 10, 34, seg(t, kw(u_band, "band") + 0.1, kw(u_band, "band") + 0.5))
    kk_ = seg(t, kw(u_yaad2, "darwaza"), kw(u_yaad2, "darwaza") + 0.8)
    if kk_ > 0:
        kx = lerp(x, 1840, ease_io(kk_)); ky = lerp(y - 70, 90, ease_io(kk_))
        c.drawCircle(kx - 14, ky, 14, paint(YEL, 255, stroke=6)); c.drawLine(kx, ky, kx + 34, ky, paint(YEL, 255, stroke=6)); c.drawLine(kx + 26, ky, kx + 26, ky + 12, paint(YEL, 255, stroke=6))

@shot(vin(u_do_raaj), vin(u_665))
def s34(c, t):
    _extra_regions(); bg(c, NW_CAM)
    hl(c, NW_CAM, "india", t, 0, flag_at=IND_FLAG)
    hl(c, NW_CAM, "kabul", t, kw(u_ts, "Turk Shahi")); hl(c, NW_CAM, "zabul", t, kw(u_ts, "Zunbil"))
    title(c, "DO RAAJ · INDIA KA DARWAZA", 960, 150, 50, seg(t, vin(u_do_raaj), vin(u_do_raaj) + 0.5), "#F1FAEE")
    label(c, "TURK SHAHI", *to_screen(NW_CAM, 69.8, 35.2), seg(t, kw(u_ts, "Turk Shahi"), kw(u_ts, "Turk Shahi") + 0.3), 30, border=REGCOL["kabul"])
    label(c, "ZUNBIL", *to_screen(NW_CAM, 65.6, 31.6), seg(t, kw(u_ts, "Zunbil"), kw(u_ts, "Zunbil") + 0.3), 30, border=REGCOL["zabul"])
    for j, (lo, la) in enumerate(((68.9, 34.0), (67.8, 33.2), (66.9, 32.4), (66.2, 31.6))):    # shields: the wall in front of India
        x, y = to_screen(NW_CAM, lo, la); shield(c, x - 70, y, 46, SAFF if j < 2 else REGCOL["zabul"], 255, seg(t, kw(u_ts, "Zunbil") + 0.3 + j * 0.1, kw(u_ts, "Zunbil") + 0.8 + j * 0.1))
    tag_note(c, "seemayein andaazan", 960, 1010, seg(t, kw(u_ts, "Zunbil"), kw(u_ts, "Zunbil") + 0.4))

@shot(vin(u_665), vin(u_698))
def s35(c, t):
    _extra_regions(); bg(c, NW_CAM)
    timeline(c, t, 665, 1.0, span=(620, 900), step=10, big_every=50)
    hl(c, NW_CAM, "caliph", t, vin(u_665) + 0.1, flag_at=(56.0, 36.4), flag="umayyad")      # the Arab side lights up first
    hl(c, NW_CAM, "india", t, 0, flag_at=IND_FLAG); hl(c, NW_CAM, "zabul", t, 0)
    tb = kw(u_665, "le liya"); kgreen = seg(t, tb, tb + 0.4) * (1 - seg(t, kw(u_bagh, "baghaawat") - 0.2, kw(u_bagh, "baghaawat") + 0.2))
    hl(c, NW_CAM, "kabul", t, 0)
    if kgreen > 0:
        cx_, cy_ = cam_xy(NW_CAM[0], NW_CAM[1]); s_ = NW_CAM[2]
        c.save(); c.translate(DW / 2, DH / 2); c.scale(s_, s_); c.translate(-cx_, -cy_); c.drawPath(gpath("kabul", s_), paint(GREEN, int(230 * kgreen))); c.restore()
    pts = [S(NW_CAM, "iran_c"), S(NW_CAM, "herat"), (S(NW_CAM, "ghazni")[0] - 40, S(NW_CAM, "ghazni")[1] - 30), S(NW_CAM, "kabul")]
    km = seg(t, vin(u_665) + 0.4, tb + 0.15)
    march(c, pts, km, t, GREEN, 9, n=7, size=50)
    if km >= 1 and t < kw(u_bagh, "baghaawat") + 0.2: route(c, pts, 1.0, GREEN, 9, dash=False, a=int(255 * (1 - seg(t, kw(u_bagh, "baghaawat"), kw(u_bagh, "baghaawat") + 0.3))))
    clash(c, *S(NW_CAM, "kabul"), seg(t, tb - 0.1, tb + 0.6), 1.2)
    x, y = S(NW_CAM, "kabul"); kf = seg(t, tb + 0.2, tb + 0.7); kd = seg(t, kw(u_bagh, "baghaawat") - 0.1, kw(u_bagh, "baghaawat") + 0.5)
    if kf > 0 and kd < 1:                                                                  # Arab flag planted ... then thrown down by the revolt
        c.save(); c.translate(x + 30, y + 10); c.rotate(-80 * ease_in(kd)); c.translate(-(x + 30), -(y + 10))
        pole_flag(c, x + 30, y + 10, "umayyad", t, kf, 0.8, False); c.restore()
    pin_at(c, NW_CAM, "kabul", "KABUL", t, vin(u_665), YEL, 30, "l")
    stamp(c, "BAGHAAWAT!", 1350, 300, 72, REGCOL["kabul"], seg(t, kw(u_bagh, "baghaawat") - 0.1, kw(u_bagh, "baghaawat") + 0.3))
    if kd > 0: skirmish(c, x + 10, y + 200, t, seg(t, kw(u_bagh, "baghaawat"), kw(u_bagh, "baghaawat") + 1.0), 3)
    SFX_MARK(kw(u_bagh, "baghaawat"), "stamp", -18); SFX_MARK(vin(u_665) + 0.4, "whoosh_long", -22)

AOD_CAM = (56.5, 31.5, 30.0)
ZB_CAM = (67.6, 32.1, 105.0)
@shot(vin(u_698), vin(u_nat))
def s36(c, t):
    _extra_regions(); bg(c, AOD_CAM)
    hl(c, AOD_CAM, "india", t, 0, flag_at=IND_FLAG, flag_label=False); hl(c, AOD_CAM, "zabul", t, 0, pole=False); hl(c, AOD_CAM, "kabul", t, 0, pole=False)
    hl(c, AOD_CAM, "iraq", t, vin(u_698) + 0.2, flag_at=(44.0, 32.6))                         # Hajjaj's base: Iraq (Kufa)
    pin_at(c, AOD_CAM, "kufa", "KUFA · HAJJAJ", t, vin(u_698) + 0.5, YEL, 26, "l")
    kfb = seg(t, us(u_aod) - 0.3, us(u_aod) + 0.2)
    timeline(c, t, 698, 1.0 - kfb, span=(620, 900), step=10, big_every=50)
    pts = [S(AOD_CAM, "kufa"), S(AOD_CAM, "iran_c"), S(AOD_CAM, "sistan"), S(AOD_CAM, "zabul")]
    km = seg(t, kw(u_bheji, "fauj") - 0.3, ue(u_aod))
    march(c, pts, km, t, RED, 10, n=8, size=44)
    if km >= 1: route(c, pts, 1.0, RED, 10, dash=False)
    title(c, "ARMY OF DESTRUCTION", 960, 170, 74, seg(t, us(u_aod) - 0.1, us(u_aod) + 0.4), RED)
    tag_note(c, '"tabaahi ki fauj"', 960, 222, seg(t, us(u_tab), us(u_tab) + 0.4), "#F1FAEE")
    army_block(c, 60, 720, 4, 10, 92, t, kfb)                                              # the formation itself
    kq = seg(t, us(u_hukm2) - 0.1, us(u_hukm2) + 0.4)
    if kq > 0:
        quote_card(c, 1040, 560, 800, ["destroy his strongholds,", "kill all his fighting men"], "Hajjaj ka hukum · Wikipedia: Zunbils", kq, t, [0, 1], seg(t, us(u_hukm2) + 0.3, ue(u_hukm2)))
    SFX_MARK(us(u_aod), "boom", -18); SFX_MARK(kw(u_bheji, "fauj"), "whoosh_long", -20)

# battle at Zabul: who falls, who turns back to Bust (sources give only the 5,000 survivors, no death count)
_AR = [(-150 + (i % 4) * 46 - (i // 4) * 14, -70 + (i // 4) * 44) for i in range(16)]
_SURV = (1, 6, 11, 14)
@shot(vin(u_nat), vin(u_peac))
def s37(c, t):
    _extra_regions()
    cam = fly(AOD_CAM, ZB_CAM, ease_io(seg(t, vin(u_nat), us(u_5000) - 0.2))); bg(c, cam)
    hl(c, cam, "india", t, 0, pole=False); hl(c, cam, "zabul", t, 0, pole=False); hl(c, cam, "kabul", t, 0, pole=False)
    title(c, "NATEEJA?", 960, 150, 70, seg(t, us(u_nat), us(u_nat) + 0.3), YEL)
    zx, zy = S(cam, "zabul"); bx, by = S(cam, "bust")
    kz = seg(t, us(u_nat) + 0.2, us(u_5000) + 0.1)
    if kz > 0:
        label(c, "JUNG: ZABUL · ZUNBIL KA ILAAKA", zx + 40, zy - 210, seg(kz, 0, 0.3), 28, border=REGCOL["zabul"])
        mt = seg(t, us(u_nat) + 0.3, us(u_nat) + 1.6)                                       # Zunbil fighters pour down from the hills
        for q in range(10):
            dx = lerp(320, 70, ease_out(mt)) + (q % 3) * 36; dy = -60 + (q // 3) * 40
            ic_soldier(c, zx + dx, zy + dy, 46, t * 1.3 + q, "#2A9D8F", int(255 * clamp(mt * 3)))
    ret = seg(t, kw(u_5000, "zinda") - 0.4, ue(u_5000) + 0.4)
    for i, (ox, oy) in enumerate(_AR):
        x, y = zx + ox, zy + oy
        if i in _SURV:
            if ret <= 0: ic_soldier(c, x, y, 44, t * 1.3 + i, "#F1FAEE", 255)
            continue
        fk = seg(t, us(u_nat) + 0.6 + (i * 7 % 16) * 0.09, us(u_nat) + 1.0 + (i * 7 % 16) * 0.09)
        fallen(c, x, y, 44, t + i, fk, face=-1 if i % 3 else 1)
    kc = seg(t, us(u_nat) + 0.4, us(u_5000) + 0.4)
    if 0 < kc < 1:
        for j in range(3): clash(c, zx - 30 + j * 50, zy - 40 + j * 30, (kc * 3 + j * 0.33) % 1, 0.7)
    if ret > 0:                                                                             # survivors turn round and walk back to Bust
        pr = route(c, [(zx - 60, zy - 10), ((zx + bx) / 2, min(zy, by) + 70), (bx, by)], ease_io(ret), "#C9D1DC", 5, dash=True)
        if pr and ret < 1:
            for q in range(4):
                f_ = clamp(ease_io(ret) - q * 0.05); sx, sy, _ = along(*pr, f_)
                c.save(); c.translate(sx, 0); c.scale(-1, 1); ic_soldier(c, 0, sy - 14 + (q % 2) * 8, 44, t * 1.3 + q, "#F1FAEE", 255); c.restore()
            sx, sy, _ = along(*pr, clamp(ease_io(ret))); pill(c, "5,000", sx, sy - 80, 26, RED)
    pin_at(c, cam, "bust", "BUST", t, kw(u_5000, "wapas") - 0.3, "#C9D1DC", 26, "l")
    stat_card(c, 1250, 300, 520, 300, "SIRF 5,000", "zinda wapas laute (Bust)", seg(t, kw(u_5000, "paanch") - 0.1, kw(u_5000, "paanch") + 0.4), RED)
    SFX_MARK(us(u_nat) + 0.4, "boom", -18); SFX_MARK(us(u_5000) - 0.2, "boom", -16)

@shot(vin(u_peac), vin(u_200))
def s38(c, t):
    _extra_regions(); bg(c, NW_CAM); hl(c, NW_CAM, "zabul", t, 0); hl(c, NW_CAM, "kabul", t, 0)
    timeline(c, t, 699, 1.0, span=(620, 900), step=10, big_every=50)
    title(c, "ARMY OF PEACOCKS", 960, 170, 70, seg(t, kw(u_peac, "Army") - 0.1, kw(u_peac, "Army") + 0.4), "#00BBF9")
    stat_card(c, 1300, 260, 420, 240, "40,000", "sainik", seg(t, kw(u_peac, "chaalis") - 0.1, kw(u_peac, "chaalis") + 0.4), "#00BBF9")
    p0, p1 = S(NW_CAM, "sistan"), S(NW_CAM, "zabul"); ku = seg(t, kw(u_ulta, "ulta") - 0.2, kw(u_ulta, "baaghi") + 0.3)
    if ku <= 0: arrow(c, p0, p1, seg(t, vin(u_peac), vin(u_peac) + 1.0), "#00BBF9", 14, 0.12)
    else: arrow(c, p1, to_screen(NW_CAM, 52.0, 32.0), ku, "#00BBF9", 14, -0.25)
    stamp(c, "BAAGHI!", 640, 300, 80, RED, seg(t, kw(u_ulta, "baaghi") - 0.1, kw(u_ulta, "baaghi") + 0.3))
    tag_note(c, "Hajjaj (Iraq) ki taraf", 520, 400, ku)
    SFX_MARK(kw(u_ulta, "baaghi"), "stamp", -18)

@shot(vin(u_200), vin(u_r1))
def s39(c, t):
    _extra_regions(); bg(c, NW_CAM); hl(c, NW_CAM, "zabul", t, 0); hl(c, NW_CAM, "kabul", t, 0); dim(c, 80)
    k = ease_io(seg(t, vin(u_200) + 0.3, ue(u_200)))
    timeline(c, t, lerp(665, 870, k) if t < us(u_870) else 870, 1.0, span=(650, 900), step=10, big_every=50, start=665,
             bracket=(665, 870, "200+ SAAL", seg(t, kw(u_200, "do sau") - 0.1, kw(u_200, "do sau") + 0.6)))
    x, y = S(NW_CAM, "kabul"); gate(c, x + 150, y - 60, 100, 0)
    stat_card(c, 1240, 240, 500, 260, "200+ SAAL", "Kabul-Zabul ki deewar", seg(t, kw(u_200, "do sau") - 0.1, kw(u_200, "do sau") + 0.4), YEL)
    kc = seg(t, kw(u_870, "870") - 0.1, kw(u_870, "870") + 0.4)
    if kc > 0: pill(c, "870 · SAFFARID RAJA (khilafat nahi)", 1490, 590, 26, "#5B6472", a=int(255 * clamp(kc * 1.5)))

@shot(vin(u_r1), vin(u_bacha))
def s40(c, t):
    c.clear(hexc(NAVY))
    slots(c, t, seg(t, us(u_r1b) - 0.3, us(u_r1b) + 0.4), 1.0, 520, labels=raaz_labels(1 if t > us(u_r1b) - 0.1 else 0))
    SFX_MARK(us(u_r1b) - 0.2, "lock", -16)

@shot(vin(u_bacha), vin(u_r2))
def s41(c, t):
    DS_CAM = (66.8, 26.6, 62.0)
    _extra_regions(); bg(c, DS_CAM)
    hl(c, DS_CAM, "desert", t, kw(u_makr, "Makran"))
    pts = [S(DS_CAM, "makran"), S(DS_CAM, "sindh"), S(DS_CAM, "thar")]
    route(c, pts, seg(t, kw(u_makr, "Makran") - 0.1, kw(u_makr, "Thar") + 0.5), "#E9C46A", 9, dash=True)
    for key, nm in (("makran", "MAKRAN"), ("sindh", "SINDH"), ("thar", "THAR")):
        x, y = S(DS_CAM, key); label(c, nm, x, y - 34, seg(t, kw(u_makr, nm.title()) - 0.1, kw(u_makr, nm.title()) + 0.3), 30, border="#E9C46A")
    title(c, "SABSE MUSHKIL RAASTA", 960, 150, 56, seg(t, vin(u_bacha), vin(u_bacha) + 0.5), "#E9C46A")
    kb = seg(t, us(u_yumar) - 0.2, us(u_yumar) + 0.7)
    if kb > 0:
        bookmark(c, lerp(1840, 1500, ease_io(kb)), lerp(90, 420, ease_io(kb)), lerp(60, 120, ease_io(kb)))
    name_card(c, '"KHARAAB, GAREEB ZAMEEN"', "Khalifa Umar ki raay (Chapter 1)", 1460, 640, seg(t, us(u_kg) - 0.2, us(u_kg) + 0.3), "#C8A26A")

@shot(vin(u_r2), vin(u_sirf_r))
def s42(c, t):
    c.clear(hexc(NAVY))
    slots(c, t, 1 + seg(t, kw(u_r2, "registaan") - 0.3, kw(u_r2, "registaan") + 0.4), 1.0, 520, labels=raaz_labels(2 if t > kw(u_r2, "registaan") - 0.1 else 1))
    SFX_MARK(kw(u_r2, "registaan") - 0.2, "lock", -16)

@shot(vin(u_sirf_r), HOSTSEG["H2"][0])
def s43(c, t):
    bg(c, IN_CAM, {"IND": (SAFF, 110)})
    for j, (lo, la) in enumerate([(70.5, 26.0), (72.0, 24.5), (71.0, 22.5), (73.5, 21.5), (74.6, 24.9), (75.8, 23.2)]):
        x, y = to_screen(IN_CAM, lo, la); shield(c, x, y, 60, SAFF, 255, seg(t, us(u_asli) - 0.4 + j * 0.08, us(u_asli) + j * 0.08))
    title(c, "ASLI JAWAB?", 960, 170, 70, seg(t, us(u_asli) - 0.1, us(u_asli) + 0.3), YEL)

@shot(HOSTSEG["H2"][0], vin(U("723.")), "cut")
def h2(c, t):
    host_frame(c, "H2", t)
    for i, st_ in enumerate(("GUJARAT", "RAJASTHAN", "MP", "KASHMIR")):
        k = seg(t, kw(U("Gujarat, Rajasthan"), st_.title() if st_ != "MP" else "MP") - 0.1, kw(U("Gujarat, Rajasthan"), st_.title() if st_ != "MP" else "MP") + 0.3)
        if k > 0: pill(c, st_, 360 + i * 400, 960, 34, "#16223A", a=int(255 * clamp(k * 1.5)))
    kc = seg(t, us(U("Comment mein likho, kyunki")) - 0.1, us(U("Comment mein likho, kyunki")) + 0.3)
    if kc > 0: pill(c, "COMMENT KARO: AAPKA STATE?", 960, 880, 40, RED, a=int(255 * clamp(kc * 1.5)))
HOSTS.append((HOSTSEG["H2"][0], vin(U("723."))))


# ======================================================================= CHAPTER 4: AL-MAHFUZA KA RAAZ
PL.update(dict(ujjain=(75.78, 23.18), kutch=(69.8, 23.4), saurashtra=(70.8, 21.7), bhinmal=(72.27, 25.0), malwa=(76.5, 23.6),
               navsari=(72.92, 20.95), vallabhi=(71.88, 21.89), chittor=(74.63, 24.89), mansura=(68.82, 25.95), gwalior=(78.18, 26.22),
               syria2=(38.0, 34.5), iraq2=(44.0, 33.0)))
def _state_regions():
    if "gujarat" in REG: return
    _extra_regions()
    j = json.load(open(MAPDATA + "states.geojson")); st = {}
    for f in j["features"]:
        p_ = f["properties"]
        if p_.get("iso_a2") == "IN": st[p_["name"]] = shape(f["geometry"]).buffer(0)
    REG["gujarat"] = st["Gujarat"]; REG["rajasthan"] = st["Rajasthan"]; REG["mp"] = st["Madhya Pradesh"]
    REG["pratihara"] = unary_union([st[k] for k in ("Rajasthan", "Gujarat", "Madhya Pradesh", "Uttar Pradesh", "Haryana", "Delhi", "Bihar")]).buffer(0.05)
    REG["raidzone"] = unary_union([st["Gujarat"], st["Rajasthan"].intersection(box(68, 23, 75.5, 27.5)), st["Madhya Pradesh"].intersection(box(74, 21.5, 77.5, 24.5))]).buffer(0.05)
    REGCOL.update({"gujarat": "#F15BB5", "rajasthan": "#F8961E", "mp": "#9B5DE5", "pratihara": "#E76F51", "raidzone": GREEN})
    IN_ = WM.geoms["IND"]; U2 = lambda ks: unary_union([st[k] for k in ks]).buffer(0.02).intersection(IN_)
    REG["kashmir"] = IN_.intersection(box(72.4, 32.0, 80.6, 37.2)).difference(unary_union([st["Himachal Pradesh"], st["Punjab"]]).buffer(0.02)).buffer(0)
    REG["kannauj"] = U2(["Uttar Pradesh", "Uttarakhand", "Haryana", "Delhi", "Punjab", "Himachal Pradesh", "Chandigarh"]).difference(REG["kashmir"])
    REG["deccan"] = U2(["Maharashtra", "Karnataka", "Telangana", "Goa"])
    REG["east"] = U2(["Bihar", "Jharkhand", "West Bengal", "Odisha", "Chhattisgarh"])
    REG["south"] = U2(["Tamil Nadu", "Kerala", "Andhra Pradesh", "Puducherry"])
    REG["kamarupa"] = U2(["Assam", "Meghalaya", "Arunachal Pradesh", "Nagaland", "Manipur", "Mizoram", "Tripura", "Sikkim"])
    REGCOL.update({"kashmir": "#B5179E", "kannauj": "#4CC9F0", "deccan": "#43AA8B", "east": "#F9C74F", "south": "#F94144", "kamarupa": "#4D908E"})
def sindh_base(c, cam, t, extra=0.0):
    bg(c, cam); draw_region(c, cam, "sindh", GREEN, 200)
    if extra > 0: draw_region(c, cam, "raidzone", GREEN, int(150 * extra))

u_723 = U("723."); u_jun = U("Junayd."); u_aage = U("Aur wo sabse aage"); u_kutch = U("Kutch."); u_saur = U("Saurashtra.")
u_bhar = U("Bharuch."); u_bhin = U("Bhinmal."); u_mal = U("Malwa."); u_teens = U("Teen saal mein"); u_ujj = U("Ujjain tak")
u_prat = U("Pratihara vansh"); u_behes = U("Ye ladai kab"); u_lekin_a = U("Lekin aage jo hua"); u_tamim = U("Agle governor Tamim")
u_syria = U("Syria aur Yemen"); u_line = U("Aur ab wo line"); u_731 = U("731."); u_hakam = U("Naya governor Al-Hakam")
u_bal = U("Arab itihaskar Baladhuri"); u_hind = U("Hind ke log"); u_musal = U("Aur Musalmanon ke paas"); u_isliye = U("Isliye Al-Hakam")
u_mah2 = U("Al-Mahfuza.", 1); u_sur2 = U("Surakshit."); u_paas = U("Paas mein hi"); u_mans = U("Al-Mansura"); u_rajd = U("Yahi aage Arab Sindh")
u_socho = U("Socho."); u_ekshe = U("Ek shehar ka naam"); u_dar = U("Ek mein dar"); u_haar = U("Aur Al-Hakam haar"); u_guj = U("Usne phir Gujarat")
u_736 = U("Lekin 736"); u_737 = U("737."); u_maange = U("Al-Hakam ne Damascus"); u_3000 = U("Teen hazaar bheje"); u_kahan = U("Kahan gaye?")
u_raazc5 = U("Ye raaz chapter"); u_navs = U("Aur phir aaya Navsari"); u_patra = U("Navsari mein mila"); u_pakka2 = U("Ye is poori kahani")
u_isme = U("Isme likha hai"); u_pulak = U("Aur yahan Chalukya"); u_740 = U("Ek saal baad, 740"); u_mara = U("Al-Hakam khud")
u_chit = U("Usi saal Chittor"); u_bappa = U("Mewar ki parampara"); u_haala = U("Haalaanki"); u_743 = U("Aur 743 tak"); u_khatam2 = U("Rajasthan aur Gujarat ki saari")
u_r3 = U("Raaz number teen"); u_baar = U("Indian rajya ek baar"); u_alag = U("Alag alag raja"); u_blank = U("Aur historian Blankinship")
u_yahi = U("Yahi Pratihara"); u_851 = U("Sau saal se zyada")
CHAPTERS.append((4, "AL-MAHFUZA KA RAAZ", u_723)); chapter(4, "AL-MAHFUZA KA RAAZ", u_723)
GJ_CAM = (71.5, 24.2, 62.0)

@shot(vin(u_723), vin(u_kutch), "cut")
def s44(c, t):
    _state_regions(); sindh_base(c, GJ_CAM, t)
    timeline(c, t, 723, 1.0, span=(700, 800), step=5, big_every=10)
    portrait(c, "JUNAYD", 1520, 430, seg(t, us(u_jun) - 0.2, us(u_jun) + 0.3), col="#3D6B4F", hat="helmet")
    arrow(c, S(GJ_CAM, "sindh"), S(GJ_CAM, "malwa"), seg(t, us(u_aage), ue(u_aage)), GREEN, 12, 0.15)
    if t > us(u_aage): label(c, "SABSE AAGE", *S(GJ_CAM, "malwa"), seg(t, ue(u_aage) - 0.2, ue(u_aage) + 0.2), 30, border=GREEN)
    label(c, "SINDH KA GOVERNOR", *S(GJ_CAM, "sindh"), seg(t, vin(U("Sindh ka naya governor")), vin(U("Sindh ka naya governor")) + 0.4), 28, border=GREEN)

RAIDS = [("kutch", "KUTCH", u_kutch, "gujarat"), ("saurashtra", "SAURASHTRA", u_saur, None), ("bharuch", "BHARUCH", u_bhar, None),
         ("bhinmal", "BHINMAL", u_bhin, "rajasthan"), ("malwa", "MALWA", u_mal, "mp")]
@shot(vin(u_kutch), vin(u_prat))
def s45(c, t):
    _state_regions(); sindh_base(c, GJ_CAM, t, seg(t, vin(u_teens), ue(u_teens)))
    timeline(c, t, lerp(723, 726, seg(t, vin(u_kutch), ue(u_teens))), 1.0, span=(700, 800), step=5, big_every=10)
    src = S(GJ_CAM, "sindh")
    for i, (key, nm, uu, reg) in enumerate(RAIDS):
        t0 = us(uu)
        if reg: hl(c, GJ_CAM, reg, t, t0)
        arrow(c, src, S(GJ_CAM, key), seg(t, t0 - 0.25, t0 + 0.25), GREEN, 7, 0.12)
        x, y = S(GJ_CAM, key); label(c, nm, x, y - 30, seg(t, t0, t0 + 0.25), 28, border=REGCOL.get(reg, GREEN) if reg else GREEN)
        SFX_MARK(t0, "pop", -22)
    tag_note(c, "aaj ke rajya-seemayein sirf pehchaan ke liye", 960, 880, seg(t, us(u_kutch), us(u_kutch) + 0.5))
    ku = seg(t, kw(u_ujj, "Ujjain") - 0.3, kw(u_ujj, "Ujjain") + 0.3)
    arrow(c, src, S(GJ_CAM, "ujjain"), ku, GREEN, 8, 0.1)
    x, y = S(GJ_CAM, "ujjain"); shield(c, x, y, 80, SAFF, 255, seg(t, kw(u_ujj, "lekin") - 0.2, kw(u_ujj, "lekin") + 0.3))
    clash(c, x, y, seg(t, kw(u_ujj, "lekin") - 0.3, kw(u_ujj, "lekin") + 0.5))
    label(c, "UJJAIN", x, y - 70, ku, 28, border=SAFF)
    stamp(c, "QABZA NAHI", x - 40, y + 110, 44, SAFF, seg(t, kw(u_ujj, "haath") - 0.1, kw(u_ujj, "haath") + 0.3))

@shot(vin(u_prat), vin(u_tamim))
def s46(c, t):
    _state_regions(); sindh_base(c, GJ_CAM, t, 1.0); dim(c, 110)
    x, y = S(GJ_CAM, "ujjain"); pin(c, x, y, "AVANTI / UJJAIN", seg(t, vin(u_prat), vin(u_prat) + 0.4), SAFF, size=26, t=t)
    portrait(c, "NAGABHATA I", 300, 470, seg(t, kw(u_prat, "Nagabhata") - 0.2, kw(u_prat, "Nagabhata") + 0.3), col="#E76F51", hat="crown", w=260, h=320)
    doc(c, "pratihara_mlechcha", 560, 220, 900, 380, t, seg(t, vin(u_prat) + 0.3, vin(u_prat) + 0.9), kw(u_prat, "taaqatwar") - 0.1, 2.2)
    pill(c, "Gwalior shilalekh (baad ka, 9vi sadi)", 1010, 660, 24, "#5B4636", a=int(255 * clamp(seg(t, vin(u_prat) + 0.8, vin(u_prat) + 1.3) * 1.5)))
    kb = seg(t, us(u_behes) - 0.1, us(u_behes) + 0.3)
    if kb > 0: pill(c, "HISTORIANS MEIN BEHES", 1010, 740, 32, RED, a=int(255 * clamp(kb * 1.5)))
    km = seg(t, us(u_lekin_a), us(u_lekin_a) + 0.6)
    if km > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint("#141019", int(255 * km))); manuscript(c, 960, 520, 560, km)

@shot(vin(u_tamim), vin(u_line))
def s47(c, t):
    _state_regions(); k = ease_io(seg(t, vin(u_tamim) + 0.5, ue(u_tamim)))
    sindh_base(c, GJ_CAM, t, 1 - k)
    timeline(c, t, 726, 1.0, span=(700, 800), step=5, big_every=10)
    portrait(c, "TAMIM", 1560, 400, seg(t, kw(u_tamim, "Tamim") - 0.2, kw(u_tamim, "Tamim") + 0.3), col="#3D6B4F", hat="helmet", w=260, h=320)
    for j in range(5):
        fx, fy = to_screen(GJ_CAM, 70.0 + j * 1.3, 23.0 + (j % 2) * 1.2)
        fort(c, fx, fy, 70, 1.0, a=int(255 * seg(t, vin(u_syria) - 0.4, vin(u_syria))))
        kw_ = seg(t, kw(u_syria, "chhodkar") - 0.3 + j * 0.1, kw(u_syria, "chhodkar") + 1.6 + j * 0.1)
        if kw_ > 0: ic_soldier(c, fx - 60 - 300 * ease_in(kw_), fy + 10, 60, t, "#C9D1DC", int(255 * (1 - kw_)))
    kc = seg(t, kw(u_syria, "chhodkar"), kw(u_syria, "chhodkar") + 0.4)
    if kc > 0: pill(c, "CHAUKIYAN KHAALI", 960, 200, 40, RED, a=int(255 * clamp(kc * 1.5)))

@shot(vin(u_line), vin(u_731))
def s48(c, t):
    c.clear(hexc("#141019"))
    manuscript(c, 960, 520, 620, 1.0, cover_k=1.0 - seg(t, ue(u_line) - 0.4, ue(u_line)), lock_k=1.0, lock_open=seg(t, kw(u_line, "wada") - 0.2, kw(u_line, "wada") + 0.5))
    SFX_MARK(kw(u_line, "wada"), "lock", -16)

@shot(vin(u_731), vin(u_bal))
def s49(c, t):
    _state_regions(); sindh_base(c, GJ_CAM, t)
    timeline(c, t, 731, 1.0, span=(700, 800), step=5, big_every=10)
    arrow(c, to_screen(GJ_CAM, 63.5, 26.0), S(GJ_CAM, "sindh"), seg(t, vin(u_731) + 0.2, ue(u_hakam)), GREEN, 10, 0.1)
    portrait(c, "AL-HAKAM", 1500, 430, seg(t, kw(u_hakam, "Al-Hakam") - 0.2, kw(u_hakam, "Al-Hakam") + 0.3), col="#3D6B4F", hat="helmet")

@shot(vin(u_bal), vin(u_isliye))
def s50(c, t):
    c.clear(hexc("#141019"))
    manuscript(c, 330, 540, 380, 1.0, hl_k=seg(t, us(u_musal), ue(u_musal)), ang=-4)
    lines = ["The people of India had returned to idolatry", "excepting those of Kassa, and the Musulmans", "had no place of security in which they", "could take refuge..."]
    kq = seg(t, vin(u_bal), vin(u_bal) + 0.6)
    if kq > 0:
        al = int(255 * clamp(kq * 1.5)); rrect(c, 640, 250, 1840, 800, 24, "#F4F1EA", al, shadow=26)
        text(c, "“", 670, 380, 150, RED, FT_BLACK, "l", al)
        tv = vt_now(t); HQ = vo_to_video(vin(u_isliye) - 0.02)                    # quote finishes inside the silent beat
        wt = [(vo_to_video(us(u_hind)), vo_to_video(us(u_hind)) + 2.6)] + [(vo_to_video(us(u_musal)) + j * 1.25, vo_to_video(us(u_musal)) + (j + 1) * 1.25) for j in range(3)]
        for i, ln in enumerate(lines):
            yy = 380 + i * 80; w_ = text_w(ln, 44, FT_SEMI); a0, a1 = wt[i]
            wk = seg(tv, a0, a1 if i < 3 else min(a1, HQ - 0.1))                    # handwriting reveal, left -> right
            if wk <= 0: continue
            hk = seg(tv, a1 + 0.1, a1 + 0.9) if i >= 1 else 0
            if hk > 0:
                hp = paint("#FFD166", int(190 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
                c.drawRect(skia.Rect(760, yy - 46, 760 + w_ * ease_out(hk), yy + 14), hp)
            c.save(); c.clipRect(skia.Rect(750, yy - 60, 760 + w_ * wk, yy + 24)); text(c, ln, 760, yy, 44, "#0F1B2D", FT_SEMI, "l", al); c.restore()
            if wk < 1:
                qx, qy = 760 + w_ * wk, yy - 6
                qp = skia.Path(); qp.moveTo(qx, qy); qp.quadTo(qx - 8, qy - 60, qx + 28, qy - 104); qp.quadTo(qx + 6, qy - 50, qx, qy)
                c.drawPath(qp, paint("#5A3B22", al)); c.drawCircle(qx, qy, 3, paint("#1A1410", al))
        text(c, "al-Baladhuri, Futuh al-Buldan · tr. Elliot & Dowson (1867)", 1810, 770, 24, "#5B6472", FT_SEMI, "r", al)
    SFX_MARK(us(u_musal), "boom", -18)

@shot(vin(u_isliye), vin(u_socho))
def s51(c, t):
    _state_regions(); cam = (68.9, 25.7, 120.0); bg(c, cam); draw_region(c, cam, "sindh", GREEN, 200)
    x, y = S(cam, "mahfuza"); fort(c, x, y, 220, seg(t, kw(u_isliye, "shehar") - 0.4, kw(u_isliye, "shehar") + 0.8))
    label(c, "AL-MAHFUZA (andaazan)", x - 330, y + 40, seg(t, us(u_mah2) - 0.1, us(u_mah2) + 0.3), 30)
    kt = seg(t, us(u_sur2) - 0.1, us(u_sur2) + 0.3)
    if kt > 0: title(c, "= SURAKSHIT", x - 330, y + 120, 50, kt, YEL)
    x2, y2 = S(cam, "mansura")
    name_card(c, "AMR", "Muhammad bin Qasim ka beta", 1500, 860, seg(t, kw(u_paas, "Amr") - 0.2, kw(u_paas, "Amr") + 0.3) * (1 - seg(t, us(u_rajd), us(u_rajd) + 0.3)))
    km = seg(t, kw(u_mans, "Al-Mansura") - 0.1, kw(u_mans, "Al-Mansura") + 0.4)
    if km > 0: crown(c, x2, y2 - 40, 90 * back(km), YEL, int(255 * clamp(km * 1.5))); label(c, "AL-MANSURA = VIJAYI", x2 + 330, y2 - 150, km, 30, border=YEL)
    kr = seg(t, kw(u_rajd, "rajdhani") - 0.1, kw(u_rajd, "rajdhani") + 0.4)
    if kr > 0: pill(c, "ARAB SINDH KI RAJDHANI", x2 + 330, y2 - 80, 26, RED, a=int(255 * clamp(kr * 1.5)))
    SFX_MARK(kw(u_isliye, "shehar"), "build", -20)

@shot(vin(u_socho), vin(u_haar))
def s52(c, t):
    c.clear(hexc(NAVY))
    for i, (word, ttl_, sub, col) in enumerate((("surakshit", "AL-MAHFUZA", "SURAKSHIT", "#00BBF9"), ("vijayi", "AL-MANSURA", "VIJAYI", YEL))):
        k = seg(t, kw(u_ekshe, word) - 0.2, kw(u_ekshe, word) + 0.3)
        if k <= 0: continue
        x = 560 + i * 800
        if i == 0: shield(c, x, 440, 220, col, 255, k)
        else: crown(c, x, 440, 200 * back(k), col, int(255 * clamp(k * 1.5)))
        text(c, ttl_, x, 690, 56, "#F1FAEE", FT_BLACK, "c", int(255 * clamp(k * 1.5))); text(c, sub, x, 750, 36, col, FT_BLACK, "c", int(255 * clamp(k * 1.5)))
    for i, word in enumerate(("dar", "ummeed")):
        k = seg(t, kw(u_dar, word) - 0.1, kw(u_dar, word) + 0.3)
        if k > 0: pill(c, word.upper(), 560 + i * 800, 840, 40, RED if i == 0 else GREEN, a=int(255 * clamp(k * 1.5)))
    title(c, "SOCHO...", 960, 180, 70, seg(t, us(u_socho), us(u_socho) + 0.3), YEL)

@shot(vin(u_haar), vin(u_737))
def s53(c, t):
    _state_regions(); sindh_base(c, GJ_CAM, t)
    hl(c, GJ_CAM, "gujarat", t, kw(u_guj, "Gujarat"))
    src = S(GJ_CAM, "sindh")
    for j, key in enumerate(("saurashtra", "vallabhi", "bharuch")):
        arrow(c, src, S(GJ_CAM, key), seg(t, kw(u_guj, "Gujarat") + j * 0.2, kw(u_guj, "Gujarat") + 0.7 + j * 0.2), GREEN, 7, 0.1)
    timeline(c, t, 736 if t > us(u_736) else 733, 1.0, span=(700, 800), step=5, big_every=10)
    kb = seg(t, kw(u_736, "Jayabhata") - 0.2, kw(u_736, "Jayabhata") + 0.3)
    x, y = S(GJ_CAM, "bharuch"); pin_at(c, GJ_CAM, "bharuch", "BHARUCH", t, kw(u_736, "Bharuch"), SAFF, 26)
    pin_at(c, GJ_CAM, "vallabhi", "VALLABHI", t, kw(u_736, "Vallabhi"), SAFF, 26, "l")
    shield(c, x - 90, y - 10, 90, SAFF, 255, kb)
    clash(c, x - 60, y, seg(t, kw(u_736, "haraya") - 0.2, kw(u_736, "haraya") + 0.6))
    if kb > 0: label(c, "JAYABHATA IV (736 ka shilalekh)", 960, 200, kb, 32, border=SAFF)
    SFX_MARK(kw(u_736, "haraya"), "stamp", -18)

@shot(vin(u_737), vin(u_navs))
def s54(c, t):
    cam = (52.0, 30.0, 14.0); bg(c, cam); draw_region(c, cam, "caliph", GREEN, 110)
    timeline(c, t, 737, 1.0, span=(700, 800), step=5, big_every=10)
    p0 = S(cam, "syria2"); p1 = S(cam, "sindh"); mid = (lerp(p0[0], p1[0], 0.48), lerp(p0[1], p1[1], 0.48) - 40)
    k = seg(t, kw(u_3000, "Teen hazaar") - 0.2, kw(u_3000, "lekin"))
    if k > 0:
        route(c, [p0, mid], ease_out(k), YEL, 10, dash=False)
        x_, y_ = lerp(p0[0], mid[0], ease_out(k)), lerp(p0[1], mid[1], ease_out(k)); pill(c, "3,000", x_, y_ - 50, 32, YEL, fg=NAVY, shadow=6)
    kq = seg(t, kw(u_3000, "nahi") - 0.1, kw(u_3000, "nahi") + 0.3)
    if kq > 0: ic_question(c, mid[0] + 60, mid[1] - 20, 120 * back(kq), int(255 * clamp(kq * 1.5)), RED)
    kf = seg(t, us(u_raazc5), us(u_raazc5) + 0.8)
    if kf > 0: pill(c, "3,000 ?", lerp(mid[0], 1780, ease_io(kf)), lerp(mid[1] - 50, 90, ease_io(kf)), 30, RED, shadow=6)
    title(c, "KAHAN GAYE?", 960, 200, 70, seg(t, us(u_kahan), us(u_kahan) + 0.3), RED)
    name_card(c, "AL-HAKAM: AUR SAINIK BHEJO", "737", 960, 820, seg(t, us(u_maange) - 0.1, us(u_maange) + 0.4), GREEN) if t < us(u_3000) else None

NV_CAM = (72.9, 21.2, 150.0)
@shot(vin(u_navs), vin(u_isme))
def s55(c, t):
    _state_regions(); cam = fly(GJ_CAM, NV_CAM, ease_io(seg(t, vin(u_navs), vin(u_navs) + 1.6)))
    bg(c, cam); hl(c, cam, "gujarat", t, vin(u_navs))
    x, y = S(cam, "navsari"); pin(c, x, y, "NAVSARI", seg(t, kw(u_navs, "Navsari"), kw(u_navs, "Navsari") + 0.4), YEL, size=34, t=t)
    timeline(c, t, 739, seg(t, us(u_patra), us(u_patra) + 0.4), span=(700, 800), step=5, big_every=10)
    kd = seg(t, us(u_patra) + 0.2, us(u_patra) + 0.8)
    doc(c, "navsari", 760, 230, 1060, 470, t, kd, kw(u_pakka2, "pakka") - 0.4, 1.4, focus=0)
    kp = seg(t, kw(u_patra, "taambe") - 0.2, kw(u_patra, "taambe") + 0.3)
    if kp > 0:
        rrect(c, 130, 300, 640, 640, 30, "#B87333", int(255 * clamp(kp * 1.5)), shadow=20)
        for r in range(7): c.drawRect(skia.Rect(170, 350 + r * 38, 600 - (r % 3) * 40, 362 + r * 38), paint("#7A4A1E", int(220 * clamp(kp * 1.5))))
        c.drawCircle(385, 300, 26, paint("#8A5523", int(255 * clamp(kp * 1.5))))
        text(c, "COPPER PLATE · 739", 385, 690, 30, "#F1FAEE", FT_BLACK, "c", int(255 * clamp(kp * 1.5)))
    kb = seg(t, kw(u_pakka2, "pakka") - 0.1, kw(u_pakka2, "pakka") + 0.3)
    if kb > 0: stamp(c, "SABSE PAKKA SABOOT", 1290, 780, 46, GREEN, kb)
    SFX_MARK(kw(u_navs, "Navsari"), "riser", -20)

PLATE = [("SINDH", "sindh"), ("KUTCH", "kutch"), ("SAURASHTRA", "saurashtra"), ("CHAVOTAKA", None), ("MAURYA", None), ("GURJARA", "bhinmal")]
@shot(vin(u_isme), vin(u_740))
def s56(c, t):
    _state_regions(); bg(c, GJ_CAM); draw_region(c, GJ_CAM, "sindh", GREEN, 150)
    pts = [S(GJ_CAM, "sindh"), S(GJ_CAM, "kutch"), S(GJ_CAM, "saurashtra"), S(GJ_CAM, "navsari")]
    k = seg(t, kw(u_isme, "Sindh") - 0.2, kw(u_isme, "Navsari") + 0.2)
    pb = route(c, pts, k, RED, 9, dash=False) if t < us(u_pulak) + 0.4 else None
    for i, (nm, key) in enumerate(PLATE):
        kk = seg(t, kw(u_isme, "Sindh") + i * 0.45, kw(u_isme, "Sindh") + i * 0.45 + 0.3)
        pill(c, nm, 260, 230 + i * 70, 28, "#5B6472", a=int(255 * clamp(kk * 1.5))) if kk > 0 else None
    tag_note(c, "Navsari plate ki list (kuch naam aaj pehchaan mein behes)", 300, 680, seg(t, kw(u_isme, "Sindh"), kw(u_isme, "Sindh") + 0.5))
    pin_at(c, GJ_CAM, "navsari", "NAVSARI", t, kw(u_isme, "Navsari"), YEL, 28)
    kp = seg(t, kw(u_pulak, "Avanijanashraya") - 0.3, kw(u_pulak, "Avanijanashraya") + 0.3)
    portrait(c, "AVANIJANASHRAYA PULAKESHIN", 1500, 420, kp, col="#E76F51", hat="crown", w=380, h=380)
    if t > kw(u_pulak, "haraaya") - 0.2:
        kx = seg(t, kw(u_pulak, "haraaya") - 0.2, kw(u_pulak, "haraaya") + 0.6); x, y = S(GJ_CAM, "navsari")
        for j in range(12):
            ang = j / 12 * math.tau; d = 20 + 200 * ease_out(kx)
            c.drawRect(skia.Rect(x + d * math.cos(ang) - 9, y + d * math.sin(ang) - 4, x + d * math.cos(ang) + 9, y + d * math.sin(ang) + 4), paint(RED, int(255 * (1 - kx))))
        shield(c, x, y, 110, SAFF, 255, kx)
    xn, yn = S(GJ_CAM, "navsari"); clash(c, xn, yn, seg(t, kw(u_pulak, "haraaya") - 0.3, kw(u_pulak, "haraaya") + 0.6), 1.3)
    SFX_MARK(kw(u_pulak, "haraaya"), "boom", -16)

@shot(vin(u_740), vin(u_bappa))
def s57(c, t):
    _state_regions(); bg(c, GJ_CAM); draw_region(c, GJ_CAM, "sindh", GREEN, 150)
    timeline(c, t, 740, 1.0, span=(700, 800), step=5, big_every=10)
    portrait(c, "AL-HAKAM", 420, 440, 1.0, grey=seg(t, kw(u_mara, "maara") - 0.2, kw(u_mara, "maara") + 0.4), col="#3D6B4F", hat="helmet", w=280, h=330)
    hl(c, GJ_CAM, "gujarat", t, kw(u_mara, "Saurashtra"))
    pin_at(c, GJ_CAM, "saurashtra", "SAURASHTRA", t, kw(u_mara, "Saurashtra"), RED, 26)
    x, y = S(GJ_CAM, "chittor"); kc = seg(t, kw(u_chit, "Chittor") - 0.1, kw(u_chit, "Chittor") + 0.3)
    if kc > 0:
        hl(c, GJ_CAM, "rajasthan", t, kw(u_chit, "Chittor"))
        fort(c, x, y, 110, 1.0); label(c, "CHITTOR (MORI)", x, y - 90, kc, 28, border=REGCOL["rajasthan"])
        kr = seg(t, kw(u_chit, "naakaam") - 0.3, kw(u_chit, "naakaam") + 0.6); clash(c, x, y, kr)
        for j in range(10):
            ang = j / 10 * math.tau; d = 120 + 180 * ease_in(kr)
            c.drawLine(x + d * math.cos(ang), y + d * math.sin(ang), x + (d - 30) * math.cos(ang), y + (d - 30) * math.sin(ang), paint(GREEN, int(255 * (1 - kr)), stroke=5, cap_round=True))

@shot(vin(u_bappa), vin(u_743))
def s58(c, t):
    _state_regions(); bg(c, GJ_CAM); hl(c, GJ_CAM, "rajasthan", t, 0); dim(c, 100)
    portrait(c, "BAPPA RAWAL", 760, 500, seg(t, kw(u_bappa, "Bappa") - 0.2, kw(u_bappa, "Bappa") + 0.3), col="#F8961E", hat="crown")
    kp = seg(t, kw(u_bappa, "parampara") - 0.1, kw(u_bappa, "parampara") + 0.3)
    if kp > 0: pill(c, "MEWAR KI PARAMPARA", 1250, 420, 34, "#5B4636", a=int(255 * clamp(kp * 1.5)))
    kb = seg(t, us(u_haala) - 0.1, us(u_haala) + 0.3)
    if kb > 0: pill(c, "PEHCHAAN PAR BEHES", 1250, 520, 34, RED, a=int(255 * clamp(kb * 1.5)))

@shot(vin(u_743), vin(u_r3))
def s59(c, t):
    _state_regions(); k = ease_io(seg(t, us(u_khatam2), ue(u_khatam2)))
    sindh_base(c, GJ_CAM, t, 1 - k)
    timeline(c, t, 743, 1.0, span=(700, 800), step=5, big_every=10)
    title(c, "743 TAK?", 960, 180, 70, seg(t, us(u_743), us(u_743) + 0.3), YEL)
    for j, key in enumerate(("bhinmal", "saurashtra", "bharuch", "malwa")):
        arrow(c, S(GJ_CAM, key), S(GJ_CAM, "sindh"), seg(t, us(u_khatam2) + j * 0.15, ue(u_khatam2) + j * 0.1), RED, 7, -0.12)
    stamp(c, "SAARI JEET KHATAM", 1300, 420, 50, SAFF, seg(t, kw(u_khatam2, "khatam") - 0.1, kw(u_khatam2, "khatam") + 0.3))

@shot(vin(u_r3), vin(u_blank))
def s60(c, t):
    c.clear(hexc(NAVY))
    slots(c, t, 2 + seg(t, us(u_baar) - 0.3, us(u_baar) + 0.4), 1.0, 440, labels=raaz_labels(3 if t > us(u_baar) - 0.1 else 2))
    for i, (nm, col) in enumerate((("PRATIHARA", "#E76F51"), ("CHALUKYA", "#F15BB5"), ("GURJARA (BHARUCH)", "#9B5DE5"), ("MORI (CHITTOR)", "#F8961E"))):
        k = seg(t, us(u_alag) + i * 0.3, us(u_alag) + 0.3 + i * 0.3)
        if k > 0:
            x = 960 + (i - 1.5) * 380; shield(c, x, 760, 70, col, 255, k); text(c, nm, x, 850, 24, "#F1FAEE", FT_BLACK, "c", int(255 * clamp(k * 1.5)))
    SFX_MARK(us(u_baar) - 0.2, "lock", -16)

@shot(vin(u_blank), vin(u_yahi))
def s61(c, t):
    c.clear(hexc(NAVY))
    k = ease_io(seg(t, kw(u_blank, "bada") - 0.5, kw(u_blank, "bada") + 1.2))
    for j in range(8):
        a0 = j / 8 * math.tau; x = 960 + 380 * (1 - k) * math.cos(a0); y = 520 + 260 * (1 - k) * math.sin(a0)
        shield(c, x, y, lerp(60, 0, k) if k < 0.98 else 0, SAFF, 255, 1.0) if k < 0.98 else None
    shield(c, 960, 520, lerp(40, 220, k), SAFF, 255, 1.0)
    for i, (sx, sy) in enumerate(((150, 520), (1770, 520))):
        arrow(c, (sx, sy), (lerp(sx, 960, 0.55), 520), seg(t, vin(u_blank), vin(u_blank) + 0.8), GREEN, 8, 0)
    name_card(c, "KHALID BLANKINSHIP", "historian · The End of the Jihad State (1994)", 960, 180, seg(t, kw(u_blank, "Blankinship") - 0.2, kw(u_blank, "Blankinship") + 0.3))
    tag_note(c, "hamle -> bade aur mazboot Indian rajya", 960, 860, seg(t, kw(u_blank, "mazboot") - 0.2, kw(u_blank, "mazboot") + 0.3), "#F1FAEE")

PH_CAM = (79.0, 25.0, 30.0)
@shot(vin(u_yahi), vin(u_851))
def s62(c, t):
    _state_regions(); bg(c, PH_CAM); draw_region(c, PH_CAM, "sindh", GREEN, 150)
    k = seg(t, kw(u_yahi, "saamrajya") - 0.4, kw(u_yahi, "Bengal") + 0.3)
    if k > 0:
        cx_, cy_ = cam_xy(PH_CAM[0], PH_CAM[1]); s_ = PH_CAM[2]; x0, _ = to_screen(PH_CAM, 68.0, 25); x1, _ = to_screen(PH_CAM, 89, 25)
        c.save(); c.clipRect(skia.Rect(0, 0, lerp(x0, x1, ease_io(k)), DH))
        c.translate(DW / 2, DH / 2); c.scale(s_, s_); c.translate(-cx_, -cy_)
        c.drawPath(gpath("pratihara", s_), paint(REGCOL["pratihara"], 210)); c.drawPath(gpath("pratihara", s_), paint(lighten(REGCOL["pratihara"]), 230, stroke=1.2 / s_)); c.restore()
    label(c, "PRATIHARA SAAMRAJYA (andaazan, c. 900)", 960, 170, seg(t, kw(u_yahi, "saamrajya") - 0.1, kw(u_yahi, "saamrajya") + 0.3), 34, border=REGCOL["pratihara"])
    for key, nm, word in (("sindh", "SINDH KI SEEMA", "Sindh"), ((88.0, 23.5), "BENGAL", "Bengal")):
        x, y = to_screen(PH_CAM, *key) if isinstance(key, tuple) else S(PH_CAM, key)
        label(c, nm, x, y - 50, seg(t, kw(u_yahi, word) - 0.1, kw(u_yahi, word) + 0.3), 28, border=REGCOL["pratihara"])

@shot(vin(u_851), vin(U("Ab yaad karo wo teen")))
def s63(c, t):
    c.clear(hexc(NAVY))
    timeline(c, t, 851, 1.0, span=(700, 900), step=10, big_every=50)
    name_card(c, "SULAIMAN", "Arab vyapari · 851", 360, 260, seg(t, kw(u_851, "Sulaiman") - 0.2, kw(u_851, "Sulaiman") + 0.3), "#00BBF9")
    doc(c, "pratihara_cavalry", 640, 300, 1180, 420, t, seg(t, kw(u_851, "Sulaiman"), kw(u_851, "Sulaiman") + 0.5), kw(u_851, "ghudsawaar") - 0.4, 1.6)
    for j in range(6):
        kj = seg(t, kw(u_851, "ghudsawaar") + j * 0.08, kw(u_851, "ghudsawaar") + 0.3 + j * 0.08)
        if kj > 0: horse(c, 180 + j * 70, 560, 50, int(255 * kj))


# ======================================================================= CHAPTER 5: DAMASCUS MEIN AAG
PL.update(dict(ferghana=(71.8, 40.4), ardabil=(48.3, 38.25), tours=(0.69, 47.39), akroinon=(30.54, 38.75), nafrica=(4.0, 34.0),
               kairouan=(10.1, 35.68), saymur=(72.93, 18.55), ghazni2=(68.42, 33.55), ghor=(64.9, 34.5), konkan=(73.2, 17.5)))
u_yk = U("Ab yaad karo wo teen"); u_wkg = U("Wo kahan gaye?"); u_nazar = U("Iske liye India se"); u_jal = U("Kyunki usi waqt")
u_724 = U("724, Central"); u_dot = U('"Day of Thirst"'); u_pyas = U("Fauj pyaas"); u_730 = U("730:"); u_khaz = U("Khazaron ne")
u_731b = U("731:"); u_sam = U("Samarkand ke paas"); u_732 = U("732:"); u_tours = U("France mein Tours"); u_739 = U("739:"); u_akr = U("Byzantine sena")
u_740b = U("740:"); u_berb = U("North Africa mein"); u_27 = U("Sattaais hazaar"); u_3k = U("Aur wo teen hazaar sainik jo"); u_iraqb = U("Unhe raaste mein")
u_ghar = U("Jab ghar mein"); u_bl2 = U("Historian Khalid Blankinship"); u_750 = U("Aur 750 mein"); u_abb = U("Abbasi kranti")
u_naye = U("Naye Abbasi"); u_776 = U("Lekin 776"); u_mahdi = U("Aur Khalifa al-Mahdi"); u_r4 = U("Raaz number chaar")
CHAPTERS.append((5, "DAMASCUS MEIN AAG", u_yk)); chapter(5, "DAMASCUS MEIN AAG", u_yk)
FRONTS = [("ferghana", "DAY OF THIRST · 724", u_724, "#00BBF9"), ("ardabil", "KHAZAR · 730", u_khaz, "#9B5DE5"), ("samarkand", "DEFILE · 731", u_sam, "#F15BB5"),
          ("tours", "TOURS · 10 OCT 732", u_tours, "#3A86FF"), ("akroinon", "AKROINON · 739", u_akr, "#F8961E"), ("kairouan", "BERBER BAGHAAWAT · 740", u_berb, "#E76F51")]
FR_CAM = (36.0, 40.0, 19.0)
FR_OFF = {"ferghana": (20, -95), "ardabil": (-40, -120), "samarkand": (120, 60), "tours": (150, -50), "akroinon": (-60, 90), "kairouan": (-40, 80)}
def fronts(c, t, cam, upto=None, all_red=0.0):
    for i, (key, lab, uu, col) in enumerate(FRONTS):
        t0 = us(uu)
        if upto is not None and t0 > upto: continue
        x, y = S(cam, key); k = seg(t, t0 - 0.1, t0 + 0.4)
        if k <= 0: continue
        rp = ((t - t0) * 0.9) % 1
        c.drawCircle(x, y, 14 + 50 * rp, paint(RED, int(200 * (1 - rp) * k), stroke=4))
        ic_flame(c, x, y - 8, 46 * back(k), t, int(255 * clamp(k * 1.5))); clash(c, x, y, seg(t, t0 - 0.1, t0 + 0.7), 0.8)
        ox, oy = FR_OFF.get(key, (140, -46))
        c.drawLine(x, y, x + ox * 0.7, y + oy * 0.7, paint("#E5E7EB", int(160 * k), stroke=1.5))
        label(c, lab, x + ox, y + oy, k, 24, border=col)

@shot(vin(u_yk), vin(u_jal), "cut")
def s64(c, t):
    k = ease_io(seg(t, us(u_nazar), ue(u_nazar)))
    cam = fly(IN_CAM, FR_CAM, k); bg(c, cam); draw_region(c, cam, "caliph", GREEN, 170)
    x0, y0 = 1780, 90; kc = seg(t, vin(u_yk), vin(u_yk) + 0.8)
    pill(c, "3,000 ?", lerp(x0, 960, ease_io(kc)), lerp(y0, 300, ease_io(kc)), 40, RED, shadow=8)
    title(c, "WO KAHAN GAYE?", 960, 180, 64, seg(t, us(u_wkg), us(u_wkg) + 0.3), RED)

@shot(vin(u_jal), vin(u_3k))
def s65(c, t):
    bg(c, FR_CAM); draw_region(c, FR_CAM, "caliph", GREEN, 170)
    title(c, "HAR TARAF AAG", 960, 150, 60, seg(t, vin(u_jal), vin(u_jal) + 0.5), RED)
    fronts(c, t, FR_CAM)
    yr = 724
    for yy, uu in ((724, u_724), (730, u_730), (731, u_731b), (732, u_732), (739, u_739), (740, u_740b)):
        if t >= us(uu) - 0.1: yr = yy
    timeline(c, t, yr, 1.0, span=(720, 760), step=1, big_every=5)
    stat_card(c, 1380, 560, 420, 230, "27,000", "Syrian sainik saaf", seg(t, kw(u_27, "Sattaais") - 0.1, kw(u_27, "Sattaais") + 0.4), RED)
    SFX_MARK(vin(u_jal) + 0.3, "whoosh_long", -22)
    for key, lab, uu, col in FRONTS: SFX_MARK(us(uu), "boom", -24)

@shot(vin(u_3k), vin(u_bl2))
def s66(c, t):
    bg(c, FR_CAM); draw_region(c, FR_CAM, "caliph", GREEN, 170); fronts(c, t, FR_CAM)
    p0 = S(FR_CAM, "syria2"); p1 = S(FR_CAM, "sindh"); p2 = S(FR_CAM, "iraq2")
    kb = seg(t, kw(u_iraqb, "Iraq") - 0.4, kw(u_iraqb, "Iraq") + 0.4)
    if kb <= 0: route(c, [p0, (lerp(p0[0], p1[0], 0.4), p0[1] - 60)], seg(t, vin(u_3k), vin(u_3k) + 0.8), YEL, 10, False)
    else: route(c, [p0, ((p0[0] + p2[0]) / 2, p0[1] - 80), p2], kb, YEL, 10, False)
    pill(c, "3,000", p0[0], p0[1] - 60, 30, YEL, fg=NAVY, shadow=6)
    kq = seg(t, kw(u_iraqb, "baghaawat") - 0.1, kw(u_iraqb, "baghaawat") + 0.3)
    if kq > 0: stamp(c, "IRAQ BAGHAAWAT", p2[0] + 40, p2[1] + 90, 40, RED, kq)
    hl(c, FR_CAM, "iraq", t, kw(u_iraqb, "Iraq"), pole=False)
    kg = seg(t, us(u_ghar), us(u_ghar) + 0.5)
    if kg > 0:
        dim(c, 120 * kg); x, y = S(FR_CAM, "sindh"); pill(c, "SINDH?", x, y - 40, 34, "#5B6472", a=int(255 * clamp(kg * 1.5)))
    SFX_MARK(kw(u_iraqb, "Iraq"), "whoosh", -20)

@shot(vin(u_bl2), vin(u_naye))
def s67(c, t):
    c.clear(hexc(NAVY))
    name_card(c, "KHALID BLANKINSHIP", "The End of the Jihad State (1994)", 400, 200, seg(t, vin(u_bl2), vin(u_bl2) + 0.4))
    doc(c, "hisham_demise", 760, 120, 1080, 560, t, seg(t, vin(u_bl2) + 0.2, vin(u_bl2) + 0.8), kw(u_bl2, "haaron") - 0.3, 1.6)
    timeline(c, t, 750 if t > us(u_750) else 743, 1.0, span=(720, 780), step=5, big_every=10)
    ka = seg(t, kw(u_abb, "Abbasi") - 0.1, kw(u_abb, "Abbasi") + 0.4)
    if ka > 0:
        rrect(c, 160, 360, 700, 720, 24, "#16223A", int(255 * clamp(ka * 1.5)), shadow=18)
        crown(c, 430, 500, 120, "#5B6472", int(255 * clamp(ka * 1.5)))
        c.drawLine(360, 440, 500, 560, paint(RED, int(255 * clamp(ka * 1.5)), stroke=8, cap_round=True))
        text(c, "UMAYYAD KHATAM · 750", 430, 650, 34, "#F1FAEE", FT_BLACK, "c", int(255 * clamp(ka * 1.5)))
    SFX_MARK(kw(u_abb, "khatam"), "boom", -16)

SH_CAM = (68.0, 21.5, 40.0)
@shot(vin(u_naye), vin(u_r4))
def s68(c, t):
    _state_regions(); bg(c, SH_CAM); draw_region(c, SH_CAM, "sindh", "#2A9D8F", 160)
    timeline(c, t, 776 if t > us(u_776) else 770, 1.0, span=(740, 800), step=5, big_every=10)
    src = to_screen(SH_CAM, 63.0, 23.0); dst = S(SH_CAM, "saurashtra")
    k = seg(t, vin(u_naye) + 0.3, us(u_776) + 1.0); sink = seg(t, kw(u_776, "haraya") - 0.3, kw(u_776, "haraya") + 0.8)
    for j in range(3):
        kk = clamp(k - j * 0.1); x = lerp(src[0], dst[0] - 120, ease_out(kk)); y = lerp(src[1], dst[1], ease_out(kk)) + j * 60 - 60 + sink * 140
        boat(c, x, y, 70, int(255 * (1 - sink)), sail="#2A9D8F")
    ks = seg(t, kw(u_776, "Saindhava") - 0.2, kw(u_776, "Saindhava") + 0.4)
    for j in range(3):
        if ks > 0: boat(c, dst[0] - 40 + j * 10, dst[1] + 40 + j * 60, 70 * back(ks), int(255 * clamp(ks * 1.5)), sail=SAFF)
    if ks > 0: label(c, "SAINDHAVA NAVY · AGGUKA I", dst[0] + 120, dst[1] - 70, ks, 28, border=SAFF)
    stamp(c, "IRAADA CHHODA", 1350, 260, 56, RED, seg(t, kw(u_mahdi, "chhod") - 0.1, kw(u_mahdi, "chhod") + 0.3))
    if t > us(u_mahdi) - 0.2: name_card(c, "KHALIFA AL-MAHDI", "Abbasi khalifa", 500, 240, seg(t, us(u_mahdi) - 0.2, us(u_mahdi) + 0.3), "#2A9D8F")
    clash(c, dst[0] - 60, dst[1] + 60, seg(t, kw(u_776, "haraya") - 0.3, kw(u_776, "haraya") + 0.6), 1.2)
    SFX_MARK(kw(u_776, "haraya"), "boom", -18)

@shot(vin(u_r4), vin(U("Toh ek baar jod")))
def s69(c, t):
    c.clear(hexc(NAVY))
    slots(c, t, 3 + seg(t, kw(u_r4, "khilafat") - 0.3, kw(u_r4, "khilafat") + 0.4), 1.0, 520, labels=raaz_labels(4 if t > kw(u_r4, "khilafat") - 0.1 else 3))
    SFX_MARK(kw(u_r4, "khilafat") - 0.2, "lock", -16)

# ======================================================================= VERDICT + OUTRO
u_jod = U("Toh ek baar jod"); u_kd = U("Kabul ki deewar."); u_reg = U("Registaan."); u_ibj = U("Indian rajyon ka baar"); u_aat = U("Aur khilafat ka andar")
u_sm = U("Arab raaj Sindh aur Multan"); u_854 = U("Aur 854"); u_lab = U("Lekin ab wo baat"); u_bahut = U("Bahut log sochte"); u_galat = U("Ye galat hai")
u_ghz = U("North India jeetne"); u_turk = U("Mahmud ek Turk"); u_twist2 = U("Aur sabse bada twist"); u_nw = U("Wo aaye north-west"); u_wahi2 = U("Yaani wahi darwaza")
u_vyap = U("Aur ek aakhri sach"); u_rash = U("Rashtrakuta raja"); u_hm = U("Toh ye kahani Hindu"); u_saam = U("Ye ek bade saamrajya")
u_agli = U("Aur agli video")
@shot(vin(u_jod), vin(u_sm))
def s70(c, t):
    c.clear(hexc(NAVY))
    slots(c, t, 4, 1.0, 520, labels=RAAZ)
    for i, uu in enumerate((u_kd, u_reg, u_ibj, u_aat)):
        k = seg(t, us(uu) - 0.1, us(uu) + 0.3) * (1 - seg(t, ue(uu) + 0.1, ue(uu) + 0.4))
        if k > 0:
            x = 960 + (i - 1.5) * 380
            c.drawRoundRect(skia.Rect(x - 170, 360, x + 170, 680), 28, 28, paint(YEL, int(255 * k), stroke=3))
    title(c, "TOH JOD KE DEKHO", 960, 220, 60, seg(t, vin(u_jod), vin(u_jod) + 0.4), YEL)

@shot(vin(u_sm), vin(u_lab))
def s71(c, t):
    cam = (68.5, 27.5, 60.0); bg(c, cam)
    k = seg(t, us(u_854) - 0.2, us(u_854) + 0.6)
    draw_region(c, cam, "sindh", GREEN, 200)
    x, y = S(cam, "multan"); pin(c, x, y, "MULTAN EMIRAT" if k > 0.5 else "MULTAN", 1.0, GREEN, size=28, t=t)
    x2, y2 = S(cam, "mansura"); pin(c, x2, y2, "MANSURA EMIRAT" if k > 0.5 else "MANSURA", 1.0, GREEN, size=28, t=t)
    if k > 0: c.drawLine(lerp(x, x2, 0.5) - 160, lerp(y, y2, 0.5), lerp(x, x2, 0.5) + 160, lerp(y, y2, 0.5), paint(RED, int(255 * k), stroke=4))
    title(c, "SIRF SINDH + MULTAN", 960, 170, 56, seg(t, vin(u_sm), vin(u_sm) + 0.4), "#F1FAEE")
    timeline(c, t, 854, seg(t, us(u_854) - 0.2, us(u_854) + 0.3), span=(700, 900), step=10, big_every=50)

@shot(vin(u_lab), vin(u_ghz))
def s72(c, t):
    c.clear(hexc(NAVY))
    slots(c, t, 4, 1.0, 520, labels=RAAZ, red4=seg(t, vin(u_lab), vin(u_lab) + 0.5)) if t < us(u_bahut) else None
    kb = seg(t, us(u_bahut) - 0.1, us(u_bahut) + 0.4)
    if kb > 0:
        cam = (60.0, 28.0, 12.0); c.save(); lp = skia.Paint(); lp.setAlphaf(kb); c.saveLayer(None, lp)
        bg(c, cam, {"IND": (SAFF, 170)}); draw_region(c, cam, "caliph", GREEN, 200)
        arrow(c, S(cam, "damascus"), S(cam, "india"), seg(t, us(u_bahut), us(u_bahut) + 1.5), GREEN, 12, 0.1)
        c.restore(); c.restore()
        dim(c, 120 * kb); title(c, "ARAB KHILAFAT NE INDIA JEETA?", 960, 200, 64, kb, "#F1FAEE")
        circle_x(c, 960, 560, 200, seg(t, us(u_galat) - 0.1, us(u_galat) + 0.7))
    SFX_MARK(us(u_galat), "stamp", -14)

@shot(vin(u_ghz), vin(u_vyap))
def s73(c, t):
    k = seg(t, vin(u_nw) - 0.3, vin(u_nw) + 1.0)
    cam = fly((72.0, 28.0, 22.0), NW_CAM, ease_io(k)); bg(c, cam); draw_region(c, cam, "sindh", GREEN, 130)
    timeline(c, t, 1192 if t > kw(u_ghz, "Ghori") else 1001, seg(t, kw(u_ghz, "Ghazni") - 0.2, kw(u_ghz, "Ghazni") + 0.3), span=(950, 1250), step=25, big_every=50)
    portrait(c, "MAHMUD GHAZNI", 400, 420, seg(t, kw(u_ghz, "Ghazni") - 0.2, kw(u_ghz, "Ghazni") + 0.3), col="#5B4B8A", hat="helmet", w=280, h=330)
    portrait(c, "MUHAMMAD GHORI", 720, 420, seg(t, kw(u_ghz, "Ghori") - 0.2, kw(u_ghz, "Ghori") + 0.3), col="#8A5B3D", hat="turban", w=280, h=330)
    kt = seg(t, kw(u_turk, "Turk") - 0.1, kw(u_turk, "Turk") + 0.3)
    if kt > 0: pill(c, "TURK · GHAZNAVID (1001 se)", 400, 640, 24, "#5B4B8A", a=int(255 * clamp(kt * 1.5))); pill(c, "GHURID (1192)", 720, 640, 24, "#8A5B3D", a=int(255 * clamp(kt * 1.5)))
    kn = seg(t, kw(u_turk, "naam") - 0.1, kw(u_turk, "naam") + 0.3)
    if kn > 0: pill(c, "KHALIFA KO SIRF NAAM KA SALAAM", 560, 720, 26, "#5B6472", a=int(255 * clamp(kn * 1.5)))
    kg = seg(t, us(u_wahi2), us(u_wahi2) + 1.2)
    if k > 0.6:
        x, y = S(cam, "kabul"); gate(c, x + 150, y - 60, 100 * ease_out(seg(k, 0.6, 1.0)), kg)
        arrow(c, S(cam, "ghazni2"), S(cam, "punjab"), seg(t, us(u_wahi2) + 0.5, ue(u_wahi2) + 0.5), "#9B5DE5", 10, 0.12)
    tw = seg(t, us(u_twist2) - 0.1, us(u_twist2) + 0.3) * (1 - seg(t, us(u_nw), us(u_nw) + 0.3))
    if tw > 0: title(c, "SABSE BADA TWIST?", 960, 160, 64, tw, YEL)
    SFX_MARK(us(u_wahi2) + 0.3, "drag", -16); SFX_MARK(ue(u_wahi2), "boom", -18)

@shot(vin(u_vyap), vin(u_hm))
def s74(c, t):
    _state_regions(); cam = (74.0, 19.5, 36.0); bg(c, cam)
    x, y = S(cam, "saymur"); pin(c, x, y, "SAYMUR (KONKAN)", seg(t, kw(u_rash, "Konkan") - 0.1, kw(u_rash, "Konkan") + 0.3), "#00BBF9", size=26, t=t)
    for j in range(3):
        kk = seg(t, vin(u_vyap) + j * 0.3, vin(u_vyap) + 2.5 + j * 0.3)
        bx = lerp(200, x - 80, ease_io(kk)); boat(c, bx, y + 40 + j * 70, 70, int(255 * clamp(kk * 3)), sail="#00BBF9")
    name_card(c, "RASHTRAKUTA RAJA (BALHARA)", "Arab vyapariyon ko izzat", 1380, 260, seg(t, us(u_rash) - 0.1, us(u_rash) + 0.3), SAFF)
    km = seg(t, kw(u_rash, "masjidein") - 0.1, kw(u_rash, "masjidein") + 0.3)
    if km > 0: pill(c, "~10,000 MUSALMAAN (al-Masudi, Saymur)", 1380, 420, 26, "#00BBF9", a=int(255 * clamp(km * 1.5)))
    doc(c, "rashtrakuta_four", 1000, 520, 760, 300, t, seg(t, kw(u_rash, "masjidein") + 0.3, kw(u_rash, "masjidein") + 0.8), kw(u_rash, "masjidein") + 0.6, 1.0)
    kv = seg(t, vin(u_vyap), vin(u_vyap) + 0.4)
    if kv > 0: title(c, "JANG + VYAPAR", 600, 170, 60, kv, YEL)

@shot(vin(u_hm), HOSTSEG["H3"][0])
def s75(c, t):
    c.clear(hexc(NAVY))
    kl = seg(t, kw(u_saam, "saamrajya") - 0.2, kw(u_saam, "saamrajya") + 0.4)
    rrect(c, 220, 380, 760, 760, 24, GREEN, int(230 * clamp(kl * 1.5)), shadow=18) if kl > 0 else None
    if kl > 0: text(c, "EK BADA SAAMRAJYA", 490, 590, 40, "#F1FAEE", FT_BLACK, "c", int(255 * clamp(kl * 1.5)))
    for j, col in enumerate(("#E76F51", "#F15BB5", "#9B5DE5", "#F8961E", "#2A9D8F", SAFF)):
        kk = seg(t, kw(u_saam, "kai") - 0.1 + j * 0.08, kw(u_saam, "kai") + 0.3 + j * 0.08)
        shield(c, 1060 + (j % 3) * 230, 470 + (j // 3) * 200, 80, col, 255, kk)
    kk2 = seg(t, kw(u_saam, "Indian") - 0.1, kw(u_saam, "Indian") + 0.3)
    if kk2 > 0: text(c, "KAI MAZBOOT INDIAN RAJYA", 1290, 800, 36, "#F1FAEE", FT_BLACK, "c", int(255 * clamp(kk2 * 1.5)))
    kh_ = seg(t, us(u_hm) - 0.1, us(u_hm) + 0.3)
    if kh_ > 0:
        title(c, "HINDU vs MUSALMAAN?", 960, 200, 60, kh_, "#F1FAEE"); xmark(c, 960, 190, 60, seg(t, kw(u_hm, "nahi") - 0.1, kw(u_hm, "nahi") + 0.3))
    ic_scale(c, 960, 900 - 60, 70, 0, int(255 * clamp(kl * 1.5))) if kl > 0 else None

@shot(HOSTSEG["H3"][0], vin(u_agli), "cut")
def h3(c, t):
    host_frame(c, "H3", t)
    for i in range(4):
        k = seg(t, kw(U("Comment mein number"), ["ek", "do", "teen", "chaar"][i], 0 if i else 0) - 0.1, kw(U("Comment mein number"), ["ek", "do", "teen", "chaar"][i]) + 0.3)
        if k > 0: pill(c, f"{i + 1}  {RAAZ[i]}", 420 if i < 2 else 1500, 720 + (i % 2) * 90, 28, "#16223A", a=int(255 * clamp(k * 1.5)))
HOSTS.append((HOSTSEG["H3"][0], vin(u_agli)))

@shot(vin(u_agli), HOSTSEG["H4"][0])
def s76(c, t):
    bg(c, NW_CAM); dim(c, 80)
    x, y = S(NW_CAM, "kabul"); og = seg(t, kw(u_agli, "Ghazni") - 0.6, kw(u_agli, "Ghazni") + 0.4)
    c.save(); c.translate(960, 560); c.scale(2.2, 2.2); c.translate(-960, -560)
    gate(c, 960, 560, 120, og)
    if og > 0.3:
        c.drawCircle(960, 540, 18, paint("#0F1B2D")); c.drawRoundRect(skia.Rect(944, 556, 976, 610), 10, 10, paint("#0F1B2D"))
    c.restore()
    title(c, "AGLI VIDEO", 960, 180, 70, seg(t, vin(u_agli), vin(u_agli) + 0.4), RED)
    kq = seg(t, kw(u_agli, "darwaza") - 0.1, kw(u_agli, "darwaza") + 0.4)
    if kq > 0: text(c, "Kabul ka darwaza Mahmud Ghazni ke liye kaise khula?", 960, 900, 44, "#F1FAEE", FT_BLACK, "c", int(255 * clamp(kq * 1.5)), shadow=True)
    km_ = seg(t, us(U("Wo kahani miss")) - 0.1, us(U("Wo kahani miss")) + 0.4)
    if km_ > 0: title(c, "MISS MAT KARNA!", 960, 330, 64, km_, YEL)
    SFX_MARK(kw(u_agli, "Ghazni") - 0.6, "drag", -16)

@shot(HOSTSEG["H4"][0], UN[-1]["end"] + 3.0, "cut")
def h4(c, t):
    if t < HOSTSEG["H4"][1]:
        host_frame(c, "H4", t)
        sub_overlay(c, t, kw(U("Abhi subscribe"), "subscribe") - 0.5)
    else:
        lt = t - HOSTSEG["H4"][1]; c.clear(hexc(NAVY))
        draw_img(c, LOGO, 810, 260, 1110, 560, int(255 * clamp(seg(lt, 0, 0.5) * 1.5)))
        title(c, "AMRIT BORI", 960, 680, 90, seg(lt, 0.2, 0.7), YEL)
        title(c, "Subscribe karo · Jai Hind", 960, 770, 40, seg(lt, 0.5, 1.0), "#F1FAEE")
        fade = seg(t, UN[-1]["end"] + 2.3, UN[-1]["end"] + 3.0)
        if fade > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(255 * fade)))
    SFX_MARK(kw(U("Abhi subscribe"), "subscribe") + 0.9, "pop", -20)
HOSTS.append((HOSTSEG["H4"][0], UN[-1]["end"] + 3.0))
VIDEO_END_VO = UN[-1]["end"] + 3.0


# (user: "hook mein mat ruko" - pauses only at chapter cards; hold() kept for later use)

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

def in_host(t): return any(a <= t < b for a, b in HOSTS)

# ------------------------------------------------------------------ frame
SHOTS.sort(key=lambda s: s[0])
def find(t):
    for i, (a, b, fn, tr) in enumerate(SHOTS):
        if a <= t < b: return i
    return None

GAPINFO = None; CUR_T = 0.0
def remap(T):
    off = 0.0
    for P, d, kind, idx in sorted(GAPS):
        vs = P + off
        if T < vs: return T - off, None
        if T < vs + d: return P, (kind, idx, T - vs)
        off += d
    return T - off, None

def render(T):
    global GAPINFO, CUR_T
    t, GAPINFO = remap(T); CUR_T = T
    load_assets()
    surf = skia.Surface(W4, H4); c = surf.getCanvas(); c.scale(SC, SC)
    if GAPINFO is not None and GAPINFO[0] == "ch":
        n, ttl, _ = CHAPTERS[GAPINFO[1]]
        chapter_card(c, GAPINFO[2], 0, n, ttl, CH_GAP)
    elif GAPINFO is not None:                      # hold beat: same shot, VO frozen, video time runs on
        i = find(t)
        if i is not None: c.save(); SHOTS[i][2](c, t); c.restore()
        if t > 0.4: watermark(c, LOGO, 140)
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
                c.save()
                if not in_host(t):
                    u_ = clamp((t - a) / max(0.5, b - a)); zz = 1.0 + 0.035 * ease_io(u_); dx = (1 if i % 2 else -1) * 14 * ease_io(u_)
                    c.translate(960 + dx, 540); c.scale(zz, zz); c.translate(-960, -540)
                fn(c, t); c.restore()
        captions(c, t)
        if not in_host(t) and t > 0.4: watermark(c, LOGO, 140)
    vignette(c, 100); grain(c, T, 12)
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

def vo_to_video(t):
    return t + sum(d for P, d, k_, i_ in GAPS if P <= t)
def vt_now(t):
    """video time for animations that must continue through a hold: the real frame time while rendering"""
    return CUR_T if CUR_T else vo_to_video(t)

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
        json.dump({"gaps": [[P, d, k_] for P, d, k_, i_ in sorted(GAPS)], "ch_gap": CH_GAP, "hosts": [[a, b] for a, b in HOSTS], "demo_end": DEMO_END,
                   "vo_end": UN[-1]["end"]}, open(ROOT + "audio/timeline.json", "w")); print("ok")
    elif cmd == "sfx":
        load_assets(); surf = skia.Surface(DW, DH); cc = surf.getCanvas()
        for a, b, fn, tr in SHOTS:
            for tt in np.arange(a + 0.01, b, 0.1): fn(cc, float(tt))
        ev = sorted([(n, round(vo_to_video(tt), 3), g) for n, tt, g in SFX], key=lambda x: x[1])
        json.dump(ev, open(ROOT + "audio/full_sfx.json", "w")); print(len(ev), "sfx events")
