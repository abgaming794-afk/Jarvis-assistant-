"""Documentary-toon storytelling devices (studied from reference frames):

  window      look into a room through a shop window: mirrored street reflection on the glass, wall + sill +
              mullions in front (each its own parallax depth)
  table       a table drawn IN FRONT of seated characters (cups with steam, bottles, napkin box)
  board       banner / whiteboard inside the scene where a line is hand-written letter by letter ([red] words)
  days_left   tear-off "DAYS LEFT" calendar with a number that gets a red marker circle
  month_cal   wall calendar whose days get crossed with red X one by one (time passing)
  bubble      thought bubble (small circles -> cloud) holding a prop or short text
  emph        comic emphasis tick-lines radiating around a point
  swoosh      motion arcs behind a moving arm/body
  steam       rising wavy steam lines
  popup       a prop rising into frame from the bottom edge, close to camera (order pad, menu card, letter)
  names       name tags: dark box + coloured side bar, white hand-written name typed on
  topdown     (scene type) table seen from above: cups, people's heads at the edges, hands that slide in holding
              money and let go, "$200" labels, piles merging into a total, a pen drawing on paper
  split       (scene type) two scenes side by side for a comparison; the right side can swap at a time
"""
import math, random, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from common import hexc, shade, clamp, ease_out, ease_in_out, back_out, lerp, font
import props

INK = (28, 22, 22, 255)


def _hand(size, dev=False):
    from toonshot import hand
    return hand(size, "kalam" if dev else "caveat")


def _marker(size):
    from toonshot import hand
    return hand(size, "marker")


def _parse(s):
    import re
    out, pos = [], 0
    for m in re.finditer(r"\[([^\]]+)\]", s):
        if m.start() > pos:
            out.append((s[pos:m.start()], False))
        out.append((m.group(1), True))
        pos = m.end()
    if pos < len(s):
        out.append((s[pos:], False))
    return out


# ------------------------------------------------------------------ window
@functools.lru_cache(maxsize=16)
def window_layers(key, CW, CH):
    import json
    w = json.loads(key)
    x0, y0, x1, y1 = [v * (CW if i % 2 == 0 else CH) for i, v in enumerate(w.get("rect", [.04, .06, .88, .70]))]
    u = CH / 1080
    # ---- reflection (mirrored street) on the glass
    refl = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(refl)
    r = random.Random(4)
    bx = x0
    while bx < x1:
        bw = r.uniform(.07, .14) * CW
        top = y0 + r.uniform(.12, .35) * (y1 - y0)
        d.rectangle([bx, top, bx + bw, y1], fill=(22, 28, 66, 70))
        for wy in np.arange(top + 30 * u, y1 - 20 * u, 70 * u):
            for wx in np.arange(bx + 18 * u, bx + bw - 30 * u, 60 * u):
                if r.random() < .38:
                    d.rectangle([wx, wy, wx + 28 * u, wy + 22 * u], fill=(250, 214, 140, 110))
        bx += bw + r.uniform(4, 30) * u
    sign = w.get("sign")
    if sign:
        f = _marker(int(64 * u))
        txt = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        g = ImageDraw.Draw(txt)
        sx, sy = x0 + (x1 - x0) * w.get("sign_x", .2), y0 + (y1 - y0) * .16
        g.text((sx, sy), sign, font=f, fill=hexc(w.get("sign_color", "#ff4f7a")), anchor="mm")
        glow = txt.filter(ImageFilter.GaussianBlur(10 * u))
        txt = ImageOps.mirror(txt)
        glow = ImageOps.mirror(glow)
        refl.alpha_composite(glow)
        refl.alpha_composite(txt)
    st = w.get("street") or []
    if st:
        f = _hand(int(40 * u))
        sx, sy = x0 + (x1 - x0) * w.get("street_x", .72), y0 + (y1 - y0) * .2
        lay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        g = ImageDraw.Draw(lay)
        g.ellipse([sx - 200 * u, sy - 70 * u, sx + 200 * u, sy + 70 * u + 55 * u * (len(st) - 1)], fill=(150, 220, 170, 60))
        for i, t in enumerate(st):
            yy = sy + i * 58 * u
            g.rectangle([sx - 160 * u, yy - 24 * u, sx + 160 * u, yy + 24 * u], fill=(36, 140, 70, 220),
                        outline=(220, 240, 220, 230), width=max(1, int(3 * u)))
            g.text((sx, yy), t, font=f, fill=(230, 245, 230, 240), anchor="mm")
        refl.alpha_composite(ImageOps.mirror(lay) if w.get("mirror_street", True) else lay)
    mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(mask).rectangle([x0, y0, x1, y1], fill=int(255 * w.get("glass", .55)))
    a = refl.getchannel("A")
    refl.putalpha(Image.fromarray((np.asarray(a, np.float32) * np.asarray(mask, np.float32) / 255).astype(np.uint8)))
    # ---- wall + frame in front
    wall = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    wc = np.array(hexc(w.get("wall", "#2f6b74"))[:3], np.float32)
    ys = np.linspace(0, 1, CH)[:, None, None]
    arr = (wc * (1.18 - .35 * ys)).clip(0, 255).repeat(CW, 1)
    wall = Image.fromarray(np.dstack([arr.astype(np.uint8), np.full((CH, CW, 1), 255, np.uint8)]), "RGBA")
    g = ImageDraw.Draw(wall)
    g.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 0))
    lw = max(2, int(5 * u))
    g.rectangle([x0, y0, x1, y1], outline=INK, width=lw)
    for m in w.get("mullions", [.33, .58]):
        mx = x0 + (x1 - x0) * m
        g.line([(mx, y0), (mx, y1)], fill=INK, width=max(1, int(3 * u)))
        g.line([(mx, y1 + 30 * u), (mx, CH)], fill=INK, width=max(1, int(3 * u)))
    g.rectangle([0, y1, CW, y1 + 24 * u], fill=hexc(shade(w.get("wall", "#2f6b74"), 1.6)), outline=INK, width=max(1, int(3 * u)))
    if w.get("lamp_spill", True):
        glow = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([CW * .3, -CH * .25, CW * .7, CH * .2], fill=(180, 255, 230, 60))
        wall.alpha_composite(glow.filter(ImageFilter.GaussianBlur(CW / 30)))
        ImageDraw.Draw(wall).rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 0))
        ImageDraw.Draw(wall).rectangle([x0, y0, x1, y1], outline=INK, width=lw)
    return refl, wall


