"""1-minute story-then-proof demo on the Khilafat VO (Navsari section, VO 397.55 - 456.4 s) - 360p review.

  python3 demo60.py stills out_dir t1 t2 ...    (demo seconds)
  python3 demo60.py video out_noaudio.mp4 [width=640] [fps=30]
  python3 demo60.py sfx                          -> sfx60.json (event list for mix60.py)
Uses the plugin kit storyproof.py, the channel's own 2D man (man2d / king_fig from kh.py) and real proof cards."""
import os, sys, json, math, ast, subprocess
PLUG = os.environ.get("UTA_PLUGIN", "/home/user/Jarvis-assistant-/plugins/unexplored-truth-by-amrit")
sys.path.insert(0, os.path.join(PLUG, "engine", "visuals"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine_wip"))   # work in progress (not in the plugin yet)
import numpy as np, skia
from PIL import Image
from shapely.geometry import shape
from core import *
from core import _poly_path
from storyproof import *
KHP = os.environ.get("KH_PROJ", "/home/user/Jarvis-assistant-/amrit-borii/khilafat-india/")

# ---------------------------------------------------------------- VO timing (same rules as kh.py)
UN = json.load(open(KHP + "voice/full_units.json"))["units"]
SIL = [tuple(map(float, l.split())) for l in open(KHP + "voice/full_sil.tsv")]
T0 = 397.55; VO_END = 456.4; END = VO_END - T0 + 1.8
def U(prefix):
    return next(i for i, u in enumerate(UN) if u["text"].lower().startswith(prefix.lower()))
def us(i): return UN[i]["start"] - T0
def ue(i): return UN[i]["end"] - T0
def kw(i, word):
    txt = UN[i]["text"]; p = txt.lower().find(word.lower())
    if p < 0: return us(i)
    est = UN[i]["start"] + (UN[i]["end"] - UN[i]["start"]) * p / max(1, len(txt)); best = None
    for a, b in SIL:
        if UN[i]["start"] < b < UN[i]["end"] and abs(b - est) < 0.35 and (best is None or abs(b - est) < abs(best - est)): best = b
    return (best if best else est) - 0.05 - T0
u_nav, u_patra, u_pakka, u_isme, u_haraa = U("Aur phir aaya Navsari"), U("Navsari mein mila"), U("Ye is poori kahani"), U("Isme likha hai ki Tajik"), U("Aur yahan Chalukya")
u_740, u_hakam, u_chittor, u_mewar, u_halaanki = U("Ek saal baad, 740"), U("Al-Hakam khud"), U("Usi saal Chittor"), U("Mewar ki parampara"), U("Haalaanki unki")
u_743, u_khatam, u_raaz3, u_baar, u_alag, u_blank = U("Aur 743 tak"), U("Rajasthan aur Gujarat ki saari"), U("Raaz number teen"), U("Indian rajya ek baar"), U("Alag alag raja"), U("Aur historian Blankinship")

# ---------------------------------------------------------------- the channel's own 2D man + king (copied from kh.py)
src = open(KHP + "visuals/engine/kh.py").read(); tree = ast.parse(src)
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in ("man2d", "king_fig", "crown"):
        exec(compile(ast.Module([node], []), "kh.py", "exec"), globals())
YEL = PAL["yel"]

# ---------------------------------------------------------------- assets
WM = WorldMap()
SAT = Satellite(0, 150, -35, 65)
STATES = json.load(open(MAPDATA + "states.geojson"))["features"]
def state_path(name):
    g = next(shape(f["geometry"]) for f in STATES if f["properties"]["name"] == name); return _poly_path(g, 0.01)
GUJ, RAJ = state_path("Gujarat"), state_path("Rajasthan")
WEST = skia.Path(GUJ); WEST.addPath(RAJ)
img = lambda p: sk_image(Image.open(p))
BATTLE = img(PLUG + "/engine/examples/storyproof-demo/battle_photoreal.jpg")
DOC_NAV, DOC_PRA, DOC_BLK = (img(KHP + f"visuals/docs/{k}.png") for k in ("navsari", "pratihara_mlechcha", "blankinship"))
JS = {k: json.load(open(KHP + f"visuals/docs/{k}.json")) for k in ("navsari", "pratihara_mlechcha", "blankinship")}
HAKAM = img(KHP + "visuals/photos/hakam_ai.jpg"); BAPPA = img(KHP + "visuals/photos/bappa_scroll.jpg")
def hl_box(key, doc, li=0):
    ln = JS[key]["lines"][li][0]; return (ln["x0"] / doc.width(), (ln["y"] - ln["h"] * 0.05) / doc.height(), ln["x1"] / doc.width(), (ln["y"] + ln["h"] * 0.95) / doc.height())
def window(hl, doc, pad=0.16):
    wn = min(1.0, (hl[2] - hl[0]) + pad); hn = wn * (doc.width() / doc.height()) * 9 / 16
    cx, cy = (hl[0] + hl[2]) / 2, (hl[1] + hl[3]) / 2; cx = min(max(cx, wn / 2), 1 - wn / 2)
    if hn < 1: cy = min(max(cy, hn / 2), 1 - hn / 2)
    return (cx - wn / 2, cy - hn / 2, cx + wn / 2, cy + hn / 2)
def banner_img(w=600, h=400):
    a = np.full((h, w, 4), 255, np.uint8); xs = np.arange(w); sh = (232 + 22 * np.sin(xs / w * 6 * math.pi)).astype(np.uint8)
    a[..., 0] = a[..., 1] = a[..., 2] = sh[None, :]; return skia.Image.fromarray(a, colorType=skia.ColorType.kRGBA_8888_ColorType)
BANNER = banner_img()
BHAGWA = "#E8A23A"
PL = dict(navsari=(72.95, 20.95), sindh=(68.6, 25.6), kutch=(69.9, 23.4), saur=(70.9, 21.9), chittor=(74.63, 24.88), mewar=(73.7, 24.6),
          kannauj=(79.9, 27.05), vatapi=(75.7, 15.9), ujjain=(75.78, 23.18))

def banner_unit(c, x, y, ph):                     # marching Arab column marker: small white banner on a pole
    bob = math.sin(ph) * 3
    c.drawLine(x, y + bob, x, y - 34 + bob, paint("#3A2A1E", 255, stroke=3))
    p = skia.Path(); p.moveTo(x, y - 34 + bob); p.lineTo(x + 26, y - 30 + bob + math.sin(ph * 1.3) * 2); p.lineTo(x, y - 20 + bob); p.close()
    c.drawPath(p, paint("#FFFFFF")); c.drawPath(p, paint("#555555", 255, stroke=1.2))

def label(c, s, x, y, k, size=30, col="#2B1D0E"):
    if k > 0: text(c, s, x, y, size, col, SERIF_DISPLAY, "c", int(255 * clamp(k)))

def ai_tag(c, a=255): text(c, "AI chitran · asli tasveer nahi", 40, DH - 30, 20, "#FFFFFF", FT_SEMI, "l", int(a * 0.75))

# ---------------------------------------------------------------- scenes
C_WIDE, C_GUJ, C_WEST, C_NORTH = (73, 23, 14.0), (71.6, 22.6, 30), (71.2, 23.4, 36), (75.5, 24.0, 22)

def sat_scene(c, t):
    cam = cam_lerp(C_WIDE, C_GUJ, seg(t, 0.0, 2.0))
    SAT.draw(c, cam)
    x, y = to_screen(cam, *PL["navsari"])
    pin_drop(c, x, y, "Navsari", "Gujarat", seg(t, kw(u_nav, "Navsari"), kw(u_nav, "Navsari") + 0.6), t)
    region_glow(c, cam, GUJ, seg(t, kw(u_nav, "Navsari"), kw(u_nav, "Navsari") + 0.6), t)
    kt = seg(t, kw(u_patra, "taambe"), kw(u_patra, "taambe") + 1.2)
    serif_title(c, "Taamra Patra", 360, 300, 92, kt, date=None)
    if t > kw(u_patra, "739") - 0.3:
        timeline_ribbon(c, [738, 739, 740], 1.0, y=96, spacing=200, a=int(255 * seg(t, kw(u_patra, "739") - 0.3, kw(u_patra, "739") + 0.2)))

def proof_nav(c, t):                              # "sabse pakka saboot" -> the real Wikipedia line
    hl = hl_box("navsari", DOC_NAV); a0 = us(u_pakka)
    if t < a0 + 1.0:
        sat_scene(c, t); c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(140 * seg(t, a0 - 0.2, a0 + 0.3))))
        doc_fly(c, DOC_NAV, seg(t, a0 - 0.1, a0 + 0.8), (DW / 2 - 700, DH / 2 - 330, DW / 2 + 700, DH / 2 + 330))
        stamp_slam(c, "SABSE PAKKA SABOOT", DW / 2, 190, 64, seg(t, kw(u_pakka, "pakka") - 0.1, kw(u_pakka, "pakka") + 0.3), "#C1121F", -4)
    else:
        doc_pan(c, DOC_NAV, t, a0 + 1.0, 1.4, (0, 0, 1, 1), window(hl, DOC_NAV), highlights=[hl + (a0 + 1.7, a0 + 2.6)])
        footnote(c, "Saboot: en.wikipedia.org - Caliphate campaigns in India")

