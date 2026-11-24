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

# ------------------------------------------------------------------ factions: period costumes (8th century, andaazan, based on period art)
# body: mail (knee-length hauberk) / bare (bare chest + cross belts) / lamellar (scale plates) / quilted / robe
# legs: trousers / dhoti / bare ; head: see _headgear ; shield: round / rect / oval / hide / big_round / none
FAC = {
    # Umayyad Arab regulars: mail hauberk over a tunic, turban wound round a conical helmet, beard, straight sword, round leather shield, white banner
    "arab":      dict(tunic="#D9D2C3", body="mail", armor="#8E9AA6", legs="trousers", leg_col="#6B5B45", head="turban_helm", head_col="#F1ECE0",
                      shield="round", shield_col="#7A5230", skin="#C99A6B", beard="#2B1D0E", weapon="sword", banner="umayyad", horses=("#E8E2D6", "#9C6B3E", "#5B3A22"), capar=None),
    "arab_gen":  dict(tunic="#9B2226", body="mail", armor="#B0B7C0", legs="trousers", leg_col="#3A2A1E", head="turban_helm", head_col="#FFFFFF", cloak="#9B2226",
                      shield="round", shield_col="#5A3A1E", skin="#C99A6B", beard="#1A120B", weapon="sword", banner="umayyad", horses=("#2B1D0E",), capar="#9B2226"),
    "syrian":    dict(tunic="#CFC6B4", body="mail", armor="#7D8793", legs="trousers", leg_col="#4A3B2A", head="turban_helm", head_col="#E9E4D8",
                      shield="round", shield_col="#6B4423", skin="#C99A6B", beard="#2B1D0E", weapon="lance", banner="umayyad", horses=("#9C6B3E", "#5B3A22", "#E8E2D6"), capar=None),
    # Chalukya (Navsari, Gujarat-Deccan): bare chest with cross belts, knee dhoti, sash, hair in a top-knot with a band, tall rectangular shield, long spear, boar (varaha) banner
    "chalukya":  dict(tunic="#B07A4F", body="bare", armor="#C1121F", legs="dhoti", leg_col="#F4E3B5", head="topknot", head_col="#1A120B", band="#C1121F",
                      shield="rect", shield_col="#8B1E1E", skin="#B07A4F", beard=None, weapon="spear", banner="varaha", horses=("#6B3F1D",), capar="#C1121F"),
    # Mori of Chittor / Guhila (Bappa Rawal): quilted coat, turban, broad khanda sword, round shield with bosses
    "rajput":    dict(tunic="#E07B1A", body="quilted", armor="#B5541A", legs="trousers", leg_col="#F4E3B5", head="pagdi", head_col="#C1121F",
                      shield="round", shield_col="#5A3A1E", skin="#B98559", beard="#1A120B", weapon="khanda", banner="sun", horses=("#F2EEE6", "#A0522D"), capar="#E07B1A"),
    # Gurjara-Pratihara heavy cavalry: quilted armour, white turban, lance, caparisoned horses, boar banner (Adivaraha)
    "pratihara": dict(tunic="#C2410C", body="quilted", armor="#7C2D12", legs="trousers", leg_col="#F4E3B5", head="pagdi", head_col="#FFFFFF",
                      shield="round", shield_col="#7C2D12", skin="#B07A4F", beard="#1A120B", weapon="lance", banner="varaha", horses=("#5B3A22", "#2B1D0E", "#A0522D"), capar="#B91C1C"),
    # Turgesh Turks (Day of Thirst, Defile): steppe horse archers, tall pointed felt cap, braids, lamellar, composite bow, wolf banner, small dun horses
    "turk":      dict(tunic="#3F6E4A", body="lamellar", armor="#6B6B5A", legs="trousers", leg_col="#3A2A1E", head="felt_cap", head_col="#E7DCC5", braids=True,
                      shield="none", shield_col="#3F3F46", skin="#D4A276", beard=None, weapon="bow", banner="wolf", horses=("#C8A26B", "#8B6B3E"), capar=None),
    # Khazars (Ardabil 730): fur-trimmed spiked helmets, lamellar, lances and bows, round shields, bay/black horses
    "khazar":    dict(tunic="#5B4636", body="lamellar", armor="#4B5563", legs="trousers", leg_col="#2B1D0E", head="fur_spike", head_col="#7C5C3E",
                      shield="round", shield_col="#374151", skin="#D9AE84", beard="#5C4033", weapon="lance", banner="khazar", horses=("#3B2A1A", "#6B4423", "#1A120B"), capar=None),
    # Franks (Tours 732): nasal spangenhelm, mail for the front rank, big painted round shield, spear / francisca axe, infantry shield wall
    "frank":     dict(tunic="#2B59C3", body="mail", armor="#9CA3AF", legs="trousers", leg_col="#6B4F2A", head="nasal", head_col="#A8AFB8",
                      shield="big_round", shield_col="#C1121F", skin="#E8B796", beard="#8B5A2B", weapon="spear", banner="frank", horses=("#6B4423",), capar=None),
    "frank_lead":dict(tunic="#1E3A8A", body="mail", armor="#C0C6CE", legs="trousers", leg_col="#3A2A1E", head="nasal", head_col="#D4AF37", cloak="#7F1D1D",
                      shield="big_round", shield_col="#D4AF37", skin="#E8B796", beard="#A0522D", weapon="axe", banner="frank", horses=("#3B2A1A",), capar=None),
    # Byzantines (Akroinon 740): kataphraktoi - plumed helmet, lamellar klibanion, oval shield, kontarion lance, armoured horses
    "byzantine": dict(tunic="#6B21A8", body="lamellar", armor="#B8A46A", legs="trousers", leg_col="#3A2A1E", head="plume", head_col="#C0C0C0",
                      shield="oval", shield_col="#B91C1C", skin="#E8B796", beard="#3A2A1E", weapon="lance", banner="byz", horses=("#1A120B", "#4B4B4B"), capar="#6B21A8"),
    # Berbers (740 revolt): shaved heads (Kharijite rebels), tunic and cloak, small hide shield, javelins, small dark Barb horses
    "berber":    dict(tunic="#E9DCC0", body="robe", armor="#1E3A8A", legs="bare", leg_col="#9C6B45", head="shaved", head_col="#9C6B45",
                      shield="hide", shield_col="#C8A26B", skin="#9C6B45", beard="#1A120B", weapon="javelin", banner="berber", horses=("#2B1D0E", "#5B3A22"), capar=None),
}
INK = "#1A1A1A"

