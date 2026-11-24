"""Ruler cards (real painting) + matching animated 2D cartoon rulers, VS layout, and the premium timeline.
Cartoons are the channel's own flat drawings (kalpanik), styled after each ruler's painting: turban/helmet, robe, beard."""
import math
import numpy as np
import skia
from core import *
from storyproof import SERIF_DISPLAY, SERIF_TEXT

INK = "#1B1410"
# ---------------------------------------------------------------- what each cartoon wears (from the paintings)
TOON = {
    "babur": dict(skin="#F0C9A0", robe="#5E8C4A", robe2="#46703A", pattern="flowers", sash="#9B2C2C", head="turban", hc="#F4EFE2", hc2="#C9B98F",
                  plume="#2B2B2B", jewel="#2F8F5B", beard="goatee", bcol="#2B1D14", eyes="narrow", pearls=False),
    "lodi":  dict(skin="#D9A877", robe="#E2552B", robe2="#B8401E", pattern="medallion", sash="#D4AF37", head="helmet", hc="#D4AF37", hc2="#A8841F",
                  plume="#1B1B1B", jewel=None, beard="full", bcol="#1B1410", eyes="round", pearls=False),
    "akbar": dict(skin="#D8A578", robe="#F5F0E6", robe2="#DAD2C2", pattern=None, sash="#7B3F99", head="turban", hc="#E8731A", hc2="#B9561A",
                  plume=None, jewel="#FFD23F", beard="moustache", bcol="#2B1D14", eyes="round", pearls=False),
    "hemu":  dict(skin="#D29A68", robe="#C0392B", robe2="#922B21", pattern="medallion", sash="#D4AF37", head="crown", hc="#D4AF37", hc2="#B03A2E",
                  plume=None, jewel="#2ECC71", beard="full", bcol="#1B1410", eyes="round", pearls=True),
    "bhau":  dict(skin="#C68B5C", robe="#F4EFE4", robe2="#D9D0BE", pattern=None, sash="#E8731A", head="pagdi_dark", hc="#2B2622", hc2="#5A4A3A",
                  plume=None, jewel="#E9C46A", beard="moustache", bcol="#1B1410", eyes="round", pearls=True),
    "abdali": dict(skin="#E2B48A", robe="#F2D45C", robe2="#D9B640", pattern="dots", sash="#2F6B3A", head="striped", hc="#3F7F4F", hc2="#E9C46A",
                   plume="#1B1B1B", jewel="#E63946", beard="full", bcol="#141010", eyes="round", pearls=True),
}