def parch(c, t):
    """the parchment explainer map (march -> retreat -> kingdoms)."""
    if t < us(u_740): cam = cam_lerp(C_GUJ, C_WEST, seg(t, us(u_isme), us(u_isme) + 1.5))
    elif t < us(u_chittor): cam = C_WEST
    else: cam = cam_lerp(C_WEST, C_NORTH, seg(t, us(u_chittor), us(u_chittor) + 1.4))
    if t > us(u_blank) - 0.5: cam = cam_lerp(C_NORTH, (78, 22, 11.5), seg(t, us(u_blank), us(u_blank) + 2.0))
    parchment_map(c, WM, cam, fills={"IND": (BHAGWA, int(150 + 60 * seg(t, kw(u_blank, "bada"), kw(u_blank, "bada") + 1.0)))})
    P = WM.paths(cam[2])
    # Arab banner: Sindh first, then over Gujarat + Rajasthan while marching; peels off at "khatam"
    flag_fill(c, cam, P["PAK"], BANNER, seg(t, kw(u_isme, "Tajik"), kw(u_isme, "Tajik") + 0.8), t, direction=(1, 0))
    wk = seg(t, kw(u_isme, "Saurashtra"), us(u_haraa))
    if t < kw(u_khatam, "khatam") - 0.6: flag_fill(c, cam, WEST, BANNER, wk, t, direction=(1, 0.2), a=230)
    else: flag_peel(c, cam, WEST, BANNER, seg(t, kw(u_khatam, "khatam") - 0.6, kw(u_khatam, "khatam") + 0.5), direction=(-1, 0.1))
    S = {k: to_screen(cam, *v) for k, v in PL.items()}
    for key, word, off in (("sindh", "Sindh", 0), ("kutch", "Kutch", 0.45), ("saur", "Saurashtra", 0)):
        k_ = seg(t, kw(u_isme, word) + off, kw(u_isme, word) + off + 0.4) * (1 - seg(t, us(u_740) - 0.3, us(u_740)))
        if k_ > 0: pill(c, word, S[key][0] - 110, S[key][1], 32, "#2B1D0E", "#F4EFE4", int(255 * k_), fpath=SERIF_TEXT)
    route_pts = [S["sindh"], S["kutch"], S["saur"], S["navsari"]]
    if t < us(u_740): march(c, route_pts, seg(t, kw(u_isme, "Sindh"), kw(u_isme, "Navsari")), t, n=4, unit=banner_unit, col="#7A1F1F")
    nx, ny = S["navsari"]
    label(c, "Navsari", nx + 70, ny + 34, seg(t, kw(u_isme, "Navsari"), kw(u_isme, "Navsari") + 0.4) * (1 - seg(t, us(u_740), us(u_740) + 0.3)))
    # timeline 739 -> 740 -> 743
    if t > us(u_740) - 0.3:
        pos = 1 + seg(t, kw(u_740, "740") - 0.2, kw(u_740, "740") + 0.4) + 3 * seg(t, kw(u_743, "743") - 0.2, kw(u_743, "743") + 0.5)
        moving = 0 < seg(t, kw(u_740, "740") - 0.2, kw(u_740, "740") + 0.4) < 1 or 0 < seg(t, kw(u_743, "743") - 0.2, kw(u_743, "743") + 0.5) < 1
        tl_a = int(255 * seg(t, us(u_740) - 0.3, us(u_740)) * (1 - seg(t, us(u_raaz3) - 0.3, us(u_raaz3))))
        if tl_a > 0: timeline_ribbon(c, [738, 739, 740, 741, 742, 743], pos, y=96, spacing=200, vel=1.0 if moving else 0, a=tl_a)
    # Al-Hakam: Saurashtra pin + AI portrait card + stamp
    hk = seg(t, us(u_hakam), us(u_hakam) + 0.5) * (1 - seg(t, us(u_chittor) - 0.2, us(u_chittor) + 0.2))
    if hk > 0:
        sx, sy = S["saur"]; pin_drop(c, sx, sy, "Saurashtra", "740 CE", hk, t)
        doc_fly(c, HAKAM, hk, (120, 230, 120 + 340, 230 + 425), frm=(-0.6, 0.1), rot0=20, rot1=3, a=int(255 * hk))
        text(c, "Al-Hakam", 290, 715, 34, "#2B1D0E", SERIF_DISPLAY, "c", int(255 * hk)); text(c, "AI chitran · asli tasveer nahi", 290, 742, 16, "#2B1D0E", FT_SEMI, "c", int(220 * hk))
        stamp_slam(c, "MAARA GAYA", 300, 470, 46, seg(t, kw(u_hakam, "maara"), kw(u_hakam, "maara") + 0.35), "#C1121F", -10)
    # Chittor: pin + neon badge (siege failed)
    ck = seg(t, kw(u_chittor, "Chittor"), kw(u_chittor, "Chittor") + 0.5) * (1 - seg(t, kw(u_mewar, "Bappa") - 0.3, kw(u_mewar, "Bappa") + 0.2))
    if ck > 0:
        cx, cy = S["chittor"]; pin_drop(c, cx, cy, "Chittor", "Mori raja", ck, t)
        def fort(cc, x, y, s):
            for i in range(-2, 3): cc.drawRect(skia.Rect(x + i * s * 0.16 - s * 0.06, y - s * 0.32, x + i * s * 0.16 + s * 0.06, y - s * 0.2), paint("#FFFFFF"))
            cc.drawRect(skia.Rect(x - s * 0.38, y - s * 0.2, x + s * 0.38, y + s * 0.3), paint("#FFFFFF"))
        neon_badge(c, cx - 170, cy - 120, 58, seg(t, kw(u_chittor, "gheraabandi"), kw(u_chittor, "gheraabandi") + 0.4), t, "#FF4D6D", fort, crossed=True)
        stamp_slam(c, "NAAKAAM", cx + 40, cy - 190, 50, seg(t, kw(u_chittor, "naakaam"), kw(u_chittor, "naakaam") + 0.35), "#C1121F", 6)
    # Bappa Rawal: REAL Mewar scroll flies in; the 2D man thinks on "ek raay nahi"
    bk = seg(t, kw(u_mewar, "Bappa"), kw(u_mewar, "Bappa") + 0.8) * (1 - seg(t, us(u_743) - 0.3, us(u_743)))
    if bk > 0:
        doc_fly(c, BAPPA, bk, (1180, 250, 1180 + 460, 250 + 460 * BAPPA.height() / BAPPA.width()), a=int(255 * min(1, bk * 1.5)))
        text(c, "Bappa Rawal · Mewar scroll c. 1730-40 (asli)", 1410, 250 + 460 * BAPPA.height() / BAPPA.width() + 50, 22, "#2B1D0E", FT_SEMI, "c", int(255 * bk))
        mx, my = S["mewar"]; white_arrow(c, mx - 60, my + 10, ang=180, size=90, t=t, k=seg(t, kw(u_mewar, "khadeda") - 0.4, kw(u_mewar, "khadeda") + 0.2))
    man2d(c, 980, 830, 100, t, seg(t, us(u_halaanki), us(u_halaanki) + 0.4) * (1 - seg(t, us(u_743) - 0.2, us(u_743) + 0.2)), "think", -1)
    if us(u_khatam) - 0.2 < t < ue(u_khatam) + 0.6:
        for i, (lo, la) in enumerate(((71.5, 22.5), (73.5, 26.5), (70.5, 24.0))):
            fx, fy = to_screen(cam, lo, la); fireworks(c, fx, fy - 40, t, kw(u_khatam, "khatam") + i * 0.18, ("#FFD6E8", "#FFE29A", "#BDE0FE")[i])
    # Raaz #3: many kingdoms fought -> small pennants + mascots with fists
    if t > us(u_baar) - 0.2:
        pts = [(PL["vatapi"], 0), (PL["kannauj"], 1), (PL["chittor"], 2), (PL["ujjain"], 3), (PL["navsari"], 4), ((77.5, 18.5), 5), ((74.0, 27.5), 6), ((80.5, 23.5), 7)]
        items = [(*to_screen(cam, *ll), PENNANT) for ll, _ in pts]
        flag_markers(c, items, t, kw(u_baar, "baar"), gap=0.18, size=36)
        for j, (ll, mood) in enumerate(((PL["kannauj"], "angry"), (PL["ujjain"], "angry"), (PL["vatapi"], "angry"))):
            ex, ey = to_screen(cam, *ll); gk = seg(t, kw(u_alag, "raja") + j * 0.25, kw(u_alag, "raja") + j * 0.25 + 0.4)
            grow = 1 + 0.5 * seg(t, kw(u_blank, "bada"), kw(u_blank, "bada") + 0.8)
            googly_eyes(c, ex, ey - 30, 17 * grow, t + j, look=(-0.7, 0.2), mood=mood, k=gk)
            if gk > 0.5: glove_hand(c, ex - 48 * grow, ey + 4, 30 * grow, ang=-20 + math.sin(t * 9 + j) * 12, a=int(255 * seg(gk, 0.5, 1)))
        if t > kw(u_alag, "morche") - 0.1: label(c, "Pratihara", to_screen(cam, *PL["kannauj"])[0], to_screen(cam, *PL["kannauj"])[1] + 40, seg(t, kw(u_alag, "morche"), kw(u_alag, "morche") + 0.4), 26)

