"""2-minute SEAMLESS demo (one continuous camera, no cuts): Khilafat VO 397.55 - 521.4 s, 360p review.

One 3D camera flies over the parchment map the whole time. At every event it dives to the place, the scene card
rises from the map (pop-up book) and fills the frame exactly, the cartoon battle plays on a REAL photo of that place,
then the card shrinks back into the map and the camera flies on. Documents (Wikipedia proofs, the Mewar scroll)
flip in over the map or the scene, a 3D camera moves across them to the highlighted line, and they flip out.
Floating flags show who ruled each place at that time (andaazan / pratik).

  python3 demo_seam.py stills out t1 t2 ...  |  python3 demo_seam.py sfx  |  python3 demo_seam.py video out.mp4 640 30 a b
"""
import os, sys, json, math, subprocess
HERE0 = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE0)
import demo60 as d6
from demo60 import *
from battle2d import *
from battle_scenes import *
from cam3d import *
from PIL import Image, ImageFilter, ImageEnhance
DS = os.path.dirname(os.path.abspath(__file__))

VO_END2 = 521.4; END = VO_END2 - T0 + 1.8
U_ = d6.U
u_nav, u_patra, u_pakka, u_isme, u_haraa = d6.u_nav, d6.u_patra, d6.u_pakka, d6.u_isme, d6.u_haraa
u_740, u_hakam, u_chittor, u_mewar, u_halaanki, u_743, u_khatam = d6.u_740, d6.u_hakam, d6.u_chittor, d6.u_mewar, d6.u_halaanki, d6.u_743, d6.u_khatam
u_raaz3, u_baar, u_alag, u_blank = d6.u_raaz3, d6.u_baar, d6.u_alag, d6.u_blank
u_bigsam, u_851, u_3000, u_kahan, u_nazar, u_jal = U_("Yahi Pratihara"), U_("Sau saal se"), U_("Ab yaad karo"), U_("Wo kahan gaye"), U_("Iske liye India"), U_("Kyunki usi waqt")
u_724, u_pyaas, u_730, u_731, u_732, u_739b, u_740b, u_27k, u_wo3k, u_iraq, u_ghar = (U_("724, Central"), U_("Fauj pyaas"), U_("730:"), U_("731:"), U_("732:"), U_("739:"), U_("740:"),
                                                                                       U_("Sattaais"), U_("Aur wo teen hazaar"), U_("Unhe raaste"), U_("Jab ghar mein"))
PLC = KHP + "visuals/places/"; DOCS = KHP + "visuals/docs/"
DIRT = PLUG + "/engine/examples/storyproof-demo/battle_photoreal.jpg"

# ---------------------------------------------------------------- real place photos as battle backgrounds
_PB = {}
def place_bg(photo, ground="dirt", blur=4, crop=None, tint=None):
    key = (photo, ground, blur, crop)
    if key not in _PB:
        im = Image.open(photo).convert("RGB")
        if crop: W, H = im.size; im = im.crop((int(crop[0] * W), int(crop[1] * H), int(crop[2] * W), int(crop[3] * H)))
        far = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(blur))).enhance(0.9)
        if tint: far = Image.blend(far, Image.new("RGB", far.size, tint), 0.15)
        gsrc = {"dirt": (DIRT, (0.40, 0.80, 0.74, 1.0)), "sand": (PLC + "karakum.jpg", (0.1, 0.72, 0.9, 1.0)), "grass": (PLC + "vouneuil.jpg", (0.0, 0.84, 1.0, 1.0)),
                "rock": (PLC + "zarafshan.jpg", (0.0, 0.8, 1.0, 1.0))}[ground]
        gi = Image.open(gsrc[0]).convert("RGB"); W, H = gi.size; b = gsrc[1]
        g = np.asarray(gi.crop((int(b[0] * W), int(b[1] * H), int(b[2] * W), int(b[3] * H))).resize((1920, 400), Image.BICUBIC).convert("RGBA")).copy()
        g[..., 3] = (np.clip(np.linspace(0, 1.7, 400), 0, 1) ** 1.4 * 255).astype(np.uint8)[:, None]
        _PB[key] = (sk_image(far), skia.Image.fromarray(g, colorType=skia.ColorType.kRGBA_8888_ColorType))
    return _PB[key]

def place_draw(c, bg, t, t0, dur, push=(1.0, 1.07)):
    far, ground = bg; k = ease_io(seg(t, t0, t0 + dur)); s = lerp(push[0], push[1], k)
    fw, fh = far.width(), far.height(); cov = max(DW / fw, DH / fh) * s; w, h = fw * cov, fh * cov
    draw_img(c, far, (DW - w) / 2, (DH - h) * 0.55, (DW + w) / 2, (DH - h) * 0.55 + h)
    gs = 1 + (s - 1) * 1.5; gw = DW * gs; draw_img(c, ground, (DW - gw) / 2, DH - 400 * gs, (DW + gw) / 2, DH)

BGS = dict(nav=place_bg(PLC + "saputara.jpg"), hak=place_bg(PLC + "girnar.jpg"), sie=place_bg(PLC + "chittor.jpg", crop=(0, 0, 1, 0.85)),
           bap=place_bg(PLC + "aravalli.jpg", ground="grass"), cav=place_bg(KHP + "visuals/photos/teli_mandir.jpg", crop=(0, 0.05, 1, 0.75)),
           col=place_bg(PLC + "palmyra.jpg"), thirst=place_bg(PLC + "karakum.jpg", ground="sand", blur=2), khazar=place_bg(PLC + "sabalan.jpg", ground="grass"),
           defile=place_bg(PLC + "zarafshan.jpg", ground="rock", blur=3), tours=place_bg(PLC + "vouneuil.jpg", ground="grass", crop=(0, 0, 1, 0.62)),
           akro=place_bg(PLC + "afyon.jpg", crop=(0.05, 0, 0.95, 0.66)), berber=place_bg(PLC + "atlas.jpg", ground="sand", crop=(0, 0.1, 1, 0.7)))
