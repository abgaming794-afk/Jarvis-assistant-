

# ================================================================ Mumbai-naam: camera, timeline, scene helpers
SA = (78.5, 21.5, 22); MUM = (72.86, 19.0, 170); ISL = (72.826, 18.968, 4000); WIN = (74.0, 20.5, 38)
WIN2 = (70.5, 20.8, 36); EU = (31.0, 36.0, 9.5); MUM2 = (72.9, 19.05, 190); MAH = (76.0, 20.0, 34)
CAM_KEYS = [(0.0, (78, 22, 6)), (1.9, SA), (us(1), SA), (us(2) + 0.6, MUM), (T("islands")[0], MUM),
            (T("islands")[0] + 1.5, ISL), (T("ptolemy")[0], ISL), (T("ptolemy")[0] + 1.2, WIN), (T("portugal")[0], WIN),
            (T("portugal")[0] + 0.9, WIN2), (T("dowry")[0], WIN2), (T("dowry")[0] + 1.4, EU), (T("company")[0], EU),
            (T("company")[0] + 1.3, MUM2), (T("merge")[0], MUM2), (T("merge")[0] + 1.1, ISL), (T("rename")[0], ISL),
            (T("rename")[0] + 1.3, MAH)]
def cam_at(t):
    for (t0, a), (t1, b) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_io(seg(t, t0, t1))
            s = math.exp(lerp(math.log(a[2]), math.log(b[2]), k))
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k), s)
    return CAM_KEYS[-1][1] if t > CAM_KEYS[-1][0] else CAM_KEYS[0][1]

PL = dict(mum=(72.86, 18.98), guj=(71.8, 22.6), lisbon=(-9.14, 38.72), london=(-0.13, 51.5), sea_w=(61.5, 16.0),
          colaba=(72.818, 18.905), mahim=(72.842, 19.041), worli=(72.815, 19.008), parel=(72.840, 19.000),
          bombay=(72.822, 18.953), boats=(72.788, 18.975), vellard=(72.814, 18.984))

TL = [(150, "c.150"), (1534, "1534"), (1661, "1661"), (1845, "1845"), (1995, "1995")]
def timeline(c, year, k):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); x0, x1, y = 110, 970, 1220
    def X(yr):
        pts = [(0, x0), (1400, x0 + 170), (1900, x0 + 720), (2026, x1)]
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= yr <= b: return lerp(xa, xb, (yr - a) / (b - a))
        return x0 if yr < 0 else x1
    c.drawRoundRect(skia.Rect(x0, y - 4, x1, y + 4), 4, 4, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 4, X(year), y + 4), 4, 4, paint(PAL["yel"], al))
    for yr, lab in TL:
        on = abs(yr - year) < 12
        c.drawCircle(X(yr), y, 12 if on else 8, paint(PAL["yel"] if X(yr) <= X(year) + 1 else "#3E5068", al))
        text(c, lab, X(yr), y + 52, 30 if on else 24, "#F1FAEE" if on else PAL["muted"], FT_BLACK if on else FT_SEMI, "c", al)
    lab = f"c. {int(year)} CE" if year < 1000 else (f"{int(year)}" if year < 2025.5 else "AAJ")
    pill(c, lab, X(year), y - 50, 34, PAL["yel"], fg="#0F1B2D", a=al)

def year_at(t):
    i0, p0, d0, c0, m0, r0 = (T(k)[0] for k in ("islands", "portugal", "dowry", "company", "merge", "rename"))
    keys = [(0, 2026), (i0, 2026), (i0 + 1.3, 150), (p0, 150), (p0 + 1.0, 1534), (d0, 1534), (d0 + 0.9, 1661),
            (c0, 1661), (c0 + 0.6, 1668), (m0, 1668), (m0 + 1.2, 1845), (r0, 1845), (r0 + 1.1, 1995), (T("cta")[0], 1995)]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp(a, b, ease_io(seg(t, t0, t1)))
    return 1995

def in_map(c, cam):
    cx_, cy_ = cam_xy(cam[0], cam[1]); s_ = cam[2]
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s_, s_); c.translate(-cx_, -cy_); return s_

def era_layer(c, cam, ek, ea):
    if ea <= 0: return
    s_ = in_map(c, cam)
    for j, (nm, pth) in enumerate(ERA_PATH[ek]):
        c.drawPath(pth, paint(BHAGWA[j % len(BHAGWA)], int(165 * ea)))
        c.drawPath(pth, paint("#FFE7C2", int(140 * ea), stroke=1.0 / s_))
    c.restore()

def draw_islands(c, cam, t, mask_a, rise, hl=None, merge_k=0.0, vel_k=0.0):
    """sea over today's reclaimed island, the seven islands rising one by one, optional highlight + reclamation"""
    if mask_a <= 0: return
    s_ = in_map(c, cam)
    c.drawPath(ISL_MASK, paint(PAL["ocean"], int(255 * mask_a)))
    if merge_k > 0:                                  # reclaimed land fills in between the islands
        c.drawPath(MERGED, paint("#C9A86A", int(235 * ease_out(merge_k) * mask_a)))
        c.drawPath(MERGED, paint("#FFF1C2", int(200 * merge_k * mask_a), stroke=1.6 / s_))
    for i, nm in enumerate(ISL_ORDER):
        k = clamp(rise[i] if isinstance(rise, (list, tuple)) else rise)
        if k <= 0: continue
        e = back(k, 1.6); p = ISL_PATH[nm]; b = p.getBounds()
        c.save(); c.translate(b.centerX(), b.centerY()); c.scale(e, e); c.translate(-b.centerX(), -b.centerY())
        on = hl is not None and hl.get(nm, 0) > 0
        c.drawPath(p, paint("#E8C27A" if not on else "#FFD166", int(255 * clamp(k * 2) * mask_a)))
        c.drawPath(p, paint("#7A5520", int(200 * clamp(k * 2) * mask_a), stroke=1.4 / s_))
        if on:
            hk = hl[nm]; pul = 0.75 + 0.25 * math.sin(t * 6)
            c.drawPath(p, paint("#FFD166", int(170 * hk * pul), stroke=8 / s_, blur=5 / s_))
            c.drawPath(p, paint("#FFF1C2", int(255 * hk), stroke=2.2 / s_))
        c.restore()
    if vel_k > 0:
        (x0, y0), (x1, y1) = cam_xy(*VELLARD[0]), cam_xy(*VELLARD[1])
        c.drawLine(x0, y0, lerp(x0, x1, ease_out(vel_k)), lerp(y0, y1, ease_out(vel_k)), paint("#FFFFFF", int(255 * mask_a), stroke=4 / s_, cap_round=True))
    c.restore()

