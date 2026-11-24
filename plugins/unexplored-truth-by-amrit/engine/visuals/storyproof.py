"""Story-then-proof effect kit (skia, design space DWxDH from core.py) - Unexplored Truth by Amrit 1.1.0.

Re-creates the editing grammar of the "How Did America Become Independent" reference (GeoGlobeTales-type explainer):
satellite map intro -> glowing region -> flag fills/peels -> parchment map switch -> map mascots with eyes and props
-> stamps, pins, neon badges, timeline ribbon -> story scene on a photoreal background -> the REAL document flies in
and the camera pans across it with marker highlights. The channel's own 2D man is drawn by the project code
(never the reference channel's characters).

Every function draws into canvas `c` at time `t` (seconds) and takes progress values k in 0..1 (use core.seg()).
Map functions take `cam = (lon, lat, px_per_degree)` like core.to_screen and a skia.Path from WorldMap.paths(s).
"""
import os, math, glob
import numpy as np
import skia
from PIL import Image, ImageFilter, ImageEnhance
from core import *

HERE = os.path.dirname(os.path.abspath(__file__)); ENG = os.path.dirname(HERE)
SERIF_DISPLAY = os.path.join(ENG, "fonts", "AbrilFatface-Regular.ttf")     # titles ("Boston Tea Party" look)
SERIF_TEXT = os.path.join(ENG, "fonts", "PlayfairDisplay-VF.ttf")          # labels, dates, list items
BLUEMARBLE = os.environ.get("AB_SATELLITE") or next(iter(glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/bluemarble.jpg", recursive=True)), "")
RED, YEL, WHITE, INK = "#E63946", "#FFD23F", "#FFFFFF", "#141414"

def _smooth(x): x = clamp(x); return x * x * (3 - 2 * x)

# =================================================================== map transform helpers
class map_space:
    """with map_space(c, cam): draw in projected map units (paths from WorldMap)."""
    def __init__(self, c, cam): self.c, self.cam = c, cam
    def __enter__(self):
        cx, cy = cam_xy(self.cam[0], self.cam[1]); s = self.cam[2]
        self.c.save(); self.c.translate(DW / 2, DH / 2); self.c.scale(s, s); self.c.translate(-cx, -cy); return s
    def __exit__(self, *a): self.c.restore()

def path_center(cam, path):
    b = path.computeTightBounds(); cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    return DW / 2 + (b.centerX() - cx) * s, DH / 2 + (b.centerY() - cy) * s

def cam_lerp(c0, c1, k):
    """smooth camera flight; zoom interpolates in log space (feels like Google Earth)."""
    k = ease_io(k)
    return (lerp(c0[0], c1[0], k), lerp(c0[1], c1[1], k), math.exp(lerp(math.log(c0[2]), math.log(c1[2]), k)))

# =================================================================== 1. satellite base (NASA Blue Marble, public domain)
_BM = {}
class Satellite:
    """Mercator-reprojected crop of the Blue Marble for the project's area (lon0..lon1, lat0..lat1).
    Build once per project area, then .draw(c, cam) every frame. Credit: 'Imagery: NASA Blue Marble'."""
    def __init__(self, lon0, lon1, lat0, lat1, src=None, out_w=None):
        Image.MAX_IMAGE_PIXELS = None
        src = src or BLUEMARBLE
        if src not in _BM: _BM[src] = np.asarray(Image.open(src).convert("RGB"))
        A = _BM[src]; H, W = A.shape[:2]
        x0, x1 = int((lon0 + 180) / 360 * W), int((lon1 + 180) / 360 * W)
        cols = A[:, x0:x1]
        my0, my1 = merc_y(lat1), merc_y(lat0)                       # top / bottom in mercator degrees
        n_out = int((x1 - x0) * (my0 - my1) / (lon1 - lon0))
        ys = np.linspace(my0, my1, n_out)
        lats = np.degrees(2 * np.arctan(np.exp(np.radians(ys))) - math.pi / 2)
        rows = np.clip(((90 - lats) / 180 * H).astype(int), 0, H - 1)
        img = Image.fromarray(cols[rows])
        img = ImageEnhance.Contrast(img).enhance(1.08); img = ImageEnhance.Color(img).enhance(1.12)
        if out_w: img = img.resize((out_w, int(out_w * img.height / img.width)), Image.LANCZOS)
        self.img = sk_image(img.filter(ImageFilter.UnsharpMask(2, 80, 2)))
        self.tl = cam_xy(lon0, lat1); self.br = cam_xy(lon1, lat0)
    def draw(self, c, cam, a=255):
        cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
        draw_img(c, self.img, DW / 2 + (self.tl[0] - cx) * s, DH / 2 + (self.tl[1] - cy) * s,
                 DW / 2 + (self.br[0] - cx) * s, DH / 2 + (self.br[1] - cy) * s, a)

# =================================================================== 2. parchment (vintage) map + paper texture
_PAPER = {}
def paper_texture(w=960, h=540, seed=3, tone=(236, 224, 196)):
    key = (w, h, seed, tone)
    if key not in _PAPER:
        rng = np.random.default_rng(seed)
        n = rng.normal(0, 1, (h // 8 + 1, w // 8 + 1)); n = np.asarray(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype("uint8")).resize((w, h), Image.BICUBIC)) / 255.0
        f = rng.normal(0, 1, (h, w)) * 0.25
        v = (n - 0.5) * 0.18 + f * 0.12
        arr = np.clip(np.array(tone)[None, None, :] * (1 + v[..., None]), 0, 255).astype("uint8")
        _PAPER[key] = sk_image(Image.fromarray(arr).filter(ImageFilter.GaussianBlur(0.6)))
    return _PAPER[key]

def paper_overlay(c, a=70, mode=skia.BlendMode.kMultiply):
    p = skia.Paint(); p.setAlphaf(a / 255); p.setBlendMode(mode)
    c.drawImageRect(paper_texture(), skia.Rect(0, 0, 960, 540), skia.Rect(0, 0, DW, DH), SAMP, p)

def parchment_map(c, wm, cam, fills=None, sea="#6F9AA4", land="#D9C9A2", coast="#9A8762", a=255, paper=80):
    """beige land / teal sea vintage map with a paper grain (the reference's 'old map' look)."""
    c.drawRect(skia.Rect(-DW, -DH, 2 * DW, 2 * DH), paint(sea, a))
    fills = fills or {}
    with map_space(c, cam) as s:
        P = wm.paths(s)
        for code, path in P.items():
            c.drawPath(path, paint(land, a))
            f = fills.get(code)
            if f: col, fa = f if isinstance(f, tuple) else (f, 255); c.drawPath(path, paint(col, int(fa * a / 255)))
            c.drawPath(path, paint(coast, int(a * 0.55), stroke=0.9 / s))
    paper_overlay(c, paper)

def style_wipe(c, k, draw_old, draw_new, to_left=True, line=True):
    """hard vertical line sweeps across; one side shows the old map style, the other the new (6.5 s in the reference)."""
    k = ease_io(k); x = DW * (1 - k) if to_left else DW * k
    old_r = skia.Rect(0, 0, x, DH) if to_left else skia.Rect(x, 0, DW, DH)
    new_r = skia.Rect(x, 0, DW, DH) if to_left else skia.Rect(0, 0, x, DH)
    c.save(); c.clipRect(old_r); draw_old(c); c.restore()
    c.save(); c.clipRect(new_r); draw_new(c); c.restore()
    if line and 0 < k < 1:
        c.drawRect(skia.Rect(x - 3, 0, x + 3, DH), paint(WHITE, 235)); c.drawRect(skia.Rect(x - 10, 0, x + 10, DH), paint(WHITE, 60, blur=8))

# =================================================================== 3. region glow, flag fill, flag peel
def region_glow(c, cam, path, k, t=0, fill="#7EC8F2", edge=WHITE):
    """light-blue translucent fill + white neon edge that fades in (states light up on their word)."""
    if k <= 0: return
    pulse = 0.85 + 0.15 * math.sin(t * 4)
    with map_space(c, cam) as s:
        c.drawPath(path, paint(fill, int(150 * k)))
        c.drawPath(path, paint(edge, int(160 * k * pulse), stroke=7 / s, blur=5 / s))
        c.drawPath(path, paint(edge, int(255 * k), stroke=1.8 / s))

def flag_fill(c, cam, path, flag, k, t=0, direction=(0, 1), wave=True, a=255):
    """the flag texture fills the region, revealed by a soft edge sweeping along `direction`
    ((0,1) = top->bottom, (1,0) = left->right); gentle cloth shading keeps it alive."""
    if k <= 0: return
    b = path.computeTightBounds()
    with map_space(c, cam) as s:
        c.save(); c.clipPath(path, doAntiAlias=True)
        c.saveLayer(skia.Rect(b.left(), b.top(), b.right(), b.bottom()))
        fw, fh = flag.width(), flag.height(); sc = max(b.width() / fw, b.height() / fh)
        w, h = fw * sc, fh * sc
        draw_img(c, flag, b.centerX() - w / 2, b.centerY() - h / 2, b.centerX() + w / 2, b.centerY() + h / 2, a)
        if wave:
            for i in range(6):
                xx = b.left() + (i / 6 + (t * 0.15) % (1 / 6)) * b.width()
                c.drawRect(skia.Rect(xx, b.top(), xx + b.width() / 12, b.bottom()), paint("#000000", 22, blur=b.width() / 40))
        dx, dy = direction; L = abs(dx) * b.width() + abs(dy) * b.height(); soft = L * 0.18
        x0 = b.left() if dx >= 0 else b.right(); y0 = b.top() if dy >= 0 else b.bottom()
        edge = -soft + (L + 2 * soft) * ease_io(k)
        p0 = (x0 + dx * (edge - soft), y0 + dy * (edge - soft)); p1 = (x0 + dx * edge, y0 + dy * edge)
        m = skia.Paint(Shader=skia.GradientShader.MakeLinear([p0, p1], [skia.ColorWHITE, skia.ColorTRANSPARENT]))
        m.setBlendMode(skia.BlendMode.kDstIn); c.drawRect(b, m)
        c.restore(); c.restore()
        c.drawPath(path, paint(WHITE, int(200 * min(1, k * 2)), stroke=1.6 / s))

def flag_peel(c, cam, path, flag, k, direction=(-0.6, 1.0), roll_col="#C9CED6"):
    """the flag peels off like a sticker (rolled edge travels along `direction`) revealing what is below
    (7-8 s in the reference: Union Jack peels off the colonies)."""
    if k >= 1: return
    b = path.computeTightBounds(); dx, dy = direction; n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
    corners = [(b.left(), b.top()), (b.right(), b.top()), (b.left(), b.bottom()), (b.right(), b.bottom())]
    proj = [x * dx + y * dy for x, y in corners]; p_min, p_max = min(proj), max(proj)
    d = lerp(p_min, p_max, ease_io(k))                  # everything with projection < d is already peeled
    with map_space(c, cam) as s:
        R = max(b.width(), b.height()) * 2
        cx, cy = dx * d, dy * d; px, py = -dy, dx       # point on the peel line and its direction
        keep = skia.Path(); keep.moveTo(cx + px * R, cy + py * R); keep.lineTo(cx - px * R, cy - py * R)
        keep.lineTo(cx - px * R + dx * R, cy - py * R + dy * R); keep.lineTo(cx + px * R + dx * R, cy + py * R + dy * R); keep.close()
        c.save(); c.clipPath(path, doAntiAlias=True); c.clipPath(keep, doAntiAlias=True)
        fw, fh = flag.width(), flag.height(); sc = max(b.width() / fw, b.height() / fh); w, h = fw * sc, fh * sc
        draw_img(c, flag, b.centerX() - w / 2, b.centerY() - h / 2, b.centerX() + w / 2, b.centerY() + h / 2)
        c.restore()
        if 0 < k < 1:                                   # the rolled-up edge (cylinder) riding the peel line
            rw = max(b.width(), b.height()) * 0.05
            c.save(); c.clipPath(path, doAntiAlias=True)
            g = skia.GradientShader.MakeLinear([(cx - dx * rw, cy - dy * rw), (cx + dx * rw * 0.2, cy + dy * rw * 0.2)],
                                               [hexc("#6B7280"), hexc(roll_col), hexc("#FFFFFF"), hexc("#8A93A0")], [0, 0.45, 0.7, 1])
            roll = skia.Path(); roll.moveTo(cx + px * R - dx * rw, cy + py * R - dy * rw); roll.lineTo(cx - px * R - dx * rw, cy - py * R - dy * rw)
            roll.lineTo(cx - px * R + dx * rw * 0.2, cy - py * R + dy * rw * 0.2); roll.lineTo(cx + px * R + dx * rw * 0.2, cy + py * R + dy * rw * 0.2); roll.close()
            c.drawPath(roll, paint("#000000", 90, blur=rw * 0.6)); c.drawPath(roll, skia.Paint(AntiAlias=True, Shader=g))
            c.restore()

def world_alliance(c, wm, cam, groups, k, t=0, stagger=0.5, land="#D9C9A2"):
    """colour whole alliances in turn (Seven Years' War red vs blue): groups = [(color, [codes]), ...]."""
    with map_space(c, cam) as s:
        P = wm.paths(s)
        for gi, (col, codes) in enumerate(groups):
            kk = ease_out(seg(k, gi * stagger / len(groups), gi * stagger / len(groups) + (1 - stagger) + stagger / len(groups)))
            for code in codes:
                if code in P and kk > 0: c.drawPath(P[code], paint(col, int(235 * kk)))

# =================================================================== 4. timeline ribbon (top of frame)
def timeline_ribbon(c, years, pos, y=70, spacing=150, vel=0.0, a=255, cx=None):
    """years = labels, pos = fractional index of the current year (animate it to rewind 1776 -> 1756).
    Current year: yellow + bigger; neighbours fade; motion-blur ghosts while |vel| > 0."""
    cx = DW / 2 if cx is None else cx
    c.drawRect(skia.Rect(cx - spacing * 1.6, y + 15, cx + spacing * 1.6, y + 19), paint("#000000", int(a * 0.35), blur=3))
    c.drawRect(skia.Rect(cx - spacing * 1.6, y + 14, cx + spacing * 1.6, y + 17.5), paint(WHITE, int(a * 0.9)))
    ghosts = [0] if abs(vel) < 0.05 else [i * vel * 14 for i in range(5)]
    for gi, off in enumerate(ghosts):
        ga = a if gi == 0 else int(a * 0.25 / gi)
        for i, yr in enumerate(years):
            dx = (i - pos) * spacing + off
            if abs(dx) > spacing * 1.7: continue
            fade = clamp(1 - (abs(dx) - spacing * 1.05) / (spacing * 0.6)); cur = clamp(1 - abs(dx) / (spacing * 0.5))
            size = lerp(44, 66, cur); col = YEL if cur > 0.5 else WHITE
            text(c, str(yr), cx + dx, y, size, col, SERIF_TEXT, "c", int(ga * fade), shadow=True)
            c.drawRect(skia.Rect(cx + dx - 1.5, y + 8, cx + dx + 1.5, y + 24), paint(WHITE, int(ga * fade)))

# =================================================================== 5. map mascots: eyes, mouth, glove hand
def googly_eyes(c, x, y, r, t=0, look=(0.3, 0.0), mood="neutral", blink_every=3.1, a=255, k=1.0):
    """two cartoon eyes on a country/territory (makes the map 'act'). mood: neutral/angry/happy/scared/sly."""
    if k <= 0: return
    r = r * back(k); bl = 1.0
    ph = (t % blink_every) / blink_every
    if ph > 0.96: bl = abs(ph - 0.98) / 0.02 * 0.9 + 0.1
    for sx in (-1, 1):
        ex = x + sx * r * 1.05
        c.save(); c.translate(ex, y); c.scale(1, bl)
        c.drawOval(skia.Rect(-r * 0.95, -r * 1.12, r * 0.95, r * 1.12), paint("#000000", int(a * 0.35), blur=r * 0.15))
        c.drawOval(skia.Rect(-r * 0.9, -r * 1.08, r * 0.9, r * 1.08), paint(WHITE, a))
        c.drawOval(skia.Rect(-r * 0.9, -r * 1.08, r * 0.9, r * 1.08), paint(INK, a, stroke=r * 0.12))
        px, py = look[0] * r * 0.38, look[1] * r * 0.45
        c.drawCircle(px, py, r * 0.42, paint(INK, a)); c.drawCircle(px + r * 0.13, py - r * 0.14, r * 0.12, paint(WHITE, a))
        c.restore()
        if mood in ("angry", "sly"):                      # brows: inner end low (angry) / flat-ish (sly)
            drop = r * (0.45 if mood == "angry" else 0.15)
            c.drawLine(ex + sx * r * 0.95, y - r * 1.5, ex - sx * r * 0.95, y - r * 1.5 + drop, paint(INK, a, stroke=r * 0.28, cap_round=True))
        if mood == "scared":                              # brows: inner end high
            c.drawLine(ex + sx * r * 0.85, y - r * 1.35, ex - sx * r * 0.85, y - r * 1.65, paint(INK, a, stroke=r * 0.2, cap_round=True))

def mascot_mouth(c, x, y, w, mood="smile", a=255):
    p = skia.Path()
    if mood == "smile": p.moveTo(x - w / 2, y); p.quadTo(x, y + w * 0.55, x + w / 2, y)
    elif mood == "frown": p.moveTo(x - w / 2, y + w * 0.25); p.quadTo(x, y - w * 0.3, x + w / 2, y + w * 0.25)
    elif mood == "grin":
        p.moveTo(x - w / 2, y); p.quadTo(x, y + w * 0.7, x + w / 2, y); p.close()
        c.drawPath(p, paint(WHITE, a)); c.drawPath(p, paint(INK, a, stroke=w * 0.08)); return
    else: p.moveTo(x - w / 2, y); p.lineTo(x + w / 2, y)
    c.drawPath(p, paint(INK, a, stroke=w * 0.1, cap_round=True))

def glove_hand(c, x, y, s, ang=0, gesture="fist", a=255):
    """white cartoon glove (shake a fist, point, hold a document). Generic, not a character."""
    c.save(); c.translate(x, y); c.rotate(ang)
    ol = paint(INK, a, stroke=s * 0.08); fl = paint(WHITE, a)
    c.drawCircle(0, 0, s * 0.5, fl); c.drawCircle(0, 0, s * 0.5, ol)
    if gesture == "point":
        c.drawRoundRect(skia.Rect(s * 0.3, -s * 0.14, s * 1.05, s * 0.14), s * 0.14, s * 0.14, fl)
        c.drawRoundRect(skia.Rect(s * 0.3, -s * 0.14, s * 1.05, s * 0.14), s * 0.14, s * 0.14, ol)
    for i in range(3):
        c.drawLine(-s * 0.15 + i * s * 0.16, -s * 0.38, -s * 0.15 + i * s * 0.16, -s * 0.05, paint(INK, a, stroke=s * 0.05, cap_round=True))
    c.drawRoundRect(skia.Rect(-s * 0.35, s * 0.42, s * 0.35, s * 0.62), s * 0.08, s * 0.08, fl)
    c.drawRoundRect(skia.Rect(-s * 0.35, s * 0.42, s * 0.35, s * 0.62), s * 0.08, s * 0.08, ol)
    c.restore()

# =================================================================== 6. props (PNG icons) that drop / pop onto the map
def prop_drop(c, img, x, y, w, k, a=255, drop=260):
    """a PNG prop (crown, hat, tax item, quill...) falls in, squashes on landing and settles; soft contact shadow."""
    if k <= 0: return
    h = w * img.height() / img.width()
    fall = 1 - ease_in(clamp(k / 0.55)); land = seg(k, 0.55, 1.0)
    sq = 1 + 0.18 * math.sin(math.pi * land) if land < 1 else 1.0
    yy = y - fall * drop
    c.drawOval(skia.Rect(x - w * 0.42, y + h * 0.42, x + w * 0.42, y + h * 0.56), paint("#000000", int(80 * clamp(k * 2)), blur=8))
    draw_img(c, img, x - w / 2 * sq, yy - h / 2 / sq + h * (1 - 1 / sq) / 2, x + w / 2 * sq, yy + h / 2, int(a * clamp(k * 3)))

def pop_icon(c, img, x, y, w, k, a=255, rot=0):
    """quick scale-pop (back easing) for icons that appear on a word (tax items, pitchforks, torches)."""
    if k <= 0: return
    s = back(clamp(k)); h = w * img.height() / img.width()
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawOval(skia.Rect(-w * 0.45, -h * 0.45 + 6, w * 0.45, h * 0.55 + 6), paint("#000000", 70, blur=10))
    draw_img(c, img, -w / 2, -h / 2, w / 2, h / 2, a); c.restore()

# =================================================================== 7. stamp slam, shake, pins, neon badges
def stamp_slam(c, s, x, y, size, k, col=RED, ang=-8, a=255, box=True):
    """rubber stamp ('DEBT', 'TAXED', 'CLOSED') slams from 2.4x to 1x with an ink flash and a tiny bounce."""
    if k <= 0: return
    sc = lerp(2.4, 1.0, ease_in(clamp(k / 0.45))) if k < 0.45 else 1 + 0.06 * math.sin(math.pi * seg(k, 0.45, 0.75))
    al = int(a * clamp(k / 0.3))
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(sc, sc)
    f = font(SERIF_DISPLAY, size); w = f.measureText(s)
    if box:
        pad = size * 0.28
        c.drawRoundRect(skia.Rect(-w / 2 - pad, -size * 0.78, w / 2 + pad, size * 0.36), size * 0.12, size * 0.12, paint(col, al, stroke=size * 0.09))
        c.drawRoundRect(skia.Rect(-w / 2 - pad * 0.65, -size * 0.66, w / 2 + pad * 0.65, size * 0.24), size * 0.08, size * 0.08, paint(col, int(al * 0.7), stroke=size * 0.03))
    c.drawString(s, -w / 2, 0, f, paint(col, al))
    p = skia.Paint(); p.setAlphaf(0.35 * al / 255); p.setBlendMode(skia.BlendMode.kDstOut)     # worn ink
    c.drawImageRect(paper_texture(seed=11, tone=(255, 255, 255)), skia.Rect(0, 0, 240, 135), skia.Rect(-w / 2 - size, -size, w / 2 + size, size * 0.6), SAMP, p)
    c.restore()

def shake(t, t0, amp=10, dur=0.35):
    """camera offset (dx, dy) for a hit (stamp, cannon). Apply with c.translate(*shake(...))."""
    k = seg(t, t0, t0 + dur)
    if k <= 0 or k >= 1: return 0.0, 0.0
    d = (1 - k) ** 2 * amp
    return d * math.sin(t * 90), d * math.cos(t * 77)

def pin_drop(c, x, y, label, date=None, k=1.0, t=0, col=RED, a=255, side="r"):
    """red location pin drops with a bounce, a pulse ring spreads, serif label + small date appear."""
    if k <= 0: return
    fall = (1 - back(clamp(k / 0.5))) * 90; yy = y - fall
    ring = (t * 0.8) % 1.0
    c.drawCircle(x, y, 10 + 34 * ring, paint(col, int(a * 0.8 * (1 - ring)), stroke=3))
    c.drawOval(skia.Rect(x - 9, y - 3, x + 9, y + 3), paint("#000000", int(a * 0.4), blur=3))
    pth = skia.Path(); pth.moveTo(x, yy); pth.cubicTo(x - 30, yy - 30, x - 18, yy - 56, x, yy - 56); pth.cubicTo(x + 18, yy - 56, x + 30, yy - 30, x, yy)
    c.drawPath(pth, paint("#000000", int(a * 0.35), blur=4)); c.drawPath(pth, paint(col, a)); c.drawCircle(x, yy - 38, 7, paint(WHITE, a))
    lk = seg(k, 0.45, 1.0)
    if lk > 0:
        lx = x + 26 if side == "r" else x - 26; al = "l" if side == "r" else "r"
        text(c, label, lx, y - 26, 38, WHITE, SERIF_DISPLAY, al, int(a * lk), shadow=True)
        if date: text(c, date, lx, y + 4, 22, WHITE, SERIF_TEXT, al, int(a * lk * 0.9), shadow=True)

def neon_badge(c, x, y, r, k, t=0, col="#FF4D6D", icon=None, crossed=False, a=255):
    """glowing circular badge with a white icon (callable icon(c, x, y, size)), optional red strike-through
    (boycott / ban / closed factory)."""
    if k <= 0: return
    s = back(clamp(k)); fl = 0.8 + 0.2 * math.sin(t * 6)
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(0, 0, r * 1.25, paint(col, int(a * 0.35 * fl), blur=r * 0.5))
    c.drawCircle(0, 0, r, paint("#10131A", int(a * 0.55))); c.drawCircle(0, 0, r, paint(col, a, stroke=r * 0.12))
    c.drawCircle(0, 0, r, paint(WHITE, int(a * 0.7), stroke=r * 0.03))
    if icon: icon(c, 0, 0, r * 1.1)
    if crossed: c.drawLine(-r * 0.7, -r * 0.7, r * 0.7, r * 0.7, paint(col, a, stroke=r * 0.16, cap_round=True))
    c.restore()

def white_arrow(c, x, y, ang=135, size=90, t=0, k=1.0, a=255):
    """chunky white arrow that bobs toward the thing being talked about."""
    if k <= 0: return
    bob = math.sin(t * 7) * size * 0.08
    c.save(); c.translate(x, y); c.rotate(ang); c.translate(-bob - size * (1 - ease_out(k)) * 0.6, 0)
    p = skia.Path(); s = size
    p.moveTo(0, 0); p.lineTo(-s * 0.45, -s * 0.38); p.lineTo(-s * 0.45, -s * 0.14); p.lineTo(-s, -s * 0.14)
    p.lineTo(-s, s * 0.14); p.lineTo(-s * 0.45, s * 0.14); p.lineTo(-s * 0.45, s * 0.38); p.close()
    c.drawPath(p, paint("#000000", int(a * 0.4), blur=8)); c.drawPath(p, paint(WHITE, int(a * clamp(k * 2)))); c.restore()

def hand_arrow(c, p0, p1, k, bend=0.35, col=WHITE, w=4, a=255):
    """hand-drawn curved arrow that draws itself from a title to the region (e.g. date -> map)."""
    if k <= 0: return
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2; dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    cp = (mx - dy * bend, my + dx * bend)
    pth = skia.Path(); pth.moveTo(*p0); pth.quadTo(*cp, *p1)
    pm = skia.PathMeasure(pth, False); L = pm.getLength(); part = skia.Path()
    pm.getSegment(0, L * ease_io(k), part, True)
    c.drawPath(part, paint(col, a, stroke=w, cap_round=True))
    if k > 0.85:
        pos, tan = pm.getPosTan(L)
        ang = math.atan2(tan.y(), tan.x()); hl = w * 5; ha = int(a * seg(k, 0.85, 1))
        for s in (2.6, -2.6):
            c.drawLine(pos.x(), pos.y(), pos.x() + math.cos(ang + s) * hl, pos.y() + math.sin(ang + s) * hl, paint(col, ha, stroke=w, cap_round=True))

# =================================================================== 8. transitions
def iris(c, k, cx=None, cy=None, wobble=0.06, t=0, col="#000000"):
    """ink-blot iris: k 0->1 closes to black (68 s in the reference), run 1->0 to open on the next scene."""
    if k <= 0: return
    cx = DW / 2 if cx is None else cx; cy = DH / 2 if cy is None else cy
    R = math.hypot(DW, DH) * 0.62 * (1 - ease_in(k))
    p = skia.Path(); p.setFillType(skia.PathFillType.kEvenOdd); p.addRect(skia.Rect(-10, -10, DW + 10, DH + 10))
    n = 72
    for i in range(n + 1):
        th = i / n * 2 * math.pi; rr = R * (1 + wobble * math.sin(5 * th + t * 3) + wobble * 0.5 * math.sin(11 * th))
        (p.moveTo if i == 0 else p.lineTo)(cx + rr * math.cos(th), cy + rr * math.sin(th))
    p.close(); c.drawPath(p, paint(col, 255, blur=6 if R > 5 else None))

def whip_blur(c, frame_img, k, cx=None, cy=None, n=6):
    """radial zoom-blur whip between two shots: draw a snapshot (skia.Image of the frame) scaled ghosts."""
    if k <= 0: return
    cx = DW / 2 if cx is None else cx; cy = DH / 2 if cy is None else cy
    for i in range(1, n + 1):
        s = 1 + 0.035 * i * k; p = skia.Paint(); p.setAlphaf(0.22 * k)
        c.save(); c.translate(cx, cy); c.scale(s, s); c.translate(-cx, -cy)
        c.drawImageRect(frame_img, skia.Rect(0, 0, frame_img.width(), frame_img.height()), skia.Rect(0, 0, DW, DH), SAMP, p); c.restore()

# =================================================================== 9. typography: serif title, quote
def serif_title(c, s, x, y, size, k, date=None, col=WHITE, align="l", a=255, stagger=0.55):
    """classic serif title revealed letter by letter (each letter fades + rises), small yellow date below."""
    if k <= 0: return
    f = font(SERIF_DISPLAY, size); w = f.measureText(s)
    x0 = x - (w / 2 if align == "c" else (w if align == "r" else 0)); xx = x0; n = max(1, len(s))
    for i, ch in enumerate(s):
        kk = seg(k, i / n * stagger, i / n * stagger + (1 - stagger))
        if kk > 0:
            c.drawString(ch, xx + size * 0.04, y + size * 0.06 + (1 - ease_out(kk)) * size * 0.25, f, paint("#000000", int(a * 0.5 * kk)))
            c.drawString(ch, xx, y + (1 - ease_out(kk)) * size * 0.25, f, paint(col, int(a * kk)))
        xx += f.measureText(ch)
    if date:
        dk = seg(k, 0.7, 1.0); text(c, date, x0 + w / 2, y + size * 0.55, size * 0.36, YEL, SERIF_TEXT, "c", int(a * dk), shadow=True)

def quote_line(c, s, who, x, y, size, k, a=255):
    """'The shot heard round the world.' - words appear one by one, attribution small under it."""
    words = s.split(); f = font(SERIF_DISPLAY, size); xx = x - f.measureText(s) / 2
    for i, wd in enumerate(words):
        kk = seg(k, i / len(words) * 0.7, i / len(words) * 0.7 + 0.3)
        if kk > 0: c.drawString(wd, xx, y, f, paint("#000000", int(a * 0.5 * kk), blur=3)); c.drawString(wd, xx, y - 2, f, paint(WHITE, int(a * kk)))
        xx += f.measureText(wd + " ")
    if who: text(c, who, x + f.measureText(s) / 2, y + size * 0.6, size * 0.3, WHITE, SERIF_TEXT, "r", int(a * seg(k, 0.8, 1)), shadow=True)

# =================================================================== 10. PROOF: real document fly-in + pan with highlights
def doc_fly(c, img, k, rect, frm=(1.4, -0.3), rot0=-28, rot1=-3, tilt=0.00035, a=255, border=0.025, ghosts=5):
    """the REAL document / print / scan flies in from off-screen (motion-blur ghosts), spins down to a slight
    angle, with a perspective tilt, white paper border and drop shadow (84 s in the reference)."""
    if k <= 0: return
    l, t_, r, b = rect; w, h = r - l, b - t_; cx1, cy1 = (l + r) / 2, (t_ + b) / 2
    def place(kk, alpha):
        e = ease_out(clamp(kk)); cx = lerp(cx1 + frm[0] * DW, cx1, e); cy = lerp(cy1 + frm[1] * DH, cy1, e)
        ang = lerp(rot0, rot1, e); per = tilt * (1 - e * 0.6)
        c.save(); c.translate(cx, cy); c.rotate(ang)
        m = skia.Matrix(); m.setAll(1, 0, 0, 0, 1, 0, per, 0, 1); c.concat(m)
        pb = w * border
        c.drawRect(skia.Rect(-w / 2 - pb + 18, -h / 2 - pb + 26, w / 2 + pb + 18, h / 2 + pb + 26), paint("#000000", int(alpha * 0.45), blur=22))
        c.drawRect(skia.Rect(-w / 2 - pb, -h / 2 - pb, w / 2 + pb, h / 2 + pb), paint("#F4EFE4", alpha))
        draw_img(c, img, -w / 2, -h / 2, w / 2, h / 2, alpha); c.restore()
    if k < 1:
        for g in range(ghosts, 0, -1): place(k - g * 0.035, int(a * 0.12))
    place(k, a)

def doc_pan(c, img, t, t0, dur, r0, r1, highlights=(), dof=True, a=255, hl_col="#FFE14D"):
    """camera glides across a real document page (normalised source rects r0 -> r1, each (x0, y0, x1, y1) in 0..1)
    with a depth-of-field falloff top/bottom and yellow marker highlights that sweep over the key words.
    highlights = [(x0, y0, x1, y1, t_start, t_end)] in normalised image coords, absolute seconds."""
    k = ease_io(seg(t, t0, t0 + dur)); W, H = img.width(), img.height()
    sr = [lerp(r0[i], r1[i], k) for i in range(4)]
    src = skia.Rect(sr[0] * W, sr[1] * H, sr[2] * W, sr[3] * H)
    sx = DW / src.width(); sy = DH / src.height(); s = max(sx, sy)
    dst_w, dst_h = src.width() * s, src.height() * s; ox, oy = (DW - dst_w) / 2, (DH - dst_h) / 2
    draw_img(c, img, ox, oy, ox + dst_w, oy + dst_h, a, src)
    for (x0, y0, x1, y1, ts, te) in highlights:
        hk = seg(t, ts, te)
        if hk <= 0: continue
        X0 = ox + (x0 * W - src.left()) * s; X1 = ox + (x1 * W - src.left()) * s
        Y0 = oy + (y0 * H - src.top()) * s; Y1 = oy + (y1 * H - src.top()) * s
        p = paint(hl_col, int(200 * min(1, a / 255))); p.setBlendMode(skia.BlendMode.kMultiply)
        c.drawRoundRect(skia.Rect(X0 - 6, Y0, lerp(X0, X1, ease_out(hk)) + 6, Y1), 6, 6, p)
    if dof:
        for top in (True, False):
            band = skia.Rect(0, 0, DW, DH * 0.24) if top else skia.Rect(0, DH * 0.76, DW, DH)
            c.save(); c.clipRect(band)
            lp = skia.Paint(ImageFilter=skia.ImageFilters.Blur(9, 9)); c.saveLayer(band, lp)
            draw_img(c, img, ox, oy, ox + dst_w, oy + dst_h, a, src); c.restore(); c.restore()
        g = skia.GradientShader.MakeLinear([(0, 0), (0, DH)], [hexc("#FFFFFF", 90), hexc("#FFFFFF", 0), hexc("#FFFFFF", 0), hexc("#FFFFFF", 90)], [0, 0.22, 0.78, 1])
        c.drawRect(skia.Rect(0, 0, DW, DH), skia.Paint(Shader=g))

def parchment_card(c, l, t_, r, b, a=255, seed=5):
    """aged paper card (tax list, decree): warm paper, darker burnt edge, soft shadow."""
    c.drawRect(skia.Rect(l + 14, t_ + 22, r + 14, b + 22), paint("#000000", int(a * 0.4), blur=20))
    c.save(); c.clipRect(skia.Rect(l, t_, r, b))
    c.drawImageRect(paper_texture(seed=seed, tone=(226, 204, 160)), skia.Rect(0, 0, 960, 540), skia.Rect(l, t_, r, b), SAMP, skia.Paint(Alphaf=a / 255))
    g = skia.GradientShader.MakeRadial(((l + r) / 2, (t_ + b) / 2), max(r - l, b - t_) * 0.7, [hexc("#000000", 0), hexc("#5A3A12", int(a * 0.55))], [0.6, 1.0])
    c.drawRect(skia.Rect(l, t_, r, b), skia.Paint(Shader=g)); c.restore()

def parchment_list(c, x, y, w, items, t, a=255, size=46, gap=78):
    """vertical list on parchment: items = [dict(text, icon=None, t_in, t_strike=None, t_stamp=None, t_circle=None)].
    Each item writes in, may be struck through (red line), stamped (TAXED) and circled (green hand ellipse)."""
    parchment_card(c, x, y, x + w, y + gap * len(items) + 60, a)
    for i, it in enumerate(items):
        yy = y + 60 + i * gap; k = seg(t, it["t_in"], it["t_in"] + 0.4)
        if k <= 0: continue
        if it.get("icon"): it["icon"](c, x + 60, yy - size * 0.3, size * 0.9)
        text(c, it["text"], x + 110, yy, size, "#2B1D0E", SERIF_TEXT, "l", int(a * k))
        tw = text_w(it["text"], size, SERIF_TEXT)
        if it.get("t_strike") is not None:
            sk_ = seg(t, it["t_strike"], it["t_strike"] + 0.3)
            if sk_ > 0: c.drawLine(x + 50, yy - size * 0.32, x + 50 + (tw + 80) * ease_out(sk_), yy - size * 0.36, paint("#B3202A", a, stroke=5, cap_round=True))
        if it.get("t_stamp") is not None: stamp_slam(c, "TAXED", x + w - 110, yy - size * 0.3, size * 0.55, seg(t, it["t_stamp"], it["t_stamp"] + 0.4), "#C1121F", -6, a)
        if it.get("t_circle") is not None:
            ck = seg(t, it["t_circle"], it["t_circle"] + 0.6)
            if ck > 0:
                p = skia.Path(); n = 60
                for j in range(int(n * ease_out(ck)) + 1):
                    th = j / n * 2.15 * math.pi - 1.2
                    px = x + 60 + (tw + 120) / 2 + (tw + 150) / 2 * math.cos(th); py = yy - size * 0.3 + size * 0.85 * math.sin(th) + j * 0.12
                    (p.moveTo if j == 0 else p.lineTo)(px, py)
                c.drawPath(p, paint("#2FA84F", a, stroke=6, cap_round=True))

# =================================================================== 11. war / movement on the map
def fireworks(c, x, y, t, t0, col="#FFD6E8", n=28, R=70, a=255):
    """celebration burst (independence, victory): particles fly out, fall with gravity, sparkle and fade."""
    k = (t - t0) / 1.2
    if k <= 0 or k >= 1: return
    rng = np.random.default_rng(int(x * 7 + y * 13))
    for i in range(n):
        ang = i / n * 2 * math.pi + rng.uniform(-0.1, 0.1); sp = R * rng.uniform(0.7, 1.1)
        px = x + math.cos(ang) * sp * ease_out(k); py = y + math.sin(ang) * sp * ease_out(k) + 40 * k * k
        al = int(a * (1 - k) * (0.6 + 0.4 * math.sin(t * 30 + i)))
        c.drawCircle(px, py, 3.2 * (1 - k * 0.5), paint(col, al)); c.drawCircle(px, py, 8, paint(col, al // 4, blur=5))

def march(c, pts, k, t, n=4, unit=None, col=WHITE, dash=True, smoke_at=None, a=255):
    """units advance along a (dashed) route: pts in screen coords, unit(c, x, y, phase) draws one marcher
    (your own icon / 2D man); smoke puffs at `smoke_at` (fraction) once the head passes it."""
    if k <= 0: return
    pth = skia.Path(); pth.moveTo(*pts[0])
    for q in pts[1:]: pth.lineTo(*q)
    pm = skia.PathMeasure(pth, False); L = pm.getLength(); part = skia.Path(); pm.getSegment(0, L * k, part, True)
    p = paint(col, int(a * 0.8), stroke=3.5, cap_round=True)
    if dash: p.setPathEffect(skia.DashPathEffect.Make([14, 12], -t * 30))
    c.drawPath(part, p)
    for i in range(n):
        f = k - i * 0.05
        if f <= 0: continue
        pos, _ = pm.getPosTan(L * f)
        if unit: unit(c, pos.x(), pos.y(), t * 6 + i)
        else: c.drawCircle(pos.x(), pos.y(), 9, paint(col, a))
    if smoke_at is not None and k > smoke_at:
        pos, _ = pm.getPosTan(L * smoke_at); sk_ = seg(k, smoke_at, smoke_at + 0.25)
        for j in range(5):
            c.drawCircle(pos.x() + (j - 2) * 14 * sk_, pos.y() - 20 * sk_ - j * 4, 12 + 16 * sk_, paint("#E8E8E8", int(a * 0.55 * (1 - sk_)), blur=6))

def flag_markers(c, items, t, t0, gap=0.12, size=34, a=255):
    """many small flags pop onto battle sites one after another: items = [(x, y, skia.Image flag), ...]."""
    for i, (x, y, fl) in enumerate(items):
        k = seg(t, t0 + i * gap, t0 + i * gap + 0.3)
        if k <= 0: continue
        s = back(k); w = size * s; h = w * fl.height() / fl.width()
        c.drawLine(x, y, x, y - size * 1.1 * s, paint(INK, a, stroke=2.5))
        draw_img(c, fl, x, y - size * 1.1 * s, x + w, y - size * 1.1 * s + h, a)

# =================================================================== 12. story scene on a photoreal background
def story_scene(c, bg, t, t0, dur, push=(1.0, 1.08), focus=(0.5, 0.5), layers=(), a=255):
    """photoreal (AI or real photo) background with a slow Ken-Burns push; `layers` are your own cut-outs
    [dict(img, x, y, h, depth)] - depth 0 = background plane, 1 = foreground (moves most -> parallax).
    Draw the channel's 2D man yourself after this call (never the reference channel's characters)."""
    k = ease_io(seg(t, t0, t0 + dur)); s = lerp(push[0], push[1], k)
    bw, bh = bg.width(), bg.height(); cov = max(DW / bw, DH / bh) * s
    w, h = bw * cov, bh * cov; ox = DW * focus[0] - w * focus[0]; oy = DH * focus[1] - h * focus[1]
    draw_img(c, bg, ox, oy, ox + w, oy + h, a)
    for L in layers:
        img = L["img"]; lh = L["h"] * (1 + (s - 1) * (1 + L.get("depth", 0.5)))
        lw = lh * img.width() / img.height(); px = L["x"] + (L["x"] - DW / 2) * (s - 1) * L.get("depth", 0.5)
        draw_img(c, img, px - lw / 2, L["y"] - lh, px + lw / 2, L["y"], a)

def crowd_silhouettes(c, n, y, t, col="#1B1B1F", size=120, a=255, seed=4):
    """dark heads-and-shoulders crowd in the foreground that bobs (watching a speech / a protest).
    Generic silhouettes, not the reference channel's characters."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = (i + 0.5) / n * DW + rng.uniform(-20, 20); s = size * rng.uniform(0.85, 1.15)
        yy = y + math.sin(t * 5 + i * 1.7) * 4 + rng.uniform(-10, 18)
        c.drawOval(skia.Rect(x - s * 0.62, yy - s * 0.15, x + s * 0.62, yy + s * 0.9), paint(col, a))
        c.drawCircle(x, yy - s * 0.42, s * 0.36, paint(col, a))

# =================================================================== 13. 3D map: tilted perspective, camera orbit, extruded regions, standing pins
def map3d_matrix(tilt=0.6, rot=0.0, pivot=None):
    """perspective that lays the flat frame on the ground like Google Earth's tilt. tilt 0 = top-down, 1 = strong.
    rot = camera orbit in degrees (rotates the ground around `pivot`)."""
    pv = pivot or (DW / 2, DH * 0.62); tl = clamp(tilt)
    top_y = DH * 0.30 * tl; top_hw = DW / 2 * (1 - 0.42 * tl); bot_y = DH * (1 + 0.30 * tl); bot_hw = DW / 2 * (1 + 0.55 * tl)
    dst = [(DW / 2 - top_hw, top_y), (DW / 2 + top_hw, top_y), (DW / 2 + bot_hw, bot_y), (DW / 2 - bot_hw, bot_y)]
    if rot:
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        dst = [(pv[0] + (x - pv[0]) * ca - (y - pv[1]) * sa * 0.35, pv[1] + (x - pv[0]) * sa * 0.35 + (y - pv[1]) * ca) for x, y in dst]
    m = skia.Matrix(); m.setPolyToPoly([skia.Point(0, 0), skia.Point(DW, 0), skia.Point(DW, DH), skia.Point(0, DH)], [skia.Point(*p) for p in dst])
    return m

def map3d(c, draw_flat, tilt=0.6, rot=0.0, sky=("#0B1424", "#E9B872"), fog=True):
    """render `draw_flat(cc)` (any flat map scene) into an offscreen layer and lay it down in 3D.
    Returns the matrix M: use proj(M, x, y), extrude(c, M, ...), pin3d(c, M, ...) for 3D extras."""
    sc = c.getTotalMatrix().getScaleX(); E = 1.0 + 0.7 * clamp(tilt * 1.5)        # draw a bigger flat plane so its edges stay off-screen
    mx, my = DW * (E - 1) / 2, DH * (E - 1) / 2
    surf = skia.Surface(max(2, int(DW * E * sc)), max(2, int(DH * E * sc))); cc = surf.getCanvas(); cc.scale(sc, sc); cc.translate(mx, my); draw_flat(cc)
    img = surf.makeImageSnapshot(); M = map3d_matrix(tilt, rot)
    if tilt > 0 and sky:
        g = skia.GradientShader.MakeLinear([(0, 0), (0, DH * 0.42)], [hexc(sky[0]), hexc(sky[1])])
        c.drawRect(skia.Rect(0, 0, DW, DH), skia.Paint(Shader=g))
    c.save(); c.concat(M); c.drawImageRect(img, skia.Rect(0, 0, img.width(), img.height()), skia.Rect(-mx, -my, DW + mx, DH + my), SAMP); c.restore()
    if fog and tilt > 0:
        top = M.mapXY(DW / 2, 0).y()
        g = skia.GradientShader.MakeLinear([(0, top - 10), (0, top + DH * 0.22)], [hexc(sky[1], int(230 * tilt)), hexc(sky[1], 0)])
        c.drawRect(skia.Rect(0, 0, DW, DH), skia.Paint(Shader=g))
    return M

def flat_path(cam, path):
    """a WorldMap path (map units) -> flat design-space path (what map_space draws)."""
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    m = skia.Matrix(); m.setAll(s, 0, DW / 2 - cx * s, 0, s, DH / 2 - cy * s, 0, 0, 1)
    p = skia.Path(path); p.transform(m); return p

def proj(M, x, y):
    q = M.mapXY(x, y); return q.x(), q.y()

def extrude(c, M, fpath, height, col, k=1.0, top=None, glow=True, steps=10):
    """region rises out of the 3D ground: side walls (darker) + lit top face + edge glow. fpath from flat_path()."""
    if k <= 0: return
    h = height * ease_out(k); p = skia.Path(fpath); p.transform(M)
    for i in range(steps + 1):
        f = i / steps; shade = int(255 * (0.55 + 0.25 * f))
        c.save(); c.translate(0, -h * f)
        c.drawPath(p, paint(col, int(255 * min(1, k * 2))) if i == steps else paint("#000000", 0))
        if i < steps:
            pp = paint(col, int(min(255, 255 * k * 2))); pp.setColorFilter(skia.ColorFilters.Blend(hexc("#000000", 255 - shade), skia.BlendMode.kSrcATop)); c.drawPath(p, pp)
        c.restore()
    c.save(); c.translate(0, -h)
    if top: c.drawPath(p, paint(top, int(180 * k)))
    if glow: c.drawPath(p, paint("#FFFFFF", int(150 * k), stroke=5, blur=4)); c.drawPath(p, paint("#FFFFFF", int(230 * k), stroke=1.6))
    c.restore()

def pin3d(c, M, x, y, label=None, k=1.0, t=0, col=RED, h=130, sub=None, a=255):
    """a pin/flag standing UP from the tilted ground (pole in screen space -> real 3D feel)."""
    if k <= 0: return
    bx, by = proj(M, x, y); hh = h * back(clamp(k))
    c.drawOval(skia.Rect(bx - 16, by - 5, bx + 16, by + 5), paint("#000000", int(a * 0.45), blur=4))
    c.drawLine(bx, by, bx, by - hh, paint("#F4EFE4", a, stroke=4, cap_round=True))
    c.drawCircle(bx, by - hh, 15, paint("#000000", int(a * 0.35), blur=5)); c.drawCircle(bx, by - hh, 13, paint(col, a)); c.drawCircle(bx - 4, by - hh - 4, 4, paint(WHITE, a))
    if label:
        lk = seg(k, 0.4, 1.0); text(c, label, bx + 22, by - hh + 12, 36, WHITE, SERIF_DISPLAY, "l", int(a * lk), shadow=True)
        if sub: text(c, sub, bx + 22, by - hh + 40, 20, WHITE, SERIF_TEXT, "l", int(a * lk), shadow=True)

def fire3d(c, M, x, y, t, k=1.0, s=1.0):
    """a burning front on the 3D map: flickering flame + rising smoke from the ground point."""
    if k <= 0: return
    bx, by = proj(M, x, y); s *= back(clamp(k))
    for i in range(4):
        sy = by - 40 * s - ((t * 30 + i * 25) % 100) * s; c.drawCircle(bx + math.sin(t * 2 + i) * 10 * s, sy, (14 + i * 4) * s, paint("#3A3A3A", int(110 * (1 - i / 4)), blur=8))
    for j, (colr, sz) in enumerate((("#FF4D00", 1.0), ("#FFB000", 0.7), ("#FFF3B0", 0.4))):
        fl = skia.Path(); w = 18 * s * sz; hh = (52 + 10 * math.sin(t * 13 + j)) * s * sz
        fl.moveTo(bx - w, by); fl.cubicTo(bx - w, by - hh * 0.5, bx - w * 0.2, by - hh * 0.8, bx + math.sin(t * 9) * 4 * s, by - hh)
        fl.cubicTo(bx + w * 0.3, by - hh * 0.7, bx + w, by - hh * 0.45, bx + w, by); fl.close()
        c.drawPath(fl, paint(colr, 235))
    c.drawCircle(bx, by - 20 * s, 34 * s, paint("#FF7A00", 70, blur=18))
