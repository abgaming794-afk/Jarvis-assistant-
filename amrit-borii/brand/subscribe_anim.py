"""Subscribe call-out animation for AMRIT BORI (2D flat, matches the documentary palette).

Usage:
  python3 subscribe_anim.py preview   -> 1920x1080 60fps MP4 over a sample background
  python3 subscribe_anim.py alpha     -> 3840x2160 60fps ProRes 4444 with transparency (for the edit)
"""
import os as _os, glob as _glob
AB_ROOT = _os.environ.get("AB_ROOT", "/home/user/amrit-borii/")          # workspace root (brand/, fonts/, host/, render_tmp/)
PROJ = _os.path.join(AB_ROOT, _os.environ.get("AB_PROJECT", "new-axis"), "")  # current video project folder
MAPDATA = _os.environ.get("AB_MAPDATA") or next(iter(_glob.glob("/root/.claude/plugins/**/map-shorts/engine/data/", recursive=True)), "")
import math, os, subprocess, sys, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BR = AB_ROOT + "brand/"
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
DUR, FPS = 4.6, 60
RED, GREY, CARD, TXT, MUTED, YEL = (229, 9, 20), (62, 66, 76), (17, 24, 39), (241, 250, 238), (156, 163, 175), (255, 209, 102)


def ease_out_back(t, s=1.70158):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def ease_io(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))


def seg(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a)))


def bell(d, cx, cy, s, filled, col):
    """Bell icon centred at cx,cy with size s."""
    w = s
    body = [(cx - 0.42 * w, cy + 0.28 * w), (cx - 0.34 * w, cy - 0.05 * w), (cx - 0.30 * w, cy - 0.25 * w),
            (cx - 0.18 * w, cy - 0.40 * w), (cx, cy - 0.45 * w), (cx + 0.18 * w, cy - 0.40 * w),
            (cx + 0.30 * w, cy - 0.25 * w), (cx + 0.34 * w, cy - 0.05 * w), (cx + 0.42 * w, cy + 0.28 * w)]
    lw = max(2, int(0.08 * w))
    if filled:
        d.polygon(body, fill=col)
    else:
        d.line(body + [body[0]], fill=col, width=lw, joint="curve")
    d.ellipse([cx - 0.10 * w, cy + 0.32 * w, cx + 0.10 * w, cy + 0.50 * w], fill=col)
    d.ellipse([cx - 0.06 * w, cy - 0.56 * w, cx + 0.06 * w, cy - 0.44 * w], fill=col)


def cursor(d, x, y, s, press):
    k = s * (0.85 if press else 1.0)
    pts = [(0, 0), (0, 1.0), (0.26, 0.76), (0.44, 1.14), (0.58, 1.07), (0.40, 0.70), (0.74, 0.70)]
    P = [(x + px * k, y + py * k) for px, py in pts]
    d.polygon([(px + 0.06 * k, py + 0.06 * k) for px, py in P], fill=(0, 0, 0, 110))
    d.polygon(P, fill=(255, 255, 255), outline=(20, 20, 20), width=max(2, int(0.05 * k)))


