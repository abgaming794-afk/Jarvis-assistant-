"""Photoreal "news-documentary" thumbnail (Nitish Rajput / Dhruv Rathee / Saqlain Khan look), 3840x2160.

Layers: graded photoreal background scene -> dark side + top/bottom gradients + vignette -> cut-out face (cutout.py)
with a soft warm rim and a dark shadow, its cropped edge feathered -> hand-drawn red marker ellipse + red arrow ->
2-line Anton headline (white + yellow, thick black outline, drop shadow) -> optional tiranga India map with "?" ->
small "AI chitran" label. Bottom-right stays clear (YouTube duration stamp).

Usage: python3 thumb_photoreal.py config.json      (paths in the config are relative to the config file)
Example config: engine/examples/khilafat-india/thumbnail/thumb_config.json (made the KHILAFAT v2 thumbnail).
Outputs <out_dir>/<tag>_4K.jpg (<1.9 MB for YouTube), <tag>_4K_master.png, <tag>_1280.jpg, <tag>_check360.png.
Needs skia-python, pillow, numpy."""
import os, sys, json, math
import numpy as np
import skia
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ENG = os.path.dirname(HERE)
cfg_path = sys.argv[1]; CFG = json.load(open(cfg_path)); BASE = os.path.dirname(os.path.abspath(cfg_path))
P = lambda p: p if os.path.isabs(p) else os.path.join(BASE, p)
W, H = 3840, 2160
ANTON = skia.Typeface.MakeFromFile(os.path.join(ENG, "fonts", "Anton-Regular.ttf"))
LABEL = skia.Typeface.MakeFromFile(os.path.join(ENG, "brand", "fonts", "Montserrat-ExtraBold.ttf"))

def col(h, a=255):
    h = h.lstrip("#"); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)
def paint(h, a=255, stroke=None, blur=None):
    p = skia.Paint(AntiAlias=True, Color=col(h, a))
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p
def sk(img):
    return skia.Image.fromarray(np.ascontiguousarray(np.asarray(img.convert("RGBA"))), colorType=skia.ColorType.kRGBA_8888_ColorType)
def rgba(r, g, b, a): return skia.Color4f(r, g, b, a).toColor()

surf = skia.Surface(W, H); c = surf.getCanvas()
def grad_rect(x0, y0, x1, y1, p0, p1, c0, c1):
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=skia.GradientShader.MakeLinear([p0, p1], [c0, c1])))

# ---------------------------------------------------------------- background (cover-fit + grade)
bg = Image.open(P(CFG["background"])).convert("RGB"); s = max(W / bg.width, H / bg.height)
bg = bg.resize((math.ceil(bg.width * s), math.ceil(bg.height * s)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
g = CFG.get("grade", {})
bg = ImageEnhance.Contrast(bg).enhance(g.get("contrast", 1.12)); bg = ImageEnhance.Color(bg).enhance(g.get("saturation", 1.08))
bg = ImageEnhance.Brightness(bg).enhance(g.get("brightness", 0.86)).filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
c.drawImage(sk(bg), 0, 0)
left = CFG.get("portrait_side", "left") == "left"
if left: grad_rect(0, 0, 1900, H, (0, 0), (1900, 0), rgba(0, 0, 0, .72), rgba(0, 0, 0, 0))
else: grad_rect(W - 1900, 0, W, H, (W, 0), (W - 1900, 0), rgba(0, 0, 0, .72), rgba(0, 0, 0, 0))
grad_rect(0, 0, W, 900, (0, 0), (0, 900), rgba(.02, .01, 0, .55), rgba(0, 0, 0, 0))
grad_rect(0, 1500, W, H, (0, 1500), (0, H), rgba(0, 0, 0, 0), rgba(0, 0, 0, .75))
c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeRadial((W * .58, H * .48), W * .72,
           [rgba(0, 0, 0, 0), rgba(0, 0, 0, 0), rgba(0, 0, 0, .8)], [0, .55, 1.0])))

# ---------------------------------------------------------------- portrait cut-out
if CFG.get("portrait"):
    cut = Image.open(P(CFG["portrait"])).convert("RGBA"); sc = CFG.get("portrait_scale", 1.6)
    cw, ch = int(cut.width * sc), int(cut.height * sc); cut = cut.resize((cw, ch), Image.LANCZOS)
    A = np.asarray(cut.getchannel("A")).astype(float)
    fpx = CFG.get("fade_edge_px", 420); frow = CFG.get("fade_from_row", int(ch * .5))
    dist = (cw - 1 - np.arange(cw)) if left else np.arange(cw)          # feather the side cropped by the AI frame
    ramp = np.clip(dist / float(fpx), 0, 1) ** 1.4; rows = np.clip((np.arange(ch) - frow) / 300.0, 0, 1)[:, None]
    A = A * (1 - rows * (1 - ramp[None, :])) * np.clip((ch - np.arange(ch)) / 500.0, 0, 1)[:, None]
    alpha = Image.fromarray(A.astype("uint8")); cut.putalpha(alpha)
    lit = ImageEnhance.Contrast(ImageEnhance.Brightness(cut).enhance(1.10)).enhance(1.06); lit.putalpha(alpha)
    px, py = CFG.get("portrait_xy", [-170, 40])
    shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(70)).point(lambda v: int(v * .85)))
    rim = Image.new("RGBA", (cw, ch), tuple(CFG.get("rim_rgb", [255, 140, 40])) + (0,)); rim.putalpha(alpha.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * .28)))
    c.drawImage(sk(shadow), px + (40 if left else -40), py + 20); c.drawImage(sk(rim), px + (8 if left else -8), py - 4); c.drawImage(sk(lit), px, py)
    x0, x1 = (0, 1700) if left else (W - 1700, W)
    grad_rect(x0, 1750, x1, H, (0, 1750), (0, H), rgba(0, 0, 0, 0), rgba(0, 0, 0, .85))

