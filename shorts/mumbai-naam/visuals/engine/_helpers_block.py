# ---------------------------------------------------------------- symbol textures blended inside borders
def _persia_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#9E1B24"))
    for i in range(-2, 16): cc.drawLine(i * 80, 0, i * 80 + h, h, paint("#FFFFFF", 18, stroke=8))
    cc.drawRect(skia.Rect(0, 0, w, h * 0.05), paint("#E8B84A")); cc.drawRect(skia.Rect(0, h * 0.95, w, h), paint("#E8B84A"))
    g = "#E8B84A"; cx, cy = w * 0.46, h * 0.5; k = min(w, h) / 420            # stylised falcon, wings spread
    for sx in (-1, 1):
        wg = skia.Path(); wg.moveTo(cx, cy - 10 * k)
        wg.cubicTo(cx + sx * 60 * k, cy - 70 * k, cx + sx * 140 * k, cy - 80 * k, cx + sx * 190 * k, cy - 60 * k)
        for j in range(5):
            yy = cy - 60 * k + j * 22 * k
            wg.lineTo(cx + sx * (190 - j * 22) * k, yy); wg.lineTo(cx + sx * (170 - j * 22) * k, yy + 14 * k)
        wg.lineTo(cx + sx * 20 * k, cy + 30 * k); wg.close(); cc.drawPath(wg, paint(g))
    cc.drawOval(skia.Rect(cx - 26 * k, cy - 40 * k, cx + 26 * k, cy + 70 * k), paint(g))
    cc.drawCircle(cx, cy - 58 * k, 22 * k, paint(g))
    bk = skia.Path(); bk.moveTo(cx + 18 * k, cy - 62 * k); bk.lineTo(cx + 40 * k, cy - 52 * k); bk.lineTo(cx + 16 * k, cy - 46 * k); bk.close()
    cc.drawPath(bk, paint("#C98A17"))
    tl = skia.Path(); tl.moveTo(cx - 22 * k, cy + 64 * k); tl.lineTo(cx, cy + 115 * k); tl.lineTo(cx + 22 * k, cy + 64 * k); tl.close(); cc.drawPath(tl, paint(g))
def _greek_tex(cc, w, h):
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#1F5FA8"))
    def meander(y0, sz):
        x = 0; p_ = paint("#FFFFFF", 255, stroke=sz * 0.18)
        while x < w:
            pa = skia.Path(); pa.moveTo(x, y0 + sz); pa.lineTo(x, y0); pa.lineTo(x + sz * 0.8, y0); pa.lineTo(x + sz * 0.8, y0 + sz * 0.6)
            pa.lineTo(x + sz * 0.4, y0 + sz * 0.6); pa.lineTo(x + sz * 0.4, y0 + sz * 0.3); cc.drawPath(pa, p_)
            cc.drawLine(x, y0 + sz, x + sz, y0 + sz, p_); x += sz
    sz = h * 0.12; meander(h * 0.04, sz); meander(h * 0.96 - sz, sz)
    cx, cy, r = w / 2, h / 2, min(w, h) * 0.22                                   # owl
    cc.drawOval(skia.Rect(cx - r * 0.8, cy - r, cx + r * 0.8, cy + r * 1.1), paint("#FFFFFF"))
    for sx in (-1, 1):
        cc.drawCircle(cx + sx * r * 0.33, cy - r * 0.35, r * 0.28, paint("#1F5FA8")); cc.drawCircle(cx + sx * r * 0.33, cy - r * 0.35, r * 0.12, paint("#FFFFFF"))
        e = skia.Path(); e.moveTo(cx + sx * r * 0.45, cy - r * 0.9); e.lineTo(cx + sx * r * 0.75, cy - r * 1.25); e.lineTo(cx + sx * r * 0.75, cy - r * 0.7); e.close()
        cc.drawPath(e, paint("#FFFFFF"))
    bk = skia.Path(); bk.moveTo(cx - r * 0.1, cy - r * 0.12); bk.lineTo(cx + r * 0.1, cy - r * 0.12); bk.lineTo(cx, cy + r * 0.12); bk.close(); cc.drawPath(bk, paint("#E8B84A"))
