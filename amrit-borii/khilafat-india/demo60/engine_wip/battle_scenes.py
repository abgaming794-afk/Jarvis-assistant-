"""Unique, period-correct cartoon battle scenes (Unexplored Truth by Amrit 1.3.0).

Every war gets its OWN choreography (the user: "ek tarah ka yudh baar baar kyun dikha rahe ho"):
  NavsariElephants  - Chalukya spear wall + war elephants fling Umayyad riders, conch, arrow volley, rout
  Duel              - two commanders charge, slow-motion clash, the loser is thrown off his horse
  Siege             - fort wall, defenders' arrows and rocks, ladders thrown back, attackers flee
  Chase             - galloping pursuit, the camera runs with the riders (scrolling ground)
  Parade            - three ranks of caparisoned cavalry with banners pass in review
  Column            - an army marching in step with a drummer
  Encircled         - steppe horse archers circle a trapped army that collapses from thirst (Day of Thirst)
  CampSweep         - a cavalry wave overruns an army camp, tents collapse (Khazars at Ardabil)
  Ambush            - column trapped in a mountain pass, archers on both cliffs, rolling boulders (Defile)
  ShieldWall        - infantry shield wall on a hill throws back cavalry waves (Tours)
  Wedge             - heavy cavalry wedge splits an enemy line (Akroinon)
  DuneAmbush        - light infantry rise from the dunes and throw javelins (Berber revolt)
Each scene: draw(c, t) and sfx() -> [(sound, time, gain_db)] for battle_sfx.py. Draw over battle_bg().
"""
import math
import numpy as np
import skia
from core import *
from battle2d import *

def _depth_s(base, y, g0=800, g1=1065): return base * lerp(0.62, 1.05, clamp((y - g0) / (g1 - g0)))

class Scene:
    def __init__(self, t0, dur): self.t0, self.dur = t0, dur
    def lt(self, t): return t - self.t0

# ------------------------------------------------------------------------------------------------ Navsari
class NavsariElephants(Scene):
    def __init__(self, t0, dur, t_rout_abs, seed=5):
        super().__init__(t0, dur)
        self.B = Battle(dict(fac="arab", cav=8, inf=7), dict(fac="chalukya", inf=12, arch=6, eleph=3, king=True), "right", t0=t0, dur=dur,
                        t_clash=1.7, t_rout=t_rout_abs - t0, volley="R", seed=seed, launch=(2.1, 0.45, "L"))
    def draw(self, c, t): self.B.draw(c, t)
    def sfx(self):
        t0, B = self.t0, self.B
        E = [("conch", t0 + 0.05, -6), ("nagara", t0 + 0.2, -9), ("warcry_in", t0 + 0.35, -7), ("warcry_ar", t0 + 0.6, -8), ("gallop_many", t0 + 0.2, -7),
             ("volley", t0 + B.tc * 0.35, -6), ("volley", t0 + B.tc * 0.35 + 0.7, -8), ("arrow_hits", t0 + B.tc * 0.35 + 0.9, -9),
             ("elephant", t0 + B.tc - 0.2, -5), ("clash_bed", t0 + B.tc, -6), ("elephant", t0 + 2.4, -8)]
        E += [("body_fly", t0 + 2.1 + i * 0.25, -9) for i in range(4)] + [("neigh", t0 + 2.3, -9), ("neigh", t0 + 3.1, -11)]
        E += [("crowd_panic", t0 + B.tr, -8), ("warcry_in", t0 + B.tr + 0.5, -9), ("gallop_few", t0 + B.tr + 0.2, -10)]
        return E

