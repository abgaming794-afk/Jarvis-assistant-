"""Turns one beat of story.json into frames.

Shot(beat, story, W, H, dur, env).frame(t) -> RGB PIL image.
See references/scenes.md for every key.
"""
import math, random, re, json, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageFilter
from common import (hexc, shade, font, serif, clamp, ease_out, ease_in_out, back_out, lerp, text_size, DATA)
import characters, backgrounds, props

OS = 1.10  # oversize factor for camera moves
RED = (232, 52, 44, 255)
WHITE = (255, 255, 255, 255)


# =============================================================== text sprites
def _parse_marked(s):
    """'EK [COMPANY] NE' -> [('EK ', False), ('COMPANY', True), (' NE', False)]"""
    out, pos = [], 0
    for m in re.finditer(r"\[([^\]]+)\]", s):
        if m.start() > pos:
            out.append((s[pos:m.start()], False))
        out.append((m.group(1), True))
        pos = m.end()
    if pos < len(s):
        out.append((s[pos:], False))
    return out


@functools.lru_cache(maxsize=256)
def headline(text, size, color="#ffffff", hl="#e8342c", stroke_ratio=0.11, max_w=None, shadow=True):
    """Big bold headline, [marked] words in red, thick dark outline. Supports '|' line breaks."""
    f = font(size, "Black")
    stroke = max(2, int(size * stroke_ratio))
    lines = [l.strip() for l in text.upper().split("|")]
    dummy = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    # auto-wrap if too wide
    if max_w:
        wrapped = []
        for l in lines:
            words, cur = l.split(" "), ""
            for w in words:
                trial = (cur + " " + w).strip()
                tw = text_size(dummy, re.sub(r"[\[\]]", "", trial), f, stroke)[0]
                if tw > max_w and cur:
                    wrapped.append(cur)
                    cur = w
                else:
                    cur = trial
            wrapped.append(cur)
        # keep [ ] balanced across wraps
        fixed, open_ = [], False
        for l in wrapped:
            if open_:
                l = "[" + l
            o = l.count("[") > l.count("]")
            if o:
                l = l + "]"
            open_ = o
            fixed.append(l)
        lines = fixed
    lh = int(size * 1.08)
    widths = [text_size(dummy, re.sub(r"[\[\]]", "", l), f, stroke)[0] for l in lines]
    Wd = max(widths) + stroke * 4
    Hd = lh * len(lines) + stroke * 4 + int(size * 0.15)
    img = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        x = (Wd - widths[i]) // 2
        y = stroke * 2 + i * lh
        for seg, red in _parse_marked(l):
            if shadow:
                d.text((x + stroke * 0.6, y + stroke * 0.9), seg, font=f, fill=(0, 0, 0, 150), stroke_width=stroke,
                       stroke_fill=(0, 0, 0, 150))
            d.text((x, y), seg, font=f, fill=hexc(hl) if red else hexc(color), stroke_width=stroke,
                   stroke_fill=(20, 12, 10, 255))
            x += d.textlength(seg, font=f)
    return img


def _paste_center(base, spr, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    if scale != 1.0:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if rot:
        spr = spr.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        a = spr.getchannel("A").point(lambda v: int(v * alpha))
        spr = spr.copy()
        spr.putalpha(a)
    base.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))


def _paste(base, spr, x, y):
    base.alpha_composite(spr, (int(x), int(y)))


_MIRROR = {}


def _mirror(img):
    k = id(img)
    hit = _MIRROR.get(k)
    if hit is None or hit[0] is not img:
        if len(_MIRROR) > 600:
            _MIRROR.clear()
        hit = (img, ImageOps.mirror(img))
        _MIRROR[k] = hit
    return hit[1]


# =============================================================== map
@functools.lru_cache(maxsize=1)
def _world():
    with open(os.path.join(DATA, "world.geojson"), encoding="utf-8") as f:
        return json.load(f)["features"]


@functools.lru_cache(maxsize=1)
def india_full():
    """India's OFFICIAL outline (full J&K incl. PoK/Gilgit-Baltistan, Ladakh incl. Aksai Chin, Arunachal).
    RULE: every map that shows India must draw this on top of the world layer."""
    with open(os.path.join(DATA, "india_full.geojson"), encoding="utf-8") as f:
        return json.load(f)["features"][0]["geometry"]


