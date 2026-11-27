# builds story.json (demo beats s01-s49) for the Mughal Empire video
import json, re, os
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = P + "/docs/"
T = {}
for line in open(P + "/SCRIPT.md", encoding="utf-8"):
    m = re.match(r"- (s\d\db?) (?:\[[^\]]*\])+ (.*)", line.strip())
    if m: T[m.group(1)] = m.group(2).strip()

EL = lambda v: {"elevenlabs": {"voice_id": v, "model": "eleven_v4"}}
story = {
 "title": "Duniya Ka Sabse Ameer Saltanat Kaise Mita? | Mughal Empire",
 "style": "toon", "res": "360", "fps": 30, "music": "epic", "music_volume": 0.1, "sfx_volume": 0.2,
 "pause": 0.1, "auto_transitions": True,
 "voice": {"engine": "edge", "voice": "hi-IN-MadhurNeural", "rate": "+6%", "pitch": "-6Hz"},
 "speakers": {"N": EL("EppcM8bFS2tfl4Xu0tpj"), "BABUR": EL("n4jGuG5wrMvqWCjMtnMS"),
              "LODI": EL("7EvySNHBey9ISwbL5Bt5"), "SOLDIER": EL("7b9mYhmnp0y2qSH1FnBL"),
              "NANI": EL("MaJjkQJkKTqVB1XVQopL")},
 "cast": {
   "babur": {"preset": "mughal_emperor", "facial": "beard", "hat_color": "#efe6cf", "color": "#3f6d5a", "accent": "#c9a227", "age": "young"},
   "babur_boy": {"preset": "nawab", "facial": None, "hat_color": "#efe6cf", "color": "#3f6d5a", "accent": "#c9a227", "age": "young"},
   "umar": {"preset": "mughal_emperor", "color": "#5a3a6a", "hat_color": "#f3e3b5", "age": "adult", "body": "fat"},
   "ibrahim": {"preset": "nawab", "facial": "full_beard", "hat_color": "#7a1f2b", "color": "#8a3f22", "accent": "#e8c547", "age": "adult", "body": "fat"},
   "daulat": {"preset": "minister", "hat_color": "#2f5d8a", "color": "#4a3a6a"},
   "sardar": {"preset": "minister", "hat_color": "#6a2a2a", "color": "#5a4a3a", "age": "adult"},
   "zafar": {"preset": "mughal_emperor", "hair_color": "#ecebe6", "age": "old", "color": "#e6dfcc", "accent": "#8a7a5a", "jewel": False, "body": "thin", "hat_color": "#f2efe6"},
   "nani": {"preset": "farmer_woman", "skin": "light", "hat_color": "#e9e2d0", "color": "#5a3a5a", "age": "old"},
   "soldier": {"preset": "minister", "hat": "helmet", "hat_color": "#8a8a90", "color": "#6a4a2a", "facial": "mustache", "age": "young"},
   "sanga": {"preset": "maharaja", "hat_color": "#e0782f", "color": "#c0322b", "accent": "#e8c547"},
   "redcoat": {"preset": "british_officer", "hat": "pith_helmet", "hat_color": "#e8e0c8", "hair": "short", "hair_color": "#8a6a4a"},
 },
 "description": "", "tags": [], "pinned_comment": "",
 "sources": [], "beats": []}

def B(i, scene, speaker="N", **kw):
    if speaker != "N" and scene.get("type") == "set":
        scene.setdefault("names", []).append({"t": "NAATYA ROOPANTARAN", "x": 0.68, "y": 0.89, "at": 0.2, "bar": "#555555"})
    b = {"id": i, "speaker": speaker, "text": T[i], "scene": scene}
    b.update(kw); story["beats"].append(b)

SRC_M = "Maddison, The World Economy: A Millennial Perspective (OECD, 2001)"
INDIA_V = [60, 5, 100, 40]
# ---------------- cold open
B("s01", {"type": "set", "bg": "mughal_court", "cam": "dolly_in", "fg": [],
          "props": [{"name": "throne", "x": 0.5, "y": 0.66, "h": 0.36, "anim": "pop"},
                    {"name": "chest", "x": 0.22, "y": 0.8, "h": 0.16, "anim": "drop"},
                    {"name": "gold_bars", "x": 0.78, "y": 0.82, "h": 0.12, "anim": "drop"}],
          "big": {"t": "1/4 DUNIYA KI DAULAT", "y": 0.16}, "names": [{"t": "MUGHAL HINDUSTAN", "x": 0.5, "y": 0.84, "at": 2.6, "bar": "#c9a227"}], "caption": "SAAL 1700",
          "stickers": [{"name": "coin", "anim": "rain", "h": 0.08, "at": 0.3}],
          "source": SRC_M, "source_by": "anumaan · India ≈ 24.4% world GDP"}, tags="[dramatically]", sfx=["cash"], chapter="Duniya ki 1/4 daulat")