def banner_emblem(c, kind, x0, y0, w, h, a=255):
    """period banners (andaazan): Umayyad plain white, Chalukya/Pratihara varaha (boar), Turk wolf head, Mewar sun,
    Byzantine purple-gold, Frankish red/yellow, Khazar and Berber plain colours."""
    bg = {"umayyad": "#FFFFFF", "varaha": "#E8A23A", "wolf": "#2F6B3A", "sun": "#C1121F", "byz": "#5B1A8A", "frank": "#B91C1C",
          "khazar": "#5B4636", "berber": "#1E3A8A"}.get(kind, "#FFFFFF")
    r = skia.Rect(x0, y0, x0 + w, y0 + h); c.drawRect(r, paint(bg, a))
    cx, cy, s = x0 + w * 0.5, y0 + h * 0.5, min(w, h)
    if kind == "varaha":            # boar silhouette
        p = skia.Path(); p.addOval(skia.Rect(cx - s * 0.32, cy - s * 0.18, cx + s * 0.28, cy + s * 0.16)); c.drawPath(p, paint("#3A1F0F", a))
        c.drawCircle(cx + s * 0.3, cy - s * 0.02, s * 0.12, paint("#3A1F0F", a))
        c.drawLine(cx + s * 0.38, cy + s * 0.04, cx + s * 0.46, cy - s * 0.06, paint("#FFFFFF", a, stroke=s * 0.04))
        for lx in (-0.22, -0.06, 0.1, 0.2): c.drawLine(cx + lx * s, cy + s * 0.12, cx + lx * s, cy + s * 0.3, paint("#3A1F0F", a, stroke=s * 0.06))
    elif kind == "wolf":
        p = skia.Path(); p.moveTo(cx - s * 0.25, cy + s * 0.2); p.lineTo(cx - s * 0.18, cy - s * 0.28); p.lineTo(cx - s * 0.02, cy - s * 0.1)
        p.lineTo(cx + s * 0.12, cy - s * 0.3); p.lineTo(cx + s * 0.18, cy - s * 0.04); p.lineTo(cx + s * 0.38, cy + s * 0.06); p.lineTo(cx + s * 0.1, cy + s * 0.22); p.close()
        c.drawPath(p, paint("#E9C46A", a))
    elif kind == "sun":
        c.drawCircle(cx, cy, s * 0.2, paint("#FFD23F", a))
        for i in range(12):
            ang = i / 12 * 2 * math.pi; c.drawLine(cx + math.cos(ang) * s * 0.26, cy + math.sin(ang) * s * 0.26, cx + math.cos(ang) * s * 0.38, cy + math.sin(ang) * s * 0.38, paint("#FFD23F", a, stroke=s * 0.04))
    elif kind == "byz":
        c.drawRect(skia.Rect(x0 + w * 0.06, y0 + h * 0.08, x0 + w * 0.94, y0 + h * 0.92), paint("#D4AF37", a, stroke=s * 0.06))
        c.drawCircle(cx, cy, s * 0.14, paint("#D4AF37", a))
    elif kind == "frank":
        for i in range(3): c.drawRect(skia.Rect(x0, y0 + h * (0.15 + i * 0.3), x0 + w, y0 + h * (0.25 + i * 0.3)), paint("#FFD23F", a))