# ------------------------------------------------------------------ in-scene elements (mid layer)
def cup(d, x, y, s, t=0.0, steam=True):
    d.rounded_rectangle([x - 22 * s, y - 34 * s, x + 22 * s, y], radius=6 * s, fill=(246, 244, 236, 255), outline=INK, width=max(1, int(3 * s)))
    d.ellipse([x - 22 * s, y - 40 * s, x + 22 * s, y - 28 * s], fill=(90, 50, 30, 255), outline=INK, width=max(1, int(2 * s)))
    d.arc([x + 14 * s, y - 28 * s, x + 36 * s, y - 8 * s], 270, 90, fill=INK, width=max(1, int(3 * s)))
    d.ellipse([x - 32 * s, y - 6 * s, x + 32 * s, y + 6 * s], fill=(240, 238, 230, 255), outline=INK, width=max(1, int(2 * s)))
    if steam:
        for k in (-8, 8):
            pts = [(x + k * s + math.sin((t * 3 + j * .35)) * 5 * s, y - 46 * s - j * 7 * s) for j in range(8)]
            d.line(pts, fill=(235, 235, 235, 170), width=max(1, int(2 * s)))


def draw_table(can, sc, t, u):
    tb = sc.get("table")
    if not tb:
        return
    CW, CH = can.size
    d = ImageDraw.Draw(can)
    x0, x1, y = tb.get("x0", .33) * CW, tb.get("x1", .62) * CW, tb.get("y", .62) * CH
    th = 26 * u
    lit = tb.get("color", "#f3ecd6")
    d.rectangle([(x0 + x1) / 2 - 9 * u, y + th, (x0 + x1) / 2 + 9 * u, CH * tb.get("pole_to", .92)], fill=(90, 92, 100, 255), outline=INK, width=max(1, int(3 * u)))
    for it in tb.get("items", ["cup", "bottle", "cup", "cup"]):
        pass
    items = tb.get("items", ["cup", "bottle", "cup", "cup"])
    n = len(items)
    for i, it in enumerate(items):
        x = lerp(x0 + 50 * u, x1 - 50 * u, i / max(1, n - 1))
        if it == "cup":
            cup(d, x, y + 2 * u, 1.0 * u * 1.1, t + i, tb.get("steam", True))
        elif it in ("bottle", "ketchup"):
            col = (214, 40, 40, 255) if it == "ketchup" else (240, 240, 236, 255)
            d.rounded_rectangle([x - 12 * u, y - 52 * u, x + 12 * u, y], radius=5 * u, fill=col, outline=INK, width=max(1, int(3 * u)))
        elif it == "box":
            d.rectangle([x - 40 * u, y - 44 * u, x + 40 * u, y], fill=(246, 244, 236, 255), outline=INK, width=max(1, int(3 * u)))
        else:
            spr = props.make(it, int(70 * u))
            can.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height)))
            d = ImageDraw.Draw(can)
    d.rounded_rectangle([x0, y, x1, y + th], radius=8 * u, fill=hexc(lit), outline=INK, width=max(1, int(4 * u)))
    glow = Image.new("RGBA", can.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([x0 - 40 * u, y - 120 * u, x1 + 40 * u, y + 60 * u], fill=(255, 240, 190, 60))
    can.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30 * u)))


