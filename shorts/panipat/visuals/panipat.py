"""Panipat mein hi 3 yudh kyun? - 9:16 Short, seamless 3D one-shot (no cuts).

  python3 panipat.py stills OUT t1 t2 ...       (design 1080x1920, saved at 540 wide)
  python3 panipat.py video out.mp4 WIDTH FPS f0 f1
  python3 panipat.py sfx                          -> ../audio/sfx_events.json
One 3D camera flies over the map from the first frame to the last; each battle rises from Panipat as a pop-up card,
fills the frame, plays as a cartoon battle on a real Haryana field photo, then folds back into the map.
"""
import os, sys, json, math, subprocess
os.environ.setdefault("AB_ORIENT", "vertical")
PLUG = "/root/.claude/plugins/synced/c39869bb-0747-4e92-a078-94e7a4b5fa51_7aeb7cf6-6ef6-493a-b987-bc6e2a55c6bf/goeglobetales-copy-edt-style-long-and-short-form"
sys.path.insert(0, PLUG + "/engine/visuals")
import numpy as np, skia
from PIL import Image, ImageFilter, ImageEnhance
from shapely.geometry import shape, box, LineString
from shapely.ops import unary_union, linemerge
from core import *
from core import _poly_path
from storyproof import (Satellite, SERIF_DISPLAY, SERIF_TEXT, serif_title, stamp_slam, shake, fireworks, paper_texture, YEL, RED, WHITE)
import battle2d
from battle2d import *
import cam3d
from cam3d import Cam, on_map, parchment, satellite, route, float_flag, pin, quad, FULL, doc_card, fire, _n, FOC

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
RAW = PROJ + "/research/raw/"; DOCS = HERE + "/docs/"; PLC = HERE + "/places/"
assert DW == 1080 and DH == 1920

# ================================================================== VO timing
UN = json.load(open(PROJ + "/voice/full_units.json"))["units"]
SIL = [tuple(map(float, l.split())) for l in open(PROJ + "/voice/full_sil.tsv")]
VO_END = UN[-1]["end"]; END = VO_END + 1.6
def U(prefix): return next(i for i, u in enumerate(UN) if u["text"].lower().startswith(prefix.lower()))
def us(i): return UN[i]["start"]
def ue(i): return UN[i]["end"]
def kw(i, word, occ=0):
    txt = UN[i]["text"]; p = -1
    for _ in range(occ + 1): p = txt.lower().find(word.lower(), p + 1)
    if p < 0: return us(i)
    est = UN[i]["start"] + (UN[i]["end"] - UN[i]["start"]) * p / max(1, len(txt)); best = None
    for a, b in SIL:
        if UN[i]["start"] < b < UN[i]["end"] and abs(b - est) < 0.35 and (best is None or abs(b - est) < abs(best - est)): best = b
    return (best if best else est) - 0.05

u_hook, u_kyun, u_1526, u_babur, u_lodi, u_lodi2, u_bhadak, u_mughal = U("Ek hi maidan"), U("Par sirf Panipat"), U("21 April"), U("Babur ke"), U("Saamne"), U("50 se"), U("Par topon"), U("Lodi maara")
u_1556, u_hemu, u_teer, u_bikhar = U("Sirf 30"), U("Hemu, jo"), U("Ladaai barabar"), U("Hemu behosh")
u_1761, u_abdali, u_badi, u_maut = U("Phir 14"), U("Marathe aur"), U("Ye athaar"), U("Sirf Maratha")
u_naksha, u_uttar, u_yamuna, u_sapaat, u_95, u_tarain, u_matlab = U("Ab naksha"), U("Kabul se"), U("Ek taraf"), U("Beech mein"), U("Aur Delhi"), U("Tarain"), U("Matlab")
u_poll, u_opts, u_sub = U("Aapke"), U("1526, 1556"), U("Comment")

# ================================================================== places
PL = dict(panipat=(76.97, 29.39), delhi=(77.21, 28.61), kabul=(69.17, 34.53), khyber=(71.1, 34.08), peshawar=(71.58, 34.01), attock=(72.36, 33.9),
          lahore=(74.35, 31.55), ludhiana=(75.85, 30.9), ambala=(76.78, 30.38), thanesar=(76.83, 29.97), karnal=(77.07, 29.72), tarain=(76.94, 29.78),
          jalalabad=(70.45, 34.43), agra=(78.01, 27.18), pune=(73.86, 18.52), gwalior=(78.18, 26.22), kandahar=(65.71, 31.61), bhopal=(77.4, 23.26))
UTTAR = [PL[k] for k in ("kabul", "jalalabad", "khyber", "peshawar", "attock", "lahore", "ludhiana", "ambala", "thanesar", "panipat", "delhi")]

# ================================================================== geodata (historical-basemaps, A. Ourednik, GPL-3.0 - approximate borders)
def hb(year, names):
    d = json.load(open(RAW + f"world_{year}.geojson")); gs = []
    for f in d["features"]:
        if f["properties"].get("NAME") in names:
            try: gs.append(shape(f["geometry"]).buffer(0))
            except Exception: pass
    return unary_union(gs)
def P(g): return _poly_path(g.buffer(0), 0.01)
WM = WorldMap()
_G = {}
def G(name):
    if name not in _G:
        if name == "lodi": g = hb(1500, ["Sultanate of Delhi"])
        elif name == "kabul": g = hb(1500, ["Timurid Emirates"]).intersection(box(61, 29.5, 72.2, 37.2))
        elif name == "mughal1530": g = hb(1530, ["Mughal Empire"])
        elif name == "akbar1556": g = hb(1530, ["Mughal Empire"]).intersection(box(60, 20, 75.4, 40))
        elif name == "sur1556": g = hb(1530, ["Mughal Empire"]).intersection(box(75.4, 20, 92, 33)).union(hb(1530, ["Bengal"]))
        elif name == "maratha": g = hb(1783, ["Maratha Confederacy", "Mahratta states"])
        elif name == "afghan": g = hb(1783, ["Afghanistan"])
        elif name == "thar":
            st = json.load(open(MAPDATA + "states.geojson"))["features"]
            raj = next(shape(f["geometry"]) for f in st if f["properties"]["name"] == "Rajasthan")
            g = raj.intersection(box(69, 24.6, 74.6, 30.3)).union(WM.geoms["PAK"].intersection(box(68.9, 24.2, 71.3, 29.2))).buffer(0.15).buffer(-0.15)
        elif name == "india": g = WM.geoms["IND"]
        _G[name] = g
    return _G[name]
_PP = {}
def PP(name):
    if name not in _PP: _PP[name] = P(G(name))
    return _PP[name]
def _yamuna():
    r = json.load(open(RAW + "rivers50.geojson")); ls = []
    for f in r["features"]:
        if f["properties"].get("name") == "Yamuna": g = shape(f["geometry"]); ls += list(getattr(g, "geoms", [g]))
    m = linemerge(ls); m = max(getattr(m, "geoms", [m]), key=lambda l: l.length)
    pts = list(m.coords)
    if pts[0][1] < pts[-1][1]: pts = pts[::-1]           # source (north) -> mouth
    return pts
YAMUNA = _yamuna()

# ================================================================== period banners (PRATIK, andaazan) + modern tiranga for present-day scenes
FLAGK = dict(mughal="#2F6B3A", lodi="#1E3A8A", sur="#7C2D12", bhagwa="#E8731A", durrani="#1F2937", tiranga="#FFFFFF")
def draw_banner(cc, kind, w=240, h=160):
    if kind == "mughal":                                   # green alam, gold sun disc (symbol only)
        cc.drawRect(skia.Rect(0, 0, w, h), paint("#2F6B3A")); cc.drawCircle(w * 0.5, h * 0.5, h * 0.24, paint("#E9C46A"))
        for i in range(16):
            a_ = i / 16 * 2 * math.pi; cc.drawLine(w * .5 + math.cos(a_) * h * .28, h * .5 + math.sin(a_) * h * .28, w * .5 + math.cos(a_) * h * .38, h * .5 + math.sin(a_) * h * .38, paint("#E9C46A", 255, stroke=5))
    elif kind == "lodi":
        cc.drawRect(skia.Rect(0, 0, w, h), paint("#1E3A8A")); cc.drawRect(skia.Rect(0, h * .42, w, h * .58), paint("#E9C46A"))
    elif kind == "sur":
        cc.drawRect(skia.Rect(0, 0, w, h), paint("#7C2D12")); cc.drawRect(skia.Rect(w * .1, h * .12, w * .9, h * .88), paint("#E9C46A", 255, stroke=8))
    elif kind == "bhagwa":                                 # saffron swallow-tailed jhenda
        p = skia.Path(); p.moveTo(0, 0); p.lineTo(w, 0); p.lineTo(w * .62, h * .5); p.lineTo(w, h); p.lineTo(0, h); p.close(); cc.drawPath(p, paint("#E8731A"))
    elif kind == "durrani":
        cc.drawRect(skia.Rect(0, 0, w, h), paint("#1F2937")); cc.drawRect(skia.Rect(0, h * .66, w, h), paint("#15803D"))
    elif kind == "tiranga":
        for i, col in enumerate(("#FF9933", "#FFFFFF", "#138808")): cc.drawRect(skia.Rect(0, h * i / 3, w, h * (i + 1) / 3), paint(col))
        cc.drawCircle(w / 2, h / 2, h * 0.13, paint("#000080", 255, stroke=3))
        for i in range(24):
            a_ = i / 24 * 2 * math.pi; cc.drawLine(w / 2, h / 2, w / 2 + math.cos(a_) * h * .13, h / 2 + math.sin(a_) * h * .13, paint("#000080", 255, stroke=1))