def pennant_img(w=120, h=80):
    a = np.zeros((h, w, 4), np.uint8); yy, xx = np.mgrid[0:h, 0:w]
    m = (yy > h * 0.5 * xx / w) & (yy < h - h * 0.5 * xx / w); a[m] = (230, 138, 30, 255); return skia.Image.fromarray(a, colorType=skia.ColorType.kRGBA_8888_ColorType)
PENNANT = pennant_img()

def story(c, t):
    """animated story: Navsari 739 - photoreal AI battle ground + the channel's 2D king and 2D men."""
    a0 = us(u_haraa) - 1.2
    story_scene(c, BATTLE, t, a0, 7.0, push=(1.0, 1.12), focus=(0.55, 0.55))
    c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", 40))
    k_in = seg(t, a0 + 0.3, a0 + 0.9)
    king_fig(c, 1430, 930, 260, 0.0, t, robe="#9B2226", face=-1, a=int(255 * k_in))
    for i, (x, pose) in enumerate(((1150, "point"), (1000, "wow"), (850, "wow"))):
        man2d(c, x, 760 + i * 12, 120, t + i, seg(t, a0 + 0.5 + i * 0.15, a0 + 1.0 + i * 0.15), pose, -1)
    crowd_silhouettes(c, 7, DH - 30, t, size=140)
    serif_title(c, "Navsari", DW / 2, 170, 110, seg(t, a0 + 0.4, a0 + 1.6), date="739 CE", align="c")
    nk = seg(t, kw(u_haraa, "Avanijanashraya") - 0.2, kw(u_haraa, "Avanijanashraya") + 0.4)
    if nk > 0:
        pill(c, "Avanijanashraya Pulakeshin", 1430, 560, 30, "#14213D", "#FFFFFF", int(255 * nk), fpath=SERIF_TEXT)
        text(c, "Chalukya raja · 2D chitran", 1430, 612, 20, "#FFFFFF", FT_SEMI, "c", int(230 * nk), shadow=True)
    dx, dy = shake(t, kw(u_haraa, "haraaya") + 0.05, 16)
    c.save(); c.translate(dx, dy); stamp_slam(c, "ARAB HAARE", 560, 420, 78, seg(t, kw(u_haraa, "haraaya") - 0.1, kw(u_haraa, "haraaya") + 0.3), "#C1121F", -8); c.restore()
    for i in range(3): fireworks(c, 1250 + i * 160, 300 + (i % 2) * 60, t, kw(u_haraa, "haraaya") + 0.3 + i * 0.2, ("#FFE29A", "#FFD6E8", "#BDE0FE")[i])
    ai_tag(c)

