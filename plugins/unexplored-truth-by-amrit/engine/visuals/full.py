"""AMRIT BORI - 'Naya Axis' full documentary renderer (4K60 10-bit). 2D flat engine + 3D host frames + captions."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import os, sys, math, json, subprocess
os.environ.setdefault("SCENE1_TIMING", "voice/scene1_full_timing.json")
os.environ.setdefault("FULL", "1"); os.environ.setdefault("FOOTNOTE_TOP", "1")
import numpy as np, skia
from PIL import Image
from core import *
from widgets import *
import scene1

ROOT = PROJ + ""
UN = json.load(open(ROOT + "voice/full_units.json"))["units"]
SIL = [tuple(map(float, l.split())) for l in open(ROOT + "voice/full_sil.tsv")]
VO_END = 522.6
T_TOTAL = 528.0
def us(i): return UN[i]["start"]
def ue(i): return UN[i]["end"]
def vin(i): return us(i) - 0.12
def kw(i, word, occ=0):
    """approximate time the word starts inside unit i (char-proportional, snapped to an internal pause)"""
    txt = UN[i]["text"]; low = txt.lower(); p = -1
    for _ in range(occ + 1): p = low.find(word.lower(), p + 1)
    if p < 0: return us(i)
    est = us(i) + (ue(i) - us(i)) * p / max(1, len(txt))
    best = None
    for a, b in SIL:
        if us(i) < b < ue(i) and abs(b - est) < 0.35 and (best is None or abs(b - est) < abs(best - est)): best = b
    return (best if best else est) - 0.05

# ------------------------------------------------------------------ places
PL = dict(wash=(-77.04, 38.9), beijing=(116.4, 39.9), halifax=(-63.57, 44.65), moscow=(37.62, 55.75), tehran=(51.39, 35.69),
          pyong=(125.76, 39.03), kyiv=(30.52, 50.45), kursk=(36.19, 51.73), alabuga=(52.05, 55.76), caspian=(50.5, 42.0),
          rason=(130.3, 42.25), vlad=(131.9, 43.1), hormuz=(56.4, 26.6), chabahar=(60.62, 25.29), gwadar=(62.33, 25.12),
          delhi=(77.21, 28.61), saudi=(50.16, 26.64), basra=(47.8, 30.5), uae=(54.4, 24.4), jamnagar=(70.0, 22.4),
          israel=(35.2, 31.8), ukraine=(31.2, 49.0), baghdad=(44.36, 33.31), novoross=(37.77, 44.72), ladakh=(78.5, 34.6))
def S(cam, key): return to_screen(cam, *PL[key])
CR = {"CHN": PAL["CHN"], "RUS": PAL["RUS"], "IRN": PAL["IRN"], "PRK": PAL["PRK"]}

LOGO = None; DOCS = {}; LOGO_BIG = None; CARDS = []
def load_assets():
    global LOGO, LOGO_BIG
    if LOGO is not None: return
    scene1.load()
    LOGO = scene1.A["logo"]; LOGO_BIG = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_4096.png").resize((1200, 1200)))
    for k in ("c1", "c2", "c3", "c4"): CARDS.append(sk_image(Image.open(ROOT + f"visuals/docs/cards/{k}.png")))
    d = ROOT + "visuals/docs/full/"
    for f in os.listdir(d):
        if f.endswith(".json"):
            k = f[:-5]; j = json.load(open(d + f)); im = Image.open(d + k + ".png").convert("RGBA")
            DOCS[k] = (sk_image(im), im.size, [[(l["x0"], l["y"], l["x1"], l["h"]) for l in L] for L in j["lines"]], j["url"].replace("https://", ""))

def doc(c, key, x0, y0, w, h, t, focus, sweeps, a=255, zoom=1.0):
    """sweeps: list of (line_index, t_start, dur)"""
    img, (iw, ih), lines, url = DOCS[key]
    bar = 54
    rrect(c, x0, y0, x0 + w, y0 + h, 18, "#FFFFFF", a, shadow=28)
    c.save(); c.clipRect(skia.Rect(x0, y0, x0 + w, y0 + bar)); c.drawRoundRect(skia.Rect(x0, y0, x0 + w, y0 + bar + 20), 18, 18, paint("#E7EAF0", a)); c.restore()
    for i, col in enumerate(("#FF5F57", "#FEBC2E", "#28C840")): c.drawCircle(x0 + 30 + i * 26, y0 + bar / 2, 8, paint(col, a))
    rrect(c, x0 + 120, y0 + 12, x0 + w - 24, y0 + bar - 12, 15, "#FFFFFF", a)
    u = url if len(url) < 70 else url[:67] + "..."
    text(c, u, x0 + 140, y0 + bar / 2 + 9, 21, "#3C4656", FT_SEMI, "l", a)
    vx0, vy0, vw, vh = x0, y0 + bar, w, h - bar
    content_w = max(l[2] for LL in lines for l in LL) + 70
    s = min(vw / content_w, vw / iw * 2.6) * zoom
    L = lines[focus]; fy = (L[0][1] + L[-1][1] + L[-1][3]) / 2
    ty = min(vy0, max(vy0 + vh - ih * s, vy0 + vh * 0.5 - fy * s)) if ih * s > vh else vy0 + (vh - ih * s) / 2
    c.save(); c.clipRect(skia.Rect(vx0, vy0, vx0 + vw, vy0 + vh)); c.translate(vx0, ty); c.scale(s, s)
    draw_img(c, img, 0, 0, iw, ih, a)
    for li, t0, dur in sweeps:
        Ls = lines[li]; n = len(Ls)
        for i, (lx0, ly, lx1, lh) in enumerate(Ls):
            k = seg(t, t0 + i * dur / n, t0 + (i + 1) * dur / n)
            if k <= 0: continue
            hp = paint("#FFD166", int(150 * a / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(lx0 - 8, ly - 10, lx0 - 8 + (lx1 - lx0 + 16) * ease_out(k), ly + lh + 10), hp)
    c.restore()

def mini_page(c, key, cx, cy, w, ang, a, line, hl_k):
    """a real document screenshot printed on a tilted sheet, highlight sweeping one line"""
    if w <= 1 or a <= 0: return
    img, (iw, ih), lines, url = DOCS[key]
    h = w * 1.3
    c.save(); c.translate(cx, cy); c.rotate(ang)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 6, "#FFFFFF", a, shadow=22)
    L = lines[line]; s = (w - 24) / iw
    fy = (L[0][1] + L[-1][1]) / 2; oy = max(-h / 2 + 12 - 0, min(-h / 2 + 12, -fy * s))
    oy = -h / 2 + 12 if ih * s < h - 24 else max(h / 2 - 12 - ih * s, min(-h / 2 + 12, -fy * s))
    c.save(); c.clipRect(skia.Rect(-w / 2 + 12, -h / 2 + 12, w / 2 - 12, h / 2 - 12)); c.translate(-w / 2 + 12, oy); c.scale(s, s)
    draw_img(c, img, 0, 0, iw, ih, a)
    for i, (lx0, ly, lx1, lh) in enumerate(L):
        k = seg(hl_k, i / len(L), (i + 1) / len(L))
        if k > 0:
            hp = paint("#FFD166", int(150 * a / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(lx0 - 8, ly - 10, lx0 - 8 + (lx1 - lx0 + 16) * ease_out(k), ly + lh + 10), hp)
    c.restore(); c.restore()

HORMUZ_PATH = [(50.3, 27.2), (51.8, 26.6), (53.3, 26.15), (54.8, 26.15), (55.9, 26.45), (56.45, 26.45), (56.75, 25.9), (57.4, 25.3), (58.6, 24.8)]
def hormuz_xy(cam, f):
    """point at fraction f along the shipping lane (Persian Gulf -> Strait -> Gulf of Oman), in screen coords"""
    pts = [to_screen(cam, *p) for p in HORMUZ_PATH]
    seglen = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; L = sum(seglen); d = clamp(f) * L
    for i, sl in enumerate(seglen):
        if d <= sl or i == len(seglen) - 1:
            k = d / sl if sl else 0; return lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)
        d -= sl

def bg(c, mapcam=None, fills=None, alpha=255):
    c.clear(hexc(PAL["ocean"]))
    if mapcam: draw_map(c, scene1.WM, mapcam, fills or {}, alpha)

def dim(c, a): c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(a)))

def date_chip(c, s, x, y, k, col=PAL["axis"]):
    if k <= 0: return
    kk = back(k); c.save(); c.translate(x, y); c.scale(kk, kk); pill(c, s, 0, 0, 38, col, a=int(255 * clamp(k * 1.5))); c.restore()

def title(c, s, x, y, size, k, col="#F1FAEE", a=255):
    if k <= 0: return
    kk = back(k); c.save(); c.translate(x, y); c.scale(kk, kk); text(c, s, 0, 0, size, col, FT_BLACK, "c", int(a * clamp(k * 1.5)), shadow=True); c.restore()

def camlerp(t, keys):
    cam = keys[0][2]
    for t0, t1, c0, c1 in keys:
        if t >= t0: cam = scene1.fly(c0, c1, ease_io(seg(t, t0, t1)))
    return cam

def swords(c, x, y, s, k, col="#F1FAEE"):
    if k <= 0: return
    kk = back(k)
    for sgn in (-1, 1):
        c.save(); c.translate(x, y); c.rotate(sgn * 45); c.scale(kk, kk)
        c.drawRect(skia.Rect(-s * 0.06, -s, s * 0.06, s * 0.55), paint(col)); c.drawRect(skia.Rect(-s * 0.28, s * 0.5, s * 0.28, s * 0.62), paint(col))
        c.drawRect(skia.Rect(-s * 0.07, s * 0.62, s * 0.07, s * 0.95), paint("#C9971E")); c.restore()

def xmark(c, x, y, s, k, col=PAL["axis"]):
    if k <= 0: return
    for i, (dx, dy) in enumerate(((1, 1), (1, -1))):
        kk = ease_out(seg(k, i * 0.3, 0.6 + i * 0.3))
        c.drawLine(x - s * dx, y - s * dy, x - s * dx + 2 * s * dx * kk, y - s * dy + 2 * s * dy * kk, paint(col, 255, stroke=s * 0.28, cap_round=True))

def tick(c, x, y, s, k, col="#5FD07A"):
    if k <= 0: return
    p = skia.Path(); p.moveTo(x - s, y); p.lineTo(x - s * 0.3, y + s * 0.7); p.lineTo(x + s, y - s * 0.8)
    pm = skia.PathMeasure(p, False); L = pm.getLength(); sp = skia.Path(); pm.getSegment(0, L * ease_out(k), sp, True)
    c.drawPath(sp, paint(col, 255, stroke=s * 0.3, cap_round=True))

# ======================================================================================= SHOTS
SHOTS = []      # (t0, t1, fn, trans)
SFX = []        # (name, t, gain_db)
def shot(t0, t1, trans="fade"):
    def deco(fn): SHOTS.append((t0, t1, fn, trans)); SFX.append(("whoosh_fast", t0, -19)); return fn
    return deco

# ---------------- S2a: Trump writes (u6) + quote (u7)
@shot(vin(6), vin(8))
def s2a(c, t):
    k_quote = seg(t, vin(7) - 0.1, vin(7) + 0.35)
    cam = camlerp(t, [(vin(6), vin(6) + 1.3, (116.4, 39.9, 9), (20, 38, 5.2))])
    bg(c, cam, {"CHN": PAL["CHN"], "USA": "#3C6FD8"})
    k = seg(t, vin(6) + 0.2, vin(6) + 1.3)
    if k > 0:
        a, b = S(cam, "beijing"), S(cam, "wash")
        mid = ((a[0] + b[0]) / 2, min(a[1], b[1]) - 260)
        route(c, [a, mid, b], ease_io(k), col=PAL["yel"])
        pin(c, *b, "WASHINGTON", seg(t, vin(6) + 1.0, vin(6) + 1.4), t=t)
    if k_quote > 0:
        dim(c, 170 * k_quote)
        hl = kw(7, "conspire")
        quote_card(c, 230, 300, 1460, ["Please give my warmest regards to", "Vladimir Putin, and Kim Jong Un,", "as you conspire against", "The United States of America."],
                   "- Donald Trump, Truth Social", k_quote, t, hl_line=[2, 3], hl_k=seg(t, hl, hl + 0.9))
        footnote(c, "Source: Trump's Truth Social post, 2 Sep 2025 (US time) · reported by NBC News, AP")

# ---------------- S2b: CRINK name (u8-u11)
@shot(vin(8), vin(12))
def s2b(c, t):
    names = [("CHN", "china"), ("RUS", "russia"), ("IRN", "iran"), ("PRK", "north korea")]
    fills = {}
    for code, w in names:
        kk = seg(t, kw(10, w), kw(10, w) + 0.3)
        if kk > 0: fills[code] = (CR[code], int(255 * kk))
    cam = (95, 52, 7.6)
    bg(c, cam, fills)
    # newspapers fan out (u8)
    kn = seg(t, vin(8), vin(8) + 0.6); kout = seg(t, vin(9) - 0.1, vin(9) + 0.3)
    if kn > 0 and kout < 1:
        dim(c, 140 * (1 - kout))
        for i in range(4):
            ang = lerp(0, (i - 1.5) * 12, ease_out(kn)); x = 960 + (i - 1.5) * 190 * ease_out(kn)
            c.save(); c.translate(x, 560 - 200 * kout); c.rotate(ang); a = int(255 * (1 - kout))
            rrect(c, -170, -220, 170, 220, 6, "#F4F1EA", a, shadow=16)
            img = CARDS[i]; iw, ih = img.width(), img.height()
            c.save(); c.clipRect(skia.Rect(-158, -208, 158, 208))
            draw_img(c, img, -158, -208, 158, -208 + 316 * ih / iw, a); c.restore(); c.restore()
    # CRINK letters (u9) + pills synced with names (u10) + axis lines (u11)
    kc = seg(t, vin(9), vin(9) + 0.5)
    if kc > 0:
        word = "CRINK"; tw = text_w(word, 220); xs = 960 - tw / 2
        for i, L_ in enumerate(word):
            ki = back(seg(t, vin(9) + i * 0.06, vin(9) + 0.35 + i * 0.06), 1.4)
            x = xs + text_w(word[:i], 220)
            if ki <= 0: continue
            y = 250 - (1 - ki) * 120
            text(c, L_, x + 6, y + 8, 220, "#000000", FT_BLACK, "l", 110); text(c, L_, x, y, 220, "#F1FAEE", FT_BLACK, "l")
    labels = [("CHINA", "CHN"), ("RUSSIA", "RUS"), ("IRAN", "IRN"), ("NORTH KOREA", "PRK")]
    x = 960 - sum(text_w(l, 40, FT_SEMI) + 70 for l, _ in labels) / 2
    for (lab, code), (_, w) in zip(labels, names):
        ww = text_w(lab, 40, FT_SEMI) + 40
        kk = back(seg(t, kw(10, w), kw(10, w) + 0.35))
        if kk > 0:
            c.save(); c.translate(x + ww / 2, 340); c.scale(kk, kk); pill(c, lab, 0, 0, 40, CR[code], fpath=FT_SEMI); c.restore()
        x += ww + 30
    ka = seg(t, vin(11), vin(11) + 0.8)
    if ka > 0:
        caps = {"CHN": PL["beijing"], "RUS": PL["moscow"], "IRN": PL["tehran"], "PRK": PL["pyong"]}
        P = {k: to_screen(cam, *v) for k, v in caps.items()}
        for i, (a_, b_) in enumerate((("RUS", "CHN"), ("CHN", "PRK"), ("RUS", "PRK"), ("RUS", "IRN"), ("IRN", "CHN"))):
            route(c, [P[a_], P[b_]], seg(ka, i * 0.12, 0.5 + i * 0.12), col=PAL["axis"], w=6, head=False)
        for v in P.values(): c.drawCircle(*v, 14, paint("#F1FAEE")); c.drawCircle(*v, 14, paint(PAL["axis"], stroke=5))
        g = seg(t, vin(11) + 0.6, vin(11) + 0.9); jitter = 8 * math.sin(t * 90) * (1 - g) if g < 1 else 0
        title(c, "EK NAYA “AXIS”?", 960 + jitter, 895, 96, g, PAL["yel"])
    SFX_MARK(vin(9), "pop", -14); SFX_MARK(vin(11) + 0.6, "glitch", -14)

_sfx_seen = set()
def SFX_MARK(t, name, g):
    key = (round(t, 2), name)
    if key not in _sfx_seen: _sfx_seen.add(key); SFX.append((name, t, g))

# ---------------- S2c: alliance or photo-op (u12) + India? (u13)
@shot(vin(12), 44.55)
def s2c(c, t):
    k13 = seg(t, vin(13), vin(13) + 0.5)
    if k13 < 1:
        bg(c)
        a = int(255 * (1 - k13))
        k1 = back(seg(t, vin(12) + 0.6, vin(12) + 1.0)); k2 = back(seg(t, kw(12, "photo"), kw(12, "photo") + 0.4))
        if k1 > 0:
            c.save(); c.translate(560, 480); c.scale(k1, k1)
            p = skia.Path(); p.moveTo(0, -170); p.lineTo(150, -110); p.cubicTo(150, 60, 80, 140, 0, 190); p.cubicTo(-80, 140, -150, 60, -150, -110); p.close()
            c.drawPath(p, paint("#2C5DAA", a)); c.drawPath(p, paint("#F1FAEE", a, stroke=8))
            for i, code in enumerate(("cn", "ru", "ir", "kp")): flag_circle(c, code, -60 + (i % 2) * 120, -40 + (i // 2) * 110, 40, a=a)
            text(c, "ALLIANCE?", 0, 300, 64, "#F1FAEE", FT_BLACK, "c", a); c.restore()
        if k2 > 0:
            c.save(); c.translate(1360, 480); c.scale(k2, k2)
            rrect(c, -170, -110, 170, 130, 26, "#C9D1DC", a); c.drawRect(skia.Rect(-60, -150, 40, -110), paint("#C9D1DC", a))
            c.drawCircle(0, 10, 80, paint("#0F1B2D", a)); c.drawCircle(0, 10, 54, paint("#2E4A6B", a))
            text(c, "PHOTO-OP?", 0, 300, 64, "#F1FAEE", FT_BLACK, "c", a); c.restore()
            fl = 1 - abs(t - kw(12, "photo") - 0.2) / 0.12
            if fl > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint("#FFFFFF", int(200 * fl)))
        if k1 > 0 and k2 > 0: title(c, "YA", 960, 500, 70, seg(t, kw(12, "ya sirf"), kw(12, "ya sirf") + 0.3), PAL["yel"])
    if k13 > 0:
        cam = camlerp(t, [(vin(13), vin(13) + 1.2, (95, 52, 7.6), (80, 32, 11.5))])
        c.save(); c.saveLayerAlpha(None, int(255 * k13))
        bg(c, cam, {**{k: (v, 200) for k, v in CR.items()}, "IND": (PAL["IND"], int(255 * seg(t, kw(13, "india"), kw(13, "india") + 0.4)))})
        x, y = S(cam, "delhi")
        ic_question(c, x, y - 140 - 15 * math.sin(t * 5), 170 * back(seg(t, kw(13, "india"), kw(13, "india") + 0.4)))
        c.restore(); c.restore()

# ---------------- host (H1/H2/H3) - drawn from rendered frames
HOST = {"H1": (44.55, 55.85), "H2": (262.35, 271.65), "H3": (512.5, 524.2)}
def host_frame(c, seg_key, t):
    f = int(round(t * 60))
    p = AB_ROOT + f"host/frames/{seg_key}/f{f:06d}.jpg"
    if not os.path.exists(p):
        fs = sorted(os.listdir(AB_ROOT + f"host/frames/{seg_key}"))
        p = AB_ROOT + f"host/frames/{seg_key}/" + (fs[-1] if f > int(fs[-1][1:7]) else fs[0])
    img = sk_image(Image.open(p)); draw_img(c, img, 0, 0, DW, DH)

def subscribe_card(c, lt):
    """skia port of brand/subscribe_anim.py (4.6 s)"""
    if lt < 0 or lt > 4.6: return
    cw, ch = 1120, 190; cx0 = (DW - cw) / 2; rest_y = DH - ch - 150
    enter = back(seg(lt, 0.0, 0.55)); leave = ease_io(seg(lt, 4.0, 4.5))
    y = DH + 40 + (rest_y - DH - 40) * enter + (DH + 40 - rest_y) * leave
    a = int(255 * min(1, seg(lt, 0, 0.2)) * (1 - leave))
    if a <= 0: return
    rrect(c, cx0, y, cx0 + cw, y + ch, 40, "#111827", a, shadow=22)
    draw_img(c, LOGO, cx0 + 26, y + 25, cx0 + 166, y + 165, a)
    text(c, "AMRIT BORI", cx0 + 190, y + 98, 54, "#F1FAEE", FT_BLACK, "l", a)
    text(c, "@AMRITBORII", cx0 + 192, y + 146, 28, "#9CA3AF", FT_SEMI, "l", a)
    clicked = lt >= 1.40; bx0, bw, bh = cx0 + 650, 300, 92; by0 = y + (ch - bh) / 2
    pop = 1 + 0.10 * math.sin(math.pi * seg(lt, 1.40, 1.62)); bcx, bcy = bx0 + bw / 2, by0 + bh / 2
    rrect(c, bcx - bw * pop / 2, bcy - bh * pop / 2, bcx + bw * pop / 2, bcy + bh * pop / 2, bh * pop / 2, "#3E424C" if clicked else "#E50914", a)
    text(c, "SUBSCRIBED ✓" if clicked else "SUBSCRIBE", bcx, bcy + 13, 34 if clicked else 40, "#F1FAEE", FT_BLACK, "c", a)
    rp = seg(lt, 1.40, 1.85)
    if 0 < rp < 1: c.drawCircle(bcx, bcy, 40 + 220 * rp, paint("#FFFFFF", int(200 * (1 - rp) * a / 255), stroke=6))
    belx, bely = cx0 + 1035, y + ch / 2; rung = lt >= 2.55
    ang = 22 * math.sin(seg(lt, 2.55, 3.6) * math.pi * 7) * (1 - seg(lt, 2.55, 3.6)) if rung else 0
    c.save(); c.translate(belx, bely - 30); c.rotate(ang); c.translate(-belx, -(bely - 30))
    bp = skia.Path(); w_ = 76
    bp.moveTo(belx - 0.42 * w_, bely + 0.28 * w_); bp.cubicTo(belx - 0.34 * w_, bely - 0.1 * w_, belx - 0.3 * w_, bely - 0.45 * w_, belx, bely - 0.45 * w_)
    bp.cubicTo(belx + 0.3 * w_, bely - 0.45 * w_, belx + 0.34 * w_, bely - 0.1 * w_, belx + 0.42 * w_, bely + 0.28 * w_); bp.close()
    c.drawPath(bp, paint("#FFD166" if rung else "#F1FAEE", a) if rung else paint("#F1FAEE", a, stroke=6))
    c.drawCircle(belx, bely + 0.4 * w_, 8, paint("#FFD166" if rung else "#F1FAEE", a)); c.restore()
    nk = back(seg(lt, 2.7, 3.1))
    if nk > 0: text(c, "Subscribe karo  •  Bell dabao!", DW / 2, y - 40, 44 * nk, "#FFD166", FT_BLACK, "c", a, shadow=True)
    if 0.55 < lt < 3.9:
        p0, p1, p2, p3 = (DW + 60, DH + 60), (bcx + 40, bcy + 10), (belx + 10, bely + 6), (DW + 80, DH + 80)
        if lt < 1.35: k = ease_io(seg(lt, 0.6, 1.3)); x, yy = lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k)
        elif lt < 2.0: x, yy = p1
        elif lt < 2.5: k = ease_io(seg(lt, 2.0, 2.5)); x, yy = lerp(p1[0], p2[0], k), lerp(p1[1], p2[1], k)
        elif lt < 3.2: x, yy = p2
        else: k = ease_io(seg(lt, 3.2, 3.85)); x, yy = lerp(p2[0], p3[0], k), lerp(p2[1], p3[1], k)
        kk = 54 * (0.85 if (1.36 <= lt <= 1.5 or 2.52 <= lt <= 2.66) else 1)
        pts = [(0, 0), (0, 1.0), (0.26, 0.76), (0.44, 1.14), (0.58, 1.07), (0.40, 0.70), (0.74, 0.70)]
        cp = skia.Path(); cp.moveTo(x, yy)
        for px, py in pts[1:]: cp.lineTo(x + px * kk, yy + py * kk)
        cp.close(); c.drawPath(cp, paint("#FFFFFF", a)); c.drawPath(cp, paint("#141414", a, stroke=2.5))

@shot(*HOST["H1"])
def h1(c, t):
    host_frame(c, "H1", t); subscribe_card(c, t - 51.25)
    SFX_MARK(51.25 + 1.40, "pop", -12); SFX_MARK(51.25 + 2.55, "ding", -14)

# ---------------- Chapter cards
CH_GAP = 1.4                     # seconds of silent chapter animation before the VO says "Chapter N"
GAPS = []                        # VO-time points where the video inserts a pause
GAPINFO = None                   # (gap_index, seconds_into_gap) while rendering inside a pause
def chapter(num, ttl, t0, t1):
    gi = len(GAPS); GAPS.append(t0)
    @shot(t0, t1, "cut")
    def _ch(c, t):
        extra = GAPINFO[1] if (GAPINFO and GAPINFO[0] == gi) else (CH_GAP if t >= t0 else 0)
        chapter_card(c, t + extra, t0, num, ttl)
    SFX.append(("boom", t0, -14)); SFX.append(("whoosh_long", t0, -12))
chapter(1, "NAAM KA KHEL", 55.85, vin(19))

# ---------------- S3: Halifax + CRINK doc (u19)
@shot(vin(19), vin(20))
def s3(c, t):
    cam = camlerp(t, [(vin(19), vin(19) + 1.4, (0, 30, 5.4), (-63.6, 44.6, 34))])
    bg(c, cam, {"CAN": "#3E5068"})
    x, y = S(cam, "halifax")
    pin(c, x, y, "HALIFAX, CANADA", seg(t, vin(19) + 1.0, vin(19) + 1.4), t=t)
    date_chip(c, "NOV 2023", 960, 150, seg(t, vin(19) + 0.3, vin(19) + 0.7))
    kd = ease_out(seg(t, kw(19, "halifax") - 0.3, kw(19, "halifax") + 0.2))
    if kd > 0:
        dim(c, 120 * kd)
        doc(c, "crink", 240, lerp(DH + 40, 300, kd), 1440, 500, t, 1, [(0, kw(19, "halifax"), 1.2), (1, kw(19, "van praagh") - 0.2, 1.2)])
        footnote(c, "Source: Wikipedia, 'CRINK' (CC BY-SA 4.0)")

# ---------------- S4: 2002 Axis of Evil (u20-u22)
@shot(vin(20), vin(23))
def s4(c, t):
    bg(c)
    # rewind slider 2023 -> 2002
    kr = ease_io(seg(t, vin(20) + 0.3, kw(20, "2002") + 0.3))
    if t < kw(20, "kyunki") + 1.2:
        yr = int(round(lerp(2023, 2002, kr)))
        c.drawLine(300, 560, 1620, 560, paint("#5B6E8C", 255, stroke=6, cap_round=True))
        for i, y_ in enumerate(range(2002, 2024, 3)):
            x = lerp(300, 1620, (y_ - 2002) / 21); c.drawLine(x, 545, x, 575, paint("#8A9BB0", 255, stroke=3)); text(c, str(y_), x, 620, 28, "#8A9BB0", FT_SEMI, "c")
        mx = lerp(1620, 300, kr)
        c.drawCircle(mx, 560, 20, paint(PAL["axis"])); text(c, str(yr), mx, 500, 72, "#F1FAEE", FT_BLACK, "c", shadow=True)
        title(c, "⏪ REWIND", 960, 300, 60, seg(t, vin(20), vin(20) + 0.4), PAL["yel"])
    kd = ease_out(seg(t, kw(20, "kyunki") + 0.6, kw(20, "kyunki") + 1.1)); kout = seg(t, kw(22, "axis") - 0.2, kw(22, "axis") + 0.2)
    if kd > 0 and kout < 1:
        doc(c, "axis_evil", 240, lerp(DH + 40, 330, kd), 1440, 420, t, 1, [(0, kw(20, "george"), 0.8), (1, kw(21, "iran"), 1.0), (2, kw(21, "kaha"), 0.8)], a=int(255 * (1 - kout)))
        footnote(c, "Source: Wikipedia, 'Axis of evil' (CC BY-SA 4.0)")
    if kout > 0:
        cam = (90, 36, 7.0)
        morph = seg(t, kw(22, "evil") + 0.5, vin(23))
        fills = {"IRN": ("#7A1020", 255), "IRQ": ("#7A1020", int(255 * (1 - morph))), "PRK": ("#7A1020", 255)}
        if morph > 0: fills.update({"CHN": (PAL["CHN"], int(255 * morph)), "RUS": (PAL["RUS"], int(255 * morph)), "IRN": PAL["IRN"], "PRK": PAL["PRK"]})
        c.save(); c.saveLayerAlpha(None, int(255 * kout)); bg(c, cam, fills)
        stamp(c, "AXIS OF EVIL · 2002" if morph < 0.5 else "CRINK · 2023", 960, 880, 72, PAL["axis"], seg(t, kw(22, "axis"), kw(22, "axis") + 0.18) if morph < 0.5 else seg(t, kw(22, "evil") + 0.75, kw(22, "evil") + 0.95))
        c.restore(); c.restore()
    SFX_MARK(kw(22, "axis"), "stamp", -10)

# ---------------- S5: toolkit board (u23-u27)
SLOTS = [("cn", "CHINA", PAL["CHN"], 24), ("ru", "RUSSIA", PAL["RUS"], 25), ("ir", "IRAN", PAL["IRN"], 26), ("kp", "NORTH KOREA", PAL["PRK"], 27)]
def toolkit(c, t, a=255, slide=0.0):
    for i, (fc, name, col, ui) in enumerate(SLOTS):
        ks = ease_out(seg(t, vin(23) + i * 0.12, vin(23) + 0.5 + i * 0.12))
        if ks <= 0: continue
        x0 = 90 + i * 440; y0 = 150 + (1 - ks) * 80 + slide
        act = seg(t, vin(ui), vin(ui) + 0.3) * (1 - seg(t, ue(ui) + 0.2, ue(ui) + 0.5)) if t < vin(28) else 0
        rrect(c, x0, y0, x0 + 400, y0 + 760, 26, "#16223A", a, shadow=20)
        c.drawRoundRect(skia.Rect(x0, y0, x0 + 400, y0 + 760), 26, 26, paint(col, a, stroke=3 + 5 * act))
        flag_circle(c, fc, x0 + 200, y0 + 90, 54, a=a)
        text(c, name, x0 + 200, y0 + 195, 40, "#F1FAEE", FT_BLACK, "c", a)
        items = {
            24: [("factory", "factory", "FACTORY"), ("paisa", "coins", "PAISA"), ("technology", "chip", "TECHNOLOGY")],
            25: [("nuclear", "warhead", "NUCLEAR #1"), ("tel", "barrel", "TEL-GAS"), ("veto", "un", "UN VETO")],
            26: [("drones", "drone", "DRONES"), ("tel", "barrel", "TEL"), ("hormuz", "hormuz", "HORMUZ")],
            27: [("artillery", "shell", "SHELLS"), ("missiles", "missile", "MISSILES"), ("sainik", "soldier", "SAINIK")]}[ui]
        for j, (w, ic, lab) in enumerate(items):
            ki = back(seg(t, kw(ui, w), kw(ui, w) + 0.35), 1.5)
            if ki <= 0: continue
            cx, cy = x0 + 200, y0 + 300 + j * 165
            c.save(); c.translate(cx - 90, cy); c.scale(ki, ki)
            if ic == "factory": ic_factory(c, 0, 0, 80, t, a=a)
            elif ic == "coins": ic_coins(c, 0, 0, 80, a=a)
            elif ic == "chip": ic_chip(c, 0, 0, 80, t, a=a)
            elif ic == "warhead": ic_warhead(c, 0, 0, 80, a=a)
            elif ic == "barrel": ic_barrel(c, -18, 0, 70, a=a); ic_flame(c, 30, 0, 50, t, a=a) if ui == 25 else None
            elif ic == "un": ic_un_table(c, 0, 0, 55, hl=1, a=a)
            elif ic == "drone": ic_drone(c, 0, 0, 80, -20 + 8 * math.sin(t * 3), a=a)
            elif ic == "hormuz":
                c.drawRoundRect(skia.Rect(-45, -40, 45, 40), 8, 8, paint("#2B3A4F", a)); c.drawRect(skia.Rect(-45, -6, 45, 6), paint("#0F1B2D", a))
                ic_ship(c, -20 + ((t * 30) % 50), -2, 26, a=a)
            elif ic == "shell":
                for q in range(3): ic_shell(c, -24 + q * 24, 0, 60, a=a)
            elif ic == "missile": ic_missile(c, 0, 0, 80, -35, t=t, a=a)
            elif ic == "soldier":
                for q in range(3): ic_soldier(c, -30 + q * 30, 0, 55, t + q * 0.3, a=a)
            c.restore()
            text(c, lab, cx + 10, cy + 10, 26, "#F1FAEE", FT_BLACK, "l", int(a * clamp(ki)))
            SFX_MARK(kw(ui, w), "pop", -18)

@shot(vin(23), vin(28))
def s5(c, t):
    bg(c); title(c, "KAUN KYA LAATA HAI?", 960, 95, 56, seg(t, vin(23), vin(23) + 0.4), PAL["yel"])
    toolkit(c, t)

# ---------------- S6: dangerous combo (u28) -> who joined? (u29) -> Ukraine (u30-31)
@shot(vin(28), 104.7)
def s6(c, t):
    k29 = seg(t, vin(29) - 0.1, vin(29) + 0.4)
    if k29 < 1:
        bg(c); a = int(255 * (1 - k29))
        sc = lerp(1, 0.8, ease_io(seg(t, vin(28), vin(28) + 0.6)))
        c.save(); c.translate(960, 540); c.scale(sc, sc); c.translate(-960, -540)
        rrect(c, 60, 110, 1860, 950, 10, "#EDE6D6", a, shadow=30); toolkit(c, t, a=a); c.restore()
        kt = ease_out(seg(t, kw(28, "khatarnak") - 0.1, kw(28, "khatarnak") + 0.5))
        if kt > 0:
            c.save(); c.translate(960, 540); c.rotate(-8)
            for row in (-60, 60):
                c.drawRect(skia.Rect(-1100 * kt, row - 40, 1100 * kt, row + 40), paint("#FFD166", a))
                for i in range(-12, 13):
                    p = skia.Path(); x = i * 90; p.moveTo(x, row - 40); p.lineTo(x + 40, row - 40); p.lineTo(x - 10, row + 40); p.lineTo(x - 50, row + 40); p.close()
                    if abs(x) < 1100 * kt: c.drawPath(p, paint("#111111", a))
            c.restore(); title(c, "KHATARNAK COMBINATION", 960, 560, 70, seg(t, kw(28, "combination"), kw(28, "combination") + 0.3), "#E63946", a)
    if k29 > 0:
        k30 = seg(t, vin(30), vin(30) + 1.4)
        cam = camlerp(t, [(vin(30), vin(31) + 0.3, (90, 42, 6.6), (32, 49, 30))])
        c.save(); c.saveLayerAlpha(None, int(255 * k29))
        bg(c, cam, {**CR, "UKR": ("#FFD166", int(255 * seg(t, kw(31, "ukraine") - 0.1, kw(31, "ukraine") + 0.3)))})
        P = {k: S(cam, v) for k, v in (("CHN", "beijing"), ("RUS", "moscow"), ("IRN", "tehran"), ("PRK", "pyong"))}
        cx, cy = to_screen(cam, 80, 42)
        if k30 < 0.3:
            for k_, v in P.items(): ic_chain(c, v[0], v[1], cx, cy, seg(t, vin(29), vin(29) + 0.8), a=255)
            ic_question(c, cx, cy - 20, 200 * back(seg(t, kw(29, "joda"), kw(29, "joda") + 0.4)))
        ku = seg(t, kw(31, "ukraine") - 0.1, kw(31, "ukraine") + 0.4)
        if ku > 0:
            x, y = S(cam, "ukraine")
            rp = (t * 1.2) % 1; c.drawCircle(x, y, 40 + 200 * rp, paint(PAL["axis"], int(200 * (1 - rp)), stroke=8))
            title(c, "UKRAINE", x, y - 120, 80, ku); date_chip(c, "24 FEB 2022", x, y + 110, ku)
            swords(c, x, y + 30, 62, ku, "#1B2433")
        c.restore(); c.restore()
    SFX_MARK(kw(31, "ukraine"), "boom", -10)

chapter(2, "WOH JUNG JISNE INHE JODA", 104.7, vin(34))

# ---------------- S7: Shahed (u34) + deal/Alabuga (u35)
@shot(vin(34), vin(36))
def s7(c, t):
    cam = camlerp(t, [(vin(34), vin(34) + 1.0, (45, 45, 9), (49, 46, 16))])
    bg(c, cam, {"IRN": PAL["IRN"], "RUS": PAL["RUS"]})
    date_chip(c, "AUGUST 2022", 960, 120, seg(t, vin(34), vin(34) + 0.4))
    k = seg(t, kw(34, "shahed") - 0.3, kw(34, "russia"))
    a_, m_, b_ = S(cam, "tehran"), S(cam, "caspian"), S(cam, "moscow")
    r = route(c, [a_, m_, b_], ease_io(k), col=PAL["yel"])
    if r and k > 0.05:
        pm, L = r
        for i in range(4):
            f = (t * 0.35 + i / 4) % 1 * ease_io(k)
            x, y, ang = along(pm, L, f); ic_drone(c, x, y, 46, ang)
    pin(c, *a_, "IRAN", seg(t, vin(34), vin(34) + 0.3), col=PAL["IRN"], t=t, side="l")
    pin(c, *b_, "RUSSIA", seg(t, kw(34, "russia") - 0.2, kw(34, "russia") + 0.2), col="#7FA6E8", t=t)
    text(c, "SHAHED-136 DRONES", 960, 905, 44, "#F1FAEE", FT_BLACK, "c", int(255 * seg(t, kw(34, "shahed"), kw(34, "shahed") + 0.3)), shadow=True)
    # deal + Alabuga
    kd = seg(t, vin(35), vin(35) + 0.4)
    if kd > 0:
        al = S(cam, "alabuga")
        kdoc = ease_out(seg(t, kw(35, "alabuga") - 0.4, kw(35, "alabuga")))
        if kdoc < 1:
            dim(c, 150 * kd * (1 - kdoc))
            mini_page(c, "shahed", 700, 560, 440 * back(kd), -5, int(255 * (1 - kdoc)), 0, seg(t, kw(35, "deal") - 0.2, kw(35, "deal") + 0.8))
            pill(c, "DEAL", 700, 560 - 300 * back(kd), 34, PAL["axis"], a=int(255 * clamp(kd) * (1 - kdoc)))
            v = lerp(0, 1.75, ease_out(seg(t, kw(35, "1.75") - 0.4, kw(35, "1.75") + 0.6)))
            stat_card(c, 1010, 380, 620, 360, f"${v:.2f} bn", "drone production deal", seg(t, kw(35, "reportedly") - 0.2, kw(35, "reportedly") + 0.2) * (1 - kdoc), tag="REPORTEDLY")
        if kdoc > 0:
            pin(c, *al, "ALABUGA, TATARSTAN", kdoc, t=t)
            ic_factory(c, al[0] - 40, al[1] + 140, 120 * kdoc, t)
            for i in range(3):
                f = (t * 0.6 + i / 3) % 1; ic_drone(c, al[0] + 30 + f * 200, al[1] + 160, 34 * kdoc, 0)
            kq = ease_out(seg(t, kw(35, "alabuga") + 0.4, kw(35, "alabuga") + 0.8))
            if kq > 0:
                doc(c, "shahed", 160, lerp(DH + 20, 540, kq), 1100, 400, t, 1, [(0, kw(35, "alabuga") + 0.6, 0.9), (1, kw(35, "alabuga") + 1.3, 1.0)])
                footnote(c, "Sources: CSIS; Wikipedia, 'HESA Shahed 136' (CC BY-SA 4.0) · deal value as reported")

# ---------------- S8: NK warehouse (u36) + shells (u37) + doc (u38)
@shot(vin(36), vin(39))
def s8(c, t):
    cam = camlerp(t, [(vin(36), vin(36) + 1.0, (127, 40, 22), (110, 50, 7.5))])
    bg(c, cam, {"PRK": PAL["PRK"], "RUS": PAL["RUS"]})
    kw_ = back(seg(t, vin(36), vin(36) + 0.5))
    x, y = S(cam, "pyong")
    if t < vin(37) + 0.6:
        c.save(); c.translate(960, 560); c.scale(kw_ * (1 - seg(t, vin(37), vin(37) + 0.6)), kw_ * (1 - seg(t, vin(37), vin(37) + 0.6)))
        ic_warehouse(c, 0, 0, 380, ease_out(seg(t, kw(36, "godown"), kw(36, "godown") + 0.8))); c.restore()
        title(c, "NORTH KOREA KE GODOWN", 960, 210, 56, kw_, PAL["yel"])
    k37 = seg(t, vin(37), vin(37) + 2.5)
    if k37 > 0:
        a_ = S(cam, "rason"); b_ = S(cam, "moscow"); m_ = ((a_[0] + b_[0]) / 2, min(a_[1], b_[1]) - 150)
        r = route(c, [a_, m_, b_], ease_io(k37), col=PAL["yel"])
        if r:
            pm, L = r
            for i in range(3):
                f = ((t * 0.25 + i / 3) % 1) * ease_io(k37); xx, yy, ang = along(pm, L, f); ic_train(c, xx, yy, 40)
        v = ease_out(seg(t, kw(37, "40"), kw(37, "artillery") + 0.6))
        stat_card(c, 610, 610, 700, 330, f"{int(40 * v)}-{int(60 * v)} LAKH", "artillery shells (Sep 2023 - Apr 2025)", seg(t, kw(37, "40") - 0.3, kw(37, "40")) * (1 - seg(t, vin(38) + 0.2, vin(38) + 0.6)),
                  tag="ESTIMATE", sub="Source: Open Source Centre via Reuters")
    kd = ease_out(seg(t, vin(38) + 0.1, vin(38) + 0.6))
    if kd > 0:
        dim(c, 130 * kd)
        doc(c, "nk_shells", 200, lerp(DH + 20, 190, kd), 1520, 560, t, 1, [(0, kw(38, "reports") , 1.0), (1, kw(38, "148") - 0.1, 1.1)])
        for i in range(12):
            ki = seg(t, kw(38, "148") + i * 0.06, kw(38, "148") + 0.3 + i * 0.06)
            if ki > 0: ic_missile(c, 260 + i * 120, 880 - 30 * math.sin(i), 70 * ki, -40, t=t)
        text(c, "148 MISSILES", 1600, 960, 50, PAL["yel"], FT_BLACK, "c", int(255 * seg(t, kw(38, "148"), kw(38, "148") + 0.3)), shadow=True)
        footnote(c, "Source: Wikipedia, 'North Korean involvement in the Russian invasion of Ukraine' (CC BY-SA 4.0)")
    SFX_MARK(kw(36, "godown"), "drag", -14)

# ---------------- S9: Kursk confirmed (u39)
@shot(vin(39), vin(40))
def s9(c, t):
    cam = camlerp(t, [(vin(39), vin(39) + 1.2, (90, 48, 6.5), (75, 50, 9.5))])
    bg(c, cam, {"PRK": PAL["PRK"], "RUS": PAL["RUS"], "UKR": "#5B6E8C"})
    date_chip(c, "APRIL 2025", 960, 120, seg(t, vin(39), vin(39) + 0.4))
    a_ = S(cam, "pyong"); b_ = S(cam, "kursk"); m_ = ((a_[0] + b_[0]) / 2, min(a_[1], b_[1]) - 200)
    k = seg(t, vin(39) + 0.4, kw(39, "kursk") + 0.4)
    r = route(c, [a_, m_, b_], ease_io(k), col="#F08AA0")
    if r and k > 0.1:
        pm, L = r
        for i in range(5):
            f = ((t * 0.3 + i / 5) % 1) * ease_io(k); xx, yy, _ = along(pm, L, f); ic_soldier(c, xx, yy, 40, t + i)
    kk = seg(t, kw(39, "kursk") - 0.1, kw(39, "kursk") + 0.3)
    if kk > 0:
        x, y = b_
        c.drawCircle(x, y, 60 * kk, paint(PAL["axis"], 90)); pin(c, x, y, "KURSK", kk, t=t, side="l")
    stamp(c, "CONFIRMED", 1350, 820, 84, PAL["axis"], seg(t, kw(39, "maana") - 0.1, kw(39, "maana") + 0.1))
    footnote(c, "Source: NPR / KCNA statement, 28 Apr 2025")
    SFX_MARK(kw(39, "maana"), "stamp", -10)

# ---------------- S10: China? (u40-u43)
@shot(vin(40), vin(44))
def s10(c, t):
    bg(c)
    k40 = 1 - seg(t, vin(41) - 0.05, vin(41) + 0.3)
    if k40 > 0:
        kk = back(seg(t, vin(40), vin(40) + 0.4))
        flag_circle(c, "cn", 960, 470, 170, k=kk, a=int(255 * k40)); ic_question(c, 1230, 420, 220 * kk, a=int(255 * k40))
    k41 = seg(t, vin(41), vin(41) + 0.4) * (1 - seg(t, vin(42) - 0.1, vin(42) + 0.3))
    if k41 > 0:
        a = int(255 * k41)
        flag_circle(c, "cn", 420, 520, 140, a=a)
        rrect(c, 640, 320, 1720, 720, 40, "#F4F1EA", a, shadow=24)
        p = skia.Path(); p.moveTo(660, 560); p.lineTo(600, 600); p.lineTo(680, 610); p.close(); c.drawPath(p, paint("#F4F1EA", a))
        text(c, "BEIJING KA DAAVA:", 700, 420, 40, PAL["axis"], FT_BLACK, "l", a)
        text(c, "Russia ko hathiyar", 700, 520, 64, "#0F1B2D", FT_BLACK, "l", a)
        text(c, "nahi dete.", 700, 610, 64, "#0F1B2D", FT_BLACK, "l", a)
        text(c, "(official position, paraphrased)", 700, 680, 26, "#5B6472", FT_SEMI, "l", a)
    k42 = seg(t, vin(42), vin(42) + 0.4) * (1 - seg(t, vin(43) + 1.5, vin(43) + 1.9))
    if k42 > 0:
        a = int(255 * k42)
        pill(c, "US INTELLIGENCE", 960, 140, 40, "#3C6FD8", a=a)
        v = ease_out(seg(t, kw(42, "70") - 0.2, kw(42, "70") + 0.8))
        cx, cy, R = 620, 560, 230
        c.drawCircle(cx, cy, R, paint("#22304A", a))
        arc = skia.Path(); arc.moveTo(cx, cy); arc.arcTo(skia.Rect(cx - R, cy - R, cx + R, cy + R), -90, 360 * 0.7 * v, False); arc.close()
        c.drawPath(arc, paint(PAL["CHN"], a)); c.drawCircle(cx, cy, R * 0.55, paint(PAL["ocean"], a))
        text(c, f"{int(70 * v)}%", cx, cy + 30, 100, "#F1FAEE", FT_BLACK, "c", a)
        text(c, "Russia ke machine tool imports", 1300, 470, 44, "#F1FAEE", FT_BLACK, "c", a)
        text(c, "China se aaye", 1300, 540, 60, PAL["yel"], FT_BLACK, "c", a)
        text(c, "(Oct-Dec 2023)", 1300, 610, 34, PAL["muted"], FT_SEMI, "c", a)
        pill(c, "LAGBHAG", 1300, 680, 26, PAL["yel"], fg="#0F1B2D", a=a, shadow=0)
        footnote(c, "Source: US intelligence finding, reported by AP (Apr 2024)")
    k43 = seg(t, vin(43) + 1.5, vin(43) + 1.9)
    if k43 > 0:
        a = int(255 * k43)
        cam = (85, 46, 7.4)
        c.save(); c.saveLayerAlpha(None, a)
        bg(c, cam, {"CHN": PAL["CHN"], "RUS": PAL["RUS"]})
        bj, mo = S(cam, "beijing"), S(cam, "moscow")
        # CNC machine at China
        mx, my = bj[0] + 20, bj[1] + 110
        rrect(c, mx - 90, my - 70, mx + 90, my + 60, 14, "#3E5068", shadow=14)
        c.drawRect(skia.Rect(mx - 70, my - 55, mx + 70, my - 5), paint("#22304A")); c.drawCircle(mx, my - 30, 18 + 3 * math.sin(t * 10), paint("#4FC3F7"))
        c.drawRect(skia.Rect(mx - 60, my + 10, mx + 60, my + 22), paint("#8A9BB0"))
        pill(c, "CHINA: CNC MACHINE TOOLS", mx, my + 110, 28, PAL["CHN"])
        # shipment route China -> Russia
        kr = seg(t, vin(43) + 1.8, vin(43) + 3.2)
        mid = ((bj[0] + mo[0]) / 2, min(bj[1], mo[1]) - 120)
        r = route(c, [bj, mid, mo], ease_io(kr), col=PAL["yel"], w=7)
        if r and kr > 0.05:
            pm, L = r
            for i in range(4):
                f = ((t * 0.28 + i / 4) % 1) * ease_io(kr); x, y, ang = along(pm, L, f)
                c.save(); c.translate(x, y); c.rotate(ang)
                rrect(c, -26, -18, 26, 18, 4, "#C9971E"); c.drawLine(-26, -18, 26, 18, paint("#8A6512", 255, stroke=3)); c.drawLine(-26, 18, 26, -18, paint("#8A6512", 255, stroke=3))
                c.restore()
        # Russian factories produce tanks + missiles
        kf = seg(t, kw(43, "tank") - 0.3, kw(43, "tank") + 0.2)
        if kf > 0:
            fx, fy = mo[0] - 60, mo[1] + 150
            ic_factory(c, fx, fy, 130 * back(kf), t)
            for i in range(4):
                f = (t * 0.3 + i / 4) % 1; x = fx + 80 + f * 360; y = fy + 70
                if i % 2: ic_missile(c, x, y, 64 * kf, 0, flame=False)
                else:
                    rrect(c, x - 40, y - 14, x + 40, y + 20, 8, "#4B5D3A"); c.drawRect(skia.Rect(x - 6, y - 30, x + 54, y - 20), paint("#4B5D3A"))
            pill(c, "RUSSIA: TANK + MISSILE FACTORIES", fx + 160, fy - 110, 28, PAL["RUS"], a=int(255 * clamp(kf * 1.5)))
        footnote(c, "Source: US intelligence finding, reported by AP (Apr 2024) · illustrative flow")
        c.restore(); c.restore()

# ---------------- S11: battlefield friendship (u44) + paper? (u45)
@shot(vin(44), 161.72)
def s11(c, t):
    k45 = seg(t, vin(45), vin(45) + 0.4)
    cam = (55, 47, 9)
    bg(c, cam, {**CR, "UKR": "#FFD166"})
    if k45 < 1:
        u = S(cam, "ukraine")
        for code, key in (("CHN", "beijing"), ("RUS", "moscow"), ("IRN", "tehran"), ("PRK", "pyong")):
            route(c, [S(cam, key), u], seg(t, vin(44), vin(44) + 0.9), col=CR[code], w=7)
        title(c, "JUNG MEIN DOSTI ✓", 960, 180, 64, seg(t, kw(44, "dosti"), kw(44, "dosti") + 0.3), "#5FD07A", int(255 * (1 - k45)))
    if k45 > 0:
        dim(c, 170 * k45)
        c.save(); c.translate(960, 480); c.rotate(lerp(-12, -3, ease_out(k45))); c.scale(back(k45) * 0.82, back(k45) * 0.82)
        rrect(c, -300, -380, 300, 380, 8, "#F4F1EA", shadow=26)
        bp = paint("#2B3440", 255); bp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6.5))
        f_ = font(FT_BLACK, 40); c.drawString("TREATY", -230, -290, f_, bp)
        f2 = font(FT_SEMI, 24)
        lines_ = ["Article 1. The Parties shall strengthen", "friendship and cooperation in all areas.", "Article 2. In case of an armed attack,",
                  "the Parties shall consult without delay", "on practical measures of assistance.", "Article 3. Neither Party shall join any", "alliance directed against the other.",
                  "Article 4. Military and other assistance", "shall be provided with all means...", "Signed in the year ..."]
        for i, ln in enumerate(lines_): c.drawString(ln, -240, -220 + i * 52, f2, bp)
        c.restore(); ic_question(c, 960, 540, 300 * back(seg(t, kw(45, "likha"), kw(45, "likha") + 0.3)), col=PAL["axis"])
        title(c, "KAAGAZ PAR?", 960, 895, 60, k45, PAL["yel"])

chapter(3, "KAAGAZ KE RISHTEY", 161.72, vin(48))

# ---------------- S12: treaty network (u48-u73) with document inserts
NODES = {"RUS": (960, 230), "CHN": (1120, 650), "PRK": (1580, 400), "IRN": (500, 600)}
NFC = {"RUS": "ru", "CHN": "cn", "PRK": "kp", "IRN": "ir"}
EDGES = [  # a, b, solid?, label, unit start, unit end(highlight), doc
    ("CHN", "PRK", True, "1961 · DEFENCE TREATY", 50, 54, "sino_nk"),
    ("RUS", "PRK", True, "2024 · ARTICLE 4", 56, 60, "nk_treaty"),
    ("RUS", "CHN", False, "2022 · 'NO LIMITS' STATEMENT", 62, 63, "no_limits"),
    ("CHN", "IRN", False, "2021 · 25-YEAR DEAL", 64, 67, "iran_china"),
    ("RUS", "IRN", False, "2025 · NO DEFENCE CLAUSE", 68, 70, "iran_russia"),
]
DOC_SWEEPS = {
    "sino_nk": lambda: [(0, kw(51, "1961"), 0.9), (1, kw(53, "ikloti"), 1.2)],
    "nk_treaty": lambda: [(0, kw(58, "article"), 0.4), (1, kw(58, "har mumkin"), 1.4)],
    "no_limits": lambda: [(0, kw(62, "no limits"), 0.5), (1, kw(62, "no limits") + 0.5, 0.6)],
    "iran_china": lambda: [(0, kw(64, "march"), 1.2), (1, kw(66, "public"), 1.4)],
    "iran_russia": lambda: [(0, kw(68, "january"), 1.6)],
}
DOC_WIN = {"sino_nk": (52, 54), "nk_treaty": (58, 58), "no_limits": (62, 62), "iran_china": (64, 66), "iran_russia": (68, 68)}
def edge_k(e, t): return seg(t, vin(e[4]), vin(e[4]) + 0.8)

@shot(vin(48), 262.35)
def s12(c, t):
    bg(c)
    # pick zoom target: active edge
    act = None
    for e in EDGES:
        if vin(e[4]) - 0.2 <= t < vin(e[5]) + (ue(e[5]) - us(e[5])) + 0.3: act = e
    # document insert window
    dk = 0; dkey = None
    for e in EDGES:
        a_, b_ = DOC_WIN[e[6]]
        k = seg(t, vin(a_), vin(a_) + 0.45) * (1 - seg(t, ue(b_) + 0.1, ue(b_) + 0.5))
        if k > dk: dk, dkey = k, e[6]
    shift = -560 * ease_io(dk); scale = lerp(1.0, 0.62, ease_io(dk))
    c.save(); c.translate(960 + shift, 540); c.scale(scale, scale); c.translate(-960, -540)
    k48 = seg(t, vin(48), vin(48) + 0.6)
    # legend
    if t > vin(48) + 0.5:
        al = int(255 * seg(t, vin(48) + 0.5, vin(48) + 0.9))
        c.drawLine(140, 920, 260, 920, paint(PAL["yel"], al, stroke=8)); text(c, "PAKKA DEFENCE VAADA", 280, 932, 30, "#F1FAEE", FT_SEMI, "l", al)
        dp = paint("#8A9BB0", al, stroke=6); dp.setPathEffect(skia.DashPathEffect.Make([16, 12], 0)); c.drawLine(760, 920, 880, 920, dp)
        text(c, "SIRF PARTNERSHIP / STATEMENT", 900, 932, 30, "#F1FAEE", FT_SEMI, "l", al)
    crack = seg(t, vin(72), ue(73))
    for e in EDGES:
        k = edge_k(e, t)
        if k <= 0: continue
        A_, B_ = NODES[e[0]], NODES[e[1]]
        hot = act is e
        col = PAL["yel"] if e[2] else "#8A9BB0"
        if e[2]:
            route(c, [A_, B_], ease_io(k), col=col, w=12 if hot else 9, dash=False, head=False)
        else:
            # dashed "thread" that frays with crack
            if crack > 0:
                mx, my = (A_[0] + B_[0]) / 2, (A_[1] + B_[1]) / 2; gap = 60 * crack
                ux, uy = (B_[0] - A_[0]), (B_[1] - A_[1]); L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
                route(c, [A_, (mx - ux * gap, my - uy * gap + 30 * crack)], 1, col="#E63946" if crack > 0.3 else col, w=6, head=False)
                route(c, [(mx + ux * gap, my + uy * gap + 30 * crack), B_], 1, col="#E63946" if crack > 0.3 else col, w=6, head=False)
            else:
                route(c, [A_, B_], ease_io(k), col=col, w=9 if hot else 6, dash=True, head=False)
        kl = back(seg(t, vin(e[4]) + 0.5, vin(e[4]) + 0.9))
        if kl > 0:
            mx, my = (A_[0] + B_[0]) / 2, (A_[1] + B_[1]) / 2
            c.save(); c.translate(mx, my); c.scale(kl * (1.12 if hot else 1), kl * (1.12 if hot else 1))
            pill(c, e[3], 0, 0, 26, PAL["yel"] if e[2] else "#3E5068", fg="#0F1B2D" if e[2] else "#F1FAEE"); c.restore()
    for code, (x, y) in NODES.items():
        kk = back(seg(t, vin(48) + 0.1 * list(NODES).index(code), vin(48) + 0.5 + 0.1 * list(NODES).index(code)))
        glow_ = act is not None and code in act[:2]
        if glow_: c.drawCircle(x, y, 120, paint(PAL["yel"], 60))
        flag_circle(c, NFC[code], x, y, 80, k=kk)
    # "kursk me sainik" badge (u60), "kabhi use nahi" (u54)
    stamp(c, "KABHI USE NAHI HUI", 1380, 760, 40, "#8A9BB0", seg(t, kw(54, "kabhi"), kw(54, "kabhi") + 0.18) * (1 - seg(t, vin(55), vin(55) + 0.3)), ang=-6)
    stamp(c, "USE HUI: KURSK", 1250, 140, 44, PAL["axis"], seg(t, kw(60, "kursk"), kw(60, "kursk") + 0.18) * (1 - seg(t, vin(61), vin(61) + 0.3)), ang=-6)
    stamp(c, "ALLIANCE TREATY NAHI", 1100, 760, 40, "#8A9BB0", seg(t, kw(63, "alliance"), kw(63, "alliance") + 0.18) * (1 - seg(t, vin(64), vin(64) + 0.3)), ang=-6)
    stamp(c, "NO DEFENCE CLAUSE", 760, 820, 44, PAL["axis"], seg(t, kw(69, "mutual"), kw(69, "mutual") + 0.18) * (1 - seg(t, vin(71), vin(71) + 0.3)), ang=-6)
    c.restore()
    # counter "sirf do" (u48)
    k2 = seg(t, kw(48, "sirf do"), kw(48, "sirf do") + 0.4) * (1 - seg(t, vin(49), vin(49) + 0.3))
    if k2 > 0: stat_card(c, 1380, 400, 420, 300, "SIRF 2", "pakke military vaade", k2)
    if dkey:
        doc(c, dkey, 860, lerp(DH + 20, 200, ease_out(dk)), 1020, 560, t, len(DOCS[dkey][2]) - 1, DOC_SWEEPS[dkey](), zoom=1.0)
        footnote(c, f"Source: Wikipedia (CC BY-SA 4.0)")
    if dkey == "iran_russia" or (vin(70) <= t < vin(71)):
        kq = seg(t, vin(70), vin(70) + 0.4) * (1 - seg(t, vin(71) - 0.1, vin(71) + 0.2))
        if kq > 0:
            quote_card(c, 980, 300, 900, ["Yeh mutual defence", "pact nahi hai."], "- Andrei Rudenko, Russian Dy. FM (Apr 2025)", kq, t, hl_line=[0, 1], hl_k=seg(t, kw(70, "mutual"), kw(70, "mutual") + 0.8))
            footnote(c, "Source: Kyiv Post / Duma ratification remarks, Apr 2025 (paraphrased in Hindi)")
    # u71 NATO comparison
    kn = seg(t, vin(71), vin(71) + 0.4) * (1 - seg(t, vin(72) - 0.1, vin(72) + 0.2))
    if kn > 0:
        dim(c, 180 * kn); a = int(255 * kn)
        rrect(c, 360, 260, 1560, 820, 30, "#16223A", a, shadow=24)
        text(c, "NATO JAISA?", 960, 360, 70, PAL["yel"], FT_BLACK, "c", a)
        for i, s_ in enumerate(("JOINT COMMAND", "CHAARON KI EK TREATY")):
            text(c, s_, 760, 500 + i * 130, 52, "#F1FAEE", FT_BLACK, "l", a)
            xmark(c, 640, 485 + i * 130, 40, seg(t, kw(71, "joint") + i * 1.2, kw(71, "joint") + 0.4 + i * 1.2))
    if t >= vin(72):
        title(c, "JAAL: KUCH DHAAGE MAZBOOT, KUCH KACHCHE", 960, 120, 48, seg(t, vin(72), vin(72) + 0.4), PAL["yel"])
    if t >= vin(73):
        date_chip(c, "2026", 960, 880, seg(t, kw(73, "2026") - 0.1, kw(73, "2026") + 0.3))
    SFX_MARK(kw(54, "kabhi"), "stamp", -14); SFX_MARK(kw(60, "kursk"), "stamp", -12); SFX_MARK(kw(69, "mutual"), "stamp", -12); SFX_MARK(vin(72) + 0.5, "glitch", -16)

@shot(*HOST["H2"])
def h2(c, t): host_frame(c, "H2", t)

chapter(4, "2026: ASLI IMTIHAAN", 271.55, vin(79))

# ---------------- S13: Iran war (u79-u82)
@shot(vin(79), vin(83))
def s13(c, t):
    cam = camlerp(t, [(vin(79), vin(80) + 0.5, (45, 32, 12), (50, 30, 26)), (vin(82), vin(82) + 1.2, (50, 30, 26), (56.3, 26.4, 120))])
    bg(c, cam, {"IRN": PAL["IRN"], "ISR": "#3C6FD8", "USA": "#3C6FD8"})
    date_chip(c, "28 FEB 2026", 960, 120, seg(t, vin(79), vin(79) + 0.4) * (1 - seg(t, vin(82), vin(82) + 0.3)))
    ir = S(cam, "tehran"); isr = S(cam, "israel")
    k80 = seg(t, vin(80), vin(80) + 1.0)
    if k80 > 0 and t < vin(82):
        flag_circle(c, "us", 230, 300, 60, k=back(seg(t, vin(80), vin(80) + 0.3))); flag_circle(c, "il", *isr, 48, k=back(seg(t, vin(80) + 0.2, vin(80) + 0.5)))
        for i, src in enumerate(((230, 300), isr)):
            route(c, [src, ((src[0] + ir[0]) / 2, min(src[1], ir[1]) - 140), ir], ease_io(seg(k80, i * 0.2, 0.8 + i * 0.2)), col="#7FA6E8", w=6)
        for i in range(5):
            kb = seg(t, vin(80) + 0.9 + i * 0.12, vin(80) + 1.3 + i * 0.12)
            if kb > 0:
                x, y = ir[0] + (i - 2) * 50, ir[1] + ((i * 37) % 60 - 30)
                c.drawCircle(x, y, 50 * kb, paint("#FF9F1C", int(220 * (1 - kb)))); c.drawCircle(x, y, 22 * kb, paint("#FFD166", int(255 * (1 - kb * 0.6))))
    k81 = seg(t, vin(81), vin(81) + 1.4)
    if k81 > 0 and t < vin(82):
        for i, tgt in enumerate((isr, (ir[0] - 120, ir[1] + 260), (ir[0] + 160, ir[1] + 300))):
            r = route(c, [ir, ((ir[0] + tgt[0]) / 2, min(ir[1], tgt[1]) - 160), tgt], ease_io(seg(k81, i * 0.15, 0.7 + i * 0.15)), col=PAL["axis"], w=5)
            if r: x, y, ang = along(*r, ease_io(seg(k81, i * 0.15, 0.7 + i * 0.15))); ic_missile(c, x, y, 50, ang, t=t)
    k82 = seg(t, vin(82), vin(82) + 1.0)
    if k82 > 0:
        h = S(cam, "hormuz")
        for i in range(6):
            x, y = hormuz_xy(cam, 0.08 + i * 0.16)
            ic_ship(c, x, y - 8, 36)
            xmark(c, x, y - 14, 18, seg(t, kw(82, "band") + i * 0.05, kw(82, "band") + 0.3 + i * 0.05))
        title(c, "HORMUZ: LAGBHAG BAND", 960, 895, 64, seg(t, kw(82, "band"), kw(82, "band") + 0.3), PAL["axis"])
    footnote(c, "Source: Al Jazeera / Wikipedia, 'Russia in the 2026 Iran war'")
    SFX_MARK(vin(80) + 0.9, "boom", -10); SFX_MARK(kw(82, "band"), "stamp", -14)

# ---------------- S14: eyes on Moscow & Beijing (u83), veto (u84), claims (u85-87)
@shot(vin(83), vin(88))
def s14(c, t):
    k84 = seg(t, vin(84), vin(84) + 0.4)
    if k84 < 1:
        cam = (85, 45, 7.2)
        bg(c, cam, {"RUS": PAL["RUS"], "CHN": PAL["CHN"], "IRN": PAL["IRN"]})
        a = int(255 * (1 - k84))
        for key in ("moscow", "beijing"):
            x, y = S(cam, key); kk = seg(t, kw(83, key), kw(83, key) + 0.3)
            c.drawCircle(x, y, 120 * kk, paint("#FFD166", int(70 * (1 - k84)))); c.drawCircle(x, y, 120 * kk, paint("#FFD166", a, stroke=5))
            if kk > 0:
                c.drawOval(skia.Rect(x - 46 * kk, y - 24 * kk, x + 46 * kk, y + 24 * kk), paint("#F1FAEE", a))
                c.drawCircle(x, y, 17 * kk, paint("#0F1B2D", a)); c.drawCircle(x + 5 * kk, y - 5 * kk, 5 * kk, paint("#F1FAEE", a))
        title(c, "SABKI NAZAR: MOSCOW + BEIJING", 960, 140, 56, seg(t, vin(83), vin(83) + 0.4), PAL["yel"], a)
    k85 = seg(t, vin(85), vin(85) + 0.4)
    if k84 > 0 and k85 < 1:
        c.save(); c.saveLayerAlpha(None, int(255 * k84 * (1 - k85))); bg(c)
        date_chip(c, "APRIL 2026", 960, 120, k84)
        c.save(); c.translate(960, 520); c.scale(back(k84) * 2.6, back(k84) * 2.6); ic_un_table(c, 0, 0, 100); c.restore()
        text(c, "UN SECURITY COUNCIL · HORMUZ RESOLUTION", 960, 860, 44, "#F1FAEE", FT_BLACK, "c")
        stamp(c, "VETO · RUSSIA", 560, 360, 64, PAL["axis"], seg(t, kw(84, "veto"), kw(84, "veto") + 0.18))
        stamp(c, "VETO · CHINA", 1360, 680, 64, PAL["axis"], seg(t, kw(84, "veto") + 0.35, kw(84, "veto") + 0.53), ang=6)
        footnote(c, "Source: Al Jazeera, 7 Apr 2026")
        c.restore(); c.restore()
    if k85 > 0:
        c.save(); c.saveLayerAlpha(None, int(255 * k85)); bg(c)
        kr = seg(t, vin(87), vin(87) + 0.8)
        split_says(c, 0.6 + 0.4 * kr if t >= vin(87) else seg(t, vin(85), vin(85) + 0.5) * 0.45,
                   ("IRAN KEHTA HAI", ["Russia aur China", "madad kar rahe hain."]), ("WASHINGTON", ["Madad 'bahut kam", "level' ki hai."]), "ir", "us", t)
        kd = seg(t, vin(86), vin(86) + 0.4) * (1 - seg(t, vin(87) - 0.15, vin(87) + 0.15))
        if kd > 0:
            dim(c, 160 * kd)
            doc(c, "russia_war", 260, lerp(DH + 20, 270, ease_out(kd)), 1400, 520, t, 1, [(1, kw(86, "intelligence") - 0.3, 1.2)], a=int(255 * kd))
            footnote(c, "Source: Wikipedia, 'Russia in the 2026 Iran war' (CC BY-SA 4.0) · CNN reporting")
        else:
            footnote(c, "Claims: Iran's Foreign Minister; US President Trump · contested")
        c.restore(); c.restore()

# ---------------- S15: no soldiers, no guarantee (u88-89)
@shot(vin(88), vin(90))
def s15(c, t):
    bg(c)
    k89 = seg(t, vin(89), vin(89) + 0.4)
    kd = ease_out(seg(t, vin(88), vin(88) + 0.5)) * (1 - k89)
    if kd > 0:
        doc(c, "russia_war", 240, lerp(DH, 140, kd), 1440, 420, t, 2, [(2, kw(88, "na koi"), 1.2)], a=int(255 * kd))
        for i, (lab, ic) in enumerate((("RUSSIAN SAINIK", "soldier"), ("CHINESE JAHAAZ", "ship"))):
            x = 640 + i * 640; y = 800
            if ic == "soldier": ic_soldier(c, x, y, 140, t, walk=False)
            else: ic_ship(c, x, y, 160)
            xmark(c, x, y - 20, 90, seg(t, kw(88, "russian" if i == 0 else "chinese"), kw(88, "russian" if i == 0 else "chinese") + 0.4))
            text(c, lab, x, y + 150, 40, "#F1FAEE", FT_BLACK, "c", int(255 * kd))
        footnote(c, "Source: Wikipedia, 'Russia in the 2026 Iran war' (CC BY-SA 4.0)")
    if k89 > 0:
        a = int(255 * k89); c.save(); c.translate(960, 480); c.scale(back(k89), back(k89))
        p = skia.Path(); p.moveTo(0, -230); p.lineTo(200, -150); p.cubicTo(200, 80, 110, 190, 0, 250); p.cubicTo(-110, 190, -200, 80, -200, -150); p.close()
        c.drawPath(p, paint("#2E4A6B", a)); c.drawPath(p, paint("#F1FAEE", a, stroke=10)); flag_circle(c, "ir", 0, 0, 90, a=a); c.restore()
        xmark(c, 960, 480, 220, seg(t, kw(89, "guarantee") - 0.2, kw(89, "guarantee") + 0.3))
        title(c, "SECURITY GUARANTEE: KISI NE NAHI DI", 960, 900, 56, k89, PAL["yel"])

# ---------------- S16: China loss (u90-91), Russia gain (u92-95)
@shot(vin(90), vin(96))
def s16(c, t):
    bg(c)
    k92 = seg(t, vin(92), vin(92) + 0.4)
    if k92 < 1:
        a = int(255 * (1 - k92))
        flag_circle(c, "cn", 260, 300, 100, a=a, k=back(seg(t, vin(90), vin(90) + 0.4)))
        title(c, "CHINA KO NUKSAAN", 840, 325, 70, seg(t, vin(90), vin(90) + 0.4), PAL["axis"], a)
        k91 = seg(t, vin(91), vin(91) + 0.4)
        if k91 > 0:
            text(c, "China ka samundari tel import (index)", 960, 480, 40, "#F1FAEE", FT_SEMI, "c", a)
            for i, (lab, v, col) in enumerate((("JUNG SE PEHLE", 100, "#8A9BB0"), ("AUGUST 2026", 60, PAL["axis"]))):
                kk = ease_out(seg(t, vin(91) + 0.3 + i * 0.8, vin(91) + 1.2 + i * 0.8))
                x = 700 + i * 520; hgt = 380 * v / 100 * kk
                rrect(c, x - 110, 960 - hgt, x + 110, 960, 12, col, a)
                text(c, lab, x, 1010, 32, "#F1FAEE", FT_BLACK, "c", a)
                if kk > 0: text(c, f"{int(v * kk)}", x, 940 - hgt, 60, "#F1FAEE", FT_BLACK, "c", a)
            stamp(c, "− 40%", 1500, 640, 90, PAL["axis"], seg(t, kw(91, "40"), kw(91, "40") + 0.2))
            footnote(c, "Source: PIIE analysis, Kpler data (Aug 2026: ~7.14 mb/d)")
    if k92 > 0:
        c.save(); c.saveLayerAlpha(None, int(255 * k92)); bg(c)
        flag_circle(c, "ru", 260, 300, 100, k=back(k92)); title(c, "RUSSIA KO FAYDA", 840, 325, 70, seg(t, vin(93), vin(93) + 0.4), "#5FD07A")
        k94 = seg(t, vin(94), vin(94) + 0.4)
        if k94 > 0:
            ic_barrel(c, 300, 640, 180);
            ar = ease_out(seg(t, kw(94, "mehenga"), kw(94, "mehenga") + 0.6))
            c.drawLine(470, 760, 470, 760 - 220 * ar, paint("#5FD07A", 255, stroke=16, cap_round=True))
            p = skia.Path(); p.moveTo(430, 760 - 220 * ar); p.lineTo(510, 760 - 220 * ar); p.lineTo(470, 700 - 220 * ar); p.close(); c.drawPath(p, paint("#5FD07A", int(255 * ar)))
            v = ease_out(seg(t, kw(94, "90") - 0.2, kw(94, "90") + 0.8))
            cx, cy, R = 1000, 640, 220
            c.drawCircle(cx, cy, R, paint("#22304A"))
            arc = skia.Path(); arc.moveTo(cx, cy); arc.arcTo(skia.Rect(cx - R, cy - R, cx + R, cy + R), -90, 324 * v, False); arc.close()
            c.drawPath(arc, paint(PAL["RUS"])); c.drawCircle(cx, cy, R * 0.55, paint(PAL["ocean"]))
            text(c, f"{int(90 * v)}%", cx, cy + 30, 96, "#F1FAEE", FT_BLACK, "c")
            text(c, "Russia ka crude export (Q1 2026)", cx, cy + R + 70, 36, "#F1FAEE", FT_SEMI, "c")
            kci = back(seg(t, vin(95), vin(95) + 0.4))
            flag_circle(c, "cn", 1480, 520, 90, k=kci); flag_circle(c, "in", 1480, 760, 90, k=back(seg(t, kw(95, "india"), kw(95, "india") + 0.4)))
            if kci > 0:
                route(c, [(cx + R, cy - 40), (1380, 520)], kci, col=PAL["yel"], w=6); route(c, [(cx + R, cy + 40), (1380, 760)], seg(t, kw(95, "india"), kw(95, "india") + 0.4), col=PAL["yel"], w=6)
            footnote(c, "Source: CNBC, 15 Apr 2026")
        c.restore(); c.restore()

# ---------------- S17: Hormuz today (u96-100)
@shot(vin(96), 370.97)
def s17(c, t):
    k97 = seg(t, vin(97), vin(97) + 0.4); k99 = seg(t, vin(99), vin(99) + 0.4); k100 = seg(t, vin(100), vin(100) + 0.4)
    cam = (56.3, 26.4, 110)
    if k97 < 1 or k99 > 0:
        bg(c, cam, {"IRN": PAL["IRN"], "OMN": "#3E5068", "ARE": "#3E5068"})
    if k97 < 1:
        a = int(255 * (1 - k97))
        h = S(cam, "hormuz")
        for i in range(3):
            f = (t * 0.05 + i / 3) % 1; x, y = hormuz_xy(cam, f); ic_ship(c, x, y - 8, 36, a=a)
        date_chip(c, "NOVEMBER 2026", 960, 120, seg(t, vin(96), vin(96) + 0.4))
        stat_card(c, 1180, 560, 620, 340, "−65%", "Hormuz traffic vs pre-war", seg(t, kw(96, "65") - 0.3, kw(96, "65")) * (1 - k97), col=PAL["axis"], sub="Source: UKMTO")
    if k97 > 0 and k99 < 1:
        c.save(); c.saveLayerAlpha(None, int(255 * k97 * (1 - k99))); bg(c)
        k98 = seg(t, vin(98), vin(98) + 0.6)
        split_says(c, 0.45 + 0.55 * k98 if t >= vin(98) else 0.45 * k97, ("IRAN KEHTA HAI", ["Tankers mines se", "takraye."]), ("AMERICA KEHTA HAI", ["Main raaste saaf", "kar diye gaye."]), "ir", "us", t)
        for i in range(3): ic_mine(c, 260 + i * 140, 690, 60 * k97, t)
        footnote(c, "Claims: Iran's IRGC; US military (Nov 2026) · not independently verified")
        c.restore(); c.restore()
    if k99 > 0 and k100 < 1:
        a = int(255 * (1 - k100))
        cam2 = (65, 40, 6.5); c.save(); c.saveLayerAlpha(None, int(255 * k99 * (1 - k100))); bg(c, cam2, {"RUS": PAL["RUS"], "CHN": PAL["CHN"], "IRN": PAL["IRN"]})
        h = S(cam2, "hormuz")
        for key in ("moscow", "beijing"):
            s_ = S(cam2, key); r = route(c, [s_, h], 0.55 * ease_io(seg(t, vin(99) + 0.4, vin(99) + 1.6)), col="#8A9BB0", w=6)
            if r: x, y, _ = along(*r, 1.0); xmark(c, x, y, 26, seg(t, vin(99) + 1.6, vin(99) + 2.0))
        pin(c, *h, "HORMUZ", k99, t=t, size=26)
        title(c, "KOI FAUJ NAHI AAYI", 960, 895, 64, seg(t, kw(99, "fauj") - 0.2, kw(99, "fauj") + 0.2), PAL["axis"])
        c.restore(); c.restore()
    if k100 > 0:
        c.save(); c.saveLayerAlpha(None, int(255 * k100)); bg(c)
        c.save(); c.translate(960, 520); c.scale(back(k100) * 3, back(k100) * 3); ic_scale(c, 0, 0, 100, 0.12 * math.sin(t * 2.5)); c.restore()
        ka = back(seg(t, kw(100, "axis") - 0.1, kw(100, "axis") + 0.3)); km = back(seg(t, kw(100, "mauka") - 0.1, kw(100, "mauka") + 0.3))
        if ka > 0: c.save(); c.translate(520, 740); c.scale(ka, ka); text(c, "\u201cAXIS\u201d", 0, 20, 80, PAL["axis"], FT_BLACK, "c"); c.restore()
        if km > 0: c.save(); c.translate(1420, 740); c.scale(km, km); text(c, "MAUKE KI DOSTI?", 0, 20, 70, PAL["yel"], FT_BLACK, "c"); c.restore()
        c.restore(); c.restore()

chapter(5, "INDIA KA DILEMMA", 370.97, vin(103))

# ---------------- S18: India and three ropes (u103-u112)
@shot(vin(103), vin(113))
def s18(c, t):
    kch = seg(t, vin(108) - 0.1, vin(108) + 0.6) * (1 - seg(t, vin(111) - 0.1, vin(111) + 0.5))
    cam = scene1.fly((78, 32, 7.5), (61.5, 25.4, 85), ease_io(kch))
    fills = {"IND": PAL["IND"], "RUS": (PAL["RUS"], int(255 * seg(t, vin(105), vin(105) + 0.4))), "IRN": (PAL["IRN"], int(255 * seg(t, vin(108), vin(108) + 0.4))),
             "CHN": (PAL["CHN"], int(255 * seg(t, vin(111), vin(111) + 0.4))), "PAK": "#3E5068"}
    bg(c, cam, fills)
    d = S(cam, "delhi")
    if kch < 0.5:
        ic_question(c, d[0], d[1] - 160, 160 * back(seg(t, kw(104, "india"), kw(104, "india") + 0.4)) * (1 - seg(t, vin(105), vin(105) + 0.3)))
        for key, ui, col, lab in (("moscow", 105, PAL["RUS"], "RUSSIA"), ("tehran", 108, PAL["IRN"], "IRAN"), ("beijing", 111, PAL["CHN"], "CHINA")):
            k = seg(t, vin(ui), vin(ui) + 0.6)
            if k > 0:
                route(c, [d, S(cam, key)], ease_io(k), col="#E8C27A", w=8, dash=False, head=False)
                x, y = S(cam, key); pill(c, lab, x, y - 50, 36, col, a=int(255 * clamp(k * 1.5)))
        # Russia items
        k105 = seg(t, vin(105), vin(105) + 0.3) * (1 - seg(t, vin(108) - 0.2, vin(108)))
        if k105 > 0:
            a = int(255 * k105); rrect(c, 1240, 300, 1840, 760, 26, "#16223A", a, shadow=20)
            flag_circle(c, "ru", 1330, 380, 50, a=a); text(c, "PURANA DEFENCE PARTNER", 1400, 395, 30, "#F1FAEE", FT_BLACK, "l", a)
            kk = back(seg(t, kw(107, "s-400"), kw(107, "s-400") + 0.4))
            if kk > 0:
                c.save(); c.translate(1380, 560); c.scale(kk, kk)
                rrect(c, -90, 20, 90, 60, 8, "#4B5D3A", a);
                for j in range(4): ic_missile(c, -50 + j * 30, -10, 60, -60, a=a, flame=False)
                c.restore(); text(c, "S-400", 1380, 690, 40, PAL["yel"], FT_BLACK, "c", a)
            kb = back(seg(t, kw(107, "sasta"), kw(107, "sasta") + 0.4))
            if kb > 0: ic_barrel(c, 1660, 560, 140 * kb, a=a); text(c, "SASTA TEL", 1660, 690, 40, PAL["yel"], FT_BLACK, "c", a)
        k111 = seg(t, vin(111) + 0.4, vin(111) + 0.8)
        if k111 > 0:
            l = S(cam, "ladakh")
            c.drawCircle(l[0], l[1], 60 + 10 * math.sin(t * 6), paint(PAL["axis"], int(200 * k111), stroke=8))
            pill(c, "LAC: RIVAL", l[0] - 40, l[1] - 110, 36, PAL["axis"], a=int(255 * k111))
            kt = seg(t, kw(112, "trade"), kw(112, "trade") + 0.4)
            if kt > 0:
                rrect(c, 1240, 620, 1840, 900, 26, "#16223A", int(255 * kt), shadow=20)
                ic_coins(c, 1340, 770, 110, a=int(255 * kt)); ic_ship(c, 1520, 780, 110, a=int(255 * kt))
                text(c, "BADA TRADE PARTNER", 1540, 680, 34, PAL["yel"], FT_BLACK, "c", int(255 * kt))
    if kch > 0.5:
        a = int(255 * min(1, (kch - 0.5) * 2))
        ch, gw = S(cam, "chabahar"), S(cam, "gwadar")
        pin(c, *ch, "CHABAHAR (India)", seg(t, kw(109, "chabahar"), kw(109, "chabahar") + 0.3), col=PAL["IND"], t=t, side="l")
        pin(c, *gw, "GWADAR (China)", seg(t, kw(109, "gwadar"), kw(109, "gwadar") + 0.3), col=PAL["CHN"], t=t)
        kd = seg(t, kw(109, "170") - 0.2, kw(109, "170") + 0.4)
        if kd > 0:
            c.drawLine(ch[0], ch[1] + 60, ch[0] + (gw[0] - ch[0]) * ease_out(kd), ch[1] + 60 + (gw[1] - ch[1]) * ease_out(kd), paint(PAL["yel"], 255, stroke=6))
            pill(c, "~170 KM", (ch[0] + gw[0]) / 2, ch[1] + 120, 40, PAL["yel"], fg="#0F1B2D", a=int(255 * clamp(kd * 1.5)))
        kq = ease_out(seg(t, kw(109, "170") + 0.6, kw(109, "170") + 1.0)) * (1 - seg(t, vin(110) - 0.1, vin(110) + 0.2))
        if kq > 0:
            doc(c, "chabahar", 260, lerp(DH, 640, kq), 1400, 300, t, 0, [(0, kw(109, "170") + 0.8, 1.2)], a=int(255 * kq))
            footnote(c, "Source: Wikipedia, 'Chabahar Port' (CC BY-SA 4.0)")
        kb = seg(t, vin(110), vin(110) + 0.4)
        if kb > 0:
            stat_card(c, 1060, 620, 800, 330, "₹ 0", "Chabahar allocation, Budget 2026-27", kb, col=PAL["axis"], tag="REPORTS", sub="after US sanctions waiver was revoked")
            footnote(c, "Source: Modern Diplomacy / IMPRI analysis (2026)")

# ---------------- S19: oil story (u113-u116)
@shot(vin(113), vin(117))
def s19(c, t):
    k115 = seg(t, vin(115), vin(115) + 0.5); k116 = seg(t, vin(116), vin(116) + 0.5)
    cam = (62, 32, 7.0) if k116 < 1 else (60, 26, 14)
    if k115 < 1 or k116 > 0:
        cam = scene1.fly((62, 34, 6.2), (60, 26, 14), ease_io(k116))
        bg(c, cam, {"IND": PAL["IND"], "RUS": PAL["RUS"], "SAU": (PAL["IRN"], int(255 * k116)), "IRQ": (PAL["IRN"], int(255 * k116)), "ARE": (PAL["IRN"], int(255 * k116))})
    title(c, "TEL KI KAHANI", 960, 120, 60, seg(t, vin(113), vin(113) + 0.4), PAL["yel"])
    if k115 < 1:
        k114 = seg(t, vin(114), vin(114) + 2.0)
        r = route(c, [S(cam, "novoross"), (to_screen(cam, 30, 30)), S(cam, "jamnagar")], ease_io(k114), col="#7FA6E8", w=7)
        if r: x, y, _ = along(*r, ease_io(k114)); ic_ship(c, x, y - 10, 60)
        text(c, "UKRAINE WAR KE BAAD: SASTA RUSSIAN TEL", 960, 900, 40, "#F1FAEE", FT_BLACK, "c", int(255 * seg(t, vin(114), vin(114) + 0.4) * (1 - k115)), shadow=True)
    if k115 > 0 and k116 < 1:
        c.save(); c.saveLayerAlpha(None, int(255 * k115 * (1 - k116))); bg(c)
        date_chip(c, "NOVEMBER 2026 · KPLER", 960, 140, k115)
        bars(c, 420, 330, 1100, 420, [("Hormuz raaste se (Gulf)", 21.0, PAL["IRN"], "sa"), ("Russia se", 18.0, PAL["RUS"], "ru")], seg(t, kw(115, "21") - 0.6, kw(115, "18") + 0.6), 24, unit=" lakh barrel/din")
        stamp(c, "PEHLI BAAR AAGE", 1300, 860, 60, PAL["yel"], seg(t, kw(115, "pehli baar"), kw(115, "pehli baar") + 0.2))
        footnote(c, "Source: Kpler data via Business Standard (Nov 2026)")
        c.restore(); c.restore()
    if k116 > 0:
        dst = S(cam, "jamnagar")
        for i, key in enumerate(("saudi", "basra", "uae")):
            r = route(c, [S(cam, key), dst], ease_io(seg(t, vin(116) + 0.3 + i * 0.2, vin(116) + 1.3 + i * 0.2)), col=PAL["yel"], w=6)
            if r: x, y, _ = along(*r, ((t * 0.3 + i / 3) % 1)); ic_ship(c, x, y - 10, 40)
        title(c, "WAPAS GULF SUPPLIERS KI TARAF", 960, 895, 50, seg(t, kw(116, "gulf"), kw(116, "gulf") + 0.3), PAL["yel"])

# ---------------- S20: India's relations reality (u117), autonomy debate (u118-120)
@shot(vin(117), vin(121))
def s20(c, t):
    bg(c)
    k118 = seg(t, vin(118), vin(118) + 0.4)
    if k118 < 1:
        a = int(255 * (1 - k118))
        flag_circle(c, "in", 960, 520, 120, a=a, k=back(seg(t, vin(117), vin(117) + 0.4)))
        items = [("ru", "RUSSIA", "GEHRE RISHTE", True, (520, 300)), ("ir", "IRAN", "GEHRE RISHTE", True, (1400, 300)),
                 ("cn", "CHINA", "SABSE BADA RIVAL", False, (1400, 760)), ("kp", "NORTH KOREA", "KOI KHAAS RISHTA NAHI", None, (520, 760))]
        for i, (fc, nm, lab, good, (x, y)) in enumerate(items):
            A = UN[117].get("anchors"); t_i = [A["russia"], A["russia"] + 0.75, A["china"] - 0.05, A["china"] + 0.8][i] if A else vin(117) + 0.5 + i * 0.6
            k = seg(t, t_i, t_i + 0.4)
            if k <= 0: continue
            col = "#5FD07A" if good else (PAL["axis"] if good is False else "#8A9BB0")
            route(c, [(960, 520), (x, y)], ease_io(k), col=col, w=8, dash=good is None, head=False)
            flag_circle(c, fc, x, y, 80, a=a, k=back(k))
            text(c, nm, x, y + 135, 38, "#F1FAEE", FT_BLACK, "c", a); text(c, lab, x, y + 180, 30, col, FT_BLACK, "c", a)
            if good: tick(c, x + 90, y - 70, 30, seg(t, t_i + 0.3, t_i + 0.7))
            elif good is False:
                c.saveLayerAlpha(None, a); swords(c, x + 100, y - 70, 44, k, PAL["axis"]); c.restore()
    if k118 > 0:
        c.save(); c.saveLayerAlpha(None, int(255 * k118))
        k119 = seg(t, vin(119), vin(119) + 0.5); k120 = seg(t, vin(120), vin(120) + 0.5)
        if k120 < 1:
            al = int(255 * (1 - k120))
            flag_circle(c, "in", 960, 520, 110, k=back(k118), a=al)
            for i, (fc, ang) in enumerate((("ru", -150), ("us", -30), ("ir", 150), ("sa", 30), ("fr", 90) if False else ("jp", 90) if False else ("eu", 90) if False else ("ae", 90))):
                pass
            for i, fc in enumerate(("ru", "us", "ir", "ae", "jp" if os.path.exists(FLAGS + "jp.png") else "au", "fr" if os.path.exists(FLAGS + "fr.png") else "gb")):
                ang = math.radians(-90 + i * 60); x, y = 960 + 330 * math.cos(ang), 520 + 300 * math.sin(ang)
                kk = seg(t, vin(118) + 0.2 + i * 0.12, vin(118) + 0.6 + i * 0.12)
                route(c, [(960, 520), (x, y)], ease_io(kk), col="#5FD07A", w=5, head=False); flag_circle(c, fc, x, y, 52, k=back(kk), a=al)
            title(c, "STRATEGIC AUTONOMY / MULTI-ALIGNMENT", 960, 120, 50, seg(t, kw(118, "strategic"), kw(118, "strategic") + 0.4), PAL["yel"], al)
            title(c, "“Sabse dosti, kisi ka ghulam nahi”", 960, 960, 46, seg(t, kw(118, "sabse"), kw(118, "sabse") + 0.4), "#F1FAEE", al)
            if k119 > 0:
                for i in range(6):
                    ang = math.radians(i * 60 + 30); x, y = 960 + 520 * math.cos(ang) * (1 - 0.35 * k119), 520 + 420 * math.sin(ang) * (1 - 0.35 * k119)
                    p = skia.Path(); p.moveTo(x, y); ux, uy = 960 - x, 520 - y; L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
                    p.moveTo(x, y); p.lineTo(x + ux * 90, y + uy * 90); c.drawPath(p, paint(PAL["axis"], al, stroke=14, cap_round=True))
                title(c, "CRITICS: DABAV MEIN BALANCING KAMZOR", 960, 210, 40, k119, PAL["axis"], al)
        if k120 > 0:
            c.save(); c.translate(960, 500); c.scale(back(k120) * 3.2, back(k120) * 3.2); ic_scale(c, 0, 0, 100, 0.05 * math.sin(t * 2)); c.restore()
            text(c, "SARKAR", 450, 780, 56, "#5FD07A", FT_BLACK, "c"); text(c, "CRITICS", 1470, 780, 56, PAL["axis"], FT_BLACK, "c")
            title(c, "SACH: SHAYAD DONO KE BEECH", 960, 895, 56, seg(t, kw(120, "beech") - 0.3, kw(120, "beech")), PAL["yel"])
        c.restore(); c.restore()

# ---------------- S21: verdict (u121-u124)
@shot(vin(121), vin(125))
def s21(c, t):
    bg(c, (95, 40, 7.6), {k: (v, 120) for k, v in CR.items()}); dim(c, 120)
    k122 = seg(t, vin(122), vin(122) + 0.4); k124 = seg(t, vin(124), vin(124) + 0.4)
    if k122 < 1: title(c, "TOH AAKHIR MEIN... YEH HAI KYA?", 960, 540, 80, seg(t, vin(121), vin(121) + 0.4), "#F1FAEE", int(255 * (1 - k122)))
    if k122 > 0 and k124 < 1:
        a = int(255 * k122 * (1 - k124))
        stamp(c, "NATO NAHI", 960, 230, 90, PAL["axis"], seg(t, kw(122, "nato"), kw(122, "nato") + 0.18), a=a)
        for i, (w, lab) in enumerate((("command", "EK COMMAND"), ("treaty", "EK TREATY"), ("marne", "MARNE KA VAADA"))):
            kk = seg(t, kw(123, w) - 0.2, kw(123, w) + 0.2)
            if kk <= 0: continue
            y = 450 + i * 150
            text(c, lab, 820, y + 20, 64, "#F1FAEE", FT_BLACK, "l", int(a * clamp(kk * 2))); xmark(c, 700, y, 46, kk)
    if k124 > 0:
        a = int(255 * k124)
        title(c, "LENE-DENE KA NETWORK", 960, 140, 64, k124, PAL["yel"])
        P = {"RUS": (960, 330), "CHN": (1330, 560), "PRK": (960, 820), "IRN": (590, 560)}
        for code, (x, y) in P.items(): flag_circle(c, NFC[code], x, y, 76, k=back(k124), a=a)
        items = [("hathiyar", "missile", ("PRK", "RUS")), ("paisa", "coins", ("CHN", "RUS")), ("technology", "chip", ("CHN", "IRN")), ("veto", "un", ("RUS", "IRN"))]
        for j, (w, ic, (s_, d_)) in enumerate(items):
            kk = seg(t, kw(124, w) - 0.1, kw(124, w) + 0.3)
            if kk <= 0: continue
            A_, B_ = P[s_], P[d_]; route(c, [A_, B_], ease_io(kk), col=PAL["yel"], w=5)
            f = (t * 0.5 + j * 0.25) % 1; x, y = lerp(A_[0], B_[0], f), lerp(A_[1], B_[1], f)
            if ic == "missile": ic_missile(c, x, y, 60, math.degrees(math.atan2(B_[1] - A_[1], B_[0] - A_[0])), t=t)
            elif ic == "coins": ic_coins(c, x, y, 60, 3)
            elif ic == "chip": ic_chip(c, x, y, 50, t)
            else: ic_un_table(c, x, y, 30, hl=1)
            text(c, {"hathiyar": "HATHIYAR", "paisa": "PAISA", "technology": "TECHNOLOGY", "veto": "VETO KA SAHARA"}[w], 1550 if j % 2 else 370, 820 + (j // 2) * 60, 36, PAL["yel"], FT_BLACK, "c", a)

# ---------------- S22: don't underestimate (u125-u129)
@shot(vin(125), 512.5)
def s22(c, t):
    bg(c)
    k126 = seg(t, vin(126), vin(126) + 0.4); k128 = seg(t, vin(128), vin(128) + 0.4); k129 = seg(t, vin(129), vin(129) + 0.4)
    if k126 < 1:
        a = int(255 * (1 - k126)); kk = back(seg(t, vin(125), vin(125) + 0.4))
        c.save(); c.translate(960, 500); c.scale(kk, kk)
        p = skia.Path(); p.moveTo(0, -230); p.lineTo(250, 200); p.lineTo(-250, 200); p.close(); c.drawPath(p, paint("#FFD166", a)); c.drawPath(p, paint("#0F1B2D", a, stroke=14))
        text(c, "!", 0, 150, 300, "#0F1B2D", FT_BLACK, "c", a); c.restore()
        title(c, "HALKE MEIN LENA GALTI", 960, 900, 64, kk, PAL["yel"], a)
    if k126 > 0 and k128 < 1:
        c.save(); c.saveLayerAlpha(None, int(255 * k126 * (1 - k128)))
        pill(c, "SIPRI YEARBOOK 2026", 960, 130, 36, "#3C6FD8")
        flag_circle(c, "cn", 420, 470, 110, k=back(k126))
        v = ease_out(seg(t, kw(126, "620") - 0.4, kw(126, "620") + 0.8))
        text(c, f"~{int(620 * v)}", 800, 520, 160, "#F1FAEE", FT_BLACK, "l"); text(c, "nuclear warheads", 810, 590, 44, PAL["muted"], FT_SEMI, "l")
        for i in range(10):
            ki = seg(t, kw(126, "620") + i * 0.07, kw(126, "620") + 0.3 + i * 0.07)
            if ki > 0: ic_warhead(c, 820 + i * 85, 700, 60 * ki)
        kf = seg(t, kw(126, "tezi"), kw(126, "tezi") + 0.4)
        if kf > 0:
            c.drawLine(1560, 760, 1560 + 160 * kf, 600 - 40 * kf, paint("#5FD07A", 255, stroke=14, cap_round=True))
            text(c, "SABSE TEZ BADHOTARI", 1560, 820, 34, "#5FD07A", FT_BLACK, "c", int(255 * kf))
        k127 = seg(t, vin(127), vin(127) + 0.4)
        if k127 > 0:
            flag_circle(c, "ru", 420, 840, 90, k=back(k127)); stat_card(c, 600, 730, 900, 220, "No.1", "duniya ka sabse bada nuclear arsenal", k127, col="#7FA6E8")
        footnote(c, "Source: SIPRI Yearbook 2026 (Jan 2026 estimates)")
        c.restore(); c.restore()
    if k128 > 0 and k129 < 1:
        a = int(255 * k128 * (1 - k129))
        c.save(); c.saveLayerAlpha(None, a)
        # frayed rope with shockwave
        c.drawLine(300, 520, 860, 520, paint("#C9A66B", 255, stroke=26, cap_round=True)); c.drawLine(1060, 520, 1620, 520, paint("#C9A66B", 255, stroke=26, cap_round=True))
        for i in range(6): c.drawLine(860, 520, 920 + (i % 3) * 20, 470 + i * 18, paint("#C9A66B", 255, stroke=6)); c.drawLine(1060, 520, 1000 - (i % 3) * 20, 470 + i * 18, paint("#C9A66B", 255, stroke=6))
        title(c, "DOSTI KACHCHI...", 960, 340, 70, seg(t, vin(128), vin(128) + 0.4), "#F1FAEE")
        ka = seg(t, kw(128, "asar"), kw(128, "asar") + 0.6)
        if ka > 0:
            for i in range(3):
                rp = (seg(t, kw(128, "asar"), kw(128, "asar") + 2.0) + i * 0.3) % 1
                c.drawCircle(960, 700, 80 + 400 * rp, paint(PAL["axis"], int(180 * (1 - rp)), stroke=8))
            title(c, "...ASAR ASLI", 960, 760, 80, ka, PAL["axis"])
        c.restore(); c.restore()
    if k129 > 0:
        c.save(); c.saveLayerAlpha(None, int(255 * k129))
        sky = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 560)], [hexc("#0F1B2D"), hexc("#26395C")])
        pp = skia.Paint(); pp.setShader(sky); c.drawRect(skia.Rect(0, 0, DW, 560), pp)
        c.drawRect(skia.Rect(0, 560, DW, DH), paint("#1B2A40"))
        # three roads from the bottom: left (USA), centre (India), right (CRINK)
        for dx, col in ((-700, "#2E3F5C"), (700, "#2E3F5C"), (0, "#3E5068")):
            p = skia.Path(); p.moveTo(960 - 230 + dx * 0.15, DH); p.lineTo(960 + dx - 40, 560); p.lineTo(960 + dx + 40, 560); p.lineTo(960 + 230 + dx * 0.15, DH); p.close()
            c.drawPath(p, paint(col))
        for i in range(8):
            y0 = 560 + (DH - 560) * (i / 8) ** 1.6; y1 = 560 + (DH - 560) * ((i + 0.5) / 8) ** 1.6
            c.drawLine(960, y0, 960, y1, paint("#FFD166", 255, stroke=3 + i * 1.5))
        flag_circle(c, "us", 960 - 700, 520, 46, a=150); flag_circle(c, "cn", 960 + 660, 520, 40, a=150); flag_circle(c, "ru", 960 + 760, 520, 40, a=150)
        kr = ease_out(seg(t, kw(129, "raasta") - 0.6, kw(129, "raasta") + 1.2))
        y = lerp(980, 600, kr); sc = lerp(1.0, 0.45, kr)
        flag_circle(c, "in", 960, y, 90 * sc)
        title(c, "SABAK", 960, 110, 44, k129, "#F1FAEE")
        title(c, "APNA RAASTA KHUD CHUNNA HOGA", 960, 230, 70, seg(t, kw(129, "apna"), kw(129, "apna") + 0.4), PAL["yel"])
        c.restore(); c.restore()

@shot(*HOST["H3"])
def h3(c, t):
    host_frame(c, "H3", t); subscribe_card(c, t - 513.0)
    SFX_MARK(513.0 + 1.40, "pop", -12); SFX_MARK(513.0 + 2.55, "ding", -14)

@shot(524.2, T_TOTAL)
def endcard(c, t):
    lt = t - 524.2
    bg(c, (95, 40, 6.2), {k: (v, 90) for k, v in CR.items()}); dim(c, 150)
    k = back(seg(lt, 0, 0.6))
    c.save(); c.translate(960, 300); c.scale(k, k); draw_img(c, LOGO_BIG, -200, -200, 200, 200); c.restore()
    title(c, "AMRIT BORI", 960, 610, 90, seg(lt, 0.3, 0.8))
    title(c, "Agla video kis desh par? Comment karo!", 960, 690, 44, seg(lt, 0.6, 1.1), PAL["yel"])
    subscribe_card(c, lt - 0.4)
    fade = seg(t, T_TOTAL - 0.6, T_TOTAL)
    if fade > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(255 * fade)))

# ======================================================================================= captions
CAPS = []
def build_caps():
    for i, u in enumerate(UN):
        words = u["text"].replace("…", "...").split()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 6 or w.endswith((",", ".", "?", ":", "!")) and len(cur) >= 3:
                chunks.append(" ".join(cur)); cur = []
        if cur: chunks.append(" ".join(cur))
        tot = sum(len(ch) for ch in chunks); acc = u["start"]
        for ch in chunks:
            d = (u["end"] - u["start"]) * len(ch) / tot
            CAPS.append((acc, acc + d, ch)); acc += d
build_caps()
NO_CAP = [(0, 4.9), (55.85, vin(19)), (104.7, vin(34)), (161.72, vin(48)), (271.55, vin(79)), (370.97, vin(103))]
def captions(c, t):
    if any(a <= t < b for a, b in NO_CAP): return
    for a, b, s in CAPS:
        if a - 0.05 <= t < b + 0.15:
            k = seg(t, a - 0.05, a + 0.1)
            w = text_w(s, 40, FT_BLACK)
            rrect(c, 960 - w / 2 - 26, 990, 960 + w / 2 + 26, 1050, 14, "#000000", int(150 * k))
            text(c, s, 960, 1033, 40, "#FFFFFF", FT_BLACK, "c", int(255 * k))
            return

# ======================================================================================= frame
SHOTS.sort(key=lambda s: s[0])
def find(t):
    for i, (a, b, fn, tr) in enumerate(SHOTS):
        if a <= t < b: return i
    return None

def remap(T):
    """video time -> (VO time, gap info). Each chapter card gets CH_GAP seconds of extra silent animation."""
    off = 0.0
    for k, P in enumerate(GAPS):
        vs = P + off
        if T < vs: return T - off, None
        if T < vs + CH_GAP: return P, (k, T - vs)
        off += CH_GAP
    return T - off, None
VIDEO_TOTAL = T_TOTAL + CH_GAP * 5

def render(T):
    global GAPINFO
    t, GAPINFO = remap(T)
    return render_vo(t, T)

def render_vo(t, T):
    load_assets()
    surf = skia.Surface(W4, H4); c = surf.getCanvas(); c.scale(SC, SC)
    T1 = scene1.TIM["2.1"]
    if t < vin(6):
        scene1.draw(c, t)
    else:
        i = find(t)
        if i is None: c.clear(hexc(PAL["ocean"]))
        else:
            a, b, fn, tr = SHOTS[i]
            TR = 0.35
            if tr == "fade" and t < a + TR:
                # previous visual underneath
                if i > 0 and SHOTS[i - 1][1] >= a - 0.01: SHOTS[i - 1][2](c, t)
                elif a == vin(6): scene1.draw(c, t)
                k = ease_io(seg(t, a, a + TR)); s = lerp(1.04, 1.0, k)
                c.save(); c.translate(960, 540); c.scale(s, s); c.translate(-960, -540); c.saveLayerAlpha(None, int(255 * k)); fn(c, t); c.restore(); c.restore()
            else:
                fn(c, t)
    captions(c, t)
    if not (HOST["H1"][0] <= t < HOST["H1"][1] or HOST["H2"][0] <= t < HOST["H2"][1] or HOST["H3"][0] <= t < HOST["H3"][1] or t >= 524.2):
        if t > 0.4: watermark(c, LOGO, 140)
    vignette(c, 100); grain(c, T, 12)
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

def still(t, out, scale=0.5):
    Image.fromarray(render(t)).convert("RGB").resize((int(3840 * scale), int(2160 * scale)), Image.LANCZOS).save(out)

def encode_chunk(i0, i1, out, fps=60):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W4}x{H4}", "-r", str(fps), "-i", "-",
                           "-c:v", "libx265", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p10le", "-x265-params", "log-level=error:pools=1",
                           "-tag:v", "hvc1", out], stdin=subprocess.PIPE)
    for i in range(i0, i1): ff.stdin.write(render(i / fps).tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for tt in sys.argv[3:]: still(float(tt), f"{sys.argv[2]}/f_{float(tt):07.2f}.png")
    elif sys.argv[1] == "chunk":
        encode_chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "sfx":
        # touch every shot once per 0.25 s so SFX_MARK events register, then dump
        load_assets()
        surf = skia.Surface(DW, DH); cc = surf.getCanvas()
        for a, b, fn, tr in SHOTS:
            for tt in (a + 0.01, b - 0.05): fn(cc, tt)
        json.dump(sorted(SFX, key=lambda x: x[1]), open(ROOT + "audio/full_sfx.json", "w"))
        print(len(SFX), "sfx events")