_BT = {}
def btex(kind):
    if kind not in _BT:
        s = skia.Surface(240, 160); cc = s.getCanvas(); cc.clear(skia.ColorTRANSPARENT); draw_banner(cc, kind); _BT[kind] = s.makeImageSnapshot()
    return _BT[kind]
for k_ in FLAGK: cam3d._FLAGIMG[k_] = btex(k_)
_old_emblem = battle2d.banner_emblem
def _emblem(c, kind, x0, y0, w, h, a=255):
    if kind in FLAGK:
        p = skia.Paint(AntiAlias=True); p.setAlphaf(a / 255); c.drawImageRect(btex(kind), skia.Rect(0, 0, 240, 160), skia.Rect(x0, y0, x0 + w, y0 + h), SAMP, p)
    else: _old_emblem(c, kind, x0, y0, w, h, a)
battle2d.banner_emblem = _emblem

# period armies (cartoon, kalpanik)
FAC.update({
    "mughal":  dict(tunic="#3F6E4A", body="lamellar", armor="#8E9AA6", legs="trousers", leg_col="#3A2A1E", head="turban_helm", head_col="#F1ECE0",
                    shield="round", shield_col="#5A3A1E", skin="#D4A276", beard="#2B1D0E", weapon="bow", banner="mughal", horses=("#C8A26B", "#8B6B3E", "#3B2A1A"), capar=None),
    "lodi":    dict(tunic="#1E3A8A", body="quilted", armor="#27408B", legs="trousers", leg_col="#E9E4D8", head="turban_helm", head_col="#E9E4D8",
                    shield="round", shield_col="#7A5230", skin="#B98559", beard="#1A120B", weapon="sword", banner="lodi", horses=("#5B3A22", "#2B1D0E"), capar="#1E3A8A"),
    "sur":     dict(tunic="#7C2D12", body="quilted", armor="#9A3412", legs="trousers", leg_col="#F4E3B5", head="pagdi", head_col="#F4E3B5",
                    shield="round", shield_col="#5A3A1E", skin="#B07A4F", beard="#1A120B", weapon="spear", banner="sur", horses=("#5B3A22", "#A0522D"), capar="#7C2D12"),
    "maratha": dict(tunic="#F4EFE4", body="quilted", armor="#E8731A", legs="trousers", leg_col="#F4E3B5", head="pagdi", head_col="#E8731A",
                    shield="round", shield_col="#3A2A1E", skin="#A9714A", beard="#1A120B", weapon="spear", banner="bhagwa", horses=("#5B3A22", "#2B1D0E", "#A0522D"), capar="#E8731A"),
    "durrani": dict(tunic="#1F2937", body="lamellar", armor="#6B7280", legs="trousers", leg_col="#3A2A1E", head="turban_helm", head_col="#14532D",
                    shield="round", shield_col="#374151", skin="#D4A276", beard="#1A120B", weapon="sword", banner="durrani", horses=("#3B2A1A", "#E8E2D6", "#6B4423"), capar=None),
})

def flag_region(c, cam, path, kind, t, k=1.0, alpha=0.78, edge="#FFFFFF"):
    """territory filled with its ruler's banner colour (multiply), whole banner in the middle, cloth waves, sweep reveal."""
    if k <= 0 or path is None: return
    tex = btex(kind); b = path.computeTightBounds(); main = FLAGK[kind]
    with on_map(c, cam) as ppd:
        c.save(); c.clipPath(path, doAntiAlias=True)
        c.clipRect(skia.Rect(b.left() - 1, b.top() - 1, b.left() + b.width() * 1.05 * ease_io(k), b.bottom() + 1))
        if kind == "tiranga":
            for i, col in enumerate(("#FF9933", "#FFFFFF", "#138808")):
                fp = paint(col, int(255 * alpha * 0.7)); fp.setBlendMode(skia.BlendMode.kMultiply if col != "#FFFFFF" else skia.BlendMode.kSrcOver)
                if col == "#FFFFFF": fp.setAlphaf(0.35)
                c.drawRect(skia.Rect(b.left(), b.top() + b.height() * i / 3, b.right(), b.top() + b.height() * (i + 1) / 3), fp)
        else:
            fp = paint(main, int(255 * alpha * 0.85)); fp.setBlendMode(skia.BlendMode.kMultiply); c.drawRect(b, fp)
            s_ = min(b.width() / 240, b.height() / 160) * 0.55; w, h = 240 * s_, 160 * s_
            p2 = skia.Paint(AntiAlias=True); p2.setAlphaf(alpha * 0.8)
            c.drawImageRect(tex, skia.Rect(0, 0, 240, 160), skia.Rect(b.centerX() - w / 2, b.centerY() - h / 2, b.centerX() + w / 2, b.centerY() + h / 2), SAMP, p2)
        n = 8
        for i in range(n):
            xx = b.left() + ((i / n + t * 0.12) % 1.0) * b.width()
            c.drawRect(skia.Rect(xx, b.top(), xx + b.width() / (n * 2), b.bottom()), paint("#000000", 24, blur=b.width() / 30))
            c.drawRect(skia.Rect(xx + b.width() / (n * 2), b.top(), xx + b.width() / n, b.bottom()), paint("#FFFFFF", 16, blur=b.width() / 30))
        c.restore()
        c.drawPath(path, paint(edge, int(150 * k), stroke=4.0 / ppd, blur=2.5 / ppd)); c.drawPath(path, paint(edge, int(220 * k), stroke=1.2 / ppd))

def glow_region(c, cam, path, k, col, t=0):
    if k <= 0: return
    with on_map(c, cam) as ppd:
        c.save(); c.clipPath(path, doAntiAlias=True)
        c.drawPath(path, paint(col, int(150 * k * (0.85 + 0.15 * math.sin(t * 4))), blur=6 / ppd)); c.restore()
        c.drawPath(path, paint("#FFF1C2", int(200 * k), stroke=7 / ppd, blur=4 / ppd)); c.drawPath(path, paint("#FFF1C2", int(230 * k), stroke=1.8 / ppd))

def river(c, cam, pts, k, t, pulse=0.0, col="#4FC3F7"):
    if k <= 0: return
    with on_map(c, cam) as ppd:
        pth = skia.Path(); q = [cam_xy(*p) for p in pts]; pth.moveTo(*q[0]); [pth.lineTo(*x) for x in q[1:]]
        pm = skia.PathMeasure(pth, False); L = pm.getLength(); part = skia.Path(); pm.getSegment(0, L * clamp(k), part, True)
        c.drawPath(part, paint("#0B2545", 200, stroke=9 / ppd, cap_round=True))
        c.drawPath(part, paint(col, 160, stroke=16 / ppd, cap_round=True, blur=7 / ppd)); c.drawPath(part, paint(col, 255, stroke=5 / ppd, cap_round=True))
        if k < 1:
            pos, _ = pm.getPosTan(L * clamp(k)); c.drawCircle(pos.x(), pos.y(), 10 / ppd, paint("#E0F7FF", 230, blur=4 / ppd))
        if pulse > 0:
            for j in range(3):
                f = ((t * 0.35 + j / 3) % 1.0); pos, _ = pm.getPosTan(L * f); c.drawCircle(pos.x(), pos.y(), 14 / ppd, paint("#FFFFFF", int(200 * pulse), blur=6 / ppd))

def popup_quad(cam, lon, lat, width, rise):
    """vertical (9:16) scene card hinging up from the map at (lon, lat)."""
    u, v = cam_xy(lon, lat); B = np.array([u, -v, 0.0])
    rg = _n(np.array([cam.r[0], cam.r[1], 0.0])); fh = _n(np.array([cam.f[0], cam.f[1], 0.0])); h = width * DH / DW
    al = math.radians(88 * ease_out(clamp(rise))); upv = math.cos(al) * fh + math.sin(al) * np.array([0, 0, 1.0])
    out = []
    for P3 in (B - rg * width / 2 + upv * h, B + rg * width / 2 + upv * h, B + rg * width / 2, B - rg * width / 2):
        q = cam.project(P3[0], -P3[1], P3[2])
        if q is None: return None
        out.append((q[0], q[1]))
    return out
def popup(c, cam, lon, lat, img, width, rise, fill):
    if rise <= 0: return
    q = popup_quad(cam, lon, lat, width, rise) or FULL
    k = ease_io(clamp(fill)); pts = [(lerp(q[i][0], FULL[i][0], k), lerp(q[i][1], FULL[i][1], k)) for i in range(4)]
    quad(c, img, pts, 255, shadow=fill < 0.95)
    if fill < 0.9:
        bp = skia.Path(); bp.moveTo(*pts[0]); [bp.lineTo(*p) for p in pts[1:]]; bp.close(); c.drawPath(bp, paint("#F4EFE4", int(255 * (1 - fill)), stroke=6))

