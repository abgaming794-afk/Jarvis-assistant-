"""2-minute demo (360p): Khilafat VO 397.55 - 521.4 s in the story-then-proof style WITH 2D cartoon battles for every
war/event and 3D map animation (tilted map, orbit, extruded empires, standing pins, burning fronts).
Reuses demo60.py (first minute's map/proof scenes) + battle2d.py (cartoon battles) + storyproof.py (3D map).

  python3 demo120.py stills out t1 t2 ...
  python3 demo120.py sfx                     -> sfx120.json
  python3 demo120.py video out.mp4 640 30 [a b]"""
import os, sys, json, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import demo60 as d6
from demo60 import *                       # core, storyproof, assets, U/us/kw, man2d/king_fig
from battle2d import *
from battle_scenes import *
from PIL import Image
D120 = os.path.dirname(os.path.abspath(__file__))

VO_END2 = 521.4; END = VO_END2 - T0 + 1.8
u_bigsam, u_851, u_3000, u_kahan, u_nazar, u_jal = U("Yahi Pratihara"), U("Sau saal se"), U("Ab yaad karo"), U("Wo kahan gaye"), U("Iske liye India"), U("Kyunki usi waqt")
u_724, u_pyaas, u_730, u_khaz, u_731, u_def, u_732, u_tours = U("724, Central"), U("Fauj pyaas"), U("730:"), U("Khazaron"), U("731:"), U("Samarkand ke paas"), U("732:"), U("France mein Tours")
u_739b, u_akro, u_740b, u_berb, u_27k, u_wo3k, u_iraq, u_ghar = U("739:"), U("Byzantine sena"), U("740:"), U("North Africa"), U("Sattaais"), U("Aur wo teen hazaar"), U("Unhe raaste"), U("Jab ghar mein")

BATTLE_IMG = PLUG + "/engine/examples/storyproof-demo/battle_photoreal.jpg"
BG_GOLD = prep_battle_bg(BATTLE_IMG)
BG_DESERT = prep_battle_bg(BATTLE_IMG, tint=(235, 200, 120)); BG_COLD = prep_battle_bg(BATTLE_IMG, tint=(120, 150, 200))
BG_GREEN = prep_battle_bg(BATTLE_IMG, tint=(110, 150, 90)); BG_GREY = prep_battle_bg(BATTLE_IMG, tint=(140, 140, 150)); BG_RED = prep_battle_bg(BATTLE_IMG, tint=(200, 110, 80))
DOC_CAV = img(KHP + "visuals/docs/pratihara_cavalry.png"); JS["pratihara_cavalry"] = json.load(open(KHP + "visuals/docs/pratihara_cavalry.json"))
P_STATES = ["Gujarat", "Rajasthan", "Haryana", "Punjab", "Delhi", "Madhya Pradesh", "Uttar Pradesh", "Uttarakhand", "Bihar", "West Bengal"]
PRAT = [state_path(n) for n in P_STATES]
CALIPH_CODES = ["ESP", "PRT", "MAR", "DZA", "TUN", "LBY", "EGY", "SAU", "YEM", "OMN", "ARE", "QAT", "KWT", "IRQ", "SYR", "JOR", "ISR", "PSX", "LBN", "IRN", "AFG", "TKM", "UZB", "TJK", "PAK"]
FRONTS = dict(thirst=(67.0, 40.6), khazar=(48.3, 38.25), defile=(66.9, 39.65), tours=(0.69, 47.39), akroinon=(30.54, 38.76), berber=(-5.0, 33.0))
C_IND3, C_WORLD = (72.5, 23.5, 26), (30, 32, 7.2)

def ttl(c, s, date, k): serif_title(c, s, DW / 2, 150, 104, k, date=date, align="c")

def world3d(c, t, cam, tilt=0.6, rot=0.0, cal_k=1.0, fires=(), extra=None):
    P = WM.paths(cam[2])
    def flat(cc): parchment_map(cc, WM, cam)
    M = map3d(c, flat, tilt, rot)
    if cal_k > 0:
        if not hasattr(world3d, "cal") or world3d.cal[0] != round(cam[2], 2) or world3d.cal[1] != (round(cam[0], 2), round(cam[1], 2)):
            u = None
            for code in CALIPH_CODES:
                if code in P: fp = flat_path(cam, P[code]); u = fp if u is None else skia.Op(u, fp, skia.PathOp.kUnion_PathOp)
            world3d.cal = (round(cam[2], 2), (round(cam[0], 2), round(cam[1], 2)), u)
        extrude(c, M, world3d.cal[2], 26, "#1F9D5C", k=cal_k, top="#2FBF71")
    for key, k in fires:
        x, y = to_screen(cam, *FRONTS[key]); fire3d(c, M, x, y, t, k, 1.0)
    if extra: extra(c, M, cam)
    return M

