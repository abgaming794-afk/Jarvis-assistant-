"""Big-head cartoon characters drawn in code (waist-up, facing RIGHT).

make(spec, expr="neutral", pose="idle", height=600, mouth=0, blink=False, look=(1,0), prop=None)
returns a transparent RGBA sprite. spec is a dict (see PRESETS / references/characters.md).
Design space: 640 x 720 units, head centre (320, 235).
"""
import functools, json
from PIL import Image
from common import Pen, hexc, shade, mix

W, H = 640, 820
TOP = 100  # head-room for hats
HX, HY = 320, 238

SKIN = {"fair": "#f6d2b5", "light": "#eec39a", "wheat": "#e0ac7e", "brown": "#c68a5c",
        "dark": "#9a6440", "deep": "#6f4329", "pale": "#f8dccb"}

PRESETS = {
    # --- India
    "mughal_emperor": {"skin": "wheat", "hair": "short", "hair_color": "#1c1410", "facial": "full_beard",
                       "hat": "turban", "hat_color": "#f3e3b5", "outfit": "jama", "color": "#c9a227",
                       "accent": "#7a1f2b", "jewel": True, "age": "adult"},
    "nawab": {"skin": "wheat", "hair": "short", "hair_color": "#1c1410", "facial": "mustache", "hat": "turban",
              "hat_color": "#e25b45", "outfit": "jama", "color": "#2f6d8a", "accent": "#e8c547", "jewel": True,
              "age": "young"},
    "minister": {"skin": "brown", "hair": "short", "hair_color": "#2a1d17", "facial": "beard", "hat": "turban",
                 "hat_color": "#3f7d4e", "outfit": "jama", "color": "#2f5d3a", "accent": "#e8c547", "age": "old"},
    "maharaja": {"skin": "brown", "hair": "short", "hair_color": "#1c1410", "facial": "handlebar",
                 "hat": "pagdi", "hat_color": "#e0782f", "outfit": "jama", "color": "#f0e2c0", "accent": "#c9a227",
                 "jewel": True, "age": "adult"},
    "farmer": {"skin": "dark", "hair": "short", "hair_color": "#1e1612", "facial": "mustache", "hat": "pagdi",
               "hat_color": "#efe6d2", "outfit": "bare", "color": "#e9dfc8", "body": "thin", "age": "old"},
    "farmer_woman": {"skin": "dark", "hair": "bun", "hair_color": "#1a1210", "female": True, "hat": "veil",
                     "hat_color": "#b8503a", "outfit": "saree", "color": "#b8503a", "body": "thin"},
    "sepoy": {"skin": "brown", "hair": "short", "hair_color": "#1a1410", "facial": "mustache", "hat": "turban",
              "hat_color": "#f2efe6", "outfit": "redcoat", "color": "#b8302a", "accent": "#f2efe6", "age": "young"},
    "indian_trader": {"skin": "wheat", "hair": "short", "hair_color": "#221814", "facial": "mustache",
                      "hat": "cap", "hat_color": "#f2efe6", "outfit": "kurta", "color": "#f1e7d0",
                      "accent": "#c9a227", "body": "fat"},
    "rani": {"skin": "wheat", "hair": "long", "hair_color": "#17110e", "female": True, "hat": "tiara",
             "hat_color": "#e8c547", "outfit": "saree", "color": "#a3233a", "accent": "#e8c547", "jewel": True},
    "freedom_fighter": {"skin": "brown", "hair": "bald", "hair_color": "#cfcfcf", "glasses": "round",
                        "outfit": "shawl", "color": "#f1ece0", "body": "thin", "age": "old"},
    "revolutionary": {"skin": "wheat", "hair": "side", "hair_color": "#1a1410", "facial": "mustache",
                      "hat": "fedora", "hat_color": "#4a3a2e", "outfit": "suit", "color": "#6b5644",
                      "accent": "#efe9dc", "age": "young"},
    # --- Britain / Europe
    "british_officer": {"skin": "fair", "hair": "wig", "hair_color": "#e9e4da", "hat": "tricorn",
                        "hat_color": "#1d1d24", "outfit": "redcoat", "color": "#c0322b", "accent": "#efe9dc",
                        "age": "adult"},
    "company_merchant": {"skin": "fair", "hair": "long_m", "hair_color": "#4a3324", "facial": "goatee",
                         "hat": "wide_hat", "hat_color": "#1f1d22", "outfit": "doublet", "color": "#2a2a33",
                         "accent": "#efe9dc", "age": "adult"},
    "fat_merchant": {"skin": "fair", "hair": "balding", "hair_color": "#8a6a4a", "facial": "mustache",
                     "outfit": "suit", "color": "#3b2f4a", "accent": "#e8c547", "body": "fat", "age": "old"},
    "queen_elizabeth": {"skin": "pale", "hair": "curly", "hair_color": "#c8552c", "female": True, "hat": "crown",
                        "hat_color": "#e8c547", "outfit": "ruff_dress", "color": "#efe9dc", "accent": "#a3233a",
                        "jewel": True},
    "victorian_lady": {"skin": "fair", "hair": "bun", "hair_color": "#3a2a22", "female": True,
                       "outfit": "dress", "color": "#2b2b3a", "accent": "#e8e3d6"},
    "king": {"skin": "fair", "hair": "side", "hair_color": "#5a4030", "facial": "full_beard", "hat": "crown",
             "hat_color": "#e8c547", "outfit": "royal", "color": "#7a1f2b", "accent": "#efe9dc", "jewel": True},
    "politician": {"skin": "fair", "hair": "side", "hair_color": "#9a9a9a", "outfit": "suit", "color": "#262a36",
                   "accent": "#a3233a", "age": "old"},
    "soldier_ww": {"skin": "fair", "hair": "short", "hair_color": "#4a3324", "hat": "helmet",
                   "hat_color": "#5d6345", "outfit": "army", "color": "#5d6345", "accent": "#3b3f2a"},
    "general": {"skin": "fair", "hair": "short", "hair_color": "#b9b4ab", "facial": "mustache", "hat": "peak_cap",
                "hat_color": "#4f5a3a", "outfit": "army", "color": "#4f5a3a", "accent": "#e8c547", "age": "old"},
    "pirate": {"skin": "light", "hair": "long_m", "hair_color": "#2a1d17", "facial": "full_beard", "hat": "tricorn",
               "hat_color": "#2a1d17", "outfit": "doublet", "color": "#5a2a2a", "accent": "#e8c547"},
    "spy": {"skin": "light", "hair": "bob", "hair_color": "#151215", "female": True, "glasses": "sunglasses",
            "outfit": "dress", "color": "#b3202a", "accent": "#e8c547", "jewel": True},
    "businessman": {"skin": "light", "hair": "side", "hair_color": "#2a1d17", "outfit": "suit", "color": "#2b3140",
                    "accent": "#c0322b"},
    "scientist": {"skin": "fair", "hair": "messy", "hair_color": "#d9d6cf", "glasses": "round", "facial": "mustache",
                  "outfit": "labcoat", "color": "#f2f2ee", "accent": "#3a5f8a", "age": "old"},
    "monk": {"skin": "wheat", "hair": "bald", "hair_color": "#222", "outfit": "robe", "color": "#d9822b"},
    "arab_trader": {"skin": "brown", "hair": "short", "hair_color": "#1a1410", "facial": "full_beard",
                    "hat": "keffiyeh", "hat_color": "#f2efe6", "outfit": "robe", "color": "#efe6d2"},
    "chinese_emperor": {"skin": "light", "hair": "short", "hair_color": "#151215", "facial": "long_mustache",
                        "hat": "chinese_hat", "hat_color": "#1d1d24", "outfit": "royal", "color": "#d8a520",
                        "accent": "#b3202a"},
}