B("s02", {"type": "map", "view": INDIA_V, "cam": "drift", "highlight": {"IND": "#d9a72b", "PAK": "#d9a72b", "BGD": "#d9a72b", "AFG": "#c99a35"},
          "labels": [{"lon": 78, "lat": 22, "t": "MUGHAL HINDUSTAN", "size": 60, "color": "#ffffff", "delay": 0.3},
                     {"lon": 78, "lat": 17.5, "t": "~40 LAKH KM²  ·  10+ CRORE LOG", "size": 34, "color": "#ffe9a8", "delay": 1.4}],
          "source": "Mughal Empire (c. 1690–1700) — Wikipedia; World History Encyclopedia", "source_by": "estimates"})
B("s03", {"type": "black", "t": "लेकिन करीब डेढ़ सौ साल बाद..."}, tags="[softly]", sfx=["tension"])
B("s04", {"type": "set", "bg": "fort", "cam": "truck_right", "caption": "DELHI, OCT 1858",
          "chars": [{"who": "zafar", "x": 0.5, "h": 0.44, "expr": "sad", "pose": "idle", "face": "right", "seated": True},
                    {"who": "redcoat", "x": 0.16, "h": 0.5, "expr": "neutral", "face": "right"},
                    {"who": "redcoat", "x": 0.84, "h": 0.5, "expr": "neutral", "face": "left"}],
          "names": [{"t": "AAKHRI MUGHAL BADSHAH · 82 SAAL", "x": 0.5, "y": 0.84, "at": 0.8}]}, tags="[slowly]")
B("s05", {"type": "set", "bg": "fort", "cam": "dolly_in", "zoom": 1.3, "focus": [0.5, 0.45],
          "chars": [{"who": "zafar", "x": 0.5, "h": 0.6, "expr": "sad", "pose": "head", "face": "left", "seated": True}],
          "names": [{"t": "2 BETE + 1 POTA — GOLI SE MAARE GAYE", "x": 0.06, "y": 0.8, "at": 1.0, "bar": "#7a1f2b"}],
          "source": "Bahadur Shah II — Wikipedia (Hodson, 22 Sep 1857)", "source_by": "historical record"}, tags="[sad]")
B("s06", {"type": "realdoc", "img": D + "zafar_1858_tytler.jpg", "tone": "sepia", "push": [1.0, 1.25], "yaw": [-8, 4], "curl": 0.3,
          "focus": [0.5, 0.45], "source": "Bahadur Shah Zafar, May 1858 — photo by Robert Tytler & Charles Shepherd",
          "source_by": "British Library via Wikimedia Commons · Public domain"}, sfx=["click"])
B("s07", {"type": "map", "view": [66, 8, 102, 40], "cam": "drift", "highlight": {"IND": "#c0322b", "MMR": "#6a5a8a"},
          "routes": [{"from": [77.2, 28.6], "via": [[81.8, 25.4], [88.3, 22.5]], "to": [96.16, 16.8], "delay": 0.4, "time": 2.6, "mover": "ship", "color": "#ffd166"}],
          "pins": [{"lon": 77.2, "lat": 28.6, "label": "DELHI", "delay": 0.1}, {"lon": 96.16, "lat": 16.8, "label": "RANGOON · 1862", "delay": 2.8}],
          "labels": [{"lon": 88, "lat": 31.5, "t": "2,000+ KM DOOR", "size": 40, "color": "#ffffff", "delay": 1.6}]})
B("s08", {"type": "split", "left": {"type": "set", "bg": "mughal_court", "cam": "dolly_in", "fg": [],
             "props": [{"name": "throne", "x": 0.5, "y": 0.66, "h": 0.4, "anim": "pop"}], "caption": "1700"},
          "right": {"type": "set", "bg": "prison", "cam": "dolly_in", "fg": [],
             "chars": [{"who": "zafar", "x": 0.5, "h": 0.46, "expr": "sad", "seated": True}], "caption": "1858",
             "stickers": [{"name": "question", "side": "top", "anim": "pop", "h": 0.2, "at": 0.8}]}}, tags="[curious]")
