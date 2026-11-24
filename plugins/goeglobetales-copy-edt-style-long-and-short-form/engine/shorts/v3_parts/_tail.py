
# ================================================================ Indian Ocean Short: camera, scenes, frame, sfx
Y = PAL["yel"]
OC_GLOW = {"ATL": [(-35, 25, 38), (-15, -20, 30)], "PAC": [(-140, 5, 55), (165, 15, 32)], "ARC": [(0, 84, 40), (-150, 78, 30), (120, 80, 30)],
           "SOU": [(0, -66, 60), (120, -64, 60), (-120, -66, 60)], "IND": [(76, -12, 45), (62, 14, 15), (88, 12, 12)]}
PAC_HL = ()   # highlight boxes on the Maris Pacifici map (fractions), set after viewing
CARY_HL = ()

def base_map2(c, cam, t, india_a=200, border_a=1.0, glows=(), ocs=()):
    """ocean background, soft ocean glows + named-ocean highlights (under the land), then the land with India filled"""
    c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"]))
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    for key, col, a in ocs:
        if a <= 0: continue
        pul = 0.8 + 0.2 * math.sin(t * 5)
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
        c.drawPath(OC_PATH[key], paint(col, int(a * 0.5 * pul), blur=max(6, 18 / s)))
        c.clipPath(OC_PATH[key], doAntiAlias=True)
        for lo, la, R in OC_GLOW[key]:
            gx, gy = cam_xy(lo, la)
            sh = skia.GradientShader.MakeRadial(skia.Point(gx, gy), R, [hexc(col, int(min(255, a * 0.85 * pul))), hexc(col, int(a * 0.4)), hexc(col, 0)], [0.0, 0.55, 1.0])
            gp = skia.Paint(); gp.setShader(sh); c.drawCircle(gx, gy, R, gp)
        c.restore()
    for col, a in glows:
        if a <= 0: continue
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
        c.clipPath(IO_PATH, doAntiAlias=True)
        ox, oy = cam_xy(76, -12); pul = 0.85 + 0.15 * math.sin(t * 3)
        sh = skia.GradientShader.MakeRadial(skia.Point(ox, oy), 75, [hexc(col, int(a * 0.42 * pul)), hexc(col, int(a * 0.16)), hexc(col, 0)], [0.0, 0.6, 1.0])
        gp = skia.Paint(); gp.setShader(sh); c.drawPaint(gp)
        c.drawPath(IO_PATH, paint(col, int(a * 0.5), stroke=10 / s, blur=12 / s))
        c.restore()
    c.save(); c.translate(0, MAP_CY - DH / 2)
    draw_map(c, WM, cam, fills={"IND": (COL["NOW"], int(india_a))}, border_a=border_a)
    c.restore()

def region_hl(c, cam, key, k, t, col):
    """glowing highlight of a land region (e.g. Europe) drawn over the map"""
    if k <= 0: return
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]; pul = 0.8 + 0.2 * math.sin(t * 5)
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
    c.drawPath(OC_PATH[key], paint(col, int(110 * k * pul)))
    c.drawPath(OC_PATH[key], paint(col, int(200 * k), stroke=6 / s, blur=4 / s))
    c.drawPath(OC_PATH[key], paint("#FFFFFF", int(230 * k), stroke=1.4 / s))
    c.restore()

def card(c, img, k, t, cx, cy, w, cap, sub, credit, ang=0, hls=()):
    """real document/photo in the gold frame (halo, motes, slow push-in); caption text auto-fits the card width"""
    if k <= 0 or img is None: return
    al = int(255 * clamp(k * 2)); kk = back(clamp(k), 1.4)
    h = w * img.height() / img.width()
    halo = skia.GradientShader.MakeRadial(skia.Point(cx, cy), w * 0.9, [skia.ColorSetARGB(int(140 * clamp(k)), 255, 190, 90), skia.ColorSetARGB(0, 255, 160, 60)])
    hp = skia.Paint(); hp.setShader(halo); c.drawCircle(cx, cy, w * 0.9, hp)
    for i in range(8):
        a_ = i * 2.4 + t * 0.6; r_ = w * (0.55 + 0.08 * math.sin(i * 1.7 + t))
        c.drawCircle(cx + math.cos(a_) * r_, cy + math.sin(a_) * r_ * 0.8, 3 + (i % 3), paint("#FFE2A8", int(150 * clamp(k) * (0.5 + 0.5 * math.sin(t * 3 + i))), blur=2))
    c.save(); c.translate(cx, cy); c.rotate(ang * kk); c.scale(kk, kk); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    rrect(c, l - 16, tp - 16, l + w + 16, tp + h + 92, 16, "#FBF3DF", al, shadow=30)
    c.drawRoundRect(skia.Rect(l - 9, tp - 9, l + w + 9, tp + h + 85), 11, 11, paint("#C9A24A", al, stroke=3))
    c.save(); c.clipRect(skia.Rect(l, tp, l + w, tp + h))
    z = 1.0 + 0.05 * clamp((t % 8) / 4)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al); c.restore()
    c.drawRect(skia.Rect(l, tp, l + w, tp + h), paint("#B8862B", al, stroke=3))
    for fx0, fy0, fx1, fy1, hk in hls:
        if hk <= 0: continue
        x0, y0, x1, y1 = l + fx0 * w, tp + fy0 * h, l + fx1 * w, tp + fy1 * h
        c.drawRoundRect(skia.Rect(x0 - 6, y0 - 5, x0 - 6 + (x1 - x0 + 12) * ease_out(hk), y1 + 5), 9, 9, paint("#FF4D5E", al, stroke=4))
    fit = lambda s_, size: min(size, size * (w + 10) / max(1, text_w(s_, size, FT_BLACK)))
    text(c, cap, cx, tp + h + 44, fit(cap, 34), "#7A1E0E", FT_BLACK, "c", al)
    text(c, sub, cx, tp + h + 76, fit(sub, 23), "#B5651D", FT_BLACK, "c", al)
    c.restore()
    text(c, credit, cx, tp + h + 122, min(17, 17 * (w + 160) / max(1, text_w(credit, 17, FT_SEMI))), "#DCE3EC", FT_SEMI, "c", int(al * 0.9), shadow=True)

