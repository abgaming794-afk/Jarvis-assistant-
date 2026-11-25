"""Cartoon props in the same outlined style. make(name, height, color=None) -> RGBA sprite.
Design space 200 x 200 units."""
import functools, math
from common import Pen, shade, hexc, font

GOLD, GOLD_D = "#f1c232", "#c9961a"


def _coin(p, cx=100, cy=100, r=70):
    p.ell(cx, cy, r, r, GOLD)
    p.ell(cx, cy, r * 0.72, r * 0.72, GOLD_D, w=4)
    p.ell(cx, cy, r * 0.6, r * 0.6, GOLD, ol=False)
    p.arc(cx - r * 0.25, cy - r * 0.25, r * 0.3, r * 0.18, 200, 300, "#fff6c8", 7)


def coin(p, c):
    _coin(p)


def coins(p, c):
    for i, (x, y) in enumerate([(60, 150), (140, 150), (100, 150), (80, 120), (120, 120), (100, 90), (100, 60)]):
        p.ell(x, y, 42, 20, GOLD)
        p.ell(x, y - 4, 32, 12, "#ffe27a", ol=False)


def money_bag(p, c):
    col = c or "#c9a56a"
    p.ell(100, 125, 75, 68, col)
    p.poly([(70, 62), (130, 62), (115, 40), (85, 40)], col)
    p.rrect(72, 56, 128, 70, 6, "#7a4a22")
    p.d.text((p.s * 100, p.s * 128), "$" if c == "usd" else "£" if c == "gbp" else "₹" if False else "$",
             font=font(80 * p.s, "Black"), anchor="mm", fill=hexc("#7a4a22"))


def gold_bars(p, c):
    for (x, y) in [(55, 150), (145, 150), (100, 105)]:
        p.poly([(x - 45, y + 25), (x + 45, y + 25), (x + 32, y - 20), (x - 32, y - 20)], GOLD)
        p.poly([(x - 32, y - 20), (x + 32, y - 20), (x + 24, y - 8), (x - 24, y - 8)], "#ffe27a", ol=False)


def scroll(p, c):
    p.rrect(40, 30, 160, 170, 6, "#f3e3b8")
    for k in range(6):
        p.line([(56, 60 + k * 18), (144 - (k % 3) * 14, 60 + k * 18)], "#8a6a3a", 4)
    p.rrect(30, 18, 170, 40, 12, "#d9b77a")
    p.rrect(30, 160, 170, 182, 12, "#d9b77a")
    p.ell(130, 150, 16, 16, "#b3202a")


def chest(p, c):
    p.rrect(25, 90, 175, 175, 10, "#8a5a2a")
    p.chord(100, 90, 75, 50, 180, 360, "#9a6a32")
    p.rrect(25, 84, 175, 96, 4, GOLD)
    p.rrect(88, 84, 112, 120, 4, GOLD)
    for x, y in [(60, 70), (90, 60), (125, 66), (150, 76)]:
        p.ell(x, y, 16, 16, GOLD)


def crown(p, c):
    p.poly([(30, 160), (30, 70), (65, 110), (100, 50), (135, 110), (170, 70), (170, 160)], GOLD)
    for x in (65, 100, 135):
        p.ell(x, 138, 12, 12, "#b3202a", w=3)


def sword(p, c):
    p.poly([(96, 20), (104, 20), (108, 140), (92, 140)], "#d9dde2")
    p.rrect(60, 136, 140, 150, 6, GOLD)
    p.rrect(93, 150, 107, 182, 4, "#5a3a20")
    p.ell(100, 186, 10, 10, GOLD)


def cannon(p, c):
    p.poly([(20, 70), (150, 50), (160, 100), (30, 112)], "#3a3a40")
    p.ell(160, 75, 16, 26, "#2a2a30")
    p.ell(70, 140, 44, 44, "#7a4a22")
    p.ell(70, 140, 12, 12, "#4a2a12")


def ship(p, c):
    p.poly([(10, 130), (190, 130), (165, 175), (30, 175)], "#6a4024")
    p.line([(100, 130), (100, 15)], "#4a2a14", 8)
    p.poly([(104, 22), (170, 80), (104, 120)], "#f3ead6")
    p.poly([(96, 30), (40, 85), (96, 120)], "#f3ead6")
    p.poly([(100, 15), (130, 22), (100, 30)], c or "#c0322b")


def flag(p, c):
    col = c or "#c0322b"
    p.line([(30, 20), (30, 190)], "#5a3a20", 8)
    p.poly([(34, 24), (180, 34), (170, 70), (180, 104), (34, 100)], col)