def draw_board(can, sc, t, u):
    """Premium dialogue card: dark glass, gold bar + border, Playfair Display, [highlight] words in gold."""
    b = sc.get("board")
    if not b:
        return
    CW, CH = can.size
    x0, y0, x1, y1 = b.get("rect", [0, .02, .6, .17])
    x0, x1, y0, y1 = x0 * CW, x1 * CW, y0 * CH, y1 * CH
    k_in = ease_out(clamp((t - b.get("at", .2) + .15) / .3))
    if k_in <= 0:
        return
    lines = b["text"].split("|")
    import re
    dev = bool(re.search(r"[ऀ-ॿ]", b["text"]))
    size = int(b.get("size", 46) * u)
    f = _hand(size, dev)
    lh = size * 1.3
    tmp = ImageDraw.Draw(can)
    tw = max(tmp.textlength(l.replace("[", "").replace("]", ""), font=f) for l in lines)
    pad = 30 * u
    w = tw + pad * 2 + 14 * u
    h = lh * len(lines) + pad * 1.4
    spk = sc.get("_speaker")
    if spk:   # keep the card off the speaker's face: try 3 slots, take the least overlap
        fx0, fy0, fx1, fy1 = spk
        fy1 = fy0 + (fy1 - fy0) * 0.45
        slots = [(0.04 * CW, 0.12 * CH), (0.96 * CW - w, 0.12 * CH), ((CW - w) / 2, 0.68 * CH)]
        if (fx0 + fx1) / 2 < CW / 2:
            slots[0], slots[1] = slots[1], slots[0]
        def ov(s):
            ax0, ay0, ax1, ay1 = s[0], s[1], s[0] + w, s[1] + h
            return max(0, min(ax1, fx1) - max(ax0, fx0)) * max(0, min(ay1, fy1) - max(ay0, fy0))
        x0, y0 = min(slots, key=ov)
    card = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    g = ImageDraw.Draw(card)
    g.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(16 * u), fill=(16, 13, 12, 226), outline=(214, 178, 96, 255), width=max(1, int(2 * u)))
    g.rectangle([int(8 * u), int(12 * u), int(14 * u), int(h - 12 * u)], fill=(214, 178, 96, 255))
    total = sum(len(l.replace("[", "").replace("]", "")) for l in lines)
    k = clamp((t - b.get("at", .2)) / max(.3, b.get("time", 2.2)))
    shown = int(total * k)
    for li, line in enumerate(lines):
        x = pad + 14 * u
        y = pad * .7 + li * lh + lh / 2
        for seg, hi in _parse(line):
            if shown <= 0:
                break
            part = seg[:shown]
            shown -= len(seg)
            g.text((x, y), part, font=f, fill=(241, 194, 50, 255) if hi else (246, 238, 220, 255), anchor="lm")
            x += g.textlength(seg, font=f)
    if x0 + w > CW - 10 * u:
        x0 = CW - 10 * u - w
    can.alpha_composite(card, (int(x0), int(y0 - (1 - k_in) * 20 * u)))