# ---------------------------------------------------------------- red marker ellipse + arrow
RED = CFG.get("red", "#E63946")
if CFG.get("circle"):
    cx, cy, rx, ry = CFG["circle"]; rot = math.radians(CFG.get("circle_rot", -6)); pth = skia.Path(); n = 90
    for i in range(n + 12):
        t = i / n * 2 * math.pi; j = 1 + .035 * math.sin(3 * t + .6) + .02 * math.sin(7 * t)
        ex, ey = rx * j * math.cos(t), ry * j * math.sin(t) + (i / n) * 26
        x, y = cx + ex * math.cos(rot) - ey * math.sin(rot), cy + ex * math.sin(rot) + ey * math.cos(rot)
        (pth.moveTo if i == 0 else pth.lineTo)(x, y)
    c.drawPath(pth, paint("#000000", 140, stroke=44, blur=8)); c.drawPath(pth, paint(RED, 255, stroke=30))
if CFG.get("arrow"):
    p0, pc, p1 = CFG["arrow"]; pth = skia.Path(); pth.moveTo(*p0); pth.quadTo(*pc, *p1)
    c.drawPath(pth, paint("#000000", 150, stroke=48, blur=8)); c.drawPath(pth, paint(RED, 255, stroke=34))
    ang = math.atan2(p1[1] - pc[1], p1[0] - pc[0]); L = 120; hd = skia.Path()
    hd.moveTo(p1[0] + math.cos(ang) * 40, p1[1] + math.sin(ang) * 40)
    hd.lineTo(p1[0] + math.cos(ang + 2.5) * L, p1[1] + math.sin(ang + 2.5) * L)
    hd.lineTo(p1[0] + math.cos(ang - 2.5) * L, p1[1] + math.sin(ang - 2.5) * L); hd.close()
    c.drawPath(hd, paint("#000000", 150, blur=8)); c.drawPath(hd, paint(RED))

# ---------------------------------------------------------------- headline (2-3 words, ends with "?")
hx, hy = CFG.get("headline_xy", [1330, 470]); hs = CFG.get("headline_size", 400); gap = CFG.get("line_gap", 430)
f = skia.Font(ANTON, hs)
for k, (txt, fill) in enumerate(CFG["headline"]):
    y = hy + k * gap
    c.drawString(txt, hx + 16, y + 22, f, paint("#000000", 190, blur=16))
    c.drawString(txt, hx, y, f, paint("#000000", 255, stroke=26)); c.drawString(txt, hx, y, f, paint(fill))

# ---------------------------------------------------------------- tiranga India map with "?" (viewer stake)
im_cfg = CFG.get("india_map")
if im_cfg:
    geo = json.load(open(os.path.join(ENG, "visuals", "india_official.geojson.json")))["IND_OFFICIAL"]["coordinates"]
    (mx, my), k = im_cfg.get("center", [2000, 1720]), im_cfg.get("px_per_deg", 19.0); lon0, lat0 = im_cfg.get("center_lonlat", [80.0, 22.5])
    pr = lambda lo, la: (mx + (lo - lon0) * k, my - (la - lat0) * k * 1.06)
    ip = skia.Path()
    for poly in geo:
        ring = poly[0]
        if len(ring) < 30: continue
        for i, (lo, la) in enumerate(ring[::3]): (ip.moveTo if i == 0 else ip.lineTo)(*pr(lo, la))
        ip.close()
    b = ip.getBounds()
    c.save(); c.translate(13, 17); c.drawPath(ip, paint("#000000", 190, blur=14)); c.restore()
    c.save(); c.clipPath(ip, doAntiAlias=True)
    for i, cc in enumerate(("#FF9933", "#FFFFFF", "#138808")):
        c.drawRect(skia.Rect(b.left(), b.top() + i * b.height() / 3, b.right(), b.top() + (i + 1) * b.height() / 3), paint(cc))
    chx, chy = pr(78.6, 22.9); c.drawCircle(chx, chy, k * 1.3, paint("#000080", 255, stroke=k * .35)); c.restore()
    c.drawPath(ip, paint("#FFFFFF", 255, stroke=3))
    qx, qy = im_cfg.get("question_xy", [b.right() + 30, b.bottom() - 40]); fq = skia.Font(ANTON, im_cfg.get("question_size", 340))
    c.drawString("?", qx + 10, qy + 14, fq, paint("#000000", 180, blur=10)); c.drawString("?", qx, qy, fq, paint("#000000", 255, stroke=20))
    c.drawString("?", qx, qy, fq, paint("#FFD23F"))

# ---------------------------------------------------------------- AI label (channel rule: every AI image is labelled)
if CFG.get("ai_label"):
    c.drawString(CFG["ai_label"], 46, 2112, skia.Font(LABEL, 40), paint("#FFFFFF", 150))

# ---------------------------------------------------------------- export
img = Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)).convert("RGB")
out = P(CFG.get("out_dir", ".")); os.makedirs(out, exist_ok=True); tag = os.path.join(out, CFG.get("tag", "thumb"))
img.save(tag + "_4K_master.png"); q = 95
while True:
    img.save(tag + "_4K.jpg", quality=q)
    if os.path.getsize(tag + "_4K.jpg") < 1.9e6 or q < 70: break
    q -= 5
img.resize((1280, 720), Image.LANCZOS).save(tag + "_1280.jpg", quality=92)
img.resize((360, 203), Image.LANCZOS).save(tag + "_check360.png")
print("thumb ok", tag + "_4K.jpg", "q", q, os.path.getsize(tag + "_4K.jpg"))
