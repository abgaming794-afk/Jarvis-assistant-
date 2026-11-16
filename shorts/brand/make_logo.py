"""AMRIT BORI channel logo, rebuilt in high quality (4096 px), based on the existing channel logo."""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
from PIL import Image, ImageDraw, ImageFont

S = 8192                 # supersample canvas
OUT = 4096
R = S * 0.48             # circle radius
CX = CY = S / 2
BLUE = (27, 70, 151, 255)
INK = (10, 10, 12, 255)
FD = AB_ROOT + "brand/fonts/"


def X(u): return CX + u * R
def Y(v): return CY + v * R


def glyph(ch, font_path, size=4000):
    f = ImageFont.truetype(font_path, size)
    l, t, r, b = f.getbbox(ch)
    im = Image.new("L", (r - l + 20, b - t + 20), 0)
    ImageDraw.Draw(im).text((10 - l, 10 - t), ch, font=f, fill=255)
    return im.crop(im.getbbox())


def place(canvas, mask, box, color=INK):
    x0, y0, x1, y1 = [int(v) for v in box]
    m = mask.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    layer = Image.new("RGBA", m.size, color)
    canvas.paste(layer, (x0, y0), m)


def explorer(d, ox, oy, w):
    """Kneeling explorer with fedora and magnifying glass, facing left. Local box 100 x 130, base at v=130."""
    k = w / 100
    P = lambda u, v: (ox + u * k, oy + v * k)
    def limb(pts, wid):
        pts = [P(*p) for p in pts]
        d.line(pts, fill=INK, width=int(wid * k), joint="curve")
        for p in pts:
            rr = wid * k / 2
            d.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=INK)
    # kneeling pose: back knee on the ground, front foot planted, torso leaning forward
    limb([(46, 92), (18, 95), (18, 126)], 12)                                       # front thigh + shin
    d.polygon([P(6, 124), P(24, 124), P(24, 131), P(4, 131)], fill=INK)             # front shoe
    limb([(56, 92), (60, 126), (88, 128)], 12)                                      # back thigh, knee down, shin
    d.polygon([P(30, 46), P(52, 42), P(62, 94), P(40, 97)], fill=INK)               # torso
    limb([(50, 50), (54, 72), (34, 90)], 8)                                         # back arm on knee
    limb([(33, 50), (20, 58), (15, 42)], 8)                                         # raised arm
    limb([(15, 42), (12, 34)], 4.5)                                                 # magnifier handle
    cx, cy, rr = P(11, 25)[0], P(11, 25)[1], 9 * k
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=INK, width=int(3.6 * k))
    d.polygon([P(32, 36), P(40, 36), P(42, 46), P(31, 47)], fill=INK)               # neck
    hx, hy, hr = P(35, 29)[0], P(35, 29)[1], 9 * k
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=INK)                       # head
    d.ellipse([*P(20, 18), *P(52, 24)], fill=INK)                                   # fedora brim
    d.rounded_rectangle([*P(26, 7), *P(45, 21)], radius=int(4 * k), fill=INK)       # fedora crown


def build():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=BLUE)

    a = glyph("A", FD + "Montserrat-ExtraBold.ttf")
    b = glyph("B", FD + "Montserrat-ExtraBold.ttf").transpose(Image.FLIP_LEFT_RIGHT)
    place(img, a, (X(-0.80), Y(-0.80), X(-0.18), Y(0.02)))
    place(img, b, (X(-0.21), Y(-0.045), X(0.25), Y(0.67)))

    # explorer sitting on top of the B, facing the A
    fw = 0.24 * R
    explorer(d, X(-0.11), Y(-0.045) - fw * 1.31, fw)

    # tagline in script
    f = ImageFont.truetype(FD + "GreatVibes-Regular.ttf", 10)
    text = "Mystery  &  Research"
    target_w = (0.86 - 0.12) * R
    size = int(10 * target_w / f.getlength(text))
    f = ImageFont.truetype(FD + "GreatVibes-Regular.ttf", size)
    d.text((X(0.12), Y(-0.13)), text, font=f, fill=INK, anchor="ls")

    out = img.resize((OUT, OUT), Image.LANCZOS)
    out.save(AB_ROOT + "brand/amrit_bori_logo_4096.png")
    sq = Image.new("RGBA", (OUT, OUT), (15, 15, 15, 255))
    sq.alpha_composite(out)
    sq.convert("RGB").save(AB_ROOT + "brand/amrit_bori_logo_4096_dark.png")
    out.resize((800, 800), Image.LANCZOS).save(AB_ROOT + "brand/amrit_bori_logo_800.png")


if __name__ == "__main__":
    build()
    print("done")