def draw_days_left(can, sc, t, u):
    c = sc.get("days_left")
    if not c:
        return
    CW, CH = can.size
    x, y, w = c.get("x", .4) * CW, c.get("y", .3) * CH, c.get("w", .1) * CW
    h = w * 1.15
    d = ImageDraw.Draw(can)
    d.rectangle([x - w / 2, y, x + w / 2, y + h], fill=(242, 240, 234, 255), outline=INK, width=max(1, int(4 * u)))
    d.rectangle([x - w / 2, y, x + w / 2, y + h * .22], fill=(206, 40, 40, 255), outline=INK, width=max(1, int(4 * u)))
    d.rectangle([x - w * .2, y - 10 * u, x + w * .2, y + 4 * u], fill=(90, 90, 96, 255), outline=INK, width=max(1, int(2 * u)))
    d.text((x, y + h * .11), c.get("title", "DAYS LEFT"), font=_hand(int(w * .14), False), fill=(255, 255, 255, 255), anchor="mm")
    d.text((x, y + h * .6), str(c.get("n", 30)), font=_marker(int(w * .34)), fill=INK, anchor="mm")
    k = ease_in_out(clamp((t - c.get("circle_at", 1.0)) / .6))
    if k > 0:
        cx, cy, rr = x, y + h * .6, w * .32
        pts = [(cx + math.cos(a) * rr, cy + math.sin(a) * rr * .92) for a in np.linspace(-2.2, -2.2 + 2 * math.pi * 1.04 * k, 50)]
        d.line(pts, fill=(214, 40, 40, 255), width=max(2, int(7 * u)), joint="curve")


def draw_month_cal(can, sc, t, u):
    c = sc.get("month_cal")
    if not c:
        return
    CW, CH = can.size
    x0, y0, w = c.get("x", .06) * CW, c.get("y", .2) * CH, c.get("w", .16) * CW
    h = w * 1.25
    d = ImageDraw.Draw(can)
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(236, 234, 230, 255), outline=INK, width=max(1, int(4 * u)))
    d.rectangle([x0, y0, x0 + w, y0 + h * .28], fill=(26, 40, 36, 255), outline=INK, width=max(1, int(3 * u)))
    if c.get("icon"):
        spr = props.make(c["icon"], int(h * .2))
        can.alpha_composite(spr, (int(x0 + w / 2 - spr.width / 2), int(y0 + h * .04)))
        d = ImageDraw.Draw(can)
    d.text((x0 + w / 2, y0 + h * .35), c.get("title", "JUL 1997"), font=_hand(int(w * .13)), fill=(196, 40, 60, 255), anchor="mm")
    rows, cols = 5, 5
    k = clamp((t - c.get("at", .3)) / max(.5, c.get("time", self_dur(sc))))
    nx = int(rows * cols * k * c.get("upto", 1.0))
    for i in range(rows * cols):
        cx = x0 + w * (.12 + (i % cols) * .19)
        cy = y0 + h * (.46 + (i // cols) * .1)
        d.rectangle([cx - w * .07, cy - h * .035, cx + w * .07, cy + h * .035], outline=(170, 170, 176, 255), width=1)
        if i < nx:
            d.line([(cx - w * .06, cy - h * .03), (cx + w * .06, cy + h * .03)], fill=(214, 50, 60, 255), width=max(1, int(3 * u)))
            d.line([(cx + w * .06, cy - h * .03), (cx - w * .06, cy + h * .03)], fill=(214, 50, 60, 255), width=max(1, int(3 * u)))


def self_dur(sc):
    return sc.get("_dur", 3.0)


# ------------------------------------------------------------------ comic devices (screen space)
def draw_bubble(fr, b, t):
    W, H = fr.size
    u = H / 1080
    at = b.get("at", .3)
    if t < at:
        return
    k = clamp((t - at) / .5)
    out = b.get("out")
    if out is not None and t > out:
        k = 1 - clamp((t - out) / .35)
    fx, fy = b.get("from", [.4, .45])
    cx, cy = b.get("x", fx + .08) * W, b.get("y", fy - .2) * H
    d = ImageDraw.Draw(fr)
    for i, (px, py, rr) in enumerate([(fx * W + 14 * u, fy * H - 10 * u, 8), (fx * W + 34 * u, fy * H - 40 * u, 13)]):
        if k > .15 * (i + 1):
            d.ellipse([px - rr * u, py - rr * u, px + rr * u, py + rr * u], fill=(245, 245, 245, 255), outline=INK, width=max(1, int(3 * u)))
    if k > .4:
        s = back_out(clamp((k - .4) / .6), 2)
        rw, rh = b.get("w", .17) * W * s, b.get("h", .12) * H * s
        cloud = Image.new("RGBA", fr.size, (0, 0, 0, 0))
        g = ImageDraw.Draw(cloud)
        for j in range(9):
            a = j / 9 * 2 * math.pi
            g.ellipse([cx + math.cos(a) * rw * .7 - rh * .5, cy + math.sin(a) * rh * .55 - rh * .5,
                       cx + math.cos(a) * rw * .7 + rh * .5, cy + math.sin(a) * rh * .55 + rh * .5], fill=INK)
        cloud = cloud.filter(ImageFilter.MaxFilter(3))
        fr.alpha_composite(cloud)
        g = ImageDraw.Draw(fr)
        for j in range(9):
            a = j / 9 * 2 * math.pi
            g.ellipse([cx + math.cos(a) * rw * .7 - rh * .46, cy + math.sin(a) * rh * .55 - rh * .46,
                       cx + math.cos(a) * rw * .7 + rh * .46, cy + math.sin(a) * rh * .55 + rh * .46], fill=(245, 245, 245, 255))
        g.ellipse([cx - rw * .8, cy - rh * .6, cx + rw * .8, cy + rh * .6], fill=(245, 245, 245, 255))
        if b.get("prop"):
            spr = props.make(b["prop"], int(rh * 1.0))
            fr.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))
        elif b.get("text"):
            import re
            dev = bool(re.search(r"[ऀ-ॿ]", b["text"]))
            g.text((cx, cy), b["text"], font=_hand(int(rh * .42), dev), fill=INK, anchor="mm")


