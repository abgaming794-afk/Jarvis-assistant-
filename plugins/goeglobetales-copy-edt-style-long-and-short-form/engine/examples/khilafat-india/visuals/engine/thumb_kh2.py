"""Thumbnail v2 'Photoreal' (3840x2160): photoreal AI battle (Arab cavalry vs Indian shield wall + fort) as background,
photoreal AI Muhammad bin Qasim cut-out on the left looking at the wall, headline ARAB / RUK GAYE? (Anton),
red marker circle on the shield wall + red arrow, small tiranga India map with '?', small AI label.
Bottom-right kept clear (duration stamp). Sources: thumbnail/src/*.png (user's ChatGPT images)."""
import os, math, random
os.environ.setdefault("AB_PROJECT", "khilafat-india"); os.environ.pop("AB_PREVIEW", None)
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import kh
from kh import *
W, H = 3840, 2160
ANTON = AB_ROOT + "fonts/Anton-Regular.ttf"
SRC = ROOT + "thumbnail/src/"
OUT = ROOT + "thumbnail/"

def sk(img):
    a = np.ascontiguousarray(np.asarray(img.convert("RGBA")))
    return skia.Image.fromarray(a, colorType=skia.ColorType.kRGBA_8888_ColorType)

# ---------------------------------------------------------------- background grade
bg = Image.open(SRC + "battle_photoreal.png").convert("RGB").resize((W, H), Image.LANCZOS)
bg = ImageEnhance.Contrast(bg).enhance(1.12)
bg = ImageEnhance.Color(bg).enhance(1.08)
bg = ImageEnhance.Brightness(bg).enhance(0.86)
bg = bg.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))

surf = skia.Surface(W, H); c = surf.getCanvas()
c.drawImage(sk(bg), 0, 0)

def grad_rect(x0, y0, x1, y1, pts, cols):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear(pts, cols)); c.drawRect(skia.Rect(x0, y0, x1, y1), p)

# darken left (behind the face) and the top band (headline readability), plus vignette
grad_rect(0, 0, 1900, H, [(0, 0), (1900, 0)], [skia.Color4f(0, 0, 0, 0.72).toColor(), skia.Color4f(0, 0, 0, 0).toColor()])
grad_rect(0, 0, W, 900, [(0, 0), (0, 900)], [skia.Color4f(0.02, 0.01, 0, 0.55).toColor(), skia.Color4f(0, 0, 0, 0).toColor()])
grad_rect(0, 1500, W, H, [(0, 1500), (0, H)], [skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0.75).toColor()])
vg = skia.Paint(Shader=skia.GradientShader.MakeRadial((W * 0.58, H * 0.48), W * 0.72,
                [skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0.8).toColor()], [0, 0.55, 1.0]))
c.drawRect(skia.Rect(0, 0, W, H), vg)

# ---------------------------------------------------------------- Muhammad bin Qasim cut-out
cut = Image.open(SRC + "mbq_cut.png").convert("RGBA")
sc = 1.62; cw, ch = int(cut.width * sc), int(cut.height * sc)
cut = cut.resize((cw, ch), Image.LANCZOS)
_a = np.asarray(cut.getchannel("A")).astype(float)
ramp = np.clip((cw - 1 - np.arange(cw)) / 420.0, 0, 1) ** 1.4          # right 420 px fade to 0 (source crop edge)
rows = np.clip((np.arange(ch) - 1150) / 300.0, 0, 1)[:, None]          # only below the shoulder line
_a = _a * (1 - rows * (1 - ramp[None, :]))
_a = _a * np.clip((ch - np.arange(ch)) / 500.0, 0, 1)[:, None]          # bottom fade
cut.putalpha(Image.fromarray(_a.astype("uint8")))
cut_rgb = ImageEnhance.Brightness(cut).enhance(1.10)
cut_rgb = ImageEnhance.Contrast(cut_rgb).enhance(1.06); cut_rgb.putalpha(cut.getchannel("A"))
px, py = -170, 40
# warm rim glow + dark shadow behind the figure (separates it from the scene)
alpha = cut.getchannel("A")
glow = Image.new("RGBA", (cw, ch), (255, 140, 40, 0)); glow.putalpha(alpha.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.28)))
shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(70)).point(lambda v: int(v * 0.85)))
c.drawImage(sk(shadow), px + 40, py + 20)
c.drawImage(sk(glow), px + 8, py - 4)
c.drawImage(sk(cut_rgb), px, py)
# fade the bottom of the figure into the dark floor
grad_rect(0, 1750, 1700, H, [(0, 1750), (0, H)], [skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0.85).toColor()])

