"""Vertical Short cover: BOMBAY (struck) -> MUMBAI, seven islands panel, name chains, Mumba Devi + Catherine"""
import os, sys, math
os.environ.setdefault("AB_ORIENT", "vertical")
ROOT = os.path.join(os.environ.get("AB_ROOT", "/home/user/amrit-borii/"), os.environ.get("AB_PROJECT", "new-short"), "")
sys.path.insert(0, ROOT + "visuals/engine")
import short_storyboard as N
from core import *
from widgets import flag_circle
import skia
from PIL import Image
ANTON = os.environ.get("AB_ROOT", "/home/user/amrit-borii/") + "fonts/Anton-Regular.ttf"
OUT = ROOT + "thumbnail/"
N.load(); N.WM = N.WorldMap()
def face_img(fn, cx, cy, sz):
    im = Image.open(N.ROOT + "visuals/photos/" + fn).convert("RGB"); w, h = im.size
    s = sz * w; box = (int(cx * w - s / 2), int(cy * h - s / 2), int(cx * w + s / 2), int(cy * h + s / 2))
    return sk_image(im.crop(box).resize((600, 600), Image.LANCZOS))
def outlined(c, s, x, y, size, col, align="c", stroke=14):
    f = font(ANTON, size); w = f.measureText(s)
    x0 = x - w / 2 if align == "c" else x
    c.drawString(s, x0 + 8, y + 12, f, paint("#000000", 150, blur=8))
    c.drawString(s, x0, y, f, paint("#000000", 255, stroke=stroke))
    c.drawString(s, x0, y, f, paint(col))
    return w
def panel(c, key, cam, rect, t=1.3):
    l, tp, r, b = rect
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(l, tp, r, b), 26, 26), True)
    cx, cy = (l + r) / 2, (tp + b) / 2
    c.save(); c.translate(cx - DW / 2, cy - N.MAP_CY)
    N.base_map(c, cam, t, 1.0, 0)
    N.draw_emp(c, cam, key, 255, fill_a=170, t=t)
    c.restore(); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, r, b), 26, 26, paint(N.COL[key] if key != "RAJ" else "#FF5A6E", 255, stroke=6))
def ruler(c, img, x, y, r, ring, marker=False):
    c.drawCircle(x + 6, y + 12, r + 10, paint("#000000", 140, blur=14))
    c.drawCircle(x, y, r + 9, paint("#FFFFFF"))
    c.save(); p = skia.Path(); p.addCircle(x, y, r); c.clipPath(p, doAntiAlias=True)
    draw_img(c, img, x - r, y - r, x + r, y + r); c.restore()
    c.drawCircle(x, y, r + 9, paint(ring, 255, stroke=6))
    if marker:   # hand-drawn red marker loop
        pm = skia.Path(); R = r + 30
        pm.moveTo(x + R * math.cos(-2.2), y + R * math.sin(-2.2))
        for i in range(1, 46):
            a = -2.2 + i * (2 * math.pi + 0.5) / 45; rr = R + 6 * math.sin(i * 0.7)
            pm.lineTo(x + rr * math.cos(a), y + rr * 0.97 * math.sin(a))
        c.drawPath(pm, paint("#E63946", 255, stroke=10, cap_round=True))
def pill_t(c, s, x, y, size, bg, fg="#FFFFFF"):
    w = text_w(s, size); rrect(c, x - w / 2 - 20, y - size * 0.95, x + w / 2 + 20, y + size * 0.4, size * 0.65, bg, 255, shadow=10)
    text(c, s, x, y, size, fg, FT_BLACK, "c")

def chain_pill(c, s, x, y, size, bg, fg="#FFFFFF"):
    w = text_w(s, size, FT_BLACK); rrect(c, x - w / 2 - 26, y - size * 0.95, x + w / 2 + 26, y + size * 0.42, size * 0.7, bg, 255, shadow=14)
    text(c, s, x, y, size, fg, FT_BLACK, "c")