def draw_emph(fr, e, t):
    W, H = fr.size
    u = H / 1080
    at = e.get("at", .2)
    if t < at or t > at + e.get("dur", .9):
        return
    k = clamp((t - at) / .2)
    d = ImageDraw.Draw(fr)
    cx, cy, rr = e.get("x", .5) * W, e.get("y", .4) * H, e.get("r", .08) * H
    n = e.get("n", 8)
    jitter = 1 + .08 * math.sin(t * 40)
    for i in range(n):
        a = i / n * 2 * math.pi + .3
        r0, r1 = rr * jitter, rr * (1.35 + .1 * (i % 2)) * jitter * k
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * max(r0, r1), cy + math.sin(a) * max(r0, r1))],
               fill=INK, width=max(2, int(4 * u)))


def draw_swoosh(fr, s, t):
    W, H = fr.size
    u = H / 1080
    at = s.get("at", .3)
    if t < at or t > at + s.get("dur", .5):
        return
    k = clamp((t - at) / s.get("dur", .5))
    d = ImageDraw.Draw(fr)
    cx, cy, rr = s.get("x", .5) * W, s.get("y", .5) * H, s.get("r", .1) * H
    a0, a1 = s.get("a0", 200), s.get("a1", 320)
    col = hexc(s.get("color", "#e9b44c"), int(220 * (1 - k)))
    for j in range(2):
        r = rr * (1 + j * .12)
        d.arc([cx - r, cy - r, cx + r, cy + r], a0 + (a1 - a0) * k * .3, a1, fill=col, width=max(2, int((5 - j * 2) * u)))


def draw_popup(fr, p, t):
    W, H = fr.size
    at = p.get("at", .4)
    if t < at:
        return
    k = back_out(clamp((t - at) / .45), 1.2)
    h = int(H * p.get("h", .32))
    spr = props.make(p.get("name", "notepad"), h, p.get("color"))
    x = p.get("x", .6) * W
    y = lerp(H + spr.height * .2, H - spr.height * p.get("show", .72), k)
    if p.get("rot"):
        spr = spr.rotate(p["rot"], expand=True, resample=Image.BICUBIC)
    fr.alpha_composite(spr, (int(x - spr.width / 2), int(y)))


