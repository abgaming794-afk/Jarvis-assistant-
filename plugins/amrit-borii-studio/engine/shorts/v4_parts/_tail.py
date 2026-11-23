
# ================================================================ Bhool-bhulaiya Short: camera, scenes, frame, sfx
Y = PAL["yel"]
STONE = COL["STONE"]
DECCAN_CREDIT = "Photo: Dheepika Karunakar, CC BY-SA 4.0 (Wikimedia Commons)"

def geo_hl(c, cam, key, k, t, col, fill=110, line=True):
    """glowing highlight of a GEO shape (Maharashtra / Crete / Roman Empire) drawn over the map"""
    if k <= 0: return
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]; pul = 0.8 + 0.2 * math.sin(t * 5)
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
    c.drawPath(GEO_PATH[key], paint(col, int(fill * k * pul)))
    if line:
        c.drawPath(GEO_PATH[key], paint(col, int(170 * k), stroke=7 / s, blur=4 / s))
        c.drawPath(GEO_PATH[key], paint("#FFF1C2", int(235 * k), stroke=1.8 / s))
    c.restore()

def card(c, img, k, t, cx, cy, w, cap, sub, credit, ang=0, hls=(), maxh=None):
    """real document/photo in the gold frame (halo, motes, slow push-in); caption text auto-fits the card width"""
    if k <= 0 or img is None: return
    h = w * img.height() / img.width()
    if maxh and h > maxh: w = w * maxh / h; h = maxh
    al = int(255 * clamp(k * 2)); kk = back(clamp(k), 1.4)
    halo = skia.GradientShader.MakeRadial(skia.Point(cx, cy), max(w, h) * 0.8, [skia.ColorSetARGB(int(140 * clamp(k)), 255, 190, 90), skia.ColorSetARGB(0, 255, 160, 60)])
    hp = skia.Paint(); hp.setShader(halo); c.drawCircle(cx, cy, max(w, h) * 0.8, hp)
    for i in range(8):
        a_ = i * 2.4 + t * 0.6; r_ = max(w, h) * (0.5 + 0.08 * math.sin(i * 1.7 + t))
        c.drawCircle(cx + math.cos(a_) * r_ * 0.8, cy + math.sin(a_) * r_ * 0.7, 3 + (i % 3), paint("#FFE2A8", int(150 * clamp(k) * (0.5 + 0.5 * math.sin(t * 3 + i))), blur=2))
    c.save(); c.translate(cx, cy); c.rotate(ang * kk); c.scale(kk, kk); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    cw = max(w, 300); lc = cx - cw / 2
    rrect(c, lc - 16, tp - 16, lc + cw + 16, tp + h + 92, 16, "#FBF3DF", al, shadow=30)
    c.drawRoundRect(skia.Rect(lc - 9, tp - 9, lc + cw + 9, tp + h + 85), 11, 11, paint("#C9A24A", al, stroke=3))
    c.save(); c.clipRect(skia.Rect(l, tp, l + w, tp + h))
    z = 1.0 + 0.05 * clamp((t % 8) / 4)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al); c.restore()
    c.drawRect(skia.Rect(l, tp, l + w, tp + h), paint("#B8862B", al, stroke=3))
    for fx0, fy0, fx1, fy1, hk in hls:
        if hk <= 0: continue
        x0, y0, x1, y1 = l + fx0 * w, tp + fy0 * h, l + fx1 * w, tp + fy1 * h
        c.drawRoundRect(skia.Rect(x0 - 6, y0 - 5, x0 - 6 + (x1 - x0 + 12) * ease_out(hk), y1 + 5), 9, 9, paint("#FF4D5E", al, stroke=4))
    fit = lambda s_, size: min(size, size * (cw + 10) / max(1, text_w(s_, size, FT_BLACK)))
    text(c, cap, cx, tp + h + 44, fit(cap, 34), "#7A1E0E", FT_BLACK, "c", al)
    text(c, sub, cx, tp + h + 76, fit(sub, 23), "#B5651D", FT_BLACK, "c", al)
    c.restore()
    text(c, credit, cx, tp + h + 122, min(17, 17 * (cw + 160) / max(1, text_w(credit, 17, FT_SEMI))), "#DCE3EC", FT_SEMI, "c", int(al * 0.9), shadow=True)

def note(c, s_, k, y0=1086):
    """small dark pill with a yellow dot (e.g. 'chitran - asli photo nahi')"""
    if k <= 0: return
    size = 22; w = text_w(s_, size, FT_SEMI); al = int(255 * clamp(k * 2))
    x0 = DW / 2 - (w + 50) / 2
    rrect(c, x0, y0, x0 + w + 50, y0 + 38, 19, "#0F1B2D", int(al * 0.85)); c.drawCircle(x0 + 20, y0 + 19, 6, paint(Y, al))
    text(c, s_, x0 + 36, y0 + 27, size, "#DCE3EC", FT_SEMI, "l", al)

def strike_chip(c, s_, x, y, k, sk, size=44, bg="#22304A"):
    chip(c, s_, x, y, k, bg=bg, size=size)
    if sk > 0 and k > 0:
        w = text_w(s_, size) + 40
        c.drawLine(x - w / 2, y + 6, x - w / 2 + w * ease_out(sk), y - 18, paint("#FF4D5E", int(255 * clamp(k)), stroke=9, cap_round=True))

def pop_words(c, t, s_, t0, y, size, col, a_):
    size = min(size, size * 980 / max(1, text_w(s_, size)))
    ws = s_.split(" "); tw = sum(text_w(w_, size) for w_ in ws) + text_w(" ", size) * (len(ws) - 1); x = DW / 2 - tw / 2
    for i, w_ in enumerate(ws):
        p = seg(t, t0 + i * 0.11, t0 + i * 0.11 + 0.35); ww = text_w(w_, size)
        if p > 0:
            e = back(p, 2.0) if p < 1 else 1.0
            c.save(); c.translate(x + ww / 2, y + (1 - e) * 30); c.scale(0.7 + 0.3 * e, 0.7 + 0.3 * e)
            text(c, w_, 0, 0, size, col, FT_BLACK, "c", int(255 * clamp(p * 2) * a_), shadow=True); c.restore()
        x += ww + text_w(" ", size)

def poll2(c, items, t):
    """items: (label, colour, t_on)"""
    for i, (s_, col, t0) in enumerate(items):
        kk = ease_out(seg(t, t0, t0 + 0.45))
        if kk <= 0: continue
        y = 520 + i * 150; al = int(255 * clamp(kk * 2)); x0 = 140 + (1 - kk) * 200
        rrect(c, x0, y - 55, 940, y + 55, 55, "#18253A", al, shadow=14)
        c.drawCircle(x0 + 58, y, 36, paint(col, al)); text(c, "ABC"[i], x0 + 58, y + 14, 40, "#FFFFFF", FT_BLACK, "c", al)
        size = min(54, 54 * (940 - x0 - 150) / max(1, text_w(s_, 54)))
        text(c, s_, x0 + 120, y + 19, size, "#F1FAEE", FT_BLACK, "l", al)

