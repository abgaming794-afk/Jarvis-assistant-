"""Full-body minimal toon characters (the 'documentary toon' look: big round head, dot eyes,
thin limbs, flat colours, thin dark outline). Same presets/spec keys as characters.py.

make(spec, expr="neutral", pose="idle", height=400, mouth=0, blink=False, face=1, walk=0.0) -> RGBA
Design space 300 x 640 units, head centre (150, 150), feet at y = 630.
"""
import functools, json, math
from common import Pen, hexc, shade
from characters import resolve, PRESETS  # noqa: F401  (re-exported)

W, H = 300, 560
HX, HY, R = 150, 120, 92
OL = 3.2
BODY_TOP, BODY_BOT, LEG_BOT = 176, 418, 548
SKIRT = ("dress", "saree", "ruff_dress", "robe", "jama", "royal", "shawl", "sherwani")
LIMB = "#1f1a1a"
LIMB_W = 5.5


def _hw(c):
    return {"fat": 84, "thin": 54, "normal": 68}[c.get("body", "normal")]


def _shade_right(p, x0, y0, x1, y1, r, amt=40):
    """Darken the right ~35% of a pill shape (soft cel shading)."""
    layer, d = p.overlay()
    d.rounded_rectangle(p.box((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - 2, (y1 - y0) / 2 - 2), radius=r * p.s,
                        fill=(0, 0, 0, amt))
    cut = x0 + (x1 - x0) * 0.62
    d.rectangle([0, 0, (cut + p.ox) * p.s, layer.height], fill=(0, 0, 0, 0))
    p.merge(layer)


def _body(p, c):
    o, col, acc = c["outfit"], c["color"], c.get("accent", "#efe9dc")
    hw = _hw(c)
    long = o in SKIRT
    bot = 500 if long else BODY_BOT
    fill = c["skin"] if o == "bare" else col
    rad = hw if not long else 56
    p.rrect(HX - hw, BODY_TOP, HX + hw, bot, rad, fill, w=OL)
    if o == "suit":
        p.poly([(HX - 26, BODY_TOP + 4), (HX, BODY_TOP + 34), (HX - 8, BODY_TOP + 2)], "#f4f1ea", w=2)
        p.poly([(HX + 26, BODY_TOP + 4), (HX, BODY_TOP + 34), (HX + 8, BODY_TOP + 2)], "#f4f1ea", w=2)
        p.line([(HX, BODY_TOP + 30), (HX + 2, BODY_TOP + 120)], acc, 9)
        p.line([(HX - 30, BODY_TOP + 8), (HX - 6, BODY_TOP + 110)], shade(col, .6), 2.5)
        p.line([(HX + 30, BODY_TOP + 8), (HX + 6, BODY_TOP + 110)], shade(col, .6), 2.5)
    elif o == "labcoat":
        p.poly([(HX - 22, BODY_TOP + 2), (HX + 22, BODY_TOP + 2), (HX, BODY_TOP + 46)], "#9cc0e0", w=2)
        p.line([(HX, BODY_TOP + 46), (HX, bot - 6)], None, 2.5)
    elif o in ("redcoat", "army"):
        lap = acc if o == "redcoat" else shade(col, .8)
        p.rrect(HX - 14, BODY_TOP + 6, HX + 14, bot - 8, 8, lap, w=2)
        for k in range(5):
            p.ell(HX, BODY_TOP + 30 + k * 40, 3.5, 3.5, "#e8c547", w=1.2)
        if o == "redcoat":
            p.line([(HX - hw + 14, BODY_TOP + 24), (HX + hw - 10, bot - 40)], "#f4f1ea", 8)
            for sx in (-1, 1):
                p.ell(HX + sx * (hw - 12), BODY_TOP + 16, 16, 7, "#e8c547", w=1.5)
        else:
            p.rrect(HX - hw + 3, BODY_TOP + 150, HX + hw - 3, BODY_TOP + 162, 3, "#3a2a1a", ol=False)
    elif o in ("kurta", "jama", "royal", "sherwani", "robe"):
        p.line([(HX + 6, BODY_TOP + 8), (HX + 6, BODY_TOP + 110)], shade(col, .7), 2.5)
        if o in ("jama", "royal", "sherwani"):
            p.rrect(HX - hw + 2, BODY_TOP + 150, HX + hw - 2, BODY_TOP + 166, 4, acc, w=1.5)
            p.line([(HX - 20, BODY_TOP + 166), (HX - 26, bot - 8)], shade(col, .75), 2.5)
    elif o == "doublet":
        for k in range(9):
            p.ell(HX - 40 + k * 10, BODY_TOP + 4, 8, 6, "#fbf8f0", w=1.2)
        for k in range(4):
            p.ell(HX, BODY_TOP + 34 + k * 34, 3.5, 3.5, acc, w=1.2)
    elif o == "bare":
        p.poly([(HX - hw + 6, BODY_TOP + 20), (HX - hw + 28, BODY_TOP + 4), (HX + hw - 6, bot - 70),
                (HX + hw - 26, bot - 50)], col, w=2)
        p.rrect(HX - hw + 1, bot - 70, HX + hw - 1, bot - 1, 30, col, w=2)
    elif o == "ruff_dress":
        for k in range(11):
            p.ell(HX - 50 + k * 10, BODY_TOP + 4, 9, 7, "#fbf8f0", w=1.2)
        p.poly([(HX - 22, BODY_TOP + 20), (HX + 22, BODY_TOP + 20), (HX + 8, BODY_TOP + 140), (HX - 8, BODY_TOP + 140)], acc, w=2)
    elif o == "dress":
        p.poly([(HX - 22, BODY_TOP + 2), (HX + 22, BODY_TOP + 2), (HX, BODY_TOP + 30)], c["skin"], w=2)
    elif o == "saree":
        p.poly([(HX - hw + 4, BODY_TOP + 30), (HX - hw + 30, BODY_TOP + 6), (HX + hw - 4, bot - 40), (HX + hw - 30, bot - 8)], acc, w=2)
    elif o == "shawl":
        p.poly([(HX - hw + 2, BODY_TOP + 20), (HX + hw - 2, BODY_TOP + 20), (HX + hw - 2, BODY_TOP + 90), (HX - hw + 2, BODY_TOP + 120)], shade(col, .9), w=2)
    elif o == "apron":
        p.rrect(HX - hw + 6, BODY_TOP + 120, HX + 10, bot - 2, 30, "#f2f0ea", w=2)
        p.poly([(HX - 16, BODY_TOP + 2), (HX + 16, BODY_TOP + 2), (HX, BODY_TOP + 20)], "#f4f1ea", w=2)
        p.ell(HX + 30, BODY_TOP + 70, 9, 9, "#c9302c", w=1.5)
    if c.get("jewel"):
        for k in range(7):
            t = k / 6
            p.ell(HX - 26 + 52 * t, BODY_TOP + 10 + 16 * (1 - (2 * t - 1) ** 2), 3, 3, "#f6f1e3", w=1)
    _shade_right(p, HX - hw, BODY_TOP, HX + hw, bot, rad, 34)
    return hw, bot


def _legs(p, c, bot, walk):
    sw = math.sin(walk * 2 * math.pi) * 26
    foot = LEG_BOT if bot < 480 else LEG_BOT + 4
    for sx, ph in ((-1, 1), (1, -1)):
        x0 = HX + sx * 22
        p.line([(x0, bot - 8), (x0 + ph * sw, foot)], LIMB, LIMB_W)


# arm = shoulder offset sign + list of points relative to the shoulder (elbow optional)
ARMS = {
    "idle": ([(-12, 124)], [(12, 124)]),
    "point": ([(-12, 124)], [(70, -6), (128, -24)]),
    "up": ([(-12, 124)], [(40, -60), (52, -132)]),
    "wave": ([(-12, 124)], [(60, -40), (76, -104)]),
    "cheer": ([(-40, -70), (-56, -136)], [(40, -70), (56, -136)]),
    "chin": ([(-12, 124)], [(30, 56), (-20, 6)]),
    "think": ([(-12, 124)], [(30, 56), (-24, -6)]),
    "hold": ([(-12, 124)], [(50, 40), (92, 52)]),
    "give": ([(-12, 124)], [(70, 30), (128, 40)]),
    "shrug": ([(-50, 30), (-84, -20)], [(50, 30), (84, -20)]),
    "fist": ([(-12, 124)], [(50, -20), (52, -96)]),
    "cross": ([(30, 70), (110, 60)], [(-30, 70), (-110, 60)]),
    "type": ([(-10, 70), (40, 96)], [(10, 70), (-40, 96)]),
    "hips": ([(-44, 46), (-6, 96)], [(44, 46), (6, 96)]),
    "bow": ([(-4, 110)], [(4, 110)]),
    "head": ([(-40, -40), (-26, -120)], [(40, -40), (26, -120)]),
}


def _shoulders(c):
    hw = _hw(c)
    return (HX - hw + 8, BODY_TOP + 52), (HX + hw - 8, BODY_TOP + 52)


def _arm(p, c, sh, pts):
    path = [sh] + [(sh[0] + dx, sh[1] + dy) for dx, dy in pts]
    p.line(path, LIMB, LIMB_W)
    hx, hy = path[-1]
    p.ell(hx, hy, 6, 6, LIMB, ol=False)


def _hair_back(p, c):
    h, col = c["hair"], c["hair_color"]
    if c.get("hat") in ("veil", "keffiyeh"):
        p.rrect(HX - R - 10, HY - R - 6, HX + R + 10, 300, 70, c["hat_color"])
    if h in ("long",):
        p.rrect(HX - R - 6, HY - 40, HX + R + 6, 300, 60, col)
    elif h == "long_m":
        p.rrect(HX - R - 4, HY - 40, HX + R + 4, 236, 40, col)
    elif h == "bob":
        p.rrect(HX - R - 8, HY - R - 6, HX + R + 8, HY + 56, 70, col)
    elif h == "bun":
        p.ell(HX, HY - R - 6, 30, 24, col)
    elif h == "curly":
        for k in range(8):
            a = k / 7
            p.ell(HX - R + 2 * R * a, HY + 50 + 20 * abs(a - .5), 22, 22, col)
    elif h == "wig":
        for sx in (-1, 1):
            for k in range(2):
                p.ell(HX + sx * (R - 4), HY + 10 + k * 26, 18, 14, col, w=2.5)


def _hair_front(p, c):
    h, col, hat = c["hair"], c["hair_color"], c.get("hat")
    covered = hat in ("turban", "pagdi", "keffiyeh", "veil", "helmet", "chinese_hat")
    if h == "bald" or (covered and h not in ("long", "bob")):
        if h == "bald":
            for sx in (-1, 1):
                p.ell(HX + sx * (R - 8), HY + 4, 12, 22, col, w=2.5)
        return
    if h == "balding":
        for sx in (-1, 1):
            p.ell(HX + sx * (R - 10), HY, 16, 30, col, w=2.5)
        return
    line = HY - 34
    if h == "messy":
        pts = [(HX - R + 2, line + 20)]
        for k in range(11):
            a = k / 10
            r = R + (18 if k % 2 else 4)
            ang = math.pi * (1 - a)
            pts.append((HX + math.cos(ang) * r, HY - 10 - math.sin(ang) * r))
        pts.append((HX + R - 2, line + 20))
        p.poly(pts, col, w=2.5)
        return
    p.chord(HX, line + 6, R + 2, R - 22 + 6, 180, 360, col, w=2.5)
    if h == "side":
        p.poly([(HX - R + 10, line + 6), (HX + 10, line - 34), (HX + R - 4, line + 8), (HX + 30, line - 10)], col, w=2.5)
    elif h in ("short", "long_m", "wig", "curly", "bob", "long", "bun"):
        for k in range(4):
            p.ell(HX - 48 + k * 32, line + 6, 18, 10, col, ol=False)
    for sx in (-1, 1):
        p.rrect(HX + sx * (R - 12) - 8, line, HX + sx * (R - 12) + 8, line + 34, 6, col, ol=False)


def _hat(p, c):
    hat, col = c.get("hat"), c["hat_color"]
    if not hat:
        return
    dk = shade(col, 0.72)
    top = HY - R
    if hat in ("turban", "pagdi"):
        p.ell(HX, top + 26, R + 14, 50, col, w=3)
        for k in range(3):
            p.arc(HX, top + 60 - k * 18, R + 4 - k * 10, 30, 200, 340, dk, 2.5)
        p.ell(HX + 6, top + 18, 9, 11, "#c9302c", w=2)
        if hat == "turban":
            p.poly([(HX + 2, top + 10), (HX + 22, top - 40), (HX + 30, top - 36), (HX + 10, top + 12)], "#f6f1e3", w=2)
    elif hat == "crown":
        y = top + 16
        p.poly([(HX - 56, y + 22), (HX - 56, y - 26), (HX - 30, y - 4), (HX, y - 40), (HX + 30, y - 4),
                (HX + 56, y - 26), (HX + 56, y + 22)], col, w=3)
        p.ell(HX, y + 6, 7, 7, "#c9302c", w=2)
    elif hat == "tiara":
        p.poly([(HX - 44, top + 22), (HX, top - 10), (HX + 44, top + 22)], col, w=2.5)
    elif hat == "tricorn":
        p.poly([(HX - 120, top + 34), (HX, top - 36), (HX + 120, top + 34), (HX, top + 14)], col, w=3)
        p.line([(HX - 120, top + 34), (HX, top + 14), (HX + 120, top + 34)], "#e8c547", 4)
    elif hat == "wide_hat":
        p.ell(HX, top + 28, 124, 18, col, w=3)
        p.rrect(HX - 62, top - 36, HX + 62, top + 28, 14, col, w=3)
        p.rrect(HX - 10, top + 6, HX + 10, top + 24, 3, "#e8c547", w=2)
    elif hat == "top_hat":
        p.ell(HX, top + 24, 108, 16, col, w=3)
        p.rrect(HX - 56, top - 76, HX + 56, top + 24, 8, col, w=3)
        p.rrect(HX - 57, top + 2, HX + 57, top + 14, 2, "#a3233a", w=2)
    elif hat == "fedora":
        p.ell(HX, top + 26, 114, 18, col, w=3)
        p.rrect(HX - 64, top - 30, HX + 64, top + 26, 24, col, w=3)
        p.rrect(HX - 65, top + 4, HX + 65, top + 16, 2, dk, w=2)
    elif hat == "helmet":
        p.chord(HX, top + 52, R + 14, 76, 180, 360, col, w=3)
        p.rrect(HX - R - 22, top + 44, HX + R + 22, top + 56, 6, dk, w=2.5)
    elif hat == "pith_helmet":
        p.ell(HX, top + 34, R + 28, 20, col, w=3)
        p.chord(HX, top + 34, 80, 70, 180, 360, col, w=3)
    elif hat == "peak_cap":
        p.ell(HX, top + 12, R + 6, 34, col, w=3)
        p.rrect(HX - R + 4, top + 16, HX + R - 4, top + 42, 10, dk, w=2.5)
        p.chord(HX + 30, top + 44, 70, 14, 0, 180, "#1d1d24", w=2.5)
    elif hat == "cap":
        p.chord(HX, top + 40, R - 6, 40, 180, 360, col, w=3)
    elif hat in ("veil", "keffiyeh"):
        p.chord(HX, top + 50, R + 10, 58, 180, 360, col, w=3)
        if hat == "keffiyeh":
            p.rrect(HX - R - 8, top + 22, HX + R + 8, top + 34, 6, "#1d1d24", w=2)
    elif hat == "chinese_hat":
        p.chord(HX, top + 40, R, 56, 180, 360, col, w=3)
        p.ell(HX, top - 14, 10, 10, "#b3202a", w=2)


def _face(p, c, expr, mouth, blink, fx):
    ex, ey = 30, HY + 8
    col = "#1b1411"
    sun = c.get("glasses") == "sunglasses"
    # eyes
    for sx in (-1, 1):
        x = HX + fx + sx * ex
        if sun:
            continue
        if blink or expr in ("laugh", "happy_closed"):
            p.arc(x, ey + 4, 9, 7, 200, 340, col, 3.4)
        elif expr == "shocked":
            p.ell(x, ey, 10, 12, "#ffffff", w=2.4)
            p.ell(x, ey, 4.5, 5, col, ol=False)
        elif expr in ("smug", "scheming", "bored"):
            p.ell(x, ey + 2, 6, 6, col, ol=False)
            p.line([(x - 10, ey - 3), (x + 10, ey - 3)], col, 3.2)
        else:
            p.ell(x, ey, 5.6, 6.8, col, ol=False)
    if sun:
        p.rrect(HX + fx - 52, ey - 12, HX + fx - 8, ey + 12, 8, "#151215", w=2)
        p.rrect(HX + fx + 8, ey - 12, HX + fx + 52, ey + 12, 8, "#151215", w=2)
        p.line([(HX + fx - 10, ey - 6), (HX + fx + 10, ey - 6)], col, 3)
    elif c.get("glasses") in ("round", "square"):
        for sx in (-1, 1):
            x = HX + fx + sx * ex
            if c["glasses"] == "round":
                p.d.ellipse(p.box(x, ey, 17, 16), outline=hexc("#2a2020"), width=p._w(3))
            else:
                p.d.rounded_rectangle(p.box(x, ey, 19, 14), radius=5 * p.s, outline=hexc("#2a2020"), width=p._w(3))
        p.line([(HX + fx - 13, ey - 2), (HX + fx + 13, ey - 2)], "#2a2020", 3)
    # brows (only when expressive)
    by = ey - 22
    bro = {"angry": (-6, 5), "shout": (-6, 5), "sad": (5, -6), "worried": (5, -6), "shocked": (-8, -8),
           "thinking": (2, -4)}
    if expr in bro:
        do, di = bro[expr]
        for sx in (-1, 1):
            x = HX + fx + sx * ex
            p.line([(x + sx * 12, by + do), (x - sx * 8, by + di)], col, 3.2)
    # facial hair under the mouth
    f = c.get("facial")
    hc = c["hair_color"]
    my = HY + 46
    if f in ("beard", "full_beard"):
        p.chord(HX + fx * 0.5, HY + 10, R - 6, R - 12, 15, 165, hc, w=2.5)
        p.ell(HX + fx, my, 15, 9, c["skin"], ol=False)
    if f == "goatee":
        p.poly([(HX + fx - 10, my + 14), (HX + fx + 10, my + 14), (HX + fx, my + 36)], hc, w=2)
    # mouth
    mx = HX + fx * 1.1
    if expr in ("happy", "laugh", "proud") or mouth:
        hgt = 14 if (expr in ("laugh",) or mouth) else 9
        p.chord(mx, my - 4, 14, hgt, 0, 180, "#5a1d1d", w=2.4)
    elif expr in ("neutral", "thinking"):
        p.line([(mx - 9, my), (mx + 9, my)], col, 3)
    elif expr in ("smug", "scheming"):
        p.line([(mx - 10, my + 1), (mx + 4, my + 2), (mx + 13, my - 5)], col, 3)
    elif expr in ("sad", "worried"):
        p.arc(mx, my + 8, 10, 7, 200, 340, col, 3)
    elif expr in ("shocked", "shout"):
        p.ell(mx, my + 2, 8 if expr == "shocked" else 12, 10 if expr == "shocked" else 12, "#5a1d1d", w=2.4)
    elif expr == "angry":
        p.arc(mx, my + 8, 11, 6, 200, 340, col, 3.4)
    else:
        p.line([(mx - 9, my), (mx + 9, my)], col, 3)
    if f in ("mustache", "full_beard", "beard", "handlebar", "long_mustache", "goatee"):
        p.chord(HX + fx - 11, my - 8, 13, 7, 180, 360, hc, w=2)
        p.chord(HX + fx + 11, my - 8, 13, 7, 180, 360, hc, w=2)
        if f == "long_mustache":
            p.line([(HX + fx - 22, my - 6), (HX + fx - 28, my + 30)], hc, 4)
            p.line([(HX + fx + 22, my - 6), (HX + fx + 28, my + 30)], hc, 4)
    if expr in ("worried", "shocked"):
        p.ell(HX + fx + 64, HY - 30, 7, 11, "#8ccdf2", w=2)
    if expr == "sad":
        p.ell(HX + fx - 34, ey + 18, 5, 8, "#8ccdf2", w=1.8)
    if c.get("age") == "old":
        p.arc(HX + fx, HY - 44, 22, 5, 200, 340, shade(c["skin"], 0.75), 2)


def _back_head(p, c):
    p.ell(HX, HY, R + 2, R - 2, c["skin"], w=OL)
    if c.get("hair") != "bald":
        p.chord(HX, HY, R + 2, R - 2, 140, 400, c["hair_color"], w=OL)


@functools.lru_cache(maxsize=2048)
def _cached(key, expr, pose, height, mouth, blink, face, walk_q, back=False):
    c = json.loads(key)
    ss = max(0.4, height * 2.0 / H)
    p = Pen(W, H, ss, lw=OL, oy=0)
    arms = ARMS.get(pose, ARMS["idle"])
    sl, sr = _shoulders(c)
    fx = 0 if back else (9 if face else 0)
    if not back:
        _hair_back(p, c)
    hw = _hw(c)
    bot = 500 if c["outfit"] in SKIRT else BODY_BOT
    _legs(p, c, bot, walk_q / 16)
    _body(p, c)
    if back:
        _back_head(p, c)
        _hat(p, c)
        _arm(p, c, sl, [(-12, 124)])
        _arm(p, c, sr, [(12, 124)])
        return p.result(height)
    p.ell(HX, HY, R + 2, R - 2, c["skin"], w=OL)
    _hair_front(p, c)
    _face(p, c, expr, mouth, blink, fx)
    _hat(p, c)
    _arm(p, c, sl, arms[0])
    _arm(p, c, sr, arms[1])
    return p.result(height)


def make(spec, expr="neutral", pose="idle", height=400, mouth=0, blink=False, face=1, walk=0.0, back=False):
    c = resolve(spec)
    return _cached(json.dumps(c, sort_keys=True), expr, pose, int(height), int(mouth), bool(blink), int(face),
                   int(walk * 16) % 16, bool(back))


def hand_point(pose, height, spec=None):
    c = resolve(spec or {})
    _, sr = _shoulders(c)
    pts = ARMS.get(pose, ARMS["idle"])[1]
    k = height / H
    return (sr[0] + pts[-1][0]) * k, (sr[1] + pts[-1][1]) * k


EXPRESSIONS = ["neutral", "happy", "laugh", "proud", "smug", "scheming", "thinking", "angry", "shout", "shocked",
               "sad", "worried"]

if __name__ == "__main__":
    import sys
    from PIL import Image, ImageDraw
    names = list(PRESETS)
    cols = 9
    tw, th = 200, 330
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * tw, rows * th), (214, 205, 186, 255))
    poses = list(ARMS)
    for i, n in enumerate(names):
        spr = make({"preset": n}, EXPRESSIONS[i % len(EXPRESSIONS)], poses[i % len(poses)], 300)
        x = (i % cols) * tw + (tw - spr.width) // 2
        y = (i // cols) * th
        sheet.alpha_composite(spr, (x, y))
        ImageDraw.Draw(sheet).text(((i % cols) * tw + 4, y + 312), f"{n}/{EXPRESSIONS[i % 12]}/{poses[i % len(poses)]}",
                                   fill=(0, 0, 0))
    sheet.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "toon_sheet.png")