# ---------------------------------------------------------------- red marker circle on the shield wall
def marker_ellipse(cx, cy, rx, ry, rot=-6, width=30, col="#E63946"):
    random.seed(7); pth = skia.Path(); n = 90
    for i in range(n + 12):
        t = i / n * 2 * math.pi; j = 1 + 0.035 * math.sin(3 * t + 0.6) + 0.02 * math.sin(7 * t)
        ex, ey = rx * j * math.cos(t), ry * j * math.sin(t) + (i / n) * 26
        r = math.radians(rot); x = cx + ex * math.cos(r) - ey * math.sin(r); y = cy + ex * math.sin(r) + ey * math.cos(r)
        (pth.moveTo if i == 0 else pth.lineTo)(x, y)
    p = paint("#000000", 140, stroke=width + 14, blur=8); p.setStrokeCap(skia.Paint.kRound_Cap); c.drawPath(pth, p)
    p = paint(col, 255, stroke=width); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join); c.drawPath(pth, p)
marker_ellipse(3260, 1440, 560, 330)

# red arrow from the headline area down to the circle
def arrow(p0, pc, p1, width=34, col="#E63946"):
    pth = skia.Path(); pth.moveTo(*p0); pth.quadTo(*pc, *p1)
    for pp, a in ((paint("#000000", 150, stroke=width + 14, blur=8), 1), (paint(col, 255, stroke=width), 1)):
        pp.setStrokeCap(skia.Paint.kRound_Cap); c.drawPath(pth, pp)
    ang = math.atan2(p1[1] - pc[1], p1[0] - pc[0]); L = 120
    hd = skia.Path(); hd.moveTo(p1[0] + math.cos(ang) * 40, p1[1] + math.sin(ang) * 40)
    hd.lineTo(p1[0] + math.cos(ang + 2.5) * L, p1[1] + math.sin(ang + 2.5) * L)
    hd.lineTo(p1[0] + math.cos(ang - 2.5) * L, p1[1] + math.sin(ang - 2.5) * L); hd.close()
    c.drawPath(hd, paint("#000000", 150, blur=8)); c.drawPath(hd, paint(col))
arrow((2330, 960), (2620, 1000), (2720, 1180))

# ---------------------------------------------------------------- headline
def outline_text(s, x, y, size, fill, stroke=26):
    f = font(ANTON, size)
    c.drawString(s, x + 16, y + 22, f, paint("#000000", 190, blur=16))
    p = paint("#000000", 255, stroke=stroke); p.setStrokeJoin(skia.Paint.kRound_Join); c.drawString(s, x, y, f, p)
    c.drawString(s, x, y, f, paint(fill))
    return f.measureText(s)
outline_text("ARAB", 1330, 470, 400, "#FFFFFF")
outline_text("RUK GAYE?", 1330, 900, 400, "#FFD23F")

# ---------------------------------------------------------------- small tiranga India map with '?'
kh.load_assets()
cx_, cy_ = cam_xy(80.0, 22.5); s_ = 19.0
c.save(); c.translate(2000, 1720); c.scale(s_, s_); c.translate(-cx_, -cy_)
ip = gpath("india", s_); b = ip.getBounds()
sh = skia.Path(ip); c.save(); c.translate(0.7, 0.9); c.drawPath(sh, paint("#000000", 190, blur=0.8)); c.restore()
c.save(); c.clipPath(ip, doAntiAlias=True)
for i, col in enumerate(("#FF9933", "#FFFFFF", "#138808")):
    c.drawRect(skia.Rect(b.left(), b.top() + i * b.height() / 3, b.right(), b.top() + (i + 1) * b.height() / 3), paint(col))
c.drawCircle(b.centerX() - 1.0, b.centerY() + 0.6, 1.3, paint("#000080", 255, stroke=0.35)); c.restore()
c.drawPath(ip, paint("#FFFFFF", 255, stroke=3 / s_)); c.restore()
fq = font(ANTON, 340)
c.drawString("?", 2330 + 10, 1960 + 14, fq, paint("#000000", 180, blur=10))
p = paint("#000000", 255, stroke=20); c.drawString("?", 2330, 1960, fq, p); c.drawString("?", 2330, 1960, fq, paint("#FFD23F"))

# ---------------------------------------------------------------- AI label (user rule: every AI image is labelled)
fl = font(FT_BLACK if "FT_BLACK" in dir(kh) else ANTON, 40)
c.drawString("AI chitran · asli tasveer nahi", 46, 2112, fl, paint("#FFFFFF", 150))

# ---------------------------------------------------------------- export
img = Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)).convert("RGB")
tag = "KHILAFAT_thumb_v2"
img.save(OUT + tag + "_4K_master.png"); q = 95
while True:
    img.save(OUT + tag + "_4K.jpg", quality=q)
    if os.path.getsize(OUT + tag + "_4K.jpg") < 1.9e6 or q < 70: break
    q -= 5
img.resize((1280, 720), Image.LANCZOS).save(OUT + tag + "_1280.jpg", quality=92)
img.resize((360, 203), Image.LANCZOS).save(OUT + "check_v2_360.png")
print("thumb ok q", q, os.path.getsize(OUT + tag + "_4K.jpg"))