# ---------------------------------------------------------------- 3D versions of the first-minute map scenes
def sat3d(c, t):
    cam = cam_lerp(d6.C_WIDE, d6.C_GUJ, seg(t, 0.0, 2.2)); tilt = 0.55 * ease_io(seg(t, 0.4, 2.6))
    M = map3d(c, lambda cc: SAT.draw(cc, cam), tilt, rot=-6 * seg(t, 0, 6), sky=("#0B1424", "#7FA7C9"))
    k = seg(t, kw(u_nav, "Navsari"), kw(u_nav, "Navsari") + 0.6)
    extrude(c, M, flat_path(cam, GUJ), 30, "#7EC8F2", k=k, top="#A9DCF7")
    x, y = to_screen(cam, *PL["navsari"]); pin3d(c, M, x, y, "Navsari", k, t, sub="Gujarat")
    serif_title(c, "Taamra Patra", 360, 300, 92, seg(t, kw(u_patra, "taambe"), kw(u_patra, "taambe") + 1.2))
    if t > kw(u_patra, "739") - 0.3:
        timeline_ribbon(c, [738, 739, 740], 1.0, y=96, spacing=200, a=int(255 * seg(t, kw(u_patra, "739") - 0.3, kw(u_patra, "739") + 0.2)))

def march3d(c, t):
    cam = d6.C_WEST; P = WM.paths(cam[2])
    M = map3d(c, lambda cc: d6.parch(cc, t), 0.5 * seg(t, us(u_isme), us(u_isme) + 1.2), rot=4 * seg(t, us(u_isme), us(u_haraa)))

# ---------------------------------------------------------------- cartoon battles (photoreal blurred background)
NAV = NavsariElephants(us(u_haraa) - 1.8, 6.3, kw(u_haraa, "haraaya") - 0.4)
HAK = Duel(us(u_hakam) - 0.2, 3.0, kw(u_hakam, "maara") - 0.15, "arab_gen", "chalukya", "right",
           bg_battle=Battle(dict(fac="arab", inf=6), dict(fac="chalukya", inf=6), "right", t0=us(u_hakam) - 0.2, dur=3.0, t_clash=0.8, t_rout=9, seed=11, base=80),
           names=("Al-Hakam", "Chalukya senapati"))
SIE = Siege(us(u_chittor) - 0.2, 4.5, kw(u_chittor, "naakaam"), "arab", "rajput")
BAP = Chase(us(u_mewar) - 0.1, 4.0, "arab", "rajput", "Bappa Rawal (parampara)")
CAV = Parade(us(u_851) - 0.5, 8.0, "pratihara")
COL = Column(us(u_3000) - 1.0, 4.0, "syrian")
VIG = {   # key: (start_unit, end_time, scene, bg, title, date) - every war has its own choreography and period armies
    "thirst": (u_724, us(u_730) - 0.1, Encircled(us(u_724) + 1.1, 4.4, "arab", "turk"), BG_DESERT, "Day of Thirst", "724 · Central Asia"),
    "khazar": (u_730, us(u_731) - 0.1, CampSweep(us(u_730) + 1.0, 3.4, "arab", "khazar"), BG_COLD, "Khazar", "730 · Ardabil"),
    "defile": (u_731, us(u_732) - 0.1, Ambush(us(u_731) + 1.0, 3.3, "arab", "turk"), BG_GREY, "Battle of the Defile", "731 · Samarkand"),
    "tours": (u_732, us(u_739b) - 0.1, ShieldWall(us(u_732) + 1.0, 4.1, "frank", "frank_lead", "arab", leader_name="Charles Martel"), BG_GREEN, "Tours", "732 · France"),
    "akroinon": (u_739b, us(u_740b) - 0.1, Wedge(us(u_739b) + 1.0, 3.1, "byzantine", "arab", leader_name="Leo III"), BG_GOLD, "Akroinon", "739-740 · Byzantine"),
    "berber": (u_740b, us(u_wo3k) - 0.1, DuneAmbush(us(u_740b) + 1.0, 5.6, "berber", "syrian", t_pop_abs=us(u_berb) + 0.6), BG_RED, "Berber baghaawat", "740 · North Africa"),
}