def resolve(spec):
    if isinstance(spec, str):
        spec = {"preset": spec}
    base = dict(PRESETS.get(spec.get("preset", ""), {}))
    base.update({k: v for k, v in spec.items() if k != "preset"})
    base.setdefault("skin", "light")
    base["skin"] = SKIN.get(base["skin"], base["skin"])
    base.setdefault("hair", "short")
    base.setdefault("hair_color", "#2a1d17")
    base.setdefault("outfit", "suit")
    base.setdefault("color", "#2b3140")
    base.setdefault("accent", "#efe9dc")
    base.setdefault("hat_color", "#222")
    return base


# ====================================================================== parts
def _torso(p, c):
    body = c.get("body", "normal")
    half = {"fat": 175, "thin": 112, "normal": 140}[body]
    col = c["color"]
    top = 392
    if c["outfit"] == "bare":
        col = c["skin"]
    p.rrect(HX - half, top, HX + half, 760, 92 if body != "thin" else 70, col)
    return half, top


def _outfit(p, c, half, top):
    o, col, acc = c["outfit"], c["color"], c["accent"]
    dk = shade(col, 0.78)
    if o == "suit":
        p.poly([(HX - 52, top + 2), (HX + 52, top + 2), (HX, top + 120)], "#f4f1ea")
        p.poly([(HX - 14, top + 18), (HX + 14, top + 18), (HX + 20, top + 150), (HX, top + 175), (HX - 20, top + 150)],
               acc)
        p.poly([(HX - 58, top), (HX - 8, top + 130), (HX - 75, top + 80)], dk)
        p.poly([(HX + 58, top), (HX + 8, top + 130), (HX + 75, top + 80)], dk)
    elif o == "labcoat":
        p.poly([(HX - 50, top + 2), (HX + 50, top + 2), (HX, top + 110)], "#7fa6c9")
        p.line([(HX, top + 110), (HX, 760)], w=4)
        p.poly([(HX - 60, top), (HX - 4, top + 140), (HX - 70, top + 90)], "#e4e4de")
        p.poly([(HX + 60, top), (HX + 4, top + 140), (HX + 70, top + 90)], "#e4e4de")
    elif o in ("redcoat", "army"):
        lap = acc if o == "redcoat" else dk
        p.poly([(HX - 46, top), (HX + 46, top), (HX + 40, 760), (HX - 40, 760)], lap)
        for i in range(5):
            p.ell(HX - 24, top + 40 + i * 58, 9, 9, "#e8c547", w=3)
            p.ell(HX + 24, top + 40 + i * 58, 9, 9, "#e8c547", w=3)
        if o == "redcoat":
            # gold epaulettes
            for sx in (-1, 1):
                cx = HX + sx * (half - 40)
                p.rrect(cx - 44, top + 6, cx + 44, top + 38, 14, "#e8c547")
        p.rrect(HX - 60, top - 12, HX + 60, top + 22, 12, lap)
    elif o in ("jama", "royal", "robe", "kurta", "sherwani"):
        p.poly([(HX - 10, top), (HX + 70, top + 10), (HX + 20, 760), (HX - 10, 760)], shade(col, 0.88), ol=False)
        p.line([(HX - 40, top + 6), (HX + 40, top + 150), (HX + 30, 760)], w=5)
        if o in ("jama", "royal", "sherwani"):
            p.line([(HX - 40, top + 6), (HX + 40, top + 150), (HX + 30, 760)], acc, 9)
            p.rrect(HX - half + 8, 640, HX + half - 8, 690, 20, acc)  # sash (patka)
        if o == "kurta":
            for i in range(3):
                p.ell(HX, top + 40 + i * 40, 7, 7, acc, w=3)
    elif o == "doublet":
        p.poly([(HX - 70, top - 4), (HX + 70, top - 4), (HX, top + 60)], "#f4f1ea")
        for i in range(6):
            p.ell(HX, top + 80 + i * 45, 8, 8, acc, w=3)
        p.line([(HX - 90, top + 60), (HX - 70, 760)], w=4)
        p.line([(HX + 90, top + 60), (HX + 70, 760)], w=4)
    elif o == "ruff_dress":
        p.poly([(HX - 120, top + 30), (HX + 120, top + 30), (HX + 50, 760), (HX - 50, 760)], acc)
        for i in range(7):
            p.ell(HX, top + 70 + i * 40, 7, 7, "#f8f4ea", w=2)
    elif o == "dress":
        p.poly([(HX - 70, top - 2), (HX + 70, top - 2), (HX, top + 70)], c["skin"], ol=False)
        p.line([(HX - 70, top - 2), (HX, top + 70), (HX + 70, top - 2)], w=5)
    elif o == "saree":
        p.poly([(HX - half + 10, top + 10), (HX + 30, top + 4), (HX + half - 20, 760), (HX - 10, 760)], acc if c.get("accent") else shade(col, 0.8))
        p.line([(HX - half + 10, top + 10), (HX + half - 20, 760)], w=5)
    elif o == "bare":
        # cloth over one shoulder (gamchha) + dhoti hint
        p.poly([(HX - half + 4, top + 20), (HX - half + 60, top - 6), (HX + half - 10, 720), (HX + half - 70, 760)],
               col)
        p.arc(HX - 40, top + 120, 40, 16, 20, 160, w=3)
        p.arc(HX + 40, top + 120, 40, 16, 20, 160, w=3)
    elif o == "shawl":
        p.poly([(HX - half, top + 20), (HX + half, top + 20), (HX + half, 760), (HX - half, 760)], col)
        p.line([(HX - 60, top), (HX + 10, 760)], w=4)
    if c.get("jewel"):
        for k in range(9):
            t = k / 8
            x = HX - 70 + 140 * t
            y = top + 26 + 70 * (1 - (2 * t - 1) ** 2)
            p.ell(x, y, 8, 8, "#f6f1e3", w=2)
        p.ell(HX, top + 104, 14, 16, "#2f9e6a", w=3)