def spice_sack(p, c):
    col = c or "#c9a56a"
    p.rrect(35, 70, 165, 185, 40, col)
    p.ell(100, 70, 60, 22, c or "#d9822b")
    for k in range(10):
        p.ell(70 + (k * 13) % 60, 62 + (k * 7) % 14, 8, 8, "#b3202a" if k % 2 else "#d9822b", ol=False)


def letter(p, c):
    p.rrect(25, 55, 175, 155, 6, "#f3ead6")
    p.line([(25, 55), (100, 110), (175, 55)], None, 5)
    p.ell(100, 112, 18, 18, "#b3202a")


def bomb(p, c):
    p.ell(100, 120, 65, 65, "#26262c")
    p.rrect(85, 40, 115, 62, 4, "#3a3a40")
    p.line([(100, 40), (120, 20), (140, 18)], "#8a6a3a", 5)
    p.ell(145, 16, 10, 10, "#ffb347", ol=False)


def chain(p, c):
    for k in range(5):
        p.d.ellipse(p.box(30 + k * 35, 100 + (k % 2) * 6, 24, 16 if k % 2 else 24), outline=hexc("#8a8f99"),
                    width=p._w(12))


def tea(p, c):
    p.rrect(50, 80, 150, 170, 30, "#f3ead6")
    p.d.ellipse(p.box(155, 120, 20, 24), outline=hexc("#2a1a14"), width=p._w(10))
    p.ell(100, 82, 50, 10, "#a0522d")
    for x in (80, 110):
        p.arc(x, 50, 10, 18, 90, 270, "#bbbbbb", 4)


def throne(p, c):
    col = c or "#c9a227"
    p.rrect(30, 10, 170, 190, 40, col)
    p.rrect(52, 34, 148, 150, 30, "#7a1f2b")
    p.rrect(20, 120, 180, 150, 10, shade(col, 0.85))


def musket(p, c):
    p.line([(20, 170), (180, 30)], "#5a3a20", 16)
    p.line([(70, 126), (185, 26)], "#7a7f88", 7)


def opium(p, c):
    p.rrect(40, 50, 160, 180, 18, "#6a4a2a")
    p.d.text((p.s * 100, p.s * 120), "OPIUM", font=font(26 * p.s, "Black"), anchor="mm", fill=hexc("#f3ead6"))


def stamp(p, c):
    p.d.ellipse(p.box(100, 100, 80, 80), outline=hexc(c or "#b3202a"), width=p._w(10))
    p.d.ellipse(p.box(100, 100, 62, 62), outline=hexc(c or "#b3202a"), width=p._w(4))


def dollar(p, c):
    col = c or "#7fb069"
    p.rrect(10, 55, 190, 145, 6, col)
    p.rrect(22, 67, 178, 133, 4, shade(col, 1.15), w=3)
    p.ell(100, 100, 26, 26, shade(col, 0.85), w=3)
    p.d.text((p.s * 100, p.s * 101), "$" if c != "rupee" else "₹", font=font(40 * p.s, "Black"), anchor="mm",
             fill=hexc("#24401c"))
    for x in (38, 162):
        p.ell(x, 100, 9, 9, shade(col, 0.8), ol=False)


def rupee(p, c):
    p.rrect(10, 55, 190, 145, 6, "#d9a35a")
    p.rrect(22, 67, 178, 133, 4, "#e9c17a", w=3)
    p.d.text((p.s * 100, p.s * 102), "₹", font=font(64 * p.s, "Black"), anchor="mm", fill=hexc("#6a3a14"))


def cash_stack(p, c):
    for k in range(5):
        y = 150 - k * 22
        p.rrect(20, y - 30, 180, y + 10, 5, "#7fb069" if c != "rupee" else "#d9a35a")
        p.rrect(80, y - 30, 120, y + 10, 2, "#e8dcc0", w=2)


def union_jack(p, c):
    p.rrect(10, 40, 190, 160, 4, "#1d3a8a")
    p.line([(14, 44), (186, 156)], "#ffffff", 26)
    p.line([(186, 44), (14, 156)], "#ffffff", 26)
    p.line([(14, 44), (186, 156)], "#c8102e", 9)
    p.line([(186, 44), (14, 156)], "#c8102e", 9)
    p.rrect(82, 42, 118, 158, 0, "#ffffff", ol=False)
    p.rrect(12, 82, 188, 118, 0, "#ffffff", ol=False)
    p.rrect(90, 42, 110, 158, 0, "#c8102e", ol=False)
    p.rrect(12, 90, 188, 110, 0, "#c8102e", ol=False)
    p.d.rectangle(p.box(100, 100, 90, 60), outline=p.ol, width=p._w(5))