def note(c, s_, k, y0=1086):
    """small dark pill with a yellow dot (e.g. 'raasta andaazan')"""
    if k <= 0: return
    size = 22; w = text_w(s_, size, FT_SEMI); al = int(255 * clamp(k * 2))
    x0 = DW / 2 - (w + 50) / 2
    rrect(c, x0, y0, x0 + w + 50, y0 + 38, 19, "#0F1B2D", int(al * 0.85)); c.drawCircle(x0 + 20, y0 + 19, 6, paint(Y, al))
    text(c, s_, x0 + 36, y0 + 27, size, "#DCE3EC", FT_SEMI, "l", al)

def strike_chip(c, s_, x, y, k, sk, size=44):
    """chip with a red line drawn across it (sk 0..1)"""
    chip(c, s_, x, y, k, bg="#22304A", size=size)
    if sk > 0 and k > 0:
        w = text_w(s_, size) + 40
        c.drawLine(x - w / 2, y + 6, x - w / 2 + w * ease_out(sk), y - 18, paint("#FF4D5E", int(255 * clamp(k)), stroke=9, cap_round=True))

def gem(c, x, y, r, a, col="#FFE08A"):
    if a <= 0: return
    p_ = skia.Path(); p_.moveTo(x, y - r); p_.lineTo(x + r * 0.32, y - r * 0.32); p_.lineTo(x + r, y); p_.lineTo(x + r * 0.32, y + r * 0.32)
    p_.lineTo(x, y + r); p_.lineTo(x - r * 0.32, y + r * 0.32); p_.lineTo(x - r, y); p_.lineTo(x - r * 0.32, y - r * 0.32); p_.close()
    c.drawCircle(x, y, r * 0.9, paint(col, int(a * 0.35), blur=r * 0.5)); c.drawPath(p_, paint("#FFFFFF", int(a)))

GEMS = [(62, 8), (66, 18), (70, 2), (84, 4), (88, 12), (91, 6), (73, -6), (80, -10), (60, -2), (95, -4), (68, -14), (86, -16), (76, 0), (57, 14)]

def doc_card(c, img, k, t, cx, cy, w, cap, sub, credit, hls=()):
    """real document/map in the gold manuscript frame (straight), with yellow highlighter boxes on parts of the image.
    hls: (fx0, fy0, fx1, fy1, k) as fractions of the image"""
    if k <= 0 or img is None: return
    manuscript_card(c, img, k, t, cx, cy, w, 0, cap, sub, credit)
    kk = back(clamp(k), 1.4); h = w * img.height() / img.width(); al = clamp(k * 2)
    l, tp = cx - w / 2, cy - h / 2
    c.save(); c.translate(cx, cy); c.scale(kk, kk); c.translate(-cx, -cy)
    for fx0, fy0, fx1, fy1, hk in hls:
        if hk <= 0: continue
        x0, y0, x1, y1 = l + fx0 * w, tp + fy0 * h, l + fx1 * w, tp + fy1 * h
        hp = paint("#FFD166", int(200 * al)); hp.setBlendMode(skia.BlendMode.kMultiply)
        c.drawRect(skia.Rect(x0, y0, x0 + (x1 - x0) * ease_out(hk), y1), hp)
        c.drawRoundRect(skia.Rect(x0 - 8, y0 - 6, x0 - 8 + (x1 - x0 + 16) * ease_out(hk), y1 + 6), 10, 10, paint("#FF4D5E", int(230 * al), stroke=4))
    c.restore()

def typed_card(c, lines, k_type, a, y0):
    """dark card where lines type in (k_type 0..1 over all characters); lines: (text, size, col)"""
    if a <= 0: return
    tot = sum(len(s_) for s_, _, _ in lines); n = int(round(tot * clamp(k_type)))
    hgt = sum(sz * 1.25 for _, sz, _ in lines) + 50
    wmax = max(text_w(s_, sz) for s_, sz, _ in lines) + 80
    rrect(c, DW / 2 - wmax / 2, y0, DW / 2 + wmax / 2, y0 + hgt, 24, "#0B1424", int(a * 0.85), shadow=20)
    c.drawRoundRect(skia.Rect(DW / 2 - wmax / 2, y0, DW / 2 + wmax / 2, y0 + hgt), 24, 24, paint(Y, int(a * 0.8), stroke=3))
    yy = y0 + 25
    for s_, sz, col in lines:
        yy += sz * 1.1
        m = max(0, min(len(s_), n)); n -= len(s_)
        if m > 0: text(c, s_[:m], DW / 2 - text_w(s_, sz) / 2, yy, sz, col, FT_BLACK, "l", int(a), shadow=True)
        if 0 < m < len(s_) and int(t_now() * 4) % 2 == 0:
            xx = DW / 2 - text_w(s_, sz) / 2 + text_w(s_[:m], sz) + 4
            c.drawRect(skia.Rect(xx, yy - sz * 0.75, xx + 5, yy + 4), paint(Y, int(a)))
        yy += sz * 0.15
_TNOW = [0.0]
def t_now(): return _TNOW[0]

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

# ---------------------------------------------------------------- camera keys (lon, lat, px/deg)
WORLD = (10, 12, 2.75); IO = (80, -6, 8.5); SAN = (78, 8, 11); GRK = (56, 17, 12.5); CHN = (90, 14, 7.2)
EUR = (60, 22, 3.6); LAT = (78, -2, 7.5); WHY = (80, 13, 15)
CAM_KEYS = [(0.0, (10, 12, 2.3)), (2.0, WORLD), (kw(2, "Indian") - 0.1, WORLD), (kw(2, "Indian") + 1.2, IO),
            (T("others")[0], IO), (T("others")[0] + 1.0, WORLD), (T("never")[0] + 0.3, WORLD), (T("never")[0] + 1.4, IO),
            (T("sanskrit")[0], IO), (T("sanskrit")[0] + 1.0, SAN), (T("greek")[0], SAN), (T("greek")[0] + 1.1, GRK),
            (T("china")[0], GRK), (T("china")[0] + 1.2, CHN), (T("europe")[0], CHN), (T("europe")[0] + 1.0, EUR),
            (T("latin")[0], EUR), (T("latin")[0] + 1.1, LAT), (T("why")[0], LAT), (T("why")[0] + 1.1, WHY),
            (T("hindi")[0], WHY), (T("hindi")[0] + 1.0, IO)]
