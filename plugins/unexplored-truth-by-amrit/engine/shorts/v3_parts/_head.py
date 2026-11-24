"""AMRIT BORII Short - 'Indian Ocean ka naam India pe kyun?'  9:16, design 1080x1920 drawn x2 into 2160x3840.
Built from _head.py + _helpers_block.py + _tail.py (cat > short_storyboard.py).
Timing comes from voice/full_units.json (aligned VO). CLI:  python3 short_storyboard.py still OUTDIR t1 t2 ...
"""
import os, sys, json, math, re
os.environ.setdefault("AB_PROJECT", "ocean-naam"); os.environ.setdefault("AB_ORIENT", "vertical")
from core import *
from core import _poly_path
from widgets import *
from shapely.geometry import shape, Polygon
from PIL import Image

ROOT = PROJ
HERE = os.path.dirname(os.path.abspath(__file__))
EMP, EMP_PATH = {}, {}
COL = dict(NOW="#FF9933", RIVER="#4FC3F7", MAURYA="#C9A24A", SEA="#7FDBFF", RED="#FF6B6B", CHINA="#FF8A65", EURO="#8FB8FF")
# South-Asian polities per era (historical-basemaps, approximate) - drawn in bhagwa shades in the historical scenes
ERAS = {k: [(f["name"], shape(f["geom"])) for f in v] for k, v in json.load(open(os.path.join(HERE, "eras2.geojson.json"))).items()}
ERA_PATH = {k: [(n, _poly_path(g, 0)) for n, g in v] for k, v in ERAS.items()}
ERA_LABEL = {"CE100": "c. 100 CE ka naksha", "CE1400": "c. 1400 ka naksha", "CE1500": "c. 1500 ka naksha"}
BHAGWA = ["#FF9933", "#F28A22", "#FFB054", "#E67A16", "#FFA347", "#F59B3A"]
# rough Indian Ocean outline (land is drawn over it, so it may overlap coasts); used for the ocean glow
IO_POLY = Polygon([(32.3, 30.2), (35.5, 27), (43.5, 13.5), (48, 30.5), (57, 27.5), (62, 25.5), (67, 25), (72, 23), (77, 26),
                   (90, 24.5), (94.5, 19), (98.5, 15), (99, 6), (101.5, 2.5), (104.5, -4), (106, -7), (115, -9), (124, -10),
                   (129, -12), (131, -20), (138, -34), (146.9, -39), (146.9, -60), (20, -60), (20, -34.8), (27, -30),
                   (36, -10), (41, 2), (38, 15)])
IO_PATH = _poly_path(IO_POLY, 0)
# real ocean shapes (Natural Earth marine polygons, merged) + Europe outline: lit up on their words
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
SCENES = [("hook", 0), ("size", 3), ("others", 4), ("never", 9), ("sanskrit", 10), ("greek", 11), ("china", 12), ("europe", 13),
          ("latin", 14), ("why", 16), ("hindi", 19), ("cta", 20)]
TAIL = 1.9
T_TOTAL = round(VO_DUR + TAIL, 2)
SC_T = {}
for n_, (k_, u_) in enumerate(SCENES):
    a_ = 0.0 if n_ == 0 else us(u_) - 0.12
    b_ = (us(SCENES[n_ + 1][1]) - 0.12) if n_ + 1 < len(SCENES) else T_TOTAL
    SC_T[k_] = (a_, b_)
def T(k): return SC_T[k]

# phrase captions straight from the VO text (<= ~4 words, split at commas), keywords in yellow
CAP_KEYS = {"indian", "ocean", "india", "mahasagar", "paanch", "ek", "desh", "teesra", "7", "crore", "atlantic", "atlas", "pacific",
            "shaant", "arctic", "bhaalu", "southern", "dakshin", "hamesha", "sanskrit", "ratnakara", "ratnon", "2000", "greek",
            "periplus", "erythraean", "laal", "samudra", "1400", "china", "zheng", "he", "western", "paschim", "europe", "eastern",
            "poorab", "1515", "latin", "oceanus", "orientalis", "indicus", "poorbi", "teer", "beech", "hindi", "hind", "comment", "subscribe"}
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
RULER_INFO = {"zhenghe": ("ZHENG HE KE JAHAZ", "Wubei Zhi woodblock, 17vi sadi (maana jaata hai)",
                          "Wubei Zhi woodblock print - public domain (Wikimedia Commons)", (0.0, 0.0, 1.0, 1.0))}
CARY_CROP = (0.1, 0.5, 0.85, 0.98)   # set after looking at the map: region around the 'SOUTHERN OCEAN' label
def load():
    global LOGO
    if LOGO is None:
        LOGO = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_800.png").resize((200, 200)))
        for k_, f_, crop in (("periplus", "periplus_map.jpg", None), ("atlas", "atlas.jpg", (0.08, 0.0, 0.92, 0.47)),
                             ("pacifici", "maris_pacifici.jpg", None), ("ursa", "ursa_major.jpg", None),
                             ("cary", "cary1806.jpg", CARY_CROP), ("ramayana", "ramayana_lanka.jpg", None)):
            try:
                im = Image.open(ROOT + "visuals/photos/" + f_).convert("RGB")
                if crop: im = im.crop((int(crop[0] * im.width), int(crop[1] * im.height), int(crop[2] * im.width), int(crop[3] * im.height)))
                DOCS[k_] = sk_image(im)
            except Exception: DOCS[k_] = None
        try: RULER["zhenghe"] = sk_image(Image.open(ROOT + "visuals/photos/zhenghe_ships.gif").convert("RGB"))
        except Exception: RULER["zhenghe"] = None

MAP_CY = 820   # map vertical centre in design space (upper-middle, clear of Shorts UI)
def scr(cam, lon, lat):
    x, y = to_screen(cam, lon, lat); return x, y - DH / 2 + MAP_CY