CREDIT = dict(nav="Saputara, Gujarat", hak="Girnar, Saurashtra", sie="Chittorgarh (aaj)", bap="Aravalli, Mewar", cav="Teli ka Mandir, Gwalior (8-9vi sadi)",
              col="Palmyra, Syria", thirst="Karakum, Central Asia", khazar="Sabalan, Ardabil", defile="Zeravshan pahad", tours="Vouneuil-sur-Vienne",
              akro="Afyonkarahisar (Akroinon)", berber="Atlas, Morocco")

# ---------------------------------------------------------------- scenes (each its own choreography) with pop-up windows
#  key: (scene, lon, lat, a = full frame from, b = shrink back from, title, date)
SC = {
    "nav": (NavsariElephants(17.1, 4.8, kw(u_haraa, "haraaya") - 0.4), 72.95, 20.95, 17.4, 21.65, "Navsari", "739 CE"),
    "hak": (Duel(23.9, 3.0, kw(u_hakam, "maara") - 0.15, "arab_gen", "chalukya", "right",
                 bg_battle=Battle(dict(fac="arab", inf=6), dict(fac="chalukya", inf=6), "right", t0=23.9, dur=3.0, t_clash=0.8, t_rout=9, seed=11, base=80),
                 names=("Al-Hakam", "Chalukya senapati")), 70.8, 21.5, 24.2, 26.9, "Saurashtra", "740 CE"),
    "sie": (Siege(28.2, 3.6, kw(u_chittor, "naakaam"), "arab", "rajput"), 74.63, 24.88, 28.5, 31.45, "Chittor", "740 CE · Mori raja"),
    "bap": (Chase(32.7, 3.2, "arab", "rajput", "Bappa Rawal (parampara)"), 73.7, 24.6, 33.0, 35.5, "Bappa Rawal", "Mewar ki parampara"),
    "cav": (Parade(65.3, 8.6, "pratihara"), 79.9, 27.05, 65.6, 73.9, "Sulaiman ki gawahi", "851 CE · Pratihara ghudsawar"),
    "col": (Column(75.4, 2.0, "syrian"), 36.3, 33.5, 75.95, 77.1, "3,000 sainik", "Syria se Sindh ki taraf"),
}
FRONT_T = dict(thirst=us(u_724), khazar=us(u_730), defile=us(u_731), tours=us(u_732), akro=us(u_739b), berber=us(u_740b))
NEXT_T = dict(thirst=us(u_730), khazar=us(u_731), defile=us(u_732), tours=us(u_739b), akro=us(u_740b), berber=us(u_wo3k))
FLOC = dict(thirst=(69.6, 40.3), khazar=(48.3, 38.25), defile=(66.9, 39.65), tours=(0.4, 46.7), akro=(30.54, 38.76), berber=(-5.0, 33.0))
FSC = dict(thirst=lambda a: Encircled(a - 0.3, 3.7, "arab", "turk"), khazar=lambda a: CampSweep(a - 0.3, 2.4, "arab", "khazar"), defile=lambda a: Ambush(a - 0.3, 2.5, "arab", "turk"),
           tours=lambda a: ShieldWall(a - 0.3, 3.1, "frank", "frank_lead", "arab", leader_name="Charles Martel"), akro=lambda a: Wedge(a - 0.3, 2.2, "byzantine", "arab", leader_name="Leo III"),
           berber=lambda a: DuneAmbush(a - 0.3, 4.8, "berber", "syrian", t_pop_abs=a + 0.4))
FTXT = dict(thirst=("Day of Thirst", "724 · Central Asia"), khazar=("Khazar", "730 · Ardabil"), defile=("Battle of the Defile", "731 · Samarkand"), tours=("Tours", "732 · France"),
            akro=("Akroinon", "739-740 · Byzantine"), berber=("Berber baghaawat", "740 · North Africa"))
for k_ in FRONT_T:
    a_ = FRONT_T[k_] + 1.4; b_ = NEXT_T[k_] - 0.9
    SC[k_] = (FSC[k_](a_), FLOC[k_][0], FLOC[k_][1], a_, b_, FTXT[k_][0], FTXT[k_][1])
POP_RISE, POP_FILL, POP_OUT, POP_FOLD = 0.75, 0.35, 0.35, 0.45

# ---------------------------------------------------------------- the one continuous camera path (time, lon, lat, dist, pitch, yaw)
KF = [(0.0, 75, 24, 95, 8, 0), (2.6, 73, 22, 24, 45, -10), (6.0, 72.4, 22.2, 17, 52, 4), (11.4, 72.0, 22.4, 16, 50, 2), (12.2, 70.5, 23.6, 14, 50, -8),
      (15.0, 72.3, 21.5, 10, 55, -4)]
def add_scene_kf(key, approach=1.1):
    sc, lo, la, a, b, *_ = SC[key]
    KF.append((a - POP_FILL - POP_RISE - 0.15, lo, la - 0.8, 9, 55, 0)); KF.append((a, lo, la - 0.4, 6.5, 58, 0)); KF.append((b + POP_OUT, lo, la - 0.4, 6.5, 58, 0))
for k_ in ("nav", "hak", "sie", "bap"): add_scene_kf(k_)
KF += [(37.0, 72.5, 23.5, 15, 50, -6), (43.0, 72.8, 23.0, 14, 52, 4), (45.6, 77.5, 22, 30, 45, 0), (50.8, 78.5, 23, 27, 48, 8), (58.6, 77.5, 23, 24, 48, 0),
       (59.2, 70.5, 25.0, 15, 52, -10), (64.0, 86, 24.5, 15, 52, 10)]