def draw_names(fr, names, t):
    """Premium lower-third tags: dark glass, gold bar, Oswald caps (Mukta for Devanagari)."""
    W, H = fr.size
    u = H / 1080
    from toonshot import hfont
    for i, n in enumerate(names):
        at = n.get("at", .4 + i * .6)
        if t < at:
            continue
        text = n["t"]
        k = clamp((t - at) / max(.3, .035 * len(text)))
        shown = text[: max(1, int(len(text) * k))]
        small = n.get("small", False)
        f = hfont(text, int(n.get("size", 26 if small else 34) * u), "oswald")
        d = ImageDraw.Draw(fr)
        full_w = d.textlength(text, font=f) + 52 * u
        bh = int((40 if small else 56) * u)
        x, y = n.get("x", .49) * W, (n.get("y", .78) + i * .065) * H
        if x + full_w > W - 12 * u:
            x = W - 12 * u - full_w
        box = Image.new("RGBA", (int(full_w), bh), (0, 0, 0, 0))
        bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, box.width - 1, bh - 1], radius=int(8 * u), fill=(16, 13, 12, 215))
        bd.rectangle([0, 0, int(7 * u), bh], fill=hexc(n.get("bar", "#d6b260")))
        bd.line([(int(7 * u), bh - 2), (box.width, bh - 2)], fill=(214, 178, 96, 160), width=max(1, int(2 * u)))
        bd.text((int(24 * u), bh / 2), shown, font=f, fill=(246, 238, 220, 255), anchor="lm")
        ka = ease_out(clamp((t - at) / .3))
        fr.alpha_composite(box, (int(x - (1 - ka) * 24 * u), int(y)))


# ------------------------------------------------------------------ top-down table scene
def topdown_base(CW, CH, sc):
    img = Image.new("RGBA", (CW, CH), hexc(sc.get("table_color", "#ece3c8")))
    a = np.asarray(img, np.float32)
    a[..., :3] += np.random.default_rng(1).normal(0, 4, (CH, CW, 1))
    yy, xx = np.mgrid[0:CH, 0:CW]
    dd = np.sqrt(((xx - CW / 2) / (CW / 2)) ** 2 + ((yy - CH / 2) / (CH / 2)) ** 2) / 1.41
    a[..., :3] *= (1 - .55 * np.clip(dd, 0, 1) ** 2.2)[..., None]
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(img)
    u = CH / 1080
    if sc.get("booth", True):
        d.rectangle([0, 0, CW, 34 * u], fill=(40, 110, 60, 255), outline=INK, width=max(1, int(4 * u)))
        d.rectangle([0, CH - 34 * u, CW, CH], fill=(40, 110, 60, 255), outline=INK, width=max(1, int(4 * u)))
    return img