# ================================================================== screen widgets
def hook_word(c, s, cx, y, size, k, t, cols=None, shine_t=None):
    """key word glides in letter by letter: rise + stretch + fade with back-ease; light shine sweeps across."""
    if k <= 0: return
    f = font(SERIF_DISPLAY, size); w = f.measureText(s); x = cx - w / 2; n = len(s); xs = []
    for i, ch in enumerate(s):
        kk = seg(k, i / n * 0.6, i / n * 0.6 + 0.4); cw = f.measureText(ch); xs.append((x, cw))
        if kk > 0:
            b = back(kk); col = (cols[i % len(cols)] if cols else "#FFFFFF")
            c.save(); c.translate(x + cw / 2, y + (1 - b) * size * 0.6); c.scale(1, lerp(1.6, 1.0, clamp(b)))
            c.drawString(ch, -cw / 2 + size * 0.03, size * 0.05, f, paint("#000000", int(140 * kk)))
            c.drawString(ch, -cw / 2, 0, f, paint(col, int(255 * clamp(kk * 1.4)))); c.restore()
        x += cw
    if shine_t is not None:
        sk_ = seg(t, shine_t, shine_t + 0.8)
        if 0 < sk_ < 1:
            sx = cx - w / 2 - 80 + (w + 160) * sk_
            c.save(); c.clipRect(skia.Rect(cx - w / 2, y - size, cx + w / 2, y + size * 0.2))
            g = skia.GradientShader.MakeLinear([(sx - 60, 0), (sx + 60, 0)], [hexc("#FFFFFF", 0), hexc("#FFFFFF", 170), hexc("#FFFFFF", 0)])
            p = skia.Paint(Shader=g); p.setBlendMode(skia.BlendMode.kSrcATop); c.drawRect(skia.Rect(sx - 60, y - size, sx + 60, y + size * 0.2), p); c.restore()

def chip(c, s, x, y, k, bg="#14213D", fg="#FFFFFF", size=40, fpath=FT_BLACK):
    if k <= 0: return
    b = back(clamp(k)); w = text_w(s, size, fpath) + size * 1.0; h = size * 1.5
    c.save(); c.translate(x, y); c.scale(b, b)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, bg, int(240 * clamp(k * 2)), shadow=12)
    text(c, s, 0, size * 0.36, size, fg, fpath, "c", int(255 * clamp(k * 2))); c.restore()

def counter(c, val, fmt, x, y, k, size=96, col=YEL, sub=None):
    if k <= 0: return
    v = val * ease_out(k); s = fmt(v)
    text(c, s, x, y, size, col, FT_BLACK, "c", int(255 * clamp(k * 3)), shadow=True)
    if sub: text(c, sub, x, y + size * 0.55, size * 0.36, "#FFFFFF", FT_SEMI, "c", int(255 * clamp(k * 3)), shadow=True)

def headline(c, s, k, sub=None, y=230, size=84, col="#FFFFFF"):
    if k <= 0: return
    serif_title(c, s, DW / 2, y, size, k, date=sub, col=col, align="c")

def credit(c, s, a=255, y=1528):
    if a <= 0 or not s: return
    f = font(FT_SEMI, 21); w = f.measureText(s)
    rrect(c, DW / 2 - w / 2 - 14, y - 22, DW / 2 + w / 2 + 14, y + 9, 8, "#000000", int(a * 0.55))
    text(c, s, DW / 2, y, 21, "#FFFFFF", FT_SEMI, "c", int(a * 0.95))

def era_chip(c, s, a):
    if a > 0: chip(c, s, DW / 2, 1462, a, "#3A2A1E", "#F4E3B5", 26, SERIF_TEXT)

_IMG = {}
def img(path, crop=None):
    key = (path, crop)
    if key not in _IMG:
        im = Image.open(path).convert("RGB")
        if crop: W, H = im.size; im = im.crop((int(crop[0] * W), int(crop[1] * H), int(crop[2] * W), int(crop[3] * H)))
        _IMG[key] = sk_image(im)
    return _IMG[key]

def card_tex(im, boxes, t, frame="#C9A227"):
    """gold-framed card texture of a real painting; boxes = [(x0,y0,x1,y1, t_on)] red marker boxes on parts of it."""
    W = 1000; H = int(W * im.height() / im.width()); pad = 26
    s = skia.Surface(W + pad * 2, H + pad * 2); cc = s.getCanvas(); cc.clear(hexc("#2B1D0E"))
    cc.drawRect(skia.Rect(4, 4, W + pad * 2 - 4, H + pad * 2 - 4), paint(frame, 255, stroke=6)); cc.drawRect(skia.Rect(14, 14, W + pad * 2 - 14, H + pad * 2 - 14), paint(frame, 200, stroke=2))
    cc.drawImageRect(im, skia.Rect(0, 0, im.width(), im.height()), skia.Rect(pad, pad, pad + W, pad + H), SAMP)
    for x0, y0, x1, y1, ton in boxes:
        k = seg(t, ton, ton + 0.45)
        if k <= 0: continue
        r = skia.Rect(pad + x0 * W, pad + y0 * H, pad + x1 * W, pad + y1 * H)
        pm = skia.PathMeasure(skia.Path().addRoundRect(r, 18, 18), False); L = pm.getLength(); part = skia.Path(); pm.getSegment(0, L * ease_out(k), part, True)
        cc.drawPath(part, paint("#E63946", 255, stroke=9, cap_round=True))
    return s.makeImageSnapshot()

def doc_show(c, t, d):
    """real painting / portrait flips in over whatever is on screen, 3D camera dollies to the marked part, flips out."""
    t_in, t_out = d["t_in"], d["t_out"]
    if not (t_in <= t <= t_out + 0.6): return
    k_in = seg(t, t_in, t_in + 0.55); k_out = seg(t, t_out, t_out + 0.55); mv = seg(t, t_in + 0.5, t_out)
    c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(120 * k_in * (1 - k_out))))
    doc_card(c, card_tex(d["img"], d.get("boxes", []), t), k_in, k_out, mv, d.get("focus", (0.5, 0.5)), d.get("zoom", 1.25), tilt=-8, yaw_end=-4, rest_w=d.get("rest_w", 0.86))
    a = int(255 * clamp(k_in * 2) * (1 - k_out))
    if d.get("cap"): chip(c, d["cap"], DW / 2, 300, clamp(k_in * 1.3) * (1 - k_out), "#14213D", "#FFFFFF", 36, SERIF_TEXT)
    if d.get("note"): chip(c, d["note"], DW / 2, 370, clamp(k_in * 1.3 - 0.2) * (1 - k_out), "#7A1F1F", "#FFFFFF", 26, FT_SEMI)
    credit(c, d.get("credit", ""), a)

# ================================================================== battle scenes (cartoon, kalpanik) on a real Haryana field photo
FARMS = PLC + "haryana_farms.jpg"
_BG = {}
def field_bg():
    if "f" not in _BG:
        im = Image.open(FARMS).convert("RGB"); W, H = im.size
        sky = ImageEnhance.Color(im.crop((0, 0, W, int(H * 0.62))).filter(ImageFilter.GaussianBlur(3))).enhance(0.9)
        grd = im.crop((0, int(H * 0.55), W, H)).filter(ImageFilter.GaussianBlur(1.5))
        _BG["f"] = (sk_image(sky), sk_image(grd))
    return _BG["f"]
def draw_field(c, t, t0, dur, tint=None):
    sky_, grd = field_bg(); k = ease_io(seg(t, t0, t0 + dur)); s = lerp(1.0, 1.06, k)
    hor = 1130
    w = DW * 1.6 * s; h = w * sky_.height() / sky_.width(); draw_img(c, sky_, DW / 2 - w / 2, hor - h, DW / 2 + w / 2, hor + 10)
    c.drawRect(skia.Rect(0, 0, DW, hor - h + 2), paint("#C9D3DA"))
    w2 = DW * 2.2 * s; h2 = DH - hor; draw_img(c, grd, DW / 2 - w2 / 2, hor - 4, DW / 2 + w2 / 2, DH)
    if tint: c.drawRect(skia.Rect(0, 0, DW, DH), paint(tint, 50))
    g = skia.GradientShader.MakeLinear([(0, 0), (0, 520)], [hexc("#000000", 150), hexc("#000000", 0)]); c.drawRect(skia.Rect(0, 0, DW, 520), skia.Paint(Shader=g))

BS = 0.86                                   # landscape battle (1920 design) -> vertical frame
def bt_begin(c):
    c.save(); c.translate(DW / 2, 0); c.scale(BS, BS); c.translate(-960, 1235 / BS - 1065 + 60)
def to_v(x, y): return DW / 2 + (x - 960) * BS, (y + 1235 / BS - 1065 + 60) * BS

def cannon(c, x, y, s, t, fires, face=1):
    c.save(); c.translate(x, y); c.scale(face * s, s)
    rec = 0
    for tf in fires:
        if 0 < t - tf < 0.25: rec = (1 - (t - tf) / 0.25) * 12
    c.save(); c.translate(-rec, 0); c.rotate(-8)
    c.drawRoundRect(skia.Rect(-60, -46, 70, -22), 10, 10, paint("#3B3B3B")); c.drawRect(skia.Rect(60, -48, 74, -20), paint("#2A2A2A")); c.restore()
    c.drawLine(-60, -10, -110, 20, paint("#6B4423", 255, stroke=10, cap_round=True))
    c.drawCircle(-10, -10, 26, paint("#6B4423", 255, stroke=7));
    for i in range(6): a_ = i / 6 * math.pi * 2 + 0.3; c.drawLine(-10, -10, -10 + math.cos(a_) * 24, -10 + math.sin(a_) * 24, paint("#6B4423", 255, stroke=3))
    for tf in fires:
        k = (t - tf)
        if 0 < k < 0.18: c.drawCircle(95, -50, 40 * (1 - k / 0.18) + 10, paint("#FFD23F", 240, blur=8)); c.drawCircle(95, -50, 18, paint("#FFFFFF", 255))
        if 0 < k < 2.2:
            for j in range(4):
                r = (20 + k * 60 + j * 14); a_ = int(160 * (1 - k / 2.2))
                c.drawCircle(100 + k * 90 + j * 26, -60 - k * 30 - j * 8, r, paint("#D8D4CC", a_, blur=10))
    c.restore()