def king_label(c, t, B, k):
    B = getattr(B, "B", B); xy = B.king_xy(t)
    if xy and k > 0:
        z, dx, dy = B.cam(t); x = B.cx + (xy[0] - B.cx) * z + dx; y = B.g[1] + (xy[1] - B.g[1]) * z + dy
        pill(c, "Avanijanashraya Pulakeshin", x - 330, y - 470 * z, 30, "#14213D", "#FFFFFF", int(255 * k), fpath=SERIF_TEXT)

def navsari_battle(c, t):
    battle_bg(c, BG_GOLD, t, NAV.t0, 7); NAV.draw(c, t)
    ttl(c, "Navsari", "739 CE", seg(t, NAV.t0 + 0.2, NAV.t0 + 1.2) * (1 - seg(t, NAV.t0 + 2.6, NAV.t0 + 3.0)))
    king_label(c, t, NAV, seg(t, kw(u_haraa, "Avanijanashraya") - 0.2, kw(u_haraa, "Avanijanashraya") + 0.3))
    dx, dy = shake(t, kw(u_haraa, "haraaya") + 0.05, 16); c.save(); c.translate(dx, dy)
    stamp_slam(c, "ARAB HAARE", 560, 330, 82, seg(t, kw(u_haraa, "haraaya") - 0.1, kw(u_haraa, "haraaya") + 0.3), "#C1121F", -8); c.restore()
    for i in range(3): fireworks(c, 1250 + i * 170, 260 + (i % 2) * 60, t, kw(u_haraa, "haraaya") + 0.3 + i * 0.2, ("#FFE29A", "#FFD6E8", "#BDE0FE")[i])
    d6.ai_tag(c)

def hakam_battle(c, t):
    battle_bg(c, BG_GOLD, t, HAK.t0, 3.5); HAK.draw(c, t)
    ttl(c, "Saurashtra", "740 CE · Al-Hakam", seg(t, HAK.t0, HAK.t0 + 0.8))
    stamp_slam(c, "AL-HAKAM MAARA GAYA", DW / 2, 470, 64, seg(t, kw(u_hakam, "maara"), kw(u_hakam, "maara") + 0.35), "#C1121F", -6)
    timeline_ribbon(c, [739, 740, 741], 1.0, y=60, spacing=180, a=200); d6.ai_tag(c)

def siege(c, t):
    t0 = SIE.t0; fail = SIE.tf
    battle_bg(c, BG_GOLD, t, t0, 4.5, push=(1.04, 1.1)); SIE.draw(c, t)
    ttl(c, "Chittor", "740 CE · Mori raja", seg(t, t0 + 0.1, t0 + 1.0) * (1 - seg(t, t0 + 2.6, t0 + 3.0)))
    dx, dy = shake(t, fail + 0.05, 14); c.save(); c.translate(dx, dy)
    stamp_slam(c, "GHERAABANDI NAAKAAM", 640, 330, 62, seg(t, fail - 0.1, fail + 0.3), "#C1121F", -6); c.restore()
    d6.ai_tag(c)

def bappa(c, t):
    BAP.ground_scroll(c, BG_GOLD, t); BAP.draw(c, t)
    ttl(c, "Bappa Rawal", "Mewar ki parampara", seg(t, BAP.t0 + 0.2, BAP.t0 + 1.0) * (1 - seg(t, kw(u_mewar, "Bappa") + 0.1, kw(u_mewar, "Bappa") + 0.4)))
    bk = seg(t, kw(u_mewar, "Bappa") + 0.1, kw(u_mewar, "Bappa") + 0.9)
    if bk > 0:
        c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(110 * bk)))
        h = 520; w = h * BAPPA.width() / BAPPA.height()
        doc_fly(c, BAPPA, bk, (DW / 2 - w / 2, 180, DW / 2 + w / 2, 180 + h))
        text(c, "Bappa Rawal · Mewar genealogical scroll c. 1730-40 (asli, public domain)", DW / 2, 180 + h + 56, 24, "#FFFFFF", FT_SEMI, "c", int(255 * bk), shadow=True)
    d6.ai_tag(c)