# ------------------------------------------------------------------------------------------------ Duel
class Duel(Scene):
    """two mounted commanders. left = loser (thrown off) unless winner='left'."""
    def __init__(self, t0, dur, t_hit_abs, left_fac="arab_gen", right_fac="chalukya", winner="right", bg_battle=None, names=("", "")):
        super().__init__(t0, dur); self.th = t_hit_abs - t0; self.Lf, self.Rf, self.win, self.bgB, self.names = left_fac, right_fac, winner, bg_battle, names
    def draw(self, c, t):
        lt = self.lt(t)
        if self.bgB:
            c.save(); c.translate(0, -140); c.scale(1, 1); self.bgB.draw(c, t, camera=False, a=170); c.restore()
            c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", 50))
        th = self.th; slow = 0.25                                   # slow motion around the hit
        def tw(x):                                                  # warped local time
            if x < th - 0.35: return x
            if x < th + 0.6: return th - 0.35 + (x - (th - 0.35)) * slow
            return th - 0.35 + 0.95 * slow + (x - th - 0.6)
        w = tw(lt); app = clamp(w / (th - 0.35 + 0.35 * slow)); s = 150
        xl = lerp(-260, DW / 2 - 150, ease_out(app)); xr = lerp(DW + 260, DW / 2 + 150, ease_out(app)); y = 1000
        phl, phr = w * 2.6, w * 2.6 + 0.4
        loser_left = self.win == "right"
        hit = clamp((lt - th) / 0.9)
        FL, FR = FAC[self.Lf], FAC[self.Rf]
        if lt < th or not loser_left:
            horse(c, xl, y, s * 1.2, t, phl, 1, FL["horses"][0], rider_fn(self.Lf, "attack", phl, t, 1), capar=FL["capar"])
        else:
            horse(c, xl + 500 * hit, y, s * 1.2, t, phl, 1, FL["horses"][0], None, capar=FL["capar"], a=int(255 * (1 - hit)))   # riderless horse runs on
            soldier_fly(c, xl, y - 150, s, t, self.Lf, hit, face=1, dist=360, height=220, spin=200)
        horse(c, xr + (lt - th) * 260 * (lt > th), y + 20, s * 1.2, t, phr, -1, FR["horses"][0], rider_fn(self.Rf, "attack", phr, t, -1), capar=FR["capar"])
        if abs(lt - th) < 0.5: sparks(c, DW / 2, y - 330, t, seed=3, k=1.0); sparks(c, DW / 2 + 20, y - 300, t + 0.13, seed=8, k=1.0)
        if th - 0.35 < lt < th + 0.6:                               # slow-motion frame: vignette + streaks
            c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", 70)); speed_lines(c, t, 0.6, "#FFF3B0")
        for i, (nm, x, k) in enumerate(((self.names[0], xl, seg(lt, 0.3, 0.8)), (self.names[1], xr, seg(lt, 0.5, 1.0)))):
            if nm and k > 0 and lt < th + 0.2: pill(c, nm, x, 470, 28, "#14213D", "#FFFFFF", int(255 * k), fpath=FT_SEMI)
    def sfx(self):
        t0, th = self.t0, self.t0 + self.th
        return [("warcry_ar", t0 + 0.1, -10), ("warcry_in", t0 + 0.3, -10), ("gallop_few", t0, -6), ("gallop_few", t0 + 0.4, -8),
                ("sword_clang", th, -2), ("slowmo", th - 0.35, -8), ("body_fly", th + 0.1, -5), ("neigh", th + 0.3, -6), ("clash_bed", t0, -14)]