def topdown_draw(can, sc, t, dur, spec_of):
    CW, CH = can.size
    u = CH / 1080
    d = ImageDraw.Draw(can)
    rot_items = []
    # cups seen from above
    for c in sc.get("cups", []):
        x, y = c[0] * CW, c[1] * CH
        r = 52 * u
        d.ellipse([x - r * 1.35, y - r * 1.35, x + r * 1.35, y + r * 1.35], fill=(244, 242, 236, 255), outline=INK, width=max(1, int(3 * u)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(246, 244, 238, 255), outline=INK, width=max(1, int(3 * u)))
        d.ellipse([x - r * .78, y - r * .78, x + r * .78, y + r * .78], fill=(96, 52, 30, 255))
        d.ellipse([x - r * .4, y - r * .5, x - r * .1, y - r * .25], fill=(200, 150, 120, 200))
        d.rounded_rectangle([x + r * .9, y - 8 * u, x + r * 1.6, y + 8 * u], radius=6 * u, fill=(244, 242, 236, 255), outline=INK, width=max(1, int(3 * u)))
    # paper with pen drawing
    pa = sc.get("paper")
    if pa:
        pw = pa.get("w", .2) * CW
        paper = Image.new("RGBA", (int(pw), int(pw * 1.02)), (250, 250, 248, 255))
        g = ImageDraw.Draw(paper)
        g.rectangle([0, 0, paper.width - 1, paper.height - 1], outline=(70, 70, 80, 255), width=max(1, int(2 * u)))
        strokes = DRAWINGS.get(pa.get("draw", "chip"), DRAWINGS["chip"])
        k = clamp((t - pa.get("at", .3)) / max(.5, pa.get("time", dur * .6)))
        tot = sum(len(s_) for s_ in strokes)
        n = int(tot * k)
        tip = None
        for s_ in strokes:
            if n <= 1:
                break
            pts = [(px * paper.width, py * paper.height) for px, py in s_[:n]]
            if len(pts) > 1:
                g.line(pts, fill=(60, 60, 170, 255), width=max(2, int(4 * u)), joint="curve")
                tip = pts[-1]
            n -= len(s_)
        if pa.get("note"):
            g.text((paper.width * .1, paper.height * .9), pa["note"], font=_hand(int(30 * u)), fill=(60, 60, 170, 255), anchor="lm")
        ang = pa.get("rot", 8)
        prot = paper.rotate(ang, expand=True, resample=Image.BICUBIC)
        px0, py0 = pa.get("x", .5) * CW - prot.width / 2, pa.get("y", .55) * CH - prot.height / 2
        can.alpha_composite(prot, (int(px0), int(py0)))
        d = ImageDraw.Draw(can)
        if tip is not None and pa.get("hand", True) and k < 1:
            # rotate tip into canvas coords
            cx0, cy0 = paper.width / 2, paper.height / 2
            a = math.radians(-ang)
            tx = (tip[0] - cx0) * math.cos(a) - (tip[1] - cy0) * math.sin(a) + pa.get("x", .5) * CW
            ty = (tip[0] - cx0) * math.sin(a) + (tip[1] - cy0) * math.cos(a) + pa.get("y", .55) * CH
            _arm_top(can, (-.05 * CW, ty + .12 * CH), (tx - 40 * u, ty + 50 * u), pa.get("sleeve", "#2f4d7a"), "#f0c49a", u)
            d = ImageDraw.Draw(can)
            d.line([(tx - 40 * u, ty + 50 * u), (tx, ty)], fill=(40, 60, 170, 255), width=max(2, int(10 * u)))
    # people seen from above at the edges
    for pp in sc.get("people", []):
        x, y = pp["x"] * CW, pp["y"] * CH
        r = pp.get("r", .1) * CH
        d.ellipse([x - r * 1.5, y - r * .9, x + r * 1.5, y + r * .9], fill=hexc(pp.get("color", "#2f4d7a")), outline=INK, width=max(1, int(4 * u)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=hexc(pp.get("hair", "#3a2418")), outline=INK, width=max(1, int(4 * u)))
    # money / props slid in by hands
    hands = sc.get("hands", [])
    piles = []
    for i, h in enumerate(hands):
        at, rel = h.get("at", .3 + i * .45), h.get("release", dur * .5)
        side = h.get("from", "left")
        tx, ty = h["to"][0] * CW, h["to"][1] * CH
        start = {"left": (-.1 * CW, ty), "right": (1.1 * CW, ty), "top": (tx, -.1 * CH), "bottom": (tx, 1.1 * CH)}[side]
        if t < at:
            continue
        k_in = ease_out(clamp((t - at) / .5))
        k_out = ease_in_out(clamp((t - rel) / .5))
        hx = lerp(start[0], tx, k_in) if t < rel else lerp(tx, start[0], k_out)
        hy = lerp(start[1], ty, k_in) if t < rel else lerp(ty, start[1], k_out)
        piles.append((h, (hx, hy) if t < rel else (tx, ty), t >= rel))
        if t < rel + .5:
            edge = {"left": (-.1 * CW, hy), "right": (1.1 * CW, hy), "top": (hx, -.1 * CH), "bottom": (hx, 1.1 * CH)}[side]
            hold = (t < rel)
            if hold:
                _cash(can, hx, hy, u, h.get("item", "cash"), h.get("rot", 10 * (i - 1)))
            _arm_top(can, edge, (hx, hy), h.get("sleeve", "#2f4d7a"), h.get("skin", "#f0c49a"), u, fingers=hold)
            d = ImageDraw.Draw(can)
    mg = sc.get("merge")
    for i, (h, (px, py), released) in enumerate(piles):
        if not released:
            continue
        if mg and t > mg.get("at", dur * .7):
            k = ease_in_out(clamp((t - mg["at"]) / .5))
            px, py = lerp(px, mg.get("to", [.5, .5])[0] * CW, k), lerp(py, mg.get("to", [.5, .5])[1] * CH, k)
        _cash(can, px, py, u, h.get("item", "cash"), h.get("rot", 10 * (i - 1)))
        if h.get("label") and not (mg and t > mg.get("at", dur * .7)):
            from toonshot import big_text
            lb = big_text(h["label"], int(40 * u), h.get("label_color", "#7fd07f"))
            can.alpha_composite(lb, (int(px - lb.width / 2 + 20 * u), int(py - 110 * u)))
    if mg and t > mg.get("at", dur * .7) + .45:
        from toonshot import big_text
        lb = big_text(mg.get("label", ""), int(70 * u), mg.get("color", "#f1d04a"))
        s = back_out(clamp((t - mg["at"] - .45) / .35), 2)
        lb = lb.resize((max(1, int(lb.width * s)), max(1, int(lb.height * s))))
        x, y = mg.get("to", [.5, .5])[0] * CW, mg.get("to", [.5, .5])[1] * CH
        can.alpha_composite(lb, (int(x - lb.width / 2), int(y - 140 * u - lb.height / 2)))


def _cash(can, x, y, u, item="cash", rot=0):
    if item == "cash":
        spr = props.make("cash_stack_top", int(120 * u))
    else:
        spr = props.make(item, int(110 * u))
    if rot:
        spr = spr.rotate(rot, expand=True, resample=Image.BICUBIC)
    can.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))


