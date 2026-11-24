"""2D cartoon battle kit (skia) - Unexplored Truth by Amrit 1.2.0.

Cartoon soldiers built on the channel's own 2D man design (round head, rounded body, stick legs) in period costumes,
riders on horses, a king on an elephant, arrow volleys, dust, sparks, and a Battle choreographer:
approach -> arrow volley -> clash (camera zoom + shake) -> melee -> rout (losers flee / fall) -> winners cheer.
Cartoon, no blood. Draw it over a photoreal background with battle_bg(). Design space DWxDH from core.py.
"""
import math
import numpy as np
import skia
from PIL import Image, ImageFilter, ImageEnhance
from core import *

# ------------------------------------------------------------------ factions (costume palettes)
FAC = {
    "arab":      dict(tunic="#E9E4D8", armor="#8E9AA6", head="turban", head_col="#F4F1EA", shield="#6B4F2A", skin="#C99A6B", banner="#FFFFFF", weapon="sword"),
    "arab_gen":  dict(tunic="#9B2226", armor="#8E9AA6", head="turban", head_col="#F4F1EA", shield="#6B4F2A", skin="#C99A6B", banner="#FFFFFF", weapon="sword"),
    "chalukya":  dict(tunic="#E8A23A", armor="#B5652B", head="pagdi", head_col="#C1121F", shield="#C9A227", skin="#B07A4F", banner="#E8A23A", weapon="spear"),
    "rajput":    dict(tunic="#F28C28", armor="#7A3E12", head="pagdi", head_col="#FFD23F", shield="#8B5A2B", skin="#B98559", banner="#F28C28", weapon="sword"),
    "pratihara": dict(tunic="#D97706", armor="#6B3F1D", head="pagdi", head_col="#FFFFFF", shield="#A16207", skin="#B07A4F", banner="#D97706", weapon="spear"),
    "frank":     dict(tunic="#2B59C3", armor="#9CA3AF", head="helmet", head_col="#9CA3AF", shield="#C1121F", skin="#E8B796", banner="#2B59C3", weapon="sword"),
    "khazar":    dict(tunic="#5B4636", armor="#3F3F46", head="fur", head_col="#7C5C3E", shield="#3F3F46", skin="#D4A276", banner="#5B4636", weapon="bow"),
    "turk":      dict(tunic="#2F855A", armor="#4A5568", head="fur", head_col="#5C4033", shield="#2F855A", skin="#D4A276", banner="#2F855A", weapon="bow"),
    "byzantine": dict(tunic="#6B21A8", armor="#D4AF37", head="crest", head_col="#C0C0C0", shield="#B91C1C", skin="#E8B796", banner="#6B21A8", weapon="spear"),
    "berber":    dict(tunic="#1E3A8A", armor="#1E3A8A", head="veil", head_col="#0F172A", shield="#92400E", skin="#9C6B45", banner="#1E3A8A", weapon="spear"),
    "syrian":    dict(tunic="#E9E4D8", armor="#8E9AA6", head="turban", head_col="#F4F1EA", shield="#6B4F2A", skin="#C99A6B", banner="#FFFFFF", weapon="spear"),
}
INK = "#1A1A1A"