class Sc1526:
    """Babur: wagon line + cannons + horse archers vs Lodi infantry and war elephants; cannon blasts panic the elephants."""
    def __init__(self, t0, dur, t_panic, t_win):
        self.t0, self.dur, self.tp, self.tw = t0, dur, t_panic, t_win
        self.B = Battle(dict(fac="mughal", cav=6, inf=3), dict(fac="lodi", inf=9, cav=3, eleph=3), "left", t0=t0, dur=dur, t_clash=1.6, t_rout=t_panic - t0 + 0.25,
                        clash_x=1040, seed=12, volley="L", base=112)
        self.fires = [t0 + 0.5 + i * 0.55 for i in range(int(dur / 0.55) + 2)]
    def draw(self, c, t):
        bt_begin(c)
        for i in range(4):                                         # araba wagons tied in a line (Baburnama)
            x = 420 + i * 70; y = 850 + i * 55
            c.drawRect(skia.Rect(x - 50, y - 60, x + 50, y - 20), paint("#7A5230")); c.drawCircle(x - 30, y - 12, 16, paint("#3A2A1E", 255, stroke=6)); c.drawCircle(x + 30, y - 12, 16, paint("#3A2A1E", 255, stroke=6))
        self.B.draw(c, t)
        for i in range(3): cannon(c, 560 + i * 60, 880 + i * 70, 0.9, t, [f + i * 0.17 for f in self.fires])
        c.restore()
    def sfx(self):
        return [("cannon", f, -9) for f in self.fires[:8]] + [("elephant", self.tp, -6), ("crowd_panic", self.tp + 0.2, -8), ("gallop_many", self.t0, -9)]

class Sc1556:
    """Hemu leads from his elephant Hawai; evenly matched; one arrow; he falls unconscious; his army scatters."""
    def __init__(self, t0, dur, t_arrow, t_rout):
        self.t0, self.dur, self.ta, self.tr = t0, dur, t_arrow, t_rout
        self.B = Battle(dict(fac="mughal", cav=7, inf=4), dict(fac="sur", inf=8, cav=3, eleph=3, king=True), "left", t0=t0, dur=dur, t_clash=1.5, t_rout=t_rout - t0,
                        clash_x=900, seed=21, base=112)
    def draw(self, c, t):
        bt_begin(c); self.B.draw(c, t)
        kx = self.B.king_xy(t)
        if kx:
            z, dx, dy = self.B.cam(t); x = self.B.cx + (kx[0] - self.B.cx) * z + dx; y = self.B.g[1] + (kx[1] - self.B.g[1]) * z + dy - 330 * z
            k = seg(t, self.ta - 0.55, self.ta)                       # the single arrow
            if 0 < k < 1:
                sx, sy = x - 900, y - 300; px, py = lerp(sx, x, k), lerp(sy, y, k) - 120 * 4 * k * (1 - k)
                c.drawLine(px - 46, py - 6, px, py, paint("#3A2A1E", 255, stroke=5)); c.drawCircle(px, py, 5, paint("#9CA3AF"))
                c.drawRect(skia.Rect(0, 0, 0, 0), paint("#000000"))
            hk = seg(t, self.ta, self.ta + 0.35)
            if hk > 0:
                c.drawCircle(x, y, 70 * (1 + hk), paint("#E63946", int(220 * (1 - hk)), stroke=10))
            nk = seg(t, self.t0 + 0.4, self.t0 + 0.9) * (1 - seg(t, self.ta + 1.2, self.ta + 1.6))
            if nk > 0: pill(c, "Hemu (haathi 'Hawai')", x, y - 150, 34, "#7C2D12", "#FFFFFF", int(255 * nk), fpath=FT_SEMI)
        c.restore()
    def sfx(self): return [("gallop_many", self.t0, -9), ("arrow_whiz", self.ta - 0.5, -4), ("arrow_hit", self.ta, -4), ("crowd_panic", self.tr + 0.1, -8)]

class Sc1761:
    """Maratha gun line (Ibrahim Khan Gardi) + cavalry vs Durrani cavalry; massive clash; Marathas routed."""
    def __init__(self, t0, dur, t_rout):
        self.t0, self.dur, self.tr = t0, dur, t_rout
        self.B = Battle(dict(fac="durrani", cav=9, inf=5), dict(fac="maratha", inf=9, cav=5), "left", t0=t0, dur=dur, t_clash=1.7, t_rout=t_rout - t0,
                        clash_x=920, seed=33, volley="R", base=108)
        self.fires = [t0 + 0.3 + i * 0.45 for i in range(int(dur / 0.45) + 2)]
    def draw(self, c, t):
        bt_begin(c); self.B.draw(c, t)
        for i in range(3): cannon(c, 1500 - i * 70, 860 + i * 70, 0.85, t, [f + i * 0.15 for f in self.fires if f < self.tr], face=-1)
        c.restore()
    def sfx(self): return [("cannon", f, -10) for f in self.fires[:6]] + [("gallop_many", self.t0, -8), ("clash_bed", self.t0 + 1.7, -8), ("crowd_panic", self.tr, -8)]

POP_RISE, POP_FILL, POP_OUT, POP_FOLD = 0.75, 0.35, 0.35, 0.45
SC = {
    "p1": (Sc1526(us(u_bhadak) - 1.5, ue(u_mughal) - us(u_bhadak) + 1.5, kw(u_bhadak, "bhadak"), kw(u_mughal, "Lodi")), us(u_bhadak) - 0.2, kw(u_mughal, "Mughal") - 0.25,
           "Panipat ka pehla yudh", "21 April 1526"),
    "p2": (Sc1556(kw(u_hemu, "Hawai") - 1.4, ue(u_bikhar) - kw(u_hemu, "Hawai") + 1.4, kw(u_teer, "teer"), kw(u_bikhar, "bikhar")), kw(u_hemu, "haathi"), ue(u_bikhar) - 0.2,
           "Panipat ka doosra yudh", "5 November 1556"),
    "p3": (Sc1761(us(u_badi) - 1.2, ue(u_maut) - us(u_badi) + 1.2, kw(u_maut, "maut") - 0.6), us(u_badi), ue(u_maut) - 0.1,
           "Panipat ka teesra yudh", "14 January 1761"),
}
def active_scene(t):
    for key, (sc, a, b, *_r) in SC.items():
        if a - POP_FILL - POP_RISE <= t <= b + POP_OUT + POP_FOLD: return key
    return None

def scene_draw(c, key, t):
    sc, a, b, title, date = SC[key]
    draw_field(c, t, a - 1.2, b - a + 2.4)
    sc.draw(c, t)
    headline(c, title, seg(t, a - 0.5, a + 0.6), date, y=230, size=72)
    if key == "p1":
        sx, sy = shake(t, kw(u_bhadak, "dhamaakon"), 18); c.save(); c.translate(sx, sy)
        stamp_slam(c, "HAATHI BHADAK GAYE", DW / 2, 520, 62, seg(t, kw(u_bhadak, "bhadak"), kw(u_bhadak, "bhadak") + 0.35) * (1 - seg(t, kw(u_mughal, "Lodi") - 0.2, kw(u_mughal, "Lodi"))), "#C1121F", -6)
        stamp_slam(c, "LODI MAARA GAYA", DW / 2, 520, 66, seg(t, kw(u_mughal, "maara"), kw(u_mughal, "maara") + 0.35), "#C1121F", -6); c.restore()
    if key == "p2":
        chip(c, "Ladaai barabar", DW / 2, 470, seg(t, us(u_teer), us(u_teer) + 0.4) * (1 - seg(t, kw(u_teer, "teer") - 0.1, kw(u_teer, "teer") + 0.2)), "#14213D")
        sx, sy = shake(t, kw(u_teer, "teer"), 14); c.save(); c.translate(sx, sy)
        stamp_slam(c, "EK TEER", DW / 2, 500, 80, seg(t, kw(u_teer, "teer"), kw(u_teer, "teer") + 0.3) * (1 - seg(t, kw(u_bikhar, "bikhar") - 0.3, kw(u_bikhar, "bikhar"))), "#C1121F", -7)
        stamp_slam(c, "FAUJ BIKHAR GAYI", DW / 2, 500, 64, seg(t, kw(u_bikhar, "bikhar"), kw(u_bikhar, "bikhar") + 0.35), "#C1121F", -6); c.restore()
    if key == "p3":
        mk = seg(t, kw(u_maut, "30"), kw(u_maut, "30") + 0.9)
        if mk > 0:
            rrect(c, 140, 380, DW - 140, 640, 30, "#000000", int(150 * clamp(mk * 3)))
            counter(c, 30000, lambda v: f"{int(v / 100) * 100:,}+", DW / 2, 520, mk, 120, YEL, "Maratha taraf maut (andaaze alag-alag)")
        else: chip(c, "18vi sadi ki sabse badi ladaaiyon mein se ek", DW / 2, 470, seg(t, kw(u_badi, "sabse"), kw(u_badi, "sabse") + 0.4), "#14213D", "#FFFFFF", 30, FT_SEMI)
    text(c, "Background: Haryana ke khet (asli photo: Last Emperor, CC BY-SA 3.0) · cartoon: kalpanik chitran", DW / 2, 1528, 19, "#FFFFFF", FT_SEMI, "c", 200, shadow=True)

def scene_image(key, t, width):
    h = int(width * DH / DW); s = skia.Surface(width, h); cc = s.getCanvas(); cc.scale(width / DW, width / DW); cc.clear(hexc("#000000"))
    scene_draw(cc, key, t); return s.makeImageSnapshot()