# ------------------------------------------------------------------------------------------------ Siege
class Siege(Scene):
    def __init__(self, t0, dur, t_fail_abs, attacker="arab", defender="rajput"):
        super().__init__(t0, dur); self.tf = t_fail_abs; self.A, self.D = attacker, defender
    def draw(self, c, t):
        lt = self.lt(t); fail = self.tf; WX, WT = 1180, 420
        c.drawRect(skia.Rect(WX, WT, DW + 20, 1070), paint("#B9925E"))
        for r in range(9):
            for q in range(8):
                off = 40 if r % 2 else 0; x0 = WX + q * 100 - off; y0 = WT + r * 72
                c.drawRect(skia.Rect(x0 + 3, y0 + 3, x0 + 97, y0 + 69), paint("#C9A46E")); c.drawRect(skia.Rect(x0 + 3, y0 + 3, x0 + 97, y0 + 69), paint("#7A5A33", 255, stroke=3))
        for q in range(8): c.drawRect(skia.Rect(WX + q * 100, WT - 60, WX + q * 100 + 60, WT), paint("#B9925E"))
        for i in range(4):                                          # defenders: archers + rock throwers
            x = WX + 60 + i * 150; archer = i % 2 == 1
            soldier(c, x, WT, 92, t, self.D, "shoot" if archer else ("attack" if lt > 0.8 else "idle"), t * 1.2 + i * 0.3, -1, banner=(i == 0), weapon="bow" if archer else None)
            st = self.t0 + 1.0 + i * 0.5
            for j in range(3):
                kf = (t - st - j * 1.1) / 0.8
                if 0 < kf < 1 and not archer:
                    sx, sy = x - 40, WT - 160; ex, ey = WX - 120 - i * 60, 900; px = lerp(sx, ex, kf); py = lerp(sy, ey, kf) - 160 * 4 * kf * (1 - kf)
                    c.drawCircle(px, py, 18, paint("#6E6259")); c.drawCircle(px - 5, py - 5, 6, paint("#9A8F86"))
            if archer: arrow_volley(c, t, self.t0 + 0.9 + i * 0.4, (x - 40, WT - 170), (700, 960), n=6, flight=0.7, spread=(140, 60), seed=40 + i, h=120)
        for i in range(3):
            bx = WX - 260 + i * 70; fk = ease_in(seg(t, fail - 0.2 + i * 0.12, fail + 0.5 + i * 0.12))
            L = math.hypot(WX - bx, 1040 - WT - 40); dxn = (WX - bx) / L; dyn = (WT + 40 - 1040) / L
            c.save(); c.translate(bx, 1040); c.rotate(fk * -55)
            up = ease_out(seg(lt, 0.4 + i * 0.2, 1.0 + i * 0.2))
            for side in (-14, 14): c.drawLine(side * -dyn, side * dxn, (WX - bx) * up + side * -dyn, (WT + 40 - 1040) * up + side * dxn, paint("#7A5230", 255, stroke=7))
            for r in range(1, 12):
                f = r / 12 * up; c.drawLine(-14 * -dyn + (WX - bx) * f, -14 * dxn + (WT + 40 - 1040) * f, 14 * -dyn + (WX - bx) * f, 14 * dxn + (WT + 40 - 1040) * f, paint("#7A5230", 255, stroke=5))
            cf = clamp(seg(lt, 1.2 + i * 0.3, 3.4) * 0.8) * up
            soldier(c, (WX - bx) * cf, (WT + 40 - 1040) * cf, 80, t, self.A, "attack", t * 2 + i, 1)
            c.restore()
        for i in range(6):
            fled = t > fail + 0.4; x = 300 + i * 120 - (520 * (t - fail - 0.4) if fled else 0)
            soldier(c, x, 980 + (i % 2) * 50, 100, t, self.A, "flee" if fled else ("block" if i % 2 else "attack"), t * 1.8 + i * 0.37, -1 if fled else 1, banner=(i == 2 and not fled))
    def sfx(self):
        t0, f = self.t0, self.tf
        E = [("warcry_ar", t0 + 0.2, -9), ("tabl", t0 + 0.1, -10), ("ladder", t0 + 0.6, -9), ("volley", t0 + 0.9, -9), ("volley", t0 + 1.7, -10),
             ("rock_hit", t0 + 1.8, -8), ("rock_hit", t0 + 2.6, -9), ("rock_hit", t0 + 2.9, -9), ("warcry_in", t0 + 1.0, -9), ("clash_bed", t0 + 1.4, -13)]
        E += [("ladder_fall", f, -5), ("body_fly", f + 0.2, -7), ("fall_thud", f + 0.6, -6), ("crowd_panic", f + 0.4, -8), ("warcry_in", f + 0.6, -8)]
        return E

# ------------------------------------------------------------------------------------------------ Chase
class Chase(Scene):
    """pursuers (right side) chase the fleeing (left side) leftwards; the camera runs with them."""
    def __init__(self, t0, dur, fleeing="arab", pursuer="rajput", lead_name=""):
        super().__init__(t0, dur); self.F, self.P, self.name = fleeing, pursuer, lead_name
        rng = np.random.default_rng(4); self.fl = [(rng.uniform(250, 800), rng.uniform(830, 1050), rng.uniform(0, 1)) for _ in range(5)]
        self.pu = [(rng.uniform(1050, 1650), rng.uniform(830, 1050), rng.uniform(0, 1)) for _ in range(6)]
    def ground_scroll(self, c, bg, t):
        far, ground = bg; off = (self.lt(t) * 900) % DW
        draw_img(c, far, -(self.lt(t) * 60) % 200 - 200, 0, DW + 200 - (self.lt(t) * 60) % 200, DH)
        for k in (0, 1): draw_img(c, ground, -off + k * DW, DH - 460, -off + (k + 1) * DW + 2, DH)
    def draw(self, c, t):
        lt = self.lt(t); units = []
        for i, (x, y, r) in enumerate(self.fl): units.append((y, "F", x - lt * 30 + math.sin(lt * 2 + r * 6) * 30, r, i))
        for i, (x, y, r) in enumerate(self.pu): units.append((y, "P", x - lt * 90 + math.sin(lt * 2 + r * 6) * 20, r, i))
        for y, side, x, r, i in sorted(units):
            s = _depth_s(110, y); fac = self.F if side == "F" else self.P; ph = lt * 2.8 + r
            HS = FAC[fac]["horses"]; col = HS[i % len(HS)]
            horse(c, x, y, s * 1.15, t, ph, -1, col, rider_fn(fac, "flee" if side == "F" else "attack", ph, t, -1), capar=FAC[fac]["capar"])
            if side == "P" and i == 0:
                c.drawLine(x + 30, y - 260 * s / 100, x + 30, y - 470 * s / 100, paint("#6B4423", 255, stroke=5))
                banner_emblem(c, FAC[fac]["banner"], x + 30, y - 470 * s / 100, 90, 64)
                if self.name: pill(c, self.name, x, y - 520 * s / 100, 26, "#14213D", "#FFFFFF", int(255 * seg(lt, 0.4, 0.9)), fpath=FT_SEMI)
            dust(c, t, x + 60, y, 160, 0.7, seed=i + (0 if side == "F" else 20))
        speed_lines(c, t, 0.7)
    def sfx(self):
        t0 = self.t0
        return [("gallop_many", t0, -5), ("gallop_many", t0 + 1.6, -6), ("warcry_in", t0 + 0.3, -8), ("crowd_panic", t0 + 0.6, -11), ("neigh", t0 + 1.0, -9), ("neigh", t0 + 2.2, -10), ("wind", t0, -12)]