def _gr_flag(cc, w, h):                     # Greece (no PNG in the flag set): 9 stripes + canton cross
    for i in range(9): cc.drawRect(skia.Rect(0, i * h / 9, w, (i + 1) * h / 9 + 1), paint("#0D5EAF" if i % 2 == 0 else "#FFFFFF"))
    cw = h * 5 / 9; cc.drawRect(skia.Rect(0, 0, cw, cw), paint("#0D5EAF"))
    cc.drawRect(skia.Rect(cw * 0.4, 0, cw * 0.6, cw), paint("#FFFFFF")); cc.drawRect(skia.Rect(0, cw * 0.4, cw, cw * 0.6), paint("#FFFFFF"))
def _bs_flag(cc, w, h):                     # Bahamas
    cc.drawRect(skia.Rect(0, 0, w, h), paint("#00778B")); cc.drawRect(skia.Rect(0, h / 3, w, 2 * h / 3), paint("#FFC72C"))
    tr = skia.Path(); tr.moveTo(0, 0); tr.lineTo(w * 0.42, h / 2); tr.lineTo(0, h); tr.close(); cc.drawPath(tr, paint("#000000"))
def flag_tex(key):
    if key not in FTEX and key.startswith("F_"):
        iso = key[2:]
        FTEX[key] = {"gr": lambda: _surf_img(900, 600, _gr_flag), "bs": lambda: _surf_img(1000, 500, _bs_flag)}.get(iso, lambda: _img_tex(iso))()
    if key not in FTEX:
        asp = lambda k_: EMP_PATH[k_].getBounds().height() / EMP_PATH[k_].getBounds().width()
        FTEX[key] = {"PERSIA": lambda: _surf_img(1000, int(1000 * asp("PERSIA")), _persia_tex),
                     "GREEK": lambda: _surf_img(700, int(700 * max(0.6, asp("GREEK"))), _greek_tex),
                     "NOW": lambda: _img_tex("in"),
                     "NOWV": lambda: _surf_img(900, int(900 * asp("NOW")), _tiranga_tex)}[key]()
    return FTEX[key]

def ruler(c, key, kbig, kbadge, col, t, bxy=(150, 950)):
    """big framed portrait (kbig) that shrinks into a corner badge over the Arabian Sea (kbadge)"""
    img = RULER.get(key)
    if img is None or kbig <= 0: return
    name, line, credit, cr = RULER_INFO[key]
    iw, ih = img.width(), img.height()
    src = skia.Rect(cr[0] * iw, cr[1] * ih, cr[2] * iw, cr[3] * ih)
    asp = src.height() / src.width()
    m = ease_io(kbadge)
    w = lerp(470, 190, m); h = w * asp
    if h > lerp(620, 230, m): h = lerp(620, 230, m); w = h / asp
    cx = lerp(540, bxy[0], m); cy = lerp(700, bxy[1], m)
    al = int(255 * clamp(kbig * 2)); kk = back(clamp(kbig))
    if m < 0.01: c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"], int(150 * clamp(kbig))))
    c.save(); c.translate(cx, cy); c.scale(kk, kk); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    pad = lerp(14, 8, m); capH = lerp(110, 52, m)
    rrect(c, l - pad, tp - pad, l + w + pad, tp + h + capH, lerp(20, 12, m), "#F4F1EA", al, shadow=26)
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(l, tp, l + w, tp + h), 8, 8), True)
    z = 1.0 + 0.05 * clamp((t % 6) / 6)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al, src=src); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, l + w, tp + h), 8, 8, paint(col, al, stroke=lerp(4, 3, m)))
    fit = lambda s_, size, fp: min(size, size * (w + pad - 10) / max(1, text_w(s_, size, fp)))
    text(c, name, cx, tp + h + lerp(48, 34, m), fit(name, lerp(40, 24, m), FT_BLACK), "#0F1B2D", FT_BLACK, "c", al)
    if m < 0.6:
        a2 = int(al * (1 - m / 0.6))
        text(c, line, cx, tp + h + 86, fit(line, 26, FT_SEMI), "#5B6472", FT_SEMI, "c", a2)
    c.restore()
    if m < 0.6: text(c, credit, cx, tp + h + capH + 40, 18, PAL["muted"], FT_SEMI, "c", int(al * (1 - m / 0.6)))