def eic_flag(p, c):
    p.rrect(10, 40, 190, 160, 4, "#ffffff")
    for k in range(7):
        if k % 2 == 0:
            p.rrect(12, 42 + k * 16.6, 188, 42 + (k + 1) * 16.6, 0, "#c8102e", ol=False)
    p.rrect(12, 42, 90, 100, 0, "#ffffff", ol=False)
    p.rrect(44, 42, 58, 100, 0, "#c8102e", ol=False)
    p.rrect(12, 64, 90, 78, 0, "#c8102e", ol=False)
    p.d.rectangle(p.box(100, 100, 90, 60), outline=p.ol, width=p._w(5))


def mughal_flag(p, c):
    import math
    p.rrect(10, 40, 190, 160, 4, "#2f7d4e")
    for k in range(12):
        a = k * math.pi / 6
        p.line([(100 + math.cos(a) * 30, 100 + math.sin(a) * 30), (100 + math.cos(a) * 48, 100 + math.sin(a) * 48)], "#e8c547", 6)
    p.ell(100, 100, 28, 28, "#e8c547", w=3)


def warning(p, c):
    p.poly([(100, 20), (185, 170), (15, 170)], "#f1c232")
    p.d.text((p.s * 100, p.s * 120), "!", font=font(90 * p.s, "Black"), anchor="mm", fill=hexc("#2a1a14"))


def question(p, c):
    p.ell(100, 100, 80, 80, c or "#e8342c")
    p.d.text((p.s * 100, p.s * 104), "?", font=font(110 * p.s, "Black"), anchor="mm", fill=hexc("#ffffff"))


def exclaim(p, c):
    p.ell(100, 100, 80, 80, c or "#f1c232")
    p.d.text((p.s * 100, p.s * 104), "!", font=font(110 * p.s, "Black"), anchor="mm", fill=hexc("#2a1a14"))


def arrow_up(p, c):
    col = c or "#2f9e44"
    p.poly([(100, 15), (180, 100), (130, 100), (130, 185), (70, 185), (70, 100), (20, 100)], col)


def arrow_down(p, c):
    col = c or "#e8342c"
    p.poly([(100, 185), (180, 100), (130, 100), (130, 15), (70, 15), (70, 100), (20, 100)], col)


def pin(p, c):
    p.poly([(100, 190), (55, 100), (145, 100)], c or "#e8342c")
    p.ell(100, 80, 55, 55, c or "#e8342c")
    p.ell(100, 80, 22, 22, "#ffffff")


def fire(p, c):
    p.poly([(100, 10), (160, 90), (170, 150), (100, 190), (30, 150), (40, 90), (70, 110)], "#f26b1d")
    p.poly([(100, 80), (135, 130), (100, 185), (65, 130)], "#f6c343", ol=False)


def skull(p, c):
    p.ell(100, 85, 70, 65, "#f3efe4")
    p.rrect(65, 120, 135, 175, 14, "#f3efe4")
    p.ell(75, 85, 18, 20, "#2a1a14", ol=False)
    p.ell(125, 85, 18, 20, "#2a1a14", ol=False)


def portrait(p, c):
    p.rrect(20, 10, 180, 190, 6, "#c9a227")
    p.rrect(36, 26, 164, 174, 4, "#3a2a22")
    p.ell(100, 85, 36, 38, "#e0ac7e")
    p.rrect(56, 125, 144, 174, 20, "#7a1f2b", ol=False)


def cash_stack_top(p, c):
    col = c or "#6aa063"
    for k, (dx, dy, a) in enumerate([(-8, 6, -6), (4, -2, 4), (0, 0, 0)]):
        x0, y0 = 30 + dx, 55 + dy
        p.rrect(x0, y0, x0 + 140, y0 + 80, 4, shade(col, 0.85 + k * .08))
    p.rrect(42, 64, 158, 126, 3, shade(col, 1.15), w=2.5)
    p.ell(100, 95, 18, 18, shade(col, .7), w=2.5)
    p.line([(94, 102), (100, 95), (104, 88)], "#e8f5e0", 3)


def coin_pile_top(p, c):
    import random
    r = random.Random(3)
    for k in range(14):
        x, y = 100 + r.uniform(-55, 55), 100 + r.uniform(-40, 40)
        p.ell(x, y, 24, 24, "#f1c232", w=3)
        p.ell(x, y, 16, 16, "#d9a821", ol=False)