B("s09", {"type": "black", "t": "एक कमज़ोरी... जो पहले दिन से अंदर थी."}, tags="[mysteriously]")
B("s10", {"type": "set", "bg": "mughal_court", "cam": "push_fast", "zoom": 1.2, "focus": [0.5, 0.55],
          "props": [{"name": "throne", "x": 0.5, "y": 0.64, "h": 0.42, "anim": "pop", "label": "TAKHT-E-TAUS"}],
          "stickers": [{"name": "question", "side": "top_right", "anim": "pop", "pulse": True, "h": 0.16, "at": 0.6}]}, sfx=["whoosh"])
B("s11", {"type": "set", "bg": "palace_room", "cam": "dolly_in",
          "props": [{"name": "crown", "x": 0.5, "y": 0.55, "h": 0.3, "anim": "spin", "label": "KOH-I-NOOR"}],
          "emph": [{"x": 0.5, "y": 0.5, "r": 0.18, "at": 0.4}],
          "stickers": [{"name": "question", "side": "top_left", "anim": "pop", "h": 0.16, "at": 0.5}]}, sfx=["ding"])
B("s12", {"type": "set", "bg": "office_day", "cam": "dolly_in",
          "popup": {"name": "charter", "x": 0.5, "at": 0.2, "h": 0.5, "rot": -6},
          "big": {"t": "FARMAN 1717 · ₹3,000 / SAAL", "y": 0.14, "at": 1.0},
          "stickers": [{"name": "eic_flag", "side": "top_right", "anim": "slide", "h": 0.14, "at": 2.0}],
          "source": "Farrukh Siyar's Farman — Banglapedia", "source_by": "historical record"}, sfx=["stamp"])
B("s13", {"type": "black", "t": "1526 से 1857 तक. 331 साल."}, sfx=["drum"])
B("s14", {"type": "black", "t": "एक ग्यारह साल का लड़का..."}, chapter="Babur: Fergana se Panipat", tags="[softly]")
# ---------------- chapter 1: Babur
CA_V = [56, 22, 86, 46]
B("s15", {"type": "map", "view": CA_V, "cam": "drift", "highlight": {"UZB": "#3f8a6a", "IND": "#8a6a3a"},
          "pins": [{"lon": 72.3, "lat": 40.8, "label": "FERGANA (ANDIJAN)", "delay": 0.4}],
          "labels": [{"lon": 63, "lat": 44.5, "t": "AAJ KA UZBEKISTAN", "size": 34, "color": "#ffffff", "delay": 1.0}],
          "caption": "1494"})
B("s16", {"type": "set", "bg": "fort", "cam": "crane_down", "caption": "AKHSI QILA, 1494",
          "chars": [{"who": "umar", "x": 0.5, "h": 0.46, "expr": "shocked", "pose": "up", "shake": True}],
          "props": [{"name": "warning", "x": 0.76, "y": 0.3, "h": 0.14, "anim": "pop"}],
          "names": [{"t": "UMAR SHAIKH MIRZA", "x": 0.06, "y": 0.8, "at": 0.4}],
          "source": "Baburnama (tr. A. S. Beveridge, 1922)", "source_by": "Public domain"}, sfx=["boom"])
B("s17", {"type": "set", "bg": "palace_room", "cam": "dolly_in",
          "chars": [{"who": "babur_boy", "x": 0.5, "h": 0.36, "expr": "worried", "face": "right"},
                    {"who": "sardar", "x": 0.2, "h": 0.5, "expr": "scheming", "face": "right", "pose": "bow"},
                    {"who": "sardar", "x": 0.82, "h": 0.5, "expr": "smug", "face": "left"}],
          "props": [{"name": "crown", "x": 0.5, "y": 0.22, "h": 0.1, "anim": "drop"}],
          "names": [{"t": "BABUR · 11 SAAL", "x": 0.5, "y": 0.84, "at": 0.6, "bar": "#c9a227"}]})
B("s18", {"type": "set", "bg": "palace_room", "cam": "truck_left",
          "chars": [{"who": "babur_boy", "x": 0.68, "h": 0.4, "expr": "proud", "pose": "hips", "face": "left"}],
          "props": [{"name": "portrait", "x": 0.28, "y": 0.42, "h": 0.32, "anim": "pop", "label": "TIMUR"}]})
B("s19", {"type": "set", "bg": "palace_room", "cam": "truck_right",
          "chars": [{"who": "babur_boy", "x": 0.32, "h": 0.4, "expr": "proud", "pose": "hips", "face": "right"}],
          "props": [{"name": "portrait", "x": 0.72, "y": 0.42, "h": 0.32, "anim": "pop", "label": "CHANGEZ KHAN"}],
          "source": "Babur — Encyclopaedia Britannica", "source_by": "britannica.com"})