def cam_at(t):
    for (t0, a), (t1, b) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_io(seg(t, t0, t1))
            s = math.exp(lerp(math.log(a[2]), math.log(b[2]), k))
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k), s)
    return CAM_KEYS[-1][1] if t > CAM_KEYS[-1][0] else CAM_KEYS[0][1]

PL = dict(io=(74, -20), atl=(-32, 18), pac=(-136, 2), arc=(2, 79), sou=(62, -63), ind=(79, 22.5), arabsea=(64, 14), bob=(88.5, 14),
          kanya=(77.5, 8.1), io_lbl=(78, -4), area=(76, -30),
          berenice=(35.5, 23.9), aden=(45, 12.6), muziris=(76.2, 10.2), barygaza=(72.9, 21.7), egypt=(31, 27),
          suzhou=(120.6, 31.3), champa=(109.2, 13.8), malacca=(102.25, 2.2), calicut=(75.8, 11.25), hormuz=(56.3, 26.6),
          europe=(10, 49))

# ---------------------------------------------------------------- timeline
TL = [(-400, "PRACHIN"), (60, "1st SADI"), (1410, "1405-33"), (1515, "1515"), (2026, "AAJ")]
def timeline(c, year, k):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); x0, x1, y = 110, 970, 1220
    def X(yr):
        pts = [(-600, 110), (0, 280), (1300, 420), (1450, 560), (1550, 700), (2026, 970)]
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= yr <= b: return lerp(xa, xb, (yr - a) / (b - a))
        return x0 if yr < -600 else x1
    c.drawRoundRect(skia.Rect(x0, y - 4, x1, y + 4), 4, 4, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 4, X(year), y + 4), 4, 4, paint(Y, al))
    for yr, lab in TL:
        on = abs(yr - year) < 30
        c.drawCircle(X(yr), y, 12 if on else 8, paint(Y if X(yr) <= X(year) + 1 else "#3E5068", al))
        text(c, lab, X(yr), y + 52, 28 if on else 22, "#F1FAEE" if on else PAL["muted"], FT_BLACK if on else FT_SEMI, "c", al)
    lab = "PRACHIN KAAL" if year < -300 else ("c. 1st SADI CE" if year < 300 else f"{int(year)}")
    pill(c, lab, X(year), y - 50, 34, Y, fg="#0F1B2D", a=al)

def year_at(t):
    n0, g0, c0, e0, l0, w0 = T("never")[0], T("greek")[0], T("china")[0], T("europe")[0], T("latin")[0], T("why")[0]
    keys = [(0, 2026), (n0 + 0.3, 2026), (n0 + 1.5, -400), (g0, -400), (g0 + 1.0, 60), (c0, 60), (c0 + 1.0, 1410), (e0, 1410),
            (e0 + 0.8, 1480), (l0, 1480), (l0 + 0.8, 1515), (w0, 1515), (w0 + 1.0, 2026)]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp(a, b, ease_io(seg(t, t0, t1)))
    return 2026

def pop_words(c, t, s_, t0, y, size, col, a_):
    ws = s_.split(" "); tw = sum(text_w(w_, size) for w_ in ws) + text_w(" ", size) * (len(ws) - 1); x = DW / 2 - tw / 2
    for i, w_ in enumerate(ws):
        p = seg(t, t0 + i * 0.11, t0 + i * 0.11 + 0.35); ww = text_w(w_, size)
        if p > 0:
            e = back(p, 2.0) if p < 1 else 1.0
            c.save(); c.translate(x + ww / 2, y + (1 - e) * 30); c.scale(0.7 + 0.3 * e, 0.7 + 0.3 * e)
            text(c, w_, 0, 0, size, col, FT_BLACK, "c", int(255 * clamp(p * 2) * a_), shadow=True); c.restore()
        x += ww + text_w(" ", size)

def teer(c, cam, k, t, a=255):
    """arrow tracing India from the north down the peninsula into the ocean"""
    if k <= 0: return
    pts = [scr(cam, *q) for q in [(76.5, 31), (78, 24), (78.2, 16), (77.5, 8.4), (77.4, 1.5)]]
    route(c, pts, ease_out(k), col="#FFFFFF", w=16, dash=False, a=int(a * 0.35), head=False)
    route(c, pts, ease_out(k), col=Y, w=8, dash=False, a=a, head=True)