# ------------------------------------------------------------------------------------------------ Parade
class Parade(Scene):
    def __init__(self, t0, dur, fac="pratihara", elephants=True):
        super().__init__(t0, dur); self.fac, self.el = fac, elephants
    def draw(self, c, t):
        lt = self.lt(t); F = FAC[self.fac]; items = []
        for row, (y, spd, n, gap) in enumerate(((835, 140, 7, 300), (920, 190, 7, 280), (1015, 240, 6, 320))):
            for i in range(n): items.append((y, row, 700 - i * gap + lt * spd + row * 120, i))
        if self.el:
            for i in range(2): items.append((800, 9, 500 - i * 620 + lt * 110, i))
        for y, row, x, i in sorted(items):
            if row == 9: elephant(c, x, y, 70, t, lt * 0.8 + i, 1, None, cloth="#B91C1C"); continue
            s = _depth_s(105, y); ph = lt * 1.6 + i * 0.3 + row
            horse(c, x, y, s * 1.15, t, ph, 1, F["horses"][(i + row) % len(F["horses"])], rider_fn(self.fac, "idle", ph, t, 1), capar=F["capar"])
            if i % 3 == 0:
                c.drawLine(x + 10, y - 250 * s / 100, x + 10, y - 450 * s / 100, paint("#6B4423", 255, stroke=5))
                banner_emblem(c, F["banner"], x + 10, y - 450 * s / 100, 80, 56)
    def sfx(self):
        t0 = self.t0
        return [("horn", t0 + 0.1, -7), ("trot_many", t0, -6), ("trot_many", t0 + 2.5, -7), ("nagara", t0 + 0.3, -9), ("elephant", t0 + 1.8, -11), ("neigh", t0 + 3.0, -12)]

# ------------------------------------------------------------------------------------------------ Column
class Column(Scene):
    def __init__(self, t0, dur, fac="syrian"):
        super().__init__(t0, dur); self.fac = fac
    def draw(self, c, t, a=255):
        lt = self.lt(t); items = []
        for row, y in enumerate((880, 1000)):
            for i in range(9): items.append((y, 900 - i * 170 + lt * 230 + row * 60, i, row))
        for y, x, i, row in sorted(items):
            s = _depth_s(105, y); step = (lt * 1.6 + (i % 2) * 0.5)
            soldier(c, x, y, s, t, self.fac, "run", step, 1, a, banner=(i == 2 and row == 0), weapon="spear")
        dx = -260 + 900 + lt * 230 - 9 * 170; soldier(c, dx, 1040, 110, t, self.fac, "idle", 0, 1, a)     # drummer
        c.drawOval(skia.Rect(dx + 20, 1040 - 150, dx + 90, 1040 - 100), paint("#8B5A2B", a))
    def sfx(self):
        t0 = self.t0
        return [("march_drum", t0, -6), ("footsteps", t0, -9), ("horn", t0 + 0.2, -12)]