def _headgear(c, kind, col, hy, k, face):
    if kind == "turban":
        c.drawOval(skia.Rect(-46 * k, hy - 62 * k, 46 * k, hy - 12 * k), paint(col)); c.drawOval(skia.Rect(-46 * k, hy - 62 * k, 46 * k, hy - 12 * k), paint("#9E9A90", 255, stroke=3 * k))
        p = skia.Path(); p.moveTo(-14 * k, hy - 58 * k); p.lineTo(0, hy - 92 * k); p.lineTo(14 * k, hy - 58 * k); p.close(); c.drawPath(p, paint("#7D8793"))
    elif kind == "pagdi":
        c.drawOval(skia.Rect(-48 * k, hy - 66 * k, 48 * k, hy - 10 * k), paint(col)); c.drawCircle(-30 * k, hy - 54 * k, 14 * k, paint(col))
        c.drawLine(-40 * k, hy - 36 * k, 40 * k, hy - 46 * k, paint("#000000", 60, stroke=4 * k)); c.drawCircle(18 * k, hy - 60 * k, 6 * k, paint("#FFD23F"))
    elif kind == "helmet":
        c.drawArc(skia.Rect(-48 * k, hy - 74 * k, 48 * k, hy + 6 * k), 180, 180, True, paint(col)); c.drawRect(skia.Rect(-4 * k, hy - 34 * k, 4 * k, hy + 6 * k), paint(col))
    elif kind == "crest":
        c.drawArc(skia.Rect(-48 * k, hy - 74 * k, 48 * k, hy + 6 * k), 180, 180, True, paint(col))
        c.drawOval(skia.Rect(-34 * k, hy - 104 * k, 34 * k, hy - 60 * k), paint("#B91C1C"))
    elif kind == "fur":
        c.drawRoundRect(skia.Rect(-50 * k, hy - 74 * k, 50 * k, hy - 20 * k), 22 * k, 22 * k, paint(col))
        for i in range(6): c.drawLine((-40 + i * 16) * k, hy - 70 * k, (-44 + i * 16) * k, hy - 24 * k, paint("#000000", 50, stroke=3 * k))
    elif kind == "veil":
        c.drawArc(skia.Rect(-48 * k, hy - 66 * k, 48 * k, hy + 10 * k), 180, 180, True, paint(col)); c.drawRect(skia.Rect(-46 * k, hy + 6 * k, 46 * k, hy + 30 * k), paint(col))

