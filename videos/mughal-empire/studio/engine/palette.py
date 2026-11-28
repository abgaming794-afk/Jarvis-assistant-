"""One accent colour for every border / stroke / underline / rule / glow edge.
Change it here (or set env NAATYA_ACCENT=name) and the whole video follows."""
import os

OPTIONS = {
    "gold":    (214, 178, 96),    # old look
    "crimson": (214, 58, 58),     # Mughal red: same family as pins + medallion ring
    "teal":    (64, 196, 200),    # cool, complementary to the warm territory fill
    "ivory":   (240, 232, 214),   # neutral white edge (no extra hue)
}
NAME = os.environ.get("NAATYA_ACCENT", "crimson")
ACC = OPTIONS[NAME]


def acc(a=255):
    return ACC + (int(a),)


def glow(a=230):
    """Brighter version of the accent for glowing map borders."""
    return tuple(min(255, int(c * 1.15 + 20)) for c in ACC) + (int(a),)