def photo_card(c, img, k, t, cx=540, cy=760, w=520, cap="", sub="", credit=""):
    """real photo in a gold frame; pops in with a slow Ken Burns push"""
    if k <= 0: return
    al = int(255 * clamp(k * 2)); kk = back(k)
    h = w * img.height() / img.width()
    c.save(); c.translate(cx, cy); c.scale(kk, kk); c.rotate(-2.5 * (1 - k)); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    rrect(c, l - 14, tp - 14, l + w + 14, tp + h + 120, 20, "#F4F1EA", al, shadow=30)
    c.save(); r = skia.RRect.MakeRectXY(skia.Rect(l, tp, l + w, tp + h), 10, 10); c.clipRRect(r, True)
    z = 1.0 + 0.06 * clamp(t % 10 / 3.0)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al); c.restore()
    c.drawRoundRect(skia.Rect(l, tp, l + w, tp + h), 10, 10, paint(COL["MAURYA"], al, stroke=4))
    fit = lambda s_, size, fp: min(size, size * (w - 20) / max(1, text_w(s_, size, fp)))
    text(c, cap, cx, tp + h + 52, fit(cap, 36, FT_BLACK), "#0F1B2D", FT_BLACK, "c", al)
    text(c, sub, cx, tp + h + 88, fit(sub, 26, FT_SEMI), "#5B6472", FT_SEMI, "c", al)
    c.restore()
    if credit: text(c, credit, cx, tp + h + 150, 18, PAL["muted"], FT_SEMI, "c", al)

def _surf_img(w, h, fn):
    sf = skia.Surface(w, h); cc = sf.getCanvas(); fn(cc, w, h); return sf.makeImageSnapshot()

def _chakra(cc, x, y, r, col, sw):
    cc.drawCircle(x, y, r, paint(col, 255, stroke=sw)); cc.drawCircle(x, y, r * 0.16, paint(col))
    for i in range(24):
        a_ = 2 * math.pi * i / 24
        cc.drawLine(x + math.cos(a_) * r * 0.16, y + math.sin(a_) * r * 0.16, x + math.cos(a_) * r, y + math.sin(a_) * r, paint(col, 255, stroke=sw * 0.45))

def _tiranga_tex(cc, w, h):
    """tiranga sized to India's box: bands fill India, a smaller chakra sits on mainland India's centre"""
    b = EMP_PATH["NOW"].getBounds(); bw, bh = b.width(), b.height()
    mx, my = cam_xy(78.6, 22.6)
    fx = (mx - (b.centerX() - bw * 1.06 / 2)) / (bw * 1.06); fy = (my - (b.centerY() - bh * 1.08 / 2)) / (bh * 1.08)
    cy = fy * h; band = h * 0.16
    cc.drawRect(skia.Rect(0, 0, w, cy - band), paint("#FF9933"))
    cc.drawRect(skia.Rect(0, cy - band, w, cy + band), paint("#FFFFFF"))
    cc.drawRect(skia.Rect(0, cy + band, w, h), paint("#138808"))
    _chakra(cc, fx * w, cy, band * 0.82, "#000080", max(3, band * 0.07))

def _img_tex(code):
    im = flag_img(code)
    return _surf_img(900, int(900 * im.height() / im.width()), lambda cc, w, h: draw_img(cc, im, 0, 0, w, h))

def wave_flag(c, path, key, t, a, s, center=None):
    """draws the flag texture inside `path` (canvas already in map coords), waving like cloth"""
    if a <= 0: return
    img = flag_tex(key); iw, ih = img.width(), img.height()
    b = path.getBounds(); bw, bh = b.width(), b.height()
    if key == "NOW" or key.startswith("F_"):      # real flags: keep proportions, cover the country box
        sc = max(bw / iw, bh / ih) * (1.08 if center is None else 1.45); w, h = iw * sc, ih * sc
    else:                                         # whole flag/emblem fits the empire box
        w = bw * 1.06; h = max(bh * 1.08, w * ih / iw)
    fx, fy = (b.centerX(), b.centerY()) if center is None else center
    x0, y0 = fx - w / 2, fy - h / 2
    c.save(); c.clipPath(path, doAntiAlias=True)
    lp = skia.Paint(); lp.setAlphaf(clamp(a / 255) * 0.5)
    c.saveLayer(skia.Rect(x0, y0 - h * 0.1, x0 + w, y0 + h * 1.1), lp)   # strips drawn opaque, blended once
    n = 140; amp = h * 0.022; pw = w / n
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n
        ph = 2 * math.pi * (u0 * 1.6 - t * 0.55)
        dy = math.sin(ph) * amp * (0.3 + 0.7 * u0)
        c.drawImageRect(img, skia.Rect(u0 * iw, 0, min(iw, u1 * iw + 2), ih), skia.Rect(x0 + u0 * w, y0 + dy, x0 + u1 * w + pw * 0.6, y0 + h + dy), SAMP, skia.Paint())
    cols, pos = [], []
    for i in range(n + 1):
        u = i / n; sh = math.cos(2 * math.pi * (u * 1.6 - t * 0.55))
        cols.append(skia.ColorSetARGB(int(abs(sh) * 40), 255, 255, 255) if sh > 0 else skia.ColorSetARGB(int(abs(sh) * 55), 0, 0, 0)); pos.append(u)
    gp = skia.Paint(); gp.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x0 + w, 0)], cols, pos))
    c.drawRect(skia.Rect(x0, y0 - amp * 2, x0 + w, y0 + h + amp * 2), gp)
    c.restore(); c.restore()

