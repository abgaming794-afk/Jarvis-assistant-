"""2.5D camera, cross-shot transitions, sticker overlays and foreground depth layers.

Camera (scene "cam"): every shot is built from 3 depth layers that move at different speeds:
  bg (k=0.5) -> mid: characters/props (k=1.0) -> fg: blurred near objects (k=1.8)
  moves: dolly_in, dolly_out, truck_left, truck_right, crane_up, crane_down, orbit_left, orbit_right,
         push_fast, drift, punch, shake, static, auto (picked from the shot id for variety)
Transitions (beat "transition"): cut, whip_left, whip_right, whip_up, zoom_through, push_left, push_right,
         flash, fade, blur, iris, glitch      (+ "into": [x, y] point for zoom_through / iris)
Stickers (scene "stickers"): PNG-style icons with white border + shadow that pop/slide in at the sides and float.
Foreground (scene "fg"): near-camera silhouettes (pillar, curtain, plant, lamp_post, crates, grass, desk_corner,
         crowd, bars, bokeh) — auto-added per set when "fg" is not given.
"""
import math, random, functools, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps
from common import hexc, shade, clamp, ease_out, ease_in_out, back_out, lerp
import props

LAYER_K = {"bg": 0.3, "mid": 1.0, "fg": 1.8}
AUTO_MOVES = ["dolly_in", "truck_right", "dolly_in", "orbit_left", "crane_up", "truck_left", "dolly_out", "orbit_right"]


def ease_in(t):
    t = clamp(t)
    return t * t * t


def camera(cam, t, dur, seed=""):
    """-> (zoom, offset_x, offset_y, roll_degrees) for the mid layer (k = 1)."""
    if cam == "auto":
        cam = AUTO_MOVES[sum(map(ord, seed)) % len(AUTO_MOVES)]
    lin = clamp(t / max(.1, dur))
    p = 1 - (1 - lin) ** 2.2          # ease-out: moving at the cut, settling at the end (hides cuts)
    z, ox, oy, roll = 1.0, 0.0, 0.0, 0.0
    if cam in ("in", "dolly_in"):
        z = lerp(1.0, 1.12, p)
    elif cam in ("out", "dolly_out"):
        z = lerp(1.12, 1.0, p)
    elif cam in ("right", "truck_right"):
        z, ox = 1.08, lerp(-.05, .05, p)
    elif cam in ("left", "truck_left"):
        z, ox = 1.08, lerp(.05, -.05, p)
    elif cam in ("up", "crane_up"):
        z, oy = 1.08, lerp(.045, -.045, p)
    elif cam in ("down", "crane_down"):
        z, oy = 1.08, lerp(-.045, .045, p)
    elif cam == "orbit_left":
        z, ox, roll = lerp(1.05, 1.11, p), lerp(.05, -.05, p), lerp(-1.4, 1.4, p)
    elif cam == "orbit_right":
        z, ox, roll = lerp(1.05, 1.11, p), lerp(-.05, .05, p), lerp(1.4, -1.4, p)
    elif cam == "push_fast":
        z = 1.0 + .18 * ease_out(lin)
    elif cam == "table_roll":
        z, roll = lerp(1.04, 1.12, p), lerp(-3.0, 3.0, lin)
    elif cam == "drift":
        z = 1.05
    elif cam == "punch":
        z = 1.0 + .09 * ease_out(t / .3)
    elif cam == "shake":
        z = 1.06
        k = 1 - clamp(t / .7)
        r = random.Random(int(t * 30))
        ox, oy = (r.random() - .5) * .016 * k, (r.random() - .5) * .016 * k
    if cam != "static":   # never fully still: slow hand-held drift
        ox += .004 * math.sin(t * .9 + 1.3)
        oy += .003 * math.sin(t * 1.3 + .4)
        z += .006 * math.sin(t * .7)
    return z, ox, oy, roll