add_scene_kf("cav")
KF += [(74.9, 58, 30, 45, 45, 0)]
add_scene_kf("col")
KF += [(79.6, 38, 33, 78, 50, 0), (84.3, 38, 33, 78, 50, 4)]
prev_end = 84.3
for k_ in FRONT_T:
    sc, lo, la, a, b, *_ = SC[k_]
    KF.append((a - POP_FILL - POP_RISE - 0.15, lo, la - 0.8, 9, 55, 0)); KF.append((a, lo, la - 0.4, 6.5, 58, 0)); KF.append((b + POP_OUT, lo, la - 0.4, 6.5, 58, 0))
KF += [(115.0, 50, 30, 32, 50, 0), (119.5, 50, 30, 32, 50, 4), (122.5, 38, 32, 80, 50, 6), (END, 38, 32, 84, 50, 8)]
KF.sort(key=lambda k: k[0])
def camera(t):
    if t <= KF[0][0]: return Cam(*KF[0][1:])
    for i in range(len(KF) - 1):
        a, b = KF[i], KF[i + 1]
        if a[0] <= t <= b[0]:
            k = (t - a[0]) / max(1e-6, b[0] - a[0])
            ca, cb = Cam(*a[1:]), Cam(*b[1:])
            far = math.hypot(a[1] - b[1], a[2] - b[2])
            cm = Cam.lerp(ca, cb, k)
            if far > 12:                                     # long flights arc up (like a plane), then come down
                hop = math.sin(math.pi * ease_io(k)); return Cam(cm.lon, cm.lat, cm.dist * (1 + hop * far / 14), cm.pitch - 8 * hop, cm.yaw)
            return cm
    return Cam(*KF[-1][1:])

# ---------------------------------------------------------------- documents that flip in over the map / scene
def hlboxes(key, img, which=None):
    js = json.load(open(DOCS + key + ".json")); W, H = img.width(), img.height(); out = []
    for gi, g in enumerate(js["lines"]):
        if which is not None and gi not in which: continue
        for q in g: out.append((q["x0"] / W, (q["y"] - 3) / H, q["x1"] / W, (q["y"] + q["h"]) / H))
    return out
DIMG = {k: sk_image(Image.open(DOCS + k + ".png")) for k in ("navsari_plate_w", "pratihara_mlechcha_w", "blankinship_w", "pratihara_cavalry_w")}
def phrase_boxes(key):
    img = DIMG[key]; js = json.load(open(DOCS + key + ".json")); W, H = img.width(), img.height()
    return [[(q["x0"] / W, (q["y"] - 3) / H, q["x1"] / W, (q["y"] + q["h"]) / H) for q in (g or [])] for g in js["lines"]]
def doc_vo(key, t_in, t_out, words, rest_w=0.72, source=""):
    """words = [(phrase index in the capture, time the VO says it)] - each phrase is highlighted exactly on its VO word."""
    P = phrase_boxes(key)
    return dict(img=DIMG[key], t_in=t_in, t_out=t_out, rest_w=rest_w, source=source, ph=[(P[i], tw) for i, tw in words])
KUTCH = kw(u_isme, "Sindh") + 0.5
DOCS_ON = [   # the highlight follows the narration word by word (Hinglish VO -> the matching words of the source)
    doc_vo("navsari_plate_w", us(u_pakka) - 0.1, kw(u_isme, "Navsari") + 0.55,
           [(0, kw(u_pakka, "saboot")), (1, kw(u_isme, "Tajik")), (2, kw(u_isme, "Sindh")), (3, KUTCH), (4, kw(u_isme, "Saurashtra")), (5, kw(u_isme, "Navsari"))],
           source="Saboot: en.wikipedia.org - Avanijanashraya Pulakeshin (Navsari taamra patra, 739)"),
    doc_vo("pratihara_mlechcha_w", kw(u_baar, "lade") - 0.5, ue(u_alag) + 0.1, [(1, kw(u_baar, "lade")), (0, kw(u_alag, "raja"))],
           source="Saboot: en.wikipedia.org - Gurjara-Pratihara dynasty (Gwalior lekh)"),
    doc_vo("blankinship_w", ue(u_alag) + 0.75, kw(u_blank, "hamlon") - 0.1, [(1, kw(u_blank, "historian")), (0, kw(u_blank, "Blankinship"))],
           source="Khalid Y. Blankinship, The End of the Jihad State (1994)"),
    doc_vo("pratihara_cavalry_w", kw(u_851, "851") - 0.4, ue(u_851) - 0.15,
           [(1, kw(u_851, "851")), (0, kw(u_851, "Sulaiman")), (2, kw(u_851, "Gurjara")), (3, kw(u_851, "ghudsawaar"))], rest_w=0.66,
           source="Saboot: en.wikipedia.org - Gurjara-Pratihara dynasty (Sulaiman, 851)"),
]
def doc_view(d, t):
    """camera target on the document: the phrase being spoken, zoomed only as far as keeps it inside the frame."""
    ph = d["ph"]
    def target(i):
        if i < 0: return (0.5, 0.5, 1.0)
        bx = ph[i][0]; x0 = min(b[0] for b in bx); x1 = max(b[2] for b in bx); y0 = min(b[1] for b in bx); y1 = max(b[3] for b in bx)
        z = min(0.97 / d["rest_w"], 1.32)                            # full line width always inside the frame (no text cut off)
        return (0.5, (y0 + y1) / 2, z)
    order = sorted(range(len(ph)), key=lambda i: ph[i][1]); cur, prev = -1, -1
    for i in order:
        if t >= ph[i][1] - 0.35: prev, cur = cur, i
    a_, b_ = target(prev), target(cur); k = ease_io(seg(t, (ph[cur][1] - 0.35) if cur >= 0 else 0, (ph[cur][1] + 0.3) if cur >= 0 else 1))
    fx, fy, z = (lerp(a_[j], b_[j], k) for j in range(3))
    m = 1.0 if cur >= 0 or prev >= 0 else 0.0
    return (fx, fy), z, m
