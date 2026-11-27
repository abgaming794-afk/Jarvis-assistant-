"""Documentary-toon shots (default style). ToonShot(beat, story, W, H, dur, env, fps).frame(t) -> RGB.

Scene types (beat["scene"]["type"]):
  set        room + full-body characters (+ props, labels, big numbers, lower third)   [default]
  black      black card with hand-written white text typed letter by letter (chapter cards, punchlines)
  map        light flat map, highlighted countries, animated dashed routes with ship/plane, pins
  chart      bar chart that grows (cream paper)
  memo       paper document / note with hand-writing, red marker circle, stamp
  newspaper  old newspaper front page that spins in, headline + toon portrait
See references/scenes.md for every key.
"""
import math, random, re, json, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from common import hexc, shade, font, serif, clamp, ease_out, ease_in_out, back_out, lerp, FONTS
import toon, props, rooms, motion, pbfx, docs3d, set3d
from common import SKILL
from scenes import MapProj, _quad, _paste_center, _paste, _mirror, _world, _indian, draw_india

OS = 1.10
DEV = re.compile(r"[ऀ-ॿ]")


@functools.lru_cache(maxsize=64)
def hand(size, kind="caveat"):
    """Hand-written fonts. kind: caveat (script), marker (bold labels), kalam (Devanagari + Latin)."""
    size = max(6, int(size))
    if kind == "marker":
        p = os.path.join(FONTS, "PermanentMarker-Regular.ttf")
    elif kind == "kalam":
        p = os.path.join(FONTS, "Kalam-Bold.ttf")
    else:
        p = os.path.join(FONTS, "Caveat-Variable.ttf")
    try:
        f = ImageFont.truetype(p, size)
        if kind == "caveat":
            try:
                f.set_variation_by_name("Bold")
            except Exception:
                pass
        return f
    except OSError:
        return font(size, "Bold")


def hfont(text, size, kind="caveat"):
    return hand(size, "kalam" if DEV.search(text or "") else kind)