def proof_pra(c, t):                              # Raaz 3 proof: Gwalior/Pratihara line on Wikipedia
    hl = hl_box("pratihara_mlechcha", DOC_PRA); a0 = us(u_alag) + 0.6
    if t < a0 + 0.9:
        parch(c, t); c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(130 * seg(t, a0 - 0.2, a0 + 0.3))))
        doc_fly(c, DOC_PRA, seg(t, a0 - 0.1, a0 + 0.8), (DW / 2 - 700, DH / 2 - 260, DW / 2 + 700, DH / 2 + 260 * 1.0))
    else:
        doc_pan(c, DOC_PRA, t, a0 + 0.9, 1.0, (0, 0, 1, 1), window(hl, DOC_PRA, 0.3), highlights=[hl + (a0 + 1.4, a0 + 2.1)])
        footnote(c, "Saboot: en.wikipedia.org - Gurjara-Pratihara dynasty")

def blank(c, t):
    parch(c, t)
    a0 = kw(u_blank, "Blankinship") - 0.2; k_ = seg(t, a0, a0 + 0.8)
    doc_fly(c, DOC_BLK, k_, (DW - 980, 120, DW - 80, 120 + 900 * DOC_BLK.height() / DOC_BLK.width()), frm=(0.8, -0.5), rot0=-14, rot1=-2)
    if k_ > 0.6: text(c, "Khalid Yahya Blankinship · The End of the Jihad State (1994)", DW - 530, 120 + 900 * DOC_BLK.height() / DOC_BLK.width() + 46, 22, "#2B1D0E", FT_SEMI, "c", int(255 * seg(k_, 0.6, 1)))
    stamp_slam(c, "BADE + MAZBOOT", DW / 2 - 300, 900, 60, seg(t, kw(u_blank, "mazboot"), kw(u_blank, "mazboot") + 0.35), "#1D6F42", -5)

