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
NAV = Battle(dict(fac="arab", cav=7, inf=8), dict(fac="chalukya", inf=12, arch=6, eleph=1, king=True), "right", t0=us(u_haraa) - 1.8, dur=6.3, t_clash=1.7, t_rout=kw(u_haraa, "haraaya") - (us(u_haraa) - 1.8) - 0.4, volley="R", seed=5)
HAK = Battle(dict(fac="arab", inf=6, cav=3), dict(fac="chalukya", inf=8, cav=3), "right", t0=us(u_hakam) - 0.2, dur=3.0, t_clash=0.9, t_rout=kw(u_hakam, "maara") - us(u_hakam) + 0.1, seed=11)
BAP = Battle(dict(fac="arab", cav=6), dict(fac="rajput", cav=7, banner=True), "right", t0=us(u_mewar) - 0.1, dur=4.0, t_clash=0.7, t_rout=1.0, clash_x=DW * 0.62, seed=13)
CAV = Battle(dict(fac="pratihara", cav=14, inf=3), dict(fac="pratihara", inf=0), "left", t0=us(u_851) - 0.5, dur=8.0, t_clash=8.5, t_rout=99, clash_x=DW * 1.15, seed=17, linear=True)
COL = Battle(dict(fac="syrian", inf=16, cav=3), dict(fac="syrian", inf=0), "left", t0=us(u_3000) - 1.0, dur=4.0, t_clash=4.5, t_rout=99, clash_x=DW * 1.05, seed=19, linear=True)
VIG = {   # key: (start_unit, end_time, battle, bg, title, date)
    "thirst": (u_724, us(u_730) - 0.1, Battle(dict(fac="arab", inf=10, cav=2), dict(fac="turk", cav=8, arch=5), "right", t0=us(u_724) + 1.1, dur=4.4, t_clash=1.1, t_rout=2.8, volley="R", seed=21), BG_DESERT, "Day of Thirst", "724 · Central Asia"),
    "khazar": (u_730, us(u_731) - 0.1, Battle(dict(fac="arab", inf=9, cav=3), dict(fac="khazar", cav=9, arch=4), "right", t0=us(u_730) + 1.0, dur=3.4, t_clash=0.9, t_rout=2.1, volley="R", seed=23), BG_COLD, "Khazar", "730 · Caucasus"),
    "defile": (u_731, us(u_732) - 0.1, Battle(dict(fac="arab", inf=10, cav=3), dict(fac="turk", cav=7, inf=4, arch=4), None, t0=us(u_731) + 1.0, dur=3.3, t_clash=0.9, t_rout=2.1, volley="R", seed=25), BG_GREY, "Battle of the Defile", "731 · Samarkand"),
    "tours": (u_732, us(u_739b) - 0.1, Battle(dict(fac="arab", cav=9, inf=3), dict(fac="frank", inf=14), "right", t0=us(u_732) + 1.0, dur=4.1, t_clash=1.0, t_rout=2.7, seed=27), BG_GREEN, "Tours", "732 · France"),
    "akroinon": (u_739b, us(u_740b) - 0.1, Battle(dict(fac="arab", inf=9, cav=3), dict(fac="byzantine", inf=10, cav=3), "right", t0=us(u_739b) + 1.0, dur=3.1, t_clash=0.9, t_rout=2.0, seed=29), BG_GOLD, "Akroinon", "739 · Byzantine"),
    "berber": (u_740b, us(u_wo3k) - 0.1, Battle(dict(fac="syrian", inf=10, cav=4), dict(fac="berber", inf=12, cav=3), "right", t0=us(u_740b) + 1.0, dur=5.6, t_clash=1.1, t_rout=3.6, seed=31), BG_RED, "Berber baghaawat", "740 · North Africa"),
}