# ================================================================== the one continuous camera path (time, lon, lat, dist, pitch, yaw)
PNP = PL["panipat"]
def dive(key):
    sc, a, b, *_ = SC[key]
    return [(a - POP_FILL - POP_RISE - 0.2, PNP[0], PNP[1] - 0.5, 7.5, 52, 0), (a, PNP[0], PNP[1] - 0.35, 6.0, 56, 0), (b + POP_OUT, PNP[0], PNP[1] - 0.35, 6.0, 56, 0)]
KF = [(0.0, 78, 24, 70, 6, 0), (2.4, 78.5, 23.5, 34, 30, -6), (ue(u_hook), 77.8, 26.0, 22, 40, 2), (ue(u_kyun), 77.2, 28.4, 11, 50, 4),
      (us(u_1526) + 0.6, 73.5, 31.0, 22, 42, -6), (ue(u_babur), 72.8, 31.6, 20, 46, -2), (us(u_lodi) + 0.6, 76.5, 28.5, 22, 44, 6), (ue(u_lodi2) - 0.3, 76.8, 28.0, 21, 46, 2)]
KF += dive("p1")
KF += [(kw(u_mughal, "Mughal") + 1.2, 76.0, 27.0, 26, 42, -4), (us(u_1556) + 0.2, 76.0, 27.5, 26, 42, 0), (kw(u_hemu, "Delhi") + 0.6, 76.8, 27.6, 18, 46, 6)]
KF += dive("p2")
KF += [(us(u_1761) + 0.3, 74.0, 26.0, 40, 40, -4), (kw(u_abdali, "Abdali") + 0.2, 72.5, 27.5, 38, 40, 4), (ue(u_abdali) - 0.1, 75.0, 28.0, 30, 44, 0)]
KF += dive("p3")
KF += [(us(u_uttar) + 0.3, 73.6, 31.0, 22, 40, -6), (ue(u_uttar), 74.2, 30.6, 20, 44, 2), (kw(u_yamuna, "Yamuna") - 0.1, 76.4, 28.6, 10, 46, -6),
       (kw(u_yamuna, "Thar") + 0.3, 74.2, 28.3, 17, 44, 4), (ue(u_sapaat), 76.4, 28.8, 9, 50, 0), (us(u_95) + 0.3, 77.1, 28.9, 5.0, 52, -4), (us(u_tarain) + 0.2, 77.0, 29.35, 3.6, 50, 0),
       (kw(u_tarain, "Karnal") + 0.4, 77.0, 29.4, 3.6, 50, 4), (ue(u_matlab), 77.0, 29.1, 7.5, 50, 0), (us(u_poll) + 1.2, 79.5, 23.0, 44, 30, 0), (END, 79.5, 22.5, 46, 28, 3)]
KF.sort(key=lambda k: k[0])
def camera(t):
    if t <= KF[0][0]: return Cam(*KF[0][1:])
    for i in range(len(KF) - 1):
        a, b = KF[i], KF[i + 1]
        if a[0] <= t <= b[0]:
            k = (t - a[0]) / max(1e-6, b[0] - a[0]); cm = Cam.lerp(Cam(*a[1:]), Cam(*b[1:]), k)
            far = math.hypot(a[1] - b[1], a[2] - b[2])
            if far > 6:
                hop = math.sin(math.pi * ease_io(k)); return Cam(cm.lon, cm.lat, cm.dist * (1 + hop * far / 16), cm.pitch - 6 * hop, cm.yaw)
            return cm
    return Cam(*KF[-1][1:])

SAT = Satellite(55, 100, 5, 42)

# ================================================================== documents / real paintings (public domain)
DOCS_ON = [
    dict(img=img(DOCS + "baburnama.jpg"), t_in=kw(u_mughal, "Mughal") - 0.1, t_out=ue(u_mughal) + 0.55, focus=(0.5, 0.62), zoom=1.3, rest_w=0.62,
         boxes=[(0.05, 0.5, 0.95, 0.9, kw(u_mughal, "Mughal") + 0.5)], cap="Baburnama: Panipat 1526", credit="Deo Gujarati, c. 1590 (Vaqi'at-i Baburi) · public domain"),
    dict(img=img(DOCS + "hemu_1910s.jpg"), t_in=kw(u_hemu, "Hemu") - 0.05, t_out=kw(u_hemu, "haathi") - POP_FILL - POP_RISE - 0.35, focus=(0.5, 0.45), zoom=1.25, rest_w=0.6,
         boxes=[(0.33, 0.33, 0.67, 0.6, kw(u_hemu, "Hemu") + 0.4)], cap="Hemu 'Vikramaditya'", note="Aadhunik chitran (1910s) · asli portrait nahi",
         credit="Print, c. 1910s · public domain"),
    dict(img=img(DOCS + "akbarnama_hemu.jpg"), t_in=kw(u_bikhar, "bikhar") + 0.35, t_out=us(u_1761) + 0.25, focus=(0.5, 0.4), zoom=1.3, rest_w=0.6,
         boxes=[(0.25, 0.22, 0.75, 0.55, kw(u_bikhar, "bikhar") + 0.8)], cap="Akbarnama: Hemu ki haar", credit="Kankar, Akbarnama c. 1590s · public domain"),
    dict(img=img(DOCS + "abdali.jpg"), t_in=kw(u_abdali, "Ahmad") - 0.1, t_out=us(u_badi) - POP_FILL - POP_RISE - 0.35, focus=(0.5, 0.35), zoom=1.2, rest_w=0.56,
         cap="Ahmad Shah Abdali (Durrani)", credit="Mughal miniature c. 1757, BnF Paris · public domain"),
    dict(img=img(DOCS + "faizabad_1761.jpg"), t_in=kw(u_badi, "sabse") + 0.2, t_out=us(u_maut) - 0.1, focus=(0.42, 0.5), zoom=1.4, rest_w=0.92,
         boxes=[(0.25, 0.15, 0.62, 0.85, kw(u_badi, "ladaai") + 0.1)], cap="Panipat 1761: topon ki do qataarein", credit="Faizabad-style painting c. 1770 · public domain"),
]