def doubt(c, t):
    cam = d6.C_NORTH
    M = map3d(c, lambda cc: parchment_map(cc, WM, cam, fills={"IND": (BHAGWA, 170)}), 0.5, rot=3)
    man2d(c, 1350, 820, 150, t, seg(t, us(u_halaanki) - 0.3, us(u_halaanki) + 0.3), "think", -1)
    pill(c, "Pehchaan par historians ek raay nahi", DW / 2 - 180, 200, 40, "#14213D", "#FFFFFF", int(255 * seg(t, kw(u_halaanki, "historians"), kw(u_halaanki, "historians") + 0.4)), fpath=SERIF_TEXT)

def pratihara3d(c, t):
    a0 = us(u_bigsam) - 0.1; cam = cam_lerp(d6.C_NORTH, (80, 25, 30), seg(t, a0, a0 + 2))
    M = map3d(c, lambda cc: parchment_map(cc, WM, cam, fills={"IND": ("#F3E3C0", 255)}), 0.5, rot=-5 + 6 * seg(t, a0, a0 + 5.5))
    for i, pth in enumerate(PRAT):
        extrude(c, M, flat_path(cam, pth), 34, BHAGWA, k=seg(t, a0 + 0.6 + i * 0.32, a0 + 1.2 + i * 0.32), top="#F4B860", glow=(i == len(PRAT) - 1))
    x, y = to_screen(cam, *PL["kannauj"]); pin3d(c, M, x, y, "Kannauj", seg(t, a0 + 1.0, a0 + 1.6), t, sub="Pratihara rajdhani")
    serif_title(c, "Pratihara Saamrajya", DW / 2, 150, 100, seg(t, a0 + 0.3, a0 + 1.4), date="Sindh ki seema se Bengal tak", align="c")

def cavalry(c, t):
    a0 = us(u_851); pk = kw(u_851, "ghudsawaar") + 0.6
    if t < pk:
        battle_bg(c, BG_GOLD, t, a0, 7); CAV.draw(c, t)
        ttl(c, "Sulaiman ki gawahi", "851 CE · Arab vyapari", seg(t, a0 + 0.2, a0 + 1.2))
        d6.ai_tag(c)
    else:
        hl = d6.hl_box("pratihara_cavalry", DOC_CAV)
        if t < pk + 1.0:
            battle_bg(c, BG_GOLD, t, a0, 7); CAV.draw(c, t)
            c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(120 * seg(t, pk, pk + 0.4))))
            doc_fly(c, DOC_CAV, seg(t, pk, pk + 0.9), (DW / 2 - 720, DH / 2 - 240, DW / 2 + 720, DH / 2 + 240))
        else:
            doc_pan(c, DOC_CAV, t, pk + 1.0, 1.1, (0, 0, 1, 1), d6.window(hl, DOC_CAV, 0.3), highlights=[hl + (pk + 1.5, pk + 2.3)])
            footnote(c, "Saboot: en.wikipedia.org - Gurjara-Pratihara dynasty (Sulaiman, 851)")

def column(c, t):
    a0 = us(u_3000) - 0.2; ka = 1 - seg(t, us(u_kahan) + 0.1, us(u_kahan) + 0.6)
    battle_bg(c, BG_GOLD, t, a0, 4); COL.draw(c, t, a=int(255 * ka))
    serif_title(c, "3,000 sainik", DW / 2, 190, 110, seg(t, a0 + 0.2, a0 + 1.0), date="Syria se Sindh ki taraf", align="c")
    qk = seg(t, us(u_kahan), us(u_kahan) + 0.4)
    if qk > 0: text(c, "?", DW / 2, 760, 420 * back(qk), "#FFD23F", SERIF_DISPLAY, "c", 255, shadow=True)
    d6.ai_tag(c)