def soldier(c, x, y, s, t, fac="arab", state="idle", ph=0.0, face=1, a=255, fall=0.0, weapon=None, banner=False):
    """one cartoon soldier, feet at (x, y), height ~2*s. state: idle / run / attack / block / hit / flee / cheer / shoot."""
    F = FAC[fac]; k = s / 100; weapon = weapon or F["weapon"]
    c.save(); c.translate(x, y)
    if fall > 0: c.rotate(-face * 88 * ease_out(clamp(fall))); c.translate(0, 0)
    c.scale(face, 1)
    run = state in ("run", "flee", "attack"); sw = math.sin(ph * 2 * math.pi) if run else 0.0
    bob = (abs(math.sin(ph * 2 * math.pi)) * 6 * k if run else math.sin(t * 2.6 + x * 0.01) * 2 * k)
    c.drawOval(skia.Rect(-55 * k, -8 * k, 55 * k, 8 * k), paint("#000000", int(a * 0.28), blur=5)) if fall < 0.5 else None
    leg = paint("#2B2F3A", a, stroke=18 * k, cap_round=True)
    c.drawLine(-14 * k, -60 * k - bob, -14 * k + sw * 26 * k, 0, leg); c.drawLine(14 * k, -60 * k - bob, 14 * k - sw * 26 * k, 0, leg)
    by = -60 * k - bob
    # back arm + shield
    arm = paint(F["tunic"], a, stroke=20 * k, cap_round=True)
    if state == "flee" or state == "cheer":
        w = math.sin(t * 14 + x) * 10 * k
        c.drawLine(-36 * k, by - 100 * k, -64 * k + w, by - 168 * k, arm); c.drawCircle(-64 * k + w, by - 172 * k, 11 * k, paint(F["skin"], a))
    else:
        c.drawLine(-34 * k, by - 100 * k, -50 * k, by - 50 * k, arm)
        if F["shield"] and weapon != "bow":
            shx = 28 * k if state == "block" else -36 * k
            c.drawCircle(shx, by - 66 * k, 36 * k, paint(F["shield"], a)); c.drawCircle(shx, by - 66 * k, 36 * k, paint(INK, a, stroke=4 * k))
            c.drawCircle(shx, by - 66 * k, 10 * k, paint("#E9C46A", a))
    # body
    c.drawRoundRect(skia.Rect(-44 * k, by - 128 * k, 44 * k, by + 4 * k), 32 * k, 32 * k, paint(F["tunic"], a))
    c.drawRoundRect(skia.Rect(-38 * k, by - 120 * k, 38 * k, by - 56 * k), 22 * k, 22 * k, paint(F["armor"], int(a * 0.9)))
    for i in range(3): c.drawLine(-30 * k, by - (108 - i * 18) * k, 30 * k, by - (108 - i * 18) * k, paint("#000000", int(a * 0.15), stroke=2.5 * k))
    c.drawRect(skia.Rect(-44 * k, by - 50 * k, 44 * k, by - 40 * k), paint("#5A3A1E", a))
    # head
    hy = by - 168 * k
    c.drawCircle(0, hy, 40 * k, paint(F["skin"], a)); _headgear(c, F["head"], F["head_col"], hy, k, face)
    angry = state in ("attack", "run", "shoot", "block")
    for ex in (2, 24):
        c.drawCircle(ex * k, hy - 2 * k, 5.5 * k, paint(INK, a))
        if angry: c.drawLine((ex - 9) * k, hy - 16 * k + (4 if ex == 24 else -1) * k, (ex + 8) * k, hy - 12 * k - (3 if ex == 24 else -2) * k, paint(INK, a, stroke=3.5 * k, cap_round=True))
    if state in ("flee", "hit") or fall > 0: c.drawOval(skia.Rect(4 * k, hy + 12 * k, 20 * k, hy + 26 * k), paint("#5A1F1F", a))
    elif state in ("attack", "cheer"): c.drawOval(skia.Rect(2 * k, hy + 12 * k, 22 * k, hy + 24 * k), paint("#5A1F1F", a))
    else: c.drawLine(4 * k, hy + 18 * k, 22 * k, hy + 17 * k, paint(INK, a, stroke=3 * k, cap_round=True))
    if F["head"] == "veil": c.drawRect(skia.Rect(-20 * k, hy + 6 * k, 40 * k, hy + 32 * k), paint(F["head_col"], a))
    # front arm + weapon
    if state not in ("flee", "cheer"):
        if weapon == "sword":
            sa = (-70 + 140 * abs(math.sin(ph * 2 * math.pi * 1.5))) if state == "attack" else (-30 if state == "run" else 10)
        elif weapon == "spear":
            sa = 0 if state != "attack" else 0
        else: sa = -10
        c.save(); c.translate(30 * k, by - 104 * k); c.rotate(sa)
        thrust = (12 + 26 * max(0, math.sin(ph * 2 * math.pi * 1.5))) * k if (weapon == "spear" and state == "attack") else 0
        c.drawLine(0, 0, 44 * k + thrust, 22 * k, arm); c.drawCircle(46 * k + thrust, 22 * k, 11 * k, paint(F["skin"], a))
        if weapon == "sword":
            c.drawLine(46 * k, 22 * k, 46 * k + 10 * k, 22 * k - 96 * k, paint("#D9DEE5", a, stroke=8 * k, cap_round=True))
            c.drawLine(34 * k, 14 * k, 58 * k, 30 * k, paint("#C9A227", a, stroke=6 * k, cap_round=True))
        elif weapon == "spear":
            c.drawLine(46 * k + thrust - 90 * k, 22 * k + 4 * k, 46 * k + thrust + 120 * k, 22 * k - 6 * k, paint("#7A5230", a, stroke=6 * k, cap_round=True))
            p = skia.Path(); p.moveTo(46 * k + thrust + 120 * k, 22 * k - 16 * k); p.lineTo(46 * k + thrust + 150 * k, 22 * k - 7 * k); p.lineTo(46 * k + thrust + 120 * k, 22 * k + 4 * k); p.close()
            c.drawPath(p, paint("#D9DEE5", a))
        elif weapon == "bow":
            bw = skia.Path(); bw.addArc(skia.Rect(30 * k, -40 * k, 70 * k, 84 * k), -80, 160); c.drawPath(bw, paint("#6B4423", a, stroke=6 * k))
            pull = 26 * k * (0.5 + 0.5 * math.sin(ph * 2 * math.pi)) if state == "shoot" else 0
            c.drawLine(50 * k, -38 * k, 50 * k - pull, 22 * k, paint("#EEEEEE", a, stroke=2 * k)); c.drawLine(50 * k - pull, 22 * k, 50 * k, 82 * k, paint("#EEEEEE", a, stroke=2 * k))
        c.restore()
    if banner:
        c.drawLine(-20 * k, by - 40 * k, -20 * k, by - 300 * k, paint("#6B4423", a, stroke=6 * k))
        fl = skia.Path(); wv = math.sin(t * 6) * 10 * k
        fl.moveTo(-20 * k, by - 300 * k); fl.quadTo(40 * k, by - 300 * k + wv, 90 * k, by - 290 * k); fl.lineTo(90 * k, by - 220 * k); fl.quadTo(40 * k, by - 228 * k - wv, -20 * k, by - 222 * k); fl.close()
        c.drawPath(fl, paint(F["banner"], a)); c.drawPath(fl, paint("#000000", int(a * 0.3), stroke=2 * k))
    c.restore()