def flag_note(c, key, k, y0=1086):
    if k <= 0: return
    s_ = FLAG_NOTE[key]; size = 22; w = text_w(s_, size, FT_SEMI)
    al = int(255 * clamp(k * 2)); x1 = DW - 36
    if y0 != 1086: x1 = DW / 2 + (w + 36) / 2
    rrect(c, x1 - w - 36, y0, x1, y0 + 38, 19, "#0F1B2D", int(al * 0.8))
    c.drawCircle(x1 - w - 18, y0 + 19, 6, paint(PAL["yel"], al))
    text(c, s_, x1 - 14, y0 + 27, size, "#DCE3EC", FT_SEMI, "r", al)

def draw_emp(c, cam, key, a, fill_a=150, stroke=2.4, draw_k=1.0, col=None, t=0.0, flag=True):
    if a <= 0: return
    col = col or COL[key]
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
    path = EMP_PATH[key]
    c.drawPath(path, paint(col, int((fill_a * 0.55 if flag else fill_a) * a / 255)))
    if flag: wave_flag(c, path, key, t, a * clamp(draw_k * 1.5 - 0.5), s)
    pm = skia.PathMeasure(path, False); out = skia.Path()
    while True:                      # progressive outline draw
        L = pm.getLength(); pm.getSegment(0, L * clamp(draw_k), out, True)
        if not pm.nextContour(): break
    glow = paint(col, int(a * 0.5), stroke=(stroke + 4) / s, blur=4 / s)
    c.drawPath(out, glow); c.drawPath(out, paint("#FFF4D6", a, stroke=stroke / s))
    c.restore()

def base_map(c, cam, t, india_k=1.0, india_a=200, border_a=1.0):
    c.drawRect(skia.Rect(0, 0, DW, DH), paint(PAL["ocean"]))
    c.save(); c.translate(0, MAP_CY - DH / 2)
    draw_map(c, WM, cam, fills={"IND": (COL["NOW"], int(india_a * india_k))}, border_a=border_a)
    c.restore()

def headline(c, s, k, col="#F1FAEE", y=230, size=92, sub=None):
    """word-by-word reveal: each word rises, un-blurs and settles with a soft overshoot; underline sweeps; sub types in"""
    if k <= 0: return
    size = min(size, size * 960 / max(1, text_w(s, size)))
    words = s.split(" "); sp = text_w(" ", size); ws = [text_w(w_, size) for w_ in words]
    tot = sum(ws) + sp * (len(words) - 1); x = DW / 2 - tot / 2; n = len(words)
    for i, (w_, ww) in enumerate(words and zip(words, ws)):
        p = clamp((k * (1 + 0.35 * (n - 1)) - 0.35 * i) / 1.0)
        if p > 0:
            e = back(p, 1.3) if p < 1 else 1.0
            al = int(255 * clamp(p * 1.8)); dy = (1 - e) * 46
            c.save(); c.translate(x + ww / 2, y + dy); sc = 0.86 + 0.14 * e; c.scale(sc, sc)
            text(c, w_, 0, 0, size, col, FT_BLACK, "c", al, shadow=True); c.restore()
        x += ww + sp
    uk = ease_out(seg(k, 0.35, 1.0)); w = tot * uk
    al = int(255 * clamp(k * 2))
    c.drawRect(skia.Rect(DW / 2 - w / 2, y + 22, DW / 2 + w / 2, y + 30), paint(PAL["axis"], al))
    if sub:
        sk = seg(k, 0.45, 1.0); nch = int(round(len(sub) * ease_out(sk)))
        if nch > 0: text(c, sub[:nch], DW / 2, y + 90, 44, PAL["yel"], FT_SEMI, "c", int(255 * clamp(sk * 3)))