def world_pull(c, t):
    a0 = us(u_nazar) - 0.1; cam = cam_lerp(C_IND3, C_WORLD, seg(t, a0, a0 + 2.6))
    world3d(c, t, cam, tilt=0.6, rot=-6 + 8 * seg(t, a0, a0 + 3.5), cal_k=seg(t, a0 + 1.2, a0 + 2.6))
    pill(c, "Poora naksha", DW / 2, 140, 40, "#14213D", "#FFFFFF", int(255 * seg(t, a0 + 0.3, a0 + 0.8) * (1 - seg(t, a0 + 2.8, a0 + 3.3))), fpath=SERIF_TEXT)

def fronts(c, t):
    a0 = us(u_jal) - 0.1; keys = list(FRONTS)
    world3d(c, t, C_WORLD, 0.6, rot=2 + 3 * seg(t, a0, a0 + 4), fires=[(k, seg(t, a0 + 0.3 + i * 0.42, a0 + 0.7 + i * 0.42)) for i, k in enumerate(keys)])
    serif_title(c, "Khilafat har taraf jal rahi thi", DW / 2, 140, 84, seg(t, a0, a0 + 1.4), align="c")

def vignette(c, t, key):
    u0, t_end, B, bg, title, date = VIG[key]; a0 = us(u0) - 0.1
    yr = int(UN[u0]["text"][:3])
    if t < a0 + 1.1:                                         # 3D map flies to the front
        lo, la = FRONTS[key]; cam = cam_lerp(C_WORLD, (lo, la, 20), seg(t, a0, a0 + 1.0))
        def ex(cc, M, cm):
            x, y = to_screen(cm, lo, la); pin3d(cc, M, x, y, title, seg(t, a0 + 0.2, a0 + 0.8), t, sub=date)
            fire3d(cc, M, x + 40, y + 10, t, 1.0, 0.8)
        world3d(c, t, cam, 0.62, rot=4, cal_k=1.0, extra=ex)
        timeline_ribbon(c, [yr - 1, yr, yr + 1], 1.0, y=80, spacing=180, a=int(255 * seg(t, a0, a0 + 0.3)))
        iris(c, seg(t, a0 + 0.8, a0 + 1.1), t=t)
        return
    battle_bg(c, bg, t, a0 + 1.1, t_end - a0); B.draw(c, t)
    iris(c, 1 - seg(t, a0 + 1.1, a0 + 1.4), t=t)
    ttl(c, title, date, seg(t, a0 + 1.2, a0 + 2.0))
    if key == "thirst":                                      # blazing sun + no-water badge on "pyaas"
        sk_ = seg(t, us(u_pyaas) - 0.2, us(u_pyaas) + 0.4)
        c.drawCircle(1600, 230, 110, paint("#FFF1A8", int(230 * sk_), blur=30)); c.drawCircle(1600, 230, 70, paint("#FFF8D6", int(255 * sk_)))
        def drop(cc, x, y, s):
            p = skia.Path(); p.moveTo(x, y - s * 0.45); p.cubicTo(x + s * 0.35, y, x + s * 0.3, y + s * 0.38, x, y + s * 0.38); p.cubicTo(x - s * 0.3, y + s * 0.38, x - s * 0.35, y, x, y - s * 0.45); cc.drawPath(p, paint("#7EC8F2"))
        neon_badge(c, 300, 330, 70, sk_, t, "#FF4D6D", drop, crossed=True)
    if key == "berber":
        kk = seg(t, kw(u_27k, "Sattaais"), kw(u_27k, "Sattaais") + 0.5)
        if kk > 0: serif_title(c, "27,000 Syrian sainik", DW / 2, 330, 80, kk, align="c", col="#FFD23F")
        stamp_slam(c, "SAAF", DW / 2, 520, 120, seg(t, kw(u_27k, "saaf"), kw(u_27k, "saaf") + 0.3), "#C1121F", -8)
    d6.ai_tag(c)