def _headgear(c, kind, F, hy, k):
    col = F["head_col"]
    if kind == "turban_helm":        # turban wound round a conical iron helmet + mail aventail
        c.drawOval(skia.Rect(-47 * k, hy - 58 * k, 47 * k, hy - 14 * k), paint(col)); c.drawOval(skia.Rect(-47 * k, hy - 58 * k, 47 * k, hy - 14 * k), paint("#A39E92", 255, stroke=3 * k))
        for i in range(3): c.drawArc(skia.Rect(-44 * k, hy - (54 - i * 10) * k, 44 * k, hy - (24 - i * 10) * k), 200, 140, False, paint("#B9B3A6", 255, stroke=2.2 * k))
        p = skia.Path(); p.moveTo(-16 * k, hy - 54 * k); p.lineTo(0, hy - 96 * k); p.lineTo(16 * k, hy - 54 * k); p.close(); c.drawPath(p, paint("#6E7884"))
    elif kind == "topknot":          # Indian top-knot with a cloth band (period sculpture)
        c.drawArc(skia.Rect(-40 * k, hy - 42 * k, 40 * k, hy + 18 * k), 180, 180, True, paint(col))
        c.drawCircle(4 * k, hy - 56 * k, 18 * k, paint(col)); c.drawRect(skia.Rect(-40 * k, hy - 22 * k, 40 * k, hy - 13 * k), paint(F.get("band", "#C1121F")))
        c.drawCircle(-38 * k, hy + 6 * k, 6 * k, paint("#FFD23F"))                    # ear ring
    elif kind == "pagdi":
        c.drawOval(skia.Rect(-48 * k, hy - 66 * k, 48 * k, hy - 10 * k), paint(col)); c.drawCircle(-30 * k, hy - 54 * k, 14 * k, paint(col))
        c.drawLine(-40 * k, hy - 36 * k, 40 * k, hy - 46 * k, paint("#000000", 60, stroke=4 * k)); c.drawCircle(18 * k, hy - 60 * k, 6 * k, paint("#FFD23F"))
    elif kind == "felt_cap":         # tall pointed Turkic felt cap with fur brim + braids
        p = skia.Path(); p.moveTo(-42 * k, hy - 20 * k); p.quadTo(-10 * k, hy - 70 * k, 14 * k, hy - 118 * k); p.quadTo(30 * k, hy - 60 * k, 42 * k, hy - 20 * k); p.close()
        c.drawPath(p, paint(col)); c.drawPath(p, paint("#9C8B6A", 255, stroke=2.5 * k))
        c.drawRoundRect(skia.Rect(-46 * k, hy - 30 * k, 46 * k, hy - 12 * k), 8 * k, 8 * k, paint("#6B4F2A"))
        if F.get("braids"):
            for bx in (-36, -28): c.drawLine(bx * k, hy - 4 * k, (bx - 6) * k, hy + 70 * k, paint("#1A120B", 255, stroke=7 * k, cap_round=True))
    elif kind == "fur_spike":        # Khazar spiked helmet with fur trim
        c.drawArc(skia.Rect(-46 * k, hy - 70 * k, 46 * k, hy + 6 * k), 180, 180, True, paint("#6B7280"))
        c.drawLine(0, hy - 70 * k, 0, hy - 100 * k, paint("#4B5563", 255, stroke=6 * k, cap_round=True))
        c.drawRoundRect(skia.Rect(-50 * k, hy - 34 * k, 50 * k, hy - 14 * k), 10 * k, 10 * k, paint(col))
    elif kind == "nasal":            # Frankish spangenhelm with nasal guard
        c.drawArc(skia.Rect(-46 * k, hy - 74 * k, 46 * k, hy + 4 * k), 180, 180, True, paint(col))
        for bx in (-22, 0, 22): c.drawLine(bx * k, hy - 34 * k, bx * 0.4 * k, hy - 72 * k, paint("#6B7280", 255, stroke=3 * k))
        c.drawRect(skia.Rect(-46 * k, hy - 40 * k, 46 * k, hy - 30 * k), paint("#6B7280")); c.drawRect(skia.Rect(8 * k, hy - 34 * k, 16 * k, hy + 6 * k), paint("#6B7280"))
    elif kind == "plume":            # Byzantine helmet with crest plume and cheek guards
        c.drawArc(skia.Rect(-46 * k, hy - 72 * k, 46 * k, hy + 6 * k), 180, 180, True, paint(col))
        c.drawRect(skia.Rect(-46 * k, hy - 34 * k, -30 * k, hy + 14 * k), paint(col))
        pl = skia.Path(); pl.moveTo(-6 * k, hy - 72 * k); pl.cubicTo(-60 * k, hy - 120 * k, -70 * k, hy - 70 * k, -40 * k, hy - 52 * k); pl.lineTo(4 * k, hy - 70 * k); pl.close()
        c.drawPath(pl, paint("#B91C1C"))
    elif kind == "shaved":           # shaved head (Kharijite Berber rebels), short beard handled by beard colour
        c.drawArc(skia.Rect(-40 * k, hy - 40 * k, 40 * k, hy + 10 * k), 200, 140, False, paint("#7A5232", 255, stroke=2 * k))

