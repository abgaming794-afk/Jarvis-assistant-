"""Thumbnail 'Fauj vs dhaal' (3840x2160): Arab army arrow (left) crashes into a wall of Indian shields (right) at the
India border, tiranga India map with '?', headline ARAB RUK GAYE? (Anton). Bottom-right kept clear (duration stamp)."""
import os
os.environ.setdefault("AB_PROJECT", "khilafat-india"); os.environ.pop("AB_PREVIEW", None)
import kh
from kh import *
from PIL import Image
ANTON = AB_ROOT + "fonts/Anton-Regular.ttf"
def outline_text(c, s, x, y, size, fill, stroke=14, align="l"):
    f = font(ANTON, size); w = f.measureText(s); x0 = x - (w / 2 if align == "c" else 0)
    c.drawString(s, x0 + 10, y + 14, f, paint("#000000", 160, blur=10))
    c.drawString(s, x0, y, f, paint("#000000", 255, stroke=stroke)); c.drawString(s, x0, y, f, paint(fill))
kh.load_assets()
surf = skia.Surface(3840, 2160); c = surf.getCanvas(); c.scale(2, 2)
cam = (68.0, 24.5, 19.0)
c.clear(hexc("#0B1424")); draw_map(c, kh.WM, cam, {"IND": (SAFF, 0)}, 255)
draw_region(c, cam, "caliph", GREEN, 210)
# tiranga India map
cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
c.save(); c.translate(DW / 2, DH / 2); c.scale(s_, s_); c.translate(-cx_, -cy_)
ip = gpath("india", s_); b = ip.getBounds(); c.save(); c.clipPath(ip, doAntiAlias=True)
for i, col in enumerate(("#FF9933", "#FFFFFF", "#138808")): c.drawRect(skia.Rect(b.left(), b.top() + i * b.height() / 3, b.right(), b.top() + (i + 1) * b.height() / 3), paint(col))
c.drawCircle(b.centerX() - 1.0, b.centerY() + 0.6, 1.3, paint("#000080", 255, stroke=0.35)); c.restore()
c.drawPath(ip, paint("#FFFFFF", 255, stroke=3 / s_)); c.restore()
vignette(c, 170)
# army arrow + soldiers (left -> right)
p0 = to_screen(cam, 46.0, 31.0); p1 = to_screen(cam, 69.6, 28.6)
r_ = route(c, [p0, ((p0[0] + p1[0]) / 2, p0[1] - 90), p1], 1.0, RED, 26, dash=False)
for q in range(7):
    sx, sy, _ = along(*r_, 0.12 + q * 0.11); ic_soldier(c, sx, sy - 40, 110, q * 0.7, "#F1FAEE", 255)
pole_flag(c, p0[0] - 10, p0[1], "umayyad", 0.4, 1.0, 1.9, False)
# wall of shields at the border
for j, (col, la) in enumerate(zip(("#E76F51", "#F15BB5", "#9B5DE5", "#F8961E", "#2A9D8F", SAFF), (33.6, 31.6, 29.6, 27.6, 25.6, 23.6))):
    sx, sy = to_screen(cam, 71.2 + (0.6 if j % 2 else 0), la); shield(c, sx, sy, 125, col, 255, 1.0)
clash(c, p1[0] + 10, p1[1], 0.35, 2.4)
xs, ys = to_screen(cam, 79.5, 21.5); text(c, "?", xs, ys + 110, 300, YEL, ANTON, "c", 255, shadow=True)
outline_text(c, "ARAB", 60, 800, 210, "#FFFFFF"); outline_text(c, "RUK GAYE?", 60, 1010, 210, YEL)
out = ROOT + "thumbnail/"; os.makedirs(out, exist_ok=True)
img = Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)).convert("RGB")
img.save(out + "KHILAFAT_thumb_4K_master.png"); q = 95
while True:
    img.save(out + "KHILAFAT_thumb_4K.jpg", quality=q)
    if os.path.getsize(out + "KHILAFAT_thumb_4K.jpg") < 1.9e6 or q < 70: break
    q -= 5
img.resize((1280, 720), Image.LANCZOS).save(out + "KHILAFAT_thumb_1280.jpg", quality=92)
img.resize((360, 203), Image.LANCZOS).save(out + "check_360.png")
print("thumb ok q", q, os.path.getsize(out + "KHILAFAT_thumb_4K.jpg"))