def _neck(p, c):
    p.rrect(HX - 42, 340, HX + 42, 420, 20, shade(c["skin"], 0.86))
    if c["outfit"] == "ruff_dress":
        for i in range(16):
            a = i / 16
            x = HX - 150 + 300 * a
            p.ell(x, 400, 26, 20, "#fbf8f0", w=3)
    elif c["outfit"] in ("redcoat", "army", "doublet", "royal"):
        p.poly([(HX - 50, 392), (HX + 50, 392), (HX + 36, 426), (HX - 36, 426)], "#f4f1ea" if c["outfit"] != "army" else shade(c["color"], 0.8))


ARM_W = 64


def _hand(p, x, y, skin, r=30, point=False, ang=0):
    p.ell(x, y, r, r * 0.95, skin)
    if point:
        p.capsule((x + 8, y - 6), (x + 46, y - 10), 16, skin)


POSES = {  # (shoulder->elbow->hand) for viewer-left (L) and viewer-right (R)
    "idle": (((205, 450), (170, 580), (190, 700)), ((435, 450), (470, 580), (450, 700))),
    "point": (((205, 450), (170, 580), (190, 700)), ((435, 450), (520, 420), (600, 380))),
    "up": (((205, 450), (170, 580), (190, 700)), ((435, 450), (520, 360), (530, 250))),
    "cheer": (((205, 450), (110, 360), (100, 250)), ((435, 450), (530, 360), (540, 250))),
    "chin": (((205, 450), (170, 580), (190, 700)), ((435, 450), (470, 520), (400, 395))),
    "hold": (((205, 450), (170, 580), (190, 700)), ((435, 450), (500, 560), (540, 520))),
    "shrug": (((205, 450), (110, 520), (70, 440)), ((435, 450), (530, 520), (570, 440))),
    "fist": (((205, 450), (170, 580), (190, 700)), ((435, 450), (540, 420), (520, 300))),
    "cross": (((205, 450), (210, 600), (420, 560)), ((435, 450), (430, 600), (220, 560))),
    "think": (((205, 450), (170, 580), (190, 700)), ((435, 450), (470, 520), (380, 360))),
    "bow": (((205, 450), (230, 560), (300, 600)), ((435, 450), (410, 560), (340, 600))),
}


