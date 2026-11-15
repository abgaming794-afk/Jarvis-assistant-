"""Flat 2D icons + widgets for the AMRIT BORI documentary (skia, design space 1920x1080)."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import math, json, os
import skia
from PIL import Image
from core import *

FLAGS = MAPDATA + "flags/"
_FL = {}
# (focus x, focus y, crop size as fraction of flag height)
FLAG_FOCUS = {"cn": (0.24, 0.36, 0.78), "us": (0.22, 0.27, 0.62), "kp": (0.36, 0.5, 1.0), "pk": (0.62, 0.5, 1.0), "sa": (0.5, 0.45, 0.9),
              "au": (0.25, 0.25, 0.62), "gb": (0.5, 0.5, 1.0), "in": (0.5, 0.5, 1.0), "ir": (0.5, 0.5, 1.0), "il": (0.5, 0.5, 1.0)}
def flag_img(code):
    if code not in _FL: _FL[code] = sk_image(Image.open(FLAGS + code + ".png"))
    return _FL[code]

def flag_circle(c, code, cx, cy, r, ring="#F1FAEE", a=255, k=1.0):
    if k <= 0: return
    r *= k
    c.drawCircle(cx + 4, cy + 8, r + 6, paint("#000000", int(110 * a / 255), blur=10))
    c.drawCircle(cx, cy, r + 6, paint(ring, a))
    img = flag_img(code); iw, ih = img.width(), img.height()
    # crop a square window around the flag's emblem so the symbol sits in the middle of the circle
    fx, fy, fs = FLAG_FOCUS.get(code, (0.5, 0.5, 1.0))
    side = ih * fs; sx = min(max(fx * iw - side / 2, 0), iw - side); sy = min(max(fy * ih - side / 2, 0), ih - side)
    c.save(); p = skia.Path(); p.addCircle(cx, cy, r); c.clipPath(p, doAntiAlias=True)
    draw_img(c, img, cx - r, cy - r, cx + r, cy + r, a, src=skia.Rect(sx, sy, sx + side, sy + side)); c.restore()

def flag_rect(c, code, x, y, h, a=255):
    img = flag_img(code); w = img.width() * h / img.height()
    rrect(c, x - 3, y - 3, x + w + 3, y + h + 3, 6, "#F1FAEE", a, shadow=8)
    draw_img(c, img, x, y, x + w, y + h, a); return w

# ------------------------------------------------------------------ icons (centered at x,y, size s ~ height)
def ic_factory(c, x, y, s, t=0, col="#C9D1DC", a=255):
    k = s / 100
    p = skia.Path(); p.moveTo(x - 50 * k, y + 40 * k); p.lineTo(x - 50 * k, y - 5 * k); p.lineTo(x - 20 * k, y + 12 * k)
    p.lineTo(x - 20 * k, y - 5 * k); p.lineTo(x + 10 * k, y + 12 * k); p.lineTo(x + 10 * k, y - 5 * k); p.lineTo(x + 50 * k, y + 15 * k)
    p.lineTo(x + 50 * k, y + 40 * k); p.close(); c.drawPath(p, paint(col, a))
    c.drawRect(skia.Rect(x + 28 * k, y - 45 * k, x + 42 * k, y + 5 * k), paint(col, a))
    for i in range(3): c.drawRect(skia.Rect(x - 40 * k + i * 28 * k, y + 20 * k, x - 28 * k + i * 28 * k, y + 32 * k), paint("#0F1B2D", a))
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1
        c.drawCircle(x + 35 * k + ph * 25 * k, y - 50 * k - ph * 40 * k, (8 + ph * 12) * k, paint("#8A9BB0", int(a * (1 - ph) * 0.8)))

def ic_coins(c, x, y, s, n=4, col="#FFD166", a=255):
    k = s / 100
    for i in range(n):
        yy = y + 30 * k - i * 16 * k
        c.drawOval(skia.Rect(x - 34 * k, yy - 10 * k, x + 34 * k, yy + 10 * k), paint("#C9971E", a))
        c.drawOval(skia.Rect(x - 34 * k, yy - 16 * k, x + 34 * k, yy + 4 * k), paint(col, a))
    text(c, "$", x, y + 34 * k - n * 16 * k + 2 * k, 26 * k, "#8A6512", FT_BLACK, "c", a)

def ic_chip(c, x, y, s, t=0, a=255):
    k = s / 100
    for i in range(4):
        for sgn in (-1, 1):
            c.drawRect(skia.Rect(x - 30 * k + i * 18 * k, y + sgn * 34 * k - 6 * k, x - 24 * k + i * 18 * k, y + sgn * 34 * k + 6 * k), paint("#8A9BB0", a))
            c.drawRect(skia.Rect(x + sgn * 34 * k - 6 * k, y - 30 * k + i * 18 * k, x + sgn * 34 * k + 6 * k, y - 24 * k + i * 18 * k), paint("#8A9BB0", a))
    rrect(c, x - 30 * k, y - 30 * k, x + 30 * k, y + 30 * k, 6 * k, "#2E4A6B", a)
    glow = 0.5 + 0.5 * math.sin(t * 6)
    rrect(c, x - 16 * k, y - 16 * k, x + 16 * k, y + 16 * k, 4 * k, "#4FC3F7", int(a * (0.5 + 0.5 * glow)))

def ic_warhead(c, x, y, s, col="#C9D1DC", a=255):
    k = s / 100
    p = skia.Path(); p.moveTo(x, y - 48 * k); p.cubicTo(x + 26 * k, y - 30 * k, x + 22 * k, y + 10 * k, x + 20 * k, y + 30 * k)
    p.lineTo(x - 20 * k, y + 30 * k); p.cubicTo(x - 22 * k, y + 10 * k, x - 26 * k, y - 30 * k, x, y - 48 * k); p.close()
    c.drawPath(p, paint(col, a))
    for sgn in (-1, 1):
        f = skia.Path(); f.moveTo(x + sgn * 20 * k, y + 14 * k); f.lineTo(x + sgn * 36 * k, y + 44 * k); f.lineTo(x + sgn * 18 * k, y + 36 * k); f.close()
        c.drawPath(f, paint(PAL["axis"], a))
    c.drawCircle(x, y - 4 * k, 11 * k, paint("#FFD166", a))
    for i in range(3):
        c.save(); c.translate(x, y - 4 * k); c.rotate(i * 120)
        q = skia.Path(); q.moveTo(0, 0); q.arcTo(skia.Rect(-10 * k, -10 * k, 10 * k, 10 * k), -120, 60, False); q.close()
        c.drawPath(q, paint("#0F1B2D", a)); c.restore()

def ic_barrel(c, x, y, s, col="#2C5DAA", a=255):
    k = s / 100
    rrect(c, x - 28 * k, y - 40 * k, x + 28 * k, y + 40 * k, 10 * k, col, a)
    for yy in (-22, 0, 22): c.drawRect(skia.Rect(x - 28 * k, y + yy * k - 3 * k, x + 28 * k, y + yy * k + 3 * k), paint("#0F1B2D", int(a * 0.5)))
    d = skia.Path(); d.moveTo(x, y - 14 * k); d.cubicTo(x + 9 * k, y - 2 * k, x + 9 * k, y + 8 * k, x, y + 9 * k); d.cubicTo(x - 9 * k, y + 8 * k, x - 9 * k, y - 2 * k, x, y - 14 * k)
    c.drawPath(d, paint("#111111", a))

def ic_flame(c, x, y, s, t=0, a=255):
    k = s / 100; f = 1 + 0.08 * math.sin(t * 12)
    for col, sc in (("#FF7A00", 1.0), ("#FFD166", 0.6)):
        p = skia.Path(); h = 46 * k * sc * f; w = 24 * k * sc
        p.moveTo(x, y - h); p.cubicTo(x + w, y - h * 0.3, x + w, y + h * 0.5, x, y + h * 0.55); p.cubicTo(x - w, y + h * 0.5, x - w, y - h * 0.3, x, y - h)
        c.drawPath(p, paint(col, a))

def ic_drone(c, x, y, s, ang=0, col="#C9D1DC", a=255):
    k = s / 100
    c.save(); c.translate(x, y); c.rotate(ang)
    p = skia.Path(); p.moveTo(48 * k, 0); p.lineTo(-30 * k, -40 * k); p.lineTo(-18 * k, 0); p.lineTo(-30 * k, 40 * k); p.close()
    c.drawPath(p, paint(col, a)); c.drawPath(p, paint("#0F1B2D", a, stroke=2 * k))
    c.drawRect(skia.Rect(-34 * k, -5 * k, -22 * k, 5 * k), paint("#5B6E8C", a)); c.restore()

def ic_shell(c, x, y, s, col="#D4A73C", a=255):
    k = s / 100
    p = skia.Path(); p.moveTo(x, y - 46 * k); p.cubicTo(x + 16 * k, y - 30 * k, x + 15 * k, y - 14 * k, x + 15 * k, y - 4 * k)
    p.lineTo(x + 15 * k, y + 40 * k); p.lineTo(x - 15 * k, y + 40 * k); p.lineTo(x - 15 * k, y - 4 * k); p.cubicTo(x - 15 * k, y - 14 * k, x - 16 * k, y - 30 * k, x, y - 46 * k); p.close()
    c.drawPath(p, paint(col, a)); c.drawRect(skia.Rect(x - 15 * k, y + 30 * k, x + 15 * k, y + 40 * k), paint("#8A6512", a))
    c.drawRect(skia.Rect(x - 15 * k, y - 6 * k, x + 15 * k, y), paint("#8A6512", a))

def ic_missile(c, x, y, s, ang=-45, col="#E8E2D0", a=255, flame=True, t=0):
    k = s / 100
    c.save(); c.translate(x, y); c.rotate(ang)
    if flame: ic_flame(c, -58 * k, 0, 30 * k, t, a) if False else None
    p = skia.Path(); p.moveTo(50 * k, 0); p.lineTo(30 * k, -9 * k); p.lineTo(-40 * k, -9 * k); p.lineTo(-40 * k, 9 * k); p.lineTo(30 * k, 9 * k); p.close()
    c.drawPath(p, paint(col, a))
    for sgn in (-1, 1):
        f = skia.Path(); f.moveTo(-26 * k, sgn * 9 * k); f.lineTo(-44 * k, sgn * 26 * k); f.lineTo(-40 * k, sgn * 9 * k); f.close(); c.drawPath(f, paint(PAL["axis"], a))
    if flame:
        fl = skia.Path(); L = 26 + 6 * math.sin(t * 20)
        fl.moveTo(-40 * k, -7 * k); fl.lineTo(-(40 + L) * k, 0); fl.lineTo(-40 * k, 7 * k); fl.close(); c.drawPath(fl, paint("#FF9F1C", a))
    c.restore()

def ic_soldier(c, x, y, s, t=0, col="#C9D1DC", a=255, walk=True):
    k = s / 100; sw = math.sin(t * 9) if walk else 0
    c.drawCircle(x, y - 38 * k, 11 * k, paint(col, a))
    c.drawRoundRect(skia.Rect(x - 16 * k, y - 50 * k, x + 16 * k, y - 40 * k), 6 * k, 6 * k, paint("#4B5D3A", a))   # helmet
    c.drawRoundRect(skia.Rect(x - 12 * k, y - 26 * k, x + 12 * k, y + 8 * k), 6 * k, 6 * k, paint("#4B5D3A", a))
    for sgn in (-1, 1):
        c.drawLine(x + sgn * 6 * k, y + 8 * k, x + sgn * 6 * k + sw * sgn * 10 * k, y + 40 * k, paint(col, a, stroke=8 * k, cap_round=True))
    c.drawLine(x + 10 * k, y - 18 * k, x + 22 * k, y - 34 * k, paint("#222222", a, stroke=5 * k, cap_round=True))   # rifle

def ic_train(c, x, y, s, a=255, col="#9B1B30"):
    k = s / 100
    rrect(c, x - 50 * k, y - 22 * k, x + 50 * k, y + 16 * k, 6 * k, col, a)
    c.drawRect(skia.Rect(x + 20 * k, y - 40 * k, x + 50 * k, y - 22 * k), paint(col, a))
    for i in range(3): c.drawCircle(x - 32 * k + i * 32 * k, y + 22 * k, 9 * k, paint("#222", a))

def ic_ship(c, x, y, s, col="#C9D1DC", a=255):
    k = s / 100
    p = skia.Path(); p.moveTo(x - 50 * k, y); p.lineTo(x + 50 * k, y); p.lineTo(x + 38 * k, y + 20 * k); p.lineTo(x - 42 * k, y + 20 * k); p.close()
    c.drawPath(p, paint(col, a))
    c.drawRect(skia.Rect(x - 30 * k, y - 18 * k, x + 4 * k, y), paint("#E63946", a))
    c.drawRect(skia.Rect(x + 8 * k, y - 26 * k, x + 28 * k, y), paint("#F1FAEE", a))

def ic_warehouse(c, x, y, s, open_k=0, a=255):
    k = s / 100
    p = skia.Path(); p.moveTo(x - 60 * k, y - 10 * k); p.lineTo(x, y - 50 * k); p.lineTo(x + 60 * k, y - 10 * k); p.close()
    c.drawPath(p, paint("#5B6E8C", a)); c.drawRect(skia.Rect(x - 55 * k, y - 10 * k, x + 55 * k, y + 50 * k), paint("#3E5068", a))
    c.drawRect(skia.Rect(x - 35 * k, y + 2 * k, x + 35 * k, y + 50 * k), paint("#0F1B2D", a))
    for i in range(5): ic_shell(c, x - 24 * k + i * 12 * k, y + 32 * k, 30 * k, a=a)
    w = 35 * k * (1 - open_k)
    c.drawRect(skia.Rect(x - 35 * k, y + 2 * k, x - 35 * k + w, y + 50 * k), paint("#7A8BA3", a))
    c.drawRect(skia.Rect(x + 35 * k - w, y + 2 * k, x + 35 * k, y + 50 * k), paint("#7A8BA3", a))

def ic_document(c, x, y, s, a=255, title=""):
    k = s / 100
    rrect(c, x - 34 * k, y - 44 * k, x + 34 * k, y + 44 * k, 5 * k, "#F4F1EA", a, shadow=8)
    for i in range(6): c.drawRect(skia.Rect(x - 24 * k, y - 26 * k + i * 11 * k, x + (24 - (i % 3) * 8) * k, y - 22 * k + i * 11 * k), paint("#8A9BB0", a))
    if title: text(c, title, x, y - 32 * k, 12 * k, "#0F1B2D", FT_BLACK, "c", a)

def ic_un_table(c, x, y, s, hl=None, a=255):
    k = s / 100
    c.drawCircle(x, y, 60 * k, paint("#2E4A6B", a)); c.drawCircle(x, y, 36 * k, paint(PAL["ocean"], a))
    for i in range(5):
        ang = math.radians(-90 + i * 72); sx, sy = x + 72 * k * math.cos(ang), y + 72 * k * math.sin(ang)
        c.drawCircle(sx, sy, 14 * k, paint("#FFD166" if hl == i else "#8A9BB0", a))
    text(c, "UNSC", x, y + 8 * k, 22 * k, "#C9D1DC", FT_BLACK, "c", a)

def stamp(c, s, x, y, size, col, k, ang=-8, a=255):
    if k <= 0: return
    sc = lerp(1.9, 1.0, ease_in(clamp(k))); al = int(a * clamp(k * 1.6))
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(sc, sc)
    w = text_w(s, size)
    c.drawRoundRect(skia.Rect(-w / 2 - size * 0.5, -size * 0.9, w / 2 + size * 0.5, size * 0.6), 12, 12, paint(col, al, stroke=size * 0.11))
    text(c, s, 0, size * 0.08, size, col, FT_BLACK, "c", al); c.restore()

def ic_chain(c, x0, y0, x1, y1, k, col="#C9D1DC", a=255, broken=0):
    n = 7; L = math.hypot(x1 - x0, y1 - y0); ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    c.save(); c.translate(x0, y0); c.rotate(ang)
    for i in range(int(n * clamp(k))):
        cx = (i + 0.5) * L / n
        if broken and i == n // 2: continue
        rr = skia.Rect(cx - L / n * 0.6, -12, cx + L / n * 0.6, 12)
        c.drawRoundRect(rr, 12, 12, paint(col, a, stroke=6))
    c.restore()

def ic_scale(c, x, y, s, tilt=0, a=255):
    k = s / 100
    c.drawLine(x, y - 40 * k, x, y + 50 * k, paint("#C9D1DC", a, stroke=6 * k)); c.drawRect(skia.Rect(x - 30 * k, y + 46 * k, x + 30 * k, y + 54 * k), paint("#C9D1DC", a))
    c.save(); c.translate(x, y - 40 * k); c.rotate(tilt)
    c.drawLine(-70 * k, 0, 70 * k, 0, paint("#C9D1DC", a, stroke=6 * k, cap_round=True))
    for sgn in (-1, 1):
        px = sgn * 66 * k
        c.save(); c.translate(px, 0); c.rotate(-tilt)
        c.drawLine(0, 0, -20 * k, 40 * k, paint("#8A9BB0", a, stroke=2 * k)); c.drawLine(0, 0, 20 * k, 40 * k, paint("#8A9BB0", a, stroke=2 * k))
        c.drawOval(skia.Rect(-28 * k, 36 * k, 28 * k, 48 * k), paint("#FFD166", a)); c.restore()
    c.restore()

def ic_question(c, x, y, s, a=255, col="#FFD166"):
    text(c, "?", x, y + s * 0.35, s, col, FT_BLACK, "c", a, shadow=True)

def ic_mine(c, x, y, s, t=0, a=255):
    k = s / 100
    for i in range(8):
        ang = i * math.pi / 4
        c.drawLine(x + 26 * k * math.cos(ang), y + 26 * k * math.sin(ang), x + 40 * k * math.cos(ang), y + 40 * k * math.sin(ang), paint("#5B6E8C", a, stroke=7 * k, cap_round=True))
    c.drawCircle(x, y, 28 * k, paint("#3E5068", a)); c.drawCircle(x - 8 * k, y - 8 * k, 7 * k, paint("#8A9BB0", a))
    c.drawCircle(x, y, 5 * k, paint(PAL["axis"], int(a * (0.5 + 0.5 * math.sin(t * 8)))))

# ------------------------------------------------------------------ layout widgets
def chapter_card(c, t, t0, num, title, dur=1.6):
    """Ink-flash chapter card. Returns nothing; draws full-screen."""
    lt = t - t0
    c.clear(hexc(PAL["ocean"]))
    k = ease_out(seg(lt, 0, 0.45))
    # ink splash: big blobby circle growing
    rng = [(0.31, 0.2, 1.0), (0.62, 0.62, 0.8), (0.45, 0.8, 0.7), (0.75, 0.25, 0.6), (0.2, 0.7, 0.55)]
    for i, (fx, fy, fr) in enumerate(rng):
        kk = ease_out(seg(lt, i * 0.05, 0.4 + i * 0.05))
        c.drawCircle(fx * DW, fy * DH, 900 * fr * kk, paint(PAL["axis"] if i % 2 == 0 else "#B3202C", 255))
    c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(200 * ease_io(seg(lt, 0.35, 0.7)))))
    kt = back(seg(lt, 0.3, 0.75))
    if kt > 0:
        c.save(); c.translate(960, 540); c.scale(lerp(1.15, 1.0, kt), lerp(1.15, 1.0, kt))
        text(c, f"CHAPTER {num}", 0, -60, 54, PAL["yel"], FT_BLACK, "c", int(255 * clamp(kt)))
        text(c, title, 0, 60, 120, "#F1FAEE", FT_BLACK, "c", int(255 * clamp(kt)), shadow=True)
        w = text_w(title, 120)
        c.drawRect(skia.Rect(-w / 2 * ease_out(seg(lt, 0.6, 1.0)), 92, w / 2 * ease_out(seg(lt, 0.6, 1.0)), 100), paint(PAL["axis"]))
        c.restore()

def stat_card(c, x, y, w, h, big, label, k, col=PAL["yel"], tag=None, sub=None, a=255):
    if k <= 0: return
    kk = back(k); al = int(a * clamp(k * 1.5))
    c.save(); c.translate(x + w / 2, y + h / 2); c.scale(kk, kk); c.translate(-(x + w / 2), -(y + h / 2))
    rrect(c, x, y, x + w, y + h, 22, "#16223A", al, shadow=20)
    c.drawRoundRect(skia.Rect(x, y, x + w, y + h), 22, 22, paint(col, al, stroke=3))
    fit = lambda s_, size, fp: min(size, size * (w - 50) / max(1, text_w(s_, size, fp)))
    text(c, big, x + w / 2, y + h * 0.52, fit(big, h * 0.38, FT_BLACK), col, FT_BLACK, "c", al)
    text(c, label, x + w / 2, y + h * 0.78, fit(label, h * 0.12, FT_SEMI), "#F1FAEE", FT_SEMI, "c", al)
    if sub: text(c, sub, x + w / 2, y + h * 0.92, fit(sub, h * 0.085, FT_SEMI), PAL["muted"], FT_SEMI, "c", al)
    if tag: pill(c, tag, x + w - 90, y + 6, 22, PAL["yel"], fg="#0F1B2D", a=al, shadow=0)
    c.restore()

def counter_text(v0, v1, k, fmt="{:.0f}"):
    return fmt.format(lerp(v0, v1, ease_out(k)))

def quote_card(c, x, y, w, lines, who, k, t, hl_line=None, hl_k=0):
    if k <= 0: return
    al = int(255 * clamp(k * 1.5)); dy = (1 - ease_out(k)) * 60
    h = 120 + 70 * len(lines)
    rrect(c, x, y + dy, x + w, y + dy + h, 24, "#F4F1EA", al, shadow=26)
    text(c, "“", x + 40, y + dy + 110, 160, PAL["axis"], FT_BLACK, "l", al)
    for i, ln in enumerate(lines):
        yy = y + dy + 110 + i * 70
        if hl_line is not None and i in (hl_line if isinstance(hl_line, (list, tuple)) else [hl_line]):
            ww = text_w(ln, 48, FT_SEMI)
            hp = paint("#FFD166", int(200 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(x + 130, yy - 44, x + 130 + ww * ease_out(hl_k), yy + 14), hp)
        text(c, ln, x + 130, yy, 48, "#0F1B2D", FT_SEMI, "l", al)
    text(c, who, x + w - 40, y + dy + h - 30, 28, "#5B6472", FT_SEMI, "r", al)

def route(c, pts, k, col="#FFD166", w=6, dash=True, a=255, head=True):
    """pts in screen coords; draws progressively k in 0..1"""
    if k <= 0 or len(pts) < 2: return None
    path = skia.Path(); path.moveTo(*pts[0])
    if len(pts) == 3: path.quadTo(*pts[1], *pts[2])
    else:
        for p in pts[1:]: path.lineTo(*p)
    pm = skia.PathMeasure(path, False); L = pm.getLength()
    sp = skia.Path(); pm.getSegment(0, L * clamp(k), sp, True)
    pt = paint(col, a, stroke=w, cap_round=True)
    if dash: pt.setPathEffect(skia.DashPathEffect.Make([18, 12], 0))
    c.drawPath(sp, paint("#000000", int(a * 0.35), stroke=w + 4, cap_round=True)); c.drawPath(sp, pt)
    pos, tan = pm.getPosTan(L * clamp(k))
    if head and k < 0.999 or head:
        hx, hy, tx, ty = pos.x(), pos.y(), tan.x(), tan.y(); s = w * 3.2
        hp = skia.Path(); hp.moveTo(hx + tx * s, hy + ty * s); hp.lineTo(hx - tx * s + ty * s * 0.8, hy - ty * s - tx * s * 0.8)
        hp.lineTo(hx - tx * s - ty * s * 0.8, hy - ty * s + tx * s * 0.8); hp.close(); c.drawPath(hp, paint(col, a))
    return pm, L

def along(pm, L, f):
    pos, tan = pm.getPosTan(L * clamp(f)); return pos.x(), pos.y(), math.degrees(math.atan2(tan.y(), tan.x()))

def pin(c, x, y, label, k, col=PAL["yel"], a=255, size=40, side="r", t=0):
    if k <= 0: return
    kk = back(k, 2.0); al = int(a * clamp(k * 1.5))
    rp = (t % 0.9) / 0.9
    c.drawCircle(x, y, 10 + 40 * rp, paint(col, int(al * (1 - rp) * 0.8), stroke=4))
    c.drawCircle(x, y - (1 - kk) * 50, 11, paint(col, al)); c.drawCircle(x, y - (1 - kk) * 50, 11, paint(PAL["ocean"], al, stroke=4))
    if label:
        w = text_w(label, size) + 36
        x0 = x + 26 if side == "r" else x - 26 - w
        rrect(c, x0, y - size * 0.95, x0 + w, y + size * 0.55, 12, PAL["ocean"], al, shadow=10)
        c.drawRoundRect(skia.Rect(x0, y - size * 0.95, x0 + w, y + size * 0.55), 12, 12, paint(col, al, stroke=3))
        text(c, label, x0 + 18, y + size * 0.2, size, "#F1FAEE", FT_BLACK, "l", al)

def bars(c, x, y, w, h, items, k, maxv, unit="", a=255):
    """items: list of (label, value, colour, flagcode or None) horizontal bars"""
    n = len(items); bh = h / n * 0.62
    for i, (lab, v, col, fc) in enumerate(items):
        kk = ease_out(seg(k, i * 0.15, 0.7 + i * 0.15))
        yy = y + i * h / n
        if fc: flag_circle(c, fc, x - 70 - bh * 0.42, yy + bh / 2, bh * 0.42, a=a)
        text(c, lab, x + 10, yy - 12, 30, "#F1FAEE", FT_SEMI, "l", a)
        rrect(c, x, yy, x + w, yy + bh, bh / 2, "#22304A", a)
        if kk > 0:
            rrect(c, x, yy, x + w * v / maxv * kk, yy + bh, bh / 2, col, a)
            text(c, f"{v * kk:.1f}{unit}" if isinstance(v, float) and v < 10 else f"{v * kk:.0f}{unit}", x + w * v / maxv * kk + 16, yy + bh * 0.72, bh * 0.6, "#F1FAEE", FT_BLACK, "l", a)

def split_says(c, k, left, right, lflag, rflag, t):
    if k <= 0: return
    for i, (lab, txt_, fc, col) in enumerate(((left[0], left[1], lflag, PAL["IRN"]), (right[0], right[1], rflag, "#3C6FD8"))):
        kk = ease_out(seg(k, i * 0.25, 0.6 + i * 0.25))
        if kk <= 0: continue
        x0 = 120 + i * 860; dy = (1 - kk) * 80
        rrect(c, x0, 200 + dy, x0 + 820, 760 + dy, 26, "#16223A", int(255 * kk), shadow=22)
        c.drawRoundRect(skia.Rect(x0, 200 + dy, x0 + 820, 760 + dy), 26, 26, paint(col, int(255 * kk), stroke=4))
        flag_circle(c, fc, x0 + 110, 310 + dy, 60, a=int(255 * kk))
        text(c, lab, x0 + 200, 330 + dy, 54, col if i == 0 else "#7FA6E8", FT_BLACK, "l", int(255 * kk))
        for j, ln in enumerate(txt_):
            text(c, ln, x0 + 60, 470 + dy + j * 70, 46, "#F1FAEE", FT_SEMI, "l", int(255 * kk))
    kv = back(seg(k, 0.5, 0.8))
    if kv > 0:
        c.drawCircle(960, 480, 60 * kv, paint(PAL["axis"])); text(c, "VS", 960, 500, 44 * kv, "#F1FAEE", FT_BLACK, "c")