def draw_docs(c, t):
    for d in DOCS_ON:
        if d["t_in"] <= t <= d["t_out"] + 0.6:
            k_in = seg(t, d["t_in"], d["t_in"] + 0.6); k_out = seg(t, d["t_out"], d["t_out"] + 0.6)
            hls = []
            for bx, tw in d["ph"]:
                for j, b in enumerate(bx): hls.append(b + (tw + j * 0.35, tw + 0.45 + j * 0.35))
            (fx, fy), z, m = doc_view(d, t)
            c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(110 * k_in * (1 - k_out))))
            doc_card(c, doc_texture(d["img"], hls, t), k_in, k_out, 1.0, (lerp(0.5, fx, m), lerp(0.5, fy, m)), lerp(1.0, z, m) if m else 1.0, tilt=-7, yaw_end=-3, rest_w=d["rest_w"])
            if k_in > 0.9 and t < d["t_out"]: footnote(c, d["source"])
    draw_bappa(c, t)
BAPPA_DOC = dict(t_in=kw(u_mewar, "Bappa") + 0.05, t_move=kw(u_mewar, "Bappa") + 0.6, t_out=kw(u_mewar, "Bappa") + 1.55)

def draw_bappa(c, t):
    b = BAPPA_DOC
    if b["t_in"] <= t <= b["t_out"] + 0.6:
        k_in = seg(t, b["t_in"], b["t_in"] + 0.55); mv = seg(t, b["t_move"], b["t_move"] + 0.9) * (1 - seg(t, b["t_out"] - 0.3, b["t_out"]))
        doc_card(c, BAPPA, k_in, seg(t, b["t_out"], b["t_out"] + 0.55), mv, (0.5, 0.42), 1.5, tilt=-10, rest_w=0.42)
        if k_in > 0.9 and t < b["t_out"]: footnote(c, "Bappa Rawal - Mewar vanshavali scroll, c. 1730-40 (asli, public domain)")

# ---------------------------------------------------------------- what is on the map at time t (period flags, routes, pins, fires)
# ---------------------------------------------------------------- territories (rough extents on modern outlines - andaazan) filled with their ruler's flag
_CP = WM.paths(40)
PRAT = [d6.state_path(n) for n in ["Gujarat", "Rajasthan", "Haryana", "Punjab", "Delhi", "Madhya Pradesh", "Uttar Pradesh", "Uttarakhand", "Bihar", "West Bengal"]]
def _st(n): return d6.state_path(n)
from shapely.geometry import box as _box, shape as _shape
from core import _poly_path
from shapely.ops import unary_union as _uu
def Gc(code): return WM.geoms[code]
def Gs(name): return next(_shape(f["geometry"]) for f in d6.STATES if f["properties"]["name"] == name)
def Bx(g, lon0, lon1, lat0, lat1): return g.intersection(_box(lon0, lat0, lon1, lat1))
def Pth(g): return _poly_path(g.buffer(0), 0.01)
REG = dict(
    umayyad_sindh=Pth(Bx(Gc("PAK"), 66.3, 71.6, 23.3, 28.6)),
    chalukya=Pth(_uu([Bx(Gs("Gujarat"), 72.3, 74.6, 20.0, 22.4), Bx(Gs("Maharashtra"), 72.6, 74.8, 19.2, 21.1)])),
    arab_west=Pth(_uu([Gs("Gujarat"), Gs("Rajasthan")])),
    mori=Pth(Bx(Gs("Rajasthan"), 73.4, 76.6, 23.7, 25.9)),
    pratihara_malwa=Pth(Bx(Gs("Madhya Pradesh"), 74.0, 78.6, 22.0, 25.2)),
    vatapi=Pth(_uu([Gs("Karnataka"), Bx(Gs("Maharashtra"), 73.0, 80.0, 15.5, 19.2)])),
    karkota=Pth(Gs("Jammu and Kashmir")),
    kannauj=Pth(Gs("Uttar Pradesh")),
    pratihara=Pth(_uu([Gs(n) for n in ["Gujarat", "Rajasthan", "Haryana", "Punjab", "Delhi", "Madhya Pradesh", "Uttar Pradesh", "Uttarakhand", "Bihar", "West Bengal"]])),
    umayyad=Pth(_uu([Gc(k) for k in ["ESP", "PRT", "DZA", "TUN", "LBY", "EGY", "SAU", "YEM", "OMN", "ARE", "QAT", "KWT", "IRQ", "SYR", "JOR", "ISR", "LBN", "IRN", "AFG", "TKM", "UZB", "TJK"] if k in WM.geoms] + [Bx(Gc("PAK"), 60, 71.6, 23.3, 30.5)])),
    turgesh=Pth(_uu([Bx(Gc("KAZ"), 60, 80, 40, 46), Gc("KGZ")])),
    khazar=Pth(_uu([Bx(Gc("RUS"), 38, 50, 42, 49), Bx(Gc("KAZ"), 46, 54, 44, 49)])),
    frank=Pth(_uu([Bx(Gc("FRA"), -5, 9, 42, 51.5), Gc("BEL"), Gc("NLD"), Gc("CHE"), Bx(Gc("DEU"), 5, 12, 47, 54)])),
    byz=Pth(_uu([Bx(Gc("TUR"), 26, 40, 36, 42.2), Gc("GRC")])),
    berber=Pth(Gc("MAR")),
)