# ---------------------------------------------------------------- the labyrinth, drawn in code (chitran, not a photo)
def laby(c, cx, cy, R, n, k, t, a=255, ground=True, spin=0.0):
    """n concentric stone rings with alternating entrance gaps + a tight central spiral.
    Rings appear from the outside in as k goes 0 -> 1 (k*n rings)."""
    if k <= 0 or a <= 0: return
    al = clamp(a / 255)
    if ground:
        g = skia.GradientShader.MakeRadial(skia.Point(cx, cy), R * 1.18, [hexc("#4A5A33", int(235 * al)), hexc("#3A4A2A", int(200 * al)), hexc("#3A4A2A", 0)], [0.0, 0.8, 1.0])
        gp = skia.Paint(); gp.setShader(g); c.drawCircle(cx, cy, R * 1.18, gp)
    r_in = R * 0.17; big = R > 120
    sp = 7.5 if big else 3.2; sr = 3.0 if big else 1.25
    for i in range(n):
        ri = clamp(k * n - i)
        if ri <= 0: break
        r = R - (R - r_in) * i / max(1, n - 1)
        gap = math.radians(26 if big else 34) * (R / max(r, 1)) ** 0.35
        base = math.radians(90 + 180 * (i % 2)) + spin
        sweep = (2 * math.pi - gap) * ease_out(ri)
        if big:
            m = max(6, int(sweep * r / sp))
            for j in range(m):
                th = base + gap / 2 + sweep * j / max(1, m - 1)
                jit = math.sin(i * 7.1 + j * 3.3) * 0.9
                x, y = cx + math.cos(th) * (r + jit), cy + math.sin(th) * (r + jit)
                shade = 225 + int(25 * math.sin(i * 1.3 + j * 0.7))
                c.drawCircle(x + 1.2, y + 1.6, sr, paint("#1B2412", int(160 * al)))
                c.drawCircle(x, y, sr * (0.9 + 0.2 * abs(math.sin(j * 2.1 + i))), paint(STONE, int(shade * al)))
        else:
            rect = skia.Rect(cx - r, cy - r, cx + r, cy + r)
            pth = skia.Path(); pth.addArc(rect, math.degrees(base + gap / 2), math.degrees(sweep))
            c.drawPath(pth, paint(STONE, int(235 * al), stroke=sr * 1.6, cap_round=True))
    sk = clamp(k * n - n + 1.2)
    if sk > 0:                                             # central spiral
        pth = skia.Path(); turns = 2.2; N = 90
        for j in range(int(N * ease_out(sk)) + 1):
            u = j / N; th = spin + u * turns * 2 * math.pi; rr = r_in * (1 - u * 0.92)
            (pth.moveTo if j == 0 else pth.lineTo)(cx + math.cos(th) * rr, cy + math.sin(th) * rr)
        if big:
            pm = skia.PathMeasure(pth, False); L = pm.getLength(); m = max(2, int(L / sp))
            for j in range(m):
                pos = pm.getPosTan(L * j / max(1, m - 1))[0]
                c.drawCircle(pos.x() + 1.2, pos.y() + 1.6, sr, paint("#1B2412", int(160 * al)))
                c.drawCircle(pos.x(), pos.y(), sr, paint("#FFE9B8", int(245 * al)))
        else:
            c.drawPath(pth, paint("#FFE9B8", int(245 * al), stroke=sr * 1.6, cap_round=True))


# ---------------------------------------------------------------- stone labyrinth in perspective on the grass plain (chitran)
_STONES = []
def _stone_list(n=15):
    if _STONES: return _STONES
    r_in = 0.17
    for i in range(n):
        f = 1.0 - (1.0 - r_in) * i / (n - 1)
        gap = math.radians(26) * (1 / f) ** 0.35; base = math.radians(90 + 180 * (i % 2))
        m = int(2 * math.pi * f * 62)
        for j in range(m):
            u = j / m
            th = base + gap / 2 + (2 * math.pi - gap) * u
            jr = 0.006 * math.sin(i * 7.1 + j * 3.3)
            _STONES.append((i, u, (f + jr) * math.cos(th), (f + jr) * math.sin(th), 0.8 + 0.4 * abs(math.sin(j * 2.1 + i * 1.3)), (i * 31 + j * 17) % 5))
    for j in range(70):                                   # central spiral
        u = j / 69; th = u * 2.2 * 2 * math.pi; rr = r_in * (1 - u * 0.9)
        _STONES.append((n, u, rr * math.cos(th), rr * math.sin(th), 0.9, j % 5))
    _STONES.sort(key=lambda q: q[3])                     # back (top of the ellipse) first
    return _STONES
STONE_COLS = ["#6B5D50", "#7A6B5C", "#5A4D42", "#857462", "#665848"]
def stone_laby(c, cx, cy, Rx, k, a=255, tilt=0.33, n=15):
    """15 rings of basalt stones on the ground, seen at an angle; rings appear outside -> in as k goes 0 -> 1"""
    if k <= 0 or a <= 0: return
    al = clamp(a / 255); Ry = Rx * tilt; sc = Rx / 420
    for i, u, x, y, sz, ci in _stone_list(n):
        ri = clamp(k * (n + 1) - i)
        if ri <= 0 or u > ease_out(ri): continue
        d = (1 + y) / 2                                   # 0 = far, 1 = near
        X, Y = cx + x * Rx, cy + y * Ry
        rs = (3.6 + 4.0 * d) * sz * sc
        c.drawOval(skia.Rect(X - rs * 1.1, Y - rs * 0.1, X + rs * 1.3, Y + rs * 0.75), paint("#1E160E", int(150 * al)))
        c.drawOval(skia.Rect(X - rs, Y - rs * 0.62, X + rs, Y + rs * 0.5), paint(STONE_COLS[ci], int(250 * al)))
        c.drawOval(skia.Rect(X - rs * 0.6, Y - rs * 0.55, X + rs * 0.15, Y - rs * 0.1), paint("#D8C6AC", int(170 * al)))

def dim_line(c, p0, p1, k, lab, a=255, off=(0, 0)):
    """measurement line with end ticks that grows from the middle, label pill in the middle"""
    if k <= 0: return
    al = int(a * clamp(k * 2)); e = ease_out(k)
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    q0 = (mx + (p0[0] - mx) * e, my + (p0[1] - my) * e); q1 = (mx + (p1[0] - mx) * e, my + (p1[1] - my) * e)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L * 16, dx / L * 16
    for w_, col_, a_ in ((9, "#000000", 0.55), (4, "#FFFFFF", 1.0)):
        pp = paint(col_, int(al * a_), stroke=w_, cap_round=True)
        c.drawLine(q0[0], q0[1], q1[0], q1[1], pp)
        for q in (q0, q1): c.drawLine(q[0] - nx, q[1] - ny, q[0] + nx, q[1] + ny, pp)
    label(c, lab, mx + off[0], my + off[1], k, col="#0F1B2D", bg="#7FDBFF", size=34)