B("s20", {"type": "set", "bg": "war_tent", "cam": "orbit_left",
          "chars": [{"who": "babur_boy", "x": 0.5, "h": 0.4, "expr": "worried", "face": "right"},
                    {"who": "sardar", "x": 0.15, "h": 0.52, "expr": "angry", "face": "right", "pose": "fist", "dim": True},
                    {"who": "daulat", "x": 0.85, "h": 0.52, "expr": "scheming", "face": "left", "dim": True}],
          "stickers": [{"name": "sword", "side": "top_left", "anim": "pop", "h": 0.14, "at": 1.2},
                       {"name": "sword", "side": "top_right", "anim": "pop", "h": 0.14, "at": 1.5}]})
B("s21", {"type": "map", "view": CA_V, "cam": "drift", "highlight": {"UZB": "#3f8a6a"},
          "routes": [{"from": [72.3, 40.8], "to": [66.97, 39.65], "delay": 0.4, "time": 1.6, "color": "#ffd166"}],
          "pins": [{"lon": 72.3, "lat": 40.8, "label": "FERGANA", "delay": 0.1}, {"lon": 66.97, "lat": 39.65, "label": "SAMARKAND", "delay": 1.8}]}, tags="[dreamy]")
B("s22", {"type": "set", "bg": "fort", "cam": "crane_up", "caption": "SAMARKAND, 1497",
          "chars": [{"who": "babur", "x": 0.5, "h": 0.46, "expr": "laugh", "pose": "cheer", "jump": True},
                    {"who": "soldier", "x": 0.25, "h": 0.44, "expr": "happy", "pose": "cheer"},
                    {"who": "soldier", "x": 0.75, "h": 0.44, "expr": "happy", "pose": "cheer"}],
          "props": [{"name": "flag", "x": 0.5, "y": 0.2, "h": 0.2, "color": "#3f6d5a", "anim": "pop"}],
          "names": [{"t": "SIRF 14 SAAL KI UMR", "x": 0.5, "y": 0.84, "at": 0.8}]}, sfx=["crowd"])
B("s23", {"type": "set", "bg": "fort", "cam": "shake",
          "days_left": {"x": 0.16, "y": 0.14, "w": 0.2, "n": 100, "title": "SAMARKAND"},
          "chars": [{"who": "babur", "x": 0.62, "h": 0.46, "expr": "shocked", "pose": "head"}],
          "stickers": [{"name": "arrow_down", "side": "top_right", "anim": "drop", "h": 0.16, "at": 1.0, "label": "FERGANA BHI GAYA"}]}, sfx=["tension"])
B("s24", {"type": "set", "bg": "village", "cam": "dolly_in", "zoom": 1.25, "focus": [0.4, 0.45],
          "chars": [{"who": "babur", "x": 0.4, "h": 0.6, "expr": "sad", "talk": True, "gesture": ["shrug", "head", "shrug"], "face": "right"},
                    {"who": "nani", "x": 0.86, "h": 1.15, "y": 0.42, "back": True, "face": "left"}],
          "board": {"text": "NA SAMARKAND, NA [GHAR]|AB KAHAN JAUN?", "rect": [0.08, 0.06, 0.64, 0.22], "at": 0.2, "time": 2.0}}, speaker="BABUR", tags="[sad] [sighs]")
B("s25", {"type": "set", "bg": "village", "cam": "orbit_right", "zoom": 1.25, "focus": [0.6, 0.45],
          "chars": [{"who": "nani", "x": 0.6, "h": 0.55, "expr": "proud", "talk": True, "gesture": ["point", "idle", "fist"], "face": "left"},
                    {"who": "babur", "x": 0.12, "h": 1.2, "y": 0.42, "back": True, "face": "right"}],
          "names": [{"t": "BABUR KI NAANI", "x": 0.06, "y": 0.82, "at": 0.3, "bar": "#a3233a"}]}, speaker="NANI", tags="[firmly]")
B("s26", {"type": "set", "bg": "village", "cam": "truck_right",
          "chars": [{"who": "babur", "x": -0.05, "to": 0.75, "walk_time": 3.5, "h": 0.42, "expr": "sad", "face": "right"},
                    {"who": "soldier", "x": -0.2, "to": 0.55, "walk_time": 3.5, "h": 0.4, "expr": "worried", "face": "right"}],
          "month_cal": {"x": 0.76, "y": 0.1, "w": 0.16, "title": "1501–1504", "icon": "sword", "at": 0.2, "time": 2.4}})