# ---------------------------------------------------------------- frame
WM = None
def frame(c, t):
    global WM
    load(); _TNOW[0] = t
    if WM is None: WM = WorldMap()
    cam = cam_at(t)
    def S(k): return scr(cam, *PL[k])
    def act(k, pad_in=0.0, pad_out=0.0):
        a, b = T(k); return a - pad_in <= t < b + pad_out
    def kin(k, d=0.5, off=0.0): return seg(t, T(k)[0] + off, T(k)[0] + off + d)
    def at(t0, d=0.45): return seg(t, t0, t0 + d)
    def out(k, d=0.3): return 1 - seg(t, T(k)[1] - d, T(k)[1])

    yr = year_at(t)
    cta0 = T("cta")[0]; s0 = T("sanskrit")[0]; g0 = T("greek")[0]; w0 = T("why")[0]
    # map of ITS time (user rule): tiranga India in the present-day scenes, solid bhagwa India in the Sanskrit lead-in,
    # period polities (historical-basemaps) in bhagwa shades in the historical scenes
    hist = seg(t, g0 - 0.3, g0 + 0.5) * (1 - seg(t, w0, w0 + 0.8))
    india_a = (200 + 30 * seg(t, s0, s0 + 0.8)) * (1 - hist)
    gl = []
    gl.append(("#4FC3F7", 255 * seg(t, kw(2, "Ocean") - 0.2, kw(2, "Ocean") + 0.6) * (1 - seg(t, T("others")[0], T("others")[0] + 0.6))))
    gl.append(("#FFD166", 200 * seg(t, kw(10, "Ratnakara") - 0.2, kw(10, "Ratnakara") + 0.6) * (1 - seg(t, g0 - 0.2, g0 + 0.4))))
    gl.append(("#FF4D5E", 190 * seg(t, kw(11, "Laal") - 0.3, kw(11, "Laal") + 0.5) * (1 - seg(t, T("china")[0] - 0.2, T("china")[0] + 0.4))))
    gl.append(("#4FC3F7", 230 * seg(t, kw(14, "Indicus") - 0.2, kw(14, "Indicus") + 0.6) * (1 - seg(t, w0, w0 + 0.5))))
    gl.append(("#4FC3F7", 255 * seg(t, kw(18, "beech") - 0.3, kw(18, "beech") + 0.5) * (1 - seg(t, cta0, cta0 + 0.6))))
    SEA = COL["SEA"]; ti0 = kw(2, "Indian") - 0.12; oe = T("others")
    ocs = []
    for i, key in enumerate(("PAC", "ATL", "IND", "ARC", "SOU")):      # hook: the five oceans light up on "paanch"
        tp_ = kw(0, "paanch") - 0.1 + i * 0.13
        ocs.append((key, SEA, 230 * at(tp_, 0.35) * (1 - seg(t, ti0 - 0.3, ti0))))
    ocs.append(("IND", "#FFD166", 255 * at(ti0, 0.4) * (1 - seg(t, T("size")[1] - 0.3, T("size")[1]))))
    for key, u_, w1 in (("ATL", 5, "Atlantic"), ("PAC", 6, "Pacific"), ("ARC", 7, "Arctic"), ("SOU", 8, "Southern")):
        ocs.append((key, SEA, 255 * at(kw(u_, w1) - 0.15, 0.35) * (1 - 0.45 * seg(t, ue(u_), ue(u_) + 0.3)) * (1 - seg(t, oe[1] - 0.1, oe[1] + 0.3))))
    ocs.append(("IND", "#FF9933", 255 * at(kw(8, "dakshin") + 0.1, 0.35) * (1 - seg(t, T("never")[0] + 0.6, T("never")[0] + 1.0))))
    ocs.append(("IND", COL["CHINA"], 240 * at(kw(12, "Western") - 0.15, 0.35) * (1 - seg(t, T("china")[1] - 0.2, T("china")[1] + 0.2))))
    ocs.append(("IND", COL["EURO"], 240 * at(kw(13, "Eastern") - 0.15, 0.35) * (1 - seg(t, T("europe")[1] - 0.2, T("europe")[1] + 0.2))))
    ocs.append(("IND", "#FF9933", 240 * at(kw(19, "Hind M") - 0.15, 0.35) * (1 - seg(t, T("hindi")[1] - 0.2, T("hindi")[1] + 0.3))))
    base_map2(c, cam, t, india_a, border_a=1 - 0.75 * hist, glows=gl, ocs=ocs)
    now_a = 255 * (1 - seg(t, s0, s0 + 0.8)) + 255 * seg(t, w0, w0 + 0.8)
    if now_a > 0:
        if "NOW" not in EMP_PATH: EMP_PATH["NOW"] = _poly_path(WM.geoms["IND"], 0.01)
        cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
        wave_flag(c, EMP_PATH["NOW"], "NOWV", t, min(255, now_a), s_); c.restore()
    c0_, e0_ = T("china")[0], T("europe")[0]
    ERA_ON = [("CE100", g0 - 0.3, c0_ + 0.3), ("CE1400", c0_, e0_ + 0.3), ("CE1500", e0_, w0 + 0.4)]
    era_now = None
    for ek, ta, tb in ERA_ON:
        ea = seg(t, ta, ta + 0.6) * (1 - seg(t, tb - 0.3, tb + 0.3))
        if ea <= 0: continue
        if ea > 0.5: era_now = ek
        cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
        c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_)
        for j, (nm, pth) in enumerate(ERA_PATH[ek]):
            c.drawPath(pth, paint(BHAGWA[j % len(BHAGWA)], int(175 * ea)))
            c.drawPath(pth, paint("#FFE7C2", int(150 * ea), stroke=1.0 / s_))
        c.restore()

    # ================= hook: "OCEAN?" letter by letter, 5 oceans pulse, then "INDIAN OCEAN" with tiranga letters
    if t < T("size")[0] + 0.8:
        ho = 1 - seg(t, T("size")[0] + 0.5, T("size")[0] + 0.8)
        ti = kw(2, "Indian") - 0.12
        qd = seg(t, kw(1, "kaunsa") - 0.1, kw(1, "kaunsa") + 0.45)
        an = seg(t, ti, ti + 0.7)
        L = []
        tir = ["#FF9933", "#FF9933", "#FFFFFF", "#FFFFFF", "#3FB950", "#3FB950"]
        for i, ch in enumerate("INDIAN"):
            p = seg(t, ti + i * 0.06, ti + i * 0.06 + 0.5); e = back(p, 1.6) if p < 1 else 1.0
            L.append(dict(ch=ch, w=ease_out(p), al=clamp(p * 1.6), dy=-(1 - e) * 90, col=tir[i], sy=0.55 + 0.45 * e))
        L.append(dict(ch=" ", w=ease_out(an), al=0))
        for i, ch in enumerate("OCEAN"):
            p = seg(t, 0.12 + i * 0.1, 0.72 + i * 0.1); e = back(p, 1.6) if p < 1 else 1.0
            L.append(dict(ch=ch, al=clamp(p * 1.6), dy=(1 - e) * 90, col="#7FDBFF", sy=0.55 + 0.45 * e))
        L.append(dict(ch="?", w=ease_out(qd) * (1 - ease_out(an)), al=qd * (1 - an), dy=-(1 - back(qd, 2.2)) * 120 if qd < 1 else 0,
                      col=Y, rot=(1 - qd) * -25))
        word_row(c, L, DW / 2, 300, lerp(170, 112, ease_io(an)), 255 * ease_io(seg(t, 0.05, 0.6)) * ho, glow=Y if t < ti else "#FF9933")
        sh = seg(t, 0.95, 1.6)
        if 0 < sh < 1:
            bw = text_w("OCEAN", 170); x0 = DW / 2 - bw / 2 - 60 + (bw + 120) * ease_io(sh)
            g_ = skia.GradientShader.MakeLinear([skia.Point(x0 - 60, 0), skia.Point(x0 + 60, 0)],
                                                [skia.ColorSetARGB(0, 255, 255, 255), skia.ColorSetARGB(int(150 * ho), 255, 255, 255), skia.ColorSetARGB(0, 255, 255, 255)])
            pp = skia.Paint(); pp.setShader(g_); pp.setBlendMode(skia.BlendMode.kPlus)
            c.save(); c.skew(-0.25, 0); c.translate(75, 0); c.drawRect(skia.Rect(x0 - 60, 150, x0 + 60, 340), pp); c.restore()
        q1 = 1 - seg(t, ti - 0.3, ti)
        if q1 > 0: pop_words(c, t, "5 MAHASAGAR. SIRF 1 PE DESH KA NAAM!", kw(0, "sirf") - 0.2, 408, 44, "#F1FAEE", q1 * ho)
        if t > ti:
            pop_words(c, t, "INDIA KE NAAM PE!", ti + 0.3, 408, 60, "#FF9933", ho)
            rk = seg(t, ti + 0.3, ti + 1.2)
            if rk > 0:
                pw = skia.Path(); x0, x1 = DW / 2 - 240, DW / 2 - 240 + 480 * ease_out(rk)
                for xx in range(int(x0), int(x1), 6):
                    yy = 442 + 7 * math.sin((xx - x0) / 34 - t * 8)
                    (pw.moveTo if xx == int(x0) else pw.lineTo)(xx, yy)
                c.drawPath(pw, paint("#7FDBFF", int(230 * ho), stroke=6, cap_round=True))
                c.drawPath(pw, paint("#7FDBFF", int(110 * ho), stroke=16, blur=8, cap_round=True))
    # ================= size
    if act("size"):
        e = out("size")
        headline(c, "TEESRA SABSE BADA", kin("size", 0.5, 0.8), col="#7FDBFF", sub="duniya ke mahasagar mein #3")
        label(c, "INDIAN OCEAN", *S("io_lbl"), at(us(3)) * e, col="#0F1B2D", bg="#7FDBFF", size=38)
        label(c, "~7.06 CRORE KM²", S("area")[0], S("area")[1], at(kw(3, "7") - 0.1) * e, col="#0F1B2D", bg=Y, size=44)
        label(c, "DHARTI KA ~20% PAANI", S("area")[0], S("area")[1] + 90, at(kw(3, "kilometre") - 0.1) * e, size=32)
    # ================= others: every other ocean's name, on its word
    if act("others", 0, 0.3):
        e = 1 - seg(t, T("others")[1] - 0.1, T("others")[1] + 0.3)
        headline(c, "BAAKI NAAM KAHAN SE?", kin("others"), col=Y)
        OC = [("atl", 5, "Atlantic", "ATLANTIC", "Atlas", "ATLAS: GREEK DEVTA"), ("pac", 6, "Pacific", "PACIFIC", "shaant", "SHAANT SAMUDRA"),
              ("arc", 7, "Arctic", "ARCTIC", "Bhaalu", "BHAALU TAARE"), ("sou", 8, "Southern", "SOUTHERN", "dakshin", "DAKSHIN")]
        for key, u_, w1, nm, w2, mean in OC:
            x, y = S(key); k1 = at(kw(u_, w1) - 0.15, 0.4) * e
            label(c, nm, x, y - 30, k1, col="#0F1B2D", bg="#7FDBFF", size=30)
            label(c, mean, x, y + 30, at(kw(u_, w2) - 0.15, 0.4) * e, col="#0F1B2D", bg=Y, size=26)
        def win(t0, t1): return at(t0, 0.35) * (1 - seg(t, t1 - 0.2, t1))
        card(c, DOCS.get("atlas"), win(kw(5, "Atlas") - 0.2, kw(6, "Pacific") - 0.05), t, 790, 640, 340,
             "ATLAS - GREEK DEVTA", "Farnese Atlas murti, 2nd sadi CE (Naples)", "Photo: Gabriel Seah, CC BY-SA 3.0 (cropped)")
        card(c, DOCS.get("pacifici"), win(kw(6, "Pacific") + 0.2, kw(7, "Arctic") - 0.05), t, 740, 640, 560,
             "MARIS PACIFICI = SHAANT SAMUDRA", "Abraham Ortelius ka naksha, 1589", "Abraham Ortelius, 1589 - public domain (Wikimedia Commons)", hls=[(0.61, 0.03, 0.855, 0.08, seg(t, kw(6, "Pacific") + 0.45, kw(6, "Pacific") + 0.85)), (0.21, 0.31, 0.62, 0.375, seg(t, kw(6, "shaant") - 0.1, kw(6, "shaant") + 0.4))])
        card(c, DOCS.get("ursa"), win(kw(7, "Bhaalu") - 0.25, kw(8, "Southern") - 0.05), t, 540, 990, 520,
             "URSA MAJOR = BADA BHAALU", "Taara-card, Urania's Mirror, c. 1825", "Sidney Hall, Urania's Mirror (LoC; restoration A. Cuerden) - public domain")
        card(c, DOCS.get("cary"), win(kw(8, "Southern") + 0.1, T("never")[0] + 0.3), t, 540, 520, 560,
             "'SOUTHERN OCEAN' = DAKSHIN KA SAMUDRA", "John Cary ka naksha, 1806", "John Cary, 1806 (Geographicus) - public domain", hls=[(0.09, 0.81, 0.91, 0.94, seg(t, kw(8, "Southern") + 0.35, kw(8, "Southern") + 0.85))])
    ti_ = kw(8, "dakshin") + 0.1                      # INDIAN = the only country name; stays into the next scene
    if ti_ <= t < T("never")[0] + 1.0:
        e2 = 1 - seg(t, T("never")[0] + 0.6, T("never")[0] + 1.0)
        x, y = S("io")
        label(c, "INDIAN", x, y - 70, at(ti_, 0.4) * e2, col="#0F1B2D", bg="#FF9933", size=32)
        label(c, "= DESH: INDIA", x + (190 if cam[2] < 4 else 0), y + (0 if cam[2] < 4 else 64), at(ti_ + 0.15, 0.4) * e2, col="#0F1B2D", bg=Y, size=28)
    # ================= never
    if act("never"):
        headline(c, "HAMESHA NAHI THA!", kin("never"), col="#FF6B75", sub="naam badalte rahe")
        strike_chip(c, "INDIAN OCEAN", DW / 2, 405, at(us(9) + 0.1, 0.4) * out("never"), seg(t, kw(9, "nahi") - 0.1, kw(9, "nahi") + 0.4))
    # ================= sanskrit
    if act("sanskrit"):
        e = out("sanskrit"); tr_ = kw(10, "Ratnakara")
        chip(c, "SANSKRIT NAAM", DW / 2, 230, kin("sanskrit") * (1 - at(tr_ - 0.3, 0.3)), bg="#C46A12", size=48)
        headline(c, "RATNAKARA", at(tr_ - 0.2, 1.2) * e, col="#FFD166", size=124, sub="ratnon ki khaan")
        card(c, DOCS.get("ramayana"), at(kw(10, "Sanskrit") - 0.1, 0.4) * (1 - seg(t, T("greek")[0] + 0.3, T("greek")[0] + 0.7)), t, 540, 760, 640,
             "SANSKRIT GRANTH: RAMAYANA", "Mewar pandulipi, 1649-53 - samudra ke paar Lanka", "Sahibdin, Mewar Ramayana, British Library Add MS 15297(1) - public domain")
        ga = at(kw(10, "ratnon") - 0.4, 0.5) * e
        for i, (lo, la) in enumerate(GEMS):
            x, y = S("io") if False else scr(cam, lo, la)
            tw_ = 0.5 + 0.5 * math.sin(t * 5 + i * 1.9)
            gem(c, x, y, 12 + 8 * tw_, 255 * ga * (0.4 + 0.6 * tw_))
    # ================= greek: Periplus, Erythraean Sea
    if act("greek"):
        e = out("greek"); te_ = kw(11, "Erythraean"); tp_ = kw(11, "Periplus")
        if t < te_ - 0.2: headline(c, "GREEK VYAPARI", kin("greek", 0.5, 0.1), col="#6FA8FF", sub="lagbhag 2000 saal pehle")
        else: headline(c, "ERYTHRAEAN SEA", at(te_ - 0.2, 1.0) * e, col=COL["RED"], sub="yaani Laal Samudra")
        rk_ = at(kw(11, "vyapariyon") - 0.3, 1.2)
        p0, p1, p2, p3 = S("berenice"), S("aden"), S("muziris"), S("barygaza")
        route(c, [p0, p1, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 40), p2], ease_out(rk_), col=Y, w=5, a=int(255 * e))
        route(c, [p1, ((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2 + 20), p3], ease_out(seg(rk_, 0.4, 1)), col=Y, w=4, a=int(255 * e))
        dk = at(tp_ - 0.15, 0.5) * e
        label(c, "EGYPT", S("egypt")[0], S("egypt")[1] - 20, at(kw(11, "vyapariyon") - 0.2) * e * (1 - dk), size=28)
        label(c, "MUZIRIS (KERALA)", p2[0] + 30, p2[1] + 60, at(kw(11, "vyapariyon") + 0.6) * e * (1 - dk), size=26)
        dk = at(tp_ - 0.15, 0.5) * e
        doc_card(c, DOCS.get("periplus"), dk, t, 540, 770, 720, "PERIPLUS PAR BANA NAKSHA", "Abraham Ortelius, 1597",
                 "Abraham Ortelius, 1597 - public domain (Wikimedia Commons)",
                 hls=[(0.33, 0.465, 0.76, 0.535, seg(t, te_ - 0.05, te_ + 0.45)), (0.36, 0.545, 0.77, 0.605, seg(t, te_ + 0.35, te_ + 0.85))])
        chip(c, "ERYTHRA (GREEK) = LAAL", DW / 2, 405, at(kw(11, "Laal") - 0.15, 0.4) * e, bg=COL["RED"], fg="#0F1B2D", size=34)
    # ================= china: Zheng He, Western Ocean
    if act("china", 0, 0.2):
        e = 1 - seg(t, T("china")[1] - 0.1, T("china")[1] + 0.2)
        headline(c, "ZHENG HE, 1405-1433", kin("china", 0.5, 0.2), col=COL["CHINA"], sub="China ke admiral ki yatraen")
        pts = [S(k_) for k_ in ("suzhou", "champa", "malacca", "calicut", "hormuz")]
        route(c, pts, ease_out(seg(t, kw(12, "China") - 0.2, kw(12, "Western") - 0.1)), col=COL["CHINA"], w=5, a=int(255 * e))
        spot = at(kw(12, "China") - 0.15, 0.4) * e
        ring_highlight(c, *S("suzhou"), 34, spot, t, col=COL["CHINA"])
        label(c, "MING CHINA", S("suzhou")[0] - 40, S("suzhou")[1] - 62, spot, size=28)
        label(c, "CALICUT", S("calicut")[0] - 120, S("calicut")[1] - 10, at(kw(12, "Zheng") + 0.3) * e, size=26)
        tw_ = kw(12, "Western")
        a0, a1 = scr(cam, 98, 1), scr(cam, 60, 1)
        route(c, [a0, ((a0[0] + a1[0]) / 2, a0[1] - 30), a1], ease_out(at(tw_ - 0.15, 0.6)), col=Y, w=12, dash=False, a=int(255 * e))
        label(c, "WESTERN OCEAN", (a0[0] + a1[0]) / 2, a0[1] + 62, at(tw_ - 0.05) * e, col="#0F1B2D", bg=Y, size=36)
        label(c, "= PASCHIM KA SAMUDRA", (a0[0] + a1[0]) / 2, a0[1] + 125, at(kw(12, "paschim") - 0.1) * e, size=30)
        note(c, "Raasta andaazan - Zheng He ka asli portrait maujood nahi", at(kw(12, "China")) * e, y0=345)
        r0z = kw(12, "China") - 0.1
        if r0z <= t: ruler(c, "zhenghe", at(r0z, 0.4) * e, seg(t, kw(12, "Western") - 0.75, kw(12, "Western") - 0.3), COL["CHINA"], t, bxy=(150, 560))
    # ================= europe: Eastern Ocean (opposite name)
    if act("europe"):
        e = out("europe"); tE = kw(13, "Eastern")
        headline(c, "EK SAMUDRA, ULTE NAAM", kin("europe", 0.5, 0.1), col=Y)
        c0, c1 = scr(cam, 118, 28), scr(cam, 88, -10)
        route(c, [c0, ((c0[0] + c1[0]) / 2 + 40, (c0[1] + c1[1]) / 2), c1], 1.0, col=COL["CHINA"], w=8, dash=False, a=int(255 * kin("europe") * e))
        label(c, "CHINA: WESTERN", c0[0] - 60, c0[1] - 60, kin("europe") * e, col="#0F1B2D", bg=COL["CHINA"], size=28)
        e0, e1 = scr(cam, 8, 47), scr(cam, 62, -10)
        route(c, [e0, ((e0[0] + e1[0]) / 2 - 60, (e0[1] + e1[1]) / 2), e1], ease_out(at(kw(13, "Europe") - 0.1, 0.8)), col=COL["EURO"], w=8, dash=False, a=int(255 * e))
        region_hl(c, cam, "EUROPE", at(kw(13, "Europe") - 0.15, 0.4) * e, t, COL["EURO"])
        label(c, "EUROPE", e0[0] + 10, e0[1] - 55, at(kw(13, "Europe") - 0.15) * e, size=30)
        label(c, "EUROPE: EASTERN", e1[0] - 80, e1[1] + 70, at(tE - 0.1) * e, col="#0F1B2D", bg=COL["EURO"], size=30)
        label(c, "= POORAB KA SAMUDRA", e1[0] - 80, e1[1] + 135, at(kw(13, "poorab") - 0.1) * e, size=26)
    # ================= latin 1515
    if act("latin"):
        e = out("latin")
        headline(c, "1515: LATIN NAAM", kin("latin", 0.5, 0.2), col=Y)
        tk = seg(t, kw(14, "Oceanus") - 0.15, kw(14, "Indicus") + 0.35)
        typed_card(c, [("OCEANUS ORIENTALIS", 58, "#F1FAEE"), ("INDICUS", 92, Y)], tk, 255 * at(kw(14, "Oceanus") - 0.3, 0.3) * e, 360)
        chip(c, "INDICUS = INDIA KA", DW / 2 - 200, 640, at(kw(15, "India") - 0.15, 0.4) * e, bg=Y, fg="#0F1B2D", size=32)
        chip(c, "ORIENTALIS = POORBI", DW / 2 + 210, 640, at(kw(15, "poorbi") - 0.15, 0.4) * e, bg="#22304A", size=32)
        label(c, "OCEANUS INDICUS", S("io_lbl")[0], S("io_lbl")[1] + 40, at(kw(14, "Indicus")) * e, col="#0F1B2D", bg="#7FDBFF", size=34)
    # ================= why India
    if act("why"):
        e = out("why")
        headline(c, "KYUN INDIA?", kin("why"), col="#FF9933", sub="naksha dekho")
        teer(c, cam, at(kw(18, "teer") - 0.3, 1.0), t, int(255 * e))
        ka = at(kw(18, "samudra") - 0.2, 0.4) * e
        ring_highlight(c, *S("arabsea"), 60, ka, t, col="#7FDBFF")
        ring_highlight(c, *S("bob"), 60, ka, t + 0.4, col="#7FDBFF")
        label(c, "ARABIAN SEA", S("arabsea")[0] - 30, S("arabsea")[1] + 100, ka, col="#7FDBFF", size=28)
        label(c, "BAY OF BENGAL", S("bob")[0] + 10, S("bob")[1] + 100, ka, col="#7FDBFF", size=28)
        chip(c, "PRAYADWEEP: 3 TARAF SAMUDRA", DW / 2, 1110, at(kw(18, "beech") - 0.1, 0.4) * e, bg=Y, fg="#0F1B2D", size=30)
    # ================= hindi name
    if act("hindi"):
        e = out("hindi"); th = kw(19, "Hind M")
        if t < th - 0.2: headline(c, "AAJ HINDI MEIN", kin("hindi"), col="#F1FAEE")
        else: headline(c, "HIND MAHASAGAR", at(th - 0.2, 0.9) * e, col="#FF9933", size=112, sub="hamara apna naam")
        label(c, "HIND MAHASAGAR", S("io_lbl")[0], S("io_lbl")[1] + 30, at(th) * e, col="#0F1B2D", bg="#FF9933", size=40)
    # ================= CTA
    if act("cta", 0, 1):
        k = kin("cta", 0.6)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(205 * k)))
        if t < us(21) - 0.1:
            headline(c, "EK DESH, POORA MAHASAGAR", k, y=230)
            chain = [("RATNAKARA", (540, 400), "#C46A12"), ("ERYTHRAEAN SEA", (540, 510), "#B8323A"), ("WESTERN / EASTERN OCEAN", (540, 620), "#22304A"),
                     ("OCEANUS INDICUS", (540, 730), "#1E4F7A"), ("INDIAN OCEAN", (540, 870), Y)]
            for j, (s_, (x, y), bg) in enumerate(chain):
                kk = at(us(20) + 0.1 + j * 0.32, 0.35)
                if j and kk > 0:
                    (xa, ya) = chain[j - 1][1]
                    route(c, [(xa, ya + 22), (x, y - 40)], ease_out(kk), col=Y, w=4, dash=False)
                chip(c, s_, x, y, kk, bg=bg, fg="#0F1B2D" if j == 4 else "#F1FAEE", size=52 if j == 4 else 32)
        else:
            headline(c, "AAPKO KAUNSA PASAND?", at(us(21) - 0.1, 0.4), y=230)
            poll2(c, [("RATNAKARA", "#C46A12", kw(22, "Ratnakara") - 0.15), ("HIND MAHASAGAR", "#FF9933", kw(22, "Hind") - 0.15),
                      ("INDIAN OCEAN", "#2F6FB5", kw(22, "Indian") - 0.15)], t)
            label(c, "COMMENT KARO", DW / 2, 1040, at(kw(23, "Comment") - 0.1, 0.5), col="#FFFFFF", bg=PAL["axis"], size=44)
            subscribe_btn(c, at(kw(23, "subscribe") - 0.4, 0.5), t, kw(23, "subscribe"))

    if era_now and t < w0:
        s_ = ERA_LABEL[era_now] + " (andaazan)"; w_ = text_w(s_, 22, FT_SEMI)
        x0_ = DW / 2 - (w_ + 50) / 2
        rrect(c, x0_, 1432, x0_ + w_ + 50, 1470, 19, "#3A2410", 215); c.drawCircle(x0_ + 20, 1451, 7, paint("#FF9933"))
        text(c, s_, x0_ + 36, 1459, 22, "#FFE7C2", FT_SEMI, "l", 255)
    doc_up = (act("greek") and t > kw(11, "Periplus") - 0.3) or act("others", 0, 0.3) or act("sanskrit") or (act("greek") and t < T("greek")[0] + 0.7)
    if 0.6 < t < cta0 and not doc_up:
        timeline(c, yr, seg(t, 0.6, 1.2))
    for a, b, cap in CAPS:
        if a - 0.05 <= t < b + 0.12: caption(c, cap, seg(t, a - 0.05, a + 0.08)); break
    if 2.0 < t < cta0:
        if g0 - 0.3 < t < w0 + 0.3:
            text(c, "Approx. historical borders: historical-basemaps (A. Ourednik)", DW / 2, 1505, 19, PAL["muted"], FT_SEMI, "c", 210)
        text(c, "Natural Earth; India boundary as per Survey of India", DW / 2, 1532, 19, PAL["muted"], FT_SEMI, "c", 210)
    draw_img(c, LOGO, DW - 150, 40, DW - 40, 150, 200)
    grain(c, t, 8); vignette(c, 120)

