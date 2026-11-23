"""Vertical Short cover: INDIA MEIN (tiranga letters) BHOOL-BHULAIYA, big stone labyrinth, Knossos coin with red marker
circle, tiranga India panel with Maharashtra lit and a Boramani pin."""
import os, sys, math
os.environ.setdefault("AB_ORIENT", "vertical")
ROOT = os.path.join(os.environ.get("AB_ROOT", "/home/user/amrit-borii/"), os.environ.get("AB_PROJECT", "bhool-bhulaiya"), "")
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
def marker_circle(c, cx, cy, rx, ry, col="#FF2D3A", w=10):
    p = skia.Path()
    for i in range(0, 380, 4):
        a = math.radians(i - 20); wob = 1 + 0.012 * math.sin(i * 0.05)
        (p.moveTo if i == 0 else p.lineTo)(cx + math.cos(a) * rx * wob, cy + math.sin(a) * ry * wob)
    c.drawPath(p, paint(col, 255, stroke=w, cap_round=True))

def draw(c):
    c.drawRect(skia.Rect(0, 0, DW, DH), paint("#0B1424"))
    g = skia.GradientShader.MakeRadial(skia.Point(DW / 2, 980), 900, [hexc("#22341F"), hexc("#0B1424")])
    p_ = skia.Paint(); p_.setShader(g); c.drawRect(skia.Rect(0, 0, DW, DH), p_)
    vignette(c, 90)
    # headline
    s1 = "INDIA MEIN"; f = font(ANTON, 170); x = DW / 2 - f.measureText(s1) / 2
    cols = ["#FF9933", "#FF9933", "#FFFFFF", "#FFFFFF", "#3FB950", "#FFFFFF", "#F1FAEE", "#F1FAEE", "#F1FAEE", "#F1FAEE"]
    for ch, col in zip(s1, cols): x += outlined(c, ch, x, 240, 170, col, align="l", stroke=14)
    sz = 190 * min(1.0, 1000 / font(ANTON, 190).measureText("BHOOL-BHULAIYA"))
    outlined(c, "BHOOL-BHULAIYA", DW / 2, 450, sz, N.STONE, stroke=16)
    outlined(c, "GREECE SE LINK?", DW / 2, 585, 100, "#FFD166", stroke=12)
    # the labyrinth (drawn, 15 rings)
    N.laby(c, 470, 1010, 330, 15, 1.0, 0.0, 255)
    # Knossos coin card + red marker circle
    img = N.DOCS["coin"]; w = 330; h = w * img.height() / img.width(); cx, cy = 840, 1230
    c.save(); c.translate(cx, cy); c.rotate(5); c.translate(-cx, -cy)
    rrect(c, cx - w / 2 - 14, cy - h / 2 - 14, cx + w / 2 + 14, cy + h / 2 + 64, 14, "#FBF3DF", 255, shadow=30)
    draw_img(c, img, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    text(c, "GREEK SIKKA, c. 400 BCE", cx, cy + h / 2 + 42, 26, "#7A1E0E", FT_BLACK, "c")
    c.restore()
    marker_circle(c, cx, cy - 5, w * 0.48, h * 0.46)
    # "=" sign between them
    chain_pill(c, "= ?", 700, 830, 70, "#FF2D3A")
    # tiranga India panel with Maharashtra + Boramani pin
    l, tp, r, b = 40, 1300, 420, 1780
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(l, tp, r, b), 24, 24), True)
    c.drawRect(skia.Rect(l, tp, r, b), paint("#0F1B2D"))
    cam = (80.5, 21.5, 11.5)
    c.save(); c.translate((l + r) / 2 - DW / 2, (tp + b) / 2 - N.MAP_CY)
    c.save(); c.translate(0, N.MAP_CY - DH / 2); draw_map(c, N.WM, cam, fills={"IND": ("#FF9933", 190)}); c.restore()
    if "NOW" not in N.EMP_PATH: N.EMP_PATH["NOW"] = N._poly_path(N.WM.geoms["IND"], 0.01)
    cx_, cy_ = cam_xy(cam[0], cam[1])
    c.save(); c.translate(DW / 2, N.MAP_CY); c.scale(cam[2], cam[2]); c.translate(-cx_, -cy_)
    N.wave_flag(c, N.EMP_PATH["NOW"], "NOWV", 1.0, 255, cam[2]); N.wave_flag(c, N.EMP_PATH["NOW"], "NOWV", 1.0, 255, cam[2]); c.restore()
    N.geo_hl(c, cam, "MH", 1.0, 0.0, "#FFD166", fill=200)
    px, py = N.scr(cam, *N.PL["boramani"])
    c.drawCircle(px, py, 16, paint("#FF2D3A")); c.drawCircle(px, py, 30, paint("#FF2D3A", 255, stroke=6))
    c.restore(); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, r, b), 24, 24, paint("#FFD166", 255, stroke=6))
    chain_pill(c, "SOLAPUR", (l + r) / 2, b - 34, 34, "#FF2D3A")
    chain_pill(c, "2000 SAAL PURANI", 760, 1650, 46, "#FFD166", "#0F1B2D")
    draw_img(c, N.LOGO, DW - 150, 40, DW - 40, 150, 230)

def save():
    surf = skia.Surface(2160, 3840); c = surf.getCanvas(); c.scale(2, 2); draw(c)
    img = surf.makeImageSnapshot(); img.save(OUT + "short_thumb_master.png", skia.kPNG)
    pil = Image.open(OUT + "short_thumb_master.png").convert("RGB")
    for q in (95, 92, 88, 85, 80):
        pil.save(OUT + "short_thumb_2160x3840.jpg", quality=q)
        if os.path.getsize(OUT + "short_thumb_2160x3840.jpg") < 2_000_000: break
    pil.resize((1080, 1920), Image.LANCZOS).save(OUT + "short_thumb_1080x1920.jpg", quality=92)
    pil.resize((540, 960), Image.LANCZOS).save(OUT + "check_540.jpg", quality=90)
    print("q", q, os.path.getsize(OUT + "short_thumb_2160x3840.jpg"))
save()