B("s27", {"type": "map", "view": CA_V, "cam": "drift", "highlight": {"AFG": "#3f8a6a"},
          "routes": [{"from": [72.3, 40.8], "via": [[68.8, 37.5]], "to": [69.2, 34.5], "delay": 0.3, "time": 1.8, "color": "#ffd166"}],
          "pins": [{"lon": 69.2, "lat": 34.5, "label": "KABUL · 1504", "delay": 2.0}]}, sfx=["drum"])
B("s28", {"type": "topdown", "paper": {"x": 0.5, "y": 0.5, "w": 0.22, "draw": "map", "at": 0.1, "note": "KABUL"},
          "hands": [{"from": "left", "to": [0.36, 0.48], "item": "coin_bag", "label": "KABUL", "at": 0.3, "release": 1.4, "sleeve": "#3f6d5a"},
                    {"from": "right", "to": [0.66, 0.5], "item": "cash", "label": "FAUJ", "at": 1.2, "release": 2.4, "sleeve": "#6a4a2a"}]})
B("s29", {"type": "map", "view": [58, 20, 86, 42], "cam": "drift", "highlight": {"AFG": "#3f8a6a", "IND": "#d9a72b", "PAK": "#d9a72b"},
          "routes": [{"from": [69.2, 34.5], "via": [[72.0, 33.6]], "to": [77.2, 28.6], "delay": 0.3, "time": 2.2, "color": "#ffd166"}],
          "labels": [{"lon": 71.8, "lat": 30.0, "t": "SINDHU", "size": 30, "color": "#9fd3ff", "delay": 1.0}],
          "pins": [{"lon": 77.2, "lat": 28.6, "label": "HINDUSTAN", "delay": 2.4}]}, sfx=["whoosh"])
B("s30", {"type": "set", "bg": "mughal_court", "cam": "dolly_in",
          "chars": [{"who": "ibrahim", "x": 0.5, "h": 0.46, "y": -0.06, "expr": "smug", "seated": True},
                    {"who": "sardar", "x": 0.18, "h": 0.5, "expr": "worried", "face": "right", "pose": "bow"},
                    {"who": "daulat", "x": 0.82, "h": 0.5, "expr": "scheming", "face": "left"}],
          "names": [{"t": "SULTAN IBRAHIM LODI", "x": 0.06, "y": 0.82, "at": 0.4, "bar": "#7a1f2b"}]})
B("s31", {"type": "set", "bg": "mughal_court", "cam": "orbit_left", "zoom": 1.2, "focus": [0.7, 0.45],
          "chars": [{"who": "daulat", "x": 0.7, "h": 0.58, "expr": "angry", "face": "left", "pose": "cross"},
                    {"who": "ibrahim", "x": 0.14, "h": 1.15, "y": 0.42, "back": True, "face": "right"}],
          "emph": [{"x": 0.7, "y": 0.3, "r": 0.12, "at": 0.5}]})
B("s32", {"type": "set", "bg": "study_night", "cam": "dolly_in",
          "chars": [{"who": "daulat", "x": 0.35, "h": 0.5, "expr": "scheming", "pose": "give", "hold": "letter", "hold_size": 0.12, "face": "right"}],
          "popup": {"name": "letter", "x": 0.72, "at": 0.8, "h": 0.4, "rot": 6},
          "names": [{"t": "DAULAT KHAN LODI · PUNJAB", "x": 0.06, "y": 0.82, "at": 0.4}],
          "source": "First Battle of Panipat — Wikipedia", "source_by": "historical record"}, sfx=["page"])
B("s33", {"type": "set", "bg": "mughal_court", "cam": "punch", "zoom": 1.25, "focus": [0.5, 0.45],
          "chars": [{"who": "ibrahim", "x": 0.5, "h": 0.6, "expr": "laugh", "talk": True, "gesture": ["idle", "point", "cross"], "seated": True}],
          "board": {"text": "KABUL SE KOI AAYEGA?|[MAZAAQ] HAI!", "rect": [0.1, 0.06, 0.62, 0.22], "at": 0.2, "time": 2.0}}, speaker="LODI", tags="[mocking] [laughs]")
B("s34", {"type": "black", "t": "बाबर आया. लेकिन मेहमान बनकर नहीं."}, chapter="Panipat, 1526", tags="[dramatically]", sfx=["boom"])
B("s35", {"type": "set", "bg": "battlefield", "cam": "crane_down", "caption": "PANIPAT · 21 APRIL 1526",
          "props": [{"name": "flag", "x": 0.2, "y": 0.5, "h": 0.2, "color": "#3f6d5a"}, {"name": "flag", "x": 0.8, "y": 0.5, "h": 0.2, "color": "#7a1f2b"}],
          "source": "First Battle of Panipat — Wikipedia; Britannica", "source_by": "historical record"}, sfx=["drum"])