def _arm(p, c, pts, hand=True, point=False):
    sleeve = c["skin"] if c["outfit"] == "bare" else c["color"]
    if c["outfit"] in ("ruff_dress",):
        sleeve = c["color"]
    p.line(list(pts), None, ARM_W + 2 * p.lw)
    p.line(list(pts), sleeve, ARM_W)
    if c["outfit"] in ("redcoat",):
        p.capsule(pts[-1], pts[-1], ARM_W * 0.9, c["accent"])  # cuff
    if hand:
        _hand(p, pts[-1][0], pts[-1][1], c["skin"], point=point)


def _hair_back(p, c):
    h, col = c["hair"], c["hair_color"]
    if c.get("hat") in ("veil", "keffiyeh"):
        hc = c["hat_color"]
        p.rrect(HX - 205, HY - 175, HX + 205, 520, 150, hc)
        p.rrect(HX - 230, 380, HX + 230, 560, 90, hc)
    if h in ("long", "long_m"):
        y1 = 470 if h == "long" else 400
        p.rrect(HX - 185, 120, HX + 185, y1, 120, col)
    elif h == "bob":
        p.rrect(HX - 190, 90, HX + 190, 380, 130, col)
    elif h == "curly":
        for i in range(12):
            a = i / 11
            p.ell(HX - 180 + 360 * a, 300 + 40 * abs(a - 0.5), 46, 46, col)
    elif h == "bun":
        p.ell(HX - 40, 78, 62, 52, col)
    elif h == "wig":
        for sx in (-1, 1):
            for k in range(3):
                p.ell(HX + sx * 172, 250 + k * 44, 34, 26, col)
        p.rrect(HX - 40, 300, HX + 40, 420, 30, col)  # queue/ribbon behind


def _ears(p, c):
    for sx in (-1, 1):
        p.ell(HX + sx * 160, 262, 30, 38, c["skin"])
        p.arc(HX + sx * 160, 262, 14, 20, 90 if sx > 0 else -90, 270 if sx > 0 else 90, w=4)


def _head(p, c):
    body = c.get("body", "normal")
    rx = 168 if body != "fat" else 178
    p.ell(HX, HY, rx, 152, c["skin"])
    # soft highlight & jaw shade
    layer, d = p.overlay()
    d.ellipse(p.box(HX - 30, HY - 50, rx * 0.62, 80), fill=(255, 255, 255, 34))
    p.merge(layer)
    if body == "fat":
        p.arc(HX, HY + 95, 90, 40, 20, 160, shade(c["skin"], 0.8), 5)


