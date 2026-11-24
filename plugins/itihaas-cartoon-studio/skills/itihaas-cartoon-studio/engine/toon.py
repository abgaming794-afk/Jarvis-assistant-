"""Full-body minimal toon characters (the 'documentary toon' look: big round head, dot eyes,
thin limbs, flat colours, thin dark outline). Same presets/spec keys as characters.py.

make(spec, expr="neutral", pose="idle", height=400, mouth=0, blink=False, face=1, walk=0.0) -> RGBA
Design space 300 x 640 units, head centre (150, 150), feet at y = 630.
"""
import functools, json, math
from common import Pen, hexc, shade
from characters import resolve, PRESETS  # noqa: F401  (re-exported)

W, H = 300, 640
HX, HY, R = 150, 150, 92
OL = 3.6
PANTS = {"suit": None, "redcoat": "#efe9dc", "army": None, "doublet": "#2a2a33", "labcoat": "#3a3f4a",
         "kurta": "#efe9dc", "jama": "#efe9dc", "royal": "#efe9dc", "bare": "#efe9dc", "shawl": "#efe9dc"}
SKIRT = ("dress", "saree", "ruff_dress", "robe", "jama", "royal", "shawl")


def _legs(p, c, walk):
    o = c["outfit"]
    pc = PANTS.get(o) or shade(c["color"], 0.6)
    if o in ("suit", "army", "labcoat"):
        pc = shade(c["color"], 0.75) if o != "labcoat" else "#3a3f4a"
    sw = math.sin(walk * 2 * math.pi) * 22
    for sx, ph in ((-1, 1), (1, -1)):
        x0 = HX + sx * 22
        x1 = x0 + ph * sw
        p.line([(x0, 420), (x1, 600)], None, 15 + 2 * OL)
        p.line([(x0, 420), (x1, 600)], pc, 15)
        p.ell(x1 + 9, 608, 21, 11, "#1e1a1a")


def _skirt(p, c):
    o, col = c["outfit"], c["color"]
    if o == "jama" or o == "royal":
        p.poly([(HX - 56, 372), (HX + 56, 372), (HX + 82, 560), (HX - 82, 560)], col)
        p.rrect(HX - 56, 362, HX + 56, 384, 6, c["accent"], w=2)
        p.line([(HX - 30, 400), (HX - 40, 560)], shade(col, 0.8), 4)
        for sx in (-1, 1):
            p.line([(HX + sx * 20, 560), (HX + sx * 22, 600)], None, 15 + 2 * OL)
            p.line([(HX + sx * 20, 560), (HX + sx * 22, 600)], "#efe9dc", 15)
            p.ell(HX + sx * 22 + 9, 608, 21, 11, "#3a2618")
        return
    p.poly([(HX - 54, 372), (HX + 54, 372), (HX + 86, 606), (HX - 86, 606)], col)
    if o == "saree":
        p.poly([(HX - 54, 372), (HX + 10, 372), (HX + 86, 606), (HX + 30, 606)], c.get("accent", "#e8c547"))
    for sx in (-1, 1):
        p.ell(HX + sx * 26 + 8, 612, 19, 9, "#1e1a1a")


def _torso(p, c):
    o, col, acc = c["outfit"], c["color"], c["accent"]
    body = c.get("body", "normal")
    hw = {"fat": 70, "thin": 44, "normal": 54}[body]
    top_col = c["skin"] if o == "bare" else col
    p.rrect(HX - hw, 228, HX + hw, 428, 34, top_col)
    if o == "suit":
        p.poly([(HX - 22, 230), (HX + 22, 230), (HX, 285)], "#f4f1ea", w=2.5)
        p.poly([(HX - 6, 238), (HX + 6, 238), (HX + 9, 300), (HX, 312), (HX - 9, 300)], acc, w=2.5)
        p.line([(HX - 24, 232), (HX - 4, 320)], shade(col, 0.6), 3)
        p.line([(HX + 24, 232), (HX + 4, 320)], shade(col, 0.6), 3)
    elif o == "labcoat":
        p.poly([(HX - 20, 230), (HX + 20, 230), (HX, 280)], "#9cc0e0", w=2.5)
        p.line([(HX, 280), (HX, 428)], None, 3)
    elif o in ("redcoat", "army"):
        lap = acc if o == "redcoat" else shade(col, 0.8)
        p.rrect(HX - 18, 232, HX + 18, 428, 6, lap, w=2.5)
        for k in range(4):
            p.ell(HX, 252 + k * 42, 4, 4, "#e8c547", w=1.5)
        if o == "redcoat":
            p.line([(HX - hw + 6, 236), (HX + hw - 6, 420)], "#f4f1ea", 9)
            for sx in (-1, 1):
                p.rrect(HX + sx * (hw - 14) - 16, 226, HX + sx * (hw - 14) + 16, 240, 6, "#e8c547", w=2)
    elif o in ("kurta", "jama", "royal", "sherwani", "robe"):
        p.line([(HX, 236), (HX, 330)], shade(col, 0.7), 3)
        if o in ("jama", "royal"):
            p.rrect(HX - hw, 366, HX + hw, 384, 6, acc, w=2)
    elif o == "doublet":
        p.poly([(HX - 34, 226), (HX + 34, 226), (HX, 254)], "#f4f1ea", w=2.5)
        for k in range(4):
            p.ell(HX, 270 + k * 36, 4, 4, acc, w=1.5)
    elif o == "bare":
        p.poly([(HX - hw + 2, 240), (HX - hw + 24, 228), (HX + hw - 4, 410), (HX + hw - 28, 428)], col, w=2.5)
    elif o == "ruff_dress":
        for k in range(9):
            p.ell(HX - 48 + k * 12, 232, 10, 8, "#fbf8f0", w=1.8)
        p.poly([(HX - 30, 250), (HX + 30, 250), (HX + 10, 380), (HX - 10, 380)], acc, w=2.5)
    elif o == "dress":
        p.poly([(HX - 26, 228), (HX + 26, 228), (HX, 258)], c["skin"], ol=False)
    elif o == "shawl":
        p.poly([(HX - hw, 236), (HX + hw, 236), (HX + hw, 300), (HX - hw, 330)], shade(col, 0.92), w=2.5)
    if c.get("jewel"):
        for k in range(7):
            t = k / 6
            p.ell(HX - 26 + 52 * t, 244 + 18 * (1 - (2 * t - 1) ** 2), 3.5, 3.5, "#f6f1e3", w=1.2)
    return hw


