"""Extra props for the Mughal Empire video (same outlined toon style, 200 x 200 design units).
Registered into props.PROPS by props.py."""
from common import shade

GOLD, GOLD_D = "#f1c232", "#c9961a"
__all__ = ["war_elephant", "elephant_panic", "horse_rider", "bullock_cart", "araba", "cannon_fire", "dovecote",
           "peacock_throne", "kohinoor", "farman", "grave", "army_block", "mughal_tent", "pigeon", "smoke",
           "matchlock_man", "rope"]


def _elephant(p, col, cap, rear=False):
    dx = 0
    if rear:  # body tilted up at the front
        p.ell(110, 118, 62, 44, col)
        for x, y in ((140, 160), (152, 150)):
            p.capsule((x, y - 30), (x + 6, y + 8), 22, col)
        for x in (78, 96):
            p.capsule((x, 140), (x, 186), 24, col)
        p.ell(150, 80, 34, 32, col)                     # head raised
        p.ell(138, 78, 20, 26, shade(col, 0.88))        # ear
        p.line([(176, 70), (192, 40), (186, 20)], col, 16)  # trunk up
        p.line([(170, 94), (188, 92)], "#f6efe0", 7)    # tusk
        p.ell(158, 72, 4, 4, "#1a1410", ol=False)
        p.poly([(80, 80), (140, 70), (146, 104), (84, 112)], cap)
        p.rrect(92, 52, 134, 76, 6, GOLD)
        return
    for x in (52, 78, 128, 152):
        p.capsule((x, 140), (x, 188), 24, col)
    p.ell(100, 112, 78, 50, col)                         # body
    p.ell(160, 96, 34, 34, col)                          # head
    p.ell(146, 96, 22, 30, shade(col, 0.88))             # ear
    p.line([(180, 104), (184, 140), (176, 174)], col, 15)  # trunk down
    p.line([(174, 118), (188, 126)], "#f6efe0", 7)       # tusk
    p.ell(170, 88, 4, 4, "#1a1410", ol=False)
    p.line([(28, 104), (20, 132)], col, 5)               # tail
    p.poly([(50, 76), (150, 76), (156, 128), (44, 128)], cap)   # caparison
    p.rrect(44, 120, 156, 130, 4, GOLD, w=3)
    for x in range(56, 150, 18):
        p.ell(x, 136, 4, 6, GOLD, w=2)


def war_elephant(p, c):
    """War elephant with howdah. color = caparison colour."""
    cap = c or "#9a2a2a"
    _elephant(p, "#8d8a94", cap)
    p.rrect(66, 40, 134, 78, 6, "#c9a227")               # howdah
    p.poly([(60, 42), (140, 42), (100, 12)], cap)
    p.line([(100, 12), (100, 4)], "#5a3a20", 4)


def elephant_panic(p, c):
    """Panicked rearing elephant (Panipat: guns frightened the elephants)."""
    _elephant(p, "#8d8a94", c or "#9a2a2a", rear=True)
    for x, y in ((40, 40), (24, 64), (52, 22)):
        p.line([(x, y), (x - 10, y - 10)], "#ffffff", 5)


def horse_rider(p, c):
    """Cavalry: horse + rider with lance. color = rider's coat."""
    coat = c or "#3f6d5a"
    horse = "#7a4a2a"
    for x0, x1 in ((58, 46), (78, 74), (128, 132), (148, 160)):
        p.capsule((x0, 128), (x1, 184), 14, horse)
    p.ell(102, 118, 60, 30, horse)
    p.poly([(140, 104), (158, 56), (182, 62), (176, 80), (154, 120)], horse)   # neck + head
    p.ell(176, 70, 14, 10, horse)
    p.poly([(150, 60), (156, 44), (162, 58)], horse)
    p.line([(140, 64), (146, 98)], "#2a1a12", 8)          # mane
    p.line([(44, 112), (26, 150)], "#2a1a12", 9)          # tail
    p.ell(172, 66, 3, 3, "#111", ol=False)
    p.rrect(84, 92, 120, 110, 6, "#c9a227")               # saddle
    p.capsule((100, 92), (104, 46), 26, coat)              # rider body
    p.capsule((104, 96), (112, 128), 12, coat)              # leg
    p.ell(104, 34, 15, 15, "#e0ac7e")                       # head
    p.chord(104, 30, 17, 16, 180, 360, "#efe6cf")          # turban
    p.line([(70, 70), (190, 20)], "#5a3a20", 5)            # lance
    p.poly([(188, 16), (198, 14), (192, 24)], "#d9dde2")