def _hair_front(p, c, hat):
    h, col = c["hair"], c["hair_color"]
    hi = shade(col, 1.25)
    if h == "bald" or (hat in ("turban", "pagdi", "keffiyeh", "helmet") and h not in ("long", "bob", "curly")):
        if h == "bald":
            for sx in (-1, 1):
                p.ell(HX + sx * 150, 200, 30, 44, col)
            p.arc(HX - 50, 140, 40, 20, 200, 300, (255, 255, 255, 140), 6)
        return
    if h == "balding":
        for sx in (-1, 1):
            p.ell(HX + sx * 152, 210, 34, 56, col)
        p.arc(HX - 50, 130, 40, 20, 200, 300, (255, 255, 255, 140), 6)
        return
    if h in ("short", "side", "long", "long_m", "bob", "bun", "wig", "messy", "curly"):
        top = HY - 168
        line = HY - 62 if h not in ("bob",) else HY - 40
        p.chord(HX, line, 176, line - top, 180, 360, col)
        # sideburns
        for sx in (-1, 1):
            p.rrect(HX + sx * 150 - 20, line - 20, HX + sx * 150 + 20, line + 70, 16, col)
        if h == "side":
            p.poly([(HX - 120, line - 10), (HX + 40, line - 70), (HX + 170, line - 5), (HX + 80, line - 40)], col)
            p.arc(HX - 20, line - 60, 90, 40, 200, 320, hi, 6)
        elif h in ("short", "long_m", "wig"):
            for k in range(5):
                p.ell(HX - 110 + k * 55, line + 2, 34, 22, col, ol=False)
            p.arc(HX - 40, line - 80, 80, 40, 200, 320, hi, 6)
        elif h == "bob":
            p.rrect(HX - 170, line - 60, HX + 170, line + 18, 30, col)
            p.arc(HX - 40, line - 90, 90, 40, 200, 320, hi, 6)
        elif h == "messy":
            pts = []
            for k in range(13):
                a = k / 12
                x = HX - 185 + 370 * a
                y = line - (70 if k % 2 == 0 else 150) * (1 - (2 * a - 1) ** 2 * 0.6) - 20
                pts.append((x, y))
            p.poly([(HX - 180, line + 30)] + pts + [(HX + 180, line + 30)], col)
        elif h == "curly":
            for k in range(9):
                a = k / 8
                p.ell(HX - 160 + 320 * a, line - 20 - 60 * (1 - (2 * a - 1) ** 2), 44, 40, col)
        elif h in ("long",):
            p.arc(HX, line - 90, 10, 80, 0, 360, shade(col, 0.7), 5)  # centre part


def _hat(p, c):
    hat, col = c.get("hat"), c["hat_color"]
    if not hat:
        return
    dk, hi = shade(col, 0.75), shade(col, 1.25)
    top = HY - 152
    if hat == "turban" or hat == "pagdi":
        p.ell(HX, top + 52, 192, 100, col)
        for k in range(4):
            p.arc(HX, top + 120 - k * 34, 180 - k * 18, 60, 195, 345, dk, 5)
        p.ell(HX + (0 if hat == "turban" else 40), top + 60, 22, 26, "#c9302c" if col != "#c9302c" else "#2f9e6a", w=4)
        if hat == "turban":
            p.poly([(HX - 6, top + 40), (HX + 40, top - 70), (HX + 60, top - 60), (HX + 14, top + 40)], "#f6f1e3")
    elif hat == "crown":
        y0 = top + 20
        pts = [(HX - 120, y0 + 40), (HX - 120, y0 - 50), (HX - 70, y0 - 10), (HX - 30, y0 - 80), (HX, y0 - 20),
               (HX + 30, y0 - 80), (HX + 70, y0 - 10), (HX + 120, y0 - 50), (HX + 120, y0 + 40)]
        p.poly(pts, col)
        for x in (-70, 0, 70):
            p.ell(HX + x, y0 + 14, 13, 13, "#c9302c", w=3)
    elif hat == "tiara":
        p.poly([(HX - 90, top + 40), (HX - 40, top + 10), (HX, top - 20), (HX + 40, top + 10), (HX + 90, top + 40)],
               col)
        p.ell(HX, top + 18, 12, 12, "#c9302c", w=3)
    elif hat == "tricorn":
        p.poly([(HX - 230, top + 70), (HX, top - 70), (HX + 230, top + 70), (HX, top + 30)], col)
        p.line([(HX - 230, top + 70), (HX, top + 30), (HX + 230, top + 70)], "#e8c547", 8)
    elif hat == "wide_hat":
        p.ell(HX, top + 60, 240, 40, col)
        p.rrect(HX - 120, top - 70, HX + 120, top + 60, 30, col)
        p.rrect(HX - 122, top + 20, HX + 122, top + 50, 6, "#3a2a22")
        p.rrect(HX - 20, top + 16, HX + 20, top + 54, 4, "#e8c547")
    elif hat == "top_hat":
        p.ell(HX, top + 50, 210, 34, col)
        p.rrect(HX - 110, top - 140, HX + 110, top + 50, 14, col)
        p.rrect(HX - 112, top + 8, HX + 112, top + 34, 4, "#a3233a")
    elif hat == "fedora":
        p.ell(HX, top + 50, 220, 36, col)
        p.rrect(HX - 125, top - 60, HX + 125, top + 48, 50, col)
        p.rrect(HX - 127, top + 12, HX + 127, top + 38, 4, dk)
    elif hat == "helmet":
        p.chord(HX, top + 90, 196, 150, 180, 360, col)
        p.rrect(HX - 210, top + 78, HX + 210, top + 102, 12, dk)
    elif hat == "pith_helmet":
        p.ell(HX, top + 70, 220, 40, col)
        p.chord(HX, top + 70, 160, 140, 180, 360, col)
        p.ell(HX, top - 70, 18, 14, dk)
    elif hat == "peak_cap":
        p.ell(HX, top + 20, 190, 70, col)
        p.rrect(HX - 170, top + 30, HX + 170, top + 80, 20, dk)
        p.chord(HX + 60, top + 84, 140, 30, 0, 180, "#1d1d24")
        p.ell(HX, top + 50, 18, 18, "#e8c547", w=3)
    elif hat == "cap":
        p.chord(HX, top + 70, 150, 70, 180, 360, col)
    elif hat in ("veil", "keffiyeh"):
        p.chord(HX, top + 92, 186, 116, 180, 360, col)
        for sx in (-1, 1):
            p.poly([(HX + sx * 186, top + 92), (HX + sx * 150, top + 92), (HX + sx * 168, top + 260),
                    (HX + sx * 200, top + 300)], col)
        if hat == "keffiyeh":
            p.rrect(HX - 186, top + 40, HX + 186, top + 66, 12, "#1d1d24")
        else:
            p.arc(HX, top + 92, 170, 100, 200, 340, shade(col, 1.3), 7)
    elif hat == "chinese_hat":
        p.chord(HX, top + 80, 170, 110, 180, 360, col)
        p.ell(HX, top - 34, 22, 22, "#b3202a")


