import sys, glob
from PIL import Image, ImageDraw
fs = sorted(glob.glob(sys.argv[1] + "/s_*.png")); cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
tw, th = 405, 720; rows = (len(fs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 30)), "black"); d = ImageDraw.Draw(sheet)
for i, f in enumerate(fs):
    im = Image.open(f).convert("RGB").resize((tw, th)); x, y = (i % cols) * tw, (i // cols) * (th + 30)
    sheet.paste(im, (x, y + 30)); d.text((x + 6, y + 8), f.split("s_")[-1][:-4], fill="yellow")
sheet.save(sys.argv[2], quality=88)