B("s36", {"type": "set", "bg": "battlefield", "cam": "truck_left",
          "chars": [{"who": "babur", "x": 0.3, "h": 0.48, "expr": "thinking", "pose": "chin", "face": "right"},
                    {"who": "soldier", "x": 0.12, "h": 0.42, "expr": "neutral", "face": "right"},
                    {"who": "soldier", "x": 0.48, "h": 0.42, "expr": "neutral", "face": "right"}],
          "big": {"t": "{n} SAINIK", "count": 12000, "y": 0.16}, "source": "anumaan — historians", "source_by": "First Battle of Panipat · Wikipedia"})
B("s37", {"type": "chart", "bars": [{"label": "BABUR", "value": 12, "text": "~12,000", "color": "#3f8a6a"},
                                    {"label": "IBRAHIM", "value": 100, "text": "1,00,000*", "color": "#c0322b"},
                                    {"label": "HAATHI", "value": 10, "text": "~1,000", "color": "#8a6a4a"}],
          "source": "*Baburnama ke mutabik · itihaskaar 40–70 hazaar maante hain", "source_by": "historyofwar.org · Wikipedia"})
B("s38", {"type": "set", "bg": "war_tent", "cam": "dolly_in", "zoom": 1.2, "focus": [0.62, 0.45],
          "chars": [{"who": "soldier", "x": 0.62, "h": 0.58, "expr": "shocked", "talk": True, "gesture": ["shrug", "point", "shrug"], "face": "left"},
                    {"who": "babur", "x": 0.12, "h": 1.2, "y": 0.42, "back": True, "face": "right"}],
          "stickers": [{"name": "exclaim", "side": "top_right", "anim": "pop", "h": 0.14, "at": 0.3}]}, speaker="SOLDIER", tags="[panicked]")
B("s39", {"type": "set", "bg": "war_tent", "cam": "push_fast", "zoom": 1.3, "focus": [0.4, 0.42],
          "chars": [{"who": "babur", "x": 0.4, "h": 0.62, "expr": "smug", "talk": True, "gesture": ["idle", "point"], "face": "right"}],
          "board": {"text": "GINTI MAT KARO.|[GAADIYAN] BAANDHO.", "rect": [0.5, 0.08, 0.92, 0.24], "at": 0.1, "time": 1.6}}, speaker="BABUR", tags="[calm] [confident]")
B("s40", {"type": "topdown", "paper": {"x": 0.5, "y": 0.5, "w": 0.34, "draw": "square", "at": 0.1, "note": "ARABA"},
          "hands": [{"from": "left", "to": [0.4, 0.52], "item": "cannon", "label": "TOPEIN", "at": 0.6, "release": 1.8, "sleeve": "#3f6d5a"},
                    {"from": "right", "to": [0.6, 0.5], "item": "musket", "label": "BANDOOK", "at": 1.6, "release": 2.8, "sleeve": "#6a4a2a"}],
          "source": "Baburnama (tr. Beveridge, 1922)", "source_by": "Public domain"}, sfx=["click"])
B("s41", {"type": "set", "bg": "battlefield", "cam": "dolly_in",
          "props": [{"name": "cannon", "x": 0.3, "y": 0.74, "h": 0.2, "anim": "slide"}, {"name": "cannon", "x": 0.55, "y": 0.76, "h": 0.2, "anim": "slide"}],
          "stickers": [{"name": "warning", "side": "top_right", "anim": "pop", "h": 0.14, "at": 1.0, "label": "USTAD ALI QULI"}]})
B("s42", {"type": "set", "bg": "battlefield", "cam": "crane_up",
          "chars": [{"who": "soldier", "x": 0.5, "h": 0.36, "expr": "angry", "pose": "fist", "label": "IBRAHIM KI FAUJ"}],
          "swoosh": [{"x": 0.5, "y": 0.55, "r": 0.32, "a0": 200, "a1": 330, "color": "#3fbf7a", "at": 0.4},
                     {"x": 0.5, "y": 0.55, "r": 0.32, "a0": 20, "a1": 150, "color": "#3fbf7a", "at": 0.9}],
          "big": {"t": "TULUGHMA", "y": 0.14, "at": 1.8}}, sfx=["swoosh"])