def _eyes(p, c, expr, blink, look):
    lx, ly = look
    ex = [HX - 62, HX + 62]
    ey = HY + 10
    rx, ry = 34, 40
    pr = 17
    if expr == "shocked":
        rx, ry, pr = 40, 48, 11
    glasses = c.get("glasses")
    for i, x in enumerate(ex):
        if blink or expr in ("laugh",):
            p.arc(x, ey + 10, 26, 18, 200, 340, w=7)
            continue
        if glasses == "sunglasses":
            continue
        p.ell(x, ey, rx, ry, "#ffffff", w=5)
        if c.get("female"):
            sx = -1 if i == 0 else 1
            for k in range(3):
                a = 0.55 + 0.18 * k
                p.line([(x + sx * rx * a, ey - ry * 0.75 + k * 8), (x + sx * (rx * a + 16), ey - ry * 0.75 + k * 8 - 12)], w=6)
        px, py = x + lx * (rx - pr - 6), ey + ly * (ry - pr - 6) + 4
        p.ell(px, py, pr, pr + 3, "#1b1411", ol=False)
        p.ell(px + 6, py - 8, 5, 5, "#ffffff", ol=False)
        if expr in ("smug", "scheming", "sleepy", "bored"):
            # heavy eyelid: skin over top half
            p.chord(x, ey, rx + 2, ry + 2, 180, 360, c["skin"], ol=False)
            p.line([(x - rx - 2, ey), (x + rx + 2, ey)], w=6)
    if glasses == "sunglasses":
        p.rrect(HX - 118, ey - 34, HX - 8, ey + 30, 26, "#151215")
        p.rrect(HX + 8, ey - 34, HX + 118, ey + 30, 26, "#151215")
        p.line([(HX - 10, ey - 18), (HX + 10, ey - 18)], w=8)
        p.line([(HX - 118, ey - 20), (HX - 160, ey - 30)], w=8)
        p.arc(HX - 80, ey - 12, 18, 10, 200, 300, (255, 255, 255, 170), 5)
        p.arc(HX + 46, ey - 12, 18, 10, 200, 300, (255, 255, 255, 170), 5)
    elif glasses in ("round", "square"):
        for x in ex:
            if glasses == "round":
                p.d.ellipse(p.box(x, ey, 50, 48), outline=p.ol, width=p._w(7))
            else:
                p.d.rounded_rectangle(p.box(x, ey, 54, 44), radius=14 * p.s, outline=p.ol, width=p._w(7))
        p.line([(HX - 12, ey - 4), (HX + 12, ey - 4)], w=7)
    elif glasses == "monocle":
        p.d.ellipse(p.box(ex[1], ey, 48, 48), outline=hexc("#e8c547"), width=p._w(6))
        p.line([(ex[1] + 40, ey + 30), (ex[1] + 60, ey + 140)], "#e8c547", 3)