@functools.lru_cache(maxsize=256)
def tag(text, size, bg="#f6f2e8", fg="#1b1717", pointer=True, kind="marker"):
    f = hfont(text, size, kind)
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    b = d.textbbox((0, 0), text, font=f)
    tw, th = b[2] - b[0], b[3] - b[1]
    pad = int(size * 0.35)
    pw = int(size * 0.35) if pointer else 0
    img = Image.new("RGBA", (tw + pad * 2 + 8, th + pad * 2 + pw + 8), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    g.rounded_rectangle([4, 4, tw + pad * 2 + 4, th + pad * 2 + 4], radius=size * 0.18, fill=hexc(bg),
                        outline=(30, 22, 20, 255), width=max(2, size // 14))
    if pointer:
        cx = img.width / 2
        g.polygon([(cx - pw, th + pad * 2 + 2), (cx + pw, th + pad * 2 + 2), (cx, th + pad * 2 + pw + 6)],
                  fill=hexc(bg), outline=(30, 22, 20, 255))
        g.line([(cx - pw + 2, th + pad * 2 + 4), (cx + pw - 2, th + pad * 2 + 4)], fill=hexc(bg), width=max(2, size // 12))
    g.text((4 + pad - b[0], 4 + pad - b[1]), text, font=f, fill=hexc(fg))
    return img


@functools.lru_cache(maxsize=128)
def big_text(text, size, color="#f1c232", kind="marker"):
    f = hfont(text, size, kind)
    c = hexc(color)
    dark = (c[0] * .3 + c[1] * .59 + c[2] * .11) < 110
    stroke = max(2, size // 12) if not dark else 0
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    b = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    img = Image.new("RGBA", (b[2] - b[0] + stroke * 4, b[3] - b[1] + stroke * 4), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    if not dark:
        g.text((stroke * 2 - b[0] + stroke, stroke * 2 - b[1] + stroke), text, font=f, fill=(0, 0, 0, 140),
               stroke_width=stroke, stroke_fill=(0, 0, 0, 140))
    g.text((stroke * 2 - b[0], stroke * 2 - b[1]), text, font=f, fill=hexc(color), stroke_width=stroke,
           stroke_fill=(24, 16, 14, 255))
    return img


def lower_third(name, role, H):
    u = H / 1080
    fn = hfont(name, int(56 * u), "marker")
    fr = font(int(22 * u), "Bold")
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    nw = d.textlength(name, font=fn)
    rw = d.textlength(role.upper(), font=fr) if role else 0
    w = int(max(nw, rw) + 80 * u)
    h = int(118 * u)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    g.rectangle([0, 0, w, h], fill=(18, 20, 30, 225))
    g.rectangle([0, 0, int(10 * u), h], fill=(214, 40, 40, 255))
    if role:
        g.text((int(32 * u), int(14 * u)), role.upper(), font=fr, fill=(214, 205, 190, 255))
    g.text((int(32 * u), int(40 * u)), name, font=fn, fill=(255, 255, 255, 255))
    return img


# ------------------------------------------------------------------ light map
@functools.lru_cache(maxsize=12)
def light_map(view, W, H, hl_json="{}"):
    hl = json.loads(hl_json)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = np.linspace(0, 1, H)[:, None]
    sea = (np.array([182, 214, 230]) * (1 - a) + np.array([150, 190, 214]) * a)[:, None, :].repeat(W, 1)
    img = Image.fromarray(sea.reshape(H, W, 3).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img)
    P = MapProj(view, W, H)
    lw = max(1, int(W / 1100))

    def polys(g):
        if g["type"] == "Polygon":
            yield g["coordinates"]
        else:
            yield from g["coordinates"]

    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for f in _world():
        for poly in polys(f["geometry"]):
            ring = [P(x, y) for x, y in poly[0]]
            if len(ring) > 2:
                sd.polygon([(x + W * .003, y + W * .004) for x, y in ring], fill=(40, 70, 90, 70))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(W / 400)))
    d = ImageDraw.Draw(img)
    for f in _world():
        iso, name = f["properties"].get("iso"), f["properties"].get("name")
        col = hl.get(iso) or hl.get(name)
        for poly in polys(f["geometry"]):
            ring = [P(x, y) for x, y in poly[0]]
            if len(ring) > 2:
                d.polygon(ring, fill=hexc(col) if col else (243, 236, 220, 255),
                          outline=hexc(shade(col, 0.7)) if col else (196, 184, 160, 255), width=lw)
    icol = hl.get("IND") or hl.get("India")
    draw_india(d, P, hexc(icol) if icol else (243, 236, 220, 255), hexc(shade(icol, .7)) if icol else (196, 184, 160, 255), lw)
    arr = np.asarray(img.convert("RGB"), np.float32)
    arr += np.random.default_rng(2).normal(0, 3, (H, W, 1))
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.41
    arr *= (1 - 0.35 * np.clip(dd, 0, 1) ** 2)[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB")


# ------------------------------------------------------------------ shot
class ToonShot:
    def __init__(self, beat, story, W, H, dur, env=None, fps=30):
        self.b, self.story = beat, story
        self.sc = dict(beat.get("scene", {}))
        self.W, self.H = W, H
        self.CW, self.CH = int(W * OS), int(H * OS)
        self.dur = max(0.2, dur)
        self.env = env if env is not None and len(env) else np.zeros(1)
        self.fps = fps
        self.type = self.sc.get("type", "set")
        self.rnd = random.Random(beat.get("id", "x"))
        self.u = self.CH / 1080.0
        self._base = None

    # ---------------- base layer (cached per shot)
    def base(self):
        if self._base is None:
            sc = self.sc
            if self.type == "topdown":
                self._base = pbfx.topdown_base(self.CW, self.CH, sc)
                return self._base
            if self.type == "map":
                hl = sc.get("highlight", {})
                if isinstance(hl, list):
                    hl = {k: "#d8402f" for k in hl}
                img = light_map(tuple(sc.get("view", [60, 5, 100, 38])), self.CW, self.CH, json.dumps(hl, sort_keys=True))
            else:
                bg = sc.get("bg", {"black": "black", "chart": "paper", "memo": "desk_top", "realdoc": "desk_top",
                                   "newspaper": "desk_top"}.get(self.type, "study_night"))
                if bg == "paper":
                    img = rooms.make("office_day", self.CW, self.CH)
                    img = Image.new("RGB", img.size, (238, 230, 212))
                else:
                    img = rooms.make(bg, self.CW, self.CH, sc.get("seed", 0))
            self._base = img.convert("RGBA")
        return self._base

    # ---------------- camera
    def camera(self, t):
        default = {"set": "auto", "black": "static", "map": "dolly_in", "memo": "dolly_in", "chart": "drift",
                   "newspaper": "dolly_in", "topdown": "table_roll", "realdoc": "drift"}.get(self.type, "dolly_in")
        return motion.camera(self.sc.get("cam", default), t, self.dur, self.b.get("id", ""))

    def _spec(self, who):
        if isinstance(who, dict):
            return who
        cast = self.story.get("cast", {})
        return cast.get(who, {"preset": who} if who in toon.PRESETS else {"preset": "businessman"})

    # ---------------- characters
    def draw_chars(self, can, t):
        floor_y = self.CH * rooms.floor(self.sc.get("bg", "study_night")) if self.type == "set" else self.CH * 0.98
        for i, ch in enumerate(self.sc.get("chars", [])):
            delay = ch.get("delay", 0.0)
            if t < delay:
                continue
            spec = self._spec(ch.get("who"))
            close = ch.get("close", False)
            h = int(self.CH * ch.get("h", 1.45 if close else 0.46))
            expr = ch.get("expr2") if ch.get("expr2") and t > self.dur * ch.get("at2", .55) else ch.get("expr", "neutral")
            pose = ch.get("pose2") if ch.get("pose2") and t > self.dur * ch.get("at2", .55) else ch.get("pose", "idle")
            if ch.get("gesture"):
                seq = ch["gesture"] if isinstance(ch["gesture"], list) else [pose, "point", pose, "shrug"]
                pose = seq[int((t + i * .37) / ch.get("gesture_rate", .75)) % len(seq)]
            per = 3.3 + i * .8
            blink = ((t + i * 1.1) % per) > per - .12
            mouth = 0
            if ch.get("talk"):
                fi = min(len(self.env) - 1, int(t * self.fps))
                mouth = 1 if self.env[fi] > .2 and (int(t * 12) % 2 == 0) else 0
            x = ch.get("x", .5)
            walk = 0.0
            if "to" in ch:
                k = clamp((t - delay) / max(.3, ch.get("walk_time", self.dur * .8)))
                x = lerp(x, ch["to"], ease_in_out(k))
                walk = (t * 1.6) % 1.0 if 0 < k < 1 else 0.0
            face = ch.get("face")
            if face is None:
                face = "right" if (ch.get("to", x) >= x and x < .5) else "left"
            spr = toon.make(spec, expr, pose, h, mouth, blink, 1, walk, ch.get("back", False))
            if ch.get("hold"):
                hx, hy = toon.hand_point(pose, h, spec)
                ps = props.make(ch["hold"], int(h * ch.get("hold_size", .16)), ch.get("hold_color"))
                spr = spr.copy()
                spr.alpha_composite(ps, (int(clamp(hx - ps.width / 2, 0, spr.width - ps.width)),
                                         int(clamp(hy - ps.height * .7, 0, spr.height - ps.height))))
            if face == "left":
                spr = _mirror(spr)
            cx = self.CW * x
            if close:
                top = self.CH * ch.get("head_y", .44) - h * (toon.HY / toon.H)
                bottom = top + h
            else:
                bottom = floor_y + self.CH * ch.get("y", 0.0)
            bob = math.sin(t * 2 * math.pi / 2.6 + i * 1.9) * self.CH * .0015
            breath = 1 + .012 * math.sin(t * 2 * math.pi / 2.8 + i * 1.3)
            spr = spr.resize((spr.width, max(1, int(spr.height * breath))), Image.BILINEAR)
            if ch.get("jump"):
                bob -= abs(math.sin(t * 2 * math.pi / .55)) * self.CH * .03
            if ch.get("shake"):
                cx += math.sin(t * 55) * self.CW * .003
            enter = ch.get("enter")
            if enter:
                k = back_out(clamp((t - delay) / .45), 1.1)
                if enter == "left":
                    cx = lerp(-spr.width, cx, k)
                elif enter == "right":
                    cx = lerp(self.CW + spr.width, cx, k)
                elif enter == "pop":
                    spr = spr.resize((max(1, int(spr.width * (.8 + .2 * k))), max(1, int(spr.height * (.8 + .2 * k)))))
            if ch.get("dim"):
                r, g, b_, a = spr.split()
                f = lambda v: int(v * .5)
                spr = Image.merge("RGBA", (r.point(f), g.point(f), b_.point(f), a))
            top = bottom - spr.height + bob
            clip = ch.get("clip", self.sc.get("table", {}).get("y") if ch.get("seated") else None)
            if clip is not None:
                keep = int(self.CH * clip - top + self.CH * .01)
                if keep <= 0:
                    continue
                spr = spr.crop((0, 0, spr.width, min(spr.height, keep)))
            _paste(can, spr, cx - spr.width / 2, top)
            if ch.get("label"):
                lk = back_out(clamp((t - delay - ch.get("label_at", .25)) / .3), 2)
                if lk > 0:
                    tg = tag(ch["label"], int(38 * self.u))
                    _paste_center(can, tg, cx, bottom - spr.height - tg.height * .55 - self.CH * .01, lk)

    # ---------------- props
    def draw_props(self, can, t, layer):
        for i, pr in enumerate(self.sc.get("props", [])):
            if pr.get("layer", "front") != layer:
                continue
            delay = pr.get("delay", 0.0 if pr.get("anim", "none") == "none" else .2 + .12 * i)
            if t < delay:
                continue
            te = t - delay
            h = int(self.CH * pr.get("h", .12))
            spr = props.make(pr["name"], h, pr.get("color"))
            x, y = self.CW * pr.get("x", .5), self.CH * pr.get("y", .7)
            anim, scale, rot = pr.get("anim", "none"), 1.0, pr.get("rot", 0)
            if anim == "pop":
                scale = back_out(clamp(te / .35), 2.4)
            elif anim == "drop":
                y = lerp(-h, y, 1 - (1 - clamp(te / .45)) ** 2)
            elif anim == "float":
                y += math.sin(te * 2.2 + i) * self.CH * .01
            elif anim == "slide":
                x = lerp(self.CW * 1.2, x, ease_out(clamp(te / .5)))
            elif anim == "spin":
                rot += te * 120
            _paste_center(can, spr, x, y, scale, 1.0, rot)
            if pr.get("label"):
                tg = tag(pr["label"], int(32 * self.u))
                _paste_center(can, tg, x, y - spr.height * scale / 2 - tg.height * .6, back_out(clamp((te - .2) / .3), 2))

    # ---------------- type specific (under camera)
    def draw_type(self, can, t):
        sc, CW, CH, u = self.sc, self.CW, self.CH, self.u
        if self.type == "map":
            P = MapProj(tuple(sc.get("view", [60, 5, 100, 38])), CW, CH)
            d = ImageDraw.Draw(can)
            for i, a in enumerate(sc.get("routes", sc.get("arrows", []))):
                st = a.get("delay", .2 + i * .5)
                k = ease_in_out(clamp((t - st) / a.get("time", max(.8, self.dur * .6))))
                if k <= 0:
                    continue
                pts = [a["from"]] + a.get("via", []) + [a["to"]]
                pp = [P(*q) for q in pts]
                segs = []
                for j in range(len(pp) - 1):
                    segs += [_quad(pp[j], pp[j + 1], a.get("bend", .18), s / 30) for s in range(30)]
                segs.append(pp[-1])
                n = max(2, int(len(segs) * k))
                path = segs[:n]
                col = hexc(a.get("color", "#ffffff"))
                wl = max(2, int(7 * u))
                for j in range(0, len(path) - 1):
                    if (j // 2) % 2 == 0:
                        d.line([path[j], path[j + 1]], fill=(30, 40, 50, 200), width=wl + int(4 * u))
                        d.line([path[j], path[j + 1]], fill=col, width=wl)
                if a.get("mover") and len(path) > 1:
                    spr = props.make(a["mover"], int(CH * .08))
                    if path[-1][0] < path[-2][0]:
                        spr = _mirror(spr)
                    _paste_center(can, spr, path[-1][0], path[-1][1] - CH * .03)
            for i, pin in enumerate(sc.get("pins", [])):
                st = pin.get("delay", .3 + i * .35)
                k = clamp((t - st) / .35)
                if k <= 0:
                    continue
                x, y = P(pin["lon"], pin["lat"])
                r = 13 * u
                pulse = (t * 1.2) % 1
                glow = Image.new("RGBA", can.size, (0, 0, 0, 0))
                ImageDraw.Draw(glow).ellipse([x - r * (1 + 2 * pulse), y - r * (1 + 2 * pulse), x + r * (1 + 2 * pulse),
                                              y + r * (1 + 2 * pulse)], outline=(230, 50, 40, int(200 * (1 - pulse))),
                                             width=int(4 * u))
                can.alpha_composite(glow)
                d = ImageDraw.Draw(can)
                rr = r * back_out(k, 2)
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=hexc(pin.get("color", "#e8342c")), outline=(30, 20, 20, 255),
                          width=int(3 * u))
                if pin.get("label"):
                    tg = tag(pin["label"], int(34 * u), bg="#1c1f2a", fg="#ffffff")
                    _paste_center(can, tg, x, y - r - tg.height * .55, back_out(k, 2))
            for lab in sc.get("labels", []):
                x, y = P(lab["lon"], lab["lat"])
                tg = big_text(lab["t"], int(lab.get("size", 44) * u), lab.get("color", "#2a2a2a"), "marker")
                _paste_center(can, tg, x, y, back_out(clamp((t - lab.get("delay", .2)) / .35), 2))
        elif self.type == "chart":
            bars = sc.get("bars", [])
            n = max(1, len(bars))
            x0, x1, yb = CW * .2, CW * .8, CH * .78
            d = ImageDraw.Draw(can)
            d.line([(x0 - 20 * u, yb), (x1 + 20 * u, yb)], fill=(60, 50, 45, 255), width=int(5 * u))
            vmax = max(float(b["value"]) for b in bars) if bars else 1
            bw = (x1 - x0) / n * .45
            for i, b in enumerate(bars):
                k = ease_out(clamp((t - .2 - i * .35) / .9))
                cx = lerp(x0, x1, (i + .5) / n)
                hgt = (CH * .46) * float(b["value"]) / vmax * k
                d.rectangle([cx - bw / 2, yb - hgt, cx + bw / 2, yb], fill=hexc(b.get("color", "#2f9e44")),
                            outline=(40, 30, 28, 255), width=int(4 * u))
                lab = big_text(b.get("label", ""), int(46 * u), "#2a2a2a", "marker")
                _paste_center(can, lab, cx, yb + 45 * u)
                if k > .05:
                    val = big_text(b.get("text", str(b["value"])), int(64 * u), b.get("text_color", "#2a2a2a"), "marker")
                    _paste_center(can, val, cx, yb - hgt - 40 * u, back_out(clamp((t - .4 - i * .35) / .4), 2))
                d = ImageDraw.Draw(can)
        elif self.type == "memo":
            self._memo(can, t)
        elif self.type == "realdoc":
            if not hasattr(self, "_doc"):
                self._doc = docs3d.DocShot(sc, CW, CH, self.dur)
            self._doc.draw(can, t)
        elif self.type == "newspaper":
            self._paper(can, t)

    def _memo(self, can, t):
        sc, CW, CH, u = self.sc, self.CW, self.CH, self.u
        pw, ph = int(CW * sc.get("w", .42)), int(CH * sc.get("h", .74))
        paper = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        g = ImageDraw.Draw(paper)
        pc = sc.get("paper", "#f3ecd8" if not sc.get("sticky") else "#f6e27a")
        g.rectangle([0, 0, pw - 1, ph - 1], fill=hexc(pc), outline=(90, 70, 50, 255), width=int(4 * u))
        if not sc.get("sticky"):
            dev0 = any(DEV.search(l) for l in sc.get("lines", []))
            stp = int((70 if dev0 else 58) * u)
            for k in range(int((160 if dev0 else 170) * u), ph - int(40 * u), stp):
                g.line([(int(36 * u), k + stp), (pw - int(36 * u), k + stp)], fill=(170, 195, 215, 255), width=max(1, int(2 * u)))
            g.line([(int(80 * u), 0), (int(80 * u), ph)], fill=(220, 120, 120, 255), width=max(1, int(2 * u)))
        title = sc.get("title", "")
        if title:
            ft = hfont(title, int(64 * u), "marker")
            g.text((pw / 2, int(80 * u)), title, font=ft, fill=(40, 30, 28, 255), anchor="mm")
        hi = sc.get("highlight", -1)
        lines = sc.get("lines", [])
        dev = any(DEV.search(l) for l in lines)
        step = int((70 if dev else 58) * u)
        y = int((160 if dev else 170) * u)
        boxes = []
        for i, line in enumerate(lines):
            fs = int((42 if DEV.search(line) else 50) * u)
            f = hfont(line, fs, "caveat")
            while g.textlength(line, font=f) > pw - 140 * u and fs > 12:
                fs = int(fs * .92)
                f = hfont(line, fs, "caveat")
            g.text((int(100 * u), y), line, font=f, fill=(30, 40, 80, 255))
            bb = g.textbbox((int(100 * u), y), line, font=f)
            boxes.append(bb)
            y += step
        if 0 <= hi < len(boxes):
            k = ease_in_out(clamp((t - self.dur * sc.get("mark_at", .35)) / .7))
            if k > 0:
                x0, y0, x1, y1 = boxes[hi]
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                rx, ry = (x1 - x0) / 2 + 30 * u, (y1 - y0) / 2 + 22 * u
                pts = [(cx + math.cos(a) * rx, cy + math.sin(a) * ry) for a in
                       np.linspace(math.pi * .9, math.pi * .9 + 2 * math.pi * 1.05 * k, 60)]
                g.line(pts, fill=(214, 40, 40, 255), width=int(7 * u), joint="curve")
        if sc.get("stamp"):
            sk = clamp((t - self.dur * .6) / .2)
            if sk > 0:
                fs = font(int(60 * u), "Black")
                tw = g.textlength(sc["stamp"], font=fs)
                st = Image.new("RGBA", (int(tw + 60 * u), int(120 * u)), (0, 0, 0, 0))
                sd = ImageDraw.Draw(st)
                sd.rounded_rectangle([4, 4, st.width - 4, st.height - 4], radius=int(12 * u), outline=(200, 30, 36, 230), width=int(9 * u))
                sd.text((st.width / 2, st.height / 2), sc["stamp"], font=fs, fill=(200, 30, 36, 230), anchor="mm")
                _paste_center(paper, st, pw * .62, ph * .8, lerp(2.0, 1.0, ease_out(sk)), 1.0, 12)
        d3 = dict(sc)
        d3.setdefault("yaw", [16, 5])
        d3.setdefault("pitch", [10, 3])
        d3.setdefault("roll", [3, -1])
        d3.setdefault("push", [1.0, 1.25])
        if 0 <= hi < len(boxes):
            x0, y0, x1, y1 = boxes[hi]
            d3.setdefault("focus", [(x0 + x1) / 2 / pw, (y0 + y1) / 2 / ph])
        docs3d.place_3d(can, paper, t, self.dur, d3)

    def _paper(self, can, t):
        sc, CW, CH, u = self.sc, self.CW, self.CH, self.u
        pw, ph = int(CW * .5), int(CH * .82)
        paper = Image.new("RGBA", (pw, ph), (236, 228, 206, 255))
        g = ImageDraw.Draw(paper)
        g.rectangle([0, 0, pw - 1, ph - 1], outline=(80, 70, 60, 255), width=int(4 * u))
        g.text((pw / 2, int(70 * u)), sc.get("name", "THE GAZETTE"), font=serif(int(70 * u)), fill=(25, 20, 20, 255), anchor="mm")
        g.line([(30 * u, 120 * u), (pw - 30 * u, 120 * u)], fill=(25, 20, 20, 255), width=int(4 * u))
        g.text((pw / 2, int(140 * u)), sc.get("date", ""), font=serif(int(24 * u)), fill=(60, 50, 45, 255), anchor="mm")
        g.line([(30 * u, 160 * u), (pw - 30 * u, 160 * u)], fill=(25, 20, 20, 255), width=int(2 * u))
        hl = sc.get("headline", "")
        f = serif(int(64 * u))
        words, lines, cur = hl.split(), [], ""
        for w in words:
            tr = (cur + " " + w).strip()
            if g.textlength(tr, font=f) > pw - 80 * u and cur:
                lines.append(cur)
                cur = w
            else:
                cur = tr
        lines.append(cur)
        y = 200 * u
        for l in lines:
            g.text((pw / 2, y), l, font=f, fill=(20, 16, 16, 255), anchor="mt")
            y += 74 * u
        y += 20 * u
        ix0, iy0, ix1, iy1 = 40 * u, y, pw * .55, y + ph * .38
        g.rectangle([ix0, iy0, ix1, iy1], fill=(200, 192, 172, 255), outline=(60, 50, 45, 255), width=int(3 * u))
        if sc.get("who"):
            spr = toon.make(self._spec(sc["who"]), sc.get("expr", "neutral"), "idle", int((iy1 - iy0) * 1.6))
            spr = ImageOps.grayscale(spr.convert("RGB")).convert("RGBA")
            a = toon.make(self._spec(sc["who"]), sc.get("expr", "neutral"), "idle", int((iy1 - iy0) * 1.6)).getchannel("A")
            spr.putalpha(a)
            crop = spr.crop((0, 0, spr.width, int(iy1 - iy0)))
            paper.alpha_composite(crop, (int((ix0 + ix1) / 2 - crop.width / 2), int(iy0)))
            g = ImageDraw.Draw(paper)
        for k in range(int(iy0), int(ph - 40 * u), int(26 * u)):
            g.line([(pw * .6, k), (pw - 40 * u, k)], fill=(120, 110, 100, 255), width=int(5 * u))
        for k in range(int(iy1 + 30 * u), int(ph - 40 * u), int(26 * u)):
            g.line([(40 * u, k), (pw * .55, k)], fill=(120, 110, 100, 255), width=int(5 * u))
        k = ease_out(clamp(t / .6))
        _paste_center(can, paper, CW / 2, CH / 2, lerp(.15, 1.0, k), 1.0, lerp(360 * 1.5, sc.get("rot", -3), k))

    # ---------------- overlay (after camera; screen space)
    def draw_overlay(self, fr, t):
        sc, W, H = self.sc, self.W, self.H
        u = H / 1080
        if self.type == "black":
            text = sc.get("t", "")
            size = int(sc.get("size", 64) * u)
            f = hfont(text, size, "caveat")
            n = len(text)
            k = clamp(t / max(.4, min(self.dur * .55, .06 * n)))
            shown = text[: int(round(n * k))] if sc.get("type_on", True) else text
            d = ImageDraw.Draw(fr)
            # wrap
            words, lines, cur = shown.split(" "), [], ""
            for w in words:
                tr = (cur + " " + w).strip()
                if d.textlength(tr, font=f) > W * .8 and cur:
                    lines.append(cur)
                    cur = w
                else:
                    cur = tr
            lines.append(cur)
            lh = size * 1.25
            full_lines = max(1, len(lines))
            y0 = H / 2 - lh * full_lines / 2
            left = sc.get("align", "left") == "left"
            for i, l in enumerate(lines):
                if left:
                    d.text((W * sc.get("x", .08), y0 + i * lh + lh / 2), l, font=f, fill=hexc(sc.get("color", "#f4f1ea")), anchor="lm")
                else:
                    d.text((W / 2, y0 + i * lh + lh / 2), l, font=f, fill=hexc(sc.get("color", "#f4f1ea")), anchor="mm")
        # big number / word inside any scene
        bg = sc.get("big")
        if bg:
            if isinstance(bg, str):
                bg = {"t": bg}
            st = bg.get("at", .2)
            if t >= st:
                txt = bg["t"]
                if "count" in bg:
                    v = lerp(float(bg.get("from", 0)), float(bg["count"]), ease_out(clamp((t - st) / max(.5, self.dur * .5))))
                    txt = txt.replace("{n}", _indian(int(round(v))))
                spr = big_text(txt, int(bg.get("size", 120) * u), bg.get("color", "#f1c232"))
                _paste_center(fr, spr, W * bg.get("x", .5), H * bg.get("y", .2), back_out(clamp((t - st) / .35), 2.2))
        lt = sc.get("lower")
        if lt:
            k = ease_out(clamp((t - lt.get("at", .3)) / .35))
            if k > 0:
                spr = lower_third(lt.get("name", ""), lt.get("role", ""), H)
                _paste(fr, spr, lerp(-spr.width, 60 * u, k), H - spr.height - 70 * u)
        cap = sc.get("caption")
        if cap:  # small hand-written note at top (date / place)
            spr = tag(cap, int(40 * u), bg="#1c1f2a", fg="#ffffff", pointer=False)
            _paste(fr, spr, 50 * u, 46 * u)

    def _fg_items(self):
        if self.type != "set":
            return []
        fg = self.sc.get("fg")
        if fg is None:
            fg = motion.AUTO_FG.get(self.sc.get("bg", "study_night"), [])
        return [{"kind": f} if isinstance(f, str) else f for f in fg]

    def _sub(self, side):
        subs = getattr(self, "_subs", None)
        if subs is None:
            subs = self._subs = {}
        if side not in subs:
            b = dict(self.b)
            b["scene"] = self.sc[side]
            b["id"] = self.b.get("id", "x") + side
            b.pop("transition", None)
            subs[side] = ToonShot(b, self.story, self.W // 2, self.H, self.dur, self.env, self.fps)
        return subs[side]

    def frame_core(self, t):
        if self.type == "split":
            fr = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 255))
            fr.paste(self._sub("left").frame_core(t), (0, 0))
            side = "right2" if self.sc.get("right2") and t >= self.sc.get("swap_at", self.dur * .55) else "right"
            rf = self._sub(side).frame_core(t)
            if side == "right2":
                k = ease_out(clamp((t - self.sc.get("swap_at", self.dur * .55)) / .3))
                old = self._sub("right").frame_core(t)
                tmp = Image.new("RGBA", rf.size, (0, 0, 0, 255))
                tmp.paste(old, (0, int(-self.H * k)))
                tmp.paste(rf, (0, int(self.H * (1 - k))))
                rf = tmp
            fr.paste(rf, (self.W // 2, 0))
            ImageDraw.Draw(fr).line([(self.W // 2, 0), (self.W // 2, self.H)], fill=(20, 16, 16, 255), width=max(2, self.H // 270))
            return fr
        z, ox, oy, roll = self.camera(t)
        focus = tuple(self.sc.get("focus", [.5, .5]))
        u = self.u
        if self.type == "set":
            mid = Image.new("RGBA", (self.CW, self.CH), (0, 0, 0, 0))
            self.draw_props(mid, t, "back")
            self.sc["_dur"] = self.dur
            pbfx.draw_board(mid, self.sc, t, u)
            pbfx.draw_days_left(mid, self.sc, t, u)
            pbfx.draw_month_cal(mid, self.sc, t, u)
            self.draw_chars(mid, t)
            pbfx.draw_table(mid, self.sc, t, u)
            self.draw_props(mid, t, "front")
            fr = motion.layer_view(self.base(), self.CW, self.CH, self.W, self.H, z, ox, oy, motion.LAYER_K["bg"], focus)
            fr.alpha_composite(motion.layer_view(mid, self.CW, self.CH, self.W, self.H, z, ox, oy, 1.0, focus))
            if self.sc.get("window"):
                refl, wall = pbfx.window_layers(json.dumps(self.sc["window"], sort_keys=True), self.CW, self.CH)
                fr.alpha_composite(motion.layer_view(refl, self.CW, self.CH, self.W, self.H, z, ox, oy, 1.35, focus))
                fr.alpha_composite(motion.layer_view(wall, self.CW, self.CH, self.W, self.H, z, ox, oy, 1.2, focus))
            items = self._fg_items()
            if items:
                fg = motion.fg_layer(json.dumps(items, sort_keys=True), self.CW, self.CH)
                fr.alpha_composite(motion.layer_view(fg, self.CW, self.CH, self.W, self.H, z, ox, oy, motion.LAYER_K["fg"], focus))
        elif self.type == "set3d":
            fr = Image.new("RGBA", (self.W, self.H), (20, 16, 14, 255))
            if self.sc.get("set") == "map":
                if not hasattr(self, "_mapsub"):
                    pd = float(self.sc.get("map_pad", 1.0))
                    msc = dict(self.sc.get("map", {}), type="map", cam="static")
                    v = msc.get("view", [60, 5, 100, 38])
                    cx, cy, hw, hh = (v[0] + v[2]) / 2, (v[1] + v[3]) / 2, (v[2] - v[0]) / 2 * pd, (v[3] - v[1]) / 2 * pd
                    msc["view"] = [cx - hw, cy - hh, cx + hw, cy + hh]   # bigger map so its edges never enter the frame
                    mb = dict(self.b); mb["scene"] = msc
                    mb.pop("transition", None)
                    self._mapsub = ToonShot(mb, self.story, int(1600 * pd), int(800 * pd), self.dur, self.env, self.fps)
                self.sc["_map_tex"] = self._mapsub.frame_core(t).convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
            labels = set3d.render(fr, self.sc, self.story, t, self.dur, self.env, self.fps, self._spec)
            self.sc["_dur"] = self.dur
            pbfx.draw_board(fr, self.sc, t, self.H / 1080.0)
            pbfx.draw_days_left(fr, self.sc, t, self.H / 1080.0)
            pbfx.draw_month_cal(fr, self.sc, t, self.H / 1080.0)
            for lab, lx, ly, hp in labels:
                tg = tag(lab, int(34 * self.H / 1080.0))
                _paste_center(fr, tg, lx, ly - tg.height * .7, 1.0)
            roll = 0.0
        elif self.type == "topdown":
            can = self.base().copy()
            pbfx.topdown_draw(can, self.sc, t, self.dur, self._spec)
            fr = motion.layer_view(can, self.CW, self.CH, self.W, self.H, z, ox, oy, 1.0, focus)
        else:
            can = self.base().copy()
            self.draw_props(can, t, "back")
            self.draw_type(can, t)
            self.draw_chars(can, t)
            self.draw_props(can, t, "front")
            fr = motion.layer_view(can, self.CW, self.CH, self.W, self.H, z, ox, oy, 1.0, focus)
        fr = motion.roll_img(fr, roll)
        if self.type not in ("black",) and self.sc.get("dust", self.type == "set"):
            motion.draw_dust(fr, t, self.b.get("id", ""))
        self.draw_overlay(fr, t)
        sc = self.sc
        for bb in ([sc["bubble"]] if isinstance(sc.get("bubble"), dict) else sc.get("bubble", [])):
            pbfx.draw_bubble(fr, bb, t)
        for e in sc.get("emph", []):
            pbfx.draw_emph(fr, e, t)
        for e in sc.get("swoosh", []):
            pbfx.draw_swoosh(fr, e, t)
        if sc.get("popup"):
            pbfx.draw_popup(fr, sc["popup"], t)
        if sc.get("names"):
            pbfx.draw_names(fr, sc["names"], t)
        if sc.get("stickers"):
            motion.draw_stickers(fr, sc["stickers"], t, self.dur, SKILL)
        if sc.get("source"):
            docs3d.draw_source(fr, sc["source"], sc.get("source_by", ""), t, sc.get("source_at", .6))
        return fr

    def frame(self, t):
        fr = self.frame_core(t)
        tr = self.b.get("transition", self.sc.get("transition"))
        if tr and tr != "cut":
            T = self.b.get("transition_time", motion.TR_DUR.get(tr, .4))
            if t < T:
                prev = getattr(self, "prev", None)
                if prev is not None:
                    pf = prev.frame_core(prev.dur + t * .5)
                else:
                    pf = Image.new("RGBA", fr.size, (0, 0, 0, 255))
                fr = motion.transition(tr, pf, fr, t / T, tuple(self.b.get("into", [.5, .5])))
        if self.type != "black" and self.b.get("year") is not None:
            import timeline
            pv = getattr(self, "prev", None)
            timeline.draw(fr, self.b, t, self.dur, pv.b if pv is not None else None)
        return fr.convert("RGB")
