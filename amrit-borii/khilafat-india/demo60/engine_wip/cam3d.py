"""True 3D camera over the map + 3D cards (work in progress, not in the plugin yet).

Cam(lon, lat, dist, pitch, yaw): a pinhole camera looking at a target on the map plane.
  dist  = camera distance in map units (degrees); pitch 0 = top-down, 60 = strong 3D; yaw = heading (deg)
  H()   = skia matrix map-units (u, v) -> screen   |  project(u, v, z) -> screen x, y, depth
Everything that lives on the map (parchment, satellite, routes, flags, pop-up scenes) is drawn through this camera,
so one continuous camera path gives a seamless "one-shot" video: fly, tilt, orbit, dive into a place, pull out.
Also: wavy floating flags on poles, pop-up scene cards that rise from the map and fill the screen exactly
(seamless hand-over to the full-screen scene), and document cards that flip in / out with their own 3D camera move.
"""
import math
import numpy as np
import skia
from PIL import Image
from core import *

FOV = 38.0
FOC = DH / (2 * math.tan(math.radians(FOV / 2)))

def _n(v): return v / (np.linalg.norm(v) + 1e-12)

class Cam:
    def __init__(self, lon, lat, dist, pitch=45.0, yaw=0.0):
        self.lon, self.lat, self.dist, self.pitch, self.yaw = lon, lat, dist, pitch, yaw
        u, v = cam_xy(lon, lat); T = np.array([u, -v, 0.0])
        p, y = math.radians(pitch), math.radians(yaw)
        self.C = T + dist * np.array([math.sin(p) * math.sin(y), -math.sin(p) * math.cos(y), math.cos(p)])
        f = _n(T - self.C); up = np.array([0, 0, 1.0]) if pitch > 0.5 else np.array([math.sin(y), math.cos(y), 0.0])
        r = _n(np.cross(f, up)); uc = np.cross(r, f); self.f, self.r, self.uc, self.T = f, r, uc, T
    @staticmethod
    def lerp(a, b, k):
        k = ease_io(k)
        return Cam(lerp(a.lon, b.lon, k), lerp(a.lat, b.lat, k), math.exp(lerp(math.log(a.dist), math.log(b.dist), k)), lerp(a.pitch, b.pitch, k), lerp(a.yaw, b.yaw, k))
    def H(self):
        f, r, uc, C = self.f, self.r, self.uc, self.C; F = FOC
        fc, rc, ucc = f @ C, r @ C, uc @ C
        m = skia.Matrix()
        m.setAll(F * r[0] + DW / 2 * f[0], -F * r[1] - DW / 2 * f[1], -F * rc - DW / 2 * fc,
                 -F * uc[0] + DH / 2 * f[0], F * uc[1] - DH / 2 * f[1], F * ucc - DH / 2 * fc,
                 f[0], -f[1], -fc)
        return m
    def project(self, u, v, z=0.0):
        P = np.array([u, -v, z]) - self.C; d = P @ self.f
        if d <= 1e-6: return None
        return DW / 2 + FOC * (P @ self.r) / d, DH / 2 - FOC * (P @ self.uc) / d, d
    def ll(self, lon, lat, z=0.0):
        u, v = cam_xy(lon, lat); return self.project(u, v, z)
    def ppd(self):                       # screen px per map unit at the target
        return FOC / self.dist
    def footprint(self, far=None):
        """visible ground quad in map units (clip), rays through the screen corners hit z=0, far-limited."""
        far = far or self.dist * 6; pts = []
        for sx, sy in ((0, 0), (DW, 0), (DW, DH), (0, DH)):
            dvec = _n(self.f * FOC + self.r * (sx - DW / 2) - self.uc * (sy - DH / 2))
            if dvec[2] < -1e-4:
                tt = min(-self.C[2] / dvec[2], far)
            else: tt = far
            P = self.C + dvec * tt; pts.append((P[0], -P[1]))
        p = skia.Path(); p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close(); return p

def sky(c, cam, top="#0E1A2B", bottom="#E9C99A"):
    g = skia.GradientShader.MakeLinear([(0, 0), (0, DH * 0.5)], [hexc(top), hexc(bottom)]); c.drawRect(skia.Rect(0, 0, DW, DH), skia.Paint(Shader=g))

def on_map(c, cam):
    """context: draw in map units (u, v) through the camera, clipped to the visible ground."""
    class _ctx:
        def __enter__(s):
            c.save(); c.concat(cam.H()); c.clipPath(cam.footprint(), doAntiAlias=True); return cam.ppd()
        def __exit__(s, *a): c.restore()
    return _ctx()