def king_label(c, t, B, k):
    xy = B.king_xy(t)
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
    t0 = us(u_chittor) - 0.2; lt = t - t0; fail = kw(u_chittor, "naakaam")
    battle_bg(c, BG_GOLD, t, t0, 4.5, push=(1.04, 1.1))
    WX, WT = 1180, 420                                                     # cartoon fort wall (foreground right)
    c.drawRect(skia.Rect(WX, WT, DW + 20, 1070), paint("#B9925E"))
    for r in range(9):
        for q in range(8):
            off = 40 if r % 2 else 0; x0 = WX + q * 100 - off; y0 = WT + r * 72
            c.drawRect(skia.Rect(x0 + 3, y0 + 3, x0 + 97, y0 + 69), paint("#C9A46E")); c.drawRect(skia.Rect(x0 + 3, y0 + 3, x0 + 97, y0 + 69), paint("#7A5A33", 255, stroke=3))
    for q in range(8): c.drawRect(skia.Rect(WX + q * 100, WT - 60, WX + q * 100 + 60, WT), paint("#B9925E"))
    c.drawRect(skia.Rect(WX - 8, WT, WX + 8, 1070), paint("#6B4A26"))
    for i in range(4):                                                     # Mori defenders on the wall
        x = WX + 60 + i * 150; soldier(c, x, WT, 92, t, "rajput", "attack" if lt > 0.8 else "idle", t * 1.2 + i * 0.3, -1, banner=(i == 0))
        st = t0 + 1.0 + i * 0.5
        for j in range(3):
            kf = (t - st - j * 1.1) / 0.8
            if 0 < kf < 1:
                sx, sy = x - 40, WT - 160; ex, ey = WX - 120 - i * 60, 900; px = lerp(sx, ex, kf); py = lerp(sy, ey, kf) - 160 * 4 * kf * (1 - kf)
                c.drawCircle(px, py, 18, paint("#6E6259")); c.drawCircle(px - 5, py - 5, 6, paint("#9A8F86"))
    for i in range(3):                                                     # ladders + climbers, they fall back at "naakaam"
        bx = WX - 260 + i * 70; fk = ease_in(seg(t, fail - 0.2 + i * 0.12, fail + 0.5 + i * 0.12)); ang = -math.degrees(math.atan2(WT + 40 - 1040, WX - bx)) - 90
        c.save(); c.translate(bx, 1040); c.rotate(-(90 + ang) * 0 + fk * -55)
        L = math.hypot(WX - bx, 1040 - WT - 40); dxn = (WX - bx) / L; dyn = (WT + 40 - 1040) / L
        up = ease_out(seg(lt, 0.4 + i * 0.2, 1.0 + i * 0.2))
        for side in (-14, 14): c.drawLine(side * -dyn, side * dxn, (WX - bx) * up + side * -dyn, (WT + 40 - 1040) * up + side * dxn, paint("#7A5230", 255, stroke=7))
        for r in range(1, 12):
            f = r / 12 * up; c.drawLine(-14 * -dyn + (WX - bx) * f, -14 * dxn + (WT + 40 - 1040) * f, 14 * -dyn + (WX - bx) * f, 14 * dxn + (WT + 40 - 1040) * f, paint("#7A5230", 255, stroke=5))
        cf = clamp(seg(lt, 1.2 + i * 0.3, 3.4) * 0.8) * up
        soldier(c, (WX - bx) * cf, (WT + 40 - 1040) * cf, 80, t, "arab", "attack", t * 2 + i, 1)
        c.restore()
    for i in range(6):                                                     # attackers at the base, flee after the failure
        x = 300 + i * 120 - (520 * max(0, t - fail - 0.4) if t > fail + 0.4 else 0)
        soldier(c, x, 980 + (i % 2) * 50, 100, t, "arab", "flee" if t > fail + 0.4 else "attack", t * 1.8 + i * 0.37, -1 if t > fail + 0.4 else 1, banner=(i == 2 and t < fail + 0.4))
    ttl(c, "Chittor", "740 CE · Mori raja", seg(t, t0 + 0.1, t0 + 1.0) * (1 - seg(t, t0 + 2.6, t0 + 3.0)))
    dx, dy = shake(t, fail + 0.05, 14); c.save(); c.translate(dx, dy)
    stamp_slam(c, "GHERAABANDI NAAKAAM", 640, 330, 62, seg(t, fail - 0.1, fail + 0.3), "#C1121F", -6); c.restore()
    d6.ai_tag(c)

