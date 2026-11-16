"""Vertical Short cover: INDIA in tiranga colours, Indus map, name chain SINDHU>HINDU>INDOS>INDIA, Darius + Columbus"""
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
    # headline: INDIA in tiranga colours + question
    f = font(ANTON, 300); x = DW / 2 - f.measureText("INDIA") / 2
    for ch, col in zip("INDIA", ("#FF9933", "#FF9933", "#FFFFFF", "#FFFFFF", "#3FB950")):
        w = outlined(c, ch, x, 330, 300, col, align="l", stroke=18); x += w
    outlined(c, "NAAM KISNE", DW / 2, 490, 140, "#FFD166", stroke=14)
    outlined(c, "DIYA?", DW / 2, 640, 150, "#FFFFFF", stroke=14)
    # map panel: Indus glowing + tiranga India
    l, tp, r, b = 50, 700, 640, 1330
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(l, tp, r, b), 26, 26), True)
    cam = (73.5, 27.0, 26)
    c.save(); c.translate((l + r) / 2 - DW / 2, (tp + b) / 2 - N.MAP_CY)
    N.base_map(c, cam, 1.0, 1.0, 120)
    if "NOW" not in N.EMP_PATH: N.EMP_PATH["NOW"] = N._poly_path(N.WM.geoms["IND"], 0.01)
    cx_, cy_ = cam_xy(cam[0], cam[1])
    c.save(); c.translate(DW / 2, N.MAP_CY); c.scale(cam[2], cam[2]); c.translate(-cx_, -cy_)
    N.wave_flag(c, N.EMP_PATH["NOW"], "NOWV", 1.0, 255, cam[2]); N.wave_flag(c, N.EMP_PATH["NOW"], "NOWV", 1.0, 255, cam[2]); c.restore()
    N.draw_river(c, cam, 1.0, 255, 0.0, glow=1.6)
    c.restore(); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, r, b), 26, 26, paint("#7FDBFF", 255, stroke=6))
    chain_pill(c, "SINDHU NADI", (l + r) / 2, b - 30, 42, "#0E5E86")
    # name chain
    items = [("SINDHU", "#22304A"), ("HINDU", "#9E1B24"), ("INDOS", "#1F5FA8"), ("INDIA", "#FF9933")]
    for i, (s_, bg) in enumerate(items):
        y = 780 + i * 160
        chain_pill(c, s_, 850, y, 58, bg, "#0F1B2D" if s_ == "INDIA" else "#FFFFFF")
        if i < 3:
            c.drawLine(850, y + 34, 850, y + 92, paint("#FFD166", 255, stroke=8, cap_round=True))
            ah = skia.Path(); ah.moveTo(834, y + 86); ah.lineTo(866, y + 86); ah.lineTo(850, y + 108); ah.close(); c.drawPath(ah, paint("#FFD166"))
    # rulers + BHARAT
    dar = face_img("darius.jpg", 0.56, 0.30, 0.55); col = face_img("columbus.jpg", 0.56, 0.21, 0.36)
    ruler(c, dar, 190, 1480, 110, "#FF6B75")
    ruler(c, col, 890, 1480, 110, "#FFD166", marker=True)
    pill_t(c, "DARIUS", 190, 1640, 32, "#9E1B24"); pill_t(c, "COLUMBUS", 890, 1640, 32, "#0F1B2D", "#FFD166")
    chain_pill(c, "YA BHARAT?", DW / 2, 1500, 66, "#FF9933", "#0F1B2D")
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