def draw_india(d, P, fill, outline, width):
    g = india_full()
    polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    for poly in polys:
        ring = [P(x, y) for x, y in poly[0]]
        if len(ring) > 2:
            d.polygon(ring, fill=fill, outline=outline, width=width)


class MapProj:
    def __init__(self, view, W, H):
        lon0, lat0, lon1, lat1 = view
        cl = math.cos(math.radians((lat0 + lat1) / 2))
        vw, vh = (lon1 - lon0) * cl, (lat1 - lat0)
        # fit view inside W x H, expand to aspect
        if vw / vh > W / H:
            vh = vw * H / W
        else:
            vw = vh * W / H
        self.cx, self.cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
        self.cl, self.k = cl, W / vw
        self.W, self.H = W, H

    def __call__(self, lon, lat):
        return (self.W / 2 + (lon - self.cx) * self.cl * self.k, self.H / 2 - (lat - self.cy) * self.k)


@functools.lru_cache(maxsize=16)
def map_image(view, W, H, highlight_json="{}", style="classic"):
    highlight = json.loads(highlight_json)
    pal = {"classic": ("#1f4e6b", "#ecdfc2", "#a68f6a"), "dark": ("#121a26", "#3a4152", "#59627a"),
           "old": ("#9ec3c9", "#ead8ad", "#9a7b4f")}[style]
    img = Image.new("RGBA", (W, H), hexc(pal[0]))
    d = ImageDraw.Draw(img)
    P = MapProj(view, W, H)
    lw = max(1, int(W / 900))
    # graticule
    for lon in range(-180, 181, 15):
        d.line([P(lon, -85), P(lon, 85)], fill=hexc(shade(pal[0], 1.12)), width=1)
    for lat in range(-75, 76, 15):
        d.line([P(-180, lat), P(180, lat)], fill=hexc(shade(pal[0], 1.12)), width=1)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    feats = _world()

    def polys(g):
        if g["type"] == "Polygon":
            yield g["coordinates"]
        else:
            for pc in g["coordinates"]:
                yield pc

    for f in feats:
        for poly in polys(f["geometry"]):
            ring = [P(x + 0.0, y) for x, y in poly[0]]
            if len(ring) > 2:
                sd.polygon([(x + W * 0.004, y + W * 0.005) for x, y in ring], fill=(0, 0, 0, 90))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(W / 300)))
    d = ImageDraw.Draw(img)
    for f in feats:
        iso = f["properties"].get("iso")
        col = highlight.get(iso) or highlight.get(f["properties"].get("name"))
        fill = hexc(col) if col else hexc(pal[1])
        for poly in polys(f["geometry"]):
            ring = [P(x, y) for x, y in poly[0]]
            if len(ring) > 2:
                d.polygon(ring, fill=fill, outline=hexc(pal[2] if not col else shade(col, 0.6)), width=lw)
    icol = highlight.get("IND") or highlight.get("India")
    draw_india(d, P, hexc(icol) if icol else hexc(pal[1]), hexc(shade(icol, 0.6) if icol else pal[2]), lw)
    return img.convert("RGB")