def soldier(c, x, y, s, t, fac="arab", state="idle", ph=0.0, face=1, a=255, fall=0.0, weapon=None, banner=False, kneel=0.0):
    """cartoon soldier in period costume, feet at (x, y), ~2*s tall. Built on the channel's 2D man (round head,
    rounded body). state: idle / run / attack / block / hit / flee / cheer / shoot / throw / thirst."""
    F = FAC[fac]; k = s / 100; weapon = weapon or F["weapon"]
    c.save(); c.translate(x, y)
    if fall > 0: c.rotate(-face * 88 * ease_out(clamp(fall)))
    c.scale(face, 1)
    run = state in ("run", "flee", "attack"); sw = math.sin(ph * 2 * math.pi) if run else 0.0
    bob = (abs(math.sin(ph * 2 * math.pi)) * 6 * k if run else math.sin(t * 2.6 + x * 0.01) * 2 * k)
    kn = clamp(kneel); drop = 50 * k * kn
    if fall < 0.5: c.drawOval(skia.Rect(-55 * k, -8 * k, 55 * k, 8 * k), paint("#000000", int(a * 0.28), blur=5))
    lc = F["leg_col"] if F["legs"] != "bare" else F["skin"]
    leg = paint(lc, a, stroke=18 * k, cap_round=True)
    if kn > 0:
        c.drawLine(-14 * k, -60 * k + drop, -40 * k, 0, leg); c.drawLine(14 * k, -60 * k + drop, 30 * k, -4 * k, leg)
    else:
        c.drawLine(-14 * k, -60 * k - bob, -14 * k + sw * 26 * k, 0, leg); c.drawLine(14 * k, -60 * k - bob, 14 * k - sw * 26 * k, 0, leg)
    if F["legs"] == "dhoti":         # knee dhoti with pleats
        c.drawRoundRect(skia.Rect(-34 * k, -78 * k - bob + drop, 34 * k, -34 * k - bob + drop), 12 * k, 12 * k, paint(F["leg_col"], a))
        for i in range(3): c.drawLine((-20 + i * 14) * k, -74 * k - bob + drop, (-24 + i * 14) * k, -38 * k - bob + drop, paint("#000000", int(a * 0.15), stroke=2 * k))
    for sx in (-14, 14):             # boots / feet
        fx = sx * k + (sw * 26 * k * (1 if sx < 0 else -1) if kn == 0 else (-26 * k if sx < 0 else 16 * k))
        c.drawOval(skia.Rect(fx - 12 * k, -8 * k, fx + 18 * k, 4 * k), paint("#2B1D0E" if F["legs"] != "bare" else F["skin"], a))
    by = -60 * k - bob + drop
    if F.get("cloak"):
        cl = skia.Path(); cl.moveTo(-30 * k, by - 120 * k); cl.quadTo(-80 * k - sw * 10 * k, by - 40 * k, -66 * k, by + 10 * k); cl.lineTo(10 * k, by); cl.close()
        c.drawPath(cl, paint(F["cloak"], a))
    arm_col = F["skin"] if F["body"] == "bare" else F["tunic"]
    arm = paint(arm_col, a, stroke=20 * k, cap_round=True)
    # back arm + shield
    if state in ("flee", "cheer"):
        w = math.sin(t * 14 + x) * 10 * k
        c.drawLine(-36 * k, by - 100 * k, -64 * k + w, by - 168 * k, arm); c.drawCircle(-64 * k + w, by - 172 * k, 11 * k, paint(F["skin"], a))
    elif state == "thirst":
        c.drawLine(-34 * k, by - 100 * k, -20 * k, by - 160 * k, arm); c.drawCircle(-18 * k, by - 164 * k, 11 * k, paint(F["skin"], a))
    else:
        c.drawLine(-34 * k, by - 100 * k, -50 * k, by - 50 * k, arm)
        sh = F["shield"]; shx = 30 * k if state == "block" else -36 * k
        if sh == "round" or sh == "hide":
            r = 36 * k if sh == "round" else 26 * k
            c.drawCircle(shx, by - 66 * k, r, paint(F["shield_col"], a)); c.drawCircle(shx, by - 66 * k, r, paint(INK, a, stroke=4 * k))
            c.drawCircle(shx, by - 66 * k, 9 * k, paint("#E9C46A" if sh == "round" else "#7A5232", a))
        elif sh == "big_round":
            c.drawCircle(shx, by - 70 * k, 50 * k, paint(F["shield_col"], a)); c.drawCircle(shx, by - 70 * k, 50 * k, paint(INK, a, stroke=4 * k))
            for i in range(4): c.drawLine(shx, by - 70 * k, shx + math.cos(i * math.pi / 2 + 0.4) * 50 * k, by - 70 * k + math.sin(i * math.pi / 2 + 0.4) * 50 * k, paint("#FFD23F", a, stroke=5 * k))
            c.drawCircle(shx, by - 70 * k, 12 * k, paint("#9CA3AF", a))
        elif sh == "rect":           # tall Indian rectangular shield (phalaka)
            c.drawRoundRect(skia.Rect(shx - 26 * k, by - 136 * k, shx + 26 * k, by + 6 * k), 10 * k, 10 * k, paint(F["shield_col"], a))
            c.drawRoundRect(skia.Rect(shx - 26 * k, by - 136 * k, shx + 26 * k, by + 6 * k), 10 * k, 10 * k, paint(INK, a, stroke=4 * k))
            for i in range(3): c.drawCircle(shx, by - (110 - i * 40) * k, 6 * k, paint("#E9C46A", a))
        elif sh == "oval":
            c.drawOval(skia.Rect(shx - 30 * k, by - 128 * k, shx + 30 * k, by - 8 * k), paint(F["shield_col"], a))
            c.drawOval(skia.Rect(shx - 30 * k, by - 128 * k, shx + 30 * k, by - 8 * k), paint("#D4AF37", a, stroke=5 * k))
    # body by type
    body = F["body"]
    if body == "bare":
        c.drawRoundRect(skia.Rect(-40 * k, by - 128 * k, 40 * k, by - 30 * k), 30 * k, 30 * k, paint(F["skin"], a))
        c.drawLine(-34 * k, by - 120 * k, 30 * k, by - 50 * k, paint(F["armor"], a, stroke=7 * k)); c.drawLine(34 * k, by - 120 * k, -30 * k, by - 50 * k, paint(F["armor"], a, stroke=7 * k))
        c.drawCircle(0, by - 86 * k, 8 * k, paint("#FFD23F", a))
        c.drawRect(skia.Rect(-42 * k, by - 42 * k, 42 * k, by - 28 * k), paint(F["armor"], a))
    else:
        c.drawRoundRect(skia.Rect(-44 * k, by - 128 * k, 44 * k, by + 4 * k), 32 * k, 32 * k, paint(F["tunic"], a))
        if body == "mail":
            c.drawRoundRect(skia.Rect(-42 * k, by - 124 * k, 42 * k, by - 6 * k), 28 * k, 28 * k, paint(F["armor"], int(a * 0.95)))
            for r in range(9):
                for q in range(7): c.drawCircle((-30 + q * 10 + (5 if r % 2 else 0)) * k, by - (114 - r * 12) * k, 2.6 * k, paint("#5F6B78", a))
        elif body == "lamellar":
            c.drawRoundRect(skia.Rect(-40 * k, by - 122 * k, 40 * k, by - 30 * k), 24 * k, 24 * k, paint(F["armor"], a))
            for r in range(7):
                for q in range(6): c.drawRoundRect(skia.Rect((-34 + q * 12) * k, by - (116 - r * 13) * k, (-25 + q * 12) * k, by - (105 - r * 13) * k), 2 * k, 2 * k, paint("#000000", int(a * 0.22), stroke=1.6 * k))
        elif body == "quilted":
            c.drawRoundRect(skia.Rect(-40 * k, by - 122 * k, 40 * k, by - 20 * k), 24 * k, 24 * k, paint(F["armor"], a))
            for i in range(5): c.drawLine((-30 + i * 15) * k, by - 118 * k, (-30 + i * 15) * k, by - 24 * k, paint("#000000", int(a * 0.18), stroke=2.5 * k))
        elif body == "robe":
            c.drawRoundRect(skia.Rect(-46 * k, by - 128 * k, 46 * k, by + 24 * k), 30 * k, 30 * k, paint(F["tunic"], a))
            c.drawLine(-40 * k, by - 120 * k, 36 * k, by - 10 * k, paint(F["armor"], a, stroke=12 * k))
        c.drawRect(skia.Rect(-44 * k, by - 50 * k, 44 * k, by - 40 * k), paint("#5A3A1E", a))
    # head
    hy = by - 168 * k
    if F["head"] == "turban_helm":   # mail aventail hangs behind the face, over neck and shoulders
        c.drawRoundRect(skia.Rect(-50 * k, hy - 26 * k, 50 * k, hy + 52 * k), 22 * k, 22 * k, paint("#8E9AA6", a))
        for i in range(6): c.drawLine(-46 * k, hy + (-14 + i * 11) * k, 46 * k, hy + (-14 + i * 11) * k, paint("#5F6B78", a, stroke=1.6 * k))
    c.drawCircle(0, hy, 40 * k, paint(F["skin"], a))
    if F.get("beard"): c.drawArc(skia.Rect(-14 * k, hy - 4 * k, 40 * k, hy + 40 * k), 0, 180, True, paint(F["beard"], a))
    _headgear(c, F["head"], F, hy, k)
    angry = state in ("attack", "run", "shoot", "block", "throw")
    for ex in (2, 24):
        if state == "thirst": c.drawLine((ex - 5) * k, hy - 2 * k, (ex + 5) * k, hy - 2 * k, paint(INK, a, stroke=3 * k))
        else: c.drawCircle(ex * k, hy - 2 * k, 5.5 * k, paint(INK, a))
        if angry: c.drawLine((ex - 9) * k, hy - 16 * k + (4 if ex == 24 else -1) * k, (ex + 8) * k, hy - 12 * k - (3 if ex == 24 else -2) * k, paint(INK, a, stroke=3.5 * k, cap_round=True))
    if state == "thirst":
        c.drawOval(skia.Rect(6 * k, hy + 12 * k, 20 * k, hy + 26 * k), paint("#5A1F1F", a)); c.drawOval(skia.Rect(9 * k, hy + 20 * k, 17 * k, hy + 32 * k), paint("#E76F8A", a))
        for i in range(2): c.drawCircle((40 + i * 8) * k, hy - (20 - i * 14) * k, 4 * k, paint("#7EC8F2", a))   # sweat
    elif state in ("flee", "hit") or fall > 0: c.drawOval(skia.Rect(4 * k, hy + 12 * k, 20 * k, hy + 26 * k), paint("#5A1F1F", a))
    elif state in ("attack", "cheer", "throw"): c.drawOval(skia.Rect(2 * k, hy + 12 * k, 22 * k, hy + 24 * k), paint("#5A1F1F", a))
    else: c.drawLine(4 * k, hy + 18 * k, 22 * k, hy + 17 * k, paint(INK, a, stroke=3 * k, cap_round=True))
    # front arm + weapon
    if state not in ("flee", "cheer", "thirst"):
        if weapon in ("sword", "khanda", "axe"):
            sa = (-70 + 140 * abs(math.sin(ph * 2 * math.pi * 1.5))) if state == "attack" else (-30 if state == "run" else 10)
        elif weapon == "javelin" and state == "throw":
            sa = -80 + 150 * clamp((ph % 1.0) * 2)
        else: sa = -10 if weapon == "bow" else 0
        c.save(); c.translate(30 * k, by - 104 * k); c.rotate(sa)
        thrust = (12 + 26 * max(0, math.sin(ph * 2 * math.pi * 1.5))) * k if (weapon in ("spear", "lance") and state == "attack") else 0
        c.drawLine(0, 0, 44 * k + thrust, 22 * k, arm); c.drawCircle(46 * k + thrust, 22 * k, 11 * k, paint(F["skin"], a))
        hx = 46 * k + thrust
        if weapon == "sword":
            c.drawLine(hx, 22 * k, hx + 10 * k, 22 * k - 96 * k, paint("#D9DEE5", a, stroke=8 * k, cap_round=True)); c.drawLine(34 * k, 14 * k, 58 * k, 30 * k, paint("#C9A227", a, stroke=6 * k, cap_round=True))
        elif weapon == "khanda":     # broad straight blade widening to the tip
            p = skia.Path(); p.moveTo(hx - 4 * k, 18 * k); p.lineTo(hx + 4 * k, -80 * k); p.lineTo(hx + 22 * k, -86 * k); p.lineTo(hx + 10 * k, 18 * k); p.close(); c.drawPath(p, paint("#D9DEE5", a))
            c.drawLine(32 * k, 14 * k, 60 * k, 28 * k, paint("#C9A227", a, stroke=7 * k, cap_round=True))
        elif weapon == "axe":
            c.drawLine(hx, 30 * k, hx + 8 * k, -70 * k, paint("#7A5230", a, stroke=7 * k, cap_round=True))
            p = skia.Path(); p.moveTo(hx + 6 * k, -60 * k); p.quadTo(hx + 50 * k, -80 * k, hx + 44 * k, -30 * k); p.lineTo(hx + 8 * k, -40 * k); p.close(); c.drawPath(p, paint("#C0C6CE", a))
        elif weapon in ("spear", "lance", "javelin"):
            L0, L1 = (90, 120) if weapon == "spear" else ((120, 170) if weapon == "lance" else (40, 80))
            c.drawLine(hx - L0 * k, 26 * k, hx + L1 * k, 16 * k, paint("#7A5230", a, stroke=(6 if weapon != "javelin" else 4.5) * k, cap_round=True))
            p = skia.Path(); p.moveTo(hx + L1 * k, 6 * k); p.lineTo(hx + (L1 + 30) * k, 15 * k); p.lineTo(hx + L1 * k, 26 * k); p.close(); c.drawPath(p, paint("#D9DEE5", a))
            if weapon == "lance" and F["banner"] in ("umayyad", "byz", "varaha"):
                pn = skia.Path(); pn.moveTo(hx + (L1 - 10) * k, 14 * k); pn.lineTo(hx + (L1 - 40) * k, -6 * k + math.sin(t * 9) * 4 * k); pn.lineTo(hx + (L1 - 44) * k, 18 * k); pn.close()
                c.drawPath(pn, paint({"umayyad": "#FFFFFF", "byz": "#6B21A8", "varaha": "#E8A23A"}[F["banner"]], a))
        elif weapon == "bow":        # composite recurve bow
            bw = skia.Path(); bw.moveTo(50 * k, -46 * k); bw.cubicTo(80 * k, -40 * k, 66 * k, 0, 70 * k, 22 * k); bw.cubicTo(66 * k, 44 * k, 80 * k, 84 * k, 50 * k, 90 * k)
            c.drawPath(bw, paint("#6B4423", a, stroke=6 * k))
            pull = 26 * k * (0.5 + 0.5 * math.sin(ph * 2 * math.pi)) if state == "shoot" else 0
            c.drawLine(50 * k, -46 * k, 50 * k - pull, 22 * k, paint("#EEEEEE", a, stroke=2 * k)); c.drawLine(50 * k - pull, 22 * k, 50 * k, 90 * k, paint("#EEEEEE", a, stroke=2 * k))
        c.restore()
    if banner:
        c.drawLine(-20 * k, by - 40 * k, -20 * k, by - 300 * k, paint("#6B4423", a, stroke=6 * k))
        c.save(); c.translate(-20 * k, by - 300 * k); c.skew(0, math.sin(t * 6) * 0.06)
        banner_emblem(c, F["banner"], 0, 0, 110 * k, 78 * k, a); c.restore()
    c.restore()

