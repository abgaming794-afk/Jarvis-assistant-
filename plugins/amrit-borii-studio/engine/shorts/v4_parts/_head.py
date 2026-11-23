"""AMRIT BORII Short - 'Maharashtra ki 2000 saal purani bhool-bhulaiya'  9:16, design 1080x1920 drawn x2 into 2160x3840.
Built from _head.py + _helpers_block.py + _tail.py (cat > short_storyboard.py).
Timing comes from voice/full_units.json (aligned VO). CLI:  python3 short_storyboard.py still OUTDIR t1 t2 ...
"""
import os, sys, json, math, re
os.environ.setdefault("AB_PROJECT", "bhool-bhulaiya"); os.environ.setdefault("AB_ORIENT", "vertical")
from core import *
from core import _poly_path
from widgets import *
from shapely.geometry import shape, Polygon
from PIL import Image

ROOT = PROJ
HERE = os.path.dirname(os.path.abspath(__file__))
EMP, EMP_PATH = {}, {}
COL = dict(NOW="#FF9933", MAURYA="#C9A24A", SEA="#7FDBFF", RED="#FF6B6B", ROME="#C0504D", STONE="#E8D9B5", GREEK="#6FA8FF")
# South-Asian polities c. 100 CE (historical-basemaps, approximate) - bhagwa shades in the historical scenes
ERAS = {k: [(f["name"], shape(f["geom"])) for f in v] for k, v in json.load(open(os.path.join(HERE, "eras2.geojson.json"))).items()}
ERA_PATH = {k: [(n, _poly_path(g, 0)) for n, g in v] for k, v in ERAS.items()}
BHAGWA = ["#FF9933", "#F28A22", "#FFB054", "#E67A16", "#FFA347", "#F59B3A"]
# Maharashtra (Natural Earth admin-1), Crete (Natural Earth), Roman Empire c. 100 CE (historical-basemaps)
GEO = {k: shape(v) for k, v in json.load(open(os.path.join(HERE, "laby.geojson.json"))).items()}
GEO_PATH = {k: _poly_path(g, 0) for k, g in GEO.items()}
OCEANS = {k: shape(v) for k, v in json.load(open(os.path.join(HERE, "oceans.geojson.json"))).items()}
OC_PATH = {k: _poly_path(g, 0) for k, g in OCEANS.items()}

# ---------------------------------------------------------------- timing from the aligned VO (voice/full_units.json)
UN = json.load(open(ROOT + "voice/full_units.json"))["units"]
VO_DUR = json.load(open(ROOT + "voice/full_units.json"))["duration"]
SIL = [tuple(map(float, l.split())) for l in open(ROOT + "voice/full_sil.tsv") if l.strip()]
def us(i): return UN[i]["start"]
def ue(i): return UN[i]["end"]
def kw(i, word, occ=0):
    """approximate start of `word` inside unit i (char-proportional, snapped to an internal pause)"""
    txt = UN[i]["text"]; low = txt.lower(); p_ = -1
    for _ in range(occ + 1): p_ = low.find(word.lower(), p_ + 1)
    if p_ < 0: return us(i)
    est = us(i) + (ue(i) - us(i)) * p_ / max(1, len(txt))
    best = None
    for a_, b_ in SIL:
        if us(i) < b_ < ue(i) and abs(b_ - est) < 0.35 and (best is None or abs(b_ - est) < abs(best - est)): best = b_
    return (best if best else est) - 0.05
# units: 0 hook, 1 kaise aaya, 2 Boramani, 3 15 chakkar, 4 record, 5 found, 6 Crete, 7 Knossos coin, 8 Daedalus,
# 9 age, 10 jaanch, 11 Strabo, 12 ship coin, 13 Pompeii, 14 theory, 15 Satara.., 16 kode/chakravyuh, 17-19 CTA
SCENES = [("hook", 0), ("bora", 2), ("found", 5), ("crete", 6), ("myth", 8), ("age", 9), ("strabo", 11), ("ship", 12),
          ("pompeii", 13), ("theory", 14), ("others", 15), ("chakra", 16), ("cta", 17)]