def frame(t, W, H, logo):
    u = W / 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # ---- card geometry
    cw, ch = 1120 * u, 190 * u
    cx0 = (W - cw) / 2
    rest_y = H - ch - 110 * u
    enter = ease_out_back(seg(t, 0.0, 0.55))
    leave = ease_io(seg(t, 4.0, 4.5))
    y = H + 40 * u + (rest_y - H - 40 * u) * enter + (H + 40 * u - rest_y) * leave
    alpha = int(255 * min(1, seg(t, 0, 0.2)) * (1 - leave))
    if alpha <= 0:
        return img
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([cx0 + 8 * u, y + 16 * u, cx0 + cw + 8 * u, y + ch + 16 * u], int(40 * u), fill=(0, 0, 0, 150))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14 * u)))
    d.rounded_rectangle([cx0, y, cx0 + cw, y + ch], int(40 * u), fill=CARD + (252,), outline=(255, 255, 255, 30), width=max(1, int(2 * u)))
    # logo avatar (spins in slightly)
    ls = int(140 * u)
    lg = logo.resize((ls, ls), Image.LANCZOS).rotate(-20 * (1 - ease_out_back(seg(t, 0.1, 0.6))), resample=Image.BICUBIC)
    lay.alpha_composite(lg, (int(cx0 + 26 * u), int(y + (ch - ls) / 2)))
    # names
    d.text((cx0 + 190 * u, y + 52 * u), "AMRIT BORI", font=ImageFont.truetype(FB, int(54 * u)), fill=TXT)
    d.text((cx0 + 192 * u, y + 118 * u), "@AMRITBORII", font=ImageFont.truetype(FS, int(28 * u)), fill=MUTED)
    # subscribe button
    clicked = t >= 1.40
    bx0, bw, bh = cx0 + 650 * u, 300 * u, 92 * u
    by0 = y + (ch - bh) / 2
    pop = 1 + 0.10 * math.sin(math.pi * seg(t, 1.40, 1.62))
    bcx, bcy = bx0 + bw / 2, by0 + bh / 2
    bw2, bh2 = bw * pop / 2, bh * pop / 2
    d.rounded_rectangle([bcx - bw2, bcy - bh2, bcx + bw2, bcy + bh2], int(bh2), fill=(GREY if clicked else RED) + (255,))
    label = "SUBSCRIBED ✓" if clicked else "SUBSCRIBE"
    d.text((bcx, bcy), label, font=ImageFont.truetype(FB, int((34 if clicked else 40) * u)), fill=TXT, anchor="mm")
    # click ripple
    rp = seg(t, 1.40, 1.85)
    if 0 < rp < 1:
        r = (40 + 220 * rp) * u
        d.ellipse([bcx - r, bcy - r, bcx + r, bcy + r], outline=(255, 255, 255, int(200 * (1 - rp))), width=max(2, int(6 * u)))
    # bell
    belx, bely, bs = cx0 + 1035 * u, y + ch / 2, 76 * u
    rung = t >= 2.55
    ang = 0
    if rung:
        k = seg(t, 2.55, 3.6)
        ang = 22 * math.sin(k * math.pi * 7) * (1 - k)
    bl = Image.new("RGBA", (int(bs * 2), int(bs * 2)), (0, 0, 0, 0))
    bell(ImageDraw.Draw(bl), bs, bs, bs, rung, YEL if rung else TXT)
    bl = bl.rotate(ang, center=(bs, bs * 0.5), resample=Image.BICUBIC)
    lay.alpha_composite(bl, (int(belx - bs), int(bely - bs)))
    if rung and t < 3.4:  # ring rays
        k = seg(t, 2.55, 3.4)
        for sgn in (-1, 1):
            for i, a0 in enumerate((-35, 0, 35)):
                a = math.radians(a0)
                r1, r2 = (58 + 30 * k) * u, (78 + 34 * k) * u
                x1, y1 = belx + sgn * r1 * math.cos(a), bely - 8 * u + r1 * math.sin(a)
                x2, y2 = belx + sgn * r2 * math.cos(a), bely - 8 * u + r2 * math.sin(a)
                d.line([(x1, y1), (x2, y2)], fill=YEL + (int(255 * (1 - k)),), width=max(2, int(6 * u)))
    # hinglish nudge above the card
    nk = ease_out_back(seg(t, 2.7, 3.1))
    if nk > 0:
        fnt = ImageFont.truetype(FB, max(1, int(44 * u * nk)))
        d.text((W / 2, y - 48 * u), "Subscribe karo  •  Bell dabao!", font=fnt, fill=YEL, anchor="mm")
    # cursor path: enter -> button -> click -> bell -> click -> exit
    if 0.55 < t < 3.9:
        p0, p1, p2, p3 = (W + 60 * u, H + 60 * u), (bcx + 40 * u, bcy + 10 * u), (belx + 10 * u, bely + 6 * u), (W + 80 * u, H + 80 * u)
        if t < 1.35:
            k = ease_io(seg(t, 0.6, 1.3)); x, yy = p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k
        elif t < 2.0:
            x, yy = p1
        elif t < 2.5:
            k = ease_io(seg(t, 2.0, 2.5)); x, yy = p1[0] + (p2[0] - p1[0]) * k, p1[1] + (p2[1] - p1[1]) * k
        elif t < 3.2:
            x, yy = p2
        else:
            k = ease_io(seg(t, 3.2, 3.85)); x, yy = p2[0] + (p3[0] - p2[0]) * k, p2[1] + (p3[1] - p2[1]) * k
        press = 1.36 <= t <= 1.50 or 2.52 <= t <= 2.66
        cursor(d, x, yy, 64 * u, press)
    if alpha < 255:
        a = lay.getchannel("A").point(lambda v: v * alpha // 255)
        lay.putalpha(a)
    img.alpha_composite(lay)
    return img


def run(mode):
    logo = Image.open(BR + "amrit_bori_logo_4096.png").convert("RGBA")
    if mode == "preview":
        W, H = 1920, 1080
        bg = Image.open(PROJ + "visuals/styleframes/C_crink_axis.png").convert("RGBA").resize((W, H))
        out = BR + "subscribe_preview_1080p60.mp4"
    else:
        W, H = 3840, 2160
        bg = None
        out = BR + "subscribe_overlay_4k60_alpha.mov"
    tmp = "/tmp/claude-0/sub_frames"
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    logo_small = logo.resize((600, 600), Image.LANCZOS)
    n = int(DUR * FPS)
    for i in range(n):
        f = frame(i / FPS, W, H, logo_small)
        if bg is not None:
            b = bg.copy(); b.alpha_composite(f); f = b.convert("RGB")
        f.save(f"{tmp}/f{i:04d}.png", compress_level=1)
    if mode == "preview":
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
               "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", out]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", out)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "preview")