def _p(pts, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    return p
def _fill(c, path, col, a=255, ink=True, w=3.2):
    c.drawPath(path, paint(col, a))
    if ink: c.drawPath(path, paint(INK, a, stroke=w))

def toon(c, cx, base, H, t, key, face=1, k=1.0, point=0.0, a=255, seed=0, knocked=0.0, arrow=0.0):
    """half-body cartoon ruler. base = bottom of the torso, H = full height. face = +1 looks right.
    k = entry (pops up from below), point = 0..1 raises the pointing arm toward the opponent."""
    if k <= 0: return
    S = TOON[key]; s = H / 600.0
    rise = (1 - back(clamp(k))) * 260 * s
    br = 1 + 0.012 * math.sin(t * 2.4 + seed)                                # breathing
    c.save(); c.translate(cx, base + rise); c.scale(face * s, s * br); c.rotate(-7 * ease_out(knocked))
    al = int(a * clamp(k * 2))
    # ---- torso (robe) with shoulders
    torso = skia.Path(); torso.moveTo(-170, 0); torso.cubicTo(-175, -150, -150, -250, -80, -270); torso.lineTo(80, -270)
    torso.cubicTo(150, -250, 175, -150, 170, 0); torso.close()
    _fill(c, torso, S["robe"], al)
    c.save(); c.clipPath(torso, doAntiAlias=True)
    c.drawRect(skia.Rect(-170, -270, -20, 0), paint(S["robe2"], int(al * 0.45)))
    if S["pattern"] == "flowers":
        for i in range(14):
            x = -150 + (i * 53) % 300; y = -240 + (i * 71) % 230; c.drawCircle(x, y, 7, paint("#E9DFA8", int(al * 0.8))); c.drawCircle(x, y, 3, paint("#9B2C2C", al))
    elif S["pattern"] == "dots":
        for i in range(30): c.drawCircle(-160 + (i * 37) % 320, -250 + (i * 53) % 240, 5, paint("#B8862B", al))
    elif S["pattern"] == "medallion":
        c.drawCircle(-10, -150, 46, paint(S["sash"], al)); c.drawCircle(-10, -150, 46, paint(INK, al, stroke=3))
        for i in range(10):
            ang = i / 10 * math.tau; c.drawLine(-10, -150, -10 + math.cos(ang) * 40, -150 + math.sin(ang) * 40, paint("#8A6A12", al, stroke=3))
    c.restore()
    # robe opening (angrakha cross-over) + sash
    c.drawPath(_p([(-60, -270), (40, -120), (40, 0)], False), paint(INK, int(al * 0.7), stroke=3))
    _fill(c, _p([(-168, -40), (168, -40), (170, -2), (-170, -2)]), S["sash"], al)
    if S["pearls"]:
        for i in range(13):
            ang = math.pi * (0.15 + 0.7 * i / 12); c.drawCircle(math.cos(ang) * 70 - 0, -270 + math.sin(ang) * 85, 7.5, paint("#FFFDF4", al)); c.drawCircle(math.cos(ang) * 70, -270 + math.sin(ang) * 85, 7.5, paint(INK, int(al * 0.6), stroke=1.5))
    # ---- arms: resting arm (back) and pointing / raised arm (front)
    _fill(c, _p([(-150, -235), (-185, -120), (-160, -30), (-125, -40), (-140, -125), (-118, -215)]), S["robe"], al)
    c.drawCircle(-142, -32, 24, paint(S["skin"], al)); c.drawCircle(-142, -32, 24, paint(INK, al, stroke=3))
    pk = ease_io(clamp(point)); wav = math.sin(t * 5 + seed) * 4 * pk
    ang = math.radians(lerp(100, 20, pk)) + math.radians(wav)                 # arm angle from straight down
    sx, sy = 135, -225; L1 = 150
    ex, ey = sx + math.sin(ang) * L1, sy + math.cos(ang) * L1 * (1 if pk < 0.5 else 0.9) - pk * 120
    hx, hy = ex + (ex - sx) * 0.75, ey + (ey - sy) * 0.75
    arm = skia.Path(); arm.moveTo(sx, sy); arm.lineTo(ex, ey); arm.lineTo(hx, hy)
    c.drawPath(arm, paint(INK, al, stroke=58, cap_round=True)); c.drawPath(arm, paint(S["robe"], al, stroke=50, cap_round=True))
    c.drawCircle(hx, hy, 25, paint(S["skin"], al)); c.drawCircle(hx, hy, 25, paint(INK, al, stroke=3))
    if pk > 0.4:                                                               # index finger
        fx, fy = hx + (hx - ex) * 0.45, hy + (hy - ey) * 0.45
        c.drawLine(hx, hy, fx, fy, paint(INK, al, stroke=15, cap_round=True)); c.drawLine(hx, hy, fx, fy, paint(S["skin"], al, stroke=10, cap_round=True))
    # ---- neck + head (slight nod)
    nod = math.sin(t * 1.7 + seed) * 2.5 * (1 - knocked) - 28 * ease_out(knocked)
    c.save(); c.rotate(nod)
    _fill(c, skia.Path().addRect(skia.Rect(-32, -320, 32, -262)), S["skin"], al)
    hy0 = -400; head = skia.Path().addOval(skia.Rect(-82, hy0 - 95, 82, hy0 + 92)); _fill(c, head, S["skin"], al)
    c.drawOval(skia.Rect(-96, hy0 - 22, -66, hy0 + 26), paint(S["skin"], al)); c.drawOval(skia.Rect(-96, hy0 - 22, -66, hy0 + 26), paint(INK, al, stroke=3))
    # beard / moustache
    if S["beard"] == "full":
        bd = skia.Path(); bd.moveTo(-80, hy0 + 5); bd.cubicTo(-80, hy0 + 120, 40, hy0 + 150, 84, hy0 + 30); bd.lineTo(84, hy0 + 10); bd.cubicTo(50, hy0 + 40, -30, hy0 + 55, -80, hy0 + 5); bd.close()
        _fill(c, bd, S["bcol"], al)
    elif S["beard"] == "goatee":
        bd = skia.Path(); bd.moveTo(2, hy0 + 76); bd.cubicTo(6, hy0 + 130, 34, hy0 + 132, 38, hy0 + 76); bd.close(); _fill(c, bd, S["bcol"], al)
    # 3/4 face: two eyes, nose, moustache, mouth (features turned toward `face`)
    ms = skia.Path(); ms.moveTo(18, hy0 + 38); ms.cubicTo(-4, hy0 + 30, -24, hy0 + 36, -30, hy0 + 52); ms.cubicTo(-10, hy0 + 44, 6, hy0 + 46, 18, hy0 + 48)
    ms.cubicTo(30, hy0 + 46, 50, hy0 + 44, 66, hy0 + 52); ms.cubicTo(60, hy0 + 36, 40, hy0 + 30, 18, hy0 + 38); ms.close()
    _fill(c, ms, S["bcol"], al, w=2)
    if knocked > 0.5:
        c.drawOval(skia.Rect(6, hy0 + 60, 32, hy0 + 80), paint("#5A1A12", al)); c.drawOval(skia.Rect(6, hy0 + 60, 32, hy0 + 80), paint(INK, al, stroke=2.5))
    else: c.drawLine(6, hy0 + 66, 34, hy0 + 66, paint(INK, al, stroke=3.5, cap_round=True))
    nose = _p([(22, hy0 - 12), (36, hy0 + 20), (20, hy0 + 26)], False); c.drawPath(nose, paint(INK, al, stroke=3.5, cap_round=True))
    bl = 1.0
    ph = (t + seed * 1.3) % 3.2
    if ph < 0.13: bl = abs(ph - 0.065) / 0.065
    if knocked > 0.3: bl = 0.0
    ehf = (9 if S["eyes"] == "narrow" else 14)
    for ex, ew in ((-18, 13), (42, 16)):                                      # back eye (smaller) + front eye
        eh = ehf * max(0.08, bl) * (0.9 if ew == 13 else 1.0)
        if bl > 0.05:
            c.drawOval(skia.Rect(ex - ew, hy0 - 22 - eh, ex + ew, hy0 - 22 + eh), paint("#FFFFFF", al)); c.drawOval(skia.Rect(ex - ew, hy0 - 22 - eh, ex + ew, hy0 - 22 + eh), paint(INK, al, stroke=2.5))
            if bl > 0.3: c.drawCircle(ex + ew * 0.35, hy0 - 21, 6.5 * min(1, eh / 9), paint(INK, al)); c.drawCircle(ex + ew * 0.35 + 2, hy0 - 24, 2, paint("#FFFFFF", al))
        else:
            c.drawLine(ex - ew, hy0 - 20, ex + ew, hy0 - 22, paint(INK, al, stroke=3.5, cap_round=True))
        c.drawLine(ex - ew - 2, hy0 - 48, ex + ew + 2, hy0 - 46 - (4 if knocked > 0.3 else 0), paint(S["bcol"], al, stroke=7, cap_round=True))
    if arrow > 0:                                                              # the arrow stuck at the front eye
        c.save(); c.translate(42, hy0 - 22); c.rotate(-18 + 6 * math.sin(t * 9) * (1 - knocked))
        c.drawLine(0, 0, 150, 0, paint("#3A2A1E", al, stroke=6)); c.drawPath(_p([(150, 0), (176, -12), (170, 0), (176, 12)]), paint("#C0392B", al))
        c.drawPath(_p([(132, 0), (156, -14), (150, 0), (156, 14)]), paint("#ECF0F1", al)); c.restore()
    # headgear
    hd = S["head"]
    if hd in ("turban", "striped", "pagdi_dark"):
        tb = skia.Path(); tb.moveTo(-92, hy0 - 40); tb.cubicTo(-110, hy0 - 160, 110, hy0 - 175, 92, hy0 - 40); tb.cubicTo(40, hy0 - 70, -40, hy0 - 70, -92, hy0 - 40); tb.close()
        if hd == "pagdi_dark": tb = skia.Path(); tb.moveTo(-88, hy0 - 40); tb.cubicTo(-96, hy0 - 120, 96, hy0 - 125, 90, hy0 - 40); tb.cubicTo(40, hy0 - 62, -40, hy0 - 62, -88, hy0 - 40); tb.close()
        _fill(c, tb, S["hc"], al)
        c.save(); c.clipPath(tb, doAntiAlias=True)
        for i in range(6):
            yy = hy0 - 150 + i * 22
            col = S["hc2"] if hd != "striped" else ("#7B3F99", "#E9C46A", "#3F7F4F", "#C0392B")[i % 4]
            c.drawPath(_p([(-120, yy + 30), (120, yy - 10)], False), paint(col, int(al * (0.9 if hd == "striped" else 0.55)), stroke=12 if hd == "striped" else 4))
        c.restore(); c.drawPath(tb, paint(INK, al, stroke=3.2))
        if S["jewel"]: c.drawCircle(20, hy0 - 95, 14, paint(S["jewel"], al)); c.drawCircle(20, hy0 - 95, 14, paint(INK, al, stroke=2.5))
        if S["plume"]:
            pl = skia.Path(); pl.moveTo(18, hy0 - 105); pl.cubicTo(-10, hy0 - 190, -60, hy0 - 200, -70, hy0 - 170); pl.cubicTo(-30, hy0 - 165, 0, hy0 - 140, 18, hy0 - 105)
            c.save(); c.rotate(math.sin(t * 3 + seed) * 4); _fill(c, pl, S["plume"], al, w=2); c.restore()
    elif hd == "helmet":
        hm = skia.Path(); hm.moveTo(-90, hy0 - 30); hm.cubicTo(-100, hy0 - 170, 100, hy0 - 170, 90, hy0 - 30); hm.close(); _fill(c, hm, S["hc"], al)
        for i in range(-3, 4): c.drawLine(i * 24, hy0 - 140 + abs(i) * 6, i * 30, hy0 - 32, paint(S["hc2"], al, stroke=4))
        _fill(c, _p([(-92, hy0 - 44), (92, hy0 - 44), (92, hy0 - 24), (-92, hy0 - 24)]), S["hc2"], al)
        _fill(c, _p([(-6, hy0 - 150), (6, hy0 - 150), (3, hy0 - 205), (-3, hy0 - 205)]), "#8A6A12", al, w=2)
        pl = skia.Path(); pl.moveTo(0, hy0 - 200); pl.cubicTo(-20, hy0 - 250, -70, hy0 - 255, -80, hy0 - 225); pl.cubicTo(-40, hy0 - 222, -15, hy0 - 210, 0, hy0 - 200)
        c.save(); c.rotate(math.sin(t * 3 + seed) * 4); _fill(c, pl, S["plume"], al, w=2); c.restore()
    elif hd == "crown":
        cr = _p([(-88, hy0 - 40), (-92, hy0 - 120), (-55, hy0 - 90), (-25, hy0 - 140), (0, hy0 - 95), (25, hy0 - 140), (55, hy0 - 90), (92, hy0 - 120), (88, hy0 - 40)])
        _fill(c, cr, S["hc"], al); _fill(c, _p([(-90, hy0 - 52), (90, hy0 - 52), (90, hy0 - 36), (-90, hy0 - 36)]), S["hc2"], al)
        for x in (-50, 0, 50): c.drawCircle(x, hy0 - 70, 9, paint(S["jewel"], al))
    c.restore()
    c.restore()

# ---------------------------------------------------------------- real painting card (cover-fit crop) with name plate
_CROP = {}
def crop_img(img, box):
    key = (id(img), box)
    if key not in _CROP:
        W, H = img.width(), img.height(); r = skia.Rect(box[0] * W, box[1] * H, box[2] * W, box[3] * H)
        s = skia.Surface(int(r.width()), int(r.height())); cc = s.getCanvas(); cc.drawImageRect(img, r, skia.Rect(0, 0, r.width(), r.height()), SAMP)
        _CROP[key] = (s.makeImageSnapshot(), img)
    return _CROP[key][0]

def portrait_card(c, img, box, x0, y0, x1, y1, k, t, name, note, col="#D4AF37", tilt=0.0):
    """framed real painting that swings in (3D-ish: scale + slight rotation) with a gold frame, sheen and name plate."""
    if k <= 0: return
    im = crop_img(img, box); kk = back(clamp(k)); al = int(255 * clamp(k * 2.5))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c.save(); c.translate(cx, cy); c.rotate(tilt * (1 - clamp(k)) * 12 + tilt * 1.2); c.scale(lerp(0.7, 1.0, kk), lerp(0.7, 1.0, kk)); c.translate(-cx, -cy)
    rrect(c, x0 - 14, y0 - 14, x1 + 14, y1 + 14, 10, "#1B1410", al, shadow=22)
    c.drawRect(skia.Rect(x0 - 8, y0 - 8, x1 + 8, y1 + 8), paint(col, al, stroke=6)); c.drawRect(skia.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2), paint("#FFF1C2", int(al * 0.6), stroke=1.5))
    iw, ih = im.width(), im.height(); sc = max((x1 - x0) / iw, (y1 - y0) / ih)
    c.save(); c.clipRect(skia.Rect(x0, y0, x1, y1))
    zw, zh = iw * sc * (1 + 0.04 * clamp(k)), ih * sc * (1 + 0.04 * clamp(k))                     # slow push-in
    draw_img(c, im, cx - zw / 2, cy - zh / 2, cx + zw / 2, cy + zh / 2, al)
    sh = ((t * 0.35) % 1.6) - 0.3                                                                 # gold sheen sweep
    if 0 < sh < 1:
        sx = x0 + (x1 - x0) * sh; g = skia.GradientShader.MakeLinear([(sx - 90, y0), (sx + 90, y1)], [hexc("#FFFFFF", 0), hexc("#FFFFFF", 70), hexc("#FFFFFF", 0)])
        c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=g))
    c.restore()
    pw = min(text_w(name, 40, SERIF_DISPLAY) + 50, (x1 - x0) + 20); py = y0 - 6
    rrect(c, cx - pw / 2, py - 30, cx + pw / 2, py + 26, 10, "#7A1F1F", al, shadow=8); c.drawRect(skia.Rect(cx - pw / 2 + 4, py - 26, cx + pw / 2 - 4, py + 22), paint(col, al, stroke=2))
    text(c, name, cx, py + 13, 40 if text_w(name, 40, SERIF_DISPLAY) + 50 <= pw else 40 * (pw - 50) / text_w(name, 40, SERIF_DISPLAY), "#FFF1C2", SERIF_DISPLAY, "c", al)
    c.restore()
    if note: text(c, note, cx, y0 + 50, 19, "#FFFFFF", FT_SEMI, "c", int(al * 0.95), shadow=True)

