"""Premium kinetic typography for titles, years and map labels.
kinetic(text, size, te, anim) -> RGBA sprite for time te (seconds since the text started).
  anim = "rise"  : letters rise out of an invisible baseline mask, tracking settles, then a light sweep + gold rule
  anim = "roll"  : digits roll like a slot machine and lock one by one (years / numbers), then light sweep + gold rule
"""
import functools, math
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from common import clamp, ease_out, ease_in_out

GOLD = (214, 178, 96, 255)


@functools.lru_cache(maxsize=512)
def _glyph(ch, size):
    import toonshot
    return toonshot.big_text(ch, size, "#ffffff") if ch.strip() else None


def _advance(ch, size):
    import toonshot
    f = toonshot.hfont(ch, size * 1.22, "cinzel_black")
    return f.getlength(ch if ch.strip() else "n") * (1.0 if ch.strip() else 0.55)


@functools.lru_cache(maxsize=64)
def _window(sz):
    """Feathered slot window: digits fade out toward the top/bottom of their cell."""
    w, h = sz
    col = Image.new("L", (1, h))
    for y in range(h):
        e = (min(y, h - 1 - y) - h * .04) / (h * .30)
        col.putpixel((0, y), int(255 * clamp(e)))
    return col.resize((w, h))


def _sweep(img, k):
    """Diagonal light band passing once across the text (k 0..1)."""
    if k <= 0 or k >= 1:
        return img
    W, H = img.size
    band = Image.new("L", (W, H), 0)
    x = -H + k * (W + 2 * H)
    ImageDraw.Draw(band).polygon([(x, 0), (x + H * .45, 0), (x + H * .45 - H, H), (x - H, H)], fill=150)
    band = band.filter(ImageFilter.GaussianBlur(H * .06))
    a = img.getchannel("A")
    from PIL import ImageChops
    m = ImageChops.multiply(band, a)
    white = Image.new("RGBA", (W, H), (255, 250, 235, 0))
    white.putalpha(m)
    out = img.copy()
    out.alpha_composite(white)
    return out


def kinetic(text, size, te, anim="rise", frm=None, rule=True):
    chars = list(text)
    adv = [_advance(c, size) for c in chars]
    if anim == "roll":
        cw = max(_glyph(str(k), size).width for k in range(10))
        dadv = max(_advance(str(k), size) for k in range(10))
        adv = [dadv if c.isdigit() else a for a, c in zip(adv, chars)]
    gl = [_glyph(c, size) for c in chars]
    gh = max((g.height for g in gl if g), default=size)
    pad = int(size * .25)
    track0 = size * .28
    n = len(chars)
    k_all = clamp(te / (0.45 + 0.035 * n))
    track = track0 * (1 - ease_out(k_all))
    total = sum(adv) + track * max(0, n - 1)
    W, H = int(total + pad * 2 + size * .5), int(gh + pad * 2 + size * .25)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = pad
    base_y = pad
    if anim == "roll":
        target = text
        src = frm if frm is not None else "".join("0" if c.isdigit() else c for c in text)
        src = src.rjust(len(target), "0")[-len(target):]
    for i, (c, g, a) in enumerate(zip(chars, gl, adv)):
        if g is None:
            x += a + track
            continue
        if anim == "roll" and c.isdigit():
            cw = max(_glyph(str(k), size).width for k in range(10))
            cell = Image.new("RGBA", (int(cw), int(gh)), (0, 0, 0, 0))
            ki = ease_out(clamp((te - i * 0.12) / 0.9))
            d0, d1 = int(src[i]) if src[i].isdigit() else 0, int(c)
            spins = 1 + i                                  # later digits spin more
            pos = d0 + (spins * 10 + (d1 - d0) % 10) * ki  # continuous digit position
            fr_ = pos - math.floor(pos)
            for off in (0, 1):
                gg = _glyph(str(int(math.floor(pos) + off) % 10), size)
                yy = (off - fr_) * gh * 1.05
                tmp = Image.new("RGBA", cell.size, (0, 0, 0, 0))
                tmp.alpha_composite(gg, (int((cw - gg.width) / 2), 0))
                cell.alpha_composite(tmp.transform(cell.size, Image.AFFINE, (1, 0, 0, 0, 1, -yy), Image.BILINEAR))
            speed = 1 - ki
            if speed > .04:   # vertical motion blur while spinning
                cell = cell.resize((cell.width, max(2, int(cell.height / (1 + 5 * speed))))).resize(cell.size, Image.BILINEAR)
            if ki < 1:
                win = _window(cell.size).point(lambda v, q=ki ** 3: int(v + (255 - v) * q))
                cell.putalpha(ImageChops.multiply(cell.getchannel("A"), win))
            al = 1.0
            x_shift = (a - cw) / 2
        else:
            cell = Image.new("RGBA", (int(g.width), int(gh)), (0, 0, 0, 0))
            ki = ease_out(clamp((te - i * 0.035) / 0.45))
            yoff = (1 - ki) * gh * .85
            cell.alpha_composite(g, (0, 0))
            cell = cell.transform(cell.size, Image.AFFINE, (1, 0, 0, 0, 1, -yoff), Image.BILINEAR)
            al = ki
        else_shift = locals().get("x_shift", 0) if anim == "roll" and c.isdigit() else 0
        if al < 1:
            cell.putalpha(cell.getchannel("A").point(lambda v, al=al: int(v * al)))
        img.alpha_composite(cell, (max(0, int(x + else_shift)), base_y))
        x += a + track
    done = 0.45 + 0.035 * n if anim != "roll" else 0.9 + 0.12 * n
    img = _sweep(img, clamp((te - done) / 0.7))
    if rule:
        kr = ease_in_out(clamp((te - done * .6) / 0.5))
        if kr > 0:
            d = ImageDraw.Draw(img)
            w_ = (total) * kr
            y_ = base_y + gh + size * .06
            d.line([(W / 2 - w_ / 2, y_), (W / 2 + w_ / 2, y_)], fill=GOLD, width=max(2, size // 22))
    return img