def bullock_cart(p, c):
    """Bullock cart with a canopy (Zafar's exile, Oct 1858)."""
    bull = "#c9b89a"
    for x in (150, 176):
        p.capsule((x, 140), (x, 184), 12, bull)
    p.ell(162, 126, 34, 22, bull)
    p.ell(192, 114, 12, 14, bull)
    p.line([(186, 102), (180, 90)], "#efe6cf", 5)
    p.line([(196, 102), (200, 90)], "#efe6cf", 5)
    p.line([(60, 140), (150, 118)], "#5a3a20", 6)          # yoke pole
    p.rrect(18, 108, 120, 138, 4, "#8a5a2a")               # cart bed
    p.ell(46, 156, 28, 28, "#6a4a2a")                       # wheel
    p.ell(46, 156, 8, 8, "#3a2a1a")
    for a in range(0, 180, 45):
        import math
        dx, dy = 26 * math.cos(math.radians(a)), 26 * math.sin(math.radians(a))
        p.line([(46 - dx, 156 - dy), (46 + dx, 156 + dy)], "#3a2a1a", 3)
    p.chord(70, 110, 54, 46, 180, 360, c or "#e9e2d0")    # canopy
    p.line([(18, 110), (18, 80)], "#5a3a20", 4)
    p.line([(122, 110), (122, 80)], "#5a3a20", 4)


def araba(p, c):
    """Wall of carts tied with ropes (Babur's defence at Panipat)."""
    for k, x in enumerate((10, 74, 138)):
        p.rrect(x, 96, x + 56, 130, 4, "#8a5a2a")
        p.ell(x + 16, 146, 16, 16, "#6a4a2a")
        p.ell(x + 16, 146, 5, 5, "#3a2a1a")
        p.rrect(x + 6, 76, x + 50, 98, 3, "#a87442")
    for x in (66, 130):
        p.line([(x - 6, 108), (x + 14, 112), (x - 6, 118), (x + 14, 122)], "#d9b77a", 5)
    p.poly([(60, 60), (100, 40), (140, 60), (100, 70)], "#3a3a40")   # gun barrel peeking
    p.ell(140, 60, 6, 8, "#2a2a30")


def cannon_fire(p, c):
    """Cannon firing with muzzle flash and smoke."""
    p.ell(146, 72, 40, 28, "#bdb6ad", ol=False)
    p.ell(166, 58, 24, 20, "#d6d0c8", ol=False)
    p.poly([(136, 60), (186, 42), (166, 70), (188, 94), (136, 82)], "#ffb347")
    p.poly([(142, 64), (172, 54), (160, 72), (174, 86), (142, 78)], "#fff1a8", ol=False)
    p.poly([(10, 90), (130, 64), (140, 92), (20, 122)], "#3a3a40")
    p.ell(56, 146, 38, 38, "#7a4a22")
    p.ell(56, 146, 10, 10, "#4a2a12")


def dovecote(p, c):
    """Pigeon house on a fort wall edge (Umar Shaikh Mirza, Akhsi, 1494)."""
    p.rrect(60, 70, 140, 190, 4, "#c9a27a")
    p.poly([(50, 72), (150, 72), (100, 20)], "#8a3f22")
    for y in (96, 132):
        for x in (78, 100, 122):
            p.ell(x, y, 8, 10, "#3a2a1a")
    for x, y in ((40, 40), (164, 52), (30, 96)):
        pigeon(p, None, x, y, 0.35)


def pigeon(p, c, x=100, y=100, k=1.0):
    col = c or "#c8ccd4"
    p.ell(x, y, 40 * k, 24 * k, col)
    p.ell(x + 34 * k, y - 16 * k, 16 * k, 16 * k, col)
    p.poly([(x + 48 * k, y - 18 * k), (x + 60 * k, y - 14 * k), (x + 48 * k, y - 10 * k)], "#e8a33a")
    p.poly([(x - 10 * k, y - 10 * k), (x - 40 * k, y - 50 * k), (x + 14 * k, y - 18 * k)], shade(col, 0.85))