def horse(c, x, y, s, t, ph, face=1, col="#8B5A2B", rider=None, a=255, fall=0.0):
    """galloping cartoon horse, hooves at y; rider(c, x, y_seat, s) draws the soldier's upper body."""
    k = s / 100; c.save(); c.translate(x, y)
    if fall > 0: c.rotate(-face * 70 * ease_out(clamp(fall)))
    c.scale(face, 1)
    g = ph * 2 * math.pi; bob = abs(math.sin(g)) * 8 * k
    c.drawOval(skia.Rect(-110 * k, -10 * k, 110 * k, 10 * k), paint("#000000", int(a * 0.25), blur=6))
    lp = paint(col, a, stroke=16 * k, cap_round=True); lp2 = paint("#3B2A1A", a, stroke=16 * k, cap_round=True)
    for i, (hx, off) in enumerate(((-60, 0), (-40, 0.5), (55, 0.25), (75, 0.75))):
        sw = math.sin(g + off * 2 * math.pi) * 30 * k
        c.drawLine(hx * k, -90 * k - bob, hx * k + sw, -40 * k, lp if i % 2 else lp2); c.drawLine(hx * k + sw, -40 * k, hx * k + sw * 0.6, 0, lp if i % 2 else lp2)
    c.drawOval(skia.Rect(-95 * k, -150 * k - bob, 95 * k, -80 * k - bob), paint(col, a))
    nk = skia.Path(); nk.moveTo(60 * k, -140 * k - bob); nk.lineTo(110 * k, -215 * k - bob); nk.lineTo(140 * k, -200 * k - bob); nk.lineTo(95 * k, -110 * k - bob); nk.close(); c.drawPath(nk, paint(col, a))
    c.drawOval(skia.Rect(100 * k, -232 * k - bob, 175 * k, -192 * k - bob), paint(col, a)); c.drawCircle(128 * k, -220 * k - bob, 5 * k, paint(INK, a))
    for i in range(5): c.drawLine((70 + i * 12) * k, (-170 - i * 12) * k - bob, (58 + i * 12) * k, (-150 - i * 12) * k - bob, paint("#2B1D0E", a, stroke=7 * k, cap_round=True))
    c.drawLine(-95 * k, -130 * k - bob, -140 * k + math.sin(g * 1.3) * 10 * k, -90 * k - bob, paint("#2B1D0E", a, stroke=12 * k, cap_round=True))
    c.drawRoundRect(skia.Rect(-40 * k, -162 * k - bob, 30 * k, -138 * k - bob), 8 * k, 8 * k, paint("#9B2226", a))
    c.restore()
    if rider: rider(c, x - face * 4 * k, y - 150 * k - bob, s * 0.95)