def soldier_fly(c, x, y, s, t, fac, k, face=1, dist=420, height=260, spin=540, a=255):
    """a soldier knocked flying (elephant trunk swat, cavalry impact): arc + spin, lands on his back."""
    kk = clamp(k); fx = x - face * dist * kk; fy = y - height * 4 * kk * (1 - kk)
    c.save(); c.translate(fx, fy - s * 0.9); c.rotate(-face * spin * ease_out(kk)); c.translate(0, s * 0.9)
    soldier(c, 0, 0, s, t, fac, "hit", 0, face, a); c.restore()
    if kk >= 1: pass

def horse(c, x, y, s, t, ph, face=1, col="#8B5A2B", rider=None, a=255, fall=0.0, capar=None, mane="#2B1D0E"):
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
    for i in range(5): c.drawLine((70 + i * 12) * k, (-170 - i * 12) * k - bob, (58 + i * 12) * k, (-150 - i * 12) * k - bob, paint(mane, a, stroke=7 * k, cap_round=True))
    c.drawLine(-95 * k, -130 * k - bob, -140 * k + math.sin(g * 1.3) * 10 * k, -90 * k - bob, paint(mane, a, stroke=12 * k, cap_round=True))
    if capar:                        # caparison / horse armour cloth (Byzantine, Indian, general)
        cp = skia.Path(); cp.moveTo(-92 * k, -140 * k - bob); cp.lineTo(80 * k, -140 * k - bob); cp.lineTo(70 * k, -78 * k - bob)
        for i in range(8): cp.lineTo((70 - i * 21) * k, (-70 if i % 2 else -82) * k - bob)
        cp.lineTo(-92 * k, -82 * k - bob); cp.close(); c.drawPath(cp, paint(capar, a)); c.drawPath(cp, paint("#E9C46A", a, stroke=3 * k))
    c.drawRoundRect(skia.Rect(-40 * k, -162 * k - bob, 30 * k, -138 * k - bob), 8 * k, 8 * k, paint("#9B2226" if not capar else "#E9C46A", a))
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
                 ground=(800, 1065), seed=5, volley=None, base=118, linear=False, launch=None):
        self.linear = linear; self.launch = launch     # launch = (t_rel, fraction, side "L"/"R")
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
            if self.launch and u["side"] == self.launch[2] and u["back"] < 0.25 and u["r"] < self.launch[1] and u["kind"] != "eleph":
                tl = self.launch[0] + u["r"] * 0.9
                if lt > tl:
                    soldier_fly(c, x, u["y"], s, t, u["fac"], seg(lt, tl, tl + 0.9), face=u["d"], dist=380 + u["r"] * 300, height=240 + u["r"] * 200)
                    continue
            if u["kind"] == "cav":
                HS = FAC[u["fac"]]["horses"]; col = HS[int(u["r"] * 997) % len(HS)]
                horse(c, x, u["y"], s * 1.15, t, ph, face, col, rider_fn(u["fac"], "flee" if state == "flee" else "attack", ph, t, face), a, fall, capar=FAC[u["fac"]]["capar"],
                      mane="#E9DCC0" if col in ("#C8A26B",) else "#2B1D0E")
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
