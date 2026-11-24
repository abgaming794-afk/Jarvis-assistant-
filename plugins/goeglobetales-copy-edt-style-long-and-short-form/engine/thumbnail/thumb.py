"""AMRIT BORI thumbnail: Naya AXIS (3840x2160, 16-bit PNG master + YouTube JPG)."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import sys, math, random
sys.path.insert(0, PROJ + "visuals/engine")
import numpy as np, skia
from PIL import Image, ImageEnhance, ImageFilter
from widgets import flag_circle
W, H = 3840, 2160
OUT = PROJ + "thumbnail/"
ANTON = AB_ROOT + "fonts/Anton-Regular.ttf"
PH = PROJ + "visuals/photos/"
def F(size): return skia.Font(skia.Typeface.MakeFromFile(ANTON), size)
def P(col, a=255, **kw):
    p = skia.Paint(AntiAlias=True, Color=skia.Color(*col, a))
    if "stroke" in kw: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(kw["stroke"]); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if "blur" in kw: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, kw["blur"]))
    return p
def skimg(pil):
    a = np.ascontiguousarray(np.array(pil.convert("RGBA")))
    return skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType)
RED = (255, 38, 38); YEL = (255, 214, 10); WHITE = (255, 255, 255); NAVY = (6, 10, 22)

# ---------- photo: crop Putin / Xi / Kim, grade
X0, CW, Y0 = 840, 2260, 990
S = W / CW
im = Image.open(PH + "parade_xi_putin_kim.jpg").convert("RGB")
crop = im.crop((X0, Y0, X0 + CW, Y0 + round(H / S))).resize((W, H), Image.LANCZOS)
crop = ImageEnhance.Color(crop).enhance(0.80)
crop = ImageEnhance.Contrast(crop).enhance(1.22)
crop = crop.filter(ImageFilter.UnsharpMask(radius=3, percent=70, threshold=2))
full = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(0.85)).enhance(1.22).filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
FULL = None
def to_c(x, y): return ((x - X0) * S, (y - Y0) * S)
SRC = {"ru": (1037, 1412), "cn": (1916, 1322), "kp": (2861, 1410)}
FACES = {k: to_c(*v) for k, v in SRC.items()}
FACES['ru'] = (FACES['ru'][0] + 70, FACES['ru'][1]); FACES['kp'] = (FACES['kp'][0] - 70, FACES['kp'][1])
R_FACE = 250; ZOOM = 1.32

surf = skia.Surface(W, H); c = surf.getCanvas()
c.drawImageRect(skimg(crop), skia.Rect(0, 0, W, H), skia.SamplingOptions(skia.FilterMode.kLinear))
# darken background lattice (keep faces bright): radial spotlights on faces
dark = skia.Paint(); dark.setColor(skia.Color(4, 6, 14, 150)); c.drawRect(skia.Rect(0, 0, W, H), dark)
for code, (x, y) in FACES.items():
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y + 60), 520, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0)], [0, 1])
# re-draw faces region brighter by clipping the original photo inside soft circles
# bottom gradient for text, top gradient
g = skia.Paint(); g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 1050), skia.Point(0, H)], [skia.Color(*NAVY, 0), skia.Color(*NAVY, 235), skia.Color(*NAVY, 250)], [0, 0.55, 1])); c.drawRect(skia.Rect(0, 0, W, H), g)
g2 = skia.Paint(); g2.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 320)], [skia.Color(*NAVY, 170), skia.Color(*NAVY, 0)], [0, 1])); c.drawRect(skia.Rect(0, 0, W, 320), g2)
# vignette sides
v = skia.Paint(); v.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H * 0.42), W * 0.72, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 190)], [0, 0.6, 1])); c.drawRect(skia.Rect(0, 0, W, H), v)

FULL = skimg(full)
for code, (x, y) in FACES.items():
    sx, sy = SRC[code]
    c.drawCircle(x, y + 18, R_FACE + 20, P((0, 0, 0), 170, blur=30))
    c.save(); pth = skia.Path(); pth.addCircle(x, y, R_FACE); c.clipPath(pth, doAntiAlias=True)
    k = S * ZOOM
    c.translate(x, y); c.scale(k, k); c.translate(-sx, -sy)
    c.drawImage(FULL, 0, 0, skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    c.restore()
    c.drawCircle(x, y, R_FACE, P(WHITE, stroke=12))
# ---------- Pezeshkian (Iran) circle inset
pz = Image.open(PH + "pezeshkian_2025.jpg").convert("RGB")
pw, ph_ = pz.size
side = int(pw * 0.62); cx0 = pw // 2 - side // 2; cy0 = int(ph_ * 0.10)
pzc = ImageEnhance.Contrast(ImageEnhance.Color(pz.crop((cx0, cy0, cx0 + side, cy0 + side))).enhance(0.85)).enhance(1.15)
IR = (2640, 340); R_IR = 220
FACES_ALL = dict(FACES); FACES_ALL["ir"] = IR

# ---------- connecting "network" lines (behind circles)
def edge_line(a, b, ra, rb):
    (x1, y1), (x2, y2) = a, b; d = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / d, (y2 - y1) / d
    return (x1 + ux * ra, y1 + uy * ra), (x2 - ux * rb, y2 - uy * rb)
lp = P(RED, 235, stroke=16); lp.setPathEffect(skia.DashPathEffect.Make([46, 30], 0))
glow = P(RED, 120, stroke=34, blur=18)
links = [("ru", "cn"), ("cn", "kp"), ("cn", "ir"), ("kp", "ir")]
RAD = {"ru": R_FACE + 45, "cn": R_FACE + 45, "kp": R_FACE + 45, "ir": R_IR + 30}
for a, b in links:
    p1, p2 = edge_line(FACES_ALL[a], FACES_ALL[b], RAD[a], RAD[b])
    c.drawLine(*p1, *p2, glow); c.drawLine(*p1, *p2, lp)
    for p in (p1, p2): c.drawCircle(*p, 16, P(RED))

# Iran inset draw
c.drawCircle(IR[0], IR[1] + 14, R_IR + 18, P((0, 0, 0), 160, blur=26))
c.save(); pth = skia.Path(); pth.addCircle(*IR, R_IR); c.clipPath(pth, doAntiAlias=True)
c.drawImageRect(skimg(pzc), skia.Rect(IR[0] - R_IR, IR[1] - R_IR, IR[0] + R_IR, IR[1] + R_IR), skia.SamplingOptions(skia.FilterMode.kLinear)); c.restore()
c.drawCircle(*IR, R_IR, P(WHITE, stroke=14))

# ---------- hand-drawn red marker circles
random.seed(7)
def marker(cx, cy, r, w=26, turns=1.12, seed=0):
    rnd = random.Random(seed)
    pth = skia.Path(); n = 120; ph0 = rnd.uniform(0, 6.28)
    wob = [rnd.uniform(-1, 1) for _ in range(5)]
    for i in range(n + 1):
        t = i / n; ang = ph0 + t * turns * 2 * math.pi
        rr = r * (1 + 0.035 * math.sin(3 * ang + wob[0]) + 0.02 * math.sin(5 * ang + wob[1])) * (1 + 0.06 * t)
        x = cx + rr * math.cos(ang) * 1.04; y = cy + rr * math.sin(ang) * 0.98
        pth.moveTo(x, y) if i == 0 else pth.lineTo(x, y)
    c.drawPath(pth, P((0, 0, 0), 110, stroke=w + 14, blur=10))
    c.drawPath(pth, P(RED, stroke=w))
for i, (code, (x, y)) in enumerate(FACES.items()): marker(x, y, R_FACE + 22, seed=i + 3)
marker(IR[0], IR[1], R_IR + 26, w=22, seed=11)

# flag badges
for code, (x, y) in FACES_ALL.items():
    r = R_IR + 26 if code == "ir" else R_FACE + 18
    bx, by = x + r * 0.74, y + r * 0.78
    c.drawCircle(bx, by + 6, 74, P((0, 0, 0), 140, blur=12))
    flag_circle(c, code, bx, by, 66, ring="#FFFFFF")

# ---------- headline
def outlined(s, x, y, size, fill, stroke_w=26, shadow=True):
    f = F(size); blob = skia.TextBlob.MakeFromString(s, f)
    if shadow: c.drawTextBlob(blob, x + 18, y + 26, P((0, 0, 0), 200, blur=22))
    c.drawTextBlob(blob, x, y, P((0, 0, 0), stroke=stroke_w))
    c.drawTextBlob(blob, x, y, P(fill))
    return f.measureText(s)
SZ = 700; base = 2060
f = F(SZ); w1 = f.measureText("NAYA "); w2 = f.measureText("AXIS?")
x = 130
outlined("NAYA", x, base, SZ, WHITE)
ax = x + w1
# yellow block behind AXIS? for punch
outlined("AXIS?", ax, base, SZ, YEL)
# red underline swoosh
u = skia.Path(); u.moveTo(ax + 10, base + 40); u.quadTo(ax + w2 * 0.5, base + 70, ax + w2 - 20, base + 30)

# ---------- India corner: "INDIA KA KYA?"
ix, iy, ir_ = 3520, 1720, 175
c.drawCircle(ix, iy + 10, ir_ + 14, P((0, 0, 0), 170, blur=20))
flag_circle(c, "in", ix, iy, ir_, ring="#FFFFFF")
# big question badge
qx, qy = ix + 120, iy - 120
c.drawCircle(qx, qy, 78, P(YEL)); c.drawCircle(qx, qy, 78, P((0, 0, 0), stroke=10))
fq = F(120); c.drawString("?", qx - fq.measureText("?") / 2, qy + 44, fq, P((0, 0, 0)))

# brand bug
img = surf.makeImageSnapshot()
arr = img.toarray(colorType=skia.kRGBA_8888_ColorType)
Image.fromarray(arr[..., :3]).save(OUT + "draft.png")
print("ok", w1, w2)