UMAY = dict(sindh=(68.5, 25.8), damascus=(36.3, 33.5), kufa=(44.4, 32.0), merv=(61.8, 37.6), kairouan=(10.1, 35.7), cordoba=(-4.8, 37.9), egypt=(31.2, 30.0))
def map_layer(c, cam, t):
    sat_a = 1 - seg(t, 3.0, 5.2)
    parchment(c, WM, cam, fills={"IND": (BHAGWA, int(90 + 60 * seg(t, kw(u_blank, "bada"), kw(u_blank, "bada") + 1.0)))})
    if sat_a > 0:
        satellite(c, SAT, cam, int(255 * sat_a))
    # the ruler's flag blended into the land it ruled at that moment (period, andaazan)
    wk = seg(t, us(u_nazar) + 0.4, us(u_nazar) + 1.8)
    arab_w = seg(t, kw(u_isme, "Saurashtra"), us(u_haraa) - 1.0) * (1 - seg(t, kw(u_khatam, "khatam") - 0.4, kw(u_khatam, "khatam") + 0.4))
    terr = [("umayyad_sindh", "umayyad", seg(t, 0.6, 1.6) * (1 - wk)), ("arab_west", "umayyad", arab_w),
            ("chalukya", "varaha", seg(t, kw(u_nav, "Navsari"), kw(u_nav, "Navsari") + 0.9)),
            ("mori", "sun", seg(t, us(u_chittor) - 0.6, us(u_chittor) + 0.3)),
            ("pratihara_malwa", "varaha", seg(t, us(u_baar), us(u_baar) + 0.6) * (1 - seg(t, us(u_bigsam), us(u_bigsam) + 0.5))),
            ("vatapi", "varaha", seg(t, us(u_baar) + 0.3, us(u_baar) + 0.9)), ("karkota", "karkota", seg(t, us(u_baar) + 0.6, us(u_baar) + 1.2)),
            ("kannauj", "kannauj", seg(t, us(u_baar) + 0.9, us(u_baar) + 1.5) * (1 - seg(t, us(u_bigsam) + 1.5, us(u_bigsam) + 2.2))),
            ("pratihara", "varaha", seg(t, us(u_bigsam) + 0.3, kw(u_bigsam, "Bengal") + 0.3)),
            ("umayyad", "umayyad", wk), ("turgesh", "wolf", wk), ("khazar", "khazar", wk), ("frank", "frank", wk), ("byz", "byz", wk), ("berber", "berber", wk)]
    for rk, kind, k in terr:
        if k > 0: flag_region(c, cam, REG[rk], kind, t, k)
    # march: Sindh -> Kutch -> Saurashtra -> Navsari, Umayyad banner travels with the column
    mk = seg(t, kw(u_isme, "Sindh"), kw(u_isme, "Navsari"))
    if 0 < mk and t < SC["nav"][3] + 0.5:
        rr = route(c, cam, [PL["sindh"], PL["kutch"], PL["saur"], PL["navsari"]], mk, "#7A1F1F", 6, True, t)
        if rr:
            pm, L = rr; pos, _ = pm.getPosTan(L * mk); d6.banner_unit(c, pos.x(), pos.y(), t * 6)
        for key, word, off in (("sindh", "Sindh", 0), ("kutch", "Kutch", 0.45), ("saur", "Saurashtra", 0)):
            pin(c, cam, *PL[key], word, seg(t, kw(u_isme, word) + off, kw(u_isme, word) + off + 0.4), t)
    # floating flags of the rulers of that time
    fl = []
    fl.append((68.5, 25.8, "umayyad", "Umayyad Sindh", seg(t, 0.5, 1.2)))
    fl.append((73.0, 21.0, "varaha", "Chalukya", seg(t, kw(u_nav, "Navsari"), kw(u_nav, "Navsari") + 0.6)))
    arab_west = seg(t, kw(u_isme, "Saurashtra"), kw(u_isme, "Saurashtra") + 0.5) * (1 - seg(t, kw(u_khatam, "khatam") - 0.3, kw(u_khatam, "khatam") + 0.4))
    fl.append((71.2, 22.4, "umayyad", "", arab_west)); fl.append((72.9, 26.3, "umayyad", "", arab_west * seg(t, 22, 23)))
    fl.append((74.63, 24.88, "sun", "Mori, Chittor", seg(t, us(u_chittor) - 0.5, us(u_chittor))))
    fl.append((75.8, 23.2, "varaha", "Gurjara-Pratihara", seg(t, us(u_baar), us(u_baar) + 0.5)))
    fl.append((75.7, 15.9, "varaha", "Chalukya Vatapi", seg(t, us(u_baar) + 0.3, us(u_baar) + 0.8)))
    fl.append((74.8, 34.1, "karkota", "Karkota Kashmir", seg(t, us(u_baar) + 0.6, us(u_baar) + 1.1)))
    fl.append((79.9, 27.05, "kannauj", "Kannauj", seg(t, us(u_baar) + 0.9, us(u_baar) + 1.4)))
    for i, (lo, la) in enumerate(((72.3, 25.0), (78.2, 26.2), (85.5, 25.6), (88.2, 23.6))):
        fl.append((lo, la, "varaha", "", seg(t, us(u_bigsam) + 0.6 + i * 0.7, us(u_bigsam) + 1.1 + i * 0.7)))
    wk = seg(t, us(u_nazar) + 0.4, us(u_nazar) + 1.6)
    for nm, (lo, la) in UMAY.items():
        if nm != "sindh": fl.append((lo, la, "umayyad", "Umayyad" if nm == "damascus" else "", wk))
    for lo, la, kd, lb in ((69.6, 41.5, "wolf", "Turgesh"), (46.0, 43.5, "khazar", "Khazar"), (2.3, 47.6, "frank", "Frank"), (32.0, 39.8, "byz", "Byzantine"), (-6.0, 33.6, "berber", "Berber")):
        fl.append((lo, la, kd, lb, wk))
    grow = 1 + 0.35 * seg(t, kw(u_blank, "bada"), kw(u_blank, "bada") + 0.8) * (1 - seg(t, us(u_bigsam), us(u_bigsam) + 1))
    fl.sort(key=lambda f: -(cam.ll(f[0], f[1]) or (0, 0, 1e9))[2])
    for lo, la, kd, lb, k in fl:
        if k > 0: float_flag(c, cam, lo, la, kd, t, k, lb, size=grow if kd in ("varaha", "sun", "karkota", "kannauj") else 1.0)
    if us(u_jal) < t < END:                                 # the whole caliphate burns on six fronts
        for i, (lo, la) in enumerate(FLOC.values()): fire(c, cam, lo, la, t, seg(t, us(u_jal) + 0.3 + i * 0.4, us(u_jal) + 0.7 + i * 0.4), 1.2)
    if t > us(u_wo3k) - 0.3:                                # the 3,000 diverted to Iraq
        bend = kw(u_iraq, "Iraq"); dam, sin_, kuf = (36.3, 33.5), (68.4, 25.4), (44.4, 32.0); mid = ((dam[0] + sin_[0]) / 2, (dam[1] + sin_[1]) / 2)
        if t < bend:
            k = seg(t, us(u_wo3k) + 0.3, bend); rr = route(c, cam, [dam, mid], k, "#FFFFFF", 6, True, t)
            if rr: pm, L = rr; pos, _ = pm.getPosTan(L * k); d6.banner_unit(c, pos.x(), pos.y(), t * 6); text(c, "3,000", pos.x(), pos.y() - 60, 40, "#FFFFFF", SERIF_DISPLAY, "c", 255, shadow=True)
        else:
            k = seg(t, bend, bend + 1.4); rr = route(c, cam, [dam, (mid[0] - 6, mid[1] + 1), kuf], 0.35 + 0.65 * k, "#FFD23F", 6, True, t)
            if rr: pm, L = rr; pos, _ = pm.getPosTan(L * (0.35 + 0.65 * k)); d6.banner_unit(c, pos.x(), pos.y(), t * 6)
            fire(c, cam, *kuf, t, seg(t, bend, bend + 0.5), 1.4)
        pin(c, cam, 68.4, 25.4, "Sindh", seg(t, us(u_wo3k), us(u_wo3k) + 0.5), t)
    pin(c, cam, 72.95, 20.95, "Navsari", seg(t, kw(u_nav, "Navsari"), kw(u_nav, "Navsari") + 0.5) * (1 - seg(t, 16.0, 16.4)), t, sub="Gujarat")