# ------------------------------------------------------------------------------------------------ Encircled (Day of Thirst)
class Encircled(Scene):
    def __init__(self, t0, dur, inner="arab", outer="turk"):
        super().__init__(t0, dur); self.I, self.O = inner, outer
        rng = np.random.default_rng(9); self.cl = [(DW / 2 + rng.uniform(-260, 260), rng.uniform(870, 1010), rng.uniform(0, 1)) for _ in range(12)]
    def draw(self, c, t):
        lt = self.lt(t); cx, cy, rx, ry = DW / 2, 930, 760, 150; items = []
        for i in range(10):
            ang = i / 10 * 2 * math.pi + lt * 0.9; x = cx + math.cos(ang) * rx; y = cy + math.sin(ang) * ry
            items.append((y, "O", x, -1 if math.sin(ang) > 0 else 1, ang, i))
        for i, (x, y, r) in enumerate(self.cl): items.append((y, "I", x, 1 if x < cx else -1, r, i))
        for y, kind, x, face, v, i in sorted(items):
            s = _depth_s(105, y)
            if kind == "O":
                horse(c, x, y, s * 1.1, t, lt * 2.6 + i * 0.3, face, FAC[self.O]["horses"][i % 2], rider_fn(self.O, "shoot", lt * 1.4 + i, t, face), mane="#E9DCC0")
            else:
                kn = seg(lt, 0.8 + v * 2.2, 1.4 + v * 2.2); fall = seg(lt, 2.4 + v * 1.6, 3.0 + v * 1.6) if v < 0.45 else 0
                soldier(c, x, y, s, t, self.I, "thirst" if kn > 0.3 else "block", lt + v, face, 255, fall, kneel=kn, banner=(i == 0 and kn < 0.3))
        for j in range(4): arrow_volley(c, t, self.t0 + 0.4 + j * 0.9, (cx + (-1) ** j * rx * 0.9, cy - 120), (cx, cy - 20), n=10, flight=0.8, spread=(200, 60), seed=60 + j, h=180)
    def sfx(self):
        t0 = self.t0
        E = [("warcry_steppe", t0 + 0.1, -7), ("gallop_many", t0, -7), ("gallop_many", t0 + 1.8, -8), ("heat_drone", t0, -10)]
        E += [("volley", t0 + 0.4 + j * 0.9, -8) for j in range(4)] + [("arrow_hits", t0 + 1.2 + j * 0.9, -10) for j in range(3)]
        E += [("groan", t0 + 1.4, -9), ("groan", t0 + 2.6, -10), ("fall_thud", t0 + 2.8, -9)]
        return E

# ------------------------------------------------------------------------------------------------ CampSweep (Khazars)
class CampSweep(Scene):
    def __init__(self, t0, dur, camp="arab", riders="khazar"):
        super().__init__(t0, dur); self.C, self.R = camp, riders
        rng = np.random.default_rng(12); self.men = [(rng.uniform(700, 1800), rng.uniform(880, 1040), rng.uniform(0, 1)) for _ in range(9)]
        self.wave = [(rng.uniform(-200, 250), rng.uniform(840, 1060), rng.uniform(0, 1)) for _ in range(14)]
    def front(self, lt): return -300 + max(0, lt - 0.5) * 720
    def draw(self, c, t):
        lt = self.lt(t); fx = self.front(lt)
        for i, tx in enumerate((820, 1150, 1480, 1780)):            # tents collapse when the wave passes
            col = fx - 120 > tx; k = seg(fx - 120, tx, tx + 200)
            h = 230 * (1 - 0.85 * k); y0 = 860
            p = skia.Path(); p.moveTo(tx - 130, y0); p.lineTo(tx, y0 - h); p.lineTo(tx + 130, y0); p.close()
            c.drawPath(p, paint("#E9E1CF")); c.drawPath(p, paint("#8B7355", 255, stroke=4))
            c.drawLine(tx, y0 - h, tx, y0, paint("#B91C1C" if i % 2 else "#2B59C3", 255, stroke=8))
        items = []
        for i, (x, y, r) in enumerate(self.men): items.append((y, "M", x, r, i))
        for i, (x, y, r) in enumerate(self.wave): items.append((y, "W", fx + x, r, i))
        for y, kind, x, r, i in sorted(items):
            s = _depth_s(108, y)
            if kind == "W":
                horse(c, x, y, s * 1.15, t, lt * 2.8 + r, 1, FAC[self.R]["horses"][i % 3], rider_fn(self.R, "attack", lt * 2 + r, t, 1), capar=FAC[self.R]["capar"])
            else:
                hit_t = (x - (-300)) / 720 + 0.5 - 0.15
                if lt > hit_t and r < 0.55: soldier_fly(c, x, y, s, t, self.C, seg(lt, hit_t, hit_t + 0.9), face=-1, dist=-300, height=200)
                elif lt > hit_t - 0.6: soldier(c, x + (lt - hit_t + 0.6) * 380, y, s, t, self.C, "flee", lt * 2 + r, 1)
                else: soldier(c, x, y, s, t, self.C, "idle" if lt < 0.7 else "block", lt + r, -1, banner=(i == 0))
        dust(c, t, fx + 100, 900, 700, seg(lt, 0.5, 1.0), seed=31)
    def sfx(self):
        t0 = self.t0
        return [("warcry_steppe", t0 + 0.3, -6), ("gallop_many", t0 + 0.3, -4), ("gallop_many", t0 + 1.8, -5), ("crowd_panic", t0 + 1.0, -7), ("tent", t0 + 1.4, -8),
                ("tent", t0 + 2.0, -9), ("body_fly", t0 + 1.3, -8), ("body_fly", t0 + 1.8, -9), ("clash_bed", t0 + 1.1, -9), ("neigh", t0 + 0.6, -8)]