B("s43", {"type": "set", "bg": "battlefield", "cam": "shake",
          "props": [{"name": "cannon", "x": 0.3, "y": 0.74, "h": 0.22}, {"name": "fire", "x": 0.42, "y": 0.62, "h": 0.2, "anim": "pop"},
                    {"name": "cannon", "x": 0.6, "y": 0.76, "h": 0.22}, {"name": "fire", "x": 0.72, "y": 0.64, "h": 0.2, "anim": "pop"}]}, sfx=["boom", "boom"])
B("s44", {"type": "set", "bg": "battlefield", "cam": "truck_right",
          "chars": [{"who": "soldier", "x": 0.3, "h": 0.42, "expr": "shocked", "pose": "head", "shake": True, "face": "left"},
                    {"who": "sardar", "x": 0.6, "h": 0.44, "expr": "shocked", "pose": "up", "shake": True, "face": "left"}],
          "stickers": [{"name": "exclaim", "side": "top", "anim": "pop", "h": 0.16, "at": 0.4, "label": "HAATHI BIDKE"}],
          "source": "Panipat — panipat.gov.in", "source_by": "Govt. of Haryana"}, sfx=["crowd"])
B("s45", {"type": "set", "bg": "battlefield", "cam": "crane_up",
          "chars": [{"who": "babur", "x": 0.5, "h": 0.48, "expr": "proud", "pose": "fist"}],
          "names": [{"t": "IBRAHIM LODI — MAIDAN ME MAARE GAYE", "x": 0.5, "y": 0.84, "at": 1.4, "bar": "#7a1f2b"}],
          "source": "Ibrahim Lodi — Wikipedia", "source_by": "historical record"})
B("s46", {"type": "realdoc", "img": D + "panipat_baburnama_1598.jpg", "tone": "ink", "push": [1.0, 1.35], "yaw": [6, -4], "curl": 0.25,
          "focus": [0.5, 0.5],
          "source": "Battle of Panipat (20 April 1526), Baburnama, 1598 copy", "source_by": "Wikimedia Commons · Public domain"}, sfx=["page"])
B("s47", {"type": "set", "bg": "mughal_court", "cam": "crane_up",
          "chars": [{"who": "babur", "x": 0.5, "h": 0.46, "y": -0.06, "expr": "proud", "seated": True},
                    {"who": "soldier", "x": 0.18, "h": 0.48, "expr": "happy", "pose": "cheer"},
                    {"who": "soldier", "x": 0.82, "h": 0.48, "expr": "happy", "pose": "cheer"}],
          "props": [{"name": "mughal_flag", "x": 0.5, "y": 0.16, "h": 0.18, "anim": "pop"}],
          "big": {"t": "MUGHAL SALTANAT · 1526", "y": 0.86, "at": 2.0}}, sfx=["crowd"])
B("s48", {"type": "black", "t": "असली इम्तिहान अभी बाक़ी था..."}, tags="[dramatically]", sfx=["tension"])
B("s49", {"type": "set", "bg": "fort", "cam": "dolly_in", "caption": "MEWAR, 1527",
          "zoom": 1.3, "focus": [0.5, 0.42], "chars": [{"who": "sanga", "x": 0.5, "h": 0.62, "expr": "angry", "pose": "fist"}],
          "big": {"t": "{n} GHAAV?", "count": 80, "y": 0.16, "at": 1.2},
          "source": "parampara (James Tod, Annals of Rajasthan)", "source_by": "kehte hain"}, tags="[mysteriously]", sfx=["riser"])