def draw(c):
    c.drawRect(skia.Rect(0, 0, DW, DH), paint("#0B1424"))
    g = skia.GradientShader.MakeRadial(skia.Point(DW / 2, 900), 900, [hexc("#1C2C48"), hexc("#0B1424")])
    p_ = skia.Paint(); p_.setShader(g); c.drawRect(skia.Rect(0, 0, DW, DH), p_)
    vignette(c, 90)
    w = outlined(c, "BOMBAY", DW / 2, 250, 190, "#9CC3FF", stroke=14)
    c.drawLine(DW / 2 - w / 2 - 20, 190, DW / 2 + w / 2 + 20, 160, paint("#E63946", 255, stroke=22, cap_round=True))
    outlined(c, "MUMBAI", DW / 2, 500, 250, "#FFB054", stroke=18)
    outlined(c, "NAAM KAHAN SE AAYA?", DW / 2, 640, 96, "#FFFFFF", stroke=12)
    # islands panel
    l, tp, r, b = 50, 700, 600, 1360
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(l, tp, r, b), 26, 26), True)
    cam = (72.826, 18.97, 3900)
    c.save(); c.translate((l + r) / 2 - DW / 2, (tp + b) / 2 - N.MAP_CY)
    N.base_map(c, cam, 1.0, 1.0, 0, border_a=0.3)
    N.draw_islands(c, cam, 1.0, 1.0, [1.0] * 7, {"BOMBAY": 1.0})
    c.restore(); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, r, b), 26, 26, paint("#FFD166", 255, stroke=6))
    chain_pill(c, "KABHI 7 DWEEP!", (l + r) / 2, b - 34, 44, "#C46A12")
    # chains
    chain_pill(c, "MUMBA AAI", 840, 790, 54, "#C46A12")
    c.drawLine(840, 822, 840, 880, paint("#FFD166", 255, stroke=8, cap_round=True))
    chain_pill(c, "MUMBAI", 840, 950, 60, "#FFB054", "#0F1B2D")
    chain_pill(c, "BOMBAIM", 840, 1110, 54, "#1F5FA8")
    c.drawLine(840, 1142, 840, 1200, paint("#9CC3FF", 255, stroke=8, cap_round=True))
    chain_pill(c, "BOMBAY", 840, 1270, 60, "#9CC3FF", "#0F1B2D")
    # faces
    devi = face_img("mumbadevi.jpg", 0.5, 0.33, 0.62); cat = face_img("catherine.jpg", 0.50, 0.22, 0.34)
    ruler(c, devi, 200, 1500, 115, "#FFB054", marker=True)
    ruler(c, cat, 880, 1500, 115, "#9CC3FF")
    pill_t(c, "MUMBA DEVI", 200, 1665, 32, "#C46A12"); pill_t(c, "DAHEJ?!", 880, 1665, 34, "#9E1B24")
    chain_pill(c, "\"GOOD BAY\"? NAHI!", DW / 2, 1500, 46, "#E63946")
    draw_img(c, N.LOGO, DW - 150, 40, DW - 40, 150, 230)

def save():
    surf = skia.Surface(2160, 3840); c = surf.getCanvas(); c.scale(2, 2); draw(c)
    img = surf.makeImageSnapshot(); img.save(OUT + "short_thumb_master.png", skia.kPNG)
    pil = Image.open(OUT + "short_thumb_master.png").convert("RGB")
    for q in (95, 92, 88, 85):
        pil.save(OUT + "short_thumb_2160x3840.jpg", quality=q)
        if os.path.getsize(OUT + "short_thumb_2160x3840.jpg") < 2_000_000: break
    pil.resize((1080, 1920), Image.LANCZOS).save(OUT + "short_thumb_1080x1920.jpg", quality=92)
    pil.resize((360, 640), Image.LANCZOS).save(OUT + "check_360.jpg", quality=90)
    print("q", q, os.path.getsize(OUT + "short_thumb_2160x3840.jpg"))
save()