def vs_badge(c, x, y, k, t):
    if k <= 0: return
    s = back(clamp(k)) * (1 + 0.04 * math.sin(t * 6))
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-8)
    c.drawCircle(0, 0, 62, paint("#000000", 120, blur=12)); c.drawCircle(0, 0, 56, paint("#C1121F")); c.drawCircle(0, 0, 56, paint("#FFD23F", 255, stroke=5))
    text(c, "VS", 0, 20, 54, "#FFFFFF", FT_BLACK, "c"); c.restore()

# ---------------------------------------------------------------- premium timeline (glass panel, glowing progress, ripples, rolling year)
def _roll_year(c, y, cx, cy, size, col, a):
    lo = int(math.floor(y)); hi = lo + 1; f = ease_io(y - lo); s0, s1 = str(lo), str(hi)
    f_ = font(FT_BLACK, size); w = f_.measureText(s0); x = cx - w / 2
    c.save(); c.clipRect(skia.Rect(cx - w, cy - size * 0.92, cx + w, cy + size * 0.18))
    for i, ch in enumerate(s0):
        ch1 = s1[i] if i < len(s1) else ch; cw = f_.measureText(ch)
        if ch1 != ch and f > 0.001:
            c.drawString(ch, x, cy - f * size * 1.05, f_, paint(col, a)); c.drawString(ch1, x, cy + (1 - f) * size * 1.05, f_, paint(col, a))
        else: c.drawString(ch, x, cy, f_, paint(col, a))
        x += cw
    c.restore()