def frame(c, t):
    c.clear(hexc("#000000"))
    if t < us(u_pakka) - 0.2: sat_scene(c, t)
    elif t < us(u_isme) - 0.1: proof_nav(c, t)
    elif t < us(u_isme) + 0.6:
        style_wipe(c, seg(t, us(u_isme) - 0.1, us(u_isme) + 0.6), lambda cc: proof_nav(cc, t), lambda cc: parch(cc, t), to_left=True)
    elif t < us(u_haraa) - 1.2:
        parch(c, t); iris(c, seg(t, us(u_haraa) - 1.7, us(u_haraa) - 1.2), t=t)
    elif t < us(u_740) - 0.1:
        story(c, t); iris(c, 1 - seg(t, us(u_haraa) - 1.2, us(u_haraa) - 0.8), t=t); iris(c, seg(t, us(u_740) - 0.5, us(u_740) - 0.1), t=t)
    elif t < us(u_raaz3) - 0.1:
        parch(c, t); iris(c, 1 - seg(t, us(u_740) - 0.1, us(u_740) + 0.3), t=t)
    elif t < us(u_baar) - 0.1:                                           # "Raaz number teen" title card
        parch(c, t); c.drawRect(skia.Rect(0, 0, DW, DH), paint("#0B0B0F", 200))
        serif_title(c, "RAAZ #3", DW / 2, DH / 2 + 40, 170, seg(t, us(u_raaz3) - 0.05, us(u_raaz3) + 0.8), align="c", col=YEL)
    elif t < us(u_alag) + 0.5: parch(c, t)
    elif t < us(u_blank) - 0.2: proof_pra(c, t)
    else:
        blank(c, t)
        if t > VO_END - T0: c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(255 * seg(t, VO_END - T0 + 0.2, END))))