def caption(c, s, k):
    if k <= 0 or not s: return
    al = int(255 * clamp(k * 3)); size = 62
    w = text_w(s, size)
    if w > 960: size *= 960 / w; w = 960
    kk = 0.85 + 0.15 * back(clamp(k))
    c.save(); c.translate(DW / 2, 1390); c.scale(kk, kk)
    rrect(c, -w / 2 - 24, -size * 0.95, w / 2 + 24, size * 0.38, 16, "#000000", int(al * 0.6))
    x = -w / 2
    for i, word in enumerate(s.split(" ")):
        key = re.sub(r"[^a-z0-9]", "", word.lower())
        col = PAL["yel"] if key in CAP_KEYS else "#FFFFFF"
        x += text(c, word + " ", x, 0, size, col, FT_BLACK, "l", al)
    c.restore()

def timeline(c, year, k):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); x0, x1, y = 110, 970, 1220
    def X(yr):  # piecewise so BCE fits
        pts = [(-300, x0), (1600, x0 + 300), (1800, x0 + 520), (2026, x1)]
        for (a, xa), (b, xb) in zip(pts, pts[1:]):
            if a <= yr <= b: return lerp(xa, xb, (yr - a) / (b - a))
        return x0 if yr < -300 else x1
    c.drawRoundRect(skia.Rect(x0, y - 4, x1, y + 4), 4, 4, paint("#3E5068", al))
    c.drawRoundRect(skia.Rect(x0, y - 4, X(year), y + 4), 4, 4, paint(PAL["yel"], al))
    for yr, lab in TL:
        on = abs(yr - year) < 30
        c.drawCircle(X(yr), y, 12 if on else 8, paint(PAL["yel"] if X(yr) <= X(year) + 1 else "#3E5068", al))
        text(c, lab, X(yr), y + 52, 30 if on else 24, "#F1FAEE" if on else PAL["muted"], FT_BLACK if on else FT_SEMI, "c", al)
    lab = f"{-int(year)} BCE" if year < 0 else f"{int(year)}"
    pill(c, lab, X(year), y - 50, 34, PAL["yel"], fg="#0F1B2D", a=al)

def label(c, s, x, y, k, col="#F1FAEE", size=34, bg=PAL["ocean"]):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); kk = back(k)
    c.save(); c.translate(x, y); c.scale(kk, kk)
    pill(c, s, 0, 0, size, bg, fg=col, a=al, shadow=8)
    c.restore()

def arrow(c, p0, p1, k, col=PAL["yel"]):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 80
    route(c, [p0, (mx, my), p1], ease_out(k), col=col, w=6, dash=False)

def highlight_country(c, cam, code, k, t, col="#FFD166"):
    """glowing, pulsing highlight of a modern country (Natural Earth geometry) on the map"""
    if k <= 0: return
    key = "HL_" + code
    if key not in EMP_PATH: EMP_PATH[key] = _poly_path(WM.geoms[code], 0.01)
    cx, cy = cam_xy(cam[0], cam[1]); s = cam[2]; pulse = 0.75 + 0.25 * math.sin(t * 6.0)
    c.save(); c.translate(DW / 2, MAP_CY); c.scale(s, s); c.translate(-cx, -cy)
    path = EMP_PATH[key]; al = clamp(k)
    c.drawPath(path, paint(col, int(95 * al * pulse)))
    c.drawPath(path, paint(col, int(170 * al), stroke=7 / s, blur=4 / s))
    c.drawPath(path, paint("#FFF1C2", int(255 * al), stroke=1.8 / s))
    c.restore()

def spotlight(c, x, y, k, t, r0=95, col="#FFD166"):
    """darkens everything except a circle around (x, y), with a pulsing ring"""
    if k <= 0: return
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r0 * 3.2, [skia.ColorSetARGB(0, 0, 0, 0), skia.ColorSetARGB(int(165 * clamp(k)), 4, 8, 18)], [0.3, 1.0])
    p_ = skia.Paint(); p_.setShader(sh); c.drawRect(skia.Rect(0, 0, DW, DH), p_)
    rp = (t % 1.1) / 1.1
    c.drawCircle(x, y, r0 * (0.55 + 0.25 * ease_out(clamp(k))), paint(col, int(255 * clamp(k)), stroke=6))
    c.drawCircle(x, y, r0 * (0.6 + 0.9 * rp), paint(col, int(200 * clamp(k) * (1 - rp)), stroke=5))

