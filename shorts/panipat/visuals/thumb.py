"""Vertical thumbnail 2160x3840: blurred battle-on-map frame, PANIPAT?, '3 YUDH · 1 MAIDAN', three real faces with years."""
import os, sys
os.environ["AB_ORIENT"] = "vertical"
import panipat as p
from panipat import *
from PIL import Image, ImageFilter, ImageEnhance
W = 2160
bg = Image.fromarray(p.render(15.4, W)).convert("RGB").filter(ImageFilter.GaussianBlur(10))
bg = ImageEnhance.Brightness(bg).enhance(0.55)
s = skia.Surface(W, 3840); c = s.getCanvas(); c.drawImage(sk_image(bg), 0, 0); c.scale(2, 2)
g = skia.GradientShader.MakeRadial((540, 980), 900, [hexc("#000000", 0), hexc("#000000", 170)]); c.drawRect(skia.Rect(0, 0, 1080, 1920), skia.Paint(Shader=g))
# title
f = font(SERIF_DISPLAY, 210); w = f.measureText("PANIPAT"); x = 540 - (w + 120) / 2
c.drawString("PANIPAT", x + 8, 470 + 10, f, paint("#000000", 200)); 
gp = skia.GradientShader.MakeLinear([(0, 300), (0, 480)], [hexc("#FFF1A8"), hexc("#F4B400")]); pt = skia.Paint(Shader=gp, AntiAlias=True)
c.drawString("PANIPAT", x, 470, f, pt); c.drawString("PANIPAT", x, 470, f, paint("#5A3A00", 255, stroke=4))
text(c, "?", x + w + 60, 480, 240, "#E63946", SERIF_DISPLAY, "c", 255, shadow=True)
rrect(c, 150, 540, 930, 650, 18, "#C1121F", 255, shadow=16)
text(c, "3 YUDH · 1 MAIDAN", 540, 622, 70, "#FFFFFF", FT_BLACK, "c")
# three real faces
faces = [("babur", "1526"), ("akbar", "1556"), ("abdali", "1761")]
for i, (k, yr) in enumerate(faces):
    im, box, name, note = p.RP[k]; cx = 190 + i * 350; cy = 900; r = 150
    cimg = p.crop_img(im, box) if hasattr(p, "crop_img") else None
    from rulers import crop_img
    ci = crop_img(im, box)
    c.drawCircle(cx, cy + 10, r + 14, paint("#000000", 160, blur=14))
    c.save(); pth = skia.Path(); pth.addCircle(cx, cy, r); c.clipPath(pth, doAntiAlias=True)
    sc_ = max(2 * r / ci.width(), 2 * r / ci.height()); ww, hh = ci.width() * sc_, ci.height() * sc_
    draw_img(c, ci, cx - ww / 2, cy - hh / 2 + 20, cx + ww / 2, cy + hh / 2 + 20); c.restore()
    c.drawCircle(cx, cy, r, paint("#F4B400", 255, stroke=10))
    chip(c, yr, cx, cy + r + 40, 1.0, "#7A1F1F", "#FFFFFF", 50)
    text(c, ("BABUR", "AKBAR", "ABDALI")[i], cx, cy - r - 24, 40, "#FFFFFF", FT_BLACK, "c", 255, shadow=True)
# crossed swords between
from panipat import swords
for i in range(2): swords(c, 365 + i * 350, 900, 0.9, 1.0)
# question strip
rrect(c, 110, 1200, 970, 1330, 24, "#FFFFFF", 240, shadow=16)
text(c, "Kyun yahin? Delhi ka darwaza!", 540, 1285, 52, "#14213D", FT_BLACK, "c")
img = Image.fromarray(s.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)).convert("RGB")
out = os.path.join(p.PROJ, "Panipat_thumbnail.jpg"); img.save(os.path.join(p.PROJ, "render", "thumb_master.png"))
q = 92
while True:
    img.save(out, quality=q, optimize=True)
    if os.path.getsize(out) < 1.9e6 or q < 60: break
    q -= 4
print("thumb", out, os.path.getsize(out), q)