def temple_icon(c, x, y, s, a=255, col="#FFD166"):
    """small temple (shikhara) icon"""
    if a <= 0: return
    p = skia.Path(); p.moveTo(x - 0.55 * s, y); p.lineTo(x - 0.55 * s, y - 0.35 * s); p.lineTo(x - 0.3 * s, y - 0.35 * s)
    p.quadTo(x - 0.25 * s, y - 0.95 * s, x, y - 1.15 * s); p.quadTo(x + 0.25 * s, y - 0.95 * s, x + 0.3 * s, y - 0.35 * s)
    p.lineTo(x + 0.55 * s, y - 0.35 * s); p.lineTo(x + 0.55 * s, y); p.close()
    c.drawPath(p, paint(col, a)); c.drawPath(p, paint("#5A3E10", a, stroke=max(2, s * 0.05)))
    c.drawRect(skia.Rect(x - 0.12 * s, y - 0.3 * s, x + 0.12 * s, y), paint("#5A3E10", a))
    c.drawLine(x, y - 1.15 * s, x, y - 1.45 * s, paint("#5A3E10", a, stroke=max(2, s * 0.04)))
    fl = skia.Path(); fl.moveTo(x, y - 1.45 * s); fl.lineTo(x + 0.28 * s, y - 1.37 * s); fl.lineTo(x, y - 1.29 * s); fl.close()
    c.drawPath(fl, paint("#FF7A1A", a))

# ---- period symbols (never called real national flags)
def _guj_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#1F6B45")); cc.drawRect(skia.Rect(0, 0, w, h), paint("#E8B84A", 255, stroke=h * 0.12))
    for i in range(3): cc.drawCircle(w * (0.3 + 0.2 * i), h / 2, h * 0.09, paint("#E8B84A"))
def _prt_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#F4F1EA"))
    sw, sh = w * 0.34, h * 0.66; l, tp = w / 2 - sw / 2, h / 2 - sh / 2
    sp = skia.Path(); sp.moveTo(l, tp); sp.lineTo(l + sw, tp); sp.lineTo(l + sw, tp + sh * 0.7); sp.quadTo(l + sw, tp + sh, l + sw / 2, tp + sh)
    sp.quadTo(l, tp + sh, l, tp + sh * 0.7); sp.close(); cc.drawPath(sp, paint("#C8102E"))
    i = sw * 0.16; ip = skia.Path(); ip.moveTo(l + i, tp + i); ip.lineTo(l + sw - i, tp + i); ip.lineTo(l + sw - i, tp + sh * 0.68)
    ip.quadTo(l + sw - i, tp + sh - i, l + sw / 2, tp + sh - i); ip.quadTo(l + i, tp + sh - i, l + i, tp + sh * 0.68); ip.close(); cc.drawPath(ip, paint("#FFFFFF"))
    for k_ in range(6):
        a_ = k_ / 6 * 2 * math.pi; cc.drawRect(skia.Rect(w / 2 + math.cos(a_) * sw * 0.42 - 4, h / 2 + math.sin(a_) * sh * 0.38 - 4, w / 2 + math.cos(a_) * sw * 0.42 + 4, h / 2 + math.sin(a_) * sh * 0.38 + 4), paint("#FFD166"))
    q = sw * 0.11
    for dx, dy in ((0, -1.4), (-1.3, 0), (0, 0), (1.3, 0), (0, 1.4)):
        cx, cy = w / 2 + dx * q * 1.2, h / 2 + dy * q * 1.2
        cc.drawRect(skia.Rect(cx - q / 2, cy - q / 2, cx + q / 2, cy + q / 2), paint("#1F4FA8"))
def _eng_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#FFFFFF"))
    cc.drawRect(skia.Rect(w * 0.42, 0, w * 0.58, h), paint("#CE1124")); cc.drawRect(skia.Rect(0, h * 0.38, w, h * 0.62), paint("#CE1124"))
def _eic_tex(cc, w, h):
    for i in range(13): cc.drawRect(skia.Rect(0, i * h / 13, w, (i + 1) * h / 13 + 1), paint("#CE1124" if i % 2 == 0 else "#FFFFFF"))
    cw, ch = w * 0.4, h * 7 / 13; cc.drawRect(skia.Rect(0, 0, cw, ch), paint("#FFFFFF"))
    cc.drawRect(skia.Rect(cw * 0.42, 0, cw * 0.58, ch), paint("#CE1124")); cc.drawRect(skia.Rect(0, ch * 0.4, cw, ch * 0.6), paint("#CE1124"))
SYM = {"GUJ": _guj_tex, "PRT": _prt_tex, "ENG": _eng_tex, "EIC": _eic_tex}
def sym_flag(c, key, x, y, w, k, t):
    """small waving period symbol on a pole at (x, y) = top of the pole"""
    if k <= 0: return
    if key not in FTEX: FTEX[key] = _surf_img(600, 400, SYM[key])
    img = FTEX[key]; al = clamp(k); h = w * 2 / 3; kk = back(al)
    c.save(); c.translate(x, y); c.scale(kk, kk)
    c.drawLine(0, -4, 0, h * 1.9, paint("#DCE3EC", int(255 * al), stroke=4, cap_round=True))
    n = 40
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n; dy = math.sin(2 * math.pi * (u0 * 1.3 - t * 0.9)) * h * 0.06 * u0
        c.drawImageRect(img, skia.Rect(u0 * 600, 0, min(600, u1 * 600 + 2), 400), skia.Rect(u0 * w, dy, u1 * w + 1, h + dy), SAMP, paint("#FFFFFF", int(255 * al)))
    c.restore()