def haze(c, cam, col="#E9C99A"):
    q = cam.project(*cam.T[:2] * np.array([1, -1]), 0)
    if cam.pitch < 5: return
    far = cam.footprint().getBounds()
    yh = min(DH, max(0, DH * 0.5 - FOC * math.tan(math.radians(90 - cam.pitch)) + 40))
    g = skia.GradientShader.MakeLinear([(0, yh - 40), (0, yh + DH * 0.25)], [hexc(col, int(230 * min(1, cam.pitch / 45))), hexc(col, 0)])
    c.drawRect(skia.Rect(0, 0, DW, DH), skia.Paint(Shader=g))

def parchment(c, wm, cam, fills=None, sea="#6F9AA4", land="#D9C9A2", coast="#9A8762", a=255):
    sky(c, cam)
    with on_map(c, cam) as ppd:
        lvl_scale = ppd * 1.0
        c.drawRect(skia.Rect(-400, -400, 400, 400), paint(sea, a))
        P = wm.paths(lvl_scale); fills = fills or {}
        for code, path in P.items():
            c.drawPath(path, paint(land, a))
            fl = fills.get(code)
            if fl: col, fa = fl; c.drawPath(path, paint(col, int(fa * a / 255)))
            c.drawPath(path, paint(coast, int(a * 0.55), stroke=1.2 / ppd))
    from storyproof import paper_overlay
    paper_overlay(c, 60)
    haze(c, cam)

def satellite(c, sat, cam, a=255):
    with on_map(c, cam):
        draw_img(c, sat.img, sat.tl[0], sat.tl[1], sat.br[0], sat.br[1], a)

def fill_regions(c, cam, paths, col, k=1.0):
    if k <= 0: return
    with on_map(c, cam) as ppd:
        for p in paths: c.drawPath(p, paint(col, int(170 * k))); c.drawPath(p, paint("#FFFFFF", int(200 * k), stroke=2.0 / ppd))

def route(c, cam, lonlats, k, col="#7A1F1F", w=5, dash=True, t=0):
    if k <= 0: return None
    pts = [cam.ll(lo, la) for lo, la in lonlats]
    if any(p is None for p in pts): return None
    pth = skia.Path(); pth.moveTo(pts[0][0], pts[0][1]); [pth.lineTo(p[0], p[1]) for p in pts[1:]]
    pm = skia.PathMeasure(pth, False); L = pm.getLength(); part = skia.Path(); pm.getSegment(0, L * clamp(k), part, True)
    pp = paint(col, 230, stroke=w, cap_round=True)
    if dash: pp.setPathEffect(skia.DashPathEffect.Make([16, 12], -t * 40))
    c.drawPath(part, pp)
    return pm, L

# ------------------------------------------------------------------ floating period flags on poles
_FLAGIMG = {}
def _flag_tex(kind):
    if kind not in _FLAGIMG:
        from battle2d import banner_emblem
        surf = skia.Surface(240, 160); cc = surf.getCanvas(); cc.clear(skia.ColorTRANSPARENT)
        PLAIN = {"karkota": ("#1D4ED8", "#FACC15"), "kannauj": ("#FACC15", "#B91C1C"), "rashtrakuta": ("#15803D", "#FDE68A")}
        if kind in PLAIN:
            cc.drawRect(skia.Rect(0, 0, 240, 160), paint(PLAIN[kind][0])); cc.drawRect(skia.Rect(0, 60, 240, 100), paint(PLAIN[kind][1]))
        else: banner_emblem(cc, kind, 0, 0, 240, 160)
        _FLAGIMG[kind] = surf.makeImageSnapshot()
    return _FLAGIMG[kind]