def elephant(c, x, y, s, t, ph, face=1, rider=None, a=255, cloth="#9B2226"):
    """war elephant with howdah and royal umbrella; rider(c, x, y_seat, s) draws the king."""
    k = s / 100; c.save(); c.translate(x, y); c.scale(face, 1)
    g = ph * 2 * math.pi; bob = abs(math.sin(g)) * 4 * k; grey = "#8A8F98"
    c.drawOval(skia.Rect(-170 * k, -14 * k, 170 * k, 14 * k), paint("#000000", int(a * 0.3), blur=8))
    for i, (lx, off) in enumerate(((-110, 0), (-70, 0.5), (60, 0.5), (100, 0))):
        sw = math.sin(g + off * 2 * math.pi) * 14 * k
        c.drawRoundRect(skia.Rect(lx * k - 24 * k + sw, -110 * k - bob, lx * k + 24 * k + sw, 0), 14 * k, 14 * k, paint(grey if i % 2 else "#767B84", a))
    c.drawOval(skia.Rect(-160 * k, -270 * k - bob, 150 * k, -90 * k - bob), paint(grey, a))
    c.drawCircle(150 * k, -230 * k - bob, 70 * k, paint(grey, a))
    c.drawOval(skia.Rect(80 * k, -290 * k - bob, 150 * k, -170 * k - bob), paint("#9CA1AA", a))
    tr = skia.Path(); tw = math.sin(t * 3) * 25 * k
    tr.moveTo(200 * k, -220 * k - bob); tr.cubicTo(250 * k, -160 * k, 230 * k + tw, -60 * k, 260 * k + tw, -30 * k)
    c.drawPath(tr, paint(grey, a, stroke=28 * k, cap_round=True))
    c.drawLine(195 * k, -190 * k - bob, 250 * k, -170 * k - bob, paint("#F4F1EA", a, stroke=10 * k, cap_round=True))
    c.drawCircle(170 * k, -248 * k - bob, 7 * k, paint(INK, a))
    c.drawRoundRect(skia.Rect(-130 * k, -250 * k - bob, 90 * k, -140 * k - bob), 20 * k, 20 * k, paint(cloth, a))
    for i in range(6): c.drawCircle((-110 + i * 38) * k, -146 * k - bob, 8 * k, paint("#E9C46A", a))
    c.drawRect(skia.Rect(-90 * k, -330 * k - bob, 60 * k, -260 * k - bob), paint("#C9A227", a)); c.drawRect(skia.Rect(-90 * k, -330 * k - bob, 60 * k, -260 * k - bob), paint(INK, a, stroke=4 * k))
    c.drawLine(-15 * k, -330 * k - bob, -15 * k, -520 * k - bob, paint("#6B4423", a, stroke=6 * k))
    um = skia.Path(); um.moveTo(-110 * k, -500 * k - bob); um.quadTo(-15 * k, -580 * k - bob, 80 * k, -500 * k - bob); um.close()
    c.drawPath(um, paint("#FFD23F", a)); c.drawPath(um, paint("#9B2226", a, stroke=6 * k))
    c.restore()
    if rider: rider(c, x - face * 15 * k, y - 330 * k - bob, s)

def king_bust(c, x, y, s, t, robe="#9B2226", a=255, face=1, sword_up=0.0):
    """king's upper body for the howdah / saddle (crown, robe, raised sword)."""
    k = s / 100; c.save(); c.translate(x, y); c.scale(face, 1)
    c.drawRoundRect(skia.Rect(-40 * k, -110 * k, 40 * k, 0), 28 * k, 28 * k, paint(robe, a))
    c.drawLine(-30 * k, -100 * k, 30 * k, -10 * k, paint("#E9C46A", a, stroke=7 * k))
    c.drawCircle(0, -150 * k, 38 * k, paint("#B07A4F", a))
    cr = skia.Path(); cr.moveTo(-34 * k, -178 * k); cr.lineTo(-38 * k, -218 * k); cr.lineTo(-16 * k, -196 * k); cr.lineTo(0, -228 * k); cr.lineTo(16 * k, -196 * k); cr.lineTo(38 * k, -218 * k); cr.lineTo(34 * k, -178 * k); cr.close()
    c.drawPath(cr, paint("#FFD23F", a)); c.drawPath(cr, paint(INK, a, stroke=3 * k))
    for ex in (4, 24): c.drawCircle(ex * k, -152 * k, 5 * k, paint(INK, a))
    c.drawArc(skia.Rect(-10 * k, -142 * k, 36 * k, -110 * k), 0, 180, True, paint("#2B1D0E", a))
    ang = lerp(20, -60, clamp(sword_up)) + math.sin(t * 6) * 6 * sword_up
    c.save(); c.translate(30 * k, -90 * k); c.rotate(ang)
    c.drawLine(0, 0, 50 * k, 0, paint(robe, a, stroke=18 * k, cap_round=True)); c.drawCircle(52 * k, 0, 10 * k, paint("#B07A4F", a))
    c.drawLine(52 * k, 0, 150 * k, -10 * k, paint("#D9DEE5", a, stroke=8 * k, cap_round=True)); c.restore()
    c.restore()

def rider_fn(fac, state="attack", ph=0.0, t=0.0, face=1):
    def _r(c, x, y, s): soldier(c, x, y + 60 * s / 100, s, t, fac, state if state != "run" else "attack", ph * 0.7, face)
    return _r