# ================================================================== what is on the map at time t
def map_layer(c, cam, t):
    ind_k = 1 - seg(t, us(u_1526) - 0.4, us(u_1526) + 0.4)                       # present-day India only in the hook...
    ind_k = max(ind_k, seg(t, us(u_poll) - 0.2, us(u_poll) + 0.8))               # ...and at the end
    parchment(c, WM, cam)
    sat_a = 1 - seg(t, 1.6, 3.4)
    if sat_a > 0: satellite(c, SAT, cam, int(255 * sat_a))
    # ---- territories of each moment (period, andaazan)
    t1, t2, t3 = us(u_1526), us(u_1556), us(u_1761)
    terr = [("india", "tiranga", ind_k * seg(t, 0.8, 2.2) if t < t1 else ind_k),
            ("kabul", "mughal", seg(t, kw(u_babur, "Babur"), kw(u_babur, "Babur") + 0.8) * (1 - seg(t, kw(u_mughal, "Mughal") - 0.2, kw(u_mughal, "Mughal") + 0.2))),
            ("lodi", "lodi", 0.8 * seg(t, kw(u_lodi, "Lodi") - 0.3, kw(u_lodi, "Lodi") + 0.6) * (1 - seg(t, kw(u_mughal, "Mughal") - 0.2, kw(u_mughal, "Mughal") + 0.3))),
            ("mughal1530", "mughal", seg(t, kw(u_mughal, "Mughal"), kw(u_mughal, "Mughal") + 0.9) * (1 - seg(t, t2 - 0.1, t2 + 0.4))),
            ("akbar1556", "mughal", seg(t, t2, t2 + 0.6) * (1 - seg(t, kw(u_bikhar, "bikhar"), kw(u_bikhar, "bikhar") + 0.2))),
            ("sur1556", "sur", seg(t, kw(u_hemu, "Delhi"), kw(u_hemu, "Delhi") + 0.6) * (1 - seg(t, kw(u_bikhar, "bikhar"), kw(u_bikhar, "bikhar") + 0.2))),
            ("maratha", "bhagwa", seg(t, kw(u_abdali, "Marathe") - 0.1, kw(u_abdali, "Marathe") + 0.7) * (1 - seg(t, us(u_naksha), us(u_naksha) + 0.5))),
            ("afghan", "durrani", seg(t, kw(u_abdali, "Abdali") - 0.2, kw(u_abdali, "Abdali") + 0.6) * (1 - seg(t, us(u_naksha), us(u_naksha) + 0.5)))]
    for rk, kind, k in terr:
        if k > 0: flag_region(c, cam, PP(rk), kind, t, k)
    # ---- Babur's march Kabul -> Panipat, Abdali Kabul -> Panipat, Marathas Pune -> Delhi -> Panipat
    mk = seg(t, kw(u_babur, "Babur") + 0.3, ue(u_babur) + 0.3)
    if mk > 0 and t < SC["p1"][1]: route(c, cam, [PL["kabul"], PL["khyber"], PL["lahore"], PL["ambala"], PNP], mk, "#2F6B3A", 7, True, t)
    ak = seg(t, kw(u_abdali, "Abdali") + 0.1, ue(u_abdali) + 0.4); mk2 = seg(t, kw(u_abdali, "Marathe"), ue(u_abdali) + 0.4)
    if t < SC["p3"][1]:
        if ak > 0: route(c, cam, [PL["kandahar"], PL["kabul"], PL["khyber"], PL["lahore"], PL["ambala"], PNP], ak, "#1F2937", 7, True, t)
        if mk2 > 0: route(c, cam, [PL["pune"], PL["bhopal"], PL["gwalior"], PL["agra"], PL["delhi"], PNP], mk2, "#E8731A", 7, True, t)
    # ---- the corridor: Uttarapath, Yamuna, Thar, flat land, 95 km, Tarain + Karnal
    uk = seg(t, kw(u_uttar, "Kabul"), kw(u_uttar, "Uttarapath") + 0.4)
    if uk > 0 and t < us(u_poll):
        rr = route(c, cam, UTTAR, uk, "#FFD23F", 9, False, t)
        if rr and uk >= 1:
            pm, L = rr; f = (t * 0.25) % 1.0; pos, _ = pm.getPosTan(L * f); c.drawCircle(pos.x(), pos.y(), 14, paint("#FFFFFF", 220, blur=6))
    yk = seg(t, kw(u_yamuna, "Yamuna") - 0.2, kw(u_yamuna, "Yamuna") + 1.0) * (1 - seg(t, us(u_poll), us(u_poll) + 0.6))
    river(c, cam, YAMUNA, yk, t, pulse=seg(t, kw(u_yamuna, "Yamuna") + 0.8, kw(u_yamuna, "Yamuna") + 1.2) * (1 - seg(t, us(u_95), us(u_95) + 0.5)))
    tk = seg(t, kw(u_yamuna, "Thar") - 0.1, kw(u_yamuna, "Thar") + 0.6) * (1 - seg(t, us(u_95), us(u_95) + 0.6))
    glow_region(c, cam, PP("thar"), tk, "#F5B83D", t)
    bk = seg(t, us(u_sapaat), us(u_sapaat) + 0.8) * (1 - seg(t, us(u_poll), us(u_poll) + 0.5))
    if bk > 0:                                                     # the flat strip between river and desert: horses gallop down it
        cor = [(75.2, 31.2), (76.2, 30.4), (76.85, 29.5), (77.1, 28.7)]
        route(c, cam, cor, bk, "#FFFFFF", 26, False, t)
        for j in range(3):
            f = ((t - us(u_sapaat)) * 0.3 + j / 3) % 1.0
            rr = route(c, cam, cor, 1.0, "#FFFFFF", 0.01, False, t)
            if rr: pm, L = rr; pos, tan = pm.getPosTan(L * f); horse(c, pos.x(), pos.y() + 14, 26, t, t * 3 + j, 1 if tan.x() > 0 else -1, "#5B3A22", rider_fn("rajput", "attack", t * 3 + j, t, 1), int(255 * bk))
    dk = seg(t, kw(u_95, "95") - 0.2, kw(u_95, "95") + 0.6) * (1 - seg(t, us(u_tarain) - 0.2, us(u_tarain) + 0.3))
    if dk > 0:
        a_ = cam.ll(*PNP); b_ = cam.ll(*PL["delhi"])
        if a_ and b_:
            ex, ey = lerp(a_[0], b_[0], ease_out(dk)), lerp(a_[1], b_[1], ease_out(dk))
            c.drawLine(a_[0], a_[1], ex, ey, paint("#000000", 160, stroke=12, cap_round=True)); c.drawLine(a_[0], a_[1], ex, ey, paint(YEL, 255, stroke=6, cap_round=True))
            for j in range(1, 6):
                f = j / 6
                if f < dk: x_, y_ = lerp(a_[0], b_[0], f), lerp(a_[1], b_[1], f); c.drawCircle(x_, y_, 6, paint("#FFFFFF"))
            mx, my = (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2; chip(c, "95 km", mx + 120, my, dk, "#C1121F", "#FFFFFF", 44)
    # ---- pins
    pk = 1 - seg(t, us(u_poll) - 0.2, us(u_poll) + 0.3)
    pin(c, cam, *PNP, "Panipat", seg(t, 1.0, 1.6) * pk * (1 - seg(t, kw(u_kyun, "Panipat") - 0.3, kw(u_kyun, "Panipat")) * (1 - seg(t, us(u_1526) - 0.2, us(u_1526) + 0.3))), t, sub="Haryana", col="#E63946")
    pin(c, cam, *PL["delhi"], "Delhi", (seg(t, kw(u_lodi, "Lodi"), kw(u_lodi, "Lodi") + 0.4) * (1 - seg(t, us(u_1761), us(u_1761) + 0.3)) + seg(t, kw(u_uttar, "Delhi"), kw(u_uttar, "Delhi") + 0.4)) * pk, t, col="#1D4ED8")
    pin(c, cam, *PL["kabul"], "Kabul", (seg(t, kw(u_babur, "Babur"), kw(u_babur, "Babur") + 0.4) * (1 - seg(t, us(u_lodi), us(u_lodi) + 0.3)) + seg(t, kw(u_uttar, "Kabul"), kw(u_uttar, "Kabul") + 0.4)) * pk, t, col="#2F6B3A")
    for nm, yr, dx, word in (("tarain", "Tarain 1192", -170, "Tarain"), ("karnal", "Karnal 1739", 170, "Karnal")):
        k = seg(t, kw(u_tarain, word), kw(u_tarain, word) + 0.4) * pk
        pin(c, cam, *PL[nm], "", k, t, col="#7A1F1F"); q = cam.ll(*PL[nm])
        if q and k > 0: swords(c, q[0], q[1] - 120, 0.45, k); chip(c, yr, q[0] + dx, q[1] - 60, k, "#7A1F1F", "#FFFFFF", 34)
    # ---- floating period banners (PRATIK) with the ruler's name
    fl = [(PL["kabul"][0], PL["kabul"][1] + 0.6, "mughal", "Babur (Kabul)", seg(t, kw(u_babur, "Babur") + 0.2, kw(u_babur, "Babur") + 0.7) * (1 - seg(t, us(u_lodi), us(u_lodi) + 0.4))),
          (78.0, 28.0, "lodi", "Ibrahim Lodi", seg(t, kw(u_lodi, "Lodi"), kw(u_lodi, "Lodi") + 0.5) * (1 - seg(t, SC["p1"][1] - 1.1, SC["p1"][1] - 0.8))),
          (73.0, 31.5, "mughal", "Akbar + Bairam Khan", seg(t, us(u_1556) + 0.3, us(u_1556) + 0.8) * (1 - seg(t, SC["p2"][1] - 1.1, SC["p2"][1] - 0.8))),
          (79.5, 27.0, "sur", "Hemu", seg(t, kw(u_hemu, "Delhi"), kw(u_hemu, "Delhi") + 0.5) * (1 - seg(t, SC["p2"][1] - 1.1, SC["p2"][1] - 0.8))),
          (PL["pune"][0], PL["pune"][1] + 1.0, "bhagwa", "Marathe (Sadashivrao Bhau)", seg(t, kw(u_abdali, "Marathe"), kw(u_abdali, "Marathe") + 0.5) * (1 - seg(t, SC["p3"][1] - 1.1, SC["p3"][1] - 0.8))),
          (66.5, 33.0, "durrani", "Ahmad Shah Abdali", seg(t, kw(u_abdali, "Abdali"), kw(u_abdali, "Abdali") + 0.5) * (1 - seg(t, SC["p3"][1] - 1.1, SC["p3"][1] - 0.8)))]
    fl.sort(key=lambda f: -((cam.ll(f[0], f[1]) or (0, 0, 1e9))[2]))
    for lo, la, kd, lb, k in fl:
        if k > 0: float_flag(c, cam, lo, la, kd, t, k, lb, size=1.25)
    # ---- crossed-sword marks of all battles on the corridor at the end of the explanation
    for j, (key, y_) in enumerate((("panipat", "3x"), ("tarain", ""), ("karnal", ""))):
        pass

def swords(c, x, y, s, k, col="#FFD23F"):
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(back(k) * s, back(k) * s)
    for r in (-40, 40):
        c.save(); c.rotate(r); c.drawLine(0, -46, 0, 40, paint("#1A1A1A", 200, stroke=13, cap_round=True)); c.drawLine(0, -46, 0, 40, paint(col, 255, stroke=7, cap_round=True))
        c.drawLine(-14, 24, 14, 24, paint(col, 255, stroke=7, cap_round=True)); c.restore()
    c.restore()

# ================================================================== screen overlays: hook, timeline, captions, ending
YRS = [1192, 1526, 1556, 1739, 1761]
def year_pos(t):
    k1 = seg(t, us(u_1526) - 0.2, us(u_1526) + 0.4); k2 = seg(t, us(u_1556) - 0.1, us(u_1556) + 0.6); k3 = seg(t, us(u_1761) - 0.1, us(u_1761) + 0.6)
    return 1 + k2 + 2 * k3, (k2 * (1 - k2) + k3 * (1 - k3)) * 4

CAPS = []
KEYW = ("Panipat", "Babur", "Lodi", "Mughal", "Hemu", "Vikramaditya", "Hawai", "Marathe", "Maratha", "Abdali", "Uttarapath", "Yamuna", "Thar", "Delhi", "Tarain", "Karnal", "teer", "topein", "haathi", "kismat", "maut", "subscribe", "Comment")
def _caps():
    for i, u in enumerate(UN):
        w = u["text"].split(); n = len(w); groups = [w[j:j + 4] for j in range(0, n, 4)]
        if len(groups) > 1 and len(groups[-1]) == 1: groups[-2] += groups[-1]; groups.pop()
        d = u["end"] - u["start"]; pos = 0
        for g in groups:
            a = u["start"] + d * pos / n; pos += len(g); b = u["start"] + d * pos / n
            CAPS.append((a, b, g))
_caps()
def captions(c, t):
    for a, b, g in CAPS:
        if a - 0.05 <= t < b + 0.05:
            k = seg(t, a - 0.05, a + 0.15); size = 54; ws = [(x, text_w(x + " ", size)) for x in g]; W = sum(w for _, w in ws)
            x = DW / 2 - W / 2; y = 1395 + (1 - ease_out(k)) * 16
            for wd, w in ws:
                hot = any(ch.isdigit() for ch in wd) or any(wd.strip(".,?!").lower().startswith(kk.lower()) for kk in KEYW)
                c.drawString(wd, x + 3, y + 4, font(FT_BLACK, size), paint("#000000", int(200 * k)))
                st = paint("#000000", int(255 * k), stroke=9); c.drawString(wd, x, y, font(FT_BLACK, size), st)
                c.drawString(wd, x, y, font(FT_BLACK, size), paint(YEL if hot else "#FFFFFF", int(255 * k))); x += w
            return

def timeline(c, t, a):
    if a <= 0: return
    from storyproof import timeline_ribbon
    pos, vel = year_pos(t)
    rrect(c, DW / 2 - 320, 1180, DW / 2 + 320, 1268, 44, "#000000", int(120 * a))
    timeline_ribbon(c, YRS, pos, y=1236, spacing=190, vel=vel, a=int(255 * a))

def poll(c, t):
    k0 = seg(t, us(u_poll) + 0.2, us(u_poll) + 0.7)
    if k0 <= 0: return
    rrect(c, 90, 430, DW - 90, 1120, 36, "#F4EFE4", int(245 * k0), shadow=20)
    text(c, "Kis ladaai ne India ko", DW / 2, 520, 50, "#14213D", SERIF_DISPLAY, "c", int(255 * k0))
    text(c, "sabse zyada badla?", DW / 2, 585, 50, "#14213D", SERIF_DISPLAY, "c", int(255 * k0))
    opts = [("A", "1526 · Babur vs Lodi", "1526"), ("B", "1556 · Akbar vs Hemu", "1556"), ("C", "1761 · Marathe vs Abdali", "1761")]
    for i, (l, s, word) in enumerate(opts):
        k = seg(t, kw(u_opts, word) - 0.1, kw(u_opts, word) + 0.3); y = 690 + i * 130
        if k <= 0: continue
        c.save(); c.translate(DW / 2, y); c.scale(back(k), back(k))
        rrect(c, -400, -50, 400, 50, 25, "#14213D", 255); c.drawCircle(-340, 0, 34, paint(YEL)); text(c, l, -340, 15, 40, "#14213D", FT_BLACK, "c")
        text(c, s, 20, 14, 38, "#FFFFFF", FT_SEMI, "c"); c.restore()
    ck = seg(t, kw(u_sub, "Comment"), kw(u_sub, "Comment") + 0.4)
    stamp_slam(c, "COMMENT KARO", DW / 2, 1090, 56, ck, "#C1121F", -4)

def subscribe(c, t):
    k = seg(t, kw(u_sub, "subscribe") - 0.3, kw(u_sub, "subscribe") + 0.2)
    if k <= 0: return
    clk = seg(t, kw(u_sub, "subscribe") + 0.5, kw(u_sub, "subscribe") + 0.7); done = clk >= 1
    c.save(); c.translate(DW / 2, 260); s = back(k) * (1 - 0.08 * math.sin(math.pi * clk)); c.scale(s, s)
    rrect(c, -230, -55, 230, 55, 55, "#606060" if done else "#E62117", 255, shadow=14)
    text(c, "SUBSCRIBED" if done else "SUBSCRIBE", 0, 16, 44, "#FFFFFF", FT_BLACK, "c"); c.restore()
    cx_, cy_ = lerp(DW / 2 + 320, DW / 2 + 90, ease_out(seg(t, kw(u_sub, "subscribe"), kw(u_sub, "subscribe") + 0.45))), lerp(420, 290, ease_out(seg(t, kw(u_sub, "subscribe"), kw(u_sub, "subscribe") + 0.45)))
    p = skia.Path(); p.moveTo(cx_, cy_); p.lineTo(cx_, cy_ + 56); p.lineTo(cx_ + 14, cy_ + 43); p.lineTo(cx_ + 26, cy_ + 66); p.lineTo(cx_ + 35, cy_ + 61); p.lineTo(cx_ + 24, cy_ + 39); p.lineTo(cx_ + 42, cy_ + 38); p.close()
    c.drawPath(p, paint("#FFFFFF")); c.drawPath(p, paint("#000000", 255, stroke=3))

def overlays(c, t, cam):
    # ---- hook: "EK HI MAIDAN" -> PANIPAT glides in letter by letter, "?" drops on "kyun", three battle years pop on "teen"
    hk_out = 1 - seg(t, us(u_1526) - 0.3, us(u_1526) + 0.1)
    if hk_out > 0:
        serif_title(c, "Ek hi maidan", DW / 2, 230, 70, seg(t, 0.1, 1.0) * hk_out, align="c")
        for i, y_ in enumerate(("1526", "1556", "1761")):
            k = seg(t, kw(u_hook, "teen") + i * 0.18, kw(u_hook, "teen") + i * 0.18 + 0.4) * hk_out
            if k > 0: swords(c, 240 + i * 300, 340, 0.55, k); chip(c, y_, 240 + i * 300, 420, k, "#7A1F1F", "#FFFFFF", 40)
        pk = seg(t, kw(u_kyun, "Panipat") - 0.15, kw(u_kyun, "Panipat") + 0.55) * hk_out
        hook_word(c, "PANIPAT", DW / 2, 640, 150, pk, t, cols=["#FFD23F", "#FFFFFF"], shine_t=kw(u_kyun, "Panipat") + 0.6)
        qk = seg(t, kw(u_kyun, "kyun") - 0.05, kw(u_kyun, "kyun") + 0.35) * hk_out
        if qk > 0:
            yq = lerp(-200, 650, ease_out(qk)) + (math.sin(qk * 9) * 20 * (1 - qk))
            text(c, "?", DW / 2 + text_w("PANIPAT", 150, SERIF_DISPLAY) / 2 + 60, yq, 190, "#E63946", SERIF_DISPLAY, "c", 255, shadow=True)
        chip(c, "Teen baar kismat badli", DW / 2, 760, seg(t, kw(u_hook, "kismat"), kw(u_hook, "kismat") + 0.4) * (1 - seg(t, kw(u_kyun, "Panipat") - 0.3, kw(u_kyun, "Panipat"))), "#14213D", "#FFFFFF", 38)
    # ---- 1526 numbers
    b_k = seg(t, kw(u_babur, "12"), kw(u_babur, "12") + 0.9) * (1 - seg(t, us(u_lodi) - 0.3, us(u_lodi)))
    headline(c, "Babur", seg(t, kw(u_babur, "Babur") - 0.1, kw(u_babur, "Babur") + 0.7) * (1 - seg(t, us(u_lodi) - 0.3, us(u_lodi))), "Kabul se aaya")
    if b_k > 0:
        counter(c, 12000, lambda v: f"{int(v):,}", 300, 470, b_k, 86, "#9BE59B", "sainik")
        chip(c, "15-20 topein", 780, 445, seg(t, kw(u_babur, "topein") - 0.2, kw(u_babur, "topein") + 0.3) * (1 - seg(t, us(u_lodi) - 0.3, us(u_lodi))), "#2F6B3A", "#FFFFFF", 40)
    headline(c, "Ibrahim Lodi", seg(t, kw(u_lodi, "Lodi") - 0.3, kw(u_lodi, "Lodi") + 0.7) * (1 - seg(t, SC["p1"][1] - 1.2, SC["p1"][1] - 0.9)), "Delhi Sultanat")
    l_k = seg(t, us(u_lodi2), us(u_lodi2) + 0.9) * (1 - seg(t, SC["p1"][1] - 1.2, SC["p1"][1] - 0.9))
    if l_k > 0:
        chip(c, "50-70 hazaar", 300, 450, l_k, "#1E3A8A", "#FFFFFF", 48); text(c, "sainik (andaaze alag, behes)", 300, 525, 24, "#FFFFFF", FT_SEMI, "c", int(255 * clamp(l_k * 2)), shadow=True)
        k2 = seg(t, kw(u_lodi2, "1,000") - 0.2, kw(u_lodi2, "1,000") + 0.5) * (1 - seg(t, SC["p1"][1] - 1.2, SC["p1"][1] - 0.9))
        counter(c, 1000, lambda v: f"{int(v):,}", 790, 470, k2, 72, "#9CC3FF", "haathi")
    # ---- after 1526
    headline(c, "Mughal raaj shuru", seg(t, SC["p1"][2] + POP_OUT, SC["p1"][2] + POP_OUT + 0.6) * (1 - seg(t, us(u_1556) - 0.3, us(u_1556))), "1526 ke baad (naksha c. 1530, andaazan)")
    headline(c, "30 saal baad", seg(t, us(u_1556), us(u_1556) + 0.6) * (1 - seg(t, kw(u_hemu, "Hemu") - 0.3, kw(u_hemu, "Hemu"))), "1556")
    chip(c, "Delhi jeeti -> 'Vikramaditya'", DW / 2, 460, seg(t, kw(u_hemu, "Vikramaditya") - 0.3, kw(u_hemu, "Vikramaditya") + 0.2) * (1 - seg(t, kw(u_hemu, "haathi") - 0.6, kw(u_hemu, "haathi") - 0.3)), "#7C2D12", "#FFFFFF", 38)
    headline(c, "Marathe vs Abdali", seg(t, kw(u_abdali, "Marathe") - 0.2, kw(u_abdali, "Marathe") + 0.8) * (1 - seg(t, SC["p3"][1] - 1.2, SC["p3"][1] - 0.9)), "14 January 1761")
    # ---- the why
    headline(c, "Ab naksha dekho", seg(t, us(u_naksha), us(u_naksha) + 0.6) * (1 - seg(t, kw(u_uttar, "Uttarapath") - 0.3, kw(u_uttar, "Uttarapath"))))
    headline(c, "UTTARAPATH", seg(t, kw(u_uttar, "Uttarapath") - 0.1, kw(u_uttar, "Uttarapath") + 0.7) * (1 - seg(t, us(u_yamuna) - 0.2, us(u_yamuna) + 0.1)), "Kabul -> Delhi ka purana raasta (aaj GT Road)", col=YEL)
    chip(c, "YAMUNA", 800, 470, seg(t, kw(u_yamuna, "Yamuna") - 0.1, kw(u_yamuna, "Yamuna") + 0.3) * (1 - seg(t, us(u_95), us(u_95) + 0.3)), "#0B6E99", "#FFFFFF", 44)
    chip(c, "THAR REGISTAN", 300, 470, seg(t, kw(u_yamuna, "Thar") - 0.1, kw(u_yamuna, "Thar") + 0.3) * (1 - seg(t, us(u_95), us(u_95) + 0.3)), "#B7791F", "#FFFFFF", 40)
    chip(c, "SAPAAT ZAMEEN = GHUDSAWAARI", DW / 2, 330, seg(t, kw(u_sapaat, "sapaat"), kw(u_sapaat, "sapaat") + 0.4) * (1 - seg(t, us(u_95), us(u_95) + 0.3)), "#14213D", YEL, 38)
    mk = seg(t, us(u_matlab) + 0.2, us(u_matlab) + 0.6) * (1 - seg(t, us(u_poll) - 0.3, us(u_poll)))
    if mk > 0:
        sx, sy = shake(t, kw(u_matlab, "Panipat"), 12); c.save(); c.translate(sx, sy)
        stamp_slam(c, "DELHI KA DARWAZA", DW / 2, 330, 72, mk, "#C1121F", -5)
        stamp_slam(c, "= PANIPAT", DW / 2, 450, 72, seg(t, kw(u_matlab, "Panipat"), kw(u_matlab, "Panipat") + 0.35) * (1 - seg(t, us(u_poll) - 0.3, us(u_poll))), "#1D6F42", -5); c.restore()
    # ---- era chips (map of its own time) and timeline
    era = [(us(u_1526), SC["p1"][1] - 1.0, "Naksha: c. 1500 (andaazan) · flags: PRATIK"), (SC["p1"][2] + 0.4, us(u_1556), "Naksha: c. 1530 (andaazan) · flags: PRATIK"),
           (us(u_1556), SC["p2"][1] - 1.0, "Naksha: 1556 andaazan · flags: PRATIK"), (us(u_1761), SC["p3"][1] - 1.0, "Naksha: c. 1760s-80s (andaazan) · flags: PRATIK"),
           (us(u_poll) + 0.3, END, "Aaj ka Bharat")]
    for a, b, s in era: era_chip(c, s, seg(t, a, a + 0.4) * (1 - seg(t, b - 0.3, b)))
    tl_a = seg(t, us(u_1526) - 0.2, us(u_1526) + 0.3) * (1 - seg(t, us(u_naksha), us(u_naksha) + 0.4))
    for key in SC:
        sc, a, b, *_ = SC[key]; tl_a *= 1 - seg(t, a - 1.1, a - 0.8) * (1 - seg(t, b + 0.6, b + 0.9))
    for d in DOCS_ON: tl_a *= 1 - seg(t, d["t_in"], d["t_in"] + 0.3) * (1 - seg(t, d["t_out"], d["t_out"] + 0.3))
    timeline(c, t, tl_a)
    if t > us(u_poll) - 0.2: poll(c, t); subscribe(c, t)
    credit(c, "Borders: historical-basemaps (A. Ourednik, GPL-3.0), andaazan · Satellite: NASA Blue Marble", int(255 * seg(t, us(u_1526), us(u_1526) + 0.5) * (1 - seg(t, us(u_lodi2), us(u_lodi2) + 0.4))), y=1560)

# ================================================================== frame
_LOGO = {}
def logo(c):
    if "l" not in _LOGO:
        import glob as _g
        f = next(iter(_g.glob(PLUG + "/engine/brand/*logo*.png")), None); _LOGO["l"] = sk_image(Image.open(f).convert("RGBA")) if f else None
    L = _LOGO["l"]
    if L: draw_img(c, L, DW - 150, 40, DW - 40, 40 + 110 * L.height() / L.width(), 170)

def frame(c, t, width):
    cam = camera(t); key = active_scene(t)
    if key:
        sc, a, b, *_r = SC[key]
        if a <= t <= b: scene_draw(c, key, t)
        else:
            map_layer(c, cam, t); overlays(c, t, cam)
            if t < a: rise, fill = seg(t, a - POP_FILL - POP_RISE, a - POP_FILL), seg(t, a - POP_FILL, a)
            else: fill, rise = 1 - seg(t, b, b + POP_OUT), 1 - seg(t, b + POP_OUT, b + POP_OUT + POP_FOLD)
            popup(c, cam, *PNP, scene_image(key, min(max(t, a - 0.6), b + 0.6), width), cam.dist * 0.32, rise, fill)
    else:
        map_layer(c, cam, t); overlays(c, t, cam)
    for d in DOCS_ON: doc_show(c, t, d)
    captions(c, t)
    logo(c)
    if t > VO_END + 0.4: c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(255 * seg(t, VO_END + 0.4, END))))