def overlays(c, t):
    """screen-space titles / stamps / the channel's 2D man on top of the map."""
    serif_title(c, "Taamra Patra", 360, 300, 92, seg(t, kw(u_patra, "taambe"), kw(u_patra, "taambe") + 1.2) * (1 - seg(t, us(u_pakka) - 0.4, us(u_pakka))))
    if kw(u_patra, "739") - 0.3 < t < us(u_pakka): timeline_ribbon(c, [738, 739, 740], 1.0, y=96, spacing=200, a=int(255 * seg(t, kw(u_patra, "739") - 0.3, kw(u_patra, "739") + 0.2)))
    if us(u_740) - 0.4 < t < SC["hak"][3] - 1.2:
        timeline_ribbon(c, [738, 739, 740, 741], 1 + seg(t, us(u_740) - 0.1, us(u_740) + 0.5), y=96, spacing=200, vel=1.0 if us(u_740) - 0.1 < t < us(u_740) + 0.5 else 0)
    if us(u_halaanki) - 0.3 < t < us(u_743) + 0.2:
        pill(c, "Pehchaan par historians ek raay nahi", DW / 2 - 200, 200, 38, "#14213D", "#FFFFFF", int(255 * seg(t, us(u_halaanki) + 0.6, us(u_halaanki) + 1.0) * (1 - seg(t, us(u_743) - 0.2, us(u_743)))), fpath=SERIF_TEXT)
    if us(u_743) - 0.3 < t < us(u_raaz3):
        pos = 2 + 3 * seg(t, us(u_743) - 0.1, us(u_743) + 0.6); timeline_ribbon(c, [738, 739, 740, 741, 742, 743], pos, y=96, spacing=200, vel=1.0 if us(u_743) - 0.1 < t < us(u_743) + 0.6 else 0)
    if us(u_khatam) - 0.2 < t < ue(u_khatam) + 0.8:
        for i in range(3): fireworks(c, 600 + i * 380, 380 + (i % 2) * 80, t, kw(u_khatam, "khatam") + i * 0.2, ("#FFD6E8", "#FFE29A", "#BDE0FE")[i])
    rk = seg(t, us(u_raaz3) - 0.1, us(u_raaz3) + 0.5) * (1 - seg(t, us(u_baar) - 0.3, us(u_baar) + 0.1))
    if rk > 0:
        c.drawRect(skia.Rect(0, 0, DW, DH), paint("#0B0B0F", int(170 * rk))); serif_title(c, "RAAZ #3", DW / 2, DH / 2 + 40, 170, seg(t, us(u_raaz3) - 0.05, us(u_raaz3) + 0.8), align="c", col=YEL)
    stamp_slam(c, "BADE + MAZBOOT", DW / 2 - 300, 900, 60, seg(t, kw(u_blank, "mazboot"), kw(u_blank, "mazboot") + 0.35) * (1 - seg(t, us(u_bigsam) - 0.3, us(u_bigsam))), "#1D6F42", -5)
    serif_title(c, "Pratihara Saamrajya", DW / 2, 150, 96, seg(t, us(u_bigsam) + 0.2, us(u_bigsam) + 1.3) * (1 - seg(t, us(u_851) - 0.4, us(u_851))), date="Sindh ki seema se Bengal tak", align="c")
    pill(c, "Poora naksha", DW / 2, 140, 40, "#14213D", "#FFFFFF", int(255 * seg(t, us(u_nazar) + 0.3, us(u_nazar) + 0.8) * (1 - seg(t, us(u_jal) - 0.4, us(u_jal)))), fpath=SERIF_TEXT)
    serif_title(c, "Khilafat har taraf jal rahi thi", DW / 2, 140, 84, seg(t, us(u_jal), us(u_jal) + 1.4) * (1 - seg(t, us(u_724) - 0.3, us(u_724))), align="c")
    for k_ in FRONT_T:
        F0 = FRONT_T[k_]; yr = int(UN[[u_724, u_730, u_731, u_732, u_739b, u_740b][list(FRONT_T).index(k_)]]["text"][:3])
        if F0 - 0.2 < t < SC[k_][3] - 0.2: timeline_ribbon(c, [yr - 1, yr, yr + 1], 1.0, y=80, spacing=180, a=int(255 * seg(t, F0 - 0.2, F0 + 0.2)))
    if kw(u_iraq, "Iraq") < t < us(u_ghar): stamp_slam(c, "RAASTE MEIN HI MOD DIYA", DW / 2, 230, 60, seg(t, kw(u_iraq, "Iraq") + 0.3, kw(u_iraq, "Iraq") + 0.7), "#C1121F", -5)
    if t > us(u_ghar) - 0.2:
        serif_title(c, "Ghar mein aag, Sindh ki kaun sune?", DW / 2, 150, 76, seg(t, us(u_ghar) + 0.2, us(u_ghar) + 1.6), align="c")
        c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(255 * seg(t, VO_END2 - T0 + 0.3, END))))

