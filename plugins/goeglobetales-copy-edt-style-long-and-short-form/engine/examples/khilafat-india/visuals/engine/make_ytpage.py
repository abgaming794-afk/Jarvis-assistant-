"""Rebuild the AMRIT BORI YouTube channel page (mobile, dark) from the user's screenshot details -> photos/yt/page.png.
Real thumbnails cannot be fetched from this container, so video thumbnails are stylised title cards."""
import os
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__)) + "/../"
AB = os.environ.get("AB_ROOT", "/home/user/amrit-borii/")
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"; FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"; FR = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
if not os.path.exists(FR): FR = FS
f = lambda p, s: ImageFont.truetype(p, s)
W, H = 900, 2000
im = Image.new("RGB", (W, H), (15, 15, 15)); d = ImageDraw.Draw(im)
d.text((40, 115), "←", font=f(FS, 54), fill="white"); d.ellipse((720, 112, 770, 162), outline="white", width=5); d.line((762, 156, 778, 172), fill="white", width=5)
for y in (120, 140, 160): d.ellipse((843, y - 4, 851, y + 4), fill="white")
d.rounded_rectangle((34, 190, 866, 216), 10, fill=(40, 45, 140))
logo = Image.open(AB + "brand/amrit_bori_logo_800.png").convert("RGBA").resize((156, 156))
mask = Image.new("L", (156, 156), 0); ImageDraw.Draw(mask).ellipse((0, 0, 155, 155), fill=255); im.paste(logo, (34, 241), mask)
d.text((222, 245), "AMRIT BORI", font=f(FB, 50), fill="white")
d.text((222, 315), "@ITSAMRITBORII", font=f(FS, 25), fill=(235, 235, 235))
d.text((222, 357), "21 subscribers  •  24 videos", font=f(FR, 25), fill=(170, 170, 170))
d.text((34, 425), "This channel brings you unexplored truths from history, mystery,", font=f(FR, 24), fill=(190, 190, 190))
d.text((34, 459), "geopolitics, geography, and real-world case studies. ...more", font=f(FR, 24), fill=(190, 190, 190))
d.rounded_rectangle((34, 512, 866, 596), 42, fill=(241, 241, 241)); d.text((450, 554), "Subscribe", font=f(FB, 32), fill=(15, 15, 15), anchor="mm")
for x, t in ((34, "Videos"), (192, "Shorts"), (354, "Posts")): d.text((x, 755), t, font=f(FS, 32), fill="white" if t == "Videos" else (170, 170, 170))
d.line((34, 820, 140, 820), fill="white", width=4); d.line((0, 824, W, 824), fill=(50, 50, 50), width=2)
for x0, x1, t, on in ((34, 170, "Latest", 1), (188, 344, "Popular", 0), (362, 500, "Oldest", 0)):
    d.rounded_rectangle((x0, 858, x1, 926), 14, fill=(241, 241, 241) if on else (39, 39, 39)); d.text(((x0 + x1) / 2, 892), t, font=f(FS, 28), fill=(15, 15, 15) if on else "white", anchor="mm")
VIDS = [("CRINK", "NAYA AXIS?", (170, 20, 30), "8:56", "Naya \"AXIS\": Russia, China,", "Iran, North Korea — Dosti ya D...", "8 · 4h ago"),
        ("ASLI KHATRA", "LPG", (25, 45, 110), "9:12", "Iran-US War ka Asli Shikaar:", "Aapki Rasoi", "10 · 1d ago"),
        ("CHOLA", "EMPIRE", (120, 60, 20), "25:16", "The Entire History of the", "Chola Empire", "13 · 5d ago"),
        ("INDIA WAS", "AHEAD!", (190, 150, 20), "18:49", "China Ameer Kaise Bana, India", "Peeche Kyun Reh Gaya? | India...", "14 · 7d ago")]
for i, (a, b, col, dur, t1, t2, meta) in enumerate(VIDS):
    y = 962 + i * 224
    d.rounded_rectangle((34, y, 376, y + 190), 14, fill=col)
    d.text((50, y + 18), a, font=f(FB, 46), fill="white"); d.text((50, y + 76), b, font=f(FB, 40), fill=(255, 215, 90))
    d.rounded_rectangle((286, y + 136, 368, y + 176), 8, fill=(0, 0, 0)); d.text((327, y + 156), dur, font=f(FS, 24), fill="white", anchor="mm")
    d.text((412, y + 8), t1, font=f(FR, 28), fill="white"); d.text((412, y + 44), t2, font=f(FR, 28), fill="white"); d.text((412, y + 86), meta, font=f(FR, 24), fill=(170, 170, 170))
    for k in range(3): d.ellipse((853 + 0, y + 14 + k * 0, 861, y + 22), fill="white") if k == 0 else None
d.line((0, 1820, W, 1820), fill=(40, 40, 40), width=2)
for x, t in ((90, "Home"), (270, "Shorts"), (630, "Subscriptions"), (810, "You")): d.text((x, 1886), t, font=f(FR, 22), fill="white", anchor="mm")
d.ellipse((412, 1822, 488, 1898), fill=(39, 39, 39)); d.text((450, 1858), "+", font=f(FS, 48), fill="white", anchor="mm")
im.save(R + "photos/yt/page.png"); print("ok")