def float_flag(c, cam, lon, lat, kind, t, k=1.0, label=None, size=1.0, a=255):
    """flag of the ruler of that place at that time, waving on a pole standing on the 3D map."""
    if k <= 0: return
    u, v = cam_xy(lon, lat); b = cam.project(u, v, 0)
    if b is None or not (-200 < b[0] < DW + 200 and -200 < b[1] < DH + 300): return
    hz = cam.dist * 0.075 * size * back(clamp(k)); tp = cam.project(u, v, hz)
    if tp is None: return
    L = math.hypot(tp[0] - b[0], tp[1] - b[1]); fw = L * 0.95; fh = fw * 0.66
    c.drawOval(skia.Rect(b[0] - fw * 0.2, b[1] - fw * 0.05, b[0] + fw * 0.2, b[1] + fw * 0.05), paint("#000000", int(a * 0.35), blur=4))
    c.drawLine(b[0], b[1], tp[0], tp[1], paint("#5A3A1E", a, stroke=max(2, fw * 0.05), cap_round=True))
    c.drawCircle(tp[0], tp[1], max(2, fw * 0.05), paint("#E9C46A", a))
    tex = _flag_tex(kind); n = 14; p = skia.Paint(AntiAlias=True); p.setAlphaf(a / 255)
    for i in range(n):                                     # waving cloth in vertical strips
        f0, f1 = i / n, (i + 1) / n; wv = math.sin(t * 6 - f0 * 5) * fh * 0.10 * f0
        sh = 0.82 + 0.18 * math.sin(t * 6 - f0 * 5 + 1.2)
        src = skia.Rect(240 * f0, 0, 240 * f1 + 1, 160); dst = skia.Rect(tp[0] + fw * f0, tp[1] + wv, tp[0] + fw * f1 + 1, tp[1] + wv + fh)
        c.drawImageRect(tex, src, dst, SAMP, p)
        c.drawRect(dst, paint("#000000", int(a * (1 - sh) * 0.9)))
    if label:
        text(c, label, tp[0] + fw * 0.5, tp[1] + fh + 24, max(15, min(24, fw * 0.3)), "#FFFFFF", FT_SEMI, "c", int(a * clamp(k * 1.5)), shadow=True)

def fire(c, cam, lon, lat, t, k=1.0, s=1.0):
    if k <= 0: return
    p = cam.ll(lon, lat)
    if p is None: return
    bx, by = p[0], p[1]; s *= back(clamp(k)) * max(0.5, min(1.6, 6 / cam.dist))
    for i in range(4):
        sy = by - 40 * s - ((t * 30 + i * 25) % 100) * s; c.drawCircle(bx + math.sin(t * 2 + i) * 10 * s, sy, (14 + i * 4) * s, paint("#3A3A3A", int(110 * (1 - i / 4)), blur=8))
    for j, (colr, sz) in enumerate((("#FF4D00", 1.0), ("#FFB000", 0.7), ("#FFF3B0", 0.4))):
        fl = skia.Path(); w = 18 * s * sz; hh = (52 + 10 * math.sin(t * 13 + j)) * s * sz
        fl.moveTo(bx - w, by); fl.cubicTo(bx - w, by - hh * 0.5, bx - w * 0.2, by - hh * 0.8, bx + math.sin(t * 9) * 4 * s, by - hh)
        fl.cubicTo(bx + w * 0.3, by - hh * 0.7, bx + w, by - hh * 0.45, bx + w, by); fl.close(); c.drawPath(fl, paint(colr, 235))
    c.drawCircle(bx, by - 20 * s, 34 * s, paint("#FF7A00", 70, blur=18))

def pin(c, cam, lon, lat, label, k, t, sub=None, col="#E63946"):
    if k <= 0: return
    u, v = cam_xy(lon, lat); b = cam.project(u, v, 0); tp = cam.project(u, v, cam.dist * 0.09 * back(clamp(k)))
    if b is None or tp is None: return
    c.drawOval(skia.Rect(b[0] - 12, b[1] - 4, b[0] + 12, b[1] + 4), paint("#000000", 110, blur=3))
    c.drawLine(b[0], b[1], tp[0], tp[1], paint("#F4EFE4", 255, stroke=3.5, cap_round=True)); c.drawCircle(tp[0], tp[1], 12, paint(col)); c.drawCircle(tp[0] - 3, tp[1] - 3, 3.5, paint("#FFFFFF"))
    from storyproof import SERIF_DISPLAY, SERIF_TEXT
    lk = seg(k, 0.4, 1.0); text(c, label, tp[0] + 18, tp[1] + 10, 34, "#FFFFFF", SERIF_DISPLAY, "l", int(255 * lk), shadow=True)
    if sub: text(c, sub, tp[0] + 18, tp[1] + 36, 19, "#FFFFFF", SERIF_TEXT, "l", int(255 * lk), shadow=True)