def scene_draw(c, key, t):
    sc, lo, la, a, b, title, date = SC[key]
    bg = BGS[key]
    if key == "bap": sc.ground_scroll(c, bg, t)
    else: place_draw(c, bg, t, a - 1.2, b - a + 2.4)
    if key == "col": sc.draw(c, t, a=int(255 * (1 - seg(t, us(u_kahan) + 0.1, us(u_kahan) + 0.6))))
    else: sc.draw(c, t)
    serif_title(c, title, DW / 2, 150, 100, seg(t, a - 0.6, a + 0.4), date=date, align="c")
    if key == "nav":
        nk = seg(t, kw(u_haraa, "Avanijanashraya") - 0.2, kw(u_haraa, "Avanijanashraya") + 0.3)
        xy = sc.B.king_xy(t)
        if xy and nk > 0:
            z, dx, dy = sc.B.cam(t); x = sc.B.cx + (xy[0] - sc.B.cx) * z + dx; y = sc.B.g[1] + (xy[1] - sc.B.g[1]) * z + dy
            pill(c, "Avanijanashraya Pulakeshin", x - 330, y - 470 * z, 30, "#14213D", "#FFFFFF", int(255 * nk), fpath=SERIF_TEXT)
        sx, sy = shake(t, kw(u_haraa, "haraaya") + 0.05, 16); c.save(); c.translate(sx, sy)
        stamp_slam(c, "ARAB HAARE", 560, 330, 82, seg(t, kw(u_haraa, "haraaya") - 0.1, kw(u_haraa, "haraaya") + 0.3), "#C1121F", -8); c.restore()
        for i in range(3): fireworks(c, 1250 + i * 170, 260 + (i % 2) * 60, t, kw(u_haraa, "haraaya") + 0.3 + i * 0.2, ("#FFE29A", "#FFD6E8", "#BDE0FE")[i])
    if key == "hak": stamp_slam(c, "AL-HAKAM MAARA GAYA", DW / 2, 470, 64, seg(t, kw(u_hakam, "maara"), kw(u_hakam, "maara") + 0.35), "#C1121F", -6)
    if key == "sie":
        sx, sy = shake(t, sc.tf + 0.05, 14); c.save(); c.translate(sx, sy)
        stamp_slam(c, "GHERAABANDI NAAKAAM", 640, 330, 62, seg(t, sc.tf - 0.1, sc.tf + 0.3), "#C1121F", -6); c.restore()
    if key == "col":
        qk = seg(t, us(u_kahan), us(u_kahan) + 0.4)
        if qk > 0: text(c, "?", DW / 2, 760, 420 * back(qk), "#FFD23F", SERIF_DISPLAY, "c", 255, shadow=True)
    if key == "thirst":
        sk_ = seg(t, us(u_pyaas) - 0.2, us(u_pyaas) + 0.4)
        c.drawCircle(1600, 230, 110, paint("#FFF1A8", int(230 * sk_), blur=30)); c.drawCircle(1600, 230, 70, paint("#FFF8D6", int(255 * sk_)))
    if key == "berber":
        kk = seg(t, kw(u_27k, "Sattaais"), kw(u_27k, "Sattaais") + 0.5)
        if kk > 0: serif_title(c, "27,000 Syrian sainik", DW / 2, 330, 80, kk, align="c", col="#FFD23F")
        stamp_slam(c, "SAAF", DW / 2, 520, 120, seg(t, kw(u_27k, "saaf"), kw(u_27k, "saaf") + 0.3), "#C1121F", -8)
    text(c, "Background: " + CREDIT[key] + " (asli photo)  ·  cartoon: kalpanik chitran", 40, DH - 30, 20, "#FFFFFF", FT_SEMI, "l", 190)