ARMS = {  # (shoulder, hand) for viewer-left arm and viewer-right arm, relative to HX
    "idle": (((-46, 248), (-62, 392)), ((46, 248), (62, 392))),
    "point": (((-46, 248), (-62, 392)), ((46, 248), (128, 238))),
    "up": (((-46, 248), (-62, 392)), ((46, 248), (86, 140))),
    "cheer": (((-46, 248), (-92, 140)), ((46, 248), (92, 140))),
    "chin": (((-46, 248), (-62, 392)), ((46, 248), (14, 222))),
    "think": (((-46, 248), (-62, 392)), ((46, 248), (10, 214))),
    "hold": (((-46, 248), (-62, 392)), ((46, 248), (96, 318))),
    "give": (((-46, 248), (-62, 392)), ((46, 248), (120, 300))),
    "shrug": (((-46, 248), (-108, 262)), ((46, 248), (108, 262))),
    "fist": (((-46, 248), (-62, 392)), ((46, 248), (96, 180))),
    "cross": (((-46, 248), (34, 330)), ((46, 248), (-34, 330))),
    "type": (((-46, 248), (-10, 340)), ((46, 248), (40, 340))),
    "hips": (((-46, 248), (-58, 350)), ((46, 248), (58, 350))),
    "bow": (((-46, 248), (-10, 380)), ((46, 248), (10, 380))),
    "head": (((-46, 248), (-80, 120)), ((46, 248), (80, 120))),  # hands on head (panic)
}


def _arm(p, c, sh, hand, sleeve):
    a = (HX + sh[0], sh[1])
    b = (HX + hand[0], hand[1])
    p.line([a, b], None, 15 + 2 * OL)
    p.line([a, b], sleeve, 15)
    p.ell(b[0], b[1], 11, 11, c["skin"], w=2.6)


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
            p.ell(x, ey, 6.2, 7.4, col, ol=False)
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


@functools.lru_cache(maxsize=2048)
def _cached(key, expr, pose, height, mouth, blink, face, walk_q):
    c = json.loads(key)
    ss = max(0.4, height * 2.0 / H)
    p = Pen(W, H, ss, lw=OL, oy=0)
    arms = ARMS.get(pose, ARMS["idle"])
    sleeve = c["skin"] if c["outfit"] == "bare" else c["color"]
    if c["outfit"] == "labcoat":
        sleeve = "#eeeeea"
    fx = 10 if face else 0
    _hair_back(p, c)
    skirt = c["outfit"] in SKIRT
    if not skirt:
        _legs(p, c, walk_q / 16)
    back_arm = pose in ("idle", "hips", "bow", "type") or pose in ("point", "up", "chin", "think", "hold", "give", "fist")
    if back_arm:
        _arm(p, c, *arms[0], sleeve)
    _torso(p, c)
    if skirt:
        _skirt(p, c)
    if pose in ("idle", "hips", "bow", "type"):
        _arm(p, c, *arms[1], sleeve)
    p.ell(HX, HY, R + 2, R - 2, c["skin"], w=OL)
    _hair_front(p, c)
    _face(p, c, expr, mouth, blink, fx)
    _hat(p, c)
    if not back_arm:
        _arm(p, c, *arms[0], sleeve)
        _arm(p, c, *arms[1], sleeve)
    elif pose not in ("idle", "hips", "bow", "type"):
        _arm(p, c, *arms[1], sleeve)
    return p.result(height)


def make(spec, expr="neutral", pose="idle", height=400, mouth=0, blink=False, face=1, walk=0.0):
    c = resolve(spec)
    return _cached(json.dumps(c, sort_keys=True), expr, pose, int(height), int(mouth), bool(blink), int(face),
                   int(walk * 16) % 16)


def hand_point(pose, height):
    (_, _), (_, hand) = ARMS.get(pose, ARMS["idle"])
    k = height / H
    return (HX + hand[0]) * k, hand[1] * k


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