def bappa(c, t):
    battle_bg(c, BG_GOLD, t, BAP.t0, 4.5); BAP.draw(c, t)
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
        battle_bg(c, BG_GOLD, t, a0, 7); CAV.draw(c, t, camera=False)
        ttl(c, "Sulaiman ki gawahi", "851 CE · Arab vyapari", seg(t, a0 + 0.2, a0 + 1.2))
        d6.ai_tag(c)
    else:
        hl = d6.hl_box("pratihara_cavalry", DOC_CAV)
        if t < pk + 1.0:
            battle_bg(c, BG_GOLD, t, a0, 7); CAV.draw(c, t, camera=False)
            c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(120 * seg(t, pk, pk + 0.4))))
            doc_fly(c, DOC_CAV, seg(t, pk, pk + 0.9), (DW / 2 - 720, DH / 2 - 240, DW / 2 + 720, DH / 2 + 240))
        else:
            doc_pan(c, DOC_CAV, t, pk + 1.0, 1.1, (0, 0, 1, 1), d6.window(hl, DOC_CAV, 0.3), highlights=[hl + (pk + 1.5, pk + 2.3)])
            footnote(c, "Saboot: en.wikipedia.org - Gurjara-Pratihara dynasty (Sulaiman, 851)")

def column(c, t):
    a0 = us(u_3000) - 0.2; ka = 1 - seg(t, us(u_kahan) + 0.1, us(u_kahan) + 0.6)
    battle_bg(c, BG_GOLD, t, a0, 4); COL.draw(c, t, camera=False, a=int(255 * ka))
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
    E += [("riser", NAV.t0 - 1.2, -14), ("boom", NAV.t0 - 0.4, -8), ("battle", NAV.t0 + 0.2, -7), ("whoosh", NAV.t0 + NAV.tc * 0.35, -10), ("whoosh", NAV.t0 + NAV.tc * 0.35 + 0.7, -12),
          ("drum_big", NAV.t0 + NAV.tc, -5), ("stamp", kw(u_haraa, "haraaya"), -3), ("firework", kw(u_haraa, "haraaya") + 0.3, -10), ("firework", kw(u_haraa, "haraaya") + 0.7, -12),
          ("boom", us(u_740) - 0.5, -10), ("tick", kw(u_740, "740") - 0.2, -8), ("pin", us(u_740), -8),
          ("battle", HAK.t0, -10), ("drum_big", HAK.t0 + HAK.tc, -8), ("stamp", kw(u_hakam, "maara"), -4),
          ("battle", us(u_chittor) - 0.2, -11), ("drum", us(u_chittor) + 0.8, -10), ("drum", us(u_chittor) + 1.3, -10), ("stamp", kw(u_chittor, "naakaam"), -4), ("boom", kw(u_chittor, "naakaam") + 0.1, -12),
          ("battle", BAP.t0, -11), ("whoosh", BAP.t0 + 0.3, -9), ("paper", kw(u_mewar, "Bappa") + 0.1, -6), ("pop", us(u_halaanki), -10)]
    E += [("riser", us(u_bigsam) - 1.0, -16), ("drum_big", us(u_bigsam) + 0.6, -10)] + [("pop", us(u_bigsam) + 0.6 + i * 0.32, -12) for i in range(10)]
    pk = kw(u_851, "ghudsawaar") + 0.6
    E += [("battle", us(u_851), -12)] + [("drum", us(u_851) + i * 0.38, -14) for i in range(14)] + [("paper", pk, -6), ("marker", pk + 1.5, -10)]
    E += [("drum", us(u_3000) + i * 0.4, -12) for i in range(6)] + [("pop", us(u_kahan), -6), ("whoosh", us(u_nazar), -8), ("riser", us(u_nazar) + 0.4, -14)]
    E += [("firework", us(u_jal) + 0.3 + i * 0.42, -16) for i in range(6)] + [("boom", us(u_jal), -10)]
    for key in VIG:
        u0, _, B, *_ = VIG[key]; a0 = us(u0) - 0.1
        E += [("whoosh", a0, -9), ("pin", a0 + 0.3, -8), ("tick", a0, -10), ("boom", a0 + 0.85, -10), ("battle", a0 + 1.1, -8), ("drum_big", B.t0 + B.tc, -7)]
        if B.volley: E += [("whoosh", B.t0 + B.tc * 0.35, -11)]
    E += [("stamp", kw(u_27k, "saaf"), -4), ("pin", us(u_wo3k), -8)] + [("drum", us(u_wo3k) + 0.6 + i * 0.45, -13) for i in range(5)]
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
