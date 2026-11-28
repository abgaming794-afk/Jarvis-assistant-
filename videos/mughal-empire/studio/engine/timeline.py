"""Year timeline ruler (bottom right). A beat sets "year": 1526 or "year": [1526, 1857] (animates across the beat).
Between beats the ruler scrolls from the previous beat's year to this one, so time jumps read on screen."""
import palette
import math
from PIL import Image, ImageDraw
from common import font, clamp, ease_in_out


def _year_at(beat, t, dur):
    y = beat.get("year")
    if y is None:
        return None
    if isinstance(y, (list, tuple)):
        k = ease_in_out(clamp((t - 0.3) / max(0.5, dur - 0.6)))
        return y[0] + (y[1] - y[0]) * k
    return float(y)


def _end_year(beat):
    y = beat.get("year")
    return None if y is None else float(y[-1] if isinstance(y, (list, tuple)) else y)


def draw(fr, beat, t, dur, prev_beat=None):
    cur = _year_at(beat, t, dur)
    if cur is None:
        return
    py = _end_year(prev_beat) if prev_beat is not None else None
    if py is not None and py != cur and not isinstance(beat.get("year"), (list, tuple)):
        span = abs(cur - py)
        T = 0.5 if span <= 12 else 0.9
        cur = py + (cur - py) * ease_in_out(clamp(t / T))
    W, H = fr.size
    u = H / 1080.0
    x0, x1 = int(W * .03), int(W * .36)
    y0, y1 = int(H * .915), int(H * .985)
    band = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    bw, bh = band.size
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=int(bh * .35), fill=(18, 14, 12, 170))
    span_years = 50.0
    px_per_year = bw / span_years
    base = bh * .62
    d.line([(int(bh * .3), base), (bw - int(bh * .3), base)], fill=(240, 228, 200, 200), width=max(1, int(2 * u)))
    from toonshot import hand
    f_small = hand(int(19 * u), "oswald")
    first = int(math.floor(cur - span_years / 2))
    for yr in range(first, first + int(span_years) + 2):
        x = bw / 2 + (yr - cur) * px_per_year
        if x < bh * .3 or x > bw - bh * .3:
            continue
        edge = min(x, bw - x) / (bw * .5)
        a = int(255 * clamp(edge * 2.2))
        if yr % 10 == 0:
            d.line([(x, base - bh * .22), (x, base + bh * .12)], fill=(240, 228, 200, a), width=max(1, int(3 * u)))
            d.text((x, base - bh * .26), str(yr), font=f_small, fill=(240, 228, 200, a), anchor="md")
        elif yr % 5 == 0:
            d.line([(x, base - bh * .12), (x, base + bh * .08)], fill=(240, 228, 200, int(a * .7)), width=max(1, int(2 * u)))
    # centre marker
    cx = bw / 2
    d.polygon([(cx - bh * .16, base + bh * .32), (cx + bh * .16, base + bh * .32), (cx, base + bh * .06)],
              fill=palette.acc())
    fr.alpha_composite(band, (x0, y0))
    # current year pill above the band
    yr = int(round(cur))
    f_big = hand(int(30 * u), "cinzel_black")
    txt = str(yr)
    tw = ImageDraw.Draw(fr).textlength(txt, font=f_big)
    pw, ph = int(tw + 26 * u), int(40 * u)
    pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=int(ph * .45), fill=(16, 13, 12, 230), outline=palette.acc(),
                         width=max(1, int(2 * u)))
    pd.text((pw / 2, ph / 2), txt, font=f_big, fill=(247, 243, 234, 255), anchor="mm")
    fr.alpha_composite(pill, (int(x0 + cx - pw / 2), int(y0 - ph * .78)))