# ------------------------------------------------------------------ 3D cards (pop-up scenes, documents)
def quad(c, img, pts, a=255, shadow=True):
    """draw an image onto any screen quad (perspective-correct homography). pts = TL, TR, BR, BL."""
    m = skia.Matrix()
    if not m.setPolyToPoly([skia.Point(0, 0), skia.Point(img.width(), 0), skia.Point(img.width(), img.height()), skia.Point(0, img.height())], [skia.Point(*p) for p in pts]): return
    if shadow:
        sp = skia.Path(); sp.moveTo(*pts[0]); [sp.lineTo(*p) for p in pts[1:]]; sp.close(); sp.offset(14, 22); c.drawPath(sp, paint("#000000", int(a * 0.4), blur=18))
    c.save(); c.concat(m); p = skia.Paint(AntiAlias=True); p.setAlphaf(a / 255); c.drawImage(img, 0, 0, SAMP, p); c.restore()

FULL = [(0, 0), (DW, 0), (DW, DH), (0, DH)]
def popup_quad(cam, lon, lat, width, rise):
    """screen quad of a scene card standing on the map at (lon, lat): it hinges up from the ground (rise 0 -> 1)."""
    u, v = cam_xy(lon, lat); B = np.array([u, -v, 0.0])
    rg = _n(np.array([cam.r[0], cam.r[1], 0.0])); fh = _n(np.array([cam.f[0], cam.f[1], 0.0])); h = width * 9 / 16
    al = math.radians(88 * ease_out(clamp(rise))); upv = math.cos(al) * fh + math.sin(al) * np.array([0, 0, 1.0])
    W3 = [B - rg * width / 2 + upv * h, B + rg * width / 2 + upv * h, B + rg * width / 2, B - rg * width / 2]
    out = []
    for P in W3:
        q = cam.project(P[0], -P[1], P[2])
        if q is None: return None
        out.append((q[0], q[1]))
    return out

def popup(c, cam, lon, lat, scene_img, width, rise, fill, a=255):
    """scene card rises from the map; fill 0 -> 1 morphs it to the exact full frame (then hand over to the scene)."""
    if rise <= 0: return
    q = popup_quad(cam, lon, lat, width, rise)
    if q is None: q = FULL
    k = ease_io(clamp(fill)); pts = [(lerp(q[i][0], FULL[i][0], k), lerp(q[i][1], FULL[i][1], k)) for i in range(4)]
    quad(c, scene_img, pts, a, shadow=fill < 0.95)
    if fill < 0.9:
        bp = skia.Path(); bp.moveTo(*pts[0]); [bp.lineTo(*p) for p in pts[1:]]; bp.close(); c.drawPath(bp, paint("#F4EFE4", int(a * (1 - fill)), stroke=6))

def doc_card(c, tex, k_in, k_out, move, focus=(0.5, 0.5), zoom=2.2, tilt=-16, yaw_end=-8, rest_w=0.72):
    """document card in its own 3D space in front of whatever is behind (map or scene).
    k_in: flips in around its left edge; move: 3D camera move (tilt back, dolly in, pan to `focus` in the doc);
    k_out: flips out around its right edge. tex = skia.Image of the document (with highlights already painted)."""
    if k_in <= 0 or k_out >= 1: return
    w = 1000.0; h = w * tex.height() / tex.width(); Z0 = FOC * w / (rest_w * DW)
    m = ease_io(clamp(move)); ki, ko = ease_out(clamp(k_in)), ease_in(clamp(k_out))
    def P(x, y):
        p = np.array([x - w / 2, y - h / 2, 0.0])
        th = math.radians(90 * (1 - ki)); hx = -w / 2               # flip in about the left edge
        p = np.array([hx + (p[0] - hx) * math.cos(th), p[1], -(p[0] - hx) * math.sin(th)])
        th2 = math.radians(-90 * ko); hx2 = w / 2                    # flip out about the right edge
        p = np.array([hx2 + (p[0] - hx2) * math.cos(th2), p[1], -(p[0] - hx2) * math.sin(th2) + p[2]])
        ta = math.radians(tilt * m); yw = math.radians(yaw_end * m)
        p = np.array([p[0], p[1] * math.cos(ta) - p[2] * math.sin(ta), p[1] * math.sin(ta) + p[2] * math.cos(ta)])
        p = np.array([p[0] * math.cos(yw) + p[2] * math.sin(yw), p[1], -p[0] * math.sin(yw) + p[2] * math.cos(yw)])
        fx, fy = (focus[0] - 0.5) * w, (focus[1] - 0.5) * h
        p = p - np.array([fx * m, fy * m, 0.0])
        z = Z0 * lerp(1.0, 1.0 / zoom, m) + p[2]
        return DW / 2 + FOC * p[0] / z, DH / 2 + FOC * p[1] / z
    pts = [P(0, 0), P(w, 0), P(w, h), P(0, h)]
    quad(c, tex, pts, 255, shadow=True)