def ring_highlight(c, x, y, r, k, t, col="#FFD166"):
    """region without a modern border (Bengal, Deccan...): soft glow disc + pulsing double ring, no darkening"""
    if k <= 0: return
    al = clamp(k); kk = back(al); rp = (t % 1.0)
    c.drawCircle(x, y, r * kk, paint(col, int(70 * al)))
    c.drawCircle(x, y, r * kk, paint(col, int(230 * al), stroke=6))
    c.drawCircle(x, y, r * (1.0 + 0.6 * rp), paint(col, int(180 * al * (1 - rp)), stroke=4))

def subscribe_btn(c, k, t, t_click):
    if k <= 0: return
    al = int(255 * clamp(k * 2)); clicked = t >= t_click + 0.35
    kk = back(clamp(k)) * (1 - 0.08 * math.sin(math.pi * seg(t, t_click + 0.25, t_click + 0.45)))
    cx, cy = DW / 2, 1255
    c.save(); c.translate(cx, cy); c.scale(kk, kk)
    w = 420; bg = "#3A3F4B" if clicked else "#E62117"
    rrect(c, -w / 2, -44, w / 2, 44, 44, bg, al, shadow=14)
    text(c, "SUBSCRIBED" if clicked else "SUBSCRIBE", 22, 15, 40, "#FFFFFF", FT_BLACK, "c", al)
    bx = -w / 2 + 52                                   # bell
    pb = skia.Path(); pb.moveTo(bx - 14, 10); pb.quadTo(bx - 14, -20, bx, -20); pb.quadTo(bx + 14, -20, bx + 14, 10); pb.close()
    c.drawPath(pb, paint("#FFFFFF", al)); c.drawCircle(bx, 15, 5, paint("#FFFFFF", al))
    c.restore()
    if t < t_click + 0.9:                              # cursor slides in and clicks
        m = ease_out(seg(t, t_click - 0.4, t_click + 0.2)); px, py = lerp(cx + 330, cx + 60, m), lerp(cy + 170, cy + 18, m)
        pc = skia.Path(); pc.moveTo(px, py); pc.lineTo(px, py + 46); pc.lineTo(px + 12, py + 35); pc.lineTo(px + 22, py + 56)
        pc.lineTo(px + 30, py + 52); pc.lineTo(px + 20, py + 32); pc.lineTo(px + 36, py + 32); pc.close()
        c.drawPath(pc, paint("#FFFFFF", al)); c.drawPath(pc, paint("#000000", al, stroke=2.5))

def render_still(t, out):
    surf = skia.Surface(W4, H4); c = surf.getCanvas(); c.scale(SC, SC)
    frame(c, t)
    surf.makeImageSnapshot().save(out, skia.kPNG)

# ---------------------------------------------------------------- big morphing word
def word_row(c, letters, cx, cy, size, a=255, glow=None):
    """letters: list of dicts {ch, w (width 0..1), al (0..1), col, dy, sy (flip scale)}; centred on cx"""
    if a <= 0: return
    ws = [text_w(L["ch"], size) * L.get("w", 1) for L in letters]
    x = cx - sum(ws) / 2
    if glow:
        tw = sum(ws); rrect(c, cx - tw / 2 - 40, cy - size * 0.95, cx + tw / 2 + 40, cy + size * 0.32, 26, "#0B1424", int(a * 0.82), shadow=20)
        c.drawRoundRect(skia.Rect(cx - tw / 2 - 40, cy - size * 0.95, cx + tw / 2 + 40, cy + size * 0.32), 26, 26, paint(glow, int(a * 0.9), stroke=4))
    for L, w_ in zip(letters, ws):
        al = int(a * clamp(L.get("al", 1)))
        if al > 0 and L.get("w", 1) > 0.02:
            lx = x + w_ / 2
            c.save(); c.translate(lx, cy - size * 0.33 + L.get("dy", 0)); c.scale(1, max(0.02, L.get("sy", 1))); c.rotate(L.get("rot", 0))
            text(c, L["ch"], 0, size * 0.33, size, L.get("col", "#F1FAEE"), FT_BLACK, "c", al, shadow=True)
            c.restore()
            if L.get("strike", 0) > 0:
                sk_ = L["strike"]; c.drawLine(lx - w_ * 0.6, cy - size * 0.7, lx - w_ * 0.6 + w_ * 1.2 * sk_, cy + size * 0.05, paint("#FF4D5E", al, stroke=10, cap_round=True))
        x += w_