def _brows(p, c, expr):
    col = shade(c["hair_color"], 0.85) if c["hair"] != "bald" else shade(c["skin"], 0.55)
    y = HY - 52
    w = 13 if not c.get("female") else 9
    if c.get("glasses") == "sunglasses":
        y -= 8
    shapes = {
        "neutral": ((-100, 0), (-30, -4), (30, -4), (100, 0)),
        "happy": ((-100, 4), (-30, -12), (30, -12), (100, 4)),
        "laugh": ((-100, 0), (-30, -16), (30, -16), (100, 0)),
        "angry": ((-100, -16), (-28, 16), (28, 16), (100, -16)),
        "shout": ((-100, -16), (-28, 16), (28, 16), (100, -16)),
        "sad": ((-100, 12), (-30, -14), (30, -14), (100, 12)),
        "worried": ((-100, 10), (-30, -16), (30, -16), (100, 10)),
        "shocked": ((-100, -22), (-30, -34), (30, -34), (100, -22)),
        "smug": ((-100, 4), (-30, 4), (30, -22), (100, -10)),
        "scheming": ((-100, -6), (-30, 10), (30, 10), (100, -6)),
        "thinking": ((-100, 6), (-30, 0), (30, -24), (100, -14)),
        "proud": ((-100, -4), (-30, -10), (30, -10), (100, -4)),
    }
    s = shapes.get(expr, shapes["neutral"])
    p.line([(HX + s[0][0], y + s[0][1]), (HX + s[1][0], y + s[1][1])], col, w)
    p.line([(HX + s[2][0], y + s[2][1]), (HX + s[3][0], y + s[3][1])], col, w)


def _nose(p, c):
    p.arc(HX + 4, HY + 70, 18, 14, 330, 150, shade(c["skin"], 0.6), 6)


def _cheeks(p, c, expr):
    layer, d = p.overlay()
    a = 70 if expr not in ("angry", "shout") else 110
    col = (230, 90, 80, a)
    for sx in (-1, 1):
        d.ellipse(p.box(HX + sx * 100, HY + 82, 30, 18), fill=col)
    p.merge(layer)


def _facial_hair(p, c, expr):
    f = c.get("facial")
    col = c["hair_color"]
    if not f:
        return
    if f in ("beard", "full_beard"):
        p.chord(HX, HY + 40, 162, 150, 10, 170, col)
        # hole for the mouth
        p.ell(HX, HY + 118, 46, 26, c["skin"], ol=False)
    if f == "goatee":
        p.poly([(HX - 26, HY + 140), (HX + 26, HY + 140), (HX, HY + 200)], col)
    if f in ("mustache", "full_beard", "beard", "goatee", "handlebar", "long_mustache"):
        y = HY + 96
        p.chord(HX - 34, y + 6, 40, 20, 180, 360, col)
        p.chord(HX + 34, y + 6, 40, 20, 180, 360, col)
        if f == "handlebar":
            p.line([(HX - 70, y + 2), (HX - 100, y - 20)], col, 12)
            p.line([(HX + 70, y + 2), (HX + 100, y - 20)], col, 12)
        if f == "long_mustache":
            p.line([(HX - 60, y + 4), (HX - 80, y + 90)], col, 9)
            p.line([(HX + 60, y + 4), (HX + 80, y + 90)], col, 9)


def _mouth(p, c, expr, mouth):
    if c.get("female"):
        p.ol, saved = (176, 48, 58, 255), p.ol
        try:
            return _mouth_core(p, c, expr, mouth)
        finally:
            p.ol = saved
    return _mouth_core(p, c, expr, mouth)


def _mouth_core(p, c, expr, mouth):
    y = HY + 122
    m = mouth  # 0 closed, 1 open (talk)
    dark, tongue = "#5a1d1d", "#e0676a"
    if expr in ("happy", "laugh", "proud") or (expr in ("neutral",) and m):
        h = 56 if expr == "laugh" else 44 if m or expr == "happy" else 30
        if expr == "neutral":
            h = 30
        p.chord(HX + 4, y - 8, 52, h, 0, 180, dark)
        p.chord(HX + 4, y + h * 0.55 - 8, 30, h * 0.4, 180, 360, tongue, ol=False)
        p.chord(HX + 4, y - 6, 46, 10, 0, 180, "#ffffff", ol=False)
    elif expr in ("neutral", "thinking"):
        p.arc(HX + 4, y - 14, 34, 16, 20, 160, w=7)
    elif expr in ("smug", "scheming"):
        if m:
            p.chord(HX + 14, y - 10, 44, 26, 0, 180, dark)
        else:
            p.line([(HX - 36, y - 6), (HX + 10, y - 2), (HX + 50, y - 22)], w=7)
        if expr == "scheming":
            p.chord(HX + 14, y - 8, 42, 18, 0, 180, "#ffffff")
            p.line([(HX - 24, y - 8), (HX + 54, y - 8)], w=4)
    elif expr in ("angry",):
        p.rrect(HX - 44, y - 22, HX + 50, y + 14 + 12 * m, 12, "#ffffff")
        p.line([(HX - 40, y - 4 + 6 * m), (HX + 46, y - 4 + 6 * m)], w=4)
    elif expr in ("shout",):
        p.ell(HX + 4, y + 2, 46, 40, dark)
        p.chord(HX + 4, y + 22, 26, 16, 180, 360, tongue, ol=False)
    elif expr in ("shocked",):
        p.ell(HX + 4, y + 6, 26 + 6 * m, 34 + 6 * m, dark)
    elif expr in ("sad", "worried"):
        if m:
            p.ell(HX + 4, y + 4, 24, 16, dark)
        elif expr == "sad":
            p.arc(HX + 4, y + 18, 34, 18, 200, 340, w=7)
        else:
            p.line([(HX - 36, y + 6), (HX - 12, y - 4), (HX + 12, y + 6), (HX + 40, y - 4)], w=7)
    else:
        p.arc(HX + 4, y - 14, 34, 16, 20, 160, w=7)