def render(t, width=540):
    h = int(width * DH / DW) // 2 * 2; s = skia.Surface(width, h); c = s.getCanvas(); c.scale(width / DW, width / DW); c.clear(hexc("#000000"))
    frame(c, t, width); return s.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

def sfx_events():
    E = [("whoosh", 0.0, -8), ("riser", 0.3, -14), ("pin", 1.1, -8)]
    E += [("pop", kw(u_hook, "teen") + i * 0.18, -10) for i in range(3)] + [("whoosh", kw(u_kyun, "Panipat") - 0.1, -9), ("drop", kw(u_kyun, "kyun"), -8)]
    for d in DOCS_ON: E += [("paper", d["t_in"], -5), ("paper", d["t_out"], -7)]
    for key, (sc, a, b, *_r) in SC.items():
        E += [("whoosh", a - POP_FILL - POP_RISE - 0.2, -8), ("paper", a - POP_FILL - POP_RISE, -9), ("swish", a - POP_FILL, -10), ("swish", b, -11), ("paper", b + POP_OUT, -11)]
        E += sc.sfx()
    E += [("tick", us(u_1526), -8), ("tick", us(u_1556), -8), ("tick", us(u_1761), -8), ("pop", kw(u_babur, "12"), -10), ("pop", kw(u_babur, "topein"), -10),
          ("pop", us(u_lodi2), -10), ("pop", kw(u_lodi2, "1,000"), -10), ("stamp", kw(u_bhadak, "bhadak"), -4), ("stamp", kw(u_mughal, "maara"), -4),
          ("stamp", kw(u_teer, "teer"), -4), ("stamp", kw(u_bikhar, "bikhar"), -5), ("pop", kw(u_maut, "30"), -8), ("whoosh", us(u_naksha), -8),
          ("riser", kw(u_uttar, "Kabul"), -14), ("chime", kw(u_uttar, "Uttarapath"), -10), ("water", kw(u_yamuna, "Yamuna"), -10), ("wind", kw(u_yamuna, "Thar"), -12),
          ("gallop_few", us(u_sapaat), -10), ("tick", kw(u_95, "95"), -8), ("pin", kw(u_tarain, "Tarain"), -8), ("pin", kw(u_tarain, "Karnal"), -8),
          ("stamp", us(u_matlab) + 0.2, -4), ("stamp", kw(u_matlab, "Panipat"), -4), ("whoosh", us(u_poll), -8)]
    E += [("pop", kw(u_opts, w), -9) for w in ("1526", "1556", "1761")] + [("stamp", kw(u_sub, "Comment"), -6), ("click", kw(u_sub, "subscribe") + 0.6, -6), ("chime", VO_END + 0.1, -12)]
    return sorted([e for e in E if 0 <= e[1] < END], key=lambda e: e[1])

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        for ts in sys.argv[3:]: Image.fromarray(render(float(ts), 540)).convert("RGB").save(os.path.join(out, f"t{float(ts):06.2f}.png"))
    elif mode == "sfx":
        json.dump({"end": END, "events": sfx_events()}, open(PROJ + "/audio/sfx_events.json", "w"), indent=1); print("sfx", len(sfx_events()), "end", round(END, 2))
    elif mode == "info":
        print("END", round(END, 2)); [print(k, round(v[1], 2), round(v[2], 2)) for k, v in SC.items()]
    else:
        out = sys.argv[2]; width = int(sys.argv[3]); fps = int(sys.argv[4]); a_ = int(sys.argv[5]); b_ = int(sys.argv[6]); h = int(width * DH / DW) // 2 * 2
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{width}x{h}", "-r", str(fps), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a_, b_): ff.stdin.write(render(f / fps, width).tobytes())
        ff.stdin.close(); ff.wait(); print("video ok", out, a_, b_)