def flip(ch0, ch1, p, col0="#F1FAEE", col1=None):
    """letter that flips from ch0 to ch1 as p goes 0 -> 1"""
    col1 = col1 or PAL["yel"]
    return dict(ch=ch0 if p < 0.5 else ch1, sy=abs(math.cos(math.pi * clamp(p))), col=col0 if p < 0.5 else col1)
def Lw(ch, col="#F1FAEE", w=1, al=1, dy=0, rot=0, strike=0): return dict(ch=ch, col=col, w=w, al=al, dy=dy, rot=rot, strike=strike)

def chip(c, s, x, y, k, bg="#22304A", fg="#F1FAEE", size=34):
    label(c, s, x, y, k, col=fg, size=size, bg=bg)

def manuscript_card(c, img, k, t, cx, cy, w, ang, cap, sub, credit):
    """sacred-text document card: warm golden halo, gold double frame, slow push-in, caption + credit"""
    if k <= 0 or img is None: return
    al = int(255 * clamp(k * 2)); kk = back(clamp(k), 1.4)
    h = w * img.height() / img.width()
    halo = skia.GradientShader.MakeRadial(skia.Point(cx, cy), w * 0.95, [skia.ColorSetARGB(int(150 * clamp(k)), 255, 190, 90), skia.ColorSetARGB(0, 255, 160, 60)])
    hp = skia.Paint(); hp.setShader(halo); c.drawCircle(cx, cy, w * 0.95, hp)
    for i in range(10):                                   # a few drifting light motes
        a_ = i * 2.4 + t * 0.6; r_ = w * (0.55 + 0.08 * math.sin(i * 1.7 + t))
        mx, my = cx + math.cos(a_) * r_, cy + math.sin(a_) * r_ * 0.8
        c.drawCircle(mx, my, 3 + (i % 3), paint("#FFE2A8", int(160 * clamp(k) * (0.5 + 0.5 * math.sin(t * 3 + i))), blur=2))
    c.save(); c.translate(cx, cy); c.rotate(ang * kk); c.scale(kk, kk); c.translate(-cx, -cy)
    l, tp = cx - w / 2, cy - h / 2
    rrect(c, l - 18, tp - 18, l + w + 18, tp + h + 104, 18, "#FBF3DF", al, shadow=30)
    c.drawRoundRect(skia.Rect(l - 10, tp - 10, l + w + 10, tp + h + 96), 12, 12, paint("#C9A24A", al, stroke=3))
    c.save(); c.clipRect(skia.Rect(l, tp, l + w, tp + h))
    z = 1.0 + 0.05 * clamp((t % 8) / 4)
    draw_img(c, img, cx - w / 2 * z, cy - h / 2 * z, cx + w / 2 * z, cy + h / 2 * z, al); c.restore()
    c.drawRect(skia.Rect(l, tp, l + w, tp + h), paint("#B8862B", al, stroke=4))
    text(c, cap, cx, tp + h + 50, 38, "#7A1E0E", FT_BLACK, "c", al)
    text(c, sub, cx, tp + h + 84, 26, "#B5651D", FT_BLACK, "c", al)
    c.restore()
    text(c, credit, cx, tp + h + 140, 17, "#DCE3EC", FT_SEMI, "c", int(al * 0.9), shadow=True)

def poll(c, k, t):
    items = [("INDIA", "#2F6FB5"), ("BHARAT", "#FF9933"), ("HINDUSTAN", "#2FA36B")]
    for i, (s_, col) in enumerate(items):
        kk = ease_out(seg(k, i * 0.18, 0.5 + i * 0.18))
        if kk <= 0: continue
        y = 520 + i * 150; al = int(255 * clamp(kk * 2)); x0 = 160 + (1 - kk) * 200
        rrect(c, x0, y - 55, 920, y + 55, 55, "#18253A", al, shadow=14)
        c.drawCircle(x0 + 58, y, 36, paint(col, al)); text(c, "ABC"[i], x0 + 58, y + 14, 40, "#FFFFFF", FT_BLACK, "c", al)
        text(c, s_, x0 + 120, y + 20, 56, "#F1FAEE", FT_BLACK, "l", al)

