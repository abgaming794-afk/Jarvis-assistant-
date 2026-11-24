"""Cut a person out of a plain (dark or flat) studio background - no model download needed.

Usage: python3 cutout.py portrait.png out_cut.png [tolerance=14] [seed_rows=900]
- The background colour is sampled from the top-left corner. Pixels close to it (RGB distance < tolerance) that are
  connected to the top edge, or to the left/right edges above `seed_rows`, become transparent.
- Holes are filled, the edge is closed and feathered (2.5 px), so dark hair/chainmail inside the figure stays.
- Writes out_cut.png (RGBA), out_cut_mask.png and out_cut_check.png (figure on red, to inspect the edge).
Works best when the AI prompt asks for "plain solid dark charcoal background, head and shoulders only".
If the edge is ragged, raise/lower tolerance by 4. Needs numpy, pillow, scipy (pip install scipy)."""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd

src, out = sys.argv[1], sys.argv[2]
tol = float(sys.argv[3]) if len(sys.argv) > 3 else 14.0
im = Image.open(src).convert("RGB"); a = np.asarray(im).astype(float)
seed_rows = int(sys.argv[4]) if len(sys.argv) > 4 else int(a.shape[0] * 0.64)
bg = a[:20, :20].reshape(-1, 3).mean(0)
near = np.sqrt(((a - bg) ** 2).sum(2)) < tol
lab, _ = nd.label(near)
seeds = set(lab[0, :]) | set(lab[:seed_rows, 0]) | set(lab[:seed_rows, -1]); seeds.discard(0)
bgm = nd.binary_fill_holes(nd.binary_opening(np.isin(lab, list(seeds)), iterations=2))
fg = nd.binary_fill_holes(nd.binary_closing(~bgm, iterations=4))
mask = Image.fromarray((fg * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2.5))
rgba = im.convert("RGBA"); rgba.putalpha(mask); rgba.save(out)
mask.save(out.rsplit(".", 1)[0] + "_mask.png")
chk = Image.new("RGBA", im.size, (200, 60, 40, 255)); chk.alpha_composite(rgba)
chk.convert("RGB").resize((im.width // 2, im.height // 2)).save(out.rsplit(".", 1)[0] + "_check.png")
print("cut ok", out, "bg", bg.round(1).tolist())