def premium_timeline(c, t, k, year, nodes, xmap, y=1222, x0=110, x1=970, t_on=0.0):
    """nodes = [(year, label, sub)]; xmap(year) -> x."""
    if k <= 0: return
    al = int(255 * clamp(k * 1.6)); up = (1 - ease_out(clamp(k))) * 60
    c.save(); c.translate(0, up)
    # glass panel
    r = skia.Rect(x0 - 50, y - 108, x1 + 50, y + 92)
    c.drawRoundRect(r.makeOffset(0, 10), 34, 34, paint("#000000", int(al * 0.45), blur=22))
    g = skia.GradientShader.MakeLinear([(0, r.top()), (0, r.bottom())], [hexc("#1A2740", int(al * 0.82)), hexc("#0B1220", int(al * 0.9))])
    c.drawRoundRect(r, 34, 34, skia.Paint(Shader=g, AntiAlias=True))
    c.drawRoundRect(r, 34, 34, paint("#FFD166", int(al * 0.35), stroke=2)); c.drawRoundRect(r.makeInset(4, 4), 30, 30, paint("#FFFFFF", int(al * 0.08), stroke=1.5))
    # track + glowing progress + travelling sheen
    xp = xmap(year)
    c.drawRoundRect(skia.Rect(x0, y - 3, x1, y + 3), 3, 3, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 7, xp, y + 7), 7, 7, paint("#FFB703", int(al * 0.5), blur=8))
    gg = skia.GradientShader.MakeLinear([(x0, 0), (max(x0 + 1, xp), 0)], [hexc("#E9A400", al), hexc("#FFE08A", al)])
    c.drawRoundRect(skia.Rect(x0, y - 4, xp, y + 4), 4, 4, skia.Paint(Shader=gg, AntiAlias=True))
    sh = x0 + ((t * 260) % max(1, xp - x0 + 120)) - 60
    if sh < xp: c.drawCircle(sh, y, 10, paint("#FFFFFF", int(al * 0.55), blur=6))
    # nodes: pop in one by one, ripple when the year reaches them
    for i, (yr, lab, sub) in enumerate(nodes):
        x = xmap(yr); nk = seg(k, 0.15 + i * 0.1, 0.45 + i * 0.1); reached = year >= yr - 0.5 if True else False
        on = abs(yr - year) < 6
        if nk <= 0: continue
        rad = (14 if on else 9) * back(nk)
        if reached: c.drawCircle(x, y, rad + 6, paint("#FFB703", int(al * 0.45), blur=6))
        c.drawCircle(x, y, rad, paint("#FFD166" if reached else "#3E5068", al)); c.drawCircle(x, y, rad, paint("#FFFFFF", int(al * 0.7), stroke=2))
        if on:
            rp = (t * 0.9) % 1.0; c.drawCircle(x, y, rad + 8 + rp * 26, paint("#FFD166", int(al * 0.6 * (1 - rp)), stroke=3))
        text(c, lab, x, y + 46, 28 if on else 22, "#FFFFFF" if on else "#9FB0C6", FT_BLACK if on else FT_SEMI, "c", int(al * nk))
        text(c, sub, x, y + 72, 17, "#FFD166" if on else "#7F90A6", FT_SEMI, "c", int(al * nk))
    # year pill with pointer and rolling digits
    pw, ph = 150, 58; py = y - 60
    c.drawRoundRect(skia.Rect(xp - pw / 2, py - ph / 2 + 6, xp + pw / 2, py + ph / 2 + 6), 29, 29, paint("#000000", int(al * 0.4), blur=8))
    c.drawPath(_p([(xp - 10, py + ph / 2 - 2), (xp + 10, py + ph / 2 - 2), (xp, py + ph / 2 + 12)]), paint("#FFD166", al))
    gp = skia.GradientShader.MakeLinear([(0, py - ph / 2), (0, py + ph / 2)], [hexc("#FFE59A", al), hexc("#F4B400", al)])
    c.drawRoundRect(skia.Rect(xp - pw / 2, py - ph / 2, xp + pw / 2, py + ph / 2), 29, 29, skia.Paint(Shader=gp, AntiAlias=True))
    _roll_year(c, year, xp, py + 15, 40, "#0F1B2D", al)
    c.restore()