def notepad(p, c):
    p.rrect(30, 10, 170, 195, 4, "#f7f6f0")
    p.rrect(30, 10, 170, 40, 4, c or "#2f8a4e")
    for k in range(5):
        p.line([(45, 70 + k * 24), (155, 70 + k * 24)], "#b8c7d8", 2)
    p.line([(120, 60), (160, 150)], "#e8b33a", 9)
    p.poly([(156, 142), (166, 162), (152, 156)], "#3a2a1a", w=1.5)


def menu_card(p, c):
    p.rrect(25, 5, 175, 195, 4, "#f6f1e6")
    p.d.rectangle(p.box(100, 100, 70, 90), outline=hexc(c or "#b8302a"), width=p._w(4))
    p.rrect(45, 45, 155, 120, 3, "#dfe8d8", w=2)
    for k in range(4):
        p.ell(100, 98 - k * 9, 34, 9, "#c98a3a", w=2)
    for k in range(4):
        p.line([(48, 140 + k * 12), (150, 140 + k * 12)], "#9a948a", 2)


def coin_bag(p, c):
    col = c or "#b98e55"
    p.ell(100, 125, 70, 62, col)
    p.poly([(72, 66), (128, 66), (115, 42), (85, 42)], col)
    p.rrect(72, 60, 128, 72, 6, "#6a4422")
    p.d.text((p.s * 100, p.s * 128), "£", font=font(70 * p.s, "Black"), anchor="mm", fill=hexc("#6a4422"))


def charter(p, c):
    p.rrect(30, 20, 170, 180, 4, "#f1e3bf")
    for k in range(6):
        p.line([(48, 52 + k * 18), (152 - (k % 2) * 20, 52 + k * 18)], "#8a6a3a", 3)
    p.ell(128, 158, 18, 18, "#b3202a")
    p.line([(120, 172), (112, 196)], "#b3202a", 6)
    p.line([(136, 172), (144, 196)], "#b3202a", 6)


def diamond(p, c):
    """Big Mughal-style oval rose-cut diamond with sparkle."""
    col = c or "#dff3ff"
    p.ell(100, 112, 78, 62, col)
    p.ell(100, 106, 50, 36, "#f6fdff", ol=False)
    for a in range(0, 360, 40):
        x = 100 + math.cos(math.radians(a)) * 78
        y = 112 + math.sin(math.radians(a)) * 62
        p.line([(100, 106), (x, y)], "#9cc6dc", 3)
    p.ell(100, 106, 50, 36, None if False else "#ffffff", w=3, ol=False) if False else None
    p.line([(46, 70), (154, 70)], "#bfe2f2", 3)
    for (sx, sy, r) in [(62, 70, 14), (150, 150, 10), (140, 58, 8)]:
        p.line([(sx - r, sy), (sx + r, sy)], "#ffffff", 5)
        p.line([(sx, sy - r), (sx, sy + r)], "#ffffff", 5)


def armlet(p, c):
    """Koh-i-Noor in its old armlet setting: big stone between two smaller ones on a gold band."""
    p.rrect(8, 104, 192, 122, 8, "#c9961a")
    for cx, rx in ((42, 26), (158, 26)):
        p.ell(cx, 112, rx + 8, 30, GOLD)
        p.ell(cx, 112, rx, 22, "#e8f6ff")
    p.ell(100, 110, 46, 50, GOLD)
    p.ell(100, 110, 36, 40, "#eefaff")
    p.ell(92, 98, 12, 10, "#ffffff", ol=False)


PROPS = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_") and k not in
         ("Pen", "shade", "hexc", "font", "make")}


@functools.lru_cache(maxsize=128)
def make(name, height=120, color=None):
    fn = PROPS.get(name)
    if fn is None:
        raise KeyError(f"unknown prop '{name}'. Use one of: {', '.join(sorted(PROPS))}")
    ss = max(0.3, height * 2 / 200)
    p = Pen(200, 200, ss, lw=5)
    fn(p, color)
    return p.result(height)


if __name__ == "__main__":
    import sys
    from PIL import Image, ImageDraw
    names = sorted(PROPS)
    sheet = Image.new("RGBA", (len(names) * 140, 170), (60, 52, 48, 255))
    for i, n in enumerate(names):
        sheet.alpha_composite(make(n, 120), (i * 140 + 10, 10))
        ImageDraw.Draw(sheet).text((i * 140 + 10, 150), n, fill=(255, 255, 255))
    sheet.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "props.png")