def _wrinkles(p, c):
    if c.get("age") == "old":
        col = shade(c["skin"], 0.72)
        p.arc(HX, HY - 100, 60, 14, 200, 340, col, 4)
        p.arc(HX, HY - 84, 46, 10, 200, 340, col, 4)
        for sx in (-1, 1):
            p.arc(HX + sx * 62, HY + 56, 26, 10, 20, 160, col, 4)


def _tear(p):
    p.ell(HX - 92, HY + 70, 12, 18, "#8ccdf2", w=3)


def _sweat(p):
    p.ell(HX + 150, HY - 60, 12, 20, "#8ccdf2", w=3)


@functools.lru_cache(maxsize=512)
def _cached(spec_json, expr, pose, height, mouth, blink, look, female_flag=None):
    c = json.loads(spec_json)
    ss = max(0.5, height * 2.0 / H)
    p = Pen(W, H, ss, lw=6, oy=TOP)
    arms = POSES.get(pose, POSES["idle"])
    _hair_back(p, c)
    half, top = _torso(p, c)
    _outfit(p, c, half, top)
    _neck(p, c)
    front_arms = pose not in ("idle",)
    # back arms (idle hang by the sides)
    if not front_arms:
        _arm(p, c, arms[0], hand=False)
        _arm(p, c, arms[1], hand=False)
    else:
        _arm(p, c, arms[0], hand=pose in ("cheer", "shrug", "bow", "cross"))
    _ears(p, c)
    _head(p, c)
    _hair_front(p, c, c.get("hat"))
    _wrinkles(p, c)
    _cheeks(p, c, expr)
    _facial_hair(p, c, expr)
    _brows(p, c, expr)
    _eyes(p, c, expr, blink, look)
    _nose(p, c)
    _mouth(p, c, expr, mouth)
    if expr == "sad":
        _tear(p)
    if expr in ("worried", "shocked"):
        _sweat(p)
    _hat(p, c)
    if front_arms:
        _arm(p, c, arms[1], hand=True, point=(pose == "point"))
    img = p.result(height)
    return img


def make(spec, expr="neutral", pose="idle", height=600, mouth=0, blink=False, look=(0.6, 0.0)):
    c = resolve(spec)
    key = json.dumps(c, sort_keys=True)
    return _cached(key, expr, pose, int(height), int(mouth), bool(blink), (round(look[0], 2), round(look[1], 2)))


def hand_point(pose, height):
    """Where the front (right) hand is, in sprite pixels — props are held there."""
    pts = POSES.get(pose, POSES["idle"])[1]
    x, y = pts[-1]
    k = height / H
    return x * k, (y + TOP) * k


EXPRESSIONS = ["neutral", "happy", "laugh", "proud", "smug", "scheming", "thinking", "angry", "shout", "shocked",
               "sad", "worried"]


if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "cast_sheet.png"
    names = list(PRESETS)
    cols = 7
    h = 300
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * 270, rows * 320), (60, 52, 48, 255))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    exprs = EXPRESSIONS
    poses = list(POSES)
    for i, n in enumerate(names):
        spr = make({"preset": n}, exprs[i % len(exprs)], poses[i % len(poses)], h)
        x = (i % cols) * 270 + (270 - spr.width) // 2
        y = (i // cols) * 320
        sheet.alpha_composite(spr, (max(0, x), y))
        d.text(((i % cols) * 270 + 6, y + 302), f"{n} / {exprs[i % len(exprs)]} / {poses[i % len(poses)]}",
               fill=(255, 255, 255))
    sheet.convert("RGB").save(out)
    print(out)