def diverted(c, t):
    a0 = us(u_wo3k) - 0.1; cam = (50, 30, 11); bend = kw(u_iraq, "Iraq")
    def ex(cc, M, cm):
        dam = proj(M, *to_screen(cm, 36.3, 33.5)); sin = proj(M, *to_screen(cm, 68.4, 25.4)); kuf = proj(M, *to_screen(cm, 44.4, 32.0))
        pin3d(cc, M, *to_screen(cm, 36.3, 33.5), "Damascus", seg(t, a0, a0 + 0.5), t, col="#1F9D5C")
        pin3d(cc, M, *to_screen(cm, 68.4, 25.4), "Sindh", seg(t, a0 + 0.3, a0 + 0.8), t)
        if t < bend:
            k = seg(t, a0 + 0.6, bend); end = (lerp(dam[0], sin[0], 0.5), lerp(dam[1], sin[1], 0.5))
            march(cc, [dam, end], k, t, n=5, unit=d6.banner_unit, col="#FFFFFF")
            if k > 0: text(cc, "3,000", end[0], end[1] - 70, 44, "#FFFFFF", SERIF_DISPLAY, "c", int(255 * k), shadow=True)
        else:
            k = seg(t, bend, bend + 1.5); mid = (lerp(dam[0], sin[0], 0.5), lerp(dam[1], sin[1], 0.5))
            march(cc, [dam, mid, kuf], 0.5 + 0.5 * k, t, n=5, unit=d6.banner_unit, col="#FFD23F")
            fire3d(cc, M, *to_screen(cm, 44.4, 32.0), t, seg(t, bend, bend + 0.5), 1.1)
            stamp_slam(cc, "RAASTE MEIN HI MOD DIYA", DW / 2, 260, 60, seg(t, bend + 0.3, bend + 0.7), "#C1121F", -5)
    world3d(c, t, cam, 0.58, rot=-3, cal_k=1.0, extra=ex)

def finale(c, t):
    a0 = us(u_ghar) - 0.1
    def ex(cc, M, cm):
        pin3d(cc, M, *to_screen(cm, 68.4, 25.4), "Sindh?", seg(t, a0 + 1.2, a0 + 1.8), t, h=90)
    world3d(c, t, C_WORLD, 0.6, rot=5 * seg(t, a0, END), fires=[(k, 1.0) for k in FRONTS], extra=ex)
    man2d(c, 1560, 860, 150, t, seg(t, a0 + 0.4, a0 + 0.9), "wow", -1)
    serif_title(c, "Ghar mein aag, Sindh ki kaun sune?", DW / 2, 150, 76, seg(t, a0 + 0.2, a0 + 1.6), align="c")
    c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(255 * seg(t, VO_END2 - T0 + 0.3, END))))

def frame(c, t):
    c.clear(hexc("#000000"))
    if t < us(u_pakka) - 0.2: sat3d(c, t); return
    if t < us(u_isme) - 0.1: d6.proof_nav(c, t); return
    if t < us(u_isme) + 0.6: style_wipe(c, seg(t, us(u_isme) - 0.1, us(u_isme) + 0.6), lambda cc: d6.proof_nav(cc, t), lambda cc: march3d(cc, t)); return
    if t < NAV.t0: march3d(c, t); iris(c, seg(t, NAV.t0 - 0.45, NAV.t0), t=t); return
    if t < us(u_740) - 0.1: navsari_battle(c, t); iris(c, 1 - seg(t, NAV.t0, NAV.t0 + 0.35), t=t); iris(c, seg(t, us(u_740) - 0.45, us(u_740) - 0.1), t=t); return
    if t < HAK.t0:
        cam = d6.C_WEST
        def ex(cc, M, cm=cam): pin3d(cc, M, *to_screen(cm, *PL["saur"]), "Saurashtra", seg(t, us(u_740), us(u_740) + 0.5), t, sub="740 CE")
        M = map3d(c, lambda cc: parchment_map(cc, WM, cam, fills={"IND": (BHAGWA, 170)}), 0.55, rot=-3); ex(c, M)
        pos = 1 + seg(t, kw(u_740, "740") - 0.2, kw(u_740, "740") + 0.4)
        timeline_ribbon(c, [738, 739, 740, 741], pos, y=96, spacing=200, vel=1.0 if 0 < seg(t, kw(u_740, "740") - 0.2, kw(u_740, "740") + 0.4) < 1 else 0)
        iris(c, 1 - seg(t, us(u_740) - 0.1, us(u_740) + 0.3), t=t); return
    if t < us(u_chittor) - 0.2: hakam_battle(c, t); return
    if t < us(u_mewar) - 0.1: siege(c, t); return
    if t < us(u_halaanki) - 0.3: bappa(c, t); return
    if t < us(u_743) - 0.3: doubt(c, t); return
    if t < us(u_bigsam) - 0.1: d6.frame(c, t); return                      # 743 -> RAAZ #3 -> pennants -> proof -> Blankinship
    if t < us(u_851): pratihara3d(c, t); return
    if t < us(u_3000) - 0.2: cavalry(c, t); return
    if t < us(u_nazar) - 0.1: column(c, t); return
    if t < us(u_jal) - 0.1: world_pull(c, t); return
    if t < us(u_724) - 0.1: fronts(c, t); return
    for key in ("thirst", "khazar", "defile", "tours", "akroinon", "berber"):
        if t < VIG[key][1]: vignette(c, t, key); return
    if t < us(u_ghar) - 0.1: diverted(c, t); return
    finale(c, t)

