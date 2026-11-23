"""Vertical Short cover: INDIAN (tiranga letters) OCEAN, Indian Ocean map panel with tiranga India, name chain, Periplus map"""
import os, sys, math
os.environ.setdefault("AB_ORIENT", "vertical")
ROOT = os.path.join(os.environ.get("AB_ROOT", "/home/user/amrit-borii/"), os.environ.get("AB_PROJECT", "ocean-naam"), "")
sys.path.insert(0, ROOT + "visuals/engine")
import short_storyboard as N
from core import *
import skia
from PIL import Image
ANTON = os.environ.get("AB_ROOT", "/home/user/amrit-borii/") + "fonts/Anton-Regular.ttf"
OUT = ROOT + "thumbnail/"; os.makedirs(OUT, exist_ok=True)
N.load(); N.WM = N.WorldMap()

def outlined(c, s, x, y, size, col, align="c", stroke=14):
    f = font(ANTON, size); w = f.measureText(s)
    x0 = x - w / 2 if align == "c" else x
    c.drawString(s, x0 + 8, y + 12, f, paint("#000000", 150, blur=8))
    c.drawString(s, x0, y, f, paint("#000000", 255, stroke=stroke))
    c.drawString(s, x0, y, f, paint(col))
    return w
def chain_pill(c, s, x, y, size, bg, fg="#FFFFFF"):
    w = text_w(s, size, FT_BLACK); rrect(c, x - w / 2 - 26, y - size * 0.95, x + w / 2 + 26, y + size * 0.42, size * 0.7, bg, 255, shadow=14)
    text(c, s, x, y, size, fg, FT_BLACK, "c")

def draw(c):
    c.drawRect(skia.Rect(0, 0, DW, DH), paint("#0B1424"))
    g = skia.GradientShader.MakeRadial(skia.Point(DW / 2, 900), 900, [hexc("#1C2C48"), hexc("#0B1424")])
    p_ = skia.Paint(); p_.setShader(g); c.drawRect(skia.Rect(0, 0, DW, DH), p_)
    vignette(c, 90)
    f = font(ANTON, 230); x = DW / 2 - f.measureText("INDIAN") / 2
    for ch, col in zip("INDIAN", ("#FF9933", "#FF9933", "#FFFFFF", "#FFFFFF", "#3FB950", "#3FB950")):
        x += outlined(c, ch, x, 270, 230, col, align="l", stroke=16)
    outlined(c, "OCEAN", DW / 2, 470, 200, "#7FDBFF", stroke=16)
    outlined(c, "INDIA KE NAAM PE KYUN?", DW / 2, 590, 84, "#FFD166", stroke=10)
    # map panel: Indian Ocean glowing + tiranga India
    l, tp, r, b = 50, 650, 640, 1330
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(l, tp, r, b), 26, 26), True)
    cam = (78, 2, 9.5)
    c.save(); c.translate((l + r) / 2 - DW / 2, (tp + b) / 2 - N.MAP_CY)
    N.base_map2(c, cam, 1.0, 120, glows=[("#4FC3F7", 255)])
    if "NOW" not in N.EMP_PATH: N.EMP_PATH["NOW"] = N._poly_path(N.WM.geoms["IND"], 0.01)
    cx_, cy_ = cam_xy(cam[0], cam[1])
    c.save(); c.translate(DW / 2, N.MAP_CY); c.scale(cam[2], cam[2]); c.translate(-cx_, -cy_)
    N.wave_flag(c, N.EMP_PATH["NOW"], "NOWV", 1.0, 255, cam[2]); N.wave_flag(c, N.EMP_PATH["NOW"], "NOWV", 1.0, 255, cam[2]); c.restore()
    N.teer(c, cam, 1.0, 1.0)
    c.restore(); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, r, b), 26, 26, paint("#7FDBFF", 255, stroke=6))
    chain_pill(c, "SIRF 1 DESH KA OCEAN!", (l + r) / 2, b - 120, 36, "#0E5E86")
    items = [("RATNAKARA", "#C46A12"), ("ERYTHRAEAN", "#B8323A"), ("INDICUS", "#1E4F7A"), ("INDIAN OCEAN", "#FFD166")]
    for i, (s_, bg) in enumerate(items):
        y = 740 + i * 165
        chain_pill(c, s_, 862, y, 44 if i < 3 else 40, bg, "#0F1B2D" if i == 3 else "#FFFFFF")
        if i < 3:
            c.drawLine(862, y + 30, 862, y + 96, paint("#FFD166", 255, stroke=8, cap_round=True))
            ah = skia.Path(); ah.moveTo(846, y + 90); ah.lineTo(878, y + 90); ah.lineTo(862, y + 112); ah.close(); c.drawPath(ah, paint("#FFD166"))
    # the real 1597 Periplus map, framed
    img = N.DOCS["periplus"]; w = 560; h = w * img.height() / img.width(); cx, cy = DW / 2, 1580
    c.save(); c.translate(cx, cy); c.rotate(-3); c.translate(-cx, -cy)
    rrect(c, cx - w / 2 - 14, cy - h / 2 - 14, cx + w / 2 + 14, cy + h / 2 + 14, 14, "#FBF3DF", 255, shadow=30)
    draw_img(c, img, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    c.drawRect(skia.Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), paint("#B8862B", 255, stroke=4))
    c.restore()
    chain_pill(c, "NAKSHA, 1597", cx + 230, cy + h / 2 - 10, 34, "#7A1E0E")
    draw_img(c, N.LOGO, DW - 150, 40, DW - 40, 150, 230)

def save():
    surf = skia.Surface(2160, 3840); c = surf.getCanvas(); c.scale(2, 2); draw(c)
    img = surf.makeImageSnapshot(); img.save(OUT + "short_thumb_master.png", skia.kPNG)
    pil = Image.open(OUT + "short_thumb_master.png").convert("RGB")
    for q in (95, 92, 88, 85, 80):
        pil.save(OUT + "short_thumb_2160x3840.jpg", quality=q)
        if os.path.getsize(OUT + "short_thumb_2160x3840.jpg") < 2_000_000: break
    pil.resize((1080, 1920), Image.LANCZOS).save(OUT + "short_thumb_1080x1920.jpg", quality=92)
    pil.resize((360, 640), Image.LANCZOS).save(OUT + "check_360.jpg", quality=90)
    print("q", q, os.path.getsize(OUT + "short_thumb_2160x3840.jpg"))
save()