# ------------------------------------------------------------------------------------------------ Ambush in a pass (Defile)
class Ambush(Scene):
    def __init__(self, t0, dur, column="arab", ambusher="turk"):
        super().__init__(t0, dur); self.C, self.A = column, ambusher
        rng = np.random.default_rng(14); self.col = [(-100 - i * 150, rng.uniform(930, 1040), rng.uniform(0, 1)) for i in range(12)]
        self.boulders = [(0.9, 460, 1.0), (1.6, 1480, -1.0), (2.3, 640, 1.0)]
    def cliffs(self, c):
        for side in (-1, 1):
            p = skia.Path(); x0 = 0 if side < 0 else DW
            p.moveTo(x0, 0); p.lineTo(x0 - side * 760, 0); p.lineTo(x0 - side * 520, 330); p.lineTo(x0 - side * 620, 520); p.lineTo(x0 - side * 300, 860); p.lineTo(x0, 920); p.close()
            c.drawPath(p, paint("#6B5A48")); c.drawPath(p, paint("#3B2F25", 255, stroke=6))
            for i in range(6): c.drawLine(x0 - side * (120 + i * 90), 60 + i * 120, x0 - side * (200 + i * 70), 120 + i * 120, paint("#4A3D30", 255, stroke=5))
    def draw(self, c, t):
        lt = self.lt(t); self.cliffs(c)
        for side in (-1, 1):                                         # archers on the cliff tops
            for i in range(5):
                x = (300 + i * 80) if side < 0 else (DW - 300 - i * 80); y = 330 - i * 5 + (i % 2) * 30
                up = seg(lt, 0.5 + i * 0.08, 0.9 + i * 0.08)
                if up > 0: soldier(c, x, y + (1 - up) * 80, 70, t, self.A, "shoot", lt * 1.5 + i, 1 if side < 0 else -1, int(255 * up))
            for j in range(3): arrow_volley(c, t, self.t0 + 0.8 + j * 0.8 + (0.3 if side > 0 else 0), ((520 if side < 0 else DW - 520), 250), (DW / 2, 980), n=9, flight=0.7, spread=(300, 60), seed=70 + j + side, h=60)
        for bt, bx, dirn in self.boulders:                           # rolling boulders down the slopes
            k = seg(lt, bt, bt + 0.9)
            if 0 < k <= 1:
                x = lerp(bx, DW / 2 - dirn * 120, k); y = lerp(420, 990, ease_in(k)) - abs(math.sin(k * 9)) * 40
                c.save(); c.translate(x, y); c.rotate(k * 720 * dirn); c.drawCircle(0, 0, 44, paint("#6E6259")); c.drawCircle(-12, -10, 12, paint("#8C8178")); c.restore()
        for i, (x0, y, r) in enumerate(sorted(self.col, key=lambda u: u[1])):
            x = x0 + lt * 300; s = _depth_s(100, y)
            hit = any(bt + 0.9 < lt and abs(x - (DW / 2 - d * 120)) < 160 for bt, _, d in self.boulders) and r < 0.5
            fall = seg(lt, 1.8 + r * 1.5, 2.3 + r * 1.5) if (hit or r < 0.18) else 0
            soldier(c, x, y, s, t, self.C, "block" if lt > 0.9 else "run", lt * 1.7 + r, 1, 255, fall, banner=(i == 3))
    def sfx(self):
        t0 = self.t0
        E = [("march_drum", t0, -11), ("warcry_steppe", t0 + 0.6, -7), ("echo_shout", t0 + 0.7, -10)]
        E += [("volley", t0 + 0.8 + j * 0.8, -7) for j in range(3)] + [("arrow_hits", t0 + 1.4 + j * 0.8, -9) for j in range(3)]
        E += [("boulder", t0 + bt, -5) for bt, _, _ in self.boulders] + [("groan", t0 + 2.0, -9), ("fall_thud", t0 + 2.3, -8)]
        return E