def _arm_top(can, a, b, sleeve, skin, u, fingers=False):
    d = ImageDraw.Draw(can)
    w = 64 * u
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    nx, ny = -math.sin(ang) * w / 2, math.cos(ang) * w / 2
    poly = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
    d.polygon(poly, fill=hexc(sleeve))
    d.line(poly[:2], fill=INK, width=max(1, int(4 * u)))
    d.line(poly[2:], fill=INK, width=max(1, int(4 * u)))
    r = 40 * u
    hx, hy = b[0] + math.cos(ang) * r * .6, b[1] + math.sin(ang) * r * .6
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=hexc(skin), outline=INK, width=max(1, int(4 * u)))
    if fingers:
        for j in range(4):
            off = (j - 1.5) * 16 * u
            fx, fy = hx + math.cos(ang) * r * .7 + nx / (w / 2) * off, hy + math.sin(ang) * r * .7 + ny / (w / 2) * off
            ex, ey = fx + math.cos(ang) * 30 * u, fy + math.sin(ang) * 30 * u
            d.line([(fx, fy), (ex, ey)], fill=INK, width=max(2, int(11 * u)))


def _chip_drawing():
    S = []
    S.append([(.3, .3), (.7, .3), (.7, .7), (.3, .7), (.3, .3)])
    S.append([(.42, .42), (.58, .42), (.58, .58), (.42, .58), (.42, .42)])
    for k in range(6):
        x = .34 + k * .064
        S.append([(x, .3), (x, .22)])
        S.append([(x, .7), (x, .78)])
        y = .34 + k * .064
        S.append([(.3, y), (.22, y)])
        S.append([(.7, y), (.78, y)])
    return [[(p[0], p[1]) for p in _densify(s_)] for s_ in S]


def _densify(pts, step=.01):
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(1, n + 1)]
    return out


def _ship_drawing():
    S = [[(.15, .62), (.85, .62), (.72, .78), (.28, .78), (.15, .62)], [(.5, .62), (.5, .15)],
         [(.52, .18), (.78, .45), (.52, .58)], [(.48, .22), (.25, .48), (.48, .58)], [(.5, .15), (.62, .19), (.5, .23)],
         [(.05, .86), (.2, .82), (.35, .86), (.5, .82), (.65, .86), (.8, .82), (.95, .86)]]
    return [_densify(s_) for s_ in S]


def _map_drawing():
    S = [[(.2, .25), (.45, .18), (.62, .3), (.7, .55), (.55, .82), (.42, .7), (.3, .5), (.2, .25)],
         [(.42, .5), (.48, .5)], [(.45, .47), (.45, .53)]]
    return [_densify(s_) for s_ in S]


DRAWINGS = {"chip": _chip_drawing(), "ship": _ship_drawing(), "map": _map_drawing(),
            "square": [_densify([(.3, .3), (.7, .3), (.7, .7), (.3, .7), (.3, .3)])]}