def doc_texture(img, hls, t, width=1400, hl_col="#FFE14D"):
    """paint the marker highlights onto a copy of the document. hls = [(x0, y0, x1, y1, t_start, t_end)] normalised."""
    W = width; Hh = int(W * img.height() / img.width())
    surf = skia.Surface(W, Hh); cc = surf.getCanvas(); cc.clear(hexc("#FFFFFF"))
    cc.drawImageRect(img, skia.Rect(0, 0, img.width(), img.height()), skia.Rect(0, 0, W, Hh), SAMP)
    for x0, y0, x1, y1, ts, te in hls:
        k = seg(t, ts, te)
        if k <= 0: continue
        p = paint(hl_col, 200); p.setBlendMode(skia.BlendMode.kMultiply)
        cc.drawRoundRect(skia.Rect(x0 * W - 6, y0 * Hh, lerp(x0 * W, x1 * W, ease_out(k)) + 6, y1 * Hh), 6, 6, p)
    cc.drawRect(skia.Rect(0, 0, W, Hh), paint("#B8B0A0", 255, stroke=6))
    return surf.makeImageSnapshot()

# ------------------------------------------------------------------ ruler's flag blended INTO the territory it ruled
def clip_box(path, lon0, lon1, lat0, lat1):
    """intersect a map path with a lon/lat box (rough historical extents on modern outlines, andaazan)."""
    x0, y1 = cam_xy(lon0, lat0); x1, y0 = cam_xy(lon1, lat1); r = skia.Path(); r.addRect(skia.Rect(x0, y0, x1, y1))
    return skia.Op(path, r, skia.PathOp.kIntersect_PathOp)

def union(paths):
    u = None
    for p in paths:
        if p is None: continue
        u = skia.Path(p) if u is None else skia.Op(u, p, skia.PathOp.kUnion_PathOp)
    return u

def flag_region(c, cam, path, kind, t, k=1.0, alpha=0.78, edge="#FFFFFF"):
    """the territory is filled with its ruler's flag, waving, blended with the parchment (multiply), revealed by a sweep."""
    if k <= 0 or path is None: return
    tex = _flag_tex(kind); b = path.computeTightBounds()
    main = {"umayyad": "#FFFFFF", "varaha": "#E8A23A", "wolf": "#2F6B3A", "sun": "#C1121F", "byz": "#5B1A8A", "frank": "#B91C1C", "khazar": "#5B4636",
            "berber": "#1E3A8A", "karkota": "#1D4ED8", "kannauj": "#FACC15"}.get(kind, "#FFFFFF")
    with on_map(c, cam) as ppd:
        c.save(); c.clipPath(path, doAntiAlias=True)
        rx = b.left() + (b.width() * 1.05) * ease_io(k)                                         # sweep reveal (left -> right)
        c.clipRect(skia.Rect(b.left() - 1, b.top() - 1, rx, b.bottom() + 1))
        fp = paint(main, int(255 * alpha * 0.85)); fp.setBlendMode(skia.BlendMode.kMultiply if main != "#FFFFFF" else skia.BlendMode.kSrcOver)
        if main == "#FFFFFF": fp.setAlphaf(0.55)
        c.drawRect(b, fp)                                                                       # territory in the flag's colour
        s_ = min(b.width() / 240, b.height() / 160) * 0.6; w, h = 240 * s_, 160 * s_            # the whole flag, centred, inside the land
        p2 = skia.Paint(AntiAlias=True); p2.setAlphaf(alpha * 0.75)
        c.drawImageRect(tex, skia.Rect(0, 0, 240, 160), skia.Rect(b.centerX() - w / 2, b.centerY() - h / 2, b.centerX() + w / 2, b.centerY() + h / 2), SAMP, p2)
        n = 8                                                                                   # cloth waves moving across the territory
        for i in range(n):
            xx = b.left() + ((i / n + t * 0.12) % 1.0) * b.width()
            c.drawRect(skia.Rect(xx, b.top(), xx + b.width() / (n * 2), b.bottom()), paint("#000000", 26, blur=b.width() / 30))
            c.drawRect(skia.Rect(xx + b.width() / (n * 2), b.top(), xx + b.width() / n, b.bottom()), paint("#FFFFFF", 18, blur=b.width() / 30))
        c.restore()
        c.drawPath(path, paint(edge, int(170 * k), stroke=4.5 / ppd, blur=2.5 / ppd)); c.drawPath(path, paint(edge, int(230 * k), stroke=1.4 / ppd))