# ------------------------------------------------------------------------------------------------ Shield wall on a hill (Tours)
class ShieldWall(Scene):
    def __init__(self, t0, dur, wall="frank", leader="frank_lead", cav="arab", t_retreat_abs=None, leader_name=""):
        super().__init__(t0, dur); self.W, self.Ld, self.Cv, self.name = wall, leader, cav, leader_name
        self.tr = (t_retreat_abs - t0) if t_retreat_abs else dur - 1.2
    def hill(self, c):
        p = skia.Path(); p.moveTo(1050, 1080); p.quadTo(1240, 760, 1500, 700); p.lineTo(DW, 690); p.lineTo(DW, 1080); p.close()
        c.drawPath(p, paint("#6E7F3A")); c.drawPath(p, paint("#4E5C28", 255, stroke=5))
    def draw(self, c, t):
        lt = self.lt(t); self.hill(c)
        rng = np.random.default_rng(int(t * 8))
        for i in range(10):                                           # October leaves
            x = (i * 211 + t * 60) % DW; y = (i * 97 + t * 90) % 700 + 100; c.drawOval(skia.Rect(x, y, x + 12, y + 7), paint(("#C2410C", "#D97706", "#A16207")[i % 3], 200))
        soldier(c, 1760, 690, 105, t, self.Ld, "attack" if lt > 1 else "idle", lt * 1.5, -1, banner=True)
        if self.name: pill(c, self.name, 1760, 330, 26, "#14213D", "#FFFFFF", int(255 * seg(lt, 0.4, 0.9)), fpath=FT_SEMI)
        for rank, (bx, by) in enumerate(((1560, 720), (1500, 760))):
            for i in range(6): soldier(c, bx - i * 0 + (i % 2) * 6, by + i * 52, 92, t, self.W, "block", lt + i * 0.2, -1)
        for w in range(2):                                            # two cavalry waves that bounce off
            wt = 0.3 + w * 1.6
            for i in range(6):
                y = 820 + i * 40; r = (i * 37 % 10) / 10; s = _depth_s(105, y)
                hit_x = 1360 + (y - 820) * 0.3
                k = seg(lt, wt, wt + 1.0); x = lerp(-200 - r * 200, hit_x, ease_in(k))
                if lt > wt + 1.0:
                    back = lt - wt - 1.0
                    if r < 0.4: soldier_fly(c, hit_x, y, s, t, self.Cv, seg(back, 0, 0.9), face=1, dist=320, height=200); continue
                    x = hit_x - back * 420; face = -1; st = "flee"
                else: face = 1; st = "attack"
                horse(c, x, y, s * 1.15, t, lt * 2.8 + r, face, FAC[self.Cv]["horses"][i % 3], rider_fn(self.Cv, st, lt * 2 + r, t, face))
            if wt + 0.9 < lt < wt + 1.3:
                for j in range(4): sparks(c, 1380 + j * 20, 760 + j * 60, t + j * 0.1, seed=j + w * 5)
    def sfx(self):
        t0 = self.t0
        E = [("horn", t0, -8), ("warcry_frank", t0 + 0.2, -8)]
        for w in range(2):
            wt = t0 + 0.3 + w * 1.6
            E += [("gallop_many", wt, -6), ("warcry_ar", wt + 0.1, -9), ("shield_bash", wt + 1.0, -3), ("sword_clang", wt + 1.05, -6), ("body_fly", wt + 1.1, -8), ("neigh", wt + 1.2, -8)]
        E += [("warcry_frank", t0 + 3.6, -8)]
        return E

# ------------------------------------------------------------------------------------------------ Heavy cavalry wedge (Akroinon)
class Wedge(Scene):
    def __init__(self, t0, dur, wedge="byzantine", line="arab", leader_name=""):
        super().__init__(t0, dur); self.Wf, self.Lf, self.name = wedge, line, leader_name
        self.pos = [(0, 940)] + [(-i * 170, 940 + sgn * i * 45) for i in range(1, 5) for sgn in (-1, 1)]
        rng = np.random.default_rng(15); self.line = [(rng.uniform(1100, 1600), rng.uniform(840, 1050), rng.uniform(0, 1)) for _ in range(12)]
    def draw(self, c, t):
        lt = self.lt(t); tip = -250 + lt * 620; items = []
        for i, (dx, y) in enumerate(self.pos): items.append((y, "W", tip + dx, i))
        for i, (x, y, r) in enumerate(self.line): items.append((y, "L", x, i))
        for y, kind, x, i in sorted(items):
            s = _depth_s(108, y)
            if kind == "W":
                horse(c, x, y, s * 1.2, t, lt * 2.7 + i * 0.2, 1, FAC[self.Wf]["horses"][i % 2], rider_fn(self.Wf, "attack", lt * 2 + i, t, 1), capar=FAC[self.Wf]["capar"])
                if i == 0 and self.name: pill(c, self.name, x, y - 560 * s / 100, 26, "#14213D", "#FFFFFF", int(255 * seg(lt, 0.3, 0.8)), fpath=FT_SEMI)
            else:
                x0, y0, r = self.line[i]; reach = abs(y0 - 940) * 2.6
                ht = (x0 - reach + 250) / 620
                if lt > ht:
                    if r < 0.5: soldier_fly(c, x0, y0, s, t, self.Lf, seg(lt, ht, ht + 0.9), face=-1, dist=-280, height=220 + r * 100); continue
                    soldier(c, x0 + (lt - ht) * 420, y0, s, t, self.Lf, "flee", lt * 2 + r, 1)
                else: soldier(c, x0, y0, s, t, self.Lf, "block", lt + r, -1, banner=(i == 0))
        dust(c, t, tip - 300, 900, 600, 0.8, seed=41)
    def sfx(self):
        t0 = self.t0
        return [("horn", t0, -7), ("gallop_many", t0, -4), ("gallop_many", t0 + 1.6, -5), ("warcry_frank", t0 + 0.3, -9), ("warcry_ar", t0 + 0.6, -10),
                ("shield_bash", t0 + 1.9, -3), ("clash_bed", t0 + 1.9, -6), ("body_fly", t0 + 2.0, -7), ("body_fly", t0 + 2.3, -8), ("crowd_panic", t0 + 2.4, -8)]