# ------------------------------------------------------------------ effects
def arrow_volley(c, t, t0, src, dst, n=24, flight=0.9, spread=(160, 120), seed=3, a=255, h=320):
    """arrows rise from the archers (src x, y) and rain on dst, staggered over 0.6 s; they stick in the ground."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        st = t0 + rng.uniform(0, 0.6); kf = (t - st) / flight
        if kf <= 0: continue
        sx = src[0] + rng.uniform(-spread[0], spread[0]) * 0.4; sy = src[1] + rng.uniform(-30, 30)
        ex = dst[0] + rng.uniform(-spread[0], spread[0]); ey = dst[1] + rng.uniform(-spread[1], spread[1])
        kk = min(1.0, kf); x = lerp(sx, ex, kk); y = lerp(sy, ey, kk) - h * 4 * kk * (1 - kk)
        dx = ex - sx; dy = (ey - sy) - h * 4 * (1 - 2 * kk); ang = math.atan2(dy, dx); L = 42
        al = int(a * (1 if kf < 1 else clamp(1 - (kf - 1) * 2)))
        if al <= 0: continue
        x0, y0 = x - math.cos(ang) * L, y - math.sin(ang) * L
        c.drawLine(x0, y0, x, y, paint("#3B2A1A", al, stroke=3.2, cap_round=True))
        c.drawLine(x0, y0, x0 - math.cos(ang + 0.5) * 10, y0 - math.sin(ang + 0.5) * 10, paint("#F4F1EA", al, stroke=2.5))
        c.drawLine(x0, y0, x0 - math.cos(ang - 0.5) * 10, y0 - math.sin(ang - 0.5) * 10, paint("#F4F1EA", al, stroke=2.5))

def dust(c, t, x, y, w, k=1.0, seed=1, col="#C8A97E"):
    if k <= 0: return
    rng = np.random.default_rng(seed)
    for i in range(14):
        px = x + rng.uniform(-w / 2, w / 2) + math.sin(t * 0.8 + i) * 20; py = y - rng.uniform(0, 90) - (t * 18 + i * 9) % 40
        r = rng.uniform(40, 100); c.drawCircle(px, py, r, paint(col, int(70 * k), blur=r * 0.5))

def sparks(c, x, y, t, seed=0, k=1.0):
    rng = np.random.default_rng(seed); ph = (t * 3 + rng.uniform(0, 1)) % 1.0
    if ph > 0.35 or k <= 0: return
    for i in range(8):
        ang = i / 8 * 2 * math.pi + rng.uniform(-0.2, 0.2); r0 = 8 + ph * 60; r1 = r0 + 18
        c.drawLine(x + math.cos(ang) * r0, y + math.sin(ang) * r0, x + math.cos(ang) * r1, y + math.sin(ang) * r1, paint("#FFE066", int(255 * k * (1 - ph / 0.35)), stroke=4, cap_round=True))
    c.drawCircle(x, y, 18, paint("#FFF3B0", int(200 * k * (1 - ph / 0.35)), blur=8))

def speed_lines(c, t, k, col="#FFFFFF"):
    if k <= 0: return
    rng = np.random.default_rng(int(t * 12))
    for i in range(18):
        y = rng.uniform(0, DH); x = rng.uniform(0, DW); L = rng.uniform(120, 360)
        c.drawLine(x, y, x + L, y, paint(col, int(60 * k), stroke=rng.uniform(1.5, 4)))

# ------------------------------------------------------------------ photoreal background for cartoon battles
_BG = {}
def prep_battle_bg(img_path, ground_box=(0.40, 0.80, 0.74, 1.0), blur=12, tint=None):
    """blur the photoreal scene (painted armies become a distant bokeh) and cut a sharp foreground ground strip
    from `ground_box` (normalised x0, y0, x1, y1 of bare earth in the photo)."""
    key = (img_path, ground_box, blur, tint)
    if key not in _BG:
        im = Image.open(img_path).convert("RGB")
        far = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(blur))).enhance(0.82)
        if tint: far = Image.blend(far, Image.new("RGB", far.size, tint), 0.22)
        W, H = im.size; gb = im.crop((int(ground_box[0] * W), int(ground_box[1] * H), int(ground_box[2] * W), int(ground_box[3] * H)))
        if tint: gb = Image.blend(gb, Image.new("RGB", gb.size, tint), 0.15)
        g = np.asarray(gb.resize((1920, 460), Image.BICUBIC).convert("RGBA")).copy()
        g[..., 3] = (np.clip(np.linspace(0, 1.6, 460), 0, 1) ** 1.3 * 255).astype(np.uint8)[:, None]
        _BG[key] = (sk_image(far), skia.Image.fromarray(g, colorType=skia.ColorType.kRGBA_8888_ColorType))
    return _BG[key]

def battle_bg(c, bg, t, t0, dur, push=(1.0, 1.06), haze="#E9B872"):
    far, ground = bg; k = ease_io(seg(t, t0, t0 + dur)); s = lerp(push[0], push[1], k)
    fw, fh = far.width(), far.height(); cov = max(DW / fw, DH / fh) * s; w, h = fw * cov, fh * cov
    draw_img(c, far, (DW - w) / 2, (DH - h) * 0.45, (DW + w) / 2, (DH - h) * 0.45 + h)
    g = skia.GradientShader.MakeLinear([(0, DH * 0.40), (0, DH * 0.66)], [hexc(haze, 0), hexc(haze, 120), hexc(haze, 0)], [0, 0.6, 1])
    c.drawRect(skia.Rect(0, 0, DW, DH), skia.Paint(Shader=g))
    gs = 1 + (s - 1) * 1.6; gw = DW * gs; draw_img(c, ground, (DW - gw) / 2, DH - 460 * gs, (DW + gw) / 2, DH)

# ------------------------------------------------------------------ the choreographer
class Battle:
    """left/right = dict(fac, inf, cav, arch, eleph, king, banner) ; winner = 'left' | 'right'.
    Times (seconds from t0): clash at `t_clash`, rout at `t_rout`, end at `dur`. Units are drawn depth-sorted.
    cam(t) gives the zoom/shake to apply before drawing (use with Battle.draw(..., camera=True))."""
    def __init__(self, left, right, winner="right", t0=0.0, dur=6.0, t_clash=1.5, t_rout=4.2, clash_x=DW * 0.5,
                 ground=(800, 1065), seed=5, volley=None, base=118, linear=False):
        self.linear = linear
        self.L, self.R, self.win, self.t0, self.dur = left, right, winner, t0, dur
        self.tc, self.tr, self.cx, self.g, self.base, self.volley = t_clash, t_rout, clash_x, ground, base, volley
        rng = np.random.default_rng(seed); self.units = []
        for side, spec in (("L", left), ("R", right)):
            d = 1 if side == "L" else -1
            for kind in ("eleph", "cav", "inf", "arch"):
                for i in range(spec.get(kind, 0)):
                    lane = rng.uniform(ground[0], ground[1]); depth = (lane - ground[0]) / (ground[1] - ground[0])
                    back = {"cav": 0.0, "inf": 0.12, "eleph": 0.42, "arch": 0.62}[kind] + rng.uniform(0, 0.35)
                    if kind == "eleph": lane = ground[0] + 10 + i * 30; depth = 0.15
                    self.units.append(dict(side=side, d=d, kind=kind, y=lane, depth=depth, back=back, r=rng.uniform(0, 1), ph0=rng.uniform(0, 1),
                                           fac=spec["fac"], king=(kind == "eleph" and i == 0 and spec.get("king")), banner=(kind == "inf" and i == 0 and spec.get("banner", True))))
        self.units.sort(key=lambda u: u["y"])

    def pos(self, u, lt):
        d = u["d"]; front = self.cx - d * (50 + u["back"] * 700); start = self.cx - d * (DW * 0.8 + u["back"] * 700)
        speed_k = {"cav": 1.0, "inf": 0.8, "eleph": 0.6, "arch": 0.0}[u["kind"]]
        if u["kind"] == "arch": return self.cx - d * (620 + u["back"] * 200), "shoot" if lt < self.tr else "idle", d
        kr = clamp(lt / max(0.1, self.tc * (1.15 - 0.15 * speed_k))); ka = kr if self.linear else ease_out(kr)
        x = lerp(start, front, ka); state = "run" if ka < 1 else "attack"
        if lt > self.tc: x += math.sin(lt * 5 + u["r"] * 6) * 18
        loser = self.is_loser(u)
        if lt > self.tr and self.win is not None:
            k = lt - self.tr
            if loser: x -= d * 520 * k * (0.7 + u["r"] * 0.6); state = "flee"; d = -d
            else: x += d * 160 * min(k, 1.2); state = "cheer" if k > 1.0 else "run"
        return x, state, d

    def is_loser(self, u):
        return (self.win == "left" and u["side"] == "R") or (self.win == "right" and u["side"] == "L")

    def cam(self, t):
        lt = t - self.t0; z = 1 + 0.22 * ease_io(seg(lt, self.tc - 0.3, self.tc + 0.6)) - 0.14 * ease_io(seg(lt, self.tr, self.tr + 1.0))
        k = seg(lt, self.tc, self.tc + 0.45); sh = (1 - k) ** 2 * 18 if 0 < k < 1 else 0
        return z, sh * math.sin(t * 80), sh * math.cos(t * 67)

    def draw(self, c, t, camera=True, a=255):
        lt = t - self.t0
        if lt < 0 or lt > self.dur + 2: return
        if camera:
            z, dx, dy = self.cam(t); c.save(); c.translate(self.cx + dx, self.g[1] + dy); c.scale(z, z); c.translate(-self.cx, -self.g[1])
        dust(c, t, self.cx, self.g[0] + 40, 900, seg(lt, self.tc - 0.4, self.tc + 0.4) * (1 - seg(lt, self.dur - 0.5, self.dur + 1)), seed=3)
        for u in self.units:
            x, state, face = self.pos(u, lt); s = self.base * lerp(0.62, 1.05, u["depth"])
            ph = u["ph0"] + lt * (2.6 if u["kind"] == "cav" else 1.8)
            loser = self.is_loser(u)
            fall = seg(lt, self.tr - 0.4 + u["r"] * 0.8, self.tr + u["r"] * 0.8) if ((loser and u["r"] < 0.28) or (self.win is None and u["r"] < 0.22 and u["kind"] != "eleph")) else 0.0
            if fall > 0: state = "hit"
            if u["kind"] == "cav":
                col = ("#F2EEE6", "#8B5A2B", "#3B2A1A")[int(u["r"] * 3)]
                horse(c, x, u["y"], s * 1.15, t, ph, face, col, rider_fn(u["fac"], "flee" if state == "flee" else "attack", ph, t, face), a, fall)
            elif u["kind"] == "eleph":
                kb = (lambda cc, X, Y, S, f=face: king_bust(cc, X, Y, S * 0.55, t, face=f, sword_up=seg(lt, self.tc - 0.5, self.tc))) if u["king"] else None
                elephant(c, x, u["y"], s * 1.55, t, ph * 0.6, face, kb, a)
            else:
                soldier(c, x, u["y"], s, t, u["fac"], state, ph, face, a, fall, banner=u["banner"] and state != "flee")
            if self.tc < lt < self.tr and u["back"] < 0.12 and u["side"] == "L": sparks(c, self.cx + math.sin(u["r"] * 9) * 60, u["y"] - s * 1.4, t, seed=int(u["r"] * 99))
        if self.volley:
            side = self.volley; src_x = self.cx + (620 if side == "R" else -620); dst_x = self.cx - (260 if side == "R" else -260)
            arrow_volley(c, t, self.t0 + self.tc * 0.35, (src_x, self.g[0] - 80), (dst_x, (self.g[0] + self.g[1]) / 2), n=26, seed=7)
            arrow_volley(c, t, self.t0 + self.tc * 0.35 + 0.7, (src_x, self.g[0] - 80), (dst_x - (100 if side == "R" else -100), (self.g[0] + self.g[1]) / 2), n=22, seed=9)
        if camera: c.restore()
        speed_lines(c, t, seg(lt, 0, 0.3) * (1 - seg(lt, self.tc - 0.4, self.tc)) * 0.8)

    def king_xy(self, t):
        for u in self.units:
            if u["king"]: x, _, _ = self.pos(u, t - self.t0); return x, u["y"]
        return None
