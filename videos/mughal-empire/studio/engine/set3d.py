"""set3d — real 3D sets for the toon style.

Environment = textured quads (walls, floors, pillars, roofs) rendered with a true perspective camera
(homography per quad, near-plane clipping). Characters and props are 2D toon billboards standing at
3D positions, so the 3D camera (dolly / truck / crane / orbit) gives real perspective and parallax.

scene = {"type": "set3d", "set": "court|palace|fort|battlefield|village|tent|cell|study|plain|map",
         "cam": "dolly_in|dolly_out|truck_left|truck_right|crane_up|crane_down|orbit_left|orbit_right|push|static|fly",
         "target": [x, y, z], "dist": 7, "height": 1.6, "yaw": 0, "fov": 50,       # optional camera framing
         "actors": [{"who": cast, "x": 0, "z": 0, "h": 1.0, "expr", "pose", "face", "talk", "gesture",
                     "to": [x, z], "walk_time", "delay", "dim", "label", "jump", "shake", "back"}],
         "objs":   [{"prop": name, "x", "z", "y": 0, "h": 1.0, "color", "anim": pop|drop|bob|shake|slide|march,
                     "delay", "label", "to": [x, z], "move_time"}],
         "map": {...map scene keys...}   # only for set "map": the map image lies on the ground plane
        }
World units ~ metres: y up, z away from the default camera. Characters are ~1.0 tall, rooms ~4 tall.
"""
import functools, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import hexc, shade, clamp, ease_in_out, ease_out, back_out, lerp
import toon, props

TEX = 512


# ------------------------------------------------------------------ math
def _rot(yaw, pitch):
    cy, sy, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    Ry = np.array([[cy, 0, -sy], [0, 1, 0], [sy, 0, cy]])          # world -> yawed
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])          # pitch (look up = +)
    return Rx @ Ry


class Cam:
    def __init__(self, pos, target, fov, W, H, roll=0.0):
        self.C = np.array(pos, float)
        d = np.array(target, float) - self.C
        yaw = math.atan2(d[0], d[2])
        pitch = math.atan2(d[1], math.hypot(d[0], d[2]))
        self.M = _rot(yaw, pitch)
        self.W, self.H = W, H
        self.f = (W / 2) / math.tan(math.radians(fov) / 2)
        self.K = np.array([[self.f, 0, W / 2], [0, -self.f, H / 2], [0, 0, 1.0]])
        self.roll = roll

    def to_cam(self, P):
        return self.M @ (np.asarray(P, float) - self.C)

    def project(self, P):
        x, y, z = self.to_cam(P)
        if z <= 1e-4:
            return None
        return (self.W / 2 + self.f * x / z, self.H / 2 - self.f * y / z, z)


# ------------------------------------------------------------------ quad renderer
def draw_quad(fr, cam, O, E1, E2, tex, shade_k=1.0, near=0.08):
    """Paint texture `tex` (RGBA) on the 3D parallelogram O + u*E1 + v*E2 (u,v in [0,1])."""
    O, E1, E2 = (np.asarray(v, float) for v in (O, E1, E2))
    corners = [O, O + E1, O + E1 + E2, O + E2]
    cc = [cam.to_cam(p) for p in corners]
    if all(c[2] < near for c in cc):
        return
    # clip polygon against near plane (Sutherland-Hodgman, one plane)
    poly = []
    for i in range(4):
        a, b = cc[i], cc[(i + 1) % 4]
        ina, inb = a[2] >= near, b[2] >= near
        if ina:
            poly.append(a)
        if ina != inb:
            t = (near - a[2]) / (b[2] - a[2])
            poly.append(a + (b - a) * t)
    if len(poly) < 3:
        return
    pts = [(cam.W / 2 + cam.f * p[0] / p[2], cam.H / 2 - cam.f * p[1] / p[2]) for p in poly]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    if max(xs) < 0 or min(xs) > cam.W or max(ys) < 0 or min(ys) > cam.H:
        return
    A = np.column_stack([cam.M @ E1, cam.M @ E2, cam.M @ (O - cam.C)])
    tw, th = tex.size
    Ht = cam.K @ A @ np.diag([1.0 / tw, 1.0 / th, 1.0])
    try:
        Hi = np.linalg.inv(Ht)
    except np.linalg.LinAlgError:
        return
    Hi = Hi / Hi[2, 2]
    x0, y0 = max(0, int(min(xs)) - 1), max(0, int(min(ys)) - 1)
    x1, y1 = min(cam.W, int(max(xs)) + 2), min(cam.H, int(max(ys)) + 2)
    if x1 <= x0 or y1 <= y0:
        return
    # transform only the bounding box (shift output origin)
    T = Hi @ np.array([[1, 0, x0], [0, 1, y0], [0, 0, 1.0]])
    T = T / T[2, 2]
    coeffs = (T[0, 0], T[0, 1], T[0, 2], T[1, 0], T[1, 1], T[1, 2], T[2, 0], T[2, 1])
    img = tex.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, coeffs, Image.BILINEAR)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
    a = img.getchannel("A")
    from PIL import ImageChops
    a = ImageChops.multiply(a, mask)
    if shade_k != 1.0:
        img = Image.eval(img.convert("RGB"), lambda v: int(min(255, v * shade_k))).convert("RGBA")
    img.putalpha(a)
    fr.alpha_composite(img, (x0, y0))


