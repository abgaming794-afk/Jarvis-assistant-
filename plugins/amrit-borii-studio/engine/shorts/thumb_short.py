"""Vertical Short cover: 3 empire maps with waving flags + 3 rulers in zoom circles + 'SABSE BADA NAKSHA?'"""
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

def draw(c):
    c.drawRect(skia.Rect(0, 0, DW, DH), paint("#0B1424"))
    g = skia.GradientShader.MakeRadial(skia.Point(DW / 2, 900), 900, [hexc("#1C2C48"), hexc("#0B1424")])
    p_ = skia.Paint(); p_.setShader(g); c.drawRect(skia.Rect(0, 0, DW, DH), p_)
    vignette(c, 90)
    # headline
    outlined(c, "INDIA KA", DW / 2, 175, 120, "#FFFFFF")
    outlined(c, "SABSE BADA", DW / 2, 360, 205, "#FFD166", stroke=16)
    outlined(c, "NAKSHA?", DW / 2, 545, 185, "#FFFFFF", stroke=16)
    rows = [("MAURYA", (80, 22.0, 9.6), "ashoka", "c. 250 BCE", N.COL["MAURYA"]),
            ("MUGHAL", (79, 24.0, 9.0), "aurangzeb", "1690", N.COL["MUGHAL"]),
            ("RAJ", (81, 22.0, 8.9), "george5", "1920", "#FF5A6E")]
    faces = {"ashoka": face_img("ashoka_relief.jpg", 0.565, 0.25, 0.34), "aurangzeb": face_img("aurangzeb.jpg", 0.43, 0.37, 0.42),
             "george5": face_img("george5.jpg", 0.50, 0.21, 0.50)}
    names = {"MAURYA": "MAURYA", "MUGHAL": "MUGHAL", "RAJ": "BRITISH RAJ"}
    y0 = 610
    for i, (key, cam, fk, yr, col) in enumerate(rows):
        tp = y0 + i * 310; rect = (60, tp, 640, tp + 290)
        panel(c, key, cam, rect)
        ruler(c, faces[fk], 830, tp + 135, 112, col, marker=(key == "RAJ"))
        pill_t(c, names[key], 350, tp + 274, 38, col if key != "MAURYA" else "#B8860B")
        pill_t(c, yr, 830, tp + 290, 30, "#0F1B2D", "#FFD166")
    # dashed link between the three rulers
    pe = paint("#E63946", 230, stroke=6); pe.setPathEffect(skia.DashPathEffect.Make([18, 12], 0))
    c.drawLine(830, 610 + 300, 830, 610 + 320, pe); c.drawLine(830, 610 + 610, 830, 610 + 630, pe)
    # viewer stake: India flag with '?'
    # viewer stake: today's India as a tiranga flag-map (no logo) with a '?'
    if "NOW" not in N.EMP_PATH: N.EMP_PATH["NOW"] = N._poly_path(N.WM.geoms["IND"], 0.01)
    cam = (80.5, 22.5, 8.6); cx_, cy_ = cam_xy(cam[0], cam[1])
    c.save(); c.translate(185, 1715); c.scale(cam[2], cam[2]); c.translate(-cx_, -cy_)
    path = N.EMP_PATH["NOW"]
    c.drawPath(path, paint("#000000", 160, blur=1.2))
    c.drawPath(path, paint("#FF9933", 120))
    N.wave_flag(c, path, "NOWV", 1.0, 255, cam[2])           # same small-chakra tiranga as in the video
    N.wave_flag(c, path, "NOWV", 1.0, 255, cam[2])           # twice -> fully opaque
    c.drawPath(path, paint("#FFFFFF", 255, stroke=3.5 / cam[2]))
    c.restore()
    c.drawCircle(300, 1590, 40, paint("#000000", 120, blur=8)); c.drawCircle(296, 1584, 40, paint("#FFD166"))
    text(c, "?", 296, 1602, 56, "#0F1B2D", FT_BLACK, "c")
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