def scene_image(key, t, width):
    h = int(width * 9 / 16); surf = skia.Surface(width, h); cc = surf.getCanvas(); cc.scale(width / DW, width / DW); cc.clear(hexc("#000000"))
    scene_draw(cc, key, t); return surf.makeImageSnapshot()

def active_scene(t):
    for key, (sc, lo, la, a, b, *_r) in SC.items():
        if a - POP_FILL - POP_RISE <= t <= b + POP_OUT + POP_FOLD: return key
    return None

def frame(c, t, width):
    cam = camera(t); key = active_scene(t)
    if key:
        sc, lo, la, a, b, *_r = SC[key]
        if a <= t <= b:
            scene_draw(c, key, t)                                   # the scene owns the full frame (camera "inside" it)
        else:
            map_layer(c, cam, t); overlays(c, t)
            if t < a: rise, fill = seg(t, a - POP_FILL - POP_RISE, a - POP_FILL), seg(t, a - POP_FILL, a)
            else: fill, rise = 1 - seg(t, b, b + POP_OUT), 1 - seg(t, b + POP_OUT, b + POP_OUT + POP_FOLD)
            img = scene_image(key, min(max(t, a - 0.6), b + 0.6), width)
            popup(c, cam, lo, la, img, cam.dist * 0.45, rise, fill)
    else:
        map_layer(c, cam, t); overlays(c, t)
    draw_docs(c, t)
    d6.ai_tag(c) if key and SC[key][3] <= t <= SC[key][4] else None

USER_SFX = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(DS, "sfx_user"))} if os.path.isdir(os.path.join(DS, "sfx_user")) else set()
def sfx_events():
    E = []
    E += [("whoosh", 0.0, -8), ("riser", 0.4, -14), ("pin", kw(u_nav, "Navsari"), -6), ("chime", kw(u_patra, "taambe"), -10), ("tick", kw(u_patra, "739") - 0.2, -10)]
    for d in DOCS_ON: E += [("paper", d["t_in"], -5), ("paper", d["t_out"], -7)] + [("marker", tw, -11) for _, tw in d["ph"]]
    E += [("paper", BAPPA_DOC["t_in"], -5), ("paper", BAPPA_DOC["t_out"], -7)]
    for w in ("Sindh", "Kutch", "Saurashtra"): E.append(("pin", kw(u_isme, w), -9))
    E += [("march_drum", kw(u_isme, "Sindh"), -12)]
    for key, (sc, lo, la, a, b, *_r) in SC.items():
        E += [("whoosh", a - POP_FILL - POP_RISE - 0.2, -8), ("paper", a - POP_FILL - POP_RISE, -9), ("swish", a - POP_FILL, -10), ("swish", b, -11), ("paper", b + POP_OUT, -11)]
        E += [e for e in sc.sfx() if e[0] in USER_SFX]
    E += [("stamp", kw(u_haraa, "haraaya"), -3), ("firework", kw(u_haraa, "haraaya") + 0.3, -10), ("tick", us(u_740) - 0.1, -8), ("stamp", kw(u_hakam, "maara") + 0.1, -5),
          ("stamp", kw(u_chittor, "naakaam"), -4), ("pop", us(u_halaanki), -10), ("tick", us(u_743) - 0.1, -8), ("firework", kw(u_khatam, "khatam"), -9),
          ("firework", kw(u_khatam, "khatam") + 0.35, -11), ("drum_big", us(u_raaz3) - 0.05, -4), ("riser", us(u_baar) - 1.3, -16)]
    E += [("pop", us(u_baar) + i * 0.3, -11) for i in range(4)] + [("stamp", kw(u_blank, "mazboot"), -5)]
    E += [("riser", us(u_bigsam) - 0.6, -16)] + [("pop", us(u_bigsam) + 0.6 + i * 0.7, -11) for i in range(4)]
    E += [("whoosh", us(u_nazar), -7), ("riser", us(u_nazar) + 0.3, -14), ("boom", us(u_jal), -10)] + [("firework", us(u_jal) + 0.3 + i * 0.4, -16) for i in range(6)]
    for k_ in FRONT_T: E += [("tick", FRONT_T[k_] - 0.2, -10)]
    E += [("stamp", kw(u_27k, "saaf"), -4), ("pin", us(u_wo3k), -8), ("march_drum", us(u_wo3k) + 0.4, -10), ("swish", kw(u_iraq, "Iraq"), -8), ("stamp", kw(u_iraq, "Iraq") + 0.3, -4),
          ("boom", us(u_ghar), -12), ("pop", us(u_ghar) + 0.4, -10), ("chime", VO_END2 - T0 + 0.1, -12)]
    return sorted([e for e in E if 0 <= e[1] < END], key=lambda e: e[1])

def render(t, width=640):
    surf = skia.Surface(width, int(width * 9 / 16)); c = surf.getCanvas(); c.scale(width / DW, width / DW); c.clear(hexc("#000000"))
    frame(c, t, width); return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        for ts in sys.argv[3:]: Image.fromarray(render(float(ts), 960)).convert("RGB").save(os.path.join(out, f"t{float(ts):06.2f}.png"))
    elif mode == "sfx":
        json.dump({"end": END, "t0": T0, "vo_end": VO_END2, "events": sfx_events()}, open(os.path.join(DS, "sfx_seam.json"), "w"), indent=1); print("sfx", len(sfx_events()), "end", round(END, 2))
    else:
        out = sys.argv[2]; width = int(sys.argv[3]); fps = int(sys.argv[4]); a_ = int(sys.argv[5]); b_ = int(sys.argv[6]); h = int(width * 9 / 16)
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{width}x{h}", "-r", str(fps), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a_, b_): ff.stdin.write(render(f / fps, width).tobytes())
        ff.stdin.close(); ff.wait(); print("video ok", out, a_, b_)