# ------------------------------------------------------------------ textures (toon look, cached)
def _canvas(w=TEX, h=TEX, col="#888"):
    c = tuple(hexc(col))
    im = Image.new("RGBA", (w, h), c[:3] + (255,))
    return im, ImageDraw.Draw(im)


OL = (40, 28, 22, 255)


@functools.lru_cache(maxsize=64)
def tex(name):
    if name == "sandstone_arches":
        im, d = _canvas(1024, 512, "#e2b07e")
        for k in range(4):
            x = 40 + k * 250
            d.rectangle([x, 60, x + 200, 512], fill=hexc("#f3e6cc"), outline=OL, width=5)
            d.rectangle([x + 20, 140, x + 180, 512], fill=hexc("#b8603a"), outline=OL, width=4)
            d.pieslice([x + 20, 60, x + 180, 220], 180, 360, fill=hexc("#b8603a"), outline=OL, width=4)
            d.rectangle([x + 46, 190, x + 154, 512], fill=hexc("#8a3f22"), outline=OL, width=3)
            d.pieslice([x + 46, 136, x + 154, 244], 180, 360, fill=hexc("#8a3f22"), outline=OL, width=3)
        d.rectangle([0, 0, 1024, 40], fill=hexc("#c9784a"), outline=OL, width=4)
        for x in range(0, 1024, 48):
            d.polygon([(x, 40), (x + 24, 62), (x + 48, 40)], fill=hexc("#a85a32"), outline=OL)
        return im
    if name == "marble_floor":
        im, d = _canvas(512, 512, "#efe2c8")
        for k in range(0, 513, 64):
            d.line([(k, 0), (k, 512)], fill=hexc("#d6c6a2"), width=3)
            d.line([(0, k), (512, k)], fill=hexc("#d6c6a2"), width=3)
        for i in range(0, 512, 128):
            for j in range(0, 512, 128):
                d.regular_polygon((i + 64, j + 64, 18), 4, rotation=45, fill=hexc("#c9a227"))
        return im
    if name == "carpet":
        im, d = _canvas(256, 1024, "#b5362e")
        d.rectangle([0, 0, 255, 1023], outline=hexc("#e8c547"), width=18)
        for y in range(60, 1024, 140):
            d.regular_polygon((128, y, 34), 4, rotation=45, fill=hexc("#7a1f2b"), outline=hexc("#e8c547"))
        return im
    if name == "pillar":
        im, d = _canvas(128, 512, "#f3e6cc")
        d.rectangle([0, 0, 127, 511], outline=OL, width=6)
        d.rectangle([0, 0, 127, 40], fill=hexc("#c9a227"), outline=OL, width=5)
        d.rectangle([0, 472, 127, 511], fill=hexc("#c9a227"), outline=OL, width=5)
        d.line([(64, 40), (64, 472)], fill=hexc("#d9c39a"), width=6)
        return im
    if name == "red_wall":
        im, d = _canvas(1024, 512, "#6a1a20")
        for k in range(0, 1024, 256):
            d.rectangle([k + 30, 60, k + 226, 470], outline=hexc("#c9a227"), width=8)
            d.rectangle([k + 60, 100, k + 196, 300], fill=hexc("#3a2a22"), outline=hexc("#c9a227"), width=6)
            d.ellipse([k + 98, 140, k + 158, 210], fill=hexc("#e0ac7e"), outline=OL, width=3)
        return im
    if name == "wood_floor":
        im, d = _canvas(512, 512, "#6a3f24")
        for k in range(0, 512, 40):
            d.line([(0, k), (512, k)], fill=hexc("#4a2a18"), width=3)
            off = (k * 7) % 180
            d.line([(off, k), (off, k + 40)], fill=hexc("#4a2a18"), width=3)
        return im
    if name == "fort_wall":
        im, d = _canvas(1024, 512, "#c46a3e")
        for y in range(120, 512, 36):
            for x in range((y // 36 % 2) * 30, 1024, 60):
                d.rectangle([x, y, x + 60, y + 36], outline=hexc("#a8552e"), width=2)
        for x in range(0, 1024, 64):
            d.rectangle([x, 80, x + 40, 120], fill=hexc("#c46a3e"), outline=OL, width=4)
        d.rectangle([0, 116, 1024, 124], fill=hexc("#a8552e"))
        d.rectangle([420, 260, 600, 512], fill=hexc("#5a2a18"), outline=OL, width=5)
        d.pieslice([420, 170, 600, 350], 180, 360, fill=hexc("#5a2a18"), outline=OL, width=5)
        im = im.copy()
        ImageDraw.Draw(im).rectangle([0, 0, 1024, 79], fill=(0, 0, 0, 0))
        for x in range(0, 1024, 64):
            ImageDraw.Draw(im).rectangle([x, 80, x + 40, 120], fill=hexc("#c46a3e"), outline=OL, width=4)
        ImageDraw.Draw(im).rectangle([0, 0, 1024, 79], fill=(0, 0, 0, 0))
        return im
    if name == "tower":
        im, d = _canvas(256, 512, "#b95e34")
        for y in range(80, 512, 40):
            d.line([(0, y), (256, y)], fill=hexc("#9a4a28"), width=3)
        d.rectangle([0, 0, 255, 511], outline=OL, width=6)
        d.rectangle([96, 200, 160, 300], fill=hexc("#3a1a10"), outline=OL, width=4)
        return im
    if name == "dirt":
        im, d = _canvas(512, 512, "#b98a55")
        rnd = np.random.default_rng(3)
        for _ in range(260):
            x, y = rnd.integers(0, 512, 2)
            r = int(rnd.integers(3, 10))
            d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=hexc("#a87a48"))
        return im
    if name == "grass":
        im, d = _canvas(512, 512, "#7a9a4a")
        rnd = np.random.default_rng(5)
        for _ in range(500):
            x, y = rnd.integers(0, 512, 2)
            d.line([(x, y), (x + rnd.integers(-4, 5), y - rnd.integers(6, 14))], fill=hexc("#5e7e36"), width=3)
        return im
    if name == "battle_ground":
        im, d = _canvas(512, 512, "#8a7448")
        rnd = np.random.default_rng(7)
        for _ in range(240):
            x, y = rnd.integers(0, 512, 2)
            d.line([(x, y), (x + 4, y - 10)], fill=hexc("#6e5a34"), width=3)
        return im
    if name == "hut_wall":
        im, d = _canvas(256, 256, "#c8955a")
        d.rectangle([0, 0, 255, 255], outline=OL, width=6)
        d.rectangle([96, 120, 160, 256], fill=hexc("#4a2a18"), outline=OL, width=4)
        return im
    if name == "thatch":
        im, d = _canvas(256, 256, "#b88a3a")
        for x in range(0, 256, 14):
            d.line([(x, 0), (x + 6, 256)], fill=hexc("#8a6424"), width=3)
        d.rectangle([0, 0, 255, 255], outline=OL, width=6)
        return im
    if name == "tent_cloth":
        im, d = _canvas(512, 512, "#7a5a3a")
        for x in range(0, 512, 64):
            d.rectangle([x, 0, x + 32, 512], fill=hexc("#6a4a2e"))
        return im
    if name == "stone_cell":
        im, d = _canvas(512, 512, "#3a3f4a")
        for y in range(0, 512, 48):
            for x in range((y // 48 % 2) * 40, 512, 80):
                d.rectangle([x, y, x + 80, y + 48], outline=hexc("#2a2e36"), width=3)
        return im
    if name == "study_wall":
        im, d = _canvas(1024, 512, "#1e2a44")
        for k in range(3):
            x = 80 + k * 320
            d.rectangle([x, 120, x + 200, 380], fill=hexc("#0d1a33"), outline=OL, width=6)
            for j in range(1, 3):
                d.line([(x + j * 66, 120), (x + j * 66, 380)], fill=OL, width=4)
            d.ellipse([x + 140, 150, x + 180, 190], fill=hexc("#f3ead6"))
        return im
    if name == "sky_day":
        im = Image.new("RGBA", (64, 512))
        a, b = np.array(hexc("#7fb2e0")[:3]), np.array(hexc("#f0e2c4")[:3])
        for y in range(512):
            im.paste(tuple(int(v) for v in a + (b - a) * (y / 511)) + (255,), (0, y, 64, y + 1))
        return im
    if name == "sky_dusk":
        im = Image.new("RGBA", (64, 512))
        a, b = np.array(hexc("#3a2a3a")[:3]), np.array(hexc("#e07a3a")[:3])
        for y in range(512):
            im.paste(tuple(int(v) for v in a + (b - a) * (y / 511)) + (255,), (0, y, 64, y + 1))
        return im
    if name in ("hills_far", "hills_near"):
        im = Image.new("RGBA", (1024, 256), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        rnd = np.random.default_rng(11 if name == "hills_far" else 13)
        col = "#6a5a6a" if name == "hills_far" else "#5a4a3a"
        pts = [(0, 256)] + [(i * 64, int(rnd.integers(40, 150))) for i in range(17)] + [(1024, 256)]
        d.polygon(pts, fill=hexc(col))
        return im.filter(ImageFilter.GaussianBlur(1))
    raise KeyError(name)


def tinted(name, k):
    return tex(name) if k == 1 else Image.eval(tex(name).convert("RGB"), lambda v: int(v * k)).convert("RGBA")


# ------------------------------------------------------------------ set builders
def _box(q, x, z, w, d, h, side_tex, top_tex=None, y=0.0, k_side=0.8):
    """Axis aligned box: front, left, right, top faces (back face is never seen in our framing)."""
    x0, x1, z0, z1 = x - w / 2, x + w / 2, z - d / 2, z + d / 2
    yt = y + h
    q.append((("box", z0), [x0, yt, z0], [w, 0, 0], [0, -h, 0], side_tex, 1.0, True))
    q.append((("box", z0), [x0, yt, z1], [0, 0, -d], [0, -h, 0], side_tex, k_side, True))
    q.append((("box", z0), [x1, yt, z0], [0, 0, d], [0, -h, 0], side_tex, k_side, True))
    if top_tex:
        q.append((("box", z0), [x0, yt, z0], [w, 0, 0], [0, 0, d], top_tex, 1.1, True))


def _vflip(E2, h):  # textures are top-down: v grows downward, so walls start at the top edge
    return E2


def build(setname, sc):
    """Return (env_quads, objs_quads, defaults). quad = (sortkey, O, E1, E2, texname, shade, is_obj)."""
    env, obj = [], []
    dflt = {"target": [0, 1.0, 4], "dist": 7.5, "height": 1.7, "fov": 52, "mood": 1.0, "floor": 0.0}
    W = 14
    if setname == "court":
        env.append((0, [-W / 2, 5, 10], [W, 0, 0], [0, -5, 0], "sandstone_arches", 1.0, False))   # back wall
        env.append((0, [-W / 2, 0, -6], [W, 0, 0], [0, 0, 16], "marble_floor_big", 1.0, False))
        env.append((0, [-2.2, 0.01, -6], [4.4, 0, 0], [0, 0, 16], "carpet", 1.0, False))
        env.append((0, [-W / 2, 5, -6], [0, 0, 16], [0, -5, 0], "sandstone_arches", 0.72, False))  # left wall
        env.append((0, [W / 2, 5, 10], [0, 0, -16], [0, -5, 0], "sandstone_arches", 0.72, False))  # right wall
        for x in (-4.6, 4.6):
            for z in (1.5, 6.0):
                _box(obj, x, z, 0.7, 0.7, 4.2, "pillar", k_side=0.75)
        _box(obj, 0, 9.0, 3.2, 1.2, 0.6, "gold_block", "gold_block")                             # dais
        dflt.update(target=[0, 1.2, 6.0], dist=7.0, height=2.0)
    elif setname == "palace":
        env.append((0, [-6, 4.5, 7], [12, 0, 0], [0, -4.5, 0], "red_wall", 1.0, False))
        env.append((0, [-6, 0, -4], [12, 0, 0], [0, 0, 11], "marble_floor_big", 0.9, False))
        env.append((0, [-1.6, 0.01, -4], [3.2, 0, 0], [0, 0, 11], "carpet", 1.0, False))
        env.append((0, [-6, 4.5, -4], [0, 0, 11], [0, -4.5, 0], "red_wall", 0.65, False))
        env.append((0, [6, 4.5, 7], [0, 0, -11], [0, -4.5, 0], "red_wall", 0.65, False))
        dflt.update(target=[0, 1.0, 4.5], dist=5.6, height=1.7, mood=0.95)
    elif setname == "study":
        env.append((0, [-5, 4, 6], [10, 0, 0], [0, -4, 0], "study_wall", 1.0, False))
        env.append((0, [-5, 0, -4], [10, 0, 0], [0, 0, 10], "wood_floor", 0.85, False))
        env.append((0, [-5, 4, -4], [0, 0, 10], [0, -4, 0], "study_wall", 0.6, False))
        env.append((0, [5, 4, 6], [0, 0, -10], [0, -4, 0], "study_wall", 0.6, False))
        _box(obj, 0, 5.2, 3.0, 1.0, 0.8, "wood_block", "wood_block")
        dflt.update(target=[0, 1.0, 4.0], dist=5.0, height=1.7, mood=0.85)
    elif setname == "cell":
        env.append((0, [-4, 4, 5], [8, 0, 0], [0, -4, 0], "stone_cell", 1.0, False))
        env.append((0, [-4, 0, -4], [8, 0, 0], [0, 0, 9], "stone_cell", 0.7, False))
        env.append((0, [-4, 4, -4], [0, 0, 9], [0, -4, 0], "stone_cell", 0.6, False))
        env.append((0, [4, 4, 5], [0, 0, -9], [0, -4, 0], "stone_cell", 0.6, False))
        dflt.update(target=[0, 0.8, 3], dist=4.6, height=1.6, mood=0.75)
    elif setname == "tent":
        env.append((0, [-5, 4, 6], [10, 0, 0], [0, -4, 0], "tent_cloth", 1.0, False))
        env.append((0, [-5, 0, -4], [10, 0, 0], [0, 0, 10], "dirt", 0.7, False))
        env.append((0, [-5, 4, -4], [0, 0, 10], [0, -4, 0], "tent_cloth", 0.7, False))
        env.append((0, [5, 4, 6], [0, 0, -10], [0, -4, 0], "tent_cloth", 0.7, False))
        _box(obj, 0, 6.4, 3.4, 1.2, 0.75, "wood_block", "map_top")
        dflt.update(target=[0, 1.0, 4.0], dist=5.2, height=1.9, mood=0.85)
    elif setname == "map":
        env.append((0, [-30, 0, -10], [60, 0, 0], [0, 0, 50], "table_dark", 1.0, False))
        env.append((0, [-12, 0.01, 0], [24, 0, 0], [0, 0, 12], "map_ground", 1.0, False))
        dflt.update(target=[0, 0, 6.0], dist=9.5, height=13.0, fov=56)
    elif setname == "cliff":   # fort terrace on the edge of a ravine (Akhsi, 1494)
        env.append((0, [-60, 30, 60], [120, 0, 0], [0, -32, 0], "sky_day", 1.0, False))
        env.append((0, [-50, 6, 50], [100, 0, 0], [0, -6.2, 0], "hills_far", 1.0, False))
        env.append((0, [-40, -7, 7], [80, 0, 0], [0, 0, 40], "grass_big", 0.8, False))        # valley floor far below
        env.append((0, [-40, 0, 7], [80, 0, 0], [0, -7, 0], "rock", 0.75, False))           # cliff face
        env.append((0, [-40, 0, -6], [80, 0, 0], [0, 0, 13], "dirt_big", 1.0, False))        # terrace
        env.append((0, [-14, 3.2, 2.5], [0, 0, 4.5], [0, -3.2, 0], "fort_wall_side", 0.7, False))
        dflt.update(target=[0.8, 0.6, 6.0], dist=6.0, height=2.6)
    elif setname == "river":   # ghat / river bank with water and ships (Bengal trade)
        env.append((0, [-60, 30, 60], [120, 0, 0], [0, -32, 0], "sky_day", 1.0, False))
        env.append((0, [-50, 6, 50], [100, 0, 0], [0, -6.2, 0], "hills_far", 1.0, False))
        env.append((0, [-40, -0.05, 8], [80, 0, 0], [0, 0, 40], "water", 1.0, False))
        env.append((0, [-40, 0, -6], [80, 0, 0], [0, 0, 14], "dirt_big", 1.0, False))
        dflt.update(target=[0, 1.0, 6], dist=6.5, height=1.8)
    elif setname in ("fort", "village", "battlefield", "plain"):
        sky = "sky_dusk" if setname == "battlefield" else "sky_day"
        env.append((0, [-60, 30, 60], [120, 0, 0], [0, -32, 0], sky, 1.0, False))
        if setname != "map":
            env.append((0, [-50, 6, 50], [100, 0, 0], [0, -6.2, 0], "hills_far", 1.0, False))
            env.append((0, [-40, 4, 34], [80, 0, 0], [0, -4.2, 0], "hills_near", 1.0, False))
        ground = {"fort": "dirt_big", "village": "grass_big", "battlefield": "battle_big", "plain": "grass_big",
                  "map": "map_ground"}[setname]
        env.append((0, [-40, 0, -6], [80, 0, 0], [0, 0, 40], ground, 1.0, False))
        if setname == "fort":
            env.append((0, [-12, 4.4, 9], [24, 0, 0], [0, -4.4, 0], "fort_wall", 1.0, False))
            for x in (-7.5, 7.5):
                _box(obj, x, 9.0, 2.2, 1.6, 6.0, "tower", "roof_red")
            dflt.update(target=[0, 1.2, 5], dist=6.5, height=1.7)
        elif setname == "village":
            for x, z in ((-5, 9), (-1, 11), (3.5, 10), (7, 8.5)):
                _box(obj, x, z, 2.4, 2.0, 1.6, "hut_wall", "thatch")
            dflt.update(target=[0, 1.0, 5], dist=6.5, height=1.7)
        elif setname == "battlefield":
            dflt.update(target=[0, 1.0, 6], dist=9.0, height=2.6, mood=0.92)
        elif setname == "map":
            dflt.update(target=[0, 0, 6], dist=9, height=7.5, fov=48)
        else:
            dflt.update(target=[0, 1.0, 5], dist=8.0, height=1.8)
    return env, obj, dflt


@functools.lru_cache(maxsize=32)
def surface(name, map_json=None, W=None, H=None):
    """Big/derived textures."""
    if name == "marble_floor_big":
        t = tex("marble_floor")
        im = Image.new("RGBA", (1024, 2048))
        for x in range(0, 1024, 512):
            for y in range(0, 2048, 512):
                im.paste(t, (x, y))
        return im
    if name in ("dirt_big", "grass_big", "battle_big"):
        t = tex({"dirt_big": "dirt", "grass_big": "grass", "battle_big": "battle_ground"}[name])
        im = Image.new("RGBA", (2048, 1024))
        for x in range(0, 2048, 512):
            for y in range(0, 1024, 512):
                im.paste(t, (x, y))
        return im
    if name == "gold_block":
        im, d = _canvas(256, 128, "#c9a227")
        d.rectangle([0, 0, 255, 127], outline=OL, width=6)
        d.rectangle([20, 20, 236, 108], outline=hexc("#7a1f2b"), width=6)
        return im
    if name == "wood_block":
        im, d = _canvas(256, 128, "#6a4a2a")
        d.rectangle([0, 0, 255, 127], outline=OL, width=6)
        return im
    if name == "map_top":
        im, d = _canvas(256, 128, "#e8d8b0")
        d.rectangle([0, 0, 255, 127], outline=OL, width=6)
        d.line([(30, 90), (90, 40), (160, 70), (220, 30)], fill=hexc("#b3202a"), width=5)
        return im
    if name == "rock":
        im, d = _canvas(1024, 256, "#7a6a5a")
        rnd = np.random.default_rng(17)
        for _ in range(90):
            x, y = rnd.integers(0, 1024), rnd.integers(0, 256)
            d.polygon([(x, y), (x + 40, y + 10), (x + 30, y + 40), (x - 10, y + 30)], fill=hexc("#6a5a4a"), outline=OL)
        return im
    if name == "water":
        im, d = _canvas(1024, 512, "#3f7fa8")
        rnd = np.random.default_rng(19)
        for _ in range(160):
            x, y = rnd.integers(0, 1024), rnd.integers(0, 512)
            d.line([(x, y), (x + 30, y)], fill=hexc("#8fc0dc"), width=3)
        return im
    if name == "fort_wall_side":
        return tex("fort_wall")
    if name == "table_dark":
        im, d = _canvas(256, 256, "#2a1f1a")
        for y in range(0, 256, 32):
            d.line([(0, y), (256, y)], fill=hexc("#241a15"), width=4)
        return im
    if name == "roof_red":
        im, d = _canvas(128, 128, "#8a3f22")
        d.rectangle([0, 0, 127, 127], outline=OL, width=6)
        return im
    return tex(name)


# ------------------------------------------------------------------ camera moves
def cam_pose(sc, dflt, t, dur):
    tgt = np.array(sc.get("target", dflt["target"]), float)
    dist = sc.get("dist", dflt["dist"])
    h = sc.get("height", dflt["height"])
    yaw = math.radians(sc.get("yaw", 0))
    mv = sc.get("cam", "dolly_in")
    lin = max(-0.3, min(1.3, t / max(dur, 1e-3)))          # keeps moving through cuts (seamless)
    k = 0.72 * lin + 0.28 * ease_in_out(clamp(lin))
    amt = sc.get("amount", 1.0)
    d_yaw, d_dist, d_h, d_x = 0.0, 0.0, 0.0, 0.0
    if mv == "dolly_in":
        d_dist = -0.28 * dist * amt * k
    elif mv == "dolly_out":
        d_dist = 0.28 * dist * amt * (k - 1) * -1 - 0.28 * dist * amt
        d_dist = -0.28 * dist * amt * (1 - k)
    elif mv == "push":
        d_dist = -0.45 * dist * amt * ease_out(clamp(t / max(dur, 1e-3)))
    elif mv == "truck_left":
        d_x = 1.4 * amt * (0.5 - k)
    elif mv == "truck_right":
        d_x = 1.4 * amt * (k - 0.5)
    elif mv == "crane_up":
        d_h = 1.6 * amt * (k - 0.3)
    elif mv == "crane_down":
        d_h = 1.6 * amt * (0.7 - k)
    elif mv == "orbit_left":
        d_yaw = math.radians(22 * amt) * (0.5 - k)
    elif mv == "orbit_right":
        d_yaw = math.radians(22 * amt) * (k - 0.5)
    elif mv == "shake":
        d_dist = -0.12 * dist * amt * k
        d_x = 0.06 * math.sin(t * 37) + 0.04 * math.sin(t * 23)
        d_h = 0.05 * math.sin(t * 31)
    elif mv == "top":   # high angle looking down (battle plans)
        d_h = 0.6 * amt * (0.5 - k)
        d_dist = -0.1 * dist * amt * k
    elif mv == "fly":   # high descending arc, for establishing shots
        d_h = 3.0 * amt * (1 - k)
        d_dist = 0.35 * dist * amt * (1 - k)
        d_yaw = math.radians(14 * amt) * (0.5 - k)
    yy = yaw + d_yaw
    dd = dist + d_dist
    pos = tgt + np.array([math.sin(yy) * -dd + d_x, h + d_h - tgt[1], math.cos(yy) * -dd])
    look = tgt + np.array([d_x, 0, 0])
    # tiny handheld drift so nothing is ever frozen
    pos = pos + np.array([0.03 * math.sin(t * 0.9), 0.02 * math.sin(t * 1.3), 0])
    return pos, look


# ------------------------------------------------------------------ billboards
def _sprite_char(spec, ch, t, env, fps, h_px):
    expr = ch.get("expr", "neutral")
    pose = ch.get("pose", "idle")
    if ch.get("gesture"):
        seq = ch["gesture"]
        pose = seq[int(t / ch.get("gesture_rate", .75)) % len(seq)]
    mouth = 0
    if ch.get("talk") and env is not None and len(env):
        fi = min(len(env) - 1, int(t * fps))
        mouth = 1 if env[fi] > .2 and (int(t * 12) % 2 == 0) else 0
    blink = (t % 3.4) > 3.28
    walk = 0.0
    if ch.get("to") is not None:
        kk = clamp((t - ch.get("delay", 0)) / max(.3, ch.get("walk_time", 2.5)))
        walk = (t * 1.6) % 1.0 if 0 < kk < 1 else 0.0
    base = 600
    spr = toon.make(spec, expr, pose, base, mouth, blink, 1, walk, ch.get("back", False))
    if ch.get("hold"):
        hx, hy = toon.hand_point(pose, base, spec)
        ps = props.make(ch["hold"], int(base * ch.get("hold_size", .16)), ch.get("hold_color"))
        spr = spr.copy()
        spr.alpha_composite(ps, (int(clamp(hx - ps.width / 2, 0, spr.width - ps.width)),
                                 int(clamp(hy - ps.height * .7, 0, spr.height - ps.height))))
    return spr


def render(fr, sc, story, t, dur, env=None, fps=30, spec_fn=None):
    W, H = fr.size
    setname = sc.get("set", "court")
    envq, objq, dflt = build(setname, sc)
    pos, look = cam_pose(sc, dflt, t, dur)
    cam = Cam(pos, look, sc.get("fov", dflt["fov"]), W, H)
    mood = sc.get("mood", dflt["mood"])
    for (_, O, E1, E2, tn, sk, _) in envq:
        if tn == "map_ground":
            tx = sc.get("_map_tex") or map_texture(json.dumps(sc.get("map", {}), sort_keys=True))
        else:
            tx = surface(tn)
        draw_quad(fr, cam, O, E1, E2, tx, sk * mood)
    # draw list: box faces + billboards, far -> near
    items = []
    for (key, O, E1, E2, tn, sk, _) in objq:
        c = np.asarray(O) + np.asarray(E1) / 2 + np.asarray(E2) / 2
        items.append((float(cam.to_cam(c)[2]), "quad", (O, E1, E2, tn, sk)))
    for ch in sc.get("actors", []):
        if t < ch.get("delay", 0):
            continue
        x, z = ch.get("x", 0.0), ch.get("z", 4.0)
        if ch.get("to") is not None:
            kk = ease_in_out(clamp((t - ch.get("delay", 0)) / max(.3, ch.get("walk_time", 2.5))))
            x, z = lerp(x, ch["to"][0], kk), lerp(z, ch["to"][1], kk)
        P = np.array([x, ch.get("y", 0.0), z])
        items.append((float(cam.to_cam(P)[2]), "char", (ch, P)))
    for ob in sc.get("objs", []):
        if t < ob.get("delay", 0):
            continue
        x, z = ob.get("x", 0.0), ob.get("z", 4.0)
        if ob.get("to") is not None:
            kk = ease_in_out(clamp((t - ob.get("delay", 0)) / max(.3, ob.get("move_time", 2.5))))
            x, z = lerp(x, ob["to"][0], kk), lerp(z, ob["to"][1], kk)
        P = np.array([x, ob.get("y", 0.0), z])
        items.append((float(cam.to_cam(P)[2]), "obj", (ob, P)))
    items.sort(key=lambda it: -it[0])
    labels = []
    for zc, kind, data in items:
        if kind == "quad":
            O, E1, E2, tn, sk = data
            draw_quad(fr, cam, O, E1, E2, surface(tn), sk * mood)
            continue
        cfg, P = data
        pr = cam.project(P)
        if pr is None or pr[2] < 0.3:
            continue
        sx, sy, zc = pr
        world_h = cfg.get("h", 1.35 if kind == "char" else 0.8)
        hp = cam.f * world_h / zc
        if hp < 4 or hp > H * 4:
            continue
        te = t - cfg.get("delay", 0)
        if kind == "char":
            spec = spec_fn(cfg.get("who")) if spec_fn else cfg.get("who")
            spr = _sprite_char(spec, cfg, t, env, fps, hp)
            face = cfg.get("face", "right")
        else:
            spr = props.make(cfg["prop"], 400, cfg.get("color"))
            face = cfg.get("face", "right")
        scale = hp / spr.height
        anim = cfg.get("anim", "none")
        dy = 0.0
        if anim == "pop" or (kind == "char" and cfg.get("enter") == "pop"):
            scale *= back_out(clamp(te / .4), 1.8)
        elif anim == "drop":
            dy = -(1 - ease_out(clamp(te / .45))) * hp * 2
        elif anim == "bob":
            dy = math.sin(te * 3) * hp * .03
        elif anim == "fall":
            kf = clamp(te / .9) ** 2
            dy = kf * hp * 2.2
            if kf >= 1:
                continue
        elif anim == "rise":
            dy = -ease_out(clamp(te / 1.2)) * hp * 1.5
        elif anim == "march":
            dy = -abs(math.sin(te * 5)) * hp * .04
        if cfg.get("jump"):
            dy -= abs(math.sin(te * 2 * math.pi / .55)) * hp * .08
        if cfg.get("shake") or anim == "shake":
            sx += math.sin(te * 55) * hp * .02
        w2, h2 = max(1, int(spr.width * scale)), max(1, int(spr.height * scale))
        if w2 * h2 > W * H * 6:
            continue
        img = spr.resize((w2, h2), Image.BILINEAR)
        if face == "left":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if cfg.get("dim"):
            r, g, b_, a = img.split()
            f = lambda v: int(v * .55)
            img = Image.merge("RGBA", (r.point(f), g.point(f), b_.point(f), a))
        # contact shadow on the floor
        sh = Image.new("RGBA", (max(2, int(w2 * .9)), max(2, int(h2 * .07))), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([0, 0, sh.width - 1, sh.height - 1], fill=(0, 0, 0, 70))
        fr.alpha_composite(sh, (int(sx - sh.width / 2), int(sy - sh.height / 2)))
        fr.alpha_composite(img, (int(sx - w2 / 2), int(sy - h2 + dy)))
        if cfg.get("label") and te > .3:
            labels.append((cfg["label"], sx, sy - h2 + dy, hp))
    fr.alpha_composite(_vignette(W, H))
    return labels


@functools.lru_cache(maxsize=4)
def _vignette(W, H):
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = (np.clip((r - 0.65) / 0.7, 0, 1) ** 1.6 * 150).astype(np.uint8)
    warm = np.clip((yy / H) * 0, 0, 0)
    im = np.zeros((H, W, 4), np.uint8); im[..., 3] = a; im[..., 0] = 12; im[..., 1] = 6
    return Image.fromarray(im, "RGBA")


@functools.lru_cache(maxsize=8)
def map_texture(map_json):
    """The flat light map (scenes/toonshot) rendered once and used as a ground texture."""
    import toonshot
    m = json.loads(map_json)
    hl = m.get("highlight", {})
    img = toonshot.light_map(tuple(m.get("view", [60, 5, 100, 38])), 2048, 1024, json.dumps(hl, sort_keys=True))
    return img.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