def person(c, x, y, h, k):
    """simple standing person silhouette, feet at (x, y), height h px"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); s = h / 100; p = paint("#111111", al)
    c.drawOval(skia.Rect(x - 16 * s, y - 4 * s, x + 16 * s, y + 4 * s), paint("#000000", int(al * 0.5)))
    c.drawCircle(x, y - 90 * s, 9 * s, p)
    c.drawRoundRect(skia.Rect(x - 10 * s, y - 79 * s, x + 10 * s, y - 40 * s), 6 * s, 6 * s, p)
    c.drawRoundRect(skia.Rect(x - 9 * s, y - 44 * s, x - 1.5 * s, y), 3 * s, 3 * s, p)
    c.drawRoundRect(skia.Rect(x + 1.5 * s, y - 44 * s, x + 9 * s, y), 3 * s, 3 * s, p)
    c.drawRoundRect(skia.Rect(x - 15 * s, y - 77 * s, x - 9 * s, y - 46 * s), 3 * s, 3 * s, p)
    c.drawRoundRect(skia.Rect(x + 9 * s, y - 77 * s, x + 15 * s, y - 46 * s), 3 * s, 3 * s, p)

STONE_CARD = {}
def stone_card_img():
    """offscreen 'grass plain + stone labyrinth' picture for the hook card"""
    if "img" not in STONE_CARD:
        gi = DOCS.get("grassfull")
        W_, H_ = 800, 600; sf = skia.Surface(W_, H_); cc = sf.getCanvas()
        if gi is not None: draw_img(cc, gi, 0, 0, W_, H_)
        stone_laby(cc, 400, 440, 330, 1.0)
        STONE_CARD["img"] = sf.makeImageSnapshot()
    return STONE_CARD["img"]

# ---------------------------------------------------------------- camera keys (lon, lat, px/deg)
IND0 = (78.6, 21.2, 19.5); MAH = (75.6, 18.7, 80); MID = (52, 28, 5.0); CRETE = (24.9, 35.1, 72); DEC = (78, 19, 11.5)
ROUTE = (54, 18, 10.5); POMP = (44, 31, 12.5); THE = (75.0, 18.6, 95); OTH = (74.9, 17.4, 92)
def _cam_keys():
    b0, f0, c0, a0, s0, p0, th0, o0 = T("bora")[0], T("found")[0], T("crete")[0], T("age")[0], T("strabo")[0], T("pompeii")[0], T("theory")[0], T("others")[0]
    return [(0.0, (78.8, 21.8, 14.0)), (1.6, IND0), (b0, IND0), (b0 + 1.1, MAH), (c0, MAH), (c0 + 0.9, MID), (c0 + 1.8, CRETE),
            (a0, CRETE), (a0 + 0.6, MID), (a0 + 1.5, DEC), (s0, DEC), (s0 + 1.0, ROUTE), (p0, ROUTE), (p0 + 1.0, POMP),
            (th0, POMP), (th0 + 1.2, THE), (o0, THE), (o0 + 0.9, OTH)]
CAM_KEYS = _cam_keys()
def cam_at(t):
    for (t0, a), (t1, b) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_io(seg(t, t0, t1))
            s = math.exp(lerp(math.log(a[2]), math.log(b[2]), k))
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k), s)
    return CAM_KEYS[-1][1] if t > CAM_KEYS[-1][0] else CAM_KEYS[0][1]

PL = dict(solapur=(75.91, 17.66), boramani=(75.75, 17.55), pune=(73.86, 18.52), crete=(24.9, 35.2), knossos=(25.16, 35.30),
          myos=(34.25, 26.15), bab=(43.4, 12.6), socotra=(56, 12.5), barygaza=(72.6, 21.7), muziris=(76.2, 10.2),
          bhokardan=(75.75, 20.27), alex=(29.9, 31.2), pompeii=(14.48, 40.75), kalyan=(73.13, 19.24), paithan=(75.38, 19.48),
          ter=(76.15, 18.32), satara=(74.0, 17.68), sangli=(74.58, 16.85), kolhapur=(74.24, 16.70), kalambi=(74.42, 17.62),
          sata_lbl=(78.6, 20.6), rome_lbl=(18, 45.5))

# ---------------------------------------------------------------- timeline (BCE supported)
TL = [(-400, "KNOSSOS SIKKA"), (100, "SATAVAHANA"), (2026, "AAJ")]
def timeline(c, year, k):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); x0, x1, y = 110, 970, 1220
    def X(yr):
        pts = [(-500, 110), (-400, 170), (100, 520), (2026, 970)]
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= yr <= b: return lerp(xa, xb, (yr - a) / (b - a))
        return x0 if yr < -500 else x1
    c.drawRoundRect(skia.Rect(x0, y - 4, x1, y + 4), 4, 4, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 4, X(year), y + 4), 4, 4, paint(Y, al))
    for yr, lab in TL:
        on = abs(yr - year) < 30
        c.drawCircle(X(yr), y, 12 if on else 8, paint(Y if X(yr) <= X(year) + 1 else "#3E5068", al))
        text(c, lab, X(yr), y + 52, 28 if on else 22, "#F1FAEE" if on else PAL["muted"], FT_BLACK if on else FT_SEMI, "c", al)
    lab = "c. 400 BCE" if year < -300 else ("c. 1st-2nd SADI CE" if year < 400 else f"{int(year)}")
    pill(c, lab, X(year), y - 50, 34, Y, fg="#0F1B2D", a=al)

def year_at(t):
    c0, m1, a0, o0 = T("crete")[0], T("myth")[1], T("age")[0], T("others")[0]
    keys = [(0, 2026), (c0 + 0.2, 2026), (c0 + 1.6, -400), (m1, -400), (a0 + 1.0, 100), (o0, 100), (o0 + 0.9, 2026)]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp(a, b, ease_io(seg(t, t0, t1)))
    return 2026

def lonlat_route(c, cam, pts, k, col=Y, w=5, dash=True, a=255, head=True):
    route(c, [scr(cam, *p) for p in pts], k, col=col, w=w, dash=dash, a=a, head=head)

def poly_at(pts, f):
    """point at fraction f along a screen polyline"""
    L = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]; tot = sum(L) or 1; d = f * tot
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l: q = d / max(l, 1e-6); return a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q
        d -= l
    return pts[-1]

# ---------------------------------------------------------------- frame
WM = None
def frame(c, t):
    global WM
    load()
    if WM is None: WM = WorldMap()
    cam = cam_at(t)
    def S(k): return scr(cam, *PL[k])
    def act(k, pad_in=0.0, pad_out=0.0):
        a, b = T(k); return a - pad_in <= t < b + pad_out
    def kin(k, d=0.5, off=0.0): return seg(t, T(k)[0] + off, T(k)[0] + off + d)
    def at(t0, d=0.45): return seg(t, t0, t0 + d)
    def out(k, d=0.3): return 1 - seg(t, T(k)[1] - d, T(k)[1])
    def win(t0, t1, d=0.35): return at(t0, d) * (1 - seg(t, t1 - 0.25, t1))

    yr = year_at(t)
    b0, c0, a0, o0, cta0 = T("bora")[0], T("crete")[0], T("age")[0], T("others")[0], T("cta")[0]
    th1 = T("theory")[1]
    # map of ITS time (user rule): tiranga India in present-day scenes (hook, find, other finds); plain land in the
    # Crete scenes (c. 400 BCE); c. 100 CE polities in bhagwa shades in the Satavahana-era scenes
    hist = seg(t, c0, c0 + 0.6) * (1 - seg(t, o0 - 0.2, o0 + 0.6))
    era = seg(t, a0 + 0.3, a0 + 1.1) * (1 - seg(t, o0 - 0.2, o0 + 0.6))
    zk = seg(cam[2], 20, 40)                                   # zoomed into Maharashtra: no giant chakra, lighter fill
    india_a = 190 * (1 - hist) * (1 - 0.55 * zk)
    c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"]))
    c.save(); c.translate(0, MAP_CY - DH / 2)
    draw_map(c, WM, cam, fills={"IND": (COL["NOW"], int(india_a))}, border_a=1 - 0.75 * hist)
    c.restore()
    cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
    now_a = 235 * (1 - hist) * (1 - zk)
    if now_a > 0:
        if "NOW" not in EMP_PATH: EMP_PATH["NOW"] = _poly_path(WM.geoms["IND"], 0.01)
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
        wave_flag(c, EMP_PATH["NOW"], "NOWV", t, min(255, now_a), s_); c.restore()
    if era > 0:
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
        for j, (nm, pth) in enumerate(ERA_PATH["CE100"]):
            c.drawPath(pth, paint(BHAGWA[j % len(BHAGWA)], int(175 * era)))
            c.drawPath(pth, paint("#FFE7C2", int(150 * era), stroke=1.0 / s_))
        c.restore()
    rome_a = seg(t, T("strabo")[0] + 0.4, T("strabo")[0] + 1.2) * (1 - seg(t, th1 - 0.2, th1 + 0.4))
    geo_hl(c, cam, "ROME", rome_a * 0.85, t, COL["ROME"], fill=120)

    # ================= hook: BHOOL-BHULAIYA letter by letter, Maharashtra lights up, Knossos coin, '?'
    if t < b0 + 0.8:
        ho = 1 - seg(t, b0 - 0.15, b0 + 0.2)
        tm = kw(0, "Maharashtra"); tb = kw(0, "bhool"); tg = kw(0, "Greek"); tq = kw(1, "kaise")
        tgh = kw(0, "ghaas"); tpt = kw(0, "patthar")
        # every thing named in line 1 lights up on its word: Maharashtra -> ghaas ka maidan -> patthar ki bhool-bhulaiya
        mk = at(tm + 0.15, 0.4) * ho
        geo_hl(c, cam, "MH", mk, t, Y, fill=200)
        mx, my = scr(cam, 76.4, 19.3)
        rb = seg(t, tm + 0.15, tm + 1.0)
        if 0 < rb < 1: c.drawCircle(mx, my, 40 + 120 * ease_out(rb), paint(Y, int(220 * (1 - rb) * ho), stroke=6))
        label(c, "MAHARASHTRA", mx - 215, my - 20, mk, col="#0F1B2D", bg=Y, size=34)
        x, y = S("boramani")
        gk = at(tgh - 0.1, 0.4) * ho
        if gk > 0:                                           # ghaas ka maidan: green grass glow + blades
            gr = 58 * back(clamp(gk)); pul = 0.85 + 0.15 * math.sin(t * 5)
            sh_ = skia.GradientShader.MakeRadial(skia.Point(x, y), gr, [hexc("#7BD148", int(230 * gk * pul)), hexc("#3FA34D", int(150 * gk)), hexc("#3FA34D", 0)], [0.0, 0.6, 1.0])
            gp = skia.Paint(); gp.setShader(sh_); c.drawCircle(x, y, gr, gp)
            for j in range(16):
                a_ = j * 2.39996; rr = gr * (0.25 + 0.6 * ((j * 0.37) % 1.0))
                bx, by = x + math.cos(a_) * rr, y + math.sin(a_) * rr * 0.8
                sw = math.sin(t * 4 + j) * 3
                c.drawLine(bx, by, bx + sw, by - 11, paint("#B8F27C", int(230 * gk), stroke=2.2, cap_round=True))
                c.drawLine(bx + 3, by, bx + 5 + sw, by - 8, paint("#8DDB5A", int(200 * gk), stroke=2, cap_round=True))
            c.drawCircle(x, y, gr, paint("#B8F27C", int(220 * gk), stroke=3))
        label(c, "GHAAS KA MAIDAN", x - 200, y + 75, gk, col="#0F1B2D", bg="#8DDB5A", size=32)
        card(c, DOCS.get("grass"), win(tgh - 0.15, tpt + 0.05), t, 790, 640, 330, "GHAAS KA MAIDAN (SEMI-ARID)", "AI chitran - asli photo nahi",
             "AI-generated illustration (not Boramani)")
        lk = seg(t, tpt - 0.1, tpt + 1.4)                    # patthar ki bhool-bhulaiya: the maze builds and grows
        lr = lerp(30, 46, ease_out(at(tpt - 0.1, 0.6)))
        laby(c, x, y, lr, 15, lk, t, 255 * ho, ground=False, spin=t * 0.4)
        ring_highlight(c, x, y, lr + 16, at(tpt - 0.1, 0.4) * ho, t)
        card(c, stone_card_img(), win(tpt + 0.05, tg - 0.2), t, 790, 640, 330, "PATTHAR KI BHOOL-BHULAIYA", "Chitran (andaaza) - asli photo nahi",
             "Drawing on an AI-generated grass image")
        label(c, "PATTHAR KI BHOOL-BHULAIYA", 540, y + 150, at(tpt - 0.05, 0.4) * ho * (1 - at(tg - 0.3, 0.3)), col="#0F1B2D", bg=STONE, size=36)
        word = "BHOOL-BHULAIYA"; size = min(132, 132 * 900 / text_w(word + "?", 132))
        L = []
        for i, ch in enumerate(word):
            p = seg(t, 0.1 + i * 0.07, 0.65 + i * 0.07); e = back(p, 1.6) if p < 1 else 1.0
            L.append(dict(ch=ch, al=clamp(p * 1.6), dy=(1 - e) * 90, col=STONE if ch != "-" else Y, sy=0.55 + 0.45 * e))
        qd = seg(t, tq - 0.1, tq + 0.45)
        L.append(dict(ch="?", w=ease_out(qd), al=qd, dy=-(1 - back(qd, 2.2)) * 120 if qd < 1 else 0, col=Y, rot=(1 - qd) * -25))
        word_row(c, L, DW / 2, 300, size, 255 * ease_io(seg(t, 0.05, 0.6)) * ho, glow=Y)
        sh = max(seg(t, 1.2, 1.9) if t < 1.9 else 0.0, seg(t, tb, tb + 0.7) if t >= tb else 0.0)
        if 0 < sh < 1:
            bw = text_w(word, size); x0 = DW / 2 - bw / 2 - 60 + (bw + 120) * ease_io(sh)
            g_ = skia.GradientShader.MakeLinear([skia.Point(x0 - 60, 0), skia.Point(x0 + 60, 0)],
                                                [skia.ColorSetARGB(0, 255, 255, 255), skia.ColorSetARGB(int(150 * ho), 255, 255, 255), skia.ColorSetARGB(0, 255, 255, 255)])
            pp = skia.Paint(); pp.setShader(g_); pp.setBlendMode(skia.BlendMode.kPlus)
            c.save(); c.skew(-0.25, 0); c.translate(75, 0); c.drawRect(skia.Rect(x0 - 60, 180, x0 + 60, 340), pp); c.restore()
        q1 = 1 - seg(t, tg - 0.3, tg)
        if q1 > 0: pop_words(c, t, "MAHARASHTRA MEIN MILI!", tm - 0.1, 408, 50, "#F1FAEE", q1 * ho)
        if t > tg - 0.3: pop_words(c, t, "DESIGN GREEK SIKKON JAISA?", tg - 0.1, 408, 50, Y, ho)
        cw = win(tg - 0.15, b0 + 0.2)
        card(c, DOCS.get("coin"), cw, t, 815, 930, 250, "KNOSSOS KA SIKKA", "Crete, c. 400 BCE", "Photo: AlMare, CC BY-SA 3.0",
             hls=[(0.14, 0.12, 0.86, 0.84, seg(t, tg + 0.3, tg + 0.8))])
        if cw > 0:
            p0 = (815 - 140, 930 - 40); p1 = (x + 30, y - 10)
            route(c, [p0, ((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 90), p1], ease_out(at(tg + 0.2, 0.6)), col=Y, w=4, a=int(255 * cw))
    # ================= bora: Solapur / Boramani, then the big labyrinth counts its rings
    if act("bora", 0, 0.3):
        e = 1 - seg(t, T("bora")[1] - 0.1, T("bora")[1] + 0.3)
        geo_hl(c, cam, "MH", kin("bora", 0.5) * e * (1 - at(us(3) - 0.2, 0.4)), t, Y, fill=60)
        sk = at(kw(2, "Solapur") - 0.1, 0.4) * (1 - at(us(3) - 0.3, 0.4))
        spotlight(c, *S("boramani"), sk, t, r0=80)
        label(c, "SOLAPUR", S("solapur")[0] + 110, S("solapur")[1] - 70, at(kw(2, "Solapur") - 0.1) * e * (1 - at(us(3) - 0.3, 0.4)), size=30)
        label(c, "BORAMANI GHAAS KA MAIDAN", S("boramani")[0] - 10, S("boramani")[1] + 95, at(kw(2, "Boramani") - 0.1) * e * (1 - at(us(3) - 0.3, 0.4)),
              col="#0F1B2D", bg=Y, size=30)
        headline(c, "SOLAPUR KA BORAMANI", kin("bora", 0.5, 0.3) * (1 - at(us(3) - 0.4, 0.3)), col=Y, sub="ghaas ka maidan, Maharashtra")
        bk = at(us(3) - 0.3, 0.5) * e
        if bk > 0:
            c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(170 * bk)))
            gi = DOCS.get("grassfull")
            gy0, gh_ = 420, DW * 0.75
            if gi is not None:                              # AI grass plain, edges fade into the dark map
                c.saveLayer(skia.Rect(0, gy0, DW, gy0 + gh_), None)
                draw_img(c, gi, 0, gy0, DW, gy0 + gh_, int(255 * bk))
                mk_ = skia.GradientShader.MakeLinear([skia.Point(0, gy0), skia.Point(0, gy0 + gh_)],
                                                     [skia.ColorSetARGB(0, 0, 0, 0), skia.ColorSetARGB(255, 0, 0, 0), skia.ColorSetARGB(255, 0, 0, 0), skia.ColorSetARGB(0, 0, 0, 0)], [0.0, 0.12, 0.88, 1.0])
                mp = skia.Paint(); mp.setShader(mk_); mp.setBlendMode(skia.BlendMode.kDstIn); c.drawRect(skia.Rect(0, gy0, DW, gy0 + gh_), mp)
                c.restore()
            nk = seg(t, us(3) - 0.1, ue(3) - 0.2)
            LCX, LCY, LRX = 540, 990, 455; LRY = LRX * 0.33
            stone_laby(c, LCX, LCY, LRX, nk, 255 * bk)
            t50 = kw(3, "50"); dk = at(t50 - 0.15, 0.5) * e
            dim_line(c, (LCX - LRX, LCY + LRY + 45), (LCX + LRX, LCY + LRY + 45), dk, "50 FOOT", off=(0, 0))
            dim_line(c, (LCX - LRX - 40, LCY - LRY), (LCX - LRX - 40, LCY + LRY), at(t50 + 0.35, 0.5) * e, "50 FT", off=(55, 0))
            person(c, LCX + LRX * 0.62, LCY + LRY * 0.78, 98, at(t50 + 0.6, 0.4) * e)
            label(c, "INSAAN ~5.5 FT", LCX + LRX * 0.62, LCY + LRY * 0.78 + 34, at(t50 + 0.6, 0.4) * e * (1 - at(us(4) + 1.2, 0.3)), size=24)
            n_on = min(15, int(nk * 15 + 0.999))
            chip(c, f"{n_on} GOL CHAKKAR", 540, 760, bk, bg=Y, fg="#0F1B2D", size=44)
            label(c, "~50 x 50 FOOT", 540, 330, at(kw(3, "50") - 0.1) * e * (1 - at(us(4) - 0.3, 0.25)), col="#0F1B2D", bg="#7FDBFF", size=44)
            note(c, "Chitran (andaaza): AI ghaas + code se patthar - Boramani ka asli photo nahi", bk, y0=1262)
            rk = at(us(4) - 0.1, 0.4) * e
            chip(c, "INDIA KI SABSE BADI GOL!", 540, 300, rk, bg="#FF9933", fg="#0F1B2D", size=44)
            strike_chip(c, "PICHHLA RECORD: 11 CHAKKAR", 540, 385, at(kw(4, "pichhla") - 0.1) * e, seg(t, kw(4, "11") - 0.1, kw(4, "11") + 0.4), size=34)
    # ================= found: who found it
    if act("found"):
        e = out("found")
        geo_hl(c, cam, "MH", e, t, Y, fill=60)
        headline(c, "KISNE DHOONDHA?", kin("found", 0.5, 0.1), col="#F1FAEE")
        spotlight(c, *S("pune"), at(kw(5, "Deccan") - 0.1) * e, t, r0=70)
        label(c, "PUNE", S("pune")[0], S("pune")[1] - 70, at(kw(5, "Deccan") - 0.1) * e, size=28)
        ring_highlight(c, *S("boramani"), 34, kin("found") * e, t)
        chip(c, "DHOONDHA: LOCAL CONSERVATION TEAM", 540, 410, at(kw(5, "local") - 0.15) * e, bg="#2E7D4F", size=32)
        chip(c, "PEHCHANA: SACHIN PATIL, DECCAN COLLEGE", 540, 480, at(kw(5, "Deccan") - 0.15) * e, bg="#22304A", size=32)
        card(c, DOCS.get("deccan"), at(kw(5, "Deccan") - 0.2, 0.4) * e, t, 540, 790, 560, "DECCAN COLLEGE, PUNE", "Sachin Patil yahan ke archaeologist hain",
             DECCAN_CREDIT)
        note(c, "Sachin Patil ki free-licence photo uplabdh nahi", at(kw(5, "Sachin") - 0.1) * e, y0=1150)
        note(c, "Report: Times of India, 19 Dec 2025", at(kw(5, "Sachin")) * e, y0=1200)
    # ================= crete: fly to Greece's Crete, Knossos coin
    if act("crete", 0, 0.2):
        e = 1 - seg(t, T("crete")[1] - 0.1, T("crete")[1] + 0.2)
        tc = kw(6, "Crete"); tk = kw(7, "Knossos")
        headline(c, "GREECE KA CRETE DWEEP", kin("crete", 0.5, 0.2), col=COL["GREEK"])
        geo_hl(c, cam, "CRETE", at(tc - 0.1, 0.4) * e, t, COL["GREEK"], fill=150)
        label(c, "CRETE", S("crete")[0] - 40, S("crete")[1] - 90, at(tc - 0.1) * e * (1 - at(tk - 0.2, 0.3)), col="#0F1B2D", bg=COL["GREEK"], size=34)
        spotlight(c, *S("knossos"), at(tk - 0.2) * e * (1 - at(tk + 0.4, 0.3)), t, r0=50, col=COL["GREEK"])
        card(c, DOCS.get("coin"), win(tk - 0.1, T("crete")[1] + 0.2), t, 540, 760, 470, "KNOSSOS KA CHAANDI KA SIKKA", "c. 400 BCE - Heraklion Museum, Crete",
             "Photo: AlMare, CC BY-SA 3.0 (Wikimedia Commons)", hls=[(0.14, 0.12, 0.86, 0.84, seg(t, kw(7, "bhool") - 0.1, kw(7, "bhool") + 0.4))])
    # ================= myth: Daedalus / Minotaur
    if act("myth"):
        e = out("myth"); td = kw(8, "Daedalus")
        headline(c, "MITHAK: MINOTAUR KI QAID", kin("myth", 0.5, 0.1), col="#FF8A65")
        card(c, DOCS.get("daedalus"), at(td - 0.3, 0.4) * e, t, 540, 760, 900, "DAEDALUS (RAJA MINOS KA KARIGAR)", "Roman mosaic, Zeugma (Turkey) - kahani ka chitra",
             "Photo: Dick Osseman (Dosseman), CC BY-SA 4.0", hls=[(0.71, 0.37, 0.81, 0.41, seg(t, td + 0.1, td + 0.5))])
        chip(c, "KAHANI HAI, ITIHAAS NAHI", 540, 1090, at(kw(8, "Minotaur") - 0.1) * e, bg="#22304A", size=30)
    # ================= age: c. 2000 years, Satavahana era map
    if act("age"):
        e = out("age")
        tn = kw(9, "2000")
        if t < us(10) - 0.1: headline(c, "~2000 SAAL PURANI?", at(tn - 0.2, 0.6) * e, col=Y, sub="Satavahana daur")
        else: headline(c, "ABHI ANDAAZA HAI", at(us(10) - 0.15, 0.5) * e, col="#FF6B75", sub="pakki jaanch baaki")
        label(c, "SATAVAHANA", S("sata_lbl")[0], S("sata_lbl")[1], at(kw(9, "Satavahana") - 0.1) * e, col="#0F1B2D", bg=Y, size=34)
        laby(c, *S("boramani"), 18, 15, 1.0, t, 255 * kin("age") * e, ground=False)
        ring_highlight(c, *S("boramani"), 28, kin("age") * e, t)
        stamp(c, "JAANCH JAARI", 760, 1080, 46, "#FF4D5E", at(kw(10, "jaanch") - 0.1, 0.35) * e)
    # ================= strabo: 120 ships a year Egypt -> India
    if act("strabo", 0, 0.2):
        e = 1 - seg(t, T("strabo")[1] - 0.1, T("strabo")[1] + 0.2)
        headline(c, "ROMAN DAUR KA VYAPAR", kin("strabo", 0.5, 0.1), col=COL["RED"])
        rk = seg(t, kw(11, "120") - 0.4, kw(11, "India") + 0.2)
        r1 = [PL["myos"], (38.5, 19), PL["bab"], PL["socotra"], (64, 17), PL["barygaza"]]
        r2 = [PL["socotra"], (66, 10), PL["muziris"]]
        lonlat_route(c, cam, r1, ease_out(rk), col=Y, w=5, a=int(255 * e))
        lonlat_route(c, cam, r2, ease_out(seg(rk, 0.5, 1)), col=Y, w=4, a=int(255 * e))
        if rk > 0.3:
            pts = [scr(cam, *p) for p in r1]
            for j in range(4):
                f = ((t * 0.12 + j * 0.25) % 1.0)
                sx, sy = poly_at(pts, f)
                ic_ship(c, sx, sy - 8, 0.55, col="#F1FAEE", a=int(235 * e * clamp((rk - 0.3) * 3)))
        label(c, "EGYPT", S("myos")[0] - 40, S("myos")[1] - 60, at(kw(11, "Egypt") - 0.15) * e, size=28)
        label(c, "BHARUCH (BARYGAZA)", S("barygaza")[0] - 60, S("barygaza")[1] - 70, at(kw(11, "India") - 0.1) * e, size=24)
        label(c, "ROMAN SAMRAJYA", S("rome_lbl")[0] + 40, S("rome_lbl")[1], kin("strabo", 0.5, 0.6) * e, col="#FFFFFF", bg=COL["ROME"], size=26)
        chip(c, "120 JAHAZ / SAAL", 540, 420, at(kw(11, "120") - 0.1) * e, bg=Y, fg="#0F1B2D", size=48)
        note(c, "Strabo, Geography 2.5.12 (c. 25 BCE)", at(kw(11, "Strabo") - 0.1) * e, y0=1090)
    # ================= ship coin
    if act("ship"):
        e = out("ship")
        headline(c, "SATAVAHANA SIKKE PE JAHAZ", kin("ship", 0.5, 0.0), col=Y)
        card(c, DOCS.get("ship"), at(us(12) - 0.15, 0.4) * e, t, 540, 740, 520, "VASISHTHIPUTRA PULAMAVI KA SIKKA",
             "Seese ka sikka, 1st-2nd sadi CE - British Museum", "Photo: PHGCOM - public domain (Wikimedia Commons)",
             hls=[(0.12, 0.08, 0.92, 0.72, seg(t, kw(12, "jahaz") - 0.1, kw(12, "jahaz") + 0.4))])
    # ================= pompeii: ivory Lakshmi / yakshi, perhaps from Bhokardan
    if act("pompeii", 0, 0.2):
        e = 1 - seg(t, T("pompeii")[1] - 0.1, T("pompeii")[1] + 0.2)
        tp_ = kw(13, "Pompeii"); tm_ = kw(13, "murti"); tbk = kw(13, "Bhokardan")
        headline(c, "POMPEII MEIN INDIA?", kin("pompeii", 0.5, 0.0), col="#FF8A65", sub="Vesuvius ne 79 CE mein dhak diya")
        spotlight(c, *S("pompeii"), at(tp_ - 0.2) * e * (1 - at(tm_ - 0.3, 0.3)), t, r0=60)
        label(c, "POMPEII (ITALY)", S("pompeii")[0] + 50, S("pompeii")[1] - 75, at(tp_ - 0.2) * e, size=28)
        rp = [PL["bhokardan"], PL["barygaza"], (64, 17), PL["socotra"], PL["bab"], (38.5, 19), PL["myos"], PL["alex"], (22, 35.5), (17, 38.5), PL["pompeii"]]
        lonlat_route(c, cam, rp, ease_out(seg(t, tbk - 0.6, tbk + 0.6)), col="#FFB054", w=5, a=int(255 * e))
        ring_highlight(c, *S("bhokardan"), 22, at(tbk - 0.2) * e, t, col="#FF9933")
        label(c, "BHOKARDAN", S("bhokardan")[0] - 80, S("bhokardan")[1] - 55, at(tbk - 0.2) * e, col="#0F1B2D", bg="#FF9933", size=28)
        ck = win(tm_ - 0.3, tbk - 0.05)
        card(c, DOCS.get("lakshmi"), ck, t, 540, 720, 300, "LAKSHMI YA YAKSHI? (behes)", "Haathi-daant, 1st sadi CE - Naples Museum",
             "Photo: Sailko, CC BY-SA 3.0 (Wikimedia Commons)", maxh=560)
        chip(c, "SHAYAD BHOKARDAN (MAHARASHTRA) MEIN BANI", 540, 1100, at(tbk - 0.1) * e, bg="#FF9933", fg="#0F1B2D", size=28)
    # ================= theory: trade markers, coast -> Paithan, Ter
    if act("theory"):
        e = out("theory")
        headline(c, "EK THEORY: RAASTE KE NISHAAN", kin("theory", 0.5, 0.1), col=Y)
        tp_ = kw(14, "Paithan"); tt_ = kw(14, "Ter ")
        rt = [PL["kalyan"], (74.4, 19.35), PL["paithan"], PL["ter"]]
        lonlat_route(c, cam, rt, ease_out(seg(t, kw(14, "samundar") - 0.3, tt_ + 0.4)), col=Y, w=6, a=int(255 * e))
        lonlat_route(c, cam, [PL["ter"], PL["boramani"]], ease_out(seg(t, tt_ + 0.2, tt_ + 0.9)), col=Y, w=4, a=int(200 * e))
        label(c, "SAMUNDAR KINARA (KALYAN)", S("kalyan")[0] + 30, S("kalyan")[1] + 70, at(kw(14, "samundar") - 0.1) * e, size=24)
        label(c, "PAITHAN", S("paithan")[0], S("paithan")[1] - 60, at(tp_ - 0.1) * e, col="#0F1B2D", bg=Y, size=30)
        label(c, "TER (TAGARA)", S("ter")[0] + 90, S("ter")[1] - 40, at(tt_ - 0.1) * e, col="#0F1B2D", bg=Y, size=30)
        pul = 0.6 + 0.4 * math.sin(t * 6)
        laby(c, *S("boramani"), 22, 15, 1.0, t, 255 * kin("theory") * e * pul, ground=False)
        label(c, "BORAMANI", S("boramani")[0], S("boramani")[1] + 55, kin("theory", 0.5, 0.3) * e, size=24)
        note(c, "Theory hai - pakka saboot abhi nahi", at(kw(14, "theory") - 0.1) * e, y0=1090)
    # ================= others: Satara, Sangli, Kolhapur + Kalambi plan
    if act("others"):
        e = out("others")
        headline(c, "AUR BHI MILI HAIN!", kin("others", 0.5, 0.0), col="#7FDBFF")
        geo_hl(c, cam, "MH", kin("others", 0.6) * e, t, Y, fill=40)
        for key, w_, dx, dy in (("satara", "Satara", -110, -55), ("sangli", "Sangli", 110, 0), ("kolhapur", "Kolhapur", -120, 40)):
            x, y = S(key); kk = at(kw(15, w_) - 0.15) * e
            laby(c, x, y, 16, 9, kk, t, 255 * kk, ground=False)
            label(c, w_.upper(), x + dx, y + dy, kk, col="#0F1B2D", bg="#7FDBFF", size=26)
        laby(c, *S("boramani"), 16, 15, 1.0, t, 200 * e, ground=False)
    card(c, DOCS.get("kalambi"), win(kw(15, "Kolhapur") + 0.35, kw(16, "kode") + 0.15), t, 540, 760, 400, "KALAMBI-III (KHATAV, SATARA)",
         "patthar ki bhool-bhulaiya ka naksha", "Phoenixhit, CC0 (Wikimedia Commons)")
    # ================= chakra: kode / chakravyuh
    if act("chakra", 0, 0.2):
        e = 1 - seg(t, T("chakra")[1] - 0.1, T("chakra")[1] + 0.2)
        tk_ = kw(16, "kode"); tc_ = kw(16, "chakravyuh"); ta_ = kw(16, "Abhimanyu")
        headline(c, "LOCAL NAAM", kin("chakra", 0.5, 0.0), col=Y)
        chip(c, "KODE = PAHELI", 330, 410, at(tk_ - 0.1) * e, bg=Y, fg="#0F1B2D", size=36)
        chip(c, "CHAKRAVYUH", 760, 410, at(tc_ - 0.1) * e, bg="#FF9933", fg="#0F1B2D", size=36)
        card(c, DOCS.get("halebid"), at(tc_ - 0.2, 0.4) * e, t, 540, 790, 470, "ABHIMANYU AUR CHAKRAVYUH (MAHABHARATA)",
             "Hoysaleswara mandir, Halebidu - 12vi sadi", "Photo: Calvinkrishy, CC BY-SA 3.0 (Wikimedia Commons)",
             hls=[(0.05, 0.02, 0.95, 0.98, seg(t, ta_ - 0.1, ta_ + 0.4))])
    # ================= CTA
    if act("cta", 0, 1):
        k = kin("cta", 0.6)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(238 * k)))
        laby(c, 540, 1500, 120, 15, 1.0, t, 70 * k, ground=False, spin=t * 0.15)
        headline(c, "AAPKO KYA LAGTA HAI?", k, y=230)
        poll2(c, [("VYAPAR KA NISHAAN", "#C46A12", kw(18, "Vyapariyon") - 0.15), ("POOJA KI JAGAH", "#2E7D4F", kw(18, "pooja") - 0.15),
                  ("CHAKRAVYUH", "#2F6FB5", kw(18, "chakravyuh") - 0.15)], t)
        label(c, "COMMENT KARO", DW / 2, 1040, at(kw(19, "Comment") - 0.1, 0.5), col="#FFFFFF", bg=PAL["axis"], size=44)
        subscribe_btn(c, at(kw(19, "subscribe") - 0.4, 0.5), t, kw(19, "subscribe"))

    # era chip + footers
    if era > 0.5 and t < o0:
        s_ = "c. 100 CE ka naksha (andaazan)"; w_ = text_w(s_, 22, FT_SEMI)
        x0_ = DW / 2 - (w_ + 50) / 2
        rrect(c, x0_, 1432, x0_ + w_ + 50, 1470, 19, "#3A2410", 215); c.drawCircle(x0_ + 20, 1451, 7, paint("#FF9933"))
        text(c, s_, x0_ + 36, 1459, 22, "#FFE7C2", FT_SEMI, "l", 255)
    tg = kw(0, "Greek")
    doc_up = (tg - 0.2 < t < b0 + 0.5) or (act("found") and t > kw(5, "Deccan") - 0.3) or (act("bora") and t > us(3) - 0.4) or (act("crete") and t > kw(7, "Knossos") - 0.2) or act("myth") \
        or act("ship") or (act("pompeii") and kw(13, "murti") - 0.4 < t < kw(13, "Bhokardan")) or act("others") or act("chakra")
    if 0.6 < t < cta0 and not doc_up:
        timeline(c, yr, seg(t, 0.6, 1.2))
    for a, b, cap in CAPS:
        if a - 0.05 <= t < b + 0.12: caption(c, cap, seg(t, a - 0.05, a + 0.08)); break
    if 2.0 < t < cta0:
        if era > 0.3 or rome_a > 0.3:
            text(c, "Approx. historical borders: historical-basemaps (A. Ourednik)", DW / 2, 1505, 19, PAL["muted"], FT_SEMI, "c", 210)
        text(c, "Natural Earth; India boundary as per Survey of India", DW / 2, 1532, 19, PAL["muted"], FT_SEMI, "c", 210)
    draw_img(c, LOGO, DW - 150, 40, DW - 40, 150, 200)
    grain(c, t, 8); vignette(c, 120)

if __name__ == "__main__":
    if sys.argv[1] == "still":
        od = sys.argv[2]; os.makedirs(od, exist_ok=True)
        for ts in sys.argv[3:]:
            render_still(float(ts), f"{od}/s_{float(ts):06.2f}.png"); print("ok", ts)
    elif sys.argv[1] == "times":
        for i, u in enumerate(UN): print(i, u["start"], u["end"], u["text"][:60])
        for k_, (a_, b_) in SC_T.items(): print(k_, round(a_, 2), round(b_, 2))

def sfx_events():
    """(name, time, gain_db) keyed to the same word times as the visuals"""
    tg = kw(0, "Greek")
    E = [("whoosh_long", 0.15, -14), ("pop", kw(0, "Maharashtra") + 0.15, -14), ("pop", kw(0, "ghaas") - 0.1, -15), ("ding", kw(0, "patthar") - 0.1, -15),
         ("pop", tg - 0.15, -13), ("boom", kw(1, "kaise") - 0.1, -13)]
    for k_ in ("bora", "found", "crete", "myth", "age", "strabo", "ship", "pompeii", "theory", "others", "chakra", "cta"):
        E.append(("whoosh_fast", T(k_)[0], -19))
    for j in range(15): E.append(("pop", us(3) - 0.1 + j * (ue(3) - 0.1 - us(3)) / 15, -22))
    E += [("pop", kw(2, "Solapur") - 0.1, -15), ("ding", kw(2, "Boramani") - 0.1, -15), ("pop", kw(3, "50") - 0.1, -15),
          ("ding", us(4) - 0.1, -13), ("glitch", kw(4, "11") - 0.1, -15),
          ("pop", kw(5, "local") - 0.15, -15), ("pop", kw(5, "Deccan") - 0.2, -14), ("pop", kw(0, "patthar") + 0.05, -15), ("whoosh_fast", kw(3, "50") - 0.15, -16), ("pop", kw(3, "50") + 0.6, -17),
          ("drag", T("crete")[0] + 0.1, -16), ("pop", kw(6, "Crete") - 0.1, -15), ("pop", kw(7, "Knossos") - 0.1, -13),
          ("pop", kw(8, "Daedalus") - 0.3, -14), ("ding", kw(9, "2000") - 0.2, -14), ("stamp", kw(10, "jaanch") - 0.1, -12),
          ("drag", kw(11, "120") - 0.4, -16), ("ding", kw(11, "120") - 0.1, -13), ("pop", us(12) - 0.15, -13),
          ("pop", kw(13, "Pompeii") - 0.2, -15), ("pop", kw(13, "murti") - 0.3, -13), ("drag", kw(13, "Bhokardan") - 0.6, -16),
          ("ding", kw(13, "Bhokardan") - 0.1, -14), ("drag", kw(14, "samundar") - 0.3, -17), ("pop", kw(14, "Paithan") - 0.1, -15),
          ("pop", kw(14, "Ter ") - 0.1, -15), ("pop", kw(15, "Satara") - 0.15, -16), ("pop", kw(15, "Sangli") - 0.15, -16),
          ("pop", kw(15, "Kolhapur") - 0.15, -16), ("pop", kw(15, "Kolhapur") + 0.35, -14), ("pop", kw(16, "kode") - 0.1, -15),
          ("ding", kw(16, "chakravyuh") - 0.2, -13),
          ("pop", kw(18, "Vyapariyon") - 0.15, -16), ("pop", kw(18, "pooja") - 0.15, -16), ("pop", kw(18, "chakravyuh") - 0.15, -16),
          ("pop", kw(19, "Comment") - 0.1, -14), ("ding", kw(19, "subscribe") + 0.35, -12)]
    return sorted(E, key=lambda e: e[1])
