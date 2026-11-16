"""AMRIT BORI Short - 'Bombay ya Mumbai - naam kahan se aaya?'  9:16, design 1080x1920 drawn x2 into 2160x3840.
Timing comes from voice/full_units.json (aligned VO). CLI:  python3 short_storyboard.py still OUTDIR t1 t2 ...
Built from _head.py + _helpers_block.py + _tail.py (cat ... > short_storyboard.py).
"""
import os, sys, json, math, re
os.environ.setdefault("AB_PROJECT", "mumbai-naam"); os.environ.setdefault("AB_ORIENT", "vertical")
from core import *
from core import _poly_path
from widgets import *
from shapely.geometry import shape, Polygon
from PIL import Image

ROOT = PROJ
HERE = os.path.dirname(os.path.abspath(__file__))
from shapely.geometry import Polygon as _P, MultiPolygon as _MP
def _nohole(g): return _P(g.exterior) if g.geom_type == "Polygon" else _MP([_P(q.exterior) for q in g.geoms])
EMP = {k: _nohole(shape(v)) for k, v in json.load(open(os.path.join(HERE, "ancient.geojson.json"))).items()}
EMP_PATH = {k: _poly_path(g, 0) for k, g in EMP.items()}
COL = dict(NOW="#FF9933", SEA="#4FC3F7", GOLD="#E8B84A", MAURYA="#E8B84A", PORT="#3B6FD8", ENG="#D8323A")

# South-Asian polities per era (historical-basemaps, approximate) - bhagwa shades in the historical scenes
_ERA_SKIP = {"Simhala", "Parthian Empire", "Safavid Empire", "Tibet", "Burmese kingdoms", "Pegu", "Shan states", "Saylan",
             "Aceh", "Khiva Khanate", "Bukara Khanate", "Ayutthaya", "Dutch East Indies", "Arakan", "Ava", "Post-Ming Warlords",
             "Ceylon", "Kandy", "Ceylon (Dutch)", "central Asian khanates", "Nepal", "Bhutan", "Lan Na", "Afghanistan", "Persia",
             "Manchu Empire", "Assam", "Burma", "Rattanakosin Kingdom", "Turan", "?", "Suren Kingdom", "Sikkim (Indian princely state)"}
ERAS = {k: [(f["name"], shape(f["geom"])) for f in v if f["name"] not in _ERA_SKIP]
        for k, v in json.load(open(os.path.join(HERE, "eras_mumbai.geojson.json"))).items()}
ERA_PATH = {k: [(n, _poly_path(g, 0)) for n, g in v] for k, v in ERAS.items()}
ERA_LABEL = {"CE200": "c. 200 CE ka naksha", "CE1530": "c. 1530 ka naksha", "CE1650": "c. 1650 ka naksha",
             "CE1815": "c. 1815 ka naksha"}
BHAGWA = ["#FF9933", "#F28A22", "#FFB054", "#E67A16", "#FFA347", "#F59B3A"]

# ---- the seven islands of Bombay (hand-traced, approximate; on screen "andaazan") lon, lat
ISLANDS = {
    "COLABA": [(72.8095, 18.8925), (72.8150, 18.8945), (72.8215, 18.9040), (72.8275, 18.9120), (72.8250, 18.9150),
               (72.8165, 18.9065), (72.8100, 18.8985)],
    "OLD WOMAN'S": [(72.8255, 18.9170), (72.8310, 18.9205), (72.8330, 18.9255), (72.8285, 18.9255), (72.8240, 18.9205)],
    "BOMBAY": [(72.8285, 18.9285), (72.8395, 18.9320), (72.8450, 18.9445), (72.8430, 18.9615), (72.8355, 18.9680),
               (72.8240, 18.9640), (72.8120, 18.9660), (72.8000, 18.9600), (72.7945, 18.9500), (72.8000, 18.9465),
               (72.8100, 18.9520), (72.8180, 18.9480), (72.8220, 18.9380)],
    "MAZAGAON": [(72.8465, 18.9550), (72.8520, 18.9600), (72.8525, 18.9720), (72.8455, 18.9745), (72.8420, 18.9650)],
    "PAREL": [(72.8320, 18.9780), (72.8450, 18.9820), (72.8500, 18.9950), (72.8480, 19.0120), (72.8400, 19.0220),
              (72.8320, 19.0180), (72.8280, 19.0000)],
    "WORLI": [(72.8120, 18.9900), (72.8180, 18.9930), (72.8220, 19.0050), (72.8200, 19.0220), (72.8140, 19.0250),
              (72.8100, 19.0120), (72.8090, 18.9980)],
    "MAHIM": [(72.8360, 19.0300), (72.8460, 19.0320), (72.8500, 19.0420), (72.8450, 19.0500), (72.8360, 19.0480),
              (72.8320, 19.0400)],
}
ISL_ORDER = ["COLABA", "OLD WOMAN'S", "BOMBAY", "MAZAGAON", "WORLI", "PAREL", "MAHIM"]
ISL_PATH = {k: _poly_path(Polygon(v), 0) for k, v in ISLANDS.items()}
ISL_MASK = _poly_path(Polygon([(72.70, 18.86), (72.80, 18.86), (72.88, 18.88), (72.905, 18.96), (72.89, 19.035), (72.865, 19.058),
                               (72.80, 19.062), (72.70, 19.062)]), 0)     # sea painted over today's reclaimed island