TAIL = 1.9
T_TOTAL = round(VO_DUR + TAIL, 2)
SC_T = {}
for n_, (k_, u_) in enumerate(SCENES):
    a_ = 0.0 if n_ == 0 else us(u_) - 0.12
    b_ = (us(SCENES[n_ + 1][1]) - 0.12) if n_ + 1 < len(SCENES) else T_TOTAL
    SC_T[k_] = (a_, b_)
def T(k): return SC_T[k]

# phrase captions straight from the VO text (<= ~4 words, split at commas), keywords in yellow
CAP_KEYS = {"maharashtra", "ghaas", "maidan", "patthar", "bhoolbhulaiya", "bhoolbhulaiyan", "2400", "greek", "sikkon", "solapur", "boramani", "15", "gol", "chakkar",
            "50", "11", "sabse", "badi", "deccan", "college", "sachin", "patil", "greece", "crete", "knossos", "chaandi", "daedalus",
            "minotaur", "2000", "satavahana", "pakki", "jaanch", "strabo", "120", "jahaz", "egypt", "india", "sikke", "pompeii",
            "lakshmi", "yakshi", "bhokardan", "theory", "nishaan", "paithan", "ter", "satara", "sangli", "kolhapur", "kode",
            "chakravyuh", "abhimanyu", "comment", "subscribe", "pooja"}
CAPS = []
for u in UN:
    parts = []
    for clause in re.split(r"(?<=,)\s+", u["text"]):
        w_ = clause.split()
        while w_:
            n_ = 4 if len(w_) > 5 else len(w_)
            parts.append(" ".join(w_[:n_])); w_ = w_[n_:]
    tot = sum(len(x) + 1 for x in parts); t0 = u["start"]
    for x in parts:
        d_ = (u["end"] - u["start"]) * (len(x) + 1) / tot
        CAPS.append((t0, t0 + d_, x)); t0 += d_

LOGO = None
DOCS = {}
RULER = {}
RULER_INFO = {}
# (key, file, crop fractions) - crops set after looking at each image
DOC_FILES = (("coin", "knossos_coin.jpg", (0.02, 0.02, 0.98, 0.98)), ("daedalus", "daedalus_mosaic.jpg", (0.06, 0.17, 0.95, 0.85)),
             ("ship", "ship_coin.jpg", None), ("lakshmi", "pompeii_lakshmi.jpg", (0.12, 0.02, 0.92, 0.98)),
             ("kalambi", "kalambi.png", None), ("halebid", "halebid_chakra.jpg", (0.12, 0.0, 0.76, 1.0)),
             ("grass", "grass.jpg", (0.0, 0.25, 1.0, 1.0)), ("grassfull", "grass.jpg", None),
             ("deccan", "deccan.jpg", None))
def load():
    global LOGO
    if LOGO is None:
        LOGO = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_800.png").resize((200, 200)))
        for k_, f_, crop in DOC_FILES:
            try:
                im = Image.open(ROOT + "visuals/photos/" + f_)
                if im.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", im.size, "white"); im = im.convert("RGBA"); bg.paste(im, mask=im.split()[3]); im = bg
                im = im.convert("RGB")
                if crop: im = im.crop((int(crop[0] * im.width), int(crop[1] * im.height), int(crop[2] * im.width), int(crop[3] * im.height)))
                DOCS[k_] = sk_image(im)
            except Exception as ex:
                print("doc load fail", f_, ex); DOCS[k_] = None

MAP_CY = 820   # map vertical centre in design space (upper-middle, clear of Shorts UI)
def scr(cam, lon, lat):
    x, y = to_screen(cam, lon, lat); return x, y - DH / 2 + MAP_CY