def pop_words(c, t, s_, t0, y, size, col, a_, gap=0.11):
    ws = s_.split(" "); tw = sum(text_w(w_, size) for w_ in ws) + text_w(" ", size) * (len(ws) - 1); x = DW / 2 - tw / 2
    for i, w_ in enumerate(ws):
        p = seg(t, t0 + i * gap, t0 + i * gap + 0.35); ww = text_w(w_, size)
        if p > 0 and a_ > 0:
            e = back(p, 2.0) if p < 1 else 1.0
            c.save(); c.translate(x + ww / 2, y + (1 - e) * 30); c.scale(0.7 + 0.3 * e, 0.7 + 0.3 * e)
            text(c, w_, 0, 0, size, col, FT_BLACK, "c", int(255 * clamp(p * 2) * a_), shadow=True); c.restore()
        x += ww + text_w(" ", size)
    return tw

def wiki_card2(c, k, t, y0, hs):
    """browser card: Wikipedia 'Mumbai - Etymology', yellow highlighter on 'with no scientific basis' from time hs"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); dy = (1 - ease_out(k)) * 120
    x0, y0, w, h = 100, y0 + dy, 880, 330
    rrect(c, x0, y0, x0 + w, y0 + h, 18, "#FFFFFF", al, shadow=28)
    rrect(c, x0, y0, x0 + w, y0 + 52, 18, "#E9ECF1", al)
    for i, cc in enumerate(("#FF5F57", "#FEBC2E", "#28C840")): c.drawCircle(x0 + 28 + i * 24, y0 + 26, 7, paint(cc, al))
    rrect(c, x0 + 110, y0 + 10, x0 + w - 20, y0 + 42, 16, "#FFFFFF", al)
    text(c, "en.wikipedia.org/wiki/Mumbai#Etymology", x0 + 130, y0 + 33, 19, "#5B6472", FT_SEMI, "l", al)
    text(c, "Mumbai - Etymology", x0 + 28, y0 + 98, 32, "#0F1B2D", FT_BLACK, "l", al)
    c.drawRect(skia.Rect(x0 + 28, y0 + 112, x0 + w - 28, y0 + 114), paint("#C8CCD1", al))
    lines = [("Some Anglophone authors have suggested this", None), ("came from a supposed phrase bom baim,", None),
             ("\"good little bay\", ", "with no scientific basis.")]
    for i, (ln, hl) in enumerate(lines):
        yy = y0 + 160 + i * 44
        text(c, ln, x0 + 28, yy, 28, "#202122", FT_SEMI, "l", al)
        if hl:
            xs = x0 + 28 + text_w(ln, 28, FT_SEMI); hk = ease_out(seg(t, hs, hs + 0.7))
            hp = paint("#FFD166", int(220 * al / 255)); hp.setBlendMode(skia.BlendMode.kMultiply)
            c.drawRect(skia.Rect(xs - 4, yy - 29, xs + (text_w(hl, 28, FT_SEMI) + 6) * hk, yy + 9), hp)
            text(c, hl, xs, yy, 28, "#202122", FT_BLACK, "l", al)
    text(c, "Source: Wikipedia (Shirodkar 1998; J. P. Machado)", x0 + w - 28, y0 + h - 18, 18, "#5B6472", FT_SEMI, "r", al)

def poll(c, k, t):
    items = [("BOMBAY", "#2F6FB5"), ("MUMBAI", "#FF9933"), ("DONO", "#2FA36B")]
    for i, (s_, col) in enumerate(items):
        kk = ease_out(seg(k, i * 0.18, 0.5 + i * 0.18))
        if kk <= 0: continue
        y = 520 + i * 150; al = int(255 * clamp(kk * 2)); x0 = 160 + (1 - kk) * 200
        rrect(c, x0, y - 55, 920, y + 55, 55, "#18253A", al, shadow=14)
        c.drawCircle(x0 + 58, y, 36, paint(col, al)); text(c, "ABC"[i], x0 + 58, y + 14, 40, "#FFFFFF", FT_BLACK, "c", al)
        text(c, s_, x0 + 120, y + 20, 56, "#F1FAEE", FT_BLACK, "l", al)

def era_chip(c, s_):
    w_ = text_w(s_, 22, FT_SEMI); x0_ = DW / 2 - (w_ + 50) / 2
    rrect(c, x0_, 1432, x0_ + w_ + 50, 1470, 19, "#3A2410", 215); c.drawCircle(x0_ + 20, 1451, 7, paint("#FF9933"))
    text(c, s_, x0_ + 36, 1459, 22, "#FFE7C2", FT_SEMI, "l", 255)

def sign_board(c, k, flip_k, t):
    """green road-sign that flips from BOMBAY to MUMBAI"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); kk = back(clamp(k)); cx, cy = DW / 2, 520
    sy = abs(math.cos(math.pi * clamp(flip_k)))
    word = "BOMBAY" if flip_k < 0.5 else "MUMBAI"
    c.save(); c.translate(cx, cy); c.scale(kk, kk * max(0.03, sy))
    rrect(c, -330, -110, 330, 110, 22, "#0E6B3A", al, shadow=24)
    c.drawRoundRect(skia.Rect(-314, -94, 314, 94), 16, 16, paint("#FFFFFF", al, stroke=6))
    text(c, word, 0, 42, 118, "#FFFFFF", FT_BLACK, "c", al)
    c.restore()
    c.drawLine(cx - 200, cy + 110 * kk, cx - 200, cy + 230, paint("#9AA5B4", al, stroke=12))
    c.drawLine(cx + 200, cy + 110 * kk, cx + 200, cy + 230, paint("#9AA5B4", al, stroke=12))

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
    Y = PAL["yel"]
    yr = year_at(t)
    i0, d0, p0, dw0, c0, m0, r0, cta0 = (T(k)[0] for k in ("islands", "devi", "portugal", "dowry", "company", "merge", "rename", "cta"))

    # ---- base map: tiranga India in present-day scenes only; historical scenes dim modern borders
    hist = seg(t, i0 + 0.2, i0 + 1.0) * (1 - seg(t, r0, r0 + 0.8))
    base_map(c, cam, t, 1.0, 200 * (1 - hist), border_a=1 - 0.75 * hist)
    now_a = 255 * (1 - hist) * (1 - 0.6 * clamp((cam[2] - 40) / 100))
    if now_a > 0:
        if "NOW" not in EMP_PATH: EMP_PATH["NOW"] = _poly_path(WM.geoms["IND"], 0.01)
        s_ = in_map(c, cam); wave_flag(c, EMP_PATH["NOW"], "NOWV", t, now_a, s_); c.restore()
    # period polities (bhagwa) - only at zooms where the approximate borders read well
    ERA_ON = [("CE200", T("ptolemy")[0], p0 + 0.3), ("CE1530", p0, dw0 + 0.3), ("CE1650", dw0, m0 + 0.2)]
    era_now = None
    for ek, ta, tb in ERA_ON:
        ea = seg(t, ta, ta + 0.6) * (1 - seg(t, tb - 0.3, tb + 0.3))
        if ea > 0.5: era_now = ek
        era_layer(c, cam, ek, ea)
    # the seven islands (islands / devi scenes) and the merged island (merge / local)
    isl_a = seg(t, i0 + 0.5, i0 + 1.3) * (1 - seg(t, T("ptolemy")[0], T("ptolemy")[0] + 0.6)) + \
            seg(t, m0 + 0.3, m0 + 1.0) * (1 - seg(t, r0, r0 + 0.7))
    if isl_a > 0:
        rise = [at(i0 + 1.0 + 0.13 * j, 0.45) if t < T("ptolemy")[0] + 1 else 1.0 for j in range(7)]
        hl = {}
        for nm, w_ in (("COLABA", "Colaba"), ("MAHIM", "Mahim"), ("WORLI", "Worli"), ("PAREL", "Parel")):
            hl[nm] = at(kw(4, w_) - 0.1, 0.3) * (1 - seg(t, ue(4) + 0.6, ue(4) + 0.9))
        mk = seg(t, us(18) + 0.4, kw(18, "1845") + 0.3) if t > m0 else 0.0
        vk = seg(t, kw(18, "samundar") - 0.1, kw(18, "samundar") + 0.6) if t > m0 else 0.0
        draw_islands(c, cam, t, isl_a, rise, hl, mk, vk)

    # ================================================================ scene overlays
    if t < i0:                                           # ---- HOOK
        ho = 1 - seg(t, i0 - 0.35, i0)
        sp_k = at(kw(0, "Bombay") - 0.1, 0.5) * ho
        spotlight(c, *S("mum"), sp_k, t, r0=80)
        label(c, "MUMBAI (BOMBAY)", S("mum")[0] + 10, S("mum")[1] + 110, at(kw(0, "Bombay") + 0.2) * ho, col="#0F1B2D", bg=Y, size=34)
        L = []
        for i, ch in enumerate("BOMBAY"):
            p = seg(t, 0.12 + i * 0.09, 0.12 + i * 0.09 + 0.6); e = back(p, 1.6) if p < 1 else 1.0
            L.append(dict(ch=ch, al=clamp(p * 1.6), dy=(1 - e) * 90, col="#F1FAEE", sy=0.55 + 0.45 * e))
        qd = seg(t, kw(0, "Good") - 0.1, kw(0, "Good") + 0.45)
        L.append(dict(ch="?", w=ease_out(qd), al=qd, dy=-(1 - back(qd, 2.2)) * 120 if qd < 1 else 0, col=Y, rot=(1 - qd) * -25))
        word_row(c, L, DW / 2, 300, 165, 255 * ease_io(seg(t, 0.05, 0.6)) * ho, glow=Y if t < us(2) - 0.2 else "#FFB054")
        sh = seg(t, 0.95, 1.6)
        if 0 < sh < 1:
            bw = text_w("BOMBAY", 165); x0 = DW / 2 - bw / 2 - 60 + (bw + 120) * ease_io(sh)
            g_ = skia.GradientShader.MakeLinear([skia.Point(x0 - 60, 0), skia.Point(x0 + 60, 0)],
                                                [skia.ColorSetARGB(0, 255, 255, 255), skia.ColorSetARGB(int(150 * ho), 255, 255, 255), skia.ColorSetARGB(0, 255, 255, 255)])
            pp = skia.Paint(); pp.setShader(g_); pp.setBlendMode(skia.BlendMode.kPlus)
            c.save(); c.skew(-0.25, 0); c.translate(75, 0); c.drawRect(skia.Rect(x0 - 60, 150, x0 + 60, 340), pp); c.restore()
        q1 = 1 - seg(t, us(2) - 0.3, us(2))
        if q1 > 0:
            tw = pop_words(c, t, "MATLAB = \"GOOD BAY\"?", kw(0, "matlab") - 0.25, 420, 58, "#F1FAEE", q1 * ho)
            sk_ = at(us(1) - 0.05, 0.3)
            if sk_ > 0: c.drawLine(DW / 2 - tw / 2 - 10, 400, DW / 2 - tw / 2 - 10 + (tw + 20) * sk_, 400, paint("#FF4D5E", int(255 * q1), stroke=9, cap_round=True))
            stamp(c, "NAHI!", DW / 2, 540, 70, PAL["axis"], at(us(1) - 0.05, 0.35) * q1)
        if t > us(2) - 0.3:
            ak = seg(t, us(2) - 0.3, us(2)) * ho
            pop_words(c, t, "JAWAB: EK DEVI KA MANDIR", kw(2, "jawab") - 0.1, 420, 56, "#FFD166", ak)
            dk = at(kw(2, "devi") - 0.15, 0.5) * ho
            if dk > 0:
                x, y = S("mum")
                c.drawCircle(x, y - 40, 120 * ease_out(dk), paint("#FFD166", int(90 * dk), blur=30))
                temple_icon(c, x, y - 10, 90 * back(dk), int(255 * clamp(dk * 2)))
                rp = (t % 1.0); c.drawCircle(x, y - 40, 60 + 90 * rp, paint("#FFD166", int(180 * dk * (1 - rp)), stroke=4))
    if act("islands"):                                   # ---- SAAT DWEEP
        headline(c, "KABHI SAAT DWEEP THE", kin("islands", 0.5, 0.2), col=Y, sub="Aaj ke Mumbai ki jagah")
        n7 = sum(1 for j in range(7) if t > i0 + 1.0 + 0.13 * j + 0.2)
        if n7: chip(c, f"{n7} DWEEP", 905, 1110, at(i0 + 1.1) * out("islands"), bg=Y, fg="#0F1B2D", size=34)
        for nm, w_, key, dx, dy in (("COLABA", "Colaba", "colaba", -170, 30), ("MAHIM", "Mahim", "mahim", 150, -20),
                                    ("WORLI", "Worli", "worli", -150, -60), ("PAREL", "Parel", "parel", 170, 10)):
            x, y = S(key); label(c, nm, x + dx, y + dy, at(kw(4, w_) - 0.05) * out("islands"), size=32)
        bk = at(kw(5, "Koli") - 0.2, 0.5) * out("islands")
        if bk > 0:
            bx, by = S("boats")
            for j, (ox, oy) in enumerate(((-70, -130), (-120, 10), (-60, 150))):
                ic_ship(c, bx + ox + 6 * math.sin(t * 2 + j), by + oy, 34 * back(bk), col="#DCE3EC", a=int(255 * clamp(bk * 2)))
            label(c, "KOLI MACHHUARE", bx - 40, by - 270, bk, col="#0F1B2D", bg="#7FDBFF", size=32)
    if act("devi"):                                      # ---- MUMBA DEVI
        k_ = kin("devi", 0.5) * out("devi", 0.25)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(170 * k_)))
        headline(c, "MUMBA DEVI", kin("devi", 0.4), col="#FFB054", size=96)
        if DOC.get("devi") is not None:
            manuscript_card(c, DOC["devi"], at(kw(6, "Mumba") - 0.3, 0.5) * out("devi", 0.25), t, 540, 600, 360, -2,
                            "MUMBA DEVI", "KOLI KULDEVI KA MANDIR", "Photo: Magiceye (Flickr), CC BY-SA 2.0")
        c1 = at(kw(7, "Maha") - 0.15) * (1 - seg(t, us(8) - 0.2, us(8)))
        c2 = at(kw(7, "Aai") - 0.15) * (1 - seg(t, us(8) - 0.2, us(8)))
        chip(c, "MUMBA = MAHA AMBA (MAHAN MAA)", DW / 2, 1040, c1, bg="#C46A12", size=34)
        chip(c, "AAI = MAA (MARATHI)", DW / 2, 1118, c2, bg="#22304A", size=34)
        if t > us(8) - 0.2:
            a_ = 255 * at(us(8) - 0.2, 0.4) * out("devi", 0.25)
            pk = seg(t, kw(8, "Aai") - 0.1, kw(8, "Aai") + 0.35)
            bk = seg(t, kw(8, "bana") - 0.05, kw(8, "bana") + 0.5)
            L = [Lw(ch, "#FFB054") for ch in "MUMBA"] + [Lw("+", "#F1FAEE", w=pk * (1 - bk), al=pk * (1 - bk))] + \
                [Lw("A", "#F1FAEE", w=pk * (1 - bk), al=pk * (1 - bk * 1.5)), Lw("A", "#F1FAEE", w=pk * (1 - bk), al=pk * (1 - bk * 1.5)),
                 Lw("I", Y if bk > 0.5 else "#F1FAEE", w=pk, al=pk)]
            word_row(c, L, DW / 2, 1080, 120, a_, glow=Y if bk > 0.5 else "#FFB054")
    if act("ptolemy"):                                   # ---- PTOLEMY / HEPTANESIA
        k_ = kin("ptolemy", 0.5) * out("ptolemy", 0.25)
        mk = at(kw(9, "Ptolemy") - 0.4, 0.5) * out("ptolemy", 0.25)
        if mk > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(140 * mk)))
        headline(c, "c. 150 CE: PTOLEMY", kin("ptolemy", 0.5, 0.1), col="#6FA8FF")
        manuscript_card(c, DOC["ptolemy"], mk, t, 540, 620, 820, -1.5, "PTOLEMY KA NAKSHA", "GEOGRAPHIA - 15vi SADI KI PRATI",
                        "British Library, Harley MS 7182 (public domain)")
        hk = at(kw(9, "Heptanesia") - 0.15, 0.4) * out("ptolemy", 0.25)
        if hk > 0:
            sk_ = seg(t, kw(9, "saat") - 0.1, kw(9, "saat") + 0.4)
            L = [Lw(ch, "#6FA8FF") for ch in "HEPTA"] + [Lw(ch, "#F1FAEE") for ch in "NESIA"]
            word_row(c, L, DW / 2, 1110, 92, 255 * hk, glow="#6FA8FF")
            chip(c, "HEPTA = 7  +  NESOS = DWEEP", DW / 2, 1010 - 0, sk_ * out("ptolemy", 0.25), bg=Y, fg="#0F1B2D", size=32)
    if act("portugal"):                                  # ---- 1534 PORTUGAL
        gk = at(kw(10, "Gujarat") - 0.15, 0.4) * out("portugal")
        ring_highlight(c, *S("guj"), 70, gk * (1 - 0.6 * seg(t, kw(10, "Portugal"), kw(10, "Portugal") + 0.4)), t)
        label(c, "GUJARAT SULTANATE", S("guj")[0] + 40, S("guj")[1] - 100, gk * (1 - seg(t, kw(11, "Bombaim") - 0.6, kw(11, "Bombaim") - 0.3)), size=32)
        sym_flag(c, "GUJ", S("guj")[0] + 180, S("guj")[1] - 40, 90, gk, t)
        pk = at(kw(10, "Portugal") - 0.25, 1.0) * out("portugal")
        p0_, p1_ = S("sea_w"), S("mum")
        route(c, [p0_, ((p0_[0] + p1_[0]) / 2, p1_[1] - 120), p1_], ease_out(pk), col="#6FA8FF", w=6)
        if pk > 0:
            ic_ship(c, lerp(p0_[0], p1_[0], ease_out(pk)), lerp(p0_[1], p1_[1], ease_out(pk)) - 50 * math.sin(math.pi * ease_out(pk)), 40, col="#F1FAEE", a=int(255 * clamp(pk * 3)))
            label(c, "PORTUGAL KE JAHAZ", p0_[0] + 150, p0_[1] + 90, at(kw(10, "Portugal")) * out("portugal"), col="#0F1B2D", bg="#9CC3FF", size=30)
            sym_flag(c, "PRT", p0_[0] + 40, p0_[1] - 170, 100, at(kw(10, "Portugal")) * out("portugal"), t)
        spotlight(c, *S("mum"), at(kw(10, "dweep") - 0.1, 0.4) * out("portugal") * 0.6, t, r0=50)
        headline(c, "1534: PORTUGAL", kin("portugal", 0.5, 0.2), col="#6FA8FF", sub="Sandhi 1534, kabza 1535")
        bk = at(kw(11, "Bombaim") - 0.45, 0.4) * out("portugal")
        if bk > 0:
            L = []
            for i, ch in enumerate("BOMBAIM"):
                p = seg(t, kw(11, "Bombaim") - 0.25 + i * 0.07, kw(11, "Bombaim") - 0.25 + i * 0.07 + 0.4)
                L.append(dict(ch=ch, al=p, w=1, dy=(1 - ease_out(p)) * -40, col="#9CC3FF", rot=(1 - p) * 20))
            word_row(c, L, DW / 2, 470, 120, 255 * bk, glow="#6FA8FF")
            chip(c, "PORTUGUESE LEKH: \"BOMBAIM\"", DW / 2, 580, at(kw(11, "likhte") - 0.1) * out("portugal"), bg="#22304A", size=30)
    if act("myth"):                                      # ---- BOM BAIM MYTH
        k_ = kin("myth", 0.5) * out("myth", 0.25)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(170 * k_)))
        headline(c, "\"GOOD BAY\" WALI KAHANI", kin("myth", 0.5), col=Y)
        L = [Lw(ch, "#9CC3FF") for ch in "BOM"] + [Lw(" ")] + [Lw(ch, "#9CC3FF") for ch in "BAIM"]
        word_row(c, L, DW / 2, 430, 110, 255 * kin("myth", 0.4, 0.1) * out("myth", 0.25), glow="#6FA8FF")
        chip(c, "BOM = ACHHA", DW / 2 - 220, 545, at(kw(12, "achhi") - 0.15) * out("myth", 0.25), bg="#22304A", size=32)
        chip(c, "BAIM = KHAADI?", DW / 2 + 220, 545, at(kw(12, "khaadi") - 0.15) * out("myth", 0.25), bg="#22304A", size=32)
        wiki_card2(c, at(us(13) - 0.1, 0.6) * out("myth", 0.25), t, 620, kw(13, "jaankaar") - 0.1)
        stamp(c, "MYTH", 800, 1060, 70, PAL["axis"], at(kw(13, "galat") - 0.1, 0.35) * out("myth", 0.25))
    if act("dowry"):                                     # ---- 1661 DOWRY
        e = out("dowry")
        lk = at(dw0 + 1.2, 0.4) * e
        ring_highlight(c, *S("lisbon"), 34, lk, t, col="#9CC3FF"); ring_highlight(c, *S("london"), 34, lk, t, col="#FF8A92")
        label(c, "PORTUGAL", S("lisbon")[0] - 30, S("lisbon")[1] + 70, lk, size=28)
        label(c, "ENGLAND", S("london")[0] + 10, S("london")[1] - 70, lk, size=28)
        sym_flag(c, "PRT", S("lisbon")[0] + 40, S("lisbon")[1] - 20, 70, lk, t)
        sym_flag(c, "ENG", S("london")[0] + 90, S("london")[1] - 60, 80, lk, t)
        spotlight(c, *S("mum"), lk * 0.5, t, r0=40)
        label(c, "BOMBAY", S("mum")[0] + 20, S("mum")[1] + 70, lk, col="#0F1B2D", bg=Y, size=28)
        headline(c, "1661: DAHEJ MEIN DWEEP!", kin("dowry", 0.5, 0.2), col="#FF8A92")
        dk = at(kw(14, "dahej") - 0.3, 1.3) * e
        p0_, p1_ = S("mum"), S("london")
        rr = route(c, [p0_, ((p0_[0] + p1_[0]) / 2 + 60, min(p0_[1], p1_[1]) - 60), p1_], ease_out(dk), col=Y, w=6)
        label(c, "DAHEJ, 1661", (p0_[0] + p1_[0]) / 2 + 120, (p0_[1] + p1_[1]) / 2 - 40, at(kw(14, "dahej")) * e, col="#0F1B2D", bg=Y, size=32)
        hk = at(kw(15, "shaadi") - 0.1, 0.4) * e
        if hk > 0:                                       # heart between the two portrait badges
            x, y, s = DW / 2, 1010, 34 * back(hk)
            hp = skia.Path(); hp.moveTo(x, y + s); hp.cubicTo(x - 2.2 * s, y - 0.4 * s, x - 0.9 * s, y - 1.8 * s, x, y - 0.6 * s)
            hp.cubicTo(x + 0.9 * s, y - 1.8 * s, x + 2.2 * s, y - 0.4 * s, x, y + s); c.drawPath(hp, paint("#FF4D5E", int(255 * clamp(hk * 2))))
            text(c, "SHAADI, 1662", DW / 2, 1085, 26, "#F1FAEE", FT_BLACK, "c", int(255 * hk), shadow=True)
    if act("company"):                                   # ---- 1668 EAST INDIA COMPANY
        headline(c, "1668: EAST INDIA COMPANY", kin("company", 0.5, 0.2), col="#FF8A92")
        dk = at(kw(16, "East") - 0.3, 0.5) * (1 - seg(t, us(17) - 0.25, us(17)))
        if dk > 0: c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(130 * dk)))
        manuscript_card(c, DOC["b1672"], dk, t, 290, 640, 320, -3, "BOMBAY, 1672", "JOHN FRYER KA NAKSHA",
                        "Bombay Gazetteer 1896 / British Library (public domain)")
        sk_ = at(kw(16, "10") - 0.2, 0.6) * (1 - seg(t, us(17) - 0.25, us(17)))
        if sk_ > 0:
            v = int(round(lerp(0, 10, ease_out(seg(t, kw(16, "10") - 0.2, kw(16, "10") + 0.5)))))
            stat_card(c, 610, 400, 400, 270, f"£{v}", "SAALANA KIRAYA", sk_, col=Y)
        ek = at(kw(16, "Company") - 0.2) * (1 - seg(t, us(17) - 0.25, us(17)))
        sym_flag(c, "EIC", 700, 760, 150, ek, t)
        if ek > 0: text(c, "EAST INDIA COMPANY", 810, 1000, 28, "#F1FAEE", FT_BLACK, "c", int(255 * ek), shadow=True)
        if t > us(17) - 0.3:
            a_ = 255 * at(us(17) - 0.3, 0.4) * out("company", 0.25)
            yk = seg(t, kw(17, "Bombay") - 0.1, kw(17, "Bombay") + 0.5)
            L = [Lw(ch, "#9CC3FF") for ch in "BOMBA"] + \
                [Lw("I", "#FF4D5E" if yk > 0.05 else "#9CC3FF", w=1 - seg(yk, 0.5, 1), al=1 - seg(yk, 0.4, 1), dy=ease_in(yk) * 120, rot=yk * 35, strike=seg(yk, 0, 0.35)),
                 flip("M", "Y", seg(yk, 0.3, 1), "#9CC3FF", Y)]
            word_row(c, L, DW / 2, 600, 140, a_, glow="#FF8A92")
            chip(c, "ANGREZI ROOP: BOMBAY", DW / 2, 730, at(kw(17, "Bombay") + 0.2) * out("company", 0.25), bg=Y, fg="#0F1B2D", size=34)
    if act("merge"):                                     # ---- SAAT DWEEP, EK SHEHAR
        headline(c, "SAAT DWEEP, EK SHEHAR", kin("merge", 0.5, 0.2), col=Y, sub="Samundar bhar ke zameen banayi")
        x, y = S("vellard")
        label(c, "HORNBY VELLARD, 1782-84", x - 60, y - 70, at(kw(18, "samundar") + 0.2) * out("merge"), size=26)
        chip(c, "1838-1845 TAK (behes)", DW / 2, 1110, at(kw(18, "1845") - 0.1) * out("merge"), bg=Y, fg="#0F1B2D", size=32)
    if act("local"):                                     # ---- LOCAL NAAM
        k_ = kin("local", 0.4) * out("local", 0.25)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(120 * k_)))
        headline(c, "LOCAL NAAM: MUMBAI", kin("local", 0.4), col="#FFB054")
        chip(c, "MARATHI:  MUMBAI", DW / 2, 430, at(kw(19, "Marathi") - 0.1) * out("local", 0.25), bg="#C46A12", size=40)
        chip(c, "GUJARATI:  MUMBAI / MAMBAI", DW / 2, 530, at(kw(19, "Gujarati") - 0.1) * out("local", 0.25), bg="#C46A12", size=40)
        chip(c, "HINDI:  BAMBAI", DW / 2, 630, at(kw(19, "Mambai") + 0.1) * out("local", 0.25), bg="#22304A", size=34)
        text(c, "Purane lekh: 1516 \"Maiambu\" (Barbosa) - 1762 \"Manbai\" (Mirat-i Ahmadi)", DW / 2, 720, 24, "#DCE3EC", FT_SEMI, "c",
             int(255 * at(kw(19, "hi raha") - 0.1) * out("local", 0.25)), shadow=True)
    if act("rename"):                                    # ---- 1995
        spotlight(c, *S("mum"), at(kw(20, "sarkar") - 0.1) * out("rename") * 0.6, t, r0=45)
        headline(c, "1995: OFFICIAL NAAM MUMBAI", kin("rename", 0.5, 0.2), col="#FF9933")
        sign_board(c, at(r0 + 0.4, 0.5) * out("rename"), seg(t, kw(20, "Mumbai") - 0.1, kw(20, "Mumbai") + 0.4), t)
        chip(c, "SHIV SENA (MAHARASHTRA SARKAR) KI MAANG", DW / 2, 790, at(kw(20, "Shiv") - 0.1) * out("rename"), bg="#22304A", size=28)
    if act("cta", 0, 1):                                 # ---- CTA
        k = kin("cta", 0.6)
        c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(205 * k)))
        if t < us(22) - 0.1:
            headline(c, "EK SHEHAR, DO NAAM", k, y=230)
            r1 = at(us(21) + 0.1, 0.4); r2 = at(kw(21, "Bombay") - 0.15, 0.4)
            temple_icon(c, 160, 600, 60, int(255 * clamp(r1 * 2)))
            chip(c, "MUMBA AAI  >  MUMBAI", DW / 2 + 40, 565, r1, bg="#C46A12", size=44)
            chip(c, "BOMBAIM  >  BOMBAY", DW / 2 + 40, 725, r2, bg="#1E4F7A", size=44)
            text(c, "devi ka naam", DW / 2 + 40, 640, 28, "#FFE7C2", FT_SEMI, "c", int(255 * r1))
            text(c, "videshi roop", DW / 2 + 40, 800, 28, "#CFE4FF", FT_SEMI, "c", int(255 * r2))
        else:
            headline(c, "AAP KYA BOLTE HO?", at(us(22) - 0.1, 0.4), y=230)
            poll(c, seg(t, us(22) - 0.1, us(22) + 1.2), t)
            label(c, "COMMENT KARO", DW / 2, 1040, at(kw(23, "Comment") - 0.1, 0.5), col="#FFFFFF", bg=PAL["axis"], size=44)
            subscribe_btn(c, at(kw(23, "subscribe") - 0.4, 0.5), t, kw(23, "subscribe"))

    # ---- rulers: big card on the name, then a badge for the rest of the scene
    rb = kw(10, "Bahadur") - 0.35
    if rb <= t < T("portugal")[1]:
        ruler(c, "bahadur", at(rb, 0.4) * out("portugal"), seg(t, kw(10, "Portugal") - 0.2, kw(10, "Portugal") + 0.25), "#6FD38F", t, bxy=(915, 990))
    rc = kw(15, "Catherine") - 0.4
    if rc <= t < T("dowry")[1]:
        ruler(c, "catherine", at(rc, 0.4) * out("dowry"), seg(t, kw(15, "England") - 0.3, kw(15, "England") + 0.1), "#9CC3FF", t, bxy=(250, 990))
    rh = kw(15, "Charles") - 0.45
    if rh <= t < T("dowry")[1]:
        ruler(c, "charles", at(rh, 0.4) * out("dowry"), seg(t, ue(15) - 0.15, ue(15) + 0.3), "#FF8A92", t, bxy=(830, 990))
    # ---- period symbol notes (never called real flags)
    note = None
    if act("portugal") and t > kw(10, "Portugal") + 0.3: note = "PRT"
    elif act("portugal") and t > kw(10, "Gujarat") + 0.3: note = "GUJ"
    elif act("dowry") and t > dw0 + 1.6: note = "ENG"
    elif act("company") and t > kw(16, "Company") + 0.2 and t < us(17) - 0.3: note = "EIC"
    if note: flag_note(c, note, 1.0)
    # ---- era chip
    chip_s = None
    if act("islands") or act("devi"): chip_s = "Saat dweep, c. 150 CE (andaazan)"
    elif act("merge") or act("local"): chip_s = "Dweep jodne ka kaam, 1782-1845 (andaazan)"
    elif era_now: chip_s = ERA_LABEL[era_now] + " (andaazan)"
    if chip_s and not act("myth"): era_chip(c, chip_s)

    if 0.6 < t < cta0 and not act("myth") and not act("devi"):
        timeline(c, yr, seg(t, 0.6, 1.2))
    for a, b, cap in CAPS:
        if a - 0.05 <= t < b + 0.12: caption(c, cap, seg(t, a - 0.05, a + 0.08)); break
    if 2.0 < t < cta0 and not act("myth") and not act("devi"):
        text(c, "Approx. borders: historical-basemaps (A. Ourednik); dweep: andaazan", DW / 2, 1505, 19, PAL["muted"], FT_SEMI, "c", 210)
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
    E = [("whoosh_long", 0.15, -14), ("pop", kw(0, "Good") - 0.1, -12), ("stamp", us(1) - 0.05, -11), ("ding", kw(2, "devi") - 0.1, -14)]
    for k_ in ("islands", "devi", "ptolemy", "portugal", "myth", "dowry", "company", "merge", "local", "rename", "cta"):
        E.append(("whoosh_fast", T(k_)[0], -19))
    E += [("riser", T("islands")[0] + 0.1, -16)]
    for j in range(7): E.append(("pop", T("islands")[0] + 1.0 + 0.13 * j, -20))
    for w in ("Colaba", "Mahim", "Worli", "Parel"): E.append(("pop", kw(4, w) - 0.1, -16))
    E += [("pop", kw(5, "Koli") - 0.2, -16), ("pop", kw(6, "Mumba") - 0.3, -14), ("pop", kw(7, "Maha") - 0.15, -15),
          ("pop", kw(7, "Aai") - 0.15, -15), ("ding", kw(8, "bana") - 0.05, -13),
          ("pop", kw(9, "Ptolemy") - 0.4, -14), ("pop", kw(9, "Heptanesia") - 0.15, -15), ("ding", kw(9, "saat") - 0.1, -15),
          ("pop", kw(10, "Gujarat") - 0.15, -15), ("pop", kw(10, "Bahadur") - 0.35, -13), ("drag", kw(10, "Portugal") - 0.25, -16),
          ("pop", kw(11, "Bombaim") - 0.25, -15), ("pop", kw(12, "achhi") - 0.15, -15), ("pop", kw(12, "khaadi") - 0.15, -15),
          ("drag", kw(13, "jaankaar") - 0.1, -17), ("stamp", kw(13, "galat") - 0.1, -11),
          ("riser", T("dowry")[0], -16), ("whoosh_long", kw(14, "dahej") - 0.3, -15), ("pop", kw(15, "Catherine") - 0.4, -13),
          ("pop", kw(15, "Charles") - 0.45, -13), ("ding", kw(15, "shaadi") - 0.1, -15),
          ("pop", kw(16, "East") - 0.3, -14), ("pop", kw(16, "10") - 0.2, -13), ("glitch", kw(17, "Bombay") - 0.1, -14),
          ("drag", kw(18, "samundar") - 0.1, -15), ("ding", kw(18, "1845") - 0.1, -14),
          ("pop", kw(19, "Marathi") - 0.1, -15), ("pop", kw(19, "Gujarati") - 0.1, -15), ("pop", kw(19, "Mambai") + 0.1, -16),
          ("boom", T("rename")[0] + 0.1, -13), ("glitch", kw(20, "Mumbai") - 0.1, -13), ("pop", kw(20, "Shiv") - 0.1, -16),
          ("pop", us(21) + 0.1, -15), ("pop", kw(21, "Bombay") - 0.15, -14), ("pop", us(22) - 0.1, -15), ("pop", us(22) + 0.1, -17),
          ("pop", us(22) + 0.3, -17), ("pop", kw(23, "Comment") - 0.1, -14), ("ding", kw(23, "subscribe") + 0.35, -12)]
    return sorted(E, key=lambda e: e[1])