MERGED = _poly_path(Polygon(ISLANDS["COLABA"][:4] + [(72.8330, 18.9255), (72.8450, 18.9445), (72.8525, 18.9720), (72.8500, 18.9950),
                                                    (72.8500, 19.0420), (72.8450, 19.0500), (72.8360, 19.0480), (72.8200, 19.0300),
                                                    (72.8090, 18.9980), (72.8120, 18.9700), (72.7945, 18.9500), (72.8100, 18.9520),
                                                    (72.8180, 18.9480), (72.8220, 18.9380), (72.8165, 18.9065), (72.8100, 18.8985)]), 0)
VELLARD = [(72.8130, 18.9800), (72.8150, 18.9880)]     # Hornby Vellard (Worli - Mahalaxmi), approximate

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
SCENES = [("hook", 0), ("islands", 3), ("devi", 6), ("ptolemy", 9), ("portugal", 10), ("myth", 12), ("dowry", 14),
          ("company", 16), ("merge", 18), ("local", 19), ("rename", 20), ("cta", 21)]
TAIL = 1.9
T_TOTAL = round(VO_DUR + TAIL, 2)
SC_T = {}
for n_, (k_, u_) in enumerate(SCENES):
    a_ = 0.0 if n_ == 0 else us(u_) - 0.12
    b_ = (us(SCENES[n_ + 1][1]) - 0.12) if n_ + 1 < len(SCENES) else T_TOTAL
    SC_T[k_] = (a_, b_)
def T(k): return SC_T[k]

# phrase captions straight from the VO text (<= ~4 words, split at commas), keywords in yellow
CAP_KEYS = {"bombay", "good", "bay", "nahi", "devi", "mandir", "saat", "dweep", "colaba", "mahim", "worli", "parel", "koli",
            "mumba", "maha", "amba", "aai", "maa", "mumbai", "2nd", "ptolemy", "heptanesia", "1534", "gujarat", "bahadur",
            "shah", "portugal", "bombaim", "bom", "baim", "khaadi", "galat", "1661", "dahej", "catherine", "england",
            "charles", "ii", "1668", "east", "india", "company", "10", "pound", "1845", "shehar", "marathi", "gujarati",
            "mambai", "1995", "shiv", "sena", "english", "videshi", "comment", "subscribe"}
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
RULER = {}
DOC = {}
RULER_INFO = {  # name, line, credit, crop (x0,y0,x1,y1 as fractions)
    "catherine": ("CATHERINE OF BRAGANZA", "Portugal ki rajkumari - Peter Lely ki painting, c. 1663-65", "Royal Collection, public domain", (0.22, 0.03, 0.78, 0.46)),
    "charles": ("RAJA CHARLES II", "England ke raja - J. M. Wright (ya studio), c. 1660s", "Royal Collection, public domain", (0.20, 0.02, 0.80, 0.50)),
    "bahadur": ("SULTAN BAHADUR SHAH", "Mughal painting, c. 1586-87 - baad ka chitran, asli portrait nahi", "LACMA, public domain", (0.25, 0.0, 0.95, 0.56)),
}
def _load_img(f, crop=None):
    try:
        im = Image.open(ROOT + "visuals/photos/" + f).convert("RGB")
        if crop: im = im.crop((int(crop[0] * im.width), int(crop[1] * im.height), int(crop[2] * im.width), int(crop[3] * im.height)))
        return sk_image(im)
    except Exception:
        return None
def load():
    global LOGO
    if LOGO is None:
        LOGO = sk_image(Image.open(AB_ROOT + "brand/amrit_bori_logo_800.png").resize((200, 200)))
        for k_ in ("catherine", "charles", "bahadur"): RULER[k_] = _load_img(k_ + ".jpg")
        DOC["ptolemy"] = _load_img("ptolemy_map.jpg")
        DOC["bahadur"] = _load_img("bahadur.jpg", (0.0, 0.0, 1.0, 0.72))
        DOC["b1672"] = _load_img("bombay1672.jpg")
        DOC["i1893"] = _load_img("islands1893.jpg", (0.22, 0.36, 0.78, 0.80))
        DOC["devi"] = _load_img("mumbadevi.jpg")

MAP_CY = 820   # map vertical centre in design space (upper-middle, clear of Shorts UI)
def scr(cam, lon, lat):
    x, y = to_screen(cam, lon, lat); return x, y - DH / 2 + MAP_CY

FTEX = {}
FLAG_NOTE = {"GUJ": "PRATIK: GUJARAT SULTANATE (andaazan chitran)", "PRT": "PRATIK: PORTUGAL SHAHI NISHAN (andaazan)",
             "ENG": "PRATIK: ENGLAND - ST GEORGE CROSS", "EIC": "PRATIK: EAST INDIA COMPANY ENSIGN (andaazan)", "NOW": "TIRANGA"}