def sfx_events():
    E = [e for e in d6.sfx_events() if e[1] < us(u_bigsam) - 0.2 and not (us(u_haraa) - 2 < e[1] < us(u_740)) and not (us(u_hakam) - 0.5 < e[1] < us(u_halaanki))]
    E += [("riser", NAV.t0 - 1.2, -14), ("boom", NAV.t0 - 0.4, -8), ("stamp", kw(u_haraa, "haraaya"), -3), ("firework", kw(u_haraa, "haraaya") + 0.3, -10),
          ("boom", us(u_740) - 0.5, -10), ("tick", kw(u_740, "740") - 0.2, -8), ("pin", us(u_740), -8), ("stamp", kw(u_hakam, "maara") + 0.1, -5),
          ("stamp", kw(u_chittor, "naakaam"), -4), ("paper", kw(u_mewar, "Bappa") + 0.1, -6), ("pop", us(u_halaanki), -10)]
    for sc in (NAV, HAK, SIE, BAP, CAV, COL): E += sc.sfx()
    E += [("riser", us(u_bigsam) - 1.0, -16), ("drum_big", us(u_bigsam) + 0.6, -10)] + [("pop", us(u_bigsam) + 0.6 + i * 0.32, -12) for i in range(10)]
    pk = kw(u_851, "ghudsawaar") + 0.6
    E += [("paper", pk, -6), ("marker", pk + 1.5, -10), ("pop", us(u_kahan), -6), ("whoosh", us(u_nazar), -8), ("riser", us(u_nazar) + 0.4, -14)]
    E += [("firework", us(u_jal) + 0.3 + i * 0.42, -16) for i in range(6)] + [("boom", us(u_jal), -10)]
    for key in VIG:
        u0, _, B, *_ = VIG[key]; a0 = us(u0) - 0.1
        E += [("whoosh", a0, -9), ("pin", a0 + 0.3, -8), ("tick", a0, -10), ("boom", a0 + 0.85, -10)] + B.sfx()
    E += [("stamp", kw(u_27k, "saaf"), -4), ("pin", us(u_wo3k), -8), ("march_drum", us(u_wo3k) + 0.6, -10)]
    E += [("swish", kw(u_iraq, "Iraq"), -8), ("stamp", kw(u_iraq, "Iraq") + 0.3, -4), ("boom", us(u_ghar), -12), ("pop", us(u_ghar) + 0.4, -10), ("chime", VO_END2 - T0 + 0.1, -12)]
    return sorted(E, key=lambda e: e[1])

def render(t, width=640):
    surf = skia.Surface(width, int(width * 9 / 16)); c = surf.getCanvas(); c.scale(width / DW, width / DW)
    frame(c, t); return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        for ts in sys.argv[3:]: Image.fromarray(render(float(ts), 960)).convert("RGB").save(os.path.join(out, f"t{float(ts):06.2f}.png"))
    elif mode == "sfx":
        json.dump({"end": END, "t0": T0, "vo_end": VO_END2, "events": sfx_events()}, open(os.path.join(D120, "sfx120.json"), "w"), indent=1); print("sfx", len(sfx_events()), "end", round(END, 2))
    else:
        out = sys.argv[2]; width = int(sys.argv[3]); fps = int(sys.argv[4]); a_ = int(sys.argv[5]); b_ = int(sys.argv[6]); h = int(width * 9 / 16)
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{width}x{h}", "-r", str(fps), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for f in range(a_, b_): ff.stdin.write(render(f / fps, width).tobytes())
        ff.stdin.close(); ff.wait(); print("video ok", out, a_, b_)