if __name__ == "__main__":
    if sys.argv[1] == "still":
        od = sys.argv[2]; os.makedirs(od, exist_ok=True)
        for ts in sys.argv[3:]:
            render_still(float(ts), f"{od}/s_{float(ts):06.2f}.png"); print("ok", ts)

def sfx_events():
    """(name, time, gain_db) keyed to the same word times as the visuals"""
    ti = kw(2, "Indian") - 0.12
    E = [("whoosh_long", 0.15, -14), ("pop", kw(1, "kaunsa"), -12), ("boom", ti, -13), ("ding", ti + 0.3, -15)]
    for i in range(5): E.append(("pop", kw(0, "paanch") - 0.1 + i * 0.13, -19))
    for k_ in ("size", "others", "never", "sanskrit", "greek", "china", "europe", "latin", "why", "hindi", "cta"):
        E.append(("whoosh_fast", T(k_)[0], -19))
    E += [("pop", kw(3, "7") - 0.1, -14), ("pop", kw(3, "kilometre") - 0.1, -16)]
    for u_, w1, w2 in ((5, "Atlantic", "Atlas"), (6, "Pacific", "shaant"), (7, "Arctic", "Bhaalu"), (8, "Southern", "dakshin")):
        E += [("pop", kw(u_, w1) - 0.1, -15), ("pop", kw(u_, w2) - 0.1, -17)]
    E += [("ding", kw(8, "dakshin") + 0.1, -13), ("riser", T("never")[0], -16), ("glitch", kw(9, "nahi") - 0.1, -14),
          ("ding", kw(10, "Ratnakara") - 0.15, -14), ("pop", kw(10, "ratnon") - 0.3, -16),
          ("drag", kw(11, "vyapariyon") - 0.3, -18), ("pop", kw(11, "Periplus") - 0.15, -13), ("drag", kw(11, "Erythraean") - 0.05, -16),
          ("pop", kw(11, "Laal") - 0.15, -15), ("drag", kw(12, "China") - 0.2, -18), ("pop", kw(12, "China") - 0.15, -16),
          ("whoosh_fast", kw(12, "Western") - 0.15, -16), ("pop", kw(12, "paschim") - 0.1, -17),
          ("whoosh_fast", kw(13, "Europe") - 0.1, -17), ("stamp", kw(13, "Eastern") - 0.1, -14), ("pop", kw(13, "poorab") - 0.1, -17),
          ("riser", T("latin")[0], -17), ("ding", kw(14, "Indicus") - 0.1, -13), ("pop", kw(15, "India") - 0.15, -15),
          ("pop", kw(15, "poorbi") - 0.15, -16), ("drag", kw(18, "teer") - 0.3, -15), ("pop", kw(18, "samudra") - 0.2, -16),
          ("boom", kw(19, "Hind M") - 0.2, -12)]
    for j in range(5): E.append(("pop", us(20) + 0.1 + j * 0.32, -17))
    E += [("pop", us(21) - 0.1, -15), ("pop", kw(22, "Ratnakara") - 0.15, -16), ("pop", kw(22, "Hind") - 0.15, -16),
          ("pop", kw(22, "Indian") - 0.15, -16), ("pop", kw(23, "Comment") - 0.1, -14), ("ding", kw(23, "subscribe") + 0.35, -12)]
    E += [("pop", kw(5, "Atlas") - 0.2, -14), ("pop", kw(6, "Pacific") + 0.2, -14), ("pop", kw(7, "Bhaalu") - 0.25, -14),
          ("pop", kw(8, "Southern") + 0.1, -14), ("pop", kw(10, "Sanskrit") - 0.1, -14), ("whoosh_fast", kw(12, "China") - 0.15, -16),
          ("glitch", kw(13, "Europe") - 0.15, -18)]
    return sorted(E, key=lambda e: e[1])