def _quad(p0, p1, bend, t):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    cx, cy = mx - dy * bend, my + dx * bend
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * cx + t * t * p1[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * cy + t * t * p1[1]
    return x, y


# =============================================================== shot
class Shot:
    def __init__(self, beat, story, W, H, dur, env=None, fps=30):
        self.b = beat
        self.sc = dict(beat.get("scene", {}))
        self.story = story
        self.W, self.H = W, H
        self.CW, self.CH = int(W * OS), int(H * OS)
        self.dur = max(0.2, dur)
        self.env = env if env is not None else np.zeros(1)
        self.fps = fps
        self.type = self.sc.get("type", "chars")
        self.rnd = random.Random(beat.get("id", "x"))
        self.u = self.CH / 1080.0  # unit: 1 = 1px at 1080p canvas
        self._base = None

    # ------------------------------------------------ static base
    def base(self):
        if self._base is not None:
            return self._base
        sc, CW, CH = self.sc, self.CW, self.CH
        if self.type == "map":
            hl = sc.get("highlight", {})
            if isinstance(hl, list):
                hl = {k: "#d8402f" for k in hl}
            img = map_image(tuple(sc.get("view", [60, 5, 100, 38])), CW, CH, json.dumps(hl, sort_keys=True),
                            sc.get("style", "classic"))
        else:
            default_bg = {"title": "studio_dark", "number": "studio_gold", "document": "war_room",
                          "timeline": "studio_dark"}.get(self.type, "studio_dark")
            img = backgrounds.make(sc.get("bg", default_bg), CW, CH, sc.get("seed", 0))
        self._base = img.convert("RGBA")
        return self._base

    # ------------------------------------------------ camera
    def camera(self, t):
        cam = self.sc.get("cam", "in" if self.type in ("chars", "map", "document") else "static")
        p = ease_in_out(t / self.dur)
        z, ox, oy = 1.0, 0.0, 0.0
        if cam == "in":
            z = lerp(1.0, 1.09, p)
        elif cam == "out":
            z = lerp(1.09, 1.0, p)
        elif cam == "left":
            z, ox = 1.06, lerp(0.03, -0.03, p)
        elif cam == "right":
            z, ox = 1.06, lerp(-0.03, 0.03, p)
        elif cam == "up":
            z, oy = 1.06, lerp(0.03, -0.03, p)
        elif cam == "punch":
            z = 1.0 + 0.08 * ease_out(t / 0.35) - 0.02 * ease_in_out(clamp((t - 0.35) / max(0.1, self.dur - 0.35)))
        elif cam == "shake":
            z = 1.05
            ox = (self.rnd.random() - 0.5) * 0.012 * (1 - clamp(t / 0.8))
            oy = (self.rnd.random() - 0.5) * 0.012 * (1 - clamp(t / 0.8))
        fx, fy = self.sc.get("focus", [0.5, 0.5])
        return z, ox + (fx - 0.5) * (z - 1) * 1.2, oy + (fy - 0.5) * (z - 1) * 1.2

    # ------------------------------------------------ characters
    def _cast(self, who):
        cast = self.story.get("cast", {})
        if isinstance(who, dict):
            return who
        return cast.get(who, {"preset": who} if who in characters.PRESETS else {"preset": "businessman"})

    def draw_chars(self, can, t):
        chars = self.sc.get("chars", [])
        n = len(chars)
        for i, ch in enumerate(chars):
            spec = self._cast(ch.get("who"))
            h = int(self.CH * ch.get("h", 0.82 if n <= 2 else 0.66))
            expr = ch.get("expr", "neutral")
            if ch.get("expr2") and t > self.dur * ch.get("at2", 0.55):
                expr = ch["expr2"]
            pose = ch.get("pose", "idle")
            if ch.get("pose2") and t > self.dur * ch.get("at2", 0.55):
                pose = ch["pose2"]
            # blink
            per = 3.1 + i * 0.7
            ph = (t + i * 1.3) % per
            blink = ph > per - 0.13
            mouth = 0
            if ch.get("talk"):
                fi = min(len(self.env) - 1, int(t * self.fps))
                mouth = 1 if self.env[fi] > 0.18 else 0
            face = ch.get("face", "right" if ch.get("x", 0.5) < 0.5 else "left")
            look = ch.get("look", [0.6, 0.0])
            spr = characters.make(spec, expr, pose, h, mouth, blink, tuple(look))
            hold = ch.get("hold")
            if hold:
                hx, hy = characters.hand_point(pose, h)
                ps = props.make(hold, int(h * ch.get("hold_size", 0.22)), ch.get("hold_color"))
                spr = spr.copy()
                spr.alpha_composite(ps, (int(min(spr.width - ps.width, max(0, hx - ps.width / 2))),
                                         int(min(spr.height - ps.height, max(0, hy - ps.height * 0.75)))))
            if face == "left":
                spr = _mirror(spr)
            cx = self.CW * ch.get("x", 0.5)
            bottom = self.CH * (1.0 + ch.get("y", 0.06))
            # entrance
            enter = ch.get("enter", "pop" if i == 0 and t < 1 else "none")
            delay = ch.get("delay", 0.0)
            te = clamp((t - delay) / 0.4)
            if t < delay:
                continue
            scale, alpha = 1.0, 1.0
            if enter == "left":
                cx = lerp(-spr.width, cx, back_out(te, 1.2))
            elif enter == "right":
                cx = lerp(self.CW + spr.width, cx, back_out(te, 1.2))
            elif enter == "up":
                bottom = lerp(self.CH + spr.height, bottom, back_out(te, 1.2))
            elif enter == "pop":
                scale = 0.85 + 0.15 * back_out(te, 2.2)
            bob = math.sin(t * 2 * math.pi / 2.4 + i * 1.7) * self.CH * 0.004
            if ch.get("jump"):
                bob -= abs(math.sin(t * 2 * math.pi / 0.6)) * self.CH * 0.03 * (1 - clamp(t / 1.5))
            if ch.get("shake"):
                cx += math.sin(t * 60) * self.CW * 0.004
            if ch.get("dim"):
                r, g, b_, a = spr.split()
                f = lambda v: int(v * 0.55)
                spr = Image.merge("RGBA", (r.point(f), g.point(f), b_.point(f), a))
            if scale != 1.0:
                spr = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.BILINEAR)
            _paste(can, spr, cx - spr.width / 2, bottom - spr.height + bob)

    # ------------------------------------------------ props
    def draw_props(self, can, t, layer="front"):
        for i, pr in enumerate(self.sc.get("props", [])):
            if pr.get("layer", "front") != layer:
                continue
            delay = pr.get("delay", 0.15 + 0.12 * i)
            if t < delay:
                continue
            te = t - delay
            h = int(self.CH * pr.get("h", 0.18))
            spr = props.make(pr["name"], h, pr.get("color"))
            x, y = self.CW * pr.get("x", 0.5), self.CH * pr.get("y", 0.6)
            anim = pr.get("anim", "pop")
            scale, rot = 1.0, pr.get("rot", 0)
            if anim == "pop":
                scale = back_out(clamp(te / 0.35), 2.5)
            elif anim == "drop":
                k = clamp(te / 0.5)
                y = lerp(-h, y, 1 - (1 - k) ** 2) if k < 1 else y
            elif anim == "float":
                y += math.sin(te * 2.2 + i) * self.CH * 0.012
                scale = back_out(clamp(te / 0.35), 2.0)
            elif anim == "spin":
                rot += te * 90
                scale = back_out(clamp(te / 0.35), 2.0)
            elif anim == "slide":
                x = lerp(self.CW * 1.2, x, ease_out(clamp(te / 0.5)))
            _paste_center(can, spr, x, y, scale, 1.0, rot)

    # ------------------------------------------------ effects
    def draw_fx(self, can, t):
        fx = self.sc.get("fx", [])
        if isinstance(fx, str):
            fx = [fx]
        for e in fx:
            if e == "coin_rain":
                r = random.Random(7)
                for k in range(26):
                    x = r.uniform(0, self.CW)
                    sp = r.uniform(0.35, 0.7)
                    y = ((t * sp + r.random()) % 1.2 - 0.1) * self.CH
                    _paste_center(can, props.make("coin", int(self.CH * r.uniform(0.05, 0.09))), x, y, 1.0, 1.0,
                                  (t * 200 + k * 40) % 360)
            elif e == "red_alert":
                a = int(70 + 50 * math.sin(t * 6))
                ov = Image.new("RGBA", can.size, (200, 20, 20, max(0, a)))
                mask = Image.new("L", can.size, 0)
                ImageDraw.Draw(mask).rectangle([0, 0, can.width, can.height], fill=255)
                ImageDraw.Draw(mask).ellipse([can.width * 0.12, can.height * 0.1, can.width * 0.88, can.height * 0.9], fill=0)
                mask = mask.filter(ImageFilter.GaussianBlur(can.width * 0.06))
                can.paste(Image.alpha_composite(can, ov), (0, 0), mask)
            elif e == "smoke":
                r = random.Random(3)
                lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
                d = ImageDraw.Draw(lay)
                for k in range(10):
                    x = (r.uniform(0, 1) + t * 0.02 * (1 + k % 3)) % 1.2 * self.CW
                    y = r.uniform(0.5, 0.95) * self.CH
                    rr = r.uniform(0.08, 0.16) * self.CW
                    d.ellipse([x - rr, y - rr * 0.6, x + rr, y + rr * 0.6], fill=(60, 55, 55, 90))
                can.alpha_composite(lay.filter(ImageFilter.GaussianBlur(self.CW * 0.02)))
            elif e == "spotlight":
                mask = Image.new("L", can.size, 170)
                ImageDraw.Draw(mask).ellipse([can.width * 0.22, can.height * 0.0, can.width * 0.78, can.height * 1.1], fill=0)
                mask = mask.filter(ImageFilter.GaussianBlur(can.width * 0.05))
                can.paste((0, 0, 0, 255), (0, 0), mask)

    # ------------------------------------------------ type layers (under camera)
    def draw_type(self, can, t):
        sc, CW, CH, u = self.sc, self.CW, self.CH, self.u
        if self.type == "map":
            P = MapProj(tuple(sc.get("view", [60, 5, 100, 38])), CW, CH)
            for i, a in enumerate(sc.get("arrows", [])):
                st = a.get("delay", 0.2 + i * 0.4)
                k = ease_in_out(clamp((t - st) / a.get("time", max(0.8, self.dur * 0.55))))
                if k <= 0:
                    continue
                p0, p1 = P(*a["from"]), P(*a["to"])
                bend = a.get("bend", 0.25)
                n = 60
                pts = [_quad(p0, p1, bend, k * j / n) for j in range(n + 1)]
                col = hexc(a.get("color", "#e8342c"))
                d = ImageDraw.Draw(can)
                wl = int(10 * u)
                for j in range(0, n, 2):
                    d.line([pts[j], pts[j + 1]], fill=(20, 12, 10, 255), width=wl + int(6 * u))
                for j in range(0, n, 2):
                    d.line([pts[j], pts[j + 1]], fill=col, width=wl)
                hx, hy = pts[-1]
                px, py = pts[-2]
                ang = math.atan2(hy - py, hx - px)
                L = 34 * u
                tri = [(hx + math.cos(ang) * L * 0.6, hy + math.sin(ang) * L * 0.6),
                       (hx + math.cos(ang + 2.5) * L, hy + math.sin(ang + 2.5) * L),
                       (hx + math.cos(ang - 2.5) * L, hy + math.sin(ang - 2.5) * L)]
                d.polygon(tri, fill=col, outline=(20, 12, 10, 255), width=int(4 * u))
                if a.get("mover"):
                    spr = props.make(a["mover"], int(CH * 0.12))
                    if p1[0] < p0[0]:
                        spr = _mirror(spr)
                    _paste_center(can, spr, hx, hy - CH * 0.04)
            for i, pin in enumerate(sc.get("pins", [])):
                st = pin.get("delay", 0.3 + i * 0.35)
                k = clamp((t - st) / 0.4)
                if k <= 0:
                    continue
                x, y = P(pin["lon"], pin["lat"])
                y -= (1 - back_out(k, 2)) * 60 * u
                d = ImageDraw.Draw(can)
                r = 16 * u
                col = hexc(pin.get("color", "#e8342c"))
                d.polygon([(x, y), (x - r * 0.9, y - r * 1.6), (x + r * 0.9, y - r * 1.6)], fill=col,
                          outline=(20, 12, 10, 255), width=int(4 * u))
                d.ellipse([x - r, y - r * 2.6, x + r, y - r * 0.6], fill=col, outline=(20, 12, 10, 255), width=int(4 * u))
                d.ellipse([x - r * 0.4, y - r * 2.0, x + r * 0.4, y - r * 1.2], fill=(255, 255, 255, 255))
                if pin.get("label"):
                    lab = headline(pin["label"], int(46 * u), stroke_ratio=0.14)
                    _paste_center(can, lab, x, y - r * 2.6 - lab.height * 0.55, back_out(k, 2))
            for lab in sc.get("labels", []):
                x, y = P(lab["lon"], lab["lat"])
                spr = headline(lab["t"], int(lab.get("size", 40) * u), color=lab.get("color", "#ffffff"),
                               stroke_ratio=0.14)
                _paste_center(can, spr, x, y, back_out(clamp((t - lab.get("delay", 0.2)) / 0.4), 2))
        elif self.type == "document":
            k = ease_out(clamp(t / 0.45))
            pw, ph = int(CW * 0.46), int(CH * 0.78)
            paper = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
            d = ImageDraw.Draw(paper)
            d.rectangle([0, 0, pw - 1, ph - 1], fill=hexc(sc.get("paper", "#f1e3bf")), outline=(110, 80, 40, 255),
                        width=int(6 * u))
            d.rectangle([int(18 * u), int(18 * u), pw - int(18 * u), ph - int(18 * u)], outline=(150, 115, 60, 255),
                        width=int(3 * u))
            title = sc.get("title", "DOCUMENT")
            ft = serif(int(52 * u))
            d.text((pw / 2, int(80 * u)), title, font=ft, fill=(60, 35, 20, 255), anchor="mm")
            d.line([(pw * 0.2, int(125 * u)), (pw * 0.8, int(125 * u))], fill=(120, 80, 40, 255), width=int(3 * u))
            fl = serif(int(34 * u))
            y = int(175 * u)
            lines = sc.get("lines", [])
            hi = sc.get("highlight", -1)
            for li, line in enumerate(lines):
                if li == hi:
                    hk = ease_in_out(clamp((t - self.dur * 0.3) / 0.6))
                    tw = d.textlength(line, font=fl)
                    hl = Image.new("RGBA", paper.size, (0, 0, 0, 0))
                    ImageDraw.Draw(hl).rectangle([int(50 * u) - 6, y - int(6 * u), int(50 * u) + tw * hk + 6, y + int(44 * u)],
                                                 fill=(255, 214, 0, 150))
                    paper.alpha_composite(hl)
                    d = ImageDraw.Draw(paper)
                d.text((int(50 * u), y), line, font=fl, fill=(50, 30, 20, 255))
                y += int(62 * u)
            if sc.get("stamp"):
                sk = clamp((t - self.dur * 0.55) / 0.25)
                if sk > 0:
                    fs = font(int(56 * u), "Black")
                    tw = ImageDraw.Draw(paper).textlength(sc["stamp"], font=fs)
                    st = Image.new("RGBA", (int(tw + 70 * u), int(140 * u)), (0, 0, 0, 0))
                    sd = ImageDraw.Draw(st)
                    sd.rounded_rectangle([4, 4, st.width - 4, st.height - 4], radius=int(14 * u),
                                         outline=(190, 30, 36, 230), width=int(10 * u))
                    sd.text((st.width / 2, st.height / 2), sc["stamp"], font=fs,
                            fill=(190, 30, 36, 230), anchor="mm")
                    _paste_center(paper, st, pw - st.width * 0.62, ph * 0.82, lerp(2.2, 1.0, ease_out(sk)), 1.0, 14)
            _paste_center(can, paper, CW * sc.get("x", 0.5), lerp(CH * 1.4, CH * 0.52, k), 1.0, 1.0, sc.get("rot", -3))
        elif self.type == "timeline":
            items = sc.get("items", [])
            n = max(1, len(items))
            y = CH * 0.55
            d = ImageDraw.Draw(can)
            x0, x1 = CW * 0.1, CW * 0.9
            d.line([(x0, y), (x1, y)], fill=(240, 230, 210, 255), width=int(10 * u))
            focus = sc.get("focus", n - 1)
            for i, it in enumerate(items):
                x = lerp(x0 + CW * 0.06, x1 - CW * 0.06, i / max(1, n - 1)) if n > 1 else CW / 2
                k = back_out(clamp((t - 0.15 - i * 0.18) / 0.35), 2)
                big = i == focus
                r = (26 if big else 16) * u * k
                d.ellipse([x - r, y - r, x + r, y + r], fill=RED if big else (240, 230, 210, 255),
                          outline=(20, 12, 10, 255), width=int(5 * u))
                if k > 0:
                    yr = headline(str(it.get("year", "")), int((84 if big else 54) * u), hl="#e8342c",
                                  color="#e8342c" if big else "#ffffff")
                    _paste_center(can, yr, x, y - CH * 0.11, k)
                    if it.get("label"):
                        lb = headline(it["label"], int((40 if big else 32) * u), max_w=int(CW / n * 0.95))
                        _paste_center(can, lb, x, y + CH * 0.1 + lb.height / 2 - CH * 0.03, k)
                    d = ImageDraw.Draw(can)

    # ------------------------------------------------ overlay (not affected by camera)
    def draw_overlay(self, fr, t):
        sc, W, H = self.sc, self.W, self.H
        u = H / 1080.0
        if self.type == "title":
            lines = sc.get("lines", [sc.get("t", "")])
            txt = "|".join(lines)
            size = int(sc.get("size", 150) * u)
            spr = headline(txt, size, max_w=int(W * 0.9))
            k = clamp(t / 0.35)
            _paste_center(fr, spr, W / 2, H * sc.get("y", 0.47), back_out(k, 2.2))
            if sc.get("sub"):
                sub = headline(sc["sub"], int(size * 0.38), color="#f1c232", max_w=int(W * 0.85))
                _paste_center(fr, sub, W / 2, H * sc.get("y", 0.47) + spr.height / 2 + sub.height * 0.7,
                              back_out(clamp((t - 0.35) / 0.35), 2))
        elif self.type == "number":
            k = ease_out(clamp(t / max(0.6, self.dur * 0.6)))
            v0, v1 = float(sc.get("from", 0)), float(sc["value"])
            v = lerp(v0, v1, k)
            dec = int(sc.get("decimals", 0))
            if sc.get("format", "indian") == "indian" and dec == 0:
                s = _indian(int(round(v)))
            else:
                s = f"{v:,.{dec}f}"
            txt = f"{sc.get('prefix', '')}{s}{sc.get('suffix', '')}"
            size = int(sc.get("size", 190) * u)
            spr = headline(txt, size, color=sc.get("color", "#f1c232"))
            if spr.width > W * 0.92:
                spr = headline(txt, int(size * W * 0.92 / spr.width), color=sc.get("color", "#f1c232"))
            _paste_center(fr, spr, W / 2, H * sc.get("y", 0.42), back_out(clamp(t / 0.3), 2))
            if sc.get("label"):
                lb = headline(sc["label"], int(size * 0.36), max_w=int(W * 0.85))
                _paste_center(fr, lb, W / 2, H * sc.get("y", 0.42) + spr.height * 0.5 + lb.height * 0.75,
                              back_out(clamp((t - 0.3) / 0.35), 2))
        # generic headline text on any scene
        tx = sc.get("text")
        if tx:
            if isinstance(tx, str):
                tx = {"t": tx}
            st = tx.get("at", 0.15)
            if t >= st:
                size = int(tx.get("size", 108) * u)
                spr = headline(tx["t"], size, color=tx.get("color", "#ffffff"), max_w=int(W * 0.92))
                pos = tx.get("pos", "top")
                y = {"top": H * 0.04 + spr.height / 2, "bottom": H * 0.96 - spr.height / 2,
                     "center": H * 0.5}.get(pos, H * 0.12)
                _paste_center(fr, spr, W * tx.get("x", 0.5), y, back_out(clamp((t - st) / 0.3), 2.2))

    # ------------------------------------------------ frame
    def frame(self, t):
        can = self.base().copy()
        self.draw_props(can, t, "back")
        self.draw_type(can, t)
        self.draw_chars(can, t)
        self.draw_props(can, t, "front")
        self.draw_fx(can, t)
        z, ox, oy = self.camera(t)
        cw, ch = self.CW / z, self.CH / z
        cx = self.CW / 2 + ox * self.CW
        cy = self.CH / 2 + oy * self.CH
        x0 = clamp(cx - cw / 2, 0, self.CW - cw)
        y0 = clamp(cy - ch / 2, 0, self.CH - ch)
        fr = can.resize((self.W, self.H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        self.draw_overlay(fr, t)
        # quick fade-in from black on chapter starts
        if self.b.get("chapter") and t < 0.25:
            fr = Image.blend(Image.new("RGBA", fr.size, (0, 0, 0, 255)), fr, t / 0.25)
        return fr.convert("RGB")


def _indian(n):
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if n < 0 else "") + s