def sfx_events():
    """(name, demo_time, gain_db) for mix60.py"""
    E = [("whoosh", 0.0, -8), ("pin", kw(u_nav, "Navsari"), -6), ("chime", kw(u_patra, "taambe"), -10), ("tick", kw(u_patra, "739") - 0.2, -10),
         ("paper", us(u_pakka) - 0.1, -6), ("stamp", kw(u_pakka, "pakka"), -4), ("whoosh", us(u_pakka) + 1.0, -10), ("marker", us(u_pakka) + 1.7, -10),
         ("swish", us(u_isme) - 0.1, -6), ("pop", kw(u_isme, "Tajik"), -8)]
    for w in ("Sindh", "Kutch", "Saurashtra"): E.append(("pop", kw(u_isme, w), -9))
    for k_ in range(10): E.append(("drum", kw(u_isme, "Sindh") + k_ * 0.45, -14))
    E += [("boom", us(u_haraa) - 1.6, -8), ("battle", us(u_haraa) - 1.2, -9), ("stamp", kw(u_haraa, "haraaya"), -3),
          ("firework", kw(u_haraa, "haraaya") + 0.3, -10), ("firework", kw(u_haraa, "haraaya") + 0.7, -12),
          ("boom", us(u_740) - 0.5, -10), ("tick", kw(u_740, "740") - 0.2, -8), ("pin", us(u_hakam), -7), ("paper", us(u_hakam), -9),
          ("stamp", kw(u_hakam, "maara"), -5), ("pin", kw(u_chittor, "Chittor"), -7), ("pop", kw(u_chittor, "gheraabandi"), -8),
          ("stamp", kw(u_chittor, "naakaam"), -5), ("paper", kw(u_mewar, "Bappa"), -6), ("whoosh", kw(u_mewar, "khadeda") - 0.4, -10),
          ("pop", us(u_halaanki), -10), ("tick", kw(u_743, "743") - 0.2, -8), ("swish", kw(u_khatam, "khatam") - 0.6, -8),
          ("firework", kw(u_khatam, "khatam"), -9), ("firework", kw(u_khatam, "khatam") + 0.35, -11),
          ("drum_big", us(u_raaz3) - 0.05, -4), ("riser", us(u_baar) - 1.3, -16)]
    for i in range(8): E.append(("pop", kw(u_baar, "baar") + i * 0.18, -12))
    E += [("pop", kw(u_alag, "raja"), -10), ("pop", kw(u_alag, "raja") + 0.25, -10), ("pop", kw(u_alag, "raja") + 0.5, -10),
          ("paper", us(u_alag) + 0.5, -6), ("marker", us(u_alag) + 2.0, -10), ("paper", kw(u_blank, "Blankinship") - 0.2, -8),
          ("stamp", kw(u_blank, "mazboot"), -5), ("chime", VO_END - T0 + 0.1, -12)]
    return E

def render(t, width=640):
    surf = skia.Surface(width, int(width * 9 / 16)); c = surf.getCanvas(); c.scale(width / DW, width / DW)
    frame(c, t); return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        for ts in sys.argv[3:]: Image.fromarray(render(float(ts), 960)).convert("RGB").save(os.path.join(out, f"t{float(ts):05.2f}.png"))
    elif mode == "sfx":
        json.dump({"end": END, "t0": T0, "vo_end": VO_END, "events": sfx_events()}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx60.json"), "w"), indent=1); print("sfx", len(sfx_events()))
    else:
        out = sys.argv[2]; width = int(sys.argv[3]) if len(sys.argv) > 3 else 640; fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
        a_ = int(sys.argv[5]) if len(sys.argv) > 5 else 0; b_ = int(sys.argv[6]) if len(sys.argv) > 6 else int(END * fps)
        h = int(width * 9 / 16)
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{width}x{h}", "-r", str(fps), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a_, b_): ff.stdin.write(render(f / fps, width).tobytes())
        ff.stdin.close(); ff.wait(); print("video ok", out, a_, b_)