# ---------- split long beats: every scene <= ~5 s
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from splits import SPLITS
A_SCENES = {
 "s18": {"type": "set", "bg": "palace_room", "cam": "push_fast", "zoom": 1.35, "focus": [0.5, 0.42],
         "chars": [{"who": "babur_boy", "x": 0.5, "h": 0.62, "expr": "proud", "pose": "hips"}],
         "emph": [{"x": 0.5, "y": 0.3, "r": 0.14, "at": 0.3}],
         "stickers": [{"name": "crown", "side": "top_left", "anim": "pop", "h": 0.12, "at": 0.6, "label": "2 BADE NAAM"}]},
 "s20": {"type": "map", "view": CA_V, "cam": "drift", "highlight": {"UZB": "#3f8a6a"},
         "pins": [{"lon": 72.3, "lat": 40.8, "label": "FERGANA", "delay": 0.2}],
         "labels": [{"lon": 66, "lat": 44.5, "t": "CHHOTA SA RAJYA", "size": 40, "color": "#ffffff", "delay": 0.8}]},
 "s22": {"type": "set", "bg": "village", "cam": "truck_right", "caption": "1497",
         "chars": [{"who": "babur", "x": -0.05, "to": 0.6, "walk_time": 3.2, "h": 0.44, "expr": "proud", "face": "right"},
                   {"who": "soldier", "x": -0.25, "to": 0.4, "walk_time": 3.2, "h": 0.42, "face": "right"},
                   {"who": "soldier", "x": -0.4, "to": 0.22, "walk_time": 3.2, "h": 0.42, "face": "right"}],
         "names": [{"t": "SIRF 14 SAAL KI UMR", "x": 0.06, "y": 0.82, "at": 0.6}]},
 "s29": {"type": "set", "bg": "fort", "cam": "truck_right", "caption": "KABUL, 1519",
         "chars": [{"who": "babur", "x": 0.35, "h": 0.48, "expr": "scheming", "pose": "point", "face": "right"}],
         "stickers": [{"name": "arrow_up", "side": "top_right", "anim": "pop", "h": 0.16, "at": 0.5, "label": "PURAB"}]},
 "s37": {"type": "set", "bg": "battlefield", "cam": "truck_right",
         "chars": [{"who": "ibrahim", "x": 0.68, "h": 0.48, "expr": "smug", "pose": "cross", "face": "left"},
                   {"who": "sardar", "x": 0.5, "h": 0.44, "face": "left"}, {"who": "sardar", "x": 0.86, "h": 0.44, "face": "left"}],
         "big": {"t": "{n} SAINIK*", "count": 100000, "y": 0.16},
         "source": "*Baburnama ke mutabik · itihaskaar 40–70 hazaar", "source_by": "Wikipedia · historyofwar.org"},
 "s47": {"type": "set", "bg": "battlefield", "cam": "crane_up",
         "chars": [{"who": "babur", "x": 0.5, "h": 0.5, "expr": "laugh", "pose": "cheer", "jump": True},
                   {"who": "soldier", "x": 0.26, "h": 0.44, "expr": "happy", "pose": "cheer"}, {"who": "soldier", "x": 0.74, "h": 0.44, "expr": "happy", "pose": "cheer"}],
         "big": {"t": "~12,000 NE GIRAYI SALTANAT", "y": 0.16, "at": 0.8}},
 "s49": {"type": "set", "bg": "fort", "cam": "truck_left", "caption": "MEWAR, 1527",
         "chars": [{"who": "sanga", "x": 0.5, "h": 0.46, "expr": "angry", "pose": "fist", "dim": True},
                   {"who": "soldier", "x": 0.22, "h": 0.42, "expr": "angry", "dim": True}, {"who": "soldier", "x": 0.78, "h": 0.42, "expr": "angry", "dim": True}]},
}
out = []
for b in story["beats"]:
    sp = SPLITS.get(b["id"])
    if not sp: out.append(b); continue
    _, _, scB, extra = sp
    nb = {"id": b["id"] + "b", "speaker": b["speaker"], "text": T[b["id"] + "b"]}
    if isinstance(scB, dict):
        nb["scene"] = scB
    else:  # part B keeps the original scene, part A gets a new one
        nb["scene"] = b["scene"]; b["scene"] = A_SCENES[b["id"]]
        for k in ("sfx",): b.pop(k, None)
    nb.update(extra)
    if b.get("tags") and "tags" not in nb: nb["tags"] = b["tags"]
    out += [b, nb]
story["beats"] = out
story["sources"] = [
 {"t": SRC_M, "url": "https://en.wikipedia.org/wiki/Economic_history_of_the_Indian_subcontinent"},
 {"t": "Mughal Empire — Wikipedia", "url": "https://en.wikipedia.org/wiki/Mughal_Empire"},
 {"t": "Bahadur Shah II — Wikipedia", "url": "https://en.wikipedia.org/wiki/Bahadur_Shah_II"},
 {"t": "Babur — Britannica", "url": "https://www.britannica.com/biography/Babur"},
 {"t": "First Battle of Panipat — Wikipedia", "url": "https://en.wikipedia.org/wiki/First_Battle_of_Panipat"},
 {"t": "Farrukh Siyar's Farman — Banglapedia", "url": "https://en.banglapedia.org/index.php/Farrukh_Siyar%E2%80%99s_Farman"},
 {"t": "Photo: Bahadur Shah Zafar, 1858 (Tytler) — Commons", "url": "https://commons.wikimedia.org/wiki/File:Bahadur_Shah_Zafar.jpg"},
 {"t": "Baburnama 1598, Battle of Panipat — Commons", "url": "https://commons.wikimedia.org/wiki/File:Battle_of_Panipat_(20_April_1526)._Baburnama_of_1598.jpg"}]
json.dump(story, open(P + "/story.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(story["beats"]), "beats", sum(len(b["text"].split()) for b in story["beats"]), "words")