def peacock_throne(p, c):
    """Takht-e-Taus: golden throne with a jewelled peacock fan."""
    for i, a in enumerate(range(-70, 71, 20)):
        import math
        x, y = 100 + 76 * math.sin(math.radians(a)), 96 - 70 * math.cos(math.radians(a))
        p.line([(100, 100), (x, y)], "#2f8a6a", 7)
        p.ell(x, y, 12, 14, "#1f6f8a")
        p.ell(x, y, 5, 6, GOLD, ol=False)
    p.rrect(44, 92, 156, 176, 14, GOLD)
    p.rrect(62, 104, 138, 150, 10, "#7a1f2b")
    p.rrect(34, 150, 166, 172, 6, GOLD_D)
    for x in (56, 100, 144):
        p.ell(x, 162, 6, 6, "#c0322b", w=2)
    p.ell(100, 70, 12, 12, "#2f8a6a")                       # peacock head
    p.poly([(100, 58), (96, 46), (104, 46)], "#2f8a6a")


def kohinoor(p, c):
    """Koh-i-Noor diamond on a cushion."""
    p.ell(100, 160, 70, 22, "#7a1f2b")
    p.poly([(60, 96), (140, 96), (100, 156)], "#d9f2ff")
    p.poly([(60, 96), (76, 72), (124, 72), (140, 96)], "#eefaff")
    p.line([(76, 72), (88, 96), (100, 72), (112, 96), (124, 72)], "#8fbfd9", 3)
    p.line([(60, 96), (100, 156), (140, 96)], "#8fbfd9", 3)


def farman(p, c):
    """Mughal farman: tall scroll with tughra and seal."""
    p.rrect(52, 14, 148, 186, 4, "#efe0b8")
    p.arc(100, 40, 30, 14, 180, 360, "#c9961a", 5)          # tughra arc
    p.line([(80, 40), (120, 40)], "#c9961a", 4)
    for k in range(7):
        y = 66 + k * 14
        p.line([(140 - (k % 3) * 10, y), (62, y)], "#5a3a20", 3)
    p.ell(78, 164, 16, 16, "#b3202a")
    p.ell(78, 164, 9, 9, "#8a1a20", ol=False)
    p.rrect(46, 8, 154, 20, 6, "#c9a56a")
    p.rrect(46, 180, 154, 192, 6, "#c9a56a")


def grave(p, c):
    """Unmarked grave mound."""
    p.ell(100, 170, 90, 18, "#5a4a3a", ol=False)
    p.chord(100, 168, 70, 40, 180, 360, "#8a7a5a")
    for x in (60, 90, 126, 150):
        p.line([(x, 150), (x - 4, 138)], "#4a7a3a", 4)


def army_block(p, c):
    """A block of soldiers with spears. color = coat."""
    coat = c or "#6a4a2a"
    for row in range(3):
        for k in range(5):
            x, y = 28 + k * 36 + row * 6, 70 + row * 40
            p.line([(x + 10, y - 40), (x + 10, y + 10)], "#5a3a20", 3)
            p.poly([(x + 6, y - 40), (x + 14, y - 40), (x + 10, y - 52)], "#d9dde2", w=2)
            p.rrect(x - 12, y + 6, x + 12, y + 40, 8, shade(coat, 1 - row * 0.08))
            p.ell(x, y, 11, 11, "#c68a5c")
            p.chord(x, y - 3, 12, 10, 180, 360, "#8a8a90")


def mughal_tent(p, c):
    col = c or "#c0322b"
    p.poly([(20, 180), (180, 180), (150, 70), (50, 70)], col)
    p.poly([(50, 70), (150, 70), (100, 20)], shade(col, 0.85))
    p.poly([(84, 180), (116, 180), (100, 110)], "#3a1a14")
    for x in (50, 100, 150):
        p.line([(x, 70), (x, 180)], shade(col, 0.7), 3)
    p.line([(100, 20), (100, 4)], "#5a3a20", 4)
    p.poly([(100, 4), (126, 10), (100, 16)], GOLD)


def smoke(p, c):
    for x, y, r in ((70, 120, 46), (110, 100, 54), (140, 130, 40), (96, 140, 44)):
        p.ell(x, y, r, r * 0.8, c or "#c9c2b8", ol=False)


def matchlock_man(p, c):
    """Kneeling musketeer (toredar)."""
    coat = c or "#3f6d5a"
    p.rrect(70, 100, 130, 160, 18, coat)
    p.capsule((80, 160), (60, 186), 16, shade(coat, 0.8))
    p.capsule((120, 160), (140, 180), 16, shade(coat, 0.8))
    p.ell(100, 82, 20, 20, "#e0ac7e")
    p.chord(100, 76, 22, 18, 180, 360, "#efe6cf")
    p.line([(90, 120), (196, 96)], "#5a3a20", 8)
    p.line([(130, 112), (198, 96)], "#7a7f88", 4)


def rope(p, c):
    for k in range(6):
        p.arc(30 + k * 28, 100, 16, 10, 0, 360, "#d9b77a", 6)