# ------------------------------------------------------------------------------------------------ Dune ambush (Berber revolt)
class DuneAmbush(Scene):
    def __init__(self, t0, dur, rebels="berber", army="syrian", t_pop_abs=None):
        super().__init__(t0, dur); self.R, self.A = rebels, army; self.tp = (t_pop_abs - t0) if t_pop_abs else 0.9
        rng = np.random.default_rng(16); self.army = [(-300 - i * 140, rng.uniform(860, 1050), rng.uniform(0, 1), i % 3 == 0) for i in range(11)]
        self.reb = [(1100 + i * 85 + rng.uniform(-20, 20), 760 + (i % 3) * 18, rng.uniform(0, 1)) for i in range(10)]
    def dunes(self, c, front=True):
        p = skia.Path()
        if front: p.moveTo(980, 1080); p.cubicTo(1200, 780, 1500, 760, 1700, 800); p.cubicTo(1820, 820, 1900, 840, DW, 830); p.lineTo(DW, 1080); p.close()
        else: p.moveTo(900, 900); p.cubicTo(1200, 700, 1600, 690, DW, 720); p.lineTo(DW, 900); p.close()
        c.drawPath(p, paint("#D9B26F" if front else "#C9A060")); c.drawPath(p, paint("#A47B3C", 255, stroke=4))
    def draw(self, c, t):
        lt = self.lt(t); self.dunes(c, False)
        charge = lt > self.tp + 1.6
        for i, (x0, y, r) in enumerate(self.reb):                     # rise behind the dune crest, throw, then charge
            up = seg(lt, self.tp + r * 0.3, self.tp + 0.4 + r * 0.3)
            x = x0 - (lt - self.tp - 1.6) * 420 if charge else x0; yy = y + (1 - up) * 160 + (200 if charge else 0) * seg(lt, self.tp + 1.6, self.tp + 2.0)
            if up > 0: soldier(c, x, yy, 92, t, self.R, "attack" if charge else "throw", (lt - self.tp) * 1.2 + r, -1)
            jk = (lt - self.tp - 0.5 - r * 0.4) / 0.7
            if 0 < jk < 1 and not charge:
                tx = 500 + r * 400; px = lerp(x0 - 40, tx, jk); py = lerp(y - 190, 980, jk) - 150 * 4 * jk * (1 - jk)
                ang = math.atan2(980 - (y - 190) - 150 * 4 * (1 - 2 * jk), tx - x0); c.drawLine(px - math.cos(ang) * 50, py - math.sin(ang) * 50, px, py, paint("#7A5230", 255, stroke=4))
        self.dunes(c, True)
        for x0, y, r, cav in sorted(self.army, key=lambda u: u[1]):
            s = _depth_s(105, y); hit = lt > self.tp + 1.0 + r * 0.8 and r < 0.4; flee = lt > self.tp + 2.2
            x = x0 + min(lt, self.tp + 1.0) * 260 - (max(0, lt - self.tp - 2.2) * 420 if flee else 0)
            fall = seg(lt, self.tp + 1.0 + r * 0.8, self.tp + 1.5 + r * 0.8) if hit else 0
            if cav and fall == 0: horse(c, x, y, s * 1.15, t, lt * 2.4 + r, -1 if flee else 1, FAC[self.A]["horses"][int(r * 3) % 3], rider_fn(self.A, "flee" if flee else "attack", lt + r, t, -1 if flee else 1))
            else: soldier(c, x, y, s, t, self.A, "flee" if flee else "block", lt * 1.8 + r, -1 if flee else 1, 255, fall)
    def sfx(self):
        t0, tp = self.t0, self.t0 + self.tp
        return [("gallop_many", t0, -8), ("tabl", t0, -11), ("warcry_berber", tp, -6), ("javelin", tp + 0.5, -6), ("javelin", tp + 0.8, -7), ("javelin", tp + 1.1, -8),
                ("arrow_hits", tp + 1.2, -8), ("groan", tp + 1.4, -9), ("warcry_berber", tp + 1.6, -6), ("clash_bed", tp + 1.8, -7), ("crowd_panic", tp + 2.2, -7), ("wind", t0, -14)]