def layer_view(img, CW, CH, W, H, z, ox, oy, k, focus=(.5, .5)):
    """Crop/resize one depth layer for camera (z, ox, oy) scaled by depth factor k."""
    zk = max(.2, 1 + (z - 1) * k)
    cw, ch = CW / zk, CH / zk
    fx, fy = focus
    cx = CW / 2 + (ox * k + (fx - .5) * (zk - 1) * 1.6) * CW
    cy = CH / 2 + (oy * k + (fy - .5) * (zk - 1) * 1.6) * CH
    x0 = clamp(cx - cw / 2, 0, CW - cw)
    y0 = clamp(cy - ch / 2, 0, CH - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def roll_img(img, deg):
    if abs(deg) < .05:
        return img
    W, H = img.size
    s = 1 + abs(math.sin(math.radians(deg))) * 1.9
    big = img.resize((int(W * s), int(H * s)), Image.BILINEAR).rotate(deg, resample=Image.BILINEAR)
    l, t = (big.width - W) // 2, (big.height - H) // 2
    return big.crop((l, t, l + W, t + H))


# ------------------------------------------------------------------ transitions
TR_DUR = {"flow": .42, "whip_left": .34, "whip_right": .34, "whip_up": .34, "whip": .34, "zoom_through": .55, "push_left": .45,
          "push_right": .45, "flash": .35, "fade": .5, "blur": .45, "iris": .5, "glitch": .28}


def _hblur(img, amt):
    if amt < 1.5:
        return img
    W, H = img.size
    return img.resize((max(4, int(W / amt)), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)


def _vblur(img, amt):
    if amt < 1.5:
        return img
    W, H = img.size
    return img.resize((W, max(4, int(H / amt))), Image.BILINEAR).resize((W, H), Image.BILINEAR)


def _shift(img, dx, dy):
    return img.transform(img.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR,
                         fillcolor=(0, 0, 0, 255))


def _zoom_at(img, s, pt):
    W, H = img.size
    px, py = pt[0] * W, pt[1] * H
    cw, ch = W / s, H / s
    x0, y0 = clamp(px - cw * pt[0], 0, W - cw), clamp(py - ch * pt[1], 0, H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def transition(kind, prev, new, p, into=(.5, .5)):
    """Blend prev (end of last shot) into new (start of this shot); p goes 0 -> 1."""
    W, H = new.size
    if kind in ("whip", "whip_left", "whip_right", "whip_up"):
        dirx = -1 if kind in ("whip_left",) else 1
        if kind == "whip_up":
            if p < .5:
                k = ease_in(p * 2)
                return _vblur(_shift(prev, 0, -H * .6 * k), 1 + 30 * k)
            k = 1 - ease_out((p - .5) * 2)
            return _vblur(_shift(new, 0, H * .6 * k), 1 + 30 * k)
        if p < .5:
            k = ease_in(p * 2)
            return _hblur(_shift(prev, -dirx * W * .6 * k, 0), 1 + 40 * k)
        k = 1 - ease_out((p - .5) * 2)
        return _hblur(_shift(new, dirx * W * .6 * k, 0), 1 + 40 * k)
    if kind == "flow":
        k = ease_in_out(p)
        b = 1 - abs(2 * p - 1)
        a = _zoom_at(prev, 1 + .22 * k, into)
        n = _zoom_at(new, 1.16 - .16 * k, (.5, .5))
        out = Image.blend(a, n, k)
        return out.filter(ImageFilter.GaussianBlur(b * W / 170)) if b > .08 else out
    if kind == "zoom_through":
        if p < .5:
            k = ease_in(p * 2)
            a = _zoom_at(prev, 1 + 3.5 * k, into)
            return a.filter(ImageFilter.GaussianBlur(k * W / 150))
        k = 1 - ease_out((p - .5) * 2)
        b = _zoom_at(new, 1 + .8 * k, (.5, .5))
        return b.filter(ImageFilter.GaussianBlur(k * W / 220)) if k > .05 else b
    if kind in ("push_left", "push_right"):
        k = ease_in_out(p)
        d = -1 if kind == "push_left" else 1
        out = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        out.paste(prev, (int(-d * W * k), 0))
        out.paste(new, (int(d * W * (1 - k)), 0))
        return out
    if kind == "flash":
        if p < .3:
            return Image.blend(prev, Image.new("RGBA", (W, H), (255, 255, 255, 255)), p / .3)
        return Image.blend(Image.new("RGBA", (W, H), (255, 255, 255, 255)), new, ease_out((p - .3) / .7))
    if kind == "fade":
        if p < .5:
            return Image.blend(prev, Image.new("RGBA", (W, H), (0, 0, 0, 255)), p * 2)
        return Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), new, (p - .5) * 2)
    if kind == "blur":
        k = 1 - abs(2 * p - 1)
        a = Image.blend(prev, new, ease_in_out(p))
        return a.filter(ImageFilter.GaussianBlur(k * W / 90))
    if kind == "iris":
        mask = Image.new("L", (W, H), 0)
        r = ease_in_out(p) * math.hypot(W, H)
        cx, cy = into[0] * W, into[1] * H
        ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        out = prev.copy()
        out.paste(new, (0, 0), mask)
        return out
    if kind == "glitch":
        src = prev if p < .5 else new
        r, g, b, a = src.split()
        off = int(W * .02 * (1 - abs(2 * p - 1)) + 2)
        r = ImageChops.offset(r, off, 0)
        b = ImageChops.offset(b, -off, 0)
        out = Image.merge("RGBA", (r, g, b, a))
        rnd = random.Random(int(p * 100))
        for _ in range(4):
            y = rnd.randint(0, H - 10)
            h = rnd.randint(4, max(5, H // 14))
            band = out.crop((0, y, W, y + h))
            out.paste(band, (rnd.randint(-W // 12, W // 12), y))
        return out
    return new


# ------------------------------------------------------------------ stickers
@functools.lru_cache(maxsize=256)
def sticker(name, h, color=None, border=True, path=None):
    if path:
        spr = Image.open(path).convert("RGBA")
        spr = spr.resize((max(1, int(spr.width * h / spr.height)), int(h)), Image.LANCZOS)
    else:
        spr = props.make(name, int(h), color)
    if not border:
        base = spr
    else:
        pad = max(4, int(h * .07))
        base = Image.new("RGBA", (spr.width + pad * 2, spr.height + pad * 2), (0, 0, 0, 0))
        base.alpha_composite(spr, (pad, pad))
        a = base.getchannel("A").point(lambda v: 255 if v > 40 else 0)
        a = a.filter(ImageFilter.MaxFilter(((pad * 2) // 2) * 2 + 1))
        white = Image.new("RGBA", base.size, (255, 255, 255, 255))
        white.putalpha(a)
        white.alpha_composite(base)
        base = white
    pad = max(10, int(h * .12))
    sh = Image.new("RGBA", (base.width + pad * 3, base.height + pad * 3), (0, 0, 0, 0))
    shadow = Image.new("RGBA", base.size, (8, 6, 12, 255))
    shadow.putalpha(base.getchannel("A").point(lambda v: v * 95 // 255))
    sh.alpha_composite(shadow, (pad + int(h * .03), pad + int(h * .06)))
    sh = sh.filter(ImageFilter.GaussianBlur(max(2, h * .05)))
    sh.alpha_composite(base, (pad, pad))
    # subtle top-left rim light so cut-outs read as real objects, not stickers
    rim = Image.new("RGBA", base.size, (255, 248, 230, 0))
    a = base.getchannel("A")
    edge = ImageChops.subtract(a, ImageChops.offset(a, int(max(1, h * .015)), int(max(1, h * .015))))
    rim.putalpha(edge.point(lambda v: v * 70 // 255))
    sh.alpha_composite(rim, (pad, pad))
    return sh


SIDE_POS = {"left": (.12, .5), "right": (.88, .5), "top_left": (.13, .22), "top_right": (.87, .22),
            "bottom_left": (.13, .78), "bottom_right": (.87, .78), "top": (.5, .16), "bottom": (.5, .84),
            "center": (.5, .5)}


def draw_stickers(fr, items, t, dur, skill_dir=""):
    W, H = fr.size
    for i, s in enumerate(items):
        at = s.get("at", .25 + .2 * i)
        out_at = s.get("out", None)
        if t < at:
            continue
        te = t - at
        h = int(H * s.get("h", .2))
        path = None
        if s.get("img"):
            path = s["img"] if os.path.isabs(s["img"]) else os.path.join(skill_dir, s["img"])
        spr = sticker(s.get("name", "coin"), h, s.get("color"), s.get("border", False), path)
        if s.get("side") in SIDE_POS:
            x, y = SIDE_POS[s["side"]]
        else:
            x, y = s.get("x", .85), s.get("y", .5)
        x, y = x * W, y * H
        anim = s.get("anim", "pop")
        scale, rot, alpha = 1.0, s.get("rot", (-6 if x > W / 2 else 6)), 1.0
        if anim == "pop":
            scale = back_out(clamp(te / .35), 2.6)
        elif anim == "slide":
            from_right = x > W / 2
            x = lerp(W + spr.width if from_right else -spr.width, x, back_out(clamp(te / .45), 1.3))
        elif anim == "drop":
            y = lerp(-spr.height, y, back_out(clamp(te / .5), 1.6))
        elif anim == "spin":
            scale = back_out(clamp(te / .45), 2)
            rot += (1 - ease_out(clamp(te / .45))) * 360
        elif anim == "rain":
            r = random.Random(i * 7 + 3)
            for k in range(s.get("count", 14)):
                xx = r.uniform(0, W)
                sp = r.uniform(.35, .6)
                yy = ((te * sp + r.random()) % 1.25 - .15) * H
                small = sticker(s.get("name", "coin"), int(h * r.uniform(.4, .7)), s.get("color"), False, path)
                small = small.rotate((te * 160 + k * 37) % 360, expand=True, resample=Image.BILINEAR)
                fr.alpha_composite(small, (int(xx - small.width / 2), int(yy - small.height / 2)))
            continue
        # idle float + wiggle
        y += math.sin(te * 2.4 + i) * H * .012
        rot += math.sin(te * 1.9 + i * 2) * 3
        if s.get("pulse"):
            scale *= 1 + .05 * math.sin(te * 6)
        if out_at is not None and t > out_at:
            k = clamp((t - out_at) / .3)
            scale *= 1 - ease_in(k)
        if scale <= .02:
            continue
        img = spr
        if abs(scale - 1) > .01:
            img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
        if abs(rot) > .3:
            img = img.rotate(rot, expand=True, resample=Image.BILINEAR)
        fr.alpha_composite(img, (int(x - img.width / 2), int(y - img.height / 2)))
        if s.get("label"):
            from toonshot import tag
            tg = tag(s["label"], int(H * .035), bg="#1c1f2a", fg="#ffffff", pointer=False)
            fr.alpha_composite(tg, (int(x - tg.width / 2), int(y + img.height / 2 - tg.height * .2)))


# ------------------------------------------------------------------ foreground depth layer
AUTO_FG = {
    "study_night": [{"kind": "desk_corner", "x": .02}, {"kind": "plant", "x": .95}],
    "office_day": [{"kind": "plant", "x": .03}],
    "palace_room": [{"kind": "curtain", "x": 0.0}, {"kind": "curtain", "x": 1.0}],
    "mughal_court": [{"kind": "pillar", "x": .02}, {"kind": "pillar", "x": .98}],
    "company_hall": [{"kind": "pillar", "x": .03}, {"kind": "crowd", "x": .5}],
    "london_street": [{"kind": "lamp_post", "x": .04}],
    "bazaar": [{"kind": "crates", "x": .05}, {"kind": "crates", "x": .95}],
    "port": [{"kind": "crates", "x": .95}],
    "battlefield": [{"kind": "grass", "x": .5}, {"kind": "bokeh", "x": .5}],
    "war_tent": [{"kind": "bokeh", "x": .5}, {"kind": "desk_corner", "x": .97}],
    "village": [{"kind": "grass", "x": .5}],
    "fort": [{"kind": "grass", "x": .5}],
    "prison": [{"kind": "bars", "x": .5}],
    "parliament": [{"kind": "crowd", "x": .5}],
    "senate": [{"kind": "crowd", "x": .5}],
    "hallway": [{"kind": "bokeh", "x": .5}],
}


@functools.lru_cache(maxsize=48)
def fg_layer(spec_key, CW, CH):
    import json
    items = json.loads(spec_key)
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    dark = (16, 12, 12, 255)
    for it in items:
        kind, x = it.get("kind"), it.get("x", .5) * CW
        r = random.Random(kind + str(it.get("x")))
        if kind == "pillar":
            d.rectangle([x - CW * .06, -10, x + CW * .06, CH + 10], fill=(46, 30, 22, 255))
            d.rectangle([x - CW * .045, -10, x - CW * .03, CH + 10], fill=(70, 48, 34, 255))
        elif kind == "curtain":
            for k in range(5):
                xx = x + (k * CW * .025 if x < CW / 2 else -k * CW * .025)
                d.rectangle([xx - CW * .02, -10, xx + CW * .02, CH + 10], fill=(90 - k * 6, 14, 18, 255))
        elif kind == "plant":
            for a in range(-70, 71, 20):
                ang = math.radians(a - 90)
                ex, ey = x + math.cos(ang) * CH * .5, CH * 1.02 + math.sin(ang) * CH * .5
                d.polygon([(x, CH * 1.02), (ex - CW * .02, ey), (ex + CW * .02, ey)], fill=(20, 40, 26, 255))
        elif kind == "lamp_post":
            d.rectangle([x - CW * .012, -10, x + CW * .012, CH + 10], fill=dark)
            d.ellipse([x - CW * .03, CH * .08, x + CW * .03, CH * .16], fill=(255, 214, 140, 255))
        elif kind == "crates":
            for k in range(2):
                yy = CH * (.78 - k * .22)
                d.rectangle([x - CW * .09, yy, x + CW * .09, yy + CH * .24], fill=(60, 38, 22, 255), outline=(30, 18, 10, 255), width=6)
        elif kind == "grass":
            for _ in range(70):
                gx = r.uniform(0, CW)
                gh = r.uniform(.06, .16) * CH
                d.polygon([(gx - CW * .006, CH + 5), (gx + r.uniform(-20, 20), CH - gh), (gx + CW * .006, CH + 5)], fill=(30, 26, 14, 255))
        elif kind == "desk_corner":
            if x < CW / 2:
                d.polygon([(-10, CH * .82), (CW * .2, CH * .9), (CW * .16, CH + 10), (-10, CH + 10)], fill=(34, 22, 16, 255))
            else:
                d.polygon([(CW + 10, CH * .82), (CW * .8, CH * .9), (CW * .84, CH + 10), (CW + 10, CH + 10)], fill=(34, 22, 16, 255))
        elif kind == "crowd":
            for k in range(14):
                hx = (k + .5) * CW / 14 + r.uniform(-20, 20)
                hr = CH * r.uniform(.07, .09)
                hy = CH * 1.0 + r.uniform(-.02, .03) * CH
                d.ellipse([hx - hr, hy - hr * 2.2, hx + hr, hy - .2 * hr], fill=(20, 16, 18, 255))
                d.rounded_rectangle([hx - hr * 1.5, hy - hr * .6, hx + hr * 1.5, hy + hr * 2], radius=hr, fill=(20, 16, 18, 255))
        elif kind == "bars":
            for k in range(7):
                bx = (k + .5) * CW / 7
                d.rectangle([bx - CW * .008, -10, bx + CW * .008, CH + 10], fill=(24, 24, 28, 255))
        elif kind == "bokeh":
            for _ in range(10):
                bx, by, br = r.uniform(0, CW), r.uniform(.7, 1.0) * CH, r.uniform(.012, .03) * CW
                d.ellipse([bx - br, by - br, bx + br, by + br], fill=(255, 190, 110, 45))
    return img.filter(ImageFilter.GaussianBlur(CW / 260))


def draw_dust(fr, t, seed=""):
    """Tiny motes drifting through the light - keeps every frame alive."""
    W, H = fr.size
    r = random.Random(seed)
    d = ImageDraw.Draw(fr)
    for k in range(18):
        x0, y0, sp = r.random(), r.random(), r.uniform(.006, .02)
        x = ((x0 + t * sp) % 1.0) * W
        y = ((y0 - t * sp * .6 + .05 * math.sin(t + k)) % 1.0) * H
        rr = max(1, H / 540 * r.uniform(.8, 1.8))
        a = int(70 + 60 * math.sin(t * 2 + k))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 240, 200, max(0, a)))


AUTO_TR = ["whip_right", "zoom_through", "whip_left", "blur", "push_left", "zoom_through", "whip_up"]


def auto_transitions(story):
    """Give every beat without a transition a seamless one (same set -> cut on matching motion)."""
    if not story.get("auto_transitions", True):
        return story
    beats = story["beats"]
    j = 0
    for i, b in enumerate(beats):
        if "transition" in b or i == 0:
            continue
        sc, pv = b.get("scene", {}), beats[i - 1].get("scene", {})
        typ, ptyp = sc.get("type", "set"), pv.get("type", "set")
        pcam = pv.get("cam", "")
        if typ == "black" or ptyp == "black":
            b["transition"] = "fade"
            b.setdefault("transition_time", .3)
        elif ptyp == "set3d" and pcam in ("dolly_in", "push", "fly"):
            b["transition"] = "zoom_through"
        elif ptyp == "set3d" and pcam in ("truck_right", "orbit_right"):
            b["transition"] = "whip_right"
        elif ptyp == "set3d" and pcam in ("truck_left", "orbit_left"):
            b["transition"] = "whip_left"
        elif typ == ptyp == "set" and sc.get("bg") == pv.get("bg"):
            b["transition"] = "cut"
        else:
            b["transition"] = "flow"
            j += 1
    return story
